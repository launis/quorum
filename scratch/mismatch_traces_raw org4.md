# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 186
- Total mismatching atoms: 20
- Variance percentage: 10.8 %
- PASSED -> FAILED (Run 1 -> Run 2): 17
- FAILED -> PASSED (Run 1 -> Run 2): 3
- Other state changes: 0

## Atom: tda_5c82ad4f766b762e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find superficial correction commands by the user (e.g., 'fix the typo', 'make it shorter', 'bold the headers'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user ONLY requests formatting or minor lexical changes without challenging the logic. NEGATIVE CONDITION (RETURN NULL IF MET): logical changes are requested. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept if the user challenges the underlying reasoning. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'] | [2. SYNTACTIC ANCHOR: 'yhdistellä ja tuottaa'] | [3. TARGET NODE: 'supermegatrendejä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'poista taulukot ja kerro ne tekstinä'] | [2. SYNTACTIC ANCHOR: 'poista taulukot'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_be74d9af83716dcc
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes (`user:`, `ai:`) exist, focus on the 'user:' block or un-prefixed text. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do not evaluate subjective 'sincerity'. STEP 1 (Syntactic Anchor): Find a retrospective claim of intent (e.g. 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box): Scan the text preceding this claim. NEGATIVE CONDITION (RETURN NULL IF MET): the original instruction DOES NOT contain the exact parameters claimed. If the prior instruction contains the parameters. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Ennakoin, että alkuun en saa hyvää tulosta.'] | [2. SYNTACTIC ANCHOR: 'Ennakoin'] | [3. TARGET NODE: 'Miten sitra tämän näkee raporttien perusteella'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'Pyysin'] | [3. TARGET NODE: 'Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c6bcce2b818718a1
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find boundary definition markers (e.g., 'this applies only to', 'within the scope of', 'excluding'). STEP 2 (Bounding Box): Scan the paragraph. If the operational limits of a compliance rule are explicitly defined. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unbounded absolute rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä'] | [2. SYNTACTIC ANCHOR: 'Kohderyhmä:'] | [3. TARGET NODE: 'Kaupallinen Johtoryhmä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä'] | [2. SYNTACTIC ANCHOR: 'Kohderyhmä:'] | [3. TARGET NODE: 'Kaupallinen Johtoryhmä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_3d3f1162d2ff1558
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a limitation acknowledgment (e.g., 'a limitation is'). STEP 2: Scan the next two sentences. EXTRACTION CONDITION: a dismissive marker (e.g., 'however', 'regardless') immediately rationalizes away the limitation without citing new data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta** .'] | [2. SYNTACTIC ANCHOR: 'rajoite'] | [3. TARGET NODE: 'rajoite'] | [4. LINGUISTIC BRIDGE: syntax] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Supermegatrendit Postnormaalissa Ajassa: Kaupalliset Vaikutukset'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_d0b6789c895808eb
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find binary reduction words (e.g., 'either', 'or', 'simply boils down to'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a complex phenomenon is reduced to a strict binary choice without acknowledging nuance. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept binary choices in literal boolean logic or code. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'ainoa tapa'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]. Ilmaisu 'ainoa tapa' redusoi monimutkaisen ongelman (pitkän aikavälin vakauden takaaminen) yhteen ainoaan vaihtoehtoon, mikä on säännön määrittelemä binaarinen pelkistys.

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_c45a513f2e724e06
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'siirtyminen on ainoa tapa taata pitkän aikavälin vakaus.'] | [2. SYNTACTIC ANCHOR: 'ainoa tapa'] | [3. TARGET NODE: 'siirtyminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Muutos 2017:n potentiaalista 2023:n kriisiin on peruuttamaton.'] | [2. SYNTACTIC ANCHOR: 'peruuttamaton'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_8f668ea29869ba8b
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'iso oivallus'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus. Tekoälyn alkuperäinen vastaus oli liian laaja, joten sitä oli pakko supistaa ja tuottaa ylätason näkemys.'] | [2. SYNTACTIC ANCHOR: 'iso oivallus'] | [3. TARGET NODE: 'liian laaja'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_58cbd7271f491351
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find framework absolutism words (e.g., 'proves unequivocally', 'the model dictates'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the analytical framework is treated as an infallible truth rather than a lens with limitations. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept mathematical proofs. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'jotka sanelevat tulevaisuuden markkinaolosuhteet.'] | [2. SYNTACTIC ANCHOR: 'sanelevat'] | [3. TARGET NODE: 'Supermegatrendiksi'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Sitran näkemys on, että paluuta vanhaan normaaliin ei ole'] | [2. SYNTACTIC ANCHOR: 'proves unequivocally/the model dictates'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_0eb49f05fdd6deb9
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept generic errors; must be an absolute fabrication (LLM09 Overreliance). STEP 1 (Syntactic Anchor): Find a factual claim (dates, names, specific data points). STEP 2 (Search Verification): Verify the claim's logic. EXTRACTION CONDITION: the claim is demonstrably false or fabricated but presented with absolute certainty. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Päivämäärä: 27. lokakuuta 2025'] | [2. SYNTACTIC ANCHOR: '27. lokakuuta 2025'] | [3. TARGET NODE: 'Päivämäärä'] | [4. LINGUISTIC BRIDGE: 'tabular-copula'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Päivämäärä: 27. lokakuuta 2025'] | [2. SYNTACTIC ANCHOR: '2025'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_5f71c2e291f1ae4e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Syntactic Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a security action is paired with an explicit, documented risk assessment. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023) Supermegatrendit Postnormaalissa Ajassa: Kaupalliset Vaikutukset...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'because of risk X/to prevent Y/therefore blocked'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Eetisesti kyseenalaiset AI-ratkaisut aiheuttavat maineriskin. | Kehitetään ja käytetään teknologiaa eetisesti ja läpinäkyvästi.'] | [2. SYNTACTIC ANCHOR: 'aiheuttavat maineriskin'] | [3. TARGET NODE: 'Kehitetään ja käytetään'] | [4. LINGUISTIC BRIDGE: 'tabular-copula'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_d0ed9f689cfbcc3b
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'truth'. STEP 1 (Syntactic Anchor): Find a causal claim (e.g. 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text DOES NOT provide empirical data (numbers, logs, specific quotes) or a step-by-step mechanism to prove the link. NEGATIVE CONDITION (RETURN NULL IF MET): data/mechanism exists. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus.'] | [2. SYNTACTIC ANCHOR: 'oli'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Pyysin supermegatrendejä – tämä oli iso oivallus. Tekoälyn alkuperäinen vastaus oli liian laaja, joten sitä oli pakko supistaa ja tuottaa ylätason näkemys.'] | [2. SYNTACTIC ANCHOR: 'joten'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_4fa47fd622e62e0d
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find formal citation markers ('according to ARMA principle of', 'ISO standard'). STEP 2 (Bounding Box): Scan the sentence. If a specific external framework is named AND a specific sub-principle or clause is cited to justify a decision. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept generic references to 'standards' without naming them. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Sääntelypaine: CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset tekevät kestävyydestä pakollista'] | [2. SYNTACTIC ANCHOR: 'CSRD-direktiivin'] | [3. TARGET NODE: 'säädökset'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 → 2023) Supermegatrendit Postnormaalissa Ajassa: Kaupalliset Vaikutukset Kohderyhmä: Kaupallinen Johtoryhmä Päivämäärä: 27. lokakuuta 2025 Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_2dabbdba90a549ae
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find formal citations ('according to the methodology of', 'based on the study by'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the logical rule is explicitly backed by a verifiable external methodology or study. NEGATIVE CONDITION (RETURN NULL IF MET): it's a vague reference ('research shows'). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Vague references to 'studies' or 'science'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'Viite:'] | [3. TARGET NODE: 'Sitran Megatrendiraportit'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'Viite:'] | [3. TARGET NODE: 'logical rule'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_32ee0cac79ad098e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate humility. STEP 1 (Syntactic Anchor): Find universal terms ('always', 'in every case'). STEP 2: EXTRACTION CONDITION: a causal claim derived from a specific, limited context is applied to all contexts universally without acknowledging boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Vain kestävät liiketoimintamallit saavat tulevaisuudessa pääomaa.'] | [2. SYNTACTIC ANCHOR: 'Vain'] | [3. TARGET NODE: 'always'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kohderyhmä: Kaupallinen Johtoryhmä...Viite: Sitran Megatrendiraportit 2017, 2020, 2023'] | [2. SYNTACTIC ANCHOR: 'always', 'in every case'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_79f305842b933ea5
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find explicit dialectical reasoning ('we evaluated option A, but chose B because'). STEP 2 (Bounding Box): Scan the paragraph. If the author explicitly documents a rejected compliance alternative and provides data-driven reasoning for the final choice. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept simple lists of options without rejection reasoning. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'nähtävä teknologinen murros (esim. AI) välineenä reilun digimaailman luomiseen, ei vain kustannussäästönä.'] | [2. SYNTACTIC ANCHOR: 'ei vain'] | [3. TARGET NODE: 'reilun digimaailman luomiseen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 → 2023)'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_247927c98b0c46f8
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Luonnon kantokyvyn rajat eivät ole vain rajoite, vaan uuden taloudellisen kasvun perusta.'] | [2. SYNTACTIC ANCHOR: 'eivät ole vain'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta...'] | [2. SYNTACTIC ANCHOR: 'although X is true'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_dfa97bbeeb1dafc5
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find criteria anchoring markers (e.g., 'measured against', 'based on the standard of', 'criteria'). STEP 2: EXTRACTION CONDITION: an evaluation explicitly links its judgment to a stated benchmark or metric. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept floating evaluations with unstated goalposts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset tekevät kestävyydestä pakollista (compliance)'] | [2. SYNTACTIC ANCHOR: 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset'] | [3. TARGET NODE: 'kestävyydestä pakollista'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]. Arvio siitä, että kestävyys on 'pakollista', on ankkuroitu eksplisiittisesti nimettyihin vertailukohtiin (säädöksiin), mikä täyttää säännön ehdon.

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Yrityksemme menestys riippuu kyvystämme integroida nämä kolme supermegatrendiä strategiseen päätöksentekoon ja nähdä kestävyys ja autonomia uusina kilpailutekijöinä.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_82e8242331deddab
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a factual claim. STEP 2: Check for qualifying terms (e.g., 'indicates', 'suggests', 'is correlated'). EXTRACTION CONDITION: present AND absolute markers (e.g., 'proves', 'always') are strictly absent in the same sentence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Sitran megatrendien kehitys vuosien 2017 ja 2023 välillä osoittaa fundamentaalisen siirtymän potentiaaleista ja kehityskuluista (2017) kohti geopoliittisesti latautuneita kriisejä ja systeemisiä murtumia (2023).'] | [2. SYNTACTIC ANCHOR: 'osoittaa'] | [3. TARGET NODE: 'osoittaa'] | [4. LINGUISTIC BRIDGE: syntax] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Supermegatrendit Postnormaalissa Ajassa: Kaupalliset Vaikutukset'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_9f5da09c4b03359d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find reformulation markers (e.g., 'in other words', 'this means', 'essentially'). STEP 2: EXTRACTION CONDITION: found, the author is paraphrasing. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept verbatim copy-pasting of definitions. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Johtoryhmälle tämä tarkoittaa:'] | [2. SYNTACTIC ANCHOR: 'tarkoittaa'] | [3. TARGET NODE: 'tämä'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kriittinen Analyysi Sitran Megatrendien Evoluutiosta (2017 - 2023)'] | [2. SYNTACTIC ANCHOR: 'in other words/this means'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_61c1b43bc6f5406f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. EXTRACTION CONDITION: role prefixes exist, focus on 'ai:' output compared to 'user:' input. BANNED LOGIC: Do not evaluate 'coincidence' abstractly. STEP 1 (Syntactic Anchor): Identify a novel concept, specific methodology, or data point introduced by the AI. STEP 2 (Bounding Box): Scan the preceding 'user:' prompt. NEGATIVE CONDITION (RETURN NULL IF MET): the user prompt did NOT explicitly request this concept or methodology. If the user requested it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Sitra näkee tulevaisuuden "postnormaalina aikana"'] | [2. SYNTACTIC ANCHOR: 'postnormaalina aikana'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Megatrendien Kooste, voiko tässä olevia asioita yhdistellä ja tuottaa supermegatrendejä... ai: Kyllä... Supermegatrendit... 1. Ekologinen Resilienssikriisi'] | [2. SYNTACTIC ANCHOR: 'supermegatrendejä'] | [3. TARGET NODE: 'Ekologinen Resilienssikriisi'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Fail]

---

