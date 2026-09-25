<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Pipeline State Transit Type Safety & Validation Hardening

## Problem Overview & Physical Codebase Verification
Deep Tier 0 research confirms the current physical status across the DAG execution pipeline and state transit boundaries. Crucially, several prerequisite contracts have **already been implemented**, while key leak sites and technical debt items remain:

### Already Implemented (Verified SSOT)
1. **`StepOutputDTO` and `StepPayloadValue`** in @[backend_v2/models/dtos/step_output.py#L55-L69]: Closed union `StepPayloadValue` and strict frozen DTO `StepOutputDTO` are already defined and active.
2. **`ContextVariablesDTO`** in @[backend_v2/models/dtos/context_variables.py#L38-L191]: Configured with `ConfigDict(strict=True, extra="forbid", frozen=True)`. Uses typed `variables: dict[str, ContextVariableValue]` and implements mapping protocol (`__getitem__`, `__contains__`).
3. **`ExecutionInputsDTO`** in @[backend_v2/models/dtos/hook_state.py#L36-L63]: Strictly typed container with `raw_inputs` and `dynamic_inputs`.
4. **`LightweightMatrixOutput`** in @[backend_v2/models/dtos/lightweight_matrix.py#L76-L128]: Authoritative typed matrix output DTO.

### Remaining Leak Sites & Discovered Technical Debt (To Fix)
1. **`TraceEvent.content` and `metadata` Naked Dictionaries**: In @[backend_v2/models/state.py#L157-L207], both fields remain annotated as `dict[str, Any]`, causing 2 FATAL AST violations under `scripts/audit_dict_eradication.py`.
2. **`StateProjector._snapshot` & Duct-Tape Fallback**:
   - In @[backend_v2/models/state.py#L480-L612], `_snapshot: dict[str, Any]` causes 1 AST violation. Directly typing as `dict[str, dict[str, StepPayloadValue]]` triggers a fatal AST Primitive Obsession violation under `_find_nested_dict_subscript`. It must be typed as `dict[str, StepOutputContentDTO]` using the authoritative SSOT DTO.
   - In @[backend_v2/models/state.py#L551-L589], `StateProjector._build_dto_list()` catches `ValidationError` and invokes `StepOutputDTO.model_construct(...)`, silently swallowing malformed data and bypassing type contracts.
3. **Dynamic Reflection & Negative String Filter in `state.py`**: In @[backend_v2/models/state.py] at module-level namespace binding lines 240-299, `_state_localns` uses `.__dict__` reflection (`_inputs_mod.__dict__`, `_step_output_mod.__dict__`) and negative filtering (`not k.startswith("__")`), triggering 2 FATAL AST reflection violations (`QGR001`).
4. **`ContextRouter.route_and_prune` Permissive Signature**: In @[backend_v2/services/orchestrator/context_router.py#L52-L127], accepts `trace_event: Any` and maintains 38 lines of duck-typing (`isinstance(trace_event, Mapping)`), `evaluated_atoms` key checking, and generic exception wrapping.
5. **`DAGExecutor` State Transit Intermediate Dumps & Duck-Typing**:
   - In @[backend_v2/services/orchestrator/dag_executor.py#L185-L350], `NodeExecutor.execute()` has fallback branches checking `isinstance(global_context_vars, Mapping)` and `isinstance(metadata.global_context_vars, Mapping)`.
   - In @[backend_v2/services/orchestrator/dag_executor.py#L438-L1295], dumps `exec_record.raw_inputs.model_dump(mode="json")` into `TraceEvent(content=inputs_dict)`.
   - In @[backend_v2/services/orchestrator/dag_executor.py#L438-L1295], executes cascading dictionary unpackings for pre-hydration hook deltas.
   - In @[backend_v2/services/orchestrator/dag_executor.py#L727-L1028], dumps `lightweight_matrix.model_dump()` into `TraceEvent(content=...)`.
   - In @[backend_v2/services/orchestrator/dag_executor.py#L727-L1028], checks `"generated_schema" in evt.metadata` (dict membership) instead of typed property access.
   - In @[backend_v2/services/orchestrator/dag_executor.py#L1059-L1090], `_emit_preflight_progress` passes raw untyped dict `content={"message": message, "progress_pct": pct}`.
6. **`synthesis_payload_compressor.py` Naked Dicts & Dead Code**: In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384], 3 naked `dict[str, Any]` annotations trigger 3 FATAL AST violations, and line 384 contains unreachable dead code.
7. **Failing Unit Tests in `test_state.py`**: In @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384], running test suite triggers 2 failures (`test_workflow_state_accessors_and_properties` and `test_workflow_state_none_branches`) because tests pass unnested dictionaries (`{"organization_id": ...}`) to `context_variables`, which now enforces `extra="forbid"`.
8. **Cross-Domain DTO Parity & State Transit DTO Leaks**:
   - `DistilledEvaluation`: Backend `synthesis.py#L102` defines `status: str | None = None`, but Flutter `client_app_v2/lib/features/execution/models/distilled_evaluation.dart` lacks `status`, failing `scripts/audit_dto_parity.py`.
   - `StepContextMetadataDTO.gvars`: In @[backend_v2/models/dtos/hook_delta.py#L264-L286], `gvars: dict[str, object]` triggers `naked_dict_annotations`.
   - `TranslationResponseDTO.translated_data`: In @[backend_v2/models/dtos/state.py#L42-L51], `translated_data: dict[str, Any]` triggers `naked_dict_annotations`.
   - `LightweightMatrixOutput.extensions`: In @[backend_v2/models/dtos/lightweight_matrix.py#L43-L57, #L76-L128], `engine_debug_trace: dict[str, Any]` and `extensions: dict[LaxXaiExtensionType, Any]` trigger `naked_dict_annotations`.
   - `SynthesisMetadataDTO`: In @[backend_v2/models/domain/synthesis.py#L225-L251], `global_context_vars`, `execution_summary`, and `step_metrics` are annotated with `dict[str, Any] | None`.
9. **Hardcoded Language Specifications & Ad-Hoc Locale Fallbacks**:
   - In @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L106-L343], hardcoded tuple `if context.locale in ("fi", "en")` with `else: locale = "en"` drops valid locales (specifically Swedish `"sv"`) down to `"en"`.
   - In @[backend_v2/models/auth.py#L176-L215, #L384-L403], `UserBase.language` uses ad-hoc `Literal["fi", "en", "sv"]` disconnected from `SystemLocale` enum, while `UserUpdate.language` is untyped `str | None`.
   - In @[backend_v2/models/enums.py#L488-L492] and @[client_app_v2/lib/core/models/enums.dart#L380-L389], `SystemLocale` only defines `EN = "en"` and `FI = "fi"`, omitting `SV = "sv"` and creating a cross-domain mismatch with `auth.py`.
   - In @[backend_v2/hooks/input_processing.py#L88-L129], `_process_questionnaire` executes `title_text = expected_input.label.resolve("en")` and crashes fail-fast with `System Configuration Error: Missing mandatory English label for '{key}' questionnaire.` even when running a Finnish/Swedish workflow where `state.global_context_vars.language` is active.
   - In @[backend_v2/core/registry.py#L195-L211, #L335-L350, #L357-L372, #L379-L788], @[backend_v2/database/repositories/knowledge.py#L50-L60], @[backend_v2/hooks/input_processing.py#L133-L203], and @[backend_v2/hooks/source_verification_hook.py#L117-L234], function signatures and fallback branches use raw string literals `"en"` instead of referencing `SystemLocale.EN.value`.

---

## Target Scope & Boundaries

### TARGET Files (To Modify)
- @[backend_v2/models/enums.py#L488-L492] [MODIFY]: Add `SV = "sv"` to `SystemLocale` enum to establish unified trilingual SSOT (`EN`, `FI`, `SV`).
- @[client_app_v2/lib/core/models/enums.dart#L380-L389] [MODIFY]: Add `@JsonValue('sv') sv` to `SystemLocale` enum to maintain 100% full-duplex cross-domain parity.
- @[client_app_v2/lib/l10n/app_en.arb#L1418-L1425] [MODIFY]: Add `"profileLanguageSv": "Swedish (sv)"` to support Swedish locale display.
- @[client_app_v2/lib/l10n/app_fi.arb#L916-L922] [MODIFY]: Add `"profileLanguageSv": "Ruotsi (sv)"` to support Swedish locale display in Finnish UI.
- @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart#L199-L207] [MODIFY]: Add `SystemLocale.sv => l10n.profileLanguageSv` to the exhaustive `switch (locale)` expression.
- @[backend_v2/models/auth.py#L176-L215, #L384-L403] [MODIFY]: Bind `UserBase.language` to `Annotated[SystemLocale, Field(description="Preferred UI language")]` and `UserUpdate.language` to `SystemLocale | None = None`.
- @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L106-L343] [MODIFY]: Eradicate hardcoded `if context.locale in ("fi", "en")` tuple and assign `locale = context.locale` directly without lazy `or` operators (AdapterContext.locale is guaranteed non-empty by ingress validation).
- @[backend_v2/hooks/input_processing.py#L88-L129, #L133-L203, #L236-L421] [MODIFY]: Update `_process_questionnaire` to accept `target_locale: str`, resolve title sequentially (attempting `expected_input.label.resolve(target_locale)`, then `expected_input.label.resolve(SystemLocale.EN.value)`, then fallback to `key`) using explicit `if not title_text:` checks without QGR016 chained `or` operators, pass `target_locale=language` from `_extract_raw_value` loop, and harmonize `_process_chat_history(..., language=SystemLocale.EN.value)`.
- @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L40-L114] [MODIFY]: Validate `value` into `LightweightMatrixOutput` before calling `ContextRouter.route_and_prune`, ensuring typed domain transit and eliminating raw dictionary duck-typing at prompt context generation.
- @[backend_v2/core/registry.py#L195-L211, #L335-L350, #L357-L372, #L379-L788] [MODIFY]: Harmonize `target_locale: str = SystemLocale.EN.value` across `SchemaBuilderStrategy` and concrete strategies (`MarkdownSchemaStrategy`, `HeroInsightSchemaStrategy`, `GridSchemaStrategy`).
- @[backend_v2/database/repositories/knowledge.py#L50-L60] [MODIFY]: Bind default `language: str = SystemLocale.EN.value` in `add_banned_phrase`.
- @[backend_v2/hooks/source_verification_hook.py#L117-L234] [MODIFY]: Update fallback locale in `source_verification_hook.py` to `SystemLocale.EN.value`.
- @[backend_v2/models/execution_core.py#L56-L106] [MODIFY]: Clean up duplicate `= Field(default_factory=ContextVariablesDTO)` assignment on `context_variables` Annotated property per `pydantic_annotated_fields_mandate`.
- @[backend_v2/models/dtos/context_variables.py#L18-L29, #L38-L191] [MODIFY]: Clean up duplicate `= Field(...)` assignments on Annotated properties in `EvaluatedMatrixContextDTO.raw_atoms` and `ContextVariablesDTO.variables` per `pydantic_annotated_fields_mandate`.
- @[backend_v2/models/state.py#L69-L134, #L157-L207, #L301-L477, #L615-L631] [MODIFY]: Bind `TraceEvent.content` to closed union `StepPayloadValue | DomainInputValue | BaseModel | StepOutputContentDTO | dict[str, StepPayloadValue | DomainInputValue] | None`, bind `TraceEvent.metadata` to typed `TraceEventMetadataDTO`, clean up duplicate `Field(...)` assignments on Annotated attributes across all sibling classes (`ReasoningTrace.token_usage`, `TraceEvent.event_id`, `TraceEvent.timestamp`, `TraceEvent.content`, `TraceEvent.metadata`, `TraceEvent.mcp_audit_traces`, `WorkflowState.execution_id`, `WorkflowState.created_at`, `ExecutionState.evidence_quotes`) per `pydantic_annotated_fields_mandate`, and type `StateProjector._snapshot` as `dict[str, StepOutputContentDTO]` (preventing Primitive Obsession nested dict violations).
- @[backend_v2/models/state.py] [MODIFY]: In module-level namespace binding lines 240-299, eradicate legacy module imports (`_inputs_mod`, `_step_output_mod`), eradicate `.__dict__` dynamic reflection, and eradicate negative string filter in `_state_localns`; explicitly import and bind required model types (specifically and exhaustively: `WorkflowInputs`, `WorkflowInputsIngress`, `DomainInputValue`, `StepOutputDTO`, and `StepPayloadValue`) and ensure rebuild calls execute cleanly.
- @[backend_v2/models/state.py#L480-L612] [MODIFY]: Eradicate `model_construct()` fallback in `StateProjector._build_dto_list()`; raise `AppException(ErrorCodes.VALIDATION_FAILED)` immediately upon validation failure. Update `_build_dto_list()` to iterate `step_output.data.items()` directly. Unpack `ExecutionInputsDTO`, `WorkflowInputs`, `StepOutputContentDTO`, and `LightweightMatrixDTO` in `apply_delta()` into `StepOutputContentDTO(data=...)`, and wrap GDPR tombstone markers into `StepOutputContentDTO(data={"_redacted": True, "hash": redacted_hash})`.
- @[backend_v2/models/dtos/trace.py#L150-L155, #L179-L200] [MODIFY]: Preserve sanctioned AST exemption on `TraceEventMetadataEnvelope` (as an envelope projection filter extracting `_step_metadata` from polymorphic content in `execution_worker.py` and `synthesis_reducers.py`), tighten `TraceMatrixPayloadDTO.atom_quotes` to `Annotated[list[str] | None, Field(default=None, description="Optional accumulated atom quotes from matrix evaluation")] = None`, and define [NEW] `TraceEventMetadataDTO` and [NEW] `ProgressTracePayloadDTO` in @[backend_v2/models/dtos/trace.py] with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` using Python 3.14 Annotated syntax.
- @[backend_v2/models/dtos/step_output.py#L55-L69] [MODIFY]: Add `ProgressTracePayloadDTO` to `StepPayloadValue` closed union.
- @[backend_v2/models/dtos/node_execution.py#L73-L90, #L93-L124, #L130-L142] [MODIFY]: Clean up duplicate `= Field(...)` assignments across all sibling classes (`LogicNodeStateDTO.steps`, `LogicNodeStateDTO.dynamic_inputs`, `LogicEvaluationContextDTO.global_context_vars`, `LogicEvaluationContextDTO.inputs`, `StepOutputContentDTO.data`) per `pydantic_annotated_fields_mandate`, and implement Mapping protocol (`items()`, `__getitem__`) on `StepOutputContentDTO` delegating to `self.data`.
- @[backend_v2/services/orchestrator/context_router.py#L52-L127] [MODIFY]: Restrict `ContextRouter.route_and_prune` signature strictly to `trace_event: LightweightMatrixOutput`, eradicate `isinstance(trace_event, Mapping)` branches, and deterministically resolve to empty dictionary `{}` when `output_profile` is `None` (banning all-inclusive fallback).
- @[backend_v2/services/orchestrator/dag_executor.py#L185-L350] [MODIFY]: Eradicate `isinstance(..., Mapping)` fallback dict unpacking for `global_context_vars` in `NodeExecutor.execute()`.
- @[backend_v2/services/orchestrator/dag_executor.py#L438-L1295] [MODIFY]: Pass typed `exec_record.raw_inputs` and `StepOutputContentDTO` directly into `TraceEvent` without intermediate `.model_dump()` dictionary conversions.
- @[backend_v2/services/orchestrator/dag_executor.py#L727-L1028] [MODIFY]: Pass `content=lightweight_matrix` directly to `TraceEvent` without intermediate `.model_dump()`.
- @[backend_v2/services/orchestrator/dag_executor.py#L727-L1028] [MODIFY]: Update `evt.metadata` check to use typed property `evt.metadata.generated_schema is not None`.
- @[backend_v2/services/orchestrator/dag_executor.py#L1059-L1090] [MODIFY]: Instantiate typed `ProgressTracePayloadDTO(message=message, progress_pct=pct)` in `_emit_preflight_progress`.
- @[backend_v2/services/orchestrator/strategies/llm.py#L220-L1020] [MODIFY]: Instantiate `TraceEventMetadataDTO` directly instead of constructing a raw metadata dictionary.
- @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L48-L267] [MODIFY]: Pass `content=starvation_dto` directly to `TraceEvent` without intermediate `.model_dump(mode="json")` double-serialization.
- @[backend_v2/services/orchestrator/state_reducer.py#L109-L424] [MODIFY]: Instantiate `TraceEventMetadataDTO` directly across decision and context update events (`mcp_audit_traces`, `estimated_token_count`, and `is_context_update=True`).
- @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384] [MODIFY]: Replace 3 naked `dict[str, Any]` annotations with `dict[str, JsonValue]` and delete unreachable dead return statement at L384.
- @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart#L1-L24] [MODIFY]: Add `String? status` field to restore 1:1 cross-domain DTO parity with backend `DistilledEvaluation`.
- @[backend_v2/models/dtos/hook_delta.py#L264-L286] [MODIFY]: Replace `gvars: dict[str, object]` with `Annotated[dict[str, JsonValue], Field(default_factory=dict, description="Global context variables dictionary.")]` in `StepContextMetadataDTO`.
- @[backend_v2/models/dtos/state.py#L16-L27, #L42-L51] [MODIFY]: Replace mutable default in `HookStateMetadata.fields_to_translate: list[str] = []` with `Annotated[list[str], Field(default_factory=list)]`, type `target_locale` with `Annotated[str, Field(...)]`, and replace `translated_data: dict[str, Any]` with `Annotated[dict[str, JsonValue], Field(description="Fully translated dictionary.")]` in `TranslationResponseDTO`.
- @[backend_v2/models/dtos/lightweight_matrix.py#L43-L57, #L76-L128] [MODIFY]: Replace naked dict in `XAILogDto.engine_debug_trace` (`Annotated[dict[str, JsonValue], Field(default_factory=dict, description="System diagnostic trace")]`), clean up duplicate `= Field(...)` on `LightweightMatrixOutput.evaluated_atoms` and `XAILogDto.engine_debug_trace`, replace loose `atom_quotes` with `Annotated[list[str] | None, Field(default=None, description="Atom quotes")] = None`, and type `LightweightMatrixOutput.extensions` as `Annotated[dict[LaxXaiExtensionType, JsonValue], Field(default_factory=dict, description="Mapped XAI extensions")]` using Python 3.14 Annotated syntax.
- @[backend_v2/models/domain/synthesis.py#L96-L114, #L225-L251, #L254-L262] [MODIFY]: Type `SynthesisMetadataDTO.global_context_vars` as `Annotated[GlobalContextVarsDTO | None, Field(default=None, description="Global context variables")] = None`, `execution_summary` as `Annotated[dict[str, JsonValue] | None, Field(default=None, description="Execution summary")] = None`, `step_metrics` as `Annotated[dict[str, JsonValue] | None, Field(default=None, description="Step metrics")] = None`, and clean up duplicate `= Field(...)` assignments across all sibling classes (`DistilledEvaluation.exact_quotes`, `SynthesisStepDataDTO.token_usage`, `SynthesisMetadataDTO.token_usage`, `SynthesisMetadataDTO.step_results`) using Python 3.14 Annotated syntax.
- @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384] [MODIFY]: Fix legacy unnested `context_variables` fixtures in `test_workflow_state_accessors_and_properties` and `test_workflow_state_none_branches`, wrap legacy raw string assignment in `test_state_projector_fail_fast_on_legacy_data` with `# type: ignore[assignment]`, and add ISTQB negative partitions asserting Fail-Fast on invalid payloads and zero `model_construct()` bypasses.
- @[backend_v2/tests/unit/services/orchestrator/test_context_router.py#L184-L195] [MODIFY]: Align test fixtures to pass `LightweightMatrixOutput` directly, update `test_route_and_prune_missing_profile()` to assert `assert result.extensions == {}` (proving eradication of all-inclusive fallback), and assert `ConfigurationError` on untyped inputs.
- @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1807-L1883] [MODIFY]: Update test fixture passing dict `global_context_vars={"language": "fi"}` to `GlobalContextVarsDTO(language="fi")`.
- @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py#L321-L388] [MODIFY]: Update `assert events[0].metadata == {"is_context_update": True}` to direct typed attribute assertion `assert events[0].metadata.is_context_update is True`.
- @[backend_v2/tests/unit/services/orchestrator/test_linguistics_state_reduction_regression.py#L44-L79, #L129-L176] [MODIFY]: Update `assert evt.metadata == {"is_context_update": True}` to direct typed attribute assertion `assert evt.metadata.is_context_update is True`, and eliminate `model_construct()` at L165.
- @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L1029-L1085] [MODIFY]: Eradicate `model_construct()` in test fixtures, instantiating typed `ReducedAtomDTO` instances directly.
- @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L201-L264] [MODIFY]: Update `assert result.trace_events[0].content["event_type"] == "starvation"` to typed attribute check `assert result.trace_events[0].content.event_type == "starvation"`.
- @[backend_v2/tests/unit/hooks/test_input_processing.py#L191-L245, #L640-L651] [MODIFY]: Add test asserting that `_process_questionnaire` resolves questionnaire titles under non-English locales without configuration errors.

### CONTEXT Files (Read-Only SSOT References)
- @[backend_v2/models/domain/inputs.py#L175-L212]: SSOT for `DomainInputValue` closed union.
- @[backend_v2/models/dtos/hook_state.py#L36-L63]: SSOT for `ExecutionInputsDTO`.
- @[backend_v2/models/dtos/context_variables.py#L38-L191]: SSOT for `ContextVariablesDTO`.
- @[backend_v2/models/dtos/lightweight_matrix.py#L76-L128]: SSOT for `LightweightMatrixOutput`.
- @[backend_v2/models/dtos/atom_evaluation.py#L42-L57]: SSOT for `LightweightMatrixDTO`.
- @[backend_v2/models/domain/synthesis.py#L96-L114]: SSOT for backend `DistilledEvaluation`.

---

## Phase 1: Pre-Implementation Technical Debt Cleanups
Before introducing structural schema modifications, the following technical debt items must be eradicated:
1. **`test_state.py` Legacy Fixture Repair**:
   - Location: @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384].
   - Action: Update `test_workflow_state_accessors_and_properties` and `test_workflow_state_none_branches` to pass `context_variables=ContextVariablesDTO(variables={...})` or `{"variables": {...}}`, resolving the 2 active test failures. In `test_state_projector_fail_fast_on_legacy_data`, wrap legacy raw string assignment in `# type: ignore[assignment]` with audit explanation.
2. **`_state_localns` Reflection & Negative Filter Purge**:
   - Location: @[backend_v2/models/state.py] at module-level namespace binding lines 240-299.
   - Action: Remove `import backend_v2.models.domain.inputs as _inputs_mod` and `import backend_v2.models.dtos.step_output as _step_output_mod`. Eradicate `_inputs_mod.__dict__` and `not k.startswith("__")`. Explicitly import and bind `WorkflowInputs`, `WorkflowInputsIngress`, `DomainInputValue`, `StepOutputDTO`, and `StepPayloadValue`.
3. **`synthesis_payload_compressor.py` Dead Code Removal**:
   - Location: @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384].
   - Action: Remove unreachable `return val` following the return comprehension.
4. **1-Hop Caller Test Assertion & Fixture Alignment**:
   - Location: @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py#L321-L388] and @[backend_v2/tests/unit/services/orchestrator/test_linguistics_state_reduction_regression.py#L44-L79, #L129-L176].
   - Action: Update dictionary equality checks (`assert evt.metadata == {"is_context_update": True}`) to direct typed attribute checks (`assert evt.metadata.is_context_update is True`), and eliminate `model_construct()` in `HookState` test fixture at L165.
   - Location: @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L1029-L1085].
   - Action: Replace `StepOutputDTO.model_construct()` fixtures with typed `ReducedAtomDTO` instances to eliminate duct-tape test fixtures.
   - Location: @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L201-L264].
   - Action: Update `assert result.trace_events[0].content["event_type"] == "starvation"` to typed dot-notation assertion `assert result.trace_events[0].content.event_type == "starvation"`.
   - Location: @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1807-L1883].
   - Action: Update `ExecutionMetadata(global_context_vars={"language": "fi"})` fixture to pass typed `GlobalContextVarsDTO(language="fi")`.
   - Location: @[backend_v2/tests/unit/services/orchestrator/test_context_router.py#L184-L195].
   - Action: Update `test_route_and_prune_missing_profile()` to assert `assert result.extensions == {}`, mathematically verifying the eradication of all-inclusive fallbacks when `output_profile is None`.
5. **Duplicate Field() Default Cleanups on Annotated Attributes Across All Sibling Classes**:
   - Location: @[backend_v2/models/state.py#L69-L134, #L157-L207, #L301-L477, #L615-L631], @[backend_v2/models/execution_core.py#L56-L106], @[backend_v2/models/dtos/node_execution.py#L73-L90, #L93-L124, #L130-L142], @[backend_v2/models/dtos/context_variables.py#L18-L29, #L38-L191], @[backend_v2/models/dtos/lightweight_matrix.py#L43-L57, #L76-L128], and @[backend_v2/models/domain/synthesis.py#L96-L114, #L225-L251, #L254-L262].
   - Action: Remove redundant `= Field(...)` assignments on Annotated properties across all sibling classes (`ReasoningTrace.token_usage`, `TraceEvent.event_id`, `TraceEvent.timestamp`, `TraceEvent.content`, `TraceEvent.metadata`, `TraceEvent.mcp_audit_traces`, `WorkflowState.execution_id`, `WorkflowState.created_at`, `ExecutionState.evidence_quotes`, `ExecutionCoreFields.context_variables`, `LogicNodeStateDTO.steps`, `LogicNodeStateDTO.dynamic_inputs`, `LogicEvaluationContextDTO.global_context_vars`, `LogicEvaluationContextDTO.inputs`, `StepOutputContentDTO.data`, `EvaluatedMatrixContextDTO.raw_atoms`, `ContextVariablesDTO.variables`, `XAILogDto.engine_debug_trace`, `LightweightMatrixOutput.evaluated_atoms`, `LightweightMatrixOutput.extensions`, `DistilledEvaluation.exact_quotes`, `SynthesisStepDataDTO.token_usage`, `SynthesisMetadataDTO.token_usage`, `SynthesisMetadataDTO.step_results`) to strictly comply with `pydantic_annotated_fields_mandate`.
6. **`input_processing.py` Python Syntax Normalization**:
   - Location: @[backend_v2/hooks/input_processing.py#L236-L421].
   - Action: Fix unparenthesized exception tuple syntax `except ValidationError, TypeError:` by wrapping in standard parentheses `except (ValidationError, TypeError):`.
7. **`auth.py` Model Typing Hardening**:
   - Location: @[backend_v2/models/auth.py#L176-L215, #L384-L403].
   - Action: Replace bare type annotations in `UserUpdate` with strictly typed Annotated fields: `language: Annotated[SystemLocale | None, Field(default=None, description="Preferred UI language")] = None` and `theme_mode: Annotated[Literal["system", "light", "dark"] | None, Field(default=None, description="Preferred Theme Mode")] = None`.
8. **`context_builder.py` In-Place Mutation Eradication**:
   - Location: @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L40-L114].
   - Action: Eradicate in-place `del pruned_dict["evaluated_atoms"]` mutation and replace with pure immutable serialization `pruned.model_dump(exclude={"evaluated_atoms"})` without mutable dictionary side-effects.
9. **`HookStateMetadata` Mutable Default Eradication**:
   - Location: @[backend_v2/models/dtos/state.py#L16-L27].
   - Action: Replace mutable default `fields_to_translate: list[str] = []` with `Annotated[list[str], Field(default_factory=list, description="Targeted translation fields")]` and type `target_locale: Annotated[str, Field(description="Target locale code")]`.
10. **`StepOutputContentDTO` Mapping Protocol & `StateProjector._build_dto_list` Iteration**:
    - Location: @[backend_v2/models/dtos/node_execution.py#L130-L142] and @[backend_v2/models/state.py#L551-L589].
    - Action: Implement Mapping protocol (`def items(self): return self.data.items()` and `def __getitem__(self, key: str): return self.data[key]`) on `StepOutputContentDTO` delegating to `self.data`. In `StateProjector._build_dto_list()`, update iteration to access `step_output.data.items()` directly, preventing `AttributeError` during reconstitution.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`TraceEvent` Content & Metadata**<br>@[backend_v2/models/state.py#L157-L207]<br>@[backend_v2/models/dtos/trace.py#L150-L155] | Banned `content: dict[str, Any]` and `metadata: dict[str, Any]`. Banned duplicate `Field(...)` assignments on Annotated attributes across all sibling classes. | Bind `content` to `StepPayloadValue \| DomainInputValue \| BaseModel \| StepOutputContentDTO \| dict[str, StepPayloadValue \| DomainInputValue] \| None`. Define `TraceEventMetadataDTO` with 8 explicit typed fields (`latency_ms`, `chunk_size`, `context_char_length`, `prompt_contexts`, `generated_schema`, `is_context_update`, `mcp_audit_traces`, `estimated_token_count`). Clean up duplicate `Field()` default assignments across all sibling classes. | Pruned generic dynamic event wrappers. Direct typed Pydantic V2 native validation with `extra="forbid"`. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict` reports 0 violations. |
| **`Trace Metadata Typing & Envelope Governance`**<br>@[backend_v2/models/dtos/trace.py#L150-L155, #L179-L200] | Banned naked dictionaries `metadata: dict[str, Any]`, untyped `list[Any]` in `atom_quotes`, and untyped progress payloads `content={"message": ..., "progress_pct": ...}`. Banned extending `extra="ignore"` to domain models. | Author [NEW] `TraceEventMetadataDTO` and [NEW] `ProgressTracePayloadDTO` in @[backend_v2/models/dtos/trace.py] with `ConfigDict(strict=True, extra="forbid", frozen=True)`. Tighten `TraceMatrixPayloadDTO.atom_quotes` to `list[str] | None`. Preserve `TraceEventMetadataEnvelope` with explicit AST exemption in `test_ast_domain_security_guardrails.py#L81` strictly as an envelope projection filter for `_step_metadata`. | Pruned dynamic dictionary indexing, loose list typing, and loose runtime parsing in worker trace inspection. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos/trace.py --strict` reports 0 violations. Pydantic validation rejects unmapped keys in metadata. |
| **`StateProjector` & Reconstitution**<br>@[backend_v2/models/state.py#L480-L612]<br>@[backend_v2/models/dtos/node_execution.py#L130-L142] | Banned `_snapshot: dict[str, Any]`, banned Primitive Obsession nested dict `dict[str, dict[...]]`, banned `.model_construct()` fallback in `_build_dto_list()`, banned raw dict GDPR tombstone assignment, and banned calling `.items()` on models lacking mapping protocol. | `_snapshot: dict[str, StepOutputContentDTO]`. Implement mapping protocol (`items()`, `__getitem__`) on `StepOutputContentDTO` delegating to `self.data`. Update `_build_dto_list()` to iterate `step_output.data.items()`. When validation fails, log RFC 7807 error and re-raise `AppException(ErrorCodes.VALIDATION_FAILED)` immediately. In `apply_delta()`, unwrap payloads into `StepOutputContentDTO(data=...)` and wrap GDPR tombstone into `StepOutputContentDTO(data={"_redacted": True, "hash": redacted_hash})`. | Pruned fallback compaction layers and redundant intermediate dict dumps. Reuses existing SSOT `StepOutputContentDTO`. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict` reports 0 violations. ISTQB negative test passes 100%. |
| **`_state_localns` Namespace Binding**<br>@[backend_v2/models/state.py] | Banned `_inputs_mod.__dict__` dynamic reflection and banned `not k.startswith("__")` negative string filtering in module-level namespace binding. | Remove legacy module imports; explicit positive dictionary mapping of authoritative imported types (specifically and exhaustively: `WorkflowInputs`, `WorkflowInputsIngress`, `DomainInputValue`, `StepOutputDTO`, and `StepPayloadValue`). | Pruned dynamic module namespace introspection cascades. | `audit_dict_eradication.py` reports 0 reflection violations (`QGR001`). |
| **`ContextRouter.route_and_prune`**<br>@[backend_v2/services/orchestrator/context_router.py#L52-L127]<br>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L40-L114] | Banned `trace_event: Any`, banned `isinstance(trace_event, Mapping)`, banned dictionary key checks (`"evaluated_atoms" not in trace_event`), and banned all-inclusive fallback when `output_profile` is `None`. Banned dictionary duck-typing and `del` mutation in `context_builder.py`. | Signature strictly enforces `trace_event: LightweightMatrixOutput`. Validate type fail-fast and prune visible extensions directly from typed model; if `output_profile` is `None`, deterministically resolve extensions to empty dict `{}`. In `context_builder.py`, validate `value` into `LightweightMatrixOutput` before calling `route_and_prune`, and prune via immutable `pruned.model_dump(exclude={"evaluated_atoms"})`. | Pruned 38 lines of defensive parsing, mapping validation, dictionary re-packing, and legacy fallback shims. | `test_context_router.py` unit suite passes with zero `Mapping` checks and 100% typed inputs. |
| **`DAGExecutor` Node Execution**<br>@[backend_v2/services/orchestrator/dag_executor.py#L185-L350] | Banned `isinstance(global_context_vars, Mapping)` and `GlobalContextVarsDTO(**dict(...))` conversion. | Pass `global_context_vars: GlobalContextVarsDTO` strictly as typed DTO instance. Remove fallback dict unpackers. | Pruned defensive `isinstance` cascades across NodeExecutor. | `test_dag_executor.py` asserts strict DTO transit without dictionary wrapping. |
| **`DAGExecutor` Pipeline Trace Construction**<br>@[backend_v2/services/orchestrator/dag_executor.py#L438-L1295] | Banned `.model_dump()` before appending to trace events (`raw_inputs`, `lightweight_matrix`). Banned untyped progress dict. | Pass `content=exec_record.raw_inputs` and `content=lightweight_matrix` directly. Define `ProgressTracePayloadDTO` for progress events. Use dot-notation `evt.metadata.generated_schema is not None`. | Pruned intermediate JSON serialization and deserialization overhead across DAG loop. | `test_dag_executor.py` verifies zero double-serialization in trace events. |
| **LLM Strategy Trace Event Metadata**<br>@[backend_v2/services/orchestrator/strategies/llm.py#L220-L1020] | Banned building raw metadata dictionary `metadata = {"latency_ms": ..., "chunk_size": ..., ...}` and `metadata["generated_schema"] = ...`. | Instantiate typed `TraceEventMetadataDTO` directly with explicit arguments. | Pruned manual dictionary mutation and string-keyed metadata unpacking. | `uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/strategies/llm.py --strict` reports 0 violations. |
| **Synthesis Engine Starvation Trace**<br>@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L48-L267] | Banned `.model_dump(mode="json")` before appending `starvation_dto` to `TraceEvent(content=...)`. | Pass `content=starvation_dto` directly as typed domain DTO. | Pruned intermediate JSON dump double-serialization overhead. | Unit test verifies typed DTO payload in trace event. |
| **`state_reducer.py` Trace Event Emission**<br>@[backend_v2/services/orchestrator/state_reducer.py#L109-L424] | Banned passing untyped dictionaries `metadata={"is_context_update": True}`, `metadata={"estimated_token_count": ...}`, and `metadata={"mcp_audit_traces": ...}`. | Instantiate typed `TraceEventMetadataDTO` directly across decision and context update events. | Pruned ad-hoc dictionary construction in state reducer. | `test_state_reducer.py` and `test_linguistics_state_reduction_regression.py` pass 100% with direct typed attribute assertions. |
| **`synthesis_payload_compressor.py`**<br>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384] | Banned 3 naked `dict[str, Any]` annotations and banned dead unreachable code at L384. | Annotate `filtered`, `eval_dict`, and `result_dict` as `dict[str, JsonValue]`. Delete dead return. | Pruned obsolete dictionary type hints. | `uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --strict` reports 0 violations. |
| **Cross-Domain DTO Parity (`DistilledEvaluation`)**<br>@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart#L1-L24]<br>@[backend_v2/models/domain/synthesis.py#L96-L114] | Banned asymmetric field definitions where backend serializes `status` but frontend Dart Freezed model lacks the field. | Add `String? status` to `DistilledEvaluation` factory constructor in Flutter and regenerate freezed models. | Pruned manual client-side JSON stripping. Full-duplex serialization parity. | `uv run python scripts/audit_dto_parity.py` reports 0 mismatches. |
| **State Transit DTO Hardening**<br>@[backend_v2/models/dtos/hook_delta.py#L264-L286]<br>@[backend_v2/models/dtos/state.py#L16-L27, #L42-L51]<br>@[backend_v2/models/dtos/lightweight_matrix.py#L43-L57, #L76-L128]<br>@[backend_v2/models/domain/synthesis.py#L96-L114, #L225-L251, #L254-L262] | Banned naked `dict[str, Any]`, `dict[str, object]`, mutable defaults `fields_to_translate = []`, and untyped `Any` in DTO metadata fields. Banned bare type hints, phantom explanation DTOs, and duplicate `= Field(...)` trailing assignments. | Enforce Python 3.14 `Annotated[..., Field(...)]` on `StepContextMetadataDTO.gvars`, `TranslationResponseDTO.translated_data`, `XAILogDto.engine_debug_trace`, `HookStateMetadata.fields_to_translate/target_locale`, and `LightweightMatrixOutput.extensions`. Bind `SynthesisMetadataDTO.global_context_vars` to `GlobalContextVarsDTO \| None`. Zero duplicate `= Field()` assignments when `default_factory` is in Annotated. | Pruned loose type annotations across intermediate step and synthesis DTOs. | `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos/ --strict` reports 0 violations on target files. |
| **1-Hop Caller Test Modernization**<br>@[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py#L321-L388]<br>@[backend_v2/tests/unit/services/orchestrator/test_linguistics_state_reduction_regression.py#L44-L79, #L129-L176]<br>@[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L1029-L1085]<br>@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L201-L264]<br>@[backend_v2/tests/unit/services/orchestrator/test_context_router.py#L184-L195] | Banned asserting raw dictionary equality against typed `TraceEvent.metadata`, banned dictionary indexing on typed `content`, banned `.model_construct()` in test fixtures, and banned asserting legacy all-inclusive fallback in `test_context_router.py`. | Assert direct typed attribute access (`assert evt.metadata.is_context_update is True`, `assert result.trace_events[0].content.event_type == "starvation"`). Modernize fixtures to instantiate typed `ReducedAtomDTO` models. Update `test_route_and_prune_missing_profile()` to assert `assert result.extensions == {}`. | Pruned legacy test fixtures, dictionary assumptions, and fallback assertions in caller tests. | All caller test suites pass 100% with typed attribute assertions. |
| **Internationalization & Dynamic Locale SSOT**<br>@[backend_v2/models/enums.py#L488-L492]<br>@[client_app_v2/lib/core/models/enums.dart#L380-L389]<br>@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart#L199-L208]<br>@[client_app_v2/lib/l10n/app_en.arb#L1418-L1425]<br>@[client_app_v2/lib/l10n/app_fi.arb#L916-L922]<br>@[backend_v2/models/auth.py#L176-L215, #L384-L403]<br>@[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L106-L343]<br>@[backend_v2/hooks/input_processing.py#L88-L129, #L133-L203, #L236-L421] | Banned hardcoded locale tuples `("fi", "en")`, ad-hoc `Literal["fi", "en", "sv"]`, untyped strings `target_locale = "en"`, non-exhaustive Dart enum switch expressions, QGR016 chained `or` operators (`a or b or c`), and mandatory English crashes on non-English workflows. | Expand `SystemLocale` with `SV = "sv"` in Python and Dart. Add `profileLanguageSv` to `.arb` files and exhaustively handle in `profile_general_tab.dart`. Bind `UserBase.language` to `SystemLocale`. Dynamically pass runtime `language` to `_process_questionnaire` and resolve `I18nText` sequentially with explicit `if not title_text:` checks. Assign `locale = context.locale` directly. Use `SystemLocale.EN.value` for default signatures. | Pruned brittle hardcoded string literals, artificial monolingual constraints, and QGR016 multi-fallback chains. Full-duplex trilingual SSOT (`EN`, `FI`, `SV`). | `scripts/audit_dto_parity.py` reports 0 mismatches. Flutter build and unit test verify questionnaire and profile dropdown resolution under non-English locales without configuration crash and without QGR016 warnings. |

---

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS">
    <action>In @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384], update `test_workflow_state_accessors_and_properties` and `test_workflow_state_none_branches` to pass `context_variables=ContextVariablesDTO(variables={...})` or `{"variables": {...}}`, resolving the 2 active test failures. In `test_state_projector_fail_fast_on_legacy_data`, wrap legacy raw string assignment in `# type: ignore[assignment]` with audit explanation.</action>
    <action>In @[backend_v2/models/state.py], at module-level namespace binding lines 240-299, remove legacy module imports (_inputs_mod, _step_output_mod), eradicate dynamic `.__dict__` reflection, and eradicate negative string filter in `_state_localns`. Explicitly import and bind required imported types (specifically and exhaustively: `WorkflowInputs`, `WorkflowInputsIngress`, `DomainInputValue`, `StepOutputDTO`, and `StepPayloadValue`). Also clean up duplicate `Field(...)` assignments on Annotated attributes across all sibling classes in @[backend_v2/models/state.py#L69-L134, #L157-L207, #L301-L477, #L615-L631], @[backend_v2/models/execution_core.py#L56-L106], @[backend_v2/models/dtos/node_execution.py#L73-L90, #L93-L124, #L130-L142], @[backend_v2/models/dtos/context_variables.py#L18-L29, #L38-L191], @[backend_v2/models/dtos/lightweight_matrix.py#L43-L57, #L76-L128], and @[backend_v2/models/domain/synthesis.py#L96-L114, #L225-L251, #L254-L262].</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L40-L114], replace in-place `del` mutation with immutable `pruned.model_dump(exclude={"evaluated_atoms"})`.</action>
    <action>In @[backend_v2/hooks/input_processing.py#L236-L421], fix exception tuple syntax by replacing `except ValidationError, TypeError:` with `except (ValidationError, TypeError):`.</action>
    <action>In @[backend_v2/models/auth.py#L176-L215, #L384-L403], harden `UserUpdate` with strictly typed Annotated fields: `language: Annotated[SystemLocale | None, Field(default=None, description="Preferred UI language")] = None` and `theme_mode: Annotated[Literal["system", "light", "dark"] | None, Field(default=None, description="Preferred Theme Mode")] = None`.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384], remove the unreachable dead code `return val` following the return comprehension.</action>
    <action>In @[backend_v2/models/dtos/state.py#L16-L27], replace mutable default `fields_to_translate: list[str] = []` with `Annotated[list[str], Field(default_factory=list, description="Targeted translation fields")]` and type `target_locale: Annotated[str, Field(description="Target locale code")]`.</action>
    <action>In @[backend_v2/models/dtos/node_execution.py#L130-L142] and @[backend_v2/models/state.py#L551-L589], implement Mapping protocol (`def items(self): return self.data.items()` and `def __getitem__(self, key: str): return self.data[key]`) on `StepOutputContentDTO` delegating to `self.data`. In `StateProjector._build_dto_list()`, update iteration to access `step_output.data.items()` directly, preventing `AttributeError` during reconstitution.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py#L321-L388] and @[backend_v2/tests/unit/services/orchestrator/test_linguistics_state_reduction_regression.py#L44-L79, #L129-L176], update dictionary equality assertions `assert evt.metadata == {"is_context_update": True}` to direct typed attribute checks `assert evt.metadata.is_context_update is True`, and eliminate `model_construct()` at L165.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py#L1029-L1085], modernize test fixtures by instantiating typed `ReducedAtomDTO` instances instead of untyped dictionaries via `StepOutputDTO.model_construct()`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py#L201-L264], update `assert result.trace_events[0].content["event_type"] == "starvation"` to typed dot-notation assertion `assert result.trace_events[0].content.event_type == "starvation"`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1807-L1883], modernize fixture passing dict `global_context_vars={"language": "fi"}` to `GlobalContextVarsDTO(language="fi")`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_context_router.py#L184-L195], update `test_route_and_prune_missing_profile()` to assert `assert result.extensions == {}`, mathematically verifying the eradication of all-inclusive fallbacks when `output_profile is None`.</action>
    <constraint invariant="the_duct_tape_ban">Zero tolerance for fallback bypasses or dynamic reflection in domain models.</constraint>
    <constraint invariant="zero_tolerance_audit_loop">Pre-implementation cleanups restore baseline test pass rate to 100%.</constraint>
  </step>

  <step id="2" name="DEFINE_TRACE_DTOS_AND_EXPAND_PAYLOAD_UNION">
    <action>In @[backend_v2/models/dtos/trace.py#L150-L155], preserve sanctioned AST exemption on `TraceEventMetadataEnvelope` (as an envelope projection filter extracting `_step_metadata` from polymorphic content in `execution_worker.py` and `synthesis_reducers.py` per `test_ast_domain_security_guardrails.py#L81`).</action>
    <action>In @[backend_v2/models/dtos/trace.py#L179-L200], tighten `TraceMatrixPayloadDTO.atom_quotes` to `Annotated[list[str] | None, Field(default=None, description="Optional accumulated atom quotes from matrix evaluation")] = None` using pure Python 3.14 Annotated syntax.</action>
    <action>In @[backend_v2/models/dtos/trace.py#L202-L245], define [NEW] `ProgressTracePayloadDTO` inheriting from `BaseDTO` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` using pure Python 3.14 Annotated syntax: `message: Annotated[str, Field(description="Progress status message")]`, `progress_pct: Annotated[int, Field(ge=0, le=100, description="Progress percentage")]` (zero bare type hints).</action>
    <action>In @[backend_v2/models/dtos/trace.py#L202-L245], define [NEW] `TraceEventMetadataDTO` inheriting from `V2CoreBase` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` using pure Python 3.14 Annotated syntax: `latency_ms: Annotated[float | None, Field(description="Step latency in milliseconds")] = None`, `chunk_size: Annotated[int | None, Field(description="Number of chunks processed")] = None`, `context_char_length: Annotated[int | None, Field(description="Length of context characters")] = None`, `prompt_contexts: Annotated[list[str] | None, Field(description="Prompt context identifiers")] = None`, `generated_schema: Annotated[dict[str, JsonValue] | None, Field(description="Dynamic generated schema")] = None`, `is_context_update: Annotated[bool, Field(description="Indicates context update decision")] = False`, `mcp_audit_traces: Annotated[list[MCPAuditTrace], Field(default_factory=list, description="MCP tool audit traces")]`, `estimated_token_count: Annotated[int | None, Field(description="Estimated token count")] = None`, `step_metadata: Annotated[StepTraceMetadataDTO | None, Field(default=None, alias="_step_metadata", description="Step metadata envelope")] = None` (zero bare type hints, zero duplicate `= Field()` assignments when `default_factory` is inside `Field()`).</action>
    <action>In @[backend_v2/models/dtos/step_output.py#L55-L69], add `ProgressTracePayloadDTO` to the `StepPayloadValue` closed union.</action>
    <constraint invariant="strict_pydantic_v2_rust">Enforce strict Pydantic V2 validation on all TraceEvent payloads and metadata.</constraint>
    <constraint invariant="no_naked_dicts_in_state">Eradicate naked dict[str, Any] in state metadata.</constraint>
  </step>

  <step id="3" name="TRACE_EVENT_AND_STATE_PROJECTOR_TYPING">
    <action>In @[backend_v2/models/state.py#L157-L207], update `TraceEvent.content` to `Annotated[StepPayloadValue | DomainInputValue | BaseModel | dict[str, StepPayloadValue] | None, Field(default=None, description="Typed event payload")] = None` and `TraceEvent.metadata` to `Annotated[TraceEventMetadataDTO, Field(default_factory=TraceEventMetadataDTO, description="Typed event metadata")]` using pure Python 3.14 Annotated syntax (with zero duplicate `= Field(...)` trailing assignments).</action>
    <action>In @[backend_v2/models/state.py#L480-L612], update `StateProjector._snapshot` type annotation to `dict[str, StepOutputContentDTO]` to strictly eradicate Primitive Obsession nested dict violations.</action>
    <action>In @[backend_v2/models/state.py#L480-L612], eradicate `.model_construct()` fallback in `_build_dto_list()`. Log structured RFC 7807 error and raise `AppException(status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})` immediately upon `ValidationError`.</action>
    <action>In @[backend_v2/models/state.py#L480-L612], update `apply_delta()` to unwrap `ExecutionInputsDTO`, `WorkflowInputs`, `StepOutputContentDTO`, and `LightweightMatrixDTO` directly into `StepOutputContentDTO(data=...)` in `_snapshot[step_id]` without intermediate dict dumps or duct tape.</action>
    <action>In @[backend_v2/models/state.py#L591-L612], wrap GDPR tombstone marker in `apply_delta()` into `StepOutputContentDTO(data={"_redacted": True, "hash": redacted_hash})` instead of raw dictionary assignment into `_snapshot`.</action>
    <constraint invariant="the_duct_tape_ban">Zero tolerance for fallback bypasses via model_construct.</constraint>
    <constraint invariant="pydantic_pure_hydration_boundary">Zero intermediate model_dump dictionary roundtrips in in-memory state projection.</constraint>
  </step>

  <step id="4" name="CONTEXT_ROUTER_STRICT_TYPING">
    <action>In @[backend_v2/services/orchestrator/context_router.py#L52-L127], update `ContextRouter.route_and_prune` signature to strictly accept `trace_event: LightweightMatrixOutput`.</action>
    <action>In @[backend_v2/services/orchestrator/context_router.py#L52-L127], delete the `isinstance(trace_event, Mapping)` branch, delete `evaluated_atoms` missing key validation, prune visible block extensions directly from the typed model, and deterministically resolve extensions to `{}` when `output_profile` is `None`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L40-L114], update `case "MATRIX":` to validate `value` into `LightweightMatrixOutput` before delegating to `ContextRouter.route_and_prune`, and prune atoms via `pruned.model_dump(exclude={"evaluated_atoms"})` without in-place `del` dictionary mutation.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All steps flow through one sovereign, strictly typed execution path with zero legacy dictionary shims.</constraint>
  </step>

  <step id="5" name="DAG_EXECUTOR_AND_STRATEGY_TRANSIT_CLEANUP">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L185-L350], eradicate `isinstance(..., Mapping)` duck-typing fallback for `global_context_vars` in `NodeExecutor.execute()`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L438-L1295], pass `content=exec_record.raw_inputs` directly into `TraceEvent` without intermediate `.model_dump()`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L438-L1295], streamline pre-hydration state delta processing to pass typed payloads directly to `TraceEvent`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L727-L1028], pass `content=lightweight_matrix` directly to `TraceEvent` without `.model_dump()`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L727-L1028], update `"generated_schema" in evt.metadata` to typed dot access `evt.metadata.generated_schema is not None`.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L1059-L1090], instantiate `ProgressTracePayloadDTO(message=message, progress_pct=pct)` in `_emit_preflight_progress`.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L220-L1020], instantiate `TraceEventMetadataDTO` directly with `latency_ms`, `chunk_size`, `context_char_length`, `prompt_contexts`, and `generated_schema` instead of constructing a raw metadata dictionary.</action>
    <action>In @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L48-L267], pass `content=starvation_dto` directly to `TraceEvent` without intermediate `.model_dump(mode="json")` double-serialization.</action>
    <action>In @[backend_v2/services/orchestrator/state_reducer.py#L109-L424], instantiate `TraceEventMetadataDTO` directly across decision and context update events (`mcp_audit_traces`, `estimated_token_count`, and `is_context_update=True`).</action>
    <constraint invariant="zero_backward_compatibility_planning_ban">Do not maintain backwards-compatibility branches for legacy dictionary traces.</constraint>
    <constraint invariant="absolute_pydantic_strictness">Eliminate double-serialization across pipeline boundaries.</constraint>
  </step>

  <step id="6" name="SYNTHESIS_PAYLOAD_COMPRESSOR_CLEANUP">
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L181-L384], replace 3 naked `dict[str, Any]` annotations with `dict[str, JsonValue]` at lines 221, 293, and 374.</action>
    <constraint invariant="zero_naked_dicts_and_permissive_typing">Pass deterministic AST audit with 0 naked dict annotations.</constraint>
  </step>

  <step id="7" name="DTO_AND_CROSS_DOMAIN_PARITY_HARDENING">
    <action>In @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart#L1-L24], add `String? status` field to the `DistilledEvaluation` factory constructor and remove `// ignore_for_file: invalid_annotation_target` per project-level analysis options standards.</action>
    <action>Run Freezed code generation: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/distilled_evaluation.dart --build`.</action>
    <action>In @[backend_v2/models/dtos/hook_delta.py#L264-L286], replace `gvars: dict[str, object]` with `Annotated[dict[str, JsonValue], Field(default_factory=dict, description="Global context variables dictionary.")]` in `StepContextMetadataDTO`.</action>
    <action>In @[backend_v2/models/dtos/state.py#L16-L27, #L42-L51], replace mutable default `fields_to_translate: list[str] = []` with `Annotated[list[str], Field(default_factory=list, description="Targeted translation fields")]`, type `target_locale: Annotated[str, Field(description="Target locale code")]` in `HookStateMetadata`, and replace `translated_data: dict[str, Any]` with `Annotated[dict[str, JsonValue], Field(description="Fully translated dictionary.")]` in `TranslationResponseDTO`.</action>
    <action>In @[backend_v2/models/dtos/lightweight_matrix.py#L43-L57, #L76-L128], annotate `XAILogDto.engine_debug_trace` as `Annotated[dict[str, JsonValue], Field(default_factory=dict, description="System dictionary containing mathematical/diagnostic reasoning")]`, annotate `LightweightMatrixOutput.extensions` as `Annotated[dict[LaxXaiExtensionType, JsonValue], Field(default_factory=dict, description="Arbitrarily mapped XAI extensions dict for UI components")]`, tighten `atom_quotes` as `Annotated[list[str] | None, Field(default=None, description="Atom quotes list if provided")] = None`, and clean up duplicate `= Field(...)` trailing assignments on `evaluated_atoms` and `engine_debug_trace` using pure Python 3.14 Annotated syntax.</action>
    <action>In @[backend_v2/models/domain/synthesis.py#L96-L114, #L225-L251, #L254-L262], annotate `SynthesisMetadataDTO.global_context_vars` as `Annotated[GlobalContextVarsDTO | None, Field(default=None, description="Global context variables")] = None`, `execution_summary` as `Annotated[dict[str, JsonValue] | None, Field(default=None, description="Execution summary")] = None`, and `step_metrics` as `Annotated[dict[str, JsonValue] | None, Field(default=None, description="Step metrics")] = None` using pure Python 3.14 Annotated syntax.</action>
    <constraint invariant="cross_language_enum_parity">Guarantee 100% full-duplex DTO parity between Python backend and Flutter client.</constraint>
    <constraint invariant="no_naked_dicts_in_state">Eradicate naked dictionaries in state transit DTOs.</constraint>
  </step>

  <step id="8" name="LOCALE_AND_INTERNATIONALIZATION_SSOT_HARMONIZATION">
    <action>In @[backend_v2/models/enums.py#L488-L492], add `SV = "sv"` to `SystemLocale` enum.</action>
    <action>In @[client_app_v2/lib/core/models/enums.dart#L380-L389], add `@JsonValue('sv') sv` to `SystemLocale` enum.</action>
    <action>In @[client_app_v2/lib/l10n/app_en.arb#L1418-L1425] and @[client_app_v2/lib/l10n/app_fi.arb#L916-L922], add `"profileLanguageSv": "Swedish (sv)"` and `"profileLanguageSv": "Ruotsi (sv)"`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart#L199-L208], add `SystemLocale.sv => l10n.profileLanguageSv` to the exhaustive `switch (locale)` expression.</action>
    <action>Run client localization generation: `cd client_app_v2; flutter gen-l10n`.</action>
    <action>In @[backend_v2/models/auth.py#L176-L215, #L384-L403], replace `Literal["fi", "en", "sv"]` with `Annotated[SystemLocale, Field(description="Preferred UI language")]` in `UserBase`, and type `UserUpdate.language` as `SystemLocale | None = None`.</action>
    <action>In @[backend_v2/services/sdui/adapters/printable_sources_adapter.py#L106-L343], eradicate `if context.locale in ("fi", "en"): locale = context.locale` and assign `locale = context.locale` directly (without lazy `or` operators).</action>
    <action>In @[backend_v2/hooks/input_processing.py#L88-L129], update `_process_questionnaire` signature to `_process_questionnaire(raw_val: Any, key: str, expected_input: ExpectedInput, target_locale: str)` and resolve title sequentially (attempting `expected_input.label.resolve(target_locale)`, then `expected_input.label.resolve(SystemLocale.EN.value)`, then fallback to `key`) using explicit `if not title_text:` checks without QGR016 chained `or` operators, eliminating the mandatory English configuration crash.</action>
    <action>In @[backend_v2/hooks/input_processing.py#L236-L421], pass `target_locale=language` into `_process_questionnaire`.</action>
    <action>In @[backend_v2/hooks/input_processing.py#L133-L203], bind default parameter `language: str = SystemLocale.EN.value` in `_process_chat_history`.</action>
    <action>In @[backend_v2/core/registry.py#L195-L211, #L335-L350, #L357-L372, #L379-L788], update default `target_locale: str = SystemLocale.EN.value` in `SchemaBuilderStrategy` and concrete subclasses.</action>
    <action>In @[backend_v2/database/repositories/knowledge.py#L50-L60], update default `language: str = SystemLocale.EN.value` in `add_banned_phrase`.</action>
    <action>In @[backend_v2/hooks/source_verification_hook.py#L117-L234], update fallback locale to `SystemLocale.EN.value`.</action>
    <constraint invariant="cross_language_mapping_mandate">Enforce dynamic locale resolution from execution state; eliminate hardcoded English-only lockouts.</constraint>
    <constraint invariant="cross_language_enum_parity">Enforce 1:1 parity for SystemLocale across Python and Flutter.</constraint>
  </step>

  <step id="9" name="UNIT_TEST_MODERNIZATION_AND_ISTQB_EXPANSION">
    <action>In @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384], modernize fixtures to pass typed DTO instances to `TraceEvent`.</action>
    <action>In @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384], add ISTQB negative boundary partition 1: `test_state_projector_invalid_payload_raises_validation_failed` asserting that feeding malformed event data raises `AppException(ErrorCodes.VALIDATION_FAILED)` instead of silently constructing via `model_construct()`.</action>
    <action>In @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384], add ISTQB negative boundary partition 2: `test_trace_event_untyped_arbitrary_object_raises_validation_error` asserting that passing unregistered objects to `TraceEvent.content` raises Pydantic `ValidationError`.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_context_router.py#L184-L195], align all test cases to pass `LightweightMatrixOutput` and add negative partition asserting `ConfigurationError` when non-`LightweightMatrixOutput` is provided.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L1807-L1883], update fixture to pass `GlobalContextVarsDTO(language="fi")`.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_input_processing.py#L191-L245, #L640-L651], add unit test verifying that `_process_questionnaire` successfully resolves Finnish and Swedish questionnaire titles without demanding an English label.</action>
    <constraint invariant="anti_happy_path_mandate">Mandate >=2 negative failure partitions per feature module.</constraint>
  </step>

  <step id="10" name="DETERMINISTIC_AST_AUDIT_VERIFICATION">
    <action>Run deterministic AST scan on touched files: `uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict` to verify 0 naked dicts and 0 reflection calls.</action>
    <action>Run deterministic AST scan on compressor: `uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --strict` to verify 0 violations.</action>
    <action>Run deterministic AST scan on target DTO files: `uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos/hook_delta.py backend_v2/models/dtos/state.py backend_v2/models/dtos/lightweight_matrix.py backend_v2/models/domain/synthesis.py --strict` to verify 0 violations.</action>
    <action>Run deterministic AST scan on orchestrator strategies, engines, and reducers: `uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/services/orchestrator/state_reducer.py --strict` to verify 0 violations.</action>
    <action>Run deterministic DTO parity audit: `uv run python scripts/audit_dto_parity.py` to mathematically verify 0 mismatches between backend and client.</action>
    <constraint invariant="zero_naked_dicts_and_permissive_typing">Enforce 100% mathematical zero violations across all 8 AST metrics.</constraint>
  </step>

  <step id="11" name="UNIVERSAL_QUALITY_GATE_COMPLETION">
    <action>Run localized audit loop on models: `uv run python scripts/backend_audit_loop.py backend_v2/models/state.py --test`.</action>
    <action>Run localized audit loop on enums and auth: `uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py --test` and `uv run python scripts/backend_audit_loop.py backend_v2/models/auth.py --test`.</action>
    <action>Run localized audit loop on input processing: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/input_processing.py --test`.</action>
    <action>Run localized audit loop on context router: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/context_router.py --test`.</action>
    <action>Run localized audit loop on dag executor: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test`.</action>
    <action>Run localized audit loop on llm strategy: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test`.</action>
    <action>Run localized audit loop on state reducer: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/state_reducer.py --test`.</action>
    <action>Run Flutter audit loop on modified models and views: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/distilled_evaluation.dart`, `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/models/enums.dart`, and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart`.</action>
    <action>Run isolated unit test suites: `uv run pytest backend_v2/tests/unit/models/test_state.py backend_v2/tests/unit/test_auth.py backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/test_state_reducer.py backend_v2/tests/unit/services/orchestrator/test_linguistics_state_reduction_regression.py backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py backend_v2/tests/unit/hooks/test_input_processing.py`.</action>
    <constraint invariant="zero_tolerance_audit_loop">Universal quality gate must pass 100% with clean Mypy, Ruff, and 90%+ test coverage.</constraint>
  </step>

  <step id="12" name="ATOMIC_CHECKPOINT_COMMITS">
    <action>Instruct atomic git commit for staged changes with Conventional Commits message: `refactor(orchestrator): enforce strict pydantic v2 type safety and dynamic locale ssot across pipeline state transit`.</action>
    <constraint invariant="atomic_checkpoint_mandate">Stage specifically and exhaustively touched files.</constraint>
  </step>
</execution_protocol>
```

---

## Architectural Falsification & Red-Team Analysis

### Attack Vector 1: `StateProjector.apply_delta()` Payload Desynchronization with `LightweightMatrixDTO`
- **Failure Scenario**: `MatrixReducer.reduce_matrix(exec_record)` produces a strongly typed `LightweightMatrixDTO` containing `reduced_atoms: list[ReducedAtomDTO]`. If `StateProjector.apply_delta()` blindly sets `self._snapshot[event.step_name] = event.content`, subsequent call to `_build_dto_list()` attempts to iterate over `items()` of `LightweightMatrixDTO` as if it were a dictionary, triggering `AttributeError: 'LightweightMatrixDTO' object has no attribute 'items'`.
- **Proof Anchor & Mitigation**: `apply_delta()` explicitly matches and unpacks `LightweightMatrixDTO` into a canonical `{block_id: payload}` mapping: `{"reduced_atoms": event.content.reduced_atoms, "evaluated_matrices": event.content.evaluated_matrices, "global_metrics": event.content.global_metrics, "raw_extensions": event.content.raw_extensions}`. Unit test `test_matrix_explanation_service.py` is modernized with typed `ReducedAtomDTO` instances, proving 100% fail-safe in-memory fold with zero `model_construct()` bypasses.

### Attack Vector 2: `TraceEventMetadataDTO` Pydantic `extra="forbid"` Strictness vs. Callers
- **Failure Scenario**: Legacy callers and test cases may pass unmapped dictionary keys to `TraceEvent(..., metadata={...})`. With `extra="forbid"`, any unregistered key immediately throws `ValidationError`.
- **Proof Anchor & Mitigation**: Production audit confirms all metadata consumers strictly require the 8 standardized fields (`latency_ms`, `chunk_size`, `context_char_length`, `prompt_contexts`, `generated_schema`, `is_context_update`, `mcp_audit_traces`, `estimated_token_count`). Callers passing `metadata={"is_context_update": True}` automatically coerce safely into `TraceEventMetadataDTO(is_context_update=True)`. Tests in `test_state_reducer.py` and `test_linguistics_state_reduction_regression.py` are synchronously updated to assert typed attribute access `assert evt.metadata.is_context_update is True`.

### Attack Vector 3: `ContextVariablesDTO` Unnested Dictionary Crash in `test_state.py`
- **Failure Scenario**: Running `test_state.py` currently crashes with 2 `ValidationError` failures because tests pass unnested dictionaries `{"organization_id": ...}` to `context_variables`, which enforces `extra="forbid"` on fields outside `variables`.
- **Proof Anchor & Mitigation**: Phase 1 cleanups immediately update @[backend_v2/tests/unit/models/test_state.py#L224-L234, #L275-L384] to pass `context_variables=ContextVariablesDTO(variables={...})`, establishing a clean 100% green test baseline before pipeline state transit modifications commence.

### Attack Vector 4: Cross-Domain Flutter `DistilledEvaluation` Freezed Code Generation Desynchronization
- **Failure Scenario**: Adding `String? status` to Dart Freezed model without synchronously regenerating `distilled_evaluation.freezed.dart` leaves the Flutter analyzer in a broken compilation state, and `audit_dto_parity.py` fails.
- **Proof Anchor & Mitigation**: Step 7 mandates running `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/distilled_evaluation.dart --build`, generating immutable Freezed models and proving 0 parity mismatches via `scripts/audit_dto_parity.py`.

### Attack Vector 5: Primitive Obsession AST Violation in `StateProjector._snapshot`
- **Failure Scenario**: Annotating `StateProjector._snapshot` as `dict[str, dict[str, StepPayloadValue]]` satisfies basic type checking, but immediately triggers a fatal AST `primitive_obsession_nested_dict` violation under `scripts/audit_dict_eradication.py` (Pattern 1 in `_find_nested_dict_subscript` bans all `dict[..., dict[...]]` annotations).
- **Proof Anchor & Mitigation**: Encapsulate the per-step folded state inside the authoritative SSOT DTO `StepOutputContentDTO` (`backend_v2/models/dtos/node_execution.py#L130-L143`), typing `_snapshot` strictly as `dict[str, StepOutputContentDTO]`. In `apply_delta()`, fold payloads cleanly into `StepOutputContentDTO(data={...})`. Deterministic AST scan `uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict` mathematically confirms 0 naked dict and 0 primitive obsession violations.

### Attack Vector 6: `StateProjector.apply_delta()` GDPR Tombstone Primitive Obsession Violation
- **Failure Scenario**: When processing a GDPR `tombstone` event, `apply_delta()` assigns `self._snapshot[event.step_name] = {"_redacted": True, "hash": redacted_hash}`. Under typed `_snapshot: dict[str, StepOutputContentDTO]`, assigning a raw dictionary creates a fatal type mismatch and fails AST Primitive Obsession validation.
- **Proof Anchor & Mitigation**: Wrap the tombstone payload directly into `StepOutputContentDTO(data={"_redacted": True, "hash": redacted_hash})`. This guarantees that every entry in `_snapshot` is strictly a `StepOutputContentDTO`, preserving 100% type uniformity across the reconstitution lifecycle.

### Attack Vector 7: `TraceEvent.content` Closed Union Serialization with `exclude_none=True` vs. Downstream Deserialization
- **Failure Scenario**: When persisting `TraceEvent` containing strongly typed DTOs (`StepPayloadValue`), calling `model_dump()` without `exclude_none=True` serializes `null` keys that cause validation crashes in downstream reader DTOs enforcing `extra="forbid"`.
- **Proof Anchor & Mitigation**: Per `full_duplex_serialization_parity_mandate`, all event serialization in `dag_executor.py` explicitly enforces `exclude_none=True`. In addition, `StateProjector` unpacks incoming typed DTO instances directly into `StepOutputContentDTO(data=...)` in memory without intermediate JSON serialization roundtrips, eliminating the double-serialization hazard entirely.

### Attack Vector 8: `DAGExecutor._emit_preflight_progress` Untyped Progress Trace Payload
- **Failure Scenario**: `DAGExecutor._emit_preflight_progress` constructs `TraceEvent(content={"message": message, "progress_pct": pct})` using a raw dictionary. When `TraceEvent.content` is typed to `StepPayloadValue`, raw dictionaries without structural wrapping violate typed domain transit and trigger AST naked dictionary warnings.
- **Proof Anchor & Mitigation**: Step 2 defines `ProgressTracePayloadDTO(BaseDTO)` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` containing `message: str` and `progress_pct: Annotated[int, Field(ge=0, le=100)]`, and adds it to `StepPayloadValue`. Step 5 updates `_emit_preflight_progress` to instantiate `ProgressTracePayloadDTO` directly, mathematically proving 100% typed transit across background progress events.

### Attack Vector 9: Hardcoded Language Tuple & English Label Lockout in International Workflows
- **Failure Scenario**: Workflows running under Finnish (`"fi"`) or Swedish (`"sv"`) crash fail-fast in `_process_questionnaire` because `expected_input.label.resolve("en")` returns empty string for inputs seeded only in the localized target language, raising `System Configuration Error: Missing mandatory English label for '{key}' questionnaire.`. In addition, `printable_sources_adapter.py` drops Swedish `"sv"` down to `"en"` due to hardcoded tuple `("fi", "en")`, and `auth.py` contains disconnected `Literal["fi", "en", "sv"]` breaking cross-domain enum contracts.
- **Proof Anchor & Mitigation**: Step 8 expands `SystemLocale` to include `SV = "sv"` synchronously in both Python and Flutter, binds `UserBase.language` to `SystemLocale`, dynamically passes runtime execution `language` from `state.global_context_vars` to `_process_questionnaire`, and resolves `I18nText` against `target_locale` with graceful fallback to `SystemLocale.EN.value` or the input key before raising errors. Unit test in @[backend_v2/tests/unit/hooks/test_input_processing.py#L191-L245, #L640-L651] proves 100% localized questionnaire parsing without English label lockout.

### Attack Vector 10: `TraceEventMetadataEnvelope` AST Exemption vs. Token Shield Ban Paradox
- **Failure Scenario**: Attempting to force `extra="forbid"` onto `TraceEventMetadataEnvelope` under a blanket interpretation of the token shield ban breaks `TraceEventMetadataEnvelope.model_validate(event.content)` across `execution_worker.py#L268`, `synthesis_reducers.py#L410`, and `blueprint.py#L406`, causing ISTQB partitions in `test_trace_envelope.py` to violently fail with `ValidationError: Extra inputs are not permitted` whenever reading trace events containing polymorphic SDUI block data alongside `_step_metadata`.
- **Proof Anchor & Mitigation**: Grounded AST audit confirms `test_ast_domain_security_guardrails.py#L81` explicitly whitelists `allowed_exceptions = {"TraceEventMetadataEnvelope"}` precisely because it operates as an envelope projection filter extracting `_step_metadata` from heterogeneous event payloads. The sovereign `extra="forbid"` invariant is strictly applied to the newly authored `TraceEventMetadataDTO` (governing `TraceEvent.metadata`), `ProgressTracePayloadDTO`, and `TraceEvent` itself.

### Attack Vector 11: `QGR016` Multi-Fallback Chain and Lazy Literal Fallback Hazard
- **Failure Scenario**: Resolving locale via `context.locale or SystemLocale.EN.value` or chaining questionnaire label resolution via `expected_input.label.resolve(target_locale) or expected_input.label.resolve(SystemLocale.EN.value) or key` triggers fatal `QGR016` AST guardrail violations (`Banned lazy literal fallback` and `Banned multi-fallback chain >= 3 alternatives`).
- **Proof Anchor & Mitigation**: Step 8 mandates direct attribute assignment `locale = context.locale` (guaranteed non-empty at ingress by `AdapterContext`) and sequential `if not title_text:` checks in `_process_questionnaire`. Running `uv run python scripts/audit_dict_eradication.py backend_v2/hooks/input_processing.py --strict` mathematically confirms 0 `QGR016` violations.

### Attack Vector 12: `ContextBuilder` Matrix Value Duck-Typing at LLM Prompt Generation
- **Failure Scenario**: `ContextBuilder._prune_context` checks `isinstance(value, (str, int, float, bool)) or value is None` and passes `value` to `ContextRouter.route_and_prune`. If `value` is an untyped dictionary rather than `LightweightMatrixOutput`, a strictly typed `route_and_prune(trace_event: LightweightMatrixOutput, ...)` signature raises a type mismatch.
- **Proof Anchor & Mitigation**: Step 4 updates `ContextBuilder` to validate `value` explicitly into `LightweightMatrixOutput` before dispatching to `route_and_prune`, guaranteeing 100% typed domain transit across prompt generation boundaries.

### Attack Vector 13: `SystemLocale.sv` Dart Exhaustive Switch Breakdown in `profile_general_tab.dart`
- **Failure Scenario**: Expanding `SystemLocale` in Dart with `@JsonValue('sv') sv` causes `client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart#L202-L205` to fail compilation because its `switch (locale)` expression only covers `SystemLocale.fi` and `SystemLocale.en`, failing the Flutter audit loop.
- **Proof Anchor & Mitigation**: Step 8 mandates adding `"profileLanguageSv"` to both `app_en.arb` and `app_fi.arb`, generating localizations via `cd client_app_v2; flutter gen-l10n`, and adding `SystemLocale.sv => l10n.profileLanguageSv` to the switch expression in `profile_general_tab.dart`, guaranteeing 100% exhaustive matching and zero Flutter compilation errors.

### Attack Vector 14: `TraceMatrixPayloadDTO.atom_quotes` Loose `list[Any]` Serialization Hazard
- **Failure Scenario**: If `TraceMatrixPayloadDTO.atom_quotes` is typed as `list[Any] | None`, untyped objects or complex mappings can be serialized into trace events, bypassing forensic quote string validation and re-introducing loose data into downstream presentation layers.
- **Proof Anchor & Mitigation**: Step 2 explicitly tightens `TraceMatrixPayloadDTO.atom_quotes` to `Annotated[list[str] | None, Field(default=None, description="Optional accumulated atom quotes from matrix evaluation")] = None` using pure Python 3.14 Annotated syntax. Deterministic AST scan confirms 0 loose type annotations.

### Attack Vector 15: Markdown AST Boundary Mismatch & Automated Gate Failure Hazard
- **Failure Scenario**: Markdown implementation plans referencing Python codebase entities with speculative line bounds (`#L157-L208`, `#L480-L613`, `#L181-L385`, `#L488-L493`, `#L179-L201`) or non-ClassDef/FunctionDef module spans fail deterministic AST boundary validation under `scripts/audit_markdown_boundaries.py` with fatal MBD004 findings, blocking automated CI/CD and pre-flight execution gates.
- **Proof Anchor & Mitigation**: All Python line bounds in the plan are anchored to exact AST node spans verified via `ast.walk()`: `TraceEvent` span `(157, 207)`, `StateProjector` span `(480, 612)`, `StateProjector.apply_delta` span `(591, 612)`, `_clean_and_distill_payload` span `(181, 384)`, `SystemLocale` span `(488, 492)`, `TraceMatrixPayloadDTO` span `(179, 200)`. Module-level namespace statements (`_state_localns`) are referenced at file scope without speculative line tags. Deterministic gate `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Pipeline_State_Transit_Type_Safety.md` passes with 0 findings.

---

## Architectural Safeguards & Verification Plan

### Automated Test Gates
1. **Localized Unit Tests**:
   ```powershell
   uv run pytest backend_v2/tests/unit/models/test_state.py backend_v2/tests/unit/test_auth.py backend_v2/tests/unit/hooks/test_input_processing.py backend_v2/tests/unit/services/orchestrator/test_context_router.py backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/test_state_reducer.py backend_v2/tests/unit/services/orchestrator/test_linguistics_state_reduction_regression.py backend_v2/tests/unit/services/orchestrator/test_matrix_explanation_service.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py -v
   ```
2. **Deterministic AST Dict Eradication Gate**:
   ```powershell
   uv run python scripts/audit_dict_eradication.py backend_v2/models/state.py --strict
   uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/synthesis_payload_compressor.py --strict
   uv run python scripts/audit_dict_eradication.py backend_v2/models/dtos/hook_delta.py backend_v2/models/dtos/state.py backend_v2/models/dtos/lightweight_matrix.py backend_v2/models/domain/synthesis.py --strict
   uv run python scripts/audit_dict_eradication.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/services/orchestrator/engines/synthesis_engine.py backend_v2/services/orchestrator/state_reducer.py --strict
   ```
3. **Deterministic DTO Parity Verification Gate**:
   ```powershell
   uv run python scripts/audit_dto_parity.py
   ```
4. **Flutter Code Generation & Audit Gate**:
   ```powershell
   cd client_app_v2; flutter gen-l10n; cd ..
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/distilled_evaluation.dart --build
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart
   ```
5. **Backend Audit Loops**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/models/state.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/context_router.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/state_reducer.py --test
   ```
6. **Final Integration REST API Gate (Offline Mocked)**:
   ```powershell
   uv run pytest backend_v2/tests/integration/test_pipeline_state_transit.py -v
   ```

---

## Architectural Handover & Backlog Horizon: Pre- vs. Post-PostgreSQL Migration

This section defines the mathematical division of labor and architectural boundary between this implementation plan and the upcoming PostgreSQL 17+ migration plan (@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]).

### 1. State and Value Delivered by this Plan (What We Have)
- **100% Typed In-Memory State Transit**: State passing through the execution pipeline (`DAGExecutor`, `StateProjector`, `ContextRouter`, `LLM Strategy`, `StateReducer`, `SynthesisEngine`) contains zero naked dictionaries (`dict[str, Any]` or `dict[str, object]`).
- **TraceEvent and Metadata Contracts**: `TraceEvent.content` is a type-safe closed union, `TraceEvent.metadata` is strictly validated `TraceEventMetadataDTO(extra="forbid")`, and `StateProjector._snapshot` is typed `dict[str, StepOutputContentDTO]` (cleanly resolving GDPR tombstone handling without *Primitive Obsession* violations).
- **Complete Eradication of Double-Serialization**: Pydantic models do not perform redundant back-and-forth `.model_dump()` dictionary conversions during in-memory pipeline execution.
- **Fail-Fast RFC 7807 Error Boundaries**: `StateProjector._build_dto_list()` eliminates `.model_construct()` workarounds and immediately raises structured `AppException(ErrorCodes.VALIDATION_FAILED)`.
- **1:1 Full-Duplex DTO Parity**: Backend `DistilledEvaluation` and Flutter Freezed model `distilled_evaluation.dart` are 100% identical (including the `status` field).

### 2. Benefits in Development with AI Pair (Antigravity / LLM)
- **Elimination of Hallucinated Fields and Keys**: When state is governed by strongly typed Pydantic V2 DTO models (`extra="forbid"`), the AI cannot hallucinate or guess field names from context: an invalid field name crashes execution immediately in local type checking.
- **Deterministic AST and Linter Gates**: Deterministic audit tools (`audit_dict_eradication.py` and `backend_audit_loop.py`) provide mathematical proof (0 violations) in fractions of a second, eliminating human guesswork and preventing *Agentic Drift*.
- **Refactoring Immunity**: When matrices, prompt compilers, or SDUI structures are refactored, MyPy and Pydantic expose type errors directly during static analysis without risk of random runtime `KeyError` crashes in production.
- **Closing the "Path of Least Resistance" Trap**: Banned shortcuts (specifically shoving ad-hoc dictionaries into execution traces to pass tests) are mathematically prevented at compile time.

### 3. The Tripartite Roadmap and Dependencies
This plan serves as the first and most critical step in achieving comprehensive type safety across Quorum:
1. **Phase 1: In-Memory Execution Pipeline State Transit (THIS PLAN)**:
   - Hardens the execution pipeline (`DAGExecutor`, `StateProjector`, `ContextRouter`, `SynthesisEngine`) and eradicates all state transit dictionaries.
   - Produces clean DTO models (`TraceEventMetadataDTO`, `StepOutputContentDTO`, `ExecutionInputsDTO`) leveraged by subsequent phases.
2. **Phase 2: Persistence Layer & All-in-PostgreSQL 17+ (@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md])**:
   - **Dependency**: Requires completion of Phase 1 as its foundation.
   - **Phase 1.5 (Pre-Flight)**: Cleans up persisted domain models (`system_config.py`, `xai.py`, `mcp.py`, `atom_evaluation.py`).
   - **Phase 2+**: Replaces the deprecated `TinyDBDriver` and `db_v2.json` file with SQLAlchemy 2.0 ORM, `PydanticJSONB` wrappers, and row-level locking (`SELECT ... FOR UPDATE`).
   - Resolves the 13 `QGR003` repository exceptions and standardizes RFC 7807 error formatting in `exceptions.py`.
3. **Phase 3: LLM Adapters & Peripheral Boundaries (@[docs/implementationplans/IMPLEMENTATION_PLAN_LLM_Adapter_Strict_Typing.md])**:
   - **Dependency**: Executed following Phase 1 and Phase 2.
   - Cleans up the external AI SDK adapter layer (`backend_v2/llm/adapters/`) and peripheral hooks (`hooks/`, `registry.py`).
   - Achieves a mathematical state of exactly 0 violations across the entire `backend_v2` scope (`audit_dict_eradication.py`).
