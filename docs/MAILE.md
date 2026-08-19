# Maile kampanii CN

Listy B2B po **polsku** do **polskich dystrybutorów i importerów**.  
Nadawca reprezentuje **chińskiego producenta / eksportera** szukającego partnera dystrybucyjnego w Polsce.

Kod: `cn_claude_inquiry_email.py`, `cn_claude_prompts.py`, `cn_materialy_inquiry_email_zh.py`

---

## Zasady

| Zasada | Opis |
|--------|------|
| Język | wyłącznie polski |
| Personalizacja | **inna treść i temat dla każdej firmy** |
| Nazwa odbiorcy | musi wystąpić w treści (inaczej list jest odrzucany) |
| Fakt ze strony | asortyment, miasto, rola (importer / dystrybutor) |
| Obiekt budowy | tylko z bazy (`cn_regional_construction_refs.py`) — przykład zapotrzebowania w Polsce |
| Telefon | **brak** (nie w treści, nie w podpisie) |
| Strona www nadawcy | **brak** (`swinczakdata.pl` nie wchodzi do listu) |
| Załączniki | **brak** |
| Podpis | `Z poważaniem,` + Maksym Swinczak + linia roli |

Claude dostaje unikalny prompt per firma (nazwa, URL, województwo, adres, kategorie, wyciąg ze strony).  
Szablon stały jest tylko **fallbackiem**, gdy API nie działa — też wstawia nazwę tej firmy.

Limity wysyłki: **300 / dzień**, **2 / domena / dzień** (poniedziałek i wtorek).

---

## Struktura listu

1. `Szanowni Państwo,`
2. Akapit z **nazwą firmy** i konkretem (płytki w Warszawie, armatura w Krakowie, …)
3. Akapit z obiektem budowy (nazwa + adres dosłownie) i prośbą o kontakt ds. importu / dystrybucji
4. Podpis bez telefonu i bez URL

Temat (do 78 znaków), np. `Współpraca dystrybucyjna — {nazwa firmy}`.

---

## Przykład 1 — dystrybutor płytek, Warszawa

**Temat:** Współpraca dystrybucyjna — Warszawski Dystrybutor Płytek Sp. z o.o.

```
Szanowni Państwo,

Zwracam się do Warszawski Dystrybutor Płytek Sp. z o.o., bo na stronie widać import i dystrybucję płytek ceramicznych w Warszawie. Reprezentuję chińskiego producenta płytek i szukamy partnera dystrybucyjnego właśnie w takim profilu.

Jako przykład zapotrzebowania: osiedle mieszkaniowe wielorodzinne Osiedle Wilno, Warszawa, ul. Odkryta 10. Proszę o kontakt do osoby odpowiedzialnej za import lub dystrybucję.

Z poważaniem,
Maksym Swinczak
Współpraca dystrybucyjna / import z Chin
```

---

## Przykład 2 — importer armatury, Kraków

**Temat:** Współpraca dystrybucyjna — Krakowska Armatura Import Sp. z o.o.

```
Szanowni Państwo,

Piszę do Krakowska Armatura Import Sp. z o.o. w związku z Waszą ofertą armatury i oficjalną dystrybucją w Krakowie. Szukamy importera na rynku polskim dla chińskiego producenta armatury i ceramiki sanitarnej.

Przy inwestycjach takich jak kompleks mieszkaniowy Bonarka Living, Kraków, ul. Puszkarska 7H, potrzebne są stałe dostawy. Czy rozważacie Państwo nową linię z Chin?

Z poważaniem,
Maksym Swinczak
Współpraca dystrybucyjna / import z Chin
```

Ten sam ogólnik skopiowany do wszystkich firm **nie przechodzi** weryfikacji.

---

## Czego nie wolno w mailu

- numer telefonu nadawcy, strona www nadawcy
- telefony +380 / +49
- gratis, promocja, kliknij, darmowy
- fikcyjna polska firma-nadawca („Budownictwo XYZ Sp. z o.o.”)
- inny adres budowy niż z bloku «OBIEKT BUDOWY»
- HTML, markdown, załączniki
