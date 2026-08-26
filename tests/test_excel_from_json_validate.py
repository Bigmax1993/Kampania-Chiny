# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.excel_from_json_validate import (
    fill_export_from_json,
    find_excel_gaps,
    json_contact_has_needed_data,
    merge_contacts_maps,
    verify_and_fill_until_complete,
)


class JsonNeededDataTests(unittest.TestCase):
    def test_passes_email(self):
        self.assertTrue(
            json_contact_has_needed_data(
                "https://firma.pl",
                {"email_target": "a@firma.pl", "company_name_clean": ""},
            )
        )

    def test_passes_name(self):
        self.assertTrue(
            json_contact_has_needed_data(
                "https://hurt.pl", {"company_name_clean": "Hurtownia X"}
            )
        )

    def test_rejects_empty(self):
        self.assertFalse(json_contact_has_needed_data("https://x.pl", {}))
        self.assertFalse(json_contact_has_needed_data("", {"company_name_clean": "X"}))

    def test_accepts_address_only_and_rejects_junk(self):
        self.assertTrue(
            json_contact_has_needed_data(
                "https://hurt.pl",
                {"full_address": "ul. Testowa 12, Warszawa"},
            )
        )
        self.assertFalse(
            json_contact_has_needed_data(
                "https://olx.pl/oferta",
                {"company_name_clean": "Ogłoszenie", "email_target": "a@olx.pl"},
            )
        )
        self.assertFalse(
            json_contact_has_needed_data(
                "https://firma.pl",
                {"company_name_clean": "Kontakt", "email_target": "noreply@firma.pl"},
            )
        )
        self.assertFalse(
            json_contact_has_needed_data(
                "https://firma.pl",
                {
                    "full_address": (
                        "W naszym asortymencie znajdziecie Państwo wysokiej jakości materiały"
                    )
                },
            )
        )

    def test_fill_uses_loose_address_and_skips_marketing(self):
        contacts = {
            "https://a.pl": {
                "company_name_clean": "Hurtownia Materiałów Warszawa",
                "full_address": "ul. Przemysłowa 12, Warszawa",
                "page_snippet": "NIP: 1234563218 dystrybutor płytek",
            }
        }
        excel = [
            {
                "URL": "https://a.pl",
                "Name of Company": "",
                "Line of business": "",
                "Company website": "",
                "E-Mail": "",
                "Phone number": "",
                "Region": "",
                "Localisation": "",
                "Postcode": "",
                "Tax Identification Number": "",
            }
        ]
        filled, n = fill_export_from_json(contacts, excel)
        self.assertGreater(n, 0)
        row = filled[0]
        self.assertEqual(row["Name of Company"], "Hurtownia Materiałów Warszawa")
        self.assertIn("St.", row["Localisation"])
        self.assertIn("Warsaw", row["Localisation"])
        self.assertEqual(row["Tax Identification Number"], "1234563218")
        self.assertTrue(row["Line of business"])

    def test_fill_postcode_from_address(self):
        contacts = {
            "https://a.pl": {
                "company_name_clean": "Alpha",
                "full_address": "ul. Testowa 1, 00-001 Warszawa",
            }
        }
        excel = [
            {
                "URL": "https://a.pl",
                "Name of Company": "Alpha",
                "Localisation": "",
                "Postcode": "",
            }
        ]
        filled, n = fill_export_from_json(contacts, excel)
        self.assertGreater(n, 0)
        self.assertEqual(filled[0]["Postcode"], "00-001")
        from_loc = [
            {
                "URL": "https://b.pl",
                "Name of Company": "Beta",
                "Localisation": "St. Testowa 1, 05-800 Warsaw",
                "Postcode": "",
            }
        ]
        filled2, n2 = fill_export_from_json({}, from_loc)
        self.assertGreater(n2, 0)
        self.assertEqual(filled2[0]["Postcode"], "05-800")


class MergeAndFillLoopTests(unittest.TestCase):
    def test_merge_prefers_richer_email(self):
        a = {"https://a.pl": {"company_name_clean": "A"}}
        b = {"https://a.pl": {"company_name_clean": "A", "email_target": "a@a.pl"}}
        merged = merge_contacts_maps(a, b)
        self.assertEqual(merged["https://a.pl"]["email_target"], "a@a.pl")

    def test_fill_missing_row_and_empty_email(self):
        contacts = {
            "https://a.pl": {
                "company_name_clean": "Alpha",
                "email_target": "a@a.pl",
                "phones_found": "500100200",
            },
            "https://b.pl": {
                "company_name_clean": "Beta",
                "email_target": "b@b.pl",
            },
        }
        excel = [
            {
                "URL": "https://a.pl",
                "Name of Company": "Alpha",
                "Line of business": "",
                "Company website": "",
                "E-Mail": "",
                "Phone number": "",
                "Region": "",
                "Localisation": "",
                "Postcode": "",
                "Tax Identification Number": "",
            }
        ]
        gaps = find_excel_gaps(contacts, excel)
        reasons = {g["url"]: g["reason"] for g in gaps}
        self.assertEqual(reasons["https://a.pl"], "empty_columns")
        self.assertEqual(reasons["https://b.pl"], "missing_row")
        filled, n = fill_export_from_json(contacts, excel)
        self.assertGreater(n, 0)
        done, gaps2, rounds = verify_and_fill_until_complete(contacts, filled)
        self.assertEqual(gaps2, [])
        self.assertGreaterEqual(rounds, 0)
        by_url = {r["URL"]: r for r in done}
        self.assertEqual(by_url["https://a.pl"]["E-Mail"], "a@a.pl")
        self.assertEqual(by_url["https://a.pl"]["Phone number"], "500100200")
        self.assertEqual(by_url["https://b.pl"]["E-Mail"], "b@b.pl")

    def test_second_json_reload_fills_fields_added_later(self):
        excel = [
            {
                "URL": "https://a.pl",
                "Name of Company": "Alpha",
                "Line of business": "",
                "Company website": "",
                "E-Mail": "",
                "Phone number": "",
                "Region": "",
                "Localisation": "",
                "Postcode": "",
                "Tax Identification Number": "",
            }
        ]
        first = {"https://a.pl": {"company_name_clean": "Alpha"}}
        filled, _n1 = fill_export_from_json(first, excel)
        self.assertEqual(filled[0]["E-Mail"], "")
        self.assertEqual(filled[0]["Phone number"], "")
        second = {
            "https://a.pl": {
                "company_name_clean": "Alpha",
                "email_target": "a@a.pl",
                "phones_found": "500100200",
            }
        }
        filled, n2 = fill_export_from_json(second, filled)
        self.assertGreater(n2, 0)
        self.assertEqual(filled[0]["E-Mail"], "a@a.pl")
        self.assertEqual(filled[0]["Phone number"], "500100200")


class DoubleJsonReloadTests(unittest.TestCase):
    def test_verify_reloads_json_from_disk_twice(self):
        import tempfile
        from scripts import verify_excel_from_json as v

        loads: list[dict] = []
        first = {"https://a.pl": {"company_name_clean": "Alpha"}}
        second = {
            "https://a.pl": {
                "company_name_clean": "Alpha",
                "email_target": "a@a.pl",
            }
        }

        def fake_collect(wyniki, xlsx, scraper, logger):
            payload = first if len(loads) == 0 else second
            loads.append(payload)
            return payload

        fills: list[dict] = []

        def fake_fill(scraper, spec, contacts, xlsx, cache, logger, *, pass_label):
            fills.append(dict(contacts))
            return (1, [])

        orig_collect = v.collect_needed_contacts
        orig_fill = v.fill_excel_from_contacts
        v.collect_needed_contacts = fake_collect
        v.fill_excel_from_contacts = fake_fill
        xlsx = Path(tempfile.mkdtemp()) / "cn_materialy_kontakte.xlsx"
        try:
            n_rows, gaps, n_passes = v.verify_excel_with_double_json(
                scraper=object(),
                spec={"xlsx_name": "cn_materialy_kontakte.xlsx"},
                wyniki=xlsx.parent,
                xlsx=xlsx,
                logger=__import__("logging").getLogger("test"),
                passes=2,
            )
        finally:
            v.collect_needed_contacts = orig_collect
            v.fill_excel_from_contacts = orig_fill
        self.assertEqual(n_passes, 2)
        self.assertGreaterEqual(len(loads), 2)
        self.assertEqual(len(fills), 2)
        self.assertNotIn("email_target", fills[0]["https://a.pl"])
        self.assertEqual(fills[1]["https://a.pl"]["email_target"], "a@a.pl")
        self.assertEqual(n_rows, 1)
        self.assertEqual(gaps, [])


if __name__ == "__main__":
    unittest.main()
