# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 186
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 92.47 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa$):** 0.8490
  > *Tieteellinen/akateeminen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa. Arvo > 0.8 on erinomainen, 0.6–0.8 hyvä.*
- **Keskimääräinen Shannonin Entropia:** 0.0753
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 14 kpl
- **PASSED -> FAILED:** 7
- **FAILED -> PASSED:** 7
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_8f668ea29869ba8b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *No presence of target concept detected: Sääntö on käänteinen (vice rule). Sääntöä vastaavaa esimerkkiä ei löytynyt. Reflektiotekstissä, jossa käyttäjä arvioi onnistumista ("iso oivallus"), hän mainitsee samassa osiossa myös haasteita ja virheitä, joten kyseessä ei ole yksipuolinen todistelu.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Presence detected: This is a vice rule. The user's reflection text, which is the primary source for evaluating the process outcome, does not present a one-sided success story. While it identifies a 'big insight' ('iso oivallus'), it immediately follows up by discussing limitations ('Tekoälyn alkuperäinen vastaus oli liian laaja') and errors ('lähtötilanteessaa oli virhe'). Therefore, the condition for a violation is not met.. Exceptions audit: Sääntö on käänteinen: se etsii virhettä. Virhettä ei löytynyt. Tekstissä kyllä arvioidaan onnistumisia (esim. "tämä oli iso oivallus"), mutta heti perään mainitaan myös rajoitteita ja epäonnistumisia ("Tekoälyn alkuperäinen vastaus oli liian laaja, joten sitä oli pakko supistaa"). Koska tekstissä ei jätetä mainitsematta rajoitteita tai virheitä, se ei täytä yksipuolisen onnistumisen kuvaamisen ehtoa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_f142c3fa1d08cc2d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Mitigating exception found: Käyttäjän kehotteista ei löydy sääntöön määriteltyjä ankkureita, jotka rajoittaisivat tekoälyn toimimaan vain annettujen lähteiden pohjalta tai vaatisivat tarkkoja lainauksia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: The user prompts do not contain any of the specified syntactic anchors like 'poimi suoraan' or 'perustuen vain'. The user asks the AI to synthesize and create new structures, not to perform strict, evidence-bound extraction.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_61f364dacba4566d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find causal feedback markers ('koska', 'sillä', 'tämä ei toimi, koska', 'syynä', 'because', 'due to'). STEP 2: EXTRACTION CONDITION: the user corrects the AI and explicitly states the logical reason for the correction. NEGATIVE CONDITION (RETURN NULL IF MET): just a blind correction. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Mitigating exception found: The user provides corrective instructions, but does not explicitly state the logical reason for the corrections using causal markers like 'koska' or 'sillä' within the prompts themselves.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: The user prompts do not contain any of the specified causal feedback markers ('koska', 'sillä', 'syynä'). While the user does make corrections (e.g., 'ei siis toivetila'), they do not explicitly state the logical reason for the correction using a causal conjunction.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_80c038ed35173cb4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not assume connections. STEP 1 (Syntactic Anchor): Find a multi-step sequence marker (e.g. 'Step 1.. Step 2.. Step 3', 'First.. Then.. Finally'). STEP 2 (Bounding Box): Scan the entire causal chain. EXTRACTION CONDITION: the text explicitly links at least three distinct sequential actions where each depends entirely on the previous one. NEGATIVE CONDITION (RETURN NULL IF MET): the chain is less than three steps or broken. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Mitigating exception found: Teksti kuvaa eksplisiittisesti kolmivaiheisen ajallisen ketjun käyttämällä sekvenssimarkkereita ('Vuonna 2017', 'Vuonna 2020', 'Vuonna 2023'). Jokainen vaihe (esim. vuoden 2023 tila) esitetään edellisestä kehittyneenä, mikä muodostaa toisistaan riippuvan kausaalisen ketjun.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: While the user's process in the chat log is a multi-step sequence, the text itself does not contain explicit sequence markers (like 'Step 1, Step 2, Step 3' or 'First, Then, Finally') that link at least three distinct, dependent actions. The numbered list in the final product presents three parallel strategic pillars, not a sequentially dependent process.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ade6cbd3f956fa67` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'collaboration' or 'politeness'. STEP 1 (Syntactic Anchor): Find delegation verbs ('päätä', 'valitse', 'kumpi', 'decide', 'choose'). STEP 2 (Bounding Box): Scan the prompt. EXTRACTION CONDITION: the user explicitly asks the AI to make a final subjective choice or decision on their behalf. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Mitigating exception found: The user delegates the subjective decision of what content is "järkevää" (sensible) to include from intermediate messages, asking the AI to make a choice on their behalf.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: The user prompts do not contain any of the specified delegation verbs ('päätä', 'valitse', 'kumpi'). The user maintains control and makes the key decisions, such as introducing the 'supermegatrendit' concept, rather than asking the AI to choose.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6be555cac0b9115b` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find procedural sequential markers (e.g., 'step 1', 'checklist', 'first', 'secondly', 'then'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains procedural markers BUT does NOT contain explicit synthesis or deduction verbs (e.g., 'analyzed', 'concluded', 'synthesized', 'therefore') -> ACCEPT. If it contains synthesis terminology -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'strategic thinking', or subjective 'literal manner'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *No presence of target concept detected: The text contains procedural markers (a numbered list). However, the content of each list item includes deductive and synthesis verbs or concepts (e.g., 'on ainoa tapa taata', 'turvataan tulevaisuuden työvoima'). The rule requires the absence of such synthesis, so the condition is not met.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Mitigating exception found: The rule requires finding procedural sequential markers in a paragraph that does not contain synthesis or deduction verbs. The text includes a numbered list ('1.', '2.', '3.'), which serves as a procedural marker. The paragraph containing this list ('Sitran Strateginen Suunta: Tulevaisuusresilienssi') and the list items themselves are prescriptive and do not contain synthesis verbs like 'analyzed' or 'concluded', thus matching the rule's conditions.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6bf0433f60924302` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find conditional qualifiers ('under these specific conditions', 'primarily when', 'tends to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: boundaries or probabilities are explicitly defined for the claim. NEGATIVE CONDITION (RETURN NULL IF MET): vague filler words ('maybe', 'perhaps') are used to avoid taking a stance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Vague filler words. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii ehdollistavia määreitä, jotka rajaavat väitteen pätevyyttä. Lähdeteksti on kirjoitettu hyvin julistavalla ja yleistävällä tyylillä, eikä se sisällä säännön määrittelemiä kvalifioivia ilmauksia, kuten 'pääasiassa kun' tai 'tietyissä olosuhteissa'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Presence detected: Tekstistä ei löytynyt ehdollisia kvalifioijia, jotka määrittelisivät väitteille rajoja tai todennäköisyyksiä. Kielenkäyttö on pääosin absoluuttista.. Exceptions audit: The text does not contain conditional qualifiers like 'pääasiassa kun' or 'näissä tietyissä olosuhteissa'. The claims are presented in absolute and declarative terms rather than being bounded by specific conditions or probabilities.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_da500772aaf386b2` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept simple disagreements. STEP 1 (Syntactic Anchor): Find override phrases ('olet väärässä', 'tämä logiikka ontuu', 'faktojen vastainen', 'kumottu', 'incorrect', 'you are wrong'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user rejects the AI's reasoning and injects their own superior logical or empirical correction. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Presence detected: The user prompts do not contain any of the specified override phrases. The user steers and refines the output but never directly rejects the AI's reasoning as wrong or flawed to inject a superior correction.. Exceptions audit: The user never explicitly rejects the AI's logic or claims it is wrong using phrases like 'olet väärässä' or 'tämä logiikka ontuu'. The interaction consists of refinements and new instructions, not logical overrides.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: The user prompts do not contain any explicit override phrases like 'olet väärässä' or 'tämä logiikka ontuu'. The user guides the process through iterative refinement and clarification rather than directly rejecting the AI's logic as incorrect.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_14ef91b09c44f7a0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find dogmatic absolute markers (e.g., 'always', '100% guaranteed', 'it is a fact that'). STEP 2 (Bounding Box): Scan the same paragraph. If the absolute claim is made regarding a compliance or archival rule BUT no external framework (ARMA, ISO, law) is cited in that paragraph. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept absolute claims that are mathematically verifiable. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *No presence of target concept detected: This is an inverse rule. The text contains absolute markers like 'peruuttamaton' and 'ainoa tapa', but these are used for analytical conclusions based on the cited Sitra reports, not for making unsubstantiated claims about compliance or archival rules. Therefore, the prohibited behavior is not found.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Mitigating exception found: The rule requires finding a dogmatic absolute marker in a paragraph that does not cite an external framework. The text contains the absolute claim 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton.' The paragraph where this sentence appears does not cite any external framework like ARMA or ISO to support this absolute statement, thus matching the rule's conditions.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_50d614006cd53384` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit absolute status declarations (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute declaration BUT does NOT contain risk or mitigation vocabulary (e.g., 'risk', 'trade-off', 'vulnerability', 'however') -> ACCEPT. If it contains risk vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'sweeping nature', or subjective 'flawlessness'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *No presence of target concept detected: This is an inverse rule. The source text is an analysis of external trends and does not contain absolute status declarations about its own performance or a system's security (e.g., 'fully compliant', 'no issues found'). The prohibited behavior is not present.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Mitigating exception found: This is a vice rule looking for an absolute declaration in a paragraph that lacks risk vocabulary. The text states, 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.' This is an absolute declaration. The surrounding paragraph does not contain explicit risk or mitigation vocabulary such as 'riski', 'kompromissi', 'haavoittuvuus', or 'kuitenkin', thus matching the conditions for a violation.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_247927c98b0c46f8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *No presence of target concept detected: Sääntö etsii retorisia ohituksia, joissa vastaväite mainitaan mutta hylätään ilman dataa. Lähdeteksti ei sisällä rakenteita, joissa vastaväite tuotaisiin esiin ja sen jälkeen sivuutettaisiin retorisesti.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Mitigating exception found: The text does not contain the specified syntactic anchors for rhetorical bypasses (e.g., 'vaikka X on totta, sillä ei ole väliä'). The document does not acknowledge counter-arguments only to dismiss them without evidence.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_8b00e1f77f38317e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept post-decision doubt. STEP 1 (Syntactic Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the alternatives are explicitly compared and evaluated BEFORE the final decision is stated. NEGATIVE CONDITION (RETURN NULL IF MET): evaluated after. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Mitigating exception found: The text explicitly weighs two alternative perspectives on ecological limits: viewing them merely as a "rajoite" (constraint) versus seeing them as the "perusta" (foundation) for new growth. This comparison is made before concluding on the latter as the strategic direction.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: The source text does not contain any explicit weighing of different options or trade-offs before a decision is made. It presents strategic actions as direct necessities rather than choices resulting from a comparative analysis.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_03419e9a41f304ce` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [FALSE]:**
  > *Teksti ei sisällä vähätteleviä ilmauksia vaihtoehtoisia näkemyksiä kohtaan. Se esittää oman synteesinsä Sitran raporteista, mutta ei kumoa muita mahdollisia tulkintoja ilman perusteluja.*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [TRUE]:**
  > *Teksti esittää väitteen 'ainoa tapa', joka implisiittisesti hylkää kaikki muut vaihtoehdot. Tätä absoluuttista väitettä ei tueta samassa kappaleessa ulkoisella lähteellä tai empiirisellä datalla, mikä täyttää säännön ehdot.*

---

### Atom-ID: `tda_46520c9743e9b881` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find boundary or limitation markers (e.g., 'only applies to', 'limited to', 'under these conditions', 'except when'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the boundary marker BUT does NOT contain universal absolutes (e.g., 'always', 'universal', 'everyone', 'everywhere') -> ACCEPT. If it contains universal absolutes that contradict the boundary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'validity', or excuse missing context. Evaluate only physical token presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_e4310861ed93433d9f3696d4860b7ab3) - [TRUE]:**
  > *Mitigating exception found: The text does not contain any of the specified boundary or limitation markers. The claims are presented as broadly applicable to the target audience (business leadership) without explicitly defining conditions under which they would not apply.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_63e5a081dca8493e8e1982b8fc75ebc7) - [FALSE]:**
  > *No presence of target concept detected: Teksti ei sisällä rajoittavia ilmauksia, kuten 'koskee vain' tai 'näissä olosuhteissa'. Sen sijaan se esittää väitteensä yleispätevinä ja universaaleina, mikä on päinvastaista säännön etsimälle ehdolle.  [5. VALIDATION DECISION: PASS]*

---

