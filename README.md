# Wyszukiwarka materiałów budowlanych — Chiny (CN)

Repozytorium: [wyszukiwarka-materialow-budowlanych-chiny](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny)

Kampania siostrzana (Polska): [wyszukiwarka-materialow-budowlanych-polska](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-polska)  
Kampania siostrzana (Ukraina): [wyszukiwarka-materialow-budowlanych-ukraina](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-ukraina)

**Produkcja:** `cn_materialy` — hurtownie i składy budowlane w Chinach (GitHub Actions + opcjonalnie Task Scheduler PC).

---

## Pipeline

**Serper (gl=cn, hl=zh-cn) → crawl www → Claude verify (CN) → Excel → maile ZH**

Szczegóły: [`docs/CN_MATERIALY.md`](docs/CN_MATERIALY.md)

| Moduł | Plik |
|-------|------|
| Scraper | `cn_materialy_scraper.py` |
| Frazy per prowincjio | `cn_province_keywords.py` |
| Rotacja prowincji | `cn_province_rotation.py` |
| Filtr dostawców | `cn_materialy_supplier_filter.py` |
| Prompty Claude CN | `cn_claude_prompts.py` |
| Treść maila ZH | `cn_materialy_inquiry_email_zh.py` |

Maile po chińsku, tel. **516513965**, **bez załączników**.

Wyniki: `Wyniki/cn_materialy_cache.json`, `cn_materialy_kontakte.xlsx`.

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
python -m unittest tests.test_cn_materialy_regression -v
python -m pytest tests/test_cn_inquiry_email_zh.py tests/test_cn_materialy_integration.py tests/test_repo_isolation.py -q
```

Pełna bateria: `powershell -ExecutionPolicy Bypass -File scripts\RUN_ALL_TESTS.ps1`

`tests/test_repo_isolation.py` — regresja: brak plików kampanii UA i `legacy/` w tym repo.

---

## Harmonogram

Szczegóły: [`schedule/cn/PLAN_5_DNI_CN.md`](schedule/cn/PLAN_5_DNI_CN.md), [`docs/GITHUB_ACTIONS.md`](docs/GITHUB_ACTIONS.md)

| Dzień | Godzina (Asia/Shanghai) | GitHub Actions |
|-------|------------------------|----------------|
| Pon–Pt | 22:00 / 20:00 / 00:00 / 01:00 / 21:00 | `CN discovery` |
| Niedziela | 10:30 | `CN niedziela backfill` |
| Poniedziałek | 11:00 / 12:00 / 14:00 | sync Drive → prep → send |
| Wtorek | 14:00 | `CN wtorek send` |

Offset +5h względem UA — pipeline PL w **osobnym repo**, bez kolizji cron.

Task Scheduler (PC):

```powershell
powershell -ExecutionPolicy Bypass -File schedule\cn\register_tasks_5_dni.ps1
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
| Rotacja | 1 prowincjio / tydzień |

---

## GitHub Actions

8 workflowów: `cn_materialy_{pi,thu,mon,tue,fri}.yml`, `sync-google-drive-cn.yml`, `tests.yml`, `ci-deploy.yml`.

Concurrency: `cn-pipeline` (w tym repo).

### GitHub Secrets

| Secret | Wymagany | Opis |
|--------|----------|------|
| `SERPER_API_KEY` | tak | API Serper |
| `ANTHROPIC_API_KEY` | tak | Claude API |
| `MAIL_USER`, `MAIL_PASSWORD` | tak (send) | SMTP / Gmail |
| `MAIL_SENDER_NAME` | tak | Maksym Swinczak |
| `GDRIVE_FOLDER_ID_CN` | tak | ID folderu Drive (utwórz folder CN i wklej secret) |
| `GDRIVE_OAUTH_*` | zalecany | Upload OAuth |

**Nie ustawiaj** `GDRIVE_FOLDER_ID_UA` w tym repo.

Google Drive: [`docs/GOOGLE_DRIVE.md`](docs/GOOGLE_DRIVE.md)

---

## Struktura repo

```
├── cn_materialy_scraper.py
├── cn_province_rotation.py
├── run_config/cn_materialy.json
├── schedule/cn/
├── .github/workflows/cn_materialy_*.yml
├── docs/CN_MATERIALY.md
├── scripts/run_full_pipeline_gha.ps1
├── tests/test_cn_* + test_repo_isolation.py
└── Wyniki/
```
