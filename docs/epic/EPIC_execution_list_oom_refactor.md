# EPIC: Execution List OOM Prevention & Projection Refactor

## 1. Yhteenveto (Summary)
Palvelimen `ExecutionService.list_executions()` hakee tällä hetkellä kaikki tietokannan ajot (executions) kerralla palvelimen RAM-muistiin (`repo.get_all_executions()`) ja suodattaa ne vasta Python-listakomprehensiolla. Koska yksi ajo voi sisältää megatavukaupalla forensiikka-lokeja (prompts), Base64-tietoja ja Pydantic-tuloksia (`results`, `raw_inputs`), 500 ajon hakeminen kaataa koko FastAPI-palvelimen Out-Of-Memory (OOM) -virheeseen ja tukkii koko verkkokaistan.

## 2. Tavoitteet (Objectives)
- **Tietokantatason suodatus (Push-Down Filtering):** Siirtää `organization_id` ja `created_by` -suodatukset Pythonin RAM-muistista suoraan tietokantamoottoriin (Firestore / TinyDB).
- **Kevyt Projektio (Lightweight Projection):** Estää valtavien `results` ja `raw_inputs` -kenttien lataaminen ja sarjallistaminen silloin, kun API-rajapinta ja käyttöliittymä tarvitsevat vain listanäkymän (ID, status, aika).

## 3. Vaiheet (Execution Plan)

### Vaihe 1: DTO-Projektion Luonti (ExecutionSummary)
- **Toimenpide:** Luodaan `backend_v2/models/v2_core.py` -tiedostoon uusi kevyt Pydantic-malli `ExecutionSummary`, joka esittää ajon metatiedot, mutta jättää raskaat `results`, `raw_inputs` ja `frozen_context` -kentät pois.

### Vaihe 2: Repository-rajapinnan päivitys (Tietokantasuodatus)
- **Toimenpide:** Lisätään `AbstractWorkflowRepository` -luokkaan uusi metodi `get_executions_summary(...)`.
- **Toimenpide (Firestore):** Toteutetaan vähintään `where("organization_id", "==", org_id)` haku Firestore-tasolla. Tämän jälkeen datasta poistetaan raskaat avaimet ennen Python-objektien luontia.
- **Toimenpide (TinyDB/Local):** Toteutetaan `Query().organization_id == org_id` TinyDB:n `search()` -funktiolla suorien `.all()` -kutsujen korvikkeena.

### Vaihe 3: Service & API-kerroksen refaktorointi
- **Toimenpide:** Muutetaan `ExecutionService.list_executions()` kutsumaan uutta tietokantatason suodatusmetodia tehottoman "Hae Kaikki" -latauksen sijaan.
- **Toimenpide:** Päivitetään FastAPI:n reititin (`routers/execution/executions.py`) palauttamaan `list[ExecutionSummary]` aiemman `list[ExecutionRecord]` sijaan.

### Vaihe 4: QA & Regressiotestaus
- **Toimenpide:** Todennetaan HTTP-kutsulla, että listausrajapinta ei enää palauta megatavuluokan `results`-objekteja ja että rajapinnan vasteaika tippuu sekunneista millisekunteihin skaalautuen satoihin ajoihin.

---
*Noudattaa Quorumin V2 Enterprise Scalability -vaatimuksia.*
