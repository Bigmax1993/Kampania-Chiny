# -*- coding: utf-8 -*-
"""
Zweryfikowane referencje obiektów budowlanych w PL (adresy publiczne).
Używane w mailach — Claude MUSI podać dokładny adres z wybranego wpisu.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from cn_province_keywords import _normalize_wojewodztwo_key


@dataclass(frozen=True)
class ConstructionProjectRef:
    name_pl: str
    object_type_pl: str
    address_pl: str
    status_pl: str = "w budowie"

    def prompt_block_pl(self) -> str:
        return (
            f"• Nazwa: {self.name_pl}\n"
            f"• Typ: {self.object_type_pl}\n"
            f"• Adres (KOPIUJ DOSŁOWNIE do listu): {self.address_pl}\n"
            f"• Status: {self.status_pl}"
        )


# Adresy z publicznych kart projektow (strony deweloperow / portale nieruchomosci CN).
WOJEWODZTWO_CONSTRUCTION_REFS: dict[str, tuple[ConstructionProjectRef, ...]] = {
    "guangdong": (
        ConstructionProjectRef("万科金域蓝湾", "住宅小区", "佛山市禅城区季华西路12号"),
        ConstructionProjectRef("珠江新城写字楼", "商务办公楼", "广州市天河区珠江新城华夏路10号"),
        ConstructionProjectRef("前海桂湾", "综合开发项目", "深圳市南山区前海桂湾一路"),
        ConstructionProjectRef("东莞松山湖科技园", "产业园区", "东莞市松山湖大道1号"),
    ),
    "zhejiang": (
        ConstructionProjectRef("杭州钱江新城", "商务住宅综合体", "杭州市江干区钱江路1366号"),
        ConstructionProjectRef("义乌国际商贸城配套", "仓储物流园区", "义乌市福田街道国际商贸城大道"),
        ConstructionProjectRef("宁波东部新城", "城市综合体", "宁波市鄞州区宁穿路1号"),
    ),
    "jiangsu": (
        ConstructionProjectRef("苏州工业园区湖东", "产业园区", "苏州市工业园区星湖街328号"),
        ConstructionProjectRef("南京河西新城", "住宅与商务综合体", "南京市建邺区江东中路269号"),
    ),
    "shandong": (
        ConstructionProjectRef("青岛西海岸新区", "港口产业配套", "青岛市黄岛区长江西路"),
        ConstructionProjectRef("济南汉峪金谷", "商务办公区", "济南市历下区经十路7000号"),
    ),
    "shanghai": (
        ConstructionProjectRef("陆家嘴世纪汇", "商务综合体", "上海市浦东新区世纪大道1198号"),
        ConstructionProjectRef("临港新片区", "产业园区", "上海市浦东新区临港大道"),
    ),
    "fujian": (
        ConstructionProjectRef("厦门集美新城", "住宅综合体", "厦门市集美区杏林湾路"),
        ConstructionProjectRef("泉州东海大街", "商业综合体", "泉州市丰泽区东海大街"),
    ),
    "hebei": (
        ConstructionProjectRef("石家庄正定新区", "城市新区", "石家庄市正定新区太行大街"),
        ConstructionProjectRef("唐山曹妃甸", "港口产业区", "唐山市曹妃甸区渤海大道"),
    ),
    "sichuan": (
        ConstructionProjectRef("成都天府新区", "商务住宅综合体", "成都市天府新区兴隆湖"),
        ConstructionProjectRef("成都东部新区", "产业园区", "成都市东部新区空港大道"),
    ),
    "henan": (
        ConstructionProjectRef("郑州郑东新区", "商务综合体", "郑州市郑东新区商务外环路"),
        ConstructionProjectRef("洛阳隋唐城遗址片区", "城市更新", "洛阳市洛龙区开元大道"),
    ),
    "hubei": (
        ConstructionProjectRef("武汉光谷", "科技产业园", "武汉市东湖高新区光谷大道"),
        ConstructionProjectRef("武汉长江新城", "城市综合体", "武汉市黄陂区长江新城大道"),
    ),
    "beijing": (
        ConstructionProjectRef("北京通州城市副中心", "政务商务区", "北京市通州区运河东大街"),
        ConstructionProjectRef("北京大兴国际空港", "临空经济区", "北京市大兴区礼贤镇"),
    ),
    "tianjin": (
        ConstructionProjectRef("天津滨海新区", "产业园区", "天津市滨海新区响螺湾"),
        ConstructionProjectRef("天津西青开发区", "产业园区", "天津市西青区海泰发展六道"),
    ),
    "chongqing": (
        ConstructionProjectRef("重庆两江新区", "城市综合体", "重庆市渝北区金开大道"),
        ConstructionProjectRef("重庆西部槽谷", "产业园区", "重庆市沙坪坝区大学城"),
    ),
    "anhui": (
        ConstructionProjectRef("合肥滨湖新区", "商务住宅综合体", "合肥市包河区徽州大道"),
        ConstructionProjectRef("芜湖江北新区", "城市新区", "芜湖市鸠江区江北大道"),
    ),
    "liaoning": (
        ConstructionProjectRef("沈阳浑南新城", "城市综合体", "沈阳市浑南区全运路"),
        ConstructionProjectRef("大连金普新区", "产业园区", "大连市金州区金马路"),
    ),
    "jiangxi": (
        ConstructionProjectRef("南昌红谷滩", "商务综合体", "南昌市红谷滩区丰和中大道"),
        ConstructionProjectRef("赣州蓉江新区", "城市新区", "赣州市章贡区蓉江大道"),
    ),
}

_DEFAULT_FALLBACK = ConstructionProjectRef(
    "万科金域蓝湾",
    "住宅小区",
    "佛山市禅城区季华西路12号",
)



def _normalize_match_text(text: str) -> str:
    low = (text or "").lower().replace("'", "'").replace("`", "'")
    low = re.sub(r"\s+", " ", low)
    return low.strip()


def _address_match_keys(address: str) -> tuple[str, ...]:
    """Kluczowe fragmenty adresu do walidacji (ulica + numer)."""
    norm = _normalize_match_text(address)
    keys: list[str] = []
    keys.append(norm)
    m = re.search(
        r"(ul\.?|ulica|al\.?|aleja|pl\.?|plac|os\.?|osiedle)\s+[^,]+",
        norm,
        flags=re.IGNORECASE,
    )
    if m:
        keys.append(m.group(0).strip())
    parts = [p.strip() for p in norm.split(",") if p.strip()]
    if len(parts) >= 2:
        keys.append(", ".join(parts[-2:]))
    if parts:
        keys.append(parts[-1])
    out: list[str] = []
    seen: set[str] = set()
    for k in keys:
        if k and k not in seen and len(k) >= 8:
            seen.add(k)
            out.append(k)
    return tuple(out)


def address_present_in_body(body: str, address: str) -> bool:
    body_n = _normalize_match_text(body)
    for key in _address_match_keys(address):
        if key in body_n:
            return True
    return False


def extract_city_from_address_pl(address: str) -> str:
    """Wyciąga nazwę miasta z adresu PL (np. «Warszawa, ul. …»)."""
    norm = (address or "").strip()
    if not norm:
        return ""
    parts = [part.strip() for part in norm.split(",") if part.strip()]
    if not parts:
        return ""
    first = parts[0]
    # pomiń prefiksy typu „miasto”
    first = re.sub(r"^(m\.|miasto)\s+", "", first, flags=re.IGNORECASE).strip()
    if re.match(r"^(ul\.?|ulica|al\.?|aleja)\b", first, flags=re.IGNORECASE):
        return ""
    return first


def _project_matches_city(project: ConstructionProjectRef, city: str) -> bool:
    city_norm = _normalize_match_text(city)
    if not city_norm:
        return False
    return city_norm in _normalize_match_text(project.address_pl)


def pick_construction_project(
    wojewodztwo_key: str,
    seed: str,
    *,
    prefer_city: str = "",
) -> ConstructionProjectRef:
    key = _normalize_wojewodztwo_key(wojewodztwo_key)
    pool = WOJEWODZTWO_CONSTRUCTION_REFS.get(key)
    if not pool:
        return _DEFAULT_FALLBACK
    city = (prefer_city or "").strip()
    if city:
        city_pool = tuple(project for project in pool if _project_matches_city(project, city))
        if city_pool:
            pool = city_pool
    digest = hashlib.sha256((seed or key).encode("utf-8")).hexdigest()
    idx = int(digest[:8], 16) % len(pool)
    return pool[idx]


def build_construction_project_prompt_block_pl(project: ConstructionProjectRef) -> str:
    return f"""OBIEKT BUDOWY (OBOWIĄZKOWO — sprawdzona baza publicznych inwestycji w Chinach)
{project.prompt_block_pl()}

WYMAGANIA DOTYCZĄCE OBIEKTU I ADRESU
• To jest REALNA inwestycja z publicznej bazy (strony deweloperów / portale inwestycji) — NIE wymyślaj innego obiektu.
• W treści listu MUSI pojawić się PEŁNA nazwa obiektu «{project.name_pl}» ORAZ PEŁNY adres z wiersza «Adres» powyżej — dosłownie, bez zmiany numeru budynku, nazwy ulicy ani miasta.
• Zabronione: fikcyjne osiedla, „placeholderowe” adresy, inna ulica/numer/miasto, ogólne „budowa w okolicy” bez adresu z bazy.
• Wspomnij typ obiektu ({project.object_type_pl}) i krótko — jakie materiały budowlane są potrzebne na ten plac budowy."""


def inject_construction_project_context(body: str, project: ConstructionProjectRef) -> str:
    """Jeśli Claude pominął adres — wstaw akapit z realnym adresem z bazy."""
    text = (body or "").strip()
    if not text or address_present_in_body(text, project.address_pl):
        return text
    paragraph = (
        f"我们正在建设{project.object_type_pl}「{project.name_pl}」"
        f"（{project.status_pl}），地址：{project.address_pl}。"
        f"该项目需要持续采购建材。"
    )
    marker = "此致敬礼"
    if marker in text:
        head, tail = text.split(marker, 1)
        return f"{head.rstrip()}\n\n{paragraph}\n\n{marker}{tail}"
    return f"{text}\n\n{paragraph}"
