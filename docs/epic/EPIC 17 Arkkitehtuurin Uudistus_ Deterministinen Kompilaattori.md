# **KEHITYSSUUNNITELMA: COGNITIVE QUORUM 2.0 (PRAGMATIC DETERMINISTIC COMPILER)**

**Ydinkonsepti:** Siirretään päätösvalta LLM:n subjektiiviselta "mustalta laatikolta" deterministiselle Python-backendille (Compiler). LLM alennetaan *totuusarvopiirteiden erottelijaksi* (Boolean Feature Extractor), jonka ainoa tehtävä on etsiä empiiristä näyttöä aineistosta. Python-backend lukee nämä piirteet ja laskee lopullisen arvosanan ehdottomalla matemaattisella logiikalla tietokannan JSON-matriisiin (DSL) nojaten. Tämä tuhoaa varianssin, "Say-Do"-kuilun ja tekoälyn myötäilyvinouman.

### ---

**MILESTONE 1: Semanttinen Sanitaatio (Data & Prompt Layer)**

**Tavoite:** Puhdistaa DSL (JSON-matriisit) ja muuttaa LLM:n psykologinen konteksti. Torjutaan "Garbage In, Garbage Out" \-ilmiö, mutta vältetään "Brittle Recall" (liian tiukan haun aiheuttamat väärät negatiiviset tulokset).

* **Task 1.1: JSON-matriisien (DSL) kliininen puhdistus ja joustavuus.**  
  * **Toimenpide:** Kaikki ai\_description \-kentät seed\_data.json \-tiedostossa kirjoitetaan uusiksi. Emotionaalisesti latautuneet ja rankaisevat ohjeet (esim. SEVERE HUBRIS PENALTY) poistetaan, sillä ne aiheuttavat epädeterminististä varianssia mallin piiloavaruudessa.  
  * **Anti-Brittle Recall \-ratkaisu:** Ohjeet korvataan neutraaleilla, mutta riittävän joustavilla tiedonlouhintaohjeilla. LLM:ää ei käsketä etsimään vain "100 % absoluuttista faktaa", vaan ohjeistetaan: *"EXTRACTION DIRECTIVE: Etsi tekstistä kohdat, joissa kirjoittaja esittää subjektiivisen näkemyksen absoluuttisena faktana. Huomioi myös implisiittiset vahvat väitteet, joille ei esitetä perusteita tai varauksia. Jos löydät tällaisen, poimi sanatarkka lainaus."*  
* **Task 1.2: Järjestelmäkehotteen (System Prompt) kääntö.**  
  * **Toimenpide:** Päivitetään prompt\_compiler.py:n injektoima ydinrooli. Mallille kerrotaan suoraan sen uusi asema: *"Olet kliininen, forensinen data-analyytikko. Tehtäväsi on skannata tekstiä ja etsiä täsmällisiä osumia annettuihin kriteereihin. Et tee johtopäätöksiä, etkä jaa arvosanoja. Poimit vain empiirisiä todisteita annetuilla säännöillä."*  
* **Task 1.3: Virhetilojen (Flaws) koneluettavuus.**  
  * **Toimenpide:** Lisätään JSON-matriisien claims-tasolle uusi boolean-lippu "is\_flaw": true niille väitteille, jotka edustavat epäonnistumista tai rangaistavaa puutetta (esim. vastaväitteiden sivuuttaminen). Tämä on elintärkeää Milestone 3:n Fail-Fast \-logiikan automatisoinnille.

### ---

**MILESTONE 2: Käänteinen Skeema ja Y-Funnel Reititys (Interface Layer)**

**Tavoite:** Pakotetaan LLM sitomaan itsensä aineistoon *ennen* totuusarvojen generointia. Ratkaistaan laiskuusongelma puhtaalla ohjaustason arkkitehtuurilla raskaiden asynkronisten JSON-mergejen sijaan.

* **Task 2.1: Dynaaminen AST-Skeemageneraattori (schema\_builder.py).**  
  * **Toimenpide:** Koodataan generaattori, joka lukee puhdistetun JSONin ja rakentaa lennosta tiukan Pydantic V2 \-skeeman create\_model \-funktiolla (extra='forbid'). Arvosanoja ei pyydetä LLM:ltä lainkaan.  
* **Task 2.2: Tietotyyppien tiukka pakotus.**  
  * **Toimenpide:** Jos lohko sallii matemaattiset arvot (allow\_decimals), Pydantic-malliin rakennetaan lennosta tiukka tyyppivihje float ja ohjeistus *"Float numerical value for \[slug\]"*.  
  * Jos LLM yrittää syöttää Chain-of-Thought \-tageja (esim. ||DECIMAL: 3.4||) numerokenttään, normalize\_matrix\_scores\_hook siivoaa ne säännöllisillä lausekkeilla (RegEx) puhtaaksi floatiksi ennen backendin käsittelyä.  
* **Task 2.3: Rakenteellinen pakotus (Property Ordering / Micro-CoT).**  
  * **Toimenpide:** Varmistetaan kooditasolla, että **kolmivaiheinen rakenne pakotetaan:** quotes\_sX\_cY (lainaukset, eli kryptografinen Työntodiste) määritellään Pydantic-mallissa pakollisesti ennen **lyhyttä perustelukenttää (reasoning\_sX\_cY), jotka molemmat on tuotettava ennen** vastaavia is\_true\_sX\_cY (boolean) \-kenttiä. Autoregressiivinen malli ei voi vastata "True" ennen kuin se on fyysisesti etsinyt ja tulostanut tekstistä lainauksen **sekä perustellut lyhyesti, miten lainaus täyttää annetun kriteerin.**  
* **Task 2.4: Laiskuuden ehkäisy Y-Funnel \-arkkitehtuurilla.**  
  * **Haasteen ratkaisu:** Yli 15 väitteen matriisien pilkkominen ja yhdistäminen (Matrix Sharding) lennossa backendissä on liian riskialtista ja moninkertaistaa Token-kustannukset (lähdeteksti on lähetettävä jokaiseen haaraan erikseen).  
  * **Toimenpide:** Toteutetaan pilkkominen Y-Funnel \-mallilla Workflow Studiossa (DAG) **hyödyntäen LLM-rajapintojen tarjoamaa Prompt/Context Caching \-ominaisuutta**. Laajat matriisit (esim. Bloom) jaetaan staattisiksi, peräkkäisiksi Nodeiksi jo työnkulun suunnitteluvaiheessa (esim. Node A: Bloomin tasot 1-3, Node B: Tasot 4-6). **Massiivinen lähdedokumentti ladataan välimuistiin vain kerran työnkulun alussa, jolloin yksittäiset Nodet voivat hakea kontekstin siitä edullisesti ja nopeasti.** Näin LLM saa käsiteltäväkseen vain kapean skeeman kerrallaan, mallin vireystila säilyy, **eivätkä rinnakkaiset API-kutsut räjäytä Token-kustannuksia**. Backendin scoring.py kokoaa lopullisen arvosanan näiden erillisten Nodejen tuloksista puhtaasti loogisella tasolla ohjaimen kautta.

### ---

**MILESTONE 3: Deterministinen Python-Tuomari (Execution Layer)**

**Tavoite:** Siirretään tuomarointi täysin Python-koodille. Asennetaan pragmaattinen suodatin, joka tappaa "Say-Do" \-kuilut murhaamatta aitoja lainauksia OCR-virheiden vuoksi.

* **Task 3.1: Joustava Hallusinaatiosuodatin (integrity.py).**  
  * **Haasteen ratkaisu:** Raaka Levenshtein-etäisyys hylätään, koska se kaatuu PDF-asiakirjojen rivinvaihtoihin ja tavuviivoihin, tuhoten aidot lainaukset.  
  * **Toimenpide:** Toteutetaan **Sliding Window N-gram matching**.  
    1. *Tokenien puhdistus:* Ennen vertailua sekä LLM:n palauttama lainaus että lähdeteksti normalisoidaan armotta (poistetaan välilyönnit, välimerkit, pakotetaan lowercase).  
    2. Toimenpide: Toteutetaan Sliding Window N-gram matching **sekä sitä varajärjestelmänä tukeva kevyt semanttinen vektorivertailu (esim. BM25 tai paikallinen sentence-transformers**  
    3. *Käännös-hallusinaatioiden esto:* Koska N-gram \-suodatin etsii tarkkoja sanajonoja, LLM:n vahingossa englanniksi kääntämät suomenkieliset lainaukset hylätään automaattisesti.  
    4. Vertailu: Etsitään lainauksen N-grammeja (esim. 5–7 peräkkäistä sanaa) lähdetekstistä liukuvan ikkunan avulla. **Jos N-gram \-suodatin ei löydä osumaa, vertailu varmistetaan semanttisella vektorikyselyllä, joka kykenee tunnistamaan oikean lainauksen merkkitason korruptiosta (OCR-piilomerkit) huolimatta.** Tämä sietää OCR-typöt **ja asetteluvirheet**, mutta hylkää täysin keksityt lauseet  
  * **Fail-Fast Trigger:** Jos riittävää N-gram \-osumaa ei löydy, koodi tyhjentää quotes-taulukon ja kääntää kyseisen is\_true \-booleanin deterministisesti False \-tilaan.  
* **Task 3.2: Fail-Fast Tuomari (scoring.py).**  
  * **Toimenpide:** Implementoidaan calculate\_universal\_score \-logiikka, joka lukee JSON-matriisia alhaalta ylös.  
  * Logiikka: Koodi tarkistaa ensin Milestone 1.3:ssa asetetut "Virhetilat" (Flaws). Jos yksikin kriittinen virhetila saa arvon True (ja sille löytyy N-gram \-suodattimen läpäissyt lainaus), **sovelletaan pehmennettyä tuomarointia (Soft Degradation): täyden nollauksen sijaan maksimi arvosanaa leikataan asteittain (esim. \-1.0 per kriittinen puute), jolloin arvostelu skaalasta tulee psykologisesti hyväksyttävämpi.** Ylempien tasojen saavutuksia **mitataan edelleen laadun jatkuvan asteen varmistamiseksi, mutta virhe lukitsee huippuarvosanat tavoittamattomiin**.

### ---

**MILESTONE 4: R\&D ja Tulevaisuuden Ominaisuudet (Nice-to-Have Tier)**

**Tavoite:** Vältetään ylisuunnittelu (over-engineering). Siirretään ominaisuudet, joiden hyöty/kustannus-suhde on huono tai teknologia liian haurasta, suosiolla myöhempään vaiheeseen, jotta kriittinen polku ei hidastu.

* **Hyllytetty: Tiukkuuden AST-mutaatio (min\_length=3).** Dynaaminen pakotus on vaarallista. Jos alkuperäisessä aineistossa aidosti on vain yksi relevantti lause, järjestelmä pakottaisi LLM:n hallusinoimaan lisälauseita tai kaataisi JSON API \-kutsun (422 ValidationError). Tiukkuutta ohjataan matriisien sisällöllä, ei keinotekoisilla määrillä.  
* **Hyllytetty: Red Team Sabotööri & Cosine Similarity.** Useiden agenttien ajaminen rinnan tilaromahduksen havaitsemiseksi on liian hidasta ja kolminkertaistaa API-kustannukset. Deterministinen Python-tuomari eliminoi "Goodhartin lain" huijaukset jo pakottamalla empiiriset todisteet.  
* **Hyllytetty: Episteeminen Tiheys (NLP).** Leksikaalisen tiheyden ja kausaalisten konjunktioiden laskenta spaCy:lla toimii heikosti suomen kielen aggregaattisissa substantiivimuodoissa. Vakion $D$ laskenta IRT-normalisointia varten vaatisi hienosäädettyä koneoppimismallia. Lineaarinen Zero-Math \-normalisointi pidetään toistaiseksi tunnistettuna kompromissina.

### ---

**STRATEGINEN TOTEUTUS JA JULKAISU (DEPLOYMENT)**

Arkkitehtuurimuutos viedään tuotantoon vaiheistaen, jotta asiakkaiden historiallinen data ja XAI-raportit eivät korruptoidu takautuvasti.

1. **Tietokannan Versiointi (DSL Versioning):** Luodaan matriiseista uudet versiot (esim. seed\_data\_v2.json). Vanhat työnkulut reititetään historiadataa haettaessa edelleen V1-moottoriin.  
2. **Shadow Deployment (Varjoajo):** Rakennetaan uusi UniversalV2Compiler täysin eristettynä. Tuotannossa asiakkaalle näytetään toistaiseksi V1-tuomarin tulokset, mutta taustalla Arq Worker ajaa äänettömästi uuden V2-moottorin samaa dataa vasten analytiikkakantaan.  
3. **Delta-Analyysi (Kalibrointi):** Vertaamalla V1- ja V2-tuloksia (Delta) nähdään, kuinka paljon vanha malli antoi perusteetonta etua. Varjoajon aikana N-gram \-suodattimen kynnysarvo kalibroidaan optimaaliseksi OCR-virheiden ja hallusinaatioiden välimaastoon (esim. 80 % token-osumaprosentti riittää).  
4. **Asteittainen Julkaisu:** V2-moottori kytketään päälle yhdelle selkeälle matriisille kerrallaan (esim. aloittaen Toulminista), testataan tuotannossa ja laajennetaan muihin.

### ---

**VAIKUTUKSET LIIKETOIMINTAAN JA ODOTUSTEN HALLINTA**

Tämä siirtymä muuttaa työkalun luonnetta radikaalisti. Seuraavat ilmiöt on viestittävä asiakkaille ennakkoon järjestelmän **ominaisuuksina, ei bugeina**:

**1\. Arvosanojen deflaatio (Illuusion särkyminen):**

Aiemmin LLM saattoi antaa säälistä arvosanan 4 ("Hyvä") sujuvan tekstin perusteella, vaikka kovat kriteerit puuttuivat. Uudessa mallissa Fail-Fast Tuomari lukitsee arvosanan säälimättä tasolle 2, jos Tason 3 todiste (lainaus) puuttuu tai ei läpäise N-gram suodatinta. Asiakkaiden on ymmärrettävä, että 5.0 edustaa jatkossa aidosti teoreettista täydellisyyttä, ja 3.0 on uusi normaali ammattimainen suoritus.

**2\. Tekoäly-fluffin armoton paljastuminen:**

Laiskasti generoidut, itsevarmat pinta-analyysit lukittuvat välittömästi "Hubris"-virhetilaan (Arvosana 1), koska niistä puuttuu episteeminen nöyryys ja kognitiivinen kitka. Quorumista tulee markkinoiden tarkin työkalu tekoälyllä tuotetun katteettoman sisällön paljastamiseen.

**3\. Varianssin kuolema (Oikeudellinen toistettavuus):**

Saman tekstin ajaminen 100 kertaa järjestelmän läpi tuottaa 100 kertaa täsmälleen saman arvosanan. LLM:n "fiilispohjainen" satunnaisuus katoaa, tehden auditoinneista kliinisen toistettavia.

**4\. XAI muuttuu todistusaineistoksi:**

XAI-raportti ei ole enää LLM:n keksimä narratiivi (post-hoc rationalisointi). Raportti generoidaan suoraan Pythonin totuustaulusta: *"Arvosana lukittiin tasolle 2, koska tason 3 ehto 'Vastaväitteet' jäi täyttymättä. Tekoäly poimi lainauksen, mutta N-gram \-suodatin hylkäsi sen, koska tekstiä ei löytynyt alkuperäisestä dokumentista."* Tämä tekee raporteista kiistattomia compliance-dokumentteja Enterprise-asiakkaille.