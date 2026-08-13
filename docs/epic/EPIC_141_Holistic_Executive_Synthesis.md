# EPIC 141: Holistic Executive Synthesis & RAG Alignment

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore the deep, analytical, and humanistic "Soul" to the Executive Summary (Synthesis Generation) and the XAI Row Explanations. The system must produce rich, topic-aware qualitative texts (as it did in early July 2026) while maintaining the strict, hallucination-free Zero-Trust verification of the Tripartite pipeline.

### Problem Statement
Currently, the Quorum architecture produces robotic, disjointed text during the Synthesis phase and Matrix XAI phase. The Synthesis LLMs and Matrix Evaluator LLMs desperately try to build a cohesive narrative from abstract boolean proofs without actually knowing what the user's claims were.

### Root Cause / Gap Analysis
This problem stems from three architectural "sabotage" points that completely blind the LLM nodes:

1. **The 20-Atom Cutoff (Distiller Sabotage):**
   In `synthesis_distiller.py` (@[backend_v2/services/orchestrator/synthesis_distiller.py#L30-L113]), a brutal token-saving cap exists: `lite_evals = lite_evals[:20]`. The Synthesis LLM sees only 20 random mathematical truths from the execution, discarding up to 80% of facts.

2. **Loss of Claim Context (`resolved_claim`) & Anaphora Sabotage:**
   The Anaphora Resolution pipeline resolves ambiguous pronouns into explicit claims via `resolved_claim`. However, `synthesis_distiller.py` (@[backend_v2/services/orchestrator/synthesis_distiller.py#L30-L113]) strips this critical field from the `lite_ev` dict, forwarding only the unresolved `exact_quotes` text (containing bare pronouns, specifically "It crashed"). The Synthesis LLM is forced to guess facts from dangling pronoun references.

3. **Causal Graph & Execution Status Erasure (DAG Sabotage):**
   The DAG pipeline builds a hierarchical causal graph (`depends_on` via `LinkedAtomGraph.depends_on: list[CausalEdge]` in @[backend_v2/models/dtos/dag_models.py#L94-L111]). However, `synthesis_distiller.py` cuts the `lite_ev` object so aggressively that it removes all causality data. Additionally, `matrix_sensor_prompt_builder.py` (@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L89-L157]) generates XAI extensions (specifically and exhaustively English Enums: `PRACTICAL_TIP` and `COUNTER_ARGUMENT`, per the `no_string_l10n` and `native_english_generation_mandate` rules) without injecting the atom's dependency statuses into the prompt. The LLM evaluates claims in a blind vacuum without understanding the causal event chain.

## 2. Architectural Impact & Safeguards

- **UI & DB Sovereignty (The Orchestration Rule):** The UI (Input Mappings) and consequently the database's `context_injections` govern execution 100%. If the UI does not route source texts to Synthesis, the backend MUST NOT read them (Zero-Trust Source Isolation). If the UI *does* route text to Synthesis, the backend must obey unconditionally.
- **Enriched Atom Dependency:** Because the Synthesis LLM is by default "blind" to the original document, it must receive ALL required context directly from the atoms. Therefore, `resolved_claim` (containing the anaphora-resolved full context) and `depends_on` (containing the causal chain) are absolutely vital for Synthesis and Row Explanations.
- **Tripartite Boundary Compliance:** These changes operate across Phase 1 (Execution) and Phase 2 (Synthesis) of the Tripartite Pipeline, but strictly enforce the boundary between them. Phase 1 provides enriched causal dependency data, and Phase 2 consumes it exclusively via `list[StepOutputDTO]` envelopes (enforcing PEP 695 modern syntax). No SDUI/Presentation logic is introduced. Ensure that Synthesis LLM outputs strictly map to `section_syntheses` (avoiding generic string arrays) to comply with the SDUI Polymorphic Synthesis Mandate.

## 3. Proposed Changes (Technical Implementation Plan)

### Phase 1: Restore UI/DB Sovereignty (Remove Hardcoded Blueprint Bypass)
- **Target Files**:
  - @[backend_v2/services/orchestrator/dag_executor.py#L558-L750]
- **Action:** Remove the hardcoded check `if step_obj.task_blueprint == "sp_7a8b9c0d1e2f3a4b":` at line 584.
- **Implementation:** The engine is currently hardcoded to run `MatrixReducer` ONLY if the step's `task_blueprint` ID is exactly that specific string. This completely breaks database-driven orchestration: if a new workflow is created in the UI and the Synthesis step receives a new ID, the execution will silently skip the MatrixReducer.
- **Fix:** Replace the hardcoded ID check with dynamic strategy inference using the existing `Step.model_strategy` field (@[backend_v2/models/v2_core.py#L706-L795]).
- **Exact Lookup Chain:** `step_obj` (which is a `StepRule`) → `step_def_map[step_obj.task_blueprint]` (resolves to a `Step` instance) → `step_def.model_strategy == "synthesis"`. The `step_def_map` is already constructed from `all_steps` in the executor initialization.
- **Verification:** The seed data confirms `sp_7a8b9c0d1e2f3a4b` has `"model_strategy": "synthesis"` (@[backend_v2/seed/seed_data.json#L9053-L9056]), ensuring behavioral parity after migration.

### Phase 2: Synthesis Distiller Bottleneck Removal & God Code Prevention
- **Target Files**:
  - [MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py#L30-L113]
  - [NEW] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [MODIFY] @[backend_v2/settings.py#L42-L598]
  - [MODIFY] @[backend_v2/models/domain/synthesis.py]
- **God Code Prevention Mandate:** Because `synthesis_distiller.py` is over 500 lines (a God File), you MUST NOT append new private helpers or bloat existing methods per the `private_helper_bloat_ban` and `anti_god_file_dumping` rules. You MUST extract the `_compress_synthesis_payload` logic and the new context cross-referencing logic into a dedicated new module (specifically: [NEW] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]).
- **Action (Extraction):** Move the compression logic out of `synthesis_distiller.py` into the [NEW] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] module. Update `synthesis_distiller_hook` to import and call this new module.
- **Action (Configuration):** Remove the blind `[:20]` cutoff at line 98.
- **Replace With:** A configurable limit sourced from the application configuration SSOT (@[backend_v2/settings.py#L42-L598], specifically a [NEW] field `max_synthesis_evaluations: Annotated[int, Field(description="Maximum evaluations forwarded to synthesis LLM")] = 60`, respecting the `strict_configuration_segregation` mandate. **Architectural Rationale:** This limit protects the LLM token budget from exploding. Because token budgets are environment-dependent (specifically: Local models vs. Cloud Vertex AI limits), this value MUST NOT be stored in the database. Storing infrastructure limits in the database violates the database ban for environment variables). This preserves token budget control while removing the arbitrary blindness.
- **Enrich `lite_ev` -> DistilledEvaluation:** The backend must safely strip massive Pydantic metadata inside the execution state BEFORE it hits the `synthesis_generation` step. This Epic mandates replacing the naked dict with a new [NEW] `DistilledEvaluation` model (@[backend_v2/models/domain/synthesis.py]) to guarantee schema strictness.
- **Consumer Crash Prevention:** When changing the `lite_ev` dictionary to a strict `DistilledEvaluation` Pydantic model, its consumer (specifically: @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L20-L161]) MUST also be updated. If the engine attempts to read the instance as a dictionary (specifically: `eval["resolved_claim"]`), the program will crash with a `TypeError: 'DistilledEvaluation' object is not subscriptable`. This must be corrected to use object references (specifically: `eval.resolved_claim`).
- **Frontend Parsing Crash Prevention:** If the new DTO structure is transmitted across the API boundary to the Dart/Flutter client, the Dart Freezed models (specifically: `client_app_v2/lib/features/execution/models/distilled_evaluation.dart`) MUST be updated synchronously and enforce strict JSON conformity by setting `disallowUnrecognizedKeys: true` on the `@Freezed` annotation. If the backend schema changes without a matching Dart `freezed` model update, the UI will immediately crash with a `CheckedFromJsonException`. Both systems must maintain strict schema parity.

### 2. DAG Engine Semantic Data Erasure

**Current State**: In the DAG pipeline, when a child node executes, it only knows its parent's TDA ID, but it lacks the contextual status (`expected_status` vs `actual_status`) that caused an N_A status (Blame determinism).
**Target Solution**: Epic mandates extracting a `lightweight_matrix` inside `DAGExecutor` using a native topological Reducer. The payload MUST be parsed into its strict Pydantic model (specifically: `SynthesisStepDataDTO`) before processing.
  - `resolved_claim`: The anaphora-resolved standalone claim text.
  - `depends_on`: List of parent dependency atom IDs (mapped to short Aliases via `AliasEngine`).
  - `status`: The execution status (typed as `ExecutionStatus` Enum natively) of this atom.
  - `short_circuit_reason_tda_ids`: The list of parent aliases that caused an `N_A` status (Blame determinism).
  - `is_logical_deduction`: Ensure atoms without `exact_quotes` (where `is_logical_deduction` is True) are NOT silently dropped by the `if valid_quotes:` check.
  - **Reasoning Preservation:** Stop truncating `semantic_reasoning` / `evaluation_reasoning` to 300 characters. Epic 92 relies on this "Reason-then-Format" trace.
- **Cross-Reference Mechanism (In New File):** The extracted payload compression function consumes the `list[StepOutputDTO]` envelope from Phase 1. **CRITICAL RULE:** You MUST NOT operate on serialized `StepOutputDTO.payload` raw dicts, which violates the `event_driven_data_envelopes` mandate. The payload MUST be parsed into its strict Pydantic model (specifically: `SynthesisStepDataDTO`) before processing. These evaluation payloads contain `atom_id` (or `tda_id`) but NOT `resolved_claim` or `depends_on`, which live in the extraction-phase `LinkedAtomGraph` nodes. To bridge this gap, a new helper method inside [NEW] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] MUST pre-build a global lookup map (`tda_id_to_atom_context: dict[str, LinkedAtomGraph]`) by iterating over the strongly-typed `available_dtos` extraction payloads. **Pydantic Validation Crash Prevention:** Because `available_dtos` is a heterogeneous list containing outputs from ALL previous steps (chunking, mapping, etc.), you MUST filter the list by strategy (specifically: `step_strategy == "extraction"`) before attempting to parse the payloads into `LinkedAtomGraph`. Attempting to blindly parse all DTOs will cause an immediate Pydantic `ValidationError`. This map is then used to enrich each `DistilledEvaluation` via the `atom_id` join key. **CRITICAL RULE:** You MUST perform this join using strict dictionary access (specifically: `tda_id_to_atom_context[atom_id]`) to enforce deterministic Fail-Fast KeyError crashes if an ID is missing. The use of `.get()` or `try/except` fallback blocks is strictly prohibited per the Zero Compromise Pledge.
- **Result:** This restores the causal graph and context-aware claims back to the Synthesis LLM and Row Explanation generation, making separate RAG source text reading unnecessary, while enforcing modularity and God Code prevention.

### Phase 3: Matrix Sensor Causal Alignment (XAI)
- **Target Files**:
  - @[backend_v2/models/dtos/dag_models.py#L94-L111]
  - @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L89-L157]
  - @[backend_v2/services/orchestrator/dag_executor.py#L558-L750]
  - [NEW] @[backend_v2/services/orchestrator/extractive_sensor_service.py]
- **Action:** Inside the `<claim>` XML generation loop (lines 117-141), inject `<depends_on>` tags for each node's causal dependencies using a strict structural template engine (specifically: Jinja macros, `PromptBlock` assembly, or Pydantic XML wrappers).
- **Data Source:** The `LinkedAtomGraph.depends_on` field contains a `list[CausalEdge]` where each `CausalEdge` has `parent_tda_id` and `expected_status`. This data is already available on the `nodes` parameter.
- **Implementation:** For each `node` in the loop, iterate over `node.depends_on`. For each `CausalEdge`, generate a `<dependency>` tag specifying the resolved `parent_alias`, `expected_status`, AND `actual_status` (retrieved from `atom_status_map` using strict dictionary access `atom_status_map[edge.parent_tda_id]`). **CRITICAL RULE:** You MUST strictly avoid raw Python f-string concatenation (specifically the pattern: `f"<dependency alias='{alias}'/>"`) when assembling these tags. Raw f-string injection violates the `high_fidelity_prompting_and_caching` and `prompt_asset_ssot_mandate` rules. Use `TemplateProcessor` or Jinja rendering.
- **Caching Parity:** These new tags are injected into the `dynamic_messages` partition (the `<execution_parameters>` user message), so the `static_messages` remain 100% cacheable. No caching parity violation.
- **Action:** To provide runtime status context, the `build_compiled_prompt` method signature MUST be extended with a new parameter: `atom_status_map: dict[str, ExecutionStatus]` (mapping `tda_id` to its current execution status). This map is constructed by the caller (@[backend_v2/services/orchestrator/extractive_sensor_service.py]) from the `AtomExecutionState` results of already-evaluated parent nodes. **False-Positive KeyError Prevention (Pre-hydration):** To safely support strict dictionary access (`atom_status_map[tda_id]`) without triggering false-positive crashes when the DAG engine short-circuits (skips) a parent node, the caller MUST pre-hydrate the map with default `PENDING` or `N_A` statuses for all known `tda_id`s in the graph before applying the actual execution results. Any subsequent `KeyError` will then mathematically prove a genuinely corrupted/hallucinated UUID.
- **Result:** This allows the Matrix Evaluator LLM to write deep, causal output extensions (specifically and exhaustively English Enums: `PRACTICAL_TIP` and `COUNTER_ARGUMENT`) instead of evaluating claims in a vacuum without seeing the original document.

### Phase 4: Atomic Test Alignment
- **Target Files**:
  - @[backend_v2/tests/unit/test_synthesis_payload_compression.py]
  - [NEW] @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]
  - @[backend_v2/tests/unit/test_dag_taskgroup.py]
- **Action 1 (Fixture Migration)**: Because Phase 2 alters the structure of `lite_ev`, you MUST simultaneously update the mocked test fixtures in @[backend_v2/tests/unit/test_bug_synthesis_hook.py#L9-L21] and @[backend_v2/tests/unit/test_epic93_contract_verification.py#L205-L230] in the exact same phase, otherwise the test suite will crash continuously in a failure loop.
- **Action 2 (New Test Creation)**: Phase 3 requires creating a [NEW] test file (@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]) to validate that `<depends_on>` tags appear in the compiled prompt output.

## 4. Verification Plan

### Automated Tests
- Run `uv run python @[scripts/backend_audit_loop.py] . --test` to ensure strict typing and formatting pass across the backend.
- Ensure no regressions in existing synthesis unit tests.

### Manual Verification
- Execute a full backend run and inspect `llm_debug_prompts.md` / Logfire traces to verify that:
  1. `resolved_claim` and `depends_on` are present in the distilled synthesis payload for both Synthesis and Row Explanations.
  2. `<dependency>` tags are correctly appearing inside `<claim>` blocks in the Matrix Sensor prompt.
  3. The configurable `max_synthesis_evaluations` limit from the configuration is respected.

## 5. Required Knowledge Items (KI Registry)
<required_knowledge_items>
- @[ki_context_enriched_decompose_verify.md]
- @[ki_matrix_sensor_prompt_builder.md]
- @[ki_dag_engine_dto_projection_rules.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_ai_testing_standards.md]
- @[ki_de_generator_execution_paradigm.md]
- @[ki_llm_extraction_architecture.md]
- @[ki_execution_engine_protocol.md]
- @[ki_god_code_prevention.md]
- @[ki_sdui_matrix_synthesis.md]
- @[.agents/rules/01-python-backend.md]
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/02_flutter_desktop.md]
</required_knowledge_items>
