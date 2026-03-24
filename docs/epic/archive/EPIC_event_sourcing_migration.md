# EPIC: DAG Engine Event Sourcing Migration

## 1. Yhteenveto (Summary)
Arkkitehtuurianalyysi paljastaa kriittisen kuilun suunnitelman ja toteutuksen välillä. Vaikka `models/state.py` esittelee edistyneen ja lukituksen kestävän lokipohjaisen tilanhallinnan (`TraceEvent` ja `WorkflowState`), itse työnkulkumoottori (`DAGExecutor`) toimii yhä legacy-mallilla eli mutatoituvalla Blackboardilla (`shared_state_data`). Tämä pakottaa ohjelman tekemään raskaita ja synkronisia `copy.deepcopy()` ja `deep_merge_dicts()` haaroituksia (`_execute_step` sisällä) varmistaakseen rinnakkaisuuden turvallisuuden, mikä syö prosessoritehoa ja jarruttaa koko ajoa.

## 2. Tavoitteet (Objectives)
- **Täydellinen Event Sourcing -siirtymä:** Korvata `DAGExecutorin` jättimäinen `shared_state_data` puhtaalla append-only (vain luku ja lisäys) tapahtumalokilla (`WorkflowState.execution_trace`).
- **O(1) Rinnakkaisuus:** Koska tapahtumalokiin muodostetaan vain uusia rivejä, deepcopy-operaatioita ei työnkuluissa enää tarvita lainkaan. Jokainen agentti (node) tuottaa suorituksestaan yhden `TraceEvent`:in irrallaan muista.

## 3. Vaiheet (Execution Plan)

### Vaihe 2: O(1) Tilan Lisäys (Event Append)
- **Toimenpide:** Poistetaan `copy.deepcopy()` rivi kokonaan. Rinnakkaisessa ajossa (`_execute_step`) agentti ja hookit saavat koko lokihistorian luettavakseen (read-only). Kun agentti on tehnyt työnsä, se palauttaa `TraceEvent` -objektin.
- **Rinnakkaisuuden Turvallisuus:** Koska FastAPI-moottori on asynkroninen, orkestraattori käyttää `state.add_event(trace_event)` -funktiota suojatusti `asyncio.Lock` -mekanismilla tai kerää asynkronisten ajojen palautukset puhtaana listana (esim. `asyncio.gather`) välttäen perinteiset kilpailutilanteet (race conditions).

### Vaihe 3: Prompt Compilerin "Fold" ja Yhdistäminen
- **Toimenpide:** Jotta seuraava askeleen XML-konteksti näkee edellisten tulokset, `PromptCompiler.build_xml_context` muokataan "foldaamaan" eli tiivistämään loki sanakirjaksi dynaamisesti (`event_type == 'output'`).
- **Suorituskyvyn Optimointi (Snapshotting):** Syvien DAG-verkkojen (kymmeniä tai satoja tapahtumia) suorituskyky turvataan "Snapshotting" / Memoization -mekanismilla ("delta-fold"). Tila muistaa edellisen fold-tuloksen ja laskee lennosta vain uudet tapahtumat täydellisen läpikäynnin sijaan.

### Vaihe 4: Virheenkäsittely ja Tilan Peruminen (Compensation)
- **Kuvaus:** Event Sourcing ei salli olemassa olevan tilan muuttamista taaksepäin, joten virhetilanteet tarvitsevat oikeaoppisen tapahtumamallin.
- **Toimenpide:** Epäonnistunut ajo kirjaa lokiin `ErrorTraceEvent` -tapahtuman. Työnkulkumoottori (`DAGExecutor`) reagoi tähän tapahtumaan keskeyttämällä heti epäonnistuneen haaran (Fail-Fast) ja ohittamalla riippuvaiset "downstream" -solmut.

### Vaihe 5: Hook-rajapintojen synkronointi (Teknisen Velan Hallinta)
- **Toimenpide:** Päivitetään legacy-hookit (`HookState.inputs`). Tilaan syötetään lennosta luotu tilan tiivistelmä (fold) dynaamisesti Event-historiasta adapterin avulla.
- **Linjaus:** Tämä adapteriratkaisu kirjataan eksplisiittisesti **väliaikaiseksi siirtymäkauden tekniseksi velaksi**. Tulevaisuudessa hookit päivitetään lukemaan suoraan puhdasta `WorkflowState` -tapahtumalokia asynkronisesti.

### Vaihe 6: Laadunvarmistus (QA), Yksikkö- ja Integraatiotestaus
- **Toimenpide:** Uuden `DAGExecutorin` on läpäistävä 100% samat yksikkö- ja integraatiotestit kuin varhaisemman mallin (Parity Check). Suoritettujen testiaikojen Output-JSON -rakenteen täytyy säilyä bittitasolla identtisenä aiempien Snapshot-testien kanssa.

### Vaihe 7: Suorituskyvyn Verifiointi (Benchmarking)
- **Toimenpide:** Tieteellinen todistus O(1) -tehostumisesta. Ajetaan vertaileva Benchmark-testi vanhan (`copy.deepcopy`) ja uuden (Append-Only) moottorin välillä esimerkiksi raskaalla 50 rinnakkaisen noden kuormitustestillä. Ero muistinkulutuksessa ja suoritusajassa dokumentoidaan.

## 4. Rollout-strategia
Koko orkestroinnin ytimen muutoksen vuoksi käyttöönotto ei tapahdu kerralla (Big Bang). Uusi DAG-moottori asennetaan tuotantoon **Feature Flagien** (esim. `USE_V2_EVENT_SOURCED_EXECUTOR = True`) taakse. Tämä mahdollistaa turvallisen A/B -testauksen ja nopean Rollbackin (palauttamisen) varamoottoriin, mikäli QA-tason tuolla puolen ilmenee odottamattomia sivuvaikutuksia.

---
*Tuhoaa lopullisesti kaikki State-mutability ongelmat ja mahdollistaa äärimmäisen rinnakkaisuuden tehostamisen (O(1)). Linjassa The Zero-Compromise Pledgen kanssa.*
