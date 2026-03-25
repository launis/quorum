# EPIC: V3 Dead Code Abatement & Configuration Sovereignty

**STATUS:** Draft / Planning Phase  
**TIER:** Tier 1 (Epic Planner)  
**CONTEXT:** Quorum V3 Architecture (Python Backend V2 + Flutter Client V2)  
**LAST UPDATED:** 2026-03-25

## 📌 1. Objective

Tavoitteena on tunnistaa ja tuhota säälimättä kaikki V1/V2 jäänteet ja turhat ohjelmatodistukset sekä backendistä että frontendistä. Rinnalla:
1. Päivitetään aukottomasti `docs/reference.md` jäljelle jäävillä elävillä ohjelmilla.
2. Eliminoidaan **piilotetut fallback-oletusarvot** jotka peittävät konfiguraatiovirheitä.
3. Poistetaan **orpo-kentät** joita mikään komponentti ei enää tuota tai kuluta.

> [!CAUTION]
> NO CODE SHALL BE DELETED WITHOUT EXPLICIT USER APPROVAL. Zero-Trust -metodologia: automaattiset työkalut tuottavat false-positiivisia (esim. FastAPI Pydantic-reitit), joten jokainen poistoehdokas (Kill List) on varmennettava manuaalisesti.

---

## 📚 2. Tapaustutkimukset (Motivoivat esimerkit)

### Case 1: `synthesis` -haamukenttä (Korjattu 2026-03-24)
- **Oireet:** `Empty Synthesis` -WARNING lokissa joka renderissä, 5+ kertaa per ajo
- **Juurisyy:** `blueprint.py` etsi `"synthesis"` stepin tuloksista, mutta V2:n PromptBlock-arkkitehtuurissa yksikään blokki ei tuota kenttää tällä nimellä
- **Levinneisyys:** `v2_core.py` (malli), `blueprint.py` (palvelu), `report_data_dto.dart` (frontend), 2 testiä
- **Oppi:** Nullable/Optional -kentät eivät kaadu → ongelma jää huomaamatta kuukausiksi

### Case 2: RPM/TPM Fallback -oletusarvot (Korjattu 2026-03-24)
- **Oireet:** `429 RESOURCE_EXHAUSTED` Vertex AI:sta, hitaat ajot
- **Juurisyy:** `handler.py` käytti `cd.get("tpm_limit", 0)` — hiljainen fallback peitti puuttuvan konfiguraation
- **Levinneisyys:** `client.py`, `handler.py`, `auth.py` (3 mallia)
- **Oppi:** `or DEFAULT` / `.get(key, fallback)` piilottaa konfiguraatiovirheitä. Fail-Fast on ainoa turvallinen malli.

---

## 🔍 3. Kolmivaiheinen Varmennusprotokolla (The 3-Way Verification)

Jokainen epäilty tiedosto/kenttä käy läpi vähintään kolme toisistaan riippumatonta testiä:

| # | Vaihe | Työkalu | Mitä etsitään |
|---|-------|---------|---------------|
| 1 | **Staattinen Analyysi** | `vulture`, `flutter analyze` | Orpo-funktiot, käyttämättömät importit, dead branches |
| 2 | **Käsityö-Grep** | `grep_search` koko codebaseen | Nimellä/ID:llä etsintä, dynaamiset injektiot, test fixtures |
| 3 | **Arkkitehtuurin Todistus** | Manuaalinen analyysi | Voiko koodi toimia V3-moottorissa? Onko se SDUI/LangChain/V1-jäänne? |

---

## 🚨 4. Banned Patterns (Kielletyt Toimintamallit)

- **Blind Faith in Vulture:** Ei sokeaa poistoa AST-analyysin perusteella (Pydantic-validaattorit, FastAPI-reitit)
- **Rogue Formatting:** Ei uudelleenmuotoilua + poistoa samassa commitissa
- **Modifying Seed/DB:** Seed/DB muutokset noudattavat Configuration Backup Protocolia
- **Partial Removal:** Kentän poiston PITÄÄ kattaa: malli → palvelu → frontend DTO → testit → .arb-käännökset

---

## 🎯 5. Auditointikategoriat

### 5.1 Piilotetut Fallbackit (Configuration Sovereignty)

Nämä regex-hakulausekkeet paljastavat piilotettuja oletusarvoja:

```
# Hiljainen dict-fallback (ei 0/tyhjä usage-laskureihin)
\.get\(.+, (True|False)\)          → Boolean-oletus voi aktivoida/deaktivoida ominaisuuksia
\.get\(.+, \d{2,}\)                → Numeerinen fallback voi peittää puuttuvan rajan

# Inline-fallback
if .+ is not None else [^N]       → Korvaa None → arvolla ilman fail-fast
or \d{2,}                         → Suuret numerot (>10) ovat epäilyttäviä

# Pydantic-mallien oletusarvot
Field\(default=\d+                 → Konfiguraatioarvo jolla on oletusarvo
: int = \d{3,}                     → Tuhansia olettava oletusarvo
: int = \d+$                       → Numeerinen oletus ilman Field-validointia
```

**Sääntö:** Konfiguraatioarvot (rajat, rajaukset, featureflagit) → **fail-fast, ei oletuksia.**  
**Poikkeus:** Usage-laskurit, rendering-arvot → 0/tyhjä on semanttisesti oikea oletus.

### 5.2 Orpo-kentät (Ghost Fields)

Etsitään kenttiä jotka ovat olemassa mallissa mutta joita kukaan ei tuota:

```
1. Listaa ReportDataDTO / ExecutionResult kentät
2. Jokaiselle kentälle: grep koko codebasesta
3. Jos kenttää asetetaan VAIN mallissa (default) eikä koskaan eksplisiittisesti → ORPO
```

### 5.3 Orpo-tiedostot (Dead Files)

```bash
# Python
vulture backend_v2/ --min-confidence 80

# Dart
dart run dart_code_metrics:metrics check-unused-files lib
```

---

## 🏗️ 6. Milestones (Hakemistokohtaiset etapit)

### Milestone 1: Backend Models & Utils
**Scope:** `backend_v2/models/`, `backend_v2/utils/`

- [ ] Aja `vulture` malleja vasten
- [ ] Grep: ReportDataDTO, ExecutionResult kentät vs. käyttöpaikat
- [ ] Tarkista Pydantic-mallien oletusarvot (5.1 säännöt)
- [ ] Tarkista `utils/`-apufunktioiden käyttö
- [ ] Dokumentoi eloonjääneet → `docs/reference.md`

### Milestone 2: Backend Services & LLM
**Scope:** `backend_v2/services/`, `backend_v2/llm/`, `backend_v2/engine/`

- [ ] Metsästä LangChain / vanhat Vertex API wrapper -jäänteet
- [ ] Grep: kaikki `.get(..., fallback)` palveluista → luokittele turvallinen/riskinen
- [ ] Analysoi Hookit: käyttämättömät hookit tai hookien kentät
- [ ] Tarkista BlueprintTransformer: orpojen kenttien etsintälogiikka
- [ ] Dokumentoi eloonjääneet → `docs/reference.md`

### Milestone 3: Backend Routers & Database
**Scope:** `backend_v2/routers/`, `backend_v2/database/`

- [ ] Analysoi API-endpointit: vanhat SDUI-polut
- [ ] Tarkista tietokantamallit vs. repositorymetodit
- [ ] Dokumentoi V3-rajapinnat → `docs/reference.md`

### Milestone 4: Frontend Core & UI
**Scope:** `client_app_v2/lib/`

- [ ] Aja `flutter analyze`
- [ ] Skannaa `.arb`-käännöstiedostot orvoista teksteistä (käyttämättömät avaimet)
- [ ] Poista SDUI-viittaukset, kovat matriisi-renderöijät
- [ ] Tarkista frontend DTO:t vs. backend DTO:t (kenttäpariteetti)
- [ ] Dokumentoi säilyvät views, controllers, providers → `docs/reference.md`

### Milestone 5: Loppusiivous & Synkronointi

- [ ] Ristiinvertailu: `reference.md` = 100% kartta elävästä koodista
- [ ] `pytest` + `flutter build` → koko järjestelmä nousee jaloilleen
- [ ] Git tag: `v3.0-clean`

---

## 📋 7. Kill List Template

Jokainen milestone tuottaa Kill Listin seuraavassa muodossa:

| # | Tiedosto/Kenttä | Tyyppi | 3-Way tulos | Päätös | Kommentti |
|---|----------------|--------|-------------|--------|----------|
| 1 | `v2_core.py:synthesis` | Orpo-kenttä | ✅✅✅ | KILL | Ei tuottajaa |
| 2 | `handler.py:tpm_limit=0` | Fallback | ✅✅✅ | KILL | Peitti 429-virheet |
| 3 | `provider.py:prompt_tokens=0` | Usage-laskuri | ✅❌❌ | KEEP | Semanttisesti oikea |
