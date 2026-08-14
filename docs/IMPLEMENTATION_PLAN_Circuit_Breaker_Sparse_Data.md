# IMPLEMENTATION PLAN: Circuit Breaker & Sparse Data Synthesis Rule

**Objective**: Implement a deterministic Circuit Breaker in `SynthesisEngine` to handle "Data Starvation" (0 atoms) and introduce a `sparse_data_rule` in `SynthesisEngine` to mitigate "Attention Dilution" for sparse data (1-2 atoms). This structurally prevents Prompt Leakage (hallucinated internal commands) without violating the Tripartite Pipeline, God Code Prevention mandates, or Zero-Compromise strictness.

## Root Cause Analysis

1. **Decoupled Engine Circuit Breaker (Domain Isolation):** Placing the Circuit Breaker inside `SynthesisEngine.execute()` preserves `DAGExecutor` as a domain-agnostic graph runner.
   *Justification (`ki_god_code_prevention.md` & `ki_execution_engine_protocol.md`):* `DAGExecutor` must never contain domain-specific branching like `if model_strategy == "synthesis"`. In accordance with the Single Responsibility Principle and Anti-God Code rules, `SynthesisEngine` validates its own precondition (`GlobalAtomBlackboard`) and immediately short-circuits with `DataStarvationEvent` if `total_atoms <= starvation_threshold`, bypassing the structured LLM task executor.

2. **DAG Contract Preservation:** When skipped due to starvation, `SynthesisEngine` returns a `TraceEvent` with the executing step's exact identifier (`request.step.id`).
   *Justification:* DAG nodes must fulfill their own contract. Using the node's own ID ensures downstream dependencies and `TopologicalEvaluator` resolve deterministically without topological deadlocks.

3. **Prefix Cache Invalidation (Sparse Data Rule):** Directives injected at the top of system prompts destroy prefix cache.
   *Justification:* Dynamic XML directives (`<sparse_data_rule>`) are appended strictly to the end of the user payload (`local_messages[-1]`), preserving LLM Context Caching (FinOps) and utilizing Recency Bias to prevent Attention Dilution.

4. **Dedicated Prompt Asset File (Anti-God File Dumping):** Prompt rules must not bloat existing service files or generic utilities.
   *Justification (`ki_god_code_prevention.md`):* `build_sparse_data_context()` is placed in a dedicated domain module `backend_v2/models/prompts/synthesis_directives.py` rather than inlined into `synthesis_engine.py` or dumped into generic helpers.

5. **TraceEvent Type Trap in WarningCardAdapter:** The starvation event payload is nested in `event.content`.
   *Justification:* `context.execution.execution_trace` contains `TraceEvent` instances where `event_type` is strictly an event classification (`"output"`). The domain payload `DataStarvationEvent` is serialized into `TraceEvent.content`. The adapter MUST inspect `event.content` when `event.event_type == "output"` and verify `"event_type" in event.content and event.content["event_type"] == "starvation"`, immediately followed by strict validation via `DataStarvationEvent.model_validate(event.content, strict=True)`. Using `.get()` or `isinstance(data, dict)` is strictly forbidden.

6. **SDUI AlertBlock Field Contract:**
   *Justification:* In Quorum's Pydantic SDUI schema (`models/view/sdui.py`), `AlertBlock` strictly defines `severity: Annotated[LaxVisualIntent, Field(default=VisualIntent.INFO)]` (mapped from `VisualIntent.WARNING`), `text: str`, `exact_quotes: list[str]`, and `citations: list[int]`.

7. **Raw Atoms vs. Compressed Matrix Calculation (Scenario C):** If `total_atoms` is counted from `reduced_atoms` (the token-compressed matrix payload), an evaluation where all 10 atoms are `PASSED` will compress to 0 rows (`len(reduced_atoms) == 0`), causing a False Starvation trigger and aborting a perfect score.
   *Justification:* `total_atoms` MUST be computed from the raw uncompressed evaluation data via `len(blackboard.get_all_atom_ids())`, NEVER from `len(reduced_atoms)`.

8. **UI Duplication & I18n Hallucination Prevention in WarningCardAdapter:**
   *Justification:* The adapter MUST halt iteration on the first match (`break`) and use Quorum's standardized `I18nText(default_locale="en", translations={"en": "Evaluation data was insufficient to generate synthesis.", "fi": "Arviointiaineisto ei sisältänyt riittävästi havaintoja synteesin tuottamiseksi."}).resolve(context.locale)` (strictly adhering to Pydantic `extra="forbid"` with `default_locale` and `translations` dict).

## Scope & Target Files

- **[MODIFY]** @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
- **[NEW]** @[backend_v2/models/prompts/synthesis_directives.py]
- **[MODIFY]** @[backend_v2/models/prompts/__init__.py]
- **[MODIFY]** @[backend_v2/models/dtos/trace.py]
- **[MODIFY]** @[backend_v2/models/enums.py]
- **[NEW]** @[backend_v2/services/sdui/adapters/warning_card_adapter.py]
- **[MODIFY]** @[backend_v2/services/sdui/adapters/__init__.py]
- **[MODIFY]** @[backend_v2/services/blueprint.py]
- **[MODIFY]** @[backend_v2/settings.py]
- **[MODIFY]** @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]
- **[NEW]** @[backend_v2/tests/unit/services/sdui/adapters/test_warning_card_adapter.py]

## Knowledge Base Constraints (KIs) Applied

1. **`ki_god_code_prevention.md` (Epic 133)**: Enforces domain isolation and prevents God Code in `DAGExecutor` by moving the Circuit Breaker to `SynthesisEngine`. Enforces `anti_god_file_dumping` by isolating prompt directives in `synthesis_directives.py`.
2. **`ki_synthesis_payload_compression.md` (Epic 141)**: Validates that preventing Data Starvation at the Engine level safely fulfills the strict Fail-Fast mandate.
3. **`ki_dag_engine_dto_projection_rules.md` (Epic 91.5)**: Validates that `DAGExecutor` remains domain-agnostic and that `SynthesisEngine` returns structured DTO envelopes (`EngineExecutionResult`).
4. **`ki_flat_polymorphic_pipeline.md` (Epic 131)**: Validates that injecting an `AlertBlock` via an adapter flawlessly integrates into the Dumb Painter frontend.
5. **`ki_sdui_adapter_pattern.md` (Epic 130)**: Validates the strict two-section canonical structure (`WARNING_CARD_RULES` + `WarningCardAdapter.build(context: AdapterContext)`).
6. **@[ki_dual_axis_localization_architecture.md]**: Validates Axis 2 semantic localization where the backend computes dynamic alert text using `I18nText.resolve(context.locale)` without client-side guessing.

## User Review Required

> [!IMPORTANT]
> - Circuit Breaker execution is strictly contained within `SynthesisEngine.execute()` to preserve `DAGExecutor` domain-agnostic purity.
> - The existing `AlertBlock` with `severity=VisualIntent.WARNING` is reused, matching client-side `@FreezedUnionValue('alert_box')` with 100% parity.
> - Approve the plan below with **"PROCEED"**.

## Implementation Protocol

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="SynthesisEngine Circuit Breaker (Domain Event)">
    <action>Modify `backend_v2/settings.py` to add `synthesis_starvation_threshold: Annotated[int, Field(description="Atom count threshold at or below which synthesis short-circuits with a DataStarvationEvent.")] = 0` and `synthesis_sparse_threshold: Annotated[int, Field(description="Atom count threshold below which sparse data synthesis prompt rules are injected.")] = 3`.</action>
    <action>
      Modify `backend_v2/models/dtos/trace.py` to define a new strict Pydantic model:
      ```python
      class DataStarvationEvent(BaseDTO):
          """Strict domain event emitted when SynthesisEngine aborts due to atom starvation."""
          model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

          event_type: Annotated[Literal["starvation"], Field(default="starvation", description="Event discriminator")] = "starvation"
          total_atoms: Annotated[int, Field(ge=0, description="Total raw atoms extracted before synthesis")]
          reason: Annotated[str, Field(default="Data starvation: insufficient atoms", description="Reason for short-circuit")] = "Data starvation: insufficient atoms"
      ```
    </action>
    <action>Modify `backend_v2/models/enums.py` to ensure `VisualIntent.WARNING` is present.</action>
    <action>Ensure `from backend_v2.settings import get_settings` is imported globally at the top of `backend_v2/services/orchestrator/engines/synthesis_engine.py` (satisfying `global_settings_import`).</action>
    <action>Modify `SynthesisEngine.execute()` in `backend_v2/services/orchestrator/engines/synthesis_engine.py` to calculate `total_atoms = len(all_atom_ids)` from the validated `GlobalAtomBlackboard` via `blackboard.get_all_atom_ids()`.</action>
    <action>Read the starvation threshold via `get_settings().synthesis_starvation_threshold`.</action>
    <action>If `total_atoms <= starvation_threshold`:
      1) Log a circuit breaker warning: `logger.warning("SynthesisEngine: Circuit breaker triggered due to data starvation (total_atoms=%d). Bypassing LLM execution.", total_atoms)`.
      2) Instantiate `starvation_dto = DataStarvationEvent(total_atoms=total_atoms)`.
      3) Serialize `starvation_content = starvation_dto.model_dump(mode="json")`.
      4) Create `starvation_event = TraceEvent(step_name=request.step.id, event_type="output", content=starvation_content)`.
      5) Return `EngineExecutionResult(results=[], hydrated_references={}, synthesis_output=starvation_content, trace_events=[starvation_event])` immediately without calling `self._executor.execute_structured_task()`. Setting `synthesis_output=starvation_content` ensures `LLMNodeStrategy` forwards the exact starvation payload into the execution trace `TraceEvent.content` for downstream SDUI adapters.
    </action>
    <constraint invariant="anti_god_code_dag_isolation">
      `DAGExecutor` MUST remain completely domain-agnostic. No synthesis-specific starvation checks or short-circuits are placed in `dag_executor.py`. `SynthesisEngine` handles its own precondition and returns a valid `EngineExecutionResult`.
    </constraint>
    <constraint invariant="raw_atoms_uncompressed_calculation">
      `total_atoms` MUST be calculated strictly from raw `blackboard.get_all_atom_ids()`, NEVER from `len(reduced_atoms)` or `available_dtos` to prevent False Starvation on perfect scores and dimension mismatch.
    </constraint>
    <constraint invariant="adapter_strict_fail_fast_routing">
      The Engine MUST remain blind to visual layout decisions. It ONLY extracts raw data into pure Domain DTOs (specifically `DataStarvationEvent`). It MUST NOT emit UI blocks directly.
    </constraint>
    <constraint invariant="structured_state_envelopes_mandate">
      The synthetic TraceEvent MUST be a valid, strict Pydantic model (`ConfigDict(strict=True, extra='forbid')`). No naked dictionaries are allowed in the state stream.
    </constraint>
  </step>

  <step id="2" name="Synthesis Directives (Sparse Data Rule)">
    <action>Create a new dedicated file `backend_v2/models/prompts/synthesis_directives.py` conforming to `anti_god_file_dumping`.</action>
    <action>
      Implement `build_sparse_data_context(total_atoms: int) -> str` which formats and returns the following `<sparse_data_rule>` XML block dynamically:
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
    <action>Export `build_sparse_data_context` in `backend_v2/models/prompts/__init__.py`.</action>
    <constraint invariant="anti_god_file_dumping">
      Creating a dedicated `synthesis_directives.py` prevents dumping prompt logic into generic helper files or bloating `synthesis_engine.py`.
    </constraint>
    <constraint invariant="split_cognitive_translation">
      The Sparse Data Rule must instruct the LLM to write brief native English reasoning but output localized final text in the target language.
    </constraint>
  </step>

  <step id="3" name="Sparse Data Rule Injection">
    <action>In `synthesis_engine.py` `execute()`, read `starvation_threshold = get_settings().synthesis_starvation_threshold` and `sparse_threshold = get_settings().synthesis_sparse_threshold`.</action>
    <action>If `total_atoms > starvation_threshold` AND `total_atoms < sparse_threshold`, trigger the Sparse Data Rule.</action>
    <action>Call `build_sparse_data_context(total_atoms)` and append the resulting XML directive directly to the end of the user message (AFTER `<user_payload>` / `<raw_xai_extensions>`) to preserve Prefix Caching and leverage Recency Bias.</action>
    <constraint invariant="ephemeral_caching_topology">
      Dynamic prompt directives MUST be injected exclusively into the `user` message at the absolute end, keeping the static system prefix untouched for 100% caching efficiency.
    </constraint>
  </step>

  <step id="4" name="SDUI Warning Card Adapter Implementation">
    <action>Create a NEW file `backend_v2/services/sdui/adapters/warning_card_adapter.py` following the EXACT two-section canonical template.</action>
    <action>In Section 1: Define `WARNING_CARD_RULES: dict[str, dict[str, VisualIntent]] = {"starvation": {"severity": VisualIntent.WARNING}}` and define the SSOT localization constant `I18N_WARNING_STARVATION = I18nText(default_locale="en", translations={"en": "Evaluation data was insufficient to generate synthesis.", "fi": "Arviointiaineisto ei sisältänyt riittävästi havaintoja synteesin tuottamiseksi."})`.</action>
    <action>In Section 2: Implement `WarningCardAdapter.build(context: AdapterContext) -> list[AnySduiBlock]`. Scan `context.execution.execution_trace` for `TraceEvent` objects where `event.event_type == "output"` and `"event_type" in event.content and event.content["event_type"] == "starvation"`. Validate using `DataStarvationEvent.model_validate(event.content, strict=True)`. Catch `ValidationError` with `logger.error("[WarningCardAdapter] Corrupted starvation payload", exc_info=True)` and raise `AppException` (Fail-Fast). If valid, retrieve `severity = WARNING_CARD_RULES[starvation_event.event_type]["severity"]` with Fail-Fast direct key access, resolve localized text via `warning_msg = I18N_WARNING_STARVATION.resolve(context.locale)`, append `AlertBlock(severity=severity, text=warning_msg, exact_quotes=[], citations=[])`, and execute `break` immediately to halt iteration on the first match (preventing duplicate cards in the UI). If no starvation event exists, return `[]`.</action>
    <action>Export `WarningCardAdapter` in `backend_v2/services/sdui/adapters/__init__.py`.</action>
    <action>
      Modify `blueprint.py` `transform()`:
      1) Import `WarningCardAdapter`.
      2) In Phase 2 assembly (around line 686), before iterating `dispatch_order`:
         ```python
         warning_blocks = WarningCardAdapter.build(adapter_context)
         if warning_blocks:
             has_warning = True
             inner_sdui_blocks.extend(warning_blocks)
         ```
      3) Retain the standard target block dispatch loop. If starvation occurred, `warning_blocks` populates `inner_sdui_blocks`, gracefully preventing the `if not inner_sdui_blocks: inner_sdui_blocks = [SduiRadarChartBlock(axes=evaluative_matrices)]` fallback from creating empty placeholder radar charts.
    </action>
    <action>Do NOT register the adapter in `_target_block_hydrators` and do NOT modify `seed_data.json` to include `"warning_card_block"`. The warning card is an orchestrator-level event projection, not a static blueprint component.</action>
    <constraint invariant="adapter_two_section_structure">
      The adapter MUST have exactly two sections: a module-level dictionary for aesthetics (and static I18nText assets), and a single class with a `@staticmethod build(context)` method. No inline visual logic is allowed.
    </constraint>
    <constraint invariant="adapter_fail_fast_dictionary_access">
      Aesthetic rule lookups MUST use strict direct key access: `WARNING_CARD_RULES[key]`. Using `.get()` is strictly forbidden.
    </constraint>
    <constraint invariant="strict_sdui_polymorphic_serialization">
      The returned block MUST be a valid `AnySduiBlock` (specifically `AlertBlock`) with a strict `block_type="alert_box"` discriminator and `severity` field.
    </constraint>
    <constraint invariant="single_card_deduplication">
      The adapter MUST halt iteration on the first matched starvation event (`break`) to ensure at most one AlertBlock is generated.
    </constraint>
    <constraint invariant="semantic_localization_axis">
      The dynamic warning text MUST be resolved through the SSOT `I18nText.resolve(context.locale)` method (Axis 2 semantic localization) without client-side guessing or ad-hoc translation functions.
    </constraint>
  </step>
</execution_protocol>
```

## Verification Plan

### Automated Tests
1. **Synthesis Engine Unit Test (Circuit Breaker & Sparse Data):**
   - File: `backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py`
   - Update `base_request` fixture or provide sample atoms (`>= 3`) for `test_synthesis_engine_happy_path`.
   - Add `test_synthesis_engine_data_starvation_circuit_breaker`: Verifies that with 0 atoms (`atoms_by_input = {}`), the circuit breaker fires, returns `DataStarvationEvent` content in `synthesis_output` and `trace_events`, and bypasses `execute_structured_task`.
   - Add `test_synthesis_engine_sparse_data_rule_injected`: Verifies that with 1-2 atoms, `<sparse_data_rule>` XML block is injected at the end of the user message, and `execute_structured_task` is executed.
   - Command: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/synthesis_engine.py --test`
2. **SDUI Warning Card Adapter Test:**
   - File: `backend_v2/tests/unit/services/sdui/adapters/test_warning_card_adapter.py`
   - Test: `test_warning_card_adapter_starvation_success` (creates execution trace with `DataStarvationEvent`, verifies returned `AlertBlock` has `severity=VisualIntent.WARNING` and localized text).
   - Test: `test_warning_card_adapter_no_starvation` (execution trace with normal output, verifies returns `[]`).
   - Test: `test_warning_card_adapter_deduplication` (multiple starvation events in trace, verifies only one `AlertBlock` returned).
   - Test: `test_warning_card_adapter_corrupted_payload_fail_fast` (trace event with `"event_type": "starvation"` but invalid schema, verifies `AppException` is raised).
   - Command: `uv run pytest backend_v2/tests/unit/services/sdui/adapters/test_warning_card_adapter.py`
3. **Integration Pipeline Test:**
   - Command: `uv run pytest backend_v2/tests/unit/test_dag_taskgroup.py`

### Anti-Happy-Path Scenarios
- **Scenario A (Data Starvation / 0 Atoms):** Submit an evaluation with empty blackboard atoms (`total_atoms == 0`).
  - *Expected Output:* `SynthesisEngine` triggers Circuit Breaker. LLM execution is bypassed. `TraceEvent` with `DataStarvationEvent` is returned. UI renders Warning Card (`AlertBlock`).
- **Scenario B (Sparse Data / 1 Atom):** Submit an evaluation matching exactly 1 atom.
  - *Expected Output:* `SynthesisEngine` executes. `sparse_data_rule` is injected into the prompt end. LLM outputs concise response without hallucinated commands.
- **Scenario C (Perfect Score Compression):** Submit an evaluation with 10 atoms, all `PASSED` (green).
  - *Expected Output:* `MatrixReducer` compresses `reduced_atoms` to 0, but `total_atoms` is correctly calculated as 10 from raw blackboard atoms. Circuit Breaker does NOT fire. `SynthesisEngine` runs normally.
- **Scenario D (Schema Mismatch / Corrupted Trace Content):** Provide a `TraceEvent` with malformed starvation payload.
  - *Expected Output:* The adapter catches the validation error / KeyError, logs structured error, and raises `AppException` (Fail-Fast).

### Final E2E REST API Verification Gate
(Windows/PowerShell)
```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```
