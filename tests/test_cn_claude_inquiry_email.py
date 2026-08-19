# -*- coding: utf-8 -*-
from __future__ import annotations

import logging

import pytest

from cn_claude_prompts import build_personalized_inquiry_email_prompt_zh
from cn_materialy_inquiry_email_zh import DEFAULT_INQUIRY_PHONE_CN, DEFAULT_INQUIRY_SENDER_NAME_CN


def test_prompt_chinese_personalization():
    p = build_personalized_inquiry_email_prompt_zh(
        company_name="佛山瓷砖经销商",
        website="https://foshan-tile.cn",
        wojewodztwo="zhejiang",
        materials="瓷砖, 卫浴",
        page_snippet="瓷砖批发 义乌",
        discovery_wojewodztwo="zhejiang",
    )
    assert "佛山瓷砖经销商" in p
    assert "chiń" in p.lower() or "中国" in p
    assert "瓷砖" in p or "卫浴" in p
    assert "OBIEKT BUDOWY" in p
    assert "REGION DISCOVERY" in p


def test_prompt_no_mfg_branding(monkeypatch):
    monkeypatch.setenv("MAIL_SENDER_NAME", "Testowy Menedzer")
    monkeypatch.setenv("INQUIRY_COMPANY_NAME", " ")
    monkeypatch.setenv("INQUIRY_PHONE", "516513965")
    monkeypatch.setenv("INQUIRY_WEBSITE", " ")
    p = build_personalized_inquiry_email_prompt_zh(company_name="Test Sp. z o.o.")
    lowered = p.lower()
    assert "mfg" not in lowered
    assert "fliesen" not in lowered
    assert "moderner" not in lowered


def test_prompt_includes_pl_phone_and_sender(monkeypatch):
    from cn_materialy_inquiry_email_zh import inquiry_phone, inquiry_sender_name

    monkeypatch.setenv("MAIL_SENDER_NAME", "Maksym Swinczak Tel.+4915223655399")
    monkeypatch.setenv("INQUIRY_PHONE", "+49 1522 3655 399")
    monkeypatch.setenv("INQUIRY_COMPANY_NAME", " ")
    monkeypatch.setenv("INQUIRY_WEBSITE", " ")
    p = build_personalized_inquiry_email_prompt_zh(
        company_name="Test Sp. z o.o.",
        discovery_wojewodztwo="guangdong",
    )
    assert DEFAULT_INQUIRY_PHONE_CN in p
    assert inquiry_sender_name() in p
    assert DEFAULT_INQUIRY_SENDER_NAME_CN in p
    assert inquiry_phone() == DEFAULT_INQUIRY_PHONE_CN
    assert "1522" not in p


def test_prompt_forbids_attachments():
    p = build_personalized_inquiry_email_prompt_zh(company_name="Test")
    assert "załącznik" in p.lower() or "plik" in p.lower()


def test_prompt_requires_json_output():
    p = build_personalized_inquiry_email_prompt_zh(company_name="Test")
    assert '"subject"' in p
    assert '"body"' in p


def test_prompt_requires_paragraph_layout():
    p = build_personalized_inquiry_email_prompt_zh(company_name="Test")
    assert "FORMAT LISTU" in p
    assert "\\n\\n" in p
    assert "此致敬礼" in p


def test_cached_inquiry_without_construction_address_is_ignored():
    from cn_claude_inquiry_email import _cached_inquiry_is_usable

    assert not _cached_inquiry_is_usable(
        {"subject": "Test", "body": "Treść bez adresu budowy."}
    )


def test_cached_inquiry_with_verified_address_is_reused():
    from cn_claude_inquiry_email import _cached_inquiry_is_usable
    from cn_regional_construction_refs import pick_construction_project

    project = pick_construction_project("zhejiang", seed="demo")
    body = f"Budujemy obiekt pod adresem {project.address_pl}."
    assert _cached_inquiry_is_usable(
        {
            "subject": "Test",
            "body": body,
            "construction_address": project.address_pl,
        }
    )


def test_require_claude_raises_without_api_key(monkeypatch):
    from cn_claude_inquiry_email import claude_generate_inquiry_email_zh

    monkeypatch.setattr(
        "cn_claude_inquiry_email.get_anthropic_api_key",
        lambda: "",
    )
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        claude_generate_inquiry_email_zh(
            "Test",
            logging.getLogger("test"),
            {},
            require=True,
        )
