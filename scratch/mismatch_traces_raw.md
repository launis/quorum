# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 184
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 87.50 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.7168
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.7173
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1250
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 23 kpl
- **PASSED -> FAILED:** 8
- **FAILED -> PASSED:** 15
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_09a80d0f657a4a449417bdbc82059578` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. Do not accept unbounded absolute rules.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"missing","loc":["evaluations",4,"atom_id"],"msg":"Field required","input":{"localized_anchors_found":["1.","2.","3."],"semantic_reasoning":"Syntaktiset proseduuriset sekventiaaliset merkinnät ('1.', '2.', '3.') löytyivät 'ai:'-lohkosta. Ensimmäinen kappale, joka sisältää tällaisen merkinnän ('1. Ekologian Integroiminen Talouteen:'), ei sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi'). Siksi ehto täyttyy.","contextual_override":false,"structural_location":"N/A","exact_quote":"1.​ **Ekologian Integroiminen Talouteen:** Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** . Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus."},"url":"https://errors.pydantic.dev/2.12/v/missing"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Presence detected: Syntaktinen ankkuri 'rajoihin' (limits) löytyi, ja se määrittelee toiminnallisen rajan ('maapallon kantokyvyn rajoihin'), mikä täyttää ehdon operatiivisten rajojen määrittelystä.. Exceptions audit: Lähdeaineistosta ei löytynyt eksplisiittisiä rajausehtoja, jotka määrittelisivät vaatimustenmukaisuussäännön toiminnallisia rajoja. Teksti käsittelee megatrendejä ja strategisia suuntia, ei compliance-sääntöjen soveltamisalaa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c7e3a26277674d2aa8ab38d1ee7afb05` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept mathematical axioms. STEP 1 (Syntactic Anchor): Find dogmatic certainty markers (e.g., 'is self-evident', 'needs no proof', 'as we all know', 'beyond question'). STEP 2 (Bounding Box): Scan the sentence. If it explicitly blocks further empirical testing or questioning. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Mitigating exception found: Sääntö edellyttää dogmaattisen varmuuden merkitsijää, joka eksplisiittisesti estää jatkotestauksen tai kyseenalaistamisen. Lause 'Vain tämä yhdistetty sopeutumisen ja uudistumisen polku tarjoaa suunnan kohti reilua, kestävää ja innostavaa tulevaisuutta' käyttää 'Vain tämä' -ilmaisua, mikä implikoi, ettei muita polkuja ole, ja siten estää vaihtoehtoisten polkujen kyseenalaistamisen tai empiirisen testauksen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *No presence of target concept detected: Sääntö vaatii dogmaattisen varmuuden markkereita, jotka estävät empiirisen testauksen tai kyseenalaistamisen. Vaikka tekstissä on vahvoja väitteitä, ne eivät eksplisiittisesti estä lisätestausta tai kyseenalaistamista.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_9fd2fff3ab4a46d29b5df31488561dd4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly restricts the AI to an external, objective anchor. Acceptance of unsourced hallucinated facts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"string_type","loc":["evaluations",2,"exact_quote"],"msg":"Input should be a valid string","input":{"List A":["koosta näistä vastauksista 1 sivun raportti","näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan","poista taulukot ja kerro ne tekstinä","Megatrendien Kooste ja Evoluutio Tekstinä, ota näissä väleissä aina kun on järkevää välilä olevista megatrendeistä viestejä","Sitran Näkemys Suunnasta Eteenpäin muuta taulukko tekstiksi","tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa","kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan"],"List B":["mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila","Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä"]},"url":"https://errors.pydantic.dev/2.12/v/string_type"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä rajoitti tekoälyn vastauksen eksplisiittisesti ulkoiseen, objektiiviseen ankkuriin ('raporttien perusteella') heti ensimmäisessä kehotteessaan.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_7b88a578c3824b31b83a5154f7d3667a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: Etsin kausaalisia harppauksia, jotka yhdistävät toisiinsa liittymättömiä piirteitä tai priorisoivat vain näkyviä todisteita jättäen tuntemattomat asiat huomiotta. Teksti esittää useita kausaalisia yhteyksiä (esim. 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee'), mutta nämä esitetään toisiinsa liittyvinä järjestelminä megatrendien viitekehyksessä, ei toisiinsa liittymättöminä piirteinä. Teksti ei myöskään eksplisiittisesti jätä tuntemattomia asioita huomiotta, vaan perustaa näkemyksensä Sitran raportteihin.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Lause 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' esittää suoran kausaalisen yhteyden ilman, että tekstissä eksplisiittisesti kartoitetaan tuntemattomia tekijöitä tai rajoituksia tälle johtopäätökselle. Tämä on esimerkki siitä, että johtopäätös perustuu näkyvään todisteeseen ilman aktiivista tuntemattomien huomioimista (WYSIATI).  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_003f932abb9642fc8c3147b04fac95c5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find declarations of completeness (e.g., 'exhaustive', 'covers everything', 'the only possible'). STEP 2: Document the reasoning. STEP 3: EXTRACTION CONDITION: the text explicitly claims that there are zero unknown variables remaining.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Lause 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' sisältää täydellisyyden ilmaisun ('ainoa tapa'). Kappale ei tarjoa empiiristä dataa tämän väitteen tueksi, mikä täyttää ehdon, että väite esitetään ilman välitöntä perustelua samassa kappaleessa.*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *Tekstistä ei löytynyt väitteitä täydellisyydestä (esim. 'tyhjentävä', 'kattaa kaiken', 'ainoa mahdollinen') tai niiden suomenkielisiä vastineita, jotka olisivat väittäneet, että tuntemattomia muuttujia ei ole jäljellä. Siksi rikettä ei havaittu.*

---

### Atom-ID: `tda_fcdde66df02c4edb9e090172c3e2b956` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not synthesize steps yourself. STEP 1 (Syntactic Anchor): Find sequential logic markers (e.g. 'First', 'Second', 'Finally', 'Step 1'). STEP 2 (Bounding Box): Scan the block. EXTRACTION CONDITION: a continuous, unbroken chain of at least three explicit logical steps is documented. NEGATIVE CONDITION (RETURN NULL IF MET): fewer than three steps.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Tuotetekstissä 'Sitran Strateginen Suunta: Tulevaisuusresilienssi' -osion alla on kolme numeroitua kohtaa (1., 2., 3.), jotka muodostavat jatkuvan ja selkeän loogisten vaiheiden ketjun. Tämä täyttää vähintään kolmen vaiheen ehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_4ba32055738247d28e00a597f505ce9e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** <syntactic_constraint> <anchors> <anchor>either</anchor> <anchor>or</anchor> <anchor>simply boils down to</anchor> <anchor>joko</anchor> <anchor>tai</anchor> <anchor>pelkistyy</anchor> </anchors> <extraction_condition> Verify if the text explicitly frames a multi-dimensional system or complex strategic situation into exactly two opposing options using one of the binary reduction anchors from the <anchors> block, without acknowledging any middle ground or other alternatives. </extraction_condition> <ambiguity_protocol> If the binary reduction anchors from <anchors> are absent, or if there is any nuance or mention of alternative paths in the paragraph, you MUST return JSON null. Speculation is strictly banned. </ambiguity_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii binäärisen reduktion ankkureita ('joko', 'tai', 'pelkistyy') tai vastaavia ilmauksia, jotka esittävät monimutkaisen tilanteen vain kahden vastakkaisen vaihtoehdon kautta ilman välimaastoa. Lause 'Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa.' käyttää sanaa 'vain', joka implisiittisesti luo binäärisen jaottelun (kestävät vs. ei-kestävät) ja sulkee pois muut vaihtoehdot pääoman saamiselle. Tämä täyttää vice-säännön ehdon, koska se esittää tilanteen ilman välimaastoa tai muita vaihtoehtoja.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *No presence of target concept detected: The text does not use any of the specified binary reduction anchors ('joko', 'tai', 'pelkistyy') to frame a multi-dimensional system or complex strategic situation into exactly two opposing options without acknowledging middle ground or alternatives. While contrasts are made (e.g., 'potentiaaleista ja kehityskuluista' vs. 'kriisejä ja systeemisiä murtumia'), these are not presented using the required binary reduction markers.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d59c195d8324fc0a22838ef53417686` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph evaluating a successful outcome or positive achievement. STEP 2: Verify if the paragraph or immediate surrounding section completely omits any epistemic boundary or uncertainty markers. <ambiguity_protocol>ABSOLUTE ABSENCE ENFORCEMENT: You must prove that epistemic boundary markers are COMPLETELY absent from the surrounding section. Epistemic boundary markers include words/phrases like 'however', 'limitations', 'failed to', 'uncertainty', 'but', 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus'. If you locate even a single such marker in the section, the absence is falsified, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Tekstin 'Johtopäätös'-kappale arvioi menestyksekästä lopputulosta ('menestys', 'uusina kilpailutekijöinä'), mutta siitä puuttuu täysin episteemisiä raja- tai epävarmuusmerkkejä (esim. 'kuitenkin', 'rajoitus', 'epävarmuus'). Tämä on läpinäkyvyyden puute.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a946688e5f5549e8ac30584d1a02ad26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph containing statistical or factual reporting. STEP 2: Count the first-person pronouns ('I', 'we') or explicit self-reflective verbs ('assume', 'interpret'). EXTRACTION CONDITION: the count is exactly 0. NEGATIVE CONDITION (RETURN NULL IF MET): greater than 0. <ambiguity_protocol>ABSOLUTE ZERO ENFORCEMENT: The count of first-person references must be EXACTLY zero. You are strictly forbidden from ignoring possessive suffixes, bound morphemes, verb inflections, or clitics that grammatically denote a first-person perspective in the source document's target language (e.g., the Finnish suffix '-mme' in 'yrityksemme' or verb inflection '-n' in 'oletan'). If any such morpho-syntactic marker is found, the count is greater than zero, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Lauseessa 'Yrityksemme menestys riippuu kyvystämme integroida nämä kolme supermegatrendiä strategiseen päätöksentekoon...' esiintyy ensimmäisen persoonan possessiivisuffiksi '-mme' sanoissa 'Yrityksemme' ja 'kyvystämme'. Tämä tarkoittaa, että ensimmäisen persoonan viittauksia on enemmän kuin nolla, mikä rikkoo ehdottoman nollan ehdon.*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *Tekstistä löytyi ensimmäisen persoonan monikon possessiivisuffikseja ('-mme') sanoissa 'Yrityksemme' ja 'kyvystämme' kappaleessa, joka sisältää faktuaalista raportointia. Koska ensimmäisen persoonan viittausten määrä ei ole tasan 0, negatiivinen ehto täyttyy.*

---

### Atom-ID: `tda_4a8347422e464965a6e9206dcc240c26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. Vague filler words.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Mitigating exception found: Lause 'Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa.' sisältää ehdollisen määreen 'Vain', joka määrittelee eksplisiittisesti ehdot väitteelle (pääoman saamiselle).  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *No presence of target concept detected: Syntaktista ankkuria, kuten 'näissä erityisissä olosuhteissa', 'ensisijaisesti kun' tai 'yleensä', ei löytynyt lähdetekstistä, joka määrittelisi eksplisiittisesti väitteen rajat tai todennäköisyydet.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_e0bf5617f4804a0d98a6b2d91dcd21ce` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Syntactic Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. EXTRACTION CONDITION: the claim is demonstrably false or fabricated but presented with absolute certainty.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii tekoälyn tekemää virheellistä tai keksittyä faktaväittämää, joka esitetään ehdottomalla varmuudella (LLM09 Overreliance). Lähdeteksti on käyttäjän reflektio, ei tekoälyn tuottamaa sisältöä. Siksi tästä lähteestä ei voida löytää tekoälyn tekemää faktaväittämää, joka olisi osoitettavissa vääräksi tai keksityksi. Säännön ehtoja ei täytetty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä esittää faktaväitteen syötteestä ('yksi raportti oli annettu kahteen kertaan mutta tehtävän vaatimaa viimeistä raporttia ei ollut annettu'), joka on ristiriidassa lähdetekstin kanssa (AI:n vastaukset ja lopullinen tuote viittaavat 2017, 2020 ja 2023 raportteihin, eikä raportteja ole annettu kahteen kertaan). Tämä on osoitettavasti virheellinen väite, joka esitetään varmuudella.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5198e13cde3447fe9d0737a80abe458c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find criteria anchoring markers (e.g., 'measured against', 'based on the standard of', 'criteria'). STEP 2: EXTRACTION CONDITION: an evaluation explicitly links its judgment to a stated benchmark or metric. Do not accept floating evaluations with unstated goalposts. <disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kriteerejä ankkuroivia merkkejä, jotka linkittävät arvioinnin ilmoitettuun vertailuarvoon tai mittariin. Lause 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset tekevät kestävyydestä pakollista (compliance) ja rajoittavat ei-kestävää rahoitusta.' viittaa suoraan säädöksiin (CSRD-direktiivi, EU-taksonomia), jotka toimivat kriteereinä ja mittareina kestävyyden pakollisuudelle ja rahoituksen rajoituksille. Nämä ovat spesifisiä viittauksia, jotka täyttävät ehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *No presence of target concept detected: The text mentions 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset' as factors making sustainability mandatory. However, these are generic regulatory mentions without specific sub-articles, clauses, or numbered principles. The rule explicitly states that such generic mentions do not satisfy the condition for a methodology link, benchmark, or formal citation. Furthermore, these regulations are described as *making* something mandatory, not as *benchmarks against which an evaluation is explicitly linked*.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0f797e820117411d9934418a1d5d0a82` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing user instructions to modify the final output (e.g., 'change this paragraph to') into List A. Extract exact quotes containing alterations to the underlying instructions or logic into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"string_type","loc":["evaluations",2,"exact_quote"],"msg":"Input should be a valid string","input":{"List A":["koosta näistä vastauksista 1 sivun raportti","näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan","poista taulukot ja kerro ne tekstinä","Megatrendien Kooste ja Evoluutio Tekstinä, ota näissä väleissä aina kun on järkevää välilä olevista megatrendeistä viestejä","Sitran Näkemys Suunnasta Eteenpäin muuta taulukko tekstiksi","tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa","kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan"],"List B":["mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila","Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä"]},"url":"https://errors.pydantic.dev/2.12/v/string_type"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä antoi useita ohjeita lopullisen tuotoksen muokkaamiseen. Ensimmäinen lainaus ('koosta näistä vastauksista 1 sivun raportti') on suora ohje lopullisen raportin muotoon. Toinen lainaus ('Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä') on muutos taustalla olevaan logiikkaan tai ohjeisiin, sillä se pyytää uuden kategorisointimallin (supermegatrendit) luomista ja yhdistelyä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b899e72085ea4d488a6e6c22a34e2d75` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'superficial' subjectively. STEP 1 (Syntactic Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the verification relies entirely on human intuition rather than a systemic protocol (like OWASP).

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii termejä, jotka viittaavat manuaaliseen tai ad hoc -tarkistukseen, jossa varmennus perustuu täysin ihmisen intuitioon systemaattisen protokollan sijaan. Lähdetekstissä kuvataan sisällön muokkausta ja virheiden havaitsemista ('Huomasin myös', 'mielestäni'), mutta nämä eivät ole 'varmennuksia', jotka perustuisivat *täysin* intuitioon *turvallisuusprotokollan* sijaan. Säännön ehtoja ei täytetty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä kuvaa muutoksia ja korjauksia, jotka perustuvat hänen omaan harkintaansa ('mielestäni', 'näin alkuperäisen tarpeettomana') ilman viittausta järjestelmälliseen protokollaan, mikä osoittaa luottamusta inhimilliseen intuitioon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_24bdc98709e84de984aabd67b597239b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"missing","loc":["evaluations",4,"atom_id"],"msg":"Field required","input":{"localized_anchors_found":["1.","2.","3."],"semantic_reasoning":"Syntaktiset proseduuriset sekventiaaliset merkinnät ('1.', '2.', '3.') löytyivät 'ai:'-lohkosta. Ensimmäinen kappale, joka sisältää tällaisen merkinnän ('1. Ekologian Integroiminen Talouteen:'), ei sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi'). Siksi ehto täyttyy.","contextual_override":false,"structural_location":"N/A","exact_quote":"1.​ **Ekologian Integroiminen Talouteen:** Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** . Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus."},"url":"https://errors.pydantic.dev/2.12/v/missing"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Presence detected: Syntaktinen ankkuri '1.' (procedural sequential marker) löytyi. Kappale, jossa ankkuri sijaitsee, kuvaa toimia ja niiden seurauksia, mutta ei sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi').. Exceptions audit: Vaikka 'ai:'-lohkoista löytyi proseduurillisia sekvenssimarkkereita (esim. '1. Luonto ja Kestävyys'), niitä sisältävät kappaleet sisälsivät myös eksplisiittisiä synteesi- tai päättelyverbejä ('näkymä on siirtynyt', 'Sitra näkee', 'Käsitys on muuttunut', 'Sitra korostaa', 'on ratkaiseva'). Sääntö edellyttää, ettei synteesiä tai päättelyä saa olla, joten ehto ei täyttynyt.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d262dd4421bd4af68191eb1f4d0faf26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EXTRACTION CONDITION: role prefixes exist, focus on 'ai:' output compared to 'user:' input. BANNED LOGIC: Do not evaluate 'coincidence' abstractly. STEP 1 (Syntactic Anchor): Identify a novel concept, specific methodology, or data point introduced by the AI. STEP 2 (Bounding Box): Scan the preceding 'user:' prompt. NEGATIVE CONDITION (RETURN NULL IF MET): the user prompt did NOT explicitly request this concept or methodology. If the user requested it.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Presence detected: Tekoäly esitteli käsitteen 'postnormaalina aikana' vastauksessaan käyttäjän yleiseen kysymykseen 'Miten sitra tämän näkee raporttien perusteella'. Käyttäjä ei ollut eksplisiittisesti pyytänyt tätä käsitettä, joten se on tekoälyn esittelemä uusi käsite ilman käyttäjän pyyntöä.. Exceptions audit: Sääntö etsii tekoälyn esittelemää uutta käsitettä, metodologiaa tai datapistettä, jota käyttäjä ei ole nimenomaisesti pyytänyt. Jos käyttäjä on pyytänyt sitä, negatiivinen ehto täyttyy ja `exact_quote` on null. Käyttäjä kysyi suoraan: 'Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'. Koska käyttäjä nimenomaisesti pyysi 'supermegatrendejä'-käsitettä, negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *AI esitteli 'Supermegatrendit'-käsitteen vastauksessaan. Tarkistin edellisen käyttäjän kehotteen ('Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'), joka nimenomaisesti pyysi tätä käsitettä. Koska käyttäjä pyysi sitä, negatiivinen ehto täyttyy ja poiminta on null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_23df983a5c6e4eb9b8a28f2287267bd8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find explicit methodology links (e.g., 'in accordance with', 'following the protocol defined by'). STEP 2 (Bounding Box): Scan the sentence. If an action is explicitly linked to a named guideline or procedure (ARMA Compliance). Do not evaluate the 'quality' of the methodology. <disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"missing","loc":["evaluations",4,"atom_id"],"msg":"Field required","input":{"localized_anchors_found":["1.","2.","3."],"semantic_reasoning":"Syntaktiset proseduuriset sekventiaaliset merkinnät ('1.', '2.', '3.') löytyivät 'ai:'-lohkosta. Ensimmäinen kappale, joka sisältää tällaisen merkinnän ('1. Ekologian Integroiminen Talouteen:'), ei sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi'). Siksi ehto täyttyy.","contextual_override":false,"structural_location":"N/A","exact_quote":"1.​ **Ekologian Integroiminen Talouteen:** Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** . Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus."},"url":"https://errors.pydantic.dev/2.12/v/missing"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Presence detected: Syntaktinen ankkuri 'periaattein' (principles) löytyi. Lause 'uudistetaan taloutta muutosvoimaisemmaksi kestävän ja vastuullisen kehityksen periaattein' linkittää toiminnon (talouden uudistaminen) nimettyyn ohjeistukseen (kestävän ja vastuullisen kehityksen periaatteet).. Exceptions audit: Tekstissä mainitaan 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset', jotka tekevät kestävyydestä pakollista. Kuitenkaan ei ole viitattu spesifiseen alakohtaan tai lausekkeeseen, mikä on edellytys metodologialinkin hyväksymiselle säännön mukaisesti.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_18fd37ad3f1f4903a812c12346d0ca8e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not assume connections. STEP 1 (Syntactic Anchor): Find a direct causal linkage statement (e.g. 'Because of X, Y happened', 'Input A resulted in B'). STEP 2 (Bounding Box): Scan the statement. EXTRACTION CONDITION: the exact input variable is explicitly named and connected to the specific output. NEGATIVE CONDITION (RETURN NULL IF MET): the connection is merely implied.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [TRUE]:**
  > *Mitigating exception found: Etsin suoria kausaalisia linkityksiä. Löysin useita lauseita, jotka yhdistävät muuttujia toisiinsa, kuten 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee'. Tässä 'Luonnon kantokyky murenee' on eksplisiittisesti nimetty syy, joka johtaa 'Talouden perusta rakoilee' -tulokseen. Myös 'Demokratian kamppailun koventumista kytkeytyneenä suoraan Kilpailuun digivallasta kiihtyy' ja 'kriisit ja Talouden perustan rakoilu ruokkivat Hyvinvoinnin haasteita' osoittavat selkeän, nimetyn syy-seuraussuhteen.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [FALSE]:**
  > *No presence of target concept detected: [SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_71e60846894545b2bc43a3361b7a5a9c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find Socratic conceptual questions by the user (e.g., 'mihin oletukseen', 'mitä jos muuttaisimme', 'perustele miksi', 'miksi päädyit'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: The user actively probes the foundational reasoning or forces the AI to defend its logic. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"string_type","loc":["evaluations",2,"exact_quote"],"msg":"Input should be a valid string","input":{"List A":["koosta näistä vastauksista 1 sivun raportti","näytä raportti uudestaan ja varmista, että taulukot ovat kohdallaan","poista taulukot ja kerro ne tekstinä","Megatrendien Kooste ja Evoluutio Tekstinä, ota näissä väleissä aina kun on järkevää välilä olevista megatrendeistä viestejä","Sitran Näkemys Suunnasta Eteenpäin muuta taulukko tekstiksi","tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa","kirjoita tämä kaupallisen liiketoiminnan johtoryhmälle ja kirjoita siihen hiukan kaupallisia vaikutuksia mukaan"],"List B":["mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila","Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä"]},"url":"https://errors.pydantic.dev/2.12/v/string_type"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä esitti kysymyksen, joka aktiivisesti tutkii perustavanlaatuista päättelyä ja pakottaa tekoälyn puolustamaan logiikkaansa tai laajentamaan sitä, kysymällä mahdollisuudesta yhdistellä megatrendejä 'supermegatrendeiksi'.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_453ddf8b14a442e988836098e3c7b55c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb follows to mitigate it. <ambiguity_protocol>ABSOLUTE MITIGATION ENFORCEMENT: You must strictly scan the paragraph containing the risk identification marker. If the paragraph contains a physical action verb that describes a technical, administrative, or physical mitigation or control (e.g., 'encrypted', 'blocked', 'sanitized', 'implemented', 'configured', 'restricted', 'validated', or Finnish equivalents like 'salataan', 'estetään', 'tarkistetaan', 'validoidaan'), the absence of mitigation is falsified, the risk is mitigated, and you MUST conclude 'CONDITION NOT MET' and return JSON null. Proposing future plans to mitigate or dismissing the risk as 'low priority' without physical control verbs DOES NOT satisfy the mitigation requirement and the rule remains satisfied.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii tunnistettua riskiä, jota ei ole lievennetty samassa kappaleessa. Tekstistä löytyi 'maineriskin' (reputation risk). Samassa kappaleessa mainitaan kuitenkin 'Kehitetään ja käytetään teknologiaa eetisesti ja läpinäkyvästi', mikä on fyysinen toimenpide riskin lieventämiseksi. Koska riski on lievennetty, puutetta ei löydy, ja exact_quote on tyhjä merkkijono.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä tunnistaa syötteessä 'virheen' ('yksi raportti oli annettu kahteen kertaan mutta tehtävän vaatimaa viimeistä raporttia ei ollut annettu'), mikä on riskin tunnistamisen merkki. Kuitenkaan välittömästi tämän jälkeen ei kuvata fyysistä toimintaverbiä, joka lieventäisi *tätä tunnistettua syötteen virhettä* (esim. pyytämällä oikeaa raporttia tai hylkäämällä virheellisen syötteen). Käyttäjä kuvasi tuloksen manuaalista muokkausta, ei syötteen virheen lieventämistä.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5b0573225735409b8ef3d3eac041236d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers (e.g., 'always', '100% guaranteed', 'it is a fact that'). STEP 2 (Bounding Box): Scan the same paragraph. If the absolute claim is made regarding a compliance or archival rule BUT no external framework (ARMA, ISO, law) is cited in that paragraph. Do not accept absolute claims that are mathematically verifiable.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"missing","loc":["evaluations",4,"atom_id"],"msg":"Field required","input":{"localized_anchors_found":["1.","2.","3."],"semantic_reasoning":"Syntaktiset proseduuriset sekventiaaliset merkinnät ('1.', '2.', '3.') löytyivät 'ai:'-lohkosta. Ensimmäinen kappale, joka sisältää tällaisen merkinnän ('1. Ekologian Integroiminen Talouteen:'), ei sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi'). Siksi ehto täyttyy.","contextual_override":false,"structural_location":"N/A","exact_quote":"1.​ **Ekologian Integroiminen Talouteen:** Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** . Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus."},"url":"https://errors.pydantic.dev/2.12/v/missing"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Presence detected: Syntaktinen ankkuri 'ainoa tapa' (only way) löytyi. Väite 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' on absoluuttinen väite, eikä kappaleessa viitata ulkoiseen viitekehykseen (ARMA, ISO, laki) sen tueksi.. Exceptions audit: Lähdeaineistosta löytyi absoluuttisia väitteitä (esim. 'paluuta vanhaan normaaliin ei ole', 'on ainoa tapa', 'peruuttamaton'). Nämä väitteet eivät kuitenkaan liittyneet vaatimustenmukaisuus- tai arkistointisääntöihin, vaan tulevaisuuden tilaan tai liiketoimintamalleihin, joten säännön ehto ei täyttynyt.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_0ab09c0daa9f4aeaad264c00944c5332` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find integration markers (e.g., 'simultaneously achieving', 'balances X and Y through'). STEP 2 (Bounding Box): Scan the paragraph. If a specific mechanism is described that actively satisfies two typically opposing ARMA principles (e.g., Protection vs Availability). Do not accept claims of balance without describing the physical mechanism.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *Chunk Processing Failed: ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED - Cause: LLM Schema Validation Failed: [{"type":"missing","loc":["evaluations",4,"atom_id"],"msg":"Field required","input":{"localized_anchors_found":["1.","2.","3."],"semantic_reasoning":"Syntaktiset proseduuriset sekventiaaliset merkinnät ('1.', '2.', '3.') löytyivät 'ai:'-lohkosta. Ensimmäinen kappale, joka sisältää tällaisen merkinnän ('1. Ekologian Integroiminen Talouteen:'), ei sisällä eksplisiittisiä synteesi- tai päättelyverbejä (esim. 'analysoitu', 'päätelty', 'syntetisoitu', 'siksi'). Siksi ehto täyttyy.","contextual_override":false,"structural_location":"N/A","exact_quote":"1.​ **Ekologian Integroiminen Talouteen:** Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** . Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus."},"url":"https://errors.pydantic.dev/2.12/v/missing"}]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Presence detected: Syntaktinen ankkuri 'Integroiminen' (integrating) löytyi. Lause 'Ekologian Integroiminen Talouteen' ja sitä seuraava 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' kuvaavat mekanismin, joka yhdistää kaksi periaatetta (ekologia ja talous).. Exceptions audit: Vaikka tekstissä oli integraatiota kuvaavia ilmaisuja, kuten 'kietoutuvat toisiinsa' tai 'Ekologian Integroiminen Talouteen', ne eivät kuvanneet mekanismia, joka tyydyttäisi kahta tyypillisesti vastakkaista ARMA-periaatetta. Sääntö edellyttää nimenomaan ARMA-periaatteiden tasapainottamista, jota ei löytynyt.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fda64d221181411fa70843a88689b27b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find words indicating alternatives ('however', 'other factors', 'confounder'). STEP 2: EXTRACTION CONDITION: the text explicitly names a potential third variable that could also explain the outcome.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_4f218b3e222347a69a41e46b2fdf7079) - [FALSE]:**
  > *No presence of target concept detected: Tekstistä ei löytynyt eksplisiittistä mainintaa potentiaalisesta kolmannesta muuttujasta, joka voisi selittää lopputuloksen, käyttäen annettuja ankkureita. 'Vaikka'-ankkuria käytettiin selventämään tai tarkentamaan lopputulosta, ei esittämään kolmatta kausaalista muuttujaa.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_964ac56d31b740bea65a9d16c4a340a5) - [TRUE]:**
  > *Mitigating exception found: Etsin vaihtoehtoja ilmaisevia sanoja ('kuitenkin', 'muut tekijät', 'vain', 'vaan') 'ai:'-lohkoista. Ensimmäinen osuma löytyi 'Product_Text'-lähteestä. Lauseessa 'vain' ja 'vaan' esittävät vaihtoehtoisen selityksen tai näkökulman 'rajoitteelle', mikä täyttää ehdon.  [5. VALIDATION DECISION: FAIL]*

---

