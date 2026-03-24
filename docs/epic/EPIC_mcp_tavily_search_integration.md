# EPIC: The Tool Loop & Tavily AI Search Integraatio (V2.6)

**STATUS:** Draft / Planning Phase  
**TIER:** Tier 1 (Epic Planner)
**CONTEXT:** Quorum V3 Architecture (Python Backend V2 + Flutter Client V2)

## 📌 1. Tavoite (Objective)
Tavoitteena on irrottaa Quorum V2 LLM-riippuvaisesta "Mustasta Laatikosta" (hallusinaatioista) puhtaaseen asiantuntijajärjestelmän tilaan. Yksittäinen työnkulun askel (`StepRule`) voidaan varustaa **Serverless The Tool Loopilla**, joka ohjaa tekoälyn tekemään itsenäisen tiedonhaun internetistä The Tavily AI API:n yli, asettamaan The Evidencen työmuistiinsa (`ToolMessage`) ja pohjaamaan The BARS Matrix -arviointinsa pakottamalla tähän aineistoon.

Kaikki palautetut URL-lähteet ja raakatekstit tallennetaan The XAI Audit -lokina The `FrozenContext`-tietokantaan. Asiakkaan UI:ssa (Flutter) raportin lukijalle näytetään suora "Tekoälyn Asiantuntijalähteet (Evidence Box)" -laatikko faktojen luottamuksen takaajaksi.

---

## 🏗️ 2. Toteutuksen Etapit (Milestones / Koodaussuunnitelma)

### 🔹 Milestone 0: Totaalinen Siivous (Vanhan Hakulogiikan Purku)
V3 Zero-Compromise -arkkitehtuurin mukaisesti emme rakenna uutta ennen kuin vanha laho koodi on poltettu. Nykyinen koodikanta sisältää vahvasti kytkettyjä Vertex AI Search -jäänteitä, jotka rikkovat SRP-periaatteita (Single Responsibility Principle).
- [ ] Tuhoa säälimättä vanhat `vertex_search` Pydantic-mallit (`v2_core.py`), kuten `VertexSearchConfig`, `search_queries` ja `results_storage_path` -haamukentät.
- [ ] Etsi (`grep_search`) ja poista kaikki vanhan RAG-haun tai Vertex Grounding API:n Python-luokat (esim. kansioista `backend_v2/services/` tai `backend_v2/utils/`).
- [ ] Puhdista `backend_v2/seed/seed_data.json` poistamalla kaikista vanhoista työnkuluista `vertex_search_config` -lohkot nollaten kannan puhtaalle pöydälle.
- [ ] Poista vanha `search_web` tai vastaava kovakoodattu Hook-logiikka vanhasta The Executorista, jos sellaista on.

### 🔹 Milestone 1: Pydantic "The Spine" Update (`backend_v2/models/v2_core.py`)
Tietokannan skeemaan täytyy rakentaa turvallinen luottamusväli ulkopuolisille rajapinnoille ja the Audit lokille.
- [ ] Koodaa Pydantic DTO:t `SystemConfigMCPGateways`, `AllowedMCPTool` ja `MCPAuditTrace`.
- [ ] Lisää `allowed_mcp_tools` -listatuki `StepRule` -objektiin.
- [ ] Lisää `mcp_tool_audit` -listatuki `FrozenContext` -objektiin.
- [ ] Hydratoi (Seed) `backend_v2/seed/seed_data.json` Pydantic-turvallisesti: Lisää sinne `system` -organisaation alle Tavily API config ilman Backendin kaatumista.

### 🔹 Milestone 2: Tavily MCP Client (`backend_v2/services/mcp/`)
Valmistellaan puhdas HTTP Client Tavilyn APIn puhutteluun vähäisillä viiveillä (Serverless V2 -mukaisesti).
- [ ] Rekisteröi ilmainen Tavily AI API-Key ja laita se `.env` -tiedostoon.
- [ ] Koodaa `tavily_search_client.py`. (Funktio ottaa sisään hakusanan `query`, tekee POST-kutsun Tavilyyn, parsii nettiroskat V2.6 Pledgen mukaisesti pois, ja palauttaa puhtaan tekstiyhteenvedon ja URI-linkit).
- [ ] Testaa rajapintaa erillisellä pikkuskriptillä (lokaalisti).

### 🔹 Milestone 3: The Tool Loop Conductor (`dag_executor.py` & `mcp_tool_loop.py`)
Tämä on vaativin ohjelmointivaihe The Enginessä the SRP (Single Responsibility Principle) -sääntöjen mukaisesti.
- [ ] **Eristys:** Refaktoroi paisuva `dag_executor.execute_step` murtamalla LLM-silmukka (While LLM call) erilliseen tiedostoon `backend_v2/engine/mcp_tool_loop.py`.
- [ ] **Function Calling (Reititys):** Toteutetaan LLM-kutsu `tool_choice="auto"` (Langfuse/LiteLLM tuki function callingille). Jos askeleella on `allowed_mcp_tools`, LLM voi joko palauttaa Pydantic-matriisin TAI syöttää Tool Callin (hakusanan).
- [ ] **Ruiske (Injection):** Kun LLM tekee haun, backend ajaa M2:n `TavilyClientin`, hakee datan, luo `ToolMessage(content="fakta", role="tool")` ja heittää LLM:n uudestaan "Pakotuskierrokselle Matrixin täyttämiseksi".
- [ ] **Data Logging:** Tallenna tehty kysely, vastaukset ja URL-lähteet `MCPAuditTrace` objektina tietokantaan `record.results...frozen_context` alle.

### 🔹 Milestone 4: Admin Studio UI (Flutter / The Cascading State)
Ylläpitäjän on voitava kytkeä Haku päälle tekoälyn askeleeseen.
- [ ] Lisätään Node-editorin (DAG Builder / StepConfig) lomakkeeseen ominaisuus valita sallitut The Tools (Pudotusvalikko).
- [ ] Varmistetaan, että Flutterin koodigeneroidut Freezed-mallit osaavat purkaa backendiltä tulevat Pydantic-uutuudet (`AllowedMCPTool`).

### 🔹 Milestone 5: The End-User Evidence Viewer (Flutter / Flat MVC)
Raportin litteä DTO (Backend-For-Frontend) sisältää nyt Lokin yhtenäisellä RFC-pariteetilla.
- [ ] Luodaan uusi Widget `XAIEvidenceBox` Flutteriin.
- [ ] Jos palautetussa `ReportDataDTO.frozen_context.mcp_tool_audit` -listassa on tietoa, renderöidään laatikko UI:n loppuun. 
- [ ] Laatikko näyttää url-linkit (Clickable URIs) factcheckin todisteina.

---

## 🚨 3. Banned Patterns & Riskit
- **The Infinite Loop Limit:** Backend Tool Loop EI SAA ikinä jatkua ikuisesti. Asenna kovakoodattu limit (esim. max 3 hakua per askel), jotta Serverless Cloud Run (Timeout) ei kaadu.
- **The God Object:** Tuo 500-rivinen `dag_executor.py` on pirstottava. Älä lisää Hakulogiikkaa edellisen koodin joukkoon. Eristä se uuteen.
- **Tavily No-Spam:** Älä tee jatkuvia laajoja integrointitestejä livenä. Käytä Mock-palautteita (`unittest.mock`) backend-testeihin säästääksesi API-rahaa.
