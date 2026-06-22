# 04: Palvelukerros ja DAG-moottori (Business Services)

Cognitive Quorumin `backend_v2/services/` -hakemisto sisältää järjestelmän ydinälyn. Kaikki liiketoimintalogiikat, työnkulkujen (DAG) suoritus ja "Backend-For-Frontend" (BFF) -raporttigenerointi suoritetaan tässä kerroksessa turvallisesti eristettynä HTTP-rajapinnoista (Routers).

## Execution Service (Orkestraation portinvartija)

`execution.py` (`ExecutionService`) toimii järjestelmän primäärinä portinvartijana työnkulkujen (DAG) käynnistämiselle ja jatkamiselle (`start_execution`, `resume_execution`). Palvelu ohjaa laajasti asynkronista suoritusta ja tulosten hallintaa:
* **Ingress ja Validointi:** Suorittaa raskaat "Fail-Fast" Pydantic-validoinnit työnkulun ingress-vaiheessa ja generoi dynaamiset käyttöliittymän vihjeet (SDUI) vastaustilan hallintaan.
* **Asynkroninen Raportointi (Epic 14):** Tukee asynkronista raportointia (`render_execution` -> `render_profile_job` Arq jonoon). Tämä ehkäisee käyttöliittymän "infinite loop" -kyselyitä luomalla deterministisen työtunnisteen jota käyttöliittymä voi pollausturvallisesti kuunnella.
* **Force Re-render:** Tarjoaa `clear_profile_synthesis` -funktion, jolla käyttäjä voi pakottaa yksittäisen output profiilin (and siihen kytketyn PDF:n) tuhoamisen ja uudelleengeneroinnin tietokannasta.
* **Tenant Isolation:** Rajaa tiedon tiukan "Tenant Isolation" -periaatteen mukaisesti. Rajoite on vahvistettu kaikissa perustoiminnoissa (`list_executions`, `get_execution`, `delete_execution`), estäen ristiinlukemisen.
* **FinOps:** Valvoo puitebudjettia "Circuit Breaker" -rajoitteilla yhteistyössä `usage_service.py`:n kanssa suojellakseen osakkaiden kukkaroita karkaavalta AI-kulutukselta.

## Pyynnön Elinkaari ja Kognitiivinen Kuorma (Call Stack)

Yhden LLM-pyynnön matka HTTP-rajapinnasta varsinaiseen kielimalliin on jaettu useaan tiukkaan vastuualueeseen (Single Responsibility). Tämä eristys on teknisesti välttämätön skaalautuvuuden, tietoturvan ja virheiden hallinnan vuoksi, mutta se tekee koodin seuraamisesta aluksi hidasta.

Alla oleva sekvenssikaavio havainnollistaa täydellisen kutsuketjun (`Call Stack`), jotta koodikannassa navigoiminen helpottuisi:

```mermaid
sequenceDiagram
    autonumber
    participant API as API Router (executions.py)
    participant Exec as ExecutionService
    participant DAG as DAGExecutor
    participant Node as NodeExecutor
    participant Strat as LLMNodeStrategy
    participant LLM as LiteLLMProvider
    
    API->>Exec: start_execution(Payload)
    Note over Exec: Pydantic Fail-Fast<br/>Tenant Isolation
    Exec->>DAG: execute(WorkflowState)
    Note over DAG: Topologinen puu<br/>TaskGroup (Rinnakkaisuus)
    DAG->>Node: run_node(Step)
    Note over Node: FinOps Circuit Breaker<br/>Semaphore (Rate Limits)
    Node->>Strat: execute_strategy(HookState)
    Note over Strat: Map-Reduce (Chunking)<br/>Kontekstin karsinta (Pruning)
    Strat->>LLM: acreate(...)
    Note over LLM: Verkkopyyntö (OpenAI jne.)<br/>Token-laskenta
    LLM-->>Strat: LLM Vastaus (Pydantic Model)
    Strat-->>Node: FlattenedAtomResult
    Node-->>DAG: TraceEvent (Snapshot)
    DAG-->>Exec: Työnkulku valmis
    Exec-->>API: 200 OK (BaseResponseDTO)
```

**Abstraktioiden oikeutus:**
1. **API Router** on tyhmä ("Anemic Router") – se hoitaa vain HTTP-liikenteen.
2. **ExecutionService** vastaa käyttöoikeuksista ja tietokantatransaktioista.
3. **DAGExecutor** ymmärtää verkkorakenteen, mutta ei tiedä mitä yksittäinen solmu tekee.
4. **NodeExecutor** vastaa yhden solmun rahankäytön (FinOps) rajoittamisesta ja virheiden nappaamisesta.
5. **LLMNodeStrategy** vastaa pelkästään promptien kääntämisestä (PromptCompiler) ja kontekstin rajaamisesta.
6. **LiteLLMProvider** on fyysinen verkkokerros, joka voi vaihtua lennosta (OpenAI -> Anthropic).

## DAG-moottori: Arkkitehtuuri ja Asynkronisuus

Työnkulkujen orkesterointi on keskitetty `services/orchestrator/dag_executor.py` -moduuliin. Moottori ei ylläpidä paksua ajonaikaista muistitilaa vaan perustuu puhtaalle Event Sourcing -mallille. Arkkitehtuuri on pilkottu neljään eristettyyn komponenttiin:

```mermaid
flowchart TD
    Start((Ajoon lähtö)) --> Rehydration["Rehydration (StateProjector)"]
    Rehydration --> Check{"Onko ajamattomia solmuja?"}
    
    Check -- Kyllä --> Concurrency["Semafori jonotus (MAX_LLM)"]
    Concurrency --> NodeExec["NodeExecutor ⚡ (Strategy Pattern)"]
    
    subgraph TaskGroup["Asynkroninen TaskGroup"]
        NodeExec --> Breaker{"FinOps Circuit Breaker"}
        Breaker -- "Estetty/Raja ylittyi" --> AbortTask((TaskGroup Abort / 422))
        Breaker -- "Sallittu" --> StrategySelect{"Valittu Strategia"}
        StrategySelect --> LLMStrategy["LLMNodeStrategy (Map-Reduce & ChunkingService)"]
        StrategySelect --> LogicStrategy["LogicNodeStrategy (Puhdas koodi)"]
        LLMStrategy --> StrategyMerged((Strategia Suoritettu))
        LogicStrategy --> StrategyMerged
        StrategyMerged -- "Onnistui" --> CommitTrace["TraceEvent & ExecutionCommitter"]
        StrategyMerged -- "Epäonnistui (Error)" --> FailBoundary["Fail-Fast (Koko TaskGroup perutaan välittömästi)"]
    end
    
    CommitTrace --> Check
    Check -- "Ei (Kaikki ajettu)" --> Blueprint["Blueprint Transformer (BFF Render)"]
    Blueprint --> End((Valmis Zero-Math Raportti))
    
    FailBoundary --> ErrorLog["Tallenna RFC 7807 ErrorTraceEvent"]
    ErrorLog --> Abort((Prosessi Katkaistu))
```

1. **DAGCompilerService (Shift-Left Pre-Flight Compilation):** 
   * Esivalmistelee ja validoi ylätason riippuvuudet staattisen analytiikan avulla jo työnkulkujen tallennusvaiheessa.
   * Etsii DFS-algoritmilla syklisiä riippuvuuksia (Infinite Loops) ja varmistaa topologisen analyysin (Kahn's iteration) avulla, että eteenpäin suunnatut muuttujaviittaukset (`$inputs`, `$steps`) ovat varmasti saatavilla suorituksen aikana. Tämä Shift-Left -validointi estää API-kustannuksia tuhlaavat myöhäisvaiheen kaatumiset ja umpikujat (Deadlocks).
2. **DAGExecutor (Orkestraattori):** 
   * Vastaa verkon topologian (Dependency Graph) varmistamisesta ja solmujen rinnakkaisajosta. Ennen topologian aloitusta suoritetaan Pre-Hydration: moottori kutsuu Hook-rekisterin `input_processing` -tilaa eristetyllä `HookState`lla purkaakseen ja esikäsitelläkseen datan ajoa varten.
   * Suorittaa solmut (StepRule) natiiveina `asyncio.TaskGroup` -kapselointeina. Jos yksittäinen solmu kaatuu asynkronisen ajon aikana, `TaskGroup` perutaan ja ajon resurssit tapetaan automaattisesti taaten täydellisen "Fail-Fast" nollavuototilan.
   * Hallinnoi ajonaikaista rinnakkaiskattoa vahvan semaforin (`SystemConcurrency.MAX_CONCURRENT_LLM_STEPS`) avulla suojellakseen ulkoisia API-rajoitteita (Rate Limiting).
   * Lukee työnkulun `strictness_level` -parametrin DTO:sta ja reitittää sen eteenpäin koko verkon topologian läpi.
3. **NodeExecutor (Yksittäisen tason äly - Strategy Pattern):** 
   * Kapseloi askeleen ajologiikan (`LLMNodeStrategy` tai `LogicNodeStrategy`) täyteen eristykseen. `LLMNodeStrategy` ei ole vain putki, vaan itsessään laaja Map-Reduce -orkestraattori, joka ottaa vastaan rajattoman atomisen matriisin (`MATRIX_SAMPLING_LIMIT = 0`), pilkkoo sen `ChunkingService`:n avulla turvallisiin **Semantic Micro-Batching** -paloihin (max 10 atomia) välttyäkseen Token-ylikuormalta. Palat ajetaan rinnakkain `asyncio.TaskGroup`:n alaisuudessa. Lopulta Reducer yhdistää tulokset absoluuttisen deterministisesti lajittelemalla ne takaisin staattiseen järjestykseen ennen matemaattista reduktiota.
   * **Dead Letter Queue (DLQ) Arq Fallback Logic & Transient Error Boundary:** Rinnakkaiset `ChunkWorker`-prosessit on suojattu "Fail-Fast DLQ Routing" -logiikalla ja tiukalla virheluokittelulla (Transient vs. Structural).
     - **Transient Errors (Retryable):** Verkkokatkokset, Timeoutit, Rate Limitit ja API:n Service Unavailable -tilanteet luokitellaan ohimeneviksi. Nämä sallivat asynkronisen uudelleenyrityksen suoraan chunk-tasolla (max 2 yritystä, `MAX_CHUNK_RETRIES`) eksponentiaalisella viiveellä ennen luovuttamista. Orkestraattori seuraa näiden toipumista (`_dlq_retry_count`) telemetriassa.
     - **Structural Errors (Terminal):** Pydantic `ValidationError`, konfiguraatiovirheet (AppException) ja tietoturvarikkomukset. Näitä **ei** koskaan yritetä uudelleen (Zero Retry), vaan ne reititetään välittömästi. Worker palauttaa orkestraattorille `{"_dlq_status": "FAILED/DLQ", "reason": "<error>"}`. Tämä mahdollistaa chunkin tyylikkään siirtämisen Dead Letter Queueen auditoitavaksi ("Duct Tape Ban" -säännön puitteissa) kaatamatta koko asynkronista puuta.
   * Välittää `validation_context`:in (esim. ankaruustason) Pydantic V2 `.model_validate_json()` -metodille.
   * Suorittaa ns. "FinOps Circuit Breaker" -tarkistuksen ennen kutsua taatakseen, ettei asiakas ylitä budjettia sadoilla käskyillä.
   * Palauttaa `TraceEvent` tai virtuaalisesti siepatun `ErrorTraceEvent` -lokituksen deterministisestä lopputulemasta.
4. **ExecutionCommitter (Event Sourcing -tallennin):** 
   * Ottaa vastaan ajonaikaisen JSON-lokijonon ja puskee "Snapshotit" (`execution_trace` / `step_states`) alastomana Pydantic-datana tuettuihin tallennuskerroksiin (`repository.py`).
   * Pysyy täysin tietämättömänä itse logiikasta varmistaen vain nopeimmat asynkroniset tietokantasiirrot ajon edetessä "Optimistic UI" tukea varten.

### Orkestraattorin apukomponentit

* **`prompt_compiler.py`:** Dynaamisten Pydantic-skeemojen ("Two-Tier schema") lennosta generoiva käännin V2 Structured Outputs -käyttöön. Käännin sisältää "Self-Healing citation" -logiikan, joka korjaa LLM:n palauttamat puolittaiset viitetekstit oikeiksi sallittujen lähteiden perusteella. Ehkäisee Pydantic-käännösten räjähtämisen suurissa yli 200 askeleen DAG-ajoissa hyödyntämällä LRU-välimuistia.
* **`atomizer.py`:** Vastaa "Deep Atomization" -käsittelystä tallennusvaiheessa. Purkaa LLM:n avulla evaluointikriteerit täsmälleen 15 mikrootomiin ja obfuskoi asiantuntijatermit estääkseen kontekstipakoilua.
* **`chunk_accumulator.py`:** Kokoaa turvallisesti yhteen Map-Reduce -suoritusten LLM-palaset (chunks). Pakottaa arkkitehtuurin "No Naked Dicts in State" -säännön siirtämällä sanakirjojen hallinnan ja stringien yhdistämisen orkestraattorin pääsilmukasta testattavaan erilliskomponenttiin.
* **`context_router.py`:** Eristää UI-lähtöisen reitityksen ja datan karsinnan (`route_and_prune`). Poimii suorituspuusta (`trace_event`) skooppi-sokeasti täsmälleen vain ne block-tason XAI-laajennokset, joita käyttöliittymän valittu `OutputProfileConfig` vaatii (`visible_block_extensions`). Reititin ei enää sisällä kovakoodattuja ohituksia (esim. `variance_validation`). Toimii myös "Fail-Fast" portinvartijana muuttujien reitityksessä (`normalize_and_validate_variable`), hyläten orvot viittaukset sekä vanhentuneet V1-tyyliset `.output`-polut.

> **Syväsukellus NodeExecutorin kerrokseen:** Tarkempi arkkitehtuurikuvaus yksittäisen tason älystä ja kontekstin rakentamisesta löytyy dokumentista [03b: Orchestraattoristrategiat ja Kontekstin Rakennus](./03b_orchestrator_strategies.md).

### Rehydration (Kesken jääneen työn jatkaminen)
DAG-moottorin nojatessa Event Sourcingiin, pystyy prosessi tarvittaessa toipumaan mistä tahansa ulospäin näkyvästä konesaliradasta:
1. Orkestraattori hakee lukitun työn tietokannasta ("Rehydration").
2. `StateProjector` -luokka pyöräyttää kaikki vanhat muistiinkirjatut taustalokit järjestyksessä kerralla muokatakseen sisäisen "Virtual State"n haluttuun pisteeseen.
3. NodeExecutor herättää eloon vain ne solmut, joiden tila oli lokitettu arvoon `pending` tai `failed`, pakoen sokeita massaoletuksia.

## Admin Studio Service (Ideointi ja mallinnus)

`studio.py` (`Admin Studio Service`) hallinnoi koko järjestelmän domain-malleja (Workflows, Steps, PromptBlocks, OutputProfiles) sekä ylätason `SystemConfig` tiedostoja. Tämä palvelu kapseloi sisäänsä keskitetyn järjestelmänhallinnan logiikan:
* Suorittaa raskaampia graafioperaatioita, kuten työnkulkujen "Shallow-Deep Copy" kloonauksia, säilyttäen tiukan rakenteellisen eheyden.
* Tarjoaa `simulate_workflow()` -graafivalidoinnin etukäteen tapahtuvalle simulaatiolle.
* Valvoo ohi reitittimien kulkevia RBAC-tarkastuksia ja laajoja päivityksiä Admin Studio -toiminnoille.

## Tiedostojen renderöinti, BFF ja Ulkoiset (MCP) Palvelut

`backend_v2/services/blueprint.py` on järjestelmän näkyvin "Backend-For-Frontend" kerroksen muotoilija. Koska Frontendissä vaikuttaa tiukka nollalaskennan "Zero-Math UI" -sääntö, kaikki graafiset pisteytyslokiikat on sidottu yksinomaan tänne.

* Ajossa `BlueprintTransformer` lukee valitun `OutputProfile` -konfiguraation ja analysoi työnkulun lopullisen "FrozenContextin".
* **Extension Scope Separation:** Järjestelmä ylläpitää tiukkaa erottelua matriisitason XAI-laajennosten (`visible_block_extensions`) ja työnkulkutason globaalien laajennosten (`visible_workflow_extensions`) välillä. `SynthesisHook` ja siihen liittyvä LLM-kooste saavat käsiteltäväkseen vain `block_extensions` -datat (kuten valmennus ja falsifiointi), kun taas BlueprintTransformer poimii globaalit metriikat (kuten `variance_validation`) suoraan `workflow_extensions` -määrityksistä ohittaen LLM-synteesin. Tämä reititysmekanismi estää tekoälyä rationalisoimasta tai hallucinoimasta globaaleja mekaanisia metriikoita.
* **Zero-Math sääntö:** Blueprint paketoi numeeriset skaalaimet ja värimuunnokset valmiiseen `ReportLayoutDTO` -mallistoon. Käyttöliittymä tai PDF-generaattori ei joudu koskaan miettimään miten x/y korrelaatio ratkaistaan, sillä ne kaikki ovat puhtaasti palvelimen päättelemässä DTO-putkessa.

**Virtuaaliset Järjestelmäaskeleet ja Raportin Generointi (Arq Worker)**
Suorituksen (Execution) matemaattinen pisteytys ja loppuraportin renderöinti on irrotettu DAG-verkosta omiin **Virtuaalisiin Järjestelmäaskeleisiin** (esim. `sys_render_<profile>`). Kun LLM-työnkulku valmistuu, taustajärjestelmä siirtää vastuun Arq Workerille (`render_profile_job`). 
Tämä työntekijä lukee `OutputProfile`:n ja syöttää tarvittavat `strictness_level` ja `scoring_strategy` -arvot matemaattisille moottoreille lennosta, luoden `ReportDataDTO`:n. Työntekijä hallinnoi virtuaalisen askeleen `status`-päivityksiä (running, completed, failed) suoraan tietokantaan.

**PdfReportService (`pdf_generator.py`)**
Toimii BlueprintTransformer-luokan rinnalla ja hyödyntää samaista Layout DTO -pohjaa dynaamisten PDF-tiedostojen rakentamisessa (Jinja2 & WeasyPrint). Palvelu toimii puhtaana datamuuntimena palauttaen PDF-tavuvirran.

**Machine Control Protocol (MCP)**
Järjestelmään sisältyy `mcp/` -hakemisto, joka toimii agenttisten verkkohakujen ja tekoälyn ulkoisten toimintojen rajapintana. Palvelut kuten `mcp_tool_loop.py` ja luokat kuten `tavily_search_client.py` kykenevät tekemään itsenäistä verkkohakua ulkopuolisista viitekehyksistä.

## IAM ja Identiteetti

`services/auth.py` valvoo ja todentaa pyynnöt erillisten Custom Claims tai Firebase SDK -tokentapaisten puitteissa (JWT). Moduulissa käsitellään organisaation vaihto-operaatiot (Tenant Isolation), tuetaan sisäänrakennettuina "Bring Your Own Key" (BYOK) hallintoa ja varmennetaan, etteivät ristiin organisaatiot tallenna dataa väärillä `org_` prefikseillä. Lokaalissa "Mock_DB"-tilassa tämä osio ohitetaan ylikuormittavien HTTP-viiveiden estämiseksi ja valtuutetaan keinotekoinen rooli rajapintatestejä varten.

---

# Orkestraattoristrategiat ja Kontekstin Rakennus

Tämä dokumentti syventää DAG-kuvausta purkamalla työnkulkumoottorin strategiakerroksen (`backend_v2/services/orchestrator/strategies/`). Strategiakerros vastaa työnkulkujen yksittäisten solmujen (Step) täytäntöönpanosta NodeExecutorin alaisuudessa.

Arkkitehtuuri perustuu Strategy-suunnittelumalliin, jossa solmun tyyppi (esim. `llm` tai `logic`) määrittää käytettävän suoritusstrategian. Kerros noudattaa tiukasti Quorumin Fail-Fast -periaatteita: virheet nostetaan välittömästi ja tila on vahvasti tyypitetty.

## `BaseNodeStrategy` (base.py)
Kaikkien strategioiden kantaluokka, joka määrittelee solmun suorituksen rajapinnan ja jakaa yhteiset operaatiot.

- **Hookien suoritussilmukka:** Abstrahoi Pre- ja Post-hookien suorituksen (`run_pre_hooks`, `run_post_hooks`) ulos ydinlogiikasta. Silmukka iteroi solmun (Blueprint) määrittämät hookit ja yhdistää (deep merge) niiden palauttaman tilamuutoksen askeleen tilaan.
- **`HookState` ja `HookDependencies` injektio:** Hookeille injektoidaan aina vahvasti tyypitetty `HookState` sekä `HookDependencies`.
- **Fail-Fast ja Circuit Breaker:** Sisältää `assert_quota`-metodin, joka tarkistaa organisaation token-rajat ennen ajoa. Jos raja ylittyy, heitetään välittömästi `AppException`-poikkeus.

## `LLMNodeStrategy` (llm.py)
Vastaa tekoälysolmujen (LLM Step) raskaasta orkestroinnista dynaamisen mallintamisen ja token-optimoinnin avulla.

- **Modular Extraction Decoupling & Prompt Block Fusion (Epic 60):** 
  Työnkulun ajossa promptien ja skeemojen koostaja ei enää käsittele litteää promptBlocks-listaa. `LLMNodeStrategy` lataa tietokannasta ja validoi erikseen askeleelle määritetyt lohkot:
  * Roolilohkon (`role_block_id`) tekoälyn persona-ohjeistukseksi.
  * Poimintaprotokollalohkon (`extraction_protocol_block_id`) evidenssinpoiminnan Zero-Trust -direktiiveiksi.
  * Kriteerilohkot (`criteria_block_ids`) arvioitaviksi TDA-väitteiksi tai BARS-matriiseiksi.
  Mikäli jotakin vaadittua lohkoa ei löydy, strategia heittää välittömästi `AppException`-virheen.
- **Dynamic Schema Isolation & Caching Optimization:**
  Roolit ja protokollat injektoidaan staattisesti system-promptiin, kun taas dynaamiset TDA-kriteerit kootaan dynamic extraction -skeeman alle. Tämä pitää dynamic skeeman äärimmäisen kevyenä, estäen Vertex AI serving grammar state -rajojen ylittymisen ja mahdollistaen 95 %+ caching-osumat backendissa.
- **Map-Reduce Orkestraatio ja Micro-Batching:** Kun askeleessa on matriisiblokkeja ja deterministisesti lajiteltu syöte (satunnainen sekoitus on kielletty), LLM-solmu jakaa datan `ChunkingService`:n avulla Semantic Micro-Batch -paloihin (max 10 atomia). Palat ajetaan asynkronisesti rinnakkain `asyncio.TaskGroup`:in ja FinOps-semaforien alla. Tulokset validoidaan Fail-Fast Pydantic -säännöillä, minkä jälkeen MatrixReducer ja ChunkAccumulator lajittelevat ja yhdistävät (Reduce) ne matemaattisesti Three-State Logicin (PASSED, FAILED, DLQ) mukaisesti täydellisellä osumatarkkuudella.
- **Map-Merge-Evaluate & AST-Evaluator (System 2):**
  Downstream-arvioinnissa ei sallita vapaata LLM-tuomiota. Orkestraattori ajaa **Map-Merge-Evaluate** -prosessin:
  1. *Map:* Asynkroniset chunk-workerit poimivat semanttiset faktat LLM:n avulla `DynamicExtractionResponse` -malliin.
  2. *Merge:* Workerien poiminnat yhdistetään globaaliksi `MergedFactsDTO`-objektiksi. Mahdolliset ristiriidat (sama fakta eri sivulla) ratkaistaan deterministisellä *First-Wins* -törmäyksenestolla.
  3. *Evaluate:* Deterministinen Python-kerroksen **AST-evaluaattori** (`ast_evaluator.py`) ajaa 3-tilaista logiikkaa (`TRUE`, `FALSE`, `DLQ`) merged_facts-datalla, suojaten arvioinnin LLM:n oskilloinnilta ja rationalisoinnilta (Shannonin entropia 0.000, Fleiss Kappa 1.0).

## `LogicNodeStrategy` (logic.py)
Käsittelee puhtaasti ohjelmalliset askeleet (Native/Logic Step) delegoimalla varsinaisen suorituksen Hook Registrylle.

- **Hook Lookup:** Hakee solmuun kytketyn logiikka-hookin nimen suoraan `hook_registry`:stä Blueprintin perusteella.
- **Tilan evaluointi:** Evaluoi nykyisen tilan StateProjectorista ja kokoaa sen tiukasti tyypitettyyn `HookState`:en ennen logiikkahookin asynkronista kutsumista.
- **Fail-Fast:** Jos primaarisen logiikkahookin suoritus palauttaa `success=False`, `LogicNodeStrategy` lokittaa välittömästi kriittisen tason virheen ja heittää `AppException`-virheen. Hiljaisia epäonnistumisia ("silent fallbacks") ei sallita ohjelmallisessa logiikassa.

## `ContextBuilder` (context_builder.py)
Vastaa LLM-kontekstin rakentamisesta, muuttujamappausten resoluutiosta ja datan karsimisesta ennen token-vientiä.

- **`schema_map`-pohjainen karsinta (Allowlist):** LLM-kontekstin rakentamisessa sovelletaan tiukkaa Fail-Fast -sallintalistaa. Vain `schema_map`-sanakirjaan eksplisiittisesti rekisteröidyt avaimet päästetään läpi. Jos avainta ei löydy rekisteristä, se pudotetaan (Pruning).
- **Kronomnesian torjunta ja Spatial Slicing (Spatiaalinen paloittelu):**
  Aikahäiriöiden estämiseksi `ContextBuilder` tunnistaa säännöstä aikajanaan sidotun ehdon (esim. *"ennen vaihetta 2"*). Sen jälkeen se etsii tekstistä vastaavan rajamerkin (esim. `[PHASE 2]`) ja leikkaa mekaanisesti kaiken rajan jälkeisen aineiston irti ennen LLM-kutsua. Falsifiointivaiheessa LLM palauttaa nollahavainnon (`evidence_found = False`), ja Hook-kerros suorittaa Boolean-inversion (`inverse_evidence = True`), kääntäen tämän oikein `PASSED`-tilaksi. LLM ei näe leikattua tulevaisuutta, mikä estää kronomnesian aukottomasti.
- **Fail-Fast -ehdottomuus:** Kaikki oletukset ovat ohjelmallisesti kiellettyjä. LLM-kontekstiin lisättävät metadatat pääsevät läpi ainoastaan, jos ne on määritelty joko Pydanticin natiiveina ydinkenttinä, erillisinä vapaaehtoisina XAI-laajennuksina tai kiinteinä globaaleina järjestelmäavaimina. Tuntemattomien avainten passthrough-ohitukset eivät ole sallittuja.

## Arkkitehtoninen Rajoite: Täyden Asynkronisuuden Illuusio (The CPU Trap)

Vaikka `DAGExecutor` hyödyntää `asyncio.TaskGroup`-kapselointeja ja asynkronista rinnakkaisajoa, järjestelmässä on tehty tietoinen arkkitehtoninen päätös pitää tietyt raskaat tekstinkäsittelykomponentit (kuten `PromptCompiler`) synkronisina.

### 1. CPU-pullonkaulan Harha (The CPU Trap)
Asynkronisuus (`async/await`) nopeuttaa ainoastaan I/O-operaatioita. `PromptCompiler.py` on massiivinen komponentti, jonka ydinlogiikka koostuu raskaasta merkkijonojen manipuloinnista ja synkronisesta Pydantic-validoinnista. Nämä ovat täysin **CPU-riippuvaisia** tehtäviä. Vaikka `PromptCompiler` muutettaisiin asynkroniseksi, sen suorittama raskas tekstinmurskaus blokkaisi Pythonin tapahtumasilmukan (GIL) silti. Asynkronisuus toisi vain illuusion rinnakkaisuudesta, mutta lisäisi coroutine-overheadia.

### 2. Virheiden Hallinnan Monimutkaisuus (Fail-Fast Rinnakkaisuudessa)
Täysin asynkronisen (100% async) I/O- ja CPU-arkkitehtuurin toinen rajoittava tekijä on "Fail-Fast" -periaatteen monimutkaisuus vapaassa rinnakkaisuudessa. Jos järjestelmä ajaa useita asynkronisia alitehtäviä rinnakkain ja yksi niistä kaatuu Pydantic-validointiin, kaikkien muiden orpojen tehtävien turvallinen peruuttaminen vaatii rutiineja, jotta muisti ja yhteyspoolit eivät vuoda. Tästä syystä rinnakkaisuus on järjestelmässä keskitetty tiukasti valvottuihin `TaskGroup`-semaforeihin orkestraattorin juurella.

## Epic 57: Y-Funnel Context Flow & Agent Grounding

Epic 57 toteuttaa työnkulkujen ohjaukseen innovatiivisen **Y-Funnel-tietovuon**, jossa deterministiset mekaaniset metriikat syötetään dynaamisesti kognitiivisille LLM-agenteille:

* **Mekaanisten syötteiden valmistelu:** Kun DAG käynnistyy, `DAGExecutor` alustaa mekaaniset esikoukut (kuten `metrics.py` ja `linguistics.py`). Nämä ajetaan heti ja niiden tulokset kirjoitetaan `HookState`-kontekstiin.
* **Context Compiler & Grounding:** Kun execution-vaihe etenee `sr_` (specialist reasoning) -solmuihin, `LLMNodeStrategy` pyytää `PromptCompiler`-komponenttia luomaan promptit ja syötteet. `PromptCompiler` poimii `HookState`-kontekstista mekaaniset metriikat ja injektoi ne XML-pohjaisina ankkureina (`<mechanical_anchors>`) `Causal Analyst` ja `Performativity Detector` -agenttien system-ohjeisiin lennosta.
* **Päättelyn ankkurointi:** Tämä grounding-malli estää LLM-agentteja rationalisoimasta tai tekemästä virheellisiä arvioita, sillä niillä on system-promptissa kiistaton tieto tekstin sanamääristä, performatiivisista täytesanoista ja automaatioharha-suhteista.

<br><hr>

➡️ **Seuraavaksi:** Kun tiedät, miten DAG-verkko etenee solmusta toiseen, lue [05_llm_and_hooks.md](./05_llm_and_hooks.md). Se sukeltaa yksittäisen solmun sisään ja selittää, miten Hookit ohjaavat sokeaa tekoälyä.
