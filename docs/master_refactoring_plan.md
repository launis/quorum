# Master Refactoring Plan (Execution Plan) - RAJATTU

**KRIITTINEN SÄÄNTÖ:** Tämä suunnitelma koskee **AINOASTAAN** alla mainitun kolmen yksilöidyn virhekohdan (Bugit & puutteet) korjaamista asiakkaan toimittamien lokien ja ruutukaappausten perusteella. **Kaikki tähän liittymättömät refaktoroinnit on kielletty.**

## Vianmääritys ja Korjausaskeleet

### 1. Report Transformer "Missing Data" Varoitukset
**Virheilmoitus:**
```
WARNING | backend.api.transformers.report_core | Missing data for step_judge in Score Cards layout
WARNING | backend.api.transformers.report_core | Missing data for step_xai in XAI Report layout
... ja muita vastaavia.
```
**Analyysi:** BFF-kerroksen `ReportTransformer` (joka muuntaa `WorkflowState` -datan tai `ReportContextin` UI-ystävälliseksi `ReportView` -malliksi) ei löydä odottamiaan agenttien tuloksia. Joko `reporting.py` -hook on epäonnistunut viemään/kääntämään JSONia `ReportContextiin`, tai Transformers-kerroksen reititys odottaa dataa väärillä avaimilla uudessa V2026-arkkitehtuurissa.
**Kohdetiedostot:**
- `backend/api/transformers/report_core.py` (ja sen alimuuntimet esim. `report_transformer.py`)
- `backend/hooks/reporting.py`
**Toimenpiteet:**
- Selvitä missä kohdin `step_judge`, `step_xai` jne. katoavat (ovatko ne `None` vai puuttuvatko tyystin `state.context_variables` -välityksessä).
- Korjaa muuntimen (Transformer) hakulogiikka.

### 2. Tyhjät (Null) Metadata-kentät Agenttien Raakadatassa
**Virheilmoitus / Havainto:** "Analyysin tulokset / Koko raakadata" -näkymässä agenttien metadatassa on tyhjiä (null) arvoja, vaikka niiden pitäisi saada kontekstista tiedot:
```json
"organization_id": null,
"user_id": null,
"execution_id": null,
"step_id": null,
"workflow": null
```
**Analyysi:** Kun `BaseAgent` tai muu taustaolio "edistää" (promote) rehellisen DTO:n periytyneeksi Domain Modeliksi (`ReasoningTrace` / `Metadata`), se kutsuu esim. `_apply_python_authority` tai vastaavaa funktiota. Jos `execution_context` ei sisällä yllä mainittuja avaimia ohjelman suorituksen (Workflow Engine / Worker) aikana, tai ne ylikirjoitetaan väärin, ne jäävät arvoon `null`.
**Kohdetiedostot:**
- `backend/models/domain/base.py` (`Metadata` ja `ReasoningTrace`)
- `backend/agents/base.py` (`_apply_python_authority` tai vastaava contextin lukija)
- `backend/core/engine.py` tai `worker.py` (varmistus että `user_id` ja `organization_id` ujutetaan agenttien `execution_context`:iin suorituksen alkaessa).
**Toimenpiteet:**
- Korjaa kontekstin (context) kokoaminen `GraphEngine`:ssä tai Workerissa niin, että root-tason metatiedot valuvat alaspäin.
- Riko `metadata` null-tilat `BaseAgentissa`. (myös mahdollisesti suomennosten korjaus `luontiaika` -> `created_at` jos se on kytkeytyneenä tähän samaan tietuemuotoon, mutta prioriteetti on ensin injektoida null-arvot piiloon).

### 3. Asetukset-näytön Käyttö (Usage) näkyy nollana ($0.00 / 0.0%)
**Virheilmoitus / Havainto:** "Nykyisen kuukauden käyttö" näyttää `$0.000` ja progress bar on "0.0%". 
**Analyysi:** Joko mallien käyttöä (Tokens / Cost) ei kirjata tietokantaan suorituksen jälkeen, tai Frontendin `/organizations/{id}/usage` API-reitti on rikki / lukee väärää kenttää, jolloin summa palautuu nollana. Vertex AI ja Gemini kutsujen kustannukset jäävät lokaamatta.
**Kohdetiedostot:**
- `backend/services/usage_service.py` (`log_usage` -kutsut)
- `backend/core/engine.py` (vastaako Engine laskutuksesta vai LLM Provider itse?)
- `backend/api/routes/organization_router.py` tai `settings_router.py` (kulutuksen hakeminen).
- `client_app/.../settings_screen.dart` tai BFF-malli (miten Flutter hakee ja näyttää summan).
**Toimenpiteet:**
- Testaa mihin kohtaan LLM Token -kirjanpito katkeaa. Etsi sille ratkaisu, joka rekisteröi "cost_estimate" tai "prompt_tokens" onnistuneen Executionin jälkeen `UsageRecordiin` kantaan.
- Varmista, että UI:n haku toimii oikein BFF/API:sta.
