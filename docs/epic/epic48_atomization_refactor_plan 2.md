## **Epic 48: Atomisaation Purku, Teoreettinen Ankkurointi ja Deterministinen Orkestrointi (SSOT)**

Tämä Epic korvaa V1-aikakauden epädeterministisen ja hallusinaatioalttiin "Deep Atomization" \-mallin 100 % deterministisellä ja akateemisesti ankkuroidulla **Test-Driven Assertion (TDA)** \-arkkitehtuurilla ("Single Source of Truth"). Koko järjestelmä siirtyy sumeasta arvailusta täsmälliseen, matemaattiseen ja todistettavaan validointiin. Kaikki taaksepäin yhteensopivuutta vaativa legacy-koodi tuhotaan armotta.

### **Vaihe 1: Arkkitehtuurin Siivous ja SSOT-Tietokantamalli (Dead Code Removal)**

> [!WARNING]
> **Kananmuna vai Kana -ongelma (SUORITUSJÄRJESTYS):** 
> Älä muuta ydinmalleja vielä tiukoiksi! Jos poistat `micro_atoms`-kentät Pydantic-malleista ensin, Vaiheen 2 migraatioskripti kaatuu välittömästi `ValidationError`-poikkeuksiin, eikä pysty lukemaan vanhaa kantaa.
> **Oikea toteutusjärjestys:** 
> 1. Rakenna Vaiheen 2 migraatioskripti käyttäen *väliaikaisia, löysiä* luku-malleja (jotka sallivat vanhan rakenteen).
> 2. Aja migraatio ja luo uusi puhdas `seed_data.json`.
> 3. Vasta SITTEN toteuta Vaiheen 1 tuhoamistyöt ja pakota `extra='forbid'` Core-malleihin.

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
   * **Pakottavat säännöt (`strict_pydantic_v2_rust` & `zero_legacy_fallback_hacks`):** Malleihin pakotetaan `model_config = ConfigDict(extra='forbid', strict=True)`. Pydantic-malleihin ei saa lisätä `@model_validator(mode="before")` -funktioita tai löysiä tyyppejä vanhan V1-datan kiertämiseksi.  
   * **Hydraatiomandaatti (`fail_fast_hydration_mandate`):** Älä KOSKAAN käytä backendissä Pythonin `dict.get()`-metodia vanhojen rakenteiden kiertämiseksi (esim. `data.get("ai_description", [])`). Kaikki saapuva JSON-data on hydratoitava VÄLITTÖMÄSTI Pydanticin `.model_validate()` -komennolla.  
4. **run\_seed.py kevennys ja nollaus:**  
   * Poistetaan LLM-clientin ja välimuistin alustukset Seederistä. Seeder lataa kantaan uuden Pydantic-mallin mukaista dataa seed\_data.json \-tiedostosta sekunneissa ilman verkkokutsuja.
5. **enums.py optimointi (Suorituskyky):**
   * Päivitetään `SystemConcurrency`-arvot (esim. `MAX_CONCURRENT_LLM_STEPS = 5`, `LLM_MAX_RETRIES = 3`, `LLM_DEFAULT_TIMEOUT_SECONDS = 180`), jotta raskaista atomisointiprompteista vapautunut LLM-kapasiteetti voidaan hyödyntää täysimääräisenä ajoja nopeuttamalla.

### **Vaihe 2: Teoreettinen Ankkurointi ja Prompt Compilerin Äly**

Kaikki kriteerit irrotetaan LLM:n "musta tuntuu" \-logiikasta ja ankkuroidaan suoraan akateemisiin teorioihin.

1. **Uusi seed_data.json ja Positivity Mandate (Kertaluonteinen Migraatio):**  
   * Tietokanta saatetaan "ajovalmiiksi" erillisellä offline-migraatioskriptillä (`migrate_seed_to_tda.py`), joka lukee nykyisen V1-tyylisen `seed_data.json` -tiedoston.
   * **Theory Grounding (Web Search / MCP):** Skripti ohjeistetaan lukemaan matriisin `theory_grounding.source_url` -lähde (esim. Toulmin/Bloom). Vanhat yhdistelmäsäännöt (Compound) pilkotaan tiukoiksi, atomaarisiksi `TDAAssertion`-olioiksi peilaten näitä akateemisia alkuperäismääritelmiä.
   * **Arkkitehtuurisääntö (`llm_structured_execution_mandate`):** Skriptin tekoälykutsua varten ei saa käyttää `run_chat()`-metodia tai regex-parsimista. Strukturoitu generointi on AINA tehtävä API:n natiivin JSON-rajoitteen kautta (esim. `LLMTaskExecutor.execute_structured_task()`), palauttaen suoraan Pydantic `List[TDAAssertion]`.
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
   * **Pakottavat säännöt (`native_language_system_prompts` & `hybrid_prompting_mandate`):** Promptin on oltava yksinomaan englanniksi (kielellisen rapautumisen estämiseksi) ja sen on käytettävä Hybrid Promptingia (Markdownia XML-tagien sisällä).
   * Koska ohje on 100 % staattinen, hyödynnämme **Prompt Caching** -ominaisuuksia maksimoimaan kustannussäästöt. Dynaaminen lähdeteksti injektoidaan aina User-viestin `<source_text>`-blokkiin.  
3. **Käänteisen Logiikan Injektio (PromptCompiler):**  
   * PromptCompiler (backend\_v2/services/orchestrator/prompt\_compiler.py) lukee inverse\_evidence-lipun TDA-kohtaisesti.  
   * Jos se on tosi, compiler injektoi suoraan LLM:n promptiin ohjeen säännön tulkitsemiseksi: *"This is an inverse rule (Vice). If rule_satisfied = True (no issues found), evidence_found MUST be False and you must return EMPTY quotes []. If rule_satisfied = False (violation found), evidence_found MUST be True and you MUST quote the exact violation."*

### **Vaihe 3: Hallusinaatiosuoja ja Validointi (Industrial Grade Resilience)**

1. **DTO-rakenteiden päivitys ja Kognitiivisen Solmun Purku:**  
   * **Nimeämiskäytäntö (`is_true` kieltäminen):** Tekoäly menee sekaisin tuplanegatiivisista ("Löysitkö virheen? True/False"). Siksi `is_true`-kenttä kielletään DTO:ssa. Käytämme yksiselitteisiä kenttiä: `rule_satisfied: bool` (Läpäisikö dokumentti tämän säännön puhtaasti?) ja `evidence_found: bool` (Löytyikö kriteerin mukainen lainaus?).
   * Lisätään LLM:n tulos-DTO-malleihin pakolliset kentät `evidence_quotes: list[str]` ja `reasoning_trace: str`. LLM:n on aina ensin tuotettava `reasoning_trace` ennen boolean-päätöksiä (Chain of Thought).  
   * **Dynaamiset Output Extensions (Staattinen DTO-arkkitehtuuri):** Pydanticin `create_model()` -metodin käyttö dynaamisten luokkien luomiseksi "lennosta" on EHDOTTOMASTI KIELLETTY. Se tuhoaa Pythonin suorituskyvyn, estää Dartin staattisen tyypityksen ja rikkoo OpenAI:n Structured Outputs -välimuistin. Käytämme sen sijaan staattista tietuetta: `extensions: Dict[ExtensionType, str]` (jossa `ExtensionType` on ennalta määritetty Enum). PromptCompiler ohjeistaa tekoälyä, mitkä Enumin avaimet vaaditaan kyseisessä ajossa.
2. **Käänteiset säännöt (inverse\_evidence) ja Nollasääntö:**  
   * **Normaali hyve (`inverse_evidence == False`):** `rule_satisfied == True` VAATII, että `evidence_found == True` ja `len(quotes) > 0`. (Hyve löytyi).
   * **Negatiivinen pahe (`inverse_evidence == True`):** `rule_satisfied == True` VAATII, että `evidence_found == False` ja lainaukset ovat tyhjä lista `[]`. (Pahetta ei löytynyt = Sääntö läpäisty = Dokumentti on puhdas).
3. **Deterministinen Vertailu & RapidFuzz Fallback (Fail-Fast Kompromissi):**  
   * Luodaan Pydantic `@model_validator(mode='after')` tulosmallille. Tässä tehdään tietoinen kompromissi puristisen determinismin ja PDF-reaalimaailman (OCR-artefaktit) välillä.
   * **Kadonnut Konteksti:** Ensimmäinen koodirivi on: `assert info.context and 'source_text' in info.context`. LLMTaskExecutor pakotetaan injektoimaan tämä: `model_validate(data, context={'source_text': chunk_text})`.  
   * **Normalisointi & CPU-lukon Esto:** Ennen raskaita operaatioita tekstit normalisoidaan (`.strip().replace('\n', ' ').lower()` ja duplikaattivälilyöntien poisto). Tämän jälkeen yritetään AINA ensin eksaktia hakua (`quote in source`). Jos se onnistuu, validointi on salamannopea O(n) ja vältämme RapidFuzzin aiheuttamat CPU-lukot.
   * **Sumea Vertailu ja Asynkronisuus (FastAPI GIL Starvation):** Jos eksakti haku epäonnistuu, käytetään RapidFuzz-kirjastoa. Koska pitkien PDF-tekstien merkkijonovertailu on raskasta synkronista koodia, joka voi lukita koko FastAPI-palvelimen (GIL), RapidFuzz on EHDOTTOMASTI ajettava asynkronisesti: `await asyncio.to_thread(fuzz.partial_ratio, ...)`. Kynnysarvoa (`> 95.0`) on skaalattava lainauksen pituuden mukaan.
   * **Huijauksen Esto (Sanojen Määrä ja Sumeuden Kytkimet):** 
     * **0 sanaa (Tyhjä lista):** Sallitaan, sillä käänteiset säännöt (`inverse_evidence`) vaativat onnistuessaan tyhjän listan.
     * **1-3 sanaa:** Sallitaan, mutta niiltä vaaditaan **100 % eksakti osuma** (Exact Match). RapidFuzzin käyttö näin lyhyillä lainauksilla on ehdottomasti kielletty, jotta estetään lyhyiden termien (esim. "Kyllä", "Ei sovelleta") valheelliset sumeat osumat.
     * **4-40 sanaa:** Sallitaan. Jos eksakti haku epäonnistuu, RapidFuzz (`> 95.0`) on sallittu OCR-artefaktien korjaamiseksi.
       * **Semanttinen Lukko (Negation Check):** Pelkkä matemaattinen 95 % RapidFuzz-kynnys ei riitä, sillä se voisi sallia kieltosanan puuttumisen (esim. "Ei velvollisuutta" vs. "On velvollisuus"). Jos RapidFuzz hyväksyy osuman, validaattorin on vielä suoritettava eksakti tarkistus kriittisille negaatioille (`ei`, `on`, `saa`). Jos kieltosana esiintyy LLM:n lainauksessa mutta ei alkuperäisessä osumassa (tai toisinpäin), haku **hylätään** absoluuttisesti (`ValueError`).
       * **PDF-korostusten (Highlights) hajoamisen esto:** Jos Semanttinen Lukko läpäistään ja sumea osuma hyväksytään, validaattorin TÄYTYY korvata DTO:n `evidence_quotes`-kentän arvo ohjelmallisesti sillä täsmällisellä tekstillä, joka leikattiin suoraan lähdetiedostosta osuman kohdalta. Muuten Dart-käyttöliittymän PDF-korostustyökalu ei löydä tekstiä sivulta.
     * **> 40 sanaa:** Hylätään absoluuttisesti (`ValueError`), jotta tekoäly ei voi "huijata" lainaamalla koko sivua.
   * **Audit-loki (Hallusinaatio-seuranta):** Jos osuma hyväksytään RapidFuzzilla (alle 100 % osuma), alkuperäinen PDF-teksti ja LLM-lainaus tallennetaan telemetriaan. Näin voimme todentaa jälkikäteen, pelastiko RapidFuzz meidät OCR-virheeltä vai salliiko se kielellistä Duck-Typingia.
   * **Validation Loop of Doom -suoja (Systeemipromptin lisäys):** Estetään tekoälyä korjailemasta kirjoitusvirheitä tai kääntämästä tekstiä, mikä johtaisi aina 3 perättäiseen RapidFuzz-epäonnistumiseen ja tokeneiden palamiseen. Pakotetaan prompt: *"EXTRACT EXACT QUOTES ONLY. DO NOT PARAPHRASE. EXTRACT QUOTES IN THE EXACT ORIGINAL LANGUAGE. DO NOT TRANSLATE. DO NOT FIX TYPOS."*
4. **Dynaaminen Virhepalaute (LLM Task Executor):**  
   * Jos Pydantic nostaa ValidationErrorin, LLMTaskExecutor ottaa sen kiinni.  
   * Seuraavaan API-kutsuun injektoidaan vain *tuorein* virhe XML-lohkoon: \<PREVIOUS\_SCHEMA\_ERROR\>Error: Quote not found in source text with 95% ratio.\</PREVIOUS\_SCHEMA\_ERROR\>.  
   * Uudelleenyritysten katto on SystemConcurrency.LLM\_MAX\_RETRIES. Virheitä ei koskaan nielaista except: pass \-lausekkeilla.

### **Vaihe 4: Dead Letter Queue (DLQ) ja Matematiikka**

1. **TDA:n hylkääminen (DLQ):**  
   * Jos LLM\_MAX\_RETRIES ylittyy, kyseinen väite siirretään DLQ-tilaan. Backend Enum-päivitys: ValidationStatus.dlq.  
   * TDA:lle ei anneta 0 pistettä. Se poistetaan nimittäjästä: hit\_rate \= sum(True) / (total\_atoms \- dlq\_count).  
2. **Minimiluottamusraja & DLQ-matematiikka (Confidence Threshold):**  
   * backend\_v2/utils/scoring/ moottorit päivitetään tukemaan 3-tilalogiikkaa (True, False, DLQ).  
   * Pelkkä nollalla jakamisen esto (`valid_denominator <= 0`) ei riitä, sillä se mahdollistaisi "100 % tuloksen" saamisen lukukelvottomasta dokumentista, jos vain yksi kriteeri sattuisi onnistumaan (esim. `1 / (10 - 9) = 100 %`).
   * Lisätään tiukka luottamusraja (esim. 30 %): `if dlq_count / total_atoms > 0.30: return ScoringResult(score=None, status="FAILED_UNSCORABLE")`. DLQ ei saa koskaan olla porsaanreikä arvioinnin kiertämiselle.
3. **Map-Reduce / Chunk-Aggregointi (report\_controller.py):**  
   * Jos dokumentti on pilkottu osiin, ohjelmallinen yhdistämislogiikka on yksiselitteisesti `ANY()`-pohjainen molemmissa skenaarioissa:
     * **Hyveet (Normaali, `inverse_evidence=False`):** Jos `ANY(chunk_has_virtue)`, kriteerin lopputulos on `True` (yksikin onnistunut havainto riittää).
     * **Paheet (Käänteinen, `inverse_evidence=True`):** Jos `ANY(chunk_has_violation)`, kriteerin lopputulos on `False` (yksikin haitallinen löydös kaataa dokumentin puhtauden kyseisen kriteerin osalta).
4. **DAG-tason suojat:**  
   * Jos pisteytysmoottori palauttaa FAILED\_UNSCORABLE, Orkestraattorin on merkittävä koko arvioinnin tila luokkaan FATAL\_SOURCE\_DATA ja lopetettava prosessointi välittömästi.
5. **Synteesimoottorin yhteensopivuus (Epic 50):**
   * Jos järjestelmä tekee "Row Explanation Synthesis" -ajoja, synteesimoottorin promptille on opetettava ohittamaan (Skip) DLQ-tilassa olevat kriteerit. Järjestelmä ei saa yrittää kirjoittaa hienoa selitystä asialle, jota ei voitu edes arvioida.

### **Vaihe 5: Frontend UI \-päivitykset (Tier 2 Hardening)**

1. **Dart Freezed-mallit:**  
   * Päivitetään mallit tukemaan uutta TDAAssertion \-oliota ja sen listoja (tdaAssertions: List\<TDAAssertion\>).  
   * Lisätään Enum ValidationStatus.dlq.  
   * **Pakottava sääntö (`the_zero_compromise_pledge` ja AppErrorBoundary):** Null-coalescing-operaattoreiden (`?? []`) käyttö datan parsinnassa rakenteellisten virheiden piilottamiseksi on EHDOTTOMASTI KIELLETTY. Data-kerroksen (Freezed) pitää heittää kova poikkeus. **Mutta UI-tasolla:** Emme päästä "Red Screen of Deathia" loppukäyttäjälle asti. Virhe TÄYTYY napata siistiin `ErrorBoundary`-widgettiin, joka näyttää vain rikkinäisen komponentin kohdalla harmaan "Data Corrupted" -laatikon, sallien asiakkaan jatkaa muun sovelluksen käyttöä.
2. **Matriisieditori:**  
   * Käyttöliittymä (prompt\_block\_builder\_view.dart) päivitetään sellaiseksi, että käyttäjä voi syöttää jokaiselle Claimille rajattoman määrän TDAAssertion \-kriteerejä dynaamiseen listaan ja valita checkboxilla onko kyseessä inverse\_evidence.  
3. **N/A (DLQ) renderöinti & PDF-pariteetti:**  
   * Raporttinäkymiin (result\_dashboard.dart yms.) lisätään tuki dlq \-tuloksille. Jos kriteeri on DLQ-tilassa, se näytetään harmaana ("Ei arvioitavissa lähteen laadun vuoksi").
   * **Jinja2 PDF-raportit (Backend):** Koska arkkitehtuurissa on tiukka UI/PDF-pariteettisääntö, Python-backendin Jinja2-raporttipohjiin (`.html` / `.svg`) on lisättävä vastaava ehto (`{% if status == 'dlq' %}`), jotta fyysiseen PDF-tulosteeseen piirtyy sama harmaa laatikko kuin ruudulle.

### **6\. Definition of Done**

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