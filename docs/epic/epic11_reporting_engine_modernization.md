# Epic 11: Reporting Engine Modernization & Strict I18n Parity

## 1. Yhteenveto (Executive Summary)
**Tila:** Suunnittelussa
**Konteksti:** Phase 9 Hardening & Admin Studio Parity Hotfix
**Tavoite:** Saavuttaa 100% "Zero-Dynamic Mandate" koko järjestelmän laajuisesti korvaamalla Raportointimoottorin (Reporting Engine) käyttämät vanhanaikaiset litteät dict-lokalisoinnit uudella `I18nText`-standardilla.

Vuoden 2026 System Architecture Manifeston "No-String Mandate" vaatii, että kaikki käyttöliittymälle (Flutter) toimitettavat dynaamiset tekstit ovat rakenteellisia `I18nText` -objekteja. Phase 9 -pariteettikorjauksissa havaittiin, että V1-aikakauden Raportointimoottori tuottaa yhä otsikoita (title, description, profile_name) litteässä `{"fi": "Otsikko", "en": "Title"}` -muodossa, mikä pakotti `ReportDataDTO` ja `ReportLayoutDTO` -mallit käyttämään kompromissityypitystä `dict[str, str]` (Python) ja `Map<String, dynamic>` (Dart).

Tämä Epic eliminoi tämän viimeisen arkkitehtuurisen velan ja yhtenäistää raporttidatan Pydantic- ja Freezed-mallien absoluuttisen lokalisointipariteetin.

---

## 2. Ongelman Kuvaus ja Rajoitteet (The Core Hazard)

> [!IMPORTANT]
> **"Clean Slate" Mandaatti (Nolla-Toleranssi):**
> Koska järjestelmä ei ole vielä aktiivisessa tuotannossa, tämä Epic toteutetaan vaatimalla *puhdas pöytä* (Clean Slate). Mitään yhteensopivuutta vanhojen litteiden sanakirjojen kanssa ("fallback"), purkkavirityksiä tyyppimuunnoksissa, tai laiskoja oletusarvomäppäyksiä ei sallita (Backend/Frontend). Uuden siirtymän on oltava puhdas, ehdoton ja täydellisen tyyppiturvallinen.

**Nykyinen (Legacy) Rakenne:**
Pydantic sallii tällä hetkellä litteän dictionary-tyypityksen Raporttidatoille:
```python
# v2_core.py -> ReportLayoutDTO
title: dict[str, str] = Field(default_factory=dict) # Esim. {"fi": "Tulokset"}
```

**Tavoiteltu (Strict) Rakenne:**
Arkkitehtuurin vaatima `I18nText` -luokka on monimutkaisempi ja vaatii avaimet `default_locale` sekä `translations`:
```python
# v2_core.py -> ReportLayoutDTO
title: I18nText | None = Field(default=None)
# JSON Data UI:lle: {"default_locale": "fi", "translations": {"fi": "Tulokset"}}
```

**Miksi tätä ei voitu korjata välittömästi "lennosta" aikaisemmassa Parity Hotfixissä?**
Jos litteä tyypitys olisi vain laiskasti pyyhitty pois, se olisi aiheuttanut välittömän ja laajan kaatumisen koko arkkitehtuurissa ("Fail-Fast"), koska:
1. Sillä ei olisi ollut käytössään Freezed-generoitua `I18nText.fromJson` jäsennintä näille kentille.
2. Dartin käyttöliittymäkoodi (esim. Report Renderer) olettaa otsikon olevan `Map` ja kutsuu suoraan `title[langCode]`, kun sen tulisi kutsua `title.get(langCode)`.
3. PDF-latausmoottori (Flutter/Backend) olisi menettänyt synkronisaation tietorakenteiden kanssa.

---

## 3. Toteutussuunnitelma (Implementation Milestones)

Tämä Epic jaetaan tarkasti hallittuihin vaiheisiin, jotta tuotannon SSoT-yhteys (Single Source of Truth) ei katkea missään vaiheessa.

### Milestone 1: Raportointimoottorin Tyyppimuunnos (Backend)
- Etsi kaikki palvelut (`backend_v2/services/...`), jotka tuottavat raporttilohkojen ja akselien otsikoita.
- Refaktoroi datan kasaaminen siten, että litteiden sanakirjojen sijaan asioista luodaan aitoja `I18nText(translations={"fi": ...})` olioita, ennen kuin ne injektoidaan `ReportDataDTO`-luokkaan.
- Päivitä `ReportDataDTO` ja `ReportLayoutDTO` malleissa kenttien tyypitykseksi `I18nText` (tai `dict[str, I18nText]` esimerkiksi `available_profiles` -listaukselle).

### Milestone 2: Dart DTO ja Parseri Pariteetti (Frontend)
- Päivitä `client_app_v2/lib/features/execution/models/report_data_dto.dart`.
- Muuta `profileName`, `title` ja `description` käyttämään `I18nText`-määrittelyä.
- Päivitä Dartin `fromJson()`-tehdasmetodi lataamaan arvot turvallisesti `I18nText.fromJson(...)` kautta (Graceful Degradation -protokollan mukaisesti).
- Aja `build_runner` viedäksesi koodigeneroinnit läpi absoluuttisella tarkkuudella.

### Milestone 3: Käyttöliittymän Sovitus (UI Refactoring)
- Paikanna kaikki paikat käyttöliittymästä, jotka lukevat raporttia (`execution_view`, `dashboard_view`, PDF-generaattorin koodi jne.) ja poista vanhentunut litteä haku `element.title[locale]`.
- Korvaa haut `I18nText`-standardin mukaisella `element.title.get(locale)` -metodikutsulla.
- Varmista, että sovellus kääntyy virheittä `dart analyze` -ajossa.

### Milestone 4: Siementiedon ja Tietokannan Migraatio
- Etsi alkuperäisestä tietokannan migraatiodokumentista tai `seed_data.json`-tiedostosta kaikki Workflown Output Profilet, joissa profiilien otsikot tai layouttien tekstit makaavat litteänä jsonina tietokannassa.
- Aja skripti (tai refaktoroi Seed-data käsin), jotta se vastaa uutta monimutkaisempaa `I18nText` hierarkiaa.

---

## 4. Työn Valmiuden Määritelmä (Definition of Done)
1. Koko arkkitehtuurissa ei ole yhtäkään laiskaa `dict[str, str]` DTO-määritystä lokalisoinnille.
2. `dart analyze` ja `uv run mypy` menevät puhtaasti läpi ilman virheitä.
3. Koko "Fail-Fast" ympäristö on palautettu käyttöön; rikkinäinen litteä dict kaataa ohjelman välittömästi `AppException`-tasolla (Error Code 422 tai 500).
4. Raportit tulostuvat jälleen selkeästi käyttöliittymän Execution-näkymässä valitun lokaalin (lokalisaation) mukaisesti.
