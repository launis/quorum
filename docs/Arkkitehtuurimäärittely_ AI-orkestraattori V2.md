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
* **workflows (DAG Router):** Määrittelevät dynaamiset syötteet (`expected_inputs`). Työnkulun tärkein osa on `steps`-taulukko (Käännettynä uutena `StepRule` Node-instansseina), joka luo riippuvuusverkon eri solmujen välille.
  * **StepRule (The DAG Node):** Blueprintin ilmentymä tietyssä reitissä. Antaa mahdollisuuden hyödyntää samaa syyte-mallia samassa putkessa viidesti, jokaisella kerralla omilla **lokaaleilla, työnkulkukohtaisilla hookeillaan** (esim. `normalize_matrix_scores` tai `translation_hook_en`). Moottorin tehtävä on liimata ydin-hookit ja lokaalit hookit turvallisesti yhteen (Union-Combined Execution). Määrittelee myös lokaalin **datareitityksen** (`input_mappings`).

### KERROS 3: HISTORIA JA AUDITOINTI
* **executions (Ikuinen Jäädytys):** Tallentaa `raw_inputs` (käyttäjän syötteet), `frozen_context` (syväkopio säännöistä ajon hetkellä) ja `results` (Pydantic-validoitu tulos-JSON).

---

## **4. Syötteet, Roolit ja Datan Reititys (Semantic Data Flow)**

### **4.1. Odotetut syötteet (Expected Inputs) ja Universaali Reititys**
Käyttöliittymä lukee ohjelmallisesti `workflows`-dokumentin `expected_inputs`-taulukon ja piirtää vaaditut ohjaimet. Mukaansa jokainen syöte ottaa tiedon roolista (`ai_description`), joka injektoidaan raakadatan yläpuolelle (Universal Routing). 

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

### **5.1. Pydantic SSOT (Strict-DTO Protocol)**
Kaikki datasiirrot API-reitittimissä ja tietokannassa puskevat tiedon V2 Pydantic-validointimoottorin ja tiukan `extra="ignore"` säännön läpi estäen hallusinaatiot ja mallin väärennökset välittömästi HTTP 422 tai 500 virheellä (Fail Fast).

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

---

## **6. Esityskerros (Adaptive BFF - Flutter)**

Frontend (`client_app_v2`) on joustava, kognition ulkoistanut renderöintimoottori:

1. **Riverpod ja Koodigeneroitu Reaktiivisuus:** Tilanhallinta rakentuu Riverpod 3.0 (Notifier, AsyncNotifier) varaan hyödyntäen koodigenerointia (`@riverpod`), kieltäen `ChangeNotifier` -käytöt kokonaan.
2. **Hybridiparillinen Datanhallinta (Freezed vs. SafeCast):** Ydintila parsitaan tiukasti (`freezed`, `json_serializable`). Vahvasti dynaamiset BFF ViewModel -määritykset nojaavat defensiiviseen **SafeCast**-parsintaan, jotta ohjelmisto ei kaadu yhteen puuttuvaan avaimeen datassa (Red Screen Mitigation).
3. **Compound Widgets (Grounded UI):** Dynaamiset arviointislaiderit, the LLM-CoT näkymät ja teoriaväitteet rakennetaan Pydantic-datasta yhdeksi skaalautuvaksi widgetiksi jäännöksettömästi.
4. **Riverpod Hybrid Caching (SWR & TTL):** Käyttöliittymä ei lataa näkymiä toistuvasti alusta navigoinnissa. Lukunäkymät (kuten Dashboard-listat) hyödyntävät Stale-While-Revalidate (SWR) -mallia salamannopeaan navigointiin, ja syöttönäkymät (Lomakkeet) käyttävät lyhyttä Time-To-Live (TTL) -aikakatkaisua suojatakseen keskeneräisen datan väliaikaisesti ennen automaattista roskienkeruuta. (Lisätiedot: `flutterpromptohje.md`)