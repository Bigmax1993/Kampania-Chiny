# Kampania CN - materialy budowlane (Chiny)

Scraper B2B: hurtownie, sklady i dystrybutorzy materialow budowlanych w Chinach.

Repozytorium: [wyszukiwarka-materialow-budowlanych-chiny](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny)

| Element | Wartosc |
|---------|---------|
| Scraper | cn_materialy_scraper.py |
| Run config | run_config/cn_materialy.json |
| Cache | Wyniki/cn_materialy_cache.json |
| Excel | Wyniki/cn_materialy_kontakte.xlsx |
| Drive | GDRIVE_FOLDER_ID_CN (osobny folder Drive) |

Harmonogram: [schedule/cn/PLAN_5_DNI_CN.md](../schedule/cn/PLAN_5_DNI_CN.md)
GitHub Actions: [docs/GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)

Pelna dokumentacja kampanii: README.md i docs/GITHUB_ACTIONS.md w tym repo.

## Pipeline

Serper (gl=cn) -> filtr dostawcy -> discovery (pon-pt) / backfill (nd) -> Claude verify -> Excel -> maile PL.

## Testy

`powershell
python cn_materialy_scraper.py --test
python -m unittest tests.test_cn_materialy_regression -v
python -m pytest tests/test_cn_inquiry_email_zh.py tests/test_cn_materialy_integration.py tests/test_repo_isolation.py -q
`

## Maile

- Jezyk: chiński
- Telefon: **516513965**
- Bez zalacznikow
- Limity: 300/dzien, 2/domena/dzien
