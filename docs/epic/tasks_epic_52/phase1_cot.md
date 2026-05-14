# Phase 1: Exhaustive Pydantic Chain-of-Thought (CoT)

## Objective
Eradicate LLM Order Bias by enforcing a deterministic evaluation workflow before final scoring using strict Pydantic V2 schemas. 

## Target Files
1. `c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler.py`
2. `c:\src\quorum\backend_v2\models\v2_core.py` (if any schema extracts are required)

## Tasks
1. **Locate AtomResponse**: Inside `prompt_compiler.py`, locate the dynamically generated `AtomResponse` schema (approx line 421) and the schema extensions (e.g. `extension_coaching`, `extension_falsification`).
2. **Rename Fields**: Apply the `step_` numerical prefix mandate to all cognitive outputs:
   - `reasoning_trace` -> `step_1_reasoning_trace`
   - `extension_falsification` -> `step_2_falsification`
   - `extension_coaching` -> `step_3_coaching`
   - `rule_satisfied` -> `step_4_rule_satisfied`
   - `evidence_found` -> `step_5_evidence_found`
3. **Pydantic Aliases**: If legacy frontend consumers still expect the old names (like `reasoning_trace`), use `Field(alias="step_1_reasoning_trace")` so Pydantic handles the parsing automatically while the LLM generates the ordered key.
4. **Audit Anti-Sycophancy**: Verify that the `<ANTI_SYCOPHANCY_MANDATE>` and other mandatory system prompt additions from `prompt_compiler.py` align with these new field names.

## Acceptance Criteria
- Pydantic V2 schemas compile successfully.
- LLM response keys are strictly enforced in alphabetical/numerical order by the parser.
- Existing frontend rendering does not break (due to aliases/mappings).
