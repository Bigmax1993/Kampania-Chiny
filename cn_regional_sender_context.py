# -*- coding: utf-8 -*-
"""Kontekst nadawcy maili CN — chiński producent/eksporter do polskiego dystrybutora/importera."""
from __future__ import annotations

from cn_province_keywords import PROVINCE_CONFIG, _normalize_wojewodztwo_key

MAJOR_CITY_WOJEWODZTWO_KEYS: frozenset[str] = frozenset(PROVINCE_CONFIG.keys())


def resolve_discovery_wojewodztwo(contact_info: dict | None, *, fallback: str = "") -> str:
    """Województwo odbiorcy z discovery (discovery_bundesland) lub z wiersza kontaktu."""
    info = contact_info or {}
    for key in ("discovery_bundesland", "bundesland", "wojewodztwo"):
        raw = str(info.get(key) or "").strip()
        if not raw:
            continue
        normalized = _normalize_wojewodztwo_key(raw)
        if normalized in PROVINCE_CONFIG:
            return normalized
    fb = _normalize_wojewodztwo_key(fallback)
    return fb if fb in PROVINCE_CONFIG else (fallback or "").strip()


def wojewodztwo_primary_city_pl(wojewodztwo_key: str) -> str:
    key = _normalize_wojewodztwo_key(wojewodztwo_key)
    cfg = PROVINCE_CONFIG.get(key) or {}
    cities = cfg.get("cities") or ()
    return str(cities[0]) if cities else key


def wojewodztwo_cities_pl(wojewodztwo_key: str, *, limit: int = 5) -> tuple[str, ...]:
    key = _normalize_wojewodztwo_key(wojewodztwo_key)
    cfg = PROVINCE_CONFIG.get(key) or {}
    cities = tuple(str(c) for c in (cfg.get("cities") or ()))
    return cities[:limit] if limit > 0 else cities


def wojewodztwo_region_label_pl(wojewodztwo_key: str) -> str:
    key = _normalize_wojewodztwo_key(wojewodztwo_key)
    city = wojewodztwo_primary_city_pl(key)
    if key in PROVINCE_CONFIG:
        return f"{city} (woj. {key})"
    return wojewodztwo_key or "Polska"


def major_city_examples_pl(wojewodztwo_key: str) -> str:
    key = _normalize_wojewodztwo_key(wojewodztwo_key)
    cities = wojewodztwo_cities_pl(key, limit=3)
    if not cities:
        return ""
    return ", ".join(cities)


def build_regional_sender_instructions_pl(
    wojewodztwo_key: str,
    *,
    sender_name: str,
    sender_phone: str,
    construction_project_block: str = "",
) -> str:
    """
    Nadawca = chiński producent/eksporter (Maksym).
    Odbiorca = polski dystrybutor/importer w województwie discovery.
    Plac budowy = w Polsce (blok OBIEKT BUDOWY) jako przykład zapotrzebowania.
    """
    key = _normalize_wojewodztwo_key(wojewodztwo_key)
    region = (
        wojewodztwo_region_label_pl(key)
        if key in PROVINCE_CONFIG
        else (wojewodztwo_key or "Polska")
    )
    cities = ", ".join(wojewodztwo_cities_pl(key, limit=6)) or region
    major_examples = major_city_examples_pl(key)
    name = (sender_name or "Maksym Swinczak").strip()
    project_section = (
        f"\n\n{construction_project_block.strip()}\n"
        if (construction_project_block or "").strip()
        else ""
    )
    hub_note = ""
    if major_examples:
        hub_note = (
            f"\n• Odbiorca działa w regionie ({major_examples}) — wspomnij miasto/województwo, "
            f"plac budowy bierz z bloku «OBIEKT BUDOWY» (Polska)."
        )

    return f"""REGION DISCOVERY (lokalizacja ODBIORCY w Polsce)
Województwo / region odbiorcy: {region}
Klucz województwa: {key or "(nieznane)"}
Miasta regionu: {cities}
{hub_note}

NADAWCA — CHIŃSKI PRODUCENT / EKSPORTER (szuka dystrybutora w Polsce)
• Przedstaw się jako {name} — reprezentujesz chińskiego producenta / eksportera materiałów budowlanych.
• Szukasz polskiego dystrybutora / importera / wyłącznego dystrybutora na terenie Polski.
• NIE wymyślaj polskiej firmy-nadawcy typu „Budownictwo XYZ Sp. z o.o.”.
• NIE udawaj lokalnego wykonawcy z Warszawy / Krakowa.
• Obiekt budowy bierz WYŁĄCZNIE z bloku «OBIEKT BUDOWY» — inwestycja w POLSCE (zapotrzebowanie).
{project_section}
PODPIS (dodaj na końcu body, po polsku — BEZ telefonu i BEZ strony www):
Z poważaniem,
{name}
Współpraca dystrybucyjna / import z Chin"""
