# **Epic 48: Deterministinen Hierarkkinen Orkestrointi & XAI-Tulostevirta (Shift-to-Code & Map-Reduce)**

## **1\. Yhteenveto ja Arkkitehtuurinen Tavoite (Executive Summary)**

Tämän Epicin tavoitteena on yhdistää **Hierarchical Multi-Agent (Map-Reduce) \-tekoälyarkkitehtuuri** tiukkaan **deterministiseen Python-ohjaukseen (Shift-to-Code)**. Ratkaisemme "Duck-Typing Token Shieldin" aiheuttaman ongelman, jossa kova raakadata piilotetaan loppusynteesiltä Token-rajojen pelossa, pakottaen järjestelmän luottamaan sokeasti välitason LLM-mallien tiivistelmiin.

Siirtämällä tekoälyn tekemä mekaaninen validointi, suodatus ja hallusinaatioiden valvonta puhtaalle Pydantic/Python-koodille, vapautamme asiantuntija-agentit (kuten Falsifioijan) niiden todelliseen tehtävään: **käyttäjän syöttämien väitteiden aktiiviseen kumoamiseen (Red Teaming)**. Järjestelmästä tulee 100 % auditoitava, API-kustannuksiltaan huomattavasti edullisempi ja se kykenee tuottamaan visuaalisesti rikkaita, ohjelmallisesti todennettuja XAI-raportteja (Explainable AI).

## **2\. Nykytilan Pullonkaulat**

1. **Auditoitavuuden menetys kompressiossa:** Kun \_compress\_synthesis\_payload puristaa suoritusketjun pelkkään reasoning\_trace-tekstiin, "Chief Editor" (loppusynteesi) ei näe alkuperäisiä raakalainauksia. Virheet ja hallusinaatiot periytyvät rakenteessa alhaalta ylös.

2. **Kallista tekoälyn ylikäyttöä:** Järjestelmä yrittää ratkaista datan eheyttä käyttämällä LLM-solmuja (kuten Falsifier) tarkistamaan toisten LLM-solmujen työtä. Tämä maksaa tokeneita ja altistaa "Resource Exhausted" (400) \-virheille.

3. **Sokeat tulosteet:** Loppukäyttäjälle esitettävät XAI-raportit nojaavat tekoälyn sanaan, eikä käyttöliittymä pysty visuaalisesti erottamaan todennettua faktaa tekoälyn implisiittisestä päättelystä.

## **3\. Toteutuksen Vaiheet (Implementation Phases)**

### **Phase 1: "Chain of Custody" \- Pydantic-mallien uudistus**

Siirrytään asiantuntijamalleissa (esim. SynthesisStepDataDTO ja StepFalsifierDTO) "Evidence-Based" \-rakenteeseen.

* **Pakotettu todiste:** Jokaiseen asiantuntijasolmun DTO-malliin lisätään pakollinen kenttä evidence\_quotes: list\[str\].

* **Mandaatti:** Aina kun malli esittää väitteen reasoning\_trace-kentässä, sen on pakko nostaa täsmälleen alkuperäistä tekstiä vastaava lainaus evidence\_quotes-kenttään.

### **Phase 2: Exact Match Validator (Hallusinaatiosuoja)**

Poistetaan LLM-pohjaisten laadunvalvontasolmujen tarve raakadatan vertailussa. Tämä vaihe sisältää tietoisen arkkitehtuurisen kompromissin puristisen "Code-as-a-Judge" -determinismin ja PDF-dokumenttien reaalimaailman (OCR-virheet, ligatuurit) välillä DLQ-tulvien estämiseksi.

* **Python Fail-Fast (O(n) Exact Match + RapidFuzz Fallback):** Rakennetaan Pydantic `@model_validator`, joka ottaa asiantuntijamallin palauttaman `evidence_quotes`-taulukon ja suorittaa tekstivertailun alkuperäistä puhdistettua dokumenttia vasten. Validaattori yrittää aina ensin salamannopeaa eksaktia hakua. Vain jos se epäonnistuu, käytetään RapidFuzz-kirjastoa (sumea vertailu CPU-lukkojen välttämiseksi raskaissa dokumenteissa).

* **Dynaaminen Kynnysarvo & Audit-Loki:** Sumean logiikan tuoma "Duck-Typing" -riski minimoidaan skaalaamalla kynnysarvoa (`> 95.0`) dynaamisesti lainauksen pituuden mukaan sekä tarkistamalla sanarajat. Jos osuma on "sumea" (alle 100 %), alkuperäinen lähdeteksti ja mallin tuloste tallennetaan audit-lokiin jäljitettävyyden takaamiseksi.

* **Hylkäys & Circuit Breaker:** Jos LLM on keksinyt lainauksen omasta päästään tai RapidFuzz-tulos jää alle sallitun kynnyksen, Python heittää välittömästi `AppException`-virheen ja Arq-worker pakottaa solmun yrittämään uudelleen. Circuit Breakerin ja uudelleenyritysten maksimimäärä sidotaan tiukasti `SystemConcurrency.LLM_MAX_RETRIES` -vakioon. Jos toisto epäonnistuu kaksi kertaa, prosessi kaatuu lopullisesti.

### **Phase 3: Falsifier-agentin Uusi Rooli (Red Teaming & MCP)**

Valjastetaan vapautunut Falsifier-kognitio käyttäjän datan haastamiseen.

* **Claim Extraction Hook:** Lisätään koukku (extract\_user\_claims), joka poimii käyttäjän syötteestä kovat väitteet Pydantic UserClaim \-listaksi.

* **MCP Tool Loop:** Falsifier lukee asiantuntijasolmun (Step) konfiguraatiosta `allowed_mcp_tools` -kentän. Koska "Tavily AI -haku" on jo valittavissa käyttöliittymän "MCP Gateways" -osiosta, noudatetaan täsmälleen tätä olemassa olevaa prosessia. Jos Stepillä on lupa käyttää hakua (esim. `mcp_tavily_search`), agentti suorittaa haun `await tavily_search(query)` kutsumalla (olemassa oleva `backend_v2.services.mcp.tavily_search_client`), joka palauttaa rakenteellisen `TavilySearchResult` -mallin. Jos väite vaatii ulkoista verifiointia, agentti yrittää kumota käyttäjän väitteen tällä ulkoisella datalla, tallentaen vastaväitteen tiukasti nimettyyn asiantuntijamallin Optional-kenttään `falsifying_evidence: str | None` (ei dynaamisia tai vaihtelevia kenttänimiä).

### **Phase 4: Smart Token Shield (Älykäs Kompressio)**

Uudistetaan \_compress\_synthesis\_payload \-mekanismi.

* **Valikoiva suodatus:** Token Shield pudottaa edelleen pois raskaan kohinan (evaluations, shuffled\_atoms), mutta **päästää läpi reasoning\_trace ja koodilla vahvistetut evidence\_quotes \-kentät**.

* **Escape Hatch:** Falsifierin tuottama critical\_quote ohittaa Token Shieldin karsinnan täysin. "Chief Editor" saa synteesiinsä absoluuttisen tarkat vastatodisteet ilman Token Explosion \-riskiä.

### **Phase 5: Algoritminen Triage ja Resilience Score**

Otetaan analyysin ohjaus pois LLM:ltä koodin haltuun.

* **Matemaattinen Poikkeamien Tunnistus:** scoring.py lukee asiantuntijasolmujen pisteytykset MAD-moottorilla (Median Absolute Deviation). On eksplisiittisen tärkeää, että MAD-moottori ja Triage-arvosanan laskenta saavat matemaattiset ääriarvonsa dynaamisesti luetusta konfiguraatiosta (hyödyntäen `PromptBlock`-mallin `computed_min` ja `computed_max` -arvoja). Tämä estää vääristymät tilanteissa, joissa matriisi ei noudatakaan perinteistä 1-5 asteikkoa.

* **Resilience Score:** Falsifierin löydökset lasketaan deterministiseksi kestävyysarvosanaksi. Jos suuri osa väitteistä kumottiin, algoritmi asettaa has\_warning \= True \-lipun, joka nostaa raportin esiin Triage-tilassa. Keskihajonnan sisällä oleva data suodatetaan proaktiivisesti pois.

## ---

**4\. Tulosteiden Esitys ja XAI-Käyttöliittymä (UI/PDF Rendering)**

Todennetun datan ("Chain of Custody") on näyttävä loppukäyttäjälle saumattomasti. Raportoinnin esityskerros noudattaa tiukkaa **Zero-Math UI** ja **HTML-First** \-mandaattia. Frontend (Flutter) tai PDF-generaattori ei koskaan laske itse tuloksia, vaan renderöi Pydantic-validoitua ReportDataDTO:ta.

### **A. Triage-tila ja Varoitusvärit**

* Jos Phase 5:n algoritmi asettaa raportille has\_warning \= True \-lipun, Flutter-työpöytäkäyttöliittymän työnkulku-dashboard (Dashboard View) siirtyy välittömästi **Triage-tilaan**.

* Raportti merkitään visuaalisilla varoitusväreillä (esim. punainen/oranssi), jotta asiantuntija näkee yhdellä silmäyksellä, että asiakirjassa on Falsifioijan löytämiä kriittisiä puutteita tai kumottuja väitteitä.

### **B. Visuaaliset Fail-Fast Badget ("No-String Mandate")**

* Backend erittelee `evidence_type`-kentän avulla, mihin tekoälyn tekemä päätelmä perustuu.  
* Järjestelmän "No-String Mandate" pakottaa, että backendin `ReportDataDTO` ei saa koskaan lähettää UI:lle valmiita tekstejä. Backend palauttaa yksinomaan tiukan Dart 3 Enumin (esim. `EvidenceType.explicit_match` tai `EvidenceType.implied_intent`).
* Flutter-päässä ja PDF-generaatiossa tekstit ja visuaaliset elementit (badget) ratkaistaan tästä Enumista yksinomaan lokalisoitujen `.arb`-tiedostojen kautta.

### **C. XAI-Akkordeonit ja Todistelaatikot**

* Flutter-käyttöliittymässä todennettu data injektoidaan suoraan MatrixObservabilityAccordion ja xai\_evidence\_box.dart \-komponentteihin.

* Käyttäjä voi klikata auki Falsifioijan tai Tuomarin antaman arvion. Visuaalinen laatikko (Evidence Box) näyttää asiantuntijan reasoning\_trace-päätelmän ja sen alapuolella, visuaalisesti eristettynä, alkuperäisestä tekstistä poimitun ja koodilla todennetun evidence\_quotes-lainauksen. Tämä tuottaa 100 % auditoitavuuden.

### **D. PDF-Raportin Matriisikoontitaulukko**

* Koska PDF generoidaan tismalleen samasta ReportDataDTO-rakenteesta kuin käyttöliittymä, PDF:n loppuun renderöidään automaattisesti **Kattava Matriisikoontitaulukko** (Summary Table).

* Tämä taulukko kokoaa yhteen matriisien tasot (esim. T1-T4), LLM:n tuottamat lyhyet perustelut sekä nimenomaan Falsifioijan nostamat koodilla vahvistetut vastaväitteet (critical\_quote).

## **5\. Liiketoiminnallinen ja Arkkitehtoninen Arvo**

1. **Asiantuntijajärjestelmän Arvon Maksimointi (Stress Test):** Järjestelmä ei vain referoi tietoa, vaan testaa käyttäjän aineiston laadun. Falsifier toimii aitona Red Teaminä hyödyntäen ulkoista MCP-dataa.

2. **Nollahallusinaatio (Zero Hallucination Proof):** Normalisoitu "Exact Match" \-validointi takaa, että LLM ei voi keksiä lähteitä. Raportissa ei ole yhtäkään väitettä, jota ei pystyttäisi osoittamaan sormella alkuperäisestä asiakirjasta.

3. **Kustannusten romahdus:** AI:n omien virheiden valvonta siirtyy ilmaiselle Python-koodille, ja Token Shieldin optimointi säästää miljoonia tokeneita per ajo.

4. **Data-ohjautuva kehitys (Telemetry-First):** Pydantic Logfireen integroitu lokitus paljastaa heti tarkan Fuzz-lokituksen avulla, jos malli alkaa hallusinoida lainauksia.  
