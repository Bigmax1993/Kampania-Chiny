# -*- coding: utf-8 -*-
"""
Testy regresyjne kampanii CN — słowa kluczowe, filtry, maile, rotacja prowincji.

  python -m unittest tests.test_cn_materialy_regression -v
  python -m pytest tests/test_cn_materialy_regression.py -v
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cn_materialy_scraper as scraper
from campaign_data_paths import GOOGLE_DRIVE_CN_FOLDER_ID, campaign_output_paths
from cn_materialy_inquiry_email_zh import (
    DEFAULT_INQUIRY_PHONE_CN,
    build_fixed_material_inquiry_zh,
    build_inquiry_signature_zh,
)
from cn_materialy_supplier_filter import (
    is_loose_serper_discovery_candidate,
    is_serper_only_pending_candidate,
    is_valid_retail_store_builder_contact,
)
from cn_province_keywords import (
    ALL_PROVINCES,
    SERPER_DISCOVERY_BROAD_TERMS,
    SERPER_DISCOVERY_FALLBACK_TERMS,
    SERPER_DISCOVERY_LANDKREIS_TERMS,
    SERPER_DISCOVERY_PLACES_TERMS,
    SERPER_DISCOVERY_TERMS,
    build_discovery_terms,
    build_region_suffix,
    default_max_discovery_terms_for,
)
from cn_province_rotation import (
    PROVINCE_ROTATION_ORDER,
    commit_rotation_after_run,
    load_rotation_state,
    peek_next_province,
    rotation_state_path,
)


class WojewodztwoCoverageRegression(unittest.TestCase):
    def test_all_wojewodztwa_configured(self):
        self.assertEqual(len(ALL_PROVINCES), 16)
        self.assertEqual(len(scraper.CAMPAIGN_ACTIVE_BUNDESLAENDER), 16)

    def test_countrywide_region_suffix(self):
        self.assertEqual(build_region_suffix(list(ALL_PROVINCES)), "中国")
        self.assertEqual(build_region_suffix(["guangdong", "zhejiang"]), "中国 GD ZJ")

    def test_discovery_terms_chinese(self):
        terms = build_discovery_terms(["guangdong"], max_terms=10)
        self.assertGreaterEqual(len(terms), 5)
        joined = " ".join(terms)
        self.assertIn("经销商", joined)
        self.assertIn("佛山", joined)

    def test_discovery_waves_exported(self):
        self.assertGreaterEqual(len(SERPER_DISCOVERY_FALLBACK_TERMS), 5)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_BROAD_TERMS), 10)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_LANDKREIS_TERMS), 5)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_PLACES_TERMS), 5)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_TERMS), 100)


class SerperConfigRegression(unittest.TestCase):
    def test_serper_cn_locale(self):
        self.assertEqual(scraper.SERPER_COUNTRY, "cn")
        self.assertEqual(scraper.SERPER_LANGUAGE, "zh-cn")
        self.assertEqual(scraper.COUNTRY_RESTRICTION, "CN")

    def test_max_discovery_terms_scale(self):
        self.assertGreaterEqual(default_max_discovery_terms_for(list(ALL_PROVINCES)), 1000)


class SupplierFilterRegression(unittest.TestCase):
    def test_accepts_building_supplier(self):
        self.assertTrue(
            is_valid_retail_store_builder_contact(
                email="info@foshan-tile.cn",
                url="https://www.foshan-tile.cn/",
                name="佛山市建材经销商有限公司",
                text="瓷砖 卫浴 批发 经销商 产品目录 价格表 现货",
            )
        )

    def test_rejects_interior_design(self):
        self.assertFalse(
            is_valid_retail_store_builder_contact(
                email="info@design.pl",
                url="https://design.pl",
                name="Wykończenia wnętrz",
                text="remont mieszkań pod klucz",
            )
        )

    def test_loose_serper_candidate(self):
        self.assertTrue(
            is_loose_serper_discovery_candidate(
                url="https://foshan-tile.cn",
                name="佛山建材经销商",
                text="瓷砖 批发 经销商",
            )
        )

    def test_serper_only_pending(self):
        self.assertTrue(
            is_serper_only_pending_candidate(
                name="佛山瓷砖经销商",
                url="https://foshan-tile.cn",
                text="瓷砖 批发 经销商",
            )
        )


class EmailBrandingRegression(unittest.TestCase):
    def test_default_phone(self):
        self.assertEqual(DEFAULT_INQUIRY_PHONE_CN, "516513965")
        self.assertIn("516513965", build_inquiry_signature_zh())

    def test_chinese_template(self):
        body = build_fixed_material_inquiry_zh()
        self.assertIn("尊敬的", body)
        self.assertIn("经销商", body)
        self.assertNotIn("+380", body)

    @patch("mail_transport.send_smtp_email")
    @patch("scraper_env.get_mail_password", return_value="secret")
    @patch("scraper_env.get_mail_user", return_value="test@gmail.com")
    def test_send_email_no_attachments(self, _u, _p, mock_send):
        import logging

        mock_send.return_value = (True, "ok")
        ok, _ = scraper.send_email_cn_materialy(
            "kontakt@hurt.pl",
            "Zapytanie o dostawę materiałów budowlanych",
            build_fixed_material_inquiry_zh(),
            logging.getLogger("test"),
        )
        self.assertTrue(ok)
        self.assertEqual(mock_send.call_args.kwargs.get("attachment_paths"), [])


class WojewodztwoRotationRegression(unittest.TestCase):
    def test_rotation_order_length(self):
        self.assertEqual(len(PROVINCE_ROTATION_ORDER), 16)
        self.assertEqual(peek_next_province(), PROVINCE_ROTATION_ORDER[0])

    def test_commit_advances_index(self):
        tmp = Path(tempfile.mkdtemp())
        path = rotation_state_path(tmp)
        state = load_rotation_state(path)
        woj = peek_next_province(state)
        nxt = commit_rotation_after_run(path, state, woj)
        self.assertIn(nxt, PROVINCE_ROTATION_ORDER)
        self.assertNotEqual(nxt, woj)


class CampaignPathsRegression(unittest.TestCase):
    def test_cn_output_paths_basename(self):
        paths = campaign_output_paths(ROOT, "cn_materialy")
        self.assertTrue(str(paths["cache_file"]).endswith("cn_materialy_cache.json"))
        self.assertTrue(str(paths["output_file"]).endswith("cn_materialy_kontakte.xlsx"))

    def test_cn_drive_folder_id(self):
        self.assertEqual(GOOGLE_DRIVE_CN_FOLDER_ID, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
