# -*- coding: utf-8 -*-
from __future__ import annotations

from cn_regional_construction_refs import (
    address_present_in_body,
    extract_city_from_address_pl,
    inject_construction_project_context,
    pick_construction_project,
)


def test_pick_buyer_project_is_in_poland():
    project = pick_construction_project("wielkopolskie", seed="supplier-a")
    assert (
        "Warszawa" in project.address_pl
        or "Kraków" in project.address_pl
        or "Katowice" in project.address_pl
    )
    assert "ul." in project.address_pl


def test_address_present_detects_full_address():
    project = pick_construction_project("mazowieckie", seed="x")
    body = f"Budujemy obiekt pod adresem {project.address_pl}."
    assert address_present_in_body(body, project.address_pl)


def test_inject_adds_verified_address_when_missing():
    project = pick_construction_project("malopolskie", seed="supplier-b")
    body = "Szanowni Państwo,\n\nProszę o kontakt.\n\nZ poważaniem\nTest"
    out = inject_construction_project_context(body, project)
    assert address_present_in_body(out, project.address_pl)
    assert project.name_pl in out


def test_extract_city_from_address():
    assert extract_city_from_address_pl("Warszawa, ul. Odkryta 10") == "Warszawa"
    assert extract_city_from_address_pl("Kraków, ul. Puszkarska 7H") == "Kraków"


def test_pick_project_prefers_warszawa():
    project = pick_construction_project(
        "mazowieckie",
        seed="demo",
        prefer_city="Warszawa",
    )
    assert "Warszawa" in project.address_pl


def test_pick_project_prefers_krakow():
    project = pick_construction_project(
        "mazowieckie",
        seed="demo",
        prefer_city="Kraków",
    )
    assert "Kraków" in project.address_pl
