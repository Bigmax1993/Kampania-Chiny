# Plan tygodniowy PL — +5h względem UA (brak nakładania pipeline)

Kampania **PL materiały budowlane** (`cn_materialy_scraper.py`, `run_config/cn_materialy.json`).
Wysyłka **pon 14:00** + **wt 14:00** (2×300 maili/dzień). Maile po chińsku, tel. **516513965**.

## Offset względem UA

Każdy etap PL startuje **5 godzin po** odpowiednim etapie UA. Po rozdzieleniu repozytoriów oba pipeline działają niezależnie (osobne repo, osobne secrets, osobny `cn-pipeline` / `ua-pipeline`).

| Etap | UA (PL czas) | PL (+5h) |
|------|--------------|----------|
| Pon discovery | 17:00 | **22:00** |
| Wt discovery | 15:00 | **20:00** |
| Śr discovery | 19:00 (śr) | **00:00** (czw) |
| Czw discovery | 20:00 (czw) | **01:00** (pt) |
| Pt discovery | 16:00 | **21:00** |
| Nd backfill | 05:30 | **10:30** |
| Pon sync Drive | 06:00 | **11:00** |
| Pon prep | 07:00 | **12:00** |
| Pon send | 09:00 | **14:00** |
| Wt send | 09:00 | **14:00** |

## Cykl tygodniowy

```
Tydzień N (discovery PL):
  pon 22:00 → wt 20:00 → śr 00:00 → czw 01:00 → pt 21:00   [cn-materialy-wyniki-pi]

Tydzień N-1 (backfill + wysyłka):
  nd 10:30 → pon 11:00 sync → pon 12:00 prep → pon 14:00 send → wt 14:00 send
```

## GitHub Actions

| Workflow | Cron (Asia/Shanghai) |
|----------|----------------------|
| CN discovery | `0 22 * * 1`, `0 20 * * 2`, `0 0 * * 4`, `0 1 * * 5`, `0 21 * * 5` |
| CN niedziela backfill | `30 10 * * 0` |
| Sync Drive PL | `0 11 * * 1` |
| CN poniedzialek prep | `0 12 * * 1` |
| CN poniedzialek send | `0 14 * * 1` |
| CN wtorek send | `0 14 * * 2` |

Secret Drive: `GDRIVE_FOLDER_ID_CN` (utwórz folder CN na Drive i wklej ID do secretu).

Plik Excel: `cn_materialy_kontakte.xlsx` (wersjonowany z datą przy uploadzie).

## Task Scheduler (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File "schedule\cn\register_tasks_5_dni.ps1"
```
