# GitHub Actions — kampania CN

Repozytorium: [wyszukiwarka-materialow-budowlanych-chiny](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny)

Kampania: [`docs/CN_MATERIALY.md`](CN_MATERIALY.md)  
Maile: [`docs/MAILE.md`](MAILE.md)  
Drive: [`docs/GOOGLE_DRIVE.md`](GOOGLE_DRIVE.md)

## Workflowy

| Workflow | Plik | Trigger | Co robi |
|----------|------|---------|---------|
| **Tests** | `tests.yml` | push, PR | smoke + pytest + `test_repo_isolation` |
| **CI Deploy** | `ci-deploy.yml` | push | smoke + secrets + dry-run maili |
| **CN discovery** | `cn_materialy_pi.yml` | cron, ręcznie | Discovery pon–pt → `cn-materialy-wyniki-pi` |
| **CN niedziela backfill** | `cn_materialy_thu.yml` | cron, ręcznie | Crawl www (w tym NIP ze stron Kontakt) → append do istniejącego Excela na Drive → **2×** JSON→Excel → Drive (ten sam plik) → `cn-materialy-wyniki-thu` |
| **CN poniedzialek prep** | `cn_materialy_mon.yml` | cron, ręcznie | Rebuild Excel → **2×** JSON→Excel → Drive (append do tego samego pliku) → `cn-materialy-wyniki-mon` |
| **CN poniedzialek send** | `cn_materialy_tue.yml` | cron, ręcznie | Wysyłka partia 1 (300) → `cn-materialy-wyniki-tue` |
| **CN wtorek send** | `cn_materialy_fri.yml` | cron, ręcznie | Wysyłka partia 2 → `cn-materialy-wyniki-fri` |
| **PL rebuild Excel** | `cn_materialy_rebuild_excel.yml` | ręcznie | Przebudowa `cn_materialy_kontakte.xlsx` z cache + opcjonalny upload Drive |
| **Sync wyniki Google Drive CN** | `sync-google-drive-cn.yml` | cron pon 10:00, ręcznie | Upload `Wyniki/` → [folder CN](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC) |

Excel na Drive: arkusz **Kontakte** = pełne kontakty; **Prowincje** = indeks regionu. Opis kolumn: [`CN_MATERIALY.md`](CN_MATERIALY.md#excel-i-google-drive).

Concurrency: `cn-pipeline` (w tym repo).

## Harmonogram cron (Asia/Shanghai)

| Dzień | Workflow | Cron | Godzina (Shanghai) |
|-------|----------|------|--------------------|
| Poniedziałek | discovery | `0 20 * * 1` | 20:00 |
| Wtorek | discovery | `0 20 * * 2` | 20:00 |
| Środa | discovery | `0 21 * * 3` | 21:00 |
| Czwartek | discovery | `0 21 * * 4` | 21:00 |
| Piątek | discovery | `0 19 * * 5` | 19:00 |
| Niedziela | backfill | `30 9 * * 0` | 09:30 |
| Poniedziałek | sync Drive | `0 10 * * 1` | 10:00 |
| Poniedziałek | prep | `0 11 * * 1` | 11:00 |
| Poniedziałek | send 1 | `0 14 * * 1` | 14:00 |
| Wtorek | send 2 | `0 14 * * 2` | 14:00 |

## Sekrety

| Secret | Wymagany | Opis |
|--------|----------|------|
| `SERPER_API_KEY` | tak | API Serper |
| `ANTHROPIC_API_KEY` | tak | Claude API |
| `MAIL_USER`, `MAIL_PASSWORD` | tak | SMTP / Gmail |
| `MAIL_SENDER_NAME` | tak | Maksym Swinczak |
| `GDRIVE_FOLDER_ID_CN` | tak | `1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC` |
| `GDRIVE_OAUTH_*` | zalecany | OAuth upload |

**Nie ustawiaj** `GDRIVE_FOLDER_ID_PL` ani `GDRIVE_FOLDER_ID_UA` w tym repo.

## Artefakty

```
pon–pt discovery → cn-materialy-wyniki-pi
niedziela backfill → cn-materialy-wyniki-thu  (+ Excel na Drive)
pon prep → cn-materialy-wyniki-mon
pon send → cn-materialy-wyniki-tue
wt send → cn-materialy-wyniki-fri
```

**CN send:** bez załącznika; maile po polsku, spersonalizowane per firma (bez telefonu i bez strony www).

## Ręczne uruchomienie

```powershell
gh workflow run "CN discovery" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny
gh workflow run "CN discovery" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny -f discovery_phase=mon
gh workflow run "CN niedziela backfill" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny
gh workflow run "Sync wyniki Google Drive CN" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny
gh workflow run "CN poniedzialek prep" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny
gh workflow run "CN poniedzialek send" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny -f force_resend=true
gh workflow run "CN wtorek send" -R Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny -f force_resend=true
```

Pełny łańcuch: `scripts/run_full_pipeline_gha.ps1`  
Harmonogram PC: [`schedule/cn/PLAN_5_DNI_CN.md`](../schedule/cn/PLAN_5_DNI_CN.md)
