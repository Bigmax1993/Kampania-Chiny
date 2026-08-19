# Google Drive — wyniki kampanii CN

## Kampania CN (materiały budowlane) — produkcja

Folder w chmurze: ustaw secret `GDRIVE_FOLDER_ID_CN` (osobny folder Drive dla Chin; nie kopiuj ID z PL/UA).

| Secret | Opis |
|--------|------|
| `GDRIVE_FOLDER_ID_CN` | ID folderu Drive kampanii CN |

| Plik / folder | Gdzie |
|---------------|--------|
| `cn_materialy_kontakte.xlsx` | **Google Drive** (jeden plik — append wierszy, bez kopii z datą) |
| `wyslane/*.eml` | **Google Drive** (kopie wysłanych maili) |
| `cn_materialy_cache.json` | **GitHub Actions** (artefakt `cn-materialy-wyniki-*`) |
| `cn_materialy_scraper.log` | **GitHub Actions** (artefakt) |
| `cn_materialy_province_rotation.json` | **GitHub Actions** (artefakt) |

| Sposób | Kiedy |
|--------|--------|
| **GitHub Actions** | Niedzielny backfill (`CN niedziela backfill`): upload → weryfikacja Excel vs JSON → ponowny upload. Dodatkowo poniedziałek 11:00 `Sync wyniki Google Drive CN`. |
| **Lokalnie** | `python scripts/gdrive_upload_wyniki.py --campaign cn` |
| **PC + Drive for desktop** | `KANBUD_DATA_DIR` → folder `CN Materialy Budowlane Wyniki` |

Artefakt źródłowy sync: `cn-materialy-wyniki-thu` (niedzielny backfill). Szczegóły: [`docs/GITHUB_ACTIONS.md`](GITHUB_ACTIONS.md).

### Excel — jeden plik, append

| Zmienna | Domyślnie | Opis |
|---------|-----------|------|
| `GDRIVE_VERSION_XLSX` | `0` | Bez kopii z datą — zawsze ten sam `cn_materialy_kontakte.xlsx` |
| `GDRIVE_APPEND_XLSX` | `1` | Przed uploadem: pobierz Excel z Drive, dopisz nowe wiersze (po URL), nadpisz plik |

Stare pliki `cn_materialy_kontakte_2026-*_*.xlsx` można usunąć ręcznie z folderu Drive.

### Upload z GitHub Actions (OAuth)

```powershell
pip install -r requirements-drive.txt
python scripts/gdrive_oauth_setup.py
```

Skrypt ustawi secrets `GDRIVE_OAUTH_*`. Kolejne runy CI uploadują na folder PL.

## Stała reguła sync (GitHub Actions)

| Reguła | Wartość |
|--------|---------|
| **Kiedy** | **Poniedziałek 11:00** (Asia/Shanghai) |
| **Cron** | `0 11 * * 1` |
| **Źródło danych** | Artefakt **`cn-materialy-wyniki-thu`** |
| **Kolejność fallback** | `thu` → `mon` → `tue` → `fri` |

Lokalny skrypt `scripts/upload_wyniki_to_drive.ps1` używa tej samej kolejności artefaktów co workflow CI.
