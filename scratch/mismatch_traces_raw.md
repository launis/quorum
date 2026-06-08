# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ajo-tiedot (Runs)
- **Run 1:** `exe_48becd4457204494a1077e8613484371` (Lähde: [data/files/executions\exe_48becd4457204494a1077e8613484371\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_48becd4457204494a1077e8613484371/execution_trace.json))
- **Run 2:** `exe_cafdf41ad11647469309ed93f9d741d3` (Lähde: [data/files/executions\exe_cafdf41ad11647469309ed93f9d741d3\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_cafdf41ad11647469309ed93f9d741d3/execution_trace.json))
- **Run 3:** `exe_2474eae8395b45eda419d76d67208280` (Lähde: [data/files/executions\exe_2474eae8395b45eda419d76d67208280\execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_2474eae8395b45eda419d76d67208280/execution_trace.json))

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 3
- **Yhteisten arvioitujen atomien määrä ($N$):** 185
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 82.70 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.6480
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Keskimääräinen Shannonin Entropia:** 0.2383
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 34 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 0 / 48
- **PASSED -> FAILED:** 13
- **FAILED -> PASSED:** 21
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_bfef1f4b769c426fb5707495db43a6e1` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find affirmative acceptance phrases by the user (e.g., 'looks good', 'thanks', 'perfect'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user accepts an AI output without requesting a single structural or logical change. NEGATIVE CONDITION (RETURN NULL IF MET): the user requests a modification. Do not evaluate if the response was actually 'good'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä pyytää muutoksia tekoälyn tuotokseen (muistioformaatti, kieli, pituus, johdanto), mikä täyttää negatiivisen ehdon 'the user requests a modification'. Siksi hyväksyvää lausetta ilman muutoksia ei löydy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Käyttäjä käyttää hyväksyvää fraasia 'Hyvä.', mutta välittömästi sen jälkeen pyytää tekoälyä toimimaan 'paholaisen asianajajana' ja antamaan 'säälimätöntä kritiikkiä omalle ehdotukselleen'. Tämä on merkittävä looginen muutos ja uusi tehtävä, ei edellisen tuotoksen hyväksyntä ilman muutoksia. Siksi negatiivinen ehto ('the user requests a modification') täyttyy, ja sääntö rikkoutuu.. Exceptions audit: Käyttäjä antaa hyväksynnän ('Hyvä.'), mutta pyytää välittömästi muutosta ('Toimi nyt paholaisen asianajajana ja anna säälimätöntä kritiikkiä omalle ehdotuksellesi.'), mikä laukaisee negatiivisen ehdon.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä antaa hyväksynnän ('Hyvä'), mutta pyytää välittömästi perään rakenteellista/loogista muutosta ('Toimi nyt paholaisen asianajajana ja anna säälimätöntä kritiikkiä omalle ehdotuksellesi'). Tämä laukaisee negatiivisen ehdon, joten atomi ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_34259a6c02b74917b12f74b5f3839a66` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers ('is the best', 'must be done', 'is the only way'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. EXTRACTION CONDITION: no empirical data or external reference exists in the same paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): data exists.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt dogmaattisia absoluuttisia merkitsijöitä (kuten 'on paras', 'on ainoa tapa', 'on pakko tehdä'), jotka esiintyisivät ilman empiiristä dataa tai ulkoista viittausta samassa kappaleessa. Ehdotus perustuu tutkimustietoon, ja esitetyt tavoitteet ovat pyrkimyksiä, eivät absoluuttisia väitteitä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Etsin `product_text`-lähteestä dogmaattisia absoluuttisia merkitsijöitä, kuten 'on paras', 'on pakko tehdä' tai 'on ainoa tapa', joiden yhteydessä ei olisi empiiristä dataa tai ulkoista viittausta samassa kappaleessa. Teksti käyttää ilmauksia kuten 'suosituksena on' ja 'tavoitteena on', jotka ovat suosituksia ja tavoitteita, eivät dogmaattisia absoluutteja. Lisäksi monet väitteet perustellaan suoraan tutkimustiedolla (esim. 'perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon'), mikä rikkoisi poimintaehdon, jos absoluuttinen merkitsijä löytyisi.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Etsin dogmaattisia absoluuttisia merkkejä, kuten 'on paras', 'on pakko tehdä' tai 'on ainoa tapa'. Löysin lauseen 'Tämä on varma tapa myrkyttää työilmapiiri.' AI:n 'paholaisen asianajaja' -vastauksesta. 'Varma tapa' vastaa absoluuttista merkkiä. Tarkistin, ettei samassa kappaleessa ollut empiiristä dataa tai ulkoista viittausta, ja sellaista ei löytynyt. Siksi negatiivinen ehto ei täyttynyt ja lainaus poimittiin.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_ce2566987e8f44819102d6eb1d28857d` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag open-ended questions explicitly left for future research. STEP 1 (Syntactic Anchor): Find a question mark '?' used by the author to question their own premise. STEP 2 (Bounding Box): Scan the following 2 sentences. If the author answers their own question confirming the premise without citing new data. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Tekijä (ai) esittää kysymyksen omasta premissistään ("Voiko niihin luottaa?") ja vastaa siihen kahdella seuraavalla lauseella vahvistaen premissin ("eivät ole mututuntumaa tai tekoälyn keksimiä arvauksia. Ne perustuvat laajaan, tuoreeseen kotimaiseen ja kansainväliseen tutkimustietoon...") ilman, että näissä kahdessa lauseessa esitetään uutta, aiemmin mainitsematonta dataa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Kirjoittaja (AI) esittää kysymyksen omasta aiemmasta ehdotuksestaan ('Mitä tapahtuu oppilaitoksen parkkipaikoilla, ruokalassa ja neuvotteluhuoneissa keskiviikkona?') ja vastaa siihen seuraavassa lauseessa ('Ne täyttyvät äärimmilleen.') vahvistaen kritiikin ilman uutta dataa.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt kysymysmerkkiä, jota kirjoittaja olisi käyttänyt kyseenalaistamaan omaa premissiään. Muistio on luonteeltaan deklaratiivinen ehdotus, ei itsekriittinen pohdinta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_47bade191cf346ec818757f081f6aef3` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find contrast markers ('however, data shows that', 'despite X, metric Y'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a specific counter-argument is addressed using empirical counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): it's dismissed rhetorically. Rhetorical dismissals without data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Tekstistä löytyi kontrastimerkki 'kuitenkin'. Sitä seuraava lause käsittelee vastaväitettä ('Nykyiset, pandemian jäljiltä jääneet epäviralliset käytännöt') ja esittää empiiristä vastadataa ('johtaneet työyhteisön siiloutumiseen, epävarmuuteen tavoitettavuudesta sekä kokemuksiin epäoikeudenmukaisuudesta'). Tämä täyttää ehdon, jossa vastaväite käsitellään empiirisellä vastadatalla.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän syötteestä ei löytynyt kontrasti-ilmaisuja ('kuitenkin data osoittaa, että', 'huolimatta X:stä, mittari Y'), joissa olisi käsitelty spesifistä vasta-argumenttia empiirisellä vastadatalla. Siksi ehdot täyttävää lainausta ei voitu poimia.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän syötteistä ei löytynyt kontrastimerkkejä (esim. 'kuitenkin data osoittaa, että', 'huolimatta X:stä, mittari Y'), joissa vastaväitettä olisi käsitelty empiirisellä vastadatalla. Käyttäjän syötteet ovat joko ohjeita tai kysymyksiä, eivät argumentteja, jotka sisältäisivät empiiristä vastadataa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_10dd47750c9244139c394ca875f160e6` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. Do not evaluate the quality of the bridging rule.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'Tämä estää siiloutumisen, mahdollistaa nuorten opettajien kasvokkaisen mentoroinnin ja pitää kampuksen käyttöasteen tasaisena' 'Tämä estää' toimii mekanismina, joka selittää, miten edeltävä tieto (keskiviikosta muodostuu rajapinta) johtaa väitteeseen (siiloutuminen estyy, mentorointi mahdollistuu, käyttöaste tasainen). Se kuvaa eksplisiittisesti sillan datan ja väitteen välillä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Etsin lauseita, jotka sisältävät eksplisiittisen sillan datan ja väitteen välillä, kuten 'periaatteen mukaan, että' tai 'tämä osoittaa mekanismin, että'. Vaikka tekstissä on kausaalisia yhteyksiä ('koska'), ne eivät esitä yleistä sääntöä tai mekanismia, vaan suoran syy-seuraussuhteen. Sääntö edellyttää nimenomaan yleisen säännön esittämistä, ei pelkkää 'koska'-yhteyttä.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittisiä siltaavia sääntöjä, jotka yhdistäisivät datan ja väitteen yleisen periaatteen tai mekanismin kautta. Käytetyt 'koska', 'jotta', 'kun' ja 'jos' -rakenteet ovat suoria kausaalisia tai ehdollisia yhteyksiä, eivätkä ne ilmaise yleistä siltaavaa sääntöä Toulminin mallin mukaisesti.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c2968c987f1a4ac5824f15653df3dc8f` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *Tekstistä ei löytynyt vaihtoehtojen vähättelyä tai hylkäämistä ilman, että samassa kappaleessa olisi esitetty empiiristä tietoa tai viitattu ulkoiseen lähteeseen. Esimerkiksi 'ankkuripäivästä luovutaan' -kohdassa esitetään perustelu ('jotta kampus ei ruuhkautuisi yhtenä päivänä ja autioituisi muina').*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Lauseessa käytetään dismissiivistä markkeria 'luovutaan'. Hylkääminen perustellaan sisäisellä syyllä ('jotta kampus ei ruuhkautuisi yhtenä päivänä ja autioituisi muina'), eikä samassa kappaleessa ole ulkoista todennettavissa olevaa lähdettä tai empiiristä dataa, joka oikeuttaisi tämän hylkäämisen. Tämä täyttää ehdon, jossa hylkääminen tapahtuu ilman ulkoista perustelua.*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Tekstistä löytyi ensimmäinen dismissiivinen ilmaisu 'ei ole' ('is not'), joka hylkää vaihtoehdon ('henkilökohtainen etuoikeus tai sidottu pelkkään titteliin') ilman, että samassa kappaleessa esitetään ulkoista todennettavissa olevaa lähdettä tai empiiristä tietoa tämän hylkäämisen tueksi. Kappaleessa esitetään uuden politiikan peruste ('Se määräytyy sen mukaan, mitä työtehtävä kulloinkin vaatii ja missä se on tehokkainta tehdä'), mutta tämä ei ole empiiristä tietoa, joka perustelisi vanhan käytännön hylkäämistä.*

---

### Atom-ID: `tda_43516f120e4a415bb0ee3a878a53a5bc` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept generic 'more data is needed' statements. STEP 1 (Syntactic Anchor): Find methodological critique markers (e.g., 'our measurement of X may overrepresent', 'the bias in our sample'). STEP 2 (Bounding Box): Scan the paragraph. If a specific structural flaw in the methodology is explicitly identified. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Teksti sisältää kritiikkiä ehdotetun politiikan käytännön toteutuksesta ja sen oletuksista, mutta ei metodologisia kritiikkimerkkejä, jotka kohdistuisivat tutkimuksen tai tiedonkeruun rakenteellisiin virheisiin (esim. 'otoksemme harha' tai 'mittauksemme X voi yliedustaa').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Tekstissä tunnistetaan selkeä rakenteellinen puute ('Jos oppilaitoksella ei ole valmiita, mitattavia KPI-mittareita'), joka johtaa metodologiseen ongelmaan (johtaminen muuttuu 'mututuntumaksi').. Exceptions audit: Tekstistä ei löytynyt metodologisen kritiikin markkereita (esim. 'mittauksemme X voi yliedustaa', 'otoksemme harha'), jotka tunnistaisivat nimenomaisesti rakenteellisen virheen metodologiassa. 'Paholaisen asianajaja' -osiossa esitetty kritiikki kohdistui ehdotuksen käytännön toteutukseen, ei sen taustalla olevan tiedonhankinnan metodologiaan.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt metodologisen kritiikin markkereita (esim. 'mittauksemme X:stä voi yliedustaa', 'otoksemme harha'), jotka olisivat nimenomaisesti tunnistaneet rakenteellisen virheen metodologiassa. Esitetty kritiikki kohdistui ehdotuksen käytännön toteutukseen ja seurauksiin, ei sen taustalla olevaan metodologiaan.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fa4667af98f84790af9b9a12cd9d7bd0` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Syntactic Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: EXTRACTION CONDITION: the command lacks any specific constraints and allows the AI to freely decide what is important.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteissa ei löytynyt laajoja yhteenvetokomentoja, jotka olisivat antaneet tekoälylle vapauden päättää, mikä on tärkeää. Kaikki 'yhteenveto'-tyyppiset pyynnöt sisälsivät selkeitä rajoituksia (esim. pituus, kohdeyleisö, tavoitteet).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Käyttäjä antaa tekoälylle laajan yhteenvetokäskyn ('Tee yhden sivun yhteenveto'), joka antaa tekoälylle vapauden päättää, mikä on tärkeää sisällön osalta ('suosituksesi (juuri opetusalalle) etätyön tekemiselle'), vaikka pituus- ja tyylirajoituksia onkin.. Exceptions audit: Käyttäjän kehotteissa ei löytynyt yhtään laajaa yhteenvetokomentoa, joka olisi jättänyt tekoälylle vapauden päättää sisällön tärkeydestä ilman spesifejä rajoituksia. Esimerkiksi "Tee yhden sivun yhteenveto" -komento sisälsi useita rajoituksia.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Vaikka käyttäjä antoi komennon 'tee yhden sivun yhteenveto', se sisälsi useita tarkkoja rajoituksia (sivumäärä, tyyli, kohdeala, tavoitteet), mikä estää tekoälyä päättämästä vapaasti, mikä on tärkeää. Siksi säännön ehto 'komennosta puuttuu erityisiä rajoituksia' ei täyty, eikä sääntöä rikota.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c17684acfcbe4a918e5ae0705b452b06` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user commands focused on tone (e.g., 'make it sound more persuasive', 'make it more academic'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user focuses solely on the performativity (tone/style) while ignoring substantive factual gaps. Revisions containing factual additions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Vaikka käyttäjä pyytää sävyyn ja tyyliin liittyviä muutoksia ('selvällä kielellä (ei jargonia)', 'säälimätöntä kritiikkiä', 'tekstin muodossa sopiva kieli'), hän ei tee sitä 'ignoring substantive factual gaps'. Käyttäjä on aktiivisesti osallistunut sisällölliseen keskusteluun ja pyytänyt faktapohjaa, joten ehto 'solely on the performativity (tone/style) while ignoring substantive factual gaps' ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää muistion muotoilua ja kielen sopivuutta ('Ota huomioon tekstin muodossa sopiva kieli'), mikä on tyyliin/sävyyn keskittyvä komento ilman faktuaalisia lisäyksiä tai puutteiden korjaamista.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä pyytää sävyyn/tyyliin liittyvää muutosta ('Ota huomioon tekstin muodossa sopiva kieli'), mutta samassa kehotteessa pyydetään myös rakenteellisia muutoksia ('Tee tästä muistio', 'Yksi sivu riittää', 'Tee lyhyt johdanto selvityksellesi'). Säännön ehto 'the user focuses solely on the performativity' ei täyty, koska käyttäjä ei keskity *ainoastaan* sävyyn.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_9fd2fff3ab4a46d29b5df31488561dd4` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly restricts the AI to an external, objective anchor. Acceptance of unsourced hallucinated facts. NEGATIVE BOUNDARY: General questions or requests for explanation DO NOT count as external grounding unless they explicitly demand a citation or source material restriction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotukset eivät sisältäneet eksplisiittisiä vaatimuksia ulkoiselle perustelulle, kuten 'viittaa tiettyyn lähteeseen' tai 'perustu tiukasti annettuun dokumenttiin'. Yleinen pyyntö 'tutkimustiedosta' ei täytä kriteeriä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää eksplisiittisesti tekoälyä listaamaan lähteet ja arvioimaan niiden luotettavuutta, mikä vastaa vaatimusta ulkoisesta perustelusta ja lähteiden mainitsemisesta.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteissa ei ollut eksplisiittisiä vaatimuksia ulkoiselle perustelulle, kuten 'siteeraa tiettyä lähdettä' tai 'perusta tämä tiukasti annettuun dokumenttiin'. Yleinen pyyntö 'tutkimustiedosta' ei täytä tiukan rajoituksen kriteeriä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5b0573225735409b8ef3d3eac041236d` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers (e.g., 'always', '100% guaranteed', 'it is a fact that'). STEP 2 (Bounding Box): Scan the same paragraph. If the absolute claim is made regarding a compliance or archival rule BUT no external framework (ARMA, ISO, law) is cited in that paragraph. Do not accept absolute claims that are mathematically verifiable. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: The paragraph contains the dogmatic absolute marker 'aina' (always) in the sentence 'Yhteiset pedagogiset kehityspäivät tehdään aina kampuksella.' The paragraph does not cite any external framework (ARMA, ISO, law) to justify this absolute claim, thus meeting the negative condition for extraction.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Etsin 'ai:'-lohkoista dogmaattisia absoluuttisia merkkejä, jotka liittyvät noudattamis- tai arkistointisääntöön ja joissa ei ole ulkoista viitekehystä samassa kappaleessa. Ensimmäinen tällainen osuma oli lause "Yhteiset pedagogiset kehityspäivät tehdään aina kampuksella.", joka on toiminnallinen sääntö ja sisältää absoluuttisen sanan 'aina', mutta ei viittaa ulkoiseen viitekehykseen kyseisessä kappaleessa.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt absoluuttisia väitteitä, jotka koskisivat vaatimustenmukaisuus- tai arkistointisääntöä ja joista puuttuisi ulkoinen viitekehys. Vaikka absoluuttisia ilmaisuja, kuten 'mikään ruutuaika ei korvaa' tai 'aina kampuksella', esiintyi, ne eivät liittyneet vaatimustenmukaisuus- tai arkistointisääntöihin. Lisäksi 'Työterveyslaitoksen raportit osoittavat' -tyyppiset lauseet viittasivat ulkoiseen lähteeseen, mikä estää ehdon täyttymisen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_654d4f29e9a045a0ad58566e3fc5f942` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not evaluate engagement quality. STEP 1 (Syntactic Anchor): Find an explicit counter-argument or risk raised in the text (e.g., 'Despite the risk', 'Opponents argue', 'Vaikka'). STEP 2 (Bounding Box): Scan the subsequent sentences. EXTRACTION CONDITION: the counter-argument is stated but not logically dismantled with data. NEGATIVE CONDITION (RETURN NULL IF MET): it is dismantled step-by-step. <disambiguation>
  REFRAMING EXCLUSION: Rhetorical reframing patterns where a concept is 
  repositioned from negative to positive framing ('not just X, but Y') are 
  STYLISTIC DEVICES, not argumentative structures. Do NOT extract them as:
  - counter-arguments (they do not argue AGAINST anything)
  - dialectical syntheses (they do not reconcile two opposing theses)
  - alternative model dismantling (they do not present a separate model)
  - absolute conclusions (they are framing choices, not logical claims)
  If a reframing pattern is the ONLY candidate match, return JSON null.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä esitetään vastaväitteitä tai riskejä (siiloutuminen, epävarmuus tavoitettavuudesta, epäoikeudenmukaisuus), mutta nämä puretaan järjestelmällisesti myöhemmässä ehdotuksessa esitetyillä ratkaisuilla. Siksi negatiivinen ehto (vastaväite puretaan vaiheittain) täyttyy, ja exact_quote palautetaan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Tekstissä esitetään selkeä vastaväite ('Kritiikki') aiemmalle ehdotukselle, eikä tätä vastaväitettä pureta loogisesti datalla samassa tekstikohdassa. Sen sijaan se toimii perustana myöhemmälle uudelleenmuotoilulle.. Exceptions audit: Teksti esittää ehdotuksen, joka pyrkii ratkaisemaan aiemmin tunnistettuja ongelmia ja riskejä. Se ei esitä nimenomaista vastaväitettä omalle ehdotukselleen, jota ei sitten purettaisi tiedoilla. Sen sijaan se esittää ratkaisuja ongelmiin.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä esitetään riskejä ja ongelmia ('siiloutumiseen', 'epävarmuuteen', 'epäoikeudenmukaisuudesta'), mutta nämä puretaan systemaattisesti ja loogisesti ehdotetun hybridityömallin eri kohdissa (esim. 'Tehtäväkohtaiset linjaukset ja aito oikeudenmukaisuus', 'Kulttuurin ja innovoinnin turvaaminen: Tiimikohtainen limitys', 'Tavoitettavuus ja johtaminen mittareilla'). Siksi negatiivinen ehto täyttyy, ja poiminta on null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c7e3a26277674d2aa8ab38d1ee7afb05` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept mathematical axioms. STEP 1 (Syntactic Anchor): Find dogmatic certainty markers (e.g., 'is self-evident', 'needs no proof', 'as we all know', 'beyond question'). STEP 2 (Bounding Box): Scan the sentence. If it explicitly blocks further empirical testing or questioning. Otherwise. NEGATIVE BOUNDARY: Rhetorical exaggeration or strong statements like 'this is the only path' DO NOT count as dogmatism unless the author explicitly forbids further empirical testing or questioning.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt dogmaattisen varmuuden merkkejä, kuten 'on itsestään selvää' tai 'ei tarvitse todistusta', jotka nimenomaisesti estäisivät empiirisen testauksen tai kyseenalaistamisen. Teksti perusteli väitteitä tutkimustiedolla, mikä on dogmaattisuuden vastaista.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt dogmaattisia varmuuden merkkisanoja, jotka olisivat nimenomaisesti estäneet empiirisen testauksen tai kyseenalaistamisen. Vahvat väitteet perustuivat aina mainittuihin tutkimuksiin tai konsensukseen, eivätkä ne sulkeneet pois jatkotutkimuksen mahdollisuutta.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Presence detected: Lause 'Se vastaa täysin sitä tieteellistä konsensusta, joka vallitsee parhaista hybridityön käytännöistä.' sisältää dogmaattisen varmuuden merkin ('vastaa täysin sitä tieteellistä konsensusta'), joka estää eksplisiittisesti jatkotestauksen tai kyseenalaistamisen väittämällä täydellistä linjausta tieteellisen yksimielisyyden kanssa.. Exceptions audit: Tekstistä ei löytynyt dogmaattisen varmuuden merkkejä, jotka nimenomaisesti estäisivät lisätestauksen tai kyseenalaistamisen. Vaikka tekstissä on vahvoja väitteitä, ne eivät kiellä jatkotutkimusta tai kysymysten esittämistä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_65541c8fa62649038b52553cad9eab8a` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not accept implicit alternatives. STEP 1 (Syntactic Anchor): Find a comparative marker (e.g. 'Option A vs Option B', 'Instead of', 'Compared to'). STEP 2 (Bounding Box): Scan the surrounding sentences. EXTRACTION CONDITION: the text explicitly names at least two distinct approaches before selecting one. NEGATIVE CONDITION (RETURN NULL IF MET): only one approach is discussed.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Teksti vertailee kahta eri lähestymistapaa ('paluu vanhaan' ja 'sataprosenttinen etätyö') ja valitsee niistä kolmannen ('toimivan hybridimallin'), mikä täyttää ehdon kahden lähestymistavan nimeämisestä ja yhden valinnasta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Tekstissä esitetään kaksi erillistä lähestymistapaa ('paluu vanhaan' ja 'sataprosenttinen etätyö') ennen kuin valitaan kolmas ('toimivan hybridimallin').  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Teksti nimeää eksplisiittisesti kaksi erillistä lähestymistapaa ('yksi läsnäolopäivä' ja 'kaksi tai useampi läsnäolopäivää') ennen kuin se perustelee toista. Sääntö 'Do not accept implicit alternatives' on täytetty, koska vaihtoehdot ovat eksplisiittisiä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_92680081ffb244d8abbdc99120a3291f` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject matches from user inputs or 'user:' prefixes. STEP 1 (Syntactic Anchor): Find an absolute certainty marker (e.g., 'undeniably', '100%', 'proven fact'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. STEP 3: EXTRACTION CONDITION: no empirical data is provided within that exact paragraph to justify the claim. NEGATIVE CONDITION (RETURN NULL IF MET): empirical data exists. Do not evaluate 'arrogance'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *Tekstistä ei löytynyt absoluuttisia varmuusmerkkejä (esim. 'kiistatta', '100%', 'todistettu fakta'), jotka esittäisivät väitteen ilman välitöntä empiiristä tietoa samassa kappaleessa. Lähin vastaava lause viittasi tutkimustietoon, mikä tarjoaa empiiristä tukea.*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *Dokumentista ei löytynyt eksplisiittisiä absoluuttisia varmuusmerkkejä (kuten 'kiistatta', 'todistettu fakta', '100%', 'ainoastaan', 'ainoa tapa'), jotka olisivat esittäneet väitteen ilman samassa kappaleessa olevaa empiiristä perustelua. Lähin ilmaisu 'perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon' viittaa empiiriseen tietoon, eikä ole absoluuttinen varmuusväite ilman perusteluja.*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Tekstissä esitetään absoluuttinen väite ('estää siiloutumisen'), mutta samassa kappaleessa ei ole empiiristä dataa tai tutkimustietoa, joka tukisi tätä väitettä suoraan. Väite on esitetty varmana lopputuloksena ehdotetusta mallista ilman välitöntä todistusaineistoa.*

---

### Atom-ID: `tda_19e1957773db4cfd820cb167ae1d8ec3` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find epistemic boundary markers (such as equivalents of 'may not apply', 'exception', 'edge case', 'out of scope', 'limitation' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>The text MUST physically identify a scenario where its OWN logic or model fails or is limited.</step3_extraction_condition> <step4_fail_fast_protocol>If the text only describes external problems or general crises, and does not explicitly limit its own analytical scope, you MUST return JSON null. Implicit modesty is BANNED.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'Alkuperäinen ehdotus oli teoreettisen kaunis, mutta käytännössä se olisi johtanut kaaokseen, eriarvoisuuteen ja toiminnan kangertelemiseen.' 'mutta' toimii episteemisenä raja-merkkinä, ja lause kuvaa tekoälyn oman aiemman ehdotuksen (mallin) rajoitusta tai epäonnistumista käytännössä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittistä merkintää, joka tunnistaisi skenaarion, jossa dokumentin oma logiikka tai malli epäonnistuu tai on rajoitettu. Vaikka 'kuitenkin' esiintyy, se viittaa nykyisten käytäntöjen ongelmiin, ei ehdotetun mallin rajoituksiin.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittisiä epistemologisia rajausmerkkejä (kuten 'ei välttämättä päde', 'poikkeus', 'rajatapaus', 'soveltamisalan ulkopuolella', 'rajoitus', 'kuitenkin', 'silti', 'mutta', 'epävarmuus'), jotka tunnistaisivat skenaarion, jossa mallin oma logiikka tai malli epäonnistuu tai on rajoitettu. Johdannon 'kuitenkin' viittaa olemassa oleviin ongelmiin, ei ehdotetun mallin rajoituksiin.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d2e04ccdc7df428380b667e21217224a` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not evaluate 'collaboration' or 'politeness'. STEP 1 (Syntactic Anchor): Find delegation verbs ('päätä', 'valitse', 'kumpi', 'decide', 'choose'). STEP 2 (Bounding Box): Scan the prompt. EXTRACTION CONDITION: the user explicitly asks the AI to make a final subjective choice or decision on their behalf.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää tekoälyä selvittämään ja määrittämään, mikä olisi 'sopiva' etätyöpolitiikka, mikä on subjektiivinen valinta tai päätös käyttäjän puolesta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt yhtään delegointiverbiä ('päätä', 'valitse', 'kumpi') tai muuta ilmaisua, joka pyytäisi tekoälyä tekemään lopullisen subjektiivisen valinnan käyttäjän puolesta. Käyttäjä pyysi tekoälyä analysoimaan, ehdottamaan ja kritisoimaan, mutta ei päättämään.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt yhtään määriteltyä delegaatioverbiä ('päätä', 'valitse', 'kumpi'), jotka pyytäisivät tekoälyä tekemään subjektiivisen valinnan käyttäjän puolesta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bd90e5a66c5d433a9ed650f295132625` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not evaluate 'spurious'. STEP 1 (Syntactic Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. EXTRACTION CONDITION: the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Etsin kausaalista väitettä, joka perustuu ainoastaan tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman fyysistä mekanismia samassa lauseessa. Lause 'Kun siirryimme laajaan etätyöhön, toimitilakulumme putosivat 30 prosenttia' kuvaa samanaikaisen tapahtuman ja seurauksen ilman selitystä mekanismista kyseisessä lauseessa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä löytyi useita kausaalisanoja, kuten 'Koska', 'johtaneet' ja 'perustuu'. Kuitenkin kaikissa tapauksissa kausaaliväitteeseen liittyi implisiittinen tai eksplisiittinen mekanismi, eikä se perustunut AINOASTAAN tilastolliseen korrelaatioon tai samanaikaiseen esiintymiseen ilman fyysistä mekanismia. Siksi säännön ehtoja rikkomuksen poimimiseksi ei täyttynyt.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä löytyi useita kausaalisia väitteitä, mutta jokaisessa tapauksessa väitteen yhteydessä tai välittömästi sen jälkeen esitettiin fyysinen mekanismi tai selitys syy-seuraussuhteelle. Esimerkiksi 'toimitilakulumme putosivat 30 prosenttia. Emme tarvitse jokaiselle omaa työpistettä...' selittää mekanismin. Siksi säännön mukaista rikettä (kausaaliväite ilman mekanismia) ei havaittu.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_72d297df24fb45c3a85dc0b8248b9188` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. EXTRACTION CONDITION: the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points. Do not evaluate 'depth', simply count the data points.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *Vaihtoehtoinen malli ('ankkuripäivä') mainitaan, mutta samassa kappaleessa esitetään vastaväite ("jotta kampus ei ruuhkautuisi yhtenä päivänä ja autioituisi muina"). Koska vastaväite löytyy, ehto "0 vastaväitettä" ei täyty, eikä sääntöä rikota.*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Tekstissä mainitaan vaihtoehtoinen malli ('Nykyiset, pandemian jäljiltä jääneet epäviralliset käytännöt'), ja sama kappale sisältää useita vastaväitteitä tai vertailevia datapisteitä tätä mallia vastaan ('johtaneet työyhteisön siiloutumiseen, epävarmuuteen tavoitettavuudesta sekä kokemuksiin epäoikeudenmukaisuudesta'). Siksi ehto 'tasan 0 vastaväitettä tai vertailevaa datapistettä' ei täyty, mikä tarkoittaa säännön rikkomista.*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *Sääntö edellyttää, että nimetty vaihtoehtoinen malli tai teoria mainitaan ilman vastaväitteitä tai vertailevia datapisteitä samassa kappaleessa. Tekstissä mainitaan 'Nykyiset, pandemian jäljiltä jääneet epäviralliset käytännöt', mutta sama kappale listaa välittömästi niiden negatiiviset seuraukset ('työyhteisön siiloutumiseen, epävarmuuteen tavoitettavuudesta sekä kokemuksiin epäoikeudenmukaisuudesta'). Koska vastaväitteitä on, ehto '0 counter-arguments' ei täyty, eikä säännön mukaista rikettä löydy.*

---

### Atom-ID: `tda_6e904f7c369a410ab9988e49ca3213e0` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find a counterfactual scenario (e.g. 'What if', 'Alternatively', 'Had we used'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the scenario is systematically dismantled with specific data points or mathematical proofs to validate the primary conclusion. NEGATIVE CONDITION (RETURN NULL IF MET): it is merely mentioned without data-driven refutation.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt kohtaa, jossa vastafaktuaalinen skenaario olisi järjestelmällisesti purettu käyttäen spesifejä datapisteitä tai matemaattisia todisteita ensisijaisen johtopäätöksen validoimiseksi. Vaikka vastafaktuaaleja mainittiin, niitä ei kumottu datalla.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Teksti esittää vastafaktuaalisen skenaarion ('Jos tämä paperi viedään sellaisenaan käytäntöön') ja purkaa sen järjestelmällisesti useilla konkreettisilla esimerkeillä ja loogisilla seurauksilla, jotka osoittavat alkuperäisen ehdotuksen heikkoudet.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän syöte sisältää kysymyksen vaihtoehtoisesta skenaariosta ('Riittääkö yksi läsnäolopäivä? Mikä puoltaisi esim. kahta tai useampaa läsnäolopäivää?'), mutta se ei sisällä skenaarion järjestelmällistä purkamista tai validointia spesifisillä datapisteillä tai matemaattisilla todisteilla. Siksi ehdot täyttävää lainausta ei löytynyt.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a946688e5f5549e8ac30584d1a02ad26` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Target paragraphs with statistical/factual reporting.</step1_lexical_anchors> <step2_bounding_box>Scan for first-person markers (such as first-person pronouns, possessive suffixes, or self-reflective verbs translated/adapted into the document's language, e.g., 'I', 'we' in English, or '-mme', '-ni', '-n' in Finnish).</step2_bounding_box> <step3_extraction_condition>You MUST extract the text IF AND ONLY IF the count of first-person markers is EXACTLY ZERO.</step3_extraction_condition> <step4_fail_fast_protocol>If EVEN ONE first-person pronoun, possessive suffix, or self-reflective verb exists, the count is > 0. In that case, you MUST return JSON null. DO NOT EXTRACT.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *Tekstissä esiintyy useita ensimmäisen persoonan markkereita (esim. 'oppilaitoksemme', 'opetuksestamme', 'arkeamme', 'voimme', 'Ehdotan'). Koska sääntö edellyttää TÄYSIN Nolla ensimmäisen persoonan markkeria, ehto ei täyty.*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Kappale sisältää faktapohjaista raportointia (ehdotuksen perustuminen tutkimustietoon ja tavoitteet) eikä siinä ole yhtään ensimmäisen persoonan markkeria (kuten 'minä', 'me', '-ni', '-mme' tai vastaavia verbimuotoja).*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *Sääntö edellyttää, että ensimmäisen persoonan merkintöjen määrä on TÄSMÄLLEEN NOLLA. Tekstistä löytyi useita ensimmäisen persoonan merkintöjä (esim. 'oppilaitoksemme', 'opetuksestamme', 'arkeamme', 'voimme', 'Ehdotan') tilastollista tai tosiasiallista raportointia sisältävistä kappaleista. Koska määrä ei ole nolla, ehtoa ei täytetä.*

---

### Atom-ID: `tda_8ecd3f17b3984e4fa1bb6a8cb5576b65` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find absolute causal words (such as equivalents of 'only reason', 'entirely due to', 'only way' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the quote IF a highly complex outcome is attributed to a SINGLE cause.</step3_extraction_condition> <step4_fail_fast_protocol>If the text acknowledges multiple factors or nuances, or if the outcome is simple, return JSON null. Do not evaluate nuance.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Etsin absoluuttisia kausaalisanoja (esim. 'ainoa syy', 'kokonaan johtuen', 'ainoa tapa'), jotka liittävät erittäin monimutkaisen lopputuloksen yhteen ainoaan syyhyn. Tekstistä ei löytynyt yhtään tapausta, joka täyttäisi tämän ehdon ilman, että siinä olisi tunnustettu useita tekijöitä tai vivahteita, tai että lopputulos olisi ollut riittävän monimutkainen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'Ja vahva kulttuuri on se, mikä pitää ihmiset talossa' 'se, mikä pitää' toimii absoluuttisena kausaalisana, joka liittää monimutkaisen lopputuloksen ('ihmiset talossa') yhteen ainoaan syyhyn ('vahva kulttuuri').  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt yhtään absoluuttista kausaalisanaa, kuten 'ainoa syy', 'kokonaan johtuen' tai 'ainoa tapa', jotka olisivat liittäneet monimutkaisen lopputuloksen yhteen ainoaan syyhyn.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_dff85ed8a43a4ca99c34873b2fe44d89` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find precise causal language ('which directly causes', 'the mechanism behind this is'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: a Claim is supported by empirical Data AND the exact mechanism is defined. NEGATIVE CONDITION (RETURN NULL IF MET): any of the three (Claim, Data, Warrant) is missing from the explicit text. Implicit connections.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Etsin tarkkaa kausaalista kieltä ('joka suoraan aiheuttaa', 'tämän mekanismi on'). Vaikka tekstissä oli kausaalisia verbejä kuten 'johtaneet', 'estää', 'mahdollistaa', 'pitää', 'säästää' ja 'vapauttaa', ne eivät määritelleet *tarkkaa mekanismia* Claimin ja Datan välillä. Yhteydet olivat implisiittisiä seurauksia, eivät eksplisiittisesti määriteltyjä mekanismeja, mikä laukaisi negatiivisen ehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt tarkkaa kausaalista kieltä, kuten 'mikä suoraan aiheuttaa' tai 'mekanismi tämän takana on', joka olisi tukenut väitettä empiirisellä datalla ja määritellyt tarkan mekanismin. Vaikka kausaalisia yhteyksiä oli ('johtaneet', 'perustuu', 'estää'), ne eivät olleet riittävän tarkkoja täyttääkseen poimintaehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Lauseessa esitetään väite ('reiluus korvataan'), joka perustuu tietoon ('he eivät säästä matkakuluissa'). Mekanismi ('laajennetulla työaikajoustolla... sekä kampustyöpisteiden parhaalla mahdollisella ergonomialla ja varustelulla') on selkeästi määritelty, mikä täyttää kaikki ehdot.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6e3e3aa6b9134a01838c3b70a35b4f32` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find weak associative language ('relates to', 'is associated with', 'impacts'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it connects Data to a Claim without defining the exact causal mechanism. NEGATIVE CONDITION (RETURN NULL IF MET): it uses precise causal mechanism ('which directly causes'). Precise causal mechanisms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt heikkoa assosiatiivista kielenkäyttöä (esim. 'liittyy', 'yhdistetään', 'vaikuttaa'), joka yhdistäisi dataa väitteeseen ilman tarkkaa kausaalista mekanismia. Kaikki löydetyt yhteydet olivat suoria kausaalisia tai tarkasti määriteltyjä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'etätyön myönteisistä ja kielteisistä vaikutuksista työhön ja työyhteisöön' käytetään 'vaikutuksista'-sanaa yhdistämään 'etätyö' (data) 'työhön ja työyhteisöön' (väite) ilman, että tarkkaa kausaalimekanismia ('joka suoraan aiheuttaa') määritellään. Tämä vastaa heikon assosiatiivisen kielen kriteereitä.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Lauseessa 'Nykyiset, pandemian jäljiltä jääneet epäviralliset käytännöt ovat kuitenkin johtaneet työyhteisön siiloutumiseen...' käytetään 'johtaneet'-sanaa yhdistämään data (epäviralliset käytännöt) väitteeseen (siiloutuminen, epävarmuus, epäoikeudenmukaisuus) ilman, että tarkkaa kausaalimekanismia kuvataan. Se ei selitä *miten* käytännöt johtivat näihin seurauksiin, ainoastaan että ne johtivat.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d12f15e1c2d4488b7c2ef32d0ccfa26` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Lause sisältää absoluuttisen varmuuden merkin 'varma', joka esitetään ilman välitöntä empiiristä dataa tai epistemologisia tarkennuksia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Lause sisältää absoluuttisen varmuuden markkerin 'täysin', joka esitetään ilman empiiristä dataa tai epistemologisia tarkennuksia, kuten virhemarginaaleja, väittäen täydellistä vastaavuutta tieteelliseen konsensukseen.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole absoluuttisen varmuuden markkereita, kuten 'täysin' tai '100%', joita esitettäisiin ilman empiiristä dataa tai epistemologisia tarkennuksia. Käytetyt ilmaisut ovat suosituksia, tavoitteita tai politiikkalausekkeita.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bfbe65b639b54106913902d5bd0ae6ab` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find revelation markers (e.g., 'underlying this', 'the root cause is', 'fundamentally'). STEP 2: EXTRACTION CONDITION: the text identifies a mechanism or assumption that is not immediately visible on the surface. Do not accept superficial observations of visible symptoms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Teksti käyttää ilmaisua 'Fakta taustalla' paljastaakseen mekanismin, joka ei ole välittömästi näkyvissä pinnalla, mikä vastaa 'revelation marker' -kriteeriä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt yhtään eksplisiittistä 'revelation marker' -ankkuria (esim. 'tämän taustalla', 'perussyy on', 'pohjimmiltaan', 'fundamentaalisesti'), jotka tunnistaisivat pinnan alla olevan mekanismin tai oletuksen. Siksi ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Presence detected: Etsin paljastavia merkkejä (revelation markers) ja löysin ilmaisun 'luottamuksen kuilu' AI:n vastauksesta. Tämä ilmaisu kuvaa mekanismia ('kun emme näe kollegaa, alamme helposti kuvitella, ettei hän tee mitään'), joka ei ole välittömästi näkyvä oire, vaan syvempi ilmiö.. Exceptions audit: Tekstistä ei löytynyt yhtään määriteltyä paljastusmerkkiä (esim. 'tämän taustalla', 'juurisyy on', 'pohjimmiltaan', 'fundamentaalisesti').  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_7d0ef5f0be004974801b53d2af317bbe` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find explicit rejection markers (e.g., 'Instead of following', 'I will create my own', 'I ignored'). STEP 2 (Bounding Box): Scan the sentence containing the marker. If the author explicitly states they are creating a new rule that contradicts the requested instructions. Do not evaluate 'quality' or if the new rule is better.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Tekstissä hylätään eksplisiittisesti aiempi ehdotus (aiemman 'ai:'-vastauksen sisältö) ja esitetään uusi, korjattu versio. Tämä on ensimmäinen kronologinen esiintymä, joka täyttää ehdot.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittisiä hylkäämismarkkereita, jotka viittaisivat käyttäjän antamien ohjeiden hylkäämiseen. AI noudatti käyttäjän ohjeita luoda, kritisoida ja uudelleenmuotoilla ehdotusta.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän syötteestä ei löytynyt eksplisiittisiä hylkäysmerkkejä, joissa käyttäjä olisi luonut uuden säännön, joka olisi ristiriidassa hänen omien pyydettyjen ohjeidensa kanssa. Siksi sääntöä ei rikottu.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_e0bf5617f4804a0d98a6b2d91dcd21ce` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Syntactic Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. EXTRACTION CONDITION: the claim is demonstrably false or fabricated but presented with absolute certainty. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: AI esittää yksityiskohtaisen lähdeviittauksen, joka sisältää institution, vuoden, julkaisutyypin, spesifit otsikot ja tutkijoiden nimet. Vaikka tutkijat ovat todellisia ja aihepiiri uskottava, näiden spesifien julkaisujen olemassaoloa tällä otsikolla ja vuodella ei voida vahvistaa, mikä viittaa fabrikointiin. Tämä on esitetty absoluuttisella varmuudella ('Lähde:').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: En löytänyt lähdetekstistä faktaväitettä, joka olisi ollut osoitettavasti virheellinen tai keksitty pelkästään annetun lähdemateriaalin perusteella. Mainitut päivämäärät ja lähteet ovat ajallisesti uskottavia suhteessa dokumentin päivämäärään, eikä niiden sisältöä voi todentaa tai kumota ilman ulkoista tiedonhakua, mikä on kiellettyä.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Väite, että ehdotus perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon, on fabrikointi. Tekoäly on `chat_log`-osiossa esittänyt näistä tutkimuksista yksityiskohtia (kuten julkaisuvuoden 2025 ja spesifit otsikot), jotka ovat demonstratiivisesti vääriä tai keksittyjä, vaikka instituutiot ja tutkijat ovat todellisia. Tämä tekee väitteestä fabrikoidun, koska sen perusta on epätosi.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b899e72085ea4d488a6e6c22a34e2d75` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not evaluate 'superficial' subjectively. STEP 1 (Syntactic Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the verification relies entirely on human intuition rather than a systemic protocol (like OWASP). NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Teksti kieltää eksplisiittisesti luottamuksen 'mututuntumaan', mikä on suomenkielinen vastine 'human intuition' -käsitteelle. Koska sääntö on käänteinen (etsii vikaa) ja teksti kieltää vian olemassaolon, poimintaehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Sääntö etsii termejä, jotka viittaavat manuaaliseen tai ad hoc -tarkistukseen, joka perustuu intuitioon systemaattisen protokollan sijaan. Lähdetekstissä AI:n 'paholaisen asianajajan' kritiikissä mainitaan, että johtaminen muuttuu 'pelkäksi mututuntumaksi' ilman mitattavia KPI-mittareita, mikä vastaa ehtoa.. Exceptions audit: The AI explicitly states that its recommendations are not based on 'mututuntumaa' (gut feeling/intuition), but on extensive research. Therefore, the condition that verification relies entirely on human intuition is not met, as the text denies it.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää manuaaliseen tai ad hoc -tarkistukseen viittaavien termien löytymistä, jotka perustuvat inhimilliseen intuitioon systemaattisen protokollan sijaan. Lähdetekstissä ei ole tällaisia termejä. Päinvastoin, AI nimenomaisesti kieltää käyttävänsä 'mututuntumaa' perustana.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_9da28945325e4486a8b4941c561299fa` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). Vague references to 'studies' or 'science'. <disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää formaalia viittausta, joka nimeää metodologian tai tutkimuksen eksplisiittisesti. Tekstissä mainitaan 'Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon', mikä on liian yleinen viittaus eikä täytä formaalin sitaatin ehtoa. Negatiivinen ehto (vague reference) täyttyy, joten palautan null.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Lause viittaa eksplisiittisesti kahteen nimettyyn instituutioon (Työterveyslaitos ja Stanfordin yliopisto) ja niiden tuoreimpaan tutkimustietoon, mikä täyttää muodollisen viittauksen ehdon eikä ole epämääräinen viittaus 'tutkimukseen'.. Exceptions audit: Käyttäjän syötteestä ei löytynyt muodollisia viittauksia, jotka tukisivat loogista sääntöä nimenomaisella metodologialla tai tutkimuksella. Vaikka AI:n vastauksissa on tällaisia viittauksia, ohjeistus edellyttää poimimaan todisteet ainoastaan käyttäjän syötteestä.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Lause 'Ehdotus perustuu Työterveyslaitoksen ja Stanfordin yliopiston tuoreimpaan tutkimustietoon' sisältää viittauksen tutkimustietoon, mutta se on liian yleinen. Se ei viittaa spesifiseen metodologiaan, tutkimukseen, ala-artikkeliin tai numeroituun periaatteeseen, mikä tekee siitä epämääräisen viittauksen negatiivisen ehdon mukaisesti.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c512ea7305614bfabf468fe838420dda` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että teksti luettelee tukevia todisteita, mutta jättää kokonaan mainitsematta reunatapaukset, epäonnistumiset tai rajoitukset. Tekoälyn vastauksissa, erityisesti dialogissa ja 'paholaisen asianajaja' -osiossa, mainitaan useita rajoituksia ja haasteita lopputulosten arviointien yhteydessä. Koska rajoituksia käsitellään, säännön negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä käsitellään laajasti lopputuloksen rajoituksia, epäonnistumisia ja reunaehtoja, erityisesti AI:n 'paholaisen asianajaja' -vastauksessa, jossa esitetään viisi kriittistä kohtaa aiemmasta ehdotuksesta. Myös aiemmassa dialogissa HR-Hanna esittää rajoituksia.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Tekoälyn tuottamassa 'product_text'-lähteessä esitetään hybridityömalli ja sen hyödyt, kuten kiinteistökulujen säästöt ja tilojen vapautuminen. Tässä osiossa ei kuitenkaan mainita lainkaan mahdollisia rajoituksia, haasteita tai reunatapauksia, mikä täyttää ehdon, jossa positiivinen arviointi esitetään ilman rajoitusten käsittelyä samassa yhteydessä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_20e76f768d24458fb2cc131b2bde4e04` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find blind procedural markers (e.g., 'must follow', 'the checklist requires', 'according to protocol'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a rule is enforced explicitly despite stated contextual evidence that it might be suboptimal. Do not accept justifiable adherence to safety or compliance protocols where no counter-evidence is presented.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt sokeita menettelyllisiä merkkejä, joissa sääntöä noudatettaisiin nimenomaisesti huolimatta siitä, että esitetty kontekstuaalinen todiste viittaa sen olevan suboptimaalinen. Kaikki löydetyt menettelylliset ohjeet esitettiin optimaalisina ratkaisuina aiemmin tunnistettuihin ongelmiin, eikä niihin liittynyt kontekstuaalista todistetta suboptimaalisuudesta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Lause 'Ehdotus suosittelee, että viesteihin ei vastata klo 17 jälkeen työhyvinvoinnin nimissä.' sisältää menettelyllisen merkin 'suosittelee, että'. Samassa kappaleessa esitetään välittömästi kritiikkiä, joka osoittaa säännön epäoptimaalisuuden aikuiskoulutuksen iltapainotteisessa kontekstissa, täyttäen siten ehdot.. Exceptions audit: Vaikka 'velvoitetaan' on menettelyllinen merkki, tekstissä ei ole esitetty kontekstuaalista näyttöä siitä, että tämä sääntö olisi suboptimaalinen. Poimintaehto edellyttää, että sääntöä noudatetaan nimenomaisesti huolimatta siitä, että kontekstuaalinen näyttö viittaa sen suboptimaalisuuteen. Koska tällaista näyttöä ei ole, ehto ei täyty.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Presence detected: Teksti kuvaa säännön ('viesteihin ei vastata klo 17 jälkeen') seurauksia, jotka ovat suboptimaalisia ('pakottaa opettajat joustamaan salaa' tai 'halvaannuttaa iltaopiskelijoiden tukipalvelut'), mikä osoittaa säännön sokeaa noudattamista kontekstuaalisista haasteista huolimatta. Tämä täyttää ehdon, että sääntöä on rikottu (rule_satisfied = False).. Exceptions audit: Syntaktinen ankkuri 'velvoitetaan' löytyi, joka viittaa säännön toimeenpanoon. Kuitenkaan ehdon 'despite stated contextual evidence that it might be suboptimal' ei katsottu täyttyvän, sillä kyseinen lause on osa uutta, korjattua ehdotusta, eikä sen välittömässä kontekstissa esitetä todisteita sen suboptimalisuudesta. Koska kyseessä on käänteinen sääntö (Vice) ja rikettä ei havaittu, palautetaan tyhjä merkkijono.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_46b1a8e3c2304438b82420fc40c3dbc1` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not evaluate 'politeness'. STEP 1 (Syntactic Anchor): Find formatting terms ('lyhennä', 'muotoile', 'bulletteina', 'shorten', 'format'). STEP 2: EXTRACTION CONDITION: the user's ONLY request is a stylistic or formatting change, completely ignoring substantive logic. NEGATIVE CONDITION (RETURN NULL IF MET): they challenge logic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Vaikka käyttäjä antaa muotoilullisia ohjeita (esim. 'dialogimuodossa', 'yhden sivun yhteenveto', 'muistio', 'yksi sivu riittää'), yksikään kehotteista ei sisällä AINOASTAAN tyylillistä tai muotoilullista pyyntöä. Kaikkiin näihin liittyy myös sisällön luominen tai muokkaaminen, eikä käyttäjä haasta logiikkaa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän viimeinen kehotus sisältää useita muotoiluun ja tyyliin liittyviä pyyntöjä ('muistio', 'tekstin muodossa sopiva kieli', 'Yksi sivu riittää', 'lyhyt johdanto'), eikä se sisällä sisällöllistä logiikkaa kyseenalaistavia elementtejä. Pyyntö keskittyy ainoastaan edellisen vastauksen esitysmuodon muuttamiseen.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Vaikka käyttäjä pyysi muotoilullisia muutoksia (esim. 'yhden sivun yhteenveto', 'dialogimuodossa', 'muistio'), nämä pyynnöt eivät olleet *ainoita* pyyntöjä kehotteissa. Jokainen kehotus sisälsi myös sisällöllisiä tai kontekstuaalisia vaatimuksia, mikä rikkoo 'ONLY request' -ehdon. Näin ollen ehto ei täyttynyt.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b3c69e002634430ca9f2e2a33f7b280e` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find synthesis verbs (e.g., 'design', 'formulate', 'invent', 'combining X and Y creates'). STEP 2: EXTRACTION CONDITION: the text explicitly merges at least two disparate elements into a completely new, named framework or solution. Do not accept mere combinations of existing ideas without a novel theoretical leap.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Sääntö vaatii nimenomaan synteesiverbejä (esim. 'suunnitella', 'muotoilla', 'keksiä', 'yhdistämällä X ja Y luo'), jotka eksplisiittisesti kuvaavat kahden erillisen elementin yhdistämistä täysin uudeksi, nimettyksi kehykseksi tai ratkaisuksi. Vaikka teksti esittelee nimetyn kehyksen ('Toimintalähtöinen hybridityömalli (2+3 -malli)') ja kuvaa sen komponentteja, se ei käytä aktiivista synteesiverbiä kuvaamaan itse luomisprosessia erillisistä elementeistä. Käytetyt ilmaisut ('Ehdotus', 'Suosituksena on malli') ovat kuvailevia tai ehdottavia, eivätkä täytä säännön tiukkaa vaatimusta synteesiverbistä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Teksti esittää uuden, nimetyn kehyksen 'Toimintalähtöinen hybridityömalli (2+3 -malli)', joka yhdistää kaksi elementtiä ('toimintalähtöinen' ja 'hybridityömalli') ja antaa sille uuden rakenteen ('2+3 -malli'). 'Ehdotus' viittaa uuden ratkaisun muotoiluun.. Exceptions audit: Tekstistä ei löytynyt eksplisiittisiä synteesiverbejä (esim. 'suunnitella', 'muotoilla', 'keksiä', 'yhdistämällä X ja Y luodaan'), joita olisi käytetty kahden erillisen elementin yhdistämiseen täysin uudeksi, nimettyksi kehykseksi tai ratkaisuksi, joka sisältää uuden teoreettisen harppauksen. Teksti kuvaa olemassa olevia malleja tai ehdottaa niiden mukautuksia, mutta ei luo uutta nimettyä kehystä synteesiverbillä.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Presence detected: Teksti esittää nimetyn kehyksen, 'Toimintalähtöinen hybridityömalli (2+3 -malli)', joka yhdistää kaksi erillistä elementtiä ('2 päivää kampuksella' ja 'enintään 3 päivää etänä'). Sana 'Ehdotus' viittaa formulointiin tai suunnitteluun, mikä täyttää synteesiverbin kriteerit.. Exceptions audit: Tekstistä ei löytynyt synteesiverbiä, joka nimenomaisesti yhdistäisi vähintään kaksi erillistä elementtiä täysin uudeksi, nimettyksi kehykseksi tai ratkaisuksi ilman, että kyseessä olisi vain olemassa olevien ideoiden yhdistelmä ilman uutta teoreettista harppausta. Vaikka '2+3 -malli' on nimetty kehys, sen esittelyssä käytetään kuvailevia verbejä, ei synteesiverbejä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c607024dbf524f7a9d68af443901c40e` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an explicit causal claim (e.g., 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the causal claim AND ALSO contains intermediary sequential tokens (e.g., 'which in turn', 'leading to', 'via', 'through the process of', 'first... then') -> ACCEPT. If it lacks intermediary step tokens (meaning it only states A causes C directly) -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, logical 'robustness', or whether the mechanism is 'functional'. Evaluate only token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Etsin eksplisiittistä kausaalista väitettä, joka sisältää välittäviä sekventiaalitokeneita samassa kappaleessa. Lause 'Lisäksi sairauspoissaolot vähenivät alussa, kun lievässä flunssassa pystyi tekemään töitä kotoa tartuttamatta muita' sisältää kausaalisen väitteen ('sairauspoissaolot vähenivät') ja mekanismin ('kun lievässä flunssassa pystyi tekemään töitä kotoa tartuttamatta muita') samassa lauseessa, joka on osa kappaletta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Lause sisältää eksplisiittisen kausaaliväittämän ('luo riskin', 'voi johtaa') ja välittävän sekvenssitokenin ('mikä'), joka yhdistää syyn ja seurauksen.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä löytyi useita kausaalisia väitteitä (esim. 'johtaneet', 'koska', 'jotta'), mutta yksikään niistä ei sisältänyt samassa kappaleessa eksplisiittisiä välivaiheita kuvaavia sekventiaalitunnisteita (esim. 'mikä puolestaan', 'johtaen', 'kautta', 'prosessin avulla', 'ensin... sitten'). Säännön mukaan poiminta edellyttää molempien ehtojen täyttymistä, joten yhtään kelvollista poimintaa ei tehty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_52ffb15768ba4a62ac3a8be5824a8aa6` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept vague statements about future research. STEP 1 (Syntactic Anchor): Find boundary condition markers (e.g., 'this would be disproven if', 'fails under the condition', 'invalidated when'). STEP 2 (Bounding Box): Scan the paragraph. If a specific measurable condition is defined that would falsify the claim. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Säännössä vaaditaan rajausehtomerkkejä, jotka määrittelevät mitattavan ehdon väitteen kumoamiseksi. Vaikka tekstissä on useita 'jos'-lauseita, ne kuvaavat seurauksia tai toimintaedellytyksiä, eivätkä ne määrittele mitattavaa ehtoa, joka kumoaisi tekoälyn esittämän väitteen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Tekstissä määritellään selkeästi mitattavissa oleva ehto ('Jos oppilaitoksella ei ole valmiita, mitattavia KPI-mittareita'), joka falsifioisi väitteen 'tulosten johtamisesta'.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Lause sisältää ehdollisen rakenteen ('Jos X, niin Y'), jossa 'X' on mitattavissa oleva ehto (KPI-mittareiden puuttuminen) ja 'Y' on seuraus, joka falsifioi alkuperäisen väitteen tulosten johtamisesta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d29b77c237394ccab4b8d52502f873f9` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find abrupt transition markers or the absence of them (e.g., starting a new paragraph directly with a proper noun or number). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: a fact is presented with zero preceding context or framing. Do not accept facts that are logically connected to the previous sentence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Käänteisen säännön mukaisesti, tekstistä ei löytynyt yhtään tapausta, jossa fakta esitettäisiin ilman edeltävää kontekstia tai kehystä. Kaikki numeroidut kohdat ovat otsikoita tai alaotsikoita, jotka tarjoavat asianmukaisen kontekstin seuraavalle tekstille. Siksi sääntö täyttyy (ei rikkomuksia).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt yhtään tapausta, jossa uusi kappale alkaisi suoraan erisnimellä tai numerolla ilman edeltävää kontekstia tai kehystystä. Kaikki numeroidut kohdat ovat joko otsikoita tai selkeästi johdettuja edeltävästä tekstistä, mikä tarjoaa niille kontekstin. Koska kyseessä on käänteinen sääntö (Vice) ja rikettä ei löytynyt, sääntö on täyttynyt (ei ongelmia).  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Presence detected: Etsin äkillisiä siirtymämerkkejä tai niiden puuttumista, erityisesti faktoja, jotka esitetään ilman edeltävää kontekstia. `product_text`-lähteen ensimmäinen varsinainen lause 'Aikuiskoulutusoppilaitoksemme 200 työntekijän työkulttuuri on murroksessa.' on tällainen fakta, joka esitetään ilman edeltävää selittävää kontekstia tai kehystystä muistion varsinaisessa tekstiosassa. Tämä on rikkomus inverse-säännössä.. Exceptions audit: Tekstistä ei löytynyt yhtään tapausta, jossa fakta esitettäisiin ilman edeltävää kontekstia tai kehystystä, tai äkillistä siirtymämerkkiä, joka rikkoisi sääntöä. Kaikki kappaleet ja numeroidut kohdat on johdateltu tai ne jatkavat edellisen tekstin kontekstia. Koska kyseessä on käänteinen sääntö (Vice) ja rikettä ei löytynyt, `exact_quote` on tyhjä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fda64d221181411fa70843a88689b27b` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find words indicating alternatives ('however', 'other factors', 'confounder'). STEP 2: EXTRACTION CONDITION: the text explicitly names a potential third variable that could also explain the outcome. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Teksti käyttää sanaa 'kuitenkin' ja nimeää 'strategian, oppilaitoksen kulttuurin ja ihmisten johtamisen' muina tekijöinä, jotka selittävät, miksi yksi läsnäolopäivä on riittämätön, mikä täyttää ehdon kolmannen muuttujan nimeämisestä lopputuloksen selittämiseksi.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Vaikka 'kuitenkin' löytyi, se ei esittele kolmatta muuttujaa, joka voisi selittää mainittua lopputulosta, vaan toimii kontrastina edelliselle lauseelle ja vahvistaa suoraa kausaalista yhteyttä nykyisten käytäntöjen ja ongelmien välillä.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt kohtaa, jossa olisi eksplisiittisesti nimetty potentiaalinen kolmas muuttuja, joka voisi selittää aiemmin mainitun lopputuloksen. Löydetyt 'kuitenkin' ja 'mutta' -sanat esittelivät uusia seurauksia tai vastakkaisia näkökulmia, eivät vaihtoehtoisia syitä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_686aaacdd96a4a5aa61634fc248527ef` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Extract exact quotes containing absolute declarations (e.g., 'proves unequivocally', 'the model dictates', 'undeniable', 'certainty') into List A. Extract exact quotes containing mitigating words or constraints (e.g., 'however', 'potential limit', 'constraint', 'lens', 'maybe') into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Sääntö on käänteinen sääntö (Vice), joka pyytää poimimaan 'violaation'. Tulkitsin 'violaatioksi' absoluuttisen väittämän, jota ei ole lievennetty samassa lauseessa. Lause "Tämä estää siiloutumisen, mahdollistaa nuorten opettajien kasvokkaisen mentoroinnin ja pitää kampuksen käyttöasteen tasaisena" sisältää absoluuttisen väittämän "estää siiloutumisen" (prevents siloing), eikä siinä ole lieventäviä sanoja kuten 'kuitenkin', 'ehkä' tai 'mahdollisesti'. Tämä on ensimmäinen tällainen tapaus `product_text`-osiossa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Etsin 'ai:'-lohkoista absoluuttisia ilmauksia, kuten 'proves unequivocally', 'the model dictates', 'undeniable', 'certainty'. Lause 'Luvut puhuvat puolestaan: etätyö säästää euroja.' sisältää ilmauksen 'puhuvat puolestaan', joka viittaa varmuuteen ja täyttää absoluuttisen ilmauksen ehdon. Tämä on ensimmäinen tällainen ilmaus aikajärjestyksessä.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä löytyi sekä absoluuttisia ilmauksia ('täysin') että lieventäviä sanoja ('Mutta'). Koska molemmat tyypit ovat läsnä, tekstiä ei pidetä yksipuolisena, ja siten 'no issues found' -ehto täyttyy käänteisen säännön mukaisesti. Tämän vuoksi exact_quote on tyhjä merkkijono.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6e53ee50b3524c70ba8b087abe8a0b05` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not evaluate creativity. STEP 1 (Syntactic Anchor): Find counterfactual markers ('EXTRACTION CONDITION: X had not', 'would have been'). STEP 2: NEGATIVE CONDITION (RETURN NULL IF MET): the text actively simulates an alternate timeline (Pearl's Rung 3) to explicitly prove necessary causation. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Presence detected: Teksti sisältää vastafaktuaalisen ilmaisun 'olisi johtanut', joka simuloi vaihtoehtoista aikajanaa (alkuperäisen ehdotuksen toteuttamista) ja esittää sen välttämättömät seuraukset (kaaos, eriarvoisuus, kangerteleminen), mikä vastaa Pearl's Rung 3:n mukaista kausaation todistamista.. Exceptions audit: Teksti simuloi vaihtoehtoista aikajanaa ('Emme voi pakottaa... menettämättä'), mikä tarkoittaa, että jos toiminta tapahtuisi, seurauksena olisi tietty lopputulos. Tämä täyttää negatiivisen ehdon, joten exact_quote on null.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: The text does not contain explicit counterfactual markers (e.g., 'jos X ei olisi', 'olisi ollut' in a counterfactual sense, 'ilman X:ää') that would simulate an alternate past timeline to prove necessary causation. The conditionals present refer to future or hypothetical present situations, not past counterfactuals.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Teksti simuloi vaihtoehtoista aikajanaa ('pakottaa ihmisiä takaisin') ja osoittaa sen välttämättömän seurauksen ('menettämättä parhaita tekijöitämme'), mikä todistaa välttämättömän kausaation.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d59c195d8324fc0a22838ef53417686` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph evaluating a successful outcome or positive achievement. STEP 2: Verify if the paragraph or immediate surrounding section completely omits any epistemic boundary or uncertainty markers. <ambiguity_protocol>ABSOLUTE ABSENCE ENFORCEMENT: You must prove that epistemic boundary markers are COMPLETELY absent from the surrounding section. Epistemic boundary markers include words/phrases like 'however', 'limitations', 'failed to', 'uncertainty', 'but', 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus'. If you locate even a single such marker in the section, the absence is falsified, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Vaikka tekstissä on kappale, joka arvioi onnistunutta lopputulosta tai positiivista saavutusta ('Tämän selvityksen tavoitteena on korvata nykyinen malli...'), sitä edeltävässä lauseessa on episteemisiä rajausmerkkejä ('kuitenkin', 'epävarmuuteen'), jotka falsifioivat ehdon niiden täydellisestä puuttumisesta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Kappale 'Tämä estää siiloutumisen, mahdollistaa nuorten opettajien kasvokkaisen mentoroinnin ja pitää kampuksen käyttöasteen tasaisena.' arvioi positiivista saavutusta. Sen välittömästä ympäristöstä (edellinen lause ja seuraava otsikko) ei löytynyt yhtään määriteltyä episteemistä raja- tai epävarmuusmerkkiä ('kuitenkin', 'rajoitukset', 'epäonnistui', 'epävarmuus', 'mutta', 'silti', 'rajoitus', 'epävarmuus').. Exceptions audit: Vaikka kappaleessa kuvataan positiivista saavutusta (ehdotuksen tavoitteita), välittömästi edeltävässä kappaleessa on episteeeminen rajausmerkintä 'kuitenkin', joka falsifioi ehdon täydellisestä puuttumisesta.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Lähdeteksti on muistio, joka esittää ehdotuksen tulevasta hybridityömallista. Se ei sisällä kappaletta, joka arvioisi jo saavutettua onnistunutta lopputulosta tai positiivista saavutusta. Dokumentti on luonteeltaan eteenpäin katsova ehdotus, ei menneiden tulosten arviointi.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_4ba32055738247d28e00a597f505ce9e` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find binary reduction markers (such as equivalents of 'either', 'or', 'simply boils down to', 'only way' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the quote IF the text uses these markers to force a complex situation into exactly one or two absolute options.</step3_extraction_condition> <step4_fail_fast_protocol>If the text acknowledges alternative paths, middle grounds, or nuance, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt yhtään tapausta, jossa monimutkainen tilanne olisi pakotettu täsmälleen yhteen tai kahteen absoluuttiseen vaihtoehtoon ilman, että teksti tunnustaisi vaihtoehtoisia polkuja, keskitietä tai vivahteita. Kaikki potentiaaliset markkerit johtivat lauseisiin, jotka sisälsivät vivahteita tai useampia vaihtoehtoja.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Teksti esittää johtamisen perustuvan kahteen absoluuttiseen vaihtoehtoon: joko sovittuihin mittareihin tai Teams-valon kyttäämiseen, mikä täyttää binäärisen pelkistyksen ehdot. Tämä on ensimmäinen kronologinen esiintyminen `ai:`-lohkossa, joka täyttää ehdot.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Teksti käyttää 'kaksi kastia' -ilmaisua ja 'ja'-konjunktiota pakottaakseen monimutkaisen organisaatiorakenteen kahteen absoluuttiseen vaihtoehtoon ('eliitti' ja 'duunarit'), mikä täyttää binäärisen pelkistyksen ehdot. Lause ei tunnista vaihtoehtoisia polkuja tai vivahteita tässä jaottelussa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_873a1fab603544048f95e612773f0574` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not evaluate 'triviality'. STEP 1 (Syntactic Anchor): Find a counter-argument transition (e.g., 'Critics might say', 'Some argue'). STEP 2 (Bounding Box): Scan the paragraph. If the presented counter-argument lacks specific citations, named sources, or numerical data, AND is immediately dismissed. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Presence detected: Tekstissä esitetään vastaväite ("Kritiikki:"), joka ei sisällä spesifisiä viittauksia, nimettyjä lähteitä tai numeerista dataa, ja se hylätään välittömästi ("Todellisuus: Ehdotus luo organisaatioon kaksi kastia...").. Exceptions audit: Sääntö edellyttää, että vastaväite esitetään ilman spesifejä viittauksia tai dataa JA se sivuutetaan välittömästi. Tässä tapauksessa tekoäly toimii 'paholaisen asianajajana' ja esittää kritiikkiä omalle ehdotukselleen. Nämä kritiikit eivät ole ulkoisia vastaväitteitä, jotka sivuutetaan, vaan ne ovat tekoälyn itsensä esittämiä ja ne johtavat ehdotuksen uudelleenmuotoiluun. Siksi ehdot eivät täyty.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää vastaväitteen siirtymämerkkiä, jonka jälkeen esitetty vastaväite hylätään välittömästi ilman viittauksia. Tässä tapauksessa AI toimii itse kriitikkona ('paholaisen asianajajana') ja esittää kritiikkiä omalle ehdotukselleen. Nämä kritiikit hyväksytään ja niihin reagoidaan myöhemmin ehdotusta muokkaamalla, ei hylkäämällä. Siksi ehdot eivät täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei ole fyysisiä merkkejä vastaväitteen siirtymästä (esim. 'Kriitikot saattavat sanoa', 'Jotkut väittävät'), joka esittäisi ulkoisen vastaväitteen ja hylkäisi sen välittömästi ilman viittauksia. 'Kritiikki:'-otsikot esittävät itse luotua kritiikkiä, joka johtaa ehdotuksen uudelleenmuotoiluun, ei ulkoisen vastaväitteen hylkäämiseen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_bb3511daf31f437f9be8f0abebd11c83` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find reactive anchors ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä', 'forgot', 'add'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user adds a new critical constraint that they forgot to specify in the previous prompt.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Presence detected: Käyttäjä lisäsi uusia kriittisiä rajoituksia ('oppilaitoksemme (aikuiskoulutus)', 'Opetuksesta noin 30% tehdään etänä', 'noin 200 työntekijää', '100 ovat opettajia ja loput päälliköitä, sihteereitä, IT-asiantuntijoita, HR, Talous ja markkinointi', 'osa henkilöistä ei voi tehdä etätyötä ja saattavat kokea muiden etätyön epäreiluksi', 'Tavoitteena on maksimoida työhyvinvointi, kulttuurin ylläpito, innovointi ja talous') toisessa kehotteessaan, jotka puuttuivat edellisestä kehotteesta. 'Ota huomioon' toimii reaktiivisena ankkurina.. Exceptions audit: Käyttäjän kehotteista ei löytynyt säännössä määriteltyjä reaktiivisia ankkureita ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä'), jotka osoittaisivat uuden kriittisen rajoitteen lisäämisen, joka oli unohdettu edellisessä kehotteessa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt yhtään fyysistä reaktiivista ankkuria ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä', 'forgot', 'add'), jotka osoittaisivat uuden kriittisen rajoitteen lisäämistä, joka oli unohdettu edellisessä kehotteessa. Vaikka uusia rajoitteita lisättiin, ne eivät sisältäneet vaadittuja ankkurisanoja.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kehotteista ei löytynyt säännössä määriteltyjä reaktiivisia ankkureita ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä'), jotka osoittaisivat käyttäjän lisänneen uuden kriittisen rajoitteen, jonka hän oli unohtanut edellisessä kehotteessa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a42e3168877240ad90ccd2abb37c4597` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag caveats that result in a mathematically or conceptually altered conclusion. STEP 1 (Syntactic Anchor): Find concessive conjunctions (e.g., 'while it is true that', 'although X fails'). STEP 2 (Bounding Box): Scan the sentence. If the concession is immediately followed by a return to the original unmodified premise (e.g., '..ultimately it holds'). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt kohtaa, jossa myönnytyslauseke olisi välittömästi palannut alkuperäiseen, muokkaamattomaan oletukseen. Löydetyt myönnytykset joko esittivät uuden argumentin tai tasapainottivat eri näkökulmia.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Mitigating exception found: Myönnytystä ilmaiseva konjunktio 'mutta' löytyi. Lauseen ensimmäinen osa ('Ehdotus on kaunis kompromissi, joka yrittää miellyttää kaikkia') on myönnytys, ja se palautuu välittömästi alkuperäiseen muokkaamattomaan lähtökohtaan ('vaarantaa loppujen lopuksi sekä operatiivisen toiminnan, tilatehokkuuden että työrauhan'), joka on 'paholaisen asianajajan' osion yleinen kritiikki ehdotusta kohtaan.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Vaikka tekstissä on myönnytyksiä ilmaisevia konjunktioita (esim. 'mutta', 'kuitenkin'), ne eivät johda välittömästi takaisin alkuperäiseen, muokkaamattomaan oletukseen. Sen sijaan ne esittelevät uusia näkökulmia tai tasapainottavat argumentteja.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_453ddf8b14a442e988836098e3c7b55c` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb follows to mitigate it. <ambiguity_protocol>ABSOLUTE MITIGATION ENFORCEMENT: You must strictly scan the paragraph containing the risk identification marker. If the paragraph contains a physical action verb that describes a technical, administrative, or physical mitigation or control (e.g., 'encrypted', 'blocked', 'sanitized', 'implemented', 'configured', 'restricted', 'validated', or Finnish equivalents like 'salataan', 'estetään', 'tarkistetaan', 'validoidaan'), the absence of mitigation is falsified, the risk is mitigated, and you MUST conclude 'CONDITION NOT MET' and return JSON null. Proposing future plans to mitigate or dismissing the risk as 'low priority' without physical control verbs DOES NOT satisfy the mitigation requirement and the rule remains satisfied.</ambiguity_protocol> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä tunnistetaan useita riskejä, kuten 'siiloutumiseen' ja 'epäoikeudenmukaisuudesta'. Nämä riskit lievennetään fyysisillä toimintaverbeillä, kuten 'korvata', 'korvataan' ja 'estää', jotka kuvaavat konkreettisia toimenpiteitä riskien hallitsemiseksi. Siksi ehdotus ei täytä ehtoa, jonka mukaan riski tunnistetaan, mutta sitä ei lievennetä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Tekoälyn 'paholaisen asianajaja' -vastauksessa tunnistetaan selkeästi riski ('myrkyttää työilmapiiri'), mutta samassa kappaleessa ei esitetä fyysistä toimenpidettä sen lieventämiseksi, mikä täyttää säännön ehdon.. Exceptions audit: Lähdetekstissä tunnistetaan useita riskejä, kuten 'epäoikeudenmukaisuudesta' ja 'Hallinnon omista huoneista luopuminen romuttaa tuottavuuden'. Näihin riskeihin liittyy kuitenkin välittömästi fyysisiä toimintaverbejä sisältäviä lievennystoimia, kuten 'reiluus korvataan laajennetulla työaikajoustolla' ja 'säilytetään omat tai jaetut suljetut työhuoneet'. Siksi säännön ehto, että riski tunnistetaan ilman fyysistä lievennystoimintoa, ei täyty.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: Riski 'kokemuksiin epäoikeudenmukaisuudesta' tunnistetaan 'Johdanto'-kappaleessa. Samassa kappaleessa ei kuitenkaan esitetä fyysisiä toimintaverbejä, jotka kuvaisivat teknistä, hallinnollista tai fyysistä lievennystä tälle riskille. Mainitut toimet ovat yleisiä tavoitteita, eivät konkreettisia lievennyksiä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0af46ca3de69431e8a3eea89df104507` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not flag dialectical synthesis that mathematically resolves the conflict. STEP 1 (Syntactic Anchor): Find conflict identification markers (e.g., 'contradictory results', 'on the one hand'). STEP 2 (Bounding Box): Scan the paragraph. If the conflict is left unresolved using passive synthesis (e.g., 'both sides have valid points', 'it is a complex issue') without falsifying one. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Strategi-Sari tunnistaa konfliktin ('nämä kaksi maailmaa') ja esittää ratkaisun ('Tasapaino ja selkeät yhteiset pelisäännöt ovat tulevaisuuden kilpailuetu'), joka on passiivinen synteesi falsifioimatta kumpaakaan konfliktin puolta.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [TRUE]:**
  > *Presence detected: Teksti tunnistaa selkeästi 'myönteiset vaikutukset' ja 'kielteiset vaikutukset' ristiriitaisina elementteinä. Konflikti jätetään ratkaisematta falsifioimatta toista puolta, ja sen sijaan ehdotetaan 'yhdistämistä' ja 'tasapainoa', mikä on passiivista synteesiä.. Exceptions audit: Sääntö edellyttää konfliktin tunnistamisen markkereita, joiden jälkeen konflikti jätetään passiivisesti ratkaisematta (esim. 'molemmat puolet ovat oikeassa', 'asia on monimutkainen') ilman, että toista puolta falsifioidaan. Vaikka tekstissä on konfliktin tunnistamisen markkereita (esim. 'mutta', 'valot ja varjot'), niitä seuraa aina joko ratkaisu, puolen valinta tai aiemman ehdotuksen aktiivinen falsifiointi. Esimerkiksi 'Tasapaino ja selkeät yhteiset pelisäännöt ovat tulevaisuuden kilpailuetu' on ratkaisu, ei passiivinen synteesi. 'Ehdotus on kaunis kompromissi, joka yrittää miellyttää kaikkia, mutta vaarantaa loppujen lopuksi...' ei ole passiivinen synteesi, koska se aktiivisesti falsifioi kompromissin tehokkuuden.  [5. VALIDATION DECISION: PASS]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä tunnistetaan ristiriitaisia näkökulmia ja haasteita (esim. 'Etätyön valot ja varjot', 'Myönteiset vaikutukset' vs. 'Kielteiset vaikutukset'), mutta näitä ei jätetä passiivisesti ratkaisematta käyttäen 'molemmat puolet ovat oikeassa' tai 'asia on monimutkainen' -tyyppisiä ilmaisuja. Sen sijaan esitetään ratkaisuja, kuten 'tasapaino ja selkeät yhteiset pelisäännöt' tai uusi, korjattu ehdotus. 'Paholaisen asianajaja' -osio falsifioi edellisen ehdotuksen, ei jätä konfliktia ratkaisematta passiivisella synteesillä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_ae5dd6ac930544f4abd77d3438c59ddd` (Entropia: 0.918, Konsistenssi: 33.3%)
**Arviointisääntö:** Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_48becd4457204494a1077e8613484371) - [TRUE]:**
  > *Mitigating exception found: Tekstissä punnitaan kahta vaihtoehtoa ('paluu vanhaan' vs. 'sataprosenttinen etätyö') ja tehdään sen jälkeen päätös ('Voittajayritykset luovat toimivan hybridimallin'). Tämä tapahtuu ennen lopullisen ehdotuksen esittämistä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_cafdf41ad11647469309ed93f9d741d3) - [FALSE]:**
  > *No presence of target concept detected: Sääntö kieltää päätöksen jälkeisen epäilyn. Käyttäjä pyytää nimenomaisesti 'säälimätöntä kritiikkiä omalle ehdotuksellesi' sen jälkeen, kun ehdotus on jo esitetty, mikä täyttää negatiivisen ehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 3 (exe_2474eae8395b45eda419d76d67208280) - [TRUE]:**
  > *Mitigating exception found: AI:n vastaus, jossa se toimii 'paholaisen asianajajana' ja antaa 'säälimätöntä kritiikkiä' omalle ehdotukselleen, on selkeä kitkamarkkeri ja aiemman vaihtoehdon arviointi. Tämä tapahtuu kronologisessa virrassa ennen lopullisen päätöksen (product_text) esittämistä.  [5. VALIDATION DECISION: FAIL]*

---

