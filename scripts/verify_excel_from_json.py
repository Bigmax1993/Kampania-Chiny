# -*- coding: utf-8 -*-
"""
Weryfikuje Excel vs cache JSON, uzupelnia braki i zapisuje plik.

Dwa razy wczytuje *_cache.json z dysku, dwa razy uzupelnia luki w Excelu
i dwa razy zapisuje xlsx. Na koncu jeszcze raz porownuje Excel z JSON.

Walidacja przepuszcza z JSON pola potrzebne w Excelu (nazwa, e-mail, telefon,
adres, wojewodztwo, www, URL) — bez filtra GU/retail.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import kanbud_bootstrap as _kanbud_bootstrap  # noqa: E402

_kanbud_bootstrap.ensure_import_paths(ROOT)

from scripts.excel_from_json_validate import (  # noqa: E402
    fill_export_from_json,
    find_excel_gaps,
    json_contact_has_needed_data,
    merge_contacts_maps,
    pipeline_row_from_json,
    verify_and_fill_until_complete,
)
from scripts.recover_pi_cache_contacts import recover_contacts_from_cache_file  # noqa: E402
from libs.scraper_email_replies import ReplySyncConfig, write_excel_with_reply_styles  # noqa: E402

CAMPAIGNS = {
    "cn": {
        "module": "cn_materialy_scraper",
        "lang": "pl",
        "campaign_id": "cn_materialy",
        "xlsx_name": "cn_materialy_kontakte.xlsx",
        "cache_glob": "*_cache.json",
    },
}


def _load_scraper(campaign: str):
    spec = CAMPAIGNS[campaign]
    return __import__(spec["module"]), spec


def _cell(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def pipeline_row_as_info(row: dict) -> dict:
    return {
        "company_name_clean": _cell(row.get("company_name_clean") or row.get("nazwa")),
        "company_name": _cell(row.get("nazwa")),
        "email_target": _cell(row.get("email_target")),
        "emails_found": _cell(row.get("emails_found")),
        "phones_found": _cell(row.get("phones_found") or row.get("telefon")),
        "full_address": _cell(row.get("full_address") or row.get("adres")),
        "official_website": _cell(row.get("official_website") or row.get("www")),
        "bundesland": _cell(row.get("bundesland")),
        "retail_chains_found": _cell(row.get("retail_chains_found") or row.get("kategoria")),
        "kategoria": _cell(row.get("kategoria") or row.get("line_of_business")),
        "nip": _cell(row.get("nip") or row.get("tax_id")),
        "kod_pocztowy": _cell(row.get("kod_pocztowy") or row.get("postcode")),
        "email_status": _cell(row.get("email_status")),
        "retail_verified": bool(row.get("retail_verified")),
        "is_gu": bool(row.get("is_gu")),
        "is_small_firm": row.get("is_small_firm", True),
        "gu_marker": _cell(row.get("gu_marker")),
    }


def collect_needed_contacts(wyniki: Path, xlsx: Path, scraper, logger: logging.Logger) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for cache_path in sorted(wyniki.glob("*_cache.json")):
        recovered = recover_contacts_from_cache_file(cache_path)
        logger.info("%s: contacts=%s", cache_path.name, len(recovered))
        merged = merge_contacts_maps(merged, recovered)
    if xlsx.is_file():
        rows, _ = scraper.load_existing_output(xlsx, logger)
        excel_contacts = {}
        for row in rows:
            url = _cell(row.get("url") or row.get("www") or row.get("official_website"))
            if url:
                excel_contacts[url] = pipeline_row_as_info(row)
        logger.info("%s: excel_rows=%s", xlsx.name, len(excel_contacts))
        merged = merge_contacts_maps(merged, excel_contacts)
    needed = {}
    for url, info in merged.items():
        if not json_contact_has_needed_data(url, info):
            continue
        if scraper.is_public_portal_url(url) or scraper.is_public_portal_url(
            (info or {}).get("official_website") or ""
        ):
            continue
        needed[url] = info
    logger.info("Do Excela z JSON: %s z %s contacts", len(needed), len(merged))
    return needed


def write_sheets(
    scraper,
    spec: dict,
    xlsx: Path,
    export_rows: list[dict],
    pipeline_rows: list[dict],
    cache: dict,
    logger,
) -> None:
    state_rows = scraper.build_bundesland_rows(pipeline_rows) if pipeline_rows else []
    cfg = ReplySyncConfig(
        cache_path=scraper.CACHE_FILE,
        xlsx_path=xlsx,
        lang="en",
        campaign_id=spec["campaign_id"],
        email_column="E-Mail",
        include_reply_export_columns=False,
    )
    write_excel_with_reply_styles(
        xlsx,
        {
            "Info": scraper.build_excel_info_sheet_rows(),
            "Kontakte": export_rows,
            "Prowincje": state_rows,
        },
        cache,
        cfg,
        logger,
    )


JSON_RELOAD_PASSES = 2


def fill_excel_from_contacts(
    scraper,
    spec: dict,
    contacts: dict,
    xlsx: Path,
    cache: dict,
    logger,
    *,
    pass_label: str,
) -> tuple[int, list[dict]]:
    """Jedna runda: JSON → luki w Excelu → uzupelnienie → zapis → odczyt z dysku."""
    pipeline_rows = [pipeline_row_from_json(url, info) for url, info in contacts.items()]
    export_rows = scraper.build_export_rows(
        pipeline_rows, logger=logger, cache=cache, require_eligible=False
    )
    if xlsx.is_file():
        loaded, _ = scraper.load_existing_output(xlsx, logger)
        if loaded:
            loaded_export = scraper.build_export_rows(
                loaded, logger=logger, cache=cache, require_eligible=False
            )
            by_url = {}
            for rec in loaded_export:
                url = str(
                    rec.get("URL")
                    or rec.get("Company website")
                    or rec.get("Strona www")
                    or ""
                ).strip()
                if url:
                    by_url[url] = rec
            merged = list(loaded_export)
            for rec in export_rows:
                url = str(
                    rec.get("URL")
                    or rec.get("Company website")
                    or rec.get("Strona www")
                    or ""
                ).strip()
                if url and url not in by_url:
                    merged.append(rec)
            export_rows = merged
            pipeline_rows = loaded
    export_rows, n_fill = fill_export_from_json(contacts, export_rows)
    logger.info("%s: uzupelnienie z JSON: %s zmian", pass_label, n_fill)
    export_rows, gaps, rounds = verify_and_fill_until_complete(
        contacts, export_rows, max_rounds=2
    )
    logger.info(
        "%s: weryfikacja pamieci rund=%s luk=%s wierszy=%s",
        pass_label,
        rounds,
        len(gaps),
        len(export_rows),
    )
    write_sheets(scraper, spec, xlsx, export_rows, pipeline_rows, cache, logger)

    loaded, _ = scraper.load_existing_output(xlsx, logger)
    loaded_export = scraper.build_export_rows(
        loaded, logger=logger, cache=cache, require_eligible=False
    )
    loaded_export, gaps_after, fill_rounds = verify_and_fill_until_complete(
        contacts, loaded_export, max_rounds=2
    )
    if fill_rounds or gaps_after:
        logger.warning(
            "%s: po odczycie dysku JSON uzupelnia ponownie: rund=%s luki=%s — zapis",
            pass_label,
            fill_rounds,
            len(gaps_after),
        )
        write_sheets(scraper, spec, xlsx, loaded_export, loaded, cache, logger)
        loaded, _ = scraper.load_existing_output(xlsx, logger)
        loaded_export = scraper.build_export_rows(
            loaded, logger=logger, cache=cache, require_eligible=False
        )
        gaps_after = find_excel_gaps(contacts, loaded_export)
    logger.info(
        "%s: zapisano %s wierszy, luki=%s",
        pass_label,
        len(loaded_export),
        len(gaps_after),
    )
    return len(loaded_export), gaps_after


def verify_and_save(
    scraper,
    spec: dict,
    contacts: dict,
    xlsx: Path,
    cache: dict,
    logger,
) -> tuple[int, list[dict]]:
    """Kompatybilnosc: jedna runda na juz wczytanym JSON."""
    return fill_excel_from_contacts(
        scraper, spec, contacts, xlsx, cache, logger, pass_label="pass"
    )


def verify_excel_with_double_json(
    scraper,
    spec: dict,
    wyniki: Path,
    xlsx: Path,
    logger,
    *,
    passes: int = JSON_RELOAD_PASSES,
) -> tuple[int, list[dict], int]:
    """
    Podwojne sprawdzenie: dwa razy wczytaj JSON z dysku, uzupelnij braki w Excelu, zapisz.
    Na koncu jeszcze raz porownaj Excel vs JSON.
    """
    n_rows = 0
    gaps: list[dict] = []
    n_passes = max(2, int(passes))
    last_contacts: dict = {}
    for i in range(1, n_passes + 1):
        label = f"JSON pass {i}/{n_passes}"
        logger.info("%s: wczytuje cache JSON z dysku", label)
        contacts = collect_needed_contacts(wyniki, xlsx, scraper, logger)
        if contacts:
            last_contacts = contacts
        elif last_contacts:
            logger.warning("%s: pusty JSON, uzywam poprzedniego odczytu", label)
            contacts = last_contacts
        elif i == 1:
            raise SystemExit("Brak contacts JSON z danymi do Excela")
        cache = {"contacts": contacts}
        n_rows, gaps = fill_excel_from_contacts(
            scraper, spec, contacts, xlsx, cache, logger, pass_label=label
        )
    logger.info("Sprawdzenie koncowe: ponowny odczyt JSON i Excela")
    contacts = collect_needed_contacts(wyniki, xlsx, scraper, logger) or last_contacts
    if xlsx.is_file():
        loaded, _ = scraper.load_existing_output(xlsx, logger)
        loaded_export = scraper.build_export_rows(
            loaded, logger=logger, cache={"contacts": contacts}, require_eligible=False
        )
        gaps = find_excel_gaps(contacts, loaded_export)
        if gaps:
            logger.warning(
                "Sprawdzenie koncowe: %s luk — ostatnie uzupelnienie z JSON i zapis",
                len(gaps),
            )
            loaded_export, n_fill = fill_export_from_json(contacts, loaded_export)
            loaded_export, gaps, _ = verify_and_fill_until_complete(
                contacts, loaded_export, max_rounds=2
            )
            write_sheets(
                scraper,
                spec,
                xlsx,
                loaded_export,
                loaded,
                {"contacts": contacts},
                logger,
            )
            n_rows = len(loaded_export)
            logger.info("Zapis po sprawdzeniu koncowym: zmian=%s luk=%s", n_fill, len(gaps))
    return n_rows, gaps, n_passes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", choices=sorted(CAMPAIGNS), default="cn")
    parser.add_argument("--wyniki", type=Path, default=ROOT / "Wyniki")
    parser.add_argument(
        "--passes",
        type=int,
        default=JSON_RELOAD_PASSES,
        help="Ile razy wczytac JSON z dysku, uzupelnic Excel i zapisac (min. 2)",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("verify_excel_json")

    scraper, spec = _load_scraper(args.campaign)
    xlsx = args.wyniki / spec["xlsx_name"]
    n_rows, gaps, n_passes = verify_excel_with_double_json(
        scraper, spec, args.wyniki, xlsx, logger, passes=args.passes
    )
    if gaps:
        print(f"VERIFY_FAIL rows={n_rows} gaps={len(gaps)} json_passes={n_passes}")
        for g in gaps[:20]:
            print(f"  {g['url']}: {g['reason']} {g['columns']}")
        return 1
    print(f"VERIFY_OK rows={n_rows} json_passes={n_passes} file={xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
