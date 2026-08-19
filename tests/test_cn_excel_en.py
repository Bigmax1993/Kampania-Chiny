# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest

from cn_excel_en import (
    line_of_business_to_english,
    localisation_to_english,
    region_to_english,
    region_to_internal,
)


class ExcelEnglishExportTests(unittest.TestCase):
    def test_region_english_and_roundtrip(self):
        self.assertEqual(region_to_english("mazowieckie"), "Masovian Voivodeship")
        self.assertEqual(region_to_english("śląskie"), "Silesian Voivodeship")
        self.assertEqual(
            region_to_internal("Masovian Voivodeship"), "mazowieckie"
        )
        self.assertEqual(region_to_internal("mazowieckie"), "mazowieckie")

    def test_line_of_business_english(self):
        self.assertEqual(
            line_of_business_to_english("dystrybutor płytek mazowieckie"),
            "distributor tiles Masovian Voivodeship",
        )
        self.assertEqual(
            line_of_business_to_english("wyłączny importer ceramiki"),
            "exclusive importer ceramics",
        )
        self.assertEqual(
            line_of_business_to_english("dystrybutor kabiny prysznicowe drzwi stalowe"),
            "distributor shower cabins steel doors",
        )
        self.assertIn(
            "structural steel",
            line_of_business_to_english("importer stal konstrukcyjna"),
        )

    def test_localisation_english(self):
        self.assertEqual(
            localisation_to_english("ul. Testowa 1, 00-001 Warszawa"),
            "St. Testowa 1, 00-001 Warsaw",
        )
        self.assertIn("Krakow", localisation_to_english("al. Mickiewicza 2, Kraków"))


if __name__ == "__main__":
    unittest.main()
