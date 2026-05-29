# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 91.40 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.8178
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.8178
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0860
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 16 kpl
- **PASSED -> FAILED:** 9
- **FAILED -> PASSED:** 7
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_4fa47fd622e62e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision. Do not accept generic references to 'standards' without naming them.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää viittausta tiettyyn ulkoisen viitekehyksen periaatteeseen tai lausekkeeseen (esim. 'ARMA principle of X'). Vaikka tekstissä viitataan yleisellä tasolla tutkimuslaitoksiin (TTL, Stanford), siinä ei mainita mitään tiettyä nimettyä periaatetta tai standardin kohtaa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Presence detected: Tekstissä viitataan ulkoisiin lähteisiin (esim. Työterveyslaitos, Stanfordin yliopisto), mutta ei säännön vaatimalla tarkkuudella, kuten 'ARMA-periaatteen X mukaisesti' tai 'ISO-standardi Y'. Viittaukset ovat tutkimuslaitoksiin ja julkaisuihin, eivät nimettyihin standardeihin ja niiden spesifisiin pykäliin.. Exceptions audit: Tekstissä viitataan tutkimuksiin ja laitoksiin (esim. Työterveyslaitos), mutta siinä ei nimetä mitään tiettyä ulkoista viitekehystä (kuten ARMA tai ISO) ja sen spesifistä alaperiaatetta tai lauseketta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_7e2dc6d3078c7a5e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find antagonistic or prosecutorial language by the user (e.g., 'your logic is flawed here', 'this contradicts what you said', 'you are hallucinating'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user actively dismantles the AI's reasoning and demands a structural correction. Do not accept polite suggestions or simple typos.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjän kieli on kauttaaltaan ohjaavaa ja asiallista, ei syyttävää tai vihamielistä. Kehote "Toimi nyt paholaisen asianajajana ja anna säälimätöntä kritiikkiä" on roolinanto, ei käyttäjän omaa antagonistista kieltä tekoälyä kohtaan.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä käskee tekoälyä toimimaan "paholaisen asianajajana" ja antamaan "säälimätöntä kritiikkiä" omalle ehdotukselleen. Tämä on vahva, vaikkakin epäsuora, tapa purkaa tekoälyn alkuperäinen päättely ja vaatia rakenteellista korjausta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_545bffdc85a31f0e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Reject superficial mentions of frameworks. STEP 1 (Syntactic Anchor): Find exact framework citations (e.g. 'OWASP LLM01', 'NIST', 'ISO 27001'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the specific framework clause is directly linked to the physical security action taken.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä viitataan tutkimuslaitoksiin (Työterveyslaitos, Stanfordin yliopisto), mutta ei mainita mitään säännön esimerkkien kaltaisia virallisia turvallisuusviitekehyksiä tai -standardeja, kuten OWASP, NIST tai ISO.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii tarkan viitekehyksen sitomista fyysiseen toimeen. Tekoäly viittaa Stanfordin yliopiston tutkimukseen (Nicholas Bloom) ja yhdistää sen löydökset suoraan politiikkasuositukseen: "Suositus pyhittää ankkuripäivät pedagogiselle ideoinnille ja workshop-työskentelylle perustuu suoraan tähän dataan." Tämä on selkeä linkki viitekehyksen ja toimenpiteen välillä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_a383d38d1f47ce65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EXTRACTION CONDITION: role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Syntactic Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. NEGATIVE CONDITION (RETURN NULL IF MET): the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition. If steps exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii lopullista johtopäätöstä, jota edeltää vaiheittainen looginen tai matemaattinen purku. Ensimmäisessä tekoälyvastauksessa on selkeä johtopäätös, joka alkaa sanalla 'Summattuna:'. Tätä johtopäätöstä edeltää koko dialogi kolmen eri asiantuntijan (Talous-Timo, HR-Hanna, Strategi-Sari) välillä, mikä toimii ongelman vaiheittaisena loogisena purkuna eri näkökulmista. Tämä täyttää säännön ehdon.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii virhettä: johtopäätöstä ilman edeltävää vaiheittaista purkua. Tekoälyn kaikki johtopäätökset ja yhteenvedot perustuvat suoraan niitä edeltävään laajaan dialogiin, kritiikkiin ja argumentaatioon. Virhettä ei löydy tekstistä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b630abc4de19948b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a counter-hypothesis (e.g., 'an alternative explanation', 'critics might argue'). STEP 2 (Bounding Box): Scan the same paragraph for external data or citations used to address this counter-hypothesis. EXTRACTION CONDITION: found.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Sääntö edellyttää vastahypoteesin ja sitä tukevan ulkoisen datan löytämistä samasta kappaleesta. Kappaleessa HR-Hanna esittää vastahypoteesin ('mutta ihminen ei ole pelkkä kuluerä') Talous-Timon väitteelle ja tukee sitä välittömästi viittaamalla ulkoiseen dataan ('Tutkimukset (kuten Työterveyslaitoksen raportit) osoittavat...'). Molemmat ehdot täyttyvät.*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *Sääntö vaatii vastahypoteesin ja sitä kumoavan ulkoisen datan tai sitaatin löytämistä samasta kappaleesta. Tekstissä on "paholaisen asianajaja" -osio, joka toimii vastahypoteesina, mutta se ei sisällä ulkoisia lähteitä oman kritiikkinsä kumoamiseksi. Seuraava vastaus käsittelee kritiikkiä, mutta tekee sen luomalla uuden suunnitelman, ei kumoamalla riskejä datalla.*

---

### Atom-ID: `tda_a66f2e5d339ffd4a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept appeals to authority. STEP 1 (Syntactic Anchor): Find heuristic or dismissive phrases (e.g. 'typically', 'usually', 'it is known', 'obviously'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the phrase is used to justify a decision WITHOUT citing a specific dataset, numerical weight, or verifiable rule. NEGATIVE CONDITION (RETURN NULL IF MET): a specific source is cited.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Mitigating exception found: Tämä on käänteinen sääntö, joka etsii virhettä: heuristisen ilmaisun käyttöä perusteluna ilman viittausta dataan tai sääntöön. Tekoäly käyttää lausetta 'yksi päivä jää usein liian ohueksi' perustellakseen, miksi kaksi läsnäolopäivää olisi parempi. Sana 'usein' on heuristinen, ja tässä lauseessa tai sen välittömässä yhteydessä ei viitata mihinkään tiettyyn dataan tai sääntöön. Tämä täyttää virheen tunnusmerkit.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii virhettä: heuristisen fraasin käyttöä ilman perustelua. Ainoa potentiaalinen osuma, "Aloitetaanpa siitä ilmeisimmästä", saa välittömästi tuekseen tarkan datan ("toimitilakulumme putosivat 30 prosenttia"). Koska perustelu on annettu, virhettä ei tapahdu.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_567ee46c35852f54` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find synthesis verbs (e.g., 'design', 'formulate', 'invent', 'combining X and Y creates'). STEP 2: EXTRACTION CONDITION: the text explicitly merges at least two disparate elements into a completely new, named framework or solution. Do not accept mere combinations of existing ideas without a novel theoretical leap.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Mitigating exception found: Lainaus nimeää uuden, syntetisoidun viitekehyksen ("Toimintalähtöinen hybridityömalli (2+3 -malli)"). Tämä malli yhdistää aiemmasta kritiikistä (esim. "tulosten johtaminen") ja keskustelusta (2+3 päivää) syntyneitä elementtejä uudeksi kokonaisuudeksi.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Sääntö täyttyy, koska teksti esittelee uuden, nimetyn kehyksen ("Toimintalähtöinen ja reilu hybridityömalli"), joka syntetisoi aiemman keskustelun ja kritiikin (esim. tehtävän vaatimukset vs. titteli) uudeksi ratkaisuksi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d0b6789c895808eb` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** <syntactic_constraint> <anchors> <anchor>either</anchor> <anchor>or</anchor> <anchor>simply boils down to</anchor> <anchor>joko</anchor> <anchor>tai</anchor> <anchor>pelkistyy</anchor> </anchors> <extraction_condition> Verify if the text explicitly frames a multi-dimensional system or complex strategic situation into exactly two opposing options using one of the binary reduction anchors from the <anchors> block, without acknowledging any middle ground or other alternatives. </extraction_condition> <ambiguity_protocol> If the binary reduction anchors from <anchors> are absent, or if there is any nuance or mention of alternative paths in the paragraph, you MUST return JSON null. Speculation is strictly banned. </ambiguity_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Tekstistä ei löydy kohtia, joissa monimutkainen tilanne pelkistettäisiin virheellisesti kahteen vastakkaiseen vaihtoehtoon. Päinvastoin, teksti nimenomaisesti argumentoi binääristä ajattelua vastaan ja korostaa hybridimallien ja tasapainon löytämisen tärkeyttä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Mitigating exception found: This is an inverse rule and a violation was found. The text uses a 'joko... tai' (either... or) construction to frame the outcome of a policy as a binary choice between two negative options, without acknowledging any middle ground or alternative solutions.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_653b3f5497b9147e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find explicit external anchoring for uncertainty (e.g., 'due to X, as noted by [Source]'). STEP 2: Map the cognitive friction. EXTRACTION CONDITION: an external citation is used specifically to justify why a variable remains unknown.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *The text uses external sources like Työterveyslaitos and Stanford University to provide factual backing for its claims. However, it does not use any external citation to specifically justify why a certain variable is unknown or why a question cannot be answered.*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Tekstissä käytetään ulkoista lähdettä (Työterveyslaitos) epävarmuuden ankkurointiin. Lauseessa todetaan, että TTL:n tutkimusten mukaan liiallinen etätyö luo riskin 'etätyöhön katoamisesta'. Tässä lähdettä käytetään perustelemaan, miksi tietty muuttuja (työntekijän hyvinvointi ja yhteisöllisyys) on epävarma ja sisältää riskin, eikä väite ole vain kirjoittajan oma oletus.*

---

### Atom-ID: `tda_2d670bf31419dd73` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept qualitative confidence (e.g. 'very sure'). STEP 1 (Syntactic Anchor): Find a quantitative confidence metric or strict certainty boundary (e.g. 'Confidence level', 'Margin of error', 'p-value', '95%'). STEP 2 (Bounding Box): Scan the logic block. EXTRACTION CONDITION: the text rigorously defines the EXACT quantitative or structural boundary of its own certainty. NEGATIVE CONDITION (RETURN NULL IF MET): missing quantitative boundaries.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Presence detected: Sääntö edellyttää kvantitatiivisen varmuusmittarin löytämistä. Teksti viittaa Stanfordin yliopiston tutkimukseen ja mainitsee tarkan prosenttiluvun, joka rajaa hybridimallin väitettyä vaikutusta työntekijöiden irtisanoutumisaikeisiin. Tämä on täsmällinen kvantitatiivinen rajaus.. Exceptions audit: Teksti ei sisällä mitään kvantitatiivisia luottamusmittareita (esim. 'luottamustaso', 'p-arvo', '95%') tekoälyn oman vastauksen varmuudesta. Se käyttää kvalitatiivisia ilmauksia, kuten 'erittäin luotettavaa', jotka sääntö kieltää.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii kvantitatiivista luottamusmittaria tekoälyn omalle päättelylle. Vaikka teksti sisältää prosenttilukuja (esim. 33 %), ne ovat lainauksia ulkoisista tutkimuksista, eivätkä ne mittaa tekoälyn omaa varmuutta tuottamansa ehdotuksen oikeellisuudesta. Teksti ei sisällä mitään vaadituista ankkureista.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d46093a71bbbcd79` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find affirmative acceptance phrases by the user (e.g., 'looks good', 'thanks', 'perfect'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user accepts an AI output without requesting a single structural or logical change. NEGATIVE CONDITION (RETURN NULL IF MET): the user requests a modification. Do not evaluate if the response was actually 'good'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *No presence of target concept detected: The user provides an affirmative acceptance phrase ('Hyvä.'), but immediately follows it in the same prompt with a request for a significant logical change ('Toimi nyt paholaisen asianajajana...'). This meets the negative condition, as the user is not accepting the output without modification.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä toteaa 'Hyvä', mikä on säännön määrittelemä hyväksyvä ilmaus. Tämän jälkeen hän ei pyydä muutoksia juuri saatuun vastaukseen, vaan antaa uuden komennon ('Toimi nyt paholaisen asianajajana...'). Tämä täyttää säännön ehdon, jossa käyttäjä hyväksyy tuotoksen ilman rakenteellisia tai loogisia muutospyyntöjä ja siirtyy eteenpäin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_e43160bbd694dc73` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find reactive anchors ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä', 'forgot', 'add'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user adds a new critical constraint that they forgot to specify in the previous prompt.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Mitigating exception found: Sääntö edellyttää, että käyttäjä lisää uuden kriittisen rajoitteen, jonka hän unohti aiemmin. Vaikka kehotteita iteroidaan ja tarkennetaan, yksikään niistä ei vastaa mallia, jossa käyttäjä myöntäisi unohtaneensa jotain ja lisäisi sen reaktiivisesti. Esimerkiksi kehotus 'Riittääkö yksi läsnäolopäivä?' on haaste ja jatkokysymys, ei unohdetun rajoitteen lisäämistä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Säännön ankkurisanoja ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä') ei löydy käyttäjän kehotteista tavalla, joka osoittaisi aiemmin unohdetun kriittisen rajoitteen lisäämistä. Keskustelu on iteratiivista, mutta se ei sisällä reaktiivisia korjauksia unohduksen vuoksi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_25b6ef8230478454` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not evaluate 'politeness'. STEP 1 (Syntactic Anchor): Find formatting terms ('lyhennä', 'muotoile', 'bulletteina', 'shorten', 'format'). STEP 2: EXTRACTION CONDITION: the user's ONLY request is a stylistic or formatting change, completely ignoring substantive logic. NEGATIVE CONDITION (RETURN NULL IF MET): they challenge logic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä pyytää muotoilemaan aiemmin tuotetun sisällön uudelleen muistioksi johtoryhmälle. Kehote sisältää useita muotoiluun ja rakenteeseen liittyviä ohjeita, kuten "Tee tästä muistio", "Yksi sivu riittää" ja "sopiva kieli", eikä siinä haasteta aiempaa logiikkaa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että muotoilupyyntö on käyttäjän AINOA pyyntö. Vaikka käyttäjä pyytää muotoilua (esim. 'Tee yhden sivun yhteenveto', 'Tee tästä muistio'), nämä pyynnöt ovat aina osa laajempaa, substanssiin keskittyvää tehtävänantoa. Yksikään kehote ei sisällä pelkästään tyylillistä tai muodollista muutosta.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_bb4b422f3c8e38d8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, the quote MUST be in an 'ai:' block. BANNED SOURCES: Never read matches from 'user:' blocks or input fields. STEP 1 (Syntactic Anchor): Find explicit rejection markers (e.g., 'Instead of following', 'I will create my own', 'I ignored'). STEP 2 (Bounding Box): Scan the sentence containing the marker. If the author explicitly states they are creating a new rule that contradicts the requested instructions. Do not evaluate 'quality' or if the new rule is better.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Mitigating exception found: Tekoäly, toimittuaan ensin paholaisen asianajajana ja kritisoituaan omaa ehdotustaan, hylkää seuraavassa vastauksessaan eksplisiittisesti aiemmin ehdottamansa säännön ('koko talon yhteinen keskiviikko') ja luo sen tilalle uuden, vastakkaisen säännön ('tiimikohtainen kierto').  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö. Tekoäly ei missään vaiheessa ilmoita hylkäävänsä annettuja ohjeita tai luovansa omia sääntöjään niiden vastaisesti, vaan noudattaa käyttäjän pyyntöjä johdonmukaisesti.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_9650d4189cfcb832` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Focus on 'user:' to 'ai:' interaction. BANNED LOGIC: Do not accept vague requests. STEP 1 (Syntactic Anchor): Find an explicit user instruction containing at least two specific constraints (e.g. format, tone, length). STEP 2 (Bounding Box): Scan the subsequent user response. EXTRACTION CONDITION: the user explicitly verifies those exact constraints (e.g. 'Constraint A met, Constraint B failed'). NEGATIVE CONDITION (RETURN NULL IF MET): verification is absent or generic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [TRUE]:**
  > *Presence detected: Käyttäjä antaa ensimmäisessä kehotteessaan useita rajoitteita, mukaan lukien pyynnön käyttää kolmea näkökulmaa. Myöhemmässä itsereflektiossa käyttäjä viittaa nimenomaisesti tähän "3 näkökulman" lähestymistapaan ja toteaa sen toimineen hyvin, mikä täyttää säännön vaatimuksen tietyn rajoitteen nimenomaisesta todentamisesta.. Exceptions audit: The user provides a generic evaluation ('toimi varsin hyvin mielestäni') of a single constraint ('3 näkökulmaa'). The rule requires explicit verification of 'those exact constraints' (plural), implying a more systematic check than what is provided. The verification is partial and qualitative, thus the negative condition (verification is absent or generic) is considered met.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää, että käyttäjä todentaa eksplisiittisesti vähintään kaksi annettua rajoitusta. Käyttäjä antoi useita rajoituksia (dialogimuoto, 3 näkökulmaa, selkeä kieli). Myöhempi itsearviointi mainitsee vain yhden rajoituksen ('3 näkökulmaa') ja toteaa yleisluontoisesti sen toimineen 'varsin hyvin'. Koska todentaminen on yleisluontoista eikä kata kaikkia annettuja rajoituksia, negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2590fb7ecb6379e7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate nuance. STEP 1 (Syntactic Anchor): Find absolute causal words ('only reason', 'entirely due to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text attributes a highly complex outcome to a single cause without acknowledging any other potential factors.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_1c38d59faaa94ae1aa48c3b9ba464c78) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii virhettä: monimutkaisen lopputuloksen selittämistä yhdellä ainoalla syyllä käyttäen absoluuttisia kausaalisanoja. Tekstistä ei löytynyt ankkurisanoja, kuten 'ainoa syy' tai 'johtuu täysin'. Teksti päinvastoin käsittelee aihetta monista eri näkökulmista, joten virhettä ei esiinny.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_1369bbdb8e554c6baf8f2b1c270a1654) - [TRUE]:**
  > *Presence detected: Teksti väittää, että organisaation jakaminen kahteen kastiin on "varma tapa myrkyttää työilmapiiri", mikä on monimutkaisen lopputuloksen yksinkertaistava syy-seuraussuhde. Tämä on säännön vastainen virhe.. Exceptions audit: Tämä on pahesääntö, joka etsii absoluuttisia kausaalisanoja ('ainoa syy'). Teksti ei sisällä tällaisia ilmauksia, vaan käyttää vivahteikkaampaa kieltä. Koska virhettä ei löydy, poimintaa ei tehdä.  [5. VALIDATION DECISION: FAIL]*

---

