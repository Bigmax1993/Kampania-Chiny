# -*- coding: utf-8 -*-
from __future__ import annotations

import logging

import pytest

from cn_claude_prompts import build_personalized_inquiry_email_prompt_zh
from cn_materialy_inquiry_email_zh import DEFAULT_INQUIRY_PHONE_CN, DEFAULT_INQUIRY_SENDER_NAME_CN


def test_prompt_polish_personalization():
    p = build_personalized_inquiry_email_prompt_zh(
        company_name="Warszawski Dystrybutor Płytek",
        website="https://plytki-dystrybucja.pl",
        wojewodztwo="slaskie",
        materials="płytki, ceramika",
        page_snippet="płytki importer Katowice",
        discovery_wojewodztwo="slaskie",
    )
    assert "Warszawski Dystrybutor Płytek" in p
    assert "dystrybutor" in p.lower() or "polsk" in p.lower()
    assert "płytki" in p or "ceramika" in p
    assert "OBIEKT BUDOWY" in p
    assert "REGION DISCOVERY" in p
    assert "nazwa odbiorcy" in p.lower() or "MUSI pojawić się nazwa" in p


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


def test_prompt_omits_phone_and_website(monkeypatch):
    from cn_materialy_inquiry_email_zh import inquiry_phone, inquiry_sender_name

    monkeypatch.setenv("MAIL_SENDER_NAME", "Maksym Swinczak Tel.+4915223655399")
    monkeypatch.setenv("INQUIRY_PHONE", "+49 1522 3655 399")
    monkeypatch.setenv("INQUIRY_COMPANY_NAME", " ")
    monkeypatch.setenv("INQUIRY_WEBSITE", " ")
    p = build_personalized_inquiry_email_prompt_zh(
        company_name="Test Sp. z o.o.",
        discovery_wojewodztwo="mazowieckie",
    )
    assert "516513965" not in p
    assert "swinczakdata" not in p.lower()
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
    assert "Z poważaniem" in p


def test_cached_inquiry_without_construction_address_is_ignored():
    from cn_claude_inquiry_email import _cached_inquiry_is_usable

    assert not _cached_inquiry_is_usable(
        {"subject": "Test", "body": "Treść bez adresu budowy."}
    )


def test_cached_inquiry_with_verified_address_is_reused():
    from cn_claude_inquiry_email import _cached_inquiry_is_usable
    from cn_regional_construction_refs import pick_construction_project

    project = pick_construction_project("slaskie", seed="demo")
    body = (
        f"Zwracam się do Warszawski Dystrybutor Płytek. "
        f"Budujemy obiekt pod adresem {project.address_pl}."
    )
    assert _cached_inquiry_is_usable(
        {
            "subject": "Test",
            "body": body,
            "construction_address": project.address_pl,
        },
        "Warszawski Dystrybutor Płytek Sp. z o.o.",
    )


def test_cached_generic_body_rejected_when_company_missing():
    from cn_claude_inquiry_email import _cached_inquiry_is_usable
    from cn_regional_construction_refs import pick_construction_project

    project = pick_construction_project("slaskie", seed="demo")
    body = f"Budujemy obiekt pod adresem {project.address_pl}."
    assert not _cached_inquiry_is_usable(
        {
            "subject": "Test",
            "body": body,
            "construction_address": project.address_pl,
        },
        "Warszawski Dystrybutor Płytek Sp. z o.o.",
    )


def test_body_mentions_recipient_company():
    from cn_claude_inquiry_email import body_mentions_recipient_company

    assert body_mentions_recipient_company(
        "Zwracam się do Alfa Ceramika w sprawie płytek.",
        "Alfa Ceramika Sp. z o.o.",
    )
    assert not body_mentions_recipient_company(
        "Szukamy dystrybutora w Polsce.",
        "Alfa Ceramika Sp. z o.o.",
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
