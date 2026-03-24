# EPIC: Execution List OOM Prevention & Projection Refactor

## 1. Yhteenveto (Summary)
Palvelimen `ExecutionService.list_executions()` hakee tällä hetkellä kaikki tietokannan ajot (executions) kerralla palvelimen RAM-muistiin (`repo.get_all_executions()`) ja suodattaa ne vasta Python-listakomprehensiolla. Koska yksi ajo voi sisältää megatavukaupalla forensiikka-lokeja (prompts), Base64-tietoja ja Pydantic-tuloksia (`results`, `raw_inputs`), 500 ajon hakeminen kaataa koko FastAPI-palvelimen Out-Of-Memory (OOM) -virheeseen ja tukkii koko verkkokaistan.

## 2. Tavoitteet (Objectives)
- **Tietokantatason Suodatus ja Sivutus (Push-Down & Pagination):** Siirtää `organization_id` ja `created_by` -suodatukset Pythonin RAM-muistista suoraan tietokantamoottoriin (Firestore / TinyDB) ja ottaa käyttöön API-tason sivutuksen (limit & offset).
- **Verkkokaistan säästö ja Kevyt Projektio (Egress & Projection):** Estää valtavien `results` ja `raw_inputs` -kenttien lataaminen. Hakuihin lisätään tietokantatason `select()` -projektio, jolloin Google Firestore ei palauta raskaiden kenttien gigatavuja lainkaan verkon yli.

## 3. Vaiheet (Execution Plan)

### Vaihe 1: DTO-Projektion Luonti (ExecutionSummary)
- **Toimenpide:** Luodaan `backend_v2/models/v2_core.py` -tiedostoon uusi kevyt Pydantic-malli `ExecutionSummary`, joka esittää ajon metatiedot, mutta jättää raskaat `results`, `raw_inputs` ja `frozen_context` -kentät pois.

### Vaihe 2: Repository-rajapinnan päivitys ja Indeksointi
- **Toimenpide (Abstraktio & Sivutus):** Lisätään `AbstractWorkflowRepository` -luokkaan metodi `get_executions_summary(..., limit: int = 50, offset: int = 0)`.
- **Toimenpide (Firestore.select & Sorting):** Toteutetaan `where("organization_id", "==", org_id)` yhdistettynä lajitteluun `order_by("created_at", DESC)`. Firestore-haussa on ehdottomasti käytettävä `select(...)` (Projection) -funktiota, joka hakee kannasta vain Summaryn tarvitsemat avaimet säästäen Database Egress -laskutusta.
- **Toimenpide (Indeksit):** Koska kyselyssä yhdistetään `organization_id` -suodatus ja `created_at` -lajittelu, Firestore vaatii komposiitti-indeksin (Composite Index). Päivitetään projektin `firestore.indexes.json` -tiedosto asettamaan tämä indeksi.

### Vaihe 3: Service & API-kerroksen refaktorointi
- **Toimenpide:** Muutetaan `ExecutionService.list_executions(...)` yhdistämään reitittimestä saatavat limit/offset-parametrit.
- **Toimenpide:** Päivitetään FastAPI:n reititin (`routers/execution/executions.py`) tukemaan kyselyparametreja (`?limit=50&offset=0`) ja palauttamaan pienennetyn `list[ExecutionSummary]` -mallin aiemman massiivisen mallin sijaan.

### Vaihe 4: Käyttöliittymän (Frontend/Client) päivitys ja Lazy Loading
- **Toimenpide:** Palvelimen muutosten vuoksi Client-sovelluksen listanäkymä (esim. Flutter) rikkoontuu, ellei sitä päivitetä. Listausnäkymän malli päivitetään vastaamaan uutta kevyttä DTO:ta.
- **Toimenpide:** Käyttöliittymään ohjelmoidaan "Lazy Loading" -käytäntö: Vasta kun käyttäjä klikkaa yksittäistä ajoa listasta, UI tekee erillisen tarkan `GET /executions/{id}` -kutsun noutaakseen raskaat `results`, `raw_inputs` ja `frozen_context` -tiedot raportin näyttämiseksi.

### Vaihe 5: Laadunvarmistus (QA), Yksikkötestaus ja Benchmarking
- **Yksikkötestaus:** Ohjelmoidaan testit uuden `ExecutionSummary`-DTO:n luomiselle sekä repository-tason `get_executions_summary(...)` -metodille varmistaen, että `.select()` tiputtaa datan oikein.
- **Load Testing:** Todennetaan korjaus ajamalla API-kutsu lokaaliin tietokantaan, johon on generoitu/siemennetty yli 10 000 raskasta ajoa (megatavu per ajo). Tarkkaillaan palvelimen muistinkulutusta. Varmistetaan ehdottomasti, ettei OOM-virhettä enää esiinny ja API selviää vasteajoista sadoissa millisekunneissa limitin avulla.

---
*Noudattaa Quorumin V2 Enterprise Scalability -vaatimuksia.*
