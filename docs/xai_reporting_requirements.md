# XAI-Analytiikan Vaatimusmäärittely ja Luotettavuussuunnitelma

Tämä vaatimusmäärittely kokoaa yhteen "Courtroom 3.0" -arkkitehtuurin asiantuntija-agenttien tuottamien mittareiden alkuperän, tavoitearvot sekä strategiat datan laadun ja graafisten esitysten parantamiseksi tulevissa kehitysvaiheissa.

## 1. Mittarit ja Laskentaperusteet

Tekoälyagentit (Specialistit) lukevat keskustelulokia ja arvioivat sitä tiukkojen tieteellisten ja kognitiivisten rubriikkien kautta.

### 1.1 Logiikka ja Kognitio (Logician Agent)

Logiikka-asiantuntija arvioi käyttäjän tekstin syvyyttä ja argumentoinnin tasoa.

| Mittari | Asteikko | Kuvaus ja Laskentatapa |
| :--- | :---: | :--- |
| **Bloom Score** | 0.0 – 6.0 | Perustuu Bloomin taksonomiaan. Agentti analysoi aloitteen verbien ja konseptien vaativuutta. (esim. 1 = Muistaminen/Listaus, 6 = Luominen/Uuden syntetisointi). |
| **Toulmin Score** | 0.0 – 6.0 | Perustuu Toulminin argumentaatiomalliin. Agentti purkaa viestin osiin (Väite, Peruste, Tae, Tuki, Varaukset) ja pisteyttää rakenteen eheyden. |
| **Strategic Depth** | 1.0 – 4.0 | Arvioi strategista horisonttia: 1 = Reaktiivinen/Operatiivinen, 2 = Taktinen, 3 = Strateginen, 4 = Visionäärinen/Systeeminen. |

### 1.2 Kausaalisuus ja Uskottavuus (Causal Analyst & Falsifier)

Nämä asiantuntijat testaavat skenaarioita poikkeamien ja vinoumien havaitsemiseksi.

| Mittari | Asteikko | Kuvaus ja Laskentatapa |
| :--- | :---: | :--- |
| **Abductive Score** | 1.0 – 3.0 | Abduktiivinen päättely (parhaan selityksen päätteleminen havainnoista). 1 = Heikko, 2 = Kohtalainen, 3 = Vahva. |
| **Plausibility Score** | 1.0 – 3.0 | Vastaesimerkin (Counterfactual) uskottavuus. Agentti simuloi "mitä jos" -tilanteen ja arvioi sen realistisuuden. |
| **Fidelity Score** | 1.0 – 3.0 | Stressitestin "Uskollisuus" (Fidelity). Kuinka hyvin alkuperäinen tulkinta kestää tekoälyn Falsifier-agentin tekemän hyökkäyksen. 1 = Matala, 3 = Korkea. |

### 1.3 Performatiivisuus (Detector Agent)

Tunnistaa, onko käyttäjän teksti aitoa pohdintaa vai mekaanista "suorittamista".

| Mittari | Asteikko | Kuvaus ja Laskentatapa |
| :--- | :---: | :--- |
| **Authenticity Score** | 1.0 – 3.0 | 1 = Suorittava (Performative), 2 = Epäselvä, 3 = Aito/Orgaaninen (Organic). Lasketaan heuristiikan perusteella (löytyykö liiallista jargonia, itsekritiikin puutetta jne.). |

### 1.4 Kuskin Profiili (Profiler Agent)

Analysoi käyttäjän valtasuhdetta ja ohjausmandaattia tekoälyn kanssa käytävässä vuorovaikutuksessa.

| Mittari | Asteikko | Kuvaus ja Laskentatapa |
| :--- | :---: | :--- |
| **Control Ratio** | 0% – 100% | Ohjaussuhde. Kuinka suuren osan ajasta käyttäjä määrää suunnan vs. antaa tekoälyn viedä. |
| **Imperative Command Count** | Lukumäärä | Suorien käskymuotoisten lauseiden (esim. "Tee...", "Kirjoita...") absoluuttinen lukumäärä. |
| **Role Classification** | Kategoria | "Matkustaja", "Navigaattori", "Kuljettaja" tai "Arkkitehti". Määritetään suhteuttamalla kontrolliratio, käskyjen määrä ja strateginen syvyys toisiinsa. |

---

## 2. Datan laadun varmistaminen ja reunatapaukset

**Miksi näen joskus `null`, `N/A` tai `?` -arvoja (esim. Bloom on 0/6 vaikka teksti oli fiksua)?**  
Tämä on tarkoituksellinen **"Fail-Fast" Data Integrity** -ominaisuus backendissä. Järjestelmä käyttää tiukkoja Pydantic-tietorakenteita varmistaakseen raportin laadun. Jos asiantuntija-agentti (LLM) tuottaa vastausta generoidessaan vääränlaista dataa (esim. kirjaimen numeron sijaan, tai selitteen ilman vaadittua numeroa), järjestelmä "kaatuu hallitusti" vain kyseisen mittarin kohdalla, asettaen sen turvallisesti `null`-arvoksi. Tämä estää koko sovellusta ja raporttia kaatumasta yhteen huonoon LLM-vastaukseen.

**Miksi kontrolliratio voi olla `0%`, mutta rooli silti "Matkustaja" eikä "Invalid"?**  
Jos käyttäjä lähettää pelkän yksittäisen PDF:n ja painaa "Analysoi" ilman ainuttakaan saatesanaa, suorien käskyjen ja aloitteellisuuden määrä on teknisesti 0. Algoritmi tunnistaa tämän passiiviseksi toiminnaksi ja määrittää validisti rooliksi "Matkustajan", jolloin "0" on aito analyyttinen havainto, ei virhe.

**Mitä "Flattened Scores" tarkoittaa?**  
Raportin taustalla lasketaan kymmeniä eri ala-arvoja (kuten "synteesi", "falsification", "agency"). Nämä aggregoidaan ja muunnetaan 0-100 pisteen asteikolle, josta muodostetaan raportin lopullinen pääarvosana (Score Total) sekä "Top Strength" (vahvuus) ja "Top Weakness" (heikkous). Flattened scores on tarkoitettu ulkoisille BI-työkaluille raportoinnin helpottamiseksi.

---

## 3. LLM Datan luotettavuuden parantamisen toimenpiteet (Reliability & Grounding)

Jotta "Fail-Fast" nolla-arvoja syntyisi alun perinkin vähemmän, toteutetaan seuraavat toimenpiteet:

### 3.1 Strict Structured Outputs (esim. OpenAI:n `ResponseFormat`)
Vaikka käytämme Pydantic-mallinnusta, LLM saattaa silti yrittää vastata vapaamuotoisella JSONilla.
- **Toimenpide:** Varmistetaan, että kaikki asiantuntija-agentit (`Logician`, `Causal Analyst`, `Coach` jne.) pakotetaan käyttämään mallin tarjoamaa natiivia "Structured Outputs" -rajapintaa (esim. OpenAI:lle `response_format={"type": "json_schema", "json_schema": ...}`). Tämä poistaa mallilta mahdollisuuden vastata skeeman vastaisesti (esimerkiksi pukata tekstiä numerokenttään) ja **pudottaa `null`-arvojen määrän lähelle nollaa**.

### 3.2 Lämpötilan (Temperature) ja determinismin säätö
Analyyttisten mittareiden arviointi ei vaadi mallilta "luovuutta".
- **Toimenpide:** Asetetaan `temperature = 0.0` kaikkien evaluoivien agenttien (kuten Falsifier, Logician, Overseer) asetuksiin. Tämä tekee tuloksista toistettavia (johdonmukaisia). Luovuutta (korkeampi temperature) tarvitaan vain alkuperäisessä Coach-agentin palautteen muotoilussa.

### 3.3 Fallback-prompptaus (Paremmat "Help"-ohjeet)
Jos malli palauttaa validin numeron mutta ei ymmärrä mitä se arvioi, se saattaa arpoa keskiarvoja (esim. aina 3/6).
- **Toimenpide:** Viilataan järjestelmäprompteja (System Prompt) sisällyttämällä kunkin agentin promptiin lyhyet numeeriset kriteerit *"Esim: Jos väite on vain toteamus ilman lähdettä = toulmin 1.0. Jos siinä on tae ja tuki = toulmin 5.0."*

---

## 4. Graafisten esitysten variointi tulevaisuudessa (Design & UX)

Raportti hyödyntää "UnifiedMetricGauge"-mittareita, mutta grafiikkaa tullaan varioimaan eri analyysityyppien luonteen mukaan:

### 4.1 Tutkamalli (Radar Chart / Hämähäkinverkko)
Kun vertailemme useita eri kognitiivisia mittareita tai käyttäjän heikkouksia/vahvuuksia, Radar Chart on ylivoimainen:
- **Käyttökohde:** "Flattened Scores" (Tiivistetty Data) kokonaisuuden havainnollistamiseen yhteenveto-välilehdellä, jossa käyttäjä voi yhdellä vilkaisulla nähdä "Agency", "Synteesi", "Falsification" jne. akselien painotukset.

### 4.2 Lämmökartta (Heatmap) / Logiikkamatriisi
- **Käyttökohde:** Aikaisemmin käytetty 3D-logiikkamatriisi voidaan korvata 2D "Heatmap" -ruudukkona, missä X-akselilla on strateginen syvyys ja Y-akselilla Bloomin taksonomia. Yksittäinen rasti ruudussa näyttää mihin kvadraanttiin vuorovaikutus sijoittuu (esim. Operatiivinen/Muistava vs. Systeeminen/Luova).

### 4.3 Vuorovaikutteinen Aikajana (Interactive Timeline)
- **Käyttökohde:** "Timeline" eli tapahtumaloki muutetaan visuaaliseksi "Step-by-Step" -jäljeksi, jossa näkyy vertikaalinen graafinen linja, ja hälytykset (esim. Overseerin pysäytys) korostuvat punaisina leikkauspisteinä.

### 4.4 Sentimentti- ja Roolivirtaukset (Sparklines)
- **Käyttökohde:** Pienet, tekstiin upotetut "Sparkline"-viivagraafit, jotka osoittavat askeleittain esimerkiksi sen, tuntuiko käyttäjä alussa matkustajalta ja siirtyikö hän myöhemmin kuskin rooliin.

### 4.5 Tutkamalli (Radar Chart / Hämähäkinverkko)
Kun vertailemme useita eri kognitiivisia mittareita tai käyttäjän heikkouksia/vahvuuksia, Radar Chart on ylivoimainen:
- **Käyttökohde:** "Flattened Scores" (Tiivistetty Data) kokonaisuuden havainnollistamiseen yhteenveto-välilehdellä, jossa käyttäjä voi yhdellä vilkaisulla nähdä "Agency", "Synteesi", "Falsification" jne. akselien painotukset.

### 4.6 Lämmökartta (Heatmap) / Logiikkamatriisi
- **Käyttökohde:** Aikaisemmin käytetty 3D-logiikkamatriisi voidaan korvata 2D "Heatmap" -ruudukkona, missä X-akselilla on strateginen syvyys ja Y-akselilla Bloomin taksonomia. Yksittäinen rasti ruudussa näyttää mihin kvadraanttiin vuorovaikutus sijoittuu (esim. Operatiivinen/Muistava vs. Systeeminen/Luova).

### 4.7 Vuorovaikutteinen Aikajana (Interactive Timeline)
- **Käyttökohde:** "Timeline" eli tapahtumaloki muutetaan visuaaliseksi "Step-by-Step" -jäljeksi, jossa näkyy vertikaalinen graafinen linja, ja hälytykset (esim. Overseerin pysäytys) korostuvat punaisina leikkauspisteinä.

### 4.8 Sentimentti- ja Roolivirtaukset (Sparklines)
- **Käyttökohde:** Pienet, tekstiin upotetut "Sparkline"-viivagraafit, jotka osoittavat askeleittain esimerkiksi sen, tuntuiko käyttäjä alussa matkustajalta ja siirtyikö hän myöhemmin kuskin rooliin.

5 Tooltipit
- **Käyttökohde:** Varmista, että kaikki mittarit ja graafit on varustettu tooltipilla, joka selittää mittarin merkityksen ja laskentatavan. Näiden tooltipien tulisi olla selkeitä ja ytimekkäitä, ja niiden tulisi olla helposti saatavilla klikkaamalla tai hiiren osoittimella mittarin tai graafin päälle. Tooltipien tulisi olla responsiivisia ja toimia sekä mobiili- että työpöytäympäristöissä. Tooltippie käännökset ja kieliversiot on toteutettava .arb lokalisaatioilla suomeksi ja englanniksi.