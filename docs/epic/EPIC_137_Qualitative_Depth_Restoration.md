# EPIC 137: Qualitative Depth Restoration & TDA Extraction Fix

## Objective
1. Restore the qualitative depth of the LLM Synthesis phase by upgrading the Output Profile tone instruction from a generic "neutral and analytical" setting to an explicit Senior Executive Coach persona.
2. Restore cognitive depth to the **Extraction Phase** (TDAEngine). EPIC 92's DAG migration accidentally replaced the matrix-specific epistemic anchors with a generic "is this true" check in `ExtractiveSensorService`. We will use the native `theory_grounding` (RAG) fields from the Matrix block and inject them directly into the evaluation prompt.
3. Remove dead code left behind by EPIC 92's architectural migration, and clean up the `ai_description` in the database to comply with the Step-Level Protocol Mandate.

## Scope
- **Target Files:**
  - `@[c:\src\quorum\backend_v2\seed\seed_data.json]` — tone fix + ai_description cleanup
  - `@[c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py]` — inject `<theory_grounding>` into evaluation prompt
  - `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]` — fetch matrix block and pass `theory_grounding` to SensorService
  - `@[c:\src\quorum\backend_v2\services\orchestrator\localization_compiler.py]` — remove `compile_xml_rubrics()`
  - `@[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler.py]` — remove `compile_xml_rubrics()` wrapper
  - `@[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler_adapter.py]` — remove `compile_chunk_prompt()`

## Root Cause Analysis
The `OutputProfile`'s `tone_instruction` has degraded to a generic robotic instruction:
```json
{
  "fi": "Käytä asiallista, neutraalia ja analyyttistä sävyä.",
  "en": "Use professional, neutral, and analytical tone."
}
```
However, fixing this alone is insufficient ("Lipstick on a Pig"). Post-EPIC 92, the `TDAEngine` delegates extraction to `ExtractiveSensorService`, which uses a completely generic prompt: `"Evaluate if the following claims are true based strictly on the provided context."`

### The Theory Grounding (RAG) Solution
The matrices in `seed_data.json` already contain structured `theory_grounding` fields (e.g., `citation_reference`, `source_url`). Instead of relying on the messy `ai_description` (which violates the Step-Level Protocol Mandate by mixing Domain Knowledge with Extraction Rules), we will formally pipe the `theory_grounding` structured data into the `ExtractiveSensorService`.

## Proposed Changes

### Phase 1: Synthesis Quality Fix

#### [MODIFY] `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- **Output Profile Tone:** Upgrade the `tone_instruction` for `prf_5d6e7f8091a2b3c4` (Holistic Audit) to include explicit persona instructions:
  - EN: "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data."
  - FI: "Toimi ylemmän johdon valmentajana (Senior Executive Coach). Tarjoa syvällistä, provosoivaa ja strategista analyysiä pelkän datan luettelemisen sijaan."

### Phase 2: Dead Code, Database Hygiene & English RAG Standardization

#### [MODIFY] `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- **Matrix `ai_description` Cleanup:** Remove the `\nRULES:\n- Bounty Hunter Paradigm...` suffix from the `ai_description` of the 9 matrices (e.g. Toulmin, Bloom, Kahneman, Goodhart).
- Since we are now using `theory_grounding` for the epistemic anchors, the `ai_description` can be drastically simplified or cleared of redundant rules to maintain architectural hygiene.
- **English RAG Standardization:** Translate any Finnish citations (like "ym.") in the `theory_grounding.citation_reference` field to canonical English formats (like "et al."). We will use Web Search (`search_web`) to verify the exact canonical author list, title, and year for the 9 target matrices to maximize the LLM's latent space recall.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\localization_compiler.py]` (and related files)
- **Delete** `compile_xml_rubrics()` and `compile_chunk_prompt()` methods and their unit tests, as they are obsolete post-EPIC 92.

### Phase 3: Extraction Depth Restoration & Metadata Rewiring

The TDA pipeline (post-EPIC 92) silently drops critical assertion metadata, resulting in the generic prompt problem. We will rewire these fields end-to-end.

#### [MODIFY] `@[c:\src\quorum\backend_v2\models\dtos\dag_models.py]`
- Add missing fields to `ExtractedAtom`: `extraction_rule` (str), `anchor_target` (str), `is_inverse` (bool).
- Ensure `ConfigDict` and `model_validator` support these properly.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]`
- In `TDAEngine.execute()`, map the missing `FlattenedAtom` fields (`extraction_rule`, `anchor_target`, `is_inverse`) into the `ExtractedAtom` constructor at L106-L117.
- Fetch the Matrix `PromptBlock` using `request.matrix_block_id` and `request.prompt_compiler.prompt_block_repo`.
- **God Code Prevention - Context Injection:** Instead of passing 3+ loose arguments down the chain, create a strict `MatrixEvaluationContext` DTO (or dict) to hold `theory_grounding`, `ai_description` (as `matrix_objective`), and `allow_contextual_override`. Inject this context object down to `dag_executor.execute_graph()`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]`
- Update `execute_graph()` signature to accept the new matrix context fields and pass them to `ExtractiveSensorService.evaluate_atom_boolean_batch()`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py]`
- **God Code Prevention - Decomposition:** The file is currently 367 lines long. Adding massive XML string formatting here will push it over the 400-line God Code limit. You MUST extract the prompt construction logic into a dedicated, testable builder (e.g., `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`).
- Update `evaluate_atom_boolean_batch()` to accept the injected matrix context object, and delegate the prompt generation to the new builder.
- The new builder will inject the lost structural XML:
  - `<matrix_directive>` (from `ai_description`)
  - `<theory_grounding>` (Citation and URL)
  - `<FAIL_FAST_MANDATE>` (Including contextual override rules if `allow_contextual_override` is True)
  - `<tda_validation>` per claim (injecting `extraction_rule`, `anchor_target`, `is_inverse`)
- This completely restores the cognitive models and structural precision without violating the Step-Level Protocol Mandate.

### Architectural Constraints (God Code Prevention)
As per `ki_god_code_prevention.md`, the implementation MUST adhere to:
1. **Domain Model Purity (`domain_model_purity_mandate`):** The new fields added to `ExtractedAtom` must not introduce any business logic or hardcoded dictionaries. The model must remain strict (`extra="forbid"`, `frozen=True`).
2. **Context Injection (`protocol_driven_worker_architecture`):** We must not bloat `dag_executor.execute_graph()` or `evaluate_atom_boolean_batch()` with loose `**kwargs` for the new matrix metadata. The matrix context must be bundled into a cohesive injected Context object to maintain clean protocol routing.
3. **Proactive Decomposition (`anti_god_file_dumping`):** `extractive_sensor_service.py` is currently 367 lines. We will not append 100 lines of XML string formatting into it. We will proactively decompose the prompt logic into a new dedicated module, adhering to Tier 3 philosophy.

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="Database Snapshot">
    <action>Execute `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic137.json` to back up the seed vault.</action>
    <constraint invariant="live_database_mutation">All structural data modifications MUST occur purely in the master source file `backend_v2/seed/seed_data.json` first before sync.</constraint>
  </step>

  <step id="2" name="Synthesis Tone, DB Hygiene & RAG English Standardization">
    <action>Update `tone_instruction` for `prf_5d6e7f8091a2b3c4` in seed_data.json via `multi_replace_file_content`.</action>
    <action>Standardize `theory_grounding` citations to canonical English and verify sources using `search_web` for the 9 target matrices.</action>
    <action>Clean up `ai_description` for the 9 matrices in seed_data.json by removing the obsolete RULES and redundant EPISTEMIC ANCHORS (since they are now in theory_grounding) via `multi_replace_file_content`.</action>
  </step>

  <step id="3" name="Dead Code Removal">
    <action>Delete `compile_xml_rubrics()` from localization_compiler.py and prompt_compiler.py.</action>
    <action>Delete `compile_chunk_prompt()` from prompt_compiler_adapter.py.</action>
    <action>Delete corresponding dead tests from `test_prompt_compiler_adapter.py` and `test_localization_compiler.py`.</action>
  </step>

  <step id="4" name="DAG Models Extension">
    <action>Add `extraction_rule`, `anchor_target`, and `is_inverse` to `ExtractedAtom` in `backend_v2/models/dtos/dag_models.py`.</action>
    <action>Ensure tests pass for the DTO modifications.</action>
  </step>

  <step id="5" name="TDA Pipeline Metadata Rewiring (Context Injection)">
    <action>Modify `tda_engine.py` to map the new fields from `FlattenedAtom` to `ExtractedAtom`.</action>
    <action>Define a `MatrixEvaluationContext` object/dict to group the matrix metadata.</action>
    <action>Modify `tda_engine.py` to fetch the matrix block and inject the context object to `enriched_dag_executor.py`.</action>
    <action>Modify `enriched_dag_executor.py` to forward this context object to `extractive_sensor_service.py`.</action>
  </step>

  <step id="6" name="Sensor Prompt Re-Architecture & Proactive Decomposition">
    <action>Create a new file `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`.</action>
    <action>Implement a testable pure function/class in this new file to construct the robust XML prompt utilizing all the newly passed metadata.</action>
    <action>Modify `evaluate_atom_boolean_batch` in `extractive_sensor_service.py` to delegate prompt generation to this new builder, keeping the service file safely under 400 lines.</action>
  </step>

  <step id="7" name="JSON Syntax Validation">
    <action>Run a dry-run read of the JSON file to ensure no syntax errors were introduced: `uv run python backend_v2/seed/run_seed.py local --dry-run`</action>
  </step>

  <step id="8" name="Full Audit Loop">
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to ensure ALL Python schemas, imports, and tests pass after Python modifications.</action>
    <action>Commit the new data to the local DB: `uv run python backend_v2/seed/run_seed.py local`</action>
  </step>
</execution_protocol>
```

## Verification Plan

### Automated Tests
- Run the full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test` — confirms no import errors from removed methods and that `TDAEngine` parameter changes don't break existing tests.

### Manual Verification
- Check the output of `ExtractiveSensorService` in Logfire or `llm_debug_prompts.md` during a Matrix extraction to confirm the `<theory_grounding>` XML is injected.
- Visually confirm the Synthesis LLM produces deep, strategic analysis.
