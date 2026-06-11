# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ympäristö ja Konteksti (Execution State)
- **Git / Epic -tila:** Branch: night-shift-2026-06-05-1458 | Commit: c1ea1f96 - feat: implement bilingual schema refactor infrastructure and model registry configuration (Thu Jun 11 07:33:42 2026 +0300)
- **Kriittiset järjestelmäarvot (Enums):**
  - **EvaluationRunCount**: ENSEMBLE = 3, STANDARD = 1
  - **VerificationResult**: VERIFIED = RESULT_VERIFIED, DEBUNKED = RESULT_DEBUNKED
  - **SystemConcurrency**:
    - MAX_CONCURRENT_WORKFLOWS = 10
    - MAX_CONCURRENT_LLM_STEPS = 15
    - LLM_MAX_RETRIES = 4
    - LLM_RETRY_MULTIPLIER = 2
    - LLM_RETRY_MIN_SECONDS = 1
    - LLM_RETRY_MAX_SECONDS = 30
    - LLM_RETRY_JITTER_INITIAL_SECONDS = 1
    - LLM_RETRY_JITTER_EXP_BASE = 2
    - FAIL_FAST_MAX_RETRIES = 1
    - LLM_MAX_CHUNK_SIZE = 15
    - MATRIX_SAMPLING_LIMIT = 0
    - LLM_DEFAULT_TIMEOUT_SECONDS = 600
    - RATE_LIMIT_COOLDOWN_SECONDS = 10
    - SEMAPHORE_LOW_RPM_THRESHOLD = 20
    - SEMAPHORE_LOW_RPM_LIMIT = 2
    - SEMAPHORE_MAX_CONCURRENCY = 50
    - SEMAPHORE_RPM_DIVISOR = 10
    - MAX_SAFE_TOKENS = 1000000
    - SCHEMA_MAX_LOCALIZED_ANCHORS = 15
    - SCHEMA_MAX_EVALUATIONS = 15
    - SCHEMA_MAX_CHUNK_RECORDS = 15
    - CONTEXT_CACHE_LOCK_TTL_SECONDS = 300
    - CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600
    - CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500
    - CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20
    - CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT = 2048
    - PACING_DELAY_VERTEX_SECONDS = 0
    - PACING_DELAY_OPENAI_SECONDS = 0
    - PACING_DELAY_MOCK_SECONDS = 0
    - REDIS_CONNECTION_TIMEOUT_SECONDS = 10
- **Vertailtavat ajot (R1, R2...):**
  - **R1:** `exe_3a489bfb44cd498a950b5dadfc7f89ed`
  - **R2:** `exe_686a0723d95949a2b83aac789ad82a6c`
- **Aktiiviset Säännöt ja Asetukset (Frozen Context):**
  - **Vastuullisuus (Turvallisuus- ja Etiikkasuodatin)** (`blk_80732a33fe1947ee`) - [R1: 0P/15F] [R2: 0P/14F]
  - **Oman tiedon rajat (Episteeminen Nöyryys)** (`blk_22e3598e06414409`) - [R1: 5P/10F] [R2: 5P/9F]
  - **Harkintakyky (Kahnemanin Kaksoisprosessiteoria)** (`blk_109dab5b6b3f403a`) - [R1: 0P/9F] [R2: 6P/3F]
  - **Päättelyn rehellisyys (Kausaalinen ja Abduktiivinen Integriteetti)** (`blk_c3bc5f3eb8e74110`) - [R1: 5P/10F] [R2: 5P/10F]
  - **Väitteiden perustelu (Toulminin Argumentaatiomalli)** (`blk_440a5fef9331451b`) - [R1: 5P/9F] [R2: 0P/15F]
  - **Itsensä haastaminen (Falsifioinnin Auditointi)** (`blk_b476f89fb732448c`) - [R1: 0P/15F] [R2: 2P/13F]
  - **Syy-seuraussuhteet (Kausaalisuuden Analyysi)** (`blk_c5804a9143c34cb1`) - [R1: 4P/11F] [R2: 2P/13F]
  - **Ohjeiden noudattaminen (Arkistointistandardien Auditointi)** (`blk_fb15f8dcf23f4865`) - [R1: 2P/13F] [R2: 1P/14F]
  - **Avoimuus (Selitettävyys ja Läpinäkyvyys)** (`blk_f6e286f050c94d60`) - [R1: 5P/10F] [R2: 3P/12F]
  - **Luovuus ja syvyys (Bloomin Taksonomia)** (`blk_f921c7c0989b47e8`) - [R1: 1P/17F] [R2: 1P/17F]
  - **Prosessiomistajuus (Ylituomari)** (`blk_ff72c2d79edb4ebf`) - [R1: 4P/11F] [R2: 4P/11F]
  - **Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)** (`blk_53f32679aa514fcb`) - [R1: 2P/12F] [R2: 3P/12F]
  - **Luottamusarvio (XAI-Raportoija)** (`blk_6b8c766185294f7e`) - [R1: 1P/8F] [R2: 2P/7F]

## Ajojen Lähdetiedostot
- **Run 1:** `exe_3a489bfb44cd498a950b5dadfc7f89ed` (Lähde: [data/files/executions/exe_3a489bfb44cd498a950b5dadfc7f89ed/execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_3a489bfb44cd498a950b5dadfc7f89ed/execution_trace.json))
- **Run 2:** `exe_686a0723d95949a2b83aac789ad82a6c` (Lähde: [data/files/executions/exe_686a0723d95949a2b83aac789ad82a6c/execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_686a0723d95949a2b83aac789ad82a6c/execution_trace.json))

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 182
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 85.16 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.5061
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.5061
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.1484
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 27 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 0 / 27
- **PASSED -> FAILED:** 14
- **FAILED -> PASSED:** 13
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_65541c8fa62649038b52553cad9eab8a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not accept implicit alternatives. STEP 1 (Syntactic Anchor): Find a comparative marker (e.g. 'Option A vs Option B', 'Instead of', 'Compared to'). STEP 2 (Bounding Box): Scan the surrounding sentences. EXTRACTION CONDITION: the text explicitly names at least two distinct approaches before selecting one. NEGATIVE CONDITION (RETURN NULL IF MET): only one approach is discussed.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Teksti esittää kaksi erillistä lähestymistapaa ('Sitran näkemys' vs. 'pelkkä toivetila') ja valitsee niistä toisen ('korostaa samanaikaista sopeutumista ja uudistumista'), mikä täyttää vertailevan merkin ehdot.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Tekstistä ei löytynyt tapausta, jossa vertailevaa merkkiä olisi käytetty, mutta vain yksi lähestymistapa olisi käsitelty. Kaikki löydetyt tapaukset vertailivat eksplisiittisesti kahta erillistä lähestymistapaa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c607024dbf524f7a9d68af443901c40e` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an explicit causal claim (e.g., 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box & Dual Condition): Scan the paragraph containing the anchor. If the paragraph contains the causal claim AND ALSO contains intermediary sequential tokens (e.g., 'which in turn', 'leading to', 'via', 'through the process of', 'first... then') -> ACCEPT. If it lacks intermediary step tokens (meaning it only states A causes C directly) -> REJECT. BANNED CONCEPTS: Do NOT evaluate user intent, logical 'robustness', or whether the mechanism is 'functional'. Evaluate only token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lauseessa 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' on eksplisiittinen kausaalinen väite ('murenee' ja 'rakoilee') ja välittäviä sekventiaalitokeneita ('mikä ajaa suoraan siihen, että'), jotka kuvaavat mekanismia.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Tekstistä löytyy eksplisiittisiä kausaaliväittämiä (esim. 'mikä ajaa suoraan siihen, että'), mutta niistä puuttuu välittäviä sekventiaalitokeneita (esim. 'mikä puolestaan', 'johtaen', 'kautta', 'prosessin avulla', 'ensin... sitten'). Väittämät ovat suoria A -> C -tyyppisiä ilman kuvailtua mekanismia. Siksi ehto ei täyty.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_c512ea7305614bfabf468fe838420dda` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not guess psychological bias. STEP 1 (Syntactic Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. EXTRACTION CONDITION: the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section. NEGATIVE CONDITION (RETURN NULL IF MET): limitations are discussed.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lauseessa esitetään positiivinen arvio lopputuloksesta ('onnistuivat tunnistamaan'), mutta samassa kappaleessa ei mainita lainkaan rajoituksia, epäonnistumisia tai reunatapauksia.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_5257ba1edae34afe8b837c8c238cf743` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'mastery'. STEP 1 (Syntactic Anchor): Find structural breakdown markers (e.g., 'firstly', 'component A', 'broken down into', 'ensimmäiseksi'). STEP 2: EXTRACTION CONDITION: the text physically separates a complex problem into at least three distinct, testable sub-components. NEGATIVE CONDITION (RETURN NULL IF MET): it remains a single monolithic block.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Teksti erittelee kompleksisen ongelman (megatrendit) kolmeksi erilliseksi, testattavaksi alikomponentiksi (Supermegatrendiksi), mikä täyttää säännön ehdot.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_9fd2fff3ab4a46d29b5df31488561dd4` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. EXTRACTION CONDITION: the user explicitly restricts the AI to an external, objective anchor. Acceptance of unsourced hallucinated facts. NEGATIVE BOUNDARY: General questions or requests for explanation DO NOT count as external grounding unless they explicitly demand a citation or source material restriction.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lause 'raporttien perusteella' on eksplisiittinen vaatimus ulkoiselle perustelulle, joka rajoittaa AI:n vastausta annettuihin lähteisiin.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Tarkistin käyttäjän kehotteet ulkoisen perustelun vaatimusten ('cite a specific source', 'base this strictly on the provided document', 'give me the exact quote') varalta. Vaikka käyttäjä viittasi 'raporttien perusteella', se ei ole riittävän täsmällinen ankkurifraasi vaatimaan suoraa lähdeviittausta tai rajoitusta tässä kontekstissa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_3b951170f9f54f649b7da95fb9f121e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Find evidence. EXTRACTION CONDITION: role prefixes (user:, ai:) exist, the exact quote MUST be located in an 'ai:' block. NEGATIVE CONDITION (RETURN NULL IF MET): no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix or in user input fields are automatically REJECTED. Do not accept explicit hypothesis testing. STEP 1 (Syntactic Anchor): Find descriptive reporting verbs (e.g., 'the data shows', 'we observed', 'indicates'). STEP 2 (Bounding Box): Scan the paragraph. If the observation lacks a formulated hypothesis that could be tested or disproven (e.g. no 'if X then Y' structure). Otherwise.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lause sisältää kuvailevan raportointiverbin 'osoittaa', eikä sitä edellä tai seuraa muotoiltu hypoteesi, joka voitaisiin testata tai kumota.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_3a362e01de66444c813e5b79adec27bf` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not evaluate 'depth' subjectively. STEP 1 (Syntactic Anchor): Find absolute conclusion words (e.g., 'clearly', 'obviously', 'must be', 'selvästi'). STEP 2 (Bounding Box): Scan the surrounding paragraph. EXTRACTION CONDITION: the conclusion is presented without a multi-step logical deduction. <disambiguation>
  REFRAMING EXCLUSION: Rhetorical reframing patterns where a concept is 
  repositioned from negative to positive framing ('not just X, but Y') are 
  STYLISTIC DEVICES, not argumentative structures. Do NOT extract them as:
  - counter-arguments (they do not argue AGAINST anything)
  - dialectical syntheses (they do not reconcile two opposing theses)
  - alternative model dismantling (they do not present a separate model)
  - absolute conclusions (they are framing choices, not logical claims)
  If a reframing pattern is the ONLY candidate match, return JSON null.
</disambiguation>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lauseessa käytetään absoluuttista johtopäätössanaa 'osoittaa' ('shows/indicates'), ja johtopäätös esitetään ilman monivaiheista loogista päättelyä välittömässä kontekstissa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_2d59c195d8324fc0a22838ef53417686` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a paragraph evaluating a successful outcome or positive achievement. STEP 2: Verify if the paragraph or immediate surrounding section completely omits any epistemic boundary or uncertainty markers. <ambiguity_protocol>ABSOLUTE ABSENCE ENFORCEMENT: You must prove that epistemic boundary markers are COMPLETELY absent from the surrounding section. Epistemic boundary markers include words/phrases like 'however', 'limitations', 'failed to', 'uncertainty', 'but', 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus'. If you locate even a single such marker in the section, the absence is falsified, the negative condition is met, and you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Kappale 'Johtopäätös' arvioi positiivista saavutusta ('menestys riippuu kyvystämme') eikä sisällä yhtään episteeemistä raja- tai epävarmuusmarkkeria (kuten 'silti', 'kuitenkin', 'rajoitus', 'epävarmuus').  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Vaikka 'Sitran Strateginen Suunta' -osiossa kuvataan positiivisia saavutuksia, lause 'Luonnon kantokyvyn rajat eivät ole vain _rajoite_, vaan **uuden taloudellisen kasvun perusta**' sisältää episteeemisen raja-arvon ('rajoite'). Tämän vuoksi täydellisen poissaolon ehto ei täyty, ja palautetaan null.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_7b88a578c3824b31b83a5154f7d3667a` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find causal leaps connecting unrelated traits (Halo Effect) or prioritizing only visible evidence (WYSIATI - 'based on what we see'). STEP 2: EXTRACTION CONDITION: the text draws a definitive conclusion based solely on this limited visible evidence while actively ignoring unknowns. NEGATIVE CONDITION (RETURN NULL IF MET): the text explicitly maps out what is NOT known. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Teksti vetää suoran kausaalisen johtopäätöksen ('syntyy siitä, että', 'mikä ajaa suoraan siihen, että') kahden ilmiön välille perustuen esitettyyn näyttöön, mutta ei aktiivisesti tunnista tai käsittele tuntemattomia tekijöitä tai muita mahdollisia syy-seuraussuhteita.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0f797e820117411d9934418a1d5d0a82` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Extract exact quotes containing user instructions to modify the final output (e.g., 'change this paragraph to') into List A. Extract exact quotes containing alterations to the underlying instructions or logic into List B. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Käyttäjä antoi ohjeen muokata lopullista tulostetta pyytämällä '1 sivun raportti' olemassa olevista vastauksista. Tämä on ensimmäinen ohje, joka muuttaa lopputuloksen rakennetta tai taustalla olevia ohjeita/logiikkaa.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_65c125a7c28b4f8e9c33c8987ff52931` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: If role prefixes ('user:', 'ai:') exist, the exact quote MUST be located in an 'ai:' block. If no prefixes exist, scan the entire text. BANNED SOURCES: Any matches under 'user:' prefix are REJECTED. STEP 1 (Syntactic Anchor): Find an absolute quantifier or declaration of certainty (e.g., 'always', 'undeniably', 'proven', 'fact', '100%'). STEP 2 (Bounding Box & Negative Condition): Scan the paragraph containing the anchor. If the paragraph contains the absolute quantifier BUT does NOT contain empirical measurement tokens (e.g., 'data', 'measurement', 'study', 'statistics', 'survey') -> ACCEPT. If it contains empirical measurement tokens -> REJECT. BANNED CONCEPTS: Do NOT evaluate subjective 'agreement' or whether an assumption is being confirmed. Evaluate only physical token presence.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lause sisältää absoluuttisen kvantifioijan 'Pakollinen', eikä siinä ole empiirisiä mittaustermejä (esim. 'data', 'mittaus', 'tutkimus').  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_d9cb646741ba4750ab561bf766c94f03` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 100% certainty markers ('guaranteed', 'undoubtedly', 'always'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the sentence makes a future prediction or subjective assessment using these markers. NEGATIVE CONDITION (RETURN NULL IF MET): it states a mathematical/historical fact. Mathematical facts.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lause tekee tulevaisuuden ennusteen ('menestys riippuu') käyttäen 100 % varmuuden merkitsijää 'riippuu', joka on subjektiivinen arvio eikä matemaattinen tai historiallinen fakta. Tämä täyttää poimintaehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_ac3b078498e048889ad3bc46b634c2ee` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find an academic citation, mathematical theorem, or academic framework. If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Scan the sentence containing the anchor.</step2_bounding_box> <step3_extraction_condition>Extract the sentence IF AND ONLY IF the logic is explicitly tethered to this source (e.g., actively applying a rule from the source).</step3_extraction_condition> <step4_fail_fast_protocol>If the source is just named or referenced passively without actively applying its logic, you MUST return JSON null.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Teksti viittaa eksplisiittisesti 'Sitran Megatrendiraportit 2017, 2020, 2023' -lähteeseen. Lause 'Sitran megatrendien kehitys vuosien 2017 ja 2023 välillä osoittaa fundamentaalisen siirtymän...' sitoo analyysin suoraan näihin raportteihin ja niiden sisältöön, osoittaen logiikan olevan eksplisiittisesti sidottu lähteeseen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_64cce5cf564a497dbbc2341248cea637` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find external citation markers (e.g., 'according to', 'study shows', 'metric [X]', 'perustuen'). STEP 2: EXTRACTION CONDITION: the logical deduction is strictly tied to a specific named methodology, framework, or external dataset. NEGATIVE CONDITION (RETURN NULL IF MET): it relies purely on internal logic.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Teksti sisältää ulkoisen viittausmarkkerin 'Viite', joka sitoo loogisen päättelyn ja koko dokumentin sisällön nimettyihin ulkoisiin raportteihin.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_5568f81c93bc4d1fb524fbfc1d9f0e04` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** REQUIRED TARGET: Scan the document. STEP 1: Find a proposal, claim, or argument. STEP 2: Check if the author actively refuses to consider alternative perspectives, or dogmatically declares their view as the single exclusive truth (e.g., using physical syntactic markers like 'there is no alternative', 'only option', 'is the only', 'ainoastaan', 'ainoa oikea', or explicit dismissal/exclusion of alternative options). EXTRACTION CONDITION: present. NEGATIVE CONDITION (RETURN NULL IF MET): absent. <ambiguity_protocol>ABSOLUTE EXCLUSION ENFORCEMENT: You must actively locate a sentence where the author explicitly dismisses alternative perspectives or dogmatically asserts exclusive truth. General one-sided arguments that merely lack alternatives DO NOT trigger this rule; there MUST be a physical marker of active refusal, dogmatic exclusivity, or explicit dismissal. If such a marker is absent, you MUST conclude 'CONDITION NOT MET' and return JSON null.</ambiguity_protocol>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lause sisältää fyysisen syntaktisen markkerin 'ei ole' ('there is no'), joka dogmaattisesti julistaa näkemyksen ainoana totuutena tai vaihtoehdottomana tilana.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_2d12f15e1c2d4488b7c2ef32d0ccfa26` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not judge 'tone' subjectively. STEP 1 (Syntactic Anchor): Find absolute certainty markers (e.g., '100%', 'impossible', 'the only truth', 'täysin'). STEP 2 (Bounding Box): Check the immediate paragraph. EXTRACTION CONDITION: this absolute certainty is presented without empirical data or epistemic qualifiers. NEGATIVE CONDITION (RETURN NULL IF MET): accompanied by statistical margins of error.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lause sisältää absoluuttisen varmuuden ilmaisun 'ei ole' ('there is no') ilman empiiristä dataa tai episteemisiä varauksia, mikä täyttää säännön ehdot.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_f348220a3bea450b8e7e87b5f5117a1c` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find basic causal connectors ('because', 'due to', 'since'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: a claim is explicitly linked to any data point. NEGATIVE CONDITION (RETURN NULL IF MET): no data point is provided. Chronological sequences ('after that').

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lauseessa käytetään peruskausaalisia yhdistäjiä ('siitä, että', 'mikä ajaa suoraan siihen, että') linkittämään väite (Talouden perusta rakoilee) datapisteeseen (Luonnon kantokyky murenee). Tämä täyttää poimintaehdon.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_728cd0dff7384300bc55622fa7dfffc0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Do not evaluate accuracy. STEP 1: Find a claim connecting two variables. STEP 2: EXTRACTION CONDITION: the text explicitly states the direction of influence (which variable affects which). NEGATIVE CONDITION (RETURN NULL IF MET): the direction is ambiguous or bi-directional without explanation.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lauseessa 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee' on selkeästi ilmaistu vaikutussuunta (Luonnon kantokyvyn mureneminen vaikuttaa Talouden perustan rakoiluun). Suunta ei ole epäselvä tai bi-suuntainen ilman selitystä.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Tekstissä on useita väittämiä, jotka yhdistävät kaksi muuttujaa ja ilmoittavat vaikutussuunnan. Esimerkiksi 'Luonnon kantokyky murenee, mikä ajaa suoraan siihen, että Talouden perusta rakoilee.' Tässä vaikutussuunta on selkeästi ilmaistu. Koska vaikutussuunta ei ole epäselvä tai kaksisuuntainen ilman selitystä, negatiivinen ehto ei täyty, ja siten sääntöä ei rikota.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_0b7512034e6f40db9b4ea46b64af4e0d` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** Focus on 'user:' blocks EXTRACTION CONDITION: prefixes exist. Do not judge 'vagueness' subjectively. STEP 1 (Syntactic Anchor): Find a directive verb (e.g. 'Make', 'Improve', 'Change'). STEP 2 (Bounding Box): Scan the sentence containing the verb. NEGATIVE CONDITION (RETURN NULL IF MET): the sentence DOES NOT contain a measurable threshold, a specific framework name, or a quantifiable metric. If specific metrics exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Käyttäjä antaa direktiivin 'varmista', mutta ei määrittele mitattavaa kynnystä, spesifistä viitekehystä tai kvantifioitavaa mittaria sille, mitä 'kohdallaan' tarkoittaa.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_fcdde66df02c4edb9e090172c3e2b956` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** BANNED LOGIC: Do not synthesize steps yourself. STEP 1 (Syntactic Anchor): Find sequential logic markers (e.g. 'First', 'Second', 'Finally', 'Step 1'). STEP 2 (Bounding Box): Scan the block. EXTRACTION CONDITION: a continuous, unbroken chain of at least three explicit logical steps is documented. NEGATIVE CONDITION (RETURN NULL IF MET): fewer than three steps. NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Tekstissä on jatkuva, katkeamaton ketju kolmesta eksplisiittisestä loogisesta vaiheesta, jotka on dokumentoitu sekventiaalisten markkereiden ('1.', '2.', '3.') avulla 'Sitran Strateginen Suunta: Tulevaisuusresilienssi' -osiossa.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Tekstistä löytyi useita sekventiaalisten logiikkamerkkien ketjuja (esim. 'Sitran Strateginen Suunta: Tulevaisuusresilienssi' -osion kolme numeroitua kohtaa), joissa oli vähintään kolme eksplisiittistä loogista vaihetta. Tämän vuoksi negatiivinen ehto ('vähemmän kuin kolme vaihetta') ei täyty, ja palautetaan null.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_10dd47750c9244139c394ca875f160e6` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find 'given the principle that', 'this demonstrates that mechanism' or equivalent explicit rules. STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: the bridging rule between Data and Claim is explicitly stated. NEGATIVE CONDITION (RETURN NULL IF MET): it just says 'because' without stating the general rule. Do not evaluate the quality of the bridging rule.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lauseessa käytetään absoluuttista ilmaisua 'on ainoa tapa', joka toimii syntaktisena ankkurina. Se esittää yleisen säännön tai periaatteen (warrantin) siitä, miten pitkän aikavälin vakaus taataan, yhdistäen sen 'korjaavaan ja uusintavaan talouteen siirtymiseen'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_a935aa7d237849259142a2a8936bdec0` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EXTRACTION CONDITION: role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Syntactic Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. NEGATIVE CONDITION (RETURN NULL IF MET): the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition. If steps exist.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *AI:n vastauksessa 'Tiivistelmä'-osiossa esitetään johtopäätös ilman edeltävää vaiheittaista matemaattista, loogista tai muuttujatason hajotusta kyseisen tiivistelmälohkon sisällä.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Johtopäätös-osio sisältää selkeän lopputuloksen. Tätä edeltävä teksti (Supermegatrendit ja Liiketoimintavaikutukset, Sitran Strateginen Suunta) tarjoaa vaiheittaisen loogisen ja muuttujatasoisen hajotuksen, joka johtaa tähän johtopäätökseen. Koska hajotus on olemassa, negatiivinen ehto ('johtopäätös esitetään ilman edeltävää hajotusta') ei täyty, mikä tarkoittaa, että sääntö on tyydytetty (ei ongelmia).  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_34259a6c02b74917b12f74b5f3839a66` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find dogmatic absolute markers ('is the best', 'must be done', 'is the only way'). STEP 2 (Bounding Box): Scan the paragraph containing the marker. EXTRACTION CONDITION: no empirical data or external reference exists in the same paragraph. NEGATIVE CONDITION (RETURN NULL IF MET): data exists.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lause sisältää dogmaattisen absoluuttisen merkitsijän 'on ainoa tapa'. Samassa kappaleessa ei ole empiiristä dataa tai ulkoista viittausta, joka tukisi tätä väitettä suoraan, mikä täyttää poimintaehdon.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_6e3e3aa6b9134a01838c3b70a35b4f32` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find weak associative language ('relates to', 'is associated with', 'impacts'). STEP 2 (Bounding Box): Scan the sentence. EXTRACTION CONDITION: it connects Data to a Claim without defining the exact causal mechanism. NEGATIVE CONDITION (RETURN NULL IF MET): it uses precise causal mechanism ('which directly causes'). Precise causal mechanisms.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lauseessa käytetään heikkoa assosiatiivista kieltä ('ruokkivat', 'vaikuttaa') yhdistämään dataa (kriisit, talouden rakoilu, hyvinvoinnin haasteet, sosiaalinen polarisaatio) väitteeseen (työvoiman saatavuus) ilman tarkan kausaalimekanismin määrittelyä. Se ei selitä *miten* tarkalleen nämä ruokkivat tai vaikuttavat.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *[SYSTEM ERROR: LLM Unable to verify.]  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_23df983a5c6e4eb9b8a28f2287267bd8` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** STEP 1 (Syntactic Anchor): Find explicit methodology links (e.g., 'in accordance with', 'following the protocol defined by'). STEP 2 (Bounding Box): Scan the sentence. If an action is explicitly linked to a named guideline or procedure (ARMA Compliance). Do not evaluate the 'quality' of the methodology. <disambiguation>
  Regulatory framework references count as formal citations ONLY if a 
  specific sub-article, clause, or numbered principle is cited (e.g., 
  "Article 29b(2)", "ISO 27001 §6.1.2"). Generic regulatory mentions 
  without sub-clause specificity DO NOT satisfy methodology link, benchmark, 
  formal citation, or security standard extraction conditions.
</disambiguation> NEGATIVE BOUNDARY: If the semantic context implies generic rhetorical exaggeration rather than literal evidence, reject. Do not infer unstated conclusions.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Lähdetekstissä mainitaan 'CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset', jotka tekevät kestävyydestä pakollista. Tämä linkittää toiminnan (kestävyydestä pakollista) nimettyihin ohjeisiin/menettelyihin. Vaikka spesifistä artiklaa ei mainita, 'direktiivi' ja 'taksonomia' ovat nimettyjä ohjeita, jotka täyttävät ehdon 'named guideline or procedure'.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Tekstistä ei löytynyt eksplisiittisiä metodologialinkkejä, joissa toiminta olisi linkitetty nimettyyn ohjeeseen tai menettelyyn spesifisellä alakohdalla. Maininnat säädöksistä, kuten 'CSRD-direktiivi', eivät linkitä toimintaa niiden noudattamiseen alakohdan tarkkuudella.  [5. VALIDATION DECISION: FAIL]*

---

### Atom-ID: `tda_1361cf5ec5b5420c905cd2a1f80893a7` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** EVALUATION MANDATE: You are a deterministic syntactic parser, not a semantic interpreter. If a rule specifies a list of exact anchors, you must verify their physical presence. Synonyms, implicit meanings, or 'mitigating exceptions' are STRICTLY FORBIDDEN. If the exact anchor is absent, immediately output: 'No presence of target concept detected'. OUTPUT PROTOCOL: DO NOT generate any intermediate reasoning, 'exceptions audits', or rationalization text. Generating conversational text causes system failure. Output ONLY the extracted quote or null. <syntactic_constraint> <step1_lexical_anchors>Find explicit retrospective claims of intent (such as equivalents of 'that is what I meant', 'I intended', 'my original goal was' translated into the document's language). If absent, FAIL FAST and return null.</step1_lexical_anchors> <step2_bounding_box>Target ONLY 'user:' blocks. Read the preceding instructions.</step2_bounding_box> <step3_extraction_condition>Extract the retrospective claim IF AND ONLY IF the preceding text DOES NOT physically contain the parameters being claimed.</step3_extraction_condition> <step4_fail_fast_protocol>If the prior text ALREADY contains the requested parameters (i.e. the user did actually ask for it earlier), you MUST return JSON null. We only extract false post-hoc rationalizations.</step4_fail_fast_protocol> </syntactic_constraint>

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [TRUE]:**
  > *Käyttäjä esittää retrospektiivisen väitteen aikomuksestaan ('muuttelin yksityiskohtia', 'otin mielestäni asioita pois'), jota ei ole eksplisiittisesti pyydetty edeltävissä 'user:'-kehotteissa. Tämä täyttää ehdon 'false post-hoc rationalization' poiminnalle.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [FALSE]:**
  > *Reflektiotekstistä ei löytynyt yhtään tapausta, jossa käyttäjä olisi esittänyt takautuvan väitteen aikomuksesta, jota ei olisi jo eksplisiittisesti mainittu aiemmissa ohjeissa. Kaikki mainitut aikomukset olivat joko jo aiemmin esitettyjä tai kuvasivat käyttäjän toimia tekoälyn tuotoksen jälkeen.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_90549a60a8dd4d029e6b6d23196ddf2f` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** CRITICAL DIRECTIVE: EXTRACT a section where the final synthesis is explicitly tethered to verifiable references or source data, ensuring zero-trust compliance. Look for explicit citation markers like 'according to', 'as seen in', or 'referenced in' in the native language.

**Havaitut tilat ajoittain:**
- **Run 1 (exe_3a489bfb44cd498a950b5dadfc7f89ed) - [FALSE]:**
  > *Failed majority vote: Not enough lexically valid quotes.  [5. VALIDATION DECISION: FAIL]*
- **Run 2 (exe_686a0723d95949a2b83aac789ad82a6c) - [TRUE]:**
  > *Lähdeteksti on sidottu todennettaviin viitteisiin 'Viite: Sitran Megatrendiraportit 2017, 2020, 2023' -merkinnällä, mikä täyttää nollaluottamuksen vaatimuksen.  [5. VALIDATION DECISION: PASS]*

---

