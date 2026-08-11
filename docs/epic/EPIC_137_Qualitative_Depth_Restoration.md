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

### Out of Scope
- **ResultProjector Eradication:** Complete removal of `ResultProjector` to comply with the CQRS/SDUI projection rules (`ki_dag_engine_dto_projection_rules.md`) is OUT OF SCOPE to prevent a "Big Bang" refactoring. This is handled separately in `EPIC_138_TDA_Engine_DTO_Projection_Refactor.md`. For this Epic, we accept the technical debt and merely route the new extraction fields through the existing `ResultProjector`.

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
The matrices in `seed_data.json` already contain structured `theory_grounding` fields (specifically: `citation_reference`, `source_url`). Instead of relying on the messy `ai_description` (which violates the Step-Level Protocol Mandate by mixing Domain Knowledge with Extraction Rules), we will formally pipe the `theory_grounding` structured data into the `ExtractiveSensorService`.

## Proposed Changes

### Phase 1: Synthesis Quality Fix

#### [MODIFY] `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
> [!IMPORTANT]
> **Data Integrity Override:** Because LLMs are inherently lossy and `seed_data.json` is a massive structural file, modifying hundreds of lines via string replacement (`multi_replace_file_content`) presents an unacceptable risk of syntax corruption.
> You MUST create a single-use Python script (`scripts/epic137_seed_mutator.py`) that uses the standard library `json` module to load the data, update the dictionary values safely, and write it back out.

- **Output Profile Tone:** The Holistic Audit profile ID is `prf_5d6e7f8091a2b3c4`. Upgrade its `tone_instruction` to include explicit persona instructions:
  - EN: "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data."
  - FI: "Toimi ylemmän johdon valmentajana (Senior Executive Coach). Tarjoa syvällistä, provosoivaa ja strategista analyysiä pelkän datan luettelemisen sijaan."

### Phase 2: Dead Code, Database Hygiene & English RAG Standardization

#### [MODIFY] `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- **Matrix `ai_description` Cleanup:** Remove the `\nRULES:\n- Bounty Hunter Paradigm...` suffix from the `ai_description` of the following 9 matrices (deterministically verified via Python audit — these are the ONLY matrices with `RULES:` blocks):
  1. `matrix_toulmin` (L336, id=`blk_440a5fef9331451b`)
  2. `matrix_bloom` (L920, id=`blk_f921c7c0989b47e8`)
  3. `matrix_kahneman` (L1438, id=`blk_109dab5b6b3f403a`)
  4. `matrix_goodhart` (L1713, id=`blk_53f32679aa514fcb`)
  5. `matrix_archivist` (L2210, id=`blk_fb15f8dcf23f4865`)
  6. `matrix_causal_analyst` (L2677, id=`blk_c5804a9143c34cb1`)
  7. `matrix_falsifier` (L3172, id=`blk_b476f89fb732448c`)
  8. `matrix_judge` (L3589, id=`blk_ff72c2d79edb4ebf`)
  9. `matrix_xai_reporter` (L4151, id=`blk_6b8c766185294f7e`)
- The remaining 4 matrices (`matrix_taskguard`, `matrix_causal_abductive`, `matrix_taskxai_clarity`, `matrix_epistemic_humility`) do NOT have `RULES:` blocks and require NO cleanup.
- Since we are now using `theory_grounding` for the epistemic anchors, the `ai_description` can be drastically simplified or cleared of redundant rules to maintain architectural hygiene.
- **English APA RAG Standardization:** Translate and format ALL 13 matrices' `theory_grounding.citation_reference` fields into strict English APA format (`Author(s) (Year). Title. Publisher.`). Currently, several citations are incomplete or use Finnish abbreviations (e.g., `(toim.)`, `ym.`).
- Use Web Search (`search_web`) to verify the exact canonical author list, title, year, and publisher for ALL 13 matrices to maximize the LLM's latent space recall.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\localization_compiler.py]` (and related files)
- **Delete** `compile_xml_rubrics()` and `compile_chunk_prompt()` methods and their unit tests, as they are obsolete post-EPIC 92.

### Phase 3: Extraction Depth Restoration & Metadata Rewiring

The TDA pipeline (post-EPIC 92) silently drops critical assertion metadata, resulting in the generic prompt problem. We will rewire these fields end-to-end.

#### [MODIFY] `@[c:\src\quorum\backend_v2\models\dtos\dag_models.py]`
- Add missing fields to `ExtractedAtom`: `extraction_rule` (str | None), `anchor_target` (str | None), `is_inverse` (bool | None). These MUST be optional to prevent backward compatibility crashes with other engines. (Note: These fields already exist in `FlattenedAtom`, only `ExtractedAtom` needs them).
- Ensure `ConfigDict` and `model_validator` support these properly.
- **CQRS Decision:** These fields are purely forensic AI routing metadata. They MUST NOT be mapped to `AtomResultDTO` or sent to the Flutter Frontend to preserve the "Dumb Painter" boundary.

#### [MODIFY] `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`
- **God Code Prevention - Context Injection:** Define a strictly typed Pydantic V2 `MatrixEvaluationContext` DTO (`ConfigDict(strict=True, extra="forbid", frozen=True)`) to hold `theory_grounding`, `matrix_objective` (from `ai_description`), and `allow_contextual_override`.
- Add `matrix_context: MatrixEvaluationContext | None = None` to `EngineExecutionRequest`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]`
- **Macro-Orchestrator Responsibility:** The `PromptCompiler` is a stateless pure function orchestrator and does NOT hold database repositories. Attempting to fetch the `PromptBlock` inside `TDAEngine` via `request.prompt_compiler.prompt_block_repo` will cause a fatal `AttributeError`.
- Instead, in `LLMNodeStrategy`, fetch the Matrix `PromptBlock` using its existing `prompt_block_repo` and the `matrix_block_id`. Construct the `MatrixEvaluationContext` DTO here and inject it safely into the `EngineExecutionRequest` before calling the engine.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]`
- In `TDAEngine.execute()`, map the missing `FlattenedAtom` fields (`extraction_rule`, `anchor_target`, `is_inverse`) into the `ExtractedAtom` constructor at L106-L117.
- Pass the injected `request.matrix_context` down to `dag_executor.execute_graph()`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]`
- Update `execute_graph()` signature to accept the new matrix context parameter as `matrix_context: MatrixEvaluationContext | None = None` (Liskov Substitution / Blast Radius prevention) and pass it to `ExtractiveSensorService.evaluate_atom_boolean_batch()`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py]`
- **God Code Prevention - Decomposition:** The file is currently 367 lines long. Adding massive XML string formatting here will push it over the 400-line God Code limit. You MUST extract the prompt construction logic into a dedicated, testable builder located precisely at `@[c:\src\quorum\backend_v2\services\orchestrator\prompts\matrix_sensor_prompt_builder.py]`.
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
<anti_targets>
  - Do NOT modify the raw extraction prompt in ExtractiveSensorService with hardcoded XML strings.
  - Do NOT use generic kwargs to pass matrix metadata into dag_executor.
  - Do NOT map the new forensic metadata fields to the Flutter UI DTOs.
</anti_targets>

<dod_checklist>
  - [ ] Matrix output profile tone updated.
  - [ ] Theory grounding citations in seed_data updated to APA format.
  - [ ] Obsolete ai_descriptions cleared of RULES blocks.
  - [ ] Dead prompt compiler methods deleted.
  - [ ] ExtractedAtom updated with new forensic fields.
  - [ ] MatrixEvaluationContext DTO created and added to EngineExecutionRequest.
  - [ ] LLMNodeStrategy updated to inject MatrixEvaluationContext.
  - [ ] MatrixSensorPromptBuilder created and integrated.
  - [ ] All async mocks updated and negative tests passed.
  - [ ] Backend audit loop and seed generation script passed.
</dod_checklist>

<validation_gate>
  - Ensure backend_audit_loop.py passes flawlessly.
  - Ensure run_seed.py validates all seed changes without errors.
  - Ensure ExtractiveSensorService tests pass with missing theory_grounding.
</validation_gate>

<execution_protocol level="0_create_plan_validated">
  
  <!-- ========================================================= -->
  <!-- SESSION 1: SEED HYGIENE                                   -->
  <!-- ========================================================= -->
  <step id="1.1" name="Database Snapshot (Platform Agnostic)">
    <action>Execute Python script to safely backup data: `uv run python -c "import shutil, os; os.makedirs('backend_v2/seed/backups', exist_ok=True); shutil.copy('backend_v2/seed/seed_data.json', 'backend_v2/seed/backups/seed_data_pre_epic137.json')"`</action>
    <constraint invariant="live_database_mutation">All structural data modifications MUST occur purely in the master source file `@[backend_v2/seed/seed_data.json]` first before sync.</constraint>
  </step>

  <step id="1.2" name="Synthesis Tone & RAG English Standardization (Bounded)">
    <action>Target `@[c:\src\quorum\backend_v2\seed\seed_data.json]`. Create a single-use Python script `scripts/epic137_seed_mutator.py` to safely parse and update the JSON structure without using string replacements.</action>
    <action>In the script, update the `tone_instruction` for the output profile `prf_5d6e7f8091a2b3c4` to the Senior Executive Coach persona.</action>
    <action>In the script, standardize `theory_grounding.citation_reference` for ALL 13 matrices into strict English APA format (Author (Year). Title. Publisher.). Many are currently missing titles or years (specifically: `Kahneman, Daniel 2011.`) or using Finnish abbreviations (specifically: `matrix_bloom`, `matrix_goodhart`). Use the LLM's internal knowledge base to generate the canonical APA citations directly in the Python script to avoid web search timeouts.</action>
    <action>In the script, clean up `ai_description` by stripping obsolete `RULES:` blocks for ALL 9 matrices with RULES: blocks (deterministically verified): `matrix_toulmin`, `matrix_bloom`, `matrix_kahneman`, `matrix_goodhart`, `matrix_archivist`, `matrix_causal_analyst`, `matrix_falsifier`, `matrix_judge`, `matrix_xai_reporter`.</action>
    <action>Execute the script to apply mutations: `uv run python scripts/epic137_seed_mutator.py`.</action>
  </step>

  <step id="1.3" name="SESSION 1 HANDOVER">
    <action>STOP execution. Ensure JSON syntax is valid: `uv run python backend_v2/seed/run_seed.py local --dry-run`.</action>
    <action>Instruct the user to execute `/tier5-session-handover` to flush the context window before starting Session 2.</action>
    <constraint invariant="context_amnesia_prevention">Do NOT proceed to Dead Code Purge in the same session, as modifying 6 files violates the max-5 file limit.</constraint>
  </step>

  <!-- ========================================================= -->
  <!-- SESSION 2: DEAD CODE PURGE                                -->
  <!-- ========================================================= -->
  <step id="2.1" name="Dead Code Eradication">
    <action>Delete `compile_xml_rubrics()` from `@[backend_v2/services/orchestrator/localization_compiler.py]` (L80) and `@[backend_v2/services/orchestrator/prompt_compiler.py]` (L67-L80). **USER PERMISSION GRANTED to modify prompt_compiler.py** (dead code verified: zero production callers outside its own definition and the dead `compile_chunk_prompt` method).</action>
    <action>Delete `compile_chunk_prompt()` from `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]`.</action>
    <action>Delete corresponding dead tests from `@[tests/backend_v2/services/orchestrator/test_prompt_compiler_adapter.py]` and `@[tests/backend_v2/services/orchestrator/test_localization_compiler.py]`.</action>
  </step>

  <step id="2.2" name="SESSION 2 HANDOVER">
    <action>STOP execution. Instruct the user to execute `/tier5-session-handover` before starting Session 3.</action>
  </step>

  <!-- ========================================================= -->
  <!-- SESSION 3: DTO STRICTNESS & ENGINE METADATA WIRING        -->
  <!-- ========================================================= -->
  <step id="3.1" name="Backend DAG Models Extension">
    <action>Target `@[c:\src\quorum\backend_v2\models\dtos\dag_models.py#L46-L91]`. Add `extraction_rule: Annotated[str | None, Field(default=None, description="The specific validation rule.")] = None`, `anchor_target: Annotated[str | None, Field(default=None, description="Semantic bounding box target.")] = None`, and `is_inverse: Annotated[bool | None, Field(default=False, description="True if this is an inverse assertion.")] = False` to `ExtractedAtom`. (Verified: these fields exist in `FlattenedAtom` at engine.py L34-L36 but are completely absent from `ExtractedAtom`).</action>
    <action>Target `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`. Define a strict `MatrixEvaluationContext` Pydantic V2 DTO with `ConfigDict(strict=True, extra='forbid', frozen=True)` to hold `theory_grounding`, `matrix_objective`, and `allow_contextual_override`. CRITICAL: This class MUST be defined structurally BEFORE `EngineExecutionRequest` to prevent Pydantic NameError/Forward Reference crashes.</action>
    <action>Target `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`. Add `matrix_context: MatrixEvaluationContext | None = None` to `EngineExecutionRequest`.</action>
    <constraint invariant="cqrs_forensic_separation">Do NOT map these fields to `AtomResultDTO` or regenerate Frontend code. They are purely forensic backend metadata.</constraint>
  </step>

  <step id="3.2" name="SESSION 3 HANDOVER">
    <action>STOP execution. Summarize actions taken. Instruct the user to execute `/tier5-session-handover` before starting the complex Engine Rewiring in Session 4.</action>
  </step>

  <!-- ========================================================= -->
  <!-- SESSION 4: TDA PIPELINE WIRING & PROMPT BLOCK ASSEMBLY    -->
  <!-- ========================================================= -->
  <step id="4.1" name="TDA Pipeline Metadata Rewiring">
    <action>Modify `@[backend_v2/services/orchestrator/strategies/llm.py]` to inject the `MatrixEvaluationContext` into the `EngineExecutionRequest` before triggering the `TDAEngine`.</action>
    <action>Modify `@[backend_v2/services/orchestrator/engines/tda_engine.py]` to pass the `request.matrix_context`.</action>
    <action>Safely update `execute_graph()` in `@[backend_v2/services/orchestrator/enriched_dag_executor.py]` to accept `matrix_context: MatrixEvaluationContext | None = None` (Python 3.14 modern syntax) and forward it.</action>
  </step>

  <step id="4.2" name="Sensor Prompt Re-Architecture (Anti-God Code)">
    <action>Create a new pure builder class in `@[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]`.</action>
    <constraint invariant="llm_kv_caching_maximization">You MUST use `PromptBlock` assembly for the prompt structure. Raw XML `f-string` concatenation is strictly forbidden. Place dynamic variables (`<tda_validation>`) at the ABSOLUTE END of the prompt payload to preserve LLM Prefix Caching.</constraint>
    <action>Modify `evaluate_atom_boolean_batch` in `@[backend_v2/services/orchestrator\extractive_sensor_service.py]` to delegate generation to this new builder.</action>
    <action>Modify `batch_evaluation_callback` in `@[backend_v2/services/orchestrator/enriched_dag_executor.py]` to also use this new builder for cache pre-warming, ensuring prompt prefix parity and resolving the duplicate prompt anti-pattern.</action>
  </step>

  <step id="4.3" name="Negative Testing & Mocks">
    <action>Update ALL existing `AsyncMock` implementations for `ExtractiveSensorService` across the test suite to support the new signature.</action>
    <action>Write explicit negative tests in `@[tests/backend_v2/services/orchestrator/test_extractive_sensor_service.py]`: 1) Evaluate handling when `theory_grounding` is missing/null. 2) Evaluate strict bypass when `allow_contextual_override` is strictly set to `False`.</action>
  </step>

  <step id="4.4" name="Final System Audit & Commit">
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to mathematically prove all Python schemas, imports, and tests pass.</action>
    <action>If successful, commit seed data: `uv run python backend_v2/seed/run_seed.py local`</action>
  </step>

</execution_protocol>
```

## Verification Plan

### Automated Tests
- Run the full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test` — confirms no import errors from removed methods and that `TDAEngine` parameter changes don't break existing tests.
- Verify negative test coverage (anti_happy_path_mandate): Ensure tests validate behavior when `theory_grounding` is empty/malformed and when `allow_contextual_override` is strictly blocked.

### Manual Verification
- Check the output of `ExtractiveSensorService` in Logfire or `llm_debug_prompts.md` during a Matrix extraction to confirm the `<theory_grounding>` XML is injected.
- Visually confirm the Synthesis LLM produces deep, strategic analysis.
