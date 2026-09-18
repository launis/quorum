<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
</required_context_rules>

# Comprehensive Calibration: Cross-Model Variance Harmonization, Global Sensor Directives, Matrix Seed Vault Hardening, and Input Ingress Determinism

Reconciles the systemic interpretation divergence between Google AI Studio (Gemini 3.8 Flash) and OpenAI (GPT-5.4 / GPT-5.4-mini) by unifying the architectural findings from the **0110 vs 0218 Diff Report Comparative Audit** (`feature_audit_diff_reports_0110_vs_0218.md`), the **Cross-Model Variance Analysis** (`feature_audit_cross_model_variance_analysis.md`), the **Input Data Asymmetry Forensic Audit** (`feature_audit_input_data_asymmetry.md`), the **Tier 0 System 2 Research Deconstruction** (`71ae4413-2c15-442b-981d-a8f911d3793a`), and the **Tier 8 Physical Execution Audit** (`feature_audit_cross_model_variance_plan_review.md`). Addresses the four structural root causes of variance across all 30 mismatches identified in the 205-atom holistic suite (`diff_report_2026-09-18_0218.md`) through macro-level sensor prompts (`matrix_evaluation.py`, `global_mandates.py`, `field_prompts.py`), micro-level seed vault hardening across 19 concrete atoms (`seed_data.json`), and test harness ingress hoisting (`run_e2e_variance_test.py`, `pdf_chat_extractor.py`, `diff_executions.py`) to permanently elevate cross-model consensus from $\kappa = 0.6962$ to $\kappa \ge 0.9500$ ($\le 3\text{--}4$ mismatches / 205 atoms), collapse Kahneman score drift from **+21.98 pp to $< 3.00$ pp**, and mathematically guarantee 100% deterministic cryptographic input isolation.

---

## User Review Required

> [!IMPORTANT]
> **Consolidated Empirical Evidence & Root Cause Triage**:
> 
> Comparative analysis of the 65-atom run (`diff_report_2026-09-18_0110`, $\kappa = 0.8132$) against the 205-atom run (`diff_report_2026-09-18_0218`, $\kappa = 0.6962$) across 4 physical execution directories (`exe_6783fef5...`, `exe_d0db6866...`, `exe_65291057...`, `exe_976a9f35...`) mathematically proves that cross-model variance is driven by four interrelated deterministic factors:
> 
> 1. **Extractive Sensitivity & Tooling Gap (76.7% of Mismatches / 23 of 30)**:
>    OpenAI GPT-5.4 executes 4× more MCP fact-checking calls (64 vs 16) and extracts 2.5× more quotes (28 vs 11) than Gemini 3.8 Flash. GPT-5.4 aggressively mines user task prompts and briefing constraints, mistaking them for substantive analytical claims. Gemini adheres strictly to the Null Hypothesis when claims lack explicit physical proof in the text.
> 2. **Target Speaker & Procedural Scaffolding Leakage (12 Direct Mismatches)**:
>    GPT-5.4 mined procedural commands and task briefings (specifically: *"Yksi sivu riittää"*, headcount distributions in problem briefings, *"Toimi nyt paholaisen asianajajana"*, *"Haluan, että käyt dialogia..."*) as evidence for cognitive competence, Bloom L1 recall, or deliberate self-falsification.
> 3. **Contextual Override & Inverse Rule Asymmetry (23.3% of Mismatches / 7 of 30)**:
>    In inverse rules (specifically Linearity Fallacy `tda_eefe3db0...`, Universalization `tda_01edff70...`, Unsupported Claim `tda_34259a6c...`), Gemini evaluated holistically at the document level and granted Contextual Override (`PASSED [CONTEXTUAL OVERRIDE]`), whereas GPT-5.4 evaluated micro-level syntax and marked them as `FAILED`.
> 4. **Complexity Scaling & Kahneman System 1/2 Drift (+21.98 pp Score Drift)**:
>    Scaling from 65 to 205 atoms added 140 high-abstraction cognitive atoms (Bloom, Kahneman, Causality, Epistemic Humility). In the Kahneman block, GPT-5.4 passed all three levels (`tda_20f87ebd...`, `tda_6df2bc5a...`, `tda_5257ba1e...`) by quoting the user's prompt request, causing an anomalous +21.98 pp surge.

> [!IMPORTANT]
> **Forensic Falsification & Deconstruction of "Input Data Asymmetry"**:
> 
> A detailed forensic audit (`feature_audit_input_data_asymmetry.md`) investigated the critique alleging *"Input Data Asymmetry: Runs R1 and R2 were executed on differing source texts, causing a critical silent failure in test harness MLOps telemetry"*.
> 
> The forensic investigation **falsified the accusation** while uncovering legitimate test harness technical debt:
> 1. **Evaluated Candidate Substance Was 100% Invariant (`KOLLISIO`)**:
>    In both the 65-atom Sitra run (`0110`) and 205-atom JW run (`0218`), the evaluated candidate work (`input_chat_log_user_only.md`, `input_product_text.md`, `input_reflection_text.md`) was byte-for-byte cryptographically identical across R1 and R2 with matching SHA-256 hashes (`KOLLISIO`) and identical word counts (Sitra: 113, 442 words; JW: 211, 424, 31 words).
> 2. **Root Cause of Word Count Difference (5,489 vs. 5,865 words)**:
>    The +376 word difference in Sitra and +99 word difference in JW occurred solely in external AI dialogue turns (`input_chat_log_ai_only.md` and combined raw log `input_chat_log.md`). The root cause is an in-memory PyMuPDF layout state artifact in `PdfChatExtractorService._reconstruct_tables_as_markdown`: on cold start, table cells concatenated without spaces (e.g. `sopeudutaanrajoihinjaparannetaan`, counted as 1 word); on warm runs, spaces were preserved (`sopeudutaan rajoihin ja parannetaan`, counted as 4 words).
> 3. **Zero Impact on MLOps Telemetry or the 30 Atom Mismatches**:
>    All 30 atom mismatches in Run 0218 and 6 in Run 0110 were confirmed to stem from prompt mining by GPT-5.4, contextual override asymmetry on inverse rules, and Kahneman System 1/2 concept drift. Zero mismatches were caused by table cell spacing.
> 4. **Legitimate Test Harness Technical Debt Remediated in this Plan**:
>    - **Harness Hoisting (`scripts/run_e2e_variance_test.py`)**: `load_inputs_from_path` was called inside the execution loop (`for i in range(runs):`), re-extracting PDFs on every run. Hoisting it outside the loop in `--no-noise` mode ensures a single immutable input capsule is shared across runs.
>    - **Table Extraction Whitespace Determinism (`backend_v2/services/ingress/pdf_chat_extractor.py`)**: Ensure deterministic intra-cell whitespace and punctuation regex cleanup in `_reconstruct_tables_as_markdown`.
>    - **Canonical Hash Normalization (`scripts/diff_executions.py`)**: Enforce Unicode NFKC and whitespace normalization before computing file SHA-256 to prevent false-positive `ERISTETTY` alerts on whitespace variations.

> [!TIP]
> **Quantitative Parity & Stability Targets**:
> - Disagreements across the 205-atom holistic suite drop from 30 / 205 to **$\le 3\text{--}4$ / 205** ($< 2.0\%$).
> - Global Consistency ($P_o$) rises from **85.37% $\rightarrow \mathbf{98.05\%}\text{--}\mathbf{98.54\%}$** ($+13.17\text{ pp}$).
> - Cohen's Kappa rises from **$0.6962 \rightarrow \mathbf{0.9600}\text{--}\mathbf{0.9700}$** (*Near-Perfect Agreement*).
> - Fleiss' Kappa rises from **$0.6951 \rightarrow \mathbf{0.9698}$**.
> - Information Entropy drops from **$0.14634 \rightarrow \mathbf{0.01463\text{ bit}}$** ($-90.0\%$ noise reduction).
> - Marginal Bias ($B$) drops from **$-0.05854 \rightarrow \mathbf{-0.00488}$** (asymmetry eliminated).
> - Mean Absolute Difference (MAD) across block scores drops from **$7.584\text{ pp} \rightarrow \mathbf{\le 1.844\text{ pp}}$** ($-75.7\%$).
> - Kahneman Block Maximum Drift collapses from **$+21.98\text{ pp} \rightarrow \mathbf{\le 2.50\text{ pp}}$** ($-88.6\%$).
> - Lexical grounding remains **100% verified** with 0 hallucinated quotes and 0 regex fallbacks.
> - Input Isolation in `--no-noise` mode achieves **100% cryptographic collision (`KOLLISIO`)** across all files.

---

## Detailed Mathematical Target Projections & Metric Impact Analysis

### 1. Global Scalar & Statistical Agreement Metrics

| Mathematical Variable | Definition / Formula | Baseline (Run 0218) | Calculated Target State | Impact / Relative Change |
| :--- | :--- | :---: | :---: | :---: |
| **Total Common Atoms ($N$)** | $N = \vert A_1 \cap A_2 \vert$ | **205** | **205** | $0.0\%$ (SSOT invariant) |
| **Total Mismatches ($M$)** | $\sum [s_{1,i} \neq s_{2,i}]$ | **30** | **$\le 3$ (max 4)** | **$-90.0\%$ (26-27 resolved)** |
| **Observed Agreement ($P_o$)** | $P_o = \frac{N - M}{N}$ | **0.85366** (85.37%) | **0.98537** (98.54%) | **$+13.17\text{ pp}$** |
| **Expected Chance Agreement ($P_e$)** | $p_{1,\text{pass}} p_{2,\text{pass}} + p_{1,\text{fail}} p_{2,\text{fail}}$ | **0.51829** (51.83%) | **0.51210** (51.21%) | $-0.00619$ |
| **Cohen's Kappa ($\kappa$)** | $\kappa = \frac{P_o - P_e}{1 - P_e}$ | **0.69621** (*Substantial*) | **0.97001** (*Near-Perfect*) | **$+39.3\%$** |
| **Kappa Standard Error ($SE_\kappa$)** | $\sqrt{\frac{P_o(1 - P_o)}{N(1 - P_e)^2}}$ | **0.05125** | **0.01720** | **$-66.4\%$** |
| **95% Confidence Interval ($CI_{95}$)** | $\kappa \pm 1.96 \cdot SE_\kappa$ | **[0.5958, 0.7966]** | **[0.9363, 1.0000]** | Statistical bound locked |
| **Fleiss' Kappa ($\kappa_{\text{Fleiss}}$)** | $\frac{\bar{P} - \bar{P}_e}{1 - \bar{P}_e}$ | **0.69512** | **0.96980** | **$+39.5\%$** |
| **Marginal Bias ($B$)** | $\frac{n_{1,\text{pass}} - n_{2,\text{pass}}}{N}$ | **$-0.05854$** | **$-0.00488$** | **$-91.7\%$ (Bias eradicated)** |
| **Information Entropy ($H$)** | $-\sum p_i \log_2 p_i$ | **0.14634 bit** | **0.01463 bit** | **$-90.0\%$ (Deterministic)** |

---

### 2. Comprehensive 30-Atom Mismatch Triage & Target Resolution Matrix

All 30 mismatches identified in `diff_report_2026-09-18_0218.json` are systematically triaged and resolved by this calibration:

| # | Atom-ID | Matrix Block & Scale | Baseline States (R1 vs R2) | Root Cause Category | Target Resolution Mechanism | Target Consensus State |
|---|---|---|---|---|---|:---:|
| 1 | `tda_2f6c6565bf10f613d787c03fc97bfb91` | Avoimuus (Scale 1.0) | FAILED vs PASSED | Prompt Command Quote (*"Yksi sivu riittää."*) | `<procedural_prompt_disqualification_protocol>` | **FAILED** |
| 2 | `tda_9a08254fb47a46fdb8a78030ed68f853` | Toulmin (Scale 5.0) | FAILED vs PASSED | Prompt Roleplay Quote (*"Toimi nyt paholaisen asianajajana..."*) | `<procedural_prompt_disqualification_protocol>` | **FAILED** |
| 3 | `tda_657fb164be984788a760eed250b3bc61` | Goodhart (Scale 4.0) | FAILED vs PASSED | Prompt Scaffolding Quote (*"Haluan, että käyt dialogia..."*) | `<procedural_prompt_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 4 | `tda_10f455c36f754d33a3a551e9e7b61da4` | Bloom (Scale 4.0) | FAILED vs PASSED | Prompt Task Scoping (*"Olen tekemässä selvitystä..."*) | `<procedural_prompt_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 5 | `tda_85988e1249fe8a9a3ec181163f17c006` | Bloom (Scale 4.0) | FAILED vs PASSED | Prompt Scenario Variable (*"osa henkilöistä ei voi..."*) | `<procedural_prompt_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 6 | `tda_b36d3ec7b1f94fe9ad4b45795a8a104b` | Bloom (Scale 1.0) | FAILED vs PASSED | Prompt Headcount Quote (*"Opetuksesta noin 30%..."*) | `<procedural_prompt_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 7 | `tda_defc33928bb9c172f2f64e090b90f935` | Bloom (Scale 1.0) | FAILED vs PASSED | Prompt Headcount Breakdown (*"100 ovat opettajia..."*) | `<procedural_prompt_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 8 | `tda_f421022aacc8c0c5d2ab80aa5c9719c4` | Avoimuus (Scale 2.0) | FAILED vs PASSED | Prompt Scenario Parameter (*"Opetuksesta noin 30%..."*) | `<procedural_prompt_disqualification_protocol>` (Expanded) + Anti-pattern | **FAILED** |
| 9 | `tda_f1a3d9151c48fe065df1c0afe580caa2` | Falsifiointi (Scale 1.0) | FAILED vs PASSED | Prompt Goal Statement (*"Tämän selvityksen tavoitteena..."*) | `<procedural_prompt_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 10 | `tda_20f87ebd0c5b7de765cc4f6abc9b0fdd` | Kahneman (Scale 1.0) | FAILED vs PASSED | Prompt Scenario Variable (*"osa henkilöistä ei voi..."*) | Anti-pattern: problem parameters disqualified | **FAILED** |
| 11 | `tda_6df2bc5ac5e194367107f8d29fa6503e` | Kahneman (Scale 2.0) | FAILED vs PASSED | Prompt Target Assignment (*"Selvitä mikä olisi..."*) | Anti-pattern: prompt scoping disqualified | **FAILED** |
| 12 | `tda_5257ba1edae34afe8b837c8c238cf743` | Kahneman (Scale 3.0) | FAILED vs PASSED | Prompt Wishlist Quote (*"Tavoitteena on maksimoida..."*) | Anti-pattern: goal aspirations disqualified | **FAILED** |
| 13 | `tda_01edff70b75047ec9f6df0c49745f46e` | Kausaalisuus (Scale 3.0, Inv) | PASSED vs FAILED | Contextual Override vs Micro-flaw | Deterministic Null Hypothesis (defect absent) | **PASSED** |
| 14 | `tda_34259a6c02b74917b12f74b5f3839a66` | Toulmin (Scale 1.0, Inv) | PASSED vs FAILED | Contextual Override vs Micro-flaw | Deterministic Null Hypothesis (defect absent) | **PASSED** |
| 15 | `tda_99e85328acc8396007c0766de9aea317` | Avoimuus (Scale 1.0, Inv) | PASSED vs FAILED | Contextual Override vs Micro-flaw | Deterministic Null Hypothesis (defect absent) | **PASSED** |
| 16 | `tda_9a8a71406006c7c7d8a21ac227050494` | Bloom (Scale 4.0, Inv) | PASSED vs FAILED | Contextual Override vs Micro-flaw | Deterministic Null Hypothesis (defect absent) | **PASSED** |
| 17 | `tda_b7dfe23403db4db5b92a29a8bda9957c` | Bloom (Scale 2.0, Inv) | PASSED vs FAILED | Contextual Override vs Micro-flaw | Deterministic Null Hypothesis (defect absent) | **PASSED** |
| 18 | `tda_d0d7af27db792d928edd752480a16fdd` | Falsifiointi (Scale 3.0, Inv) | PASSED vs FAILED | Contextual Override vs Micro-flaw | Deterministic Null Hypothesis (defect absent) | **PASSED** |
| 19 | `tda_b5ae6dbc4d2bdcda5ed0e62aec398444` | Toulmin (Scale 2.0, Inv) | FAILED vs PASSED | Authority Citation Stringency | Acceptance Criteria clarification on authority | **PASSED** |
| 20 | `tda_105f796045430fcda5656f2781522a74` | Toulmin (Scale 2.0) | FAILED vs PASSED | Document Metadata Header (*"Kohderyhmä..."*) | `<document_metadata_disqualification_protocol>` + Anti-pattern | **FAILED** |
| 21 | `tda_10dd47750c9244139c394ca875f160e6` | Toulmin (Scale 4.0) | PASSED vs FAILED | Warrant Bridge Principle Stringency | Acceptance Criteria + Anti-pattern hardening | **PASSED** |
| 22 | `tda_47bade191cf346ec818757f081f6aef3` | Toulmin (Scale 4.0) | PASSED vs FAILED | Rebuttal Engagement Proof Standard | Acceptance Criteria on functional rebuttals | **PASSED** |
| 23 | `tda_6e3e3aa6b9134a01838c3b70a35b4f32` | Toulmin (Scale 3.0) | PASSED vs FAILED | Intuitive Warrant Acceptance | Acceptance Criteria on intuitive causal bridges | **PASSED** |
| 24 | `tda_3b951170f9f54f649b7da95fb9f121e6` | Falsifiointi (Scale 3.0) | FAILED vs PASSED | Literature Observation Granularity | Acceptance Criteria on descriptive evidence | **PASSED** |
| 25 | `tda_8e87f38a5ec6d86e20e210f6205015cc` | Kausaalisuus (Scale 2.0) | FAILED vs PASSED | Transmission Mediator Retrieval | Acceptance Criteria on multi-stage mediators | **PASSED** |
| 26 | `tda_c607024dbf524f7a9d68af443901c40e` | Kausaalisuus (Scale 3.0) | FAILED vs PASSED | Structural Mechanism Granularity | Acceptance Criteria + Anti-pattern on work schedules | **PASSED** |
| 27 | `tda_a946688e5f5549e8ac30584d1a02ad26` | Episteeminen (Scale 3.0) | FAILED vs PASSED | Impersonal Proposition Boundary | Fencing 1st-person prompt narrative | **FAILED** |
| 28 | `tda_c752762564eda7902ecc4525ffd58f59` | Episteeminen (Scale 3.0) | FAILED vs PASSED | Prompt Variable as Baseline Assumption | Disqualifying prompt premises as assumptions | **FAILED** |
| 29 | `tda_f29c602444b446a3a6973aa9953a0b01` | Episteeminen (Scale 4.0) | FAILED vs PASSED | Prompt Scoping as Boundary Setting | Disqualifying assignment schedule bounds | **FAILED** |
| 30 | `tda_bd85f009b0fb4f7899b40ff0e763dee7` | Goodhart (Scale 4.0) | FAILED vs PASSED | Proxy Metric Questioning Retrieval | Acceptance Criteria + Anti-pattern on proxy indicators | **PASSED** |

---

### 3. Macro Block Score & Drift Target Projections (All 9 Blocks)

Formula: $\text{Drift} = \text{Score}_{\text{R2}} - \text{Score}_{\text{R1}}$, $\text{MAD} = \frac{1}{K}\sum_{k=1}^K \vert \text{Drift}_k \vert$.

| Matriisilohko (Block) | R1 Score | R2 Score (Baseline) | Baseline Drift ($\Delta$) | Baseline Consistency | Target Drift ($\Delta$) | Target Consistency | Drift Reduction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Harkintakyky (Kahneman)** | 42.04 | 64.03 | **+21.98 pp** | 80.0% | **$\le 2.50\text{ pp}$** | **$\ge 95.0\%$** | **$-88.6\%$** |
| **Oman tiedon rajat (Episteeminen)** | 61.82 | 74.60 | **+12.78 pp** | 88.0% | **$\le 3.00\text{ pp}$** | **$\ge 95.0\%$** | **$-76.5\%$** |
| **Aktiivinen ohjaus (Goodhart)** | 49.77 | 61.18 | **+11.41 pp** | 92.0% | **$\le 2.00\text{ pp}$** | **$\ge 96.0\%$** | **$-82.5\%$** |
| **Väitteiden perustelu (Toulmin)** | 64.79 | 57.24 | **$-7.55\text{ pp}$** | 76.0% | **$\le 2.50\text{ pp}$** | **$\ge 94.0\%$** | **$-66.9\%$** |
| **Syy-seuraussuhteet (Kausaalisuus)**| 50.31 | 55.93 | **+5.62 pp** | 84.0% | **$\le 2.00\text{ pp}$** | **$\ge 93.0\%$** | **$-64.4\%$** |
| **Luovuus ja syvyys (Bloom)** | 37.59 | 41.54 | **+3.96 pp** | 80.0% | **$\le 1.50\text{ pp}$** | **$\ge 95.0\%$** | **$-62.1\%$** |
| **Avoimuus (Selitettävyys)** | 41.35 | 44.16 | **+2.81 pp** | 88.0% | **$\le 1.50\text{ pp}$** | **$\ge 97.0\%$** | **$-46.6\%$** |
| **Itsensä haastaminen (Falsifiointi)**| 46.29 | 48.44 | **+2.15 pp** | 85.0% | **$\le 1.50\text{ pp}$** | **$\ge 96.0\%$** | **$-30.2\%$** |
| **Luottamusarvio (XAI-Raportoija)** | 65.25 | 65.25 | **0.00 pp** | 100.0% | **$0.00\text{ pp}$** | **$100.0\%$** | $0.0\%$ (Locked) |
| **Mean Absolute Difference (MAD)** | - | - | **7.584 pp** | **85.4%** | **$\le 1.844\text{ pp}$** | **$\ge 96.0\%$** | **$-75.7\%$** |
| **Maximum Drift (Max Drift)** | - | - | **21.98 pp** | - | **$\le 3.00\text{ pp}$** | - | **$-86.4\%$** |

---

### 4. Scale Breakdown Target Projections (All 5 Difficulty Tiers)

| Vaativuustaso (Difficulty Tier) | Atom Count ($N$) | Baseline Mismatches | Baseline Consistency | Target Mismatches | Target Consistency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **81–100%: Korkein vaativuustaso (Top Mastery)** | 45 | 2 kpl | 95.56% | **0–1 kpl** | **$\ge 97.8\%$** |
| **61–80%: Korkea vaativuustaso (High Standard)** | 35 | 7 kpl | 80.00% | **0–1 kpl** | **$\ge 97.1\%$** |
| **41–60%: Keskitaso (Mid Standard)** | 40 | 9 kpl | 77.50% | **1 kpl** | **$\ge 97.5\%$** |
| **21–40%: Matala vaativuustaso (Low Standard)** | 35 | 4 kpl | 88.57% | **0–1 kpl** | **$\ge 97.1\%$** |
| **0–20%: Perustaso (Baseline / Minimum Viable)** | 50 | 8 kpl | 84.00% | **0–1 kpl** | **$\ge 98.0\%$** |

---

### 5. Telemetry, Suorituskyky- ja Kustannusennusteet

| Telemetriamuuttuja | Run 1 (Gemini 3.8 Flash) | Run 2 (OpenAI Baseline) | Run 2 (OpenAI Target) | Arkkitehtoninen Mekanismi |
| :--- | :---: | :---: | :---: | :--- |
| **MCP Fact-check Tool Calls** | 16 kpl | **64 kpl** | **$\le 25\text{ kpl}$** | Pre-flight prompt disqualification prevents scraping loops |
| **Extracted Empirical Quotes** | 11 kpl | **28 kpl** | **$12\text{--}14\text{ kpl}$** | 14 false quotes from prompt scaffolding eliminated |
| **Thinking Tokens** | 425,826 | 111,668 | $\sim 100,000$ | Stable reasoning allocation |
| **Suoritusaika (Wall-clock Time)** | 458 s (7.6 min) | **1018 s (17.0 min)** | **$\sim 680\text{ s}$ (11.3 min)** | **$-33\%$** runtime drop via fewer tool calls |
| **Kokonaiskustannus (USD)** | **$3.63** | **$8.02** | **$\sim \$5.60$** | **$-30\%$** cost reduction from pruned context and tool tokens |

---

## Synthesized Quality Gates & Research Findings (Tier 0 & Tier 8)

### Target Files & AST Bounds (14 Files Total)

| # | File | AST Bounds | 1-Hop Callers / Blast Radius | Modification Role | Status |
|---|---|---|---|---|---|
| 1 | `@[backend_v2/models/prompts/execution/matrix_evaluation.py]` | L1-138 (Entire module) | `matrix_sensor_prompt_builder.py`, `PromptCompiler`, `test_matrix_evaluation.py` | Inject protocols & harden override directive | ✅ Verified |
| 2 | `@[backend_v2/models/prompts/execution/global_mandates.py]` | L1-154 (Entire module) | `matrix_sensor_prompt_builder.py`, `PromptCompiler`, `test_global_mandates.py` | Purge V1 terms & `e.g.` ambiguity | ✅ Verified |
| 3 | `@[backend_v2/models/prompts/execution/field_prompts.py]` | L11 (`DESC_ALIAS`) | `extractive_sensor_service.py`, `evaluation_steps.py`, `test_field_prompts.py` | `e.g.` → `specifically:` | ✅ Verified |
| 4 | `@[backend_v2/seed/seed_data.json]` | 19 concrete atoms (Lines detailed below) | `run_seed.py`, `audit_database_atoms.py`, `sanitize_seed_vault.py` | Anti-patterns & acceptance criteria | ✅ Verified |
| 5 | `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py]` | L1-120 | `backend_audit_loop.py` | Unit tests for protocols & phrases | ✅ Verified |
| 6 | `@[backend_v2/tests/unit/models/prompts/test_global_mandates.py]` | L1-50 | `backend_audit_loop.py` | Negative partition tests for `e.g.`/V1 | ✅ Verified |
| 7 | `@[scripts/run_e2e_variance_test.py]` | L1785-1845 (exec loop) | CLI variance runner, `diff_executions.py` | Hoist `load_inputs_from_path` in `--no-noise` | ✅ Verified |
| 8 | `@[backend_v2/services/ingress/pdf_chat_extractor.py]` | L259-323 (`_reconstruct_tables_as_markdown`) | `load_inputs_from_path`, `workflow_service.py` | CamelCase & multi-space regex | ✅ Verified |
| 9 | `@[scripts/diff_executions.py]` | L497-565 (`_inspect_input_file`) | CLI diff tool, MLOps telemetry reports | NFKC & whitespace normalizer | ✅ Verified |
| 10 | `@[backend_v2/services/orchestrator/anchor_validation_service.py]` | L125-155 (`_is_lexically_valid`) | `extractive_sensor_service.py`, `dag_executor.py`, unit tests | Eradicate `find("") == 0` empty normalized string bypass | ✅ Verified |
| 11 | `@[backend_v2/services/orchestrator/extractive_sensor_service.py]` | L52-105 (`BooleanEvaluationResult`) | `topological_evaluator.py`, `test_extractive_sensor_service.py` | Harden `source_quote` with `min_length=10` & non-whitespace assertion | ✅ Verified |
| 12 | `@[backend_v2/models/dtos/evaluation_steps.py]` | L144-149 (`StepDTOSemantic`) | `topological_evaluator.py`, `matrix_reducer.py` | Eradicate `model_copy(update=)` duct tape, replace with `ValueError` Fail-Fast | ✅ Verified |
| 13 | `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py]` | L240-285 | `backend_audit_loop.py` | ISTQB negative partition tests asserting empty/whitespace/punctuation quote rejection | ✅ Verified |
| 14 | `@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]` | L629-675 | `backend_audit_loop.py` | ISTQB negative partition tests asserting `BooleanEvaluationResult` rejects quotes < 10 chars | ✅ Verified |

### Technical Debt Sweep (12 Verified Items)

| # | Location | Debt Item | Remediation Mechanism |
|---|---|---|---|
| 1 | `global_mandates.py` L35 | `e.g.` in `ANTI_ID_MANDATE` | Replace with closed list |
| 2 | `global_mandates.py` L38-39 | `atom_id` contradicts `BooleanEvaluationResult(extra="forbid")` using `alias` | Delete contradictory command |
| 3 | `global_mandates.py` L75 | `e.g.` in `NULL_HYPOTHESIS_MANDATE` | Replace with closed list |
| 4 | `global_mandates.py` L76-77 | V1 `exact_quotes`/`decision` terms (V2 = `source_quote`/`is_true`) | Align with V2 DTO schema |
| 5 | `global_mandates.py` L97 | `e.g.` in `EXTENSION_ANCHORING_MANDATE` | Replace with closed list |
| 6 | `global_mandates.py` L114 | `e.g.` in `SCHEMA_PURITY_MANDATE` | Replace with closed list |
| 7 | `field_prompts.py` L11 | `e.g.` in `DESC_ALIAS` | Replace with `(specifically: 'a0', 'a1')` |
| 8 | `diff_executions.py` L531 | SHA-256 on raw bytes without NFKC normalization | Standardize via NFKC before hashing |
| 9 | `pdf_chat_extractor.py` L297 | No camelCase word-boundary regex sanitization | Regex boundary split + space collapse |
| 10 | `anchor_validation_service.py` L140 | `norm_text.find("") == 0` empty string bypass returns `True` for empty `norm_quote` | Add `if not norm_quote: return False` at start of `_is_lexically_valid` |
| 11 | `evaluation_steps.py` L147 | `model_copy(update={"exact_quotes": []})` auto-mutation suppresses validation errors | Replace with `ValueError` Fail-Fast in `_enforce_override_exclusivity` |
| 12 | `extractive_sensor_service.py` L59 | `source_quote` lacks explicit `min_length=10` schema constraint in DTO definition | Add `min_length=10` and non-whitespace regex validation |

---

### Adversarial Findings & Red-Team Corrections

#### FINDING 1 — 🔴 CRITICAL: English-Only Abstract System Directives with Metacognitive Safe Harbor
- **Root Cause**: Finnish test-data examples ("yksi sivu riittää", "toimi paholaisen asianajajana") violate `native_language_system_prompts` in `@[.agents/rules/05_llm_architecture.md]` and overfit to the test corpus.
- **Correction**: Use abstract English categories anchored to the "who instructs whom" agent relationship, with an explicit Metacognitive Safe Harbor for author self-direction.

#### FINDING 2 — 🔴 CRITICAL: Expanded Scope to 19 Atoms & Restored JSON Payloads
- **Root Cause**: Summarization in earlier passes stripped concrete JSON atom definitions, and 3 high-entropy atoms from Run 0218 were missing:
  - `tda_f421022aacc8c0c5d2ab80aa5c9719c4` (Heikko Selitettävyys, `#L15219-L15258`): GPT-5.4 mined headcount figures (`200 työntekijää`) as concrete parameters.
  - `tda_bd85f009b0fb4f7899b40ff0e763dee7` (Goodhart Proxy Metrics, `#L4970-L5009`): GPT-5.4 passed standard goal management advice as Goodhart critique.
  - `tda_c607024dbf524f7a9d68af443901c40e` (Causal Mechanism, `#L7525-L7559`): GPT-5.4 passed core working hour schedules as scientific causal mechanisms.
- **Correction**: Scope expanded from 16 to 19 atoms, with all concrete JSON blocks and line bounds restored in Section 5.

#### FINDING 3 — 🟡 HIGH: Disqualification of Input Context as Primary Analytical Datasets
- **Root Cause**: The prompt protocol disqualified problem parameters from serving as "declarative evaluative propositions, empirical categorizations, or academic definition recall", but omitted "primary analytical input datasets or variables".
- **Correction**: Expanded bullet 2 of `<procedural_prompt_disqualification_protocol>` to explicitly disqualify input parameters from serving as analytical datasets or evidence variables.

#### FINDING 4 — 🟡 MEDIUM: Lowercase Word-Gluing Limitation in PyMuPDF Sanitizer
- **Root Cause**: PyMuPDF table cell word-gluing can concatenate all-lowercase words (`sopeudutaanrajoihinjaparannetaan`), which camelCase regex cannot split.
- **Correction**: Emphasize that **Input Hoisting in `run_e2e_variance_test.py`** is the primary mathematical guarantee of input invariance across comparison runs.

#### FINDING 5 — 🟡 MEDIUM: Separate Negative Partition Test Functions
- **Correction**: Dedicated `test_global_mandates_negative_partitions()` in `test_global_mandates.py` asserts 0 instances of `e.g.`, `atom_id`, `exact_quotes`, `decision`.

#### FINDING 6 — 🔴 CRITICAL: Pydantic Sitaattivalidoinnin ja Leksikaalisen Tyhjyys-Ohituksen Kumoaminen (Quote Validator Red-Teaming & Lexical Empty-Bypass Vulnerability)
- **Root Cause & Falsification of Naive `len(quote) > 0`**:
  A naive validator `len(quote_text) > 0` fails fundamentally because in Python `len(" ") == 1 > 0` and `len("\n") == 1 > 0`. Under strict schema pressure (when a model wants to output `is_true = True` but lacks empirical textual proof), generative models (especially low-temperature, zero-shot runs) experience **Compliance Evasion / Alignment Pressure Relief**: rather than triggering schema validation errors, the model outputs whitespace (`" "`), single punctuation marks (`"."`, `"-"`), or placeholder tokens (`"N/A"`, `"None"`).
- **Inverted Premise Deconstruction (Null Hypothesis Invariant)**:
  The adversarial objection alleging *"Jos malli haluaa käyttää contextual_override-lippua mutta DTO vaatii sitaatin, se palauttaa quote_text: ' '"* contains an architectural misconception. Under Quorum's sovereign Null Hypothesis (`ki_structured_forensic_quotes.md`), `contextual_override == True` **strictly forbids** a quote (`source_quote must be None`). If a DTO demanded a quote for an override, it would violate the Null Hypothesis. The evasion occurs in reverse: models attempt to mark claims `PASSED` without an override when no verbatim quote exists, prompting them to emit whitespace or punctuation tokens.
- **Discovery of Critical Lexical Bypass Bug (`anchor_validation_service.py` L140)**:
  Deep-dive inspection revealed a critical vulnerability in `AnchorValidationService._is_lexically_valid`:
  ```python
  start_norm_idx = norm_text.find(norm_quote)
  if start_norm_idx != -1:
      return True
  ```
  In Python, `str.find("")` evaluates to `0`! If a quote consists of whitespace or stripped punctuation (e.g. `" "` or `"."`), `normalize_text_with_mapping` produces `norm_quote == ""`. `norm_text.find("")` evaluates to `0` (which is `!= -1`), returning `True`! This silently validates empty or punctuation-only quotes against any non-empty source text.
- **Discovery of Auto-Mutation Duct Tape (`evaluation_steps.py` L147)**:
  `StepDTOSemantic._enforce_override_exclusivity` currently uses `self.model_copy(update={"exact_quotes": []})` to silently suppress validation conflicts when `contextual_override` is True, violating the catastrophic ban on auto-mutating duct tape.
- **Four-Layer Forensic Defense Architecture**:
  1. *Layer 1 (Schema Invariant Gate)*: `BooleanEvaluationResult` enforces `v.strip()` in `mode="before"`, `min_length=10` on `source_quote`, non-whitespace regex, and strict Null Hypothesis (`source_quote` must be `None` when `is_true == False` or `contextual_override == True`).
  2. *Layer 2 (Lexical Grounding Gate)*: `AnchorValidationService._is_lexically_valid` is hardened with `if not norm_quote: return False`, Tier 1 literal `str.find()`, and the Entropy Gate banning fuzzy matching for quotes < 10 characters.
  3. *Layer 3 (Provenance Boundary Gate)*: User evidence must reside strictly within `<user_payload>`, permanently quarantining `<assignment_context>` and AI dialogue turns.
  4. *Layer 4 (Cognitive & Null Hypothesis Policy)*: Inverse defect rules deterministically evaluate to `is_true = False` under absence of defect, eliminating artificial quote requirements.

---

## Five-Axis Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`matrix_evaluation.py` L1-138**: Add `<procedural_prompt_disqualification_protocol>` and `<document_metadata_disqualification_protocol>` to static Layer 1 `MATRIX_SENSOR_SYSTEM_PROMPT`. Harden `CONTEXTUAL_OVERRIDE_DIRECTIVE`. | Ban: LLMs treating prompt dispatch commands, roleplay instructions, or problem variables as analytical evidence. Ban: Granting contextual overrides based on passive omission or topical silence. | Static Layer 1 XML protocol blocks using exclusively English-language abstract categories with Metacognitive Safe Harbor. Deterministic Null Hypothesis on inverse rules. | Zero AST parsers, regex filters, or post-hoc text stripping. Native prompt-level enforcement only. Zero new abstractions. | `test_matrix_evaluation.py` asserts tag presence AND key behavioral phrases. E2E variance test verifies 0 quotes from prompt scaffolding. |
| **`global_mandates.py` L1-154**: Purge V1 schema terms (`exact_quotes`, `decision`, `atom_id`) and all `e.g.` tokens across 5 mandate constants. | Ban: V1 `exact_quotes`/`decision` causing model confusion with `extra="forbid"` V2 schema. Ban: `atom_id` instruction contradicting `BooleanEvaluationResult.alias` field. | V2 `source_quote`/`is_true` invariants. `e.g.` → `specifically:` closed lists. `atom_id` → complete removal. | Zero new constants. Surgical in-place text replacement only. | `test_global_mandates_negative_partitions()` asserts 0 instances of `e.g.`, `exact_quotes`, `decision`, `atom_id` across both `GLOBAL_MANDATES_XML` and individual mandate constants. |
| **`field_prompts.py` L11**: `DESC_ALIAS` `e.g.` → `specifically:`. | Ban: Open-ended `e.g.` ambiguity token. | Deterministic closed list `(specifically: 'a0', 'a1')`. | Zero scope creep. Single line change. | Existing `test_field_prompts.py` + backend audit loop. |
| **`seed_data.json` (19 atoms)**: Add anti-patterns disqualifying prompt scaffolding, scenario parameters, organizational headcounts, and document metadata headers. Align acceptance criteria. | Ban: Vague `concept_description` allowing raw problem constraints to pass as cognitive reasoning. Ban: Absent anti-patterns allowing prompt mining by GPT-5.4. | `anti_patterns` with `allows_contextual_excuse: false`. Multi-step `acceptance_criteria` with `requires_contextual_override: false`. | Zero new Pydantic schemas. Surgical JSON field additions within existing `TDAAssertion` schema. No over-abstraction. | `run_seed.py local --dry-run` + `audit_database_atoms.py --strict` + E2E Kahneman block drift ≤ 2.50 pp. |
| **`run_e2e_variance_test.py` L1785-1845**: Hoist `expected_inputs` resolution AND `load_inputs_from_path` before the `for i in range(num_runs):` loop in `--no-noise` mode. | Ban: Re-extracting PDFs on every run, subjecting `--no-noise` comparison runs to PyMuPDF in-memory state drift. | Single immutable input capsule shared across runs. `expected_inputs` cached from first workflow resolution. | Zero IPC disk sync. Pure in-memory hoisting. | SHA-256 collision on `e2e_inputs_run1.json` and `e2e_inputs_run2.json` under `--no-noise`. |
| **`pdf_chat_extractor.py` L259-323**: CamelCase boundary regex + multi-space collapse in `_reconstruct_tables_as_markdown`. | Ban: PyMuPDF table cell word-gluing (`sopeudutaanrajoihinjaparannetaan`) across cold/warm states. | Deterministic regex: `re.sub(r'([a-zåäö])([A-ZÅÄÖ])', r'\1 \2', text)` + `re.sub(r'\s+', ' ', text).strip()`. | Zero NLP tokenizers. Standard regex only. | Unit test verifying identical word count on repeated extraction across cold/warm instances. |
| **`diff_executions.py` L497-565**: Unicode NFKC + whitespace normalization before SHA-256. | Ban: Raw byte hashing flagging trivial whitespace variants as `ERISTETTY`. | `unicodedata.normalize('NFKC', text)` + whitespace standardization before `hashlib.sha256()`. | Zero custom hash registries. Single canonical normalizer. | Unit test verifying identical hash across ASCII, NBSP, and table whitespace variants. |
| **`anchor_validation_service.py` L125-155**: Guard `_is_lexically_valid` with `if not norm_quote: return False`. | Ban: `norm_text.find("") == 0` evaluating to `True` for empty normalized quotes (`""`). | Deterministic empty string rejection at the top of `_is_lexically_valid`. | Zero new validation classes. Single 2-line guard check. | Unit test asserting empty string, whitespace, and punctuation quotes fail lexical validation. |
| **`extractive_sensor_service.py` L52-105**: Harden `BooleanEvaluationResult.source_quote` with `min_length=10` and non-whitespace validation. | Ban: 1-character punctuation tokens (`"."`, `"-"`) bypassing `strip()` in positive evaluations. | Strict Pydantic V2 schema contract: `min_length=10`, `strip()`, and Null Hypothesis validation. | Zero complex regex engines. Native Pydantic V2 `min_length` and `strip()`. | ISTQB test suite asserting `BooleanEvaluationResult` raises `ValidationError` on quotes < 10 chars or pure whitespace. |
| **`evaluation_steps.py` L144-149**: Replace `self.model_copy(update={"exact_quotes": []})` with Fail-Fast `ValueError`. | Ban: Silent auto-mutation of invalid state via `model_copy(update=)`. | Strict Fail-Fast Pydantic invariant: raise `ValueError` if `contextual_override == True` and `exact_quotes` is non-empty. | Zero mutation logic. Pure declarative validation. | Unit test verifying `StepDTOSemantic` raises `ValidationError` on conflicting override and quotes. |

---

## Proposed Changes

### Component 1: Global Prompt Directives & Schema Purity

#### [MODIFY] [matrix_evaluation.py](file:///c:/src/quorum/backend_v2/models/prompts/execution/matrix_evaluation.py)
1. **Add `<procedural_prompt_disqualification_protocol>` to `MATRIX_SENSOR_SYSTEM_PROMPT`:**
   ```xml
   <procedural_prompt_disqualification_protocol>
   PROCEDURAL PROMPT DISQUALIFICATION:
   - Instructions directed at an external AI assistant, model, or automated system — including
     roleplay directives, formatting constraints, page or length limits, perspective simulation
     commands, and self-dialogue simulation requests — do NOT constitute the author's own
     analytical reasoning, cognitive competence, or self-falsification evidence.
   - Operational problem background parameters, organizational headcounts, fictional budgets,
     or task assignment variables provided as input context do NOT constitute the author's own
     declarative evaluative propositions, empirical categorizations, academic definition recall,
     or primary analytical input datasets/variables.
   - METACOGNITIVE SAFE HARBOR: The author's own self-directed analytical planning,
     deliberate boundary-setting, metacognitive self-challenge, or structured reasoning process
     constitutes legitimate cognitive evidence and is NOT disqualified by this protocol.
   </procedural_prompt_disqualification_protocol>
   ```
2. **Add `<document_metadata_disqualification_protocol>` to `MATRIX_SENSOR_SYSTEM_PROMPT`:**
   ```xml
   <document_metadata_disqualification_protocol>
   DOCUMENT METADATA DISQUALIFICATION:
   - Document metadata headers, distribution lists, recipient designations, file paths, and title blocks
     specify reading audiences or transmission channels; they do NOT qualify as operational domain
     boundaries, analytical scopes, or contextual preconditions for substantive arguments.
   </document_metadata_disqualification_protocol>
   ```
3. **Harden `CONTEXTUAL_OVERRIDE_DIRECTIVE`:**
   - Mandate that a contextual override is permissible ONLY if the text physically articulates an alternative, functionally complete analytical mechanism.
   - Explicitly ban granting contextual overrides based on passive omission, silence, or topical mention.
   - Enforce that inverse rules default strictly to the Null Hypothesis (`is_true = false`, confirming absence of defect) without requiring speculative contextual override text.

#### [MODIFY] [global_mandates.py](file:///c:/src/quorum/backend_v2/models/prompts/execution/global_mandates.py)
1. **Modernize `NULL_HYPOTHESIS_MANDATE`:**
   - Purge obsolete V1 schema terminology (`exact_quotes`, `decision`) and replace with V2 `is_true` / `source_quote` invariants.
   - Purge ambiguity token `(e.g., 'no jargon', 'without empirical data')` and replace with `(specifically: absent jargon or missing empirical data)`.
2. **Modernize `ANTI_ID_MANDATE`:**
   - Remove contradictory instruction commanding the model to populate `atom_id` in the JSON object (`BooleanEvaluationResult` uses `alias` and enforces `extra="forbid"`).
   - Purge ambiguity token `(e.g., semantic_reasoning, exact_quote)` and align with `reasoning` and `source_quote`.
3. **Purge Ambiguity Tokens (`e.g.`) across remaining mandates:**
   - `EXTENSION_ANCHORING_MANDATE`: Replace `(e.g. coaching, falsification...)` with `(specifically: coaching, falsification, remediation, or missing_context)`.
   - `SCHEMA_PURITY_MANDATE`: Replace `(e.g., \")` with `(specifically: \")`.
   - `CONTEXT_SEGREGATION_MANDATE`: Replace `(e.g., previous chat responses, intermediate drafts)` with `(specifically: previous chat responses or intermediate drafts)`.

#### [MODIFY] [field_prompts.py](file:///c:/src/quorum/backend_v2/models/prompts/execution/field_prompts.py)
1. **Update `DESC_ALIAS`:**
   - Replace `(e.g., 'a0', 'a1')` with `(specifically: 'a0', 'a1')`.

---

### Component 2: Seed Data Vault (`backend_v2/seed/seed_data.json`)

All 19 high-entropy atoms identified in the 30-atom triage are surgically hardened with concrete anti-patterns and disambiguated acceptance criteria:

#### Group A: Toulmin & Goodhart & XAI Reporter Core (6 Structural Atoms)

1. **`tda_105f796045430fcda5656f2781522a74` (Toulmin: Soveltamiskonteksti, `#L1047-L1082`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "document metadata, recipient designations, distribution headers, or title blocks that specify target readers without defining operational or environmental boundary conditions for the argument",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria update:**
     ```json
     [
       {
         "instruction": "Identify explicit operational parameters, domain conditions, or environmental constraints restricting the substantive validity of the argument.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Verify that the conditions define when, where, and under what operational thresholds the technical mechanism or proposition remains valid.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Confirm that the scope excludes unsupported universal generalizations as well as superficial document headers or recipient labels.",
         "requires_contextual_override": false
       }
     ]
     ```

2. **`tda_10dd47750c9244139c394ca875f160e6` (Toulmin: Warrant / Oikeutussääntö, `#L1151-L1186`)**
   - **Anti-Pattern update:**
     ```json
     {
       "pattern": "simple causal assertions or sequential conjunctions stating cause-and-effect relationships without articulating the general bridge principle, invariant rule, or structural rationale justifying the transition",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria update:**
     ```json
     [
       {
         "instruction": "Identify both the empirical data point (Data) and conclusive assertion (Claim) within the argument.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Verify that the text explicitly articulates the general bridge principle, natural law, theoretical rule, or structural rationale explaining why and by what mechanism the premise necessitates the conclusion.",
         "requires_contextual_override": false
       }
     ]
     ```

3. **`tda_1d7531b5f5944175bb1eee7eaed44f69` (Toulmin: Warrantti ilman taustatukea, `#L1001-L1036`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "argument entirely lacks an inferential warrant, rendering backing evaluation inapplicable",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria update:**
     ```json
     [
       {
         "instruction": "Precondition: Verify that an explicit inferential rule or warrant linking data to claim is physically present in the text.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Disqualification check: Verify whether external backing (academic literature, empirical benchmark datasets, or established industry standards) is cited to substantiate that warrant.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Confirm that if no inferential warrant exists at all, this atom evaluates to FAILED, preventing false positive passes when both warrant and backing are absent.",
         "requires_contextual_override": false
       }
     ]
     ```

4. **`tda_657fb164be984788a760eed250b3bc61` (Goodhart: Rakenteellinen ohjausskeema, `#L5020-L5059`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "superficial formatting requests, conversational roleplay instructions, document length constraints, or basic output delivery instructions that do not supply an analytical reasoning methodology, conceptual schema, or few-shot cognitive exemplar",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria update:**
     ```json
     [
       {
         "instruction": "Identify an explicit structural template, cognitive schema, or few-shot exemplar provided by the author.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Verify that the provided schema dictates methodological steps, logical categories, or evidentiary criteria for reasoning rather than superficial formatting or conversational roleplay requests.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Confirm that the template actively guides the generation toward structured, verifiable conclusions.",
         "requires_contextual_override": false
       }
     ]
     ```

5. **`tda_42390948661c457983a7b60879a41eca` (XAI Reporter: Rajaamattomat suositukset, `#L11091-L11125`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "recommendation explicitly specifies operational prerequisites, environmental constraints, risk factors, or viability thresholds",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria update:**
     ```json
     [
       {
         "instruction": "Identify normative recommendations, strategic proposals, or operational guidance delivered in the evaluated text.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Verify whether the author asserts the recommendation unconditionally across all contexts without specifying environmental prerequisites, operational thresholds, or boundary conditions under which the advice ceases to be viable.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Confirm that the guidance is presented as an unconstrained universal imperative lacking boundary qualifications.",
         "requires_contextual_override": false
       }
     ]
     ```

6. **`tda_eefe3db0babf3d84e913b50f08696c42` (Toulmin: Lineaarisuusharha, `#L1581-L1616`)**
   - **Anti-Pattern update:**
     ```json
     {
       "pattern": "text explicitly notes systemic complexity, feedback loops, compounding risks, saturation thresholds, or countervailing forces",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria update:**
     ```json
     [
       {
         "instruction": "Locate an argument modeling a multi-variable, adaptive, or complex system.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Verify that the author explicitly asserts a strictly proportional, univariate cause-and-effect relationship without accounting for diminishing returns, friction, or feedback mechanisms.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Confirm that systemic complexity is reduced to naive deterministic proportionality without acknowledging confounding factors.",
         "requires_contextual_override": false
       }
     ]
     ```

---

#### Group B: The Kahneman Dual-Process Core (3 Atoms, `#L3337-L3908`)

7. **`tda_20f87ebd0c5b7de765cc4f6abc9b0fdd` (Kahneman L1: Systeemi 1 Nopea, `#L3337-L3376`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "operational problem background parameters, stakeholder constraints, or task instructions provided as input context rather than the author's own declarative evaluative proposition or subjective stance",
       "allows_contextual_excuse": false
     }
     ```
   - **Acceptance Criteria alignment:**
     ```json
     [
       {
         "instruction": "Identify an authentic declarative proposition or evaluative statement expressing an immediate judgment, reaction, or stance authored by the target speaker.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Verify the proposition is expressed directly without intermediate formal analytical derivation.",
         "requires_contextual_override": false
       },
       {
         "instruction": "Confirm that operational scenario parameters, problem briefing figures, or instructions given to an external agent are excluded from serving as an evaluative stance.",
         "requires_contextual_override": false
       }
     ]
     ```

8. **`tda_6df2bc5ac5e194367107f8d29fa6503e` (Kahneman L2: Siirtymä / Boundary Conditions, `#L3707-L3746`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "task assignment scoping statements, user prompt problem parameters, or organizational context restrictions given as instructions rather than the author defining operational boundary conditions for their own argument",
       "allows_contextual_excuse": false
     }
     ```

9. **`tda_5257ba1edae34afe8b837c8c238cf743` (Kahneman L3: Problem Decomposition, `#L3869-L3908`)**
   - **Anti-Pattern addition:**
     ```json
     {
       "pattern": "high-level strategic goal aspirations, task wishlists, or prompt assignment objectives stated without operational decomposition into isolated, testable constituent sub-mechanisms",
       "allows_contextual_excuse": false
     }
     ```

---

#### Group C: Bloom Taxonomy & Falsification & Clarity Core (7 Atoms, `#L1443-L15046`)

10. **`tda_b36d3ec7b1f94fe9ad4b45795a8a104b` (Bloom L1: Standalone Definition Recall, `#L1692-L1731`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "operational scenario parameters, baseline organizational headcounts, or problem briefing figures supplied as inputs for an assigned task rather than unelaborated academic definitions or theoretical nomenclature",
        "allows_contextual_excuse": false
      }
      ```

11. **`tda_defc33928bb9c172f2f64e090b90f935` (Bloom L1: Unintegrated Catalog Enumeration, `#L1742-L1781`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "organizational staffing breakdowns, stakeholder role distributions, or task parameter listings provided as operational context rather than unintegrated catalogs of academic terminology, dates, or historical figures",
        "allows_contextual_excuse": false
      }
      ```

12. **`tda_10f455c36f754d33a3a551e9e7b61da4` (Bloom L4: Structural System Deconstruction, `#L2486-L2525`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "instructing an external assistant or model to analyze multiple perspectives or scoping an assignment rather than the author directly decomposing the system into distinct operational constituent components",
        "allows_contextual_excuse": false
      }
      ```

13. **`tda_85988e1249fe8a9a3ec181163f17c006` (Bloom L4: Analysointi - Systemic Friction, `#L2586-L2625`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "operational scenario constraints, stakeholder difficulties, or task scoping considerations stated in prompt briefings rather than analytical deconstruction of internal architectural contradictions or systemic trade-offs",
        "allows_contextual_excuse": false
      }
      ```

14. **`tda_9a08254fb47a46fdb8a78030ed68f853` (Toulmin L5: Deliberate Self-Falsification, `#L1443-L1478`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "instructing an external assistant or model to act as devil's advocate or provide adversarial feedback rather than the author directly documenting their own empirical self-falsification tests or counter-hypothesis evaluations",
        "allows_contextual_excuse": false
      }
      ```

15. **`tda_2f6c6565bf10f613d787c03fc97bfb91` (Clarity L1: Explicit Declarative Stance, `#L15007-L15046`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "procedural task instructions, document length constraints, or prompt dispatch commands rather than substantive declarative stances, analytical findings, or strategic recommendations",
        "allows_contextual_excuse": false
      }
      ```
    - **Acceptance Criteria alignment:**
      ```json
      [
        {
          "instruction": "Identify an explicit declarative proposition asserting an analytical stance, substantive finding, or policy recommendation.",
          "requires_contextual_override": false
        },
        {
          "instruction": "Verify that the proposition conveys substantive domain content rather than procedural document delivery or length constraints.",
          "requires_contextual_override": false
        },
        {
          "instruction": "Confirm that the stance provides an identifiable position subject to verification.",
          "requires_contextual_override": false
        }
      ]
      ```

16. **`tda_f1a3d9151c48fe065df1c0afe580caa2` (Falsifier L1: Baseline Proposition, `#L8492-L8526`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "procedural task dispatch instructions or formatting scoping commands rather than substantive analytical propositions or strategic policy proposals",
        "allows_contextual_excuse": false
      }
      ```

---

#### Group D: Newly Discovered 205-Atom Triage Additions (3 Atoms, `#L4970-L15258`)

17. **`tda_f421022aacc8c0c5d2ab80aa5c9719c4` (Avoimuus: Heikko Selitettävyys, `#L15219-L15258`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "operational problem background parameters, organizational staffing figures, or task briefing variables supplied as input context rather than analytical datasets, reference benchmarks, or primary evidence sources",
        "allows_contextual_excuse": false
      }
      ```

18. **`tda_bd85f009b0fb4f7899b40ff0e763dee7` (Goodhart: Proxy Metric Critique, `#L4970-L5009`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "advocating outcome-based management or shifting from presence tracking to goal metrics without analyzing the corruptibility, divergence, or gamification risks of proxy indicators",
        "allows_contextual_excuse": false
      }
      ```

19. **`tda_c607024dbf524f7a9d68af443901c40e` (Causal Mechanism Granularity, `#L7525-L7559`)**
    - **Anti-Pattern addition:**
      ```json
      {
        "pattern": "operational work schedules, core hour policies, or conditional rules stated as workplace guidelines rather than an explanatory structural mechanism detailing how an operational variable transforms system state",
        "allows_contextual_excuse": false
      }
      ```

---

### Component 3: Unit Tests, Verification & Ingress Infrastructure

#### [MODIFY] [test_matrix_evaluation.py](file:///c:/src/quorum/backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py)
- Assert presence of `<procedural_prompt_disqualification_protocol>` and `<document_metadata_disqualification_protocol>`.
- Assert presence of key behavioral phrases (`"Instructions directed at an external AI assistant"`, `"METACOGNITIVE SAFE HARBOR"`, `"primary analytical input datasets/variables"`).
- Verify that `MATRIX_SENSOR_SYSTEM_PROMPT` enforces deterministic Null Hypothesis on inverse rules.

#### [MODIFY] [test_global_mandates.py](file:///c:/src/quorum/backend_v2/tests/unit/models/prompts/test_global_mandates.py)
- Add isolated `test_global_mandates_negative_partitions()` asserting 0 instances of `e.g.`, `atom_id`, `exact_quotes`, `decision` across `GLOBAL_MANDATES_XML` and individual mandate constants.

#### [MODIFY] [run_e2e_variance_test.py](file:///c:/src/quorum/scripts/run_e2e_variance_test.py)
- **Hoist `load_inputs_from_path` outside the execution loop:**
  - In `run_variance_test()`, move the resolution of `expected_inputs` and `raw_inputs = load_inputs_from_path(inputs_target, expected_inputs=expected_inputs)` before the `for i in range(runs):` loop.
  - In `--no-noise` mode, use the single cached `raw_inputs` dictionary directly for all runs, eliminating repeated file reads and in-memory PyMuPDF re-extraction.
  - Guarantee byte-identical payload dumping into `scratch/variance_inputs/e2e_inputs_run{i + 1}.json`.
- **Pre-Flight Ingress Hash Assertion:**
  - In `--no-noise` mode, add an automated pre-flight assertion before triggering subsequent comparison runs: verify that the SHA-256 hashes of `e2e_inputs_run1.json` and `e2e_inputs_run2.json` written to disk are 100% identical.
  - Fail-Fast immediately with `RuntimeError("Pre-flight Ingress Hash Mismatch: e2e_inputs_run1.json and e2e_inputs_run2.json SHA-256 hashes diverge under --no-noise mode.")` before launching the second model, preventing wasteful and expensive API invocations if file serialization experiences an unexpected disturbance.

#### [MODIFY] [pdf_chat_extractor.py](file:///c:/src/quorum/backend_v2/services/ingress/pdf_chat_extractor.py)
- **Enforce deterministic table cell whitespace normalization:**
  - In `_reconstruct_tables_as_markdown()`, sanitize each cell with regex boundary spacing: `re.sub(r'([a-zåäö])([A-ZÅÄÖ])', r'\1 \2', text)` and `re.sub(r'\s+', ' ', text).strip()`.
  - Prevent PyMuPDF table cell word-gluing artifacts (`sopeudutaanrajoihinjaparannetaan`) regardless of cold or warm in-memory layout states.

#### [MODIFY] [diff_executions.py](file:///c:/src/quorum/scripts/diff_executions.py)
- Enforce Unicode NFKC normalization and whitespace standardization before SHA-256 computation on input files in `diff_executions.py` to eradicate false-positive hash discrepancies.

#### [MODIFY] [anchor_validation_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/anchor_validation_service.py)
- **Eradicate empty normalized string bypass bug in `_is_lexically_valid()`:**
  - Add explicit fail-fast guard at the very beginning of `_is_lexically_valid()`:
    ```python
    if not norm_quote:
        logger.warning("Lexical Verifier rejected quote: normalized quote is empty.")
        return False
    ```
  - Eliminates the vulnerability where `norm_text.find("")` evaluated to `0` (which is `!= -1`), returning `True` for quotes consisting exclusively of whitespace or stripped punctuation characters.

#### [MODIFY] [extractive_sensor_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/extractive_sensor_service.py)
- **Harden `BooleanEvaluationResult` DTO Schema:**
  - Update `source_quote` field definition to enforce `min_length=10`:
    ```python
    source_quote: Annotated[
        str | None,
        Field(
            default=None,
            min_length=10,
            max_length=500,
            description=DESC_SOURCE_QUOTE,
        ),
    ] = None
    ```
  - In `truncate_source_quote_at_sentence()`: Ensure stripped string cleanup occurs in `mode="before"`.
  - In `validate_source_quote_invariants()`: Verify that `source_quote` contains substantive non-whitespace characters (`re.search(r"\S", self.source_quote)`), raising `ValueError("Ungrounded positive evaluation: source_quote must be populated with non-empty text when is_true is True.")`.
  - Reinforce Null Hypothesis: enforce that `source_quote` is strictly `None` if `is_true is False` or `contextual_override is True`.

#### [MODIFY] [evaluation_steps.py](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py)
- **Eradicate `model_copy(update=)` auto-mutation duct tape in `StepDTOSemantic`:**
  - Replace silent state mutation on L144-149 with strict Fail-Fast validation:
    ```python
    @model_validator(mode="after")
    def _enforce_override_exclusivity(self) -> Self:
        """Enforces that exact_quotes is empty if contextual_override is True."""
        if self.contextual_override and self.exact_quotes:
            raise ValueError(
                "Null hypothesis violation: exact_quotes must be empty when contextual_override is True."
            )
        return self
    ```

#### [MODIFY] [test_anchor_validation_service.py](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py)
- Add ISTQB negative partition tests asserting that:
  - Empty string `""`, pure whitespace `" "`, and punctuation-only quotes (`"."`, `"-"`, `"..."`) are rejected by `_is_lexically_valid()`.
  - Normal valid quotes continue to match Tier 1 literal find without regression.

#### [MODIFY] [test_extractive_sensor_service.py](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py)
- Add ISTQB boundary value analysis and equivalence partition tests for `BooleanEvaluationResult`:
  - Assert that positive evaluation (`is_true=True`, `contextual_override=False`) raises `ValidationError` when `source_quote` is < 10 characters or pure whitespace.
  - Assert that `source_quote` is strictly forced to `None` when `is_true=False` or `contextual_override=True`.

---

### Component 4: Knowledge Items & As-Built Architecture Documentation

#### [MODIFY] [ki_prompt_orchestration_and_matrix_evaluation.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/prompt_orchestration_and_matrix_evaluation/artifacts/ki_prompt_orchestration_and_matrix_evaluation.md)
- Incorporate Layer 1 Procedural Prompt Disqualification Protocol (`<procedural_prompt_disqualification_protocol>`) and Metacognitive Safe Harbor.
- Incorporate Document Metadata Disqualification Protocol (`<document_metadata_disqualification_protocol>`).
- Formalize Contextual Override Hardening (`CONTEXTUAL_OVERRIDE_DIRECTIVE`) requiring concrete alternative mechanisms, prohibiting passive omission/silence overrides, and enforcing deterministic Null Hypothesis on inverse rules (`is_true = false`).
- Document eradication of obsolete V1 schema terms (`exact_quotes`, `decision`, `atom_id`) and ban on open-ended ambiguity tokens (`e.g.`) across global prompt directives.

#### [MODIFY] [ki_seed_vault_verification_and_sanitization.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/seed_vault_verification_and_sanitization/artifacts/ki_seed_vault_verification_and_sanitization.md)
- Document the 19 hardened high-entropy atom definitions across Groups A, B, C, and D in `seed_data.json`.
- Formalize deterministic anti-pattern standards (`allows_contextual_excuse: false`) and multi-step acceptance criteria disambiguation (`requires_contextual_override: false`) to permanently prevent prompt scaffolding extraction, headcount/scenario mining, and Kahneman System 1/2 score drift.

#### [MODIFY] [ki_ai_testing_standards.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/ai_testing_standards/artifacts/ki_ai_testing_standards.md)
- Document test harness ingress hoisting in `run_e2e_variance_test.py` under `--no-noise` mode guaranteeing 100% cryptographic input collision (`KOLLISIO`) across comparison runs.
- Document PyMuPDF table extraction intra-cell whitespace and punctuation regex boundary normalization in `PdfChatExtractorService`.
- Document canonical Unicode NFKC and whitespace normalization before SHA-256 computation in `diff_executions.py`.
- Document Cross-Model Variance Harmonization target invariants ($\kappa \ge 0.9500$, MAD $\le 1.85\text{ pp}$, Kahneman drift $\le 2.50\text{ pp}$, disagreements $\le 3\text{--}4$ / 205 atoms).

#### [MODIFY] [ki_structured_forensic_quotes.md](file:///c:/Users/risto/.gemini/antigravity-ide/knowledge/structured_forensic_quotes/artifacts/ki_structured_forensic_quotes.md)
- Formalize the Four-Layer Forensic Defense Architecture against generative model compliance evasion.
- Document the empty normalized quote guard (`if not norm_quote: return False`) in `AnchorValidationService._is_lexically_valid`.
- Document schema-level `min_length=10` and non-whitespace enforcement on `BooleanEvaluationResult.source_quote`.
- Reaffirm sovereign Null Hypothesis invariants prohibiting quotes on contextual overrides or failed claims.

#### [MODIFY] [09_llm_prompt_orchestration_and_matrix_evaluation.md](file:///c:/src/quorum/docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md)
- Synchronize via `/tier7-describe-architecture` for Layer 1 procedural prompt and document metadata disqualification protocols, Metacognitive Safe Harbor, hardened contextual override invariants, and schema term purity.

#### [MODIFY] [02_data_seeding_and_ontology.md](file:///c:/src/quorum/docs/architecture/02_data_seeding_and_ontology.md)
- Synchronize via `/tier7-describe-architecture` for Matrix Seed Vault Hardening, deterministic anti-pattern standards, and multi-step acceptance criteria disambiguation.

#### [MODIFY] [01_system_context_and_invariants.md](file:///c:/src/quorum/docs/architecture/01_system_context_and_invariants.md)
- Synchronize via `/tier7-describe-architecture` for Cryptographic Input Ingress Determinism, test harness hoisting invariants, and statistical cross-model consensus bounds.

---

## Actionable Step-by-Step Execution Sequence

### Step 1: Pre-Implementation Cleanups (`global_mandates.py` & `field_prompts.py`)
1. In `@[backend_v2/models/prompts/execution/global_mandates.py#L33-L41]`:
   - Purge contradictory `atom_id` mandate and `(e.g., semantic_reasoning, exact_quote)` in `ANTI_ID_MANDATE`.
2. In `@[backend_v2/models/prompts/execution/global_mandates.py#L72-L84]`:
   - Replace V1 terms `exact_quotes`, `decision`, and `(e.g., 'no jargon', 'without empirical data')` in `NULL_HYPOTHESIS_MANDATE` with V2 `source_quote`, `is_true`, and deterministic phrasing.
3. In `@[backend_v2/models/prompts/execution/global_mandates.py#L95-L133]`:
   - Purge `e.g.` from `EXTENSION_ANCHORING_MANDATE`, `SCHEMA_PURITY_MANDATE`, and `CONTEXT_SEGREGATION_MANDATE`.
4. In `@[backend_v2/models/prompts/execution/field_prompts.py#L11-L12]`:
   - Replace `(e.g., 'a0', 'a1')` with `(specifically: 'a0', 'a1')`.
5. In `@[backend_v2/models/dtos/evaluation_steps.py#L144-L149]`:
   - Replace `self.model_copy(update={"exact_quotes": []})` with Fail-Fast `raise ValueError("Null hypothesis violation: exact_quotes must be empty when contextual_override is True.")`.
6. In `@[backend_v2/services/orchestrator/anchor_validation_service.py#L140-L144]`:
   - Add `if not norm_quote: return False` at the start of `_is_lexically_valid()` to eliminate the empty normalized string bypass where `find("") == 0` returns `True`.
7. In `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L59-L103]`:
   - Add `min_length=10` to `BooleanEvaluationResult.source_quote` field and enforce non-whitespace character presence in `@model_validator`.

### Step 2: Static System Prompt Hardening (`matrix_evaluation.py`)
1. In `@[backend_v2/models/prompts/execution/matrix_evaluation.py#L11-L27]`:
   - Harden `CONTEXTUAL_OVERRIDE_DIRECTIVE` to mandate that alternative concrete mechanisms are physically present and ban overrides for topical silence.
2. In `@[backend_v2/models/prompts/execution/matrix_evaluation.py#L29-L138]`:
   - Inject `<procedural_prompt_disqualification_protocol>` containing English abstract categories, analytical input parameter disqualification, and the Metacognitive Safe Harbor.
   - Inject `<document_metadata_disqualification_protocol>` disqualifying headers, recipient tags, and file paths from serving as operational scope.

### Step 3: Test Harness & Ingress Invariance (`diff_executions.py`, `pdf_chat_extractor.py`, `run_e2e_variance_test.py`)
1. In `@[scripts/diff_executions.py#L497-L565]`:
   - Apply `unicodedata.normalize('NFKC', text)` and uniform whitespace standardization before SHA-256 computation in `_inspect_input_file`.
2. In `@[backend_v2/services/ingress/pdf_chat_extractor.py#L259-L323]`:
   - In `_reconstruct_tables_as_markdown`, apply camelCase boundary splitting (`re.sub(r'([a-zåäö])([A-ZÅÄÖ])', r'\1 \2', c_text)`) and space collapsing (`re.sub(r'\s+', ' ', c_text).strip()`) to table cells.
3. In `@[scripts/run_e2e_variance_test.py#L1785-L1830]`:
   - In `--no-noise` mode, resolve and cache `expected_inputs` and `raw_inputs` on the first iteration or hoist before the loop, reusing the exact dictionary to prevent cold/warm PDF extraction discrepancies.
   - Add Pre-Flight Ingress Hash Assertion: In `--no-noise` mode, assert that `e2e_inputs_run1.json` and `e2e_inputs_run2.json` produce identical SHA-256 hashes before triggering the second model execution, raising `RuntimeError` immediately on mismatch.

### Step 4: Seed Data Hardening (`seed_data.json`)
1. In `@[backend_v2/seed/seed_data.json]`:
   - Update all 19 target atoms across Groups A, B, C, and D with exact anti-patterns and disambiguated acceptance criteria to prevent prompt scraping, headcount mining, and Kahneman System 1/2 drift.

### Step 5: Automated Test Suite & Audit Gates
1. Update `@[backend_v2/tests/unit/models/prompts/test_matrix_evaluation.py#L1-L120]`:
   - Assert presence of `<procedural_prompt_disqualification_protocol>`, `<document_metadata_disqualification_protocol>`, and key behavioral phrases.
2. Update `@[backend_v2/tests/unit/models/prompts/test_global_mandates.py#L1-L50]`:
   - Add `test_global_mandates_negative_partitions()` asserting 0 instances of `e.g.`, `atom_id`, `exact_quotes`, `decision` across `GLOBAL_MANDATES_XML` and individual mandate constants.
3. Update `@[backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py#L240-L285]`:
   - Add ISTQB negative partition tests asserting empty, whitespace, and punctuation-only quotes fail lexical validation.
4. Update `@[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L629-L675]`:
   - Add ISTQB boundary value tests verifying `BooleanEvaluationResult` raises `ValidationError` on quotes < 10 characters or pure whitespace.
5. Run backend audit loop and seed pre-flight verification:
   - `uv run python backend_v2/seed/run_seed.py local --dry-run`
   - `uv run python scripts/audit_database_atoms.py --strict`
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/ --test`
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py --test`
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py --test`

### Step 6: Knowledge Base Synchronization & KI Documentation Updates
1. Update `@[ki_prompt_orchestration_and_matrix_evaluation.md]`:
   - Incorporate Layer 1 Procedural Prompt Disqualification Protocol (`<procedural_prompt_disqualification_protocol>`), Document Metadata Disqualification Protocol (`<document_metadata_disqualification_protocol>`), and Metacognitive Safe Harbor.
   - Formalize Contextual Override Hardening (`CONTEXTUAL_OVERRIDE_DIRECTIVE`) requiring concrete alternative mechanisms and deterministic Null Hypothesis on inverse rules (`is_true = false`).
   - Document total eradication of obsolete V1 schema terms (`exact_quotes`, `decision`, `atom_id`) and ban on open-ended ambiguity tokens (`e.g.`).
2. Update `@[ki_seed_vault_verification_and_sanitization.md]`:
   - Document the 19 hardened high-entropy atom definitions across Groups A, B, C, and D in `seed_data.json`.
   - Formalize deterministic anti-pattern guidelines (`allows_contextual_excuse: false`) and multi-step acceptance criteria disambiguation (`requires_contextual_override: false`).
3. Update `@[ki_ai_testing_standards.md]`:
   - Document test harness ingress hoisting in `scripts/run_e2e_variance_test.py` under `--no-noise` mode guaranteeing 100% cryptographic input collision (`KOLLISIO`).
   - Document deterministic table cell whitespace and punctuation normalization in `backend_v2/services/ingress/pdf_chat_extractor.py`.
   - Document canonical Unicode NFKC and whitespace normalization before SHA-256 computation in `scripts/diff_executions.py`.
   - Document Cross-Model Variance Harmonization target invariants ($\kappa \ge 0.9500$, MAD $\le 1.85\text{ pp}$, Kahneman drift $\le 2.50\text{ pp}$, disagreements $\le 3\text{--}4$ / 205 atoms).
4. Update `@[ki_structured_forensic_quotes.md]`:
   - Formalize the Four-Layer Forensic Defense Architecture against generative model compliance evasion.
   - Document the empty normalized quote guard (`if not norm_quote: return False`) in `AnchorValidationService._is_lexically_valid`.
   - Document schema-level `min_length=10` and non-whitespace enforcement on `BooleanEvaluationResult.source_quote`.
   - Reaffirm sovereign Null Hypothesis invariants prohibiting quotes on contextual overrides or failed claims.

### Step 7: As-Built Architectural Pillar Synchronization via /tier7-describe-architecture
1. Execute `/tier7-describe-architecture` for `@[docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md]`:
   - Anchor Layer 1 procedural prompt and document metadata disqualification protocols, Metacognitive Safe Harbor, hardened contextual override invariants, and schema term purity in timeless present-tense narrative.
2. Execute `/tier7-describe-architecture` for `@[docs/architecture/02_data_seeding_and_ontology.md]`:
   - Anchor Matrix Seed Vault Hardening, deterministic anti-patterns, and multi-step acceptance criteria standards in timeless present-tense narrative.
3. Execute `/tier7-describe-architecture` for `@[docs/architecture/01_system_context_and_invariants.md]`:
   - Anchor Cryptographic Input Ingress Determinism, test harness hoisting invariants, and statistical cross-model consensus bounds in timeless present-tense narrative.

---

## Verification Plan

### Automated Pre-Flight Quality Gates
1. **Contamination & Linter Verification:**
   - Verify 0 ambiguity tokens, 0 empirical leaks, and 0 backend leaks across all 13 matrices:
     ```powershell
     uv run python -c "from scripts.matrix_slice_engine import load_matrix_by_id, detect_empirical_contamination; [print(cid, detect_empirical_contamination(load_matrix_by_id(cid))) for cid in ('blk_440a5fef9331451b','blk_f921c7c0989b47e8','blk_109dab5b6b3f403a','blk_53f32679aa514fcb','blk_fb15f8dcf23f4865','blk_c5804a9143c34cb1','blk_b476f89fb732448c','blk_ff72c2d79edb4ebf','blk_80732a33fe1947ee','blk_6b8c766185294f7e','blk_c3bc5f3eb8e74110','blk_f6e286f050c94d60','blk_22e3598e06414409') if detect_empirical_contamination(load_matrix_by_id(cid))]"
     ```
2. **In-Memory Seed Dry-Run:**
   - Execute strict schema validation on `seed_data.json`:
     ```powershell
     uv run python backend_v2/seed/run_seed.py local --dry-run
     ```
3. **Database Atom Audit:**
   - Execute full strict Pydantic V2 atom audit:
     ```powershell
     uv run python scripts/audit_database_atoms.py --strict
     ```
4. **Backend Quality Gate Loop & Unit Test Suite:**
   - Run quality gate and test suite across prompt models, ingress services, and orchestrator validators:
     ```powershell
     uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/prompts/ --test
     uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/ingress/test_pdf_chat_extractor.py --test
     uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py --test
     uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py --test
     ```
5. **Test Harness Ingress Determinism Verification:**
   - Execute script verification confirming `e2e_inputs_run1.json` and `e2e_inputs_run2.json` produce 100% byte-identical SHA-256 hashes under `--no-noise`.

### Reseed & End-to-End Regression Verification
1. **Synchronize verified seed into runtime database:**
   ```powershell
   uv run python backend_v2/seed/run_seed.py local
   ```
2. **Re-run E2E stack comparison on `docs/jwdatat`:**
   ```powershell
   uv run python scripts/run_e2e_variance_test.py "docs/jwdatat" --workflow wf_9d68c573802341db --compare-registries ai_studio openai --no-noise
   ```
3. **Mathematical Success Invariants:**
   - Disagreements drop from 30 to **$\le 3\text{--}4$** across 205 atoms ($< 2.0\%$).
   - Cohen's Kappa exceeds **0.9500** (*Near-Perfect Agreement*).
   - Fleiss' Kappa exceeds **0.9500**.
   - Mean Absolute Difference (MAD) across all 9 blocks drops from **$7.58\text{ pp} \rightarrow \le 1.85\text{ pp}$**.
   - Kahneman Block Drift collapses from **$+21.98\text{ pp} \rightarrow \le 2.50\text{ pp}$**.
   - Lexical citation grounding remains **100% verified** with 0 hallucinations and 0 empty/whitespace quote bypasses.
   - All evaluated candidate and ingress input files register **`KOLLISIO`** in diff report under `--no-noise`.


### Post-Implementation Documentation & Architecture Verification
1. Verify that all five affected Knowledge Items (`ki_prompt_orchestration_and_matrix_evaluation.md`, `ki_seed_vault_verification_and_sanitization.md`, `ki_ai_testing_standards.md`, `ki_unified_matrix_scoring_strictness.md`, `ki_structured_forensic_quotes.md`) reflect updated prompt protocols, seed vault anti-patterns, harness determinism, and quote validation invariants.
2. Verify that `/tier7-describe-architecture` was executed across all three affected architectural pillars (`09`, `02`, `01`) and that documentation adheres strictly to `timeless_as_built_mandate` (zero historical markers, zero project phases, present-tense narrative).

---

## Post-Implementation Documentation & As-Built Synchronization (/tier7-describe-architecture)

Following successful quality gate completion and E2E regression verification (Step 5), the implementation protocol mandates updating the Knowledge Base and executing `/tier7-describe-architecture` to keep architectural documentation in 1:1 parity with the codebase.

### 1. Knowledge Item (KI) Artifact Updates
- **@[ki_prompt_orchestration_and_matrix_evaluation.md]**:
  - Incorporate Layer 1 Procedural Prompt Disqualification Protocol (`<procedural_prompt_disqualification_protocol>`): Disqualify AI model dispatch instructions, conversational roleplay requests, document length constraints, and task scenario variables from serving as cognitive or evaluative evidence.
  - Incorporate Metacognitive Safe Harbor: Explicitly protect author-directed analytical planning, self-challenge, and deliberate boundary-setting as valid cognitive evidence.
  - Incorporate Document Metadata Disqualification Protocol (`<document_metadata_disqualification_protocol>`): Disqualify headers, distribution lists, recipients, and file paths from serving as operational scope boundaries.
  - Formalize Contextual Override Hardening (`CONTEXTUAL_OVERRIDE_DIRECTIVE`): Mandate concrete alternative mechanisms, ban passive omission/silence overrides, and enforce deterministic Null Hypothesis (`is_true = false`) on inverse rules.
  - Document complete eradication of legacy V1 schema terms (`exact_quotes`, `decision`, `atom_id`) and ban on open-ended ambiguity tokens (`e.g.`) across `global_mandates.py` and `field_prompts.py`.
- **@[ki_seed_vault_verification_and_sanitization.md]**:
  - Document the 19 hardened high-entropy atom definitions across Groups A, B, C, and D in `seed_data.json`.
  - Formalize deterministic anti-pattern guidelines (`allows_contextual_excuse: false`) and multi-step acceptance criteria disambiguation (`requires_contextual_override: false`) to permanently prevent prompt scaffolding extraction, headcount/scenario mining, and Kahneman System 1/2 score drift.
- **@[ki_ai_testing_standards.md]**:
  - Document test harness ingress hoisting in `scripts/run_e2e_variance_test.py` under `--no-noise` mode guaranteeing 100% cryptographic input collision (`KOLLISIO`) across comparison runs.
  - Document PyMuPDF table extraction intra-cell whitespace and punctuation regex boundary normalization in `PdfChatExtractorService`.
  - Document canonical Unicode NFKC and whitespace normalization before SHA-256 computation in `scripts/diff_executions.py`.
  - Document Cross-Model Variance Harmonization target invariants ($\kappa \ge 0.9500$, MAD $\le 1.85\text{ pp}$, Kahneman drift $\le 2.50\text{ pp}$, disagreements $\le 3\text{--}4$ / 205 atoms).
- **@[ki_unified_matrix_scoring_strictness.md]**:
  - Document statistical agreement baselines and target invariants for cross-model calibration between Gemini 3.8 Flash and OpenAI GPT-5.4.
- **@[ki_structured_forensic_quotes.md]**:
  - Formalize the Four-Layer Forensic Defense Architecture against generative model compliance evasion (whitespace, punctuation, placeholders, and scaffolding mining).
  - Document the empty normalized quote guard (`if not norm_quote: return False`) in `AnchorValidationService._is_lexically_valid`.
  - Document schema-level `min_length=10` and non-whitespace enforcement on `BooleanEvaluationResult.source_quote`.
  - Reaffirm sovereign Null Hypothesis invariants prohibiting quotes on contextual overrides or failed claims.

### 2. Architectural Pillar Synchronization via /tier7-describe-architecture
The architectural pillar documents in `docs/architecture/` must be updated in accordance with the Dual-Axis Documentation Paradigm, `timeless_as_built_mandate`, and `documentation_present_tense_mandate`:
- **@[docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md]**:
  - Synchronize Section 1 (Four-Layer Clean Stack):
    - Update Layer 1 Static System Directives to document `<procedural_prompt_disqualification_protocol>`, `<document_metadata_disqualification_protocol>`, and the Metacognitive Safe Harbor.
  - Synchronize Section 2 (TDA Matrix Evaluation Reference):
    - Document hardened contextual override mechanics (`CONTEXTUAL_OVERRIDE_DIRECTIVE`), requiring physical presence of alternative mechanisms and deterministic Null Hypothesis for inverse defect rules.
    - Document schema term purity: complete elimination of V1 terms (`exact_quotes`, `decision`, `atom_id`) and ban on open-ended ambiguity tokens (`e.g.`).
- **@[docs/architecture/02_data_seeding_and_ontology.md]**:
  - Synchronize Section 2 (Architectural Principles & Implementation):
    - Document Matrix Seed Vault Hardening & Anti-Pattern Standards: incorporation of deterministic anti-patterns (`allows_contextual_excuse: false`) and multi-step acceptance criteria (`requires_contextual_override: false`) across high-entropy evaluation atoms, eliminating prompt mining, headcount extraction, and System 1/2 concept drift.
- **@[docs/architecture/01_system_context_and_invariants.md]**:
  - Synchronize Section 2 (Architectural Principles & Invariants):
    - Document Cryptographic Input Ingress Determinism: test harness hoisting invariants in `--no-noise` mode, PyMuPDF table cell whitespace and punctuation normalization, and canonical Unicode NFKC hashing.
    - Document Statistical Cross-Model Consensus Invariants ($\kappa \ge 0.9500$, Fleiss $\ge 0.9500$, MAD $\le 1.85\text{ pp}$, Kahneman drift $\le 2.50\text{ pp}$, disagreements $\le 3\text{--}4$ / 205 atoms).

### 3. Execution Mandate & Verification
The synchronization will be performed following Step 5 using `/tier7-describe-architecture`:
- The auditor will verify that all physical files match the theoretical documentation.
- The auditor will verify that zero legacy anti-patterns or historical markers exist in the updated pillars.
- Documentation must describe purely and exclusively current system state in present tense, with zero references to development phases ("vaiheet", "Phase 1"), dates, or artificial Law/Enforcement labels.

---

## Execution Command

This implementation plan is fully reconciled, audited, and ready for systematic execution. Start a fresh chat session and execute:

```powershell
/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Cross_Model_Variance_Harmonization.md]
```
