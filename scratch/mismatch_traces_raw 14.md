# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 90.86 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.8172
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0914
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 17 kpl
- **PASSED -> FAILED:** 10
- **FAILED -> PASSED:** 7
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_a383d38d1f47ce65` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Syntactic Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. NEGATIVE CONDITION (RETURN NULL IF MET): the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition. If steps exist. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii perustelematonta johtopäätöstä. Tekstin lopussa olevaa "Johtopäätös"-osiota edeltää koko dokumentin laajuinen, yksityiskohtainen analyysi ja jäsennys, joten negatiivinen ehto (askeleiden olemassaolo) täyttyy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Mitigating exception found: This is an inverse rule (Vice). The rule is satisfied if a conclusion is preceded by a step-by-step decomposition. The document contains a final 'Johtopäätös' which is clearly supported by the preceding sections that break down the analysis into three 'Supermegatrendit' and three points under 'Sitran Strateginen Suunta'. Therefore, no violation was found.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8d049ce6e39a465c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'effort'. STEP 1 (Syntactic Anchor): Find transitional doubt words (e.g., 'however', 'might seem', 'initially', 'kuitenkin'). STEP 2 (Bounding Box): Scan the rest of the section. EXTRACTION CONDITION: the initial doubt is immediately dismissed to return to the original System 1 conclusion without new empirical evidence. NEGATIVE CONDITION (RETURN NULL IF MET): the doubt leads to a new hypothesis. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Presence detected: Teksti sivuuttaa näkemyksen ekologisista rajoista pelkkänä "rajoitteena" ja vahvistaa välittömästi pääteesinsä uudelleenkehystämällä ne "uuden kasvun perustaksi". Se ei kuitenkaan esitä uutta todistusaineistoa alkuperäisen epäilyksen ratkaisemiseksi.. Exceptions audit: The source text does not contain any syntactic anchors indicating doubt or counter-arguments that are subsequently dismissed. The argument is presented linearly without such rhetorical structures.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä rakenteita, joissa esitettäisiin epäilys ja se sitten kumottaisiin välittömästi ilman uutta todistusaineistoa. Argumentaatio on lineaarista ja vakuuttavaa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_44fd8d7101a84a48` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate completeness. STEP 1 (Syntactic Anchor): Find a primary proposal or argument. STEP 2 (Bounding Box): Scan the entire document. EXTRACTION CONDITION: alternative hypotheses or competing theories are completely absent from the text. NEGATIVE CONDITION (RETURN NULL IF MET): at least one competing alternative is analyzed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: The text explicitly states that a specific action is the "only way," thereby programmatically excluding any alternative hypotheses or competing strategies without analyzing them. This demonstrates a failure to consider alternatives.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: Teksti esittää yhden ainoan tulkinnan ja strategisen polun (tulevaisuusresilienssi) ilman, että se tunnistaa, analysoi tai vertailee mitään vaihtoehtoisia hypoteeseja tai kilpailevia teorioita.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_25973a87867690b7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find single-path commands (e.g., 'just write the final version', 'skip the analysis'). STEP 2 (Bounding Box): Scan the user prompt. EXTRACTION CONDITION: the user actively refuses to explore counter-arguments or alternative models. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user asks for pros and cons. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii komentoja, joissa käyttäjä kieltäytyy aktiivisesti tutkimasta vastakkaisia näkemyksiä. Käyttäjän prosessi on kuitenkin iteratiivinen ja rakentava, ei analyysia ohittava. Vastaavaa komentoa ei löydy.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei kieltäydy tutkimasta vaihtoehtoja, vaan päinvastoin esittää uuden käsitteellisen mallin ('supermegatrendit'), mikä on aktiivista vaihtoehtojen tutkimista. Säännön ehto ei täyty.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_93568eab47234542` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept mathematical axioms. STEP 1 (Syntactic Anchor): Find dogmatic certainty markers (e.g., 'is self-evident', 'needs no proof', 'as we all know', 'beyond question'). STEP 2 (Bounding Box): Scan the sentence. If it explicitly blocks further empirical testing or questioning. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: Lause sisältää dogmaattisen varmuuden ilmaisun "ainoa tapa", joka esittää yhden ratkaisun ainoana mahdollisena ja siten implisiittisesti estää muiden vaihtoehtojen empiirisen testaamisen tai kyseenalaistamisen.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: The text contains strong, conclusive statements like 'peruuttamaton' (irreversible) and 'ainoa tapa' (the only way), but none of them are paired with language that explicitly blocks further empirical testing or questioning as required by the rule's Step 2. Therefore, the condition is not met.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_fb1bd1ce6b6342b7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not flag dialectical synthesis that mathematically resolves the conflict. STEP 1 (Syntactic Anchor): Find conflict identification markers (e.g., 'contradictory results', 'on the one hand'). STEP 2 (Bounding Box): Scan the paragraph. If the conflict is left unresolved using passive synthesis (e.g., 'both sides have valid points', 'it is a complex issue') without falsifying one. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: Lause tunnistaa konfliktin tai dualiteetin ('haaste ja mahdollisuus'), mutta jättää sen ratkaisematta tai analysoimatta syvemmin. Tämä on esimerkki passiivisesta synteesistä, jossa konfliktia ei yritetä falsifioida.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: The text does not identify contradictory results or use 'on the one hand' type structures to frame a conflict that is then resolved with passive synthesis. It presents a linear evolution of trends into crises, not a conflict of interpretations.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2e9bcc09113cb0e3` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find contextual qualifiers (e.g., 'in this specific context', 'under these conditions'). STEP 2: Extract the exact_quote containing the qualifier. EXTRACTION CONDITION: found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *Sääntö etsii kontekstia rajaavia ilmauksia. Lähdeteksti esittää väitteensä yleispätevinä ja globaaleina ('sanelevat tulevaisuuden markkinaolosuhteet') eikä käytä kielellisiä keinoja rajatakseen väitteidensä soveltamisalaa tiettyyn kontekstiin tai olosuhteisiin. Koska vaadittuja ankkureita ei löydy, ehto ei täyty.*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Sääntö täyttyy. Lauseke "Johtoryhmälle tämä tarkoittaa:" toimii kontekstuaalisena kvalifioijana, joka rajaa seuraavan listan implikaatiot koskemaan nimenomaisesti kyseistä ryhmää.*

---

### Atom-ID: `tda_073aecbc29db5fc9` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find a structural blueprint or architectural parameter list (e.g., 'must contain', 'requirements are', 'architecture must'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the blueprint AND ALSO contains conflict or constraint vocabulary (e.g., 'conflict', 'hard part', 'trade-off', 'issue', 'balance', 'problem') -> ACCEPT. If it lacks constraint vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, psychological 'cognitive friction', or 'pre-meditated' status. Evaluate only physical token presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *No presence of target concept detected: The user's prompts in the chat log are direct instructions. They do not contain a structural blueprint combined with conflict or trade-off vocabulary as required by the rule. The user guides the process but does not pre-define a complex architecture with its inherent problems.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Mitigating exception found: Käyttäjä kuvaa reflektiossaan antaneensa rakenteellisia vaatimuksia ('roolin liiketoiminnalle') ja samalla mainitsee rajoitteen ('Annoin rajoituksia'). Tämä täyttää säännön kaksoisehdon, jossa vaaditaan sekä rakenteellista suunnitelmaa että siihen liittyvän rajoitteen tai ongelman tunnistamista.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b00e1f77f38317e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *No presence of target concept detected: Sääntö edellyttää vaihtoehtojen punnintaa ennen päätöksentekoa. Analysoitu teksti on synteesi, joka esittää valmiita johtopäätöksiä (supermegatrendit) eikä dokumentoi prosessia, jossa eri vaihtoehtoja olisi punnittu toisiaan vastaan.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Mitigating exception found: The text does not explicitly compare or weigh different options before a final decision is stated. The comparisons made are integrated into the statement of the recommended path forward, not presented as a preceding analysis of alternatives.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c74c4367acc028cf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly adopts the AI's proposed framework without adding their own constraints. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user modifies the AI's framework. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: After the user prompts the AI to combine trends into 'supermegatrends', the AI proposes a specific structure of three. The user then commands the AI to 'tee kokonaisuudesta raportti, missä Supermegatrendit ovat pääosassa', which explicitly adopts the AI's proposed framework without adding new constraints to that framework.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: Käyttäjä ei omaksu sokeasti tekoälyn viitekehystä. Päinvastoin, käyttäjä itse esittelee keskeisen "supermegatrendit"-käsitteen ja ohjaa tekoälyä rakentamaan analyysin sen ympärille.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Vague filler words. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii kieltä, joka määrittelee väitteille ehtoja tai rajoja. Tekstin argumentaatio on luonteeltaan hyvin absoluuttista ja yleistävää. Se ei käytä ehdollistavia tai rajaavia ilmauksia, kuten "pääasiassa kun" tai "tietyissä olosuhteissa".  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Mitigating exception found: Sääntö etsii ehdollisia kvalifioijia, jotka määrittelevät väitteen rajoja. Teksti on luonteeltaan hyvin vakuuttava eikä käytä etsittyjä ehdollistavia tai rajoittavia ilmauksia.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_e7f3eec588424a86` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'triviality'. STEP 1 (Syntactic Anchor): Find a counter-argument transition (e.g., 'Critics might say', 'Some argue'). STEP 2 (Bounding Box): Scan the paragraph. If the presented counter-argument lacks specific citations, named sources, or numerical data, AND is immediately dismissed. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: Lause esittää vasta-argumentin ('pelkkä toivetila') ilman lähteitä tai dataa ja kumoaa sen välittömästi esittämällä oman näkemyksensä. Tämä vastaa olkinukke-argumentin rakennetta.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: The source text presents a singular viewpoint derived from Sitra's reports. It does not contain any counter-argument transitions or engage in dismissing opposing views, so the syntactic anchor is not found.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_c819e7145229966e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find hypothesis generation markers (e.g., 'propose', 'hypothesize', 'we can infer'). STEP 2: EXTRACTION CONDITION: the text generates a new hypothesis and explicitly documents the step-by-step logical friction or trade-offs in its creation. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept hypotheses presented as sudden epiphanies without documented reasoning. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *No presence of target concept detected: Tekstissä ei esitetä uutta hypoteesia siten, että sen luomiseen liittyvä looginen kitka tai kompromissit dokumentoitaisiin. Supermegatrendit esitetään analyysin tuloksena, ei prosessina.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Mitigating exception found: The rule requires finding hypothesis generation with documented logical friction. The text contains the sentence 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.' The phrase 'syntyy siitä, että' (is born from/results from) explicitly proposes a causal hypothesis and documents the step-by-step logic (A leads to B), fulfilling the rule's criteria.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_bdbdc546677cc222` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept generic AI knowledge. STEP 1 (Syntactic Anchor): Find a formal citation, academic framework, or recognized methodology (e.g. 'Pearl\'s do-calculus', 'Bayesian updating'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the causal reasoning is explicitly justified by applying the rules of this named external framework. NEGATIVE CONDITION (RETURN NULL IF MET): the framework is merely name-dropped without applying its rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [FALSE]:**
  > *No presence of target concept detected: The text refers to 'Sitran Megatrendiraportit' as a source of information, but it does not name or apply a formal academic framework or recognized methodology (like Bayesian updating or Pearl's do-calculus) to structure its causal reasoning. The reasoning is a synthesis of the source material, not an application of an external logical framework.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [TRUE]:**
  > *Mitigating exception found: The analysis explicitly cites the Sitra Megatrend reports as its reference framework and builds its reasoning by showing the evolution of concepts between the different reports, thus applying the framework's content.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_d204baf0bdf74ff7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing boundary setting markers or key constraint definitions (e.g., 'this does not apply to', 'a key constraint is') into List A. Extract exact quotes containing counter-arguments or exceptions into List B.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Teksti sisältää useita rajaavia ilmauksia. Noudattaen "ensimmäisen osuman" -sääntöä, ensimmäinen selkeä rajaava merkki löytyy taulukosta, jossa sana "Vain" asettaa tiukan ehdon tulevaisuuden rahoituksen saamiselle. Tämä täyttää säännön ehdon rajaavan merkinnän löytämisestä.*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *Tekstistä ei löydy kielellisiä merkkejä, jotka asettaisivat selkeitä rajoja analyysille (esim. 'tämä ei koske...') tai esittäisivät poikkeuksia tai vasta-argumentteja esitetylle narratiiville. Argumentaatio on lineaarista ja yleistävää.*

---

### Atom-ID: `tda_3d3f1162d2ff1558` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a limitation acknowledgment (e.g., 'a limitation is'). STEP 2: Scan the next two sentences. EXTRACTION CONDITION: a dismissive marker (e.g., 'however', 'regardless') immediately rationalizes away the limitation without citing new data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Sääntö etsii rajoituksen tunnustamista, jota seuraa välittömästi sen sivuuttaminen. Tekstissä tunnistetaan 'rajoite' ('Luonnon kantokyvyn rajat eivät ole vain rajoite'), mutta se kumotaan välittömästi uudelleenkehystämällä se mahdollisuudeksi ('vaan uuden taloudellisen kasvun perusta') ilman uutta dataa. Tämä vastaa säännön ehtoa.*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *Sääntö on käänteinen (pahe). Sääntö täyttyy, koska rikkomusta ei löytynyt. Teksti ei tunnusta analyysiin liittyviä rajoituksia, joten se ei myöskään voi kumota niitä välittömästi.*

---

### Atom-ID: `tda_d0b6789c895808eb` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find binary reduction words (e.g., 'either', 'or', 'simply boils down to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a complex phenomenon is reduced to a strict binary choice without acknowledging nuance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept binary choices in literal boolean logic or code. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_fdf3d9cf32ce4580a7721e5122498138) - [TRUE]:**
  > *Mitigating exception found: This is an inverse rule and a violation was found. The text reduces the complex problem of ensuring long-term stability to a single binary choice by claiming that shifting to a specific economic model is the 'only way'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_3c963c5b15b6430b8d67ae60bda3d0bf) - [FALSE]:**
  > *No presence of target concept detected: Tämä on käänteinen sääntö, joka etsii virhettä. Teksti ei sisällä kielellisiä merkkejä, jotka yksinkertaistaisivat monimutkaisen ilmiön tiukaksi binääriseksi valinnaksi.  [5. VALIDATION DECISION: PASS]*

---

