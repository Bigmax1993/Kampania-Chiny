# Plan tygodniowy CN — GitHub Actions (Asia/Shanghai)

Kampania **CN**: polscy dystrybutorzy / importerzy (`cn_materialy_scraper.py`, `run_config/cn_materialy.json`).

Wysyłka **pon 14:00** + **wt 14:00** (Shanghai): 2×300 maili/dzień. Maile po polsku, unikalne per firma, bez telefonu i bez strony www.

Opis kampanii: [`docs/CN_MATERIALY.md`](../../docs/CN_MATERIALY.md)  
Maile: [`docs/MAILE.md`](../../docs/MAILE.md)

## Cykl tygodniowy

```
Discovery (tydzień N):
  pon 20:00 → wt 20:00 → śr 21:00 → czw 21:00 → pt 19:00
  artefakt: cn-materialy-wyniki-pi

Backfill + Drive + wysyłka:
  nd 09:30 backfill (pobierz Excel z Drive → append → 2× JSON → ten sam plik na Drive)
  pon 10:00 sync Drive
  pon 11:00 prep (Excel → 2× JSON uzupełnienie → Drive)
  pon 14:00 send partia 1
  wt 14:00 send partia 2
```

## Cron (Asia/Shanghai)

| Workflow | Cron |
|----------|------|
| CN discovery | `0 20 * * 1`, `0 20 * * 2`, `0 21 * * 3`, `0 21 * * 4`, `0 19 * * 5` |
| CN niedziela backfill | `30 9 * * 0` |
| Sync Drive CN | `0 10 * * 1` |
| CN poniedzialek prep | `0 11 * * 1` |
| CN poniedzialek send | `0 14 * * 1` |
| CN wtorek send | `0 14 * * 2` |

Secret Drive: `GDRIVE_FOLDER_ID_CN` = `1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC`

Folder: [CN Materialy — Google Drive](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC?usp=drive_link)

Plik Excel: `cn_materialy_kontakte.xlsx`

Concurrency: `cn-pipeline` — osobne repo, bez kolizji z PL/UA.

## Task Scheduler (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File "schedule\cn\register_tasks_5_dni.ps1"
```
