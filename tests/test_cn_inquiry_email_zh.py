# -*- coding: utf-8 -*-
"""Testy maili PL — kampania materiały budowlane."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cn_materialy_inquiry_email_zh import (
    DEFAULT_INQUIRY_PHONE_CN,
    DEFAULT_INQUIRY_SENDER_NAME_CN,
    build_fixed_material_inquiry_zh,
    build_inquiry_signature_zh,
    dedupe_inquiry_signature,
    ensure_inquiry_signature,
    format_inquiry_email_body_pl,
    inquiry_phone,
    inquiry_sender_name,
)


class PlInquiryEmailTest(unittest.TestCase):
    def test_default_phone(self):
        self.assertEqual(DEFAULT_INQUIRY_PHONE_CN, "516513965")
        self.assertNotIn("516513965", build_inquiry_signature_zh())
        self.assertNotIn("swinczakdata", build_inquiry_signature_zh().lower())
        self.assertEqual(inquiry_phone(), "516513965")

    def test_polish_template(self):
        body = build_fixed_material_inquiry_zh()
        self.assertIn("Szanowni Państwo", body)
        self.assertIn("dystrybutor", body)
        self.assertIn("Z poważaniem", body)
        self.assertNotIn("516513965", body)
        self.assertNotIn("swinczakdata", body.lower())
        self.assertTrue("Maksym" in body or inquiry_sender_name() in body)

    def test_fallback_is_personalized_per_company(self):
        a = build_fixed_material_inquiry_zh("Alfa Ceramika Sp. z o.o.")
        b = build_fixed_material_inquiry_zh("Beta LED Import Sp. z o.o.")
        self.assertIn("Alfa Ceramika", a)
        self.assertIn("Beta LED", b)
        self.assertNotEqual(a, b)
        self.assertNotIn("Alfa Ceramika", b)

    def test_no_ua_phone_in_signature(self):
        sig = build_inquiry_signature_zh()
        self.assertNotIn("+380", sig)

    def test_signature_multiline_not_collapsed(self):
        sig = build_inquiry_signature_zh()
        self.assertIn("\n", sig)
        self.assertLessEqual(sig.count("Maksym"), 1)

    def test_dedupe_double_signature(self):
        sig = build_inquiry_signature_zh()
        body = f"Szanowni Państwo,\n\nTreść zapytania.\n\n{sig}\n\n{sig}"
        cleaned = dedupe_inquiry_signature(body)
        self.assertEqual(cleaned.count("Z poważaniem"), 1)
        self.assertEqual(cleaned.count("Maksym"), 1)

    def test_ensure_does_not_append_when_present(self):
        sig = build_inquiry_signature_zh()
        body = f"Szanowni Państwo,\n\nZapytanie.\n\n{sig}"
        ensured = ensure_inquiry_signature(body)
        self.assertEqual(ensured.count("Z poważaniem"), 1)

    def test_format_body_polish_signature_does_not_crash(self):
        body = (
            "Szanowni Państwo,\n\n"
            "Zwracam się do Kim24 w sprawie współpracy dystrybucyjnej.\n\n"
            "Z poważaniem\n"
            "Maksym Swinczak"
        )
        formatted = format_inquiry_email_body_pl(body)
        self.assertIn("Z poważaniem,", formatted)
        self.assertIn("Maksym Swinczak", formatted)

    def test_format_body_chinese_signature_still_works(self):
        body = "尊敬的合作伙伴：询盘内容。此致敬礼\nMaksym Swinczak"
        formatted = format_inquiry_email_body_pl(body)
        self.assertIn("此致敬礼,", formatted)
        self.assertIn("Maksym Swinczak", formatted)


if __name__ == "__main__":
    unittest.main(verbosity=2)
