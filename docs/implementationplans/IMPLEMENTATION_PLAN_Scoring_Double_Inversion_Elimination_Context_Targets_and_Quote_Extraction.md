> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified across Phases 1–7)**

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
  <knowledge_item>@[ki_matrix_boolean_evaluation_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_matrix_sensor_prompt_builder.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

**Associated Research & Audits:**
- @[docs/audit/feature_audit_theory_grounding_calibration.md]
- @[docs/audit/feature_audit_bipolar_matrix_scores.md]
- @[docs/audit/feature_audit_context_target_inputs.md]
- @[docs/audit/feature_audit_pydantic_validation_bypass.md]
- @[docs/audit/feature_audit_dag_sensor_evaluation_dto.md]
- @[docs/audit/feature_audit_frontend_sdui_and_clean_seed.md]  
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

> [!IMPORTANT]
> **5. Two-Tier Validation Firewall & Pydantic Validation Bypass Protection:**
> As established in @[docs/audit/feature_audit_pydantic_validation_bypass.md], Pydantic V2 `.model_copy(update={...})` bypasses all field validators and constraints.
> - **Untrusted Ingress (Sensor & Extractor Output):** Validated with `execute_structured_task(response_model=BatchEvaluationResponse)` via Rust `model_validate()`, which triggers `@field_validator("source_quote", mode="before")` on `BooleanEvaluationResult` to enforce sentence-boundary truncation to $\le 500$ characters.
> - **Internal High-Throughput State Transit (DAG & Orchestrator):** `TopologicalEvaluator` and `DAGExecutor` retain `.model_copy(update=...)` inside synchronized locks (`async with _update_lock:`) for shallow C-level state transitions, preventing $O(N)$ recursive serialization bottlenecks on `ExecutionRecord` per `frozen_state_mutability` and `pydantic_mutation_optimization_mandate`.
> - **Defense-in-Depth Schema Shield:** `AtomExecutionState.source_quote` explicitly defines `max_length=500` via `Annotated[str | None, Field(default=None, max_length=500)]`, ensuring direct model construction fails fast if unvalidated strings are passed.

> [!IMPORTANT]
> **6. Eliminating "Tuple Hell" via `AtomEvaluationResultDTO` (Zero Permissive Typing):**
> As established in @[docs/audit/feature_audit_dag_sensor_evaluation_dto.md], passing an untyped 4-tuple `tuple[ExecutionStatus, str | None, str | None, dict[str, str]]` (status, reasoning, source_quote, extensions) between orchestrator functions violates `no_naked_dicts_in_state` and `the_zero_compromise_pledge`.
> - **Positional Type Blindness:** Because both `reasoning` and `source_quote` share the type `str | None`, positional transpositions are invisible to static type checkers (MyPy) and cause prompt/reasoning leakage into quote UI fields.
> - **Sovereign Replacement:** Define `AtomEvaluationResultDTO` in `@[backend_v2/models/dtos/dag_models.py]` (`ConfigDict(extra="forbid", strict=True, frozen=True)`).
> - **Pipeline Invariant:** `ExtractiveSensorService` emits `dict[str, AtomEvaluationResultDTO]`, `EnrichedDagExecutor` forwards it, and `TopologicalEvaluator` unpacks typed attributes (`res.status`, `res.reasoning`, `res.source_quote`, `res.extensions`) via dot notation with zero positional tuple destructuring.

> [!IMPORTANT]
> **7. Frontend SDUI Parity, Dart Model Synchronization & Clean-Slate Seeding Mandate:**
> As established in @[docs/audit/feature_audit_frontend_sdui_and_clean_seed.md]:
> 1. **Cross-Domain Freezed Serialization Firewall:** `client_app_v2/lib/features/studio/models/prompt_block.dart` defines `MatrixPromptBlock` with `@JsonSerializable(disallowUnrecognizedKeys: true)`. Adding `target_input_key` in Python and `seed_data.json` without updating Dart causes an immediate `CheckedFromJsonException` (White Screen of Death) in `domain_parity_test.dart` and Studio CRUD views. `PromptBlock.matrix` MUST be updated with `@JsonKey(name: 'target_input_key') String? targetInputKey` and recompiled via `build_runner`.
> 2. **Clean-Slate Seeding Protocol (Zero Legacy Support):** Per `the_no_legacy_mandate` and `local_data_ephemeral_nature`, legacy runs in `data/files/executions/` and dirty states in `data/db_v2.json` are NOT supported. A complete local wipe and fresh seeding via `uv run python backend_v2/seed/run_seed.py local` MUST be executed, dropping tables and purging orphaned executions.
> 3. **Native SDUI Painter Readiness:** `client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart` already consumes `axis.contextTargetLabel?.get(locale) ?? axis.contextTarget` for context target badges and `atom.exactQuotes.map((q) => Text('"${q.quote}"', ...))` for verbatim quotes. Once backend emits populated DTOs, the client renders them immediately without SDUI model modifications.

---

## 5-Column Architectural Directives (System 2 Deconstruction)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Matrix Hook: Double-Inversion Elimination**<br>`@[backend_v2/hooks/scoring/matrix_hook.py#L38-L487]` | Banned double-negation `is_satisfied = not tda.inverse_evidence` that inverts an already-normalized sensor pass. Banned `scales or []` dead code (`MatrixPromptBlock.scales` has `min_length=1`). Banned `matrix_extensions_by_block[pb_id] if pb_id in ...` ternary (provably always present from L279 init; banned `.get()` fallback). Banned `total_evals or 1` literal default. Banned `.get("_dlq_status")` and `.get("status")` dict lookups on L246, L248, L317 (QGR016). | Sovereign contract: Upstream sensor `ExecutionStatus.PASSED` means the level assertion is satisfied. Direct access to provably-initialized state. Division protection via `max(1, total_evals)`. Evaluate `effective_override` on failed assertions only. Explicit key checks for DLQ status. | Zero custom scoring wrappers or secondary mapping tables. Re-uses native `ExecutionStatus` domain invariants directly. | `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test`. AST guardrail `_ast_guardrails.py` verifies 0 QGR016 warnings. |
| **TDA Engine: Python 2 Exception Syntax & Model Copy**<br>`@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L230]` | Banned Python 2 exception syntax `except TypeError, KeyError:` on line 88 that causes SyntaxError / silent shadowing of `KeyError`. Banned QGR016 ternary fallback on line 179 for `request.matrix_context`. | Standard Python 3 exception handling: `except (TypeError, KeyError): # fmt: skip`. Clean fail-fast error trapping. | Zero new abstractions. Single-line surgical fix restoring syntactic integrity. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py --test`. |
| **ScorecardAtomDTO: Python 2 Exception Syntax & Banned `.get()`**<br>`@[backend_v2/models/dtos/matrix_scorecard.py#L75-L134]`<br>`@[backend_v2/models/dtos/matrix_scorecard.py#L183-L340]` | Banned Python 2 exception syntax `except TypeError, ValueError:` on line 127 that silently binds `TypeError` to a local variable named `ValueError`, failing to trap actual `ValueError` on the critical SDUI rendering path. Banned `.get("status")` and `.get("contextual_override")` dict lookups on L130, L132 violating `the_duct_tape_ban` and QGR016. | Standard Python 3 exception handling: `except (TypeError, ValueError): # fmt: skip`. Explicit key membership checks: `"status" in d` and `"contextual_override" in d`. | Zero new abstractions. Surgical fix within critical DTO path. | `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/matrix_scorecard.py --test`. |
| **TopologicalEvaluator: Banned `.get()`, Tuple Unpacking & QGR016**<br>`@[backend_v2/services/orchestrator/topological_evaluator.py#L18-L176]` | Banned `results.get(node.atom.tda_id)` dictionary lookup on line 108 violating `the_duct_tape_ban` and QGR016. Banned 3-tuple destructuring on line 110 (`status, reasoning, extensions = res`). Banned `short_circuit_reason_tda_ids or []` fallback on line 149. | Explicit key membership check: `node.atom.tda_id in results` with direct access `results[node.atom.tda_id]`. Unpack typed `AtomEvaluationResultDTO` attributes via dot notation (`res.status`, `res.reasoning`, `res.source_quote`, `res.extensions`). Direct access to `short_circuit_reason_tda_ids` (guaranteed list default). | Zero new abstractions. Surgical fix within already-targeted file. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/topological_evaluator.py --test`. |
| **Matrix Domain Parser: Deterministic Target Resolution & QGR016**<br>`@[backend_v2/services/matrix_domain_parser.py#L32-L559]` | Banned legacy dictionary iteration loop `for mapped_val in input_mappings.values(): break` that unconditionally defaulted to `product_text` ("Lopputuote"). Banned QGR016 ternary fallbacks across metadata and extension extraction (lines 408, 412, 486, 492-529). Banned `.get(atom_id)` on L378, `.get(b_id)` on L118, and `.get(context_target)` on L486. Banned broad `except Exception:` on L420. | Deterministic resolution: 1) `pb_meta.target_input_key` priority, 2) Single `$inputs.*` mapping, 3) Domain mapping: `chat_log` ("Keskusteluhistoria") for goodhart/judge, `product_text` ("Lopputuote") for toulmin/bloom/causal, else `"all"` ("Kaikki syötteet"). Explicit membership checks `atom_id in step_evals_map`, `b_id in blocks_by_id`, and `context_target in expected_inputs_map`. Specific `except ValidationError:` error trapping. | No runtime regex inspection or dynamic file-reading heuristics. Pure domain mapping based on existing workflow metadata. | `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test`. 100% passing quality gates. |
| **Sensor Quote Extraction: Verbatim Language Preservation**<br>`@[backend_v2/services/orchestrator/extractive_sensor_service.py#L26-L59]`<br>`@[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L434]`<br>`@[backend_v2/models/prompts/matrix_evaluation.py#L1-L26]`<br>`@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L209]` | Banned discarding `source_quote` from LLM extraction. Banned translating or paraphrasing extracted quotes (LANGUAGE_MANDATE Exception 2). Banned fuzzy chimera quotes under `strict_physical_anchoring_mandate`. Banned injecting dynamic `locale` into static caching prefix (`ephemeral_caching_topology`). Banned unconstrained quote lengths and unvalidated boundary ingress. | `BooleanEvaluationResult` defines `source_quote: Annotated[str | None, Field(default=None, max_length=500)]` with `@field_validator(mode="before")` sentence-boundary truncation per `graceful_text_truncation_validator`. Validated via `model_validate()` at ingress boundary. Kept 100% in raw original language. Bo3 voting consolidates winning `source_quote`. Static language-AGNOSTIC `<evidence_extraction_mandate>`. | Option A direct extraction in single sensor pass (Zero extra LLM latency, zero new microservices, zero prompt bloat). | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test`. Strict Pydantic V2 schema validation (`extra="forbid"`). |
| **DAG Pipeline Transit & 1-Hop Callers**<br>`@[backend_v2/models/dtos/dag_models.py#L114-L145]`<br>`@[backend_v2/services/orchestrator/topological_evaluator.py#L18-L177]`<br>`@[backend_v2/services/orchestrator/enriched_dag_executor.py#L28-L187]`<br>`@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L231]`<br>`@[backend_v2/services/orchestrator/result_projector.py#L17-L136]` | Banned reading uninitialized `node.atom.source_quote` (static seed) in `ResultProjector` for both `AtomResultDTO` and `HydratedAtomDTO`. Banned silent fallback to empty string when quote is missing. Banned all 3-tuples and 4-tuples (`Tuple Hell`: `tuple[ExecutionStatus, str \| None, str \| None, dict[str, str]]`), positional index access (`vote_tuple[0]`), and positional tuple destructuring. Banned `model_dump() \| update` full serialization in high-throughput state loops. Banned QGR016 ternary fallbacks in `result_projector.py#L85-L90`. Banned `semaphore or asyncio.Semaphore(...)` on line 95 in `enriched_dag_executor.py` (QGR016). Banned unconditional `contextual_override=node.atom.is_logical_deduction` which triggers `AtomResultDTO.validate_cognitive_vs_system_state` to silently strip `source_quote` to `None`. | Sovereign contract: Introduce immutable `AtomEvaluationResultDTO` (`status`, `reasoning`, `source_quote`, `extensions`) with `ConfigDict(extra="forbid", strict=True, frozen=True)`. Callback type is `dict[str, AtomEvaluationResultDTO]`. Transits pre-validated `source_quote` via `AtomExecutionState.source_quote` (`max_length=500`) $\rightarrow$ `AtomResultDTO.source_quote` $\rightarrow$ `ScorecardAtomDTO.exact_quotes` (`QuoteEvidenceDTO`). In `ResultProjector`, resolve `contextual_override = False if (state and state.source_quote) else node.atom.is_logical_deduction` to preserve empirical quotes. In-memory transitions use `.model_copy(update=...)` per `frozen_state_mutability`. Explicit null check for semaphore. `ResultProjector` instantiates fresh `AtomResultDTO` running all validation. | Zero secondary database writes, zero duplicate event traces, zero speculative polymorphic sub-DTOs (no `PreFlightResultDTO` vs `LLMResultDTO`). Direct transit through existing frozen DAG state envelopes. Pruned redundant serialization cycles. | `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/result_projector.py --test`. `test_dag_models.py` asserts `AtomEvaluationResultDTO` validation & `max_length=500`. SDUI Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`. |
| **Global Prompt Mandates: Raw Quote Exception**<br>`@[backend_v2/models/prompts/global_mandates.py#L22-L34]` | Banned language translation, summarization, or mutation of `source_quote` under multilingual execution workflows. | Update `LANGUAGE_MANDATE` Exception 2 to explicitly mandate that both `exact_quotes` and `source_quote` must remain 100% in the raw, original language of the source text. | Centralized SSOT constraint; zero ad-hoc prompt monkey-patching in service classes. | `uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/global_mandates.py`. |
| **Flutter Domain Model: `prompt_block.dart`**<br>`@[client_app_v2/lib/features/studio/models/prompt_block.dart#L220-L248]` | Banned ignoring backend schema additions in Flutter models; banned runtime `CheckedFromJsonException` crashes on unrecognized keys in background isolates. | Add `@JsonKey(name: 'target_input_key') String? targetInputKey` to `PromptBlock.matrix` Freezed factory. Strict 1:1 cross-language parity with Python `MatrixPromptBlock`. Regenerate Freezed and JsonSerializable code. | Zero manual JSON map parsing; enforce native Freezed code generation. | `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --build`. |
| **Clean-Slate Seeding Protocol & Seed Vault SSOT**<br>`@[backend_v2/seed/run_seed.py]`<br>`@[backend_v2/seed/seed_data.json#L317-L350]` (Toulmin)<br>`@[backend_v2/seed/seed_data.json#L1495-L1525]` (Bloom)<br>`@[backend_v2/seed/seed_data.json#L2999-L3030]` (Kahneman)<br>`@[backend_v2/seed/seed_data.json#L3778-L3810]` (Goodhart)<br>`@[backend_v2/seed/seed_data.json#L5178-L5210]` (Archival)<br>`@[backend_v2/seed/seed_data.json#L6438-L6472]` (Causal)<br>`@[backend_v2/seed/seed_data.json#L7600-L7632]` (Popper)<br>`@[backend_v2/seed/seed_data.json#L8550-L8581]` (Supreme Adjudicator)<br>`@[backend_v2/seed/seed_data.json#L9765-L9798]` (XAI)<br>`@[backend_v2/seed/seed_data.json#L11115-L11148]` (Taskguard)<br>`@[backend_v2/seed/seed_data.json#L12375-L12409]` (Pearl & Mackenzie)<br>`@[backend_v2/seed/seed_data.json#L13735-L13768]` (Lipton)<br>`@[backend_v2/seed/seed_data.json#L15445-L15476]` (Tetlock) | Banned maintaining backwards compatibility with old runs, patching dirty TinyDB state, or building migration duct-tape. Banned inventing extra JSON keys not defined in Pydantic models. Banned using semantic slugs for data relations. | Run `uv run python backend_v2/seed/run_seed.py local` to drop all tables, wipe `data/files/executions/`, and re-seed from scratch into clean slate. Populate `target_input_key` across all 13 matrices strictly at the exact block bounds. | Zero legacy migration scripts or conditional fallback dictionaries. Clean table drop. | `uv run python backend_v2/seed/run_seed.py local --dry-run` followed by live local seeding. |

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
   - *Attack:* Changing callback return type from raw tuple to `AtomEvaluationResultDTO` without updating `EnrichedDagExecutor`, `TopologicalEvaluator`, and test fixtures causes runtime type mismatch or `AttributeError`.
   - *Mitigation & Proof:* `enriched_dag_executor.py`, `topological_evaluator.py`, `test_enriched_dag_executor.py`, and `test_topological_evaluator.py` are explicitly synchronized to consume `AtomEvaluationResultDTO` via direct dot notation (`res.status`, `res.reasoning`, `res.source_quote`, `res.extensions`).
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
12. **Failure Mode 12: Pydantic Validation Bypass via `model_copy(update={...})` in Internal Transit:**
    - *Attack:* In Pydantic V2, `model_copy(update={...})` executes a shallow dictionary patch on the instance without running `@field_validator` or constraints. If untrusted raw strings bypass ingress validation, oversized quotes could leak into `AtomExecutionState`.
    - *Mitigation & Proof:* Two-Tier Validation Firewall: 1) Ingress from LLM is strictly validated through `BooleanEvaluationResult` where `@field_validator("source_quote", mode="before")` guarantees truncation to $\le 500$ chars during `model_validate()`; 2) `AtomExecutionState.source_quote` enforces `max_length=500` as a defense-in-depth shield; 3) Internal DAG loops use `.model_copy(update=...)` with pre-validated typed attributes inside `async with _update_lock:` per `pydantic_validation_bypass_ban` and `frozen_state_mutability`, avoiding $O(N)$ recursive serialization overhead.
13. **Failure Mode 13: Flutter Isolate Deserialization Crash on Unrecognized Keys (`CheckedFromJsonException`):**
    - *Attack:* Adding `target_input_key` to `seed_data.json` causes `PromptBlock.parseListInBackground()` in `client_app_v2/test/models/domain_parity_test.dart` and Studio CRUD controllers to throw `CheckedFromJsonException` because Freezed enforces `disallowUnrecognizedKeys: true`.
    - *Mitigation & Proof:* `PromptBlock.matrix` in `client_app_v2/lib/features/studio/models/prompt_block.dart` is updated with `@JsonKey(name: 'target_input_key') String? targetInputKey` and re-generated via `build_runner` before running local database seeding.
14. **Failure Mode 14: Legacy Execution Trace Schema Collision from Previous Runs:**
   - *Attack:* Attempting to deserialize historical execution records in `data/files/executions/` containing legacy or divergent structures crashes execution view controllers.
   - *Mitigation & Proof:* Clean-slate mandate: `uv run python backend_v2/seed/run_seed.py local` drops all tables from `data/db_v2.json` and deletes `data/files/executions/`, guaranteeing zero legacy pollution per `the_no_legacy_mandate`.
15. **Failure Mode 15: Silent Quote Stripping in `AtomResultDTO` via Unconditional `contextual_override=True` (CRITICAL TIER 0 FINDING):**
   - *Attack:* In `tda_engine.py#L170`, `ExtractedAtom` is instantiated with `is_logical_deduction=True`. If `ResultProjector` sets `contextual_override=node.atom.is_logical_deduction` unconditionally, then `AtomResultDTO.validate_cognitive_vs_system_state` executes: `if self.contextual_override and self.source_quote is not None: object.__setattr__(self, "source_quote", None)`. This silently strips all extracted verbatim quotes to `None` at the projection boundary!
   - *Mitigation & Proof:* In `ResultProjector.project()`, evaluate: `has_quote = bool(state and state.source_quote); contextual_override = False if has_quote else node.atom.is_logical_deduction`. If an empirical quote is present, `contextual_override` is strictly forced to `False`, perfectly satisfying `validate_cognitive_vs_system_state` and preserving the quote. If no quote exists and `status == PASSED`, `contextual_override` remains `True` to satisfy the schema requirement.
16. **Failure Mode 16: Whitespace-only or Empty Quote Ingress into `QuoteEvidenceDTO`:**
   - *Attack:* If an LLM emits `source_quote = "   "`, wrapping it into `QuoteEvidenceDTO` populates empty quotation marks (`""`) in SDUI table cells.
   - *Mitigation & Proof:* In `matrix_domain_parser.py`, guard quote evidence construction with `if val_data.source_quote and val_data.source_quote.strip():`, guaranteeing only substantive verbatim text is rendered into `exact_quotes`.

---

## Proposed Changes

### Python Backend: Domain Models & Localization

#### [MODIFY] @[backend_v2/models/domain/prompt_blocks.py#L64-L118]
- Verify `MatrixPromptBlock` retains `target_input_key: Annotated[str | None, Field(default=None, description="Explicit target input key from workflow expected_inputs (specifically: 'chat_log', 'product_text', 'all').")] = None` (strictly adhering to PEP 593 `Annotated` syntax per `pydantic_annotated_fields_mandate` and `ki_zero_permissive_typing.md`). *(Note: Field is already verified and implemented in Python domain model; Flutter Dart model and seed data require synchronization).*

#### [MODIFY] @[backend_v2/seed/seed_data.json]
- In `seed_data.json`, populate `target_input_key` across all 13 matrix prompt blocks strictly within their exact block boundaries via their canonical Opaque Stripe IDs (strictly adhering to `slug_data_relation_ban` and `matrix_slug_identification_ban`):
  - `@[backend_v2/seed/seed_data.json#L317-L350]` (Toulmin Argumentation - `blk_440a5fef9331451b`): `"product_text"`
  - `@[backend_v2/seed/seed_data.json#L1495-L1525]` (Bloom's Taxonomy - `blk_f921c7c0989b47e8`): `"product_text"`
  - `@[backend_v2/seed/seed_data.json#L2999-L3030]` (Kahneman Dual Process - `blk_109dab5b6b3f403a`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L3778-L3810]` (Goodhart's Law - `blk_53f32679aa514fcb`): `"chat_log"`
  - `@[backend_v2/seed/seed_data.json#L5178-L5210]` (Archival Compliance - `blk_fb15f8dcf23f4865`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L6438-L6472]` (Causal Inference - `blk_c5804a9143c34cb1`): `"product_text"`
  - `@[backend_v2/seed/seed_data.json#L7600-L7632]` (Falsification Audit - `blk_b476f89fb732448c`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L8550-L8581]` (Supreme Adjudicator - `blk_ff72c2d79edb4ebf`): `"chat_log"`
  - `@[backend_v2/seed/seed_data.json#L9765-L9798]` (XAI Synthesis Reporter - `blk_6b8c766185294f7e`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L11115-L11148]` (Taskguard Responsibility - `blk_80732a33fe1947ee`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L12375-L12409]` (Causal & Abductive Integrity - `blk_c3bc5f3eb8e74110`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L13735-L13768]` (Explainability & Transparency - `blk_f6e286f050c94d60`): `"all"`
  - `@[backend_v2/seed/seed_data.json#L15445-L15476]` (Epistemic Humility - `blk_22e3598e06414409`): `"all"`

#### [MODIFY] @[backend_v2/models/prompts/global_mandates.py#L22-L34]
- In `LANGUAGE_MANDATE` Exception 2, update wording to explicitly include `source_quote` alongside `exact_quotes`:
  ```python
  "- CRITICAL EXCEPTION 2: The JSON fields `exact_quotes` and `source_quote` MUST ALWAYS remain in the raw, "
  "original language of the source text. NEVER translate, paraphrase, or modify the language "
  "of the extracted quotes.\n"
  ```

#### [MODIFY] @[backend_v2/l10n/fi.json#L50-L65]
- Add localization key `"matrix_target_all": "Kaikki syötteet"` and `"matrix_target_chat_log": "Keskusteluhistoria"`.

#### [MODIFY] @[backend_v2/l10n/en.json#L50-L65]
- Add localization key `"matrix_target_all": "All Inputs"` and `"matrix_target_chat_log": "Chat Log"`.

---

### Frontend Flutter: Domain Models & Code Generation

#### [MODIFY] @[client_app_v2/lib/features/studio/models/prompt_block.dart#L220-L248]
- In `PromptBlock.matrix` factory, add `@JsonKey(name: 'target_input_key') String? targetInputKey,` maintaining strict 1:1 cross-language parity with Python `MatrixPromptBlock`.
- Run Flutter build runner via `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build` to regenerate `prompt_block.freezed.dart` and `prompt_block.g.dart` with `target_input_key` included in `allowedKeys`.

#### [MODIFY] @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L420-L445]
- In `PromptBlockBuilderView`, preserve `targetInputKey: (payload is MatrixPromptBlock) ? payload.targetInputKey : null` across category switch rebuilds and form mutations to ensure Studio editing does not drop the attribute.

---

### Python Backend: LLM Sensor & Quote Extraction Pipeline (Option A)

#### [MODIFY] @[backend_v2/models/prompts/matrix_evaluation.py#L1-L26]
- Add `<evidence_extraction_mandate>` to `MATRIX_SENSOR_SYSTEM_PROMPT`:
  - Require that whenever a claim is confirmed or violated in the text, extract the exact verbatim sentence or clause into `source_quote`.
  - **Absolute Language Preservation:** `source_quote` MUST remain in the raw, original language of the source text. NEVER translate, paraphrase, summarize, or alter the language of the extracted quotes.
  - If a claim is rejected because the text does not mention the subject, `source_quote` must be set to `null`.
  - Absolute ban on chimeric or altered quotes: the quote must physically exist in the source text (`str.find` lexical integrity).

#### [MODIFY] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L209]
- Ensure 100% static cacheability in `build_caching_prefix` and `MatrixSensorPromptBuilder`:
  - **Ephemeral Caching Topology Mandate:** DO NOT inject dynamic `locale` parameter or `build_linguistic_context(locale)` into the static prefix to prevent cache key fragmentation across locales.
  - Inject `GLOBAL_MANDATES_XML` (containing Exception 2: *"The JSON field exact_quotes and source_quote MUST ALWAYS remain in the raw, original language of the source text."*) and `MATRIX_SENSOR_SYSTEM_PROMPT` (containing the language-agnostic `<evidence_extraction_mandate>`) as a 100% static prefix.

#### [MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py#L26-L52]
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

#### [MODIFY] @[backend_v2/models/dtos/dag_models.py#L114-L144]
- **Define `AtomEvaluationResultDTO`** to permanently eliminate "Tuple Hell" across the orchestrator pipeline (`the_zero_compromise_pledge`, `no_naked_dicts_in_state`):
  ```python
  class AtomEvaluationResultDTO(BaseModel):
      """Evaluation payload emitted by sensor or pre-flight engine for a single atom."""

      model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

      status: Annotated[ExecutionStatus, Field(description="Evaluated cognitive or execution status.")]
      reasoning: Annotated[str | None, Field(default=None, description="Cognitive chain-of-thought justification.")] = None
      source_quote: Annotated[str | None, Field(default=None, max_length=500, description="Exact verbatim quote in original source language.")] = None
      extensions: Annotated[dict[str, str], Field(default_factory=dict, description="Extracted XAI extensions.")] = Field(default_factory=dict)
  ```
- Add to `AtomExecutionState` with defense-in-depth `max_length=500`:
  ```python
  source_quote: Annotated[
      str | None,
      Field(
          default=None,
          max_length=500,
          description="Exact verbatim quote extracted by the sensor during evaluation in original language.",
      ),
  ] = None
  ```

#### [MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L434]
- Update `_batch_fuzzy_match` and `batch_pre_evaluate` return types to `tuple[dict[str, AtomEvaluationResultDTO], list[LinkedAtomGraph]]`.
- In `_batch_fuzzy_match`, instantiate clean `AtomEvaluationResultDTO(status=..., reasoning=...)` instead of tuples.
- In `evaluate_atom_boolean_batch`, build `AtomEvaluationResultDTO` directly from `eval_result`:
  ```python
  call_results[call_tda_id] = AtomEvaluationResultDTO(
      status=status,
      reasoning=eval_result.reasoning,
      source_quote=eval_result.source_quote,
      extensions=extensions,
  )
  ```
- In `resolve_majority_vote` (lines 276–295):
  - Change signature to: `expected_tda_ids: list[str], results: list[dict[str, AtomEvaluationResultDTO] | None] -> dict[str, AtomEvaluationResultDTO]`.
  - Replace index-based access `vote_tuple[0]` with clean typed attribute `vote.status`.
  - On winning consensus, assign the elected `first_seen[status]` directly (`AtomEvaluationResultDTO`), preserving the exact `source_quote` tied to the winning vote.

#### [MODIFY] @[backend_v2/services/orchestrator/topological_evaluator.py#L18-L176]
- Update `TopologicalEvaluator.evaluate_graph` callback type annotation:
  ```python
  batch_evaluation_callback: Callable[
      [list[LinkedAtomGraph], dict[str, AtomExecutionState]],
      Awaitable[dict[str, AtomEvaluationResultDTO]],
  ]
  ```
- Update wave evaluation in `evaluate_graph` to unpack typed attributes and eliminate banned `.get()` lookup (`QGR002`):
  ```python
  if node.atom.tda_id in results:
      res = results[node.atom.tda_id]
      states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
          update={
              "status": res.status,
              "evaluation_reasoning": res.reasoning,
              "source_quote": res.source_quote,
              "extensions": res.extensions,
          }
      )
  else:
      states[node.atom.tda_id] = states[node.atom.tda_id].model_copy(
          update={
              "status": ExecutionStatus.SYSTEM_ERROR,
              "evaluation_reasoning": "Missing from batch response",
          }
      )
  ```

#### [MODIFY] @[backend_v2/services/orchestrator/enriched_dag_executor.py#L28-L186]
- **Phase 1 Technical Debt Cleanup:**
  - Line 95: Clean up inline literal fallback `async with semaphore or asyncio.Semaphore(...)` $\rightarrow$ use explicit null check:
    ```python
    sem = semaphore if semaphore is not None else asyncio.Semaphore(get_settings().max_concurrent_llm_steps)
    async with sem:
    ```
- Update `process_chunk` and `batch_evaluation_callback` signatures and return structures to `dict[str, AtomEvaluationResultDTO]`.
- In error handler (line 124), emit strongly typed error objects instead of tuples:
  ```python
  res = {
      node.atom.tda_id: AtomEvaluationResultDTO(
          status=ExecutionStatus.SYSTEM_ERROR,
          reasoning=f"EVALUATION_CRASH: {str(e)}",
          source_quote=None,
          extensions={},
      )
      for node in chunk
  }
  ```
- Merge pre-flight and LLM results cleanly: `res = {**pre_flight_results, **llm_results}`.

#### [MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L230]
- **Phase 1 Technical Debt Cleanup (CRITICAL):**
  - Line 88: Fix Python 2 syntax `except TypeError, KeyError:` $\rightarrow$ `except (TypeError, KeyError): # fmt: skip` to prevent syntax crashes and ensure `KeyError` is properly trapped.
  - Line 179: Clean up QGR016 ternary fallback on `request.matrix_context`.
- **Phase 4 DAG State Integration:**
  - In starvation short-circuit handling (line 109), populate `AtomExecutionState(tda_id=..., status=ExecutionStatus.FAILED, evaluation_reasoning=..., extensions={})`. `ResultProjector` projects seamlessly from states.

#### [MODIFY] @[backend_v2/services/orchestrator/result_projector.py#L17-L136]
- Fix `ResultProjector.project` to read `source_quote` from runtime state `state.source_quote` for both `AtomResultDTO` and `HydratedAtomDTO`.
- **CRITICAL (Tier 0 Discovery):** Resolve `contextual_override = False` whenever `state.source_quote` is present to prevent `AtomResultDTO.validate_cognitive_vs_system_state` from stripping `source_quote` to `None`:
  ```python
  has_quote = bool(state and state.source_quote)
  contextual_override = False if has_quote else node.atom.is_logical_deduction

  res = AtomResultDTO(
      tda_id=tda_id,
      matrix_id=matrix_id,
      status=status,
      extracted_data=None,
      source_quote=state.source_quote if state else None,
      contextual_override=contextual_override,
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
  - Line 407: Replace ternary fallback on `exact_quotes` (`[QuoteEvidenceDTO(...)] if val_data.source_quote else []`) with clean conditional assignment guarding against empty/whitespace strings: `if (val_data.source_quote and val_data.source_quote.strip())`.
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

#### [MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py#L1436-L1478]
- Expand unit tests to verify:
  1. Standard positive atom (`inverse_evidence: False`) passing $\rightarrow$ `final_state = "TRUE"`.
  2. Inverse evidence atom (`inverse_evidence: True`) passing sensor $\rightarrow$ `final_state = "TRUE"` (confirming no regression to `FAILED`).
  3. Mixed positive and inverse atoms in a multi-level waterfall matrix.
  4. Negative ISTQB equivalence partition verifying that when `status == ExecutionStatus.FAILED`, `final_state = "FALSE"` for both positive and inverse atoms.

#### [MODIFY] @[backend_v2/tests/unit/services/test_matrix_domain_parser.py#L726-L781]
- Expand `test_parse_matrices_context_target_and_xai_extensions` to verify:
  1. Explicit `target_input_key` on `MatrixPromptBlock` resolves to the target input and localized label.
  2. Multiple `$inputs.*` mappings without explicit block key resolve to `"all"` ("Kaikki syötteet" / "All Inputs").
  3. Dedicated single input mapping (`chat_log`) resolves to "Chat Log".

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L376-L502]
- Add tests verifying:
  1. `BooleanEvaluationResult` correctly parses and validates verbatim `source_quote` in its original source language.
  2. Bo3 majority vote consolidates `source_quote` alongside status and reasoning.
  3. `ResultProjector.project()` correctly propagates `source_quote` from `AtomExecutionState` to `AtomResultDTO`.

#### [MODIFY] @[backend_v2/tests/unit/models/dtos/test_dag_models.py#L112-L120]
- Add unit test verifying that `AtomExecutionState` enforces `max_length=500` on `source_quote` and raises `ValidationError` on strings $>500$ characters.
- Add unit test verifying `AtomEvaluationResultDTO` instantiation, immutability (`frozen=True`), `extra="forbid"`, and required `status` validation.

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py#L28-L273]
- Update mock callbacks and return fixtures in `test_execute_graph_callback`, `test_execute_graph_callback_persistent_error`, and `test_execute_graph_callback_transient_error` to return `AtomEvaluationResultDTO` objects.

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py#L28-L234]
- Update mock callbacks in unit tests to return `dict[str, AtomEvaluationResultDTO]` instead of raw tuples.

#### [MODIFY] @[backend_v2/tests/integration/test_topological_evaluator.py#L29-L175]
- Update mock callbacks in integration tests to return `dict[str, AtomEvaluationResultDTO]` instead of raw tuples.

#### [MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L95-L232]
- Ensure integration semantic parity test executes against populated `exact_quotes` and multi-target matrix rows.

---

## Canonical Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Pre-Implementation Technical Debt Cleanups (QGR016, Banned .get(), Broad Except & Python 2 Syntax)">
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py#L88], verify and lock Python 2 syntax fix `except (TypeError, KeyError): # fmt: skip`.</action>
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py#L179], clean up QGR016 ternary fallback on `request.matrix_context`.</action>
    <action>In @[backend_v2/models/dtos/matrix_scorecard.py#L127-L134], verify and lock `except (TypeError, ValueError): # fmt: skip`, and replace banned `.get("status")` and `.get("contextual_override")` with explicit dictionary key membership checks.</action>
    <action>Inspect and resolve all QGR016 advisory AST guardrail warnings in @[backend_v2/hooks/scoring/matrix_hook.py#L38-L487] and @[backend_v2/services/matrix_domain_parser.py#L32-L559].</action>
    <action>In matrix_hook.py:
      1. Replace lines 246 and 248 `.get("_dlq_status")` and `.get("status")` with explicit key checks.
      2. Simplify line 274 to `scales = pb_model.scales` (Pydantic enforces min_length=1).
      3. Replace line 301 with `max(1, total_evals)`.
      4. Replace line 317 `.get("_dlq_status")` with explicit key check `"_dlq_status" in ev_dict_tmp and ev_dict_tmp["_dlq_status"] == "FAILED/DLQ"`.
      5. Replace line 327 with typed context extraction.
      6. Clean up line 397 ternary fallback on `ev_dto.evaluation_reasoning`.
      7. Replace line 454 with direct access `matrix_extensions_by_block[pb_id]` (strictly avoiding banned .get()).
    </action>
    <action>In matrix_domain_parser.py:
      1. Replace line 118 `pb_meta = blocks_by_id.get(b_id)` with explicit key check `b_id in blocks_by_id`.
      2. Replace line 378 `.get(atom_id)` with explicit key check `atom_id in step_evals_map`.
      3. Replace line 407 ternary fallback on `exact_quotes` with clean conditional assignment.
      4. Replace line 412 `val_data.evaluation_reasoning or ""` with explicit null check.
      5. Replace line 420 broad `except Exception:` with specific `except ValidationError:` handling.
      6. Replace line 486 `input_def = expected_inputs_map.get(context_target)` with explicit key check `context_target in expected_inputs_map`.
      7. Resolve ternary fallbacks on lines 492-529 (`ext.*` optional fields).
    </action>
    <action>In @[backend_v2/services/orchestrator/topological_evaluator.py#L18-L177]:
      1. Replace line 108 `results.get(node.atom.tda_id)` with explicit key membership check `node.atom.tda_id in results` (Tier 0 Discovery: QGR016).
      2. Replace line 149 `states[child_id].short_circuit_reason_tda_ids or []` with clean copy `reasons = list(states[child_id].short_circuit_reason_tda_ids); if parent_id not in reasons: reasons.append(parent_id)` to avoid in-place mutation and eliminate QGR016 fallback.
    </action>
    <action>In @[backend_v2/services/orchestrator/enriched_dag_executor.py#L95], replace `async with semaphore or asyncio.Semaphore(...)` with explicit null check (`sem = semaphore if semaphore is not None else asyncio.Semaphore(...)`) to eliminate QGR016 inline fallback.</action>
    <action>In @[backend_v2/services/orchestrator/result_projector.py#L17-L135], replace lines 85-90 ternary fallbacks on `state.*` with an explicit `if state is not None:` block initializing `status`, `reasoning`, `short_circuit`, and `extensions`, eliminating all 4 QGR016 warnings.</action>
    <constraint invariant="the_duct_tape_ban">NEVER use lazy fallbacks, banned .get(), or inline defaults in domain code.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/tda_engine.py`, `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/matrix_scorecard.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/topological_evaluator.py`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/enriched_dag_executor.py` and confirm 0 QGR016 violations.</verification>
  </step>

  <step id="2" name="Phase 2: Eliminate Double-Inversion Bug in Matrix Hook">
    <action>In @[backend_v2/hooks/scoring/matrix_hook.py#L38-L487], surgically replace lines 351–377.</action>
    <action>Eliminate `is_satisfied = not tda.inverse_evidence`. Treat `ev_dto.status == ExecutionStatus.PASSED` as the sovereign truth indicating the assertion was satisfied.</action>
    <action>Properly evaluate `ev_dto.contextual_override` and `effective_override` without inverting the base sensor decision.</action>
    <constraint invariant="universal_fail_fast">Do not guess state; enforce ExecutionStatus contracts strictly.</constraint>
    <verification>Run `uv run pytest backend_v2/tests/unit/hooks/test_scoring.py -k "test_matrix_scoring_hook"`.</verification>
  </step>

  <step id="3" name="Phase 3: Context Target Input Resolution, Flutter Model Parity & Clean-Slate Local Seeding">
    <action>Add `target_input_key: Annotated[str | None, Field(default=None, description="Explicit target input key from workflow expected_inputs (specifically: 'chat_log', 'product_text', 'all').")] = None` to `MatrixPromptBlock` in @[backend_v2/models/domain/prompt_blocks.py#L64-L118] enforcing PEP 593 Annotated syntax per `ki_zero_permissive_typing.md`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/prompt_block.dart#L220-L248], add `@JsonKey(name: 'target_input_key') String? targetInputKey` to `PromptBlock.matrix` Freezed factory.</action>
    <action>Execute Flutter code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/prompt_block.dart --build` to regenerate Freezed and JsonSerializable code with `target_input_key` in allowedKeys.</action>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart#L420-L445], preserve `targetInputKey` during form conversions and rebuilds.</action>
    <action>In @[backend_v2/seed/seed_data.json], populate `target_input_key` across all 13 matrix prompt blocks adhering to the Cognitive SSOT Map (product_text for Toulmin/Bloom/Causal, chat_log for Goodhart/Judge/Performativity, all for holistic matrices).</action>
    <action>Add `matrix_target_all` and `matrix_target_chat_log` translations to @[backend_v2/l10n/fi.json#L50-L65] and @[backend_v2/l10n/en.json#L50-L65].</action>
    <action>Execute Clean-Slate Local Seeding: `uv run python backend_v2/seed/run_seed.py local` to perform in-memory validation, drop TinyDB tables, wipe legacy executions from `data/files/executions/`, and seed a pure clean slate.</action>
    <action>In @[backend_v2/services/matrix_domain_parser.py#L32-L559], replace legacy first-item break loop with three-tier deterministic multi-input resolution.</action>
    <constraint invariant="zero_service_layer_fallbacks">Never break arbitrarily on first dict element.</constraint>
    <constraint invariant="the_no_legacy_mandate">Never build backward-compatibility bridges for old runs; purge and seed clean slate.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart`.</verification>
  </step>

  <step id="4" name="Phase 4: Sensor Quote Extraction Putki, AtomEvaluationResultDTO & Language-Agnostic Caching Prefix (Option A)">
    <action>In @[backend_v2/models/dtos/dag_models.py#L114-L144], define `AtomEvaluationResultDTO` with `status`, `reasoning`, `source_quote: str | None = None` (max_length=500), and `extensions: dict[str, str] = {}` under `ConfigDict(extra="forbid", strict=True, frozen=True)` to permanently eliminate Tuple Hell.</action>
    <action>In @[backend_v2/models/dtos/dag_models.py#L114-L144], add `source_quote: Annotated[str | None, Field(default=None, max_length=500)] = None` to `AtomExecutionState`.</action>
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py#L26-L52], add `source_quote: Annotated[str | None, Field(default=None, max_length=500)] = None` with `@field_validator(mode="before")` sentence-boundary truncation to `BooleanEvaluationResult`, and add `source_quote: str | None = None` to `PreFlightResult`.</action>
    <action>In @[backend_v2/models/prompts/matrix_evaluation.py#L1-L26], append language-agnostic `<evidence_extraction_mandate>` requiring verbatim quote extraction strictly in the raw, original language of the source text without translation.</action>
    <action>In @[backend_v2/models/prompts/global_mandates.py#L22-L34], update `LANGUAGE_MANDATE` Exception 2 to explicitly include `source_quote` alongside `exact_quotes`.</action>
    <action>In @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L24-L209], preserve 100% static prefix caching without injecting dynamic locale.</action>
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L434], update `batch_pre_evaluate`, `evaluate_atom_boolean_batch`, and `resolve_majority_vote` to emit and return `dict[str, AtomEvaluationResultDTO]`, replacing `vote_tuple[0]` with `vote.status`.</action>
    <action>In @[backend_v2/services/orchestrator/enriched_dag_executor.py#L28-L186], update `process_chunk` and `batch_evaluation_callback` to return `dict[str, AtomEvaluationResultDTO]`, emitting strongly typed error instances.</action>
    <action>In @[backend_v2/services/orchestrator/topological_evaluator.py#L18-L176], update callback type annotation to `Awaitable[dict[str, AtomEvaluationResultDTO]]` and unpack typed attributes (`res.status`, `res.reasoning`, `res.source_quote`, `res.extensions`) into `AtomExecutionState.model_copy(update={...})` per Two-Tier Validation Firewall.</action>
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L231], ensure starvation short-circuit and execution flows transit cleanly through states.</action>
    <action>In @[backend_v2/services/orchestrator/result_projector.py#L17-L136], project `source_quote` from `state.source_quote` into both `AtomResultDTO` and `HydratedAtomDTO`, explicitly resolving `contextual_override = False` whenever `state.source_quote` is present to prevent `AtomResultDTO` validator from stripping the quote.</action>
    <constraint invariant="strict_physical_anchoring_mandate">Enforce exact verbatim quotes in original source language; prohibit chimera quotes or translation of quotes.</constraint>
    <constraint invariant="pydantic_validation_bypass_ban">Validate untrusted ingress with model_validate; mutate internal high-throughput frozen states via model_copy with pre-validated typed variables inside locks.</constraint>
    <constraint invariant="no_naked_dicts_in_state">Banned all untyped tuples in domain state transit; enforce AtomEvaluationResultDTO universally.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/enriched_dag_executor.py`, `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/topological_evaluator.py`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/result_projector.py`.</verification>
  </step>

  <step id="5" name="Phase 5: ISTQB Unit & Integration Test Expansion for Scoring, Parser, DAG & Sensor Quotes">
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py#L1436-L1478], add unit test `test_matrix_scoring_hook_inverse_evidence_passed_satisfies_level`.</action>
    <action>In @[backend_v2/tests/unit/services/test_matrix_domain_parser.py#L726-L781], add test cases for single-input, multi-input ("all"), and prompt-block explicit target resolution.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py#L376-L502], add test verifying `source_quote` extraction in original language, Bo3 consensus, and projection to `AtomResultDTO`.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_dag_models.py#L112-L120], add test verifying `AtomEvaluationResultDTO` strict schema validation and `AtomExecutionState.source_quote` max_length constraint.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_enriched_dag_executor.py#L28-L273], @[backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py#L28-L234], and @[backend_v2/tests/integration/test_topological_evaluator.py#L29-L175], update mock callback fixtures to return `AtomEvaluationResultDTO` instances.</action>
    <constraint invariant="anti_happy_path_mandate">Cover both positive and negative equivalence partitions.</constraint>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring/matrix_hook.py --test`, `uv run python scripts/backend_audit_loop.py backend_v2/services/matrix_domain_parser.py --test`, and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test`.</verification>
  </step>

  <step id="6" name="Phase 6: Global Audit, Clean Slate Trace Replay & SDUI Parity Validation">
    <action>Execute full backend audit loop across all scoring hooks, matrix parser, and sensor orchestrator.</action>
    <action>Execute SDUI semantic parity test: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py#L95-L232`.</action>
    <action>Execute full Flutter audit loop across client_app_v2: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart` and `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart`.</action>
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
6. **Frontend Domain Parity & SDUI Widget Tests:**
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/test/models/domain_parity_test.dart --build
   uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart
   ```
7. **Clean-Slate Database Seeding Command:**
   ```powershell
   uv run python backend_v2/seed/run_seed.py local
   ```
8. **AST Guardrail Validation:**
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
