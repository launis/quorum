# Implementation Plan: Scoring Double-Inversion Elimination, Multi-Input Context Target Routing & Verbatim Quote Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

**Associated Research & Audits:**
- @[docs/audit/feature_audit_theory_grounding_calibration.md]
- @[docs/audit/feature_audit_bipolar_matrix_scores.md]
- @[docs/audit/feature_audit_context_target_inputs.md]  
**Execution Verification Target:** `exe_88267cb7b3cf4718ae76b7dbce04a92e`

---

## User Review Required

> [!IMPORTANT]
> **1. Eliminating the Double-Inversion Bug & Restoring Natural Score Dispersion:**
> As established in @[docs/audit/feature_audit_bipolar_matrix_scores.md], the perceived bipolarity (either `0 / 5` or `5 / 5` on matrix levels) was caused by `backend_v2/hooks/scoring/matrix_hook.py`.
> When the upstream LLM sensor verified an inverse-evidence atom as defect-free (`status = ExecutionStatus.PASSED`), `matrix_hook.py` executed `is_satisfied = not tda.inverse_evidence`, flipping `PASSED` into `FALSE` (`0 / 5` hits).
> Because Level 1 in calibrated matrices consists of fatal-flaw inverse detectors, clean text crashed at Level 1 (`hits = 0`), halting the Guttman waterfall and pinning normalized scores to `0.0%`.
> In reality, the live sensor data from `exe_88267cb7b3cf4718ae76b7dbce04a92e` shows rich, continuous variance across levels:
> - **Toulmin:** L1: 4/5, L2: 3/5, L3: 4/5, L4: 5/5, L5: 5/5 $\rightarrow$ **75.0%** (UI showed 0.0%)
> - **Archivist:** L1: 5/5, L2: 4/5, L3: 5/5, L4: 3/5, L5: 2/5 $\rightarrow$ **73.0%** (UI showed 2.2%)
> - **Causal Analyst:** L1: 5/5, L2: 5/5, L3: 5/5, L4: 3/5, L5: 2/5 $\rightarrow$ **73.0%** (UI showed 5.4%)
> - **Falsifier:** L1: 5/5, L2: 5/5, L3: 4/5, L4: 3/5 $\rightarrow$ **86.7%** (UI showed 2.5%)
> - **Goodhart:** L1: 3/5, L2: 3/5, L3: 3/5, L4: 2/5, L5: 3/5 $\rightarrow$ **30.8%** (UI showed 0.0%)
> - **Taskguard:** L1: 5/5, L2: 5/5, L3: 0/5, L4: 0/5, L5: 0/5 $\rightarrow$ **25.0%** (UI showed 0.0%)

> [!IMPORTANT]
> **2. Resolving Multi-Input Context Targets & Eliminating "Lopputuote" Monolith (Cognitive SSOT Architecture):**
> As established in @[docs/audit/feature_audit_context_target_inputs.md], `matrix_domain_parser.py` contained a dictionary iteration loop that broke on the first `$inputs.` key, unconditionally assigning `"product_text"` $\rightarrow$ `"Lopputuote"` to all 13 matrices, despite the workflow step mapping all three distinct inputs (`product_text`, `chat_log`, `reflection_text`).
> 
> **Epistemic Foundations: Three Distinct Input Streams**
> 1. **Deliverable / Final Product (`product_text`):** The definitive end-result (memo, report, code) evaluated for external rigor and executive readiness.
> 2. **Process Dialogue (`chat_log`):** The chronological co-creation exchange between human operator and AI, capturing operator steering, intellectual labor, and prompt discipline.
> 3. **Meta-Cognitive Reflection (`reflection_text`):** Post-hoc self-assessment capturing operator critical distance and self-awareness.
> 
> **The Canonical Cognitive SSOT Map:**
> 
> | Evaluation Focus | Step Role & Matrix Family | Epistemic Rationale |
> | :--- | :--- | :--- |
> | **A. Deliverable Only** (`product_text`) | **Logician:** `blk_440a5fef9331451b` (Toulmin Argumentation)<br>**Causal Analyst:** `blk_c5804a9143c34cb1` (Causal Inference)<br>**Coach:** `blk_f921c7c0989b47e8` (Bloom's Taxonomy) | **Evaluates decision-grade output.** Brainstorming or tentative conversational probes in chat must never penalize the structural logic of the final deliverable. |
> | **B. Process & Steering Only** (`chat_log`) | **Overseer:** `blk_53f32679aa514fcb` (Goodhart's Law)<br>**Judge:** `blk_ff72c2d79edb4ebf` (Supreme Adjudicator / Process Ownership) | **Evaluates human cognitive leadership.** Cannot be inferred from the final product; strictly visible in prompt phrasing, critical counter-probes, and resistance to AI sycophancy. |
> | **C. Holistic Process Integrity** (`all`) | **Profiler:** `blk_109dab5b6b3f403a` (Kahneman Dual Process)<br>**Falsifier:** `blk_b476f89fb732448c` (Falsification Audit)<br>**Archivist:** `blk_fb15f8dcf23f4865` (Archival Compliance)<br>**Analyst:** `blk_80732a33fe1947ee` (Taskguard Responsibility)<br>**Causal Abductive:** `blk_c3bc5f3eb8e74110` (Causal & Abductive Integrity)<br>**Reporting:** `blk_f6e286f050c94d60` (Explainability), `blk_22e3598e06414409` (Epistemic Humility), `blk_6b8c766185294f7e` (XAI Reporter) | **Evaluates end-to-end process coherence:**<br>1. *Taskguard:* Was the initial mandate maintained from prompt to product?<br>2. *Archivist:* Did factual verifications survive telephone-game degradation into the output?<br>3. *Profiler & Falsifier:* Were cognitive biases recognized in chat, refuted in the product, and acknowledged in reflection? |
> 
> **Three-Tier Resolution Architecture (SSOT):**
> 1. **Matrix Domain SSOT (`MatrixPromptBlock.target_input_key`):** Persisted in `seed_data.json` specifying the matrix's innate target (`"product_text"`, `"chat_log"`, or `"all"`).
> 2. **Step-Level Input Governance (`StepRule.input_mappings`):** Configured via Studio UI (Tab 3: Steps & Dependencies). Governs which inputs are fed to the step.
> 3. **Deterministic Presentation Engine (`matrix_domain_parser.py`):**
>    - If step maps a single input $\rightarrow$ resolve that input's localized label directly.
>    - If step maps multiple inputs (e.g. Profiler Step 5): inspect `pb_meta.target_input_key`. Dedicated targets (`chat_log` $\rightarrow$ "Chat Log", `product_text` $\rightarrow$ "Deliverable") resolve specifically, while holistic matrices resolve to `"all"` ("All Inputs").

> [!IMPORTANT]
> **3. Restoring "Evidence Quote" (Verbatim Quotes in Original Source Language):**
> The table column "Evidence Quote" ("Tekstin havainto") is currently empty (`-`) because:
> 1. `BooleanEvaluationResult` Pydantic schema lacked the `source_quote` field.
> 2. `MATRIX_SENSOR_SYSTEM_PROMPT` did not instruct the model to extract an exact quote from the analyzed text.
> 3. `tda_engine.py` initialized `source_quote=None` and `result_projector.py` read from `node.atom.source_quote` (which was always `None`), discarding the LLM extraction result.
> 
> **Linguistic Directive & Raw Source Language Mandate:**
> As clarified and governed by architectural rules (`LANGUAGE_MANDATE` Exception 2 and `strict_physical_anchoring_mandate`):
> - **Raw source quote (`source_quote`) MUST ALWAYS remain 100% in the original language of the source text and strictly verbatim.** If the input is Finnish, the quote remains in Finnish. It must NEVER be translated, condensed, corrected, or converted into another language.
> - **Reasoning vs. Localized Explanations:** Internal cognitive chain-of-thought (`reasoning`) is generated in English for maximum reasoning fidelity, while user-facing analyses and explanations (`row_explanation`, `coaching`) are produced in the user's target locale (`target_locale`, e.g., `fi`), exactly as mandated by `worker.py` and `linguistic_directives.py`.
> - Transit `source_quote` through the Pydantic V2 schema chain: `AtomExecutionState` $\rightarrow$ `AtomResultDTO` $\rightarrow$ `ScorecardAtomDTO.exact_quotes` $\rightarrow$ `sdui_matrix_table_widget.dart`, rendering direct verbatim quotes by level in the "Evidence Quote" table column.

> [!NOTE]
> **4. Preserving Functional Asterisks (`*` and `**`):**
> Per user confirmation, the asterisk indicators (`*` for evaluative matrices affecting global average, `**` for cognitive contextual override permitted) are functional indicators matching the scorecard legend (`matrixEvaluativeAsteriskLegend` and `matrixOverrideAsteriskLegend`). They are preserved intact in all UI views.

---

## 5-Column Architectural Directives (System 2 Deconstruction)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Matrix Hook: Double-Inversion Elimination**<br>`@[backend_v2/hooks/scoring/matrix_hook.py#L38-L487]` | Banned double-negation `is_satisfied = not tda.inverse_evidence` that inverts an already-normalized sensor pass. Banned `scales or []` dead code (`MatrixPromptBlock.scales` has `min_length=1`). Banned `matrix_extensions_by_block[pb_id] if pb_id in ...` ternary (provably always present from L279 init; banned `.get()` fallback). Banned `total_evals or 1` literal default. Banned `.get("_dlq_status")` dict lookup on L317 (QGR016). | Sovereign contract: Upstream sensor `ExecutionStatus.PASSED` means the level assertion is satisfied. Direct access to provably-initialized state. Division protection via `max(1, total_evals)`. Evaluate `effective_override` on failed assertions only. Explicit key checks for DLQ status. | Zero custom scoring wrappers or secondary mapping tables. Re-uses native `ExecutionStatus` domain invariants directly. | `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test`. AST guardrail `_ast_guardrails.py` verifies 0 QGR016 warnings. |
| **TDA Engine: Python 2 Exception Syntax (CRITICAL)**<br>`@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L231]` | Banned Python 2 exception syntax `except TypeError, KeyError:` on line 88 that causes SyntaxError / silent shadowing of `KeyError`. | Standard Python 3 exception handling: `except (TypeError, KeyError):`. Clean fail-fast error trapping. | Zero new abstractions. Single-line surgical fix restoring syntactic integrity. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py --test`. |
| **ScorecardAtomDTO: Python 2 Exception Syntax (CRITICAL — Tier 0 Discovery)**<br>`@[backend_v2/models/dtos/matrix_scorecard.py#L127]` | Banned Python 2 exception syntax `except TypeError, ValueError:` on line 127 that silently binds `TypeError` to a local variable named `ValueError`, failing to trap actual `ValueError` on the critical SDUI rendering path. | Standard Python 3 exception handling: `except (TypeError, ValueError):`. | Zero new abstractions. Single-line surgical fix. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/matrix_scorecard.py --test`. |
| **TopologicalEvaluator: Banned `.get()` (Tier 0 Discovery)**<br>`@[backend_v2/services/orchestrator/topological_evaluator.py#L108]` | Banned `results.get(node.atom.tda_id)` dictionary lookup violating `the_duct_tape_ban` and QGR016. | Explicit key membership check: `node.atom.tda_id in results` with direct access `results[node.atom.tda_id]`. | Zero new abstractions. Surgical fix within already-targeted file. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/topological_evaluator.py --test`. |
| **Matrix Domain Parser: Deterministic Target Resolution**<br>`@[backend_v2/services/matrix_domain_parser.py#L32-L559]` | Banned legacy dictionary iteration loop `for mapped_val in input_mappings.values(): break` that unconditionally defaulted to `product_text` ("Lopputuote"). Banned QGR016 ternary fallbacks across metadata and extension extraction. Banned `.get(atom_id)` dictionary lookup on L378. | Deterministic resolution: 1) `pb_meta.target_input_key` priority, 2) Single `$inputs.*` mapping, 3) Domain mapping: `chat_log` ("Keskusteluhistoria") for goodhart/judge, `product_text` ("Lopputuote") for toulmin/bloom/causal, else `"all"` ("Kaikki syötteet"). Explicit membership check `atom_id in step_evals_map`. | No runtime regex inspection or dynamic file-reading heuristics. Pure domain mapping based on existing workflow metadata. | `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test`. 100% passing quality gates. |
| **Sensor Quote Extraction: Verbatim Language Preservation**<br>`@[backend_v2/services/orchestrator/extractive_sensor_service.py#L26-L435]`<br>`@[backend_v2/models/prompts/matrix_evaluation.py#L1-L27]`<br>`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L209]` | Banned discarding `source_quote` from LLM extraction. Banned translating or paraphrasing extracted quotes (LANGUAGE_MANDATE Exception 2). Banned fuzzy chimera quotes under `strict_physical_anchoring_mandate`. Banned injecting dynamic `locale` into static caching prefix (`ephemeral_caching_topology`). Banned unconstrained quote lengths. | `BooleanEvaluationResult` defines `source_quote: Annotated[str | None, Field(default=None, max_length=500)]` with `@field_validator(mode="before")` sentence-boundary truncation per `graceful_text_truncation_validator`. Kept 100% in raw original language. Bo3 voting consolidates winning `source_quote`. Static language-AGNOSTIC `<evidence_extraction_mandate>`. | Option A direct extraction in single sensor pass (Zero extra LLM latency, zero new microservices, zero prompt bloat). | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test`. Strict Pydantic V2 schema validation (`extra="forbid"`). |
| **DAG Pipeline Transit & 1-Hop Callers**<br>`@[backend_v2/models/dtos/dag_models.py#L114-L145]`<br>`@[backend_v2/services/orchestrator/topological_evaluator.py#L18-L177]`<br>`@[backend_v2/services/orchestrator/enriched_dag_executor.py#L26-L187]`<br>`@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L231]`<br>`@[backend_v2/services/orchestrator/result_projector.py#L17-L136]` | Banned reading uninitialized `node.atom.source_quote` (static seed) in `ResultProjector` for both `AtomResultDTO` and `HydratedAtomDTO`. Banned silent fallback to empty string when quote is missing. Banned untyped 3-tuple callback when 4-tuple is transited. | Transits `source_quote` via `AtomExecutionState.source_quote` $\rightarrow$ `AtomResultDTO.source_quote` $\rightarrow$ `ScorecardAtomDTO.exact_quotes` (`QuoteEvidenceDTO`). `HydratedAtomDTO` also hydrated from `state.source_quote`. `TopologicalEvaluator` and `EnrichedDagExecutor` callback signatures and `tda_engine.py` updated to 4-tuple. | Zero secondary database writes or duplicate event traces. Direct transit through existing frozen DAG state envelopes. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/result_projector.py --test`. SDUI Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`. |

---

## Falsification & Red-Teaming Analysis (Checklist)

1. **Failure Mode 1: Sensor Hallucinates Source Quote When Rejecting Defect (Inverse Evidence Null Case):**
   - *Attack:* If an inverse-evidence atom asserts "No unhedged causal claims", and the text is clean, the sensor votes `is_true = false` (no defect). Does the model hallucinate a fake quote for a non-existent defect?
   - *Mitigation & Proof:* The `<evidence_extraction_mandate>` and `BooleanEvaluationResult` field description explicitly instruct: *"Exact verbatim sentence or clause extracted directly from the context text in its original language, substantiating or violating this claim, or null if absent."* If no violation or substantiation exists, `source_quote` is returned as `null` / `None`. Furthermore, `AtomResultDTO.validate_cognitive_vs_system_state` forcibly strips `source_quote` if status is `FAILED` or if `contextual_override=True`. `ScorecardAtomDTO` receives `exact_quotes = []`, preventing phantom text cards in the UI.
2. **Failure Mode 2: Multi-Language Bleed in Verbatim Quote Extraction:**
   - *Attack:* If the user prompt instructions or `linguistic_directives.py` instruct target language `fi`, could an English source text have its quotes translated into Finnish, violating `LANGUAGE_MANDATE` Exception 2 and `strict_physical_anchoring_mandate`?
   - *Mitigation & Proof:* `LANGUAGE_MANDATE` Exception 2 explicitly guarantees: *"The JSON field exact_quotes and source_quote MUST ALWAYS remain in the raw, original language of the source text. NEVER translate, paraphrase, or modify the language of the extracted quotes."* In `MatrixSensorPromptBuilder.build_caching_prefix()`, `GLOBAL_MANDATES_XML` is injected into the static prefix, locking this constraint at the foundational token level.
3. **Failure Mode 3: Context Target Collision in Dynamic Workflows:**
   - *Attack:* If a future workflow defines dynamic custom inputs other than `chat_log`, `product_text`, and `reflection_text`, does the hardcoded fallback break?
   - *Mitigation & Proof:* `pb_meta.target_input_key` provides the primary Single Source of Truth (SSOT). If missing, `input_mappings` from `StepRule` inspects `$inputs.*`. If multiple inputs exist without explicit metadata, it falls back to `"all"` ("Kaikki syötteet") safely without crashing.
4. **Failure Mode 4: ISTQB Anti-Happy-Path Coverage Deficit:**
   - *Requirement:* Mandatory minimum 2 negative boundary cases per feature.
   - *Proof:* In scoring hook, negative partition covers `ExecutionStatus.FAILED` for both positive and inverse atoms (verifying `final_state = "FALSE"`). In domain parser, negative partition covers missing `input_mappings`, unknown keys, and empty scales. In extractive sensor, negative partition covers `source_quote = None`, whitespace-only quotes, and Bo3 consensus splits.
5. **Failure Mode 5: Cache Prefix Invalidation from Locale Injection (Tier 0 Research Discovery):**
   - *Attack:* Injecting `build_linguistic_context(locale)` into `MatrixSensorPromptBuilder.build_caching_prefix()` alters the system prompt prefix per locale (`fi` vs `en`), shattering context caching efficiency (~2x token latency and cost explosion).
   - *Mitigation & Proof:* The `<evidence_extraction_mandate>` in `MATRIX_SENSOR_SYSTEM_PROMPT` is strictly **language-agnostic** (`"Extract the exact verbatim sentence or clause directly from the context text in its original language, without translating or paraphrasing."`). The caching prefix remains 100% static and invariant across all executions, satisfying `ephemeral_caching_topology` and `high_fidelity_prompting_and_caching`.
6. **Failure Mode 6: TopologicalEvaluator and 1-Hop Caller Callback Signature Breakage:**
   - *Attack:* Expanding the batch callback return from 3-tuple to 4-tuple without updating `EnrichedDagExecutor` and `tda_engine.py` (and test fixtures) crashes DAG execution at runtime with `ValueError: too many values to unpack (expected 3)`.
   - *Mitigation & Proof:* `enriched_dag_executor.py`, `tda_engine.py`, `test_enriched_dag_executor.py`, and `test_topological_evaluator.py` are explicitly included in TARGET scope, and the callback type annotations and unpacking logic are synchronized to 4-tuple `(status, reasoning, source_quote, extensions)`.
7. **Failure Mode 7: `HydratedAtomDTO` Retains Static Seed in `result_projector.py`:**
   - *Attack:* Updating `AtomResultDTO` to read from `state.source_quote` while leaving `HydratedAtomDTO` reading from `node.atom.source_quote` leaves ontology references with `source_quote=None`.
   - *Mitigation & Proof:* Both `AtomResultDTO` and `HydratedAtomDTO` in `ResultProjector.project()` are updated to read `state.source_quote if state else node.atom.source_quote`.
8. **Failure Mode 8: SDUI / PDF Semantic Parity Drift:**
   - *Attack:* Populating `exact_quotes` in `ScorecardAtomDTO` alters SDUI table rendering and PDF generation without parity verification.
   - *Mitigation & Proof:* `backend_v2/tests/integration/test_sdui_semantic_parity.py` is integrated into Phase 6 completion gates.
9. **Failure Mode 9: TDA Engine Python 2 Exception Syntax Crash (CRITICAL LATENT BUG):**
   - *Attack:* `except TypeError, KeyError:` on `tda_engine.py` line 88 either throws a `SyntaxError` in Python 3.14 or binds `TypeError` to a local variable named `KeyError`, completely failing to trap actual `KeyError` exceptions when parsing starved data blackboard payloads.
   - *Mitigation & Proof:* Corrected to standard Python 3 tuple syntax `except (TypeError, KeyError):` in Phase 1 cleanups, verified by `backend_audit_loop.py`.
10. **Failure Mode 10: Quote Length Explosion from LLM Generation:**
    - *Attack:* The LLM extracts an entire paragraph (500+ characters) as a "verbatim quote", inflating `ScorecardAtomDTO` payloads and disrupting SDUI table cell rendering.
    - *Mitigation & Proof:* `BooleanEvaluationResult.source_quote` is guarded with `max_length=500` and a sentence-boundary truncation `@field_validator(mode="before")` adhering strictly to `graceful_text_truncation_validator`.
11. **Failure Mode 11: Banned `.get()` Dictionary Access in Matrix Hook & Domain Parser:**
    - *Attack:* Lines `ev_dict_tmp.get("_dlq_status")` (`matrix_hook.py#L317`) and `step_evals_map.get(atom_id)` (`matrix_domain_parser.py#L378`) violate `the_duct_tape_ban` and trigger QGR016 warnings.
    - *Mitigation & Proof:* Refactored in Phase 1 cleanups to explicit key membership checks (`atom_id in step_evals_map`) and typed sentinel lookups, verified by `_ast_guardrails.py`.

---

## Proposed Changes

### Python Backend: Domain Models & Localization

#### [MODIFY] @[backend_v2/models/domain/prompt_blocks.py#L64-L108]
- In `MatrixPromptBlock`, add `target_input_key: Annotated[str | None, Field(default=None, description="Explicit target input key from workflow expected_inputs (specifically: 'chat_log', 'product_text', 'all').")] = None` (strictly adhering to PEP 593 `Annotated` syntax per `pydantic_annotated_fields_mandate` and `ki_zero_permissive_typing.md`).

#### [MODIFY] @[backend_v2/seed/seed_data.json]
- In `seed_data.json`, populate `target_input_key` across all 13 matrix prompt blocks via their canonical Opaque Stripe IDs (strictly adhering to `slug_data_relation_ban` and `matrix_slug_identification_ban`):
  - `blk_440a5fef9331451b` (Toulmin Argumentation): `"product_text"`
  - `blk_f921c7c0989b47e8` (Bloom's Taxonomy): `"product_text"`
  - `blk_c5804a9143c34cb1` (Causal Inference): `"product_text"`
  - `blk_53f32679aa514fcb` (Goodhart's Law): `"chat_log"`
  - `blk_ff72c2d79edb4ebf` (Supreme Adjudicator): `"chat_log"`
  - `blk_109dab5b6b3f403a` (Kahneman Dual Process): `"all"`
  - `blk_b476f89fb732448c` (Falsification Audit): `"all"`
  - `blk_fb15f8dcf23f4865` (Archival Compliance): `"all"`
  - `blk_80732a33fe1947ee` (Taskguard Responsibility): `"all"`
  - `blk_c3bc5f3eb8e74110` (Causal & Abductive Integrity): `"all"`
  - `blk_f6e286f050c94d60` (Explainability & Transparency): `"all"`
  - `blk_22e3598e06414409` (Epistemic Humility): `"all"`
  - `blk_6b8c766185294f7e` (XAI Synthesis Reporter): `"all"`

#### [MODIFY] @[backend_v2/l10n/fi.json#L50-L65]
- Add localization key `"matrix_target_all": "Kaikki syötteet"` and `"matrix_target_chat_log": "Keskusteluhistoria"`.

#### [MODIFY] @[backend_v2/l10n/en.json#L50-L65]
- Add localization key `"matrix_target_all": "All Inputs"` and `"matrix_target_chat_log": "Chat Log"`.

---

### Python Backend: LLM Sensor & Quote Extraction Pipeline (Option A)

#### [MODIFY] @[backend_v2/models/prompts/matrix_evaluation.py#L1-L27]
- Add `<evidence_extraction_mandate>` to `MATRIX_SENSOR_SYSTEM_PROMPT`:
  - Require that whenever a claim is confirmed or violated in the text, extract the exact verbatim sentence or clause into `source_quote`.
  - **Absolute Language Preservation:** `source_quote` MUST remain in the raw, original language of the source text. NEVER translate, paraphrase, summarize, or alter the language of the extracted quotes.
  - If a claim is rejected because the text does not mention the subject, `source_quote` must be set to `null`.
  - Absolute ban on chimeric or altered quotes: the quote must physically exist in the source text (`str.find` lexical integrity).

#### [MODIFY] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L209]
- Ensure 100% static cacheability in `build_caching_prefix` and `MatrixSensorPromptBuilder`:
  - **Ephemeral Caching Topology Mandate:** DO NOT inject dynamic `locale` parameter or `build_linguistic_context(locale)` into the static prefix to prevent cache key fragmentation across locales.
  - Inject `GLOBAL_MANDATES_XML` (containing Exception 2: *"The JSON field exact_quotes and source_quote MUST ALWAYS remain in the raw, original language of the source text."*) and `MATRIX_SENSOR_SYSTEM_PROMPT` (containing the language-agnostic `<evidence_extraction_mandate>`) as a 100% static prefix.

#### [MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py#L26-L53]
- Add to `BooleanEvaluationResult` schema with max-length and sentence-boundary truncation validator per `graceful_text_truncation_validator`:
  ```python
  source_quote: Annotated[
      str | None,
      Field(
          default=None,
          max_length=500,
          description="Exact verbatim sentence or clause extracted directly from the context text in its original language, substantiating or violating this claim, or null if absent.",
      ),
  ] = None

  @field_validator("source_quote", mode="before")
  @classmethod
  def truncate_source_quote_at_sentence(cls, v: str | None) -> str | None:
      """Truncate oversized quote at the nearest sentence boundary under 500 chars."""
      if v is not None and len(v) > 500:
          truncated = v[:500]
          last_dot = truncated.rfind(".")
          return (truncated[: last_dot + 1]) if last_dot > 100 else truncated
      return v
  ```
- Update `PreFlightResult` to include `source_quote: str | None = None`.

#### [MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L434]
- Update `_batch_fuzzy_match` and `batch_pre_evaluate` return types to 4-tuple: `tuple[dict[str, tuple[ExecutionStatus, str | None, str | None, dict[str, str]]], list[LinkedAtomGraph]]`.
- Update `call_results[call_tda_id]` in `evaluate_atom_boolean_batch` to return a 4-tuple: `(status, eval_result.reasoning, eval_result.source_quote, extensions)`.
- Update `resolve_majority_vote` signature and implementation to preserve the winning vote's original `source_quote` in 4-tuple.

#### [MODIFY] @[backend_v2/models/dtos/dag_models.py#L114-L144]
- Add to `AtomExecutionState`:
  ```python
  source_quote: Annotated[
      str | None,
      Field(default=None, description="Exact verbatim quote extracted by the sensor during evaluation in original language."),
  ] = None
  ```

#### [MODIFY] @[backend_v2/services/orchestrator/topological_evaluator.py#L18-L176]
- Update `TopologicalEvaluator.evaluate_graph` callback type annotation and wave result unpacking:
  ```python
  # Update callback type annotation to 4-tuple:
  batch_evaluation_callback: Callable[
      [list[LinkedAtomGraph], dict[str, AtomExecutionState]],
      Awaitable[dict[str, tuple[ExecutionStatus, str | None, str | None, dict[str, str]]]],
  ]
  ```
- Update wave result unpacking in method:
  ```python
  status, reasoning, source_quote, extensions = res
  states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
      update={
          "status": status,
          "evaluation_reasoning": reasoning,
          "source_quote": source_quote,
          "extensions": extensions,
      }
  )
  ```

#### [MODIFY] @[backend_v2/services/orchestrator/enriched_dag_executor.py#L26-L187]
- Update `batch_evaluation_callback` and `process_chunk` signatures and return structures from 3-tuple to 4-tuple: `dict[str, tuple[ExecutionStatus, str | None, str | None, dict[str, str]]]`.
- Forward `source_quote` from `pre_flight_results` and `llm_results` through `merged_results`.

#### [MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L231]
- **Phase 1 Technical Debt Cleanup (CRITICAL):**
  - Line 88: Fix Python 2 syntax `except TypeError, KeyError:` $\rightarrow$ `except (TypeError, KeyError):` to prevent syntax crashes and ensure `KeyError` is properly trapped.
- **Phase 4 DAG State Integration:**
  - Update `TDAEngine` execution to properly handle the 4-tuple states returned by `EnrichedDagExecutor`.

#### [MODIFY] @[backend_v2/services/orchestrator/result_projector.py#L17-L136]
- Fix `ResultProjector.project` to read `source_quote` from runtime state `state.source_quote` for both `AtomResultDTO` and `HydratedAtomDTO`:
  ```python
  res = AtomResultDTO(
      tda_id=tda_id,
      matrix_id=matrix_id,
      status=status,
      extracted_data=None,
      source_quote=state.source_quote if state else None,
      contextual_override=node.atom.is_logical_deduction,
      evaluation_reasoning=reasoning,
      extensions=extensions,
      error_details=error_details,
      depends_on_tda_ids=[e.tda_id for e in node.depends_on],
      short_circuit_reason_tda_ids=short_circuit,
  )
  results.append(res)

  hydrated_references[tda_id] = HydratedAtomDTO(
      sdui_component=sdui_component,
      resolved_claim=node.atom.resolved_claim,
      source_quote=state.source_quote if state else node.atom.source_quote,
  )
  ```

---

### Python Backend: Scoring Pipeline & Parser

#### [MODIFY] @[backend_v2/hooks/scoring/matrix_hook.py#L38-L487]
- **Phase 1 Technical Debt Cleanups (`QGR016`):**
  - Line 259: Clean up ternary fallback on `extracted_facts` into strict typed access or explicit `.get("extracted_facts", {})`.
  - Line 274: Remove dead code `scales = pb_model.scales or []` $\rightarrow$ `scales = pb_model.scales` (Pydantic `MatrixPromptBlock.scales` already guarantees `min_length=1`).
  - Line 301: Replace `total_evals or 1` with `max(1, total_evals)`.
  - Line 317: Eliminate banned `.get("_dlq_status")` dict lookup $\rightarrow$ use explicit key check `"_dlq_status" in ev_dict_tmp and ev_dict_tmp["_dlq_status"] == "FAILED/DLQ"`.
  - Line 327: Replace `state.global_context_vars or {}` with explicit typed extraction.
  - Line 397: Clean up ternary fallback on `ev_dto.evaluation_reasoning`.
  - Line 454: Remove unnecessary conditional `matrix_extensions_by_block[pb_id] if pb_id in matrix_extensions_by_block else {}` $\rightarrow$ use direct access `matrix_extensions_by_block[pb_id]` (always initialized on line 279; strictly avoiding banned `.get()` fallback).
- **Phase 2 Double-Inversion Elimination:**
  - In `matrix_scoring_hook` (lines 351–377), eliminate `is_satisfied = not tda.inverse_evidence`.
  - Treat `ev_dto.status == ExecutionStatus.PASSED` as the sovereign truth indicating the assertion was satisfied.
  - Map `ExecutionStatus.FAILED` to `final_state = "FALSE"`.

#### [MODIFY] @[backend_v2/services/matrix_domain_parser.py#L32-L559]
- **Phase 1 Technical Debt Cleanups (`QGR016`):**
  - Line 378: Eliminate banned `.get(atom_id)` dict lookup $\rightarrow$ use explicit membership check `ev_data = step_evals_map[atom_id] if atom_id in step_evals_map else None`.
  - Line 407: Replace ternary fallback on `exact_quotes` (`[QuoteEvidenceDTO(...)] if val_data.source_quote else []`) with clean conditional assignment.
  - Line 412: Replace `val_data.evaluation_reasoning or ""` with `val_data.evaluation_reasoning if val_data.evaluation_reasoning is not None else ""`.
  - Lines 486, 492-494, 505, 509-514, 521, 528-529: Eliminate ternary lazy fallbacks on optional extension fields by validating against explicit DTO definitions.
- **Phase 3 Deterministic Context Target Resolution in `parse_matrices`:**
  - Remove the legacy dictionary break loop (`for mapped_val in input_mappings.values(): break`).
  - Implement three-tier deterministic resolution:
    1. **Single-Input Step:** If `input_mappings` contains exactly one `$inputs.*` key (e.g. step configured for deliverable only), resolve that input key and its label.
    2. **Multi-Input Step with Explicit Matrix SSOT:** If `input_mappings` contains multiple inputs, inspect `pb_meta.target_input_key`:
       - If `target_input_key == "chat_log"` $\rightarrow$ `context_target = "chat_log"`, label = "Chat Log" ("Keskusteluhistoria").
       - If `target_input_key == "product_text"` $\rightarrow$ `context_target = "product_text"`, label = "Deliverable" ("Lopputuote").
       - If `target_input_key == "all"` or unspecified $\rightarrow$ `context_target = "all"`, label = "All Inputs" ("Kaikki syötteet").
    3. **Fallback & Unknown Keys:** Resolve labels via `expected_inputs_map` with fallback to `LocalizationService.translate("matrix_target_all", locale)`.

---

### Python Backend Tests

#### [MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py#L1436-L1480]
- Expand unit tests to verify:
  1. Standard positive atom (`inverse_evidence: False`) passing $\rightarrow$ `final_state = "TRUE"`.
  2. Inverse evidence atom (`inverse_evidence: True`) passing sensor $\rightarrow$ `final_state = "TRUE"` (confirming no regression to `FAILED`).
  3. Mixed positive and inverse atoms in a multi-level waterfall matrix.
  4. Negative ISTQB equivalence partition verifying that when `status == ExecutionStatus.FAILED`, `final_state = "FALSE"` for both positive and inverse atoms.

#### [MODIFY] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py#L726-L785]
- Expand `test_parse_matrices_context_target_and_xai_extensions` to verify:
  1. Explicit `target_input_key` on `MatrixPromptBlock` resolves to the target input and localized label.
  2. Multiple `$inputs.*` mappings without explicit block key resolve to `"all"` ("Kaikki syötteet" / "All Inputs").
  3. Dedicated single input mapping (`chat_log`) resolves to "Chat Log".

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L376-L503]
- Add tests verifying:
  1. `BooleanEvaluationResult` correctly parses and validates verbatim `source_quote` in its original source language.
  2. Bo3 majority vote consolidates `source_quote` alongside status and reasoning.
  3. `ResultProjector.project()` correctly propagates `source_quote` from `AtomExecutionState` to `AtomResultDTO`.

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py#L28-L270]
- Update mock callbacks and return fixtures in `test_execute_graph_callback`, `test_execute_graph_callback_persistent_error`, and `test_execute_graph_callback_transient_error` to match 4-tuple contract `(status, reasoning, source_quote, extensions)`.

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py#L28-L230]
- Update mock callbacks in unit tests to match 4-tuple contract `(status, reasoning, source_quote, extensions)`.

#### [MODIFY] @[backend_v2/tests/integration/test_topological_evaluator.py#L28-L176]
- Update mock callbacks in integration tests to match 4-tuple contract `(status, reasoning, source_quote, extensions)`.

---

## Canonical Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Pre-Implementation Technical Debt Cleanups (QGR016 & Python 2 Syntax)">
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py#L88], fix Python 2 syntax `except TypeError, KeyError:` to `except (TypeError, KeyError):`.</action>
    <action>In @[backend_v2/models/dtos/matrix_scorecard.py#L127], fix Python 2 syntax `except TypeError, ValueError:` to `except (TypeError, ValueError):` (Tier 0 Discovery: critical SDUI rendering path).</action>
    <action>Inspect and resolve all QGR016 advisory AST guardrail warnings in @[backend_v2/hooks/scoring/matrix_hook.py#L38-L487] and @[backend_v2/services/matrix_domain_parser.py#L32-L559].</action>
    <action>In matrix_hook.py, simplify line 274 to `scales = pb_model.scales` (Pydantic enforces min_length=1), replace line 301 with `max(1, total_evals)`, line 317 `.get("_dlq_status")` with explicit key check, line 327 with typed context extraction, and line 454 with direct access `matrix_extensions_by_block[pb_id]` (strictly avoiding banned .get()).</action>
    <action>In matrix_domain_parser.py, replace line 378 `.get(atom_id)` with explicit key check `atom_id in step_evals_map`, and resolve ternary fallbacks on lines 407, 412, 486, and 492-529.</action>
    <action>In @[backend_v2/services/orchestrator/topological_evaluator.py#L108], replace `results.get(node.atom.tda_id)` with explicit key membership check (Tier 0 Discovery: QGR016).</action>
    <constraint invariant="the_duct_tape_ban">NEVER use lazy fallbacks or inline defaults in domain code.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py`, `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/matrix_scorecard.py`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/topological_evaluator.py` and confirm 0 QGR016 violations.</verification>
  </step>

  <step id="2" name="Phase 2: Eliminate Double-Inversion Bug in Matrix Hook">
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py#L38-L487], surgically replace lines 351–377.</action>
    <action>Eliminate `is_satisfied = not tda.inverse_evidence`. Treat `ev_dto.status == ExecutionStatus.PASSED` as the sovereign truth indicating the assertion was satisfied.</action>
    <action>Properly evaluate `ev_dto.contextual_override` and `effective_override` without inverting the base sensor decision.</action>
    <constraint invariant="universal_fail_fast">Do not guess state; enforce ExecutionStatus contracts strictly.</constraint>
    <verification>Run `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -k "test_matrix_scoring_hook"`.</verification>
  </step>

  <step id="3" name="Phase 3: Context Target Input Resolution & Multi-Input Routing">
    <action>Add `target_input_key: Annotated[str | None, Field(default=None, description="Explicit target input key from workflow expected_inputs (specifically: 'chat_log', 'product_text', 'all').")] = None` to `MatrixPromptBlock` in @[backend_v2/models/domain/prompt_blocks.py#L64-L108] enforcing PEP 593 Annotated syntax per `ki_zero_permissive_typing.md`.</action>
    <action>In @[backend_v2/seed/seed_data.json], populate `target_input_key` across all 13 matrix prompt blocks adhering to the Cognitive SSOT Map (product_text for Toulmin/Bloom/Causal, chat_log for Goodhart/Judge/Performativity, all for holistic matrices).</action>
    <action>Add `matrix_target_all` and `matrix_target_chat_log` translations to @[backend_v2/l10n/fi.json#L50-L65] and @[backend_v2/l10n/en.json#L50-L65].</action>
    <action>In @[backend_v2/services/matrix_domain_parser.py#L32-L559], replace legacy first-item break loop with three-tier deterministic multi-input resolution.</action>
    <constraint invariant="zero_service_layer_fallbacks">Never break arbitrarily on first dict element.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py`.</verification>
  </step>

  <step id="4" name="Phase 4: Sensor Quote Extraction Putki & Language-Agnostic Caching Prefix (Option A)">
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py#L26-L53], add `source_quote: Annotated[str | None, Field(default=None, max_length=500)] = None` with `@field_validator(mode="before")` sentence-boundary truncation to `BooleanEvaluationResult`, and add `source_quote: str | None = None` to `PreFlightResult`.</action>
    <action>In @[backend_v2/models/prompts/matrix_evaluation.py#L1-L27], append language-agnostic `<evidence_extraction_mandate>` requiring verbatim quote extraction strictly in the raw, original language of the source text without translation.</action>
    <action>In @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L209], preserve 100% static prefix caching without injecting dynamic locale.</action>
    <action>In @[backend_v2/models/dtos/dag_models.py#L114-L144], add `source_quote: str | None = None` to `AtomExecutionState`.</action>
    <action>In @[backend_v2/services/orchestrator/topological_evaluator.py#L18-L176], update callback type annotation to 4-tuple and propagate `source_quote` into states.</action>
    <action>In @[backend_v2/services/orchestrator/enriched_dag_executor.py#L26-L187], update `batch_evaluation_callback` and `process_chunk` to 4-tuple.</action>
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L230], update execution to handle 4-tuple DAG states.</action>
    <action>In @[backend_v2/services/orchestrator/result_projector.py#L17-L136], project `source_quote` from `state.source_quote` into both `AtomResultDTO` and `HydratedAtomDTO`.</action>
    <constraint invariant="strict_physical_anchoring_mandate">Enforce exact verbatim quotes in original source language; prohibit chimera quotes or translation of quotes.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/result_projector.py`.</verification>
  </step>

  <step id="5" name="Phase 5: ISTQB Unit & Integration Test Expansion for Scoring, Parser, DAG & Sensor Quotes">
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py#L1436-L1480], add unit test `test_matrix_scoring_hook_inverse_evidence_passed_satisfies_level`.</action>
    <action>In @[backend_v2/tests/unit/services/test_matrix_domain_parser.py#L726-L785], add test cases for single-input, multi-input ("all"), and prompt-block explicit target resolution.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L376-L503], add test verifying `source_quote` extraction in original language, Bo3 consensus, and projection to `AtomResultDTO`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py#L28-L270], @[backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py#L28-L230], and @[backend_v2/tests/integration/test_topological_evaluator.py#L28-L176], update mock callback fixtures to 4-tuple.</action>
    <constraint invariant="anti_happy_path_mandate">Cover both positive and negative equivalence partitions.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test`, `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test`.</verification>
  </step>

  <step id="6" name="Phase 6: Global Audit, Trace Replay & SDUI Parity Validation">
    <action>Execute full backend audit loop across all scoring hooks, matrix parser, and sensor orchestrator.</action>
    <action>Execute SDUI semantic parity test: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Execute full flutter audit loop across client_app_v2.</action>
    <action>Run offline trace verification against execution `exe_88267cb7b3cf4718ae76b7dbce04a92e`, proving that Level 1 fatal-flaw matrices achieve their true 70%–86% scores, target labels display properly, and `exact_quotes` populate "Tekstin havainto" in original language.</action>
    <verification>Verify all tests pass with >90% coverage and zero AST guardrail warnings.</verification>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Scoring Hook Unit Tests & Coverage:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test
   ```
2. **Matrix Domain Parser Tests & Coverage:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test
   ```
3. **Sensor Service & Result Projector Tests & Coverage:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/result_projector.py --test
   ```
4. **DAG Orchestrator Unit & Integration Tests:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/enriched_dag_executor.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/topological_evaluator.py --test
   ```
5. **SDUI Semantic Parity Test:**
   ```powershell
   uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
   ```
6. **AST Guardrail Validation:**
   ```powershell
   uv run python scripts/_ast_guardrails.py backend_v2/hooks/scoring/matrix_hook.py backend_v2/services/matrix_domain_parser.py backend_v2/services/orchestrator/extractive_sensor_service.py backend_v2/services/orchestrator/result_projector.py backend_v2/services/orchestrator/engines/tda_engine.py backend_v2/services/orchestrator/enriched_dag_executor.py backend_v2/services/orchestrator/topological_evaluator.py
   ```

### Manual & Trace Replay Verification
- Execute offline verification against `data/files/executions/exe_88267cb7b3cf4718ae76b7dbce04a92e/execution_trace.json`, mathematically proving that:
  - *Argumentation Quality (Toulmin)* produces Level 1: 4/5, Level 2: 3/5, Level 3: 4/5, Level 4: 5/5, Level 5: 5/5 $\rightarrow$ **75.0%**.
  - *Causal Relationships (Causality)* produces Level 1: 5/5, Level 2: 5/5, Level 3: 5/5, Level 4: 3/5, Level 5: 2/5 $\rightarrow$ **73.0%**.
  - *Self-Challenge (Falsification)* produces Level 1: 5/5, Level 2: 5/5, Level 3: 4/5, Level 4: 3/5 $\rightarrow$ **86.7%**.
  - Target labels display `"Keskusteluhistoria"` ("Chat Log") for *Goodhart* & *Judge*, `"Lopputuote"` ("Deliverable") for *Toulmin* & *Bloom*, and `"Kaikki syötteet"` ("All Inputs") for cross-cutting matrices.
  - "Evidence Quote" ("Tekstin havainto") column in `exact_quotes` populates from `AtomResultDTO` $\rightarrow$ `ScorecardAtomDTO` schema 100% in raw source language without translation distortion.
