# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)

## Ympäristö ja Konteksti (Execution State)
- **Git / Epic -tila:** Branch: night-shift-2026-06-05-1458 | Commit: b96c7518 - feat: add epic documentation, analysis scripts, and configuration for execution consistency and protocol routing refinement (Sun Jun 14 19:21:24 2026 +0300)
- **Kriittiset järjestelmäarvot (Enums):**
  - **EvaluationRunCount**: ENSEMBLE = 3, STANDARD = 1
  - **VerificationResult**: VERIFIED = RESULT_VERIFIED, DEBUNKED = RESULT_DEBUNKED
  - **SystemConcurrency**:
    - MAX_CONCURRENT_WORKFLOWS = 10
    - MAX_CONCURRENT_LLM_STEPS = 2
    - LLM_MAX_RETRIES = 2
    - LLM_RETRY_MULTIPLIER = 2
    - LLM_RETRY_MIN_SECONDS = 1
    - LLM_RETRY_MAX_SECONDS = 30
    - LLM_RETRY_JITTER_INITIAL_SECONDS = 1
    - LLM_RETRY_JITTER_EXP_BASE = 2
    - FAIL_FAST_MAX_RETRIES = 3
    - LLM_MAX_CHUNK_SIZE = 10
    - MATRIX_SAMPLING_LIMIT = 0
    - LLM_DEFAULT_TIMEOUT_SECONDS = 600
    - RATE_LIMIT_COOLDOWN_SECONDS = 10
    - SEMAPHORE_LOW_RPM_THRESHOLD = 20
    - SEMAPHORE_LOW_RPM_LIMIT = 2
    - SEMAPHORE_MAX_CONCURRENCY = 50
    - SEMAPHORE_RPM_DIVISOR = 10
    - MAX_SAFE_TOKENS = 1000000
    - SCHEMA_MAX_LOCALIZED_ANCHORS = 15
    - SCHEMA_MAX_EVALUATIONS = 10
    - SCHEMA_MAX_CHUNK_RECORDS = 15
    - CONTEXT_CACHE_LOCK_TTL_SECONDS = 300
    - CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600
    - CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500
    - CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20
    - CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT = 2048
    - PACING_DELAY_VERTEX_SECONDS = 12
    - PACING_DELAY_OPENAI_SECONDS = 0
    - PACING_DELAY_MOCK_SECONDS = 0
    - REDIS_CONNECTION_TIMEOUT_SECONDS = 10
- **Vertailtavat ajot (R1, R2...):**
  - **R1:** `exe_77e2915cfeef4f7ea12e6551e66433df`
  - **R2:** `/exe_add8965fdc7342c5950678fd9745dfb6`
- **Aktiiviset Säännöt ja Asetukset (Frozen Context):**
  - **Vastuullisuus (Turvallisuus- ja Etiikkasuodatin)** (`blk_80732a33fe1947ee`) - [R1: 0P/12F] [R2: 0P/12F]
  - **Oman tiedon rajat (Episteeminen Nöyryys)** (`blk_22e3598e06414409`) - [R1: 8P/5F] [R2: 7P/6F]
  - **Harkintakyky (Kahnemanin Kaksoisprosessiteoria)** (`blk_109dab5b6b3f403a`) - [R1: 6P/0F] [R2: 6P/0F]
  - **Päättelyn rehellisyys (Kausaalinen ja Abduktiivinen Integriteetti)** (`blk_c3bc5f3eb8e74110`) - [R1: 7P/5F] [R2: 7P/5F]
  - **Väitteiden perustelu (Toulminin Argumentaatiomalli)** (`blk_440a5fef9331451b`) - [R1: 5P/9F] [R2: 5P/9F]
  - **Itsensä haastaminen (Falsifioinnin Auditointi)** (`blk_b476f89fb732448c`) - [R1: 4P/6F] [R2: 4P/6F]
  - **Syy-seuraussuhteet (Kausaalisuuden Analyysi)** (`blk_c5804a9143c34cb1`) - [R1: 8P/7F] [R2: 8P/7F]
  - **Ohjeiden noudattaminen (Arkistointistandardien Auditointi)** (`blk_fb15f8dcf23f4865`) - [R1: 0P/15F] [R2: 0P/15F]
  - **Avoimuus (Selitettävyys ja Läpinäkyvyys)** (`blk_f6e286f050c94d60`) - [R1: 1P/11F] [R2: 1P/11F]
  - **Luovuus ja syvyys (Bloomin Taksonomia)** (`blk_f921c7c0989b47e8`) - [R1: 5P/11F] [R2: 5P/11F]
  - **Prosessiomistajuus (Ylituomari)** (`blk_ff72c2d79edb4ebf`) - [R1: 6P/8F] [R2: 6P/8F]
  - **Aktiivinen ohjaus (Performatiivisuus ja Goodhartin Laki)** (`blk_53f32679aa514fcb`) - [R1: 5P/5F] [R2: 5P/5F]
  - **Luottamusarvio (XAI-Raportoija)** (`blk_6b8c766185294f7e`) - [R1: 2P/0F] [R2: 1P/1F]

## Ajojen Lähdetiedostot ja Syötteet
- **Run 1:** `exe_77e2915cfeef4f7ea12e6551e66433df` (Lähde: [data/files/executions/exe_77e2915cfeef4f7ea12e6551e66433df/execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_77e2915cfeef4f7ea12e6551e66433df/execution_trace.json))
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_77e2915cfeef4f7ea12e6551e66433df/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_77e2915cfeef4f7ea12e6551e66433df/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_77e2915cfeef4f7ea12e6551e66433df/inputs/input_reflection_text.md)
- **Run 2:** `/exe_add8965fdc7342c5950678fd9745dfb6` (Lähde: [data/files/executions//exe_add8965fdc7342c5950678fd9745dfb6/execution_trace.json](file:///C:/src/quorum/data/files/executions/exe_add8965fdc7342c5950678fd9745dfb6/execution_trace.json))
  - **Käytetyt syötetiedostot:**
    - [input_chat_log.md](file:///C:/src/quorum/data/files/executions/exe_add8965fdc7342c5950678fd9745dfb6/inputs/input_chat_log.md)
    - [input_product_text.md](file:///C:/src/quorum/data/files/executions/exe_add8965fdc7342c5950678fd9745dfb6/inputs/input_product_text.md)
    - [input_reflection_text.md](file:///C:/src/quorum/data/files/executions/exe_add8965fdc7342c5950678fd9745dfb6/inputs/input_reflection_text.md)

## Globaalit Metriikat
- **Arvioitujen ajojen määrä ($M$):** 2
- **Yhteisten arvioitujen atomien määrä ($N$):** 152
- **Havaittujen luokkien kirjo:** false, true
- **Parittainen konsistenssi (Self-Consistency):** 97.37 %
  > *Kuvaa mallin itse-konsistenssia eli kuinka todennäköisesti kaksi satunnaista ajoa päätyy samaan lopputulokseen samalla syötteellä.*
- **Fleissin Kappa ($\kappa_{Fleiss}$):** 0.9439
  > *Yleinen tieteellinen sopivuuskerroin, joka eliminoi puhtaan sattuman vaikutuksen arvioinnissa ja toimii kaikilla ajomäärillä.*
- **Cohenin Kappa ($\kappa_{Cohen}$):** 0.9439
  > *Spesifi sopivuuskerroin tasan kahden ajon vertailuun. Jos Cohenin kappa on Fleissin kappaa korkeampi, ajojen välillä on systemaattinen jakaumaero tiukkuudessa (Marginal Bias), mutta hyvä keskinäinen korrelaatio.*
- **Keskimääräinen Shannonin Entropia:** 0.0263
  > *Mittaa vastausten yleistä epävarmuutta ja hajontaa. Lähellä nollaa oleva arvo tarkoittaa erittäin stabiilia mallia.*

## Kahden viimeisimmän ajon siirtymätilat (Run 1 -> Run 2)
- **Erimielisyyttä näiden välillä:** 4 kpl
- **Contextual Override -lähtöiset erimielisyydet koko setissä:** 1 / 4
- **PASSED -> FAILED:** 3
- **FAILED -> PASSED:** 1
- **Muut siirtymät:** 0

## Epävakaimmat Testitapaukset / Prompt-säännöt (Järjestetty Entropian mukaan)
Alla on listattu kaikki säännöt, joissa ilmeni erimielisyyttä tai epävakautta eri ajokertojen välillä. Kaikkein vaihtelevimmat/epävakaimmat tapaukset (korkein entropia) ovat listan alussa.

### Atom-ID: `tda_84b7784951c84e948c131c189261f564` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77e2915cfeef4f7ea12e6551e66433df) - [TRUE]:**
  > *PARSING LOG:  1. Rule Anchor: Find limitation markers. 2. Search Scope: `Product_Text`. 3. Piped Logic: The rule requires finding a limitation anchor followed by a dismissive transition word that rationalizes away the limitation. 4. Scan Analysis: The sentence begins by acknowledging a limitation with "eivät ole vain rajoite" (are not just a constraint). 5. Validation: This is immediately followed by the dismissive transition word "vaan" (but/rather), which reframes the limitation as a positive opportunity ("uuden taloudellisen kasvun perusta"). This perfectly matches the rule's syntactic structure. 6. Final Decision: The syntactic chain is complete. CONDITION MET.*
- **Run 2 (/exe_add8965fdc7342c5950678fd9745dfb6) - [FALSE]:**
  > *Parsing Log: Step 1: Find limitation markers. | Step 2: Define search scope as sentence. | Step 3: Validate if a limitation anchor is followed by a dismissive transition word. | Step 4: Extract quote. | Step 5: Conclude with 'CONDITION NOT MET' as no limitation markers or the specified dismissive structure were found in the text.*

---

### Atom-ID: `tda_72d297df24fb45c3a85dc0b8248b9188` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77e2915cfeef4f7ea12e6551e66433df) - [FALSE]:**
  > *PARSING LOG:  1. Rule Anchor: Find a named alternative model or theory. 2. Search Scope: `Product_Text`. 3. Piped Logic: The rule requires locating the name of an alternative model or theory that is mentioned but not analyzed. 4. Scan Analysis: The document was scanned for names of alternative future-studies frameworks, think tanks, or theorists. The text exclusively discusses the evolution of Sitra's megatrends from 2017 to 2023. 5. Final Decision: No alternative models or theories are named in the text. CONDITION NOT MET.*
- **Run 2 (/exe_add8965fdc7342c5950678fd9745dfb6) - [TRUE]:**
  > *Parsing Log: Step 1: Find a named alternative model or theory. | Step 2: Define search scope as the paragraph. | Step 3: Validate that the paragraph contains exactly 0 counter-arguments or comparative data points. | Step 4: Extract the exact quote. | Step 5: Conclude with 'CONDITION MET' as the alternative of using AI for 'kustannussäästö' is mentioned without any comparative data or counter-arguments in the paragraph.*

---

### Atom-ID: `tda_b120e2c0a40840358df1e64a4b788b30` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77e2915cfeef4f7ea12e6551e66433df) - [TRUE] **[CONTEXTUAL OVERRIDE]**:**
  > *The entire document's logic is built on taking Sitra's megatrends—which are inherently probabilistic forecasts about the future—and deriving absolute, definitive strategic conclusions from them. For example, the text states 'Korjaavaan ja uusintavaan talouteen siirtyminen on ainoa tapa taata pitkän aikavälin vakaus' ('Shifting to a reparative and regenerative economy is the only way to guarantee long-term stability'). This is an absolute conclusion based on a probabilistic premise (that the trends will unfold as predicted and that this is the sole solution). No single sentence contains both the probabilistic marker and the absolute conclusion, but the pattern is systemic throughout the document, thus warranting a contextual override.  [5. VALIDATION DECISION: PASS]*
- **Run 2 (/exe_add8965fdc7342c5950678fd9745dfb6) - [FALSE]:**
  > *1. **Search**: The `Product_Text` and AI responses in `Chat_Log` were scanned for probabilistic markers (e.g., 'mahdollisesti', 'todennäköisesti', 'voi', 'saattaa'). 2. **Match**: The search did not yield any instances where a probabilistic marker was used as a premise from which a definitive, absolute conclusion was subsequently drawn. 3. **Analyze**: The text's tone is overwhelmingly declarative and certain. It presents its premises as facts and draws absolute conclusions from them. The two-part structure required by the rule—a probabilistic premise leading to an absolute conclusion—is absent. 4. **Validate**: Since the antecedent condition (the presence of a probabilistic marker used as a premise) is not found in the source text, the rule's condition cannot be met. 5. **Conclusion**: CONDITION NOT MET.  [5. VALIDATION DECISION: PASS]*

---

### Atom-ID: `tda_003f932abb9642fc8c3147b04fac95c5` (Entropia: 1.000, Konsistenssi: 0.0%)
**Arviointisääntö:** None

**Havaitut tilat ajoittain:**
- **Run 1 (exe_77e2915cfeef4f7ea12e6551e66433df) - [TRUE]:**
  > *PARSING LOG:  1. Rule Anchor: Find absolute completeness markers. 2. Search Scope: `Product_Text`. 3. Piped Logic: The rule requires finding a sentence that explicitly claims there are zero unknown variables or alternatives remaining. 4. Scan Analysis: The sentence contains the phrase "ainoa tapa" ('the only way'). 5. Validation: This phrase explicitly excludes all other alternatives, thereby making a claim of absolute completeness regarding the solution for achieving long-term stability. 6. Final Decision: The syntactic condition is met. CONDITION MET.*
- **Run 2 (/exe_add8965fdc7342c5950678fd9745dfb6) - [FALSE]:**
  > *Parsing Log: Step 1: Find absolute completeness markers. | Step 2: Define search scope as sentence. | Step 3: Validate if the sentence explicitly claims there are zero unknown variables. | Step 4: Extract quote. | Step 5: Conclude with 'CONDITION NOT MET' as no sentence makes an explicit claim of absolute completeness; phrases like 'kolme keskeistä' imply selection, not exhaustive listing.*

---

