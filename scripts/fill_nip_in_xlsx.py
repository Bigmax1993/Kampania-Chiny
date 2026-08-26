# -*- coding: utf-8 -*-
"""Uzupełnia kolumnę Tax Identification Number w Excelu — bez zmiany układu/wierszy.

NIP zawsze jako 10 cyfr (bez '-' i spacji).
Gdy brak NIP: JSON → strony Kontakt → Serper → requests+BS4 → Claude → JSON + Excel.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=ROOT / "Wyniki" / "cn_materialy_kontakte.xlsx",
    )
    parser.add_argument("--sheet", default="Kontakte")
    parser.add_argument(
        "--save-cache",
        action="store_true",
        default=True,
        help="Zapisz uzupełniony NIP też do cache JSON (contacts)",
    )
    parser.add_argument("--no-save-cache", action="store_false", dest="save_cache")
    args = parser.parse_args()

    import pandas as pd

    from cn_contact_fields import normalize_pl_nip
    from cn_materialy_scraper import (
        collect_contacts_from_contact_pages,
        load_cache,
        save_cache,
        setup_logging,
        tax_id_from_row,
    )
    from serper_nip_resolve import apply_nip_to_contact_json, resolve_missing_nip_via_serper

    logger = setup_logging()
    path = args.xlsx
    if not path.exists():
        print(f"Brak pliku: {path}", file=sys.stderr)
        return 1

    cache: dict = {}
    if args.save_cache:
        try:
            cache = load_cache(logger)
        except Exception as exc:
            logger.warning("Nie wczytano cache JSON: %s", exc)
            cache = {}

    xl = pd.ExcelFile(path)
    sheets = {name: pd.read_excel(path, sheet_name=name) for name in xl.sheet_names}
    df = sheets.get(args.sheet)
    if df is None or df.empty:
        print(f"Pusty arkusz {args.sheet}")
        return 1

    nip_col = "Tax Identification Number"
    if nip_col not in df.columns:
        print(f"Brak kolumny {nip_col}: {list(df.columns)}", file=sys.stderr)
        return 1
    # Pusta kolumna bywa float64 — wymuś string + od razu format 10 cyfr.
    df[nip_col] = df[nip_col].apply(
        lambda v: ""
        if v is None or (isinstance(v, float) and pd.isna(v))
        else (normalize_pl_nip(str(v)) or "")
    )
    name_col = "Name of Company" if "Name of Company" in df.columns else df.columns[0]
    url_col = "URL" if "URL" in df.columns else None
    www_col = "Company website" if "Company website" in df.columns else None

    contacts = cache.setdefault("contacts", {})
    # Ujednolić NIP w JSON (bez '-' / spacji).
    for _key, info in list(contacts.items()):
        if not isinstance(info, dict):
            continue
        for field in ("nip", "tax_id"):
            raw = info.get(field)
            if raw:
                norm = normalize_pl_nip(str(raw))
                if norm:
                    info[field] = norm

    filled = 0
    reformatted = int((df[nip_col].astype(str).str.len() == 10).sum())
    checked = 0
    json_writes = 0
    for idx, row in df.iterrows():
        existing = normalize_pl_nip(str(row.get(nip_col) or "")) or ""
        if existing:
            # Już znormalizowane w apply powyżej — upewnij zapis.
            if str(row.get(nip_col) or "") != existing:
                df.at[idx, nip_col] = existing
            continue
        website = ""
        if www_col:
            website = str(row.get(www_col) or "").strip()
        place_url = ""
        if url_col:
            place_url = str(row.get(url_col) or "").strip()
        if not website and place_url:
            website = place_url
        if not website.startswith("http"):
            continue
        checked += 1
        company = str(row.get(name_col) or "").strip()

        # 1) Jeśli JSON już ma NIP — weź stamtąd.
        for key in (place_url, website):
            if not key:
                continue
            info = contacts.get(key) or {}
            from_json = normalize_pl_nip(
                str(info.get("nip") or info.get("tax_id") or "")
            )
            if from_json:
                existing = from_json
                break
        if existing:
            df.at[idx, nip_col] = existing
            filled += 1
            print(f"NIP {existing} ← JSON {website}")
            continue

        try:
            # 2) Strony Kontakt (regex luźniejszy).
            collected = collect_contacts_from_contact_pages(website, logger, cache=cache)
            nip = normalize_pl_nip(str(collected.get("nip") or "")) or ""
            if not nip:
                nip = tax_id_from_row(
                    {
                        "nip": collected.get("nip"),
                        "page_snippet": collected.get("page_snippet"),
                    }
                )
            # 3) Brak w JSON / Kontakt → Serper + BS4 + Claude.
            if not nip:
                nip = resolve_missing_nip_via_serper(
                    company,
                    website,
                    logger,
                    cache,
                )
            if nip:
                df.at[idx, nip_col] = nip
                filled += 1
                if apply_nip_to_contact_json(
                    contacts, url=place_url or website, website=website, nip=nip
                ):
                    json_writes += 1
                print(f"NIP {nip} ← {website}")
            else:
                print(f"brak NIP ← {website}")
        except Exception as exc:
            print(f"błąd {website}: {exc}")

    sheets[args.sheet] = df
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=name, index=False)

    if args.save_cache and (json_writes or reformatted):
        save_cache(cache, logger)

    nip_ok = int((df[nip_col].astype(str).str.fullmatch(r"\d{10}").fillna(False)).sum())
    print(
        f"OK checked={checked} nip+={filled} json+={json_writes} "
        f"nip_digits={nip_ok}/{len(df)} file={path} rows={len(df)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
