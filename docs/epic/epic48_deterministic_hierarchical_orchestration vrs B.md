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
* **Annotoitu Hydrataatio:** Seed-datassa esiintyvien merkkijonojen (kuten model\_strategy: "precise") konversio Enum-muotoon on EHDOTTOMASTI tehtävä Pydanticin natiivilla Annotated\[Enum, Field(strict=False)\] \-mekanismilla hyödyntäen keskitetyn enums.py-tiedoston Lax-aliaksia.

### **Phase 2: Agenttien ja Matriisien Looginen Roolitus (Boolean Evaluation)**

Seed-data sisältää prompt\_blocks-matriiseja, jotka määrittelevät **BARS (Behaviorally Anchored Rating Scales)** \-rakenteet (esim. Toulmin, Bloom). Asiantuntija-agenttien rooli muutetaan pisteiden arpojista ja tekstin generoijista puhtaiksi väite-evaluaattoreiksi.

* **Nollahypoteesi ja Binäärinen Arviointi:** LLM ei enää palauta numeerista "arvosanaa". Seed-datan scales-rakenteissa on claims-väitteitä (esim. *"Oikeutus (warrant) puuttuu"*). LLM pakotetaan arvioimaan jokainen väite binäärisesti (is\_verified: bool) Nollahypoteesin alaisuudessa – eli olettamalla väite *vääriksi*, kunnes se löytää aukottoman todisteen.  
* **Pakotettu Todiste (Evidence-Based):** Aina kun LLM asettaa väitteen todeksi (is\_verified \= True), sen on pakko nostaa täsmälleen alkuperäistä tekstiä vastaava lainaus evidence\_quotes: list\[str\] \-kenttään DTO-malliin.

### **Phase 3: Code-as-a-Judge ja Fail-Fast Hallusinaatiosuoja**

Mekaaninen validointi ja matemaattinen pistelasku siirretään täysin LLM:ltä koodin suoritettavaksi.

* **Välitön Fail-Fast Hydrataatio & The Zero Compromise Pledge:** Kaikki epävarma ulkoinen data (webhookeista, tietokannasta tai LLM:n JSON-paluusanomasta) on hydratoitava Pydantic-malleiksi **välittömästi**. Sanakirjojen onkiminen tyyliin data.get("avain") ja hiljaiset "or"-ketjut (esim. oletusarvojen paikkailu lokaalisti) ovat ankarasti kiellettyjä.  
* **Asynkroninen Tekstivertailu (Blocking the FastAPI Thread \-kielto):** Rakennetaan kooditason Pydantic @model\_validator, joka suorittaa nopean sumean tekstivertailun (RapidFuzz-kirjastolla) LLM:n palauttamalle evidence\_quotes-taulukolle alkuperäistä asiakirjaa vasten. Tämä prosessorille raskas validointi ja kaikki LLM-kutsut siirretään poikkeuksetta asynkroniseen **Arq-työjonoon**.  
* **Hylkäys, Circuit Breaker & The Duct Tape Ban:** Jos LLM on keksinyt lainauksen tai muuttanut sanamuotoja, Python heittää välittömästi AppException-virheen. **Mykät virheiden ohitukset ja God Blockit (except Exception: pass) ovat ehdottomasti kiellettyjä.** Arq-worker pakottaa solmun yrittämään uudelleen. Maksimiyritykset sidotaan tiukasti SystemConcurrency.LLM\_MAX\_RETRIES-vakioon.  
* **Security Logging Ban:** Arq-jonon ja Logfiren lokeihin ei koskaan tallenneta käyttäjän alkuperäisiä prompteja (PII) tai API-avaimia.

### **Phase 4: Falsifier-agentin Red Teaming ja DAG-Orkestrointi**

Työnkulkujen agentit ja orkestrointi sidotaan tarkasti Seed Datan workflows.steps ja depends\_on \-verkkoon.

* **Topological Sort & Map-Vaihe:** Backend muodostaa Seed-datan riippuvuuksista Suunnatun Syklittömän Verkon (DAG) ja suorittaa LLM-asiantuntija-agentit rinnakkain Map-vaiheena.  
* **Claim Extraction Hook:** Lisätään koukku (extract\_user\_claims), joka poimii käyttäjän syötteestä kovat väitteet Pydantic UserClaim-listaksi ennen agenttien arviointia.  
* **LLM Structured Execution Mandate:** Kaikki tekoälyn ajot on toteutettava yksinomaan keskitettyjen LLMTaskExecutor.execute\_structured\_task() tai execute\_chat\_task() \-kääreiden kautta. Suora LLMClient-kirjastojen käyttö logiikassa on estetty. Agentit perivät ajon aikaiset temperature, top\_p ja caching\_strategy \-arvot suoraan seed-datan config\_model\_registry \-määrittelyistä.  
* **High-Fidelity Prompting & Prompt Compiler Immutability:** Dynaamiset parametrit ja injektiot eristetään \<execution\_parameters\> \-XML-tageihin promptin alussa. F-stringien käyttö sääntölogiikan rakentamiseen on kielletty. prompt\_compiler.py on muuttumaton (immutable).  
* **MCP Tool Loop:** Falsifier lukee asiantuntijasolmun konfiguraatiosta allowed\_mcp\_tools \-kentän (esim. mcp\_tavily\_search). Suoritetaan asynkroninen haku await tavily\_search(query), joka palauttaa rakenteellisen TavilySearchResult-mallin. Agentti yrittää kumota käyttäjän väitteen tällä ulkoisella datalla, tallentaen vastaväitteen tiukasti nimettyyn kenttään falsifying\_evidence: str | None (ei dynaamisia kenttänimiä).  
* **Opaque Stripe IDs & Zero DB Hardcoding Mandate:** Kaikki reititykset ja työkaluviittaukset käyttävät ainoastaan "läpinäkymättömiä" tunnisteita (esim. usr\_123 tai Seed-datan blk\_123). Tietokannan natiiveja kokonaisluku-ID:itä, "magic string" \-taulunnimiä tai listojen indeksejä (esim. lista\[0\]) ei saa koskaan kovakoodata ja vertailla logiikassa.

### **Phase 5: Smart Token Shield ja Skeemaohjattu Reititys (Schema-Driven)**

Välitilojen siirto ja \_compress\_synthesis\_payload tehdään tyyppiturvallisiksi.

* **Structured State Envelopes (no\_naked\_dicts\_in\_state):** Työnkulun välitilat kootaan ja siirretään aina tiukasti tyypitettynä StepOutputDTO-listana. Raakojen sanakirjojen (Naked Dicts) käyttö tilanhallinnassa tai reitityksessä on absoluuttisesti kielletty.  
* **Schema-Driven Polymorphic Routing O(1):** "Duck typing" (arvojen availu .endswith()-metodilla) on kielletty. Reititys solmujen välillä tehdään aina tietokannasta tulevan rakenteen perusteella hyödyntäen **Pydantic Discriminated Unioneita** ja Pythonin natiivia polymorfista match/case \-syntaksia.  
* **Valikoiva suodatus & Escape Hatch:** Token Shield pudottaa välitiloista raskaan kohinan (evaluations, shuffled\_atoms), mutta **päästää ohjelmallisesti läpi reasoning\_trace, boolean-arviot ja koodilla vahvistetut evidence\_quotes \-kentät**. Falsifierin tuottama critical\_quote on varustettu "Escape Hatchilla", joka ohittaa Token Shieldin karsinnan täysin. "Chief Editor" (XAI Reporter) saa synteesiinsä absoluuttisen tarkat vastatodisteet ilman Token Explosion \-riskiä.

### **Phase 6: Algoritminen Triage, Puhdas Matematiikka ja Logic Step (Reduce)**

Seed Datan mukainen type: "logic" solmu (esim. sp\_d245365e4a274b9e Scoring Engine) ottaa matemaattisen laskennan kokonaan pois LLM:ltä O(1)-tason ohjelmakoodin haltuun (Reduce-vaihe).

* **Pure Functions (Synthesis.py Standard):** Matriisien evaluointi tapahtuu puhtailla funktioilla Pythonissa. Koodi kääntää LLM:n palauttamat boolean-arvot numeerisiksi pisteiksi lukemalla scale\_min ja scale\_max rajat suoraan seed-datasta. Sisäkkäiset iteraatiosilmukat (O(N^2)) korvataan suorituskykyisillä O(1) Hash Map / Dictionary \-hauilla.  
* **Matemaattinen Poikkeamien Tunnistus (Strict Math Display Isolation):** scoring.py lukee koodilla lasketut pisteytykset deterministisellä MAD-moottorilla (Median Absolute Deviation) tai valitulla laskentakoukulla (esim. apply\_scoring\_logic). MAD-moottori saa matemaattiset ääriarvonsa tiukasti dynaamisesta PromptBlock-konfiguraatiosta (computed\_min ja computed\_max). Käyttöliittymän visuaalista skaalaa (scale\_min) ei saa koskaan sekoittaa backendin laskentamatematiikkaan.  
* **Resilience Score:** Falsifierin löydökset lasketaan deterministiseksi kestävyysarvosanaksi. Jos suuri osa väitteistä kumotaan, algoritmi asettaa has\_warning \= True \-lipun, joka nostaa raportin esiin Triage-tilassa. Keskihajonnan sisällä oleva data suodatetaan proaktiivisesti pois.

## **\---**

## **4\. Tulosteiden Esitys ja XAI-Käyttöliittymä (Tripartite Rendering Boundary)**

Todennetun datan ("Chain of Custody") on näyttävä loppukäyttäjälle saumattomasti ja identtisesti PDF-raportissa sekä Flutter-käyttöliittymässä. Järjestelmä noudattaa absoluuttista eristystä backend-logiikan, käyttöliittymän (Frontend/Flutter) ja PDF-generaattorin (Jinja2) välillä (**Tripartite Boundary**). Järjestelmä noudattaa **Zero-Math UI**, **Anemic Routers** ja **HTML-First** \-mandaattia.

### **A. Anemic Routers ja Tietovuotojen Esto (Data Leak Firewall)**

* **Reitittimien puhtaus (anemic\_routers):** FastAPI-reitittimet ovat täysin "aneemisia" ja käsittelevät ainoastaan HTTP-liikenteen vastaanoton. Liiketoimintalogiikkaa tai inline-skeemoja ei sallita reitittimissä (Pydantic Namespace Collisions), vaan ne tuodaan models/-kansiosta.  
* **Strict Dependency Injection & Imports:** Palvelut ladataan FastAPI:ssa yksinomaan Depends() \-mekanismin kautta. Asetukset ladataan tiedoston alussa (Global Settings Import). Inline-importteja ei sallita (**No Inline Imports**).  
* **Zero ORM Bleed & Data Leak Prevention:** Tietokantakerros palauttaa logiikalle vain puhtaita Pydantic-malleja; raa'at ORM-objektit eivät vuoda ulos. Jokaiseen endpointiin on määritettävä pakollinen response\_model (periytyen BaseResponseDTO:sta) estäen ylihaun (over-fetching) ja tietojen vuotamisen.

### **B. PDF:n ja Käyttöliittymän Absoluuttinen Pariteetti ("No-String L10N Mandate")**

* Backend erittelee evidence\_type-kentän avulla deterministisesti, mihin tekoälyn tekemä päätelmä perustuu (esim. EvidenceType.explicit\_match).  
* **Absoluuttinen kielto backendin tekstigeneroinnille (no\_string\_l10n):** Backend ei saa koskaan palauttaa rajapinnan yli valmiita, ihmisen luettavia näyttötekstejä, virheilmoituksia tai Markdown-taulukoita. Se palauttaa UI:lle ja PDF:lle yksinomaan tiukkoja Pydantic Enum- ja Literal-vakioita.  
* **Cross-Language Enum Parity:** Backendin Pydantic Enum/Literal \-muuttujien on oltava täydellisessä **1:1 pariteetissa** Flutterin Dart 3 Enum-määrittelyjen kanssa. Kaikki esitystekstit, käännökset ja visuaaliset badget ratkaistaan vain UI:n ja PDF:n lokaalien .arb / kielitiedostojen ja seed datan translations-kenttien kautta.

### **C. UI-Driven Synthesis Boundary & Data-Driven Layouts**

* Backend päättelee seed datan output\_profiles.layouts \-määrittelyistä, mitä näkymiä käyttöliittymä vaatii (esim. preset\_view: "3d\_matrix" tai "text\_only"). AI-raportointi ja DTO-kokoaminen suodatetaan backendissä jo ennakkoon tiukasti pyytävän UI-profiilin (esim. "Holistic Audit") visible\_extensions \-vaatimusten mukaisesti, jotta estetään sellaisten datarakenteiden ja tokenien renderöinti, joita ei esitetä.  
* **Triage-tila:** Jos algoritmi asettaa raportille has\_warning \= True \-lipun, Flutter-työpöytäkäyttöliittymän työnkulku-dashboard siirtyy välittömästi **Triage-tilaan** visuaalisilla varoitusväreillä osoittaen Falsifioijan löytämät puutteet.

### **D. Identtinen Renderöinti: PDF ja UI (Tripartite Synchronization)**

* **Yhteinen ReportDataDTO:** Backend rakentaa yhden, kattavan ja 100 % validoidun ReportDataDTO:n. Se sisältää vain rakenteellista dataa: numeeriset pisteet, vahvistetut lainaukset (evidence\_quotes), asiantuntijasolmujen kategoriat ja XAI Reporter \-agentin tuottaman tiukan tekstisynteesin.  
* **Renderöinnin Pariteetti:** Sekä Jinja2-PDF-moottori että Flutter-käyttöliittymä lukevat **tismalleen samaa** ReportDataDTO-vastausta. Kun data osoittaa preset\_view: "3d\_matrix", sekä Flutter että PDF piirtävät komponentit omien natiivien moottoreidensa kautta datan perusteella niin identtiseksi kuin teknologisesti on mahdollista (PDF käyttää esim. headless Python \-kuvakirjastoja tai SVG-generointia).  
* **XAI-Akkordeonit ja Todistelaatikot:** Todennettu data injektoidaan esityskerroksessa natiiveihin komponentteihin (kuten Flutterin MatrixObservabilityAccordion ja xai\_evidence\_box.dart). PDF renderöi nämä täsmälleen vastaavilla Jinja-makroilla. Visuaalinen laatikko (Evidence Box) näyttää asiantuntijan reasoning\_trace-päätelmän ja sen alapuolella alkuperäisen koodilla todennetun lainauksen.  
* **Kattava Matriisikoontitaulukko:** Jinja2 lukee DTO:n evaluations-listan ja generoi dokumentin loppuun taulukon, joka rinnastaa tasot, LLM:n tuottamat lyhyet perustelut sekä nimenomaan Falsifioijan nostamat koodilla vahvistetut vastaväitteet (critical\_quote).

## **5\. Liiketoiminnallinen ja Teknologinen Arvo (ROI)**

1. **Zero Hallucination Proof (Täydellinen Auditoitavuus):** Fail-Fast hydrataatio, kooditason "Exact Match" \-validointi ja Null Hypothesis \-mandaatti takaavat absoluuttisesti, että tekoäly ei voi hallusinoida tai keksiä lähteitä. Jokainen väite on aukottomasti osoitettavissa alkuperäisestä asiakirjasta kooditason varmuudella.  
2. **Red Teamingin Maksimointi (Kognitiivinen Stressitesti):** Kun mekaaninen auditointi ja BARS-matematiikka siirtyvät raskaalta LLM:ltä puhtaalle deterministiselle Python-koodille (Code-as-a-Judge), tekoälyn kognitio vapautuu toimimaan aitona vastaväittäjänä ulkoista MCP-dataa hyödyntäen.  
3. **Kustannusten ja Suorituskyvyn Eksponentiaalinen Optimointi:** Tyyppiturvallinen asynkroninen Python-koodi (Arq) ja Topologinen DAG-orkestrointi ottavat raskaat vertailut haltuun, poistaen API-jumiutumiset, 400-virheet ja FastAPI-säikeen blokkaukset. O(1)-tason hash-haut ja Smart Token Shield pitävät prosessoinnin salamannopeana ja LLM API \-kustannukset minimissä.  
4. **Teknisen Velan Nollaaminen (Elinikäinen Ylläpidettävyys):** Seed data toimii absoluuttisena totuuden lähteenä koko arkkitehtuurille. Single Source of Truth, duct tape \-virheiden nielujen kielto, täysi tyyppiturvallisuus (strict Pydantic V2 Rust), skeemapohjainen reititys ja täydellinen eristys käyttöliittymän sekä PDF-renderöinnin (Tripartite Boundary) välillä tekevät koodikannasta murtumattoman. Logfire-telemetria mahdollistaa välittömän "Telemetry-First" \-kehityksen ja mahdollisten hallusinaatiopoikkeamien tunnistamisen ennen kuin ne etenevät asiakkaalle.