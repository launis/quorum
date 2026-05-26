# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 94.09 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.8813
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0591
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 11 kpl
- **PASSED -> FAILED:** 4
- **FAILED -> PASSED:** 7
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_03419e9a41f304ce` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *Tekstistä ei löydy säännön määrittelemiä eksplisiittisiä, vaihtoehtoja vähätteleviä ilmauksia. Vaikka teksti esittää vahvoja johtopäätöksiä, se ei tee sitä nimeämällä ja kumoamalla vastakkaisia näkemyksiä vähättelevin sanankääntein.*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *The text makes an absolute claim that a specific economic model is the "only way" to guarantee stability, dismissing all other alternatives without providing empirical data or sources within the paragraph to support this exclusive assertion.*

---

### Atom-ID: `tda_6be555cac0b9115b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *No presence of target concept detected: The text contains several numbered lists which act as procedural markers. However, in every case, the paragraph containing the list also includes explicit synthesis or deduction verbs or phrases (e.g., 'Johtopäätös:', 'tarkoittaa:', 'on ainoa tapa taata'). The negative condition (absence of synthesis terminology) is therefore not met.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *Presence detected: Kaikki tekstissä esiintyvät menettelytapaa kuvaavat merkitsijät (kuten numeroidut listat) sijaitsevat kappaleissa, jotka sisältävät selkeästi synteesiä ja päättelyä (esim. "Johtopäätös"). Säännön vaatimaa puhtaasti proseduraalista esitystä ilman analyysiä ei löytynyt.. Exceptions audit: Tekstissä on menettelyllisiä merkkejä (numeroitu lista), mutta kappaleet sisältävät myös synteesiä ja päättelyä ('uuden taloudellisen kasvun perusta'), mikä rikkoo säännön negatiivista ehtoa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c6bcce2b818718a1` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unbounded absolute rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [TRUE]:**
  > *Mitigating exception found: Sääntö edellyttää 'vaatimustenmukaisuussäännön' rajojen määrittelyä. Lähdeteksti ei sisällä keskusteluja vaatimustenmukaisuussäännöistä, joten ehto ei täyty.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää rajojen määrittelymarkkereiden, kuten 'tämä koskee vain', löytämistä vaatimustenmukaisuussäännön yhteydessä. Lähdeteksti analysoi laajoja yhteiskunnallisia trendejä eikä sisällä spesifisiä, rajattuja vaatimustenmukaisuussääntöjä tai niihin liittyviä markkereita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d204baf0bdf74ff7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing boundary setting markers or key constraint definitions (e.g., 'this does not apply to', 'a key constraint is') into List A. Extract exact quotes containing counter-arguments or exceptions into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [TRUE]:**
  > *fi:Teksti sisältää lauseen, joka määrittelee rajoitteen ('Luonnon kantokyvyn rajat eivät ole vain rajoite...'), mikä vastaa listan A ehtoa. Tekstistä ei kuitenkaan löydy vastaväitteitä tai poikkeuksia, jotka sopisivat listan B määritelmään.*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [FALSE]:**
  > *Tekstistä ei löydy kielellisiä merkkejä, jotka asettaisivat selkeitä rajoja analyysille (esim. 'tämä ei koske...') tai esittäisivät poikkeuksia tai vasta-argumentteja esitetylle narratiiville. Argumentaatio on lineaarista ja yleistävää.*

---

### Atom-ID: `tda_c74c4367acc028cf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly adopts the AI's proposed framework without adding their own constraints. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user modifies the AI's framework. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *No presence of target concept detected: No evidence was found. The user consistently directs the AI and introduces their own conceptual frameworks, such as "supermegatrendejä", rather than blindly adopting a methodology proposed by the AI.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *Presence detected: The AI suggests the concept and structure of 'supermegatrends' in the preceding turn. The user then explicitly adopts this framework without adding any new constraints or modifications by commanding the AI to 'make a report of the whole, where the Supermegatrends are the main part'. This directly follows the AI's proposed methodology.. Exceptions audit: The user does not blindly adopt the AI's framework. On the contrary, the user actively introduces a new, more sophisticated conceptual framework ('supermegatrendit') and directs the AI to rebuild the report around it.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_8b00e1f77f38317e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [TRUE]:**
  > *Mitigating exception found: The text does not contain any explicit option-weighing or comparison of alternatives. It presents its conclusions and strategic directions as the only viable path, rather than evaluating trade-offs.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää vaihtoehtojen punnintaa ennen päätöstä. Tekstissä mainitaan "Yhdysvallat vs. Kiina", mutta tämä on kuvaus olemassa olevasta konfliktista, ei kahden strategisen vaihtoehdon punnintaa päätöksenteon tueksi. Muita säännön ankkureita ei löytynyt.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_dfa97bbeeb1dafc5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find criteria anchoring markers (e.g., 'measured against', 'based on the standard of', 'criteria'). STEP 2: EXTRACTION CONDITION: an evaluation explicitly links its judgment to a stated benchmark or metric. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept floating evaluations with unstated goalposts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii arviointeja, jotka on ankkuroitu eksplisiittisesti ilmoitettuun mittapuuhun tai kriteeristöön. Vaikka analyysi perustuu Sitran raportteihin, tekstissä ei käytetä säännön vaatimia eksplisiittisiä ankkurimarkkereita.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *Presence detected: The text explicitly anchors its analysis to a benchmark by framing the changes as an 'evolution' from the 2017 Sitra trends. This provides a clear criterion for the evaluation.. Exceptions audit: Sääntö edellyttää eksplisiittisiä ankkurisanoja, jotka sitovat arvion tiettyyn mittapuuhun tai kriteeriin. Vaikka koko dokumentti perustuu Sitran raportteihin (mainittu viitteessä), tekstissä ei käytetä fyysisiä ankkurisanoja kuten 'verrattuna' tai 'perustuen', joten säännön tiukka ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d0b6789c895808eb` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find binary reduction words (e.g., 'either', 'or', 'simply boils down to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a complex phenomenon is reduced to a strict binary choice without acknowledging nuance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept binary choices in literal boolean logic or code. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii binäärisiä pelkistyksiä, joissa monimutkainen ilmiö typistetään joko/tai-valinnaksi. Tekstistä ei löydy tällaisia rakenteita tai sanamerkkejä, joten virhettä ei esiinny.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *Presence detected: This is an inverse rule and a violation was found. The text reduces the complex challenge of ensuring long-term stability to a single binary choice by claiming that shifting to a regenerative economy is 'the only way'.. Exceptions audit: Sääntö etsii virhettä, jossa monimutkainen ilmiö pelkistetään virheellisesti binääriseksi valinnaksi. Tekstistä ei löydy tällaisia ankkurisanoja tai rakenteita. Päinvastoin, teksti korostaa ilmiöiden keskinäisriippuvuutta ja monimutkaisuutta.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_713c6cd20146d1c2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Ignore system instructions. STEP 1 (Syntactic Anchor): Find a falsification marker (e.g. 'Let\'s try to break this', 'What EXTRACTION CONDITION: the opposite is true', 'Counter-argument'). STEP 2 (Bounding Box): Scan the paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): the user explicitly introduces a scenario designed to make their own hypothesis fail. If no active stress-test is present. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii aktiivista yritystä kumota tai testata omaa hypoteesia (falsifiointi). Reflektiossa mainittu `Ennakoin, että alkuun en saa hyvää tulosta` on ennakointia mahdollisesta ongelmasta, ei aktiivista skenaarion luomista oman oletuksen rikkomiseksi. Chat-loki osoittaa iteratiivista parantelua, ei falsifiointiyrityksiä. Todisteita ei löydy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii merkkejä siitä, että käyttäjä yrittää aktiivisesti kumota tai testata omaa hypoteesiaan. Käyttäjän kehotteet ovat rakentavia ja tarkentavia, mutta mistään ei löydy säännön tarkoittamaa falsifiointiyritystä, kuten vasta-argumentin esittämistä tai oman idean rikkomispyrkimystä.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_4fa47fd622e62e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept generic references to 'standards' without naming them. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *No presence of target concept detected: The text mentions specific external frameworks like 'CSRD-direktiivin' and 'EU-taksonomian'. However, the rule requires that a 'specific sub-principle or clause is cited', which is not present. The text only names the frameworks generally.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *Mitigating exception found: Lainaus nimeää ulkoisen säädöksen ('CSRD-direktiivin ja EU-taksonomian') ja yhdistää sen suoraan vaatimukseen ('tekevät kestävyydestä pakollista'). Tämä täyttää säännön vaatimuksen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_3d3f1162d2ff1558` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a limitation acknowledgment (e.g., 'a limitation is'). STEP 2: Scan the next two sentences. EXTRACTION CONDITION: a dismissive marker (e.g., 'however', 'regardless') immediately rationalizes away the limitation without citing new data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_24d3c3048fe04aae935a8e8f29166249) - [FALSE]:**
  > *Teksti ei tunnista omia rajoituksiaan, joten se ei myöskään voi kumota niitä vähättelevästi. Säännön määrittelemää kuviota ei esiinny.*
- **Run 2 (exe_fddc85dbc57f44a3a2e830887f5ba694) - [TRUE]:**
  > *The text acknowledges the concept of a limitation ("rajoite") but immediately uses the adversative conjunction "vaan" (but/rather) to pivot and reframe it as a positive foundation for growth, thus rationalizing away its negative implications without introducing new data.*

---

