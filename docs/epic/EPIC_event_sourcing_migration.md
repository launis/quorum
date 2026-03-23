# EPIC: DAG Engine Event Sourcing Migration

## 1. Yhteenveto (Summary)
Arkkitehtuurianalyysi paljastaa kriittisen kuilun suunnitelman ja toteutuksen välillä. Vaikka `models/state.py` esittelee edistyneen ja lukituksen kestävän lokipohjaisen tilanhallinnan (`TraceEvent` ja `WorkflowState`), itse työnkulkumoottori (`DAGExecutor`) toimii yhä legacy-mallilla eli mutatoituvalla Blackboardilla (`shared_state_data`). Tämä pakottaa ohjelman tekemään raskaita ja synkronisia `copy.deepcopy()` ja `deep_merge_dicts()` haaroituksia (`_execute_step` sisällä) varmistaakseen rinnakkaisuuden turvallisuuden, mikä syö prosessoritehoa ja jarruttaa koko ajoa.

## 2. Tavoitteet (Objectives)
- **Täydellinen Event Sourcing -siirtymä:** Korvata `DAGExecutorin` jättimäinen `shared_state_data` puhtaalla append-only (vain luku ja lisäys) tapahtumalokilla (`WorkflowState.execution_trace`).
- **O(1) Rinnakkaisuus:** Koska tapahtumalokiin muodostetaan vain uusia rivejä, deepcopy-operaatioita ei työnkuluissa enää tarvita lainkaan. Jokainen agentti (node) tuottaa suorituksestaan yhden `TraceEvent`:in irrallaan muista.

## 3. Vaiheet (Execution Plan)

### Vaihe 1: DAGExecutor Signature päivitys
- **Toimenpide:** Poistetaan `shared_state_data: dict` argumentti funktioista `execute_workflow` ja `_execute_step`. Tilalle tuodaan natiivi `WorkflowState` -objekti, joka alustetaan ajon alussa vapaana listana.

### Vaihe 2: O(1) Tilan Lisäys (Event Append)
- **Toimenpide:** Poistetaan `copy.deepcopy()` rivi kokonaan. Rinnakkaisessa ajossa (`_execute_step`) agentti ja hookit saavat koko lokihistorian luettavakseen (read-only). Kun agentti on tehnyt työnsä, se palauttaa `TraceEvent` -objektin (sisältäen Pydantic JSON tuloksen ja Token-käytön `ReasoningTrace`:ssa).
- **Orkestraattori** käyttää `state.add_event(trace_event)` funktiota siististi thread-safe -periaatteella (esim. palautuksien koonti kerralla ajon jälkeen tai lock-suojatulla appendilla).

### Vaihe 3: Prompt Compilerin "Fold" (Tilan yhdistäminen)
- **Toimenpide:** Jotta seuraava askeleen XML-konteksti näkee edellisten tulokset tiettyjen avainten alta, `PromptCompiler.build_xml_context` -funktiota muokataan "foldaamaan" eli tiivistämään loki sanakirjaksi dynaamisesti (esim. ottamalla aina tuoreimman `event_type == 'output'` arvon `step_id`:n perusteella).

### Vaihe 4: Hook-rajapintojen synkronointi
- **Toimenpide:** Päivitetään olemassa olevat legacy-hookit (`HookState.inputs`). Hookin tilaan syötetään lennosta luotu tilan tiivistelmä dynaamisesti Event-historiasta, jolloin vanhoja ei tarvitse koodata täysin nollasta.

---
*Tuhoaa lopullisesti kaikki State-mutability ongelmat ja mahdollistaa äärimmäisen rinnakkaisuuden tehostamisen (O(1)).*
