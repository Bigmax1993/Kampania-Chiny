# -*- coding: utf-8 -*-
from __future__ import annotations

from cn_regional_construction_refs import (
    address_present_in_body,
    extract_city_from_address_pl,
    inject_construction_project_context,
    pick_construction_project,
)


def test_pick_project_for_zhejiang_has_real_address():
    project = pick_construction_project("zhejiang", seed="supplier-a")
    assert "杭州" in project.address_pl or "义乌" in project.address_pl or "宁波" in project.address_pl
    assert "路" in project.address_pl or "街" in project.address_pl or "大道" in project.address_pl


def test_address_present_detects_full_address():
    project = pick_construction_project("guangdong", seed="x")
    body = f"我们正在建设，地址：{project.address_pl}。"
    assert address_present_in_body(body, project.address_pl)


def test_inject_adds_verified_address_when_missing():
    project = pick_construction_project("jiangsu", seed="supplier-b")
    body = "尊敬的先生/女士：\n\n请提供价格表。\n\n此致敬礼\nTest"
    out = inject_construction_project_context(body, project)
    assert address_present_in_body(out, project.address_pl)
    assert project.name_pl in out


def test_extract_city_from_address():
    assert "佛山" in extract_city_from_address_pl("佛山市禅城区季华西路12号")
    assert extract_city_from_address_pl("杭州市江干区钱江路1366号").startswith("杭州")


def test_pick_project_prefers_supplier_city_in_province():
    project = pick_construction_project(
        "guangdong",
        seed="demo",
        prefer_city="佛山",
    )
    assert "佛山" in project.address_pl


def test_pick_project_for_guangzhou_supplier_uses_guangzhou_address():
    project = pick_construction_project(
        "guangdong",
        seed="demo",
        prefer_city="广州",
    )
    assert "广州" in project.address_pl
