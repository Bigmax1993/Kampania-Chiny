"""Weryfikacja izolacji repo CN — brak plikow PL/UA."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "pattern",
    [
        "pl_*.py",
        "ua_*.py",
        "tests/test_pl_*.py",
        "tests/test_ua_*.py",
        ".github/workflows/pl_*.yml",
        ".github/workflows/ua_*.yml",
        ".github/workflows/sync-google-drive-pl.yml",
        ".github/workflows/sync-google-drive-ua.yml",
        "run_config/pl_*.json",
        "run_config/ua_*.json",
        "schedule/pl",
        "schedule/ua",
        "legacy",
    ],
)
def test_no_sister_campaign_artifacts(pattern: str) -> None:
    matches = list(ROOT.glob(pattern))
    assert not matches, f"Znaleziono artefakty PL/UA w repo CN: {matches}"
