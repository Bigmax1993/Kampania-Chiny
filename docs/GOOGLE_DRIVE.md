# Google Drive — wyniki kampanii CN

## Kampania CN (materiały budowlane) — produkcja

Folder w chmurze: [CN Materialy Budowlane](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC)

| Secret | Opis |
|--------|------|
| `GDRIVE_FOLDER_ID_CN` | ID folderu Drive (`1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC`) |

| Plik / folder | Gdzie |
|---------------|--------|
| `cn_materialy_kontakte.xlsx` | **Google Drive** (jeden plik — bez kopii z datą). Arkusze: **Kontakte** (pełne kontakty: Name of Company, Line of business, Company website, E-Mail, Phone number, Region, Localisation, Postcode, **Tax Identification Number** = NIP 10 cyfr, URL), **Prowincje** (tylko Name of Company, Region, Localisation, URL), **Info**. |
| `wyslane/*.eml` | **Google Drive** (kopie wysłanych maili) |
| `cn_materialy_cache.json` | **GitHub Actions** (artefakt `cn-materialy-wyniki-*`) — **nie** na Drive |
| `cn_materialy_scraper.log` | **GitHub Actions** (artefakt) |
| `cn_materialy_province_rotation.json` | **GitHub Actions** (artefakt) |

Excel **nie** jest w repozytorium GitHub (`Wyniki/` w `.gitignore`). Źródło prawdy dla pliku wynikowego: folder Drive CN.  
Podgląd `.xlsx` w Google Sheets bywa mylący (puste komórki / NIP jako liczba) — lepiej **Pobierz** i otwórz w Excelu; kolumna NIP jest zapisana jako **tekst**.

| Sposób | Kiedy |
|--------|--------|
| **GitHub Actions — backfill / prep** | Niedziela / poniedziałek: pobiera Excel z Drive, **append** wierszy (po URL), 2× JSON→Excel, upload. |
| **CN fill NIP on Drive Excel** | Ręcznie: pobiera Excel z Drive → uzupełnia braki NIP (Serper + BS4 + Claude) → normalizuje do 10 cyfr → **replace** (`GDRIVE_APPEND_XLSX=0`). Kolejka `cn-drive-nip`. |
| **CN sync discovery Excel to Drive** | Ręcznie: Excel z artefaktu discovery/backfill → fill NIP → **replace** na Drive (ten sam układ co artefakt). |
| **Sync wyniki Google Drive CN** | Poniedziałek 10:00: upload z artefaktu. |
| **Lokalnie** | `python scripts/gdrive_upload_wyniki.py --campaign cn` |
| **PC + Drive for desktop** | `KANBUD_DATA_DIR` → folder `CN Materialy Budowlane Wyniki` |

Artefakt źródłowy sync: `cn-materialy-wyniki-thu` (niedzielny backfill). Szczegóły: [`docs/GITHUB_ACTIONS.md`](GITHUB_ACTIONS.md).  
Logika NIP: [`docs/CN_MATERIALY.md`](CN_MATERIALY.md#tax-identification-number-nip).

### Excel — jeden plik, append vs replace

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `GDRIVE_VERSION_XLSX` | `0` | Bez kopii z datą — zawsze ten sam `cn_materialy_kontakte.xlsx` |
| `GDRIVE_APPEND_XLSX` | `1` | Przed uploadem: pobierz Excel z Drive, dopisz nowe wiersze (po URL), zaktualizuj **ten sam** plik. |
| `GDRIVE_APPEND_XLSX` | `0` | **Replace** całego pliku (używane przez fill NIP / sync discovery→Drive). |

Stare pliki `cn_materialy_kontakte_2026-*_*.xlsx` można usunąć ręcznie z folderu Drive.

### Ręczne uzupełnienie NIP na Drive

```powershell
gh workflow run "CN fill NIP on Drive Excel" -R Bigmax1993/Kampania-Chiny -f fill_nip=true
```

Lokalnie (po pobraniu xlsx):

```powershell
python scripts/gdrive_upload_wyniki.py --campaign cn --download-xlsx
python scripts/fill_nip_in_xlsx.py --xlsx Wyniki\cn_materialy_kontakte.xlsx
python scripts/gdrive_upload_wyniki.py --campaign cn   # z GDRIVE_APPEND_XLSX=0 przy pełnym replace
```

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
