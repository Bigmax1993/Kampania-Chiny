# -*- coding: utf-8 -*-
"""
Słowniki kampanii CN — hurtownie / składy / producenci materiałów budowlanych.
Frazy Serper per prowincjio; rotacja kategorii materiałów.
"""
from __future__ import annotations

SUPPLIER_ROLE_KEYWORDS: tuple[str, ...] = (
    "建材经销商",
    "建材代理商",
    "建材进口商",
    "建材批发",
    "官方代理",
    "一级代理",
    "建材批发市场",
    "工程经销商",
    "外贸经销商",
    "B2B 批发",
)

MATERIAL_CATEGORY_KEYWORDS: tuple[str, ...] = (
    "瓷砖",
    "陶瓷",
    "卫浴",
    "洁具",
    "灯具",
    "LED灯",
    "铝型材",
    "五金",
    "地板",
    "SPC地板",
    "涂料",
    "防水材料",
    "管材",
    "钢材",
    "水泥",
    "PVC窗",
    "门窗",
    "胶粘剂",
    "保温材料",
    "石材",
)

REQUIRED_MATERIAL_CATEGORY_KEYWORDS = MATERIAL_CATEGORY_KEYWORDS

MATERIAL_SUPPLY_KEYWORDS = SUPPLIER_ROLE_KEYWORDS
MATERIAL_TRADE_ACTIVITY_KEYWORDS = (
    "产品目录",
    "价格表",
    "批发价",
    "现货",
    "库存",
    "厂家直销",
    "发货",
    "工程供货",
)
MATERIAL_CATALOG_KEYWORDS = (
    "产品中心",
    "产品展示",
    "产品目录",
    "批发",
    "价格",
)
MATERIAL_URL_PRIORITY_KEYWORDS = (
    "联系我们",
    "contact",
    "关于我们",
    "about",
    "产品中心",
    "产品",
)
IMPRESSUM_GUESS_PATHS = (
    "/contact",
    "/about",
    "/contact-us",
    "/about-us",
    "/联系我们",
    "/关于我们",
)
SUPPLIER_CONTACT_LINK_KEYWORDS = (
    "联系我们",
    "联系方式",
    "email",
    "e-mail",
    "电话",
    "询价",
    "留言",
)
SERPER_POSITIVE_TERMS = (
    *SUPPLIER_ROLE_KEYWORDS,
    *MATERIAL_CATEGORY_KEYWORDS[:20],
)
PL_PLACE_MARKERS: tuple[str, ...] = ()
PL_RURAL_HINTS: tuple[str, ...] = ()
LARGE_COMPANY_DOMAINS_EXTRA: frozenset[str] = frozenset()
LARGE_COMPANY_NAME_MARKERS_EXTRA: tuple[str, ...] = ()
SMALL_COMPANY_PAGE_MARKERS_EXTRA: tuple[str, ...] = (
    "有限公司",
    "厂家",
    "工厂",
    "私营",
    "实业",
    "贸易",
)
SMALL_COMPANY_DISCOVERY_TERMS_EXTRA: tuple[str, ...] = (
    "厂家直销",
    "工厂直销",
    "本地经销商",
)

MATERIAL_CATEGORIES_ROTATION = (
    "瓷砖",
    "卫浴",
    "灯具",
    "铝型材",
    "五金",
    "地板",
    "涂料",
    "钢材",
    "水泥",
    "管材",
    "石材",
    "防水材料",
)

CHAIN_SIMPLE_TERM_TEMPLATES = (
    "{city} {material} 经销商",
    "{city} {material} 代理商",
    "{city} {material} 进口商",
    "{city} {material} 批发",
    "{city} 建材经销商 {material}",
    "官方代理 {material} {city}",
    "{city} {material} 工程经销商",
    "{city} {material} 外贸批发",
)

SIMPLE_TERM_TEMPLATES = CHAIN_SIMPLE_TERM_TEMPLATES

TERM_TEMPLATES = (
    "{city} {oblast} {material} 经销商",
    "{city} {material} 一级代理",
    "{oblast} {material} 进口代理",
    "{city} {material} 批发市场",
    "官方经销商 {material} {city}",
    "{city} {material} B2B 批发",
)

SERPER_NEGATIVE_TERMS = (
    "新闻",
    "招聘",
    "论坛",
    "百科",
    "wikipedia",
    "二手",
    "闲置",
    "装修公司",
    "室内设计",
    "银行",
    "保险",
    "酒店",
    "旅游",
    "政府",
    "官网招聘",
)

PL_REGION_KEYWORDS = (
    "中国",
    "china",
    "广东",
    "浙江",
    "江苏",
)

COUNTRYWIDE_MAX_DISCOVERY_TERMS = 1500


PROVINCE_CONFIG: dict[str, dict] = {
    "guangdong": {"short": "GD", "cities": ("佛山", "广州", "深圳", "东莞", "中山", "珠海")},
    "zhejiang": {"short": "ZJ", "cities": ("义乌", "杭州", "宁波", "温州", "嘉兴", "金华")},
    "jiangsu": {"short": "JS", "cities": ("苏州", "无锡", "南京", "常州", "南通", "徐州")},
    "shandong": {"short": "SD", "cities": ("青岛", "济南", "临沂", "潍坊", "烟台", "淄博")},
    "shanghai": {"short": "SH", "cities": ("上海", "浦东", "嘉定", "松江", "青浦", "闵行")},
    "fujian": {"short": "FJ", "cities": ("泉州", "厦门", "福州", "漳州", "莆田", "龙岩")},
    "hebei": {"short": "HE", "cities": ("石家庄", "唐山", "保定", "邯郸", "廊坊", "沧州")},
    "sichuan": {"short": "SC", "cities": ("成都", "绵阳", "德阳", "宜宾", "南充", "乐山")},
    "henan": {"short": "HA", "cities": ("郑州", "洛阳", "南阳", "新乡", "许昌", "安阳")},
    "hubei": {"short": "HB", "cities": ("武汉", "宜昌", "襄阳", "黄石", "荆州", "十堰")},
    "beijing": {"short": "BJ", "cities": ("北京", "通州", "大兴", "昌平", "房山", "顺义")},
    "tianjin": {"short": "TJ", "cities": ("天津", "滨海", "武清", "西青", "东丽", "北辰")},
    "chongqing": {"short": "CQ", "cities": ("重庆", "渝北", "江津", "合川", "永川", "万州")},
    "anhui": {"short": "AH", "cities": ("合肥", "芜湖", "蚌埠", "阜阳", "安庆", "马鞍山")},
    "liaoning": {"short": "LN", "cities": ("沈阳", "大连", "鞍山", "营口", "锦州", "丹东")},
    "jiangxi": {"short": "JX", "cities": ("南昌", "赣州", "九江", "上饶", "宜春", "景德镇")},
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
        "guangdong": "guangdong",
        "广东": "guangdong",
        "foshan": "guangdong",
        "佛山": "guangdong",
        "广州": "guangdong",
        "zhejiang": "zhejiang",
        "浙江": "zhejiang",
        "义乌": "zhejiang",
        "杭州": "zhejiang",
        "jiangsu": "jiangsu",
        "江苏": "jiangsu",
        "shandong": "shandong",
        "山东": "shandong",
        "shanghai": "shanghai",
        "上海": "shanghai",
        "fujian": "fujian",
        "福建": "fujian",
        "hebei": "hebei",
        "河北": "hebei",
        "sichuan": "sichuan",
        "四川": "sichuan",
        "henan": "henan",
        "河南": "henan",
        "hubei": "hubei",
        "湖北": "hubei",
        "beijing": "beijing",
        "北京": "beijing",
        "tianjin": "tianjin",
        "天津": "tianjin",
        "chongqing": "chongqing",
        "重庆": "chongqing",
        "anhui": "anhui",
        "安徽": "anhui",
        "liaoning": "liaoning",
        "辽宁": "liaoning",
        "jiangxi": "jiangxi",
        "江西": "jiangxi",
    }
    low = n.lower()
    if n in aliases:
        return aliases[n]
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
            "中国 {material} 经销商",
            "中国 {material} 代理商",
            "中国 {material} 进口商",
            "中国 {material} 批发",
            "建材 {material} 外贸批发",
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
                "{city} {material} 经销商",
                "{city} {short} {material} 代理商",
                "{city} {material} 批发市场",
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
            f"{oblast} {material} 经销商",
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
                "{city} {material} 经销商",
                "{city} {material} 批发",
                "{city} {material} 厂家",
                "{city} 建材市场 {material}",
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
            f"{oblast} {material} 批发",
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
                "{city} {material} 经销商",
                "{city} {material} 代理商",
                "{city} {material} 进口商",
            ):
                material = _rotating_material(material_counter)
                _append_unique_term(
                    terms,
                    seen,
                    tmpl.format(city=city, material=material),
                    max_terms=10_000,
                )
        for tmpl in (
            "{oblast} {material} 经销商",
            "{oblast} {material} 批发",
            "{short} {material} 外贸",
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
        return "中国"
    if len(oblasts) >= 4:
        return "中国"
    shorts = " ".join(PROVINCE_CONFIG[o]["short"] for o in oblasts[:4])
    return f"中国 {shorts}"


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
            "{oblast} {material} 经销商",
            "{short} {material} 代理商",
            "{oblast} {material} 批发",
            "{oblast} {material} 进口商",
        ):
            material = _rotating_material(material_counter)
            fb.append(tmpl.format(oblast=oblast, short=short, material=material))
    for tmpl in (
        "中国 {material} 经销商",
        "中国 {material} 代理商",
        "中国 {material} 进口商",
        "中国建材 {material} 批发",
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
