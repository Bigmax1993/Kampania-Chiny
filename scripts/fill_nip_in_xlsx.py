# -*- coding: utf-8 -*-
"""Uzupełnia kolumnę Tax Identification Number w istniejącym Excelu — bez zmiany układu/wierszy."""
from __future__ import annotations

import argparse
import logging
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
    args = parser.parse_args()

    import pandas as pd

    from cn_materialy_scraper import (
        collect_contacts_from_contact_pages,
        setup_logging,
        tax_id_from_row,
    )
    from cn_contact_fields import normalize_pl_nip

    logger = setup_logging()
    path = args.xlsx
    if not path.exists():
        print(f"Brak pliku: {path}", file=sys.stderr)
        return 1

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
    url_col = "URL" if "URL" in df.columns else None
    www_col = "Company website" if "Company website" in df.columns else None

    filled = 0
    checked = 0
    for idx, row in df.iterrows():
        existing = normalize_pl_nip(str(row.get(nip_col) or "")) or ""
        if existing:
            continue
        website = ""
        if www_col:
            website = str(row.get(www_col) or "").strip()
        if not website and url_col:
            website = str(row.get(url_col) or "").strip()
        if not website.startswith("http"):
            continue
        checked += 1
        try:
            collected = collect_contacts_from_contact_pages(website, logger, cache={})
            nip = normalize_pl_nip(str(collected.get("nip") or "")) or ""
            if not nip:
                nip = tax_id_from_row({"nip": collected.get("nip"), "page_snippet": collected.get("page_snippet")})
            if nip:
                df.at[idx, nip_col] = nip
                filled += 1
                print(f"NIP {nip} ← {website}")
            else:
                print(f"brak NIP ← {website}")
        except Exception as exc:
            print(f"błąd {website}: {exc}")

    sheets[args.sheet] = df
    # Zachowaj kolejność arkuszy i kolumn — tylko nadpisz wartości.
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, sheet_df in sheets.items():
            sheet_df.to_excel(writer, sheet_name=name, index=False)

    print(f"OK checked={checked} nip+={filled} file={path} rows={len(df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
