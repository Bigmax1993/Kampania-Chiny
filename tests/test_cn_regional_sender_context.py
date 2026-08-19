# -*- coding: utf-8 -*-
from __future__ import annotations

from cn_regional_sender_context import (
    build_regional_sender_instructions_pl,
    resolve_discovery_wojewodztwo,
    wojewodztwo_primary_city_pl,
)


def test_resolve_discovery_prefers_discovery_bundesland():
    key = resolve_discovery_wojewodztwo(
        {"discovery_bundesland": "slaskie", "bundesland": "malopolskie"}
    )
    assert key == "slaskie"


def test_primary_city_mazowieckie():
    assert wojewodztwo_primary_city_pl("mazowieckie") == "Warszawa"


def test_regional_sender_mentions_construction_block():
    text = build_regional_sender_instructions_pl(
        "slaskie",
        sender_name="Maksym Swinczak",
        sender_phone="516513965",
        construction_project_block="OBIEKT BUDOWY\n• Adres: Warszawa, ul. Odkryta 10",
    )
    assert "REGION DISCOVERY" in text
    assert "Katowice" in text or "slaskie" in text
    assert "OBIEKT BUDOWY" in text
    assert "516513965" not in text
    assert "swinczakdata" not in text.lower()
    assert "Maksym Swinczak" in text
    assert "dystrybutor" in text.lower() or "importer" in text.lower() or "eksporter" in text.lower()


def test_regional_sender_is_chinese_exporter_not_fake_pl_builder():
    text = build_regional_sender_instructions_pl(
        "slaskie",
        sender_name="Maksym Swinczak",
        sender_phone="516513965",
    )
    assert "NIE wymyślaj" in text or "fikcyj" in text.lower()
    assert "Warszawa" in text or "Kraków" in text or "Polska" in text or "odbiorc" in text.lower()
