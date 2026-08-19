# -*- coding: utf-8 -*-
"""
Excel export for CN campaign: English cell values, company names unchanged.
"""
from __future__ import annotations

import re
import unicodedata

REGION_EN: dict[str, str] = {
    "mazowieckie": "Masovian Voivodeship",
    "malopolskie": "Lesser Poland Voivodeship",
    "slaskie": "Silesian Voivodeship",
    "wielkopolskie": "Greater Poland Voivodeship",
    "dolnoslaskie": "Lower Silesian Voivodeship",
    "pomorskie": "Pomeranian Voivodeship",
    "lodzkie": "Lodz Voivodeship",
    "zachodniopomorskie": "West Pomeranian Voivodeship",
    "lubelskie": "Lublin Voivodeship",
    "podkarpackie": "Subcarpathian Voivodeship",
    "kujawsko-pomorskie": "Kuyavian-Pomeranian Voivodeship",
    "warminsko-mazurskie": "Warmian-Masurian Voivodeship",
    "swietokrzyskie": "Holy Cross Voivodeship",
    "podlaskie": "Podlaskie Voivodeship",
    "lubuskie": "Lubusz Voivodeship",
    "opolskie": "Opole Voivodeship",
}

_CITY_EN: tuple[tuple[str, str], ...] = (
    ("Zielona Góra", "Zielona Gora"),
    ("Gorzów Wielkopolski", "Gorzow Wielkopolski"),
    ("Jelenia Góra", "Jelenia Gora"),
    ("Biała Podlaska", "Biala Podlaska"),
    ("Bielsko-Biała", "Bielsko-Biala"),
    ("Nowy Sącz", "Nowy Sacz"),
    ("Starogard Gdański", "Starogard Gdanski"),
    ("Ostrowiec Świętokrzyski", "Ostrowiec Swietokrzyski"),
    ("Kędzierzyn-Koźle", "Kedzierzyn-Kozle"),
    ("Częstochowa", "Czestochowa"),
    ("Świnoujście", "Swinoujscie"),
    ("Piotrków Trybunalski", "Piotrkow Trybunalski"),
    ("Warszawa", "Warsaw"),
    ("Kraków", "Krakow"),
    ("Wrocław", "Wroclaw"),
    ("Gdańsk", "Gdansk"),
    ("Poznań", "Poznan"),
    ("Łódź", "Lodz"),
    ("Toruń", "Torun"),
    ("Rzeszów", "Rzeszow"),
    ("Białystok", "Bialystok"),
    ("Łomża", "Lomza"),
    ("Kielce", "Kielce"),
    ("Gdynia", "Gdynia"),
    ("Lublin", "Lublin"),
    ("Katowice", "Katowice"),
    ("Szczecin", "Szczecin"),
    ("Bydgoszcz", "Bydgoszcz"),
    ("Olsztyn", "Olsztyn"),
    ("Opole", "Opole"),
    ("Radom", "Radom"),
    ("Płock", "Plock"),
    ("Pruszków", "Pruszkow"),
    ("Oświęcim", "Oswiecim"),
    ("Gliwice", "Gliwice"),
    ("Zabrze", "Zabrze"),
    ("Wałbrzych", "Walbrzych"),
    ("Legnica", "Legnica"),
    ("Elbląg", "Elblag"),
    ("Ełk", "Elk"),
    ("Suwałki", "Suwalki"),
    ("Zamość", "Zamosc"),
    ("Chełm", "Chelm"),
    ("Przemyśl", "Przemysl"),
    ("Włocławek", "Wloclawek"),
    ("Grudziądz", "Grudziadz"),
    ("Kołobrzeg", "Kolobrzeg"),
    ("Świdnik", "Swidnik"),
    ("Żary", "Zary"),
    ("Nowa Sól", "Nowa Sol"),
    ("Kluczbork", "Kluczbork"),
    ("Nysa", "Nysa"),
    ("Brzeg", "Brzeg"),
)

# Longest phrases first.
_BUSINESS_PHRASES: tuple[tuple[str, str], ...] = (
    ("wyłączny dystrybutor", "exclusive distributor"),
    ("wylaczny dystrybutor", "exclusive distributor"),
    ("oficjalny dystrybutor", "official distributor"),
    ("autoryzowany dystrybutor", "authorized distributor"),
    ("wyłączny importer", "exclusive importer"),
    ("wylaczny importer", "exclusive importer"),
    ("oficjalny importer", "official importer"),
    ("chemia budowlana", "construction chemicals"),
    ("ceramika sanitarna", "sanitary ceramics"),
    ("ceramika łazienkowa", "bathroom ceramics"),
    ("ceramika lazienkowa", "bathroom ceramics"),
    ("instalacje sanitarne", "sanitary installations"),
    ("armatura łazienkowa", "bathroom fittings"),
    ("armatura lazienkowa", "bathroom fittings"),
    ("baterie łazienkowe", "bathroom taps"),
    ("baterie lazienkowe", "bathroom taps"),
    ("kabiny prysznicowe", "shower cabins"),
    ("kabina prysznicowa", "shower cabin"),
    ("drzwi prysznicowe", "shower doors"),
    ("stal konstrukcyjna", "structural steel"),
    ("stal nierdzewna", "stainless steel"),
    ("stal ocynkowana", "galvanized steel"),
    ("stal zbrojeniowa", "reinforcing steel"),
    ("kształtowniki stalowe", "steel sections"),
    ("ksztaltowniki stalowe", "steel sections"),
    ("blachy stalowe", "steel sheets"),
    ("blacha stalowa", "steel sheet"),
    ("rury stalowe", "steel pipes"),
    ("profile stalowe", "steel profiles"),
    ("pręty stalowe", "steel bars"),
    ("prety stalowe", "steel bars"),
    ("drzwi wewnętrzne", "interior doors"),
    ("drzwi wewnetrzne", "interior doors"),
    ("drzwi zewnętrzne", "exterior doors"),
    ("drzwi zewnetrzne", "exterior doors"),
    ("drzwi wejściowe", "entrance doors"),
    ("drzwi wejsciowe", "entrance doors"),
    ("drzwi aluminiowe", "aluminium doors"),
    ("drzwi stalowe", "steel doors"),
    ("drzwi drewniane", "wooden doors"),
    ("płytki ceramiczne", "ceramic tiles"),
    ("plytki ceramiczne", "ceramic tiles"),
    ("płytek ceramicznych", "ceramic tiles"),
    ("profile aluminiowe", "aluminium profiles"),
    ("oświetlenie LED", "LED lighting"),
    ("oswietlenie LED", "LED lighting"),
    ("oświetlenie led", "LED lighting"),
    ("panele SPC", "SPC flooring"),
    ("okna PVC", "PVC windows"),
    ("materiałów budowlanych", "building materials"),
    ("materialow budowlanych", "building materials"),
    ("materiały budowlane", "building materials"),
    ("materialy budowlane", "building materials"),
    ("skład budowlany", "builders merchant"),
    ("sklad budowlany", "builders merchant"),
    ("hurtownia", "wholesaler"),
    ("dystrybutor", "distributor"),
    ("dystrybucja", "distribution"),
    ("importer", "importer"),
    ("przedstawiciel", "representative"),
    ("sanitariat", "sanitary ware"),
    ("ościeżnice", "door frames"),
    ("oscieznice", "door frames"),
    ("brodziki", "shower trays"),
    ("umywalki", "washbasins"),
    ("hydraulika", "plumbing"),
    ("stelaże WC", "WC frames"),
    ("stelaze WC", "WC frames"),
    ("wanny", "bathtubs"),
    ("drzwi", "doors"),
    ("płytek", "tiles"),
    ("plytek", "tiles"),
    ("płytki", "tiles"),
    ("plytki", "tiles"),
    ("ceramiki", "ceramics"),
    ("ceramika", "ceramics"),
    ("armatury", "sanitary fittings"),
    ("armatura", "sanitary fittings"),
    ("aluminium", "aluminium"),
    ("chemia", "chemicals"),
    ("stal", "steel"),
    ("hurt", "wholesale"),
    ("import", "import"),
    ("agent", "agent"),
    ("katalog", "catalogue"),
    ("cennik", "price list"),
    ("asortyment", "assortment"),
    ("produkty", "products"),
    ("województwo", "voivodeship"),
    ("wojewodztwo", "voivodeship"),
)

_STREET_RES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bulica\b", re.IGNORECASE), "Street"),
    (re.compile(r"\bul\.\s*", re.IGNORECASE), "St. "),
    (re.compile(r"\baleje\b", re.IGNORECASE), "Avenue"),
    (re.compile(r"\baleja\b", re.IGNORECASE), "Avenue"),
    (re.compile(r"\bal\.\s*", re.IGNORECASE), "Ave. "),
    (re.compile(r"\bplac\b", re.IGNORECASE), "Square"),
    (re.compile(r"\bpl\.\s*", re.IGNORECASE), "Sq. "),
    (re.compile(r"\bosiedle\b", re.IGNORECASE), "Housing estate"),
    (re.compile(r"\bos\.\s*", re.IGNORECASE), ""),
)


def _fold(text: str) -> str:
    raw = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in raw if not unicodedata.combining(ch)).lower()


def _wojewodztwo_key(value: str) -> str:
    text = _fold(value or "").strip()
    text = re.sub(r"\bvoivodeship\b", "", text).strip()
    text = re.sub(r"\s+", " ", text)
    aliases = {
        "masovian": "mazowieckie",
        "mazovia": "mazowieckie",
        "mazowsze": "mazowieckie",
        "lesser poland": "malopolskie",
        "malopolska": "malopolskie",
        "silesian": "slaskie",
        "silesia": "slaskie",
        "slask": "slaskie",
        "greater poland": "wielkopolskie",
        "wielkopolska": "wielkopolskie",
        "lower silesian": "dolnoslaskie",
        "lower silesia": "dolnoslaskie",
        "dolny slask": "dolnoslaskie",
        "pomeranian": "pomorskie",
        "pomerania": "pomorskie",
        "lodz": "lodzkie",
        "west pomeranian": "zachodniopomorskie",
        "west pomerania": "zachodniopomorskie",
        "lublin": "lubelskie",
        "subcarpathian": "podkarpackie",
        "podkarpacie": "podkarpackie",
        "kuyavian-pomeranian": "kujawsko-pomorskie",
        "kuyavian pomeranian": "kujawsko-pomorskie",
        "warmian-masurian": "warminsko-mazurskie",
        "warmian masurian": "warminsko-mazurskie",
        "holy cross": "swietokrzyskie",
        "podlaskie": "podlaskie",
        "lubusz": "lubuskie",
        "opole": "opolskie",
    }
    if text in REGION_EN:
        return text
    if text in aliases:
        return aliases[text]
    for key, en in REGION_EN.items():
        if _fold(en) == text or _fold(en.replace(" Voivodeship", "")) == text:
            return key
    return ""


def region_to_english(value: str) -> str:
    key = _wojewodztwo_key(value) or _fold(value or "").replace(" ", "-")
    if key in REGION_EN:
        return REGION_EN[key]
    raw = (value or "").strip()
    if not raw:
        return ""
    en = line_of_business_to_english(raw)
    return en or raw


def region_to_internal(value: str) -> str:
    key = _wojewodztwo_key(value)
    if key:
        return key
    folded = _fold(value or "").replace(" ", "-")
    return folded if folded in REGION_EN else (value or "").strip()


def line_of_business_to_english(value: str) -> str:
    text = " ".join((value or "").split())
    if not text:
        return ""
    for src, dst in _BUSINESS_PHRASES:
        text = re.sub(re.escape(src), dst, text, flags=re.IGNORECASE)
    for key, en in sorted(REGION_EN.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(re.escape(key), en, text, flags=re.IGNORECASE)
        diacritic = {
            "malopolskie": "małopolskie",
            "slaskie": "śląskie",
            "dolnoslaskie": "dolnośląskie",
            "lodzkie": "łódzkie",
            "warminsko-mazurskie": "warmińsko-mazurskie",
            "swietokrzyskie": "świętokrzyskie",
        }.get(key)
        if diacritic:
            text = re.sub(re.escape(diacritic), en, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" ,;-")
    return text[:220]


def localisation_to_english(value: str) -> str:
    text = " ".join((value or "").split())
    if not text:
        return ""
    for src, dst in sorted(_CITY_EN, key=lambda p: -len(p[0])):
        text = re.sub(re.escape(src), dst, text)
    for pat, repl in _STREET_RES:
        text = pat.sub(repl, text)
    text = re.sub(r"\s+", " ", text).strip(" ,;-")
    return text[:180]
