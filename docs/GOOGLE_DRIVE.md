# Google Drive — wyniki kampanii CN

## Kampania CN (materiały budowlane) — produkcja

Folder w chmurze: [CN Materialy Budowlane](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC)

| Secret | Opis |
|--------|------|
| `GDRIVE_FOLDER_ID_CN` | ID folderu Drive (`1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC`) |

| Plik / folder | Gdzie |
|---------------|--------|
| `cn_materialy_kontakte.xlsx` | **Google Drive** (jeden plik — append wierszy, bez kopii z datą). Arkusze: **Kontakte** (pełne kontakty: Name of Company, Line of business, Company website, E-Mail, Phone number, Region, Localisation, Postcode, Tax Identification Number, URL), **Prowincje** (tylko Name of Company, Region, Localisation, URL), **Info**. |
| `wyslane/*.eml` | **Google Drive** (kopie wysłanych maili) |
| `cn_materialy_cache.json` | **GitHub Actions** (artefakt `cn-materialy-wyniki-*`) — **nie** na Drive |
| `cn_materialy_scraper.log` | **GitHub Actions** (artefakt) |
| `cn_materialy_province_rotation.json` | **GitHub Actions** (artefakt) |

Excel **nie** jest w repozytorium GitHub (`Wyniki/` w `.gitignore`). Źródło prawdy dla pliku wynikowego: folder Drive CN. Podgląd `.xlsx` w Google Sheets bywa pusty — lepiej **Pobierz** i otwórz w Excelu.

| Sposób | Kiedy |
|--------|--------|
| **GitHub Actions** | Niedzielny backfill: pobiera istniejący `cn_materialy_kontakte.xlsx` z Drive, dopisuje nowe wiersze / puste pola, **nadpisuje ten sam plik** (bez kopii z datą). Potem 2× JSON→Excel i upload z append. Poniedziałkowy prep: to samo append. Dodatkowo poniedziałek 10:00 `Sync wyniki Google Drive CN`. |
| **Lokalnie** | `python scripts/gdrive_upload_wyniki.py --campaign cn` |
| **PC + Drive for desktop** | `KANBUD_DATA_DIR` → folder `CN Materialy Budowlane Wyniki` |

Artefakt źródłowy sync: `cn-materialy-wyniki-thu` (niedzielny backfill). Szczegóły: [`docs/GITHUB_ACTIONS.md`](GITHUB_ACTIONS.md).

### Excel — jeden plik, append

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `GDRIVE_VERSION_XLSX` | `0` | Bez kopii z datą — zawsze ten sam `cn_materialy_kontakte.xlsx` |
| `GDRIVE_APPEND_XLSX` | `1` | Przed uploadem: pobierz Excel z Drive, dopisz nowe wiersze (po URL), zaktualizuj **ten sam** plik. Nigdy nowa kopia. |

Stare pliki `cn_materialy_kontakte_2026-*_*.xlsx` można usunąć ręcznie z folderu Drive.

### Upload z GitHub Actions (OAuth)

```powershell
pip install -r requirements-drive.txt
python scripts/gdrive_oauth_setup.py
```

Skrypt ustawi secrets `GDRIVE_OAUTH_*`. Kolejne runy CI uploadują do folderu CN.

## Stała reguła sync (GitHub Actions)

| Reguła | Wartość |
|--------|---------|
| **Kiedy** | **Poniedziałek 10:00** (Asia/Shanghai) |
| **Cron** | `0 10 * * 1` |
| **Źródło danych** | Artefakt **`cn-materialy-wyniki-thu`** |
| **Kolejność fallback** | `thu` → `mon` → `tue` → `fri` |

Lokalny skrypt `scripts/upload_wyniki_to_drive.ps1` używa tej samej kolejności artefaktów co workflow CI.
