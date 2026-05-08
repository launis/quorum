# ---

**Epic 48: Deterministinen Hierarkkinen Orkestrointi & XAI-Tulostevirta (Agentic Shift-to-Code & Map-Reduce)**

## **1\. Yhteenveto ja Arkkitehtuurinen Tavoite (Executive Summary)**

Tämän Epicin tavoitteena on implementoida state-of-the-art **Hierarchical Multi-Agent (Map-Reduce)** \-tekoälyarkkitehtuuri, joka on täysin alistettu tiukalle, deterministiselle ja asynkronisesti skaalautuvalle Python-objektiohjaukselle (**"Shift-to-Code"** ja **"Code-as-a-Judge"**).

Ratkaisemme globaaleja tekoälyjärjestelmiä vaivaavan "Duck-Typing Token Shield" \-ongelman, jossa kovaa raakadataa piilotetaan loppusynteesiltä Token-rajojen pelossa, pakottaen järjestelmän luottamaan sokeasti välitason LLM-mallien tiivistelmiin ja menettäen täydellisen auditoitavuuden.

Seed-datan (kuten db\_v2.json) monimutkaiset matriisit ja agenttiverkostot integroidaan järjestelmään puhtaasti **Boolean Evaluation** \-paradigman kautta. Tekoäly ei enää laske pisteitä tai arvioi kokonaisuuksia vapaasti, vaan se pakotetaan arvioimaan yksittäisiä väitteitä (True/False) Nollahypoteesin alaisuudessa. Matemaattinen laskenta, mekaaninen validointi ja hallusinaatioiden valvonta siirretään 100-prosenttisesti puhtaalle, muuttumattomalle ja tyyppiturvalliselle Rust-pohjaiselle Pydantic-koodille.

Tämä vapauttaa asiantuntija-agentit (kuten *Falsifioijan*) kognitiiviseen tehtäväänsä: **käyttäjän syöttämien väitteiden aktiiviseen kumoamiseen (Red Teaming) ja ulkoisten tietolähteiden (MCP) hyödyntämiseen**.

Järjestelmästä tulee **Zero-Hallucination** \-todennettu, täysin auditoitava ja API-kustannuksiltaan optimoitu. Se kykenee tuottamaan visuaalisesti rikkaita XAI-raportteja (Explainable AI) siten, että datan laskenta-, reititys- ja esityskerrokset on täydellisesti eristetty toisistaan (**Tripartite Rendering Boundary**), taaten PDF- ja Flutter-käyttöliittymän millintarkan identtisyyden. Koodikannasta eliminoidaan kaikki legacy-painolasti, mykät virheet ja "Duct Tape" \-korjaukset tiukalla Keskitetyn Totuuden Lähteen (Single Source of Truth) mandaatilla.

## ---

**2\. Nykytilan Pullonkaulat ja Anti-Patternien Eliminointi**

Nykytilan löyhät ratkaisut korvataan puhtaalla deterministisellä arkkitehtuurilla seuraavien rakenteellisten heikkouksien eliminoimiseksi:

1. **Auditoitavuuden menetys ja Tilojen epäpuhtaus (State Impurity):** Kun \_compress\_synthesis\_payload on puristanut suoritusketjun pelkkään reasoning\_trace-tekstiin, alkuperäiset raakalainaukset ovat kadonneet loppusynteesiltä (Chief Editor). Virheet ovat periytyneet rakenteessa alhaalta ylös. Työnkulkujen ja välitilojen hallinnassa on voitu aiemmin nojata raakoihin sanakirjoihin ("Naked Dicts") ja sokeaan tyyppien arvailuun (.endswith()), mikä tuhoaa datan "Chain of Custody" \-jäljitettävyyden.  
2. **Kallista tekoälyn ylikäyttöä ja Matemaattisia Hallusinaatioita:** Järjestelmä on yrittänyt ratkaista datan eheyttä käyttämällä hitaita LLM-solmuja (kuten Falsifier) tarkistamaan toisten LLM-solmujen työtä ja laskemaan pisteitä. Tekoälymallit ovat luonnostaan surkeita matematiikassa ja sääntöpohjaisessa mekaanisessa validoinnissa. Nämä raskaat LLM-kutsut logiikkakerroksessa maksavat tokeneita, altistavat 400 "Resource Exhausted" \-virheille ja tukkivat FastAPI-pääsäikeen (Blocking the Fastapi Thread).  
3. **Mykät virheet ja "Duct Tape" \-koodi (Silent Failures):** Virheiden hiljaiset ohitukset (kuten except Exception: pass), dict-muotoisen datan sokeat .get("default")-onginnat ja vanhentuneen (V1) datan lokaali paikkailu or-ketjuilla ovat vaarantaneet prosessin deterministisyyden. Järjestelmän on kaaduttava äänekkäästi (Fail-Fast) viallisen datan edessä (Zero Compromise Pledge).  
4. **Sokeat tulosteet ja Kerrosvuodot (ORM Bleed):** Loppukäyttäjälle esitettävät XAI-raportit nojaavat tekoälyn sanaan. Backend on saattanut sekoittaa vastuita palauttamalla esitysvalmista Markdownia, mikä rikkoo esityskerroksen ja backendin välisen rajan ja tuhoaa UI:n ja PDF:n synkronoinnin.

## ---

**3\. Seed-Datan, Pydantic-mallien ja Orkestroinnin Integraatio (Shift-to-Code)**

Seed-data (esim. db\_v2.json) määrittelee koko järjestelmän kognitiivisen topologian (työnkulut, matriisit, asiantuntijaroolit, tulosteprofiilit). Backendin on kyettävä lukemaan, validoimaan ja orkestroimaan tämä data ehdottoman tyyppiturvallisesti.

### **Phase 1: Pydantic- ja Domain-mallien Absoluuttinen Puhtaus**

Seed-datan monimutkaiset rakenteet (esim. prompt\_blocks ja output\_profiles) mallinnetaan tiukasti Pythonin logiikkakerroksessa. Koodikannassa ei ylläpidetä V1- ja V2-malleja rinnakkain; vanha koodi ja kentät tuhotaan armotta (**Single Source of Truth Mandate**).

* **Natiivi Tyypitys ja Moderni Syntaksi:** Tyypityksessä käytetään yksinomaan Python 3.14+ PEP 695 generics \-syntaksia ja uusia | None \-unioneita (Optional-kirjasto poistetaan kokonaan). Pydanticin natiiveja rajoitteita (esim. Field(ge=0)) suositaan raskaiden manuaalisten field\_validator-funktioiden sijaan. Tyyppitarkastusten ohituksia (\# type: ignore) ei sallita ilman eksplisiittistä linterin virhekoodia ja kirjallista perustelua (**Zero Type Ignore Shortcuts**).  
* **Muuttumattomuus ja Rust-tason Tiukkuus:** Kaikki tilansiirroissa käytettävät domain-mallit konfiguroidaan muuttumattomiksi (ConfigDict(frozen=True)). Malleihin asetetaan extra='forbid', jotta rakenteeseen kuulumaton roska (kuten LLM:n hallusinoimat lisäkentät) hylätään Pydanticin C/Rust-kerroksessa välittömästi. Mallit validoidaan aina .model\_validate() \-metodilla (parse\_obj() on kielletty).  
* **Polymorphic Routing (Discriminated Unions):** Seed-datan output\_profiles määrittelee erilaisia layouts-objekteja (esim. preset\_view: "3d\_matrix", "2d\_compare" tai "text\_only"). Näiden käsittelyssä hyödynnetään O(1)-tason Discriminated Unioneita (esim. Field(discriminator='preset\_view')), jotta data jäsennetään suoraan oikeaan Pydantic-aliluokkaan.  
* **Pakotettu Tiukka Tyypitys (Strict Enums & Literals):** Kaikki Enumit ja Literalit on pakotettava tiukkaan tilaan (esim. `Field(strict=True)`). Jos tietokannasta tai Ingressistä tulee vieras arvo, järjestelmän on kaaduttava äänekkäästi (HTTP 500 / 422), jotta viallinen data ei etene logiikkaan. Löyhä tyypitys ja Lax-aliakset ovat ankarasti kiellettyjä.

### **Phase 2: Agenttien ja Matriisien Looginen Roolitus (Boolean Evaluation)**

Seed-data sisältää prompt\_blocks-matriiseja, jotka määrittelevät **BARS (Behaviorally Anchored Rating Scales)** \-rakenteet (esim. Toulmin, Bloom). Asiantuntija-agenttien rooli muutetaan pisteiden arpojista ja tekstin generoijista puhtaiksi väite-evaluaattoreiksi.

* **Nollahypoteesi ja Binäärinen Arviointi:** LLM ei enää palauta numeerista "arvosanaa". Seed-datan scales-rakenteissa on claims-väitteitä (esim. *"Oikeutus (warrant) puuttuu"*). LLM pakotetaan arvioimaan jokainen väite binäärisesti (is\_verified: bool) Nollahypoteesin alaisuudessa – eli olettamalla väite *vääriksi*, kunnes se löytää aukottoman todisteen.  
* **Pakotettu Todiste (Evidence-Based):** Aina kun LLM asettaa väitteen todeksi (is\_verified \= True), sen on pakko nostaa täsmälleen alkuperäistä tekstiä vastaava lainaus evidence\_quotes: list\[str\] \-kenttään DTO-malliin.

### **Phase 3: Code-as-a-Judge ja Fail-Fast Hallusinaatiosuoja**

Mekaaninen validointi ja matemaattinen pistelasku siirretään täysin LLM:ltä koodin suoritettavaksi.

* **Välitön Fail-Fast Hydrataatio & The Zero Compromise Pledge:** Kaikki epävarma ulkoinen data (webhookeista, tietokannasta tai LLM:n JSON-paluusanomasta) on hydratoitava Pydantic-malleiksi **välittömästi**. Sanakirjojen onkiminen tyyliin data.get("avain") ja hiljaiset "or"-ketjut (esim. oletusarvojen paikkailu lokaalisti) ovat ankarasti kiellettyjä.  
* **Synkroninen Pydantic-validointi ja Canonicalization (The CPU Trap Resolution):** Luovutaan "asynkronisuuden illuusiosta". O(N)-tason tekstimanipulaatio (erikoismerkkien ja välilyöntien strippaus Canonicalizationia varten) on äärimmäisen nopeaa eikä vaadi Arq-jonoa (mikä toisi vain turhaa serialisointiviivettä ja monimutkaisuutta). Lainausten "Exact Match" -validointi ja normalisointi suoritetaan puhtaasti **synkronisesti Pydantic V2:n natiivissa `@model_validator(mode='after')` -ketjussa**, hyödyntäen C/Rust-tason suorituskykyä. Samalla vanha sumea "Self-Healing Citations" -heuristiikka ja regex-arvailut poistetaan koodikannasta kokonaan.  
* **Hylkäys, Circuit Breaker, The Duct Tape Ban & Error Feedback Loop:** Jos LLM on keksinyt lainauksen tai muuttanut sanamuotoja, Python heittää välittömästi AppException-virheen. **Mykät virheiden ohitukset ja God Blockit (except Exception: pass) ovat ehdottomasti kiellettyjä.** Arq-worker pakottaa solmun yrittämään uudelleen. Koska sokea uudelleenyritys nollalämpötilalla johtaa identtiseen virheeseen, järjestelmän on siepattava Pydantic-virheet. Jos validointi epäonnistuu, seuraavaan Arq-yritykseen on injektoitava dynaaminen `<PREVIOUS_SCHEMA_ERROR>` -XML-lohko ohjaamaan tekoälyä korjaamaan virheensä. Maksimiyritykset sidotaan tiukasti SystemConcurrency.LLM\_MAX\_RETRIES-vakioon.  
* **Security Logging Ban:** Arq-jonon ja Logfiren lokeihin ei koskaan tallenneta käyttäjän alkuperäisiä prompteja (PII) tai API-avaimia.

### **Phase 4: Falsifier-agentin Red Teaming ja DAG-Orkestrointi**

Työnkulkujen agentit ja orkestrointi sidotaan tarkasti Seed Datan workflows.steps ja depends\_on \-verkkoon.

* **Asynkronisen Rinnakkaisuuden Vapauttaminen & TaskGroup Peruutusmekanismi:** Backend muodostaa Seed-datan riippuvuuksista Suunnatun Syklittömän Verkon (DAG) ja purkaa sarjalliset pullonkaulat suorittamalla LLM-agentit rinnakkain Map-vaiheena (esim. nostamalla globaalia `MAX_CONCURRENT_LLM_STEPS` -rajaa). Jotta massiivinen rinnakkaisajo on turvallista, rinnakkaisajoissa on määriteltävä selkeä TaskGroup-peruutus (Cancellation): jos yksi asiantuntijasolmu kaatuu kriittisesti, muiden keskeneräisten verkko- ja LLM-pyyntöjen suoritus on peruttava välittömästi resurssivuotojen estämiseksi ja API-budjetin säästämiseksi.  
* **Claim Extraction Hook:** Lisätään koukku (extract\_user\_claims), joka poimii käyttäjän syötteestä kovat väitteet Pydantic UserClaim-listaksi ennen agenttien arviointia.  
* **LLM Structured Execution & Static Region Pinning:** Kaikki tekoälyn ajot on toteutettava yksinomaan keskitettyjen `LLMTaskExecutor`-kääreiden kautta. Jotta natiivi Context Caching toimii (välimuistit ovat aina region-kohtaisia, esim. `europe-north1`), järjestelmä on pakotettava staattiseen region-kiinnitykseen (Region Pinning). Cross-region fallbackeja ei saa käyttää, sillä alueen vaihtuminen lennosta kumoaisi koko välimuistin ja pakottaisi lataamaan raskaat asiakirjat uudelleen. Rate Limit (429) -viiveet hallitaan puhtaasti Arq-jonojen exponential backoff -mekanismeilla. Agentit perivät ajon aikaiset `temperature` ja `caching_strategy` -arvot suoraan Seed-datan `config_model_registry` -määrittelyistä.  
* **Natiivi Kontekstivälimuisti (Context Caching) & Prompt Immutability:** Raskaita lähdedokumentteja ei saa lähettää toistuvasti verkkojen yli jokaiselle solmulle. Järjestelmän on hyödynnettävä natiivia LLM Context Caching -mekanismia. Lähdedata ladataan välimuistiin kerran työnkulun alussa, ja agentit saavat vain välimuistin tunnisteen (Cache Handle). Dynaamiset parametrit eristetään `<execution_parameters>` -XML-tageihin. F-stringien käyttö sääntölogiikan rakentamiseen on ankarasti kielletty; `prompt_compiler.py` pysyy muuttumattomana.  
* **MCP-verkkohakujen Sandbox & Tool Use Intent:** Falsifier lukee asiantuntijasolmun konfiguraatiosta allowed\_mcp\_tools \-kentän (esim. mcp\_tavily\_search). Agentti ei tee suoria `await`-kutsuja ulkoisiin palveluihin (mikä rikkoisi kerrosarkkitehtuurin), vaan palauttaa vain "Tool Use Intent" -objektin. Orkestraattori (LLMTaskExecutor) suorittaa varsinaisen fyysisen verkkokutsun eristetyssä `execute_tool_loop()` -hiekkalaatikossa tiukalla aikakatkaisulla, palauttaen rakenteellisen mallin. Agentti yrittää kumota käyttäjän väitteen tällä ulkoisella datalla, tallentaen vastaväitteen tiukasti nimettyyn kenttään falsifying\_evidence: str | None (ei dynaamisia kenttänimiä).  
* **Opaque Stripe IDs & Zero DB Hardcoding Mandate:** Kaikki reititykset ja työkaluviittaukset käyttävät ainoastaan "läpinäkymättömiä" tunnisteita (esim. usr\_123 tai Seed-datan blk\_123). Tietokannan natiiveja kokonaisluku-ID:itä, "magic string" \-taulunnimiä tai listojen indeksejä (esim. lista\[0\]) ei saa koskaan kovakoodata ja vertailla logiikassa.

### **Phase 5: Smart Token Shield ja Skeemaohjattu Reititys (Schema-Driven)**

Välitilojen siirto ja \_compress\_synthesis\_payload tehdään tyyppiturvallisiksi.

* **Structured State Envelopes (no\_naked\_dicts\_in\_state):** Työnkulun välitilat kootaan ja siirretään aina tiukasti tyypitettynä StepOutputDTO-listana. Raakojen sanakirjojen (Naked Dicts) käyttö tilanhallinnassa tai reitityksessä on absoluuttisesti kielletty.  
* **Schema-Driven Polymorphic Routing O(1):** "Duck typing" (arvojen availu .endswith()-metodilla) on kielletty. Reititys solmujen välillä tehdään aina tietokannasta tulevan rakenteen perusteella hyödyntäen **Pydantic Discriminated Unioneita** ja Pythonin natiivia polymorfista match/case \-syntaksia.  
* **Valikoiva suodatus & Rajoitettu Escape Hatch:** Token Shield pudottaa välitiloista raskaan kohinan (evaluations, shuffled\_atoms), mutta **päästää ohjelmallisesti läpi reasoning\_trace, boolean-arviot ja koodilla vahvistetut evidence\_quotes \-kentät**. Falsifierin tuottama critical\_quote on varustettu "Escape Hatchilla", joka ohittaa Token Shieldin karsinnan täysin. Escape Hatch sallitaan ainoastaan silloin, kun siihen liittyy Pydanticissa kova yläraja (esim. `Field(max_length=1500)`). Ylipitkät hallusinaatiot on hylättävä ennen XAI-synteesiä Token Explosion -riskin eliminoimiseksi.

### **Phase 6: Algoritminen Triage, Puhdas Matematiikka ja Logic Step (Reduce)**

Seed Datan mukainen type: "logic" solmu (esim. sp\_d245365e4a274b9e Scoring Engine) ottaa matemaattisen laskennan kokonaan pois LLM:ltä O(1)-tason ohjelmakoodin haltuun (Reduce-vaihe).

* **Pure Functions (Synthesis.py Standard):** Matriisien evaluointi tapahtuu puhtailla funktioilla Pythonissa. Koodi kääntää LLM:n palauttamat boolean-arvot numeerisiksi pisteiksi lukemalla scale\_min ja scale\_max rajat suoraan seed-datasta. Sisäkkäiset iteraatiosilmukat (O(N^2)) korvataan suorituskykyisillä O(1) Hash Map / Dictionary \-hauilla.  
* **Matemaattinen Poikkeamien Tunnistus (Strict Math Display Isolation):** scoring.py lukee koodilla lasketut pisteytykset deterministisellä MAD-moottorilla (Median Absolute Deviation) tai valitulla laskentakoukulla (esim. apply\_scoring\_logic). MAD-moottori saa matemaattiset ääriarvonsa tiukasti dynaamisesta PromptBlock-konfiguraatiosta (computed\_min ja computed\_max). Käyttöliittymän visuaalista skaalaa (scale\_min) ei saa koskaan sekoittaa backendin laskentamatematiikkaan.  
* **Resilience Score ja Tilamutaatioiden Kielto:** Falsifierin löydökset lasketaan deterministiseksi kestävyysarvosanaksi hyödyntäen dynaamisia raja-arvoja (esim. `triage_threshold_pct = 0.4`), ei epämääräisiä "suuri osa" -konsepteja. Jos raja-arvo ylittyy, algoritmi ei tee suoraa tilamutaatiota (koska tila on `frozen=True`), vaan algoritmit palauttavat puhtaan `HookResult(state_delta={...})` -objektin, jonka orkestraattori yhdistää uuteen, muuttumattomaan tilainstanssiin asettaen `has_warning = True` -lipun Triage-tilaa varten.
* **MD5 Hashery-Deprekaatio ja Ephemeral Runtime ID -mäppäys (Anti-Collision Protocol):** Historiallinen arkkitehtuuri, jossa matriisien kysymyksille (`micro_atoms`) luotiin kryptografinen MD5-tiiviste tekstin perusteella, on ankarasti kielletty (Hash Collision -haavoittuvuus ja turha prosessorikuorma). Tietokantaa ei myöskään paisuteta sadoilla pysyvillä atomi-ID:illä. Sen sijaan `atom_flattening.py` generoi puhtaasti ajonaikaisen, tilapäisen sekvenssitunnisteen (esim. `atom_1`, `atom_2` tai lyhyt ULID) litteytysvaiheessa. Tämä ID lähetetään LLM:lle, ja Pydantic-skeema pakottaa sen palauttamaan saman ID:n. Reverse Hash Mapping toimii 100 % deterministisesti O(1)-muistimäppäyksen avulla ilman törmäyksiä, poistaen raskaat salaukset ja tietokantataakan. Keskihajonnan sisällä oleva data suodatetaan proaktiivisesti pois.

## **\---**

## **4\. Tulosteiden Esitys ja XAI-Käyttöliittymä (Tripartite Rendering Boundary)**

Todennetun datan ("Chain of Custody") on näyttävä loppukäyttäjälle saumattomasti ja identtisesti PDF-raportissa sekä Flutter-käyttöliittymässä. Järjestelmä noudattaa absoluuttista eristystä backend-logiikan, käyttöliittymän (Frontend/Flutter) ja PDF-generaattorin (Jinja2) välillä (**Tripartite Boundary**). Järjestelmä noudattaa **Zero-Math UI**, **Anemic Routers** ja **HTML-First** \-mandaattia.

### **A. Anemic Routers ja Tietovuotojen Esto (Data Leak Firewall)**

* **Reitittimien puhtaus (anemic\_routers):** FastAPI-reitittimet ovat täysin "aneemisia" ja käsittelevät ainoastaan HTTP-liikenteen vastaanoton. Liiketoimintalogiikkaa tai inline-skeemoja ei sallita reitittimissä (Pydantic Namespace Collisions), vaan ne tuodaan models/-kansiosta.  
* **Strict Dependency Injection & Imports:** Palvelut ladataan FastAPI:ssa yksinomaan Depends() \-mekanismin kautta. Asetukset ladataan tiedoston alussa (Global Settings Import). Inline-importteja ei sallita (**No Inline Imports**).  
* **Zero ORM Bleed & Data Leak Prevention:** Tietokantakerros palauttaa logiikalle vain puhtaita Pydantic-malleja; raa'at ORM-objektit eivät vuoda ulos. Jokaiseen endpointiin on määritettävä pakollinen response\_model (periytyen BaseResponseDTO:sta) estäen ylihaun (over-fetching) ja tietojen vuotamisen.

### **B. PDF:n ja Käyttöliittymän Absoluuttinen Pariteetti ("No-String L10N Mandate")**

* Backend erittelee evidence\_type-kentän avulla deterministisesti, mihin tekoälyn tekemä päätelmä perustuu (esim. EvidenceType.explicit\_match).  
* **Absoluuttinen kielto backendin UI-tekstigeneroinnille (no\_string\_l10n):** Backend ei saa koskaan palauttaa rajapinnan yli ohjelmallisesti kovakoodattuja näyttötekstejä, virheilmoituksia tai staattisia Markdown-taulukoita. Nämä palautetaan UI:lle ja PDF:lle yksinomaan tiukkoina Pydantic Enum- ja Literal-vakioina (esim. `STATUS_FAILED`).  
* **Cross-Language Enum Parity:** Backendin Pydantic Enum/Literal \-muuttujien on oltava täydellisessä **1:1 pariteetissa** Flutterin Dart 3 Enum-määrittelyjen kanssa. Kaikki staattiset esitystekstit ja visuaaliset badget käännetään UI:n ja PDF:n lokaalien `.arb` -tiedostojen kautta.
* **Kognitiivisen Synteesin Poikkeus (Cognitive Synthesis Exception):** "No-String Mandate" koskee vain ohjelmallista UI-metadataa. Tekoälyn luomat **XAI-perustelut ja Chief Editorin tuottama dynaaminen raporttiteksti** (`reasoning_trace`, `profile_syntheses`, `critical_quote`) palautetaan aina raakana Markdown-tekstinä. Tätä vapaata kognitiivista analyysia ei voida eikä saa yrittää ahtaa staattisiin Enum-vakioihin. Synteesin kieli määräytyy suoraan Seed-datan System Promptin perusteella, ja käyttöliittymä renderöi Markdownin natiivisti sellaisenaan.

### **C. UI-Driven Synthesis Boundary & Data-Driven Layouts**

* Backend päättelee seed datan output\_profiles.layouts \-määrittelyistä, mitä näkymiä käyttöliittymä vaatii (esim. preset\_view: "3d\_matrix" tai "text\_only"). AI-raportointi ja DTO-kokoaminen suodatetaan backendissä jo ennakkoon tiukasti pyytävän UI-profiilin (esim. "Holistic Audit") visible\_extensions \-vaatimusten mukaisesti, jotta estetään sellaisten datarakenteiden ja tokenien renderöinti, joita ei esitetä.  
* **Triage-tila:** Jos algoritmi asettaa raportille has\_warning \= True \-lipun, Flutter-työpöytäkäyttöliittymän työnkulku-dashboard siirtyy välittömästi **Triage-tilaan** visuaalisilla varoitusväreillä osoittaen Falsifioijan löytämät puutteet.

### **D. Identtinen Renderöinti: PDF ja UI (Tripartite Synchronization)**

* **Yhteinen ReportDataDTO:** Backend rakentaa yhden, kattavan ja 100 % validoidun ReportDataDTO:n. Se sisältää vain rakenteellista dataa: numeeriset pisteet, vahvistetut lainaukset (evidence\_quotes), asiantuntijasolmujen kategoriat ja XAI Reporter \-agentin tuottaman tiukan tekstisynteesin.  
* **Pragmaattinen Renderöinnin Pariteetti (Natiivi Jinja2-SVG Injektio):** Sekä Jinja2-PDF-moottori että Flutter-käyttöliittymä lukevat **tismalleen samaa** ReportDataDTO-vastausta. Ydinlogiikka pysyy 100 % "Zero-Mathina" ja tietämättömänä UI:sta. Aiemmin ehdotettu Matplotlib poistetaan kokonaan arkkitehtuurista raskaan C/Numpy-bloatin estämiseksi. Sen sijaan PDF-putkessa grafiikat (kuten monimutkaiset matriisit) tuotetaan **puhtailla Jinja2-makroilla, jotka formatoivat DTO-datan suoraan natiiveiksi `<svg>` -vektorielementeiksi**. PDF-moottorit (esim. WeasyPrint) piirtävät SVG:tä täydellisesti ilman CSS Flexboxin taitto-ongelmia, ja näin esityskerroksen (pixels, colors, paths) eristys backendin logiikasta (Tripartite Boundary) pysyy täysin rikkoutumattomana ilman yhtäkään ulkoista riippuvuutta.
* **XAI-Akkordeonit ja Todistelaatikot:** Todennettu data injektoidaan esityskerroksessa natiiveihin komponentteihin (kuten Flutterin MatrixObservabilityAccordion ja xai\_evidence\_box.dart). PDF renderöi nämä täsmälleen vastaavilla Jinja-makroilla. Visuaalinen laatikko (Evidence Box) näyttää asiantuntijan reasoning\_trace-päätelmän ja sen alapuolella alkuperäisen koodilla todennetun lainauksen.  
* **Kattava Matriisikoontitaulukko:** Jinja2 lukee DTO:n evaluations-listan ja generoi dokumentin loppuun taulukon, joka rinnastaa tasot, LLM:n tuottamat lyhyet perustelut sekä nimenomaan Falsifioijan nostamat koodilla vahvistetut vastaväitteet (critical\_quote).

## **5. Teollisen Tason Pragmatismi (Resilience over Puritanism)**

Historiallinen "Zero-Compromise" ja "Fail-Fast" puritanismi on ollut välttämätön data-eheyden saavuttamiseksi, mutta se johti pinnan alla "purkkaviritysten" (duct-tape) syntymiseen tuotannon kaatumisten estämiseksi. Tämä Epic 48 -arkkitehtuuri siirtää nämä piilotetut laastarit virallisiksi, skaalautuviksi tuotantotason design patterneiksi:

1. **In-place Mutaatioista Aitoon CQRS-malliin:** 
   * **Ongelma:** Aiemmin sääntöjen ehdottomuus pakotti päivittämään dynaamiset matematiikka-arvot (`normalized_score`) suoraan vanhoihin `execution_trace` tapahtumiin, mikä tuhosi "Append-Only" -jäljitettävyyden.
   * **Tuotantoratkaisu (CQRS):** Kirjoitusoperaatiot (Command) tallentavat yksinomaan sokeat raakafaktat (`evaluated_atoms`). Lukupuoli (Query) ja renderöinti (`BlueprintTransformer`) suorittavat matemaattisen skaalauksen täysin lennosta uuden kireystason läpi (In-Memory Projektio). Tietokannan menneisyyttä ei koskaan ylikirjoiteta.
2. **MD5-hasheistä Ephemeral Runtime ID -mäppäykseen:**
   * **Ongelma:** Kysymyksille laskettiin MD5-hashit lennosta "Content-Addressable ID" -puritanismin nimissä. Seurauksena oli Hash-törmäyksiä ja orpoutunutta historiadataa typografioita korjattaessa.
   * **Tuotantoratkaisu:** Asynkroninen hajautus käyttää puhtaasti tilapäistä muistimäppäystä (esim. `atom_1`). Sadoille kysymyksille ei synnytetä raskasta kryptografiaa tai tietokanta-bloatia, vaan 100 % determinismi saavutetaan Map-Reduce -elinkaaren sisäisellä O(1) sekvenssillä.
3. **Sokeasta Fail-Fast -kaatumisesta DLQ-jonoihin (Dead Letter Queue):**
   * **Ongelma:** LLM:n satunnainen merkkivirhe lainauksessa (tai Pydantic-validointivirhe) kaatoi säälimättä koko tuntikausien työnkulun, mikä pakotti kehittäjät rakentamaan vaarallisia "Self-Healing" regex-hookeja.
   * **Tuotantoratkaisu:** Epäonnistuneet `micro_atom` -arvioinnit ajetaan ensin dynaamisen **Error Feedback Loopin** läpi (LLM yrittää itse korjata virheensä `<PREVIOUS_ERROR>` -syötteen avulla). Jos atomi on pysyvästi korruptoitunut, sitä ei yritetä parsia kasaan regexillä, vaan se siirretään puhtaasti **Dead Letter Queue (DLQ)** -jonoon. Työnkulku etenee maaliin pragmallisesti, ja loppuraportti ilmoittaa läpinäkyvästi: *"1/150 väitettä ei voitu arvioida luotettavasti"*.
4. **Token Shieldin virallistaminen (Graceful Degradation Boundary):**
   * **Ongelma:** Pydanticin `extra="forbid"` aiheutti Token Exhaustion -kaatumisia suurilla tietomassoilla. Kehittäjät joutuivat rikkomaan puritanismia asettamalla hiljaisesti `extra="ignore"`.
   * **Tuotantoratkaisu:** Asetus `extra="ignore"` on nyt virallistettu "Duck-Typing Token Shield" -arkkitehtuuriseksi poikkeukseksi. Raskaiden datamassojen pudottaminen on eksplisiittisesti sallittua LLM-synteesivaiheessa, mutta se eristetään tiukasti vain tähän yhteen rajapintaan.

## **6\. Liiketoiminnallinen ja Teknologinen Arvo (ROI)**

1. **Zero Hallucination Proof (Täydellinen Auditoitavuus):** Fail-Fast hydrataatio, kooditason "Exact Match" \-validointi ja Null Hypothesis \-mandaatti takaavat absoluuttisesti, että tekoäly ei voi hallusinoida tai keksiä lähteitä. Jokainen väite on aukottomasti osoitettavissa alkuperäisestä asiakirjasta kooditason varmuudella.  
2. **Red Teamingin Maksimointi (Kognitiivinen Stressitesti):** Kun mekaaninen auditointi ja BARS-matematiikka siirtyvät raskaalta LLM:ltä puhtaalle deterministiselle Python-koodille (Code-as-a-Judge), tekoälyn kognitio vapautuu toimimaan aitona vastaväittäjänä ulkoista MCP-dataa hyödyntäen.  
3. **Kustannusten ja Suorituskyvyn Eksponentiaalinen Optimointi (Tunneista Minuutteihin):** LLM-ajojen pullonkaulat murretaan lopullisesti vapauttamalla asynkroninen rinnakkaisuus (Concurrency Unlock) ja käyttämällä natiivia kontekstivälimuistia (Context Caching) satojen tuhansien tokenien toistuvien latausten estämiseksi (Region Pinning). Nämä yhdistettynä O(1)-tason hash-hakuihin ja Smart Token Shieldiin tekevät järjestelmästä paitsi täysin deterministisen, myös teollisen skaalan tekoälymoottorin.  
4. **Teknisen Velan Nollaaminen (Elinikäinen Ylläpidettävyys):** Seed data toimii absoluuttisena totuuden lähteenä koko arkkitehtuurille. Single Source of Truth, duct tape \-virheiden nielujen kielto, täysi tyyppiturvallisuus (strict Pydantic V2 Rust), skeemapohjainen reititys ja täydellinen eristys käyttöliittymän sekä PDF-renderöinnin (Tripartite Boundary) välillä tekevät koodikannasta murtumattoman. Logfire-telemetria mahdollistaa välittömän "Telemetry-First" \-kehityksen ja mahdollisten hallusinaatiopoikkeamien tunnistamisen ennen kuin ne etenevät asiakkaalle.