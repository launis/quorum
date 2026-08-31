<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# Phase 3B: Orchestrator Subsystem Suppression & Duck-Typing Eradication

## Overview

Eradicate all `# noqa: QGR` suppressions, `dict[str, Any]` annotations, and `isinstance(..., dict)` checks across 19 files in the Orchestrator subsystem (`backend_v2/services/orchestrator/`). Implement category pre-filtering and Discriminated Union validation for polymorphic DAG states (`synthesis_payload_compressor.py`, `strategies/llm.py`, `dag_executor.py`), and eliminate unhandled Pydantic validation bubbles.

## Target Files

- `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py#L307-L949]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L288]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompt_compiler.py#L36-L463]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L17-L206]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/context_router.py#L53-L220]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm.py#L66-L894]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/base.py#L89-L376]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py#L25-L203]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L20-L400]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L138]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L49-L228]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L27-L181]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/two_pass_atomizer.py#L33-L486]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_distiller.py#L175-L367]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L239]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/rag_preflight_service.py#L79-L230]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/localization_compiler.py#L34-L243]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/anchor_validation_service.py#L19-L401]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L235]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L224]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 3: Hooks, Orchestrator & Repository Suppression Eradication]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
      <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
      <backend>@[backend_v2/services/orchestrator/prompt_compiler.py]</backend>
      <backend>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]</backend>
      <backend>@[backend_v2/services/orchestrator/context_router.py]</backend>
      <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]</backend>
      <backend>@[backend_v2/services/orchestrator/enriched_dag_executor.py]</backend>
      <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py]</backend>
      <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
      <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
      <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py]</backend>
      <backend>@[backend_v2/services/orchestrator/localization_compiler.py]</backend>
      <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py]</backend>
      <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="OrchestratorPolymorphicPayloadHandling">
      # Heterogeneous DAG states validated strictly via Discriminated Unions or Category Pre-filtering
      # Zero isinstance(data, dict) checks
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/database/repositories/]</file>
    <file>@[backend_v2/models/domain/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero # noqa: QGR suppressions across all 19 orchestrator files</item>
    <item>Zero isinstance(..., dict) duck-typing checks in orchestrator</item>
    <item>SynthesisPayloadCompressor and DAGExecutor handle polymorphic payloads without naked dicts</item>
    <item>AST guardrails pass 100% clean on backend_v2/services/orchestrator/ in --strict mode</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK & PRE-IMPLEMENTATION CLEANUPS">
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L365], fix Starlette deprecation `HTTP_413_REQUEST_ENTITY_TOO_LARGE` by replacing with `HTTP_413_CONTENT_TOO_LARGE` or numeric 413.</action>
    <action>In @[backend_v2/services/orchestrator/context_router.py#L23-L31], eradicate `model_config = ConfigDict(strict=True, extra="ignore")` and `# noqa: QGR007` on `RoutingModeConfig` by explicitly defining all supported routing fields with `extra="forbid"`.</action>
    <action>In @[backend_v2/services/orchestrator/two_pass_atomizer.py#L482], replace broad `except Exception:` with specific `except (ValidationError, AppException, OSError):` re-raising or wrapping in DLQ response without blanket suppression.</action>
    <action>In @[backend_v2/services/orchestrator/enriched_dag_executor.py#L172], replace blanket `except Exception:` with `except (OSError, AppException):` during cache teardown.</action>
  </step>

  <step id="1" name="HARDEN ORCHESTRATOR EXECUTORS & COMPILERS">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L307-L949], eliminate 8 `dict[str, Any]` annotations, 2 QGR003, and 3 QGR012 suppressions by binding state variables to strict Pydantic DTOs (`StateProjector`, `StepOutputDTO`, `TraceEvent`).</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L288], eliminate 6 `dict[str, Any]` annotations and all QGR012 duck-typing checks via TypeAdapter-based polymorphic payload validation (`TypeAdapter(list[DistilledEvaluation] | DistilledEvaluation | dict[str, Any])`) and direct attribute access.</action>
    <action>In @[backend_v2/services/orchestrator/prompt_compiler.py#L36-L463] and @[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L17-L206], eliminate `dict[str, Any]` and QGR012 duck-typing in path traversal by using typed structural inspection.</action>
    <action>In @[backend_v2/services/orchestrator/context_router.py#L53-L220] and @[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154], eliminate QGR012 duck-typing in trace reduction and pruning via `TraceEvent` and `LightweightMatrixOutput` models.</action>
  </step>

  <step id="2" name="HARDEN STRATEGIES & PIPELINE SERVICES">
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L66-L894], eliminate 9 `dict[str, Any]` annotations, 2 QGR003, and 19 QGR012 suppressions using direct DTO access on `ExecutionInputsDTO`, `GlobalContextVarsDTO`, and guarded TypeAdapter hydration.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/base.py#L89-L376], @[backend_v2/services/orchestrator/strategies/logic.py#L25-L203], @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L20-L400], and @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L49-L228], eliminate `dict[str, Any]` annotations and duck-typing checks.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L138], eliminate 7 QGR012 suppressions by hydrating context data via `ExecutionInputsDTO` and `ExecutionMetadata`.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_distiller.py#L175-L367], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L239], @[backend_v2/services/orchestrator/rag_preflight_service.py#L79-L230], @[backend_v2/services/orchestrator/localization_compiler.py#L34-L243], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147], @[backend_v2/services/orchestrator/anchor_validation_service.py#L19-L401], @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L235], and @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L224], eliminate all remaining QGR suppressions and duck-typing.</action>
  </step>

  <step id="3" name="COMPREHENSIVE TEST EXPANSION & AST GUARDRAIL VALIDATION">
    <action>Expand unit tests across orchestrator services to satisfy ISTQB equivalence partitioning and boundary value testing.</action>
    <action>Verify zero AST violations in strict mode across the entire orchestrator subsystem.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_dag_executor_handles_discriminated_union_outputs">
      <input>DAG step emitting polymorphic atom result payload</input>
      <expected>validates and processes without dictionary coercion or KeyError</expected>
      <category>positive</category>
    </contract>
    <contract id="2" name="test_synthesis_compressor_category_prefiltering">
      <input>Synthesis payload containing mixed MATRIX and EXTRACTION step outputs</input>
      <expected>compresses and strata-sorts cleanly based on category_id without isinstance(dict)</expected>
      <category>positive</category>
    </contract>
    <contract id="3" name="test_synthesis_compressor_empty_or_malformed_fail_fast">
      <input>Synthesis payload containing empty payload or invalid non-model dict</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED (400) immediately</expected>
      <category>negative</category>
    </contract>
    <contract id="4" name="test_context_router_missing_base_fields_fail_fast">
      <input>Context trace payload missing mandatory evaluated_atoms</input>
      <expected>raises ConfigurationError with ErrorCodes.VALIDATION_FAILED immediately</expected>
      <category>negative</category>
    </contract>
    <contract id="5" name="test_execution_time_resolver_malformed_input_fallback_safety">
      <input>Context data with unparseable string timestamp or malformed structure</input>
      <expected>handles graceful resolution without crashing or returning invalid date object</expected>
      <category>boundary</category>
    </contract>
    <contract id="6" name="test_matrix_explanation_service_invalid_dto_payload_skipping">
      <input>Available StepOutputDTO containing non-dictionary payload</input>
      <expected>safely ignores invalid payload and logs warning without pipeline crash</expected>
      <category>negative</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail scan and backend audit loop on Orchestrator subsystem:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test</command>
  </validation_gate>
</execution_protocol>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`DAGExecutor`** (`@[backend_v2/services/orchestrator/dag_executor.py#L307-L949]`) | Banned `dict[str, Any]` in state signatures, `dict.get()`, and `# noqa: QGR003` silent exception swallowing. | Enforce 100% strongly typed DTO transit (`StateProjector`, `StepOutputDTO`, `TraceEvent`), structured `AppException(ErrorCodes.PROGRESS_UPDATE_FAILED)` dual-reporting. | Prune manual dict cloning; leverage Pydantic V2 `.model_dump(mode="json")` at DB boundaries. | `uv run pytest backend_v2/tests/unit/test_dag_taskgroup.py` and AST `--strict` gate. |
| **`SynthesisPayloadCompressor`** (`@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L288]`) | Banned `isinstance(..., (dict, list))` duck-typing, `# noqa: QGR012`, and manual dict pop loops. | Enforce TypeAdapter validation on incoming polymorphic payloads (`TypeAdapter(list[DistilledEvaluation] \| DistilledEvaluation \| str \| int \| float \| bool)`), strict `DistilledEvaluation` schema model validation, and Fail-Fast on empty compressed results (`ErrorCodes.VALIDATION_FAILED`). | Prune redundant deep copies; use immutable projections and direct field extraction. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py`. |
| **`PromptCompiler` & `Adapter`** (`@[backend_v2/services/orchestrator/prompt_compiler.py#L36-L463]`, `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L17-L206]`) | Banned recursive dictionary inspection (`isinstance(v, dict)` with `# noqa: QGR012`) for dot-notation state path traversal. | Enforce strictly typed path extraction via `resolve_dot_notation()` utility, Pydantic V2 model validation, and structured XML encapsulation via `TemplateProcessor`. | Prune duplicate custom string formatters; rely on centralized `TemplateProcessor.encapsulate_payload()`. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_schema_healing_prompt.py`. |
| **`ContextRouter`** (`@[backend_v2/services/orchestrator/context_router.py#L53-L220]`) | Banned `model_config = ConfigDict(strict=True, extra="ignore")` with `# noqa: QGR007` on `RoutingModeConfig`, and duck-typing `isinstance(dict)` with `# noqa: QGR012`. | Enforce `extra="forbid"` on `RoutingModeConfig`, and direct `LightweightMatrixOutput.model_validate(trace_event)` hydration with Fail-Fast `ConfigurationError` on missing `evaluated_atoms`. | Prune loose `SnapshotState` dictionaries; enforce strongly typed `ExecutionRecord` / `TraceEvent` envelopes. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py`. |
| **`MatrixReducer`** (`@[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154]`) | Banned nested `isinstance(val, dict)` inspection with `# noqa: QGR012` to extract XAI extensions from `execution_trace`. | Enforce direct DTO iteration over `record.execution_trace` extracting `TraceEvent.content` and validating typed `LightweightMatrixDTO`. | Prune nested ad-hoc dictionary loops; extract extensions via typed trace event filtering. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py`. |
| **`LLMNodeStrategy`** (`@[backend_v2/services/orchestrator/strategies/llm.py#L66-L894]`) | Banned 19 `isinstance(dict)` checks with `# noqa: QGR012`, `hook_state.inputs.get()`, and `dict[str, Any]` unpacking. | Enforce direct dot-notation on `ExecutionInputsDTO` (`inputs.dynamic_inputs`, `inputs.raw_inputs`), `GlobalContextVarsDTO`, and guarded `TypeAdapter` hydration. | Prune manual dict wrapper unpacking; pass `HookState` and `StrategyContext` directly to execution engines. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py`. |
| **`ExecutionTimeResolver`** (`@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L138]`) | Banned 7 `# noqa: QGR012` duck-typing checks on `llm_context_data` nested dictionaries. | Enforce typed parameter resolution via `ExecutionInputsDTO`, `ExecutionMetadata`, and timezone-aware `datetime.now(datetime.UTC)` parsing without raw dictionary traversal. | Prune multi-level nested `.get()` fallbacks; resolve timestamps deterministically from typed metadata. | `uv run pytest backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_execution_time_resolver.py`. |
| **`MatrixExplanationService`** (`@[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L239]`) | Banned 5 `# noqa: QGR012` duck-typing checks on `dto.payload` and `atom_dict`. | Enforce `TypeAdapter(list[AtomResultDTO] \| AtomResultDTO)` parsing on `StepOutputDTO.payload`, direct `LightweightMatrixOutput` validation, and RFC-7807 logging on invalid schemas. | Prune duplicate quote extraction loops; use `ranked_round_robin_select` directly on typed atom results. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py`. |
| **`LocalizationCompiler` & `ExtractionSchemaFactory`** (`@[backend_v2/services/orchestrator/localization_compiler.py#L34-L243]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147]`) | Banned `# noqa: QGR012` duck-typing in `resolve_i18n()` and `canonicalise_nulls()`. | Enforce `I18nText.model_validate(text_obj)` with Fail-Fast `ConfigurationError`, and typed `@field_validator` on dynamically generated extraction models (`ConfigDict(strict=True, extra="forbid", frozen=True)`). | Prune ad-hoc dictionary mutations; use Pydantic `ValidationInfo.context` for source text length checks. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_extraction_schema_factory.py`. |
| **`TwoPassAtomizer` & `EnrichedDagExecutor`** (`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L33-L486]`, `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L27-L181]`) | Banned `# noqa: QGR003` silent `except Exception:` swallows during DLQ return and cache teardown. | Enforce specific exception handlers `except (ValidationError, AppException, OSError):` with structured `logger.error` logging, and bubble up transient network errors for Arq retry. | Prune redundant try/except wrappers around `LLMCachingService.teardown_workflow_caches`. | `uv run pytest backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py`. |

