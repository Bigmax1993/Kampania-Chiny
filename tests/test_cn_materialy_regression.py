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
    MATERIAL_CATEGORIES_ROTATION,
    MATERIAL_CATEGORY_KEYWORDS,
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
        self.assertEqual(build_region_suffix(list(ALL_PROVINCES)), "Polska")
        self.assertEqual(build_region_suffix(["mazowieckie", "malopolskie"]), "Polska MZ MA")

    def test_discovery_terms_polish_distributors(self):
        terms = build_discovery_terms(["mazowieckie"], max_terms=10)
        self.assertGreaterEqual(len(terms), 5)
        joined = " ".join(terms)
        self.assertIn("dystrybutor", joined)
        self.assertTrue("Warszawa" in joined or "importer" in joined or "oficjalny" in joined)

    def test_material_keywords_steel_doors_sanitary(self):
        rotation = " ".join(MATERIAL_CATEGORIES_ROTATION).lower()
        keywords = " ".join(MATERIAL_CATEGORY_KEYWORDS).lower()
        for needle in (
            "stal konstrukcyjna",
            "stal nierdzewna",
            "drzwi",
            "kabiny prysznicowe",
            "instalacje sanitarne",
            "armatura łazienkowa",
        ):
            self.assertIn(needle, rotation)
            self.assertIn(needle, keywords)
        terms = " ".join(build_discovery_terms(["mazowieckie"], max_terms=80)).lower()
        self.assertTrue("stal" in terms)
        self.assertTrue("drzwi" in terms)
        self.assertTrue("prysznic" in terms or "sanitar" in terms or "łazienk" in terms)

    def test_discovery_waves_exported(self):
        self.assertGreaterEqual(len(SERPER_DISCOVERY_FALLBACK_TERMS), 5)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_BROAD_TERMS), 10)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_LANDKREIS_TERMS), 5)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_PLACES_TERMS), 5)
        self.assertGreaterEqual(len(SERPER_DISCOVERY_TERMS), 100)


class SerperConfigRegression(unittest.TestCase):
    def test_serper_pl_locale(self):
        self.assertEqual(scraper.SERPER_COUNTRY, "pl")
        self.assertEqual(scraper.SERPER_LANGUAGE, "pl")
        self.assertEqual(scraper.COUNTRY_RESTRICTION, "PL")

    def test_max_discovery_terms_scale(self):
        self.assertGreaterEqual(default_max_discovery_terms_for(list(ALL_PROVINCES)), 1000)


class SupplierFilterRegression(unittest.TestCase):
    def test_accepts_building_supplier(self):
        self.assertTrue(
            is_valid_retail_store_builder_contact(
                email="info@plytki-dystrybucja.pl",
                url="https://www.plytki-dystrybucja.pl/",
                name="Warszawski Dystrybutor Płytek Sp. z o.o.",
                text="płytki ceramika importer dystrybutor katalog cennik asortyment",
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

    def test_accepts_steel_and_bathroom_distributors(self):
        self.assertTrue(
            is_valid_retail_store_builder_contact(
                email="biuro@stal-import.pl",
                url="https://www.stal-import.pl/",
                name="Śląski Dystrybutor Stali Sp. z o.o.",
                text="stal nierdzewna blacha stalowa importer dystrybutor katalog cennik",
            )
        )
        self.assertTrue(
            is_valid_retail_store_builder_contact(
                email="info@drzwi-hurt.pl",
                url="https://www.drzwi-hurt.pl/",
                name="Poznański Dystrybutor Drzwi Sp. z o.o.",
                text="drzwi wewnętrzne drzwi stalowe kabiny prysznicowe dystrybutor hurt asortyment",
            )
        )
        self.assertTrue(
            is_valid_retail_store_builder_contact(
                email="kontakt@lazienki-import.pl",
                url="https://www.lazienki-import.pl/",
                name="Krakowski Importer Armatury Łazienkowej Sp. z o.o.",
                text="instalacje sanitarne armatura łazienkowa importer dystrybutor katalog",
            )
        )

    def test_loose_serper_candidate(self):
        self.assertTrue(
            is_loose_serper_discovery_candidate(
                url="https://plytki-dystrybucja.pl",
                name="Warszawski Dystrybutor Płytek",
                text="płytki dystrybutor importer",
            )
        )

    def test_serper_only_pending(self):
        self.assertTrue(
            is_serper_only_pending_candidate(
                name="Warszawski Dystrybutor Płytek",
                url="https://plytki-dystrybucja.pl",
                text="płytki dystrybutor importer",
            )
        )


class EmailBrandingRegression(unittest.TestCase):
    def test_default_phone(self):
        self.assertEqual(DEFAULT_INQUIRY_PHONE_CN, "516513965")
        self.assertNotIn("516513965", build_inquiry_signature_zh())
        self.assertNotIn("swinczakdata", build_inquiry_signature_zh().lower())

    def test_polish_template(self):
        body = build_fixed_material_inquiry_zh()
        self.assertIn("Szanowni Państwo", body)
        self.assertIn("dystrybutor", body)
        self.assertIn("drzwi", body)
        self.assertIn("kabiny prysznicowe", body)
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


class NipCrawlRegression(unittest.TestCase):
    def test_impressum_url_detects_pl_kontakt(self):
        self.assertTrue(scraper._is_impressum_url("https://firma.pl/kontakt"))
        self.assertTrue(scraper._is_impressum_url("https://firma.pl/o-firmie"))
        self.assertTrue(scraper._is_impressum_url("https://firma.pl/dane-firmy"))
        self.assertFalse(scraper._is_impressum_url("https://firma.pl/oferta/plytki"))

    def test_merge_contacts_keeps_nip_beyond_snippet_limit(self):
        from website_full_crawl import WebsiteCrawlResult

        homepage = "Dystrybutor płytek " + ("katalog oferta " * 500)
        kontakt = (
            "POL-SKONE Sp. z o.o. ul. Testowa 1, 20-328 Lublin "
            "NIP: 123-456-32-18 e-mail: biuro@firma.pl"
        )
        crawl = WebsiteCrawlResult(
            pages={
                "https://firma.pl": {"page_text": homepage, "emails": [], "phones": []},
                "https://firma.pl/kontakt": {
                    "page_text": kontakt,
                    "emails": ["biuro@firma.pl"],
                    "phones": [],
                },
            },
            urls_visited=["https://firma.pl", "https://firma.pl/kontakt"],
        )
        collected = scraper.merge_contacts_from_crawl(crawl, "https://firma.pl")
        self.assertEqual(collected.get("nip"), "123-456-32-18")
        self.assertIn("NIP", collected.get("page_snippet") or "")

    def test_prowincje_sheet_is_region_index_only(self):
        row = {
            "nazwa": "Hurtownia Beta",
            "email_target": "b@beta.pl",
            "telefon": "500100200",
            "bundesland": "lubelskie",
            "adres": "ul. Testowa 1, 20-328 Lublin",
            "kategoria": "drzwi dystrybutor",
            "nip": "123-456-32-18",
            "url": "https://beta.pl",
            "www": "https://beta.pl",
        }
        kontakte = scraper.row_to_excel_kontakte_columns(row, "b@beta.pl")
        prowincje = scraper.row_to_excel_wojewodztwa_columns(row)
        self.assertEqual(
            set(prowincje.keys()),
            {"Name of Company", "Region", "Localisation", "URL"},
        )
        self.assertIn("Tax Identification Number", kontakte)
        self.assertIn("E-Mail", kontakte)
        self.assertNotIn("Tax Identification Number", prowincje)
        self.assertNotIn("E-Mail", prowincje)
        self.assertEqual(kontakte["Tax Identification Number"], "123-456-32-18")
        self.assertIn("Lublin", prowincje["Region"])


class CampaignPathsRegression(unittest.TestCase):
    def test_cn_output_paths_basename(self):
        paths = campaign_output_paths(ROOT, "cn_materialy")
        self.assertTrue(str(paths["cache_file"]).endswith("cn_materialy_cache.json"))
        self.assertTrue(str(paths["output_file"]).endswith("cn_materialy_kontakte.xlsx"))

    def test_cn_drive_folder_id(self):
        self.assertEqual(GOOGLE_DRIVE_CN_FOLDER_ID, "1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC")


if __name__ == "__main__":
    unittest.main(verbosity=2)
