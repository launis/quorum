# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 166
- Total mismatching atoms: 5
- Variance percentage: 3.0 %
- PASSED -> FAILED (Run 1 -> Run 2): 3
- FAILED -> PASSED (Run 1 -> Run 2): 2
- Other state changes: 0

## Atom: tda_bce60530213249dd
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'spurious'. STEP 1 (Syntactic Anchor): Find causal words (e.g. 'causes', 'because'). STEP 2 (Bounding Box): Scan the same sentence. EXTRACTION CONDITION: the causal claim is backed ONLY by a statistical correlation or simultaneous occurrence without any physical mechanism. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.'] | [2. SYNTACTIC ANCHOR: 'ajaa suoraan siihen, että'] | [3. TARGET NODE: 'Talouden perusta rakoilee'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Tämä syntyy siitä, että Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.'] | [2. SYNTACTIC ANCHOR: 'ajaa suoraan siihen, että'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_3d3cb300ed841868
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find absolute novelty claims (e.g., 'a completely new paradigm', 'never seen before'). STEP 2 (Bounding Box): Scan the section. EXTRACTION CONDITION: a synthesized framework floats purely in abstraction without ANY citations or anchoring to concrete prior expert literature. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept grounded hypotheses that cite valid external precedents. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023) Supermegatrendit Postnormaalissa Ajassa: Kaupalliset Vaikutukset'] | [2. SYNTAKTINEN ANKKURI: 'none'] | [3. KOHDESOLMU: 'none'] | [4. KIELITIETEELLINEN SILTA: 'none'] | [5. VALIDOINTIPÄÄTÖS: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'Viite:'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_4a25fd353d8bd05b
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find abrupt transition markers or the absence of them (e.g., starting a new paragraph directly with a proper noun or number). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: a fact is presented with zero preceding context or framing. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept facts that are logically connected to the previous sentence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä Päivämäärä: 27. lokakuuta 2025 Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTAKTINEN ANKKURI: 'none'] | [3. KOHDESOLMU: 'none'] | [4. KIELITIETEELLINEN SILTA: 'none'] | [5. VALIDOINTIPÄÄTÖS: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023) Supermegatrendit Postnormaalissa Ajassa: Kaupalliset Vaikutukset'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_ffc598b99c3f13fc
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate relevance. STEP 1 (Syntactic Anchor): Find personal anecdotes ('for example, I', 'one time'). STEP 2: EXTRACTION CONDITION: a universal causal rule is explicitly derived SOLELY from a single personal anecdote. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023)'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023)...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_be74d9af83716dcc
**Rule:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in a 'user:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'ai:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit retrospective claims of intent (e.g., 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box & Negative Condition): Scan the text preceding this claim (the original instruction). If the preceding text DOES NOT physically contain the exact parameters now being claimed -> ACCEPT. If the preceding text physically contains the parameters -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'sincerity' or 'post-hoc rationalization'. Evaluate only the physical presence or absence of the claimed parameters in the prior text. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Annoin rajoituksia sekä roolin liiketoiminnalle koska kyse oli johtoryhmän tehtävästä.'] | [2. SYNTACTIC ANCHOR: 'Annoin'] | [3. TARGET NODE: 'Miten sitra tämän näkee raporttien perusteella'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'Pyysin'] | [3. TARGET NODE: 'supermegatrendejä'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

---

