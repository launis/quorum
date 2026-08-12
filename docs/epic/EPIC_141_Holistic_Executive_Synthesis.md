# EPIC 141: Holistic Executive Synthesis & RAG Alignment

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore the deep, analytical, and humanistic "Sielu" (Soul) to the Executive Summary (Synthesis Generation) and the XAI Row Explanations. The system must produce rich, topic-aware qualitative texts (as it did in early July 2026) while maintaining the strict, hallucination-free Zero-Trust verification of the Tripartite pipeline.

### Problem Statement
Currently, the Quorum architecture produces robotic, disjointed text during the Synthesis phase and Matrix XAI phase. The Synthesis LLMs and Matrix Evaluator LLMs desperately try to build a cohesive narrative from abstract boolean proofs without actually knowing what the user's claims were.

### Root Cause / Gap Analysis
This problem stems from three architectural "sabotage" points that completely blind the LLM nodes:

1. **The 20-Atom Cutoff (Distiller Sabotage):**
   In `synthesis_distiller.py` ([synthesis_distiller.py](file:///c:/src/quorum/backend_v2/services/orchestrator/synthesis_distiller.py#L97-L98)), a brutal token-saving cap exists: `lite_evals = lite_evals[:20]`. The Synthesis LLM sees only 20 random mathematical truths from the execution, discarding up to 80% of facts.

2. **Loss of Claim Context (`resolved_claim`) & Anaphora Sabotage:**
   The Anaphora Resolution pipeline resolves ambiguous pronouns into explicit claims via `resolved_claim`. However, `synthesis_distiller.py` ([_compress_synthesis_payload](file:///c:/src/quorum/backend_v2/services/orchestrator/synthesis_distiller.py#L89-L96)) strips this critical field from the `lite_ev` dict, forwarding only the unresolved `exact_quotes` text (containing bare pronouns, specifically "It crashed"). The Synthesis LLM is forced to guess facts from dangling pronoun references.

3. **Causal Graph & Execution Status Erasure (DAG Sabotage):**
   The DAG pipeline builds a hierarchical causal graph (`depends_on` via `LinkedAtomGraph.depends_on: list[CausalEdge]` in [dag_models.py](file:///c:/src/quorum/backend_v2/models/dtos/dag_models.py#L94-L111)). However, `synthesis_distiller.py` cuts the `lite_ev` object so aggressively that it removes all causality data. Additionally, `matrix_sensor_prompt_builder.py` ([build_compiled_prompt](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L89-L157)) generates XAI extensions (specifically and exhaustively: `ARJEN VINKKI` and `VASTA-ARGUMENTTI`) without injecting the atom's dependency statuses into the prompt. The LLM evaluates claims in a blind vacuum without understanding the causal event chain.

## 2. Architectural Impact & Safeguards

- **UI & DB Sovereignty (The Orchestration Rule):** The UI (Input Mappings) and consequently the database's `context_injections` govern execution 100%. If the UI does not route source texts to Synthesis, the backend MUST NOT read them (Zero-Trust Source Isolation). If the UI *does* route text to Synthesis, the backend must obey unconditionally.
- **Enriched Atom Dependency:** Because the Synthesis LLM is by default "blind" to the original document, it must receive ALL required context directly from the atoms. Therefore, `resolved_claim` (containing the anaphora-resolved full context) and `depends_on` (containing the causal chain) are absolutely vital for Synthesis and Row Explanations.
- **Tripartite Boundary Compliance:** These changes strictly operate within the Synthesis Phase (Phase 2) of the Tripartite Pipeline. No execution-phase logic is being moved, and no SDUI/Presentation logic is introduced.

## 3. Proposed Changes (Technical Implementation Plan)

### Phase 1: Restore UI/DB Sovereignty (Remove Hardcoded Blueprint Bypass)
- **Target File:** [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py#L583-L606)
- **Action:** Remove the hardcoded check `if step_obj.task_blueprint == "sp_7a8b9c0d1e2f3a4b":` at line 584.
- **Implementation:** The engine is currently hardcoded to run `MatrixReducer` ONLY if the step's `task_blueprint` ID is exactly that specific string. This completely breaks database-driven orchestration: if a new workflow is created in the UI and the Synthesis step receives a new ID, the execution will silently skip the MatrixReducer.
- **Fix:** Replace the hardcoded ID check with dynamic strategy inference using the existing `Step.model_strategy` field ([v2_core.py#L752](file:///c:/src/quorum/backend_v2/models/v2_core.py#L752-L758)).
- **Exact Lookup Chain:** `step_obj` (which is a `StepRule`) → `step_def_map[step_obj.task_blueprint]` (resolves to a `Step` instance) → `step_def.model_strategy == "synthesis"`. The `step_def_map` is already constructed from `all_steps` in the executor initialization.
- **Verification:** The seed data confirms `sp_7a8b9c0d1e2f3a4b` has `"model_strategy": "synthesis"` ([seed_data.json#L9053-L9056](file:///c:/src/quorum/backend_v2/seed/seed_data.json#L9053-L9056)), ensuring behavioral parity after migration.

### Phase 2: Synthesis Distiller Bottleneck Removal
- **Target File:** [synthesis_distiller.py](file:///c:/src/quorum/backend_v2/services/orchestrator/synthesis_distiller.py)
- **Action:** Modify `_compress_synthesis_payload()` ([lines 30-113](file:///c:/src/quorum/backend_v2/services/orchestrator/synthesis_distiller.py#L30-L113)).
- **Remove:** The blind `[:20]` cutoff at line 98.
- **Replace With:** A configurable limit sourced from the application configuration SSOT (specifically a [NEW] field `max_synthesis_evaluations: Annotated[int, Field(description="Maximum evaluations forwarded to synthesis LLM")]` with a default value of 60, respecting the `strict_configuration_segregation` mandate). This preserves token budget control while removing the arbitrary blindness.
- **Enrich `lite_ev`:** The current `lite_ev` dict (lines 89-96) contains ONLY `atom_id`, `exact_quotes`, `semantic_reasoning` (truncated), and `extensions`. This Epic mandates adding/fixing the following keys to restore Epic 92 functionality:
  - `resolved_claim`: The anaphora-resolved standalone claim text.
  - `depends_on`: List of parent dependency atom IDs (mapped to short Aliases via `AliasEngine`).
  - `status`: The execution status (`PASSED`, `FAILED`, `N_A`) of this atom.
  - `short_circuit_reason_tda_ids`: The list of parent aliases that caused an `N_A` status (Blame determinism).
  - `is_logical_deduction`: Ensure atoms without `exact_quotes` (where `is_logical_deduction` is True) are NOT silently dropped by the `if valid_quotes:` check.
  - **Reasoning Preservation:** Stop truncating `semantic_reasoning` / `evaluation_reasoning` to 300 characters. Epic 92 relies on this "Reason-then-Format" trace.
- **Cross-Reference Mechanism:** The `_compress_synthesis_payload()` function operates on serialized `StepOutputDTO.payload` dicts. These evaluation payloads contain `atom_id` (or `tda_id`) but NOT `resolved_claim` or `depends_on`, which live in the extraction-phase `LinkedAtomGraph` nodes. To bridge this gap, the caller (`synthesis_distiller_hook`) MUST pre-build a global lookup map (`tda_id_to_atom_context: dict[str, dict]`) by iterating over all `available_dtos` with extraction-type payloads (containing `results` arrays with `ExtractedAtom`-shaped items) BEFORE calling `_compress_synthesis_payload()`. This map must then be passed as a parameter to `_compress_synthesis_payload()`, which uses it to enrich each `lite_ev` via the `atom_id` join key.
- **Result:** This restores the causal graph and context-aware claims back to the Synthesis LLM and Row Explanation generation, making separate RAG source text reading unnecessary.

### Phase 3: Matrix Sensor Causal Alignment (XAI)
- **Target File:** [matrix_sensor_prompt_builder.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py#L89-L157)
- **Action:** Inside the `<claim>` XML generation loop (lines 117-141), inject `<depends_on>` tags for each node's causal dependencies using `TemplateProcessor.encapsulate_payload` (strictly avoiding XML f-string prompt injection vulnerabilities).
- **Data Source:** The `LinkedAtomGraph.depends_on` field contains a `list[CausalEdge]` where each `CausalEdge` has `parent_tda_id` and `expected_status`. This data is already available on the `nodes` parameter.
- **Implementation:** For each `node` in the loop, iterate over `node.depends_on`. For each `CausalEdge`, emit a `<dependency alias="{parent_alias}" expected_status="{edge.expected_status.value}"/>` tag inside the `<claim>` block. The `parent_alias` is resolved via the existing `tda_id_to_alias` mapping parameter.
- **Caching Parity:** These new tags are injected into the `dynamic_messages` partition (the `<execution_parameters>` user message), so the `static_messages` remain 100% cacheable. No caching parity violation.
- **Action:** To provide runtime status context, the `build_compiled_prompt` method signature MUST be extended with a new parameter: `atom_status_map: dict[str, ExecutionStatus]` (mapping `tda_id` to its current execution status). This map is constructed by the caller (`extractive_sensor_service.py`) from the `AtomExecutionState` results of already-evaluated parent nodes.
- **Result:** This allows the Matrix Evaluator LLM to write deep, causal output extensions (specifically and exhaustively: `ARJEN VINKKI` and `VASTA-ARGUMENTTI`) instead of evaluating claims in a vacuum without seeing the original document.

## 4. Verification Plan

### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py . --test` to ensure strict typing and formatting pass across the backend.
- Ensure no regressions in existing synthesis unit tests.
- **ATOMIC DATA FIXTURE MIGRATION:** Because Phase 2 alters the structure of `lite_ev`, you MUST simultaneously update the mocked test fixtures in [test_bug_synthesis_hook.py](file:///c:/src/quorum/backend_v2/tests/unit/test_bug_synthesis_hook.py) and [test_epic93_contract_verification.py](file:///c:/src/quorum/backend_v2/tests/unit/test_epic93_contract_verification.py) in the exact same phase, otherwise the test suite will crash continuously in a failure loop.
- Phase 3 requires creating a NEW test file: `backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py` to validate that `<depends_on>` tags appear in the compiled prompt output.

### Manual Verification
- Execute a full backend run and inspect `llm_debug_prompts.md` / Logfire traces to verify that:
  1. `resolved_claim` and `depends_on` are present in the distilled synthesis payload for both Synthesis and Row Explanations.
  2. `<dependency>` tags are correctly appearing inside `<claim>` blocks in the Matrix Sensor prompt.
  3. The configurable `max_synthesis_evaluations` limit from the configuration is respected.

## 5. Required Knowledge Items (KI Registry)
<required_knowledge_items>
- Context-Enriched Decompose-Verify Pipeline
- MatrixSensorPromptBuilder & Caching Parity
- DAG Engine and DTO Projection Rules (Epic 91.5, 92, 93 Harmonization)
- Tripartite Pipeline Architecture
- AI Testing Standards
- De-Generator Execution Paradigm
- LLM Extraction Architecture (Steps, Protocols, Matrices, Overrides)
- Execution Engine Protocol & TDA Engine Extraction
- God Code Prevention (Epic 133)
</required_knowledge_items>
