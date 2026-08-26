# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class TestSerperNipResolve(unittest.TestCase):
    def test_parse_claude_verdict(self):
        from serper_nip_resolve import _parse_claude_nip_verdict

        out = _parse_claude_nip_verdict(
            '```json\n{"match": true, "nip": "1234563218", "reason": "ok"}\n```'
        )
        self.assertTrue(out["match"])
        self.assertEqual(out["nip"], "1234563218")

        out2 = _parse_claude_nip_verdict('{"match": false, "nip": "", "reason": "no"}')
        self.assertFalse(out2["match"])
        self.assertEqual(out2["nip"], "")

    def test_apply_nip_to_contact_json(self):
        from serper_nip_resolve import apply_nip_to_contact_json

        contacts = {"https://a.pl": {"company_name": "A"}}
        ok = apply_nip_to_contact_json(
            contacts,
            url="https://a.pl",
            website="https://a.pl",
            nip="1234563218",
        )
        self.assertTrue(ok)
        self.assertEqual(contacts["https://a.pl"]["nip"], "1234563218")

    def test_resolve_uses_serper_fetch_and_claude(self):
        from serper_nip_resolve import resolve_missing_nip_via_serper

        organic = [
            {
                "title": "Firma Test NIP",
                "snippet": "NIP: 1234563218 Warszawa",
                "link": "https://firma-test.pl/kontakt",
            }
        ]
        logger = MagicMock()
        with (
            patch("serper_nip_resolve.get_serper_api_key", return_value="k"),
            patch("serper_nip_resolve._serper_organic", return_value=organic),
            patch(
                "serper_nip_resolve._fetch_page_text",
                return_value="Firma Test Sp. z o.o. NIP 123 456 32 18",
            ),
            patch(
                "serper_nip_resolve._claude_pick_nip",
                return_value="1234563218",
            ) as claude,
        ):
            nip = resolve_missing_nip_via_serper(
                "Firma Test Sp. z o.o.",
                "https://firma-test.pl",
                logger,
                cache={},
            )
        self.assertEqual(nip, "1234563218")
        claude.assert_called_once()
        args = claude.call_args[0]
        self.assertIn("1234563218", args[2])


if __name__ == "__main__":
    unittest.main()
