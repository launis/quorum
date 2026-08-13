# IMPLEMENTATION PLAN: Circuit Breaker & Sparse Data Synthesis Rule

**Objective**: Implement a deterministic Circuit Breaker in `DAGExecutor` to handle "Data Starvation" (0 atoms) and introduce a `sparse_data_rule` in `SynthesisEngine` to mitigate "Attention Dilution" for sparse data (1-2 atoms). This structurally prevents Prompt Leakage (hallucinated internal commands) without violating the Tripartite Pipeline or Zero-Compromise strictness.

## Root Cause Analysis

1. **DAG Contract Violation (Circuit Breaker):** In a previous iteration, the skipped execution (Circuit Breaker) returned a `TraceEvent` object with the wrong name (`VirtualSystemStepID.DATA_STARVATION.value`). 
   *Justification:* DAG nodes must fulfill their own contract. If node A returns data named B, the dependencies waiting for node A in the DAG network will remain in an eternal lock (`TopologicalEvaluator`). The plan is corrected to use the executed node's own ID (`step_def.step_id`).

2. **Prefix Cache Invalidation (Sparse Data Rule):** A previous phase used string concatenation to set a dynamic rule at the beginning of the prompt (e.g. `f"{sparse_directive}\n...<user_payload>"`).
   *Justification:* This violates the "Dynamic variables at absolute end" rule. When the beginning of the prompt changes, the LLM's Prefix Cache is destroyed for the entire massive `user_payload` section. The plan is mutated so that the directive is added to the absolute end of the prompt chain. This also prevents the "Attention Dilution" phenomenon by leveraging Recency Bias.

3. **Orchestrator Concurrency Bottleneck:** The plan previously ambiguously advised running the `await _safe_commit()` function inside the asynchronous `_update_lock`.
   *Justification:* Database transactions (I/O) inside an asynchronous lock halt the concurrency of the entire `TaskGroup` engine. State mutations (e.g. dictionary updates) must be done inside the lock to secure memory, but I/O operations (commit) must absolutely be executed outside the lock. The plan's protocol is clarified to forbid I/O inside the lock.

4. **AttributeError & Dead Code in BlueprintTransformer:** A previous phase attempted to read the `dto.block_id` field from tracked events (TraceEvent) where no such field exists. Registering the adapter in the dictionary was also unnecessary.
   *Justification:* `TraceEvent` and `DataStarvationEvent` do not contain a `block_id` field. If they are run through the standard `_target_block_hydrators` loop in `blueprint.py`, it results in an `AttributeError`. The plan is corrected so that `DataStarvationEvent` is identified in a type-safe manner (e.g. `getattr(dto, "event_type", None) == "starvation"`) and the adapter rendering is called manually. Dead code regarding adapter registration and the `seed_data.json` dependency is removed.

5. **NameError & Pydantic ValidationError in SDUI:** The plan used `AlertBlock(severity=...)` and a potentially undefined `WarningType` enum.
   *Justification:* Quorum's Pydantic SDUI standards (e.g. `AlertBlock`) strictly use the `intent` parameter (not `severity`). Additionally, a missing enum will immediately crash the Python application due to the `extra='forbid'` rule. The plan's protocol is updated to use the Pydantic model's `intent` parameter and ensure the existence of the enum.

## Scope & Target Files

- **[MODIFY]** @[c:\src\quorum\backend_v2\services\orchestrator\dag_executor.py#L559-L752]
- **[MODIFY]** @[c:\src\quorum\backend_v2\services\orchestrator\engines\synthesis_engine.py#L35-L161]
- **[NEW]** @[c:\src\quorum\backend_v2\models\prompts\synthesis_directives.py]
- **[MODIFY]** @[c:\src\quorum\backend_v2\models\dtos\trace.py]
- **[MODIFY]** @[c:\src\quorum\backend_v2\models\enums.py]
- **[NEW]** @[c:\src\quorum\backend_v2\services\sdui\adapters\warning_card_adapter.py]
- **[MODIFY]** @[c:\src\quorum\backend_v2\services\blueprint.py]
- **[MODIFY]** @[c:\src\quorum\backend_v2\settings.py]
- **[MODIFY]** @[c:\src\quorum\backend_v2\seed\seed_data.json]

## Knowledge Base Constraints (KIs) Applied

The following core KIs have been structurally validated to support this plan:
1. **`ki_synthesis_payload_compression.md` (Epic 141)**: Validates that preventing Data Starvation at the Orchestrator level safely fulfills the strict Fail-Fast mandate (stopping empty `evaluations` from reaching the LLM).
2. **`ki_dag_engine_dto_projection_rules.md` (Epic 91.5)**: Validates that placing the Circuit Breaker inside `dag_executor.py` correctly adheres to the Macro-Orchestration boundary (Step-to-Step).
3. **`ki_flat_polymorphic_pipeline.md` (Epic 131)**: Validates that injecting an `AlertBlock` via an adapter flawlessly integrates into the Dumb Painter frontend without requiring nested layout changes.

## User Review Required

> [!IMPORTANT]
> - Are you satisfied with using the existing `AlertBlock` instead of inventing a new `SduiWarningCard`? The `AlertBlock` is already part of the `AnySduiBlock` union and perfectly suits this need via the strict Adapter Pattern.
> - The XML execution protocol below defines the exact step-by-step logic. Approve with **"PROCEED"**.

## Implementation Protocol

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="DAGExecutor Circuit Breaker (Domain Event)">
    <action>Modify `backend_v2/settings.py` to add `synthesis_starvation_threshold: int = 0` and `synthesis_sparse_threshold: int = 3`.</action>
    <action>Modify `backend_v2/models/dtos/trace.py` to define a new strict Pydantic model `class DataStarvationEvent(BaseDTO):` with `event_type: Literal["starvation"] = "starvation"` and `total_atoms: int`.</action>
    <action>Modify `backend_v2/models/enums.py` to add `WARNING_CARD_BLOCK = "warning_card_block"` to `TargetBlockType` AND define any missing Enums (specifically `WarningType` and `VisualIntent`) required for the Warning Card.</action>
    <action>Modify `run_step_wrapper` in `dag_executor.py` to calculate `total_atoms`.</action>
    <action>Read the starvation threshold via `get_settings().synthesis_starvation_threshold`.</action>
    <action>If `total_atoms <= starvation_threshold`, instantiate `DataStarvationEvent` and append it as a `TraceEvent` with `step_id=step_def.step_id` (Crucial: MUST use the node's own ID to satisfy the DAG contract and prevent topological deadlocks) and `event_type="output"` (serialized via `model_dump()`), update the step status to `PASSED`, and execute `continue` to bypass the `SynthesisEngine`.</action>
    <constraint invariant="adapter_strict_fail_fast_routing">
      The Orchestrator MUST remain blind to visual layout decisions. It ONLY extracts raw data into pure Domain DTOs (specifically `DataStarvationEvent`). It MUST NOT emit UI blocks directly.
    </constraint>
    <constraint invariant="tripartite_phase_isolation">
      Ensure the synthetic TraceEvent uses a strict Event-Driven Data Envelope (Pydantic DTO shape) compatible with `ReportDataDTO` / `SduiMapperService`. No unstructured dicts.
    </constraint>
    <constraint invariant="structured_state_envelopes_mandate">
      The synthetic TraceEvent MUST be a valid, strict Pydantic model (`ConfigDict(strict=True, extra='forbid')`). No naked dictionaries are allowed in the state stream.
    </constraint>
    <constraint invariant="remedial_strangler_fig_proxy">
      Ensure modifications to the highly central `DAGExecutor` do not break downstream context variables. Memory state mutations MUST be strictly locked under `_update_lock`, but I/O operations (specifically `await _safe_commit()`) MUST be executed OUTSIDE the lock to prevent concurrency starvation of the `TaskGroup`.
    </constraint>
  </step>

  <step id="2" name="Synthesis Directives (Sparse Data Rule)">
    <action>Create a new file `backend_v2/models/prompts/synthesis_directives.py`.</action>
    <action>
      Implement `build_sparse_data_context(total_atoms: int) -> str` which returns the following `<sparse_data_rule>` XML block ONLY if `total_atoms > 0` and `total_atoms < 3`:
      ```xml
      <sparse_data_rule>
        <context>This execution contains extremely sparse data ({total_atoms} atoms). To prevent Attention Dilution and Prompt Leakage, strict constraints apply.</context>
        <instruction>
          1. You MUST be extremely concise and brief.
          2. You MUST leave sections completely empty if there is no direct supporting data.
          3. Do NOT invent narrative filler, do NOT guess, and do NOT write generic fluff.
          4. If a matrix or section has no relevant data, output an empty array or empty string according to the schema.
        </instruction>
      </sparse_data_rule>
      ```
    </action>
    <constraint invariant="anti_god_file_dumping">
      Creating a dedicated `synthesis_directives.py` prevents dumping this logic into generic files, specifically `global_mandates.py`, or bloating the `synthesis_engine.py`.
    </constraint>
    <constraint invariant="split_cognitive_translation">
      The Sparse Data Rule must instruct the LLM to write brief native English reasoning but output localized final text in the target language (no hallucinated JSON schemas).
    </constraint>
  </step>

  <step id="3" name="Sparse Data Rule Injection">
    <action>Modify `_build_dynamic_prompt` in `synthesis_engine.py` to calculate `total_atoms`.</action>
    <action>Read `sparse_threshold = get_settings().synthesis_sparse_threshold`.</action>
    <action>If `total_atoms > starvation_threshold` AND `total_atoms < sparse_threshold`, it triggers the Sparse Data Rule.</action>
    <action>Call `build_sparse_data_context(total_atoms)` and dynamically inject the resulting XML directive directly into the user message at the absolute end (AFTER `<user_payload>`) to preserve Prefix Caching and leverage Recency Bias.</action>
  </step>

  <step id="4" name="SDUI Adapter Pattern implementation">
    <action>Create a NEW file `backend_v2/services/sdui/adapters/warning_card_adapter.py` following the EXACT two-section canonical template.</action>
    <action>In Section 1: Define `WARNING_CARD_RULES = {"starvation": {"intent": VisualIntent.WARNING, "icon_name": "alert_triangle"}}`.</action>
    <action>In Section 2: Implement `WarningCardAdapter.build(context: AdapterContext) -> list[AnySduiBlock]`. The adapter MUST directly scan `context.execution.execution_trace` to detect if a `DataStarvationEvent` occurred by checking `getattr(dto, "event_type", None) == "starvation"` type-safely. It returns an `AlertBlock` containing the translated warning text ONLY if starvation is found, otherwise it returns `[]`.</action>
    <action>Modify `blueprint.py` to MANUALLY call `WarningCardAdapter.build(context)` and prepend/append its output to the final `inner_sdui_blocks` array.</action>
    <action>Remove dead code: Do NOT register the adapter in `_target_block_hydrators` and do NOT modify `seed_data.json` to include `"warning_card_block"`. The warning card is an orchestrator-level override, not a standard blueprint component.</action>
    <constraint invariant="adapter_two_section_structure">
      The adapter MUST have exactly two sections: a module-level dictionary for aesthetics, and a single class with a `@staticmethod build(context)` method. No inline visual logic is allowed.
    </constraint>
    <constraint invariant="adapter_fail_fast_dictionary_access">
      Aesthetic rule lookups MUST use strict direct key access: `WARNING_CARD_RULES[key]`. Using `.get()` is strictly forbidden.
    </constraint>
    <constraint invariant="strict_sdui_polymorphic_serialization">
      The returned block MUST be a valid `AnySduiBlock` (specifically `AlertBlock`) with a strict `block_type` discriminator.
    </constraint>
    <constraint invariant="ki_flat_polymorphic_pipeline">
      The returned `AlertBlock` will be flattened directly into the `inner_sdui_blocks` array by `blueprint.py` for the Dumb Painter frontend.
    </constraint>
    <constraint invariant="semantic_localization_axis">
      The translated string (specifically "Not enough data" or equivalent `l10n_key`) MUST be resolved via Enum `l10n_key` mapping. The Frontend must NEVER run translation algorithms.
    </constraint>
    <constraint invariant="cross_language_enum_parity">
      If a new Enum is introduced, it MUST have exact parity in `client_app_v2/lib/core/models/enums.dart` with a strict `@JsonEnum()`.
    </constraint>
  </step>
</execution_protocol>
```

## Verification Plan

### Automated Tests
1. **DAGExecutor Audit:**
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test`
2. **Synthesis Engine Audit:**
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test`
3. **AST Guardrail Audit (If needed):**
   `uv run python scripts/audit_markdown_boundaries.py --file c:\src\quorum\docs\IMPLEMENTATION_PLAN_Circuit_Breaker_Sparse_Data.md`

### Anti-Happy-Path Scenarios
- **Scenario A (Data Starvation / 0 Atoms):** Submit an evaluation with completely empty data.
  - *Expected Output:* `DAGExecutor` triggers Circuit Breaker. `SynthesisEngine` is skipped. UI renders "Not enough data" Warning Card.
- **Scenario B (Sparse Data / 1 Atom):** Submit an evaluation matching exactly 1 atom.
  - *Expected Output:* `SynthesisEngine` executes. `sparse_data_rule` is injected into the prompt. LLM outputs a highly truncated JSON without hallucinating instructions.
- **Scenario C (Perfect Score Compression):** Submit an evaluation with 10 atoms, all `PASSED` (green).
  - *Expected Output:* `MatrixReducer` compresses them to 0. `total_atoms` is still 10. Circuit Breaker does NOT fire. `SynthesisEngine` runs normally.
- **Scenario D (Schema Mismatch / Enum Missing):** Provide a `DataStarvationEvent` that requests a missing enum or aesthetic key.
  - *Expected Output:* The adapter catches the `KeyError`, logs it with `exc_info=True`, and throws an explicit `AppException` (Fail-Fast).

### Final E2E REST API Verification Gate
(Windows/PowerShell)
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```
(Unix/Bash)
```bash
RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```
