# Epic 43: Grand Unification - Structured State Envelopes & Data Sovereignty

## 1. Tausta ja Ongelma (The Dual "Loose Dictionary" Traps)

Olemme tunnistaneet Quorumin backend-arkkitehtuurissa kaksi kriittistä paikkaa, joissa olemme luottaneet "löyhiin sanakirjoihin" (loose dictionaries) ja suoraan datan siirtämiseen ilman asianmukaista välikerrosta (Projection Layer). Tämä rikkoo V2-arkkitehtuurin Fail-Fast -periaatteita ja johtaa jatkuvaan "laastarointiin".

### Ongelma A: The "String Manipulation" Trap (Sisäinen ajoaikainen data)
Quorumin V2-arkkitehtuuri tallentaa ajonaikaiset tulokset (Execution Trace) "Event Sourcing" -tyylillä. Kun orkestraattori tai PDF-koostaja (`blueprint.py`) tarvitsee näitä tuloksia, `StateProjector` litistää (flatten) rakenteen yksiulotteiseksi sanakirjaksi:
`"stp_123_blk_abc": { ...payload... }`
Tämä pakottaa downstream-palvelut arvailemaan pilkkomisilla (`split("_")` tai `endswith()`), mihin askeleeseen mikäkin lohko kuuluu, mikä on erittäin herkkä bugeille.

### Ongelma B: The "API Boundary Leakage" Trap (Julkinen API-data)
Backendin ydinmalleihin (`v2_core.py`) ja tietokantaan on tuotu uusia moniasiakkuuden eristyskenttiä, kuten `organization_id`. Koska Quorum käyttää tiukkaa `extra="forbid"` Pydantic-sääntöä, kaikki DTO-mallit (kuten `OutputProfileResponseDTO`) ja Flutter-rajapinnat kaatuvat heti (Validation Error), kun tietokanta tarjoilee niille tämän uuden sisäisen kentän löyhänä sanakirjana (`p_dict`). Nyt olemme korjanneet näitä yksittäin laastaroimalla `exclude=True` eri puolille koodia.

## 2. Tavoite (Objective)

Tavoitteena on saavuttaa täydellinen **Data Sovereignty** korvaamalla löyhät sanakirjat vahvasti tyypitetyillä Pydantic-kirjekuorilla (Envelopes) koko backendissä.

1. **Structured State Envelopes:** Poistetaan `StateProjector`:n merkkijonomanipulaatio ja siirrytään vahvasti tyypitettyyn `StepOutputDTO` -listaan.
2. **API Boundary Sovereignty:** Luodaan globaali API-suojakerros (`BaseResponseDTO`), joka suodattaa systemaattisesti kaikki backendin sisäiset turvakentät (kuten `organization_id`) pois ennen kuin ne päätyvät reitittimille tai Flutteriin asti.

## 3. Rajaukset ja Vaikutusalue (Impact Radius)

Tämä on puhtaasti **Backendin sisäinen refaktorointi**.
* **Tietokanta (0 %):** Event Sourcing -tietokantaan (`data/db_v2.json` / Firestore) ei kosketa. Data lepää levyllä ja sisältää `organization_id`:n entiseen tapaan.
* **Frontend (0 %):** Flutter UI pysyy ennallaan. Raporttien renderöinti on BFF-suojattu (`ReportLayoutDTO`). Tämän muutoksen myötä Flutter on täysin immuuni backendin tuleville tietokantamuutoksille.
* **Backend (100 %):** Vaikuttaa asynkronisiin työnkulkuihin, Blueprint-generointiin, DTO-malleihin ja API-reitittimiin.

## 4. Toteutuksen Vaiheet (Implementation Plan)

### Phase 1: API Boundary Sovereignty (DTO Base Layer)
* **`backend_v2/models/dtos/base.py` (UUSI):** Luodaan `BaseResponseDTO`, joka periytyy `V2CoreBase`:sta. Määritellään tänne `organization_id` ja muut tietokannan sisäiset kentät asetuksella `exclude=True`.
* **DTO-mallien päivitys:** Laitetaan `OutputProfileResponseDTO` (ja muut vastaavat API:lle näkyvät DTO:t) perimään tämä uusi `BaseResponseDTO`.
* **Reitittimien siivous:** Poistetaan reitittimistä (`steps.py`, `workflows.py`) väliaikaiset `response_model_exclude` -laastarit, sillä DTO-kerros hoitaa jatkossa suodatuksen arkkitehtuurin vaatimalla tavalla.

### Phase 2: Structured State Envelopes (Execution Layer)
* **DTO Määritelmä:** Luodaan vahva Pydantic-malli suorituksen tilaa varten:
```python
class StepOutputDTO(BaseModel):
    step_id: str
    block_id: str
    data_type: str
    payload: Any
```
* **StateProjector Refaktorointi:** Muokataan `backend_v2/services/orchestrator/state_projector.py` (`fold_trace()` metodi) palauttamaan `List[StepOutputDTO]` sanakirjan sijaan.

### Phase 3: Downstream Consumption Refactoring
* **ContextBuilder:** Muutetaan LLM:n kontekstin keräyslogiikka hyödyntämään uutta kirjekuorilistaa.
* **BlueprintTransformer:** Poistetaan lopullisesti `endswith()` ja `split()` hakkerointi matriisien hausta. Suodatetaan data suoraan `StepOutputDTO.block_id` -attribuutin perusteella.

### Phase 4: Yksikkötestien Korjaus ja Quality Loop
* Ajetaan täysi `backend_audit_loop.py --test` kohdetiedostoille.
* Korjataan hajonneet yksikkötestit (`test_blueprint.py`, `test_state_projector.py`, `test_context_builder.py`). Nykyiset mock-datat (`conftest.py`) syöttävät sanakirjoja; ne on muutettava listaformaattiin ja varustettava uusilla DTO-tyypeillä.

## 5. Työmäärä- ja Aika-arvio

* **Tekoälyagentin (Antigravity) nopeus:** 2 - 3 tuntia. Toteutetaan tiiviinä iteratiivisena execution-loopina. Suurin työ menee Phase 4:n massiivisessa yksikkötestien testidatan (mock payloads) refaktoroinnissa.
* **Ihmiskehittäjän (Agile Sprint) nopeus:** 1 - 2 työpäivää. Vaikka varsinaiset arkkitehtuuriluokat ja logiikka ovat suhteellisen kevyitä kirjoittaa, "Impact Radius" vanhoihin yksikkötesteihin on erittäin suuri, ja manuaalinen Pydantic-virheiden metsästäminen paikallisessa ympäristössä on hidasta.
