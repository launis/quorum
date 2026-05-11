## **Epic 48: Atomisaation Purku, Teoreettinen Ankkurointi ja Deterministinen Orkestrointi (SSOT)**

Tämä Epic korvaa V1-aikakauden epädeterministisen ja hallusinaatioalttiin "Deep Atomization" -mallin 100 % deterministisellä ja akateemisesti ankkuroidulla **Test-Driven Assertion (TDA)** -arkkitehtuurilla ("Single Source of Truth"). Koko järjestelmä siirtyy sumeasta arvailusta täsmälliseen, matemaattiseen ja todistettavaan validointiin. **Toteutus tehdään puhtaalta pöydältä (Clean Slate) - ei migraatioita, ei taaksepäin yhteensopivuutta.**

### **Vaihe 1: Arkkitehtuurin Siivous ja SSOT-Tietokantamalli (Clean Slate)**

> [!IMPORTANT]
> **No Legacy & Fail-Fast Mandate:** 
> V1-dataa tai vanhoja ajoja ei pelasteta. Kehityskannat tyhjennetään kokonaan. Kaikki Pydantic-mallit lukitaan välittömästi `extra='forbid'` tilaan. Jos data puuttuu, järjestelmä kaatuu. Fallback-koodit ovat kiellettyjä.

1. **atomization_cache.json tuhoaminen:**  
   * Tiedosto `backend_v2/seed/atomization_cache.json` poistetaan kokonaan repositoryn historiasta.  
2. **PromptAtomizer-luokan neutralointi (backend_v2/services/orchestrator/atomizer.py):**  
   * Poistetaan LLM-API-kutsut kokonaan. Logiikka korvataan puhtaalla O(1)-mäppäyksellä, joka lukee asiantuntijoiden tietokantaan asettamat TDA-väitteet ja luo niille efemeraaliset tunnisteet.
   * **Opaque Stripe ID Mandate:** Tunnisteiden on ehdottomasti noudatettava Opaque Stripe -muotoa (esim. `tda_a1b2c3d4`). Sekventiaaliset indeksit (kuten `tda_0`) ovat kiellettyjä. Koska dokumentit hajautetaan asynkronisiksi chunkeiksi, efemeraalisissa tunnisteissa on käytettävä kryptistä entropiaa (esim. nanoid tai lyhyt UUID), jotta vältytään ID-törmäyksiltä (Collision) aggregaatiovaiheessa.
3. **Tietokantaskeeman ja Pydantic-mallien muutos (models/v2_core.py):**  
   * Tuhotaan vanha `micro_atoms` -kenttä kokonaan kaikista malleista.  
   * Säilytetään matriisikohtainen `ai_description` (str), mutta sen rooli on jatkossa pelkkä XML-System Prompt / Agentin Persoona.  
   * Luodaan uusi alimalli `TDAAssertion`:  
     ```python
     class TDAAssertion(BaseModel, extra='forbid'):
         tda_id: str
         ai_rule_description: str
         inverse_evidence: bool  # True = etsitään rikettä (löytö = Failed)
         aggregation_mode: Literal['EXISTS', 'ALL_MUST_COMPLY']
         
         @model_validator(mode='after')
         def validate_math_logic(self):
             if self.inverse_evidence and self.aggregation_mode == 'ALL_MUST_COMPLY':
                 raise ValueError("Käänteinen sääntö (myrkyn etsintä) vaatii EHDOTTOMASTI 'EXISTS' -aggregaation. 'ALL_MUST_COMPLY' vaatisi absurdisti, että rike on toistuttava jokaisella sivulla.")
             return self
     ```
   * Muutetaan solun `Claim`-malli muotoon: `tda_assertions: list[TDAAssertion] = Field(min_length=1)`. 
   * **Staattinen Rakenne ja Validointi (`extra='forbid'`):** Kaikkiin Pydantic-malleihin (sekä ulkoisiin DTO- että sisäisiin SSOT Domain -malleihin) lisätään EHDOTTOMASTI `model_config = ConfigDict(extra='forbid')`. 
     * *Ristiriidan (Silent Scrubbing) Ratkaisu:* Ulkoisissa DTO-malleissa EI SAA käyttää `extra='ignore'` -tilaa. Jos LLM hallusinoi avaimen nimen (esim. kirjoittaa `found_evidence` oikean `evidence_found` sijaan), `ignore`-tila pudottaisi väärän avaimen hiljaisesti pois ja palauttaisi LLM:lle vain virheen "Missing field". Tämä tuhoaa LLM:n kyvyn korjata virheensä. `extra='forbid'` palauttaa täydellisen virheen: *"Missing field 'evidence_found'. Extra inputs are not permitted: 'found_evidence'"*, jolloin LLM:n `<PREVIOUS_SCHEMA_ERROR>` -retry-mekanismi näkee tarkalleen, minkä typografisen virheen se teki.
     * *Kaksivaiheinen Palomuuri (Two-Tier Firewall) ja Pydantic-korjausten kielto:* Pydanticin tehtävä ei ole "siivota" dataa, vaan tuomita se (Tuntematon data on rangaistava). Pydanticin sisällä tapahtuvat lennosta tehtävät nimiavaruuden korjaukset (kuten `alias`-määritykset tai `@model_validator(mode='before')` hallusinoitujen avaimien siivoamiseen) ovat EHDOTTOMASTI KIELLETTYJÄ, sillä ne rikkovat Fail-Fast -arkkitehtuurin.
       1. **Syntaksipalomuuri (Pydanticin ulkopuolella):** LLM:n Markdown-kääreet (esim. ```json) siivotaan puhtaalla Python Regex-esikäsittelyllä *ennen* Pydanticiin syöttämistä, jotta Rust-ydin (`jiter`) ei kaadu puhtaaseen `JSONDecodeError` -virheeseen.
       2. **Skeemapalomuuri (Pydantic V2):** Puhdas JSON syötetään `DTO.model_validate_json()` -metodille. Koska `extra='forbid'` on päällä, kaikki ylimääräinen data (kuten piilotetut `_thought_process` -injektiot) tai hallusinoidut avaimet kaatavat ohjelman välittömästi `ValidationError`:iin (Fail-Fast). Äänettömästi sivuutettuja tai korjattuja kenttiä ei suvaita. Jos LLM:n halutaan "ajattelevan ääneen", DTO-malliin on määriteltävä virallinen `reasoning_trace: str` -kenttä.
   * **Puhtaalta pöydältä (Clean Slate) -Mandaatti:** Koko arkkitehtuuri nojaa siihen, että data on täydellistä. Olemme ehdottomassa nollatoleranssissa vanhan tai epätäydellisen datan suhteen. Jos koodissa joudutaan kirjoittamaan fallback (esim. *"mitä jos kenttä puuttuu vanhasta tietokannasta"*), arkkitehtuuri on epäonnistunut. Migraatioskriptit ja taaksepäin yhteensopivuuden ylläpito ovat ehdottomasti kiellettyjä; ratkaisu on aina kantojen tyhjennys ja uudelleenseedaus (`seed_data.json`), jotta SSOT pysyy tahrattomana.
   * **Hydraatiomandaatti:** Ei `.get()`-fallbackeja. Kaikki saapuva JSON hydratoidaan Pydanticin `.model_validate()` -komennolla.
4. **run_seed.py kevennys ja nollaus:**  
   * Poistetaan LLM-clientin alustukset. Seeder lataa TDA-yhteensopivan puhtaan testidatan `seed_data.json` -tiedostosta suoraan kantaan ilman tekoälyä.

### **Vaihe 2: Teoreettinen Ankkurointi ja Käänteinen Logiikka**

Kaikki kriteerit ankkuroidaan suoraan akateemisiin teorioihin. Koska emme migroi vanhaa dataa, testidata (seed_data) luodaan manuaalisesti TDA-muotoon.

1. **Uusi seed_data.json:**  
   * Luo uusi, kompakti ja puhdas `seed_data.json`, jossa `micro_atoms` on korvattu `tda_assertions`-rakenteilla. Ei tarvetta iteratiivisille migraatioskripteille.
2. **Matriisitason PromptBlock.ai_description (System Prompt):**  
   * Käytetään yksinomaan staattisena System Promptina. Käytä Hybrid Promptingia (Markdown XML-tagien sisällä). Ohjeistus englanniksi.  
3. **Käänteisen Logiikan Injektio (PromptCompiler):**  
   * PromptCompiler lukee `inverse_evidence`-lipun. Jos se on tosi, injektoidaan LLM:lle tiukka sääntö: *"This is an inverse rule (Vice). If rule_satisfied = True (no issues found), evidence_found MUST be False and you must return an empty string \"\" for exact_quote. If rule_satisfied = False (violation found), evidence_found MUST be True and you MUST quote the exact violation."*

### **Vaihe 3: Hallusinaatiosuoja ja Fail-Fast Validointi**

1. **DTO-rakenteiden päivitys:**  
   * `is_true` kielletään. Tilalle: `rule_satisfied: bool` ja `evidence_found: bool`.
   * Lisätään tulos-malliin: `exact_quote: str`, `pre_quote_anchor: str`, `post_quote_anchor: str`, `reasoning_trace: str`.
   * **Ehdollinen Anti-Laziness (Cross-Field Validation):** Sokea `Field(min_length=1)` -sääntö on EHDOTTOMASTI KIELLETTY `exact_quote`-kentässä. Koska Map-Reduce -lohkomisessa useimmat sivut eivät sisällä etsittyä todistetta, mallin on saatava vastata tyhjällä merkkijonolla ilman rangaistusta. Validointi tehdään DTO:ssa ristiinvalidoivalla `@model_validator(mode='after')` -logiikalla:
     * *Jos `evidence_found == True`:* `exact_quote` EI SAA olla tyhjä. Muuten mallia rangaistaan sokeasti (Anti-Laziness).
     * *Jos `evidence_found == False`:* `exact_quote` ON OLTAVA tyhjä `""`. Jos malli palauttaa tekstiä vaikka väittää, ettei todistetta löydy, järjestelmä kaatuu loogiseen ristiriitaan (Anti-Hallucination).
2. **Deterministinen Vertailu & Kaskadi-Validointi (Fallback-Cascade):**  
   * **Separation of Concerns:** Semanttinen vertailu siirretään `AnchorValidationService`-luokkaan, joka on puhdas TDD-testattava palvelu ilman @model_validator-sivuvaikutuksia.
   * **Vaihe 1: Tekstin Normalisointi (EHDOTON):** Ennen vertailua sekä PDF-lähdeteksti että LLM-ankkuri ajetaan säälimättömän putken läpi (esim. regex `[^a-z0-9]`, lowercasing, `NFKC`-normalisointi). Leksikaalista vertailua ei koskaan tehdä suoraan likaiselle PDF-datalle.
   * **Vaihe 2: O(1) ja Jaettu Ankkurointi (RapidFuzz):** Etsitään `exact_quote`, tai `pre_quote_anchor` ja `post_quote_anchor` kireystason mukaisella `token_set_ratio`:lla normalisoidusta avaruudesta. *Poikkeuslupa (Performance Mandate):* Yleinen asennusympäristön C/C++ -laajennusten kielto (Zero-Trust) ohitetaan tässä tapauksessa täysin. `RapidFuzz` on järjestelmän suorituskyvyn ja skaalautuvuuden kannalta elintärkeä. Se on kertaluokkia nopeampi ja tehokkaampi kuin natiivi `difflib`, ja se on ainoa teollisen tason työkalu, joka pystyy käsittelemään tuhansia PDF-tekstirivejä reaaliajassa.
   * **VAIHE 3: SEMANTTINEN FALLBACK-KASKADI (TÄRKEÄ!):** Jos deterministinen merkkijonohaku epäonnistuu (mikä on yleistä monimutkaisessa OCR-datassa), **tulosta EI ohjata suoraan DLQ-tilaan**. Pelkän sokean kooditason Fail-Fastin sijaan laukaistaan salamannopea ja halpa LLM-kutsu (NLI-promptilla esim. GPT-4o-minille: *"Tarkoittaako väite A samaa kuin lause B tässä PDF-kontekstissa? Y/N"*). Tämä yhdistää TDA:n determinismin neuroverkkojen joustavuuteen, leikaten jopa 40 % turhista False Negative -hylkäyksistä. Jos tämä LLM-as-a-Judge -arvio epäonnistuu, vasta sitten tulos ohjataan säälimättä DLQ:hun.
     * *Arkkitehtuuristandardien noudattaminen:* Tämä malli seuraa vuoden 2026 alan standardia, joka tunnetaan nimellä **Model Cascading / LLM-as-a-Judge** (popularisoitu esim. DSPy-viitekehyksessä), missä nopeita/halpoja malleja käytetään "portinvartijoina" tai semanttisina luokittelijoina API-kulujen minimoimiseksi. Nämä LLM-kutsut on toteutettava täsmälleen `.agents/rules/05_llm_architecture.md` -sääntöjen mukaisesti: Kutsu tapahtuu Model Registryn kautta (`LLMClient.from_strategy()`), hyödyntää `LLMTaskExecutor.execute_structured_task()` -reititystä Pydantic V2 -takuilla, ja eristää syötteet `XML Fencing` -menetelmällä. Suorat OpenAI/Vertex-SDK-kutsut ovat kiellettyjä.
   * **Vaihe 4: Todistusaineiston Puhdistus:** `exact_quote` korvataan tietokantaan leikatulla `pdf_anchor_block`illa, jotta UI-pariteetti ja PDF-highlighter toimivat.

### **Vaihe 4: Dead Letter Queue (DLQ) ja Pisteiden Laskenta**

1. **Virheiden Tarkka Reititys:** 
   * `PydanticSyntaxError` -> LLM Retry (Syntaksivirheen korjaus).
   * `SemanticEvidenceError` -> Suora reititys DLQ:hun ilman retryä tai AI-päättelyä.
2. **Matemaattiset Säännöt ja Compliance Score:**  
   * **Dual-Metric -laskenta (Turvallinen Kelluva Jakaja):** 
     1. `Compliance Score` = `sum(Passed) / (total_atoms - dlq_count)`. DLQ-tilatut atomit **pudotetaan jakajasta**, jotta säilytetään puhdas semanttinen ero "En pysty lukemaan" (DLQ) ja "Tiedän, että tämä on laiton" (Failed) välillä. Kaikki arvosanalaskenta tehdään yksinomaan Backendin `scoring.py` -hookissa (SSOT).
     2. `System Confidence` = `(total_atoms - dlq_count) / total_atoms`. Tämä mittari toimii ehdottomana suojamuurina kelluvan jakajan mahdollista arvosanainflaatiota vastaan kertomalla, kuinka suuri osa luettiin luotettavasti.
   * **Dynaaminen Kova Portti:** Jos `System Confidence` putoaa alle 90 %, koko matriisi hylätään automaattisesti (`FAILED_UNSCORABLE`). Järjestelmä ei suostu antamaan pistettä, jos data on liian saastunutta.
   * **Rangaistusten poisto:** Passivity Penalty ja Post-Hoc -rangaistukset kytketään ohjelmallisesti pois päältä TDA-arkkitehtuurissa.
3. **Map-Reduce / Kolmitilalogiikka (Passed, Failed, DLQ):**  
   * **Stateless Workerit (Ei Context-serialisointia & File-based Context):** Arq-workereille ei koskaan välitetä raskaita Pydantic `ValidationInfo.context` -objekteja (esim. koko PDF-tekstiä tai tietokantasessioita) Rediksen yli. Tämä estää Rediksen RAM-muistin räjähtämisen (OOM). Worker saa vain primitiivejä (ID, indeksi, tiedostopolku).
     * *I/O-vyöryn esto (Thundering Herd):* Kun 50 rinnakkaista chunk-workeria noutaa PDF:n raakatekstin RapidFuzz-vertailua varten, ne EIVÄT tee API-kutsuja tietokantaan, EIVÄTKÄ ne lue tiedostoja natiivilla `open()`-kutsulla. Data noudetaan aina kooditasolla arkkitehtuurin virallisen asynkronisen `get_storage_driver().read_file(tiedostopolku)` -wrapperin kautta (joka lukee levylle jo aiemmin tallennetun `executions/{id}/inputs/...md` -forensiikkatiedoston). Vaikka kutsu menee `FileDriver`-abstraktion läpi, paikallisen backendin `LocalFileDriver` hyödyntää silti täysimääräisesti käyttöjärjestelmän "Page Cachea", jolloin sama 20 MB tiedosto tarjoillaan kymmenille workereille rinnakkain suoraan RAM-muistista, leikaten I/O-pullonkaulat nollaan.
   * **Asynkroninen Tila-akkumulaattori (Atominen Lua-skripti):** Koska PDF-dokumentit jaetaan kymmeniin itsenäisiin Arq-workereihin (chunks), workerit **eivät saa** aggregoida tuloksia lennossa relaatiokantaan (Race Condition -riski). Tilapäivitys (esim. Redis `HSET` ja completed-laskurin päivitys) tehdään **atomisella Lua-skriptillä**, jotta vain tasan yksi worker voi laukaista lopullisen reduktion.
   * **Synkroninen Reduktio (MatrixReducer):** Vasta kun Lua-skripti vahvistaa kaikkien `N` chunkin valmistuneen, erillinen `MatrixReducer` herätetään. Se suorittaa koko matriisin `ANY/ALL` -kolmitilalogiikan yhdessä deterministisessä, synkronisessa O(N) -operaatiossa.
   * **`EXISTS`:** `ANY(Passed) -> Passed`. `ALL(Failed) -> Failed`. Muuten `DLQ`.
   * **`ALL_MUST_COMPLY`:** Evaluointijärjestys on pakotettava absorboivan tilan vuoksi: 1. `ANY(Failed) -> Failed` (Löydös on absoluuttinen, ohittaa DLQ:n). 2. `ANY(DLQ) -> DLQ` (Ei voida taata, puuttuuko rike lopusta). 3. `ALL(Passed) -> Passed`.

### **Vaihe 5: Prompt-Topologia ja Prefix Caching**

1. **Ristiinvälimuistitus (Cross-Chunk Caching):**  
   * Topologia pakotetaan API-tason roolieristyksellä: Staattinen `[System Prompt]` ja `[TDA Rules]` lähetetään aina `"role": "system"` -lohkona, jotta ne välimuistittuvat 100 % kaikkiin workereihin. Vaihtuva `[<source_text>]` sijoitetaan myöhempään `"role": "user"` -lohkoon. Näin chunkin vaihtuminen ei riko välimuistipuuta (Prefix Tree).
2. **Laatu edellä Retryissä:**  
   * **Cachen säilyttävä Injektio (Tail-end):** Jos Pydantic kaatuu, `<PREVIOUS_SCHEMA_ERROR>` injektoidaan promptin **aivan loppuun** (User Promptin häntään ennen schema-pyyntöä). Tämä on absoluuttinen vaatimus. Promtin yläosa (System Prompt, TDA-säännöt ja massiivinen `<source_text>`) on pysyttävä bittitasolla muuttumattomana, jotta OpenAI:n ja Anthropicin Prefix Caching pysyy hengissä myös retry-luupeissa.

### **Vaihe 6: Frontend UI -päivitykset (Tier 2 Hardening)**

1. **Dart Freezed-mallit (Ei purkkaa):**  
   * Dart 3 Sealed Class (Union Type) pakottaa tarkan Pattern Matchingin. Optimistic UI:ta varten lisätään pakollinen `pending`-tila.
     ```dart
     @freezed
     sealed class TDAState with _$TDAState {
       const factory TDAState.pending() = _Pending;
       const factory TDAState.evaluated({required bool passed, required String displayQuote, required String rawAnchor}) = _Evaluated;
       const factory TDAState.dlq({required String userReason, required String backendTrace}) = _Dlq;
     }
     ```
   * Null-coalescing-operaattoreiden (`??`) käyttö parsinnassa on EHDOTTOMASTI KIELLETTY. `AppErrorBoundary` hoitaa odottamattomat poikkeukset fail-fastinä.
2. **UI-Läpinäkyvyys ja Tripartite Rendering Boundary (EI LASKENTAA UI:SSA):**
   * Matriisieditori päivitetään tukemaan `TDAAssertion` -listaa.
   * `dlq`-tila renderöidään harmaana, ja käyttäjälle näytetään tooltipillä suora backendin syy (`backendTrace`).
   * Backendin Jinja2 PDF-raportteihin lisätään sama harmaa tila (`{% if status == 'dlq' %}`).
   * **EHDOTON KIELTO:** Pistelaskentaa ei koskaan tehdä Riverpodissa tai Dart-malleissa. DLQ-jakajan vähennykset, rangaistukset ja loppumatematiikka lasketaan yksinomaan Backendin `scoring.py` -hookissa. Frontend on vain tyhmä renderöijä: se vastaanottaa `ReportDataDTO`:ssa valmiit `raw_score`, `normalized_score` ja `system_confidence` -arvot ja ainoastaan näyttää ne. Mitään laskentaa ei tapahdu `scoring.py`:n ulkopuolella.

### **7. Definition of Done**

* **Arkkitehtuuridokumentaation Päivitys:** `04_directory_reference.md` ja muut keskeiset dokumentit on päivitetty heijastamaan TDA-muutosta.
* **Kehityskannan Nollaus:** Vanhat kannat tuhottu, asennettu uusi puhdas TDA-yhteensopiva `seed_data.json`.
* **Yksikkötestit (>90%):** `AnchorValidationService` TDD-testattu ilman LLM-verkkoa. Pydantic-malleissa on kovat lukot (`extra='forbid'`), aggregaatiot on testattu. DLQ-rutinointi on aukoton.  
* **Puhdas Pöytä:** Ei yhtään vanhaa V1-datamigraatioskriptiä tai UI-fallbackia jätetty eloon.
* **Sääntöihin ankkurointi:** Kaikki uudet LLM-kutsut on toteutettava täsmälleen `.agents/rules/05_llm_architecture.md` -sääntöjen mukaisesti, mikä antaa kehittäjille selkeän raamin.