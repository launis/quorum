## **Epic 48: Atomisaation Purku, Teoreettinen Ankkurointi ja Deterministinen Orkestrointi (SSOT)**

Tämä Epic korvaa V1-aikakauden epädeterministisen ja hallusinaatioalttiin "Deep Atomization" \-mallin 100 % deterministisellä ja akateemisesti ankkuroidulla **Test-Driven Assertion (TDA)** \-arkkitehtuurilla ("Single Source of Truth"). Koko järjestelmä siirtyy sumeasta arvailusta täsmälliseen, matemaattiseen ja todistettavaan validointiin. Kaikki taaksepäin yhteensopivuutta vaativa legacy-koodi tuhotaan armotta.

### **Vaihe 1: Arkkitehtuurin Siivous ja SSOT-Tietokantamalli (Dead Code Removal)**

> [!WARNING]
> **Kananmuna vai Kana -ongelma (CQRS-Datamigraatio):** 
> Älä muuta ydinmalleja sokeasti tiukoiksi! Jos poistat `micro_atoms`-kentät ja isket `extra='forbid'` lukumalleihin ensin, Vaiheen 2 migraatioskripti (ja FastAPI-sovellus) kaatuu välittömästi `ValidationError`-poikkeuksiin, eikä pysty lukemaan vanhaa kantaa.
> **Ratkaisu (CQRS-erottelu):** 
> 1. Aseta LLM-tulostemalleille ja tietokannan **kirjoitusmalleille** välittömästi `extra='forbid'` uusien saasteiden estämiseksi.
> 2. Pidä tietokannan **lukumallit** (Read Models) tilapäisesti tilassa `extra='allow'` ja poista niistä `micro_atoms`-kenttä. Näin malli ei kaadu, ja migraatioskripti löytää yhä vanhan datan luokan `__pydantic_extra__` -sanakirjasta.
> 3. Vasta kun migraatio on 100 % valmis ja uusi kanta tuotannossa, lukumallit kiristetään `extra='forbid'` -tilaan.

Järjestelmä puhdistetaan dynaamisista atomisaatio-kutsuista. Infrastruktuuri pystytetään välittömästi ilman LLM-latensseja.

1. **atomization\_cache.json tuhoaminen:**  
   * Tiedosto backend\_v2/seed/atomization\_cache.json poistetaan kokonaan repositoryn historiasta.  
2. **PromptAtomizer-luokan neutralointi (backend\_v2/services/orchestrator/atomizer.py):**  
   * Poistetaan LLM-API-kutsut kokonaan. Logiikka korvataan puhtaalla O(1)-mäppäyksellä, joka lukee asiantuntijoiden tietokantaan asettamat TDA-väitteet ja luo niille efemeraaliset (tilapäiset) ajonaikaiset tunnisteet (esim. tda\_0, tda\_1). V1-aikaiset MD5-tiivisteet ovat kiellettyjä hallusinaatioriskien ja hitauden vuoksi.  
3. **Tietokantaskeeman ja Pydantic-mallien muutos (models/v2\_core.py):**  
   * Tuhotaan vanha micro\_atoms \-kenttä kokonaan kaikista malleista.  
   * Säilytetään matriisikohtainen ai\_description (str), mutta sen rooli on jatkossa pelkkä XML-System Prompt / Agentin Persoona.  
   * Luodaan uusi alimalli TDAAssertion:  
     Python  
     class TDAAssertion(BaseModel):  
         description: str  \# Varsinainen kriteeri (esim. "Teksti esittää numeerisen tavoitteen")  
         inverse\_evidence: bool \= False  \# Kääntää lainauksen vaatimuksen

   * Muutetaan solun Claim-malli muotoon: tda\_assertions: list\[TDAAssertion\] \= Field(min\_length=1). Tämä on järjestelmän uusi SSOT.  
   * **Pakottavat säännöt (@[c:\src\quorum\.agents\rules\01-python-backend.md]):** Pydantic-malleihin ei saa lisätä `@model_validator(mode="before")` -funktioita tai löysiä tyyppejä vanhan V1-datan kiertämiseksi (`strict_pydantic_v2_rust` & `zero_legacy_fallback_hacks`).
   * **CQRS ja extra-parametrit (Siirtymäajan hallinta):**
     * **LLM I/O ja Kirjoitusmallit:** `model_config = ConfigDict(extra='forbid', strict=True)`. Estää uuden hallusinoidun tai V1-aikaisen datan päätymisen järjestelmään.
     * **Lukumallit:** `model_config = ConfigDict(extra='allow')`. Sallii vanhan datan ohittamisen kaatumatta ja tallentaa tuntemattomat kentät (kuten `micro_atoms`) luokan `__pydantic_extra__` -sanakirjaan, jotta migraatioskripti voi lukea ne ja muuttaa uusiksi atomeiksi.
   * **Hydraatiomandaatti (@[c:\src\quorum\.agents\rules\01-python-backend.md]):** Älä KOSKAAN käytä backendissä Pythonin `dict.get()`-metodia vanhojen rakenteiden kiertämiseksi (`fail_fast_hydration_mandate`). Kaikki saapuva JSON-data on hydratoitava VÄLITTÖMÄSTI Pydanticin `.model_validate()` -komennolla.
4. **run\_seed.py kevennys ja nollaus (@[c:\src\quorum\.agents\rules\03_seed_vault.md]):**  
   * Poistetaan LLM-clientin ja välimuistin alustukset Seederistä. Seeder lataa kantaan uuden Pydantic-mallin mukaista dataa seed\_data.json \-tiedostosta sekunneissa ilman verkkokutsuja.
5. **enums.py optimointi (Suorituskyky):**
   * Päivitetään `SystemConcurrency`-arvot (esim. `MAX_CONCURRENT_LLM_STEPS = 5`, `LLM_MAX_RETRIES = 3`, `LLM_DEFAULT_TIMEOUT_SECONDS = 180`), jotta raskaista atomisointiprompteista vapautunut LLM-kapasiteetti voidaan hyödyntää täysimääräisenä ajoja nopeuttamalla.

### **Vaihe 2: Teoreettinen Ankkurointi ja Prompt Compilerin Äly**

Kaikki kriteerit irrotetaan LLM:n "musta tuntuu" \-logiikasta ja ankkuroidaan suoraan akateemisiin teorioihin.

1. **Uusi seed_data.json ja Positivity Mandate (Kertaluonteinen Migraatio):**  
   * Tietokanta saatetaan "ajovalmiiksi" erillisellä offline-migraatioskriptillä (`migrate_seed_to_tda.py`), joka lukee nykyisen V1-tyylisen `seed_data.json` -tiedoston.
   * **Theory Grounding (Web Search / MCP):** Skripti ohjeistetaan lukemaan matriisin `theory_grounding.source_url` -lähde (esim. Toulmin/Bloom). Vanhat yhdistelmäsäännöt (Compound) pilkotaan tiukoiksi, atomaarisiksi `TDAAssertion`-olioiksi peilaten näitä akateemisia alkuperäismääritelmiä.
   * **Arkkitehtuurisääntö (@[c:\src\quorum\.agents\rules\05_llm_architecture.md]):** Skriptin tekoälykutsua varten ei saa käyttää `run_chat()`-metodia tai regex-parsimista (`llm_structured_execution_mandate`). Strukturoitu generointi on AINA tehtävä API:n natiivin JSON-rajoitteen kautta (esim. `LLMTaskExecutor.execute_structured_task()`), palauttaen suoraan Pydantic `List[TDAAssertion]`.
   * **Anti-Laziness & Zero-Compromise -suojat (Kertaluonteisen ajon maksimointi):** 
     Koska kyseessä on kertaluonteinen offline-ajo, tokenien kulumisella tai ajon kestolla ei ole mitään merkitystä. Keskitymme 100 % akateemiseen laatuun ja determinismiin.
     1. **Raskaimman strategian pakotus (`direct_sdk_calls` & Model Registry):** Tekoälyä ei saa kutsua suorilla SDK-kutsuilla tai kovakoodatuilla mallinimillä (esim. `gpt-4o`). Skriptin on ladattava Model Registryn älykkäin strategia (`await LLMClient.from_strategy("reasoning", repo)`). Halvemman `"fast"`-strategian käyttö on kielletty.
     2. **Iteratiivisuus (Ei Batch-ajoa):** Skripti käsittelee täsmälleen yhden solun (Claim) kerrallaan omana API-kutsunaan varmistaen maksimaalisen fokusoinnin ja estäen Lost-in-the-Middle -ilmiön.
     3. **Generator-Critic-Refiner -luuppi (Reflektio):** Emme tyydy tekoälyn ensimmäiseen vastaukseen. Kullekin solulle suoritetaan itsekritiikkiluuppi `LLMTaskExecutor`-palvelun sisällä:
        * *Generator:* Lukee akateemisen lähteen koko syvyydessään ja luo TDA-ehdotukset.
        * *Critic (Zero-Trust Auditor):* Etsii säälimättä porsaanreikiä, subjektiivisuutta tai epämääräisyyksiä kriteereistä (esim. onko sana "relevantti" liian sumea arvioitavaksi).
        * *Refiner:* Korjaa TDA-väitteet täysin matemaattisen tarkoiksi ja aukottomiksi.
     4. **Pakotettu Chain of Thought (CoT):** Ennen lopullista TDA-listaa LLM joutuu kirjoittamaan Pydantic-tulosmalliin kentän `theory_mapping_rationale: str`, jossa se perustelee tieteellisesti uuden kriteerin.
     5. **Katkossietoisuus (Checkpointing):** Koska raskaiden mallien iterointi kestää tunteja, migraatioskriptiin on implementoitava tilaa tallentava Checkpointing-mekanismi (esim. lokaaliin SQLite-kantaan tai väliaikaiseen JSON-tiedostoon). Verkkovirheen tai kaatumisen sattuessa ajo jatkuu saumattomasti seuraavasta käsittelemättömästä solusta, jolloin satojen eurojen API-kustannuksia ei menetetä.
   * **Sanitaatio:** Skripti tuhoaa lopullisesti vanhat dynaamiset ohjeet (`micro_atoms` ja solutason `ai_description`) JSON-datasta.
2. **Matriisitason PromptBlock.ai_description (System Prompt):**  
   * Eristetään matriisin tason `ai_description` (esim. "ROLE: ZERO-TRUST AUDITOR..."). Se toimii jatkossa yksinomaan staattisena System Promptina agentin persoonan luomiseksi.
   * **Pakottavat säännöt (@[c:\src\quorum\.agents\rules\05_llm_architecture.md]):** Promptin on oltava yksinomaan englanniksi (kielellisen rapautumisen estämiseksi) ja sen on käytettävä Hybrid Promptingia (Markdownia XML-tagien sisällä) (`native_language_system_prompts` & `hybrid_prompting_mandate`).
   * Koska ohje on 100 % staattinen, hyödynnämme **Prompt Caching** -ominaisuuksia maksimoimaan kustannussäästöt. Dynaaminen lähdeteksti injektoidaan aina User-viestin `<source_text>`-blokkiin.  
3. **Käänteisen Logiikan Injektio (PromptCompiler):**  
   * PromptCompiler (backend\_v2/services/orchestrator/prompt\_compiler.py) lukee inverse\_evidence-lipun TDA-kohtaisesti.  
   * Jos se on tosi, compiler injektoi suoraan LLM:n promptiin ohjeen säännön tulkitsemiseksi: *"This is an inverse rule (Vice). If rule_satisfied = True (no issues found), evidence_found MUST be False and you must return EMPTY quotes []. If rule_satisfied = False (violation found), evidence_found MUST be True and you MUST quote the exact violation."*

### **Vaihe 3: Hallusinaatiosuoja ja Validointi (Industrial Grade Resilience)**

1. **DTO-rakenteiden päivitys ja Kognitiivisen Solmun Purku:**  
   * **Nimeämiskäytäntö (`is_true` kieltäminen):** Tekoäly menee sekaisin tuplanegatiivisista ("Löysitkö virheen? True/False"). Siksi `is_true`-kenttä kielletään DTO:ssa. Käytämme yksiselitteisiä kenttiä: `rule_satisfied: bool` (Läpäisikö dokumentti tämän säännön puhtaasti?) ja `evidence_found: bool` (Löytyikö kriteerin mukainen lainaus?).
   * **Kontekstuaalinen Ankkurointi (Uusi DTO):** Pelkän irrallisen lainauksen sijaan LLM pakotetaan ankkuroimaan löydöksensä tekstiin. Lisätään tulos-malliin pakolliset kentät:
     * `exact_quote: str` (Varsinainen todiste)
     * `pre_quote_anchor` (n. 4-5 sanaa lainausta edeltävästä tekstistä)
     * `post_quote_anchor` (n. 4-5 sanaa lainausta seuraavasta tekstistä)
     * `reasoning_trace: str` (Chain of Thought).
   * **Promptin sääntö:** *"Provide the exact quote. Then provide two separate anchors: 'pre_quote_anchor' (approx 4-5 words exactly preceding the quote) and 'post_quote_anchor' (approx 4-5 words exactly following the quote). This helps locate the quote across page breaks."*
   * **Dynaamiset Output Extensions (Staattinen DTO-arkkitehtuuri):** Pydanticin `create_model()` -metodin käyttö dynaamisten luokkien luomiseksi "lennosta" on EHDOTTOMASTI KIELLETTY. Se tuhoaa Pythonin suorituskyvyn, estää Dartin staattisen tyypityksen ja rikkoo OpenAI:n Structured Outputs -välimuistin. Käytämme sen sijaan staattista tietuetta: `extensions: Dict[ExtensionType, str]` (jossa `ExtensionType` on ennalta määritetty Enum). PromptCompiler ohjeistaa tekoälyä, mitkä Enumin avaimet vaaditaan kyseisessä ajossa.
2. **Käänteiset säännöt (inverse\_evidence) ja Nollasääntö:**  
   * **Normaali hyve (`inverse_evidence == False`):** `rule_satisfied == True` VAATII, että `evidence_found == True` ja `exact_quote` ei ole tyhjä. (Hyve löytyi).
   * **Negatiivinen pahe (`inverse_evidence == True`):** `rule_satisfied == True` VAATII, että `evidence_found == False` ja `exact_quote` on tyhjä `""`. (Pahetta ei löytynyt = Sääntö läpäisty = Dokumentti on puhdas).
3. **Deterministinen Vertailu & Kieliagnostinen Semanttinen Lukko (Fail-Fast Kompromissi):**  
   * **Arkkitehtoninen Linjaus (Event Loopin Suojelu):** Raskasta merkkijonovertailua ei KOSKAAN saa suorittaa Pydanticin sisällä. Pydanticin `@model_validator` on asynkronisessa Pythonissa synkroninen, ja raskaiden operaatioiden ajaminen sen sisällä jäädyttää palvelimen Event Loopin (GIL Starvation). Myös raskaan `source_text`-raakatekstin injektoiminen `ValidationInfo.context`-objektiin on kielletty muistivuotoriskien ja Redis-jonon tukkeutumisen estämiseksi.
   * **Separation of Concerns (Palvelukerros):** 
     1. Pydantic (`TDAOutput.model_validate(json_data)`) tekee vain salamannopean rakenteellisen validoinnin C/Rust-tasolla (Ovatko kentät olemassa ja oikean tyyppisiä?).
     2. Semanttinen ja matemaattinen vertailu siirretään erilliseen asynkroniseen palveluun (esim. `fuzz_anchor_service`).
     3. Haku heitetään taustasäikeeseen: `validated_dto = await asyncio.to_thread(fuzz_anchor_service.validate, dto, markdown_chunk)`. Tämä vapauttaa FastAPIn ja Arq-workerin.
   * **PyMuPDF4LLM ja Markdown-todellisuus (Ei brutaalia normalisointia):** Koska syöte on `pymupdf4llm`:n tuottamaa puhdasta Markdownia, ei roskaista kuva-OCR:ää, sanojen sisäistä kohinaa on vähän. Makrotason kohinaa (sivunvaihdot, ylätunnisteet, Markdown-taulukot lauseiden välissä) sen sijaan on paljon. **Brutaali merkkijonojen yhteenpuristaminen (esim. `re.sub(r'[^a-z]')`) on EHDOTTOMASTI KIELLETTY**, koska se tuhoaa Markdown-rakenteen navigointikyvyn ja epäonnistuu täydellisesti sivunvaihdoissa.
   * **Vaihe 1: O(1) Salamannopea yritys (Pääreitti):** Jos LLM palautti `exact_quote`-kenttään tismalleen Markdownissa olevan merkkijonon. Palvelu tarkistaa lokaalisti: `if exact_quote in markdown_text:`. Prosessi päättyy välittömästi (0.1 ms).
   * **Vaihe 2: Jaettu Ankkurointi (Bi-Directional Anchoring):** Jos O(1) epäonnistuu, oletetaan, että lause ylittää sivunvaihdon tai sisältää Markdown-rakenteita, jotka LLM siivosi pois. Emme hae yhtenäistä sumeaa blokkia.
     * Koodi etsii Markdown-tekstistä `pre_quote_anchor` -kohdan puhtaalla `.find()` -metodilla (tai kevyellä säätövaralla).
     * Koodi etsii `post_quote_anchor` -kohdan.
     * **Jos ankkureita ei löydy:** Palvelu nostaa poikkeuksen (`SemanticEvidenceError`). LLM hallusinoi konseptin tai tekstin.
   * **Vaihe 3: Semanttinen Lukko ja "Saksiminen" (Ei mekaanista diffausta):** Jos molemmat ankkurit löytyvät inhimillisen matkan päästä toisistaan, **emme tee enää mitään mekaanista merkkijonovertailua (difflib/avainsanat)**. LLM on jo toiminut semanttisena tuomarina ja todistanut löytönsä ankkureilla.
     * Leikataan ankkurien väliin jäävä Markdown-raakateksti irti omaksi muuttujakseen (`pdf_anchor_block`). Tämä lohko voi sisältää sisällään sivunumeroita, `\n\n### Sivu 4\n\n` -merkintöjä tai taulukoita.
     * Osuma hyväksytään välittömästi. Oletamme, että LLM tiivisti, korjasi typoja tai muutti sijamuotoja alkuperäisessä `exact_quote`-vastauksessaan (mikä aiheuttaisi väärän DLQ-hylkäyksen mekaanisessa difflibissä), mutta ankkurit todistavat sen kohdistaneen huomionsa oikeaan PDF-lauseeseen.
   * **Vaihe 4: Todistusaineiston Puhdistus (UI-pariteetti):** Jos osuma hyväksytään ankkurien avulla, emme saa koskaan tallentaa tietokantaan tekoälyn siistimää merkkijonoa.
     * Palvelu ylikirjoittaa DTO-mallin `dto.exact_quote` -kentän tällä roskaisella `pdf_anchor_block` -muuttujalla (joka on leikattu ankkurien välistä).
     * **Lopputulos:** Järjestelmä ymmärsi sisällön semanttisesti oikein, mutta säästi tietokantaan täsmälleen sen Markdown-pätkän, joka lukee PDF:ssä. UI:n PDF-Highlighter pystyy korostamaan tekstin saumattomasti jopa sivunvaihtojen yli.
   * **Miksi tämä arkkitehtuuri on ylivoimainen?**
     * **Immuuni sivunvaihdoille:** Jaettu ankkuri ("Bi-Directional") ohittaa alatunnisteet ja Markdown-taulukot lauseiden välissä.
     * **Salamannopea:** Koko haku perustuu ensisijaisesti O(1) `.find()` -operaatioihin puhtaassa Markdownissa, ilman hidasta sumeaa logiikkaa tai GIL-lukituksia.
     * **Hallusinaatio-immuuni:** Jos alku- ja loppuankkuria ei löydy, tekoäly on keksinyt asian.
   * **Audit-loki (Hallusinaatio-seuranta):** Jos osuma hyväksytään Jaetulla ankkurilla, alkuperäinen Markdown-roskainen teksti ja LLM-lainaus tallennetaan telemetriaan. Näin voimme todentaa jälkikäteen toimivuutta.
   * **Validation Loop of Doom -suoja (Strict Retry Policy):** LLM:n uudelleenyritys (Retry) on kallis ja vaarallinen operaatio, joka provosoi hallusinaatioita, jos LLM ei ymmärrä virheen syytä. Epic kieltää mekaanisten virheiden syöttämisen semanttiselle mallille.
     * **Sallittu Retry (Syntaksivirheet):** Jos Pydantic heittää `ValidationError`-poikkeuksen (esim. puuttuva avain, väärä tietotyyppi, rikkinäinen JSON), `LLMTaskExecutor` ottaa sen kiinni ja syöttää virheen takaisin LLM:lle (`<PREVIOUS_SCHEMA_ERROR>`). LLM osaa korjata JSON-syntaksinsa luotettavasti.
     * **Kielletty Retry (Semantiikka ja Kohdistus):** Jos asynkroninen palvelu hylkää tuloksen (esim. ankkureita ei löydy, tai semanttinen lukko epäonnistuu), tulosta **EI KOSKAAN** syötetä takaisin LLM:lle. Oletuksena on PDF:n kontekstivaurio tai alkuperäinen hallusinaatio, jota ei korjata arvailemalla.
4. **Ohjelmallinen DLQ-Reititys ja Esivalidointi (Fail-Fast):**  
   * **Pre-LLM Short-Circuit (Esivalidointi):** Ennen kuin `LLMTaskExecutor` tekee ainuttakaan kallista API-kutsua, se tarkistaa Markdown-chunkin laadun ohjelmallisesti (esim. `if len([w for w in chunk_text.split() if w.isalpha()]) < 15:`). Jos sivu koostuu vain erikoismerkeistä, taulukkoviivoista tai on tyhjä, koko chunk ohitetaan ja arvioinnit siirretään suoraan DLQ-tilaan. Tämä "portinvartija" säästää valtavasti turhia token-kuluja.
   * **Post-LLM Fail-Fast:** Kun kooditason palvelu nostaa semanttisen virheen (ankkurit puuttuvat), tekoälyä ei kutsuta uudelleen. Kriteeri ohjataan **välittömästi** DLQ-tilaan.
   * Tämä kaksitasoinen Fail-Fast estää tehokkaasti sekä lompakon palamisen roskadataan (Pre) että tekoälyn keksimät valheelliset lainaukset (Post).

### **Vaihe 4: Dead Letter Queue (DLQ) ja Matematiikka**

1. **TDA:n hylkääminen ja Strict Compliance (Ei pisteytysinflaatiota):**  
   * Jos asynkroninen palvelu hylkää osuman (esim. ankkureita ei löydy), kriteeri siirretään välittömästi DLQ-tilaan (`ValidationStatus.dlq`).
   * **Pisteiden Inflaation Kielto:** DLQ-statusta EI SAA poistaa nimittäjästä. Jos nimittäjää pienennetään lukuvirheiden myötä, järjestelmä antaa valheellisen hyviä arvosanoja (Score Inflation) dokumenteista, joista ei saatu selvää. Nimittäjä on AINA matriisin sääntöjen kiinteä alkuperäiskokonaismäärä.
   * **Compliance Score (Tiukka arvosana):** `sum(True) / total_atoms`. (Esim. jos 3 sääntöä 10:stä joutuu DLQ-tilaan skannerivirheen vuoksi ja loput 7 läpäistään puhtaasti, arvosana on 70 %, EI 100 %).
2. **Kaksiosainen Metriikka (Confidence Index):**  
   * Koska tiukka `Compliance Score` rokottaa loppuarvosanaa myös fyysisten lukuvirheiden osalta, arkkitehtuurin on erotettava "Liiketoiminnallinen sääntöjen noudattaminen" ja "Järjestelmän tekninen kyvykkyys lukea tiedosto" toisistaan, jotta käyttöliittymä (UX) ja auditoitavuus pysyvät selkeinä.
   * **Confidence Index (Luottamusindeksi):** `(total_atoms - dlq_count) / total_atoms`. Tämä luku paljastetaan rinnakkaisena UX-elementtinä, kertoen suoraan kuinka suuren osan dokumentista koodi kykeni todentamaan.
   * **Luottamusrajan yksinkertaistus (Thresholding):** Aiempi vaikeaselkoinen dlq_count-katkoraja muutetaan suoraan indeksipohjaiseksi järjestelmätason hylkäykseksi: `if confidence_index < 0.70: return ScoringResult(score=None, status="FAILED_UNSCORABLE")`. DLQ ei koskaan ole porsaanreikä 100 % puhtaudelle.
3. **Map-Reduce / Chunk-Aggregointi (Kolmitilalogiikka):**  
   * Jos dokumentti on pilkottu osiin, yksinkertainen boolean `ANY()` -logiikka on EHDOTTOMASTI KIELLETTY, sillä se aiheuttaa "False Purity" -vaaran (sallii dokumentin läpäisyn, jos rike oli lukukelvottomassa DLQ-osassa). Orkestraattorin on käytettävä matemaattisesti rehellistä kolmitilalogiikkaa (True, False, DLQ) yhdistämisessä:
     * **Käänteiset säännöt (Etsitään kiellettyä / Universal):**
       * Jos `ANY(Violation)` $\rightarrow$ Koko dokumentin tulos on **False** (Rike / Hylätty).
       * Jos ei rikeitä, mutta `ANY(DLQ)` $\rightarrow$ Koko dokumentin tulos on **DLQ** (Turvallisuutta ei voida taata, koska rike voi piillä lukematta jääneessä osassa).
       * Vain jos `ALL(Clean)` $\rightarrow$ Koko dokumentin tulos on **True** (Todistetusti puhdas).
     * **Normaalit säännöt (Etsitään pakollista / Existential):**
       * Jos `ANY(Hit)` $\rightarrow$ Koko dokumentin tulos on **True** (Osuma löytyi).
       * Jos ei osumia, mutta `ANY(DLQ)` $\rightarrow$ Koko dokumentin tulos on **DLQ** (Ei voida todistaa puuttuvaksi, osuma voi piillä DLQ-osassa).
       * Vain jos `ALL(Miss)` $\rightarrow$ Koko dokumentin tulos on **False** (Todistetusti puuttuu).
4. **DAG-tason suojat:**  
   * Jos pisteytysmoottori palauttaa FAILED\_UNSCORABLE, Orkestraattorin on merkittävä koko arvioinnin tila luokkaan FATAL\_SOURCE\_DATA ja lopetettava prosessointi välittömästi.
5. **Synteesimoottorin yhteensopivuus (Epic 50):**
   * Jos järjestelmä tekee "Row Explanation Synthesis" -ajoja, synteesimoottorin promptille on opetettava ohittamaan (Skip) DLQ-tilassa olevat kriteerit. Järjestelmä ei saa yrittää kirjoittaa hienoa selitystä asialle, jota ei voitu edes arvioida.

### **Vaihe 5: Prompt-Topologia ja Prefix Caching (API-optimointi, @[c:\src\quorum\.agents\rules\05_llm_architecture.md])**

Jotta järjestelmän tuotantokustannukset (Unit Economics) pysyvät hallinnassa, PromptCompilerin on noudatettava Anthropicin ja OpenAI:n vaatimaa tiukkaa "Cache-First" XML-topologiaa. Prompt Caching (Prefix Caching) on Trie-pohjainen algoritmi, joka rikkoutuu välittömästi (Cache Miss) ensimmäisestä muuttuvasta merkistä.

1. **Ristiinvälimuistitus (Cross-Chunk Caching):**  
   * Raskasta lähdetekstiä (`<source_text>`) ei koskaan saa laittaa promptin alkuun ennen ohjeita.
   * Topologia pakotetaan muotoon: `[System Prompt]` -> `[TDA Rules]` -> `[<source_text>]`.
   * **Miksi:** Kun pitkä PDF on paloiteltu kymmeneen asynkroniseen chunkkiin, `System Prompt` ja `TDA Rules` pysyvät identtisinä jokaisessa API-kutsussa. LLM välimuistittaa säännöt kerran, jolloin kaikki kymmenen Arq-workeria saavat sääntöjen osalta salamannopean "Cache Hitin". Lisäksi sääntöjen näkeminen ennen massiivista tekstiä parantaa LLM:n attention-mekanismin tarkkuutta (Priming).
2. **Retry-välimuistitus ja Tulimuuri (Cache Breakpoint):**  
   * **Kielto:** `<PREVIOUS_SCHEMA_ERROR>` tai muita dynaamisia tila-injektioita EI KOSKAAN saa sijoittaa raskaan `source_text`-lähdetekstin yläpuolelle.
   * **Topologia:** Kaikki dynaaminen retry-data sijoitetaan aivan promptin loppuun, `source_text`-lohkon alle (tulimuurin taakse).
   * **Lopputulos:** Jos LLM tekee syntaksivirheen ja joudumme tekemään uudelleenyrityksen (Retry), LLM on jo välimuistittanut massiivisen PDF-tekstin edelliseltä kierrokselta. Se joutuu laskemaan (ja veloittamaan) vain sen pienen virheviestin, joka lisättiin promptin loppuun. Säästö on luokkaa 90–95 % per retry-kierros.

### **Vaihe 6: Frontend UI \-päivitykset (Tier 2 Hardening)**

1. **Dart Freezed-mallit (Algebraic Data Types):**  
   * Päivitetään mallit tukemaan uutta `TDAAssertion` -oliota ja sen listoja.  
   * **Pakottava sääntö (Kääntäjätason suoja):** Yksinkertaisten Enum-tilojen ja `null`-purkkaviritysten käyttö on KIELLETTY. Tilan on oltava Dart 3 Sealed Class (Union Type), mikä pakottaa kääntäjätasolla Exhaustive Pattern Matchingin.
   * **Esimerkkiarkkitehtuuri:**
     ```dart
     @freezed
     sealed class TDAState with _$TDAState {
       const factory TDAState.evaluated({required bool passed, required String quote}) = _Evaluated;
       const factory TDAState.dlq({required String reason}) = _Dlq;
     }
     ```
   * Näin ollen UI-komponenttien on pakko toteuttaa `.when()` tai `.map()` -metodi. Dartin kääntäjä heittää välittömästi kääntövirheen, jos kehittäjä unohtaa koodata DLQ-tilan erillisen harmaan kortin. Tämä eliminoi täydellisesti inhimilliset "False UI State" -ongelmat renderöinnissä.
2. **Pakottava sääntö (@[c:\src\quorum\.agents\rules\02_flutter_desktop.md]):**  
   * Null-coalescing-operaattoreiden (`?? []`) käyttö JSON-parsinnassa rakenteellisten virheiden piilottamiseksi on EHDOTTOMASTI KIELLETTY. Data-kerroksen pitää heittää kova poikkeus, jos API:n data on epävalidia. **Mutta UI-tasolla:** Odotetut DLQ-tilat hoidetaan kääntäjän pakottamalla `.when()`-mäppäyksellä, ja täysin odottamattomat JSON-poikkeukset napataan siistiin `ErrorBoundary`-widgettiin, joka näyttää rikkinäisen komponentin kohdalla harmaan "Data Corrupted" -laatikon.
3. **Matriisieditori:**  
   * Käyttöliittymä (`prompt_block_builder_view.dart`) päivitetään tukemaan dynaamista listaa TDAAssertion-kriteerejä ja `inverse_evidence` -valintaa.
4. **N/A (DLQ) renderöinti & PDF-pariteetti:**  
   * Raporttinäkymiin (`result_dashboard.dart` yms.) lisätään tuki `TDAState.dlq` -tuloksille `.when()`-logiikan kautta. Se näytetään harmaana ("Ei arvioitavissa lähteen laadun vuoksi").
   * **Jinja2 PDF-raportit (Backend):** Koska arkkitehtuurissa on tiukka UI/PDF-pariteettisääntö, Python-backendin Jinja2-raporttipohjiin (`.html` / `.svg`) on lisättävä vastaava ehto (`{% if status == 'dlq' %}`), jotta fyysiseen PDF-tulosteeseen piirtyy sama harmaa laatikko kuin ruudulle.

### **7\. Definition of Done**

* **Arkkitehtuuridokumentaation Päivitys:** Varmistetaan, että `c:\src\quorum\.agents\rules\04_directory_reference.md` ja `c:\src\quorum\docs\architecture\` -hakemiston dokumentit on päivitetty vastaamaan tätä Epicissä määriteltyä uutta, vahvistettua arkkitehtuuria (esim. Ternary Logic, Dual-Metric, Cache-First Topologia ja Bi-Directional Anchors).
* **Tier 3 Nollaus:** Kehitystietokannat on tyhjennetty ja siemennetty uudella, deterministisellä datalla.  
* **Yksikkötestit (\>90%):** Pydantic RapidFuzz @model\_validator on testattu onnistumisilla, OCR-roskalla, liian pitkillä/lyhyillä lainauksilla sekä kadonneella info.context:lla. Nollalla jakaminen ja DLQ-vähennys on testattu moottoreissa. Chunk-reducer (ANY/ALL) on testattu.  
* **Verkottomuus (Strict Mocking):** Yksikään testi ei tee eläviä LLM-verkkokutsuja. Mock-LLM on viritetty palauttamaan kahdesti vääränlainen lainaus ja todistamaan, että \<PREVIOUS\_SCHEMA\_ERROR\> välitetään oikein ja kolmannella kerralla TDA ohjataan DLQ-tilaan kaatumatta.

### ---

**Yleinen vaikutus ajoihin ja niiden tuloksiin**

Kun tämä Epic on viety tuotantoon, järjestelmä kokee merkittävän paradigman muutoksen:

1. **Vauhti (Nopeus):** Ajot nopeutuvat huomattavasti. LLM:ää ei enää käytetä kriteerien keksimiseen lennosta (atomisointi), mikä säästää jopa 10–20 sekuntia ja ison pinon tokeneita per ajo. Järjestelmä hyppää suoraan O(1)-mäppäyksen kautta varsinaiseen työhön: PDF-tekstin deterministiseen validointiin.  
2. **Luotettavuus ja Hinta:** Kustannukset putoavat. Raskaat atomisointi-promptit jäävät pois. Koska matriisien System-promptit pysyvät nyt täysin staattisina, LLM API pystyy hyödyntämään **Prompt Caching** \-ominaisuutta lähes 100-prosenttisesti (vain ladattu PDF-data vaihtelee), mikä säästää satojatuhansia tokeneita raskaissa ajoissa.  
3. **Tulosten Laatu (Scoring):** "Harmaa alue" poistuu. Asiakas ei enää saa tuloksia, joissa hänellä on "80 % oikein" satunnaisten LLM-mikro-atomien takia. Tulos on raaka, läpinäkyvä ja perustuu puhtaasti asiantuntijoiden asettamaan akateemiseen kriteeristöön (SSOT). Solujen keskiarvot saattavat tippua, mutta laatu on kiistatonta ja 100 % auditoitavissa.  
4. **Ei Keksittyjä Lainauksia:** RapidFuzz-validaattorin myötä joka ikinen vihreäksi tai punaiseksi merkitty kohta on matemaattisesti sidottu PDF-tiedostossa olevaan tekstiin. Järjestelmä on auditoinnin kestävä; "AI Black Box" \-ongelma on ratkaistu lopullisesti.  
5. **Reiluus Huonolla Datalla:** Aiemmin lukukelvottomat sivut (esim. pelkät skannatut kuvat) saattoivat aiheuttaa nollapisteitä ja outoja arvioita. Jatkossa ne menevät turvallisesti DLQ (N/A) \-tilaan. Asiakasta ei rangaista teknisestä lukuvirheestä, vaan ohitetut kohdat renderöidään raporttiin harmaana. Jos sivu on täysin roskaa, ajo keskeytyy ennen kuin se polttaa rahaa (Fail-Fast: FATAL\_SOURCE\_DATA).