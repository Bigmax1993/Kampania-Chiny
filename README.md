# Wyszukiwarka materiałów budowlanych — Chiny (CN)

Repozytorium: [wyszukiwarka-materialow-budowlanych-chiny](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny)

Kampania siostrzana (Polska): [wyszukiwarka-materialow-budowlanych-polska](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-polska)  
Kampania siostrzana (Ukraina): [wyszukiwarka-materialow-budowlanych-ukraina](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-ukraina)

**Produkcja:** `cn_materialy` — polscy dystrybutorzy i importerzy materiałów budowlanych (produkt dla chińskich eksporterów; GitHub Actions + opcjonalnie Task Scheduler PC).

---

## Pipeline

**Serper (gl=pl, hl=pl) → crawl www → Claude verify (PL dystrybutor) → Excel (NIP 10 cyfr) → maile PL**

Przy braku NIP w JSON: **Serper → requests/BS4 → Claude** → zapis do JSON i Excela (`serper_nip_resolve.py`).

Szczegóły: [`docs/CN_MATERIALY.md`](docs/CN_MATERIALY.md) · maile: [`docs/MAILE.md`](docs/MAILE.md) · Drive: [`docs/GOOGLE_DRIVE.md`](docs/GOOGLE_DRIVE.md)

| Moduł | Plik |
|-------|------|
| Scraper | `cn_materialy_scraper.py` |
| NIP (regex + normalizacja 10 cyfr) | `cn_contact_fields.py` |
| Brak NIP → Serper + Claude | `serper_nip_resolve.py` |
| Fill NIP w Excelu | `scripts/fill_nip_in_xlsx.py` |
| Frazy per województwo | `cn_province_keywords.py` |
| Rotacja województw | `cn_province_rotation.py` |
| Filtr dystrybutorów | `cn_materialy_supplier_filter.py` |
| Prompty Claude | `cn_claude_prompts.py` |
| Treść maila PL | `cn_materialy_inquiry_email_zh.py` |

Maile po polsku do dystrybutorów w Polsce, **bez telefonu i bez strony www**, **bez załączników**.

Wyniki: `Wyniki/cn_materialy_cache.json`, `cn_materialy_kontakte.xlsx` (lokalnie / artefakt Actions; produkcja na [Google Drive](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC)).

Excel — arkusz **Kontakte** = pełne dane (Tax Identification Number / NIP = **10 cyfr**, bez `-` i spacji); arkusz **Prowincje** = tylko indeks regionu. Szczegóły: [`docs/CN_MATERIALY.md`](docs/CN_MATERIALY.md#excel-i-google-drive).

---

## Szybki start

```powershell
git clone https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny.git
cd wyszukiwarka-materialow-budowlanych-chiny
pip install -r requirements.txt
$env:KANBUD_PROJECT_ROOT = "$PWD\libs"

python cn_materialy_scraper.py --test
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --serper-only-discovery --no-auto-email --rotate-province
python cn_materialy_scraper.py --rotation-status
python cn_materialy_scraper.py --dry-run-email --send-emails-only
```

Skopiuj `.env.example` → `.env` (lokalnie; na CI ustaw [GitHub Secrets](#github-secrets)).

---

## Testy

```powershell
$env:KANBUD_PROJECT_ROOT = "$PWD\libs"
python cn_materialy_scraper.py --test
python -m unittest discover -s tests -p "test_*.py" -q
python -m pytest tests/ -q
```

Pełna bateria: `powershell -ExecutionPolicy Bypass -File scripts\RUN_ALL_TESTS.ps1`

`tests/test_repo_isolation.py` — regresja: brak plików kampanii UA i `legacy/` w tym repo.

---

## Harmonogram

Szczegóły: [`schedule/cn/PLAN_5_DNI_CN.md`](schedule/cn/PLAN_5_DNI_CN.md), [`docs/GITHUB_ACTIONS.md`](docs/GITHUB_ACTIONS.md)

| Dzień | Godzina (Asia/Shanghai) | GitHub Actions |
|-------|------------------------|----------------|
| Poniedziałek | 20:00 | `CN discovery` |
| Wtorek | 20:00 | `CN discovery` |
| Środa | 21:00 | `CN discovery` |
| Czwartek | 21:00 | `CN discovery` |
| Piątek | 19:00 | `CN discovery` |
| Niedziela | 09:30 | `CN niedziela backfill` |
| Poniedziałek | 10:00 / 11:00 / 14:00 | sync Drive → prep → send |
| Wtorek | 14:00 | `CN wtorek send` |

Offset +5h względem UA — pipeline PL w **osobnym repo**, bez kolizji cron.

Task Scheduler (PC):

```powershell
powershell -ExecutionPolicy Bypass -File schedule\cn\Chiny-Kampania
```

Ręczny pełny pipeline GHA:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_full_pipeline_gha.ps1
```

---

## Limity

| Limit | Wartość |
|-------|---------|
| Serper | 1000 zapytań / dzień |
| E-mail | 300 / dzień, 2 / domena / dzień (pon + wt) |
| Rotacja | 1 województwo / tydzień |

---

## GitHub Actions

Główne workflowy: `cn_materialy_{pi,thu,mon,tue,fri}.yml`, `sync-google-drive-cn.yml`, `cn_fill_nip_drive.yml`, `cn_sync_discovery_excel_drive.yml`, `tests.yml`, `ci-deploy.yml`.

Concurrency: `cn-pipeline` (pipeline tydzień); `cn-drive-nip` (uzupełnianie NIP na Drive — nie blokuje discovery).

Produkcyjny mirror: [Kampania-Chiny](https://github.com/Bigmax1993/Kampania-Chiny) — `gh workflow run … -R Bigmax1993/Kampania-Chiny`.

### GitHub Secrets

| Secret | Wymagany | Opis |
|--------|----------|------|
| `SERPER_API_KEY` | tak | API Serper |
| `ANTHROPIC_API_KEY` | tak | Claude API |
| `MAIL_USER`, `MAIL_PASSWORD` | tak (send) | SMTP / Gmail |
| `MAIL_SENDER_NAME` | tak | Maksym Swinczak |
| `GDRIVE_FOLDER_ID_CN` | tak | `1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC` |
| `GDRIVE_OAUTH_*` | zalecany | Upload OAuth |

**Nie ustawiaj** `GDRIVE_FOLDER_ID_UA` w tym repo.

Google Drive: [`docs/GOOGLE_DRIVE.md`](docs/GOOGLE_DRIVE.md)

Końcowy Excel: [folder Drive CN](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC?usp=drive_link) — `cn_materialy_kontakte.xlsx`

---

## Dokumentacja

| Dokument | Treść |
|----------|--------|
| [`docs/CN_MATERIALY.md`](docs/CN_MATERIALY.md) | Cel, wyszukiwanie, pipeline, pliki |
| [`docs/MAILE.md`](docs/MAILE.md) | Zasady maili + przykłady per firma |
| [`docs/GOOGLE_DRIVE.md`](docs/GOOGLE_DRIVE.md) | Folder Drive i upload Excela |
| [`docs/GITHUB_ACTIONS.md`](docs/GITHUB_ACTIONS.md) | Workflowy, cron, sekrety |
| [`schedule/cn/PLAN_5_DNI_CN.md`](schedule/cn/PLAN_5_DNI_CN.md) | Tydzień discovery / send |

---

## Struktura repo

```
├── cn_materialy_scraper.py
├── cn_contact_fields.py
├── serper_nip_resolve.py
├── cn_province_rotation.py
├── run_config/cn_materialy.json
├── schedule/cn/
├── .github/workflows/cn_materialy_*.yml
├── .github/workflows/cn_fill_nip_drive.yml
├── .github/workflows/cn_sync_discovery_excel_drive.yml
├── docs/CN_MATERIALY.md
├── scripts/fill_nip_in_xlsx.py
├── scripts/run_full_pipeline_gha.ps1
├── tests/test_cn_* + test_serper_nip_resolve.py + test_repo_isolation.py
└── Wyniki/
```
