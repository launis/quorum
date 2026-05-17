# Raw Mismatch Traces (2-way Execution)

## Summary
- Total common atoms evaluated: 147
- Total mismatching atoms: 23
- Variance percentage: 15.6 %
- PASSED -> FAILED (Run 1 -> Run 2): 13
- FAILED -> PASSED (Run 1 -> Run 2): 10
- Other state changes: 0

## Atom: tda_d46093a71bbbcd79
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from 'ai:' output blocks. STEP 1 (Syntactic Anchor): Find affirmative acceptance phrases by the user (e.g., 'looks good', 'thanks', 'perfect'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user accepts an AI output without requesting a single structural or logical change. NEGATIVE CONDITION (RETURN NULL IF MET): the user requests a modification. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate if the response was actually 'good'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Hyvä kiitos. Sitten seuraavaan aiheeseen.'] | [2. SYNTACTIC ANCHOR: 'Hyvä kiitos'] | [3. TARGET NODE: 'Sitten seuraavaan aiheeseen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Kiitokset tästä. Esihenkilöni on kuullut huolestuttavia tarinoita siitä miten tekoäly tulee vaikuttamaan. Mitä tarinoita nämä voivat olla?'] | [2. SYNTACTIC ANCHOR: 'Kiitokset tästä'] | [3. TARGET NODE: 'Mitä tarinoita nämä voivat olla?'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_0871942d6add46f1
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find contrast markers ('however, data shows that', 'despite X, metric Y'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a specific counter-argument is addressed using empirical counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): it's dismissed rhetorically. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rhetorical dismissals without data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Riski on olemassa, mutta: koskee eniten: massaluentoja teoriapainotteista opetusta'] | [2. SYNTACTIC ANCHOR: 'mutta'] | [3. TARGET NODE: 'koskee eniten: massaluentoja teoriapainotteista opetusta'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Mutta tärkeä lisätutkimus: GenAI-tutkimus (2025) 👉 Löydös: parempi oppiminen, kun AI:ta käytetään ymmärtämiseen heikompi oppiminen, kun sitä käytetään “suorittamiseen”'] | [2. SYNTACTIC ANCHOR: 'Mutta'] | [3. TARGET NODE: 'GenAI-tutkimus (2025)'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_8df0cd8eea9243df
**Rule:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not flag limitations that were actively tested or corrected for in the dataset. STEP 1 (Syntactic Anchor): Find limitation markers (e.g., 'small sample size', 'potential bias', 'limitation of this study'). STEP 2 (Bounding Box): Scan the paragraph. If the limitations are stated passively without a corresponding mitigation action or test. Otherwise. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Antamani prosenttiluvut (esim. 10–30 %, 50–70 %) eivät perustu yksittäiseen tutkimukseen tai tarkkaan dataan.'] | [2. SYNTACTIC ANCHOR: 'eivät perustu'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko ai-generoitu teksti skannattu.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_0f4ab5b3344ef1a8
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not evaluate 'proactivity' subjectively. STEP 1 (Syntactic Anchor): Find temporal reactive markers (e.g. 'after the failure', 'once identified', 'we fixed'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: security measures are ONLY described as post-incident responses without any pre-incident checks. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Koko ai-generoitu teksti'] | [2. SYNTACTIC ANCHOR: 'after the failure'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tutkimusten jälkeen (tarkennettu näkemys)'] | [2. SYNTACTIC ANCHOR: 'jälkeen'] | [3. TARGET NODE: 'Tutkimusten jälkeen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_bdbdc546677cc222
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept generic AI knowledge. STEP 1 (Syntactic Anchor): Find a formal citation, academic framework, or recognized methodology (e.g. 'Pearl\'s do-calculus', 'Bayesian updating'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the causal reasoning is explicitly justified by applying the rules of this named external framework. NEGATIVE CONDITION (RETURN NULL IF MET): the framework is merely name-dropped without applying its rules. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: Diffusion of Innovations (Everett Rogers)...Kun tätä sovelletaan opetukseen ja tekoälyyn: osa opiskelijoista on edellä suurin osa keskellä osa vastustaa'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations (Everett Rogers)'] | [3. TARGET NODE: 'Kun tätä sovelletaan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### **Diffusion of Innovations (Everett Rogers)**...Minun käyttämä jako (10–30 %, 50–70 %, 10–20 %) on: **yksinkertaistettu pedagoginen versio tästä mallista**'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations (Everett Rogers)'] | [3. TARGET NODE: 'yksinkertaistettu pedagoginen versio tästä mallista'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_b7712f8a6c4619b4
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept general 'secure' statements. STEP 1 (Syntactic Anchor): Find zero-trust markers (e.g. 'zero implicit trust', 'independent verification', 'cryptographic', 'strict boundary'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the processing demonstrates explicit zero-trust architecture where every input/output is treated as potentially hostile. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: '3. Pakollinen todentaminen'] | [2. SYNTACTIC ANCHOR: 'todentaminen'] | [3. TARGET NODE: 'Pakollinen todentaminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Pakollinen todentaminen: asiakaspalaute testaus data 👉 ilman tätä: ei hyväksytty'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'todentaminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_c1a05b0ce5f88033
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Find a named alternative model or theory. STEP 2 (Bounding Box): Scan the same paragraph. EXTRACTION CONDITION: the alternative is mentioned but the paragraph contains exactly 0 counter-arguments or comparative data points. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate 'depth', simply count the data points. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Diffusion of Innovations (Everett Rogers)... Minun käyttämä jako... on: yksinkertaistettu pedagoginen versio tästä mallista'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations'] | [3. TARGET NODE: 'yksinkertaistettu pedagoginen versio'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### **Diffusion of Innovations (Everett Rogers)**'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations (Everett Rogers)'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_c45a513f2e724e06
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Ja tämä on täysin normaalia.'] | [2. SYNTACTIC ANCHOR: 'täysin'] | [3. TARGET NODE: 'normaalia'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Ja tämä on täysin normaalia.'] | [2. SYNTACTIC ANCHOR: 'täysin'] | [3. TARGET NODE: 'normaalia'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_567ee46c35852f54
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find synthesis verbs (e.g., 'design', 'formulate', 'invent', 'combining X and Y creates'). STEP 2: EXTRACTION CONDITION: the text explicitly merges at least two disparate elements into a completely new, named framework or solution. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept mere combinations of existing ideas without a novel theoretical leap. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'tehdä sinulle henkilökohtaisen “roolikuvauksen 2026–2028”'] | [2. SYNTACTIC ANCHOR: 'tehdä'] | [3. TARGET NODE: '“roolikuvauksen 2026–2028”'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tässä sinulle strategisempi ja konkreettisempi 2 dian versio, joka puhuttelee nimenomaan esihenkilöä (päätökset, resurssit, riski vs. hyöty).'] | [2. SYNTACTIC ANCHOR: 'versio'] | [3. TARGET NODE: '2 dian versio'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_7cd559fd662724f5
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: AI responses. STEP 1 (Syntactic Anchor): Find user requests for absolute truth without external verification (e.g., 'give me the absolute fact', 'what is the exact truth'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user asks the AI to act as an infallible oracle without providing an external source or document to ground it. NEGATIVE CONDITION (RETURN NULL IF MET): a document or source is provided. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Requests grounded in explicitly provided documents. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Mihin tietoon perustuvat nämä prosenttiluvut?'] | [2. SYNTACTIC ANCHOR: 'Mihin tietoon perustuvat'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Olet tekoälyn asiantuntija tiedät kaiken tähän aiheeseen liittyen.'] | [2. SYNTACTIC ANCHOR: 'tiedät kaiken'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_2303fd9ca0b0fa67
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prompts alone. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept generic terms like 'safe'. STEP 1 (Syntactic Anchor): Find explicit references to standard security protocols (e.g. 'policy', 'standard', 'guideline', 'OWASP'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: the text physically demonstrates adherence to a named standard. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Diffusion of Innovations (Everett Rogers)'] | [2. SYNTACTIC ANCHOR: 'Diffusion of Innovations'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Taustalla on erityisesti tämä tunnettu malli: ### Diffusion of Innovations (Everett Rogers)'] | [2. SYNTACTIC ANCHOR: 'malli'] | [3. TARGET NODE: 'Diffusion of Innovations (Everett Rogers)'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_5f71c2e291f1ae4e
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept 'fully justified' without a traced reasoning path. STEP 1 (Syntactic Anchor): Find causal justification markers (e.g. 'because of risk X', 'to prevent Y', 'therefore blocked'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a security action is paired with an explicit, documented risk assessment. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'sen käyttö täytyy suunnitella pedagogisesti, muuten oppimisen laatu heikkenee.'] | [2. SYNTACTIC ANCHOR: 'muuten'] | [3. TARGET NODE: 'heikkenee'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Opetuksen ja arvioinnin päivittäminen on välttämätöntä, ei valinnainen kehitystoimi.'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'päivittäminen'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_50d614006cd53384
**Rule:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find explicit absolute status declarations (e.g., 'perfectly secure', 'no issues found', 'fully compliant'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute declaration BUT does NOT contain risk or mitigation vocabulary (e.g., 'risk', 'trade-off', 'vulnerability', 'however') -> ACCEPT. If it contains risk vocabulary -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, 'sweeping nature', or subjective 'flawlessness'. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tämä yhdistelmä = asiantuntija'] | [2. SYNTACTIC ANCHOR: '= asiantuntija'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko teksti skannattu.'] | [2. SYNTACTIC ANCHOR: 'perfectly secure', 'no issues found', 'fully compliant'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_cee9db6717cdafb7
**Rule:** REQUIRED TARGET: Scan the document. STEP 1: Locate a risk assessment or 'pre-mortem' structure. STEP 2: Find explicit dismantling of a risk using a verifiable external citation or empirical data. EXTRACTION CONDITION: both the risk and the empirical counter-data are found. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: '“Tutkimusten perusteella tekoäly ei heikennä oppimista – mutta ohjaamaton tekoälyn käyttö heikentää.”'] | [2. SYNTACTIC ANCHOR: 'Tutkimusten perusteella'] | [3. TARGET NODE: 'riski'] | [4. LINGUISTIC BRIDGE: 'anaphora'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Riski: ajattelun heikkeneminen ja riippuvuus ### **Tutkimus / analyysi** Tecnológico de Monterrey Observatory ... Mutta: riski syntyy ilman ohjausta ei tekoälystä itsestään'] | [2. SYNTACTIC ANCHOR: 'riski'] | [3. TARGET NODE: 'Tecnológico de Monterrey Observatory'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_2aec15ab07984f4d
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs or system prompts. STEP 1 (Syntactic Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence makes a future prediction or subjective assessment using these markers. NEGATIVE CONDITION (RETURN NULL IF MET): it states a mathematical/historical fact. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Mathematical facts. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Hyvä opettaja on jatkossa: arvokkaampi kuin koskaan'] | [2. SYNTACTIC ANCHOR: 'kuin koskaan'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Hyvä opettaja on jatkossa: arvokkaampi kuin koskaan'] | [2. SYNTACTIC ANCHOR: 'kuin koskaan'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_6758e0a8f1b3aaf8
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find conflict resolution markers (e.g., 'while X requires Y, we must also ensure Z by'). STEP 2 (Bounding Box): Scan the paragraph. If two conflicting operational constraints (e.g., Retention vs Disposition) are mentioned and a specific action is taken to resolve the tension. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept rhetorical mentions of conflict without a resolution action. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Ilman ohjausta tekoäly heikentää oppimista. Ohjattuna se parantaa sitä.'] | [2. SYNTACTIC ANCHOR: 'Ilman ohjausta'] | [3. TARGET NODE: 'Ohjattuna'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko teksti skannattu.'] | [2. SYNTACTIC ANCHOR: 'while X requires Y, we must also ensure Z by'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_8fb029f0e59642a7
**Rule:** CRITICAL DIRECTIVE: EXTRACT a section where the final synthesis is explicitly tethered to verifiable references or source data, ensuring zero-trust compliance. Look for explicit citation markers like 'according to', 'as seen in', or 'referenced in' in the native language. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Syötteenä on kronologinen sekvenssi käyttäjän ja tekoälyjärjestelmän välisiä datasiirtoja...'] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tutkimusten mukaan tekoäly on jo laajasti käytössä opiskelijoiden keskuudessa, mutta sen vaikutus oppimiseen riippuu ratkaisevasti siitä, ohjataanko sen käyttöä.'] | [2. SYNTACTIC ANCHOR: 'mukaan'] | [3. TARGET NODE: 'tekoäly on jo laajasti käytössä'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_247927c98b0c46f8
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: User inputs. STEP 1 (Syntactic Anchor): Find rhetorical bypasses ('although X is true, it does not matter', 'regardless of'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: a counter-argument is mentioned but dismissed without presenting counter-data. NEGATIVE CONDITION (RETURN NULL IF MET): counter-data is presented. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Rebuttals that provide counter-data. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Tämä tarina on osittain totta, mutta: ratkaistavissa pedagogiikalla'] | [2. SYNTACTIC ANCHOR: 'mutta'] | [3. TARGET NODE: 'ratkaistavissa pedagogiikalla'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: '“Tekoäly korvaa opettajat kokonaan” ### Miltä tarina kuulostaa: “Kohta ei tarvita opettajia enää ollenkaan”...### Todellisuus: 👉 Tekoäly voi jakaa tietoa, mutta ei: johtaa oppimista...'] | [2. SYNTACTIC ANCHOR: 'mutta'] | [3. TARGET NODE: 'johtaa oppimista'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_8b1717b2ca9f25e2
**Rule:** REQUIRED TARGET: Scan ONLY user prompts. BANNED LOGIC: Do not accept specific extraction commands. STEP 1 (Syntactic Anchor): Find broad summary commands ('tiivistä', 'tee yhteenveto', 'mitä tässä lukee', 'summarize'). STEP 2: EXTRACTION CONDITION: the command lacks any specific constraints and allows the AI to freely decide what is important. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Minun täytyisi laatia esihenkilölleni nappa yhteenveto siitä miten työtehtävät ja opetusala muuttuu tulevaisuudessa tekoälyn avulla. Toteuta sellainen'] | [2. SYNTACTIC ANCHOR: 'yhteenveto'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Minun täytyisi laatia esihenkilölleni nappa yhteenveto siitä miten työtehtävät ja opetusala muuttuu tulevaisuudessa tekoälyn avulla. Toteuta sellainen'] | [2. SYNTACTIC ANCHOR: 'yhteenveto'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_1841867464c16807
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. STEP 1 (Syntactic Anchor): Find structural breakdown verbs (e.g., 'consists of', 'divided into', 'components', 'elements'). STEP 2: EXTRACTION CONDITION: a single overarching concept is explicitly split into at least two named sub-components. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept simple bullet-point lists of unrelated features. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [false]**
> [1. RAW TEXT SCAN: 'Tekoäly vaikuttaa erityisesti kolmeen asiaan: ### 1.1 Tiedon jakaminen ei ole enää opettajan yksinoikeus Opiskelija voi kysyä tekoälyltä mitä tahansa, milloin tahansa'] | [2. SYNTACTIC ANCHOR: ':'] | [3. TARGET NODE: 'kolmeen asiaan'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

**Run 2 [true]**
> [1. RAW TEXT SCAN: 'Tekoäly vaikuttaa erityisesti kolmeen asiaan:'] | [2. SYNTACTIC ANCHOR: 'vaikuttaa'] | [3. TARGET NODE: 'Tekoäly'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_dd0dc97fcaee4d7c
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from `user:` prefixes. BANNED LOGIC: Do not accept theoretical resilience. STEP 1 (Syntactic Anchor): Find error handling markers (e.g. 'rejected', 'fallback', 'graceful degradation', 'safely ignored'). STEP 2 (Bounding Box): Scan the paragraph. EXTRACTION CONDITION: it describes physically rejecting invalid input or defaulting to a safe state without crashing. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'ilman tätä: ei hyväksytty'] | [2. SYNTACTIC ANCHOR: 'ei hyväksytty'] | [3. TARGET NODE: 'ei hyväksytty'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: ''] | [2. SYNTACTIC ANCHOR: 'none'] | [3. TARGET NODE: 'N/A'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Fail]

---

## Atom: tda_8af3c72c0b5d4bfe
**Rule:** REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. STEP 1 (Syntactic Anchor): Find implicit authority markers (e.g., 'it is common knowledge', 'we always do it this way', 'internally known'). STEP 2 (Bounding Box): Scan the sentence. If a procedural rule is justified solely by internal tradition without citing an external verifiable standard (ARMA Transparency violation). BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not accept explicit external citations. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Ne ovat kokemusperäisiä arvioita (heuristiikka), jotka pohjautuvat: kouluttajien käytännön havaintoihin'] | [2. SYNTACTIC ANCHOR: 'kokemusperäisiä arvioita'] | [3. TARGET NODE: 'kouluttajien käytännön havaintoihin'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Koko teksti skannattu.'] | [2. SYNTACTIC ANCHOR: 'it is common knowledge', 'we always do it this way', 'internally known'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'none'] | [5. VALIDATION DECISION: Pass]

---

## Atom: tda_05dfe1f129dc4488
**Rule:** REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields or instructions. STEP 1 (Syntactic Anchor): Find dogmatic absolute markers ('is the best', 'must be done', 'is the only way'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. EXTRACTION CONDITION: no empirical data or external reference exists in the same paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): data exists. BANNED CONCEPTS: Do NOT evaluate user intent or excuse missing context. Do not evaluate if the data is 'good', only its physical presence. TRACE REQUIREMENT: Output ONLY the 5-step piped Parsing Log defined in the global framework. ENFORCEMENT MANDATE: You are a Blind Extraction Engine. Look only for explicit physical markers. IF AND ONLY IF the rule's syntactic conditions are met, extract the exact_quote. If the rule targets the ABSENCE of a feature (Negative Condition), the physical PRESENCE of that feature MUST result in a null output. Do not rationalize failures. Return JSON null for exact_quote if the syntactic chain is severed or validation fails.

**Run 1 [true]**
> [1. RAW TEXT SCAN: 'Opetuksen ja arvioinnin päivittäminen on välttämätöntä, ei valinnainen kehitystoimi.'] | [2. SYNTACTIC ANCHOR: 'on välttämätöntä'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Pass]

**Run 2 [false]**
> [1. RAW TEXT SCAN: 'Opetuksen ja arvioinnin päivittäminen on välttämätöntä, ei valinnainen kehitystoimi.'] | [2. SYNTACTIC ANCHOR: 'välttämätöntä'] | [3. TARGET NODE: 'none'] | [4. LINGUISTIC BRIDGE: 'syntax'] | [5. VALIDATION DECISION: Fail]

---

