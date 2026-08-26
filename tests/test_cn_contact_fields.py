# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest

from cn_contact_fields import (
    extract_pl_address_from_text,
    extract_pl_postcode,
    is_pl_junk_company_name,
    is_pl_seo_title,
    looks_like_marketing_text,
    looks_like_pl_physical_address,
    sanitize_export_address,
    serper_discovery_address,
)


class PlContactFieldsTest(unittest.TestCase):
    def test_rejects_marketing_as_address(self):
        self.assertTrue(
            looks_like_marketing_text(
                "W naszym asortymencie znajdziecie Państwo wysokiej jakości materiały"
            )
        )
        self.assertEqual(
            sanitize_export_address(
                "Oferujemy żwir o różnych frakcjach, co pozwala na..."
            ),
            "",
        )

    def test_accepts_pl_street_address(self):
        addr = "ul. Przemysłowa 12, 05-800 Pruszków"
        self.assertTrue(looks_like_pl_physical_address(addr))
        self.assertEqual(sanitize_export_address(addr), addr)

    def test_extract_from_impressum_block(self):
        text = (
            "MAZUR Sp. z o.o.\n"
            "ul. Budowlana 5, 05-120 Legionowo\n"
            "tel. 22 123 45 67"
        )
        self.assertEqual(
            extract_pl_address_from_text(text),
            "ul. Budowlana 5, 05-120 Legionowo",
        )

    def test_extract_pl_postcode(self):
        self.assertEqual(extract_pl_postcode("ul. Testowa 1, 00-001 Warszawa"), "00-001")
        self.assertEqual(extract_pl_postcode("St. Testowa 1, 00-001 Warsaw"), "00-001")
        self.assertEqual(extract_pl_postcode("brak kodu"), "")
        self.assertEqual(extract_pl_postcode("", "05-800 Pruszków"), "05-800")

    def test_loose_json_fill_address_without_postal(self):
        from cn_contact_fields import looks_like_usable_address_for_json_fill

        self.assertTrue(
            looks_like_usable_address_for_json_fill("ul. Przemysłowa 12, Warszawa")
        )
        self.assertFalse(
            looks_like_usable_address_for_json_fill(
                "W naszym asortymencie znajdziecie Państwo wysokiej jakości materiały"
            )
        )

    def test_junk_company_names(self):
        self.assertTrue(is_pl_junk_company_name("Biuro obsługi klienta"))
        self.assertTrue(is_pl_junk_company_name("Artykuły sezonowe"))
        self.assertTrue(is_pl_seo_title("Fugi do kostki brukowej i płyt Warszawa"))

    def test_extracts_spaced_and_dotted_nip(self):
        from cn_contact_fields import extract_all_pl_nips_from_text, extract_pl_nip_from_text

        self.assertEqual(
            extract_pl_nip_from_text("NIP 123 456 32 18 ul. Test"),
            "1234563218",
        )
        self.assertEqual(
            extract_pl_nip_from_text("N.I.P.: 123.456.32.18"),
            "1234563218",
        )
        nips = extract_all_pl_nips_from_text(
            "Firma X NIP 1234563218 oraz PL 5252348078"
        )
        self.assertIn("1234563218", nips)

    def test_normalize_strips_separators_and_excel_float(self):
        from cn_contact_fields import normalize_pl_nip

        self.assertEqual(normalize_pl_nip("123-456-32-18"), "1234563218")
        self.assertEqual(normalize_pl_nip("123 456 32 18"), "1234563218")
        self.assertEqual(normalize_pl_nip("1234563218.0"), "1234563218")
        self.assertEqual(normalize_pl_nip(1234563218.0), "1234563218")
        self.assertEqual(normalize_pl_nip(1234563218), "1234563218")

    def test_extracts_labeled_nip(self):
        from cn_contact_fields import extract_pl_nip_from_text, pl_nip_checksum_ok

        nip = extract_pl_nip_from_text(
            "MAZUR Sp. z o.o. NIP: 1234563218 ul. Budowlana 1"
        )
        self.assertEqual(nip, "1234563218")
        self.assertTrue(pl_nip_checksum_ok(nip))

    def test_extracts_nr_nip_and_tax_id_label(self):
        from cn_contact_fields import extract_pl_nip_from_text

        self.assertEqual(
            extract_pl_nip_from_text("Nr NIP 1234563218 REGON 123"),
            "1234563218",
        )
        self.assertEqual(
            extract_pl_nip_from_text("Tax Identification Number: 1234563218"),
            "1234563218",
        )
        self.assertEqual(
            extract_pl_nip_from_text("Numer identyfikacji podatkowej: 1234563218"),
            "1234563218",
        )

    def test_extracts_pl_vat_with_checksum(self):
        from cn_contact_fields import extract_pl_nip_from_text

        self.assertEqual(
            extract_pl_nip_from_text("EU VAT PL1234563218"),
            "1234563218",
        )

    def test_extract_pl_nip_from_texts_priority(self):
        from cn_contact_fields import extract_pl_nip_from_texts

        homepage = "Hurtownia płytek " + ("oferta " * 400)
        kontakt = "Kontakt NIP: 1234563218 tel. 22 111 22 33"
        self.assertEqual(
            extract_pl_nip_from_texts(kontakt, homepage),
            "1234563218",
        )
        self.assertEqual(extract_pl_nip_from_texts(homepage, ""), "")

    def test_serper_organic_has_no_address(self):
        self.assertEqual(
            serper_discovery_address(
                bucket="organic",
                item={
                    "snippet": "W naszym asortymencie znajdziecie Państwo wysokiej jakości...",
                    "address": "",
                },
            ),
            "",
        )

    def test_serper_places_address(self):
        self.assertEqual(
            serper_discovery_address(
                bucket="places",
                item={"address": "ul. Testowa 1, 00-001 Warszawa"},
            ),
            "ul. Testowa 1, 00-001 Warszawa",
        )


if __name__ == "__main__":
    unittest.main()
