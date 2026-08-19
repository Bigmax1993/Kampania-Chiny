# -*- coding: utf-8 -*-
"""
Słowniki kampanii CN — dystrybutorzy / importerzy na terenie Polski materiałów budowlanych.
Frazy Serper per województwo; rotacja kategorii materiałów.
"""
from __future__ import annotations

SUPPLIER_ROLE_KEYWORDS: tuple[str, ...] = (
    "importer",
    "dystrybutor",
    "wyłączny dystrybutor",
    "oficjalny dystrybutor",
    "autoryzowany dystrybutor",
    "wyłączny importer",
    "oficjalny importer",
    "przedstawiciel",
    "agent",
    "hurt",
    "dystrybucja",
    "import",
)

MATERIAL_CATEGORY_KEYWORDS: tuple[str, ...] = (
    "płytki",
    "ceramika",
    "armatura",
    "LED",
    "oświetlenie LED",
    "SPC",
    "panele SPC",
    "profile aluminiowe",
    "aluminium",
    "chemia budowlana",
    "okna PVC",
    "PVC",
    "stal",
    "stal konstrukcyjna",
    "stal nierdzewna",
    "stal ocynkowana",
    "stal zbrojeniowa",
    "blacha stalowa",
    "blachy stalowe",
    "rury stalowe",
    "profile stalowe",
    "pręty stalowe",
    "kształtowniki stalowe",
    "belki stalowe",
    "drzwi",
    "drzwi wewnętrzne",
    "drzwi zewnętrzne",
    "drzwi wejściowe",
    "drzwi stalowe",
    "drzwi aluminiowe",
    "drzwi drewniane",
    "drzwi PVC",
    "ościeżnice",
    "kabiny prysznicowe",
    "kabina prysznicowa",
    "drzwi prysznicowe",
    "brodziki",
    "natryski",
    "instalacje sanitarne",
    "armatura łazienkowa",
    "ceramika łazienkowa",
    "baterie łazienkowe",
    "hydraulika",
    "umywalki",
    "wanny",
    "toalety",
    "stelaże WC",
    "sanitariat",
    "ceramika sanitarna",
    "płytki ceramiczne",
)

REQUIRED_MATERIAL_CATEGORY_KEYWORDS = MATERIAL_CATEGORY_KEYWORDS

MATERIAL_SUPPLY_KEYWORDS = SUPPLIER_ROLE_KEYWORDS
MATERIAL_TRADE_ACTIVITY_KEYWORDS = (
    "katalog",
    "cennik",
    "ceny",
    "asortyment",
    "dostępność",
    "program magazynowy",
    "dostawa po polsce",
    "odbiór osobisty",
)
MATERIAL_CATALOG_KEYWORDS = (
    "katalog produktów",
    "nasz asortyment",
    "produkty",
    "cennik",
    "ceny",
)
MATERIAL_URL_PRIORITY_KEYWORDS = (
    "kontakt",
    "contact",
    "produkty",
    "katalog",
    "asortyment",
    "cennik",
    "ceny",
)
IMPRESSUM_GUESS_PATHS = (
    "/kontakt",
    "/contact",
    "/o-firmie",
    "/about",
    "/impressum",
)
SUPPLIER_CONTACT_LINK_KEYWORDS = (
    "kontakt",
    "napisz do nas",
    "email",
    "e-mail",
    "telefon",
    "zamów",
    "zapytanie",
)
SERPER_POSITIVE_TERMS = (
    *SUPPLIER_ROLE_KEYWORDS,
    *(k.lower() for k in MATERIAL_CATEGORY_KEYWORDS),
)
PL_PLACE_MARKERS: tuple[str, ...] = ()
PL_RURAL_HINTS: tuple[str, ...] = ()
LARGE_COMPANY_DOMAINS_EXTRA: frozenset[str] = frozenset()
LARGE_COMPANY_NAME_MARKERS_EXTRA: tuple[str, ...] = ()
SMALL_COMPANY_PAGE_MARKERS_EXTRA: tuple[str, ...] = (
    "rodzinna firma",
    "firma rodzinna",
    "sp. z o.o.",
    "spółka z ograniczoną odpowiedzialnością",
    "regionalny",
    "lokalny",
)
SMALL_COMPANY_DISCOVERY_TERMS_EXTRA: tuple[str, ...] = (
    "regionalny dystrybutor",
    "lokalny importer",
    "wyłączny dystrybutor",
)

MATERIAL_CATEGORIES_ROTATION = (
    "płytki",
    "stal",
    "drzwi",
    "kabiny prysznicowe",
    "ceramika",
    "stal konstrukcyjna",
    "drzwi wewnętrzne",
    "instalacje sanitarne",
    "armatura",
    "stal nierdzewna",
    "drzwi zewnętrzne",
    "armatura łazienkowa",
    "LED",
    "blacha stalowa",
    "drzwi stalowe",
    "ceramika łazienkowa",
    "SPC",
    "rury stalowe",
    "drzwi aluminiowe",
    "baterie łazienkowe",
    "profile aluminiowe",
    "profile stalowe",
    "drzwi wejściowe",
    "brodziki",
    "chemia budowlana",
    "pręty stalowe",
    "ościeżnice",
    "umywalki",
    "okna PVC",
    "stal ocynkowana",
    "drzwi prysznicowe",
    "wanny",
    "sanitariat",
    "stal zbrojeniowa",
    "hydraulika",
    "ceramika sanitarna",
    "kształtowniki stalowe",
    "drzwi drewniane",
    "stelaże WC",
)

CHAIN_SIMPLE_TERM_TEMPLATES = (
    "{city} dystrybutor {material}",
    "{city} importer {material}",
    "{city} wyłączny dystrybutor {material}",
    "{city} oficjalny dystrybutor {material}",
    "{city} hurtownia {material}",
    "dystrybutor {material} {city} Polska",
    "importer {material} {city}",
    "wyłączny dystrybutor {material} {city}",
    "oficjalny dystrybutor {material} Polska",
    "hurtownia {material} {city} Polska",
)

SIMPLE_TERM_TEMPLATES = CHAIN_SIMPLE_TERM_TEMPLATES

TERM_TEMPLATES = (
    "dystrybutor {material} {city} {oblast}",
    "importer {material} {city} {oblast}",
    "wyłączny dystrybutor {material} {city}",
    "oficjalny dystrybutor {material} {oblast}",
    "hurt {material} dystrybutor {city}",
    "hurtownia {material} {city} {oblast}",
    "importer dystrybutor {material} {city} Polska",
)

SERPER_NEGATIVE_TERMS = (
    "olx",
    "allegro",
    "ogłoszenia",
    "sklep",
    "praca",
    "oferty pracy",
    "remont",
    "remont mieszkań",
    "wykończenia wnętrz",
    "wiadomości",
    "blog",
    "forum",
    "urząd",
    "ministerstwo",
    "portal",
    "encyklopedia",
    "wikipedia",
    "używane",
    "biuro architektoniczne",
    "bank",
    "ubezpieczenia",
    "restauracja",
    "hotel",
)

PL_REGION_KEYWORDS = (
    "polska",
    "poland",
    "polski",
)

COUNTRYWIDE_MAX_DISCOVERY_TERMS = 1500


PROVINCE_CONFIG: dict[str, dict] = {
    "mazowieckie": {
        "short": "MZ",
        "cities": ("Warszawa", "Radom", "Płock", "Siedlce", "Ostrołęka", "Pruszków"),
    },
    "malopolskie": {
        "short": "MA",
        "cities": ("Kraków", "Tarnów", "Nowy Sącz", "Oświęcim", "Chrzanów", "Wieliczka"),
    },
    "slaskie": {
        "short": "SL",
        "cities": ("Katowice", "Częstochowa", "Sosnowiec", "Gliwice", "Zabrze", "Bielsko-Biała"),
    },
    "wielkopolskie": {
        "short": "WP",
        "cities": ("Poznań", "Kalisz", "Konin", "Piła", "Leszno", "Gniezno"),
    },
    "dolnoslaskie": {
        "short": "DS",
        "cities": ("Wrocław", "Wałbrzych", "Legnica", "Jelenia Góra", "Lubin", "Głogów"),
    },
    "pomorskie": {
        "short": "PM",
        "cities": ("Gdańsk", "Gdynia", "Słupsk", "Tczew", "Wejherowo", "Starogard Gdański"),
    },
    "lodzkie": {
        "short": "LD",
        "cities": ("Łódź", "Piotrków Trybunalski", "Pabianice", "Zgierz", "Skierniewice", "Kutno"),
    },
    "zachodniopomorskie": {
        "short": "ZP",
        "cities": ("Szczecin", "Koszalin", "Stargard", "Kołobrzeg", "Świnoujście", "Police"),
    },
    "lubelskie": {
        "short": "LU",
        "cities": ("Lublin", "Zamość", "Chełm", "Biała Podlaska", "Puławy", "Świdnik"),
    },
    "podkarpackie": {
        "short": "PK",
        "cities": ("Rzeszów", "Przemyśl", "Stalowa Wola", "Mielec", "Tarnobrzeg", "Krosno"),
    },
    "kujawsko-pomorskie": {
        "short": "KP",
        "cities": ("Bydgoszcz", "Toruń", "Włocławek", "Grudziądz", "Inowrocław", "Brodnica"),
    },
    "warminsko-mazurskie": {
        "short": "WN",
        "cities": ("Olsztyn", "Elbląg", "Ełk", "Iława", "Ostróda", "Giżycko"),
    },
    "swietokrzyskie": {
        "short": "SK",
        "cities": ("Kielce", "Ostrowiec Świętokrzyski", "Starachowice", "Sandomierz", "Końskie"),
    },
    "podlaskie": {
        "short": "PD",
        "cities": ("Białystok", "Suwałki", "Łomża", "Augustów", "Hajnówka", "Grajewo"),
    },
    "lubuskie": {
        "short": "LB",
        "cities": ("Zielona Góra", "Gorzów Wielkopolski", "Żary", "Nowa Sól", "Świebodzin"),
    },
    "opolskie": {
        "short": "OP",
        "cities": ("Opole", "Kędzierzyn-Koźle", "Nysa", "Brzeg", "Kluczbork", "Prudnik"),
    },
}

ALL_PROVINCES: tuple[str, ...] = tuple(PROVINCE_CONFIG.keys())
DEFAULT_ACTIVE_PROVINCES: list[str] = list(ALL_PROVINCES)
CAMPAIGN_ACTIVE_PROVINCES: list[str] = list(DEFAULT_ACTIVE_PROVINCES)

# Aliasy kompatybilności z pipeline GU (scraper używa tych samych nazw funkcji)
BUNDESLAND_CONFIG = PROVINCE_CONFIG
ALL_BUNDESLAENDER = ALL_PROVINCES
DEFAULT_ACTIVE_BUNDESLAENDER = DEFAULT_ACTIVE_PROVINCES
CAMPAIGN_ACTIVE_BUNDESLAENDER = CAMPAIGN_ACTIVE_PROVINCES

COUNTRYWIDE_MAX_DISCOVERY_TERMS = 1500


def default_max_discovery_terms_for(active: list[str] | None = None) -> int:
    n = len(resolve_active_provinces(active))
    if n <= 1:
        return 120
    if n <= 3:
        return 360
    return COUNTRYWIDE_MAX_DISCOVERY_TERMS


def _normalize_wojewodztwo_key(name: str) -> str:
    n = (name or "").strip()
    aliases = {
        "mazowieckie": "mazowieckie",
        "mazowsze": "mazowieckie",
        "warszawa": "mazowieckie",
        "malopolskie": "malopolskie",
        "małopolskie": "malopolskie",
        "krakow": "malopolskie",
        "kraków": "malopolskie",
        "slaskie": "slaskie",
        "śląskie": "slaskie",
        "katowice": "slaskie",
        "wielkopolskie": "wielkopolskie",
        "poznan": "wielkopolskie",
        "poznań": "wielkopolskie",
        "dolnoslaskie": "dolnoslaskie",
        "dolnośląskie": "dolnoslaskie",
        "wroclaw": "dolnoslaskie",
        "wrocław": "dolnoslaskie",
    }
    low = n.lower()
    if low in aliases:
        return aliases[low]
    for key in PROVINCE_CONFIG:
        if key.lower() == low:
            return key
    return n



def resolve_active_provinces(names: list[str] | None = None) -> list[str]:
    if not names:
        return list(CAMPAIGN_ACTIVE_PROVINCES)
    out: list[str] = []
    for raw in names:
        for part in str(raw).replace(";", ",").split(","):
            key = _normalize_wojewodztwo_key(part)
            if key in PROVINCE_CONFIG and key not in out:
                out.append(key)
    return out or list(DEFAULT_ACTIVE_PROVINCES)


resolve_active_bundeslaender = resolve_active_provinces


def _append_unique_term(terms: list[str], seen: set[str], text: str, *, max_terms: int) -> bool:
    t = (text or "").strip()
    if not t or t in seen:
        return False
    seen.add(t)
    terms.append(t)
    return len(terms) >= max_terms


def _rotating_material(counter: list[int]) -> str:
    material = MATERIAL_CATEGORIES_ROTATION[counter[0] % len(MATERIAL_CATEGORIES_ROTATION)]
    counter[0] += 1
    return material


def _format_material_term(
    tmpl: str,
    *,
    city: str,
    oblast: str,
    material: str,
) -> str:
    return tmpl.format(city=city, oblast=oblast, material=material, land=oblast, chain=material)


def build_discovery_terms(
    active: list[str] | None = None, *, max_terms: int | None = None
) -> list[str]:
    oblasts = resolve_active_provinces(active)
    if max_terms is None:
        max_terms = default_max_discovery_terms_for(oblasts)
    seen: set[str] = set()
    terms: list[str] = []
    material_counter = [0]
    all_templates = (*CHAIN_SIMPLE_TERM_TEMPLATES, *TERM_TEMPLATES)
    for oblast in oblasts:
        cfg = PROVINCE_CONFIG[oblast]
        cities = cfg["cities"]
        for city in cities:
            for tmpl in all_templates:
                material = _rotating_material(material_counter)
                if _append_unique_term(
                    terms,
                    seen,
                    _format_material_term(
                        tmpl, city=city, oblast=oblast, material=material
                    ),
                    max_terms=max_terms,
                ):
                    return terms
    if len(oblasts) >= 8:
        countrywide = (
            "dystrybutor {material} Polska",
            "importer {material} Polska",
            "wyłączny dystrybutor {material} Polska",
            "oficjalny dystrybutor {material} Polska",
            "importer dystrybutor {material} Polska -sklep -ogłoszenia -allegro -olx",
        )
        for tmpl in countrywide:
            material = _rotating_material(material_counter)
            if _append_unique_term(
                terms,
                seen,
                tmpl.format(material=material),
                max_terms=max_terms,
            ):
                return terms
    return terms


def build_raion_discovery_terms(active: list[str] | None = None) -> list[str]:
    oblasts = resolve_active_provinces(active)
    seen: set[str] = set()
    terms: list[str] = []
    material_counter = [0]
    for oblast in oblasts:
        short = PROVINCE_CONFIG[oblast]["short"]
        for city in PROVINCE_CONFIG[oblast]["cities"][:6]:
            for tmpl in (
                "dystrybutor {material} {city} okolice",
                "importer {material} {city} {short}",
                "wyłączny dystrybutor {material} {city}",
            ):
                material = _rotating_material(material_counter)
                _append_unique_term(
                    terms,
                    seen,
                    tmpl.format(city=city, short=short, material=material),
                    max_terms=10_000,
                )
        material = _rotating_material(material_counter)
        _append_unique_term(
            terms,
            seen,
            f"dystrybutor {material} {oblast} Polska",
            max_terms=10_000,
        )
    return terms


build_landkreis_discovery_terms = build_raion_discovery_terms


def build_places_discovery_terms(active: list[str] | None = None) -> list[str]:
    oblasts = resolve_active_provinces(active)
    seen: set[str] = set()
    terms: list[str] = []
    material_counter = [0]
    for oblast in oblasts:
        for city in PROVINCE_CONFIG[oblast]["cities"][:8]:
            for tmpl in (
                "dystrybutor {material} {city}",
                "importer {material} {city}",
                "oficjalny dystrybutor {material} {city}",
                "wyłączny dystrybutor {material} {city}",
            ):
                material = _rotating_material(material_counter)
                _append_unique_term(
                    terms,
                    seen,
                    tmpl.format(city=city, material=material),
                    max_terms=10_000,
                )
        material = _rotating_material(material_counter)
        _append_unique_term(
            terms,
            seen,
            f"importer {material} {oblast}",
            max_terms=10_000,
        )
    return terms


def build_broad_discovery_terms(active: list[str] | None = None) -> list[str]:
    oblasts = resolve_active_provinces(active)
    seen: set[str] = set()
    terms: list[str] = []
    material_counter = [0]
    for oblast in oblasts:
        short = PROVINCE_CONFIG[oblast]["short"]
        for city in PROVINCE_CONFIG[oblast]["cities"]:
            for tmpl in (
                "dystrybutor {material} {city}",
                "importer {material} {city}",
                "oficjalny dystrybutor {material} {city}",
            ):
                material = _rotating_material(material_counter)
                _append_unique_term(
                    terms,
                    seen,
                    tmpl.format(city=city, material=material),
                    max_terms=10_000,
                )
        for tmpl in (
            "dystrybutor {material} {oblast}",
            "importer {material} {oblast}",
            "wyłączny dystrybutor {material} {short}",
        ):
            material = _rotating_material(material_counter)
            _append_unique_term(
                terms,
                seen,
                tmpl.format(oblast=oblast, short=short, material=material),
                max_terms=10_000,
            )
    return terms


def build_region_suffix(active: list[str] | None = None) -> str:
    oblasts = resolve_active_provinces(active)
    if len(oblasts) <= 1:
        return "Polska"
    if len(oblasts) >= 4:
        return "Polska"
    shorts = " ".join(PROVINCE_CONFIG[o]["short"] for o in oblasts[:4])
    return f"Polska {shorts}"


def configure_campaign_provinces(
    module,
    names: list[str],
    *,
    max_discovery_terms: int | None = None,
) -> list[str]:
    global CAMPAIGN_ACTIVE_PROVINCES, CAMPAIGN_ACTIVE_BUNDESLAENDER
    active = resolve_active_provinces(names)
    if max_discovery_terms is None:
        max_discovery_terms = default_max_discovery_terms_for(active)
    CAMPAIGN_ACTIVE_PROVINCES = active
    CAMPAIGN_ACTIVE_BUNDESLAENDER = active
    module.CAMPAIGN_ACTIVE_PROVINCES = active
    module.CAMPAIGN_ACTIVE_BUNDESLAENDER = active
    module.SERPER_DISCOVERY_TERMS = build_discovery_terms(
        active, max_terms=max_discovery_terms
    )
    module.SERPER_DISCOVERY_FALLBACK_TERMS = build_fallback_terms(active)
    module.SERPER_DISCOVERY_BROAD_TERMS = build_broad_discovery_terms(active)
    module.SERPER_DISCOVERY_LANDKREIS_TERMS = build_raion_discovery_terms(active)
    module.SERPER_DISCOVERY_PLACES_TERMS = build_places_discovery_terms(active)
    module.SERPER_DISCOVERY_REGION_SUFFIX = build_region_suffix(active)
    return active


configure_campaign_bundeslaender = configure_campaign_provinces


def build_fallback_terms(active: list[str] | None = None) -> list[str]:
    oblasts = resolve_active_provinces(active)
    fb: list[str] = []
    material_counter = [0]
    for oblast in oblasts:
        short = PROVINCE_CONFIG[oblast]["short"]
        for tmpl in (
            "dystrybutor {material} {oblast}",
            "importer {material} {short}",
            "wyłączny dystrybutor {material} {oblast}",
            "oficjalny dystrybutor {material} {oblast}",
        ):
            material = _rotating_material(material_counter)
            fb.append(tmpl.format(oblast=oblast, short=short, material=material))
    for tmpl in (
        "dystrybutor {material} Polska",
        "importer {material} Polska",
        "wyłączny dystrybutor {material} Polska",
        "oficjalny dystrybutor {material} Polska",
    ):
        material = _rotating_material(material_counter)
        fb.append(tmpl.format(material=material))
    seen: set[str] = set()
    out: list[str] = []
    for t in fb:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


SERPER_DISCOVERY_TERMS = build_discovery_terms()
SERPER_DISCOVERY_FALLBACK_TERMS = build_fallback_terms()
SERPER_DISCOVERY_BROAD_TERMS = build_broad_discovery_terms()
SERPER_DISCOVERY_LANDKREIS_TERMS = build_raion_discovery_terms()
SERPER_DISCOVERY_PLACES_TERMS = build_places_discovery_terms()
SERPER_DISCOVERY_REGION_SUFFIX = build_region_suffix()

# Aliasy dla importów ze scrapera GU
GU_ROLE_KEYWORDS = SUPPLIER_ROLE_KEYWORDS
RETAIL_CHAIN_KEYWORDS = MATERIAL_CATEGORY_KEYWORDS
REQUIRED_RETAIL_CHAIN_KEYWORDS = REQUIRED_MATERIAL_CATEGORY_KEYWORDS
RETAIL_BUILD_KEYWORDS = MATERIAL_SUPPLY_KEYWORDS
RETAIL_TRADE_ACTIVITY_KEYWORDS = MATERIAL_TRADE_ACTIVITY_KEYWORDS
RETAIL_HOCHBAU_CORE_KEYWORDS = MATERIAL_CATALOG_KEYWORDS
RETAIL_REFERENCE_KEYWORDS = MATERIAL_CATALOG_KEYWORDS
RETAIL_URL_PRIORITY_KEYWORDS = MATERIAL_URL_PRIORITY_KEYWORDS
RETAIL_CONTACT_LINK_KEYWORDS = SUPPLIER_CONTACT_LINK_KEYWORDS
DE_OST_PLACE_MARKERS = PL_PLACE_MARKERS
DE_OST_REGION_KEYWORDS = PL_REGION_KEYWORDS
DE_OST_RURAL_HINTS = PL_RURAL_HINTS
RETAIL_CHAINS_ROTATION = MATERIAL_CATEGORIES_ROTATION
