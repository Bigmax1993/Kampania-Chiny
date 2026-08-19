# -*- coding: utf-8 -*-
"""
Tekst maila — zapytanie o współpracę dystrybucyjną do polskich importerów/dystrybutorów
(produkt dla chińskich eksporterów). Maile bez telefonu i bez strony www.
"""
from __future__ import annotations

import re

_UA_PHONE_INLINE_RE = re.compile(
    r"(?:\+380|00380)\s*[\d\s()./-]{5,}\d",
    re.IGNORECASE,
)
_FOREIGN_TEL_LINE_RE = re.compile(
    r"^\s*(?:tel\.?|telefon|phone)\s*[.:]?\s*(?:\+380|00380|\+49|0049)[\d\s()./-]*\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_LEGACY_BRANDING_RE = re.compile(
    r"\b(?:mfg|moderner\s*fliesen\w*|fliesenboden|gmbh)\b",
    re.IGNORECASE,
)


def is_foreign_campaign_phone(phone: str) -> bool:
    raw = (phone or "").strip()
    if not raw:
        return False
    low = raw.lower().replace(" ", "")
    if low.startswith("+380") or low.startswith("00380"):
        return True
    if low.startswith("+49") or low.startswith("0049"):
        return True
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("380") and len(digits) >= 11:
        return True
    return digits.startswith("49") and len(digits) >= 11


def strip_foreign_phones_from_text(text: str) -> str:
    if not text:
        return ""
    out = _FOREIGN_TEL_LINE_RE.sub("", text)
    out = _UA_PHONE_INLINE_RE.sub("", out)
    out = re.sub(r"\b(?:tel\.?|telefon|phone)\s*[.:]?\s*(?=\s|$)", "", out, flags=re.IGNORECASE)
    out = re.sub(r"[ \t]+,", ",", out)
    out = re.sub(r",\s*,", ",", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip(" ,\n")


def strip_legacy_branding(text: str) -> str:
    if not text:
        return ""
    out = strip_foreign_phones_from_text(text)
    out = _LEGACY_BRANDING_RE.sub("", out)
    out = re.sub(r"\s+", " ", out).strip(" ,;-")
    return out


def _clean_sender_display_name(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    text = re.sub(r"\b(tel|telefon|phone)\b.*$", "", text, flags=re.IGNORECASE).strip()
    text = strip_foreign_phones_from_text(text)
    text = re.sub(r"https?://\S+|\bwww\.\S+|\S+@\S+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\+?\d[\d\s()./-]{5,}\d", "", text).strip()
    text = strip_legacy_branding(text)
    return re.sub(r"\s+", " ", text).strip(" ,;-")


DEFAULT_INQUIRY_SENDER_NAME_CN = "Maksym Swinczak"
DEFAULT_INQUIRY_PHONE_CN = "516513965"
DEFAULT_INQUIRY_WEBSITE_CN = ""
_CAMPAIGN_PHONE_RE = re.compile(
    r"(?:tel\.?\s*:?\s*)?(?:\+48\s*)?516[\s.\-/]*513[\s.\-/]*965\b",
    re.IGNORECASE,
)
_CAMPAIGN_WEB_RE = re.compile(
    r"https?://(?:www\.)?swinczakdata\.pl\S*|www\.swinczakdata\.pl\S*",
    re.IGNORECASE,
)


def inquiry_sender_name() -> str:
    from scraper_env import get_mail_sender_name, normalize_mail_sender_name

    cleaned = _clean_sender_display_name(get_mail_sender_name() or "")
    cleaned = normalize_mail_sender_name(cleaned)
    if not cleaned or any(x in cleaned.lower() for x in ("свінчак", "свинчак", "mfg", "fliesen")):
        return DEFAULT_INQUIRY_SENDER_NAME_CN
    return cleaned


def inquiry_company_name() -> str:
    from scraper_env import get_env_value

    return strip_legacy_branding(get_env_value("INQUIRY_COMPANY_NAME").strip())


def inquiry_phone() -> str:
    from scraper_env import get_env_value

    phone = get_env_value("INQUIRY_PHONE").strip()
    if phone and not is_foreign_campaign_phone(phone):
        return phone
    return DEFAULT_INQUIRY_PHONE_CN


def inquiry_website() -> str:
    from scraper_env import get_env_value

    # Kampania CN: celowo bez strony w mailu (nawet jeśli env ma URL).
    _ = get_env_value("INQUIRY_WEBSITE").strip()
    return DEFAULT_INQUIRY_WEBSITE_CN


def strip_campaign_contact_from_text(text: str) -> str:
    """Usuwa numer i stronę kampanii, jeśli model je dokleił."""
    if not text:
        return ""
    out = _CAMPAIGN_WEB_RE.sub("", text)
    out = _CAMPAIGN_PHONE_RE.sub("", out)
    lines = [re.sub(r"[ \t]+", " ", ln).strip(" ,;") for ln in out.splitlines()]
    out = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def build_inquiry_signature_zh() -> str:
    lines = ["Z poważaniem,", ""]
    name = inquiry_sender_name()
    if name:
        lines.append(name)
    company = inquiry_company_name()
    if company:
        lines.extend(["", company])
    return "\n".join(lines).strip()


def body_has_inquiry_signature(body: str) -> bool:
    low = (body or "").lower()
    if "此致敬礼" not in (body or "") and "z poważaniem" not in low:
        return False
    name = inquiry_sender_name().strip()
    if not name:
        return False
    first = name.split()[0].lower()
    tail = low[-500:]
    return first in tail


def dedupe_inquiry_signature(body: str) -> str:
    text = (body or "").strip()
    if not text:
        return text
    name = inquiry_sender_name().strip()
    if not name:
        return text
    search_from = max(0, len(text) - 800)
    region = text[search_from:]
    matches = list(re.finditer(r"此致敬礼|z poważaniem", region, flags=re.IGNORECASE))
    if len(matches) < 2:
        return text
    main = text[: search_from + matches[0].start()].rstrip()
    last_sig = text[search_from + matches[-1].start() :].strip()
    return f"{main}\n\n{last_sig}".strip()


def ensure_inquiry_signature(body: str) -> str:
    text = dedupe_inquiry_signature((body or "").strip())
    if body_has_inquiry_signature(text):
        return text
    signature = build_inquiry_signature_zh()
    if not signature:
        return text
    return text.rstrip() + "\n\n" + signature


_SALUTATION_PREFIX_RE = re.compile(
    r"^(尊敬的[^，,\n]{0,30}[：:，,]?|Szanowni Państwo,?)\s*",
    re.IGNORECASE,
)
_SIGNATURE_MARKER_RE = re.compile(r"(此致敬礼,?)|\b(Z poważaniem,?)\b", re.IGNORECASE)
_TEL_LINE_RE = re.compile(
    r"\b(?:Tel\.?|Telefon):?\s*(?:\+48)?[\d\s()./-]{7,}",
    re.IGNORECASE,
)
_WEB_INLINE_RE = re.compile(r"(?:https?://\S+|www\.\S+)", re.IGNORECASE)


def format_inquiry_email_body_pl(body: str) -> str:
    """Układa treść maila: akapity, odstępy między blokami, czytelny podpis."""
    if not body:
        return ""
    text = body.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = strip_campaign_contact_from_text(text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if "\n" not in text:
        text = _format_dense_inquiry_body_pl(text)
    else:
        text = _ensure_salutation_spacing_pl(text)
        text = _ensure_signature_spacing_pl(text)
        text = _normalize_signature_lines_pl(text)

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def _ensure_salutation_spacing_pl(text: str) -> str:
    match = _SALUTATION_PREFIX_RE.match(text)
    if not match:
        return text
    salutation = match.group(1).rstrip(",") + ","
    rest = text[match.end() :].lstrip()
    if rest.startswith("\n\n"):
        return text
    if rest.startswith("\n"):
        return f"{salutation}\n{rest.lstrip()}"
    return f"{salutation}\n\n{rest}"


def _ensure_signature_spacing_pl(text: str) -> str:
    match = _SIGNATURE_MARKER_RE.search(text)
    if not match:
        return text
    before = text[: match.start()].rstrip()
    after = text[match.start() :].lstrip()
    if before.endswith("\n\n") or not before:
        return text
    return f"{before}\n\n{after}"


def _format_dense_inquiry_body_pl(text: str) -> str:
    match = _SIGNATURE_MARKER_RE.search(text)
    if match:
        main = text[: match.start()].strip()
        signature = _normalize_signature_lines_pl(text[match.start() :].strip())
        main = _ensure_salutation_spacing_pl(main)
        return f"{main.rstrip()}\n\n{signature}"
    return _ensure_salutation_spacing_pl(text)


def _normalize_signature_lines_pl(text: str) -> str:
    match = _SIGNATURE_MARKER_RE.search(text)
    if not match:
        return text
    before = text[: match.start()].rstrip()
    marker = match.group(1)
    if not marker.endswith(","):
        marker = marker + ","
    rest = text[match.end() :].strip()
    if not rest:
        signature = marker
    else:
        tel_match = _TEL_LINE_RE.search(rest)
        tel = tel_match.group(0).strip() if tel_match else ""
        if tel_match:
            rest = (rest[: tel_match.start()] + rest[tel_match.end() :]).strip(" ,;")

        web_match = _WEB_INLINE_RE.search(rest)
        web = web_match.group(0).strip() if web_match else ""
        if web_match:
            rest = (rest[: web_match.start()] + rest[web_match.end() :]).strip(" ,;")

        name_lines = [ln.strip(" ,;") for ln in rest.splitlines() if ln.strip(" ,;")]
        parts = [marker]
        parts.extend(name_lines)
        signature = "\n".join(parts)
    if before:
        return f"{before}\n\n{signature}"
    return signature


def ensure_inquiry_contact_in_body(body: str) -> str:
    """
    Czyści telefon i stronę z podpisu. Nie dokleja numeru ani URL.
    """
    text = strip_campaign_contact_from_text(
        strip_legacy_branding_preserve_layout(
            strip_foreign_phones_from_text((body or "").strip())
        )
    )
    if not text:
        return build_inquiry_signature_zh()
    if re.search(r"此致敬礼|z\s+powa[zż]aniem", text, flags=re.IGNORECASE):
        return text
    return f"{text.rstrip()}\n\n{build_inquiry_signature_zh()}"


def strip_legacy_branding_preserve_layout(text: str) -> str:
    if not text:
        return ""
    out = strip_foreign_phones_from_text(text)
    out = _LEGACY_BRANDING_RE.sub("", out)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in out.splitlines()]
    out = "\n".join(lines).strip()
    return re.sub(r"\n{3,}", "\n\n", out)


def build_inquiry_sender_brief_pl() -> str:
    company = inquiry_company_name()
    who = company if company else "chiński producent / eksporter materiałów budowlanych"
    return (
        f"{who} — poszukujemy dystrybutora / importera na terenie Polski. "
        "Prosimy o kontakt w sprawie współpracy dystrybucyjnej."
    )


def build_sender_contact_line_pl() -> str:
    parts: list[str] = []
    name = inquiry_sender_name()
    if name:
        parts.append(name)
    company = inquiry_company_name()
    if company:
        parts.append(company)
    return strip_legacy_branding(", ".join(parts))


def build_fixed_material_inquiry_zh(company_name: str = "") -> str:
    who = (company_name or "").strip()
    intro = (
        "reprezentuję chińskiego producenta materiałów budowlanych i poszukujemy "
        "dystrybutora / importera na terenie Polski."
    )
    if inquiry_company_name():
        intro = (
            f"reprezentuję {inquiry_company_name()} — chińskiego eksportera materiałów "
            "budowlanych. Szukamy dystrybutora (w tym wyłącznego) na rynku polskim."
        )
    recipient = (
        f"Zwracam się do {who}."
        if who
        else "Zwracam się do Państwa jako do dystrybutora / importera."
    )
    return f"""Szanowni Państwo,

{recipient} {intro}

Interesuje nas współpraca w kategoriach: płytki, ceramika, armatura, oświetlenie LED, panele SPC, profile aluminiowe, chemia budowlana, okna PVC, stal (w tym konstrukcyjna, nierdzewna, ocynkowana, blachy, rury i profile), drzwi, kabiny prysznicowe oraz instalacje sanitarne do łazienki. Szukamy partnera, który importuje lub dystrybuuje takie asortymenty w Polsce.

Prosimy o kontakt do osoby odpowiedzialnej za import / dystrybucję albo o informację, czy rozważacie Państwo nową linię produktową z Chin.

Dziękujemy za odpowiedź.

{build_inquiry_signature_zh()}"""


FIXED_MATERIAL_INQUIRY_ZH = build_fixed_material_inquiry_zh()


def inquiry_email_signature_pl() -> str:
    return build_inquiry_signature_zh()


def inquiry_sender_brief_pl() -> str:
    return build_inquiry_sender_brief_pl()


INQUIRY_EMAIL_SIGNATURE_PL = build_inquiry_signature_zh()
INQUIRY_SENDER_BRIEF_PL = build_inquiry_sender_brief_pl()

# Aliasy kompatybilności ze scraperem (fork UA)
strip_de_campaign_branding = strip_legacy_branding
strip_german_phones_from_text = strip_foreign_phones_from_text
