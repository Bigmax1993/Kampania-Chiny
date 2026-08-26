# Kampania CN — dystrybutorzy materiałów budowlanych w Polsce

Produkt dla **chińskich producentów i eksporterów**: baza zweryfikowanych **polskich importerów i dystrybutorów** (w tym wyłącznych / oficjalnych) na terenie Polski.

Repozytorium: [wyszukiwarka-materialow-budowlanych-chiny](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny)

Siostrzane kampanie:

- Polska (hurtownie w PL): [wyszukiwarka-materialow-budowlanych-polska](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-polska)
- Ukraina: [wyszukiwarka-materialow-budowlanych-ukraina](https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-ukraina)

To **nie** jest wyszukiwanie firm w Chinach. Serper i crawl działają na **Polskę**; maile idą po polsku do firm w Polsce.

---

## Cel biznesowy

Chińscy eksporterzy (płytki, ceramika, armatura, LED, SPC, aluminium, chemia, okna PVC, stal, drzwi, kabiny prysznicowe, instalacje sanitarne) kupują tanie „名录” albo droższe dane celne. Lepszy produkt: **lista zweryfikowanych dystrybutorów / importerów w Polsce** pod te kategorie eksportowe.

| Szukamy | Nie szukamy |
|---------|-------------|
| importer, dystrybutor, wyłączny / oficjalny / autoryzowany dystrybutor | sklep wyłącznie detaliczny |
| hurt B2B, przedstawiciel, agent importu | ogłoszenia OLX / Allegro |
| firma z adresem w Polsce (.pl, +48, NIP, województwo) | wykonawca / wykończenia bez sprzedaży materiałów |
| katalog / cennik / asortyment | portale, urzędy, oferty pracy |

---

## Pipeline

```
Serper (gl=pl, hl=pl)
  → filtr roli (importer / dystrybutor)
  → crawl www
  → Claude verify (firma w Polsce)
  → Excel cn_materialy_kontakte.xlsx
  → maile PL (Claude, unikalne per firma)
  → Google Drive
```

| Element | Wartość |
|---------|---------|
| Scraper | `cn_materialy_scraper.py` |
| Run config | `run_config/cn_materialy.json` |
| Test config | `run_config/cn_mazowieckie_test.json` |
| Cache | `Wyniki/cn_materialy_cache.json` |
| Excel | `Wyniki/cn_materialy_kontakte.xlsx` |
| Drive | [folder CN](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC) |
| ID folderu | `1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC` |
| Secret | `GDRIVE_FOLDER_ID_CN` |
| Strefa cron | `Asia/Shanghai` |

---

## Wyszukiwanie (Serper)

- Kraj: `gl=pl`, język: `hl=pl`, ograniczenie: `PL`
- Geografia: **16 województw** (rotacja: jedno województwo na cykl discovery)
- Kolejność rotacji: mazowieckie → śląskie → małopolskie → wielkopolskie → dolnośląskie → pomorskie → łódzkie → zachodniopomorskie → lubelskie → podkarpackie → kujawsko-pomorskie → warmińsko-mazurskie → świętokrzyskie → podlaskie → lubuskie → opolskie

**Role:** importer, dystrybutor, wyłączny dystrybutor, oficjalny dystrybutor, autoryzowany dystrybutor, wyłączny / oficjalny importer, przedstawiciel, agent, hurt, dystrybucja, import

**Kategorie:** płytki, ceramika, armatura, LED, SPC, profile aluminiowe, chemia budowlana, okna PVC, stal (konstrukcyjna, nierdzewna, ocynkowana, blachy, rury, profile, pręty, zbrojeniowa), drzwi (wewnętrzne, zewnętrzne, stalowe, aluminiowe), kabiny prysznicowe, brodziki, instalacje sanitarne, armatura łazienkowa, sanitariat

**Przykładowe frazy:** `{miasto} dystrybutor {kategoria}`, `{miasto} importer {kategoria}`, `{miasto} hurtownia {kategoria}`, `wyłączny dystrybutor {kategoria} {miasto}`, `oficjalny dystrybutor {kategoria} Polska`

**Minusy:** OLX, Allegro, ogłoszenia, sklep, praca, remont, wykończenia wnętrz, urzędy, portale

Moduły: `cn_province_keywords.py`, `cn_province_rotation.py`, `cn_materialy_supplier_filter.py`

---

## Weryfikacja Claude (strona www)

Prompt: `cn_claude_prompts.py` → `build_page_verify_prompt`

Cel (`is_gu=true`) tylko gdy **jednocześnie**:

1. Rola B2B: importer / dystrybutor / wyłączny lub oficjalny dystrybutor / hurt
2. Asortyment materiałów (kategorie powyżej)
3. Działalność w **Polsce**

---

## Maile

Szczegóły i przykłady: [`docs/MAILE.md`](MAILE.md)

Krótko:

- Język: **polski**
- Nadawca: Maksym Swinczak — chiński producent / eksporter szuka dystrybutora w Polsce
- **Unikalny list na każdą firmę** (nazwa odbiorcy + fakt ze strony)
- **Bez telefonu, bez strony www, bez załączników**
- Limity: 300 / dzień, 2 / domena / dzień (poniedziałek + wtorek)

---

## Excel i Google Drive

Końcowy plik: **`cn_materialy_kontakte.xlsx`** (trzy arkusze).

| Arkusz | Rola |
|--------|------|
| **Kontakte** | Pełna baza kontaktów B2B — tu są wszystkie dane firm (e-mail, telefon, NIP itd.). |
| **Prowincje** | Tylko indeks regionu (bez e-maila / telefonu / NIP). |
| **Info** | Opis pliku i kolumn. |

**Pełne kontakty oglądaj wyłącznie w arkuszu Kontakte.** Prowincje nie jest kopią bazy — służy do szybkiego filtrowania po województwie.

### Kontakte — kolumny

Wartości po angielsku; **Name of Company** bez tłumaczenia.

| Kolumna | Źródło |
|---------|--------|
| Name of Company | nazwa firmy |
| Line of business | kategoria / fraza discovery (EN) |
| Company website | strona www |
| E-Mail | e-mail do oferty |
| Phone number | telefon |
| Region | województwo (EN, np. Masovian Voivodeship) |
| Localisation | adres (EN: St. / Warsaw) |
| Postcode | kod pocztowy PL (XX-XXX) |
| Tax Identification Number | NIP PL (10 cyfr, bez spacji i myslnikow) |
| URL | bazowy URL firmy |

### Prowincje — kolumny

| Kolumna | Opis |
|---------|------|
| Name of Company | nazwa firmy |
| Region | województwo (EN) |
| Localisation | adres (EN) |
| URL | bazowy URL |

### Tax Identification Number (NIP)

NIP jest wyciągany z crawlowanej strony (priorytet: `/kontakt`, `/o-firmie`, `/dane-firmy`, stopka) przez `cn_contact_fields.extract_pl_nip_from_text` — etykiety m.in. `NIP`, `Nr NIP`, `Tax Identification Number`, `PL` + 10 cyfr.  
Strony Kontakt trafiają na początek `page_snippet`, żeby NIP nie wypadał poza limit 3500 znaków.  
Po zmianie logiki NIP potrzebny jest **crawl / backfill** (same stare snippetty w cache bez NIP nie wystarczą).

Folder: [https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC](https://drive.google.com/drive/folders/1ZzEvH0lkoO3SSTJYFCy-HzY57ccsYaVC?usp=drive_link)

Nie używaj folderów PL (`1O15CdN0…`) ani UA (`1NeQnfW-…`).

Na końcu niedzieli (backfill) Excel to **zawsze ten sam plik** `cn_materialy_kontakte.xlsx`: pipeline pobiera go z Drive, dopisuje nowe firmy i puste pola, potem **dwa razy** sprawdza względem `*_cache.json` i wgrywa z powrotem (append po URL, bez kopii z datą). Przy uzupełnianiu z JSON walidacja jest **luźniejsza** niż przy discovery (np. adres bez kodu pocztowego), ale nadal bez śmieci (OLX/Allegro, noreply, „Kontakt”, teksty marketingowe). Jeśli po obu rundach nadal są luki — job pada (`VERIFY_FAIL`). Poniedziałkowy prep robi to samo.

**Uwaga:** Excel **nie** leży w repo GitHub (`Wyniki/` w `.gitignore`). Produkcyjny plik jest na Google Drive; lokalny / artefakt Actions może różnić się od Drive, dopóki nie przejdzie sync/backfill.

Opis sync: [`docs/GOOGLE_DRIVE.md`](GOOGLE_DRIVE.md)

---

## Harmonogram (GitHub Actions)

Strefa: **Asia/Shanghai**. Szczegóły: [`docs/GITHUB_ACTIONS.md`](GITHUB_ACTIONS.md), [`schedule/cn/PLAN_5_DNI_CN.md`](../schedule/cn/PLAN_5_DNI_CN.md)

| Dzień | Godzina (Shanghai) | Workflow |
|-------|--------------------|----------|
| Poniedziałek | 20:00 | discovery |
| Wtorek | 20:00 | discovery |
| Środa | 21:00 | discovery |
| Czwartek | 21:00 | discovery |
| Piątek | 19:00 | discovery |
| Niedziela | 09:30 | backfill www + Excel → 2× JSON → Drive |
| Poniedziałek | 10:00 | sync Drive |
| Poniedziałek | 11:00 | prep Excel → 2× JSON → Drive |
| Poniedziałek | 14:00 | wysyłka partia 1 |
| Wtorek | 14:00 | wysyłka partia 2 |

Concurrency: `cn-pipeline` (osobne repo — bez kolizji z PL/UA).

---

## Pliki kodu

| Moduł | Plik |
|-------|------|
| Scraper / Excel Kontakte + Prowincje | `cn_materialy_scraper.py` |
| NIP, adres, nazwa (PL) | `cn_contact_fields.py` |
| Tłumaczenie pól Excel (EN) | `cn_excel_en.py` |
| Frazy i województwa | `cn_province_keywords.py` |
| Rotacja | `cn_province_rotation.py` |
| Filtr | `cn_materialy_supplier_filter.py` |
| Prompty Claude | `cn_claude_prompts.py` |
| Generacja maila | `cn_claude_inquiry_email.py` |
| Szablon / podpis | `cn_materialy_inquiry_email_zh.py` |
| Kontekst nadawcy | `cn_regional_sender_context.py` |
| Obiekty budowy (zapotrzebowanie) | `cn_regional_construction_refs.py` |
| Ścieżki i Drive ID | `campaign_data_paths.py` |
| Walidacja Excel vs JSON | `scripts/verify_excel_from_json.py` |

Nazwy `cn_*` zostają (izolacja: w tym repo **nie** może być `pl_*.py` / `ua_*.py`).

---

## Testy

```powershell
$env:KANBUD_PROJECT_ROOT = "$PWD\libs"
python cn_materialy_scraper.py --test
python -m pytest tests/ -q
```

Pełna bateria (compile + smoke + regresja): `powershell -ExecutionPolicy Bypass -File scripts\RUN_ALL_TESTS.ps1`

---

## Lokalny start

```powershell
git clone https://github.com/Bigmax1993/wyszukiwarka-materialow-budowlanych-chiny.git
cd wyszukiwarka-materialow-budowlanych-chiny
pip install -r requirements.txt
$env:KANBUD_PROJECT_ROOT = "$PWD\libs"
Copy-Item .env.example .env

python cn_materialy_scraper.py --test
python cn_materialy_scraper.py --run-config run_config\cn_materialy.json --serper-only-discovery --no-auto-email --rotate-province
```

Sekrety na CI: README → GitHub Secrets. Lokalnie nie commituj `.env`.
