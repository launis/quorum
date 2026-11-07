<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# EPIC 163 - Phase 4: Strongly Typed DAG Context, Matrix Evaluation & Synthesis DTOs (`QGR027` `JsonValue` Eradication)

## 1. Executive Summary & Architectural Directives

This phase replaces all 32 `dict[str, JsonValue]` and `list[JsonValue]` occurrences across the 19 files in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` with closed Pydantic V2 DTOs and discriminated unions, and deletes `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` from `@[scripts/_ast_guardrails.py]`.

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/dtos/atom_evaluation.py#L151-L174]`, `@[backend_v2/models/dtos/hook_delta.py#HookStateDeltaDTO]`, `@[backend_v2/models/dtos/lightweight_matrix.py#L45-L59]`, `@[backend_v2/models/dtos/lightweight_matrix.py#L126-L189]`, `@[backend_v2/models/dtos/prompt_context.py#PromptCompilationContextDTO]`, `@[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]`, `@[backend_v2/models/dtos/system.py#L56-L75]`, `@[backend_v2/models/dtos/trace.py#StepTraceEventDTO]`, `@[backend_v2/models/state.py#AdapterContext]`, `@[backend_v2/models/state.py#ExecutionContext]` | Declaring open `dict[str, JsonValue]` and `list[JsonValue]` fields on internal DTOs and DAG execution state envelopes (`QGR027`). | Define closed Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` fields and discriminated unions for matrix rows, scale distributions, health component entries, trace outputs, and DAG step outputs. | Zero untyped `JsonValue` bags in `backend_v2/models/dtos/` or `backend_v2/models/state.py`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict` |
| `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`, `@[backend_v2/llm/client.py#L42-L879]`, `@[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline]`, `@[backend_v2/llm/mock_data.py#get_mock_structured_response]`, `@[backend_v2/services/llm_task_executor.py#L106-L525]` | Using `dict[str, JsonValue]` return/parameter annotations in `LLMClient`, `LLMIngressPipeline`, `get_mock_structured_response`, `LLMTaskExecutor`, and `matrix_evaluation_hook` (`QGR027`). | Enforce generic Pydantic `BaseModel` type parameters and typed `LightweightMatrixOutput` / `ScoringResultDTO` models across LLM execution and matrix scoring. | Zero raw JSON dictionary intermediates between `LLMClient` and `LLMTaskExecutor`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/services/llm_task_executor.py backend_v2/hooks/scoring/matrix_hook.py --test --ast-strict` |
| `@[backend_v2/services/orchestrator/context_router.py#L50-L196]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L345-L436]`, `@[backend_v2/services/orchestrator/matrix_reducer.py#L56-L246]`, `@[backend_v2/services/orchestrator/result_projector.py#L31-L272]`, `@[backend_v2/services/orchestrator/strategies/logic.py#L32-L231]`, `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L36-L501]`, `@[scripts/_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]` | Routing `dict[str, JsonValue]` maps across `context_router.py`, `wave_orchestrator_stage.py`, `matrix_reducer.py`, `result_projector.py`, `logic.py`, and `synthesis_payload_compressor.py` (`QGR027`). | Route strongly typed `StepOutputDTO`, `LightweightMatrixOutput`, `LightweightMatrixDTO`, and compressed synthesis payload DTOs across all orchestrator stages, and delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` from `@[scripts/_ast_guardrails.py]`. | Zero `RESIDUAL_*` exemption sets remaining in `@[scripts/_ast_guardrails.py]`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ scripts/_ast_guardrails.py --test --ast-strict` |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that all 19 files in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` are covered in this plan and that all DTO changes preserve Full-Duplex Serialization Parity (`full_duplex_serialization_parity_mandate` and `sdui_contract_fracture_prevention`).</action>
  </step>

  <dod_checklist>
    <item>All 8 DTO and state model files in `backend_v2/models/` replace `dict[str, JsonValue]` and `list[JsonValue]` with closed Pydantic V2 models.</item>
    <item>All 11 LLM, hook, and orchestrator files replace `dict[str, JsonValue]` with typed Pydantic V2 models and generic `BaseModel` parameters.</item>
    <item>`RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` is deleted from `@[scripts/_ast_guardrails.py]`, leaving zero `RESIDUAL_*` sets in `@[scripts/_ast_guardrails.py]`.</item>
  </dod_checklist>

  <anti_targets>
    <file>@[backend_v2/seed/seed_data.json]</file>
    <file>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</file>
  </anti_targets>

  <touched_artifacts>
    <file>@[backend_v2/models/dtos/atom_evaluation.py#L151-L174]</file>
    <file>@[backend_v2/models/dtos/hook_delta.py#HookStateDeltaDTO]</file>
    <file>@[backend_v2/models/dtos/lightweight_matrix.py#L45-L59]</file>
    <file>@[backend_v2/models/dtos/lightweight_matrix.py#L126-L189]</file>
    <file>@[backend_v2/models/dtos/prompt_context.py#PromptCompilationContextDTO]</file>
    <file>@[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]</file>
    <file>@[backend_v2/models/dtos/system.py#L56-L75]</file>
    <file>@[backend_v2/models/dtos/trace.py#StepTraceEventDTO]</file>
    <file>@[backend_v2/models/state.py#AdapterContext]</file>
    <file>@[backend_v2/models/state.py#ExecutionContext]</file>
    <file>@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]</file>
    <file>@[backend_v2/llm/client.py#L42-L879]</file>
    <file>@[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline]</file>
    <file>@[backend_v2/llm/mock_data.py#get_mock_structured_response]</file>
    <file>@[backend_v2/services/llm_task_executor.py#L106-L525]</file>
    <file>@[backend_v2/services/orchestrator/context_router.py#L50-L196]</file>
    <file>@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L345-L436]</file>
    <file>@[backend_v2/services/orchestrator/matrix_reducer.py#L56-L246]</file>
    <file>@[backend_v2/services/orchestrator/result_projector.py#L31-L272]</file>
    <file>@[backend_v2/services/orchestrator/strategies/logic.py#L32-L231]</file>
    <file>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L36-L501]</file>
    <file>@[scripts/_ast_guardrails.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</file>
    <file>@[backend_v2/tests/integration/test_sdui_semantic_parity.py]</file>
  </touched_artifacts>

  <step id="4.1" name="Replace JsonValue Containers in Backend DTOs &amp; State Envelopes">
    <context>
      8 DTO and state files in `backend_v2/models/` use `dict[str, JsonValue]` or `list[JsonValue]` for internal domain and trace state (`QGR027`).
    </context>
    <demolish>
      Remove `JsonValue` imports and `dict[str, JsonValue]` / `list[JsonValue]` field declarations across the 8 target model files.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/models/dtos/atom_evaluation.py#L151-L174]`: Replace open `dict[str, JsonValue]` fields with closed Pydantic V2 DTOs.
      2. `[MODIFY]` `@[backend_v2/models/dtos/hook_delta.py#HookStateDeltaDTO]`: Replace `dict[str, JsonValue]` payload fields with closed typed delta DTOs.
      3. `[MODIFY]` `@[backend_v2/models/dtos/lightweight_matrix.py#L126-L189]` and `@[backend_v2/models/dtos/lightweight_matrix.py#L45-L59]`: Create closed Pydantic V2 models for matrix rows, scale distributions, and diagnostic trace metadata replacing `dict[str, JsonValue]`.
      4. `[MODIFY]` `@[backend_v2/models/dtos/prompt_context.py#PromptCompilationContextDTO]`: Replace `dict[str, JsonValue]` context map with typed prompt context DTO fields.
      5. `[MODIFY]` `@[backend_v2/models/dtos/schema_manifest.py#StepSchemaManifestDTO]`: Replace `dict[str, JsonValue]` schema descriptor fields with typed manifest DTOs.
      6. `[MODIFY]` `@[backend_v2/models/dtos/system.py#L56-L75]`: Create typed health component entries replacing `dict[str, JsonValue]` diagnostic maps on `HealthCheckResponseDTO`.
      7. `[MODIFY]` `@[backend_v2/models/dtos/trace.py#StepTraceEventDTO]`: Replace `dict[str, JsonValue]` trace output fields with typed trace payload DTOs (`exclude_none=True`).
      8. `[MODIFY]` `@[backend_v2/models/state.py#AdapterContext]` and `@[backend_v2/models/state.py#ExecutionContext]`: Replace `dict[str, JsonValue]` step output maps with typed `StepOutputDTO` and discriminated union values.
    </action>
    <constraint>
      All new and updated Pydantic V2 DTOs must enforce `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated[T, Field(...)]` syntax.
    </constraint>
    <test_contracts>
      <contract name="test_lightweight_matrix_and_trace_dtos_enforce_extra_forbid" category="positive">
        <input>Valid typed matrix row, scale distribution, health component, and `TraceEventMetadataDTO` instances.</input>
        <expected>Validate cleanly and serialize with `exclude_none=True` without any `JsonValue` fields.</expected>
      </contract>
      <contract name="test_closed_dtos_reject_unrecognized_extra_keys" category="negative">
        <input>Payload containing an undeclared key on `HealthCheckResponseDTO`, `TraceEventMetadataDTO`, or `StepContextMetadataDTO`.</input>
        <expected>Raises `pydantic.ValidationError` (`extra_forbidden`).</expected>
      </contract>
      <contract name="test_execution_context_step_outputs_boundary_types" category="boundary">
        <input>`ExecutionContext` and `AdapterContext` populated with empty `{}` and multi-step `StepOutputDTO` entries.</input>
        <expected>Preserves O(1) typed lookup and immutability across DAG step transitions.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`
    </validation_gate>
  </step>

  <step id="4.2" name="Migrate LLM Client, Ingress Pipeline, Task Executor &amp; Matrix Hook Away from JsonValue">
    <context>
      `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`, `@[backend_v2/llm/client.py#L42-L879]`, `@[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline]`, `@[backend_v2/llm/mock_data.py#get_mock_structured_response]`, and `@[backend_v2/services/llm_task_executor.py#L106-L525]` annotate structured responses or intermediate payloads as `dict[str, JsonValue]`.
    </context>
    <demolish>
      Remove `dict[str, JsonValue]` annotations in `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`, `@[backend_v2/llm/client.py#L42-L879]`, `@[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline]`, `@[backend_v2/llm/mock_data.py#get_mock_structured_response]`, and `@[backend_v2/services/llm_task_executor.py#L106-L525]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook]`: Consume and return typed `LightweightMatrixOutput` and `ScoringResultDTO` models without `dict[str, JsonValue]`.
      2. `[MODIFY]` `@[backend_v2/llm/client.py#L42-L879]`: Replace `dict[str, JsonValue]` return/parameter annotations on structured execution helpers with generic Pydantic `BaseModel` type parameters.
      3. `[MODIFY]` `@[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline]`: Replace `dict[str, JsonValue]` intermediate payload annotations with typed ingress DTOs.
      4. `[MODIFY]` `@[backend_v2/llm/mock_data.py#get_mock_structured_response]`: Return typed Pydantic DTO fixtures instead of `dict[str, JsonValue]`.
      5. `[MODIFY]` `@[backend_v2/services/llm_task_executor.py#L106-L525]`: Enforce generic `BaseModel` return typing across structured task execution methods.
    </action>
    <constraint>
      Use PEP 695 generic syntax (`def execute_structured_task[T: BaseModel](...)`) and preserve lazy imports of `litellm` and `vertexai` (`eager_llm_dependency_loading`).
    </constraint>
    <test_contracts>
      <contract name="test_llm_task_executor_returns_typed_pydantic_model" category="positive">
        <input>Structured task execution call with a concrete `BaseModel` subclass schema.</input>
        <expected>Returns a validated instance of the target `BaseModel` subclass alongside `TokenUsage`.</expected>
      </contract>
      <contract name="test_matrix_evaluation_hook_rejects_malformed_matrix_payload" category="negative">
        <input>Invalid matrix evaluation input violating `LightweightMatrixOutput` schema constraints.</input>
        <expected>Logs structured error and raises `AppException`.</expected>
      </contract>
      <contract name="test_get_mock_structured_response_handles_minimum_and_maximum_scale_bounds" category="boundary">
        <input>Mock structured response generation for a 2-point (`1..2`) and 10-point (`1..10`) scale matrix.</input>
        <expected>Returns a valid typed DTO fixture respecting `computed_min` and `computed_max`.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/services/llm_task_executor.py backend_v2/hooks/scoring/matrix_hook.py --test --ast-strict`
    </validation_gate>
  </step>

  <step id="4.3" name="Migrate Orchestrator Stages, Compressor, Projector &amp; Reducer and Delete RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES">
    <context>
      6 orchestrator files use `dict[str, JsonValue]` for wave accumulators, context routing, matrix reduction, result projection, logic evaluation, and synthesis payload compression (`QGR027`).
    </context>
    <demolish>
      Delete all `dict[str, JsonValue]` and `list[JsonValue]` annotations in the 6 orchestrator files and delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` from `@[scripts/_ast_guardrails.py]`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/services/orchestrator/context_router.py#L50-L196]`: Route typed `StepOutputDTO` payloads without `dict[str, JsonValue]` maps.
      2. `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py#L345-L436]`: Replace `dict[str, JsonValue]` wave accumulator maps with typed wave execution state DTOs.
      3. `[MODIFY]` `@[backend_v2/services/orchestrator/matrix_reducer.py#L56-L246]`: Return typed `LightweightMatrixOutput` models from matrix reduction methods.
      4. `[MODIFY]` `@[backend_v2/services/orchestrator/result_projector.py#L31-L272]`: Project atom and matrix results into typed `LightweightMatrixDTO` and `StepOutputDTO` models instead of `dict[str, JsonValue]`.
      5. `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py#L32-L231]`: Return typed logic evaluation DTOs instead of `dict[str, JsonValue]`.
      6. `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L36-L501]`: Create typed compressed synthesis payload DTOs in `SynthesisPayloadCompressor` instead of `dict[str, JsonValue]`.
      7. `[MODIFY]` `@[scripts/_ast_guardrails.py]`: Delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`.
      8. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` and `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`: Verify that zero `RESIDUAL_*` exemption sets exist in `@[scripts/_ast_guardrails.py]` and that all 4 ISTQB Equivalence Partitions in `SynthesisPayloadCompressor` and SDUI semantic parity pass 100%.
    </action>
    <constraint>
      Enforce `heterogeneous_payload_testing_mandate` on `SynthesisPayloadCompressor` and `StepOutputDTO` consumers covering structured DTOs, list collections, strings, scalars, and falsy inputs.
    </constraint>
    <test_contracts>
      <contract name="test_synthesis_payload_compressor_typed_dto_across_four_partitions" category="positive">
        <input>1) Structured DTO, 2) List of DTOs, 3) Markdown string, 4) Scalar `int`/`float`/`bool`.</input>
        <expected>Produces deterministic typed compressed synthesis payload DTOs without `dict[str, JsonValue]`.</expected>
      </contract>
      <contract name="test_qgr027_flags_jsonvalue_in_non_boundary_module" category="negative">
        <input>Synthetic AST snippet annotating `payload: dict[str, JsonValue]` in an orchestrator or DTO module outside `BOUNDARY_EXEMPTION_FILES` and `OPEN_JSON_EXEMPTION_FILES`.</input>
        <expected>`QGR027` raises a fatal AST guardrail violation.</expected>
      </contract>
      <contract name="test_ast_guardrails_has_zero_residual_sets" category="boundary">
        <input>Inspect all module-level attributes of `@[scripts/_ast_guardrails.py]`.</input>
        <expected>Zero attributes starting with `RESIDUAL_` exist in `@[scripts/_ast_guardrails.py]`.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/ --test --ast-strict`
    </validation_gate>
  </step>
</execution_protocol>
```
