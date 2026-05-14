# **Epic 51: TDA Knowledge Grounding & Seed Data Refactor (Antigravity Master Mandate)**

## **1\. Yhteenveto ja Tavoite (Objective)**

Tämän Epicin tavoitteena on suorittaa **"Kognitiivinen Siivous" (Cognitive Cleanup)** koko järjestelmän ytimeen. Nykyinen tietokantadata (backend\_v2/seed/seed\_data.json) on jäänne V1-ajalta ja se on refaktoroitava vastaamaan V4-tason TDA-arkkitehtuuria (Test-Driven Assertion). Jokainen arviointikriteeri muutetaan huipputarkkaan XML-hybridimuotoon ja jaetaan tasan 3 mikrotason matemaattisesti todennettavaan EHDOTTOMASTI TDA-väitteeseen (MECE-periaate).

\[\!WARNING]

**Historiallinen Konteksti ja V4-Kovetus (Zero-Interpretation Doctrine):**

Epic 52:n jälkeen suoritettu ristiinajotestaus paljasti yhä **19.6 % haamuvarianssia** kahden identtisen ajon välillä. Analyysi paljasti tämän johtuvan kolmesta juurisyystä:
1. **Leksikaalisen ankkurin ohittaminen:** LLM tulkitsee "henki vs. kirjain" -periaatteella ja hallusinoi osumia ilman tarkkaa sanamuotoa.
2. **Polariteettisekaannus:** LLM hämmentyy FATAL FLAW -kriteereissä (Vice/Virtue) siitä, onko löydös sääntörikkomus vai säännön täyttyminen.
3. **Subjektiivinen intentiotulkinta:** Säännöt, jotka pakottavat arvioimaan tekijän tarkoitusta (esim. "onko muutos vain rakenteellinen"), johtavat mielivaltaisiin tuloksiin.

Tästä syystä tämä Epic nojaa ehdottomaan Zero-Interpretation -doktriiniin: Sääntöjä on käsiteltävä ikään kuin ne olisivat säännöllisiä lausekkeita (Regex). Kielimallilta EVÄTÄÄN oikeus kognitiiviseen tulkintaan (ACCEPT/REJECT -logiikka kielletty!), ja sille annetaan vain oikeus suorittaa tarkka poiminta (EXTRACT EXACT QUOTE).

**Definition of Done (DoD):**

* Koko seed\_data.json käyttää \<system\_directive\>-XML-rakennetta makrotasolla.  
* Jokaisessa solussa on **tasan 3** toisistaan riippumatonta TDA-väitettä.  
* Determinismi-aste ylittää 100,0 % ristiinajoissa (0 % haamuvarianssi).  
* Järjestelmä läpäisee Pydantic-validoinnin, verify\_claims.py -testit sekä backend\_audit\_loop.py -varmistuksen.

## **\---**

## **2\. Arkkitehtuuriset Mandaatit (Sequential 1–21)**

### **Osa A: Kognitiivinen Logiikka ja Päättelyvarmuus**

1. **Sääntö 1: Chunk-turvallinen käänteislogiikka (The Absence Paradox):** Fatal Flaw -kriteerien (inverse\_evidence: true) on materialisoiduttava aktiivisena virheenä (commission). AI ei saa koskaan etsiä tyhjiötä tai puutetta.  
2. **Sääntö 2: Lattialogiikan matematiikka (Floor vs. Ceiling Logic):** Tasojen 1 ja 2 positiiviset vaatimukset muotoillaan inklusiivisella "lattia-logiikalla", ei poissulkevalla "vain"-logiikalla.  
3. **Sääntö 3: "Palkkionmetsästäjä"-paradigma (Fatal Flaw over Consistency):** Kaikki johdonmukaisuutta vaativat säännöt on käännettävä inverse\_evidence: true -tuhoamismoodiin.  
4. **Sääntö 4: Yksinapainen looginen portti (Boolean Integrity):** Väitteet ovat yksinapaisia. Ei AND/OR-lausekkeita tai kaksoiskieltoja.  
5. **Sääntö 5: Chain-of-Thought (CoT) pakotus:** LLM on pakotettu perustelemaan looginen ketjunsa JSONin reasoning\_trace-kenttään *ennen* lainauksen poimimista.

### **Osa B: Zero-Interpretation ja Roolit (V4.1-Kovetus Haamuvarianssia Vastaan)**

6. **Sääntö 6: Subjektiivisten adjektiivien ja intentiotulkinnan kielto (The Ban of Subjectivity):** Laatusanat ja intentioiden arviointi (esim. "onko muutos vain sävyä") on EHDOTTOMASTI kielletty. Korvaa ne mekaanisilla kynnyksillä.
6.1. **Sääntö 6.1 (UUSI): ACCEPT/REJECT -kielto (The Ban of Cognitive Booleans):** Säännöissä EI SAA KÄYTTÄÄ "If X -> ACCEPT, otherwise -> REJECT" -rakenteita. Korvaa ne aina mekaanisella poiminnalla: `"EXTRACT EXACT QUOTE IF AND ONLY IF THE EXACT WORDS [X, Y, Z] ARE PRESENT. IF MISSING, RETURN NULL."`
7. **Sääntö 7: Ehdoton rooliautentikointi (Strict Role & Field Attribution):** Säännössä on EHDOTTOMASTI määriteltävä puhujan rooli ja sidottava se roolietuliitteisiin (user:, ai:).  
8. **Sääntö 8: Bounding Boxes (Anti-Laziness):** Harvinaisia lauseita etsittäessä skannaus on pakotettava fyysisiin rajauslaatikkoihin (esim. Markdown-otsikoiden väliin).  
9. **Sääntö 9: Eksplisiittiset poissulkulistat (Anti-Proxies):** Jokaiseen käsitteelliseen väitteeseen on sisällytettävä BANNED CONCEPTS -lista termeistä, joita ei saa hyväksyä osumiksi.  
10. **Sääntö 10: Leksikaaliset indikaattorit (Lexical Proxies):** Abstraktit konseptit on ankkuroitava fyysisiin siirtymäsanoihin (esim. 'however', 'therefore'). LLM ei saa tulkita näitä "hengen" mukaan, vaan ankkurin on löydyttävä EKSPLISIITTISESTI sanasta sanaan.
11. **Sääntö 11: Imperatiivinen käskymuoto (Actionable Directives):** Mikrotason sääntö ei saa olla kysymys. Sen on alettava toimintaverbillä (esim. Extract, Locate).

### **Osa C: Teoreettinen Ankkurointi ja Grounding**

12. **Sääntö 12: Teoreettinen ankkurointi (No Hollow Structures):** Jokaisen TDA-väitteen on nojattava todelliseen teoriaan (esim. Kahneman, Floridi, Toulmin).  
13. **Sääntö 13: Pakollinen tiedonhaku ja Syväteoreettinen Ohjaus:** Käytä search\_web-työkalua hakeaksesi täsmälliset teoriatermit.  
14. **Sääntö 14: Few-Shot Anti-Patternien injektointi:** Tarjoa yksi mikroskooppinen reaalimaailman esimerkkilause siitä, miltä virhe näyttää käytännössä.  
15. **Sääntö 15: Universal Language Protocol & Natiivikielen Skannaus:** Kaikki AI-promptit kirjoitetaan 100 % englanniksi. Dokumentti skannataan sen natiivikielellä etsimällä vastineita leksikaalisille indikaattoreille.

### **Osa D: Tekniset Standardit ja Pydantic-hallinta**

16. **Sääntö 16: Opaque Stripe ID \-mandaatti:** Kaikkien sääntöjen tda\_id on oltava 16-merkkinen satunnainen heksadesimaali muotoa tda\_ \+ \[a-f0-9\]{16}.  
17. **Sääntö 17: Pydantic-aggregaatio ja Fail-Fast:** Jos inverse\_evidence on true, aggregation\_mode on oltava EHDOTTOMASTI "EXISTS".  
18. **Sääntö 18: Anti-Token Bloat & Hybrid Prompting:** XML-tagit (\<system\_directive\>) sijoitetaan VAIN ylätason ai\_description-kenttään.  
19. **Sääntö 19: Turvallinen JSON-manipulaatio:** Muutokset seed\_data.json-tiedostoon on tehtävä ainoastaan lokaaleilla Python-skripteillä.  
20. **Sääntö 20: 100 % Kattavuusvaatimus (Comprehensive Traversal):** Agentin on refaktoroitava matriisin jokainen pistetaso (1–5) ja jokainen väite (claim) kattavasti.  
21. **Sääntö 21: Tracker-suvereeniys:** epic51\_matrix\_tracker.md on ainoa lähde totuudelle.
22. **Sääntö 22: Pydantic Schema Integrity (ai\_description -suojelu):** Jokaisella väitteellä (claim) ON PAKKO säilyttää `ai_description`-kenttä. Refaktorointiskripti ei saa vahingossa poistaa sitä. Sisällön tulee olla alkuperäinen ohje (tai "CRITICAL DIRECTIVE: {en_label}"). Jos tämä poistetaan, `run_seed.py` kaatuu 15 validation erroriin.

## **\---**

## **3\. Agent Execution Protocol (Mandatory Sequence)**

Tämä on ehdoton suoritusjärjestys jokaiselle tekoälyagentille. Yhdessä konteksti-ikkunassa käsitellään **VAIN YKSI MATRIISI**.

**MANDATORY AUDIT RULE:** Suorita scripts\\backend\_audit\_loop.py \[TIEDOSTOT\] \--test \--openapi EHDOTTOMASTI jokaisen pienenkin muutoksen jälkeen varmistaaksesi koodin ja skeemojen rakenteellisen eheyden.

**SUORITUSLOOPPI:**

1. **Target Selection:** Avaa epic51\_matrix\_tracker.md. Valitse ensimmäinen \[NOK-V3\] tai \[NOK\] \-merkitty matriisi.  
2. **Context Loading:** Lataa kyseinen blokki tiedostosta backend\_v2/seed/seed\_data.json.  
3. **Pre-Flight Checklist:** AI TULOSTAA vahvistuksen chattiin: *"Säännöt 4, 6 ja 9 ladattu huomioikkunaan."*  
4. **Execution:** Generoi lokaali Python-skripti (esim. scratch/refactor.py) päivittämään blokki ja aja se.  
5. **Quality Gate:** Aja järjestelmän päätteessä tismalleen tämä komentosarja:  
   uv run python scratch/verify\_claims.py; uv run pytest backend\_v2/tests/unit/test\_seed\_architectural\_guardrails.py backend\_v2/tests/unit/test\_matrix\_data\_integrity.py \-v; scripts\\backend\_audit\_loop.py scratch/refactor.py \--test \--openapi  
6. **Post-Flight Audit:** Tulosta Osan 4 mukainen 10-kohdan raportti.  
7. **Halt:** Lopeta vuoro ja anna komento:  
   /tier5-resume \--target docs/epic/epic51\_matrix\_tracker.md \--docs docs/epic/epic51\_seed\_data\_tda\_refactor.md

## **\---**

## **4\. Pakollinen Mandaatti-Audit (Loppuraportti)**

AI raportoi nämä 10 kohtaa jokaisen matriisin refaktoroinnin jälkeen:

* [ ] **1. Teoriainjektio:** Käytetty teoria ja sen injektiotapa.  
* [ ] **2. Käänteis- ja Lattialogiikka:** Miten säännöt 1 ja 2 toteutettiin.  
* [ ] **3. Boolean & Bounty Hunter:** Vahvistus yksinapaisuudesta.  
* [ ] **4. CoT-perustelu:** Miten reasoning\_trace pakotettiin.  
* [ ] **5. Subjektiivisuuden kielto (Säännöt 6 & 6.1):** ACCEPT/REJECT -logiikan ja intentiotulkinnan tuhoaminen, vahvistus EXTRACT EXACT QUOTE -käytöstä.
* [ ] **6. Rooliautentikointi:** Roolien ankkurointi (user:/ai:).  
* [ ] **7. Sanasto ja Laiskuus:** Indikaattorit, Anti-Proxies ja Bounding Boxit. Leksikaalisen ankkurin ehdoton pakotus (Sääntö 10).
* [ ] **8. Opaque ID & Aggregaatio:** Satunnaiset heksat ja EXISTS-tila.  
* [ ] **9. 100 % Kattavuus:** Vahvistus kaikkien pisteiden (1–5) käsittelystä.  
* [ ] **10. ai\_description eheys:** Vahvistus, että claim-tason `ai_description` on säilytetty ja Pydantic V2 ei kaadu.
* [ ] **11. Auditointi-varmistus:** Vahvistus, että scripts\backend\_audit\_loop.py on ajettu generoidulle skriptille onnistuneesti.

## **\---**

## **5\. Tietokannan Nollaus ja Quality Gate (Human/System Step)**

\[\!CAUTION]

**EHDOTON SÄÄNTÖ:** Tätä vaihetta EI SAA SUORITTAA ennen kuin **jokainen** matriisi Trackerissä on tilassa \[OK\].

Kun koko Tracker on puhdas, aja seuraavat komennot:

1. **Seedaus lokaaliin kantaan:**  
   Bash  
   uv run python backend\_v2/seed/run\_seed.py local

2. **Lopullinen Rakenteellinen Audit:** Varmistetaan Pydantic-skeemojen validiteetti ja rakenteellinen eheys koko backendin tasolla.  
   Bash  
   scripts\\backend\_audit\_loop.py backend\_v2/ \--test \--openapi  
