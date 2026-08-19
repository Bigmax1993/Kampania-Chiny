# -*- coding: utf-8 -*-
"""Prompty Claude — kampania CN: polscy dystrybutorzy / importerzy (dla chińskich eksporterów)."""
from __future__ import annotations

import re

from cn_campaign_keyword_profile import (
    gu_required_keywords_sample,
    large_company_markers_sample,
    negative_keywords_sample,
    retail_chain_keywords_sample,
    retail_context_keywords_sample,
    small_company_markers_sample,
)

_REQUIRED_MATERIALS = (
    "płytki, ceramika, armatura, LED, SPC, profile aluminiowe, chemia budowlana, "
    "okna PVC, stal (konstrukcyjna, nierdzewna, ocynkowana, blachy, rury, profile, pręty), "
    "drzwi, kabiny prysznicowe, instalacje sanitarne, armatura łazienkowa, sanitariat"
)
PAGE_VERIFY_MAX_CHARS = 18000
CONTACT_EXTRACT_MAX_CHARS = 16000
_CONTACT_EXTRACT_TEXT_PRIORITY = (
    "kontakt",
    "contact",
    "mailto",
    "@",
    "telefon",
    "phone",
    "email",
    "e-mail",
    "nip",
    "adres",
)
_PAGE_VERIFY_TEXT_PRIORITY = (
    "dystrybutor",
    "importer",
    "wyłączny dystrybutor",
    "oficjalny dystrybutor",
    "autoryzowany",
    "przedstawiciel",
    "hurt",
    "dystrybucja",
    "import",
    "płytki",
    "ceramika",
    "armatura",
    "led",
    "spc",
    "aluminium",
    "pvc",
    "stal",
    "drzwi",
    "kabin",
    "prysznic",
    "sanitarn",
    "łazienk",
    "hydrau",
    "katalog",
    "cennik",
)


def prioritize_page_text_for_verify(
    page_text: str,
    *,
    max_chars: int = PAGE_VERIFY_MAX_CHARS,
    priority_keywords: tuple[str, ...] | None = None,
) -> str:
    keys = priority_keywords or _PAGE_VERIFY_TEXT_PRIORITY
    raw = (page_text or "").strip()
    if len(raw) <= max_chars:
        return raw
    if "=== http" in raw:
        sections = re.split(r"(?=\n=== https?://)", "\n" + raw)
        sections = [s.strip() for s in sections if s.strip()]
        priority_sec: list[str] = []
        other_sec: list[str] = []
        for sec in sections:
            low = sec.lower()
            if any(k in low for k in keys):
                priority_sec.append(sec)
            else:
                other_sec.append(sec)
        merged = "\n\n".join(priority_sec + other_sec)
    else:
        lines = [ln.strip() for ln in re.split(r"[\n\r]+", raw) if ln.strip()]
        if not lines:
            return raw[:max_chars]
        priority: list[str] = []
        other: list[str] = []
        for ln in lines:
            low = ln.lower()
            if any(k in low for k in keys):
                priority.append(ln)
            else:
                other.append(ln)
        merged = " ".join(priority + other)
    if len(merged) <= max_chars:
        return merged
    return merged[: max_chars - 3] + "..."


def build_page_verify_prompt(
    company_name: str,
    website: str,
    page_text: str,
    *,
    max_chars: int = PAGE_VERIFY_MAX_CHARS,
    serper_blob: str = "",
    pages_crawled: int = 0,
) -> str:
    from claude_page_text import (
        build_automatic_evidence_excerpt,
        build_claude_context_header,
        extract_crawl_section_urls,
    )

    raw = page_text or ""
    priority_urls = extract_crawl_section_urls(raw)
    header = build_claude_context_header(
        company_name,
        website,
        serper_blob=serper_blob,
        pages_crawled=pages_crawled or max(raw.count("=== http"), 1 if raw else 0),
        priority_urls=priority_urls,
    )
    evidence = build_automatic_evidence_excerpt(raw)
    snippet = prioritize_page_text_for_verify(raw, max_chars=max_chars)
    supplier_kw = ", ".join(gu_required_keywords_sample())
    material_kw = ", ".join(retail_context_keywords_sample())
    category_kw = ", ".join(retail_chain_keywords_sample())
    neg_kw = ", ".join(negative_keywords_sample())
    small_kw = ", ".join(small_company_markers_sample())
    large_kw = ", ".join(large_company_markers_sample())
    return f"""ROLA
Jesteś analitykiem B2B. Szukasz WYŁĄCZNIE polskich firm, które są dystrybutorem / importerem / wyłącznym lub oficjalnym dystrybutorem materiałów budowlanych NA TERENIE POLSKI (kategorie eksportowe z Chin: płytki, ceramika, armatura, LED, SPC, aluminium, chemia, okna PVC, stal, drzwi, kabiny prysznicowe, instalacje sanitarne).

CEL (is_gu=true) — muszą być spełnione JEDNOCZEŚNIE:
1) Rola handlowa: importer, dystrybutor, wyłączny dystrybutor, oficjalny/autoryzowany dystrybutor, przedstawiciel, hurt B2B (nie sam wykonawca robót i nie sam sklep detaliczny).
2) Asortyment materiałów budowlanych (np. {_REQUIRED_MATERIALS}).
3) Działalność w POLSCE (adres, województwo, domena .pl, +48, NIP).

NIE CEL (is_gu=false):
• Sklep wyłącznie detaliczny (Castorama C2C, OLX, Allegro ogłoszenia) bez dystrybucji/importu → primary_role="Sklep detaliczny" lub "Ogłoszenie"
• Wykonawca / wykończenia wnętrz bez sprzedaży materiałów → primary_role="Wykonawca bez sprzedaży"
• Portale, media, urzędy, banki, oferty pracy
• Firma spoza Polski → dodaj "poza polską" do matched_negative_keywords

ZADANIE
Przeczytaj wyciąg ze strony (podstrony «=== URL ===»).
Czy to polski dystrybutor / importer materiałów budowlanych? Odpowiedz TYLKO JSON — bez markdown.

CO JEST DOWODEM (is_gu=true)
• Fraza roli: importer, dystrybutor, wyłączny dystrybutor, oficjalny dystrybutor, autoryzowany dystrybutor, przedstawiciel, hurt, dystrybucja, import
• Oferta handlowa: katalog, cennik, asortyment, dystrybucja, import
• Kategorie: {_REQUIRED_MATERIALS}

ODRZUĆ (is_gu=false)
• Tylko detal / ogłoszenie / marketplace bez dystrybucji i importu
• Wykończenia, remont pod klucz, biuro architektoniczne
• Firma bez działalności w Polsce

POLA JSON (klucze bez zmian — pipeline)
• is_gu = true TYLKO jeśli dystrybutor/importer B2B materiałów w Polsce
• has_retail_context = true jeśli jest katalog / cennik / asortyment
• matched_gu_keywords = frazy roli ze strony (polski)
• matched_retail_keywords = frazy oferty (katalog, cennik, …)
• matched_chains = kategorie materiałów z tekstu (płytki, LED, …) — tylko wymienione
• matched_negative_keywords = negatywy; dodaj "poza polską" gdy firma nie działa w Polsce
• is_small_firm = lokalny dystrybutor / importer (nie wielka sieć DIY)
• primary_role = jedna z: Importer, Dystrybutor, Wyłączny dystrybutor, Oficjalny dystrybutor, Hurtownia, Sklep detaliczny, Producent, Wykonawca bez sprzedaży, Media, Portal, Ogłoszenie, Inne
• reason = krótkie uzasadnienie po polsku

MAŁE OZNAKI: {small_kw}
DUŻE OZNAKI (is_small_firm=false): {large_kw}

SŁOWA KLUCZOWE ROLI: {supplier_kw}
KONTEKST OFERTY: {material_kw}
KATEGORIE: {category_kw}
NEGATYW: {neg_kw}

SCHEMA JSON
{{
  "matched_gu_keywords": [],
  "matched_retail_keywords": [],
  "matched_chains": [],
  "matched_negative_keywords": [],
  "is_gu": false,
  "has_retail_context": false,
  "is_small_firm": false,
  "primary_role": "",
  "reason": ""
}}

KONTEKST
{header}

AUTODOWODY
{evidence}

WYCIĄG ZE STRONY
{snippet or "(pusto)"}
"""


def build_row_cleanup_prompt(
    *,
    company: str,
    address: str,
    phone: str,
    email: str,
    website: str,
    states: str,
    handelsketten: str = "",
    url: str = "",
) -> str:
    return f"""ROLA
Przygotowujesz wiersz Excel dla bazy B2B polskich dystrybutorów / importerów materiałów budowlanych (produkt dla chińskich eksporterów).
Odpowiedz WYŁĄCZNIE JSON.

SCHEMAT
{{"company_name_clean":"","address":"","phone":"","website":"","bundesland":"","handelsketten":"","url":""}}

ZASADY
• company_name_clean — oficjalna nazwa (Sp. z o.o. / S.A.) z pieczęci/kontaktu; NIE tytuł SEO, NIE „Kontakt”; jeśli brak pewności — ""
• address — WYŁĄCZNIE fizyczny adres w Polsce; NIE slogan; jeśli brak — ""
• phone — jeden numer PL (+48) albo ""
• website — https://domena (korzeń) albo ""
• bundesland — jedno z województw: [{states}] albo ""
• handelsketten — kategorie (płytki, stal, drzwi, kabiny prysznicowe, instalacje sanitarne, …) przez przecinek albo ""
• url — jak website

WEJŚCIE
company={company!r}
address={address!r}
phone={phone!r}
email={email!r}
website={website!r}
handelsketten={handelsketten!r}
url={url!r}
"""


def build_personalized_inquiry_email_prompt_zh(
    *,
    company_name: str,
    website: str = "",
    wojewodztwo: str = "",
    address: str = "",
    materials: str = "",
    page_snippet: str = "",
    style_hint: str = "",
    discovery_wojewodztwo: str = "",
    construction_project=None,
) -> str:
    from cn_materialy_inquiry_email_zh import (
        inquiry_sender_name,
    )
    from cn_regional_sender_context import (
        build_regional_sender_instructions_pl,
        resolve_discovery_wojewodztwo,
    )
    from cn_regional_construction_refs import (
        build_construction_project_prompt_block_pl,
        pick_construction_project,
    )

    snippet = (page_snippet or "").strip()
    if len(snippet) > 3500:
        snippet = snippet[:3497] + "..."
    style = (style_hint or "profesjonalny, naturalny styl B2B, bez szablonowych fraz").strip()
    mats = materials or (
        "materiały budowlane (płytki, ceramika, armatura, LED, SPC, aluminium, chemia, "
        "okna PVC, stal, drzwi, kabiny prysznicowe, instalacje sanitarne)"
    )
    region_key = resolve_discovery_wojewodztwo(
        {"bundesland": wojewodztwo, "discovery_bundesland": discovery_wojewodztwo},
        fallback=wojewodztwo or discovery_wojewodztwo,
    )
    project = construction_project or pick_construction_project(
        region_key, seed=company_name or wojewodztwo or discovery_wojewodztwo
    )
    project_block = build_construction_project_prompt_block_pl(project)
    regional_sender = build_regional_sender_instructions_pl(
        region_key,
        sender_name=inquiry_sender_name(),
        sender_phone="",
        construction_project_block=project_block,
    )
    return f"""ROLA
Jesteś autorem listów B2B po polsku. Piszesz UNIKALNE zapytanie od chińskiego producenta/eksportera do KONKRETNEJ polskiej firmy (importer / dystrybutor / wyłączny dystrybutor).
Każdy list ma inne sformułowania — nie kopiuj jednego szablonu.

{regional_sender}

ODBIORCA (polski dystrybutor / importer na terenie Polski)
Nazwa: {company_name}
Strona: {website or "(brak)"}
Województwo odbiorcy: {wojewodztwo or "(nieznane)"}
Adres odbiorcy: {address or "(brak)"}
Kategorie (z bazy): {mats}

FRAGMENT STRONY (personalizacja — ich asortyment, dystrybucja, import):
{snippet or "(brak wyciągu — użyj nazwy firmy, województwa i kategorii z bazy; NIE pisz listu-szablonu)"}

ZADANIE
Napisz spersonalizowane zapytanie o współpracę dystrybucyjną — TYLKO do tej jednej firmy.
• Język: WYŁĄCZNIE polski.
• W treści MUSI pojawić się nazwa odbiorcy: «{company_name}» (nie „Państwa firma” zamiast nazwy).
• W pierwszym akapicie MUSI być konkret z FRAGMENTU STRONY albo z kategorii/miasta tej firmy (asortyment, importer/dystrybutor, miasto). Nie pisz ogólnika, który pasowałby do dowolnej hurtowni.
• Zwrot: «Szanowni Państwo,» albo do {company_name}.
• Wspomnij WYŁĄCZNIE obiekt z «OBIEKT BUDOWY» — inwestycja w POLSCE (nazwa + adres dosłownie), jako przykład zapotrzebowania.
• Przedstaw chińskiego producenta/eksportera szukającego dystrybutora (ew. wyłącznego) na terenie Polski — w kontekście TEJ firmy (ich kategoria / region).
• Poproś o: kontakt do osoby odpowiedzialnej za import/dystrybucję, warunki współpracy, ewentualny katalog.
• Nie wymyślaj cen, rabatów, MOQ, których nie ma we wejściu.
• Styl: {style}
• Długość: 140–240 słów (bez podpisu).

FORMAT LISTU (body — plain text, puste linie między blokami)
Obowiązkowa struktura — \\n\\n między blokami:
1) Zwrot, np. «Szanowni Państwo,»
2) Pusta linia
3) 2–3 akapity (każdy blok przez \\n\\n) — unikalne dla {company_name}
4) Pusta linia
5) «Z poważaniem,»
6) {inquiry_sender_name()}
7) Import / współpraca dystrybucyjna

Przykład to TYLKO układ (\\n\\n). NIE kopiuj tych zdań — wstaw fakty tej firmy:
"body":"Szanowni Państwo,\\n\\n[akapit z nazwą {company_name} i ich asortymentem]\\n\\n[akapit z obiektem budowy + prośba o kontakt]\\n\\nZ poważaniem,\\n{inquiry_sender_name()}"

ZAKAZANE
• Numer telefonu i strona www nadawcy
• Telefony +380 / +49
• gratis, promocja, kliknij, darmowy
• Ten sam tekst dla różnych firm; szablon bez nazwy odbiorcy
• List, który pasowałby 1:1 do innej firmy po zmianie nazwy
• Załączniki, HTML, markdown
• Udawanie polskiej firmy budowlanej albo fikcyjnego „Budownictwo XYZ”
• Inny adres budowy niż z «OBIEKT BUDOWY»

WYJŚCIE — TYLKO JSON (bez markdown):
{{"subject":"...","body":"..."}}

subject: do 78 znaków, po polsku; unikalny — nazwa firmy albo miasto + kategoria (np. współpraca dystrybucyjna / {company_name})
body: pełny list (plain text, akapity \\n\\n) z podpisem; nazwa {company_name} w treści
"""


def build_reminder_email_prompt_pl(
    *,
    company_name: str,
    original_subject: str = "",
    sent_date: str = "",
    original_body_excerpt: str = "",
    reminder_number: int = 1,
) -> str:
    excerpt = (original_body_excerpt or "").strip()
    if len(excerpt) > 1200:
        excerpt = excerpt[:1197] + "..."
    tone = (
        "delikatne, uprzejme przypomnienie (pierwsze)"
        if reminder_number < 2
        else "stanowcze, ale kulturalne drugie przypomnienie"
    )
    date_line = f"Data pierwszego maila: {sent_date}." if sent_date else ""
    subj_line = f"Temat pierwszego maila: {original_subject}." if original_subject else ""
    return f"""ROLA
Piszesz krótki, NATURALNY follow-up po polsku do dystrybutora/importera, który nie odpowiedział.

ODBIORCA
Firma: {company_name}
{date_line}
{subj_line}

KONTEKST (pierwszy list — NIE wklejaj ponownie):
{excerpt or "(brak — odwołaj się do współpracy dystrybucyjnej / importu)"}

ZADANIE
Napisz WYŁĄCZNIE tekst przypomnienia (bez podpisu, bez cytatu).
• Ton: {tone}
• 2–3 krótkie akapity (\\n\\n)
• Zacznij od «Dzień dobry,» albo zwrotu do {company_name}
• Krótko: czekasz na kontakt w sprawie dystrybucji / importu z Chin
• 50–110 słów
• NIE powtarzaj długiej listy produktów

ZAKAZANE
• Podpis, telefon, linki, HTML, markdown
• pilne, ostatnia szansa, natychmiast, gratis
• Ściana tekstu bez akapitów

WYJŚCIE — TYLKO JSON (bez markdown):
{{"intro":"..."}}

intro: tylko treść przypomnienia (plain text)
"""


def build_custom_email_prompt_uk(
    draft: str,
    company_name: str,
    *,
    city_name: str = "",
    delivery_address: str = "",
) -> str:
    ctx_city = f"Region: {city_name}. " if city_name else ""
    ctx_addr = f"Adres dostawy (bez zmian): {delivery_address}. " if delivery_address else ""
    return f"""ROLA
Jesteś redaktorem listów B2B po polsku. Minimalnie dostosuj szablon do konkretnej firmy.

ODBIORCA
{company_name}
{ctx_city}{ctx_addr}

ZADANIE
Dostosuj szablon (1–2 zdania kontekstu o firmie). Zachowaj WSZYSTKIE fakty: wolumeny, adresy, telefony, podpis.

ZAKAZANE
• Wymyślone ceny
• gratis, promocja, pilne
• Zmiana podpisu

WYJŚCIE (tylko JSON)
{{"subject":"...","body":"..."}}

SZABLON
{draft}
"""
