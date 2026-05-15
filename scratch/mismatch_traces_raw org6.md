# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 186
- Total mismatching atoms: 29
- Variance percentage: 15.6 %
- PASSED -> FAILED (Run 1 -> Run 2): 11
- FAILED -> PASSED (Run 1 -> Run 2): 18
- Other state changes: 0

## Atom: tda_dd0dc97fcaee4d7c
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept theoretical resilience. STEP 1 (Syntactic Anchor): Find error handling markers (e.g. 'rejected', 'fallback', 'graceful degradation', 'safely ignored'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: it describes physically rejecting invalid input or defaulting to a safe state without crashing. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Parempi tapa sanoa: “Tutkimuksiin perustuvien omaksumismallien mukaan opiskelijat jakautuvat tyypillisesti kolmeen ryhmään: edelläkävijät, enemmistö ja varovaiset.'] | [2. SYNTACTIC ANCHOR: 'Parempi tapa sanoa'] | [3. TARGET NODE: 'Parempi tapa sanoa'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Tässä sinulle napakka, esihenkilölle sopiva yhteenveto, jonka voit käyttää sellaisenaan'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUistic BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_7b644daf603c4f00
**Rule:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not flag open-ended questions explicitly left for future research. STEP 1 (Syntactic Anchor): Find a question mark '?' used by the author to question their own premise. STEP 2 (Bounding Box): Scan the following 2 sentences. If the author answers their own question confirming the premise without citing new data. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Hän miettii: Pitäisikö olla huolissaan? Muuttuuko resurssitarve? Pitääkö tehdä muutoksia nyt? Onko tämä riski vai mahdollisuus organisaatiolle?'] | [2. SYNTACTIC ANCHOR: '?'] | [3. TARGET NODE: 'Pitäisikö olla huolissaan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko teksti skannattu'] | [2. SYNTACTIC ANCHOR: '?'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_03419e9a41f304ce
**Rule:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'No dismissive markers towards alternatives found without external verifiable source or empirical data.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tämä tarina = liioiteltu + yksinkertaistettu'] | [2. SYNTACTIC ANCHOR: '='] | [3. TARGET NODE: 'liioiteltu'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_e43160bbd694dc73
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find reactive anchors ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä', 'forgot', 'add'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user adds a new critical constraint that they forgot to specify in the previous prompt. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Analysoi vielä diat esihenkilön näkökulmasta, vakuuttuuko hän näistä?'] | [2. SYNTACTIC ANCHOR: 'vielä'] | [3. TARGET NODE: 'Analysoi'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kiitokset tästä... konkretisoi vielä... Hienoa, olet nyt tuonut... Tee tekstit... Analysoi vielä...'] | [2. SYNTACTIC ANCHOR: 'unohdit'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_22859da57aad9c65
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept implicit alternatives. STEP 1 (Syntactic Anchor): Find a comparative marker (e.g. 'Option A vs Option B', 'Instead of', 'Compared to'). STEP 2 (Bounding Box): Scan the surrounding sentences. EXTRACTION CONDITION: the text explicitly names at least two distinct approaches before selecting one. NEGATIVE CONDITION (RETURN NULL IF MET): only one approach is discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Voiko opiskelijoiden ikä ja asenteet vaikuttaa tekoälyn käytön "vastaanottamiseen". Miten huomioin nämä?'] | [2. SYNTACTIC ANCHOR: 'Voiko'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: '“Fake yrittäjyys” vs. oikea yrittäjyys'] | [2. SYNTACTIC ANCHOR: 'vs.'] | [3. TARGET NODE: 'oikea yrittäjyys'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_6758e0a8f1b3aaf8
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find conflict resolution markers (e.g., 'while X requires Y, we must also ensure Z by'). STEP 2 (Bounding Box): Scan the paragraph. If two conflicting operational constraints (e.g., Retention vs Disposition) are mentioned and a specific action is taken to resolve the tension. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept rhetorical mentions of conflict without a resolution action. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Ongelma ei ole uusi: ennen kopioitiin Googlesta nyt käytetään tekoälyä 👉 Ero: nyt pitää muuttaa tehtävät, ei kieltää työkalua'] | [2. SYNTACTIC ANCHOR: 'Ero:'] | [3. TARGET NODE: 'muuttaa tehtävät, ei kieltää työkalua'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Tekoäly tuo: nopeutta tehokkuutta Mutta vie helposti: syvyyttä ymmärrystä... UUSI TEHTÄVÄ: “Suunnittele kampanja + perustele...'] | [2. SYNTACTIC ANCHOR: 'Mutta'] | [3. TARGET NODE: 'UUSI TEHTÄVÄ'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_2d670bf31419dd73
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept qualitative confidence (e.g. 'very sure'). STEP 1 (Syntactic Anchor): Find a quantitative confidence metric or strict certainty boundary (e.g. 'Confidence level', 'Margin of error', 'p-value', '95%'). STEP 2 (Bounding Box): Scan the logic block. EXTRACTION CONDITION: the text rigorously defines the EXACT quantitative or structural boundary of its own certainty. NEGATIVE CONDITION (RETURN NULL IF MET): missing quantitative boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan. Ne ovat kokemusperäisiä arvioita (heuristiikka)'] | [2. SYNTACTIC ANCHOR: 'eivät perustu'] | [3. TARGET NODE: 'tarkkaan dataan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan. Ne ovat kokemusperäisiä arvioita (heuristiikka)'] | [2. SYNTACTIC ANCHOR: 'eivät perustu'] | [3. TARGET NODE: 'yksittäiseen tutkimukseen tai tarkkaan dataan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_733767a200047a89
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find integration markers (e.g., 'simultaneously achieving', 'balances X and Y through'). STEP 2 (Bounding Box): Scan the paragraph. If a specific mechanism is described that actively satisfies two typically opposing ARMA principles (e.g., Protection vs Availability). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept claims of balance without describing the physical mechanism. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Paras yhdistelmä (ei ääripäitä) Ei: ❌ pelkkä luennointi ❌ pelkkä “sparraus ilman suuntaa” 👉 Vaan: 1. Anna perusrunko (mitä ja miksi) 2. Anna opiskelijan tehdä 3. Sparraa ja haastaa 4. Anna konkreettinen palaute'] | [2. SYNTACTIC ANCHOR: 'yhdistelmä'] | [3. TARGET NODE: '1. Anna perusrunko...4. Anna konkreettinen palaute'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Anna kaksi tasoa tehtäviin Esim: perus: tee ilman tekoälyä edistynyt: hyödynnä tekoälyä + analysoi'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_653b3f5497b9147e
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find explicit external anchoring for uncertainty (e.g., 'due to X, as noted by [Source]'). STEP 2: Map the cognitive friction. EXTRACTION CONDITION: an external citation is used specifically to justify why a variable remains unknown. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### Diffusion of Innovations (Everett Rogers)'] | [2. SYNTACTIC ANCHOR: 'tunnettu malli'] | [3. TARGET NODE: 'Diffusion of Innovations (Everett Rogers)'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: ''] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_513d51a119ef4fd6
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from 'user:' prefixed blocks. STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan.'] | [2. SYNTACTIC ANCHOR: 'eivät perustu'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Näet yleensä kolme ryhmää: ### 1. Edelläkävijät (10–30 %) ... ### 2. Keskiryhmä (50–70 %) ... ### 3. Vastustajat / epäilevät (10–20 %)'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_cee9db6717cdafb7
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. EXTRACTION CONDITION: both the risk and the empirical counter-data are found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: '3. Riski: ajattelun heikkeneminen ja riippuvuus ### Tutkimus / analyysi Tecnológico de Monterrey Observatory 👉 Nostaa esiin riskit: kriittisen ajattelun heikkeneminen liiallinen riippuvuus ongelmanratkaisun heikkeneminen ## 🔍 Mitä tämä tarkoittaa [observatory.tec.…](https://observatory.tec.mx/edu-bits-2/ai-in-higher-education-a-revolution-or-a-risk/?utm_source=chatgpt.com) 👉 Esihenkilön huoli ei ole tuulesta temmattu 👉 Mutta: riski syntyy ilman ohjausta ei tekoälystä itsestään'] | [2. SYNTACTIC ANCHOR: 'Riski: ajattelun heikkeneminen ja riippuvuus'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'parempi oppiminen, kun AI:ta käytetään ymmärtämiseen heikompi oppiminen, kun sitä käytetään “suorittamiseen” [Taylor & Franci…](https://www.tandfonline.com/doi/full/10.1080/03075079.2025.2487570?utm_source=chatgpt.com)'] | [2. SYNTACTIC ANCHOR: 'heikompi oppiminen'] | [3. TARGET NODE: 'oppiminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_063dc7919d7bbb9f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not look for 'absence' directly. BANNED SOURCES: Ignore system prompts. STEP 1 (Syntactic Anchor): Find an absolute conclusion or decision (e.g. 'Therefore', 'The solution is', 'Must be'). STEP 2 (Bounding Box): Scan the paragraph containing this conclusion. EXTRACTION CONDITION: the paragraph DOES NOT contain a lexical marker of a counterfactual (e.g. 'Alternatively', 'What if', 'Although'). NEGATIVE CONDITION (RETURN NULL IF MET): counterfactuals are present. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Uskon, että minun työtehtäväni kouluttajana tulee muuttumaan tekoälyn myötä. Uskon, että yhä vähemmän toimin tiedon välittäjänä ja kouluttajan työ muuttuu enemmän ohjaavaksi sekä opiskelijoiden oman ajattelun kehittäjäksi.'] | [2. SYNTACTIC ANCHOR: 'Uskon, että'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Uskon, että minun työtehtäväni kouluttajana tulee muuttumaan tekoälyn myötä. Uskon, että yhä vähemmän toimin tiedon välittäjänä ja kouluttajan työ muuttuu enemmän ohjaavaksi sekä opiskelijoiden oman ajattelun kehittäjäksi.'] | [2. SYNTACTIC ANCHOR: 'Uskon, että'] | [3. TARGET NODE: 'työ muuttuu'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_d5e6dd27350bcf4d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate effectiveness. STEP 1 (Syntactic Anchor): Find intervention markers ('EXTRACTION CONDITION: we change', 'by increasing', 'implementing'). STEP 2: NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly describes what would happen to the outcome if an active, deliberate intervention is made on the cause (Pearl's Rung 2). Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Jos opetus ei muutu, opiskelijat ohittavat opettajan.'] | [2. SYNTACTIC ANCHOR: 'Jos'] | [3. TARGET NODE: 'ohittavat'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'UUSI TEHTÄVÄ: “Suunnittele markkinointikampanja” 👉 opiskelija tekee (tai nyt: AI tekee) ### UUSI TEHTÄVÄ: “Suunnittele kampanja + perustele: miksi tämä toimii mikä tässä on huonoa miten erotut kilpailijoista mitä testaisit oikeasti”'] | [2. SYNTACTIC ANCHOR: 'UUSI TEHTÄVÄ'] | [3. TARGET NODE: 'Suunnittele kampanja + perustele'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_d0ed9f689cfbcc3b
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'truth'. STEP 1 (Syntactic Anchor): Find a causal claim (e.g. 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text DOES NOT provide empirical data (numbers, logs, specific quotes) or a step-by-step mechanism to prove the link. NEGATIVE CONDITION (RETURN NULL IF MET): data/mechanism exists. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACTIC ANCHOR: 'perustuvat'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Uskon, että minun työtehtäväni kouluttajana tulee muuttumaan tekoälyn myötä.'] | [2. SYNTACTIC ANCHOR: 'myötä'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_2ca8b77ba2dd43ad
**Rule:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept explicit hypothesis testing. STEP 1 (Syntactic Anchor): Find descriptive reporting verbs (e.g., 'the data shows', 'we observed', 'indicates'). STEP 2 (Bounding Box): Scan the paragraph. If the observation lacks a formulated hypothesis that could be tested or disproven (e.g. no 'if X then Y' structure). Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Tekoäly ei korvaa opettajia – mutta se muuttaa opettajan roolia merkittävästi.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'Tekoäly ei korvaa opettajia – mutta se muuttaa opettajan roolia merkittävästi.'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Keskeinen löydös: 88 % opiskelijoista käyttää tekoälyä arviointitehtävissä'] | [2. SYNTACTIC ANCHOR: 'löydös'] | [3. TARGET NODE: '88 % opiskelijoista käyttää tekoälyä arviointitehtävissä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_fe4c8f1574634233
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read from user input fields. STEP 1 (Syntactic Anchor): Find abrupt transition markers ('therefore', 'thus', 'so'). STEP 2 (Bounding Box): Scan the sentence containing the transition. EXTRACTION CONDITION: it connects two facts but lacks any explanatory mechanism ('because mechanism X'). NEGATIVE CONDITION (RETURN NULL IF MET): a mechanism is described. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept explicit causal mechanisms. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'joten: arvo siirtyy tekemiseen ja testaamiseen'] | [2. SYNTACTIC ANCHOR: 'joten'] | [3. TARGET NODE: 'arvo siirtyy'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'opiskelija voi generoida suunnitelman 👉 joten: arvo siirtyy tekemiseen ja testaamiseen'] | [2. SYNTACTIC ANCHOR: 'joten'] | [3. TARGET NODE: 'arvo siirtyy'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_55dfd9cb0adec620
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Riski on olemassa, mutta: koskee eniten: massaluentoja teoriapainotteista opetusta'] | [2. SYNTACTIC ANCHOR: 'Riski'] | [3. TARGET NODE: 'olemassa'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko ai-generoitu teksti käytiin läpi.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_3da456b757644c46
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept vague assertions like 'it is secure'. STEP 1 (Syntactic Anchor): Find explicit physical validation actions (e.g. 'validated', 'filtered', 'sanitized', 'checked against'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it describes a concrete data validation rule being applied to input or output. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Analysoin suoraan ja rehellisesti:'] | [2. SYNTACTIC ANCHOR: 'Analysoin'] | [3. TARGET NODE: 'diat'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko ai-generoitu teksti käytiin läpi.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c59639ea92894862
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find anecdotal markers ('I once saw', 'in my experience', 'some people say'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: an anecdote is used to justify a systemic rule or broad policy. NEGATIVE CONDITION (RETURN NULL IF MET): it's just a personal story without broad policy claims. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not flag rigorous case studies. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan. Ne ovat kokemusperäisiä arvioita (heuristiikka)...'] | [2. SYNTACTIC ANCHOR: 'kokemusperäisiä'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Omassa opetuksessa tämä näkyy usein niin, että suurin osa tarvitsee ohjausta, pieni osa on jo pitkällä ja osa suhtautuu varauksella.'] | [2. SYNTACTIC ANCHOR: 'Omassa opetuksessa'] | [3. TARGET NODE: 'näkyy usein niin, että'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_fea09fcabdf767c1
**Rule:** CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find absolute words (e.g., 'always', 'never', 'everyone knows', 'fact'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the absolute claim is presented without any citations or stated limitations. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept absolute statements that are mathematically proven or properly cited. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Opiskelija voi kysyä tekoälyltä mitä tahansa, milloin tahansa'] | [2. SYNTACTIC ANCHOR: 'mitä tahansa, milloin tahansa'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Tieto on opiskelijoille jatkuvasti saatavilla tekoälyn kautta'] | [2. SYNTACTIC ANCHOR: 'jatkuvasti'] | [3. TARGET NODE: 'saatavilla'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_073aecbc29db5fc9
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. Focus on 'user:' blocks. BANNED LOGIC: Do not accept vague visions. STEP 1 (Syntactic Anchor): Find a structural blueprint or architectural prediction (e.g. 'The architecture must contain X, Y, and Z'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user documents a complex, multi-variable constraint AND explicitly discusses the cognitive friction of solving it BEFORE the AI generates the solution. NEGATIVE CONDITION (RETURN NULL IF MET): the blueprint is missing or friction is omitted. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Tee strategisempi, vältä geneerisyyttä ja lisää konkretiaa'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Onko opiskelijat jo nyt valmiita muutoksiin? Voiko opiskelijoiden ikä ja asenteet vaikuttaa tekoälyn käytön "vastaanottamiseen". Miten huomioin nämä?'] | [2. SYNTACTIC ANCHOR: 'Miten huomioin nämä?'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_9650d4189cfcb832
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. Focus on 'user:' to 'ai:' interaction. BANNED LOGIC: Do not accept vague requests. STEP 1 (Syntactic Anchor): Find an explicit user instruction containing at least two specific constraints (e.g. format, tone, length). STEP 2 (Bounding Box): Scan the subsequent user response. EXTRACTION CONDITION: the user explicitly verifies those exact constraints (e.g. 'Constraint A met, Constraint B failed'). NEGATIVE CONDITION (RETURN NULL IF MET): verification is absent or generic. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tee tekstit kahteen Powerpoint diaan. Älä käytä hymiöitä.'] | [2. SYNTACTIC ANCHOR: 'kahteen... diaan... Älä käytä hymiöitä'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Tee tekstit kahteen Powerpoint diaan. Älä käytä hymiöitä. ai: ... user: Analysoi vielä diat esihenkilön näkökulmasta, vakuuttuuko hän näistä?'] | [2. SYNTACTIC ANCHOR: 'kahteen Powerpoint diaan. Älä käytä hymiöitä.'] | [3. TARGET NODE: 'Analysoi vielä diat'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_b630abc4de19948b
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a counter-hypothesis (e.g., 'an alternative explanation', 'critics might argue'). STEP 2 (Bounding Box): Scan the same paragraph for external data or citations used to address this counter-hypothesis. EXTRACTION CONDITION: found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: '1. “Tekoäly korvaa opettajat kokonaan” ### Miltä tarina kuulostaa: “Kohta ei tarvita opettajia enää ollenkaan” “Kaikki opetus siirtyy tekoälylle” “Yksi tekoäly voi opettaa tuhansia opiskelijoita” ### Miksi tämä leviää: Teknologiayritysten hype median kärjistykset pelko työn katoamisesta ### Todellisuus: 👉 Tekoäly voi jakaa tietoa, mutta ei: johtaa oppimista rakentaa motivaatiota ymmärtää ihmistä kokonaisuutena 👉 Tämä tarina = liioiteltu + yksinkertaistettu'] | [2. SYNTACTIC ANCHOR: '1. “Tekoäly korvaa opettajat kokonaan”'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Mutta tärkeä lisätutkimus: GenAI-tutkimus (2025) 👉 Löydös: parempi oppiminen, kun AI:ta käytetään ymmärtämiseen heikompi oppiminen, kun sitä käytetään “suorittamiseen” [Taylor & Franci…](https://www.tandfonline.com/doi/full/10.1080/03075079.2025.2487570?utm_source=chatgpt.com)'] | [2. SYNTACTIC ANCHOR: 'Mutta tärkeä lisätutkimus'] | [3. TARGET NODE: 'GenAI-tutkimus (2025)'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_6be555cac0b9115b
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find procedural compliance markers (e.g., 'step 1 completed', 'followed the checklist'). STEP 2 (Bounding Box): Scan the paragraph. If a process is executed exactly as listed without additional synthesis. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'strategic thinking'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'entire ai: blocks'] | [2. SYNTACTIC ANCHOR: 'step 1/followed checklist'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tässä valmis sisältö kahteen PowerPoint-diaa varten (voit kopioida suoraan): ## **DIA 1**... ## **DIA 2**...'] | [2. SYNTACTIC ANCHOR: 'Tässä valmis sisältö'] | [3. TARGET NODE: 'DIA 1... DIA 2'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c1a05b0ce5f88033
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. EXTRACTION CONDITION: the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'depth', simply count the data points. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### Diffusion of Innovations (Everett Rogers) Innovators ~2,5 % Early adopters ~13,5 % Early majority ~34 % Late majority ~34 % Laggards ~16 % 👉 Kun tätä sovelletaan opetukseen ja tekoälyyn: osa opiskelijoista on edellä suurin osa keskellä osa vastustaa 👉 Minun käyttämä jako (10–30 %, 50–70 %, 10–20 %) on: yksinkertaistettu pedagoginen versio tästä mallista'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations (Everett Rogers)'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'opiskelijat käyttävät AI:ta enemmän, kun: kokevat sen hyödylliseksi se on helppoa käyttää [academic-publis…](https://academic-publishing.org/index.php/ejel/article/view/3599?utm_source=chatgpt.com)'] | [2. SYNTACTIC ANCHOR: 'UTAUT-mallit'] | [3. TARGET NODE: 'opiskelijat'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_2aec15ab07984f4d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs or system prompts. STEP 1 (Syntactic Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence makes a future prediction or subjective assessment using these markers. NEGATIVE CONDITION (RETURN NULL IF MET): it states a mathematical/historical fact. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Mathematical facts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tekoäly ei korvaa opettajia – mutta se muuttaa opettajan roolia merkittävästi.'] | [2. SYNTACTIC ANCHOR: 'ei korvaa'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: ''] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c45a513f2e724e06
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Ja tämä on täysin normaalia.'] | [2. SYNTACTIC ANCHOR: 'täysin'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: '“Tekoäly ei korvaa opettajaa – mutta opettaja, joka ei käytä tekoälyä, voidaan korvata.”'] | [2. SYNTACTIC ANCHOR: 'voidaan korvata'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_a66f2e5d339ffd4a
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not accept appeals to authority. STEP 1 (Syntactic Anchor): Find heuristic or dismissive phrases (e.g. 'typically', 'usually', 'it is known', 'obviously'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the phrase is used to justify a decision WITHOUT citing a specific dataset, numerical weight, or verifiable rule. NEGATIVE CONDITION (RETURN NULL IF MET): a specific source is cited. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: '...opiskelijat jakautuvat tyypillisesti kolmeen ryhmään: edelläkävijät, enemmistö ja varovaiset.'] | [2. SYNTACTIC ANCHOR: 'tyypillisesti'] | [3. TARGET NODE: 'verifiable rule'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Näet yleensä kolme ryhmää: ### 1. Edelläkävijät (10–30 %)'] | [2. SYNTACTIC ANCHOR: 'yleensä'] | [3. TARGET NODE: '10–30 %'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_4956abf072945f43
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Syntactic Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context. NEGATIVE CONDITION (RETURN NULL IF MET): the alternative is dismissed without evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'etsi minulle tutkimusviitteet aiheeseen liittyen'] | [2. SYNTACTIC ANCHOR: 'etsi'] | [3. TARGET NODE: 'tutkimusviitteet'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Aiempi riski (jonka nyt ymmärrän vahvemmin) Ajattelin: opiskelija käyttää tekoälyä → ok opettaja sparraa → hyvä 👉 Nyt: tämä ei riitä'] | [2. SYNTACTIC ANCHOR: 'tämä ei riitä'] | [3. TARGET NODE: 'Aiempi riski'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

---

