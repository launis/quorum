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

## 2. Architectural Impact & Compliance Matrix

### 1. Deprecations & Sunset List
- `compile_xml_rubrics()` in `localization_compiler.py` and `prompt_compiler.py`
- `compile_chunk_prompt()` in `prompt_compiler_adapter.py`
- `RULES:` blocks from `ai_description` for 9 matrices
- Legacy non-APA citations in `theory_grounding`

### 2. Retained SSOT Invariants
- Domain Model Purity (`ExtractedAtom` remains a pure data carrier)
- Context Injection Protocol (Matrix metadata injected via `MatrixEvaluationContext`)
- LLM Prefix Caching Topography (Strict separation of static/dynamic prompt segments)
- Single Source of Truth for database data (no string replacements, must use json mutation)

### 3. Compliance Gates
- `backend_audit_loop.py backend_v2 --test`
- `run_seed.py local` for JSON syntax validation
- Negative test coverage for missing `theory_grounding` and blocked overrides

## Proposed Changes

### Phase 1: Synthesis Quality Fix

#### [MODIFY] `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
> [!IMPORTANT]
> **Seed Vault Protocol Compliance:** Per `03_seed_vault.md` rule `inline_terminal_scripting`, writing disposable Python scripts to modify JSON data is STRICTLY PROHIBITED. All structural data modifications MUST use the native MCP `multi_replace_file_content` tool with bounded line ranges. A deterministic Python VERIFICATION script (`uv run python -c "import json; json.load(open('backend_v2/seed/seed_data.json'))"`) is required after each mutation to validate JSON syntax integrity.

- **Output Profile Tone:** The Holistic Audit profile ID is `prf_5d6e7f8091a2b3c4`. Upgrade its `tone_instruction` to include explicit persona instructions:
  - EN: "Act as a Senior Executive Coach. Provide deep, provocative, and strategic analysis rather than merely listing data."
  - FI: "Toimi ylemmän johdon valmentajana (Senior Executive Coach). Tarjoa syvällistä, provosoivaa ja strategista analyysiä pelkän datan luettelemisen sijaan."
- **Tripartite Architecture Decision:** We explicitly use the `OutputProfile`'s `tone_instruction` instead of the Step's `execution_persona_block_id` to enforce the Phase 1 vs Phase 2 decoupling. The Execution Phase (Phase 1) MUST remain strictly objective to accurately evaluate matrix metrics without hallucinating or biasing the data. The Senior Executive Coach persona is purely a Phase 2 (Synthesis) presentation layer instruction.

### Phase 2: Dead Code, Database Hygiene & English RAG Standardization

#### [MODIFY] `@[c:\src\quorum\backend_v2\seed\seed_data.json]`
- **Matrix `ai_description` Cleanup:** Remove the `\nRULES:\n- Bounty Hunter Paradigm...` suffix from the `ai_description` of ALL matrices that contain `RULES:` blocks. Use bounded `multi_replace_file_content` operations per-matrix-block.
- **Matrix Identification Mandate:** The implementing agent MUST identify matrices exclusively by first running a Python audit script to list all prompt_blocks with `"category_id": "matrix"` (extracting their opaque IDs and line numbers), then using those exact line numbers for bounded MCP edits. The agent MUST NEVER use slugs to find or filter matrices.
- Since we are now using `theory_grounding` for the epistemic anchors, the `ai_description` can be drastically simplified or cleared of redundant rules to maintain architectural hygiene.
- **English APA RAG Standardization:** Translate and format ALL 13 matrices' `theory_grounding.citation_reference` fields into strict English APA format (`Author(s) (Year). Title. Publisher.`). Currently, several citations are incomplete or use Finnish abbreviations (specifically: `(toim.)`, `ym.`). Use bounded `multi_replace_file_content` per citation, verified against exact line numbers from a Python audit script.
- **Anti-Hallucination Mandate:** The AI MUST use Web Search (`search_web`) during the implementation phase to verify the exact canonical author list, title, year, and publisher for ALL 13 matrices. The verified APA strings MUST be applied via individual bounded `multi_replace_file_content` calls targeting exact line ranges. The agent MUST NOT create disposable Python scripts for mutation (per `03_seed_vault.md` `inline_terminal_scripting` ban).

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\localization_compiler.py]` (and related files)
- **Delete** `compile_xml_rubrics()` and `compile_chunk_prompt()` methods and their unit tests, as they are obsolete post-EPIC 92.

### Phase 3: Extraction Depth Restoration & Metadata Rewiring

The TDA pipeline (post-EPIC 92) silently drops critical assertion metadata, resulting in the generic prompt problem. We will rewire these fields end-to-end.

#### [REJECTED] Modifying `ExtractedAtom` (Domain Purity Decision)
- **Domain-Driven Design (DDD):** We explicitly REJECT modifying `ExtractedAtom` (`dag_models.py`) to hold `extraction_rule`, `anchor_target`, and `is_inverse`. `ExtractedAtom` is a pure data carrier for extracted claims. Adding execution instructions to it violates the Single Responsibility Principle and the Liskov Substitution Principle (since generic Atomizer nodes don't have these rules).
- Rules MUST be separated from data and injected via a strongly typed Context.
- **BARS Matrix Flattening Elegance:** In Quorum, BARS matrices have nested scales (1-5) containing individual claims. The orchestrator flattens this complex nested structure into a single 1D array of `FlattenedAtom`s before passing them to the DAG. By tying `extraction_rule` to the globally unique `atom_id` inside MatrixClaimRuleDTO, we allow the LLM to evaluate each atom independently without knowing anything about the BARS scales. The nested math is safely deferred to the `ResultProjector` post-execution.

#### [MODIFY] `@[c:\src\quorum\backend_v2\models\dtos\engine.py]`
- **Schema Convergence Mandate Compliance:** Do NOT create TheoryGroundingDTO — the existing `TheoryGrounding` model at `@[c:\src\quorum\backend_v2\models\v2_core.py#L187-L200]` already provides `source_url` and `citation_reference` with `ConfigDict(strict=True, extra="forbid")`. Reuse it directly.
- **Schema Convergence Mandate Compliance:** Do NOT create MatrixClaimRuleDTO — the existing `FlattenedAtom` model at `@[c:\src\quorum\backend_v2\models\dtos\engine.py#L21-L38]` already provides `atom_id`, `extraction_rule`, `anchor_target`, and `is_inverse` with `ConfigDict(strict=True, frozen=True, extra="forbid")`. Reuse it directly.
- **God Code Prevention - Context Injection:** Define a strictly typed Pydantic V2 `MatrixEvaluationContext` DTO (`ConfigDict(strict=True, extra="forbid", frozen=True)`) to hold `theory_grounding: TheoryGrounding | None` (reusing existing `TheoryGrounding` from `v2_core.py`), `matrix_objective: str | None` (from `ai_description`), and `allow_contextual_override: bool`. Per-claim rules are NOT needed here because they already flow through `FlattenedAtom` via `EngineExecutionRequest.shuffled_atoms`.
- Add `matrix_context: MatrixEvaluationContext | None = None` to `EngineExecutionRequest`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]`
- **Macro-Orchestrator Responsibility (Anti-Hallucination):** The `PromptCompiler` is a stateless pure function orchestrator and does NOT hold database repositories. Attempting to fetch the `PromptBlock` inside `TDAEngine` via `request.prompt_compiler.prompt_block_repo` will cause a fatal `AttributeError`.
- **Dependency Injection Path:** Do NOT hallucinate nested component registries. `LLMNodeStrategy` inherits from `NodeStrategy` (`base.py`), which natively assigns `self.prompt_block_repo = prompt_block_repo` in its constructor. You MUST use this exact, deterministically verified path: `await self.prompt_block_repo.get_by_id(step.matrix_block_id)`.
- Construct the `MatrixEvaluationContext` DTO here and inject it safely into the `EngineExecutionRequest` before calling the engine.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]`
- Do NOT map matrix rules into `ExtractedAtom` (per the Domain Purity Decision). Leave `ExtractedAtom` construction completely clean.
- Pass the natively injected `request.matrix_context` down to `dag_executor.execute_graph()`.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]`
- **Context Injection Passthrough:** Update `execute_graph()` signature to accept the new matrix context parameter as `matrix_context: MatrixEvaluationContext | None = None` and pass it directly to `ExtractiveSensorService.evaluate_atom_boolean_batch()`.
- **Liskov Substitution / Blast Radius:** By making this parameter optional (`= None`), the DAG executor acts as a pure passthrough. Existing engines (specifically: `AtomizerEngine`) that do not know about matrices can continue calling `execute_graph` without modification, completely eliminating the blast radius for open extractions.

#### [MODIFY] `@[c:\src\quorum\backend_v2\services\orchestrator\extractive_sensor_service.py]`
- **God Code Prevention - Decomposition:** The file is currently 367 lines long. Adding massive XML string formatting here will push it over the 400-line God Code limit. You MUST extract the prompt construction logic into a dedicated, testable [NEW] builder located precisely at `@[c:\src\quorum\backend_v2\services\orchestrator\prompts\matrix_sensor_prompt_builder.py]`.
- **LLM Prefix Caching Topography:** To ensure 100% cache hits on the expensive matrix descriptions, the builder MUST expose two separate methods (or return a tuple):
  1. `build_static_system_prompt()`: Returns the 100% static `SystemMessage` string containing `<matrix_directive>`, `<theory_grounding>`, and `<FAIL_FAST_MANDATE>`.
  2. `build_dynamic_user_payload()`: Returns the dynamic `<tda_validation>` payload per claim (injecting `extraction_rule`, `anchor_target`, `is_inverse`), which `ExtractiveSensorService` will wrap into a `UserMessage`.
- Update `evaluate_atom_boolean_batch()` to accept the injected matrix context object, delegate prompt generation to the new builder, and correctly construct the separated System and User messages for the `LLMClient`.
- This completely restores the cognitive models and structural precision while maximizing FinOps efficiency through flawless Prefix Caching.

### Architectural Constraints (God Code Prevention)
As per `ki_god_code_prevention.md`, the implementation MUST adhere to:
1. **Domain Model Purity (`domain_model_purity_mandate`):** We must NOT add fields to `ExtractedAtom`. Per-claim metadata already flows through `FlattenedAtom` (which carries `extraction_rule`, `anchor_target`, `is_inverse`). Matrix-level context (theory grounding, objective, override flag) is injected via `MatrixEvaluationContext`.
2. **Context Injection (`protocol_driven_worker_architecture`):** We must not bloat `dag_executor.execute_graph()` or `evaluate_atom_boolean_batch()` with loose `**kwargs` for the new matrix metadata. The matrix context must be bundled into a cohesive injected Context object to maintain clean protocol routing.
3. **Proactive Decomposition (`anti_god_file_dumping`):** `extractive_sensor_service.py` is currently 368 lines. We will not append 100 lines of XML string formatting into it. We will proactively decompose the prompt logic into a new dedicated module, adhering to Tier 3 philosophy.
4. **Schema Convergence (`schema_convergence_mandate`):** We must NOT create TheoryGroundingDTO or MatrixClaimRuleDTO as they duplicate existing models (`TheoryGrounding` at `v2_core.py:187` and `FlattenedAtom` at `engine.py:21`). One Concept = One Schema.

```xml
<anti_targets>
  - Do NOT modify the raw extraction prompt in ExtractiveSensorService with hardcoded XML strings.
  - Do NOT use generic kwargs to pass matrix metadata into dag_executor.
  - Do NOT map the new forensic metadata fields to the Flutter UI DTOs.
  - Do NOT inject dynamic claim variables into the System Prompt Builder (destroys Prefix Caching).
</anti_targets>

<dod_checklist>
  - [ ] Matrix output profile tone updated.
  - [ ] Theory grounding citations in seed_data updated to exact APA format via manual search verification and hardcoded dictionary.
  - [ ] Obsolete ai_descriptions cleared of RULES blocks via safe string splitting.
  - [ ] Dead prompt compiler methods deleted.
  - [ ] MatrixEvaluationContext DTO created strictly, reusing existing TheoryGrounding from v2_core.py and existing FlattenedAtom from engine.py. No new duplicate schemas created.
  - [ ] LLMNodeStrategy updated with safe DI to inject MatrixEvaluationContext.
  - [ ] MatrixSensorPromptBuilder created for STATIC system prompts only.
  - [ ] ExtractiveSensorService updated to inject DYNAMIC rules into User Prompts.
  - [ ] All async mocks updated and negative tests passed.
  - [ ] Backend audit loop and seed generation script passed.
</dod_checklist>

<validation_gate>
  - Ensure backend_audit_loop.py passes flawlessly.
  - Ensure run_seed.py validates all seed changes without errors.
  - Ensure ExtractiveSensorService tests pass with missing theory_grounding.
</validation_gate>

```

## Task Breakdown & Context Quarantine Strategy
To prevent Context Amnesia and token saturation, this Epic follows a strict Context Quarantine strategy. The implementation is divided into logical phases, each limited to 1-3 files. At the end of each phase, the agent will execute the `/tier5-session-handover` command to flush the context window. The next phase will then begin in a fresh session using the `/tier5-resume` command. This ensures the agent maintains absolute focus and structural fidelity during execution.

```xml
<execution_block level="0_create_plan_validated">
  
  <step id="1" name="Phase 1: Database Snapshot &amp; Seed Hygiene">
    <action>Execute PowerShell commands to safely backup data: `New-Item -ItemType Directory -Force -Path backend_v2/seed/backups; Copy-Item backend_v2/seed/seed_data.json -Destination backend_v2/seed/backups/seed_data_pre_epic137.json`</action>
    <constraint invariant="live_database_mutation">All structural data modifications MUST occur purely in the master source file before sync.</constraint>
    <constraint invariant="inline_terminal_scripting">Per `03_seed_vault.md`, disposable Python mutation scripts are STRICTLY PROHIBITED. ALL seed mutations MUST use the native MCP `multi_replace_file_content` tool with bounded line ranges. Python scripts are ONLY allowed for READ/VERIFY operations (identifying line numbers, validating JSON syntax).</constraint>
    <action>Run a Python audit script to identify all matrix opaque IDs and their line numbers: `uv run python -c "import json; data=json.load(open('backend_v2/seed/seed_data.json')); blocks=[b for b in data.get('prompt_blocks',[]) if b.get('category_id')=='matrix']; [print(b['id'], b.get('slug','')) for b in blocks]"`. Use these IDs for bounded MCP edits.</action>
    <action>Using bounded `multi_replace_file_content`, update the `tone_instruction` for the output profile `prf_5d6e7f8091a2b3c4` to the Senior Executive Coach persona.</action>
    <action>Using `search_web` to verify canonical citations for ALL 13 matrices, then apply individual bounded `multi_replace_file_content` edits to standardize `theory_grounding.citation_reference` fields into strict English APA format (Author (Year). Title. Publisher.).</action>
    <action>Using bounded `multi_replace_file_content`, clean up `ai_description` by stripping obsolete `RULES:` blocks for ALL matrices that contain them.</action>
    <action>Verify JSON syntax after each batch of mutations: `uv run python -c "import json; json.load(open('backend_v2/seed/seed_data.json')); print('JSON OK')"`. If JSON is broken, immediately restore backup and STOP.</action>
    <action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 2.</action>
    <constraint invariant="context_amnesia_prevention">Do NOT proceed to Dead Code Purge in the same session, as modifying 6 files violates the max-5 file limit.</constraint>
  </step>

  <step id="2" name="Phase 2: Dead Code Eradication (Code + Tests Atomically)">
    <action>Start session via `/tier5-resume`.</action>
    <constraint invariant="atomic_data_test_migration">Dead code methods and their corresponding tests MUST be deleted in the SAME phase to prevent a broken test suite between phases. Splitting them across phases violates the Atomic Data &amp; Test Migration mandate.</constraint>
    <action>Delete `compile_xml_rubrics()` from `backend_v2/services/orchestrator/localization_compiler.py` and `backend_v2/services/orchestrator/prompt_compiler.py`. **USER PERMISSION GRANTED to modify prompt_compiler.py** (dead code verified: zero production callers outside its own definition and the dead `compile_chunk_prompt` method).</action>
    <action>Delete `compile_chunk_prompt()` from `backend_v2/services/orchestrator/prompt_compiler_adapter.py`.</action>
    <action>Delete corresponding dead tests from `backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py` and `backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py` and `backend_v2/tests/unit/services/orchestrator/strategies/test_prompt_compiler_schema_strictness.py` and `backend_v2/tests/integration/test_prompt_compiler.py`.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to confirm no import errors from removed methods.</action>
    <action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 3.</action>
  </step>

  <step id="3" name="Phase 3: DTO Strictness &amp; Engine Metadata Wiring">
    <action>Start session via `/tier5-resume`.</action>
    <constraint invariant="schema_convergence_mandate">Do NOT create TheoryGroundingDTO — reuse the existing `TheoryGrounding` model from `@[c:\src\quorum\backend_v2\models\v2_core.py#L187-L200]`. Do NOT create MatrixClaimRuleDTO — per-claim metadata already flows through the existing `FlattenedAtom` model from `@[c:\src\quorum\backend_v2\models\dtos\engine.py#L21-L38]`. One Concept = One Schema.</constraint>
    <action>Define a strict `MatrixEvaluationContext` Pydantic V2 DTO with `ConfigDict(strict=True, extra='forbid', frozen=True)` to hold `theory_grounding: TheoryGrounding | None` (reusing existing model from `v2_core.py`), `matrix_objective: str | None`, and `allow_contextual_override: bool`. CRITICAL: This class MUST be defined structurally BEFORE `EngineExecutionRequest`.</action>
    <action>Add `matrix_context: MatrixEvaluationContext | None = None` to `EngineExecutionRequest`.</action>
    <constraint invariant="domain_model_purity_mandate">Do NOT modify `ExtractedAtom` in `dag_models.py`. It must remain a pure data carrier. Rules MUST be passed strictly via Context Injection.</constraint>
    <action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 4.</action>
  </step>

  <step id="4" name="Phase 4: TDA Pipeline Rewiring">
    <action>Start session via `/tier5-resume`.</action>
    <action>Modify `backend_v2/services/orchestrator/strategies/llm.py` to inject the `MatrixEvaluationContext` into the `EngineExecutionRequest` before triggering the `TDAEngine`. Also fix the `getattr(b, "category_id", None)` on line 607 to use direct attribute access `b.category_id` (violates `the_zero_compromise_pledge` ban on `getattr(obj, key, default)`).</action>
    <action>Modify `backend_v2/services/orchestrator/engines/tda_engine.py` to pass the `request.matrix_context`.</action>
    <action>Safely update `execute_graph()` in `backend_v2/services/orchestrator/enriched_dag_executor.py` to accept `matrix_context: MatrixEvaluationContext | None = None` (Python 3.14 modern syntax) and forward it.</action>
    <action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 5.</action>
  </step>

  <step id="5" name="Phase 5: Sensor Prompt Re-Architecture">
    <action>Start session via `/tier5-resume`.</action>
    <action>Create a new pure builder class in `backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py`. This directory already contains `atom_extraction.py` and `graph_linking.py`, confirming it is the correct location for prompt builder logic.</action>
    <constraint invariant="llm_kv_caching_maximization">You MUST use `PromptBlock` assembly for the prompt structure. Raw XML `f-string` concatenation is strictly forbidden. The builder MUST expose two separate methods: `build_static_system_prompt()` (for 100% cacheable instructions) and `build_dynamic_user_payload()` (for the `<tda_validation>` per-claim data). Dynamic variables inside the System Message are strictly forbidden.</constraint>
    <action>The builder receives `MatrixEvaluationContext` (for theory_grounding, objective, override flag) and the `FlattenedAtom` list (for per-claim extraction_rule, anchor_target, is_inverse). It maps the FlattenedAtom's `atom_id` to the corresponding `LinkedAtomGraph` node for injection.</action>
    <action>Modify `evaluate_atom_boolean_batch` in `backend_v2/services/orchestrator/extractive_sensor_service.py` to delegate generation to this new builder, constructing separated System and User messages.</action>
    <action>Modify `batch_evaluation_callback` in `backend_v2/services/orchestrator/enriched_dag_executor.py` to also use this new builder for cache pre-warming, ensuring prompt prefix parity and resolving the duplicate prompt anti-pattern (currently duplicated at `extractive_sensor_service.py:308-312` and `enriched_dag_executor.py:138-142`).</action>
    <action>Execute `/tier5-session-handover` to flush context window and prepare for Phase 6.</action>
  </step>

  <step id="6" name="Phase 6: Negative Testing &amp; Mocks &amp; Final Audit">
    <action>Start session via `/tier5-resume`.</action>
    <action>Update ALL existing `AsyncMock` implementations for `ExtractiveSensorService` across the test suite to support the new signature.</action>
    <action>Write explicit negative tests in `backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py`: 1) Evaluate handling when `theory_grounding` is missing/null. 2) Evaluate strict bypass when `allow_contextual_override` is strictly set to `False`.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to mathematically prove all Python schemas, imports, and tests pass.</action>
    <action>If successful, commit seed data: `uv run python backend_v2/seed/run_seed.py local`</action>
  </step>

</execution_block>
```

## Target Files by Phase

### Phase 1: Database Snapshot & Seed Hygiene
#### [MODIFY] @[backend_v2/seed/seed_data.json]

### Phase 2: Dead Code Eradication (Code + Tests Atomically)
#### [MODIFY] @[backend_v2/services/orchestrator/localization_compiler.py]
#### [MODIFY] @[backend_v2/services/orchestrator/prompt_compiler.py]
#### [MODIFY] @[backend_v2/services/orchestrator/prompt_compiler_adapter.py]
#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py]
#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_localization_compiler.py]
#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_prompt_compiler_schema_strictness.py]
#### [DELETE] @[backend_v2/tests/integration/test_prompt_compiler.py]

### Phase 3: DTO Strictness & Engine Metadata Wiring
#### [MODIFY] @[backend_v2/models/dtos/engine.py]

### Phase 4: TDA Pipeline Rewiring
#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]
#### [MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py]
#### [MODIFY] @[backend_v2/services/orchestrator/enriched_dag_executor.py]

### Phase 5: Sensor Prompt Re-Architecture
#### [NEW] @[backend_v2/services/orchestrator/prompts/matrix_sensor_prompt_builder.py]
#### [MODIFY] @[backend_v2/services/orchestrator/extractive_sensor_service.py]
#### [MODIFY] @[backend_v2/services/orchestrator/enriched_dag_executor.py]

### Phase 6: Negative Testing & Mocks & Final Audit
#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_extractive_sensor_service.py]

## Verification Plan

### Automated Tests
- Run the full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test` — confirms no import errors from removed methods and that `TDAEngine` parameter changes don't break existing tests.
- Verify negative test coverage (anti_happy_path_mandate): Ensure tests validate behavior when `theory_grounding` is empty/malformed and when `allow_contextual_override` is strictly blocked.

### Manual Verification
- Check the output of `ExtractiveSensorService` in Logfire or `llm_debug_prompts.md` during a Matrix extraction to confirm the `<theory_grounding>` XML is injected.
- Visually confirm the Synthesis LLM produces deep, strategic analysis.

## 5. Required Knowledge Items (KI Registry)
<required_knowledge_items>
- @[c:\src\quorum\.agents\rules\00-antigravity-core.md]
- @[c:\src\quorum\.agents\rules\01-python-backend.md]
- @[c:\src\quorum\.agents\rules\03_seed_vault.md]
- @[c:\src\quorum\.agents\rules\04_directory_reference.md]
- @[c:\src\quorum\.agents\rules\05_llm_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\agent_context_quarantine\artifacts\ki_agent_context_quarantine.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\llm_extraction_architecture\artifacts\ki_llm_extraction_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\execution_engine_protocol\artifacts\ki_execution_engine_protocol.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\domain_model_prompt_separation\artifacts\ki_domain_model_prompt_separation.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\context_enriched_pipeline\artifacts\ki_context_enriched_decompose_verify.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\de_generator_execution_paradigm\artifacts\ki_de_generator_execution_paradigm.md]
</required_knowledge_items>
