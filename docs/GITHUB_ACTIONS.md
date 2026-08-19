# GitHub Actions — kampania PL

Repozytorium: [wyszukiwarka-materialow-budowlanych-chiny](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny)

Kampania UA (osobne repo): [wyszukiwarka-materialow-budowlanych-ukraina](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-ukraina)

## Workflowy (8)

| Workflow | Plik | Trigger | Co robi |
|----------|------|---------|---------|
| **Tests** | `tests.yml` | push, PR | smoke PL + pytest + `test_repo_isolation` |
| **CI Deploy** | `ci-deploy.yml` | push | smoke PL + secrets + dry-run maili |
| **CN discovery** | `cn_materialy_pi.yml` | cron, ręcznie | Discovery pon–pt → `cn-materialy-wyniki-pi` |
| **CN niedziela backfill** | `cn_materialy_thu.yml` | cron, ręcznie | Crawl www + Excel → Drive → walidacja JSON → `cn-materialy-wyniki-thu` |
| **CN poniedzialek prep** | `cn_materialy_mon.yml` | cron, ręcznie | Rebuild Excel → `cn-materialy-wyniki-mon` |
| **CN poniedzialek send** | `cn_materialy_tue.yml` | cron, ręcznie | Wysyłka partia 1 (300) → `cn-materialy-wyniki-tue` |
| **CN wtorek send** | `cn_materialy_fri.yml` | cron, ręcznie | Wysyłka partia 2 → `cn-materialy-wyniki-fri` |
| **Sync wyniki Google Drive CN** | `sync-google-drive-cn.yml` | cron pon 10:00, ręcznie | Upload `Wyniki/` → folder CN |

## Harmonogram cron (Asia/Shanghai)

| Dzień | Workflow | Cron | Godzina |
|-------|----------|------|---------|
| Poniedziałek | discovery 1 | `0 22 * * 1` | **22:00** |
| Wtorek | discovery 2 | `0 20 * * 2` | **20:00** |
| Czwartek | discovery 3 | `0 0 * * 4` | **00:00** |
| Piątek | discovery 4 | `0 1 * * 5` | **01:00** |
| Piątek | discovery 5 | `0 21 * * 5` | **21:00** |
| Niedziela | backfill | `30 10 * * 0` | **10:30** |
| Poniedziałek | sync Drive | `0 11 * * 1` | **11:00** |
| Poniedziałek | prep | `0 12 * * 1` | **12:00** |
| Poniedziałek | send 1 | `0 14 * * 1` | **14:00** |
| Wtorek | send 2 | `0 14 * * 2` | **14:00** |

Offset +5h względem UA — osobne repozytorium, osobny `cn-pipeline`.

## Sekrety

| Secret | Wymagany | Opis |
|--------|----------|------|
| `SERPER_API_KEY` | tak | API Serper |
| `ANTHROPIC_API_KEY` | tak | Claude API |
| `MAIL_USER`, `MAIL_PASSWORD` | tak | SMTP |
| `MAIL_SENDER_NAME` | tak | Maksym Swinczak |
| `GDRIVE_FOLDER_ID_CN` | tak | osobny folder Drive dla Chin |
| `GDRIVE_OAUTH_*` | zalecany | OAuth upload |

**Nie ustawiaj** `GDRIVE_FOLDER_ID_UA` w tym repo.

## Artefakty

```
pon→pi | wt→pi | czw→pi | pt→pi (×2) → nd→thu → sync PL → pon prep→mon → pon send→tue → wt send→fri
```

**PL send:** bez załącznika; tel. **516513965**; maile po chińsku.

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
Kampania: [`docs/CN_MATERIALY.md`](PL_MATERIALY.md)
