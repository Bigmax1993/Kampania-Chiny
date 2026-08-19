# -*- coding: utf-8 -*-
"""
Testy integracyjne kampanii CN — smoke, run_config, prompty Claude, workflowy.

  python -m pytest tests/test_cn_materialy_integration.py -v
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

import pytest

import cn_materialy_scraper as scraper
from cn_claude_prompts import build_page_verify_prompt, build_personalized_inquiry_email_prompt_zh
from cn_province_keywords import configure_campaign_provinces
from cn_province_rotation import apply_rotation_to_module

ROOT = Path(__file__).resolve().parent.parent
_LOGGER = logging.getLogger("test_cn_materialy_integration")

PL_WORKFLOWS = (
    "cn_materialy_pi.yml",
    "cn_materialy_thu.yml",
    "cn_materialy_mon.yml",
    "cn_materialy_tue.yml",
    "cn_materialy_fri.yml",
    "sync-google-drive-cn.yml",
)

EXPECTED_CN_CRONS = {
    "cn_materialy_pi.yml": {
        "0 20 * * 1",
        "0 20 * * 2",
        "0 21 * * 3",
        "0 21 * * 4",
        "0 19 * * 5",
    },
    "cn_materialy_thu.yml": {"30 9 * * 0"},
    "sync-google-drive-cn.yml": {"0 10 * * 1"},
    "cn_materialy_mon.yml": {"0 11 * * 1"},
    "cn_materialy_tue.yml": {"0 14 * * 1"},
    "cn_materialy_fri.yml": {"0 14 * * 2"},
}


def test_scraper_smoke_test_entrypoint():
    scraper._run_smoke_tests()


def test_run_config_guangdong_test_loads():
    from scraper_run_config import load_run_config_file

    data = load_run_config_file("run_config/cn_guangdong_test.json", ROOT)
    assert "guangdong" in data.get("active_bundeslaender", [])


def test_apply_rotation_configures_module(tmp_path):
    mod = type("M", (), {})()
    woj, state, path = apply_rotation_to_module(mod, tmp_path, max_discovery_terms=40)
    assert woj in scraper.CAMPAIGN_ACTIVE_BUNDESLAENDER
    assert len(mod.SERPER_DISCOVERY_TERMS) <= 40
    assert path.parent == tmp_path


def test_configure_wojewodztwa_sets_discovery_waves():
    mod = type("M", (), {})()
    configure_campaign_provinces(mod, ["guangdong"], max_discovery_terms=50)
    assert mod.SERPER_DISCOVERY_TERMS
    assert mod.SERPER_DISCOVERY_FALLBACK_TERMS
    assert mod.SERPER_DISCOVERY_BROAD_TERMS
    assert mod.SERPER_DISCOVERY_LANDKREIS_TERMS
    assert mod.SERPER_DISCOVERY_PLACES_TERMS
    assert mod.SERPER_DISCOVERY_REGION_SUFFIX == "中国"


def test_page_verify_prompt_cn_context():
    p = build_page_verify_prompt(
        "佛山建材经销商",
        "https://foshan-tile.cn",
        "瓷砖 卫浴 批发 经销商 佛山",
    )
    assert "is_gu" in p
    assert "经销商" in p or "中国" in p


def test_claude_inquiry_prompt_chinese_and_phone():
    p = build_personalized_inquiry_email_prompt_zh(
        company_name="佛山建材经销商",
        wojewodztwo="guangdong",
        discovery_wojewodztwo="guangdong",
    )
    assert "chiń" in p.lower() or "中国" in p
    assert "516513965" in p
    assert "JSON" in p
    assert "FORMAT LISTU" in p
    assert "OBIEKT BUDOWY" in p
    assert "REGION DISCOVERY" in p
    assert "\\n\\n" in p
    assert "此致敬礼" in p
    assert "analizy rynku" not in p.lower()
    assert "benchmark" not in p.lower()


@pytest.mark.parametrize("workflow_file", PL_WORKFLOWS)
def test_cn_workflow_yaml_valid(workflow_file: str):
    path = ROOT / ".github" / "workflows" / workflow_file
    assert path.is_file(), f"brak {workflow_file}"
    text = path.read_text(encoding="utf-8")
    assert "jobs:" in text
    assert "runs-on:" in text
    assert "CN" in text or "cn_materialy" in text


@pytest.mark.parametrize("workflow_file", PL_WORKFLOWS)
def test_cn_workflow_cron_schedule(workflow_file: str):
    path = ROOT / ".github" / "workflows" / workflow_file
    text = path.read_text(encoding="utf-8")
    crons = set(re.findall(r'cron:\s*"([^"]+)"', text))
    if workflow_file not in EXPECTED_CN_CRONS:
        return
    assert crons == EXPECTED_CN_CRONS[workflow_file]


def test_cn_discovery_workflow_uses_pl_scraper():
    text = (ROOT / ".github" / "workflows" / "cn_materialy_pi.yml").read_text(encoding="utf-8")
    assert "cn_materialy_scraper.py" in text
    assert "run_config/cn_materialy.json" in text
    assert "--rotate-province" in text
    assert "cn-pipeline" in text


def test_sync_drive_pl_uses_pl_campaign():
    text = (ROOT / ".github" / "workflows" / "sync-google-drive-cn.yml").read_text(encoding="utf-8")
    assert "GDRIVE_FOLDER_ID_CN" in text
    assert "--campaign cn" in text


def test_sunday_backfill_verifies_excel_from_json_and_uploads_drive():
    text = (ROOT / ".github" / "workflows" / "cn_materialy_thu.yml").read_text(encoding="utf-8")
    assert "verify_excel_from_json.py" in text
    assert "gdrive_upload_wyniki.py" in text
    assert "GDRIVE_FOLDER_ID_CN" in text
    assert "--campaign cn" in text
