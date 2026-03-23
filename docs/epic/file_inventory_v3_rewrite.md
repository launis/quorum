# V3 Core Engine "Big Bang" - Kohdetiedostojen Inventaario

Alla on täydellinen lista Quorum V2 -repositorion tiedostoista, jotka osallistuvat "Moottorin Sydämenleikkaukseen" (Event Sourcing & MCP Natiivi). Tiedostot on jaettu roolin ja toimenpiteen mukaan.

### 1. Moottorin Orkestrointi ja Ydin (Core Orchestration)
Näissä tiedostoissa tapahtuu suurin muutos, kun mutatoituva `shared_state_data` korvataan asynkronisella O(1) Event-listalla.
*   **[MODIFY]** `backend_v2/services/orchestrator/dag_executor.py` (Koko `_execute_step` ja silmukka kirjoitetaan uusiksi lukkiutumattomaksi)
*   **[MODIFY]** `backend_v2/services/orchestrator/prompt_compiler.py` (Uusi `delta-fold` -funktio kootaan dynaamisesti Event-historiasta)
*   **[REVIEW]** `backend_v2/services/orchestrator/dag_compiler.py` (Varmistetaan, että validointi ei estä uusia MCP-työkalukenttiä)

### 2. Tietomallit ja Abstraktiot (Models)
Näissä Pydantic-malleissa vaihdetaan vanha datan ylikirjoitusmalli uuteen "Append-Only" -historiatallennukseen.
*   **[MODIFY]** `backend_v2/models/v2_core.py` (`ExecutionRecord` poistaa massiivisen `results`-kentän ja ottaa käyttöön `execution_trace`. `Step` -objekti sallii abstraktit MCP-työkalulistat.)
*   **[MODIFY]** `backend_v2/models/state.py` (Lisätään `TraceEvent` ja `ErrorTraceEvent` -objektien lopulliset rakenteet fail-fast virheenkäsittelylle.)

### 3. LLM-Yhteys ja MCP Tool Loop (LLM Client)
Täällä vältetään LangChain ja koodataan suora silta Pydanticin tulosteiden ja ulkoisten MCP-palvelinten välille.
*   **[MODIFY]** `backend_v2/llm/client.py` (`run_structured_task` katkaisee asynkronisesti kellon heti kun huomaa LLM:n palauttaneen pyynnön MCP-työkalulle jättimäisen "tool_calls" vastauksen myötä. Token Bucket Rate Limiter rakennetaan myös suoraan tähän putkeen.)
*   **[REVIEW]** `backend_v2/llm/provider.py` (Varmistetaan, että abstrakti LLMFactory välittää sallitut MCP-työkalujen manifestit oikein mallille API-kutsussa).

### 4. Tietokanta ja Tilan Tallennus (Persistence)
Täällä lopetetaan `update_execution` -funktion jatkuva kutsuminen (mikä ylikirjoitti vanhaa) ja siirrytään vain taulukkolistojen lisäämisarkkitehtuuriin.
*   **[MODIFY]** `backend_v2/database/repository.py` (Lisätään Firestoren/TinyDB:n ArrayUnion -tyyppinen tapa puskea eventtejä lukkoja avaamatta tai dataa lukematta uuden askeleen valmistuttua.)
*   **[DELETE/MODIFY]** `backend_v2/services/progress.py` (`DatabaseProgressTracker` poistetaan lähes kokonaan ja sen logiikka ohjataan reitittymään puhtaiden Eventtien pohjalta.)

### 5. API-rajapinnat ja Striimaus (Routers)
Ajon tilan kysely ulkomaailmasta (Frontend).
*   **[MODIFY]** `backend_v2/routers/execution/executions.py` / `routers/execution/progress.py` (Ajon tilaa tai lopputulosta kyselevä rajapinta muutetaan palauttamaan kevyt ExecutionSummary, joka tarvittaessa lukee lennosta datansa Event-historiasta. Valmistellaan SSE-striimaukselle tulevaisuutta varten.)

### 6. Siemenkanta (Master Data)
Muutetaan vain sääntöjä siihen, kuinka Agentin ja ulkomaailman välinen lupa määritellään.
*   **[MODIFY]** `backend_v2/seed/seed_data.json` (Askeleiden `pre_hooks` / `post_hooks` / `hook` -rakenteista siivotaan pois kaikki vanhan ajan hakutoiminnot, koska jatkossa ulkomaailman ymmärrystä rajapintoihin hoitaa `"allowed_mcp_tools": ["..."]`.)

### 7. Täysin Poistettavat Tiedostot (Deprecated Legacy)
Nämä tiedostot heitetään Big Bangin aikana roskiin kokonaan teknisenä velkana:
*   **[DELETE]** `backend_v2/engine/hooks/search_hook.py` (tai mikä tahansa yksilöity Vertex SDK hakufunktio tallessa `core/hook_registry.py` -rekisterissä).
*   **[DELETE]** Kaikki mahdolliset `backend_v2/services/search/`-tyyppiset wrapperit tai Vertex/Custom Search Google API integraatiot, koska kaikki etsiminen ja RAG irrotetaan jatkossa täysin erilliseksi standardoiduksi MCP Gateway -mikropalveluksi Quorumin arkkitehtuurin ulkopuolelle.
