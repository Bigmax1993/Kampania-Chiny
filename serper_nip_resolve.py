# -*- coding: utf-8 -*-
"""
Brak NIP w JSON → Serper → requests+BS4 → Claude (werdykt) → zapis NIP.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from cn_contact_fields import (
    extract_all_pl_nips_from_text,
    normalize_pl_nip,
    pl_nip_checksum_ok,
)
from claude_client import claude_generate_text
from claude_prompts import build_nip_verify_prompt
from scraper_env import get_anthropic_api_key, get_serper_api_key

SERPER_API_URL = "https://google.serper.dev/search"
_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)
_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
_MAX_SERPER_QUERIES = 3
_MAX_PAGES_FETCH = 4
_PAGE_TEXT_CAP = 8000


def _domain(url: str) -> str:
    try:
        return (urlparse(url).netloc or "").lower().replace("www.", "")
    except Exception:
        return ""


def _serper_organic(query: str, api_key: str, logger: logging.Logger | None) -> list[dict]:
    try:
        r = requests.post(
            SERPER_API_URL,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "gl": "pl", "hl": "pl", "num": 8},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        return list(data.get("organic") or [])
    except Exception as exc:
        if logger:
            logger.warning("Serper NIP fail %s: %s", query, exc)
        return []


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def _fetch_page_text(url: str, logger: logging.Logger | None) -> str:
    if not (url or "").lower().startswith(("http://", "https://")):
        return ""
    try:
        r = requests.get(url, headers=_FETCH_HEADERS, timeout=25)
        r.raise_for_status()
        text = _html_to_text(r.text or "")
        if len(text) > _PAGE_TEXT_CAP:
            text = text[:_PAGE_TEXT_CAP]
        return text
    except Exception as exc:
        if logger:
            logger.info("NIP page fetch skip %s: %s", url, exc)
        return ""


def _build_queries(company_name: str, website: str) -> list[str]:
    name = (company_name or "").strip()
    domain = _domain(website)
    queries: list[str] = []
    if name:
        queries.append(f"{name} NIP")
        queries.append(f'"{name}" NIP Polska')
        queries.append(f"{name} numer NIP")
    if domain:
        queries.append(f"NIP site:{domain}")
        queries.append(f"{domain} NIP")
    # Unikalne, zachowaj kolejność.
    out: list[str] = []
    seen: set[str] = set()
    for q in queries:
        if q not in seen:
            seen.add(q)
            out.append(q)
    return out[:_MAX_SERPER_QUERIES]


def _parse_claude_nip_verdict(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    match = _JSON_BLOCK_RE.search(raw)
    payload = match.group(0) if match else raw
    data = json.loads(payload)
    if not isinstance(data, dict):
        return {"match": False, "nip": "", "reason": "bad_json"}
    nip = normalize_pl_nip(str(data.get("nip") or ""))
    matched = bool(data.get("match")) and bool(nip)
    return {
        "match": matched,
        "nip": nip if matched else "",
        "reason": str(data.get("reason") or "").strip(),
    }


def _claude_pick_nip(
    company_name: str,
    website: str,
    candidates: list[str],
    evidence: str,
    logger: logging.Logger | None,
    cache: dict | None,
) -> str:
    api_key = get_anthropic_api_key()
    if not api_key or not candidates:
        return ""
    prompt = build_nip_verify_prompt(company_name, website, candidates, evidence)
    try:
        text, model = claude_generate_text(
            prompt,
            logger,
            api_key,
            cache=cache,
            model_tier="verify",
        )
        if logger:
            logger.info("Claude NIP verify model=%s candidates=%s", model, candidates)
        verdict = _parse_claude_nip_verdict(text)
        if verdict.get("match") and verdict.get("nip") in candidates:
            if logger:
                logger.info(
                    "Claude NIP OK %s ← %s",
                    verdict["nip"],
                    (verdict.get("reason") or "")[:120],
                )
            return str(verdict["nip"])
        if logger:
            logger.info(
                "Claude NIP reject: %s",
                (verdict.get("reason") or "no match")[:160],
            )
    except Exception as exc:
        if logger:
            logger.warning("Claude NIP verify: %s", exc)
    return ""


def resolve_missing_nip_via_serper(
    company_name: str,
    website: str,
    logger: logging.Logger | None = None,
    cache: dict | None = None,
    *,
    existing_nip: str = "",
) -> str:
    """
    Gdy brak NIP: Serper → pobranie stron (requests+BS4) → luźny regex → Claude.
    Zwraca NIP jako 10 cyfr (bez spacji/myślników) albo "".
    """
    existing = normalize_pl_nip(existing_nip or "")
    if existing:
        return existing

    api_key = get_serper_api_key()
    if not api_key:
        if logger:
            logger.warning("Brak SERPER_API_KEY — pomijam Serper NIP")
        return ""

    resolve_cache = (cache or {}).setdefault("serper_nip_resolve", {})
    cache_key = f"{(company_name or '').strip().lower()}|{_domain(website)}"
    if cache_key in resolve_cache:
        cached = resolve_cache[cache_key]
        if isinstance(cached, dict):
            return normalize_pl_nip(str(cached.get("nip") or ""))
        return normalize_pl_nip(str(cached or ""))

    queries = _build_queries(company_name, website)
    organic_all: list[dict] = []
    snippet_blob_parts: list[str] = []
    candidates: list[str] = []
    seen_nip: set[str] = set()

    def _push_nips(text: str) -> None:
        for nip in extract_all_pl_nips_from_text(text, loose=True):
            if nip not in seen_nip:
                seen_nip.add(nip)
                candidates.append(nip)

    for q in queries:
        organic = _serper_organic(q, api_key, logger)
        for item in organic:
            organic_all.append(item)
            title = str(item.get("title") or "")
            snippet = str(item.get("snippet") or "")
            link = str(item.get("link") or "")
            blob = f"{title} {snippet} {link}"
            snippet_blob_parts.append(blob)
            _push_nips(blob)
            if logger and candidates:
                logger.info("Serper NIP kandydat(y) %s ← query=%s", candidates, q)

    # Pobierz top strony z wyników (requests + BS4).
    page_parts: list[str] = []
    seen_urls: set[str] = set()
    company_domain = _domain(website)
    # Preferuj domenę firmy, potem pozostałe.
    ranked_links: list[str] = []
    for item in organic_all:
        link = str(item.get("link") or "").strip()
        if not link or link in seen_urls:
            continue
        seen_urls.add(link)
        ranked_links.append(link)
    ranked_links.sort(
        key=lambda u: (0 if company_domain and company_domain in _domain(u) else 1, u)
    )
    for link in ranked_links[:_MAX_PAGES_FETCH]:
        text = _fetch_page_text(link, logger)
        if not text:
            continue
        page_parts.append(f"=== {link}\n{text}")
        _push_nips(text)

    evidence = "\n\n".join(
        [
            "SERPER SNIPPETS:\n" + "\n".join(snippet_blob_parts[:12]),
            "PAGES:\n" + "\n\n".join(page_parts),
        ]
    ).strip()

    nip = ""
    if candidates:
        nip = _claude_pick_nip(
            company_name, website, candidates, evidence, logger, cache
        )
    # Fallback bez Claude: jeden NIP z checksum z własnej domeny / etykiety.
    if not nip and len(candidates) == 1 and pl_nip_checksum_ok(candidates[0]):
        nip = candidates[0]
        if logger:
            logger.info("NIP fallback (1 kandydat checksum) %s", nip)

    if cache is not None:
        resolve_cache[cache_key] = {"nip": nip, "candidates": candidates}
    return nip


def apply_nip_to_contact_json(
    contacts: dict,
    *,
    url: str,
    website: str,
    nip: str,
) -> bool:
    """Nadpisuje nip w contacts JSON (klucz = URL miejsca lub www)."""
    nip = normalize_pl_nip(nip)
    if not nip:
        return False
    keys = []
    for k in (url, website):
        k = (k or "").strip()
        if k and k not in keys:
            keys.append(k)
    if not keys:
        return False
    wrote = False
    for key in keys:
        info = dict(contacts.get(key) or {})
        info["nip"] = nip
        info["tax_id"] = nip
        contacts[key] = info
        wrote = True
    return wrote
