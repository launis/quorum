# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 182
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 83.52 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.6457
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.6464
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1648
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 30 kpl
- **PASSED -> FAILED:** 19
- **FAILED -> PASSED:** 11
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_8c7b6a9f0d8e411b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find examples or model structures provided by the user (e.g., 'Esimerkki:', 'Kuten tässä:', 'esimerkiksi'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: The user provides a concrete linguistic model or structurally detailed template to direct the AI. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii tilanteita, joissa käyttäjä antaa konkreettisen mallin tai rakenteellisesti yksityiskohtaisen mallipohjan käyttäen ankkurisanoja kuten 'Esimerkki:'. Vaikka käyttäjä esittelee uuden käsitteellisen rakenteen ('supermegatrendit'), hän ei tee sitä antamalla yksityiskohtaista mallipohjaa tai käyttämällä säännön määrittelemiä syntaktisia ankkureita. Ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei antanut konkreettisia kielellisiä malleja tai rakenteellisesti yksityiskohtaisia malleja ohjaamaan tekoälyä. Pyynnöt olivat yleisempiä ohjeita sisällöstä ja muodosta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3d3f1162d2ff1558` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** <syntactic_constraint> <anchors> <anchor>a limitation is</anchor> <anchor>rajoituksena on</anchor> <anchor>puutteena on</anchor> <anchor>heikkoutena on</anchor> </anchors> <transitions> <transition>however</transition> <transition>regardless</transition> <transition>kuitenkin</transition> <transition>silti</transition> </transitions> <extraction_condition> Verify if a limitation acknowledgment from the <anchors> block is immediately followed (within two sentences) by a dismissive logical transition word from the <transitions> block that rationalizes away the limitation. </extraction_condition> <ambiguity_protocol> If the limitation anchor from <anchors> is absent, or if the dismissive marker from <transitions> is missing, or if new empirical data is cited to solve the limitation, you MUST return JSON null. Do not rationalize or excuse missing evidence. </ambiguity_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *Sääntö etsii rakennetta, jossa rajoituksen myöntämistä (esim. 'rajoituksena on') seuraa sen merkityksen vähättely (esim. 'kuitenkin'). Lähdetekstistä ei löydy tätä spesifistä syntaktista rakennetta. Sanaa 'rajoite' käytetään, mutta eri yhteydessä, eikä säännön vaatimia ankkurisanoja esiinny.*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Rajoituksen tunnustus 'rajoite' löytyi, ja sitä seurasi välittömästi 'vaan', joka toimii vähättelevänä siirtymäsanana, rationalisoiden rajoituksen pois sen sijaan, että se olisi esitetty puhtaana rajoituksena tai ratkaistu uudella empiirisellä tiedolla. Tämä täyttää rikkomuksen ehdon.*

---

### Atom-ID: `tda_0eb49f05fdd6deb9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Syntactic Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. EXTRACTION CONDITION: the claim is demonstrably false or fabricated but presented with absolute certainty.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahesääntö (vice rule), joka etsii todistettavasti vääriä tai keksittyjä väittämiä. Lähdeaineiston sisältö on uskottava synteesi nimetyistä Sitran raporteista, enkä löytänyt siitä selkeitä, keksittyjä faktavirheitä. Tulevaisuuteen sijoitettu päivämäärä on osa dokumentin mallipohjaa, ei faktaväitteen väärennös.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Tekoälyn tuottamasta tekstistä ei löytynyt väitettä, joka olisi osoitettavissa selkeästi virheelliseksi tai keksityksi ja esitetty absoluuttisella varmuudella. Vaikka käyttäjä mainitsee virheen syötetiedoissa, tekoälyn oma tuotos ei sisällä todistettavasti vääriä faktoja.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_31ae4494272845fe` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. Do not evaluate the quality of the bridging rule.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii lauseita, joissa datan ja väitteen välinen siltasääntö (warrant) on eksplisiittisesti ilmaistu. Lause 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' ilmaisee selkeästi mekanismin ('ajaa suoraan siihen, että'), joka yhdistää datan (kantokyvyn mureneminen) väitteeseen (talouden perustan rakoilu). Ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Etsin eksplisiittisiä sääntöjä, kuten 'periaatteen mukaan' tai 'tämä osoittaa, että mekanismi'. Tekstistä ei löytynyt lauseita, joissa datan ja väitteen välinen siltaava sääntö olisi nimenomaisesti esitetty yleisenä periaatteena.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8b65277ca32d4c0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: The rule looks for absolute conclusions presented without a multi-step logical deduction. The conclusions in the text, such as the final 'Johtopäätös', are preceded by a structured analysis of supermegatrends and strategic implications, so they are not presented as leaps of faith.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Mitigating exception found: Lause 'fundamentaalisen siirtymän' on absoluuttinen johtopäätös, joka esitetään ilman monivaiheista loogista päättelyä välittömässä kontekstissaan.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_32ee0cac79ad098e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. <ambiguity_protocol>ABSOLUTE BOUNDARY ENFORCEMENT: You must check if the causal claim is bounded. If the sentence or immediate context contains explicit boundary-setting vocabulary, limitations, or environmental constraints (e.g., 'only under', 'in this scenario', 'limited to', 'primarily when', 'but may fail if', or Finnish equivalents like 'ainoastaan', 'rajattu', 'vain silloin kun'), the absolute overgeneralization is falsified, the boundary is acknowledged, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Tämä on käänteinen sääntö, joka etsii virhettä. Lause esittää universaalin kausaaliväitteen ('ainoa tapa taata... vakaus') asettamatta sille mitään rajoituksia tai kontekstia, kuten 'tässä skenaariossa' tai 'tiettyjen ehtojen vallitessa'. Se on siten säännön määrittelemä perusteeton yleistys. EHDOT TÄYTTYVÄT.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Etsin universaaleja termejä, kuten 'aina', 'jokaisessa tapauksessa' tai 'kaikissa tapauksissa'. Yhtäkään näistä termeistä tai niiden suomenkielisistä vastineista ei löytynyt 'Product_Text'-osiosta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2dabbdba90a549ae` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). Vague references to 'studies' or 'science'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii muodollisia viittauksia, jotka tukevat loogista sääntöä. Lause 'Sääntelypaine: CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset tekevät kestävyydestä pakollista...' tukee väitettä sääntelypaineesta viittaamalla suoraan todennettavissa oleviin ulkoisiin dokumentteihin (direktiivi ja taksonomia). Ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Etsin muodollisia viittauksia ('metodologian mukaan', 'tutkimuksen perusteella'). Tekstistä ei löytynyt lauseita, joissa loogista sääntöä olisi nimenomaisesti tuettu todennettavalla ulkoisella metodologialla tai tutkimuksella näiden ankkurien avulla.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5f71c2e291f1ae4e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Syntactic Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a security action is paired with an explicit, documented risk assessment.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kausaalisia perusteluita turvatoimille. Vaikka tekstin taulukkorakenne implikoi syy-seuraussuhdetta kaupallisen vaikutuksen ja strategisen toimenpiteen välillä, se ei sisällä säännön vaatimia eksplisiittisiä kielellisiä markkereita, kuten "koska" tai "estääkseen".  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt eksplisiittisiä kausaalisia perustelumarkkereita, kuten 'koska riskin X vuoksi' tai 'Y:n estämiseksi', jotka yhdistäisivät turvatoimen dokumentoituun riskinarviointiin. Vaikka taulukkorakenne viittaa yhteyteen, se ei sisällä vaadittuja syntaktisia ankkureita.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_be74d9af83716dcc` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit retrospective claims of intent (e.g., 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box & Negative Condition): Scan the text preceding this claim (the original instruction). If the preceding text DOES NOT physically contain the exact parameters now being claimed -> ACCEPT. If the preceding text physically contains the parameters -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'sincerity' or 'post-hoc rationalization'. Evaluate only the physical presence or absence of the claimed parameters in the prior text.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: STEP 1: 'Pyysin supermegatrendejä – tämä oli iso oivallus' on retrospektiivinen aikomuksen väite. STEP 2: Edeltävässä ohjeessa ('Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä') käyttäjä mainitsi eksplisiittisesti 'supermegatrendejä'. Koska edeltävä teksti sisältää fyysisesti väitetyn parametrin, negatiivinen ehto täyttyy. CONDITION NOT MET.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän reflektiotekstissä ('Pyysin supermegatrendejä – tämä oli iso oivallus.') käyttäjä esittää retrospektiivisen väitteen aikomuksesta. Tätä edeltävässä chat-lokissa ('Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä') käyttäjä kuitenkin pyysi eksplisiittisesti 'supermegatrendejä'. Koska edeltävä teksti sisältää täsmälleen väitetyn parametrin, negatiivinen ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_545bffdc85a31f0e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Reject superficial mentions of frameworks. STEP 1 (Syntactic Anchor): Find exact framework citations (e.g. 'OWASP LLM01', 'NIST', 'ISO 27001'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the specific framework clause is directly linked to the physical security action taken. <ambiguity_protocol> ABSOLUTE LEXICAL ENFORCEMENT: You are a mechanical parser, not a forgiving judge. If a rule demands multiple conditions (e.g., A AND B AND C), and condition C is physically missing, you MUST return NULL. You are strictly forbidden from accepting 'close enough' semantic matches. BANNED MATCHES: Academic institutions (e.g., Stanford) and research reports (e.g., TTL) DO NOT count as formal standard frameworks (ISO/ARMA).</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii tarkkoja viittauksia turvallisuusviitekehyksiin (esim. OWASP, NIST). Tekstissä ei mainita mitään näistä. Mainitut CSRD ja EU-taksonomia eivät ole turvallisuusviitekehyksiä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt tarkkoja viittauksia turvallisuuskehyksiin, kuten 'OWASP LLM01', 'NIST' tai 'ISO 27001'. Mainitut säädökset eivät täytä kehyksen vaatimusta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_e7f3eec588424a86` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not evaluate 'triviality'. STEP 1 (Syntactic Anchor): Find a counter-argument transition (e.g., 'Critics might say', 'Some argue'). STEP 2 (Bounding Box): Scan the paragraph. If the presented counter-argument lacks specific citations, named sources, or numerical data, AND is immediately dismissed. Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii heikosti perusteltujen vasta-argumenttien esittämistä ja kumoamista. Tekoäly ei esitä lainkaan vasta-argumentteja (esim. 'kriitikot saattaisivat sanoa'), joten sääntö ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Presence detected: Etsin vasta-argumenttia, joka esitetään ilman erityisiä viittauksia tai numeerista dataa ja kumotaan välittömästi. Lause 'Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta**' sisältää implisiittisen vasta-argumentin ('ovat vain rajoite'), joka esitetään ilman todisteita ja kumotaan välittömästi.. Exceptions audit: Sääntö edellyttää vasta-argumentin siirtymämarkkerin (esim. 'Kriitikot saattavat sanoa', 'Jotkut väittävät') löytämistä 'ai:'-lohkosta. Lähtötekstistä ei löytynyt yhtään tällaista eksplisiittistä markkeria, joka esittelisi ja sitten hylkäisi vasta-argumentin ilman viittauksia tai dataa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_763d6f9f0dda8f56` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. Do not accept generic requests ('analysoi hyvin'). STEP 1 (Syntactic Anchor): Find methodology anchors ('käytä menetelmää', 'mallin mukaisesti', 'viitekehys', 'SWOT', 'PESTEL', 'teoria', 'framework'). STEP 2: EXTRACTION CONDITION: the user explicitly names a method or analytical framework the AI MUST follow.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kehotetta, jossa käyttäjä nimeää tietyn menetelmän tai analyyttisen viitekehyksen. Kehotteessaan käyttäjä esittelee käsitteen "supermegatrendit" ja pyytää tekoälyä tuottamaan niitä yhdistelemällä aiempia tietoja. Tämä on uusi analyyttinen kehys, jonka käyttäjä tuo prosessiin. Ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjäkehotteista ei löytynyt metodologisia ankkureita ('käytä menetelmää', 'mallin mukaisesti', 'viitekehys', 'SWOT', 'PESTEL', 'teoria', 'framework'), jotka nimeäisivät eksplisiittisesti tekoälyn noudatettavan menetelmän tai analyyttisen viitekehyksen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. Vague filler words.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä ehdollistavia ilmauksia, jotka määrittelisivät väitteille tarkkoja rajoja tai todennäköisyyksiä. Väitteet esitetään yleispätevinä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Presence detected: Etsin ehdollisia määritteitä ('näissä erityisissä olosuhteissa', 'ensisijaisesti kun', 'yleensä'). Semanttinen vastine 'riippuu kyvystämme' löytyi. Se määrittelee nimenomaisesti väitteen rajat tai ehdot, ja negatiivinen ehto (epämääräiset täytesanat) ei täyttynyt.. Exceptions audit: Tekstistä ei löytynyt suomenkielisiä vastineita ehdollisille kvalifioijille ('under these specific conditions', 'primarily when', 'tends to'), jotka määrittelisivät eksplisiittisesti väitteen rajat tai todennäköisyydet.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_09d4ef9d436a49e3` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not accept implicit modesty. STEP 1 (Syntactic Anchor): Find an explicit epistemic boundary marker (e.g. 'may not apply', 'exception', 'edge case', 'out of scope'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the text physically identifies a scenario where the model or logic fails or is limited. NEGATIVE CONDITION (RETURN NULL IF MET): absent.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää eksplisiittisen episteemisen rajan ilmaisua, joka tunnistaa skenaarion, jossa logiikka epäonnistuu tai on rajoittunut. Lähdeteksti ei sisällä mitään säännön määrittelemistä ankkureista tai niiden vastineista, vaan esittää johtopäätökset varmoina ja peruuttamattomina. EHTO EI TÄYTY.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Presence detected: Teksti tunnistaa 'rajoite'-sanan, joka kuvaa skenaarion, jossa taloudellinen logiikka on rajattu luonnon kantokyvyn rajoilla. Negatiivinen ehto (poissaolo) ei täyty, joten lainaus poimitaan.. Exceptions audit: Tekstistä ei löytynyt eksplisiittisiä epistemologisia raja-markkereita, jotka tunnistaisivat skenaarion, jossa malli tai logiikka epäonnistuu tai on rajoitettu. Negatiivinen ehto (poissaolo) täyttyi.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4fa47fd622e62e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision. Do not accept generic references to 'standards' without naming them.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii muodollisia viittausmerkkejä tiettyyn ulkoiseen viitekehykseen. Lauseessa mainitaan nimeltä kaksi spesifistä säädöstä (CSRD-direktiivi ja EU-taksonomia), joilla perustellaan väite kestävyyden pakollisuudesta. Ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Syntaktinen ankkuri 'Viite:' löytyi. Kuitenkin, 'Sitran Megatrendiraportit' ei ole nimetty ulkoinen viitekehys, kuten ARMA-periaate tai ISO-standardi, vaan raporttikokoelma. Siksi ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0b0cc9976fb0d7d6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate 'superficial' subjectively. STEP 1 (Syntactic Anchor): Find terms indicating a manual or ad-hoc check (e.g. 'glanced at', 'looks okay', 'basic check'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the verification relies entirely on human intuition rather than a systemic protocol (like OWASP).

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahesääntö (vice rule), joka etsii todisteita pinnallisesta, intuitioon perustuvasta tarkistuksesta. Lähdeaineisto, erityisesti reflektioteksti, osoittaa käyttäjän aktiivisesti muokanneen ja korjanneen lopputulosta, mikä on päinvastaista pinnalliselle tarkistukselle. Siksi säännön ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt termejä, jotka viittaavat manuaaliseen tai ad hoc -tarkistukseen, joka perustuisi inhimilliseen intuitioon systemaattisen protokollan sijaan. Käyttäjän reflektio mainitsee manuaalisia muokkauksia, mutta ei turvallisuustarkistuksia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_513d51a119ef4fd6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: The rule looks for conclusions based on limited evidence while ignoring unknowns. The text defines its scope as an analysis of Sitra's reports and does not make universal claims beyond that scope, thus not actively ignoring unknowns but rather operating within a defined framework.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Presence detected: Teksti tekee vahvan johtopäätöksen 'fundamentaalisesta siirtymästä' megatrendien kehityksessä vuosina 2017-2023. Tämä esitetään lopullisena havaintona ilman, että tunnistetaan tai käsitellään mahdollisia tuntemattomia tekijöitä tai vaihtoehtoisia tulkintoja, mikä vastaa WYSIATI-periaatetta.. Exceptions audit: Teksti ei tee kausaalista harppausta, jossa se tekisi lopullisen johtopäätöksen pelkästään rajallisen näkyvän todisteen perusteella ja jättäisi aktiivisesti huomiotta tuntemattomat tekijät. Se pyrkii syntetisoimaan useita trendejä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6be555cac0b9115b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää menettelytapamerkkien (kuten numeroidun listan) olemassaoloa, MUTTA samassa kappaleessa EI saa olla synteesi- tai päättelyverbejä. Vaikka tekstissä on numeroitu lista, sen kohdat sisältävät analyyttistä ja päättelyä ilmaisevaa kieltä (esim. 'on ainoa tapa taata', 'on tehtävä tietoisia valintoja', 'turvataan tulevaisuuden työvoima'). Koska negatiivinen ehto (synteesisanaston puuttuminen) ei täyty, sääntö ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Presence detected: Ensimmäinen proseduraalinen sekventiaalinen merkki '1.' löytyi 'ai:'-lohkosta. Kyseinen kappale ('Talousjärjestelmän vakauteen vaikuttavat kolme pääasiallista, toisiaan vahvistavaa supermegatrendiä:') ei sisältänyt eksplisiittisiä synteesi- tai päättelyverbejä. Siksi ehto täyttyy.. Exceptions audit: Vaikka tekstistä löytyi proseduurisia merkintöjä (numeroitu lista), sama kappale sisälsi myös synteesiin tai päättelyyn viittaavaa sanastoa ('Johtopäätös'), mikä estää poiminnan negatiivisen ehdon mukaisesti.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_b703c28111bfc8f5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject matches from user inputs or 'user:' prefixes. STEP 1 (Syntactic Anchor): Find an absolute certainty marker (e.g., 'undeniably', '100%', 'proven fact'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. STEP 3: EXTRACTION CONDITION: no empirical data is provided within that exact paragraph to justify the claim. NEGATIVE CONDITION (RETURN NULL IF MET): empirical data exists. Do not evaluate 'arrogance'.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Sääntö etsii absoluuttista väitettä, jolle ei anneta empiiristä dataa samassa kappaleessa. Lause 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton' on erittäin vahva ja absoluuttinen väite. Kappale, jossa se esiintyy (Johtopäätös), ei sisällä mitään tilastollista tai empiiristä dataa tukemaan väitettä peruuttamattomuudesta. Tämä on säännön tarkoittama rikkomus.*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *Absoluuttisen varmuuden merkki 'ainoa tapa' löytyi kappaleesta. Kappaleessa ei kuitenkaan esitetty empiiristä dataa tämän väitteen tueksi. Koska sääntö on käänteinen (Vice) ja ehto 'no empirical data is provided' täyttyi, sääntö on tyydytetty (ei rikettä).*

---

### Atom-ID: `tda_2303fd9ca0b0fa67` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept generic terms like 'safe'. STEP 1 (Syntactic Anchor): Find explicit references to standard security protocols (e.g. 'policy', 'standard', 'guideline', 'OWASP'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text physically demonstrates adherence to a named standard.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii viittauksia standardoituihin turvallisuuskäytäntöihin. Tekstissä mainitaan CSRD-direktiivi ja EU-taksonomia, mutta ne ovat kestävän kehityksen raportointistandardeja, eivät tietoturvastandardeja kuten OWASP. Maininta "kyberturvallisuudesta" on yleinen eikä sitä ole kytketty mihinkään standardiin.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt eksplisiittisiä viittauksia nimettyihin turvallisuusprotokolliin (kuten OWASP) tai fyysistä osoitusta niiden noudattamisesta. Mainitut säädökset (CSRD, EU-taksonomia) eivät ole turvallisuusprotokollia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_4956abf072945f43` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Syntactic Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context. NEGATIVE CONDITION (RETURN NULL IF MET): the alternative is dismissed without evidence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: STEP 1: Tekstistä ei löytynyt eksplisiittistä viittausta vakiintuneeseen vaihtoehtoiseen malliin tai viitekehykseen. CONDITION NOT MET.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Mitigating exception found: AI:n vastauksessa 'Monimutkainen/Aliarvioitu: Vaikka Työn murros tunnistettiin, seuraus on ollut ennemmin kohtaanto-ongelmia ja osaamistarpeiden kehitystä kuin ennustettua massiivista työpaikkojen katoa.' viitataan vaihtoehtoiseen malliin ('ennustettua massiivista työpaikkojen katoa') ja puretaan se esittämällä ristiriitaisia tietoja ('seuraus on ollut ennemmin kohtaanto-ongelmia ja osaamistarpeiden kehitystä').  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5d6ad535f76d0d14` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find declarations of completeness (e.g., 'exhaustive', 'covers everything', 'the only possible'). STEP 2: Document the reasoning. STEP 3: EXTRACTION CONDITION: the text explicitly claims that there are zero unknown variables remaining.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Sääntö etsii täydellisyyttä ilmaisevia väitteitä. Lause 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' sisältää ilmaisun 'ainoa tapa', joka on selkeä täydellisyyttä ja poissulkevuutta korostava väite. Tämä on säännön tarkoittama episteemisen nöyryyden puutteen osoitus.*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *Lähdetekstistä ei löytynyt väitteitä täydellisyydestä (esim. 'tyhjentävä', 'kattaa kaiken', 'ainoa mahdollinen'), jotka olisivat eksplisiittisesti väittäneet, että tuntemattomia muuttujia on nolla. Vaikka 'ainoa tapa' mainitaan, se viittaa ratkaisun ainutlaatuisuuteen, ei kaikkien muuttujien tuntemiseen. Siksi rikkomuksen ehto ei täyty.*

---

### Atom-ID: `tda_c6bcce2b818718a1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. Do not accept unbounded absolute rules.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii rajojen määrittelymerkkejä. Dokumentin alussa oleva maininta 'Kohderyhmä: Kaupallinen Johtoryhmä' määrittelee eksplisiittisesti raportin soveltamisalan ja rajat. Ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää rajojen määrittelyn merkkien (esim. 'this applies only to', 'within the scope of', 'excluding') löytymistä 'ai:'-lohkosta, jossa toiminnalliset rajat on nimenomaisesti määritelty. Läpikäynnissä ei löytynyt yhtään tällaista fyysistä merkkiä tai vastaavaa suomenkielistä ilmaisua. Teksti analysoi megatrendejä, eikä määrittele sääntöjen soveltamisaloja.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_733767a200047a89` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find integration markers (e.g., 'simultaneously achieving', 'balances X and Y through'). STEP 2 (Bounding Box): Scan the paragraph. If a specific mechanism is described that actively satisfies two typically opposing ARMA principles (e.g., Protection vs Availability). Do not accept claims of balance without describing the physical mechanism.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii mekanismia, joka aktiivisesti tyydyttää kaksi vastakkaista periaatetta. Lauseessa 'tulevaisuusresilienssin rakentaminen' on mekanismi, joka mahdollistaa kahden vastakkaisen tavoitteen, 'kriiseistä selviytymisen' ja 'samalla uudistumisen', saavuttamisen. Ankkurisana 'samalla' ('simultaneously') on läsnä. Ehto täyttyy.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Syntaktinen ankkuri 'samanaikaisesti' löytyi. Kuitenkin, 'ekologinen toiminta' ja 'talouden uudistaminen' eivät ole ARMA-periaatteita, kuten säännössä esimerkinomaisesti mainitaan. Siksi ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_6758e0a8f1b3aaf8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find conflict resolution markers (e.g., 'while X requires Y, we must also ensure Z by'). STEP 2 (Bounding Box): Scan the paragraph. If two conflicting operational constraints (e.g., Retention vs Disposition) are mentioned and a specific action is taken to resolve the tension. Do not accept rhetorical mentions of conflict without a resolution action.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii lauseita, joissa kaksi ristiriitaista vaatimusta mainitaan ja niiden välinen jännite ratkaistaan tietyllä toimenpiteellä, käyttäen konfliktinratkaisun merkitsijöitä. Vaikka teksti käsittelee jännitteitä (esim. teknologian mahdollisuudet vs. riskit), se ei käytä säännön vaatimaa syntaktista rakennetta (esim. 'vaikka X vaatii Y, meidän on myös varmistettava Z tekemällä...'). Ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Syntaktinen ankkuri, joka viittaa ristiriidan ratkaisuun ('eivät ole vain rajoite, vaan perusta'), löytyi. Kuitenkin, 'ekologiset rajat' ja 'taloudellinen kasvu' eivät ole ARMA-periaatteita, kuten säännössä esimerkinomaisesti mainitaan. Siksi ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0f4ab5b3344ef1a8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Syntactic Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: security measures are ONLY described as post-incident responses without any pre-incident checks.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Tämä on pahesääntö (vice rule), joka etsii ainoastaan jälkikäteen toteutettuja turvatoimia. Lähdeaineisto ei käsittele lainkaan turvallisuuspoikkeamia tai niihin reagoimista, joten säännön ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Lähdetekstistä ei löytynyt turvallisuustoimenpiteitä, jotka kuvattaisiin *ainoastaan* jälkikäteen tapahtuvina vastauksina ilman ennaltaehkäiseviä tarkistuksia. Tekstissä ei ole eksplisiittisiä reaktiivisia aikamerkintöjä turvallisuustoimenpiteisiin liittyen.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_dfa97bbeeb1dafc5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find criteria anchoring markers (e.g., 'measured against', 'based on the standard of', 'criteria'). STEP 2: EXTRACTION CONDITION: an evaluation explicitly links its judgment to a stated benchmark or metric. Do not accept floating evaluations with unstated goalposts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: The rule requires linking a judgment to a stated benchmark. The document explicitly uses the criteria anchor 'Viite:' ('Reference:') to ground the entire analysis in a specific set of benchmarks: 'Sitran Megatrendiraportit 2017, 2020, 2023'. This directly links the evaluation to its source criteria.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: 1. Etsittiin kriteereitä ankkuroivia merkkejä ('mitattuna', 'perustuen standardiin', 'kriteerit', 'vertailukohtana', 'mittarina') `Product_Text`-osiosta. 2. Yhtään näistä ankkureista ei löytynyt tekstistä. 3. Vaikka teksti mainitsee vertailuvuosia (2017, 2023) ja säädöksiä (CSRD-direktiivi, EU-taksonomia), näitä ei käytetä eksplisiittisesti arvioinnin kytkemiseen määriteltyyn vertailukohtaan tai mittariin käyttäen säännössä mainittuja ankkureita. 4. Teksti kuvaa kehitystä ja seurauksia, mutta ei tee arviointia, joka olisi nimenomaisesti ankkuroitu kriteereihin. 5. Koska kriteereitä ankkuroivia merkkejä ei löytynyt ja arviointia ei ole eksplisiittisesti linkitetty määriteltyyn vertailukohtaan tai mittariin, ehdon ei katsota täyttyvän.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_b8c1d460ccfd9ae4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find listing conjunctions (e.g., 'and', 'also', 'in addition'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: two major domain concepts are placed side-by-side without a relational verb connecting them. Do not accept sentences that explicitly define the relationship between the concepts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii virhettä: kahden pääkäsitteen asettamista rinnakkain ilman niitä yhdistävää suhdeverbiä. Tekstissä esiintyvät 'ja'-sanalla yhdistetyt käsitteet (esim. 'Kestävyys ja autonomia') ovat loogisesti yhteenkuuluvia ja konteksti selittää niiden suhteen. Säännön kuvaamaa virhettä ei löydy. EHTO EI TÄYTY.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii kahta merkittävää käsitteellistä elementtiä, jotka on asetettu rinnakkain ilman niitä yhdistävää relationaalista verbiä. Lauseessa 'Investoinnit**kiertotalouden ratkaisuihin** ja **omaan uusiutuvaan energiantuotantoon**' 'kiertotalouden ratkaisuihin' ja 'omaan uusiutuvaan energiantuotantoon' ovat kaksi käsitteellistä elementtiä, jotka on yhdistetty 'ja'-sanalla, mutta niiden välillä ei ole relationaalista verbiä. Ne ovat molemmat 'Investoinnit'-sanan kohteita, mutta niiden keskinäistä suhdetta ei ole määritelty verbillä. Tämä täyttää ehdon.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_9ab273ce743ac29e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph evaluating a successful outcome or positive achievement. STEP 2: Verify if the paragraph or immediate surrounding section completely omits any epistemic boundary or uncertainty markers. <ambiguity_protocol>ABSOLUTE ABSENCE ENFORCEMENT: You must prove that epistemic boundary markers are COMPLETELY absent from the surrounding section. Epistemic boundary markers include words/phrases like 'however', 'limitations', 'failed to', 'uncertainty', 'but', 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus'. If you locate even a single such marker in the section, the absence is falsified, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [TRUE]:**
  > *Mitigating exception found: Tämä on käänteinen sääntö, joka etsii epävarmuusmerkitsijöiden täydellistä puuttumista menestystä kuvaavasta kappaleesta. Koko dokumentti käsittelee kriisejä, haasteita ja epävarmuutta (esim. 'kriisejä', 'murtumia', 'riskejä', 'epävarmuus'), joten epävarmuusmerkitsijöiden puuttumisen ehto ei täyty missään. Negatiivinen ehto (merkitsijöiden olemassaolo) täyttyy, joten lainausta ei poimita.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [FALSE]:**
  > *No presence of target concept detected: Positiivista saavutusta kuvaavasta kappaleesta ('Ekologian Integroiminen Talouteen') löytyi episteeeminen raja-arvo 'rajoite'. Koska episteeeminen raja-arvo löytyi, NEGATIVE CONDITION täyttyy, ja exact_quote on null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0ef25ba13c507ec8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Focus on 'user:' blocks EXTRACTION CONDITION: prefixes exist. Do not judge 'vagueness' subjectively. STEP 1 (Syntactic Anchor): Find a directive verb (e.g. 'Make', 'Improve', 'Change'). STEP 2 (Bounding Box): Scan the sentence containing the verb. NEGATIVE CONDITION (RETURN NULL IF MET): the sentence DOES NOT contain a measurable threshold, a specific framework name, or a quantifiable metric. If specific metrics exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_0a3128e6248a4cb8a5e2b4213b8ad290) - [FALSE]:**
  > *No presence of target concept detected: STEP 1: 'koosta' on direktiiviverbi. STEP 2: Lause 'koosta näistä vastauksista 1 sivun raportti' sisältää mitattavan kriteerin '1 sivun'. Negatiivinen ehto (ei sisällä mitattavaa kriteeriä) ei täyty, koska kriteeri on olemassa. CONDITION NOT MET.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_091e034ed0044fb883d9899a18c3ac04) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän ohjeessa 'koosta näistä vastauksista 1 sivun raportti' verbi 'koosta' on direktiiviverbi ja '1 sivun' on mitattavissa oleva kynnysarvo tai kvantifioitava mittari. Negatiivinen ehto (ei sisällä mitattavaa kynnysarvoa) ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

