# -*- coding: utf-8 -*-
from __future__ import annotations

from cn_regional_sender_context import (
    build_regional_sender_instructions_pl,
    resolve_discovery_wojewodztwo,
    wojewodztwo_primary_city_pl,
)


def test_resolve_discovery_prefers_discovery_bundesland():
    key = resolve_discovery_wojewodztwo(
        {"discovery_bundesland": "zhejiang", "bundesland": "jiangsu"}
    )
    assert key == "zhejiang"


def test_primary_city_guangdong():
    assert wojewodztwo_primary_city_pl("guangdong") == "佛山"


def test_regional_sender_mentions_construction_block():
    text = build_regional_sender_instructions_pl(
        "sichuan",
        sender_name="Maksym Swinczak",
        sender_phone="516513965",
        construction_project_block="OBIEKT BUDOWY\n• Adres: 成都市天府新区兴隆湖",
    )
    assert "REGION DISCOVERY" in text
    assert "成都" in text or "sichuan" in text
    assert "OBIEKT BUDOWY" in text
    assert "516513965" in text
    assert "Maksym Swinczak" in text
    assert "średni" in text.lower()


def test_regional_sender_requires_real_company():
    text = build_regional_sender_instructions_pl(
        "sichuan",
        sender_name="Maksym Swinczak",
        sender_phone="516513965",
    )
    assert "REALNĄ" in text or "istniejącą" in text.lower() or "ISTNIEJĄCĄ" in text
    assert "NIE wymyślaj" in text or "fikcyjnych" in text.lower()
