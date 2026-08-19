# -*- coding: utf-8 -*-
"""Walidacja Excel vs cache JSON: przepuszcza potrzebne dane z JSON i uzupelnia braki.

Przy uzupełnianiu braków walidacja jest luźniejsza niż przy discovery, ale nadal
odrzuca śmieci (marketing, portale, noreply, „kontakt”, puste URL).
"""
from __future__ import annotations

import re
from typing import Any

EXCEL_REQUIRED_IF_JSON_HAS = (
    "Name of Company",
    "Line of business",
    "Company website",
    "E-Mail",
    "Phone number",
    "Region",
    "Localisation",
    "Postcode",
    "Tax Identification Number",
)

_JSON_FILL_JUNK_NAMES = {
    "kontakt",
    "o nas",
    "start",
    "home",
    "strona główna",
    "strona glowna",
    "nieznana firma",
    "unknown",
    "n/a",
    "na",
    "-",
    "test",
    "regulamin",
    "newsletter",
    "blog",
    "promocje",
    "polityka prywatności",
    "polityka prywatnosci",
}
_JSON_FILL_JUNK_NAME_FRAGMENTS = (
    "biuro obsługi klienta",
    "biuro obslugi klienta",
    "kontakt z nami",
    "sklep internetowy",
    "strona główna",
    "strona glowna",
)
_JSON_FILL_JUNK_EMAIL_LOCAL = {
    "noreply",
    "no-reply",
    "do-not-reply",
    "donotreply",
    "mailer-daemon",
    "postmaster",
}
_JSON_FILL_JUNK_HOSTS = (
    "olx.pl",
    "allegro.pl",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "linkedin.com",
    "maps.google",
    "goo.gl",
    "bit.ly",
)
_PHONE_RE = re.compile(
    r"(?:\+48)?[\s\-.(/]*\d(?:[\d\s\-()./]{6,18})\d"
)


def _s(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def first_email_from_contact(info: dict) -> str:
    email = _s(info.get("email_target"))
    cleaned = _sanitize_json_fill_email(email)
    if cleaned:
        return cleaned
    found = [
        x.strip()
        for x in _s(info.get("emails_found")).split(",")
        if x.strip() and "@" in x
    ]
    for item in found:
        cleaned = _sanitize_json_fill_email(item)
        if cleaned:
            return cleaned
    return ""


def first_phone_from_contact(info: dict) -> str:
    for raw in (_s(info.get("phones_found")), _s(info.get("telefon"))):
        cleaned = _sanitize_json_fill_phone(raw)
        if cleaned:
            return cleaned
    return ""


def _sanitize_json_fill_email(value: str) -> str:
    email = _s(value).lower()
    if "@" not in email or " " in email:
        return ""
    local, _, host = email.partition("@")
    if not local or not host or "." not in host:
        return ""
    if local in _JSON_FILL_JUNK_EMAIL_LOCAL:
        return ""
    if any(h in host for h in _JSON_FILL_JUNK_HOSTS):
        return ""
    return _s(value)


def _sanitize_json_fill_phone(value: str) -> str:
    blob = _s(value)
    if not blob:
        return ""
    match = _PHONE_RE.search(blob)
    if not match:
        return ""
    candidate = " ".join(match.group(0).split()).strip()
    digits = re.sub(r"\D", "", candidate)
    if len(digits) < 7 or len(digits) > 15:
        return ""
    return candidate


def _sanitize_json_fill_name(value: str) -> str:
    name = " ".join(_s(value).split())
    if len(name) < 3:
        return ""
    low = name.lower()
    if low in _JSON_FILL_JUNK_NAMES:
        return ""
    if any(frag in low for frag in _JSON_FILL_JUNK_NAME_FRAGMENTS):
        return ""
    if re.match(r"^[\W\d_]+$", name):
        return ""
    from cn_contact_fields import looks_like_marketing_text

    if looks_like_marketing_text(name):
        return ""
    return name[:120]


def _sanitize_json_fill_website(value: str) -> str:
    url = _s(value)
    if not url:
        return ""
    low = url.lower()
    if any(h in low for h in _JSON_FILL_JUNK_HOSTS):
        return ""
    if low.startswith("mailto:"):
        return ""
    if not re.search(r"[.][a-z]{2,}", low):
        return ""
    return url


def _sanitize_json_fill_address(value: str, snippet: str = "") -> str:
    from cn_contact_fields import (
        extract_usable_address_for_json_fill,
        looks_like_marketing_text,
        looks_like_usable_address_for_json_fill,
    )

    raw = " ".join(_s(value).split())
    if raw and looks_like_usable_address_for_json_fill(raw):
        return raw[:180]
    if raw and not looks_like_marketing_text(raw) and 8 <= len(raw) <= 180:
        extracted = extract_usable_address_for_json_fill(raw)
        if extracted:
            return extracted
    if snippet:
        extracted = extract_usable_address_for_json_fill(snippet)
        if extracted:
            return extracted
    return ""


def _line_of_business_from_snippet(snippet: str) -> str:
    from cn_province_keywords import MATERIAL_CATEGORY_KEYWORDS, SUPPLIER_ROLE_KEYWORDS

    low = (snippet or "").lower()
    hits: list[str] = []
    for word in (*SUPPLIER_ROLE_KEYWORDS, *MATERIAL_CATEGORY_KEYWORDS):
        if word.lower() in low and word not in hits:
            hits.append(word)
        if len(hits) >= 4:
            break
    return ", ".join(hits)


def json_fill_fields(place_url: str, info: dict) -> dict[str, str]:
    """Pola z JSON do Excela: luźniej niż discovery, bez śmieci."""
    from cn_contact_fields import extract_pl_nip_from_text, extract_pl_postcode, normalize_pl_nip
    from cn_excel_en import region_to_internal

    snippet = _s(info.get("page_snippet"))
    name = _sanitize_json_fill_name(
        _s(info.get("company_name_clean"))
        or _s(info.get("company_name"))
        or _s(info.get("company_name_raw"))
    )
    website = _sanitize_json_fill_website(
        _s(info.get("official_website")) or _s(place_url)
    )
    address = _sanitize_json_fill_address(_s(info.get("full_address")), snippet)
    region = _s(info.get("bundesland")) or _s(info.get("discovery_bundesland"))
    if not region:
        region = region_to_internal(address) or region_to_internal(snippet)
    line = (
        _s(info.get("kategoria"))
        or _s(info.get("line_of_business"))
        or _s(info.get("retail_chains_found"))
        or _line_of_business_from_snippet(snippet)
    )
    nip = normalize_pl_nip(_s(info.get("nip") or info.get("tax_id")))
    if not nip:
        nip = extract_pl_nip_from_text(snippet)
    postcode = extract_pl_postcode(
        _s(info.get("kod_pocztowy") or info.get("postcode")),
        address,
        snippet,
    )
    return {
        "name": name,
        "line": line,
        "website": website,
        "email": first_email_from_contact(info),
        "phone": first_phone_from_contact(info),
        "region": region,
        "address": address,
        "postcode": postcode,
        "nip": nip,
        "url": _s(place_url) or website,
    }


def json_contact_has_needed_data(place_url: str, info: Any) -> bool:
    """Przepuszcza rekord JSON, jesli ma choć jedno użyteczne pole (bez śmieci)."""
    if not isinstance(info, dict):
        return False
    url = _s(place_url) or _s(info.get("official_website"))
    if not url or not _sanitize_json_fill_website(url):
        return False
    fields = json_fill_fields(place_url, info)
    return any(
        fields[key]
        for key in ("name", "email", "phone", "address", "nip", "line", "region")
    )


def contact_richness(info: dict) -> int:
    if not isinstance(info, dict):
        return 0
    score = 0
    for key in (
        "company_name_clean",
        "company_name",
        "email_target",
        "emails_found",
        "phones_found",
        "full_address",
        "official_website",
        "bundesland",
        "email_status",
        "retail_chains_found",
        "nip",
        "kategoria",
    ):
        if _s(info.get(key)):
            score += 2 if key in {"email_target", "emails_found", "phones_found"} else 1
    if info.get("retail_verified"):
        score += 1
    return score


def merge_contact_info(base: dict, incoming: dict) -> dict:
    out = dict(base or {})
    for key, val in (incoming or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = merge_contact_info(out[key], val)
            continue
        if val in (None, "", [], {}):
            continue
        cur = out.get(key)
        if cur in (None, "", [], {}):
            out[key] = val
            continue
        if isinstance(val, str) and isinstance(cur, str) and len(val) > len(cur):
            out[key] = val
        elif isinstance(val, bool) and val and not cur:
            out[key] = val
        elif isinstance(val, (int, float)) and isinstance(cur, (int, float)) and val > cur:
            out[key] = val
    return out


def merge_contacts_maps(*maps: dict) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for blob in maps:
        if not isinstance(blob, dict):
            continue
        for url, info in blob.items():
            key = _s(url)
            if not key or not isinstance(info, dict):
                continue
            if key not in merged:
                merged[key] = dict(info)
            elif contact_richness(info) >= contact_richness(merged[key]):
                merged[key] = merge_contact_info(merged[key], info)
            else:
                merged[key] = merge_contact_info(info, merged[key])
    return merged


def pipeline_row_from_json(place_url: str, info: dict) -> dict:
    name = (
        _s(info.get("company_name_clean"))
        or _s(info.get("company_name"))
        or _s(info.get("company_name_raw"))
    )
    email = first_email_from_contact(info)
    phone = first_phone_from_contact(info)
    website = _s(info.get("official_website")) or _s(place_url)
    return {
        "url": _s(place_url) or website,
        "www": website,
        "official_website": website,
        "nazwa": name,
        "company_name_clean": name,
        "company_name_raw": _s(info.get("company_name_raw")) or name,
        "email_target": email,
        "emails_found": _s(info.get("emails_found")),
        "telefon": phone,
        "phones_found": _s(info.get("phones_found")) or phone,
        "full_address": _s(info.get("full_address")),
        "adres": _s(info.get("full_address")),
        "bundesland": _s(info.get("bundesland")) or _s(info.get("discovery_bundesland")),
        "retail_verified": bool(info.get("retail_verified")),
        "verification_reason": _s(info.get("verification_reason")),
        "page_snippet": _s(info.get("page_snippet")),
        "retail_chains_found": _s(info.get("retail_chains_found")),
        "is_gu": bool(info.get("is_gu")),
        "is_small_firm": info.get("is_small_firm", True),
        "gu_marker": _s(info.get("gu_marker")),
        "email_status": _s(info.get("email_status")),
        "contact_sources": _s(info.get("contact_sources")),
        "contact_quality_score": int(info.get("contact_quality_score", 0) or 0),
        "nip": _s(info.get("nip") or info.get("tax_id")),
        "kod_pocztowy": _s(info.get("kod_pocztowy") or info.get("postcode")),
        "kategoria": _s(info.get("kategoria") or info.get("line_of_business")),
        "line_of_business": _s(info.get("line_of_business") or info.get("kategoria")),
    }


def excel_row_from_json(place_url: str, info: dict) -> dict:
    from cn_excel_en import (
        line_of_business_to_english,
        localisation_to_english,
        region_to_english,
    )

    fields = json_fill_fields(place_url, info)
    return {
        "Name of Company": fields["name"],
        "Line of business": line_of_business_to_english(fields["line"]),
        "Company website": fields["website"],
        "E-Mail": fields["email"],
        "Phone number": fields["phone"],
        "Region": region_to_english(fields["region"]),
        "Localisation": localisation_to_english(fields["address"]),
        "Postcode": fields["postcode"],
        "Tax Identification Number": fields["nip"],
        "URL": fields["url"],
    }


def index_excel_by_url(export_rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for rec in export_rows:
        for key in (
            rec.get("URL"),
            rec.get("Company website"),
            rec.get("Strona www"),
            rec.get("Webseite"),
        ):
            url = _s(key)
            if url and url not in out:
                out[url] = rec
    return out


def json_field_for_excel_col(info: dict, col: str, place_url: str) -> str:
    from cn_excel_en import (
        line_of_business_to_english,
        localisation_to_english,
        region_to_english,
    )

    fields = json_fill_fields(place_url, info)
    mapping = {
        "Name of Company": fields["name"],
        "Nazwa firmy": fields["name"],
        "Line of business": line_of_business_to_english(fields["line"]),
        "Kategorie_materialow": line_of_business_to_english(fields["line"]),
        "Company website": fields["website"],
        "Strona www": fields["website"],
        "Webseite": fields["website"],
        "E-Mail": fields["email"],
        "E-mail": fields["email"],
        "Phone number": fields["phone"],
        "Telefon": fields["phone"],
        "Region": region_to_english(fields["region"]),
        "Prowincja": region_to_english(fields["region"]),
        "Localisation": localisation_to_english(fields["address"]),
        "Adres": localisation_to_english(fields["address"]),
        "Postcode": fields["postcode"],
        "Postal code": fields["postcode"],
        "Kod pocztowy": fields["postcode"],
        "Tax Identification Number": fields["nip"],
        "URL": fields["url"],
        "Status": _s(info.get("email_status")),
    }
    return mapping.get(col, "")


def find_excel_gaps(contacts: dict[str, dict], export_rows: list[dict]) -> list[dict]:
    """Luki: brak wiersza albo pusta kolumna Excela przy niepustym polu JSON."""
    by_url = index_excel_by_url(export_rows)
    gaps: list[dict] = []
    for place_url, info in contacts.items():
        if not json_contact_has_needed_data(place_url, info):
            continue
        rec = by_url.get(_s(place_url))
        if rec is None:
            gaps.append({"url": _s(place_url), "reason": "missing_row", "columns": ["*"]})
            continue
        missing_cols = []
        for col in EXCEL_REQUIRED_IF_JSON_HAS:
            json_val = json_field_for_excel_col(info, col, place_url)
            excel_val = _s(rec.get(col))
            if json_val and not excel_val:
                missing_cols.append(col)
        if missing_cols:
            gaps.append(
                {"url": _s(place_url), "reason": "empty_columns", "columns": missing_cols}
            )
    return gaps


def fill_export_from_json(contacts: dict[str, dict], export_rows: list[dict]) -> tuple[list[dict], int]:
    """Uzupelnia Excel danymi z JSON. Zwraca (wiersze, liczba zmian)."""
    by_url = index_excel_by_url(export_rows)
    changed = 0
    for place_url, info in contacts.items():
        if not json_contact_has_needed_data(place_url, info):
            continue
        url = _s(place_url)
        rec = by_url.get(url)
        if rec is None:
            rec = excel_row_from_json(place_url, info)
            export_rows.append(rec)
            by_url[url] = rec
            changed += 1
            continue
        filled = excel_row_from_json(place_url, info)
        for col, val in filled.items():
            if _s(val) and not _s(rec.get(col)):
                rec[col] = val
                changed += 1
    from cn_contact_fields import extract_pl_postcode

    for rec in export_rows:
        if _s(rec.get("Postcode")):
            continue
        postcode = extract_pl_postcode(
            rec.get("Localisation"),
            rec.get("Adres"),
        )
        if postcode:
            rec["Postcode"] = postcode
            changed += 1
    return export_rows, changed


def verify_and_fill_until_complete(
    contacts: dict[str, dict],
    export_rows: list[dict],
    *,
    max_rounds: int = 5,
) -> tuple[list[dict], list[dict], int]:
    """Petla: weryfikacja calego Excela → JSON → uzupelnienie."""
    rounds = 0
    gaps = find_excel_gaps(contacts, export_rows)
    while gaps and rounds < max_rounds:
        export_rows, _n = fill_export_from_json(contacts, export_rows)
        rounds += 1
        gaps = find_excel_gaps(contacts, export_rows)
    return export_rows, gaps, rounds
