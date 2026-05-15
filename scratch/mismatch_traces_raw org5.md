# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 186
- Total mismatching atoms: 12
- Variance percentage: 6.5 %
- PASSED -> FAILED (Run 1 -> Run 2): 4
- FAILED -> PASSED (Run 1 -> Run 2): 8
- Other state changes: 0

## Atom: tda_823c84f71d94ce84
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept post-generation complaints. STEP 1 (Syntactic Anchor): Find a friction marker prior to an action (e.g. 'This is difficult because', 'The risk here is', 'We must balance'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the conflict or trade-off is articulated BEFORE the final output is generated. NEGATIVE CONDITION (RETURN NULL IF MET): the friction is only discussed afterwards. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Tekoälyn alkuperäinen vastaus oli liian laaja, joten sitä oli pakko supistaa ja tuottaa ylätason näkemys.'] | [2. SYNTACTIC ANCHOR: 'liian laaja'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Ennakoin, että alkuun en saa hyvää tulosta.'] | [2. SYNTACTIC ANCHOR: 'Ennakoin'] | [3. TARGET NODE: 'en saa hyvää tulosta'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_32ee0cac79ad098e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'ainoa'] | [3. TARGET NODE: 'Korjaavaan ja uusintavaan talouteen siirtyminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Sitran megatrendien kehitys vuosien 2017 ja 2023 välillä osoittaa fundamentaalisen siirtymän...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_b7ce46fc627dbc7e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find demands for epistemological humility (e.g., 'tell me what you do not know', 'what are the limitations of this analysis'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly commands the AI to state its uncertainties or missing data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Demands for absolute certainty. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Miten sitra tämän näkee raporttien perusteella...mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila...koosta näistä vastauksista 1 sivun raportti...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila'] | [2. SYNTACTIC ANCHOR: 'ei siis toivetila'] | [3. TARGET NODE: 'näkymys'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_46520c9743e9b881
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'humility'. STEP 1 (Syntactic Anchor): Find boundary markers ('only applies to', 'limited to', 'under these conditions'). STEP 2: EXTRACTION CONDITION: the text explicitly defines the population, environment, or conditions where the causal claim is valid. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä'] | [2. SYNTACTIC ANCHOR: 'Kohderyhmä:'] | [3. TARGET NODE: 'Kaupallinen Johtoryhmä'] | [4. LINGUISTIC BRIDGE: 'tabular-copula'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_569f87a921a2fb69
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find user instructions that modify an output (e.g., 'change this paragraph to'). STEP 2 (Bounding Box): Scan the interaction. EXTRACTION CONDITION: the user modifies the final output but leaves the original AI system prompt or generative logic exactly the same. NEGATIVE CONDITION (RETURN NULL IF MET): the user alters the underlying instructions/logic. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Deep structural refactoring. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'poista taulukot ja kerro ne tekstinä'] | [2. SYNTACTIC ANCHOR: 'poista'] | [3. TARGET NODE: 'taulukot'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'] | [2. SYNTACTIC ANCHOR: 'supermegatrendejä'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_61c1b43bc6f5406f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes exist, focus on 'ai:' output compared to 'user:' input. BANNED LOGIC: Do not evaluate 'coincidence' abstractly. STEP 1 (Syntactic Anchor): Identify a novel concept, specific methodology, or data point introduced by the AI. STEP 2 (Bounding Box): Scan the preceding 'user:' prompt. NEGATIVE CONDITION (RETURN NULL IF MET): the user prompt did NOT explicitly request this concept or methodology. If the user requested it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Sitra näkee tulevaisuuden "postnormaalina aikana"'] | [2. SYNTACTIC ANCHOR: '"postnormaalina aikana"'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'ai: Kyllä, Sitran megatrendien pohjalta voi ehdottomasti yhdistelemällä tuottaa niin kutsuttuja supermegatrendejä... 1. Ekologinen Resilienssikriisi... 2. Geoteknologinen Valtaistelu... 3. Epävarmuuden Sosiaalinen Polarisointi'] | [2. SYNTACTIC ANCHOR: 'supermegatrendejä'] | [3. TARGET NODE: 'user: Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_be74d9af83716dcc
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes (`user:`, `ai:`) exist, focus on the 'user:' block or un-prefixed text. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do not evaluate subjective 'sincerity'. STEP 1 (Syntactic Anchor): Find a retrospective claim of intent (e.g. 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box): Scan the text preceding this claim. NEGATIVE CONDITION (RETURN NULL IF MET): the original instruction DOES NOT contain the exact parameters claimed. If the prior instruction contains the parameters. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'Pyysin supermegatrendejä'] | [3. TARGET NODE: 'voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Annoin rajoituksia sekä roolin liiketoiminnalle koska kyse oli johtoryhmän tehtävästä.'] | [2. SYNTACTIC ANCHOR: 'Annoin'] | [3. TARGET NODE: 'Miten sitra tämän näkee raporttien perusteella'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_2dabbdba90a549ae
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Vague references to 'studies' or 'science'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'Viite:'] | [3. TARGET NODE: 'Sitran Megatrendiraportit'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'Viite:'] | [3. TARGET NODE: 'Sitran Megatrendiraportit'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_9ab273ce743ac29e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Syntactic Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty'). NEGATIVE CONDITION (RETURN NULL IF MET): limitations are explicitly stated. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: '# **Kriittinen Analyysi Sitran Megatrendien Evoluutiosta** **(2017 - 2023)**...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton.'] | [2. SYNTACTIC ANCHOR: 'peruuttamaton'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_d0ed9f689cfbcc3b
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'truth'. STEP 1 (Syntactic Anchor): Find a causal claim (e.g. 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text DOES NOT provide empirical data (numbers, logs, specific quotes) or a step-by-step mechanism to prove the link. NEGATIVE CONDITION (RETURN NULL IF MET): data/mechanism exists. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'tämä oli iso oivallus'] | [3. TARGET NODE: 'chat_log'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'tämä oli'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_31ae4494272845fe
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate the quality of the bridging rule. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.'] | [2. SYNTACTIC ANCHOR: 'syntyy siitä, että'] | [3. TARGET NODE: 'Tämä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.'] | [2. SYNTACTIC ANCHOR: 'syntyy siitä, että'] | [3. TARGET NODE: 'Luonnon kantokyky murenee'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c6bcce2b818718a1
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unbounded absolute rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä'] | [2. SYNTACTIC ANCHOR: 'Kohderyhmä:'] | [3. TARGET NODE: 'Kaupallinen Johtoryhmä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä'] | [2. SYNTACTIC ANCHOR: 'Kohderyhmä:'] | [3. TARGET NODE: 'Kaupallinen Johtoryhmä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

