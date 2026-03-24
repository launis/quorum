# **ARKKITEHTUURIMÄÄRITTELY: Komponenttipohjainen AI-orkestraattori (Enterprise V2.5)**

Tämä dokumentti määrittelee dynaamisen, palvelinohjatun (SDUI) ja sataprosenttisesti auditoitavan tekoälyorkestraattorin arkkitehtuurin. Järjestelmä siirtää kaiken kognitiivisen liiketoimintalogiikan, datareitityksen, arvioinnin kalibroinnin ja käyttöliittymän piirtosäännöt tietokantaan, mikä mahdollistaa ominaisuuksien globaalin skaalaamisen välittömästi ilman koodipäivityksiä (Zero-Deploy).

## **1. Arkkitehtuurin Ydinfilosofiat**

1. **Zero-Deploy, BFF (Backend-For-Frontend) & Responsiivisuus:** Käyttöliittymä ja tulostemoottorit ovat liiketoimintalogiikasta tietämättömiä renderöijiä. Kaikki syötevaatimukset, arviointikriteerit, tekoälymallit ja käyttöliittymäkomponentit konfiguroidaan tietokannassa.
2. **Reaktiivinen Tilanhallinta (Riverpod):** Koko käyttöliittymän tilanhallinta ja asynkroniset datavirrat rakennetaan Riverpodilla uusimpien best practice -mallien mukaisesti.
3. **Schema-Driven AI (Dynaaminen Pydantic):** Tekoälyltä ei koskaan pyydetä tulosteen muotoa vapaassa tekstissä. Tulostevaatimukset käännetään lennosta OpenAPI JSON Schema -validointiluokiksi (`Structured Outputs`).
4. **Universaali Mittausarkkitehtuuri ("PromptBlocks"):** Vapaamuotoiset laadulliset analyysit, numeeriset/desimaaliset mittaristot ja ohjeistukset yhdistetään yhdeksi "PromptBlock" -tietokantamalliksi poistaen siilot.
5. **Arvioinnin Dynaaminen Kalibrointi (Model Strategy):** Järjestelmä erottaa kognitiiviset intentiot (`fast`, `deep`, `strict`, `precise`) fyysisistä malleista globaalissa `system_config` rekisterissä.
6. **Empiirinen XAI (Grounded Explainable AI via MCP):** Arvioinnit eivät perustu sokeaan LLM-päättelyyn, vaan dynaamisiin Model Context Protocol (MCP) -verkkohakuihin, joiden löytämät absoluuttiset faktat sementoidaan näyttöinä osaksi muuttumatonta raporttia.
7. **Dynaaminen Datan Reititys (Semantic Data Flow):** Työnkulkuun tulevan datan määrä on dynaaminen. Askeleet muodostavat suunnatun syklittömän verkon (DAG), jossa data reititetään nimenomaisilla `$inputs.` tai `$steps.` viittauksilla.
8. **Ikuinen Auditoitavuus (Append-Only & Snapshotting):** Mitään kognitiivista palikkaa ei koskaan ylikirjoiteta ajon aikana. Historialliset ajot jäädyttävät suoritushetken absoluuttisen tilan (frozen_context).
9. **Single Source of Truth (Domain Service Layer):** API-reitittimet ovat rakenteellisesti aneemisia. Kaikki tietokantaintegraatiot ja Tenant-eristys tapahtuvat suojatussa Service-kerroksessa.
10. **Strict Pydantic Roolipakotus (Role Enforcement):** Pydantic-skeemat estävät "geneeriset yhteenvedot" aktiivisesti. Kentät (kuten `evaluation_notes`) vaativat kovaa arviointia *vain* kunkin agentin oman roolilinssin läpi, poistaen LLM:n matemaattisen kloonautumisen (cloning effect) rinnakkaissuorituksissa.
11. **The Anti-Mirror Protocol (Sokkotestaus & Ihmisdatan Eristys):** Järjestelmä ei koskaan salli tekoälyn arvioida toista tekoälyä silloin, kun pisteytetään loppukäyttäjää. Kognitiivisen Groupthinkin estämiseksi kaikki asiantuntija-agentit suoritetaan täysin rinnakkain (Parallel Blind Audit). He lukevat `$inputs`-syötteenä puhtaaksi rajattua "Käyttäjän tekstiä", josta on riisuttu muiden AI-entiteettien tuotokset. Tämä takaa EU:n tekoälyasetuksen (XAI) vaatimukset ihmisen suorituksen selitettävyydestä.
12. **Itsekorjautuva Tekoäly (Self-Healing LLM):** Jos kielimalli tuottaa vastauksessaan virheellisen tietorakenteen (esim. puuttuva JSON-avain JSON Schemassa), arkkitehtuuri ei kaadu varoittamatta. Se sieppaa virheen (`ValidationError`), palauttaa poikkeuksen suoraan takaisin tekoälylle, ja käskee mallia korjaamaan oman hallusinaationsa lennosta.
13. **Ennakoiva DAG-Kääntäjä (Pre-Flight Validation):** Työnkuluille tehdään staattinen rakenneanalyysi (Kahnin algoritmi - silmukoiden ja puuttuvien viittausten tunnistus) "kuiva-ajona". Järjestelmä estää mahdottomien kognitiivisten solmujen käynnistämisen matemaattisesti etukäteen (Zero-Token waste), säästäen rahaa reitittimen API-tasolla.
14. **Älykäs Kuormanhallinta (Concurrency Limiting):** Järjestelmä suojelee ulkoisia LLM-rajapintoja (kuten Google Vertex AI) dynaamisella asynkronisella nopeusrajoittimella. Laajatkin rinnakkaisverkot kykenevät hidastamaan omaa suoritustaan automaattisesti Model Registryn mallikohtaisten `rpm_limit` ja `tpm_limit` -määritteiden pohjalta, suojaten arkkitehtuuria `429 Resource Exhausted` -pullonkauloilta.

---

## **2. Kognitiivinen Monikielisyys (I18n Fallback & The 5-Layer Strategy)**

Quorum V2:n työnkulut irrottavat tekoälyn "kognitiivisen" päättelymekanismin (aina englanniksi laadun maksimoimiseksi) loppukäyttäjän "esitys- ja asiointikielestä" (esim. suomi) hyödyntäen The Holistic Localization Strategy -mallia.

### Kerros 1: Staattinen Käyttöliittymä (Compile-Time l10n)
Flutterin luontaiset `.arb`-tiedostot (esim. `app_fi.arb`) on varattu **ainoastaan** käyttöliittymän kiinteille komponenteille (napit, navigaatio, staattiset otsakkeet). Virheenhallinnassa (RFC 7807) käytetään `AppErrorExt` reititintä, joka muuntaa backendin Enum-tunnisteet yhdistetyksi *Actionable Hintiksi* omalla kielellä.

### Kerros 2: BFF-Tietokanta & Dynaamiset Tulostusprofiilit (Runtime Payload)
Kun järjestelmään lisätään matriiseja tai sääntöjä, Pydantic DTO (esim. PromptBlock) tallentaa ne kantaan muodossa `translations: {"fi": "Syyttäjä...", "en": "Prosecutor..."}`. Flutter lukee aina oman lokaalinsa mukaisen käännöksen dynaamisesti (SafeCast).

### Kerros 3: Kognitiivinen Moottori & English-Only Mandate (The Deep Engine)
Tekoälymalli on huomattavasti kyvykkäämpi englanninkielisenä. Asiantuntija-agenttien metatiedot ja PromptBlockien järjestelmätason ohjeet on **pakko kirjoittaa englanniksi** (`translations["en"]`). Malli pakotetaan ajattelemaan (JSON `reasoning_trace`) englanniksi, mutta se on velvoitettu poimimaan käyttäjän alkuperäiset lainaukset täysin koskemattomina alkukielellä.

### Kerros 4: Numeerinen ja Temporaalinen Standardi (Dates, Numbers)
Numeroita, päivämääriä, kellonaikoja ja valuuttoja ei koskaan lokalisoida backendissä. Kaikki aika kulkee ISO 8601 UTC -muodossa (`"2026-03-14T15:30:00Z"`) ja numerot primitiiveinä (esim. `5.0`). Flutter vastaa formatointilogiikasta käyttäjän laitteen paikalleen Dartin `intl`-kirjaston avulla (ICU).

### Kerros 5: The Translation Boundary & Loppusynteesi 
Koska `.arb` ei voi kääntää lennossa syntyneitä tekoälyn ajatusketjuja tai raportteja, Backend käyttää tarvittaessa "Translation Hook" -suodatinta. Se kääntää vain askeleen JSON-tuloksen luonnolliset arvot asiakkaan pyytämälle kielelle muuttamatta JSON-avaimia. Lopulta Markdown-tuote muodostetaan tästä lokaalista rakenteesta täysin ihmisluettavaksi.

---

## **3. Tietokantamalli (NoSQL Document DB)**

Tietokanta on suunniteltu Firestoren varaan tuotannossa ja lokaalin `db_v2.json` varaan kehityksessä. 

### KERROS 1: KIRJASTOT (Peruspalikat)
* **system_configs:** Singleton-kokoelma, joka mapittaa kognitiiviset strategiat (fast, deep, strict) fyysisiin LLM-malleihin.

### KERROS 2: ORKESTRAATIO (Äly ja Työnkulut)
* **prompt_blocks (Matrix & Rules):** Sisältää kaikki kognitiiviset ohjeet (`type`: `instruction`, `matrix`, `hook`).
* **steps (TaskBlueprints):** Sitovat abstraktin ohjeen (`prompt_block`) kognitiiviseen strategiaan (`model_strategy`) tehden nieluista uudelleenkäytettäviä palikoita verkolle. Oletuksena näissä asuu myös sisäinen **ydin-hookkien** lista (`Step.pre/post_hooks`), joka ajetaan poikkeuksetta (esim. `json_parser_hook`) estääkseen kaatumiset missä tahansa työnkulussa.
* **workflows (DAG Router):** Määrittelevät laajan datamallin käyttöliittymän piirtämiseksi (`ui_schema` json-valikot) sekä dynaamiset syötteet (`expected_inputs`). Työnkulun loppukäyttäjänäkyvyys ohjataan suoraan absoluuttisilla tilalipuilla (`status: active`, `is_public: true`), jotka estävät keskeneräisten (draft) luonnosten laukeamisen tuotantoon. Työnkulun tärkein osa on `steps`-taulukko (Käännettynä uutena `StepRule` Node-instansseina), joka luo riippuvuusverkon eri solmujen välille.
  * **StepRule (The DAG Node):** Blueprintin ilmentymä tietyssä reitissä. Antaa mahdollisuuden hyödyntää samaa syyte-mallia samassa putkessa viidesti, jokaisella kerralla omilla **lokaaleilla, työnkulkukohtaisilla hookeillaan** (esim. `normalize_matrix_scores` tai `translation_hook_en`). Moottorin tehtävä on liimata ydin-hookit ja lokaalit hookit turvallisesti yhteen (Union-Combined Execution). Määrittelee myös lokaalin **datareitityksen** (`input_mappings`).

### KERROS 3: HISTORIA JA AUDITOINTI
* **executions (Ikuinen Jäädytys):** Tallentaa `raw_inputs` (käyttäjän syötteet), `frozen_context` (syväkopio säännöistä ajon hetkellä) ja `results` (Pydantic-validoitu tulos-JSON).

---

## **4. Syötteet, Roolit ja Datan Reititys (Semantic Data Flow)**

### **4.1. Odotetut syötteet (Expected Inputs) ja Universaali Reititys**
Käyttöliittymä lukee ohjelmallisesti `workflows`-dokumentin `expected_inputs`-taulukon ja piirtää vaaditut ohjaimet. Mukaansa jokainen syöte ottaa tiedon roolista (`ai_description`), joka injektoidaan raakadatan yläpuolelle ("ai_instruction" The English-Only Mandaten mukaisesti). 

Ennen syötteiden laittamista LLM-analyysiin niille ajetaan järeä ohjelmallinen raivaus (Pre-Hooks). Esimerkiksi sekavat, kopioidut chattelokit (merkitty `is_chat_history = True`) työnnetään yksinomaan `ChatParserService` -älyn läpi. Tämä parserointi muuttaa sekavan leikepöytätekstin täydellisen puhtaaseen `<Rooli>: <Viesti>` Markdown -formaattiin, ennen kuin varsinainen laadun arviointi ehtii alkaa, ehkäisten mallin matemaattisen harhautumisen.

### **4.2. Routing Variables ($)**
DAG-verkossa askelilla on `input_mappings`-määritys:
1. **Globaalit syötteet (`$inputs.chat_log`):** Puhtaaksi eristetty Käyttäjän teksti.
2. **Aiempien askeleiden tulokset (`$steps.step_node_1.output.risk_score`):** Viittaus jo suoritettuun DAG-nodeen. (HUOM: The Anti-Mirror Protocolin takia ihmisen arviointimatriisit kytketään oletuksena aina rinnakkain saamaan sisäänsä vain `$inputs`).

### **4.3. 5-Level Strictness Framework ja Kognitiiviset Injektiot (2D-Moottori)**
Arviointi mukautuu 5-portaisella tiukkuusasteikolla:
*   **Makrotaso (Laadullinen Asenneinjektio):** Järjestelmä laukaisee laadullisen leikkauksen (Qualitative Shift) esim. Tasolla 5 ohittaen perustason blokkeja injektoimalla armottoman "Syyttäjä"-roolin ja korkean kognitiivisen kitkan.
*   **Mikrotaso (Määrällinen Ohjelmallinen Pakotus):** `dag_executor.py` ylikirjoittaa matriisien `strictness_level` -arvon matemaattisesti lennosta (asteikko 0-100). Taso 100 pakottaa matemaattisen joustovaran nolliin ja sallii täyden arvosanan vain täydellisyydestä.

### **4.4. Monimallinen Debattiarkkitehtuuri (Adversarial AI Pipeline)**
DAG-reititys mahdollistaa ihmisen arvioinnista ulos rajatut tekoälyjen väliset "debattityönkulut" (LLM-as-a-Judge vs. LLM-as-a-Judge). Syöttämällä esim. Analyytikon-mallille `strategy: fast` ja Syyttäjä-mallille `strategy: strict`, voidaan ketjuttaa erilaisten kielimallien neuroverkkoja tutkimaan toistensa sokeita pisteitä (`input_mappings: {"ai_report": "$step_analyst"}`). Anti-Mirror protokolla sallii tämäntyyppiset kytkennät vain silloin, kun pisteytyksen kohteena ei enää ole inhimillinen käyttäjä, vaan toisen robotin analyysi.

---

## **5. FastAPI Backend ja Suoritusmoottori**

### **5.1. Pydantic SSOT (Strict-DTO Protocol, Memory Isolation & Fail-Fast)**
Kaikki datasiirrot API-reitittimissä ja tietokannassa puskevat tiedon V2 Pydantic-validointimoottorin läpi. Mallit hyödyntävät tiukasti tyypitettyä `extra="forbid"` -sääntöä, joka kaataa tiedon sisäänoton heti (Fail-Fast), jos kanta yrittää tarjota yhtäkään hylättyä asetusavainta (ghost field).
Samalla dynaamisten JSON Schema -luokkien koodigenerointi (`SchemaBuilderService`) optimoidaan nojautumaan lokaaliin MD5-tiivisteen välimuistiin (`lru_cache`), tehden schema-latauksista miljoonien ajojen kohdalla salamannopeita. Orpokielimallin sisäinen muistivuoto (globaalit yhteismuuttujat) on täysin kielletty – kaikki data sidotaan absoluuttisella tarkkuudella eristettyyn `state.inputs` Pydantic-rakenteeseen solmutasolla, ehkäisten "haamusyötteiden" (`Ghost Input`) ylikirjoitukset.

### **5.2. Dynaaminen Faktantarkistus ja Maadoitus (Model Context Protocol - MCP)**
Vanha staattinen RAG (theory_grounding.source_url) on korvattu modernilla **Model Context Protocol (MCP)** -arkkitehtuurilla. 
Jos `StepRule` -työnkulkusolmulle on sallittu internet-oikeudet (`allowed_mcp_tools`), Quorum-moottorin Executor asettuu The Tool Loop -tilaan. Tekoäly voi asynkronisesti keskeyttää päätöksenteon, hakea empiiriset faktat pilvipohjaisilta The SSE MCP -palvelimilta, ja tallentaa haut muuttumattomaan `FrozenContext`-lokitietueeseen absoluuttisen auditoitavuuden (XAI) takaamiseksi.
*(Tarkka laajennettu tekninen kuvaus: Katso rinnakkaisdokumentti `Arkkitehtuurimaarittely_MCP_Integraatio_V2_6.md`)*

### **5.3. Hook-Riippuvuuksien Ruiskutus (Dependency Injection)**
Kaikki tietokanta- ja LLM-yhteydet ruiskutetaan suoraan FastAPIn `Depends` injektiosta Service-kerrokselle. API-kontrolleri on aneeminen mahdollistaen täydellisen eristetyn yksikkötestauksen.

### **5.4. Dual-Reporting (RFC 7807)**
API rajapinnoissa virheet hoidetaan **RFC 7807** standardin mukaisesti:
1. Poikkeus tulostetaan `logger.error` puolelle teknisen syyn (Stack Trace) kera.
2. Ulospäin nostetaan asiallinen JSON enumi (Esim. `VALIDATION_FAILED`), estäen teknologiavuodot frontendiin.

### **5.5. CoT String-Tuple Pre-Parsing (LLM Decimal Bias Ohitus)**
Koska LLM Structured Outputs ohjaa vastaukset usein tasakymmeniin tai vahvoihin kokonaislukuihin, V2 soveltaa dynaamista CoT String-Tuple ratkaisua (esim. ohjelmoi LLMn palauttamaan perustelun perään `||DECIMAL: 4.2||`). `normalize_matrix_scores`-hook sieppaa tiedon Pydanticissa, regexaa kätketyn liukuluvun ja ylikirjoittaa "tyhmän" kokonaisluvun tietokantaan säilyttäen API-tyyppiturvallisuuden.

### **5.6. O(1) Asynkroninen Orkestraatio ja Tilanhallinta (Event Sourcing)**
Moottori ei koskaan mutatoi ajon tilaa (esim. ylikirjoita vanhoja sanakirjoja). Suoritus on täysin puhdas asynkroninen "Append-Only" -nauha yksittäisiä `TraceEvent` -tapahtumia. Ajon tila rakennetaan muistiin deterministisellä ja lukkiutumattomalla `fold_trace()` -kokoajalla. Tämä mahdollistaa massiivisen satojen agenttien rinnakkaisuuden (`asyncio.gather`) ilman thread-lukkoja ja tarjoaa täydellisen toistettavuuden (Rehydration) vikatiloista toipumiseen ilman redundantteja API-kutsuja LLM:lle.

### **5.7. Checkpointing ja "The Flush Strategy"**
Kun työnkulun looginen solmu valmistuu, I/O-viiveiden ja tietokantalukkojen eliminoimiseksi `ExecutionCommitter` purskauttaa (flush) In-Memory puskuriin kertyneen `execution_trace` -taulukon sellaisenaan kerralla tietokantaan / Blob-storageen. Tästä muodostuu synkronoitu palautumispiste. Menetelmä mahdollistaa jopa gigatavujen tila-analyysien käsittelyn suojellen FastAPI-podien RAM-muistia.

---

## **6. Esityskerros (Adaptive BFF - Flutter)**

1. **Riverpod Mutaatiot ja Koodigeneroitu Reaktiivisuus:** Tilanhallinta rakentuu Riverpod 3.0 (Notifier, AsyncNotifier) varaan hyödyntäen koodigenerointia (`@riverpod`). Optimistiset UI-päivitykset (Loading Statet) pakotetaan vahvasti tyypitetyillä `Mutation<void>` -funktioilla, kieltäen tunkkaiset lokaalit `_isLoading` -liput kokonaan.
2. **Litteä MVC ja Isolate-Parsinta (Main Thread Protection):** Renderöinti ja graafit perustuvat ainoastaan yksinkertaiseen litteään `ReportDataDTO`:hon (The De-Generator Mandaatti, SDUI on poistettu). Koska RAG-raporttien JSONit ovat valtavia, niiden Pydantic DTO kuorinta (deserialisaatio) siirretään ehdottomasti Dartin **`Isolate.run()`** -taustasäikeeseen. Tämä estää käyttöliittymän jäätymiset (Main Thread Jank) kokonaisuudessaan.
3. **Signal & Fetch (The Payload Trap -esto):** Raskasta Lukumallia ei koskaan työnnetä SSE-putken kautta (Server-Sent Events) tukkimaan verkkokaistaa. SSE välittää ainoastaan ohuita tilamuutoksia ja versiotunnisteita (Deltas & `trace_version`). Vasta kun SSE-ping merkitsee askeleen valmiiksi, Frontend noutaa raskaamman `ReportDataDTO`:n erillisellä asynkronisella HTTP GET -haulla (Heavy Fetch).
4. **Hybridiparillinen Datanhallinta (Freezed & SafeCast):** Ydintila parsitaan tiukasti (`freezed`), mutta vahvasti dynaamiset näkymät nojaavat defensiiviseen **SafeCast**-parsintaan ja sokaiseviin `SizedBox.shrink()` turvatulppiin korruptoituneiden kenttien varalta (Graceful Degradation). Vika ei saa aiheuttaa "Red Screen of Death" -kaatumista mobiilissa.
5. **Actionable Hints (Global Error Handling V3):** Jos Backend katkaisee ajon (Fail-Fast RFC 7807 poikkeuksella esim. `TOOL_EXECUTION_FAILED`), Frontend ei kaadu vaan uudelleenreitittää sivun `GlobalErrorView V3` -komponenttiin. Se kääntää konerajatiedon ymmärrettäväksi ohjeeksi lokaalien `.arb` tiedostojen avulla ("Välivaiheen verkkoyhteys katkesi. [Jatka ajoa]"). "Jatka ajoa" -painike herättää backendin Rehydration-tilan ilman ajon nollausta.

---

## **7. Tulostusprofiilit ja Kääntäjä (The BFF Compiler)**

Järjestelmä erottaa kognitiivisen datan esittämisestä täydellisesti (Zero-Math Frontend). Yksittäistä työnkulkua voidaan välittömästi lukea erilaisten dynaamisten tulostusprofiilien (esim. Tiivistelmä, DataGrid/Excel) läpi ilman mutaatioita historiadataan.

### **7.1 The BFF Compiler (Geometrinen Degradaatio)**
Sielu lepää `blueprint.py` Kääntäjässä. Tämä rajapinta purkaa pyydetyn Output-profiilin, etsii vastaavuudet ajon tulosdatasta ja laskee näytön/PDF:n tarvitseman ViewModel-rakenteen lennosta.
1. **Collision Avoidance Hierarchy:** Kun kääntäjä kohtaa kaksi samannimistä komponenttia (esim. "Riski"), se kiipeää automaattisesti isä-puulistan (DAG) ylemmille tasoille eriyttääkseen nimen uniikiksi (esim. "Myynti - Riski"), taaten 100% uniikit Excel-sarakeotsikot ohjelmallisesti.
2. **Geometrinen Degradaatio (Geometric Degradation):** Jos tulostin odottaa `2D Matriisia`, mutta ohitetun askeleen takia data sisältää vain 1 akselin, Backendin Kääntäjä ei lähetä rikkinäistä 2D-koodia eteenpäin. Se suorittaa automaattisen degradaation, lakkauttaen paketin turvallisesti "1D Info Box" muotoon suojaten vikaherkkää Frontendiä kaatumisilta.

### **7.2 Pariteetti (Flutter vs. PDF-Worker)**
Tavoitteena on 100% pariteetti Flutter-näytön ja palvelimella generoidun PDF-raportin välillä. Molemmat moottorit saavat täsmälleen saman kääntäjän generoiman litteän `ReportDataDTO` -paketin (Backend-For-Frontend). Kun Flutter puskee kortteja laitteen ruudulle, PDF-Worker käyttää Jinja2 HTML/CSS -moottoria ja WeasyPrintiä palvelimella iteroidakseen saman asettelun puhtaana statiikkana. Matematiikka asuu vain Kääntäjässä.

---

## **8. The Tool Loop & Serverless MCP Integraatio (V2.6)**
Quorum käyttää ohjelmistosta riippumatonta asynkronista reititystä tiedonhaussa varmistaen determinismin. 
1. **The Gateway Array (Firebase/Cloud Run):** MCP (Model Context Protocol) Etsivät (The Tools) pyörivät joko täysin erillisissä Cloud Run -mikropalveluissa tai ulkoisissa SaaS-Soketeissa (Tavily AI). Quorum Backend kommunikoi näiden kanssa asynkronisella HTTP/SSE-tekstillä (`SystemConfigMCPGateways`).
2. **The Injector (Faktantarkistus):** Kun LLM valitsee "Tool Choicen" (Epistemic Uncertainty), moottori hakee faktan netistä tai RAG:ista ToolLoopin kautta. Faktan sisältävä `ToolMessage` isketään ohjelmallisesti LLM:n työmuistiin pakottaen BARS Matrix -arvioijat (Toisella Pydantic-pakotuskierroksella) antamaan arvosanan ulkoisen todistusaineiston (Evidence), ei subjektiivisen tiedon perusteella.
3. **FrozenContext Audit:** Kaikki verkkohaut ja palautetut raakatekstit tallennetaan välittömästi `MCPAuditTrace` -komponenttiin osana Execution-lokia (Forensic XAI Audit).

---

## **9. Tietokannan Tunnisteet ja Relaatiot (The Stripe Pattern)**
Välttääksemme hajautetun NoSQL-kannan ID-kollisiot (DocumentTooLarge) ja IDOR-tietoturvavuodot, kaikki kantaan asetettava data Quorumissa on alistettu tiukalle The Stripe Pattern -suojaukselle (`^([a-z]+)_[a-zA-Z0-9]{8,}$`).
1. **Opaque Primary Keys:** Yksikään tietokannan `id` (esim. `org_9a8b7c`, `wf_K8j2P`) ei saa koskaan sisältää ihmisluettavaa sanaa. Lukkolyöty salakirjoitus takaa "Zero Exceptions" Pydantic-validoinnin.
2. **The Slug Routing:** Ihmisluettavuus ja nätit URL-osoitteet hoituvat ainoastaan erillisellä `slug` -kentällä. Backend erottaa dynaamiset reititykset (Slug) täydellisesti erikseen turvatarkastuksia varten. Asiakas saa vaihtaa Slugiansa vapaasti rikkomatta sisäistä relaatiopuuta.
3. **Flat Referencing (Ei Embeddingiä):** Äärettömästi kasvavia datalistoja (Käyttäjät, Työnkulut, Ajot) ei ikinä upoteta (Embed) Isäntädokumentteihin. Ne viitataan täysin litistettyinä Document Reference -vierailla avaimilla (esim. `organization_id`).

---

## **10. Identiteetin ja Pääsynhallinta (Hybrid IAM & SaaS)**
Quorum nojaa vahvaan 2-tasoiseen SaaS-malliin (System-tason ylläpito vs. Eristetyt Tenant/Asiakas-organisaatiot).
1. **SaaS Isolaatio:** Asiakkailla on omat UUID-pohjaiset organisaationsa. Firestore kieltää tasollaan Backend/Frontend-kyselyt, joissa käyttäjän JWT Tokenin `organization_id` risteää dokumentin datan kanssa (Defense in Depth).
2. **Rooleihin Perustuva (RBAC):** Roolit nojaavat hierarkiaan: ROOT (Järjestelmänvaltias) > ADMIN (Asiakkaan Pääkäyttäjä) > MANAGER (Ai-Asiantuntija) > MEMBER (Ajaa työnkulkuja) > VIEWER (Lukulupa).
3. **Hybrid Auth:** Salasanojen ja sähköpostien turva, sekä Enterprise SSO (Entra ID / SAML) on kokonaan delegoitu Firebase Authille. Tietokanta säilyttää täällä ainoastaan valtuuttamisen (Authority/Roolit).
4. **Deep Copy -Kloonaus (GDPR & AI Act):** Asiakkaat eivät koskaan linkitä System-tason julkisiin AI-sääntöihin tuotantoajoissaan. Asiakkaan on aina kloonattava (`Kopioi Omaksi / Cascading Clone`) säännöt omaan Tenantiinsa. Tämä takaa AI Act -jäljitettävyyden: sääntöjen ohjeistukset eivät voi koskaan muuttua System-ylläpitäjän toimesta asiakkaan tietämättä.

---

## **11. Admin Studion UX Abstraktio (The Cascading Dropdowns)**
Koska Backend V2 puhuu ainoastaan Opaque Stripe ID -kryptografiaa (`steprule_d90f...`), Pääkäyttäjiltä ohjelmoidaan tämä monimutkaisuus piiloon käyttöliittymätasolla (Flutter).
1. **Reaaliaikainen Nimenkäännös (Nomenclature):** Työnkulkuja kootessa (DAG Builder) Admin UI agentit lukevat Riverpodin varastoiman koko puun rakenteen (State) läpi ja kääntävät Opaque ID:t visuaalisesti ihmisluettaviksi nimiksi.
2. **Data Path -Kaskadit:** Kun ylläpitäjä asettaa Blueprint Editorissa Matriisin lähteeksi aiemman työnkulun askeleen datan, UI paljastaa ainoastaan toisistaan riippuvaisia Pudotusvalikoita (Cascading Dropdowns) estäen manuaalisen typo-syöttämisen. UI "kääntää" säädöt The `$results.steprule_XYZ.output...` ohjelmointimuotoon vain JSON-tallennushetkellä.