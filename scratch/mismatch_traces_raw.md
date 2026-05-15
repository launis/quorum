# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 186
- Total mismatching atoms: 29
- Variance percentage: 15.6 %
- PASSED -> FAILED (Run 1 -> Run 2): 14
- FAILED -> PASSED (Run 1 -> Run 2): 15
- Other state changes: 0

## Atom: tda_e7f3eec588424a86
**Rule:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'triviality'. STEP 1 (Syntactic Anchor): Find a counter-argument transition (e.g., 'Critics might say', 'Some argue'). STEP 2 (Bounding Box): Scan the paragraph. If the presented counter-argument lacks specific citations, named sources, or numerical data, AND is immediately dismissed. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: '“Tekoäly korvaa opettajat kokonaan” ### Miltä tarina kuulostaa: ... ### Todellisuus: 👉 Tekoäly voi jakaa tietoa, mutta ei: ... 👉 Tämä tarina = liioiteltu + yksinkertaistettu'] | [2. SYNTACTIC ANCHOR: 'Miltä tarina kuulostaa:'] | [3. TARGET NODE: 'Todellisuus:'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: '“Opiskelijat eivät enää opi mitään itse” ... Tämä tarina on osittain totta, mutta: ratkaistavissa pedagogiikalla'] | [2. SYNTACTIC ANCHOR: 'osittain totta'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_5b0fbdd9eeacdfeb
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate subjective 'importance'. STEP 1 (Syntactic Anchor): Find a stated decision outcome. STEP 2 (Bounding Box): Scan the explanation. EXTRACTION CONDITION: the text mentions a causal factor but DOES NOT explicitly assign a quantitative weight, rank, or specific value to it (e.g. 'Factor X was considered' vs 'Factor X had a 40% impact'). NEGATIVE CONDITION (RETURN NULL IF MET): weights/ranks exist. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tekoäly vaikuttaa erityisesti kolmeen asiaan: ### 1.1 Tiedon jakaminen ei ole enää opettajan yksinoikeus ### 1.2 Oppiminen muuttuu itseohjautuvammaksi ### 1.3 Tehtävien tekeminen muuttuu'] | [2. SYNTACTIC ANCHOR: 'vaikuttaa'] | [3. TARGET NODE: 'kolmeen asiaan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Tämä on se tärkein osa esihenkilöllesi.'] | [2. SYNTACTIC ANCHOR: 'tärkein'] | [3. TARGET NODE: 'osa'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_6be555cac0b9115b
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find procedural compliance markers (e.g., 'step 1 completed', 'followed the checklist'). STEP 2 (Bounding Box): Scan the paragraph. If a process is executed exactly as listed without additional synthesis. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'strategic thinking'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Koko chat-loki'] | [2. SYNTACTIC ANCHOR: 'step 1 completed', 'followed the checklist'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tässä valmis sisältö kahteen PowerPoint-diaa varten (voit kopioida suoraan): ## **DIA 1**... ## **DIA 2**...'] | [2. SYNTACTIC ANCHOR: 'Tässä valmis sisältö'] | [3. TARGET NODE: 'DIA 1', 'DIA 2'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_247927c98b0c46f8
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'entire AI response'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Suurin osa huolista liittyy siihen, että opetus pysyy ennallaan – vaikka maailma muuttuu.'] | [2. SYNTACTIC ANCHOR: 'vaikka'] | [3. TARGET NODE: 'maailma muuttuu'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_a2d1fa749b77d3de
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find boundary conditions (e.g., 'assuming that', 'only if', 'the exception is'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly forces the AI to acknowledge a specific edge case or foundational premise. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Broad, unconditional statements. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'konkretisoi vielä miten tämä tulee näkymään nimenomaan yrittäjyyden alalla.'] | [2. SYNTACTIC ANCHOR: 'nimenomaan'] | [3. TARGET NODE: 'yrittäjyyden alalla'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail] - Käyttäjä tarkentaa pyynnön soveltamisalaa, mutta ei aseta loogista reunaehtoa tai poikkeusta.

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Voiko opiskelijoiden ikä ja asenteet vaikuttaa tekoälyn käytön "vastaanottamiseen". Miten huomioin nämä?'] | [2. SYNTACTIC ANCHOR: 'Voiko... vaikuttaa'] | [3. TARGET NODE: 'ikä ja asenteet'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_4956abf072945f43
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Syntactic Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context. NEGATIVE CONDITION (RETURN NULL IF MET): the alternative is dismissed without evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: '“Tekoäly korvaa opettajat kokonaan” ... Todellisuus: 👉 Tekoäly voi jakaa tietoa, mutta ei: johtaa oppimista rakentaa motivaatiota ymmärtää ihmistä kokonaisuutena 👉 Tämä tarina = liioiteltu + yksinkertaistettu'] | [2. SYNTACTIC ANCHOR: 'Todellisuus:'] | [3. TARGET NODE: 'Tekoäly korvaa opettajat kokonaan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_063dc7919d7bbb9f
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not look for 'absence' directly. BANNED SOURCES: Ignore system prompts. STEP 1 (Syntactic Anchor): Find an absolute conclusion or decision (e.g. 'Therefore', 'The solution is', 'Must be'). STEP 2 (Bounding Box): Scan the paragraph containing this conclusion. EXTRACTION CONDITION: the paragraph DOES NOT contain a lexical marker of a counterfactual (e.g. 'Alternatively', 'What if', 'Although'). NEGATIVE CONDITION (RETURN NULL IF MET): counterfactuals are present. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'DIA 1 – lisää yksi rivi loppuun: Lisää tämä: Johtopäätös organisaatiolle Tekoäly tekee opetuksen uudistamisesta välttämätöntä lähivuosina.'] | [2. SYNTACTIC ANCHOR: 'Johtopäätös'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Uskon, että minun työtehtäväni kouluttajana tulee muuttumaan tekoälyn myötä. Uskon, että yhä vähemmän toimin tiedon välittäjänä ja kouluttajan työ muuttuu enemmän ohjaavaksi sekä opiskelijoiden oman ajattelun kehittäjäksi.'] | [2. SYNTACTIC ANCHOR: 'Uskon, että'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_f142c3fa1d08cc2d
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find extraction anchors ('poimi suoraan', 'tarkka lainaus', 'älä keksi itse', 'perustuen vain', 'exact quote', 'do not hallucinate'). STEP 2: EXTRACTION CONDITION: the user explicitly restricts the AI to the provided data and demands exact evidence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'etsi minulle tutkimusviitteet aiheeseen liittyen'] | [2. SYNTACTIC ANCHOR: 'poimi suoraan/tarkka lainaus/älä keksi itse/perustuen vain'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'etsi minulle tutkimusviitteet aiheeseen liittyen'] | [2. SYNTACTIC ANCHOR: 'tutkimusviitteet'] | [3. TARGET NODE: 'etsi'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_d0ed9f689cfbcc3b
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'truth'. STEP 1 (Syntactic Anchor): Find a causal claim (e.g. 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text DOES NOT provide empirical data (numbers, logs, specific quotes) or a step-by-step mechanism to prove the link. NEGATIVE CONDITION (RETURN NULL IF MET): data/mechanism exists. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Uskon, että minun työtehtäväni kouluttajana tulee muuttumaan tekoälyn myötä.'] | [2. SYNTACTIC ANCHOR: 'myötä'] | [3. TARGET NODE: 'muuttumaan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Esihenkilöni on huolissaan tekoälyn tuottamista haasteita ja siitä, että tekoäly tulee korvaamaan opettajat tulevaisuudessa.'] | [2. SYNTACTIC ANCHOR: 'siitä, että'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_9a0fa3967ebb2497
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate creativity. STEP 1 (Syntactic Anchor): Find counterfactual markers ('EXTRACTION CONDITION: X had not', 'would have been'). STEP 2: NEGATIVE CONDITION (RETURN NULL IF MET): the text actively simulates an alternate timeline (Pearl's Rung 3) to explicitly prove necessary causation. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Mitä tapahtuu, jos ei tehdä muutosta'] | [2. SYNTACTIC ANCHOR: 'jos'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Mitä tapahtuu, jos ei tehdä muutosta'] | [2. SYNTAKTINEN ANKKURI: 'jos ei'] | [3. KOHDESOLMU: 'Mitä tapahtuu'] | [4. KIELITIETEELLINEN SILTA: 'syntaksi'] | [5. VALIDOINTIPÄÄTÖS: Pass]

---

## Atom: tda_80c038ed35173cb4
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not assume connections. STEP 1 (Syntactic Anchor): Find a multi-step sequence marker (e.g. 'Step 1.. Step 2.. Step 3', 'First.. Then.. Finally'). STEP 2 (Bounding Box): Scan the entire causal chain. EXTRACTION CONDITION: the text explicitly links at least three distinct sequential actions where each depends entirely on the previous one. NEGATIVE CONDITION (RETURN NULL IF MET): the chain is less than three steps or broken. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: '1. Anna perusrunko (mitä ja miksi) 2. Anna opiskelijan tehdä 3. Sparraa ja haastaa 4. Anna konkreettinen palaute'] | [2. SYNTACTIC ANCHOR: '1. ... 2. ... 3. ... 4.'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Hienoa, olet nyt tuonut tärkeitä asioita esille. Minun täytyisi laatia esihenkilölleni nappa yhteenveto... Toteuta sellainen ... user: Tee tekstit kahteen Powerpoint diaan... user: Analysoi vielä diat esihenkilön näkökulmasta...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_d5e6dd27350bcf4d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate effectiveness. STEP 1 (Syntactic Anchor): Find intervention markers ('EXTRACTION CONDITION: we change', 'by increasing', 'implementing'). STEP 2: NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly describes what would happen to the outcome if an active, deliberate intervention is made on the cause (Pearl's Rung 2). Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: '“Meidän ei pitäisi kysyä korvaako tekoäly opettajat, vaan: kuinka koulutamme opettajat käyttämään tekoälyä paremmin kuin opiskelijat.”'] | [2. SYNTACTIC ANCHOR: 'koulutamme'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Ilman ohjausta tekoäly heikentää oppimista. Ohjattuna se parantaa sitä.'] | [2. SYNTACTIC ANCHOR: 'Ilman ohjausta'] | [3. TARGET NODE: 'heikentää oppimista'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_b7712f8a6c4619b4
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept general 'secure' statements. STEP 1 (Syntactic Anchor): Find zero-trust markers (e.g. 'zero implicit trust', 'independent verification', 'cryptographic', 'strict boundary'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the processing demonstrates explicit zero-trust architecture where every input/output is treated as potentially hostile. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan. Ne ovat kokemusperäisiä arvioita (heuristiikka)'] | [2. SYNTACTIC ANCHOR: 'eivät perustu'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan. Ne ovat kokemusperäisiä arvioita (heuristiikka)'] | [2. SYNTACTIC ANCHOR: 'eivät perustu'] | [3. TARGET NODE: 'yksittäiseen tutkimukseen tai tarkkaan dataan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c6f705f7a5f94f53
**Rule:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED LOGIC: Do not evaluate subjective 'agreement'. STEP 1 (Syntactic Anchor): Find an absolute quantifier (e.g., 'always', 'undeniably', '100%', 'proven'). STEP 2 (Bounding Box): Scan the paragraph. If the sentence uses this absolute word to confirm a premise without presenting a numerical measurement or verifiable dataset in the same paragraph. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kaikki opetus siirtyy tekoälylle', 'Tieto on opiskelijoille jatkuvasti saatavilla tekoälyn kautta'] | [2. SYNTACTIC ANCHOR: 'Kaikki/jatkuvasti'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tiedon jakaminen ei ole enää opettajan yksinoikeus'] | [2. SYNTACTIC ANCHOR: 'ei enää'] | [3. TARGET NODE: 'yksinoikeus'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_03419e9a41f304ce
**Rule:** REQUIRED TARGET: Scan the target document. BANNED SOURCES: Reject user inputs. STEP 1 (Syntactic Anchor): Find dismissive markers towards alternatives (e.g., 'obviously false', 'nonsense', 'irrelevant'). STEP 2 (Bounding Box): Scan the paragraph. STEP 3: EXTRACTION CONDITION: the dismissal occurs without citing an external verifiable source or empirical data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tämä tarina = liioiteltu + yksinkertaistettu'] | [2. SYNTACTIC ANCHOR: '='] | [3. TARGET NODE: 'liioiteltu'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Ei pidä paikkaansa osa käyttää hyvin osa käyttää todella pinnallisesti'] | [2. SYNTACTIC ANCHOR: 'Ei pidä paikkaansa'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_55dfd9cb0adec620
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept subjective assessments of risk severity. STEP 1 (Syntactic Anchor): Find risk identification markers (e.g. 'potential risk', 'hazard', 'vulnerability'). STEP 2 (Bounding Box): Scan the paragraph downwards. EXTRACTION CONDITION: the risk is identified but no physical action verb (e.g. 'encrypted', 'blocked', 'sanitized') follows to mitigate it. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Riski: ajattelun heikkeneminen ja riippuvuus ... riski syntyy ilman ohjausta'] | [2. SYNTACTIC ANCHOR: 'Riski'] | [3. TARGET NODE: 'ohjausta'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Nostaa esiin riskit: kriittisen ajattelun heikkeneminen liiallinen riippuvuus ongelmanratkaisun heikkeneminen'] | [2. SYNTACTIC ANCHOR: 'riskit'] | [3. TARGET NODE: 'kriittisen ajattelun heikkeneminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_7cdd3652e248e6a9
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find tension markers between metrics and goals (e.g., 'this metric is flawed because', 'we need to ensure this actually works'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly questions the reliability of a proxy metric in relation to the ultimate qualitative goal. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept simple metric tracking. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACTIC ANCHOR: 'Mihin'] | [3. TARGET NODE: 'prosenttiluvut'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail] - Käyttäjä kyseenalaistaa tietyn datan, ei välillisen mittarin luotettavuutta suhteessa laadulliseen päämäärään.

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACHTIC ANCHOR: 'Mihin tietoon perustuvat'] | [3. TARGET NODE: 'prosenttiluvut'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_567ee46c35852f54
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find synthesis verbs (e.g., 'design', 'formulate', 'invent', 'combining X and Y creates'). STEP 2: EXTRACTION CONDITION: the text explicitly merges at least two disparate elements into a completely new, named framework or solution. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept mere combinations of existing ideas without a novel theoretical leap. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'VANHA TEHTÄVÄ: “Suunnittele markkinointikampanja” ### **UUSI TEHTÄVÄ:** “Suunnittele kampanja + perustele:'] | [2. SYNTACTIC ANCHOR: 'UUSI TEHTÄVÄ'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'UUSI TEHTÄVÄ: “Suunnittele markkinointikampanja + perustele: miksi tämä toimii mikä tässä on huonoa miten erotut kilpailijoista mitä testaisit oikeasti”'] | [2. SYNTACTIC ANCHOR: 'UUSI TEHTÄVÄ'] | [3. TARGET NODE: 'Suunnittele kampanja + perustele...'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_0871942d6add46f1
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find contrast markers ('however, data shows that', 'despite X, metric Y'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a specific counter-argument is addressed using empirical counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): it's dismissed rhetorically. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rhetorical dismissals without data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Mutta tärkeä lisätutkimus: GenAI-tutkimus (2025) 👉 Löydös: parempi oppiminen, kun AI:ta käytetään ymmärtämiseen heikompi oppiminen, kun sitä käytetään “suorittamiseen”'] | [2. SYNTACTIC ANCHOR: 'Mutta'] | [3. TARGET NODE: 'GenAI-tutkimus (2025)'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Tekoäly ei korvaa opettajia – mutta se muuttaa opettajan roolia merkittävästi.'] | [2. SYNTACTIC ANCHOR: 'mutta'] | [3. TARGET NODE: 'se muuttaa opettajan roolia merkittävästi'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_22859da57aad9c65
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept implicit alternatives. STEP 1 (Syntactic Anchor): Find a comparative marker (e.g. 'Option A vs Option B', 'Instead of', 'Compared to'). STEP 2 (Bounding Box): Scan the surrounding sentences. EXTRACTION CONDITION: the text explicitly names at least two distinct approaches before selecting one. NEGATIVE CONDITION (RETURN NULL IF MET): only one approach is discussed. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Vaihda viimeinen osio: Nykyinen: Opettajan rooli ei katoa, vaan vahvistuu eri tavalla 👉 Muuta muotoon: Johtopäätös Opettajan rooli säilyy, mutta työn sisältö muuttuu merkittävästi'] | [2. SYNTACTIC ANCHOR: 'Nykyinen: ... Muuta muotoon:'] | [3. TARGET NODE: 'Opettajan rooli ei katoa, vaan vahvistuu eri tavalla'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Hyvä kiitos. Sitten seuraavaan aiheeseen. Uskon, että minun työtehtäväni kouluttajana tulee muuttumaan tekoälyn myötä. Uskon, että yhä vähemmän toimin tiedon välittäjänä ja kouluttajan työ muuttuu enemmän ohjaavaksi sekä opiskelijoiden oman ajattelun kehittäjäksi. Miten sinä näet tämän muutoksen tulevaisuudessa?'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_4fb15d2eff06dbb4
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not judge 'vagueness' subjectively. STEP 1 (Syntactic Anchor): Find a justification sentence (e.g. 'This is because', 'Due to'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the justification DOES NOT contain any specific domain variables, numbers, or exact verbatim quotes from the input data (relying only on generic templates). NEGATIVE CONDITION (RETURN NULL IF MET): specific variables are present. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Todella hyvä jatkokysymys – koska usein huoli ei synny faktoista, vaan tarinoista ja tulkinnoista.'] | [2. SYNTACTIC ANCHOR: 'koska'] | [3. TARGET NODE: 'usein huoli ei synny faktoista, vaan tarinoista ja tulkinnoista'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Miksi tämä leviää: Teknologiayritysten hype median kärjistykset pelko työn katoamisesta'] | [2. SYNTACTIC ANCHOR: 'Miksi'] | [3. TARGET NODE: 'Teknologiayritysten hype'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_2aec15ab07984f4d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs or system prompts. STEP 1 (Syntactic Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence makes a future prediction or subjective assessment using these markers. NEGATIVE CONDITION (RETURN NULL IF MET): it states a mathematical/historical fact. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Mathematical facts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'entire AI response'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'ja tässä kohtaa sinä olet oikeasti etulyöntiasemassa.'] | [2. SYNTACTIC ANCHOR: 'oikeasti'] | [3. TARGET NODE: 'olet... etulyöntiasemassa'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_cee9db6717cdafb7
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. EXTRACTION CONDITION: both the risk and the empirical counter-data are found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: '### **Tutkimus / analyysi** Tecnológico de Monterrey Observatory 👉 Nostaa esiin riskit: kriittisen ajattelun heikkeneminen liiallinen riippuvuus ongelmanratkaisun heikkeneminen ## 🔍 Mitä tämä tarkoittaa [observatory.tec.…](https://observatory.tec.mx/edu-bits-2/ai-in-higher-education-a-revolution-or-a-risk/?utm_source=chatgpt.com) 👉 Esihenkilön huoli ei ole tuulesta temmattu 👉 Mutta: riski syntyy ilman ohjausta ei tekoälystä itsestään'] | [2. SYNTACTIC ANCHOR: 'riskit'] | [3. TARGET NODE: 'kriittisen ajattelun heikkeneminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tecnológico de Monterrey Observatory 👉 Nostaa esiin riskit: kriittisen ajattelun heikkeneminen liiallinen riippuvuus ongelmanratkaisun heikkeneminen ## 🔍 Mitä tämä tarkoittaa [observatory.tec.…](https://observatory.tec.mx/edu-bits-2/ai-in-higher-education-a-revolution-or-a-risk/?utm_source=chatgpt.com) 👉 Esihenkilön huoli ei ole tuulesta temmattu 👉 Mutta: riski syntyy ilman ohjausta ei tekoälystä itsestään'] | [2. SYNTACTIC ANCHOR: 'riskit'] | [3. TARGET NODE: 'kriittisen ajattelun heikkeneminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_8b1717b2ca9f25e2
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Syntactic Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: EXTRACTION CONDITION: the command lacks any specific constraints and allows the AI to freely decide what is important. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'laatia esihenkilölleni nappa yhteenveto siitä miten työtehtävät ja opetusala muuttuu tulevaisuudessa tekoälyn avulla. Toteuta sellainen'] | [2. SYNTACTIC ANCHOR: 'yhteenveto'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Minun täytyisi laatia esihenkilölleni nappa yhteenveto siitä miten työtehtävät ja opetusala muuttuu tulevaisuudessa tekoälyn avulla. Toteuta sellainen'] | [2. SYNTACTIC ANCHOR: 'yhteenveto'] | [3. TARGET NODE: 'laatia'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_e43160bbd694dc73
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. STEP 1 (Syntactic Anchor): Find reactive anchors ('unohdit', 'lisää vielä', 'korjaa tuo', 'entä', 'forgot', 'add'). STEP 2 (Bounding Box): Scan the sequence. EXTRACTION CONDITION: the user adds a new critical constraint that they forgot to specify in the previous prompt. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Kiitos, konkretisoi vielä miten tämä tulee näkymään nimenomaan yrittäjyyden alalla.'] | [2. SYNTACTIC ANCHOR: 'vielä'] | [3. TARGET NODE: 'konkretisoi'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Kiitos, konkretisoi vielä miten tämä tulee näkymään nimenomaan yrittäjyyden alalla.'] | [2. SYNTACTIC ANCHOR: 'vielä'] | [3. TARGET NODE: 'konkretisoi'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c1a05b0ce5f88033
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. EXTRACTION CONDITION: the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'depth', simply count the data points. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### **Diffusion of Innovations (Everett Rogers)** Innovators ~2,5 % Early adopters ~13,5 % Early majority ~34 % Late majority ~34 % Laggards ~16 % 👉 Kun tätä sovelletaan opetukseen ja tekoälyyn: osa opiskelijoista on edellä suurin osa keskellä osa vastustaa 👉 Minun käyttämä jako (10–30 %, 50–70 %, 10–20 %) on: **yksinkertaistettu pedagoginen versio tästä mallista**'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations (Everett Rogers)'] | [3. TARGET NODE: 'Diffusion of Innovations (Everett Rogers)'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### **Diffusion of Innovations (Everett Rogers)** Innovators ~2,5 % Early adopters ~13,5 % Early majority ~34 % Late majority ~34 % Laggards ~16 % 👉 Kun tätä sovelletaan opetukseen ja tekoälyyn: osa opiskelijoista on edellä suurin osa keskellä osa vastustaa 👉 Minun käyttämä jako (10–30 %, 50–70 %, 10–20 %) on: **yksinkertaistettu pedagoginen versio tästä mallista**'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations (Everett Rogers)'] | [3. TARGET NODE: 'malli'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_47219840710895f0
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Syntactic Anchor): Find explicit reasoning markers by the user (e.g., 'I am challenging this because', 'the reason this is wrong is'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly documents the 'why' behind their challenge to the AI. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept unreasoned rejections ('this is bad'). TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACTIC ANCHOR: 'Mihin'] | [3. TARGET NODE: 'prosenttiluvut'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail] - Käyttäjä esittää haastavan kysymyksen, mutta ei eksplisiittisesti dokumentoi syytä haasteen takana säännön vaatimalla tavalla (esim. 'Tämä on väärin, koska...').

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACTIC ANCHOR: 'Mihin tietoon perustuvat'] | [3. TARGET NODE: 'prosenttiluvut'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_2d670bf31419dd73
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept qualitative confidence (e.g. 'very sure'). STEP 1 (Syntactic Anchor): Find a quantitative confidence metric or strict certainty boundary (e.g. 'Confidence level', 'Margin of error', 'p-value', '95%'). STEP 2 (Bounding Box): Scan the logic block. EXTRACTION CONDITION: the text rigorously defines the EXACT quantitative or structural boundary of its own certainty. NEGATIVE CONDITION (RETURN NULL IF MET): missing quantitative boundaries. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: '88 % opiskelijoista käyttää tekoälyä arviointitehtävissä'] | [2. SYNTACTIC ANCHOR: '88 %'] | [3. TARGET NODE: '88 %'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_823c84f71d94ce84
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept post-generation complaints. STEP 1 (Syntactic Anchor): Find a friction marker prior to an action (e.g. 'This is difficult because', 'The risk here is', 'We must balance'). STEP 2 (Bounding Box): Scan the chronological flow. EXTRACTION CONDITION: the conflict or trade-off is articulated BEFORE the final output is generated. NEGATIVE CONDITION (RETURN NULL IF MET): the friction is only discussed afterwards. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'user: Analysoi vielä diat esihenkilön näkökulmasta, vakuuttuuko hän näistä? ai: ... Mutta esihenkilön näkökulmasta niistä puuttuu vielä yksi asia: 👉 “Mitä tämä tarkoittaa meille käytännössä?”'] | [2. SYNTACTIC ANCHOR: 'puuttuu'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'user: Analysoi vielä diat esihenkilön näkökulmasta, vakuuttuuko hän näistä?'] | [2. SYNTACTIC ANCHOR: 'Analysoi'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

