# EPIC: V3 Core Engine "Big Bang" Rewrite (Event Sourcing & MCP)

## 1. Yhteenveto (Summary)
Koska ohjelmistolla ei ole aktiivisia tuotanto-asiakkaita (ei taaksepäinyhteensopivuuden taakkaa), toteutamme täydellisen **"Big Bang" -refaktoroinnin**. Tämä Epic yhdistää asynkronisen Event Sourcing -arkkitehtuurin, natiivin MCP (Model Context Protocol) -integraation ja O(1)-tason työnkulkuorkestroinnin. Vanhat `shared_state_data` -rakenteet ja synkroniset tietokantamutaatiot hävitetään kokonaan.

### Korvatut ja Sisällytetyt Epicit:
Tämä radikaali uudistus korvaa ja yhdistää seuraavat aiemmat suunnitelmat:
1. **Korvaa: `EPIC_event_sourcing_migration.md`** -> "Nollasta rakentaminen" korvaa vanhat Adapteri- ja Siirtymäkauden teknisen velan vaiheet.
2. **Sisällyttää: `EPIC_mcp_integration_v2_6.md`** -> Työkaluloopit (`tool_choice`) rakennetaan suoraan uuden moottorin ytimeen, eikä irralliseksi purkaksi.
3. **Sisällyttää: `EPIC_llm_rate_limiter.md`** -> Kun `asyncio.gather` nostetaan puhtaana ydinloopiksi, Jitter-Backoff ja Token Bucket istuvat natiivisti samaan refaktorointiin.

## 2. Tavoitteet (Objectives)
- **Zero-State Mutation:** Mitään ajon tilaa (`results`, `inputs`) ei enää ylikirjoiteta Firestoreen / `repository.py` ajon aikana. Ajon tila on = Lista `TraceEvent` -objekteja.
- **Natiivi Python (Ei LangChainia):** Työnkulku rakennetaan täydellisellä hallinnalla suoraan `asyncio` ja Pydantic-kirjastojen varaan.
- **Maksimaalinen Suorituskyky O(1):** `copy.deepcopy()` hävitetään moottorista. 10 yhtäaikaista agenttia suoritetaan rinnakkain sekunnin murto-osissa.

## 3. Vaiheet (Big Bang Execution)

### Vaihe 1: DTO-arkkitehtuurin puhdistus (Pydantic Mutaatio)
*   **Toimenpide:** Päivitetään `backend_v2/models/state.py` ja `backend_v2/models/v2_core.py`. `WorkflowState` -mallin ainoaksi totuudeksi (`Source of Truth`) nostetaan `execution_trace: list[TraceEvent] = []`.
*   **Toimenpide:** Tuhotaan `HookState.inputs` mutaatio-oletukset. Luodaan `ErrorTraceEvent`, joka edustaa Fail-Fast virhekatkoksia.

### Vaihe 2: Keskusmoottorin Sydänkirurgia (`DAGExecutor`)
*   **Toimenpide:** Poistetaan `backend_v2/services/orchestrator/dag_executor.py` -tiedostosta kaikki `shared_state_data`. 
*   **Asynkroninen Loop:** Muutetaan `_execute_step` puhtaaksi funktioksi, joka saa sisäänsä "Delta-Fold" sanakirjan ja palauttaa pelkän Eventin: `async def _execute_step(step, folded_context) -> TraceEvent`. 
*   **Gather & Semaphore:** Orkestraattori komentaa solmut: `events = await asyncio.gather(*tasks)`, mutta kietoo rinnakkaisajon konfiguroitavaan `asyncio.Semaphore(MAX_CONCURRENCY)` -rajoittimeen. Näin vältetään massiiviset `429 Too Many Requests` API-virheet ja omat OOM-kaatumiset kymmenien agenttien ryntäyksessä.

### Vaihe 3: Delta-Fold ja Kontekstin Purku (`PromptCompiler`)
*   **Toimenpide:** Rakennetaan tyhjästä korkean performanssin funktio, joka osaa rullata Event-nauhan läpi (esim. `fold_trace(trace: list) -> dict`) ja palauttaa viimeisimmän tilan Pydantic-validointia ja XML-promptia varten. Tuetaan Snapshotting-varastointia jos loki kasvaa satoihin tapahtumiin.

### Vaihe 4: Tietokannan I/O-optimointi ja "The Flush Strategy" (`ExecutionCommitter`)
*   **Toimenpide:** Poistetaan ylikirjoittava `DatabaseProgressTracker` (`backend_v2/services/progress.py`).
*   **Puskuroitu tallennus (ArrayUnionin hylkääminen):** Koska `repository.py` hyödyntää `_offload_payloads` -mekanismia (joka siirtää yli 100KB taulukot Blob-storageen JSON-tiedostoiksi jättäen kantaan vain tekstiviitteen), emme voi käyttää Firestoren natiivia `ArrayUnion` -operaatiota yksittäisten TraceEvent-objektien striimaukseen ajon aikana.
*   **Uusi I/O-malli:** Moottori kerää ajon aikana syntyvät TraceEventit nopeaan asynkroniseen välimuistiin (In-Memory Buffer / StateProjector). Kun työnkulun looginen askel (Node) päättyy tai saavutetaan turvallinen tallennuspiste, uusi `ExecutionCommitter` -komponentti puskee koko kertyneen `execution_trace` -taulukon kerralla `repository.update_execution` -metodille (Checkpointing). Jos loki on kasvanut yli rajan, repositoryn interceptori ylikirjoittaa sen automaattisesti Blob-storageen yhtenä ehjänä tiedostona.

## 4. Rollout & Testausstrategia (The Deterministic Reducer)
Koska ohjelmistolla ei ole live-asiakkaita, koodinvaihto ajetaan tuotantoon **Dirty Cutover** -periaatteella (Big Bang). 
Koska kyseessä on Event Sourcing, QA siirtyy manuaalisesta testauksesta vahvasti **yksikkötestauksen** puolelle:
- **Reducereiden 100% determinismi:** `fold_trace(trace: list)` ottaa sisään vain asioita ja sylkee vain asioita ulos. Sen logiikka testataan puhtailla asynkronittomilla testeillä triviaalisti.
- **Rehydration QA:** Lokaalin testauksen rinnalla rakennetaan kokoelma puhtaita "korruptoituneita" JSON/puskuri -vedoksia (katkenneita ajoja), joilla testataan `DAGOrchestratorin` jatkamiskyvyn eheyttä.

## 5. Vaikutukset Koodiin (Mitä ja Miksi muutetaan)

**1. `backend_v2/services/orchestrator/dag_executor.py` (Tuhoava muutos)**
*   **Mitä:** Koko tiedoston suoritusmalli kirjoitetaan uusiksi. `copy.deepcopy(shared_state_data)` (Rivi 286) hävitetään kokonaan. Ajon tilapäivitykset (esim. `repository.update_execution` joka ylikirjoitteli `results` -sanakirjaa) muutetaan puhtaiksi Event-append -kutsuiksi. LLM-kutsulooppiin lisätään asynkroninen keskeytys MCP-työkalukutsuja varten.
*   **Miksi:** Tilan mutatoiminen esti puhtaan O(1) rinnakkaisuuden ja vikasietoisuuden. Uusi `asyncio.gather` mahdollistaa satojen agenttien samanaikaisen ajamisen ilman lukituksia.

**2. `backend_v2/models/v2_core.py`**
*   **Mitä:** `ExecutionRecord` menettää/deprecatoi massiivisen `results: dict` tietorakenteensa. Tilalle tulee `execution_trace: list[TraceEvent]`. `Step` -objekti (TaskBlueprint) saa uuden kentän: `allowed_mcp_tools: list[str] = []`.
*   **Miksi:** Vanhat sanakirjat tallensivat vain lopputuloksen yliajaen vanhan datan. Uusi trace-lista on "Append-Only", jolloin ajon voi jatkaa katkoksen jälkeen katkeamattomasti logista.

**3. `backend_v2/llm/client.py` (The Native Tool Loop)**
*   **Mitä:** `run_structured_task` päivitetään tunnistamaan MCP Serverin manifesti. Kun Pydantic-validointi näkee vastauksessa `tool_calls` -pyynnön, generaatio pysäytetään, soitetaan HTTP-kutsu MCP-serverille, lisätään vastauksen raakateksti `messages` arrayn loppuun ja jatketaan LLM-kelloa.
*   **Miksi:** LangChain-vapaa integrointi. Näin Quorum toimii natiivina siltana kielimallin työmuistin ja minkä tahansa maailman RAG- tai MCP-palvelimen välillä.

**4. `backend_v2/services/progress.py` & `backend_v2/database/repository.py` (Kooditason Vahvistus)**
*   **Mitä:** `DatabaseProgressTracker` -luokan jatkuvat mikropäivitykset poistetaan kokonaan. Tilalle nousee `ExecutionCommitter`, joka flushaa `execution_trace` -taulukon sellaisenaan kerralla. **Kooditason löydös:** Nykyinen `UnifiedWorkflowRepository` ja sen `_offload_payloads()` -metodi (rivi 435) tukevat uutta Checkpointing-mallia jo 100% natiivisti! Se tarkkailee jo nyt `execution_trace` sanakirja-avainta, lukee sen JSON-kokoa (100KB soft limit) ja offloadaa sen automaattisesti Blob-storageen (`execution_trace_storage_path`) heti rajan ylittyessä. `backend_v2/database/repository.py` -tiedostoa ei erikseen tarvitse edes muokata tältä osin, riittää että `ExecutionCommitter` syöttää sille askeleen päätteeksi kokonaisen päivitetyin taulukon.
*   **Miksi:** ArrayUnion pudotetaan, sillä nykyinen repository-arkkitehtuuri on jo täysin valmis tallentamaan saumattomasti massiivisiakin Trace-lokeja muistipuskurista.

**5. Observabiliteetti ja Korrelaatiotunnisteet (Asynkroninen Spagetti)**
*   **Mitä:** Kaikki `TraceEvent` -objektit ja `NodeExecutorin` kirjaamat `logger` viestit pakotetaan sisältämään `execution_id`:n lisäksi askeleelle täysin uniikki `step_id` tai `correlation_id`.
*   **Miksi:** Puhtaassa asynkronisessa 10-Agentin työnkulussa perinteinen `stdout` loki muuttuu sekunneissa lukukelvottomaksi spagetiksi. Vianetsintä vaatii vahvan ID:n, jolla yksittäisen Node-säikeen kohtalo erotetaan taustamelusta.

## 6. Frontend-integraation vaatimukset (BFF & Signal-Fetch)

Jotta V3 Core Engine -koodaaja tai -tekoäly ei vahingossa tuhoa The Zero-Compromise Pledgen mukaista mobiilisovelluksen suorituskykyä, seuraavat asiat ovat ehdottomia moottoritason pakotteita:

**A) Zero-Math UI (BFF-Lukumallin taittaminen):**
Frontend ei koskaan lue tai vastaanota raakoja `TraceEvent` -taulukoita. Backendin on tarjottava laiskalle mobiilisovellukselle valmiiksi pureskeltu litteä Lukumalli (esim. `/render` -BFF reitin kautta) `fold_trace()` avulla taitettuna. `TraceEvent` on vain Backendin sisäinen salaisuus.

**B) The Payload Trap vs. Live UI (Deltas & Signal-Fetch):**
Vaikka moottorin `ExecutionCommitter` puskee massiivisia Trace-lokeja Blob-storageen, **SSE-striimiputkeen ei koskaan työnnetä valtavia sanakirjoja**. Ristiriita Live-UI:n ja PING-Fetchin välillä ratkaistaan seuraavasti: SSE välittää tasaisesti **ohuet Delta-päivitykset (esim. askeleen statuksen uusi tila tai streamattu tekstin pala)**, jotta "Live UI" voi piirtyä saumattomasti ilman Frontendin jatkuvaa HTTP GET -spämmiä. Kuitenkin itse raskas historiallinen Lukumalli noudetaan puhelimelle täydellä HTTP GET -kutsulla ("Fetch") vasta askeleiden päättyessä tai käyttäjän pyytäessä.

**C) Human-in-the-Loop Rehydration (Valinnainen):**
Rehydration-mekanismi palvelee Frontendin optimoituja jatkamis-mutaatioita. FAILED-kaatumisten ohella moottorin tilakone tukee valinnaista **`SUSPENDED_FOR_INPUT`** (HITL) -tilaa, jolloin ajo sallii ulkoisen syötteen lisäämisen (esim. käyttäjän vahvistus) ennen moottorin jatkamista. Tämä HITL-ominaisuus lasketaan mukaan Rehydration-polkuun, mutta on työnkuluissa oletuksena aina off-tilassa.

## 7. Vaikutukset Siemenstietokantaan (seed_data.json)

Itse Workflown ja Steps / Prompt Blocks -määrittelyiden tekstit ja säännöt **ovat täysin turvassa**, mutta niiden liitännät abstrahoidaan:

*   **Vanha Legacy Hook poistuu:** Jos `seed_data.json`-tiedostossa ("steps"-puussa) oli esim. `"hook": "search_hook"`, se otetaan pois.
*   **Uusi MCP Kytkentä:** Tilalle asetetaan suoraan työkaluoikeus, esim. `"allowed_mcp_tools": ["mcp_tavily_search"]`.
*   **Miksi:** Siemenkanta pysyy täysin riippumattomana python-koodiston hookeista. Backend hoitaa loput ilman ylimääräistä ohjelmointia.

## 8. Korvattavat ja Poistettavat Ohjelmat / Epicit

Koska "Sydämenleikkaus" rakennetaan uuden V3 Event Sourcingin varaan, ohjelmistosta voidaan huoletta **poistaa satoja rivejä** koodia ja hylätä vanhat suunnitelmat:

**Täysin Romukoppaan (Deprecated):**
1.  **`backend_v2/hooks/search.py` (sekä `search_client.py`)**: Aiemmat Vertex Search -kovakoodatut hookit heitetään täysin roskiin, koska korvike on erillinen MCP Gateway.
2.  **`EPIC_vertex_search_reintegration.md`**: Legacy "Post-Hook" -hakuideologia. Ei relevantti modernissa Tool Loopissa.
3.  **Tekninen Velka (Adapterit):** Kaikki välivaiheet ohitetaan.

**Integroidaan ja Korvataan Yhteen:**
1.  **`EPIC_mcp_integration_v2_6.md`**: Askeleet ohjelmoidaan suoraan `client.py` -tiedostoon.
2.  **`EPIC_llm_rate_limiter.md`**: Rajoitin ujutetaan suoraan asynkronisen LLM-loopin ytimeen `client.py` -tiedostossa samalla kertaa.
3.  **`EPIC_event_sourcing_migration.md`**: Vanha siirtymäkauden varovainen adapterisuunnitelma korvautuu tällä suoraan koodattavalla Big Bang -refaktoroinnilla.

---
*Nolla-asiakaan etu käytetty maksimaalisesti arkkitehtuurijäänteiden siivoamiseen The Zero-Compromise Pledgen hengessä.*

## 9. Kriittiset Arkkitehtuurilinjaukset (JSON-analyysin korjaukset)

**1. I/O-Hookit vs. Data Transformation -Hookit:**
Kaikkia "Legacy Hookeja" ei suinkaan poisteta. On tehtävä tiukka rajanveto tietorakenteen totuuden mukaan:
*   **I/O Hookit poistuvat:** `execute_google_search` ja vastaavat korvataan MCP Tool Loopilla, jotta LLM hakee datan suoraan gatewaylta.
*   **Data Transformation säilyy natiivina:** Funktiot kuten `normalize_matrix_scores`, `sanitize_text` tai `calculate_text_metrics` **SÄILYTETÄÄN** moottorissa natiiveina Python-funktioina (Event Reducers).
*   **Kriittinen lisäys (Main Event Loop Tukos):** Koska nämä funktiot voivat olla raskaita synkronisia operaatioita (esim. matriisilaskenta), ne on **EHDOTTOMASTI Eristettävä `asyncio.to_thread()` tai `run_in_executor` taustasäikeisiin**. Jos raskas synkroninen funktio ajetaan suoraan Event Loopissa, se tukkii koko säikeen ja pysäyttää muiden kymmenien agenttien rinnakkaisen `asyncio.gather` -suorituksen "kuolemanlaaksoon".

**2. Natiivit Logic-solmut (Ei-LLM -askeleet):**
Askeleet, joiden tyyppi on `"type": "logic"` (kuten `step_scoreengine1`), jatkavat toimintaansa osana Event Sourcing -putkea ilman Kielimallia. Ne toimivat Reducer-pohjaisesti: lukevat snapshotin taitetusta tilasta (`fold_trace`), suorittavat matemaattisen Python-hookinsa (esim. `apply_scoring_logic`) ja emittoivat lopputuloksen yhden tai useamman `TraceEvent` -objektin muodossa suoraan lokiin.

**3. Grounding-ristiriidan ratkaisu (Vertex vs MCP):**
Moottori ei tue kahta päällekkäistä verkkohakua samanaikaisesti. Epic linjaa: Kun uusi MCP Search Gateway otetaan käyttöön myöhemmin, vanha natiivi Vertex Grounding kytketään pois päältä. Siihen asti V3-moottori tukee `supports_grounding: true` asetusta siemenkannasta siirtymäkauden ajan.

**4. O(N) Suorituskykyriskin ratkaisu (Snapshotting ja Karsinta):**
Event Sourcing -tilan taitto (`fold_trace`) pelkistettynä on kriittinen riski kasvaen auttamattomasti $O(N)$ -aikaan pitkissä askeleissa. Uuteen moottoriin rakennetaan vahva **In-Memory Snapshotting** välimuisti. `StateProjector` ei lue lokia tyhjästä joka kerta. Rehydration-kylmäkäynnistyksien CPU-tuhon estämiseksi `ExecutionCommitter` tallentaa säännöllisesti (esim. 50 askeleen välein) **Hard Snapshotteja** (valmiiksi taitettuja tilakuvia) Blob-storageen varsinaisen ohuen lokin ohella, palauttaen eheyden hakunopeudeksi jälleen O(1). Lisäksi pitkien RAG-työnkulkujen LLM-konteksti-ikkunan räjähtämisen estämiseksi `fold_trace()` vastaa vanhojen TraceEvent-objektien aggressiivisesta tiivistämisestä (Pruning) askeleen vaihtuessa, pitäen syötteen aina sallituissa LLM Token -rajoissa.

**5. Sudenkuopat ja Resilienssi (Pilvikaatumisista toipuminen)**
Uuden moottorin elinehto on kyky toipua kaatumisista ilman, että kalliita LLM-kutsuja toistetaan.
* **RFC 7807 Virheenhallinta ja Dual-Reporting (Sääntö 6 -Mandaatti):** V3-moottori ei saa kaataa API-rajapintoja tai asynkronisia looppeja raaoilla `ValueError` tai `HTTPException` nostoilla. NodeExecutor ottaa kiinni lokaalit virheet (Dual-Reporting: ensin `logger.error` kera stack tracen backend-lokiin), jonka jälkeen se paketoi ne tiukkaan RFC 7807 -yhteensopivaan `AppException`-formaattiin (`error_code`, `status`, `message`). Tätä ei kuitenkaan nosteta poikkeuksena ilmaan, vaan moottori **emittoi sen puhtaana `ErrorTraceEvent` -objektina** suoraan tapahtumalokiin. Askeleen tila lukitaan deterministisesti `FAILED` (tai `SUSPENDED_FOR_INPUT`) ja rinnakkaisuus jatkuu muissa solmuissa.
* **Schema Evolution (Versiointi):** `TraceEvent` -objekteihin lisätään heti alussa `v: 1` kenttä. Tulevaisuudessa, kun tietorakenne muuttuu, `fold_trace()` kykenee konvertoimaan (upcastaamaan) vanhat eventit lennosta.
* **Buffered Committer ja Muistin OOM-Turvaventtiili:** Aina kun askeleen tila "commitoidaan" puskurista kantaan massiivisena tiedostona suojellen I/O-viiveitä, askeleen logiikka hoitaa sen "Logical Flushina". Mutta tuen takia committeriin rakennetaan The Size-based Eviction -turvaventtiili: jos In-Memory -puskurin koko ylittää esim. 5MB askeleen kesken (esim LLM lukee RAG-dataa), se tuupataan väkisin levylle OOM (Out-of-Memory) podi-kaatumisten estämiseksi "kesken askeleen".
* **Kisaustilat ja Eventual Consistency (Versionumero):** Olemme luomassa hajautettua pilveä. Jokaiseen ajoon leivotaan `trace_version` -numero (Optimistic Concurrency Control). Kun SSE huutaa Frontendille `{"event": "STEP_DONE", "version_ready": 42}`, ja Frontend pyytää APIlta tuoretta litteää tilaa `GET /render?min_version=42`. Jos BFF katsoo Blob Storagea (jonka Storage/CDN -replikointi on yhä pilvessä Eventual Consistencyssa sekunnin murto-osan jäljessä tunkkaisessa versiossa 41), se ei palauta epäsynkronoivaa virheellistä tilaa, vaan tekee automaattisen Long Polling -odotuksen kunnes uusi pilvitiedosto ilmestyy, ratkaisten ns. Stale Data kisaustilan täydellisesti!
* **Exceptions taustasäikeissä (Jäätymisen esto):** Raskaat `asyncio.to_thread()` taustasäikeet synkronisille Hook-Reducereille varustetaan kovalla vuotamattomalla exception-handlerilla, joka takaa asynkronisen Event Loopin eheyden muuntamalla nolliinjakamiset yms taustalla siisteiksi `ErrorTraceEvent` -merkinnöiksi, estäen taustasäikeen hiljaisen "kuolemanlaakson" ja moottorin deadlock-jäätymiset.
* **Sivuvaikutusten Idempotenssi ja "Safe/Unsafe" -työkalut:** Rehydrationissa piilee jättimäinen tuplasuoritusten (Two-Generals Problem) riski. Siksi se ratkaistaan kolmitasoisesti: (1) Askeleet kovatakoodataan `seed_data.json` asetuksiin `"safety": "safe"` (Read-only MCP) tai `"safety": "unsafe"` (Sähköpostit ja API-POST kutsut). (2) Unsafe-työkalujen laukaisuille on pakko leipoa oma `Idempotency Key` estämään ulkoiset tuplaukset. (3) Jos ajo kuolee epämääräisen Unsafe-työkalun suoritukseen, automaattinen Rehydration estetään kokonaan tuplavahingon minimoimiseksi. Sen sijaan ajo asetetaan tilaan **`SUSPENDED_FOR_INPUT` (HITL)** ja sen purkaminen palautetaan aina takaisin ihmisen vastuulle.
* **GDPR ja Append-Only (Tombstonet):** `TraceEvent` -lokien muuttumattomuus kohtaa lain vaatiman PII-datan poisto-oikeuden ristiriidan. Tämä arkkitehtuuri ratkaisee sen **Tombstone-eventeillä** tai rankalla Redaction-filtterillä: poistopyynnön jälkeen historiallinen PII-laatikko vain korvataan kryptografisella hajautusarvolla O(1) eheyttä tuhoamatta.
* **Ikuisten Luuppien Esto (Infinite Tool Execution):** LLM ei saa jäädä yksin jauhamaan MCP-työkalua virheellisillä parametreilla loputtomasti. Askeleelle asetetaan kova `MAX_TOOL_ITERATIONS` -katto (esim. 5), jonka jälkeen tapahtuu armoton Fail-Fast ja `ErrorTraceEvent`.
* **Rehydration (Tilan jatkaminen):** Kun DAG kaatuu API-virheeseen (Fail-Fast), uuden ajon alussa `DAGOrchestrator` ottaa paramterina sisään vanhan ajon ID:n, rullaa `fold_trace()` -funktiolla tilan takaisin juuri siihen pisteeseen, missä kaatuminen tapahtui, ja jatkaa suoritusta turvallisesti (huomioiden ylläolevat Unsafe-linjaukset).

## 10. Tuhoava Päivitys ja Laadunvarmistus (QA)

**Tietokannan Tyhjennys (Database Wipe):**
Tämä on Big Bang -tason tuhoava päivitys tiedostorakenteeseen. Kun V3-moottori otetaan käyttöön, vanha `results`-sanakirjoihin perustuva tietokantamuoto tuhoutuu Frontendin lukukelvottomaksi. Järjestelmäarkkitehtuuri linjaa, että **kaikki vanhat ajot (Executions) tuhotaan Firestoresta ja TinyDB:stä kokonaisuudessaan siirtymän yhteydessä**. Legacy-dataa ei yritetä säästää, vaan vanha rakenne pyyhitään tyhjäksi.

**Backendin QA ja Testausstrategia:**
1. **O(1) Concurrency Test (Rinnakkaisuus):** Yksikkötesti koordinaattorille. Ajetaan 10 rinnakkaista tyhmää feikkisolmua (joissa on jokaisessa 1 sekunnin sleep). Koska lukkoja ei enää ole, testin kokonaiskesto mitataan ja sen on oltava noin tasan 1.1 sekuntia (eikä 10 sekuntia perätysten, kuten vanhassa synkronisessa moottorissa).
2. **Delta-Fold Test (Reducerin Puhtaus):** Luodaan 100 manuaalista `TraceEvent` -objektia listaan. Ajetaan uusi `fold_trace()` läpi rakentaen pelkästään muistissa Pydantic-tilan (esim. Prompteja/kontekstia varten) ja varmistetaan Assert-lauseilla, että sanakirja litistyy lennosta oikeansisältöiseksi rikkoutumatta (ilman objektimutaatiota tai logaritmista hitautta).
3. **Rehydration Recovery Test ("Kaadu ja Herää"):** Tahallinen virhesimulaatio. Luodaan skenaario, jossa askeleen suoritus pakotetaan kaatumaan (esim. nostamalla tahallinen `TimeoutError` tai syöttämällä täysin invalidi JSON Pydanticiin). Varmistetaan ensin, että moottori kuolee hallitusti Fail-Fast säännön mukaan tuottaen puhtaan `ErrorTraceEvent` -lokimerkinnän. Välittömästi tämän jälkeen testi kutsuu rehydration-pohjaista `resume` -tilaa samalle ajolle. Testi on läpi vain, kun vanha ohjelmisto herää kuolleista täysin puhtaana, palauttaa taitetun tilan ja vie askeleen lopulta onnistuneesti maaliin tuplaamatta aiemmin onnistuneita kutsuja.
4. **Manuaalinen QA (backend_debug.log):** Manuaalinen testi Quorumin Admin Studiosta lokaalisti, kytkien siemenkantaan "Natiivi AI" ohitukselle. Seurataan konsolia ja `backend_debug.log` -tiedostoa livenä sen varmistamiseksi, että lokaaliin kantaan syntyy puhdas Event-nauha ilman minkäänlaista "results"-avaimen ylikirjoitettua sekasotkua.

## 11. Priorisoitu Toteutustiekartta (Action Roadmap P1-P5)

Tämä tiekartta ohjaa varsinaista koodaustyötä:

**P1: Event Sourcing -tilan ytimen rakentaminen (The State Reducer)**
*   Eristetään `models/state.py` (TraceEvent, WorkflowState) arkkitehtuurin ainoaksi totuudenlähteeksi (SSOT).
*   Toteutetaan erillinen `StateProjector` ja `fold_trace()` -logiikka In-Memory Snapshot -välimuistilla.

**P2: Pura "God Object" (DAGExecutor) SRP:n mukaiseksi**
Halkaistaan `dag_executor.py` kolmeen erilliseen, injektoitavaan vastuualueeseen:
*   `DAGOrchestrator`: Vastaa vain graafin etenemisestä ja rajoittaa rinnakkaisuutta `asyncio.Semaphore` avulla (välttää 429 & OOM).
*   `NodeExecutor`: Hakee foldatun tilan, ajaa LLMClientin (Tool Loopilla) tai synkronisen Logic-Noden, ja emittoi `TraceEventtejä`.
*   `ExecutionCommitter` (I/O-Sydän): Vastaa tilan turvallisesta tallentamisesta (Checkpointing). Lukee kootun In-Memory `execution_trace` -puskurin askeleen päätyttyä ja lähettää koko taulukon kerralla `repository.update_execution` -metodille. Tämä mahdollistaa saumattoman yhteentoimivuuden `_offload_payloads` -Blob-tallennuksen kanssa ja poistaa hitaat tietokannan I/O-lukot täysin moottorin kognitiiviselta kriittiseltä polulta.

**P3: Tapa copy.deepcopy() lopullisesti**
Kun P1 ja P2 ovat valmiit, `copy.deepcopy()` poistuu moottorista kokonaan. Tämä vapauttaa Pythonin GIL-lukon prosessoinnin ajaksi.

**P4: Optimoi dynaaminen skeemagenerointi (Memory Safety)**
Lisätään `PromptCompiler.build_dynamic_schema` -metodiin `@lru_cache` (hashaamalla sisääntulevat kriteerit). Tämä estää dynaamisten luokkien rajattoman luonnin tuotannossa ja estää muistivuodon.

**P5: Rajoita "Self-Healing" -silmukan laajuutta (`client.py`)**
Asynkroninen retry-luuppi muutetaan älykkäämmäksi: Jos LLM hallusinoi täysin väärän rakenteen, tapahtuu **Fail-Fast**. Self-Healing jätetään vain ilmeisten JSON-syntaksivirheiden korjaamiseen. Lisäksi MCP-työkalujen kutsumiselle asetetaan absoluuttinen absoluuttinen yläraja (`MAX_TOOL_ITERATIONS`), jottei malli jumiudu kutsumaan työkalua yhä uudelleen väärillä parametreilla ilman, että ohjelma ymmärtää kaatua The Zero-Compromise Pledgen mukaisesti.
