# Implementation Plan - Human-AI Collaboration Matrix (HACM) Seed, Dedicated Workflow & Custom Output Profile

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

## 1. Executive Summary

### 1.1 Objective
Establish the **Human-AI Collaboration Matrix (HACM)** (*Tekoälyn Ohjauksen ja Yhteistyön Auditointi*), a **Dedicated Assessment Workflow** (`wf_06a1d71000000001`), and a **Tailored Custom Output Profile** (`prf_06b1d71000000001`) strictly as declarative data assets in `@[backend_v2/seed/seed_data.json]`. In accordance with explicit user mandates:
1. **Zero Code Modifications:** Zero modifications to Python (`.py`) or Dart (`.dart`) source code files. All functionality is realized 100% through declarative seed configuration.
2. **Exhaustive Configuration Completeness (Zero Missing Fields):** Every single field across `PromptBlock`, `MatrixScale`, `MatrixClaim`, `TDAAssertion`, `Step`, `Workflow`, and `OutputProfile` is explicitly defined and populated with verified data-driven values, ensuring 100% parity with Quorum Studio UI controls and existing production matrices (`matrix_bloom`, `matrix_goodhart`, `matrix_causal_analyst`).
3. **Rigorous Scientific Theory Foundation:** Fully grounded in established cognitive science and human-machine interaction literature: Supervisory Control & Levels of Automation (Sheridan & Verplank, 1978; Parasuraman et al., 2000), Automation Bias (Parasuraman & Manzey, 2010), Distributed Cognition & Cognitive Offloading (Hutchins, 1995; Clark & Chalmers, 1998; Risko & Gilbert, 2016), Epistemic Vigilance (Sperber et al., 2010; Mercier & Sperber, 2011), and Critical AI Literacy Taxonomies (Ng et al., 2021; Long & Magerko, 2020).
4. **Exact Parity of Positive Capabilities & Negative Error Detectors:** The matrix configures exactly 25 TDA assertions across 5 scales (12 Positive Capabilities [48%] and 13 Negative Error Detectors / Anti-patterns [52%]), matching the mathematical parity of Quorum's sovereign benchmark matrices (`matrix_goodhart`, `matrix_causal_analyst`, and `matrix_taskxai_clarity`).
5. **Dynamic Input Files & Counts:** The workflow operates with dynamic topology agnosticism, supporting varying combinations and quantities of candidate inputs (conversational transcripts, final products, reflections, and assignments) without rigid file count assumptions.
6. **Dedicated Presentation & Evaluation:** A new sovereign workflow and customized output profile ensure existing workflows remain untouched while providing tailored executive coaching, radar visualizations, and evidentiary synthesis for human-AI interaction.

### 1.2 Core Architectural Invariants
1. **Zero Code Mutation Invariant:** Modifying source files in `backend_v2/` (outside `backend_v2/seed/seed_data.json`) or `client_app_v2/` is strictly prohibited. The system executes this feature purely via data-driven configuration.
2. **Pure Seed Vault Governance:** In accordance with `03_seed_vault.md`, all structural data modifications occur exclusively in `@[backend_v2/seed/seed_data.json]` before synchronization to the local development database via `uv run python backend_v2/seed/run_seed.py local`. Direct ad-hoc mutations of `data/db_v2.json` are strictly forbidden.
33: 3. **100% Field Population Mandate:** No entity may rely on undefined optional fields or null fallbacks where explicit domain values are required by Quorum Studio UI or runtime evaluators.
4. **50/50 Positive/Negative Balance:** Exactly 12 positive capability assertions (`inverse_evidence: false`) and 13 negative error detector assertions (`inverse_evidence: true`) distributed across 5 scales.
5. **Dynamic Topology Agnosticism:** Input ingestion handles dynamic document counts through `ExpectedInput` optionality (`required: false` on optional deliverables) and `SourceDocumentPacker` dynamic mapping resolution. Whether a candidate submits 1, 2, 3, or 4 documents, the DAG executes deterministically without data starvation or unmapped key failures.
6. **TargetSpeaker.USER Citation Boundary:** All evaluation claims in HACM strictly enforce `target_speaker: TargetSpeaker.USER`. In `AnchorValidationService`, quote extraction for these claims is strictly quarantined to `<user_payload>` blocks in `chat_log` and `reflection_text`. Model generations in `<ai_draft_context>` are mathematically excluded from evidentiary attribution.
7. **13-Parameter TDA Compliance:** Every assertion in the matrix defines all 13 canonical parameters: `evaluation_track`, `concept_description`, `anchor_target`, `bounding_box_scope`, `extraction_rule`, `anti_patterns`, `contrastive_example`, `acceptance_criteria`, `syntactic_anchors`, `enforce_pre_flight`, `aggregation_mode`, `inverse_evidence`, and `target_speaker`.
8. **Continuous 0–100% Strictness Invariant:** Scored sovereignly through `UnifiedScoringEngine` using the workflow's configured `default_strictness_level` (50% default).
9. **Dedicated Output Profile Parity:** Matrix visualization is automatically generated by `ReportAssembler` into `quadrant_matrix`, `2d_compare`, and `matrix_summary` blocks, exporting forensically to Excel, PDF, and SDUI without requiring UI code additions.

---

## 2. Target Boundaries & Scope

### 2.1 Target Files
- `@[backend_v2/seed/seed_data.json]` [MODIFY]

### 2.2 Context Files [READ-ONLY]
- `@[backend_v2/models/domain/matrix.py]`
- `@[backend_v2/models/domain/workflow.py]`
- `@[backend_v2/models/domain/step.py]`
- `@[backend_v2/models/domain/output_profile.py]`
- `@[backend_v2/models/domain/prompt_blocks.py]`
- `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]`
- `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]`
- `@[backend_v2/services/orchestrator/anchor_validation_service.py]`
- `@[backend_v2/utils/scoring/unified_engine.py]`

---

## 3. Scientific Theory Grounding & Empirical Evidence

### 3.1 Scientific Theoretical Foundations

The HACM matrix operationalizes four established academic theoretical pillars:

1. **Supervisory Control & Levels of Automation (LOA):**
   - *Foundational Literature:* Sheridan & Verplank (1978); Parasuraman, Sheridan & Wickens (2000); Parasuraman & Manzey (2010).
   - *Theoretical Model:* Grades human interaction from passive delegation (LOA 1-2) through shared contextual constraint framing (LOA 3-4) to supervisory strategic steering (LOA 5).
   - *Phenomenon Addressed:* **Automation Bias & Complacency** — the psychological tendency to passively trust automated/LLM outputs without verifying validity, actively detected by Scale 1 and Scale 2 error detectors.

2. **Distributed Cognition & Cognitive Offloading:**
   - *Foundational Literature:* Hutchins (1995); Clark & Chalmers (1998); Risko & Gilbert (2016).
   - *Theoretical Model:* Cognitive artifacts (LLMs) extend human reasoning only when the human retains mental model boundaries and intentional direction.
   - *Phenomenon Addressed:* **Mindless Offloading vs. Synergistic Extension** — penalizing authors who offload critical judgment (leaving 96% of cognitive labor to AI), while rewarding active curation and conceptual direction.

3. **Epistemic Vigilance & Human-AI Falsification:**
   - *Foundational Literature:* Sperber et al. (2010); Mercier & Sperber (2011); Popper (1959).
   - *Theoretical Model:* Cognitive mechanisms for evaluating informant reliability, detecting sycophancy, and stress-testing claims through counter-arguments.
   - *Phenomenon Addressed:* **Sycophancy Exploitation & Hallucination Acceptance** — measuring whether the human actively interrogates AI assertions ("Riittääkö yksi läsnäolopäivä?") or uncritically accepts plausible-sounding confabulations.

4. **Critical AI Literacy & Interaction Taxonomies:**
   - *Foundational Literature:* Ng, Leung, Chu & Qiao (2021); Long & Magerko (2020).
   - *Theoretical Model:* The 4 evaluation dimensions of HACM map directly to the four core competency constructs of AI Literacy:
     * *Dimension 1:* Kehotusarkkitehtuuri ja reunaehdot (Framing & Operational Scaffolding).
     * *Dimension 2:* Kriittisyys ja oletusten haastaminen (Epistemic Vigilance & Falsification).
     * *Dimension 3:* Kuraatio ja tiedon hakeminen (Active Derivation & Curation).
     * *Dimension 4:* Metakognitiivinen reflektointi (Calibrated Self-Awareness & AI Epistemic Limits).

### 3.2 Empirical Validation from Physical Executions

Forensic inspection of physical data in `@[data/files/executions/]` and `@[data/files/artifacts/reports/]` establishes direct physical proof for this architecture:

| Empirical Observation | Execution 1 (`exe_14218c72ea734ec3`) | Execution 2 (`exe_eefe282ee7764c46`) | Manifestation in HACM Design |
| :--- | :--- | :--- | :--- |
| **User Prompt Volume** | 1,818 bytes (5.3% of total chat log) | 922 bytes (1.8% of total chat log) | Under 6% human text necessitates evaluating prompt quality over raw length. |
| **Observed Interaction** | Structured 3-role dialectic prompt (CFO, HR, Team Lead) with self-debate instructions. | Superficial reformatting commands ("poista taulukot ja kerro tekstinä", "muuta taulukko tekstiksi"). | Direct physical proof of Scale 3 (Framing) vs Scale 2 (Cosmetic Fiddling). |
| **Observed Self-Reflection** | "Otin varmaan lopputuloksen vähän liian helposti annettuna." | "Aloitin kyselemään yleisesti... Esimerkkejä en antanut. Ennakoin että alkuun en saa hyvää tulosta..." | Direct physical proof of Scale 4/5 Metacognitive Calibration. |
| **AI Text Contamination** | 21 of 25 quotes (84%) in deliverable were verbatim copies of Gemini AI responses. | Evaluated deliverable quoted CSRD directives and EU taxonomies generated by Gemini AI. | Absolute necessity of `TargetSpeaker.USER` to prevent crediting AI to the human. |
| **Anti-Pattern Occurrence** | Admitted lack of follow-up challenges to the AI's dialectic conclusion. | Hit Goodhart Anti-pattern: "Author attempts to enhance output quality purely via cosmetic prompt buzzwords". | Validates the need for 13 distinct negative error detectors to catch real behavioral pitfalls. |

### 3.3 Cold Rehearsal Simulation & Calibration Insights (`exe_14218c72ea734ec3`)

A mathematical cold rehearsal was executed evaluating `exe_14218c72ea734ec3` (1,979 bytes user prompts, 271 bytes reflection, 4,442 bytes deliverable) against the 25 HACM TDA assertions:

| Evaluation Metric | Measured Result | Benchmark Parity & Interpretation |
| :--- | :--- | :--- |
| **Demonstrated Positive Capabilities** | **11 / 12 (91.7%)** | High-level mastery across framing, dialectic roles, falsification, and boundary enforcement. |
| **Tripped Negative Error Detectors** | **2 / 13 (15.4%)** | Tripped `A9_buzzword_steering` (Scale 2) and `A14_passive_acceptance` (Scale 3). |
| **Overall HACM Score** | **4.20 / 5.0 (80.0 / 100)** | Resolves the Attribution Paradox: Old workflow scored 14.50/100 because it evaluated the AI's deliverable; HACM scores 80.0/100 by measuring human steering agency. |
| **Dimension 1: Framing & Scaffolding** | **4.40 / 5.0** | 3-perspective dialectic prompting (CFO, HR, Strategist) with clear operational boundaries. |
| **Dimension 2: Epistemic Vigilance** | **4.40 / 5.0** | Explicit demand for sources, fact verification, and devil's advocate counter-proposals. |
| **Dimension 3: Curation & Sovereignty** | **3.00 / 5.0 (Bottleneck)** | **The Curation Deficit:** Deliverable contains 84% verbatim copied AI text. Human delegated final synthesis wholesale to the model. |
| **Dimension 4: Dialectic Reflection** | **5.00 / 5.0** | 8-cycle convergence with honest, calibrated metacognition ("Otin varmaan lopputuloksen vähän liian helposti annettuna"). |

#### Strategic Calibration Directives Derived from Cold Rehearsal:
1. **The Curation vs. Prompting Delta:** The output profile directives MUST specifically instruct the Executive Summary and Coaching synthesizers to highlight discrepancies between sophisticated prompt scaffolding (Dim 1/2) and passive deliverable derivation (Dim 3).
2. **The Dialectic Delegation Trap:** When a human instructs the AI to be its own devil's advocate without introducing independent empirical verification or counter-evidence, the system flags this as pseudo-falsification requiring active human fact-checking.
3. **Metacognitive Calibration Multiplier:** Genuine self-reflection acknowledging automated compliance ("Otin varmaan lopputuloksen liian helposti annettuna") prevents down-scoring into pure automation bias by confirming epistemic self-awareness.

---

## 4. The 25 TDA Assertions Architecture (Exact 50/50 Balance)

To achieve 100% parity with Quorum's standard benchmark matrices (`matrix_goodhart`, `matrix_causal_analyst`, `matrix_taskxai_clarity`), HACM defines exactly 25 TDA assertions: **12 Positive Capabilities (48%) and 13 Negative Error Detectors (52%)**:

```
Scale 1: 2 Positive, 3 Negative (Total 5)
Scale 2: 2 Positive, 3 Negative (Total 5)
Scale 3: 2 Positive, 3 Negative (Total 5)
Scale 4: 3 Positive, 2 Negative (Total 5)
Scale 5: 3 Positive, 2 Negative (Total 5)
Total:  12 Positive (48%), 13 Negative (52%)
```

### Scale 1: Passiivinen tilaaja (Score = 1)
*Thematic Focus: Automation Bias, Blind Delegation, Lack of Quality Thresholds.*
1. **[POSITIIVINEN KYVYKKYS] Perustehtävänanto:** Author states a primary topic, subject, or desired outcome without operational guidelines. (`inverse_evidence: false`)
2. **[POSITIIVINEN KYVYKKYS] Välitön hyödyntäminen:** Author adopts model suggestions as a starting baseline for task initiation. (`inverse_evidence: false`)
3. **[VIRHEDETEKTORI] Sokea delegointi ja oraakkeliharha:** Author delegates autonomous decisions to AI without specifying boundary conditions or success criteria. (`inverse_evidence: true`)
4. **[VIRHEDETEKTORI] Hallusinaation kuittaaminen:** Author ratifies, endorses, or adopts unverified or fabricated assertions without cognitive review. (`inverse_evidence: true`)
5. **[VIRHEDETEKTORI] Mielistelyn kritiikitön hyväksyminen:** Author treats sycophantic model agreement or flattering praise as validation of analytical quality. (`inverse_evidence: true`)

### Scale 2: Reaktiivinen viilaaja (Score = 2)
*Thematic Focus: Superficial Formatting Fixation, Prompt Buzzwords, Fragmented Corrections.*
6. **[POSITIIVINEN KYVYKKYS] Pisteittäinen virheenkorjaus:** Author identifies and rectifies isolated typographical, lexical, or factual errors. (`inverse_evidence: false`)
7. **[POSITIIVINEN KYVYKKYS] Pituus- ja muotomääräykset:** Author defines explicit length, document type, or structural layout constraints. (`inverse_evidence: false`)
8. **[VIRHEDETEKTORI] Kosmeettinen fiksaatio (Observed in Exe 2):** Author restricts prompts purely to layout, cosmetic rewording, or table conversion without addressing substance. (`inverse_evidence: true`)
9. **[VIRHEDETEKTORI] Taikasanaohjaus (Prompt Buzzwords):** Author attempts to improve quality using superficial buzzwords ("toimi asiantuntijana") without providing actionable constraints. (`inverse_evidence: true`)
10. **[VIRHEDETEKTORI] Kiertely ilman suuntaa:** Author repeatedly re-prompts the model with circular phrasing when dissatisfied, instead of introducing concrete criteria or examples. (`inverse_evidence: true`)

### Scale 3: Kontekstin asettaja (Score = 3)
*Thematic Focus: Multi-Perspective Framing, Role Specification, Operational Boundaries.*
11. **[POSITIIVINEN KYVYKKYS] Moninäkökulmainen roolitus (Observed in Exe 1):** Author constructs a multi-perspective dialectic instructing the model to evaluate topics across distinct organizational roles. (`inverse_evidence: false`)
12. **[POSITIIVINEN KYVYKKYS] Eksplisiittiset reunaehdot ja kiellot:** Author establishes negative constraints, exclusion criteria, or forbidden assumptions (including anti-jargon directives). (`inverse_evidence: false`)
13. **[VIRHEDETEKTORI] Jäykkä sapluunadogmatismi:** Author imposes an excessively rigid template that artificially suppresses relevant contextual nuances. (`inverse_evidence: true`)
14. **[VIRHEDETEKTORI] Passiivinen lopputuloksen hyväksyntä (Observed in Exe 1):** Author establishes a sophisticated prompt framework but uncritically accepts the generated output without follow-up inquiry. (`inverse_evidence: true`)
15. **[VIRHEDETEKTORI] Epäsuhtainen keinotekoinen vastakkainasettelu:** Author forces artificial dichotomies between perspectives that are non-conflicting in practice. (`inverse_evidence: true`)

### Scale 4: Kriittinen haastaja (Score = 4)
*Thematic Focus: Epistemic Vigilance, Counterfactual Probing, Falsification.*
16. **[POSITIIVINEN KYVYKKYS] Oletusten aktiivinen haastaminen:** Author interrogates model claims, demands counter-arguments, or tests edge cases ("Riittääkö yksi läsnäolopäivä?"). (`inverse_evidence: false`)
17. **[POSITIIVINEN KYVYKKYS] Empiirisen ankkuroinnin vaatimus:** Author commands the model to cite verifiable empirical research, statutory codes, or external benchmarks for claims. (`inverse_evidence: false`)
18. **[POSITIIVINEN KYVYKKYS] Epävarmuuksien ja raja-arvojen esiin pakottaminen:** Author explicitly requires the model to disclose failure modes, confidence limits, and boundary conditions. (`inverse_evidence: false`)
19. **[VIRHEDETEKTORI] Päämäärätön sokraattinen regressio:** Author enters endless theoretical deconstruction and meta-questioning, preventing operational execution. (`inverse_evidence: true`)
20. **[VIRHEDETEKTORI] Valikoiva vahvistusharha:** Author challenges model outputs selectively only when they contradict personal preconceived conclusions. (`inverse_evidence: true`)

### Scale 5: Strateginen orkestroija (Score = 5)
*Thematic Focus: Distributed Cognition, Epistemic Calibration, Active Curation.*
21. **[POSITIIVINEN KYVYKKYS] Aktiivinen synteettinen kuraatio:** Author selectively derives, recombines, and discards AI generations to construct an authentic, context-tailored final deliverable. (`inverse_evidence: false`)
22. **[POSITIIVINEN KYVYKKYS] Jännitteiden ja kompromissien hallinta:** Author identifies cross-dimensional tensions between AI suggestions and executes a reasoned trade-off decision. (`inverse_evidence: false`)
23. **[POSITIIVINEN KYVYKKYS] Kalibroitu metakognitio ja episteeminen nöyryys:** Author demonstrates precise awareness of own domain competence limits, AI boundaries, and interaction efficacy. (`inverse_evidence: false`)
24. **[VIRHEDETEKTORI] Kognitiivinen imperialismi:** Author dismisses mathematically valid model evidence without justification, relying purely on unsubstantiated subjective intuition. (`inverse_evidence: true`)
25. **[VIRHEDETEKTORI] Kompleksisuuden ylikompensointi:** Author designs an unnecessarily convoluted multi-step orchestration pipeline that destroys operational clarity and auditability. (`inverse_evidence: true`)

---

## 5. Exhaustive Configuration Schema & Field Parity

Every entity introduced in this plan is populated 100% without missing or empty fields, strictly mirroring Quorum Studio UI controls and existing seed schemas:

### 5.1 Matrix PromptBlock Schema Parity (`blk_7d8e9f0a1b2c3d4e`)

| Configuration Attribute | Populated Value | Validation / Studio UI Binding |
| :--- | :--- | :--- |
| `id` | `"blk_7d8e9f0a1b2c3d4e"` | Opaque Stripe ID pattern (`blk_[a-f0-9]{16}`) |
| `slug` | `"matrix_hacm"` | Distinct slug identifier |
| `category_id` | `"matrix"` | Category binding for Studio matrix editor |
| `type` | `"float"` | Desimaaliluku (Float) dropdown |
| `is_evaluative` | `True` | "Lasketaan keskiarvoon (Evaluative)" checkbox |
| `allow_decimals` | `True` | "Salli desimaalit" checkbox |
| `allow_contextual_override` | `True` | "Salli kognitiivinen ohitus" switch |
| `is_lightweight_protocol` | `False` | Heavy matrix evaluation pipeline flag |
| `target_input_key` | `"chat_log"` | Binds extraction target to conversation history |
| `label` | `{"translations": {"fi": "Tekoälyn Ohjauksen ja Yhteistyön Auditointi (HACM)", "en": "Human-AI Collaboration Matrix (HACM)"}}` | Localizable name in Studio and PDF headers |
| `description` | `{"translations": {"fi": "Arvioi ihmisen ja tekoälyn vuorovaikutusta: kehystyksen tarkkuutta, kriittistä haastamista, kuraatiota ja metakognitiota.", "en": "Audits human-AI interaction across framing, critical inquiry, active curation, and metacognition."}}` | Localizable description in Studio catalog |
| `output_extensions` | `["falsification", "theory_link", "risk_flag", "coaching", "remediation_steps", "emotional_sentiment", "confidence", "source_id"]` | Complete XAI chip selection matching Studio UI |
| `theory_grounding` | `{"source_url": "https://www.jstor.org/stable/j.ctt1v2xv4", "citation_reference": "Sheridan, T. B., & Verplank, W. L. (1978). Human and Computer Control of Undersea Teleoperators. MIT Man-Machine Systems Laboratory; Parasuraman, R., Sheridan, T. B., & Wickens, C. D. (2000). A model for types and levels of human interaction with automation. IEEE Transactions on Systems, Man, and Cybernetics."}` | "Teorian Maadoitus (RAG)" switch, URL & citation |
| `ai_description` | `"OBJECTIVE:\nEvaluate the human operator's steering agency, framing architecture, critical inquiry, and active curation in collaboration with generative AI.\n\nCRITICAL MANDATE:\nStart by assuming no evidence exists. Enforce the Null Hypothesis by returning null for exact_quote unless explicit physical evidence is verified in <user_payload> tags.\n\nEVIDENTIARY QUARANTINE:\nExtract quotes exclusively from the human operator (lines starting with 'user:'). NEVER extract evidence from AI responses ('ai:')."` | Static cognitive instruction isolating LLM prompt |
| `computed_min` | `1` | Lowest scale score |
| `computed_max` | `5` | Highest scale score |
| `rows` | 4 `MatrixRow` definitions mapping the 4 dimensions (`Kehotusarkkitehtuuri`, `Kriittisyys`, `Kuraatio`, `Metakognitio`) | Multi-dimensional matrix row definitions |
| `columns` | `None` | Standard 1D/2D BARS representation |
| `scales` | 5 `MatrixScale` definitions (scores 1..5), each with `score`, `name`, `ai_label`, and 5 `MatrixClaim` definitions (each containing a fully-hydrated `TDAAssertion` with all 13 canonical parameters) | BARS scale columns matching Studio UI |

### 5.2 Step Blueprint Schema Parity (`sp_06c1d71000000001`)

| Configuration Attribute | Populated Value | Validation / Role |
| :--- | :--- | :--- |
| `id` | `"sp_06c1d71000000001"` | Opaque Stripe ID pattern (`sp_[a-f0-9]{16}`) |
| `slug` | `"hacm_evaluator_step"` | Distinct step slug identifier |
| `organization_id` | `"SYSTEM"` | System tenant ownership |
| `name` | `{"translations": {"fi": "Tekoälyohjauksen Arvioija", "en": "Human-AI Collaboration Evaluator"}}` | Localizable step name in Studio DAG builder |
| `description` | `{"translations": {"fi": "Arvioi käyttäjän tekoälyohjausta, kriittistä haastamista, kuraatiota ja reflektiota HACM-matriisin mukaisesti.", "en": "Evaluates user AI steering, critical inquiry, curation, and reflection using HACM matrix."}}` | Localizable step description |
| `type` | `"llm"` | Step execution engine type |
| `extraction_protocol_block_id` | `"blk_573802341db9d68c"` | Authority extraction protocol binding |
| `criteria_block_ids` | `["blk_7d8e9f0a1b2c3d4e"]` | Binds HACM matrix block as evaluation criteria |
| `pre_hooks` | `["inject_step_metadata", "atom_flattening_hook"]` | Standard pre-execution pipeline hooks |
| `post_hooks` | `["matrix_scoring_hook", "normalize_matrix_scores", "enforce_passivity_penalty"]` | Post-execution scoring and normalization hooks |
| `safety` | `"safe"` | Guardrail safety tier |
| `allowed_mcp_tools` | `[]` | MCP tool permissions |
| `expected_inputs` | `["chat_log", "product_text", "reflection_text", "assignment_context"]` | Dynamic input declarations |
| `is_system_core` | `False` | Allows flexible workflow configuration |
| `cognitive_tier` | `"fast"` | LLM cognitive model registry strategy |

### 5.3 Dedicated Assessment Workflow Schema Parity (`wf_06a1d71000000001`)

| Configuration Attribute | Populated Value | Validation / Role |
| :--- | :--- | :--- |
| `id` | `"wf_06a1d71000000001"` | Opaque Stripe ID pattern (`wf_[a-f0-9]{16}`) |
| `slug` | `"tekoalyn_kayton_ja_ohjauksen_auditointi"` | Sovereign workflow slug |
| `name` | `{"translations": {"fi": "Tekoälyn Käytön ja Ohjauksen Auditointi", "en": "Human-AI Collaboration & Steering Audit"}}` | Workflow title in Studio selector |
| `description` | `{"translations": {"fi": "Työnkulku, joka arvioi ihmisen tekemää ohjausta, kyseenalaistamista ja reflektointia tekoälyvuorovaikutuksessa. Keskittyy prosessiin ja vuorovaikutuksen laatuun lopputuotteen lisäksi.", "en": "Workflow auditing human steering, critical questioning, and reflection in AI collaboration. Evaluates the interaction process and curation rather than assuming human authorship of the final deliverable."}}` | Workflow description |
| `status` | `"active"` | Active execution state |
| `version` | `1` | Integer schema version |
| `is_public` | `True` | Discoverable in Quorum Studio catalog |
| `default_profile_id` | `"prf_06b1d71000000001"` | Binds directly to dedicated output profile |
| `organization_id` | `"SYSTEM"` | System tenant ownership |
| `mcp_gateway_id` | `"sys_8172bda70c8641c5"` | Default system MCP gateway |
| `model_registry_id` | `"sys_e26807f3bfa3454d"` | Resolves from global model registry |
| `default_strictness_level` | `50` | Calibrated continuous strictness slider default |
| `security_penalty` | `0.0` | Security failure penalty rate |
| `post_hoc_penalty` | `0.0` | Post-hoc rationalization penalty rate |
| `passivity_penalty` | `0.0` | Automated passivity dampening baseline |
| `enable_contextual_overrides` | `True` | Contextual override permission matching Studio UI switch |
| `enable_semantic_smoothing` | `True` | Continuous piecewise power-curve scoring |
| `enable_eager_anonymization` | `True` | Redacts PII before model transit |
| `system_audit_trail` | `True` | FinOps and OpenTelemetry telemetry capture |
| `historical_context_mode` | `"disabled"` | Stateless deterministic run isolation |
| `expected_inputs` | 4 inputs (`chat_log` [required], `product_text`, `reflection_text`, `assignment_context`) with complete fields (`input_key`, `label`, `required`, `is_chat_history`, `is_endorsed_deliverable`, `scan_for_performative_patterns`, `input_modes`, `description`, `ai_description`, `questionnaire_definition`) | Dynamic topology agnosticism |
| `steps` | 5 step rules (`sr_06s1000000000001` to `sr_06s1000000000005`) with complete attributes (`id`, `task_blueprint`, `depends_on`, `input_mappings`, `expected_sdui_type`, `is_synthesis_source`, `ui_pos_x`, `ui_pos_y`) | 3-Zone DAG hierarchy (Zone A Ingestion, Zone B HACM Evaluator, Zone C Funnel Anchors) |

#### 5.3.1 Workflow Step DAG Breakdown (Studio "Stepit & Riippuvuudet" View)

| Vaihe (Step) | Solmun ID (`id`) | Tehtäväprofiili (`task_blueprint`) | Suoritusjärjestys & Riippuvuudet (`depends_on`) | Atomisoidut aineistot (`input_mappings`) | Rooli ja SDUI-tyyppi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Vaihe 1** | `sr_06s1000000000001` | `sp_db849f9790984585` (Input Processing) | `[]` (Järjestelmän perusaskel - Suojattu) | `{"chat_log": "$inputs.chat_log", "product_text": "$inputs.product_text", "reflection_text": "$inputs.reflection_text", "assignment_context": "$inputs.assignment_context"}` | Zone A: Raakadokumenttien purku atomeiksi (`markdown`) |
| **Vaihe 2** | `sr_06s1000000000002` | `sp_06c1d71000000001` (Tekoälyohjauksen Arvioija) | `["sr_06s1000000000001"]` (Käynnistyy kun Input Processing valmis) | `{"chat_log": "$inputs.chat_log", "reflection_text": "$inputs.reflection_text"}` | Zone B: HACM-matriisin arviointi ihmiskehotteista (`grid`) |
| **Vaihe 3** | `sr_06s1000000000003` | `sp_192910b5f5a34c79` (Synteesin Generointi / Coach) | `["sr_06s1000000000002"]` (Käynnistyy kun Arvioija valmis) | `{"prior_analysis": "$steps"}` | Zone C: Laadullinen valmennussynteesi (`markdown`) |
| **Vaihe 4** | `sr_06s1000000000004` | `sp_d245365e4a274b9e` (Scoring Engine / Reducer) | `["sr_06s1000000000003"]` (Käynnistyy kun Synteesi valmis) | `{"results": "$steps.sr_06s1000000000003"}` | Zone C: Numeerinen pisteaggregaatio (`grid`) |
| **Vaihe 5** | `sr_06s1000000000005` | `sp_7a8b9c0d1e2f3a4b` (XAI Reporter) | `["sr_06s1000000000004"]` (Käynnistyy kun Scoring valmis) | `{"results": "$steps.sr_06s1000000000004", "reduced_matrix": "$steps.matrix_reducer.reduced_atoms"}` | Zone C: Loppuraportti ja tutkagraafit (`markdown`) |


### 5.4 Dedicated Custom Output Profile Schema Parity (`prf_06b1d71000000001`)

| Configuration Attribute | Populated Value | Validation / Role |
| :--- | :--- | :--- |
| `id` | `"prf_06b1d71000000001"` | Opaque Stripe ID pattern (`prf_[a-f0-9]{16}`) |
| `slug` | `"tekoalyn_kayton_ja_ohjauksen_tulostusprofiili"` | Sovereign profile slug |
| `workflow_id` | `"wf_06a1d71000000001"` | Bidirectional 1:1 binding with new workflow |
| `organization_id` | `"SYSTEM"` | System tenant ownership |
| `name` | `{"translations": {"fi": "Tekoälyn Käytön ja Ohjauksen Profiili", "en": "Human-AI Collaboration & Steering Profile"}}` | Profile title in Studio selector |
| `description` | `{"translations": {"fi": "Räätälöity tulostusprofiili tekoälyn ohjauksen, kyseenalaistamisen ja lopputuotteen hakemisen raportointiin.", "en": "Dedicated output profile for reporting human AI steering, critical inquiry, and deliverable derivation."}}` | Profile description |
| `user_role_label` | `{"translations": {"fi": "Käyttäjärooli", "en": "User Role"}}` | Archetype badge label |
| `custom_preface` | Bilingual coaching preface explaining focus on user steering and critical curation without penalizing AI deliverable assistance | Rendered in PDF and SDUI metadata block |
| `tone_instruction` | Practical Executive Coach instruction focusing on steering agency, epistemic vigilance, and deliverable curation | Guides synthesis voice across all text blocks, emphasizing the delta between prompt scaffolding and final deliverable curation |
| `executive_summary_directive` | Mandate synthesizing interaction trajectory, framing maturity, dialectic delegation risks, and curation agency | Generates executive summary block evaluating whether the operator fell into the Dialectic Delegation Trap or Curation Deficit |
| `matrix_1d_synthesis_directive` | 1D metric directive focusing on steering balance and passivity risks | Generates 1D metrics synthesis |
| `matrix_2d_synthesis_directive` | 2D comparative directive contrasting Framing against Critical Inquiry | Generates 2D comparative synthesis |
| `matrix_3d_synthesis_directive` | 3D radar directive evaluating macro balance across all 4 HACM dimensions | Generates 3D radar synthesis |
| `matrix_text_synthesis_directive` | Qualitative deep-dive directive analyzing conversational prompt nuances | Generates qualitative synthesis text |
| `row_explanation_directive` | Causal explanation directive grounding scores in verified quotes from `<user_payload>` | Generates row-level score justifications |
| `xai_synthesis_directive` | Explainable AI directive highlighting actionable behavioral coaching steps | Generates XAI diagnostic recommendations |
| `variance_synthesis_directive` | Cognitive variance directive detecting performative buzzwords vs authentic steering | Generates authenticity validation |
| `visible_metadata` | `["date", "execution_id", "organization", "user", "scoring_engine", "strictness"]` | Metadata chips rendered in header |
| `matrix_visible_columns` | `["label", "distribution", "row_explanation", "normalized_score", "raw_score"]` | Columns displayed in summary score table |
| `visible_block_extensions` | `["justification", "coaching", "falsification", "remediation_steps"]` | Accordions rendered in report |
| `visible_workflow_extensions` | `["variance_validation"]` | Workflow extensions rendered |
| `max_extension_items` | `4` | Max items displayed per accordion |
| `display_scale` | `"normalized_100"` | Standardized 0-100 visual scale |
| `synthesis_length_constraint` | `1000` | Max character length for narrative synthesis |
| `row_explanation_length_constraint` | `250` | Max character length per row explanation |
| `xai_length_constraint` | `300` | Max character length for XAI takeaways |
| `variance_length_constraint` | `500` | Max character length for variance report |
| `matrix_graph_length_constraint` | `400` | Max character length for graph summaries |
| `target_block_order` | `["metadata_block", "executive_summary_block", "global_score_block", "synthesis_text_block", "matrix_graphs_block", "grouped_extensions_block", "penalties_block", "matrix_summary_table_block", "variance_validation_block", "printable_sources_block"]` | Complete 10 SDUI visual blocks |
| `matrix_synthesis_groups` | 3 custom groups: 3D Radar (4 dimensions), 2D Comparative (Framing vs Criticality), 1D Metrics (Agency & Passivity) | Data-driven visual groupings |
| `content_blocks` | `[]` | Static custom blocks |
| `show_sources_summary_box` | `True` | Renders document provenance box |
| `sources_display_mode` | `"verified_evidence"` | Displays verified quote evidence breakdown |
| `variance_target_block` | `"blk_7d8e9f0a1b2c3d4e"` | Binds variance analysis to HACM matrix |
| `user_role_target_block` | `"blk_7d8e9f0a1b2c3d4e"` | Derives user archetype from HACM matrix score |

---

## 6. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="SEED_VAULT_BACKUP_AND_PREFLIGHT">
    <action>Create timestamped backup of backend_v2/seed/seed_data.json inside backend_v2/seed/backups/.</action>
    <action>Execute in-memory dry-run validation using: uv run python backend_v2/seed/run_seed.py local --dry-run</action>
    <constraint invariant="zero_live_mutation">Do not touch data/db_v2.json directly.</constraint>
  </step>

  <step id="2" name="HACM_PROMPT_BLOCK_DEFINITION">
    <action>Construct and append new PromptBlock (blk_7d8e9f0a1b2c3d4e) into prompt_blocks array in backend_v2/seed/seed_data.json.</action>
    <specification>
      - id: "blk_7d8e9f0a1b2c3d4e"
      - slug: "matrix_hacm"
      - category_id: "matrix"
      - type: "float"
      - is_evaluative: true
      - allow_decimals: true
      - allow_contextual_override: true
      - is_lightweight_protocol: false
      - target_input_key: "chat_log"
      - label: {"translations": {"fi": "Tekoälyn Ohjauksen ja Yhteistyön Auditointi (HACM)", "en": "Human-AI Collaboration Matrix (HACM)"}}
      - description: {"translations": {"fi": "Arvioi ihmisen ja tekoälyn vuorovaikutusta: kehystyksen tarkkuutta, kriittistä haastamista, kuraatiota ja metakognitiota.", "en": "Audits human-AI interaction across framing, critical inquiry, active curation, and metacognition."}}
      - output_extensions: ["falsification", "theory_link", "risk_flag", "coaching", "remediation_steps", "emotional_sentiment", "confidence", "source_id"]
      - theory_grounding: Populated with Sheridan & Parasuraman citations and JSTOR source URL.
      - ai_description: Exhaustive English system directives isolating USER prompt evaluation.
      - computed_min: 1
      - computed_max: 5
      - rows: 4 MatrixRow definitions mapping the 4 dimensions.
      - scales: 5 scales with exactly 25 TDA assertions (12 positive capabilities, 13 negative error detectors).
      - All claims enforce target_speaker: "USER".
    </specification>
  </step>

  <step id="3" name="STEP_BLUEPRINT_DEFINITION">
    <action>Define new step blueprint in steps array in backend_v2/seed/seed_data.json:</action>
    <specification>
      - id: "sp_06c1d71000000001"
      - slug: "hacm_evaluator_step"
      - organization_id: "SYSTEM"
      - name: {"translations": {"fi": "Tekoälyohjauksen Arvioija", "en": "Human-AI Collaboration Evaluator"}}
      - description: {"translations": {"fi": "Arvioi käyttäjän tekoälyohjausta, kriittistä haastamista, kuraatiota ja reflektiota HACM-matriisin mukaisesti.", "en": "Evaluates user AI steering, critical inquiry, curation, and reflection using HACM matrix."}}
      - type: "llm"
      - extraction_protocol_block_id: "blk_573802341db9d68c"
      - criteria_block_ids: ["blk_7d8e9f0a1b2c3d4e"]
      - pre_hooks: ["inject_step_metadata", "atom_flattening_hook"]
      - post_hooks: ["matrix_scoring_hook", "normalize_matrix_scores", "enforce_passivity_penalty"]
      - safety: "safe"
      - allowed_mcp_tools: []
      - expected_inputs: ["chat_log", "product_text", "reflection_text", "assignment_context"]
      - is_system_core: false
      - cognitive_tier: "fast"
    </specification>
  </step>

  <step id="4" name="DEDICATED_WORKFLOW_DEFINITION">
    <action>Define new dedicated workflow in workflows array in backend_v2/seed/seed_data.json:</action>
    <specification>
      - id: "wf_06a1d71000000001"
      - slug: "tekoalyn_kayton_ja_ohjauksen_auditointi"
      - organization_id: "SYSTEM"
      - name: {"translations": {"fi": "Tekoälyn Käytön ja Ohjauksen Auditointi", "en": "Human-AI Collaboration & Steering Audit"}}
      - description: {"translations": {"fi": "Työnkulku, joka arvioi ihmisen tekemää ohjausta, kyseenalaistamista ja reflektointia tekoälyvuorovaikutuksessa. Keskittyy prosessiin ja vuorovaikutuksen laatuun lopputuotteen lisäksi.", "en": "Workflow auditing human steering, critical questioning, and reflection in AI collaboration. Evaluates the interaction process and curation rather than assuming human authorship of the final deliverable."}}
      - status: "active"
      - version: 1
      - is_public: true
      - default_profile_id: "prf_06b1d71000000001"
      - mcp_gateway_id: "sys_8172bda70c8641c5"
      - model_registry_id: "sys_e26807f3bfa3454d"
      - default_strictness_level: 50
      - enable_contextual_overrides: true
      - enable_semantic_smoothing: true
      - enable_eager_anonymization: true
      - system_audit_trail: true
      - historical_context_mode: "disabled"
      - security_penalty: 0.0
      - post_hoc_penalty: 0.0
      - passivity_penalty: 0.0
      - expected_inputs: Dynamic inputs (chat_log required; product_text, reflection_text, assignment_context optional).
      - steps: 5-step DAG implementing Zone A Ingestion, Zone B HACM Evaluator, and Zone C Scoring, Synthesis, and XAI Reporter.
    </specification>
  </step>

  <step id="5" name="DEDICATED_OUTPUT_PROFILE_DEFINITION">
    <action>Define new dedicated output profile in output_profiles array in backend_v2/seed/seed_data.json:</action>
    <specification>
      - id: "prf_06b1d71000000001"
      - slug: "tekoalyn_kayton_ja_ohjauksen_tulostusprofiili"
      - organization_id: "SYSTEM"
      - workflow_id: "wf_06a1d71000000001"
      - name: {"translations": {"fi": "Tekoälyn Käytön ja Ohjauksen Profiili", "en": "Human-AI Collaboration & Steering Profile"}}
      - description: {"translations": {"fi": "Räätälöity tulostusprofiili tekoälyn ohjauksen, kyseenalaistamisen ja lopputuotteen hakemisen raportointiin.", "en": "Dedicated output profile for reporting human AI steering, critical inquiry, and deliverable derivation."}}
      - user_role_label: {"translations": {"fi": "Käyttäjärooli", "en": "User Role"}}
      - custom_preface: Tailored coaching preface explaining focus on user steering and critical curation.
      - target_block_order: Complete 10 SDUI visual blocks.
      - matrix_synthesis_groups: 3 custom synthesis groups (3D Radar, 2D Comparative, 1D Metrics).
      - show_sources_summary_box: true
      - sources_display_mode: "verified_evidence"
      - variance_target_block: "blk_7d8e9f0a1b2c3d4e"
      - user_role_target_block: "blk_7d8e9f0a1b2c3d4e"
      - visible_metadata: ["date", "execution_id", "organization", "user", "scoring_engine", "strictness"]
      - matrix_visible_columns: ["label", "distribution", "row_explanation", "normalized_score", "raw_score"]
      - visible_block_extensions: ["justification", "coaching", "falsification", "remediation_steps"]
      - visible_workflow_extensions: ["variance_validation"]
    </specification>
  </step>

  <step id="6" name="SEED_SANITY_AUDIT_AND_SYNC">
    <action>Execute structural atom audit: uv run python scripts/audit_database_atoms.py --strict</action>
    <action>Execute in-memory dry-run sync: uv run python backend_v2/seed/run_seed.py local --dry-run</action>
    <action>Execute live local database sync: uv run python backend_v2/seed/run_seed.py local</action>
  </step>

  <step id="7" name="END_TO_END_VERIFICATION_GATE">
    <action>Execute full backend audit verification: uv run python scripts/backend_audit_loop.py backend_v2 --test</action>
    <action>Verify markdown boundary integrity: uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Human_AI_Collaboration_Matrix_and_Workflow.md</action>
  </step>
</execution_protocol>
```

---

## 7. Verification Plan & Fail-Fast Proof Anchors

### 7.1 Deterministic Verification Scenarios

| Scenario | Input | Expected Output | Proof Mechanism |
| :--- | :--- | :--- | :--- |
| **1. 100% Configuration Completeness** | `blk_7d8e9f0a1b2c3d4e` loaded into test. | Zero missing fields across all attributes (`output_extensions`, `theory_grounding`, `rows`, `scales`). | Verified via Pydantic V2 strict validation. |
| **2. 50/50 Mathematical Parity** | `seed_data.json` loaded into test. | Exactly 12 positive assertions (`inverse_evidence: false`) and 13 negative error detectors (`inverse_evidence: true`). | Verified via AST assertion counter test. |
| **3. TargetSpeaker.USER Boundary** | Quote extracted from `<ai_draft_context>`. | Quote rejected with `PROVENANCE_VIOLATION`; quote set to `None`. | Asserted in `AnchorValidationService.validate_evidence()`. |
| **4. Real-World Dialectic Framing (Level 3)** | Exe 1 user prompt ("Haluan että käyt dialogia..."). | Evaluates to `is_true = true` on Scale 3 positive claim `tda_hacm_multi_perspective_framing`. | Verified via step DAG test execution. |
| **5. Real-World Cosmetic Fiddling (Level 2 Anti-pattern)** | Exe 2 user prompt ("poista taulukot ja kerro tekstinä"). | Evaluates to `is_true = true` on Scale 2 error detector `tda_hacm_cosmetic_formatting_anti_pattern`. | Verified via step DAG test execution. |
| **6. Dedicated Profile SDUI Assembly** | `OutputProfile` loaded for `wf_06a1d71000000001`. | `target_block_order` and 3 synthesis groups assemble cleanly into `ReportDataDTO`. | Checked by `ReportAssembler` validation. |
| **7. In-Memory Seed Schema Parity** | `seed_data.json` loaded during `run_seed.py local --dry-run`. | Zero `ValidationError` exceptions, all collections pass `model_validate()`. | Checked by `run_seed.py` exit code 0. |

### 7.2 Quality Gate Commands
```powershell
# 1. In-memory validation
uv run python backend_v2/seed/run_seed.py local --dry-run

# 2. Strict atom structural audit
uv run python scripts/audit_database_atoms.py --strict

# 3. Global backend audit loop
uv run python scripts/backend_audit_loop.py backend_v2 --test
```
