# Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)

**Phase Title:** Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)
**Objective:** Eliminate ALL `isinstance(..., dict)`, `getattr()`, `hasattr()`, and `.get()` branches from the orchestration engine, strategy dispatchers, prompt compilers, and evaluation engines, updating state transitions to use strictly typed dot-notation and immutable `model_copy(update={...})` within `async with _update_lock:`, and modernizing orchestrator unit tests atomically.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L259-L286] (Phase 4: Orchestration & Strategy Core Refactoring & Tests)

**Target Files** (exhaustive — 19 production files + test suites):
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py] (1x isinstance, 1x getattr, 1x hasattr)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py] (6x isinstance, 2x getattr, model_dump -> dict)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py] (2x isinstance + dict.pop chains)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py] (8x isinstance, 10x getattr, 2x .get)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py] (4x isinstance nested, .get chains)
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler.py] (4x isinstance + model_dump -> dict traversal)
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler_adapter.py] (1x getattr delegation)
- `[MODIFY]` @[backend_v2/services/orchestrator/context_router.py] (2x isinstance, 1x getattr, model_config missing)
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] (3x isinstance, .get chains)
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py] (2x isinstance, 1x .get)
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py] (6x isinstance — heavy)
- `[MODIFY]` @[backend_v2/services/orchestrator/rag_preflight_service.py] (2x isinstance, .get chains)
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py] (1x isinstance)
- `[MODIFY]` @[backend_v2/services/orchestrator/extraction_schema_factory.py] (model_dump -> dict, isinstance)
- `[MODIFY]` @[backend_v2/services/orchestrator/atomizer.py] (model_dump optimizations)
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py] (model_dump | dict union, isinstance)
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_reducer.py] (2x isinstance + dict nesting)
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py] (1x isinstance, 1x .get)
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py] (model_dump -> dict + dict mutation, 3x .get)
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-FLIGHT VERIFICATION">
    <action>Look backward: Verify codebase state left by Phase 3B. Verify hooks emit strictly typed HookDeltaDTO and consume HookState(inputs: ExecutionInputsDTO, global_context_vars: GlobalContextVarsDTO).</action>
    <action>Look forward: Verify orchestrator consumers against AST Guardrails report (QGR001 reflection, QGR002 .get(), QGR007 ConfigDict) in @[backend_v2/services/orchestrator/].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document (@[docs/epic/EPIC_149_tracker.md]), and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] All `isinstance(..., dict)`, `getattr()`, `hasattr()`, and `.get()` branches eliminated across all 19 orchestrator and strategy files.
    - [ ] `StrategyContext` and `ExecutionMetadata` accessed via direct typed dot-notation with `ConfigDict(strict=True, extra='forbid')`.
    - [ ] `run_pre_hooks` and `run_post_hooks` in `base.py` consume typed `HookDeltaDTO` (`delta.delta`, `delta.metadata_updates`) without `.pop("metadata")` dict hacks.
    - [ ] `ContextBuilder` and `ContextRouter` operate on typed `StepOutputDTO`, `LightweightMatrixOutput`, and `OutputProfileConfig` without reflection `getattr()`.
    - [ ] `TDAEngine` and `SynthesisEngine` pass typed `ErrorCodes` members to `AppException` and access context variables via strict types or fail-fast keys.
    - [ ] State transitions in `DAGExecutor` execute inside `async with _update_lock:` using `.model_copy(update=...)` strictly with typed instances.
    - [ ] Orchestrator unit tests in @[backend_v2/tests/unit/services/orchestrator/] modernized with polyfactory and typed model fixtures.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.
    - [ ] AST Guardrails pass: `uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict`.
    - [ ] Semantic Parity Gate passes: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]</backend>
    <backend>@[backend_v2/services/orchestrator/context_router.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py]</backend>
    <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py]</backend>
    <backend>@[backend_v2/services/orchestrator/atomizer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <test>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py]</test>
    <test>@[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]</test>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/services/execution.py` in Phase 4 (reserved strictly for Phase 5).
    - Do NOT modify `backend_v2/services/usage_service.py` in Phase 4 (reserved for Phase 5).
    - Do NOT re-introduce loose `dict` handling in DAG execution steps or hook invocation interfaces.
  </anti_targets>

  <step id="1" name="STRATEGY BASE &amp; HOOK INTEGRATION MODERNIZATION">
    <action>Refactor @[backend_v2/services/orchestrator/strategies/base.py]:
      1. Enforce `model_config = ConfigDict(strict=True, extra='forbid')` on `StrategyContext`.
      2. Modernize `run_pre_hooks` and `run_post_hooks` to consume typed `HookDeltaDTO` (`res.state_delta`).
      3. Access `res.state_delta.metadata_updates` and `res.state_delta.delta` directly without `delta.pop("metadata")` or `isinstance(..., dict)` fallbacks.
      4. Access `context.metadata.target_locale` and `context.global_context_vars` via strict dot-notation.</action>
    <constraint invariant="zero_service_layer_fallbacks">No `.get()` or `getattr()` on StrategyContext or HookDeltaDTO.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">Pre/post-hook execution failures logged with structured context before raising.</constraint>
  </step>

  <step id="2" name="LLM EXECUTION &amp; CONTEXT BUILDER REFAC">
    <action>Refactor @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py] and @[backend_v2/services/orchestrator/strategies/llm.py]:
      1. In `ContextBuilder`: replace `getattr(dto, "block_id", None)` and `getattr(dto, "payload", None)` with direct typed attribute access on `StepOutputDTO` (`dto.block_id`, `dto.payload`, `dto.step_id`).
      2. In `ContextBuilder._collect_rule_descriptions`: replace `getattr()` calls with direct model properties (`block.ai_description`, `block.scales`, `scale.claims`, `claim.tda_assertions`).
      3. In `ContextBuilder.apply_spatial_slicing` &amp; path resolution: replace `.get("steps")` with direct dictionary indexing or validated `StateProjector.snapshot` filtering.
      4. In `LLMNodeStrategy`: replace `inputs_payload.get("inputs")` and `hook_state.global_context_vars.get()` with direct keys or typed `GlobalContextVarsDTO` access.
      5. In `LLMNodeStrategy`: replace `getattr(step, "expected_sdui_type", "grid")` with `step.expected_sdui_type or "grid"`.
      6. In `ExecutionTimeResolver`: eliminate recursive `.get()` chains on `raw_inputs` and `dynamic_inputs`; use direct typed fields on `WorkflowInputs` / `ExecutionInputsDTO`.</action>
    <constraint invariant="strict_attribute_integrity">Never convert strict dot-notation attribute access into dynamic getattr() fallbacks.</constraint>
    <constraint invariant="the_duct_tape_ban">Eliminate all `isinstance(..., dict)` branches and `.get()` fallback chains.</constraint>
  </step>

  <step id="3" name="PROMPT COMPILER, ADAPTER &amp; CONTEXT ROUTER REFACTORING">
    <action>Refactor @[backend_v2/services/orchestrator/prompt_compiler.py], @[backend_v2/services/orchestrator/prompt_compiler_adapter.py], and @[backend_v2/services/orchestrator/context_router.py]:
      1. In `PromptCompiler`: replace `model_dump()` to dict traversals in `build_xml_context` with typed `I18nText` model access (`ei.label.resolve(target_locale)`).
      2. In `PromptCompilerAdapter`: wrap delegate calls explicitly rather than bare `__getattr__` reflection that violates QGR001.
      3. In `ContextRouter`: add `model_config = ConfigDict(strict=True, extra='forbid')` to `RoutingModeConfig` and `SnapshotState`.
      4. In `ContextRouter`: replace `getattr(dto, "step_id", None)` with typed `dto.step_id`.</action>
    <constraint invariant="xml_structural_sovereignty_mandate">Maintain strict XML tag generation just-in-time via PromptCompiler.</constraint>
    <constraint invariant="strict_pydantic_v2_rust">Enforce ConfigDict(strict=True, extra='forbid') on all context models.</constraint>
  </step>

  <step id="4" name="SYNTHESIS &amp; EVALUATION ENGINES REFAC">
    <action>Refactor @[backend_v2/services/orchestrator/engines/tda_engine.py], @[backend_v2/services/orchestrator/engines/synthesis_engine.py], @[backend_v2/services/orchestrator/matrix_explanation_service.py], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py], @[backend_v2/services/orchestrator/synthesis_distiller.py], @[backend_v2/services/orchestrator/matrix_reducer.py], and @[backend_v2/services/orchestrator/anchor_validation_service.py]:
      1. In `TDAEngine` and `SynthesisEngine`: update `AppException` calls to pass typed `ErrorCodes.VALIDATION_FAILED` or `ErrorCodes.CONFIGURATION_ERROR` enum members (satisfying QGR009).
      2. In `TDAEngine`: eliminate `.get()` on blackboard; use typed `GlobalAtomBlackboard.is_data_starved`.
      3. In `SynthesisEngine`: replace `raw_blackboard = request.context.context_variables.get("__GLOBAL_ATOM_BLACKBOARD__")` with direct lookup and `model_validate()`.
      4. In `SynthesisPayloadCompressor`: eliminate `isinstance(..., dict)` checks; accept typed `StepOutputDTO` payload models and sanitize through Pydantic V2 `DistilledEvaluation`.
      5. In `SynthesisDistiller`: replace `uid_to_alias.get(uid, uid)` with direct lookup `uid_to_alias[uid]`.
      6. In `MatrixExplanationService`: replace polymorphic `isinstance` branches with typed `AtomResultDTO` validation.
      7. In `MatrixReducer`: iterate directly over typed `ReducedAtomDTO` and `QuoteEvidenceDTO` without raw dictionary nesting.
      8. In `AnchorValidationService`: eliminate dictionary merges with `model_dump() | {...}`; use typed `model_copy(update={...})`.</action>
    <constraint invariant="pydantic_mutation_optimization_mandate">Use model_copy(update=...) instead of model_dump() serialization cycles.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">AppException instantiated with typed ErrorCodes enum members.</constraint>
  </step>

  <step id="5" name="DAG EXECUTOR &amp; REASONING ORCHESTRATION REFACTORING">
    <action>Refactor @[backend_v2/services/orchestrator/dag_executor.py], @[backend_v2/services/orchestrator/rag_preflight_service.py], @[backend_v2/services/orchestrator/localization_compiler.py], @[backend_v2/services/orchestrator/extraction_schema_factory.py], and @[backend_v2/services/orchestrator/atomizer.py]:
      1. In `DAGExecutor._resolve_execution_engine`: eliminate `getattr(b, "is_synthesis", False)` by checking typed `PromptBlockCategory` and domain properties on `PromptBlock`.
      2. In `DAGExecutor` exception handler: replace `hasattr(e, "details")` and `e.details.get("error_code")` with typed `isinstance(e, AppException)` and `e.error_code`.
      3. In `DAGExecutor`: ensure all state mutations execute inside `async with _update_lock:` using `.model_copy(update=...)` with typed instances.
      4. In `RAGPreflightService`: eliminate `.get("inputs")` by extracting dynamic inputs from typed `ExecutionInputsDTO` / `WorkflowInputs`.
      5. In `ExtractionSchemaFactory`: eliminate `isinstance(data, dict)` in `canonicalise_nulls` validators by using strict model validation.</action>
    <constraint invariant="frozen_state_mutability">State transitions in DAGExecutor execute inside async with _update_lock: using .model_copy(update=...) with typed instances.</constraint>
    <constraint invariant="orchestrator_god_object_fragility">Full blast-radius evaluation and verification across topological flow.</constraint>
  </step>

  <step id="6" name="ATOMIC TEST SUITE MODERNIZATION &amp; QUALITY GATES">
    <action>Modernize all orchestrator and strategy test suites under @[backend_v2/tests/unit/services/orchestrator/]:
      1. Modernize @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]: replace raw dict mocks with typed `Workflow`, `Step`, `StepRule`, and `ExecutionMetadata` fixtures.
      2. Modernize @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]: replace legacy dictionary fixtures with `polyfactory` and typed `StrategyContext` models.
      3. Modernize @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]: test typed hook execution with `HookDeltaDTO`.
      4. Modernize @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]: verify typed `StepOutputDTO` pruning across 4 ISTQB partitions.
      5. Modernize @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py] and `test_synthesis_engine.py`: test typed execution with mock LLM outputs.
      6. Run AST Guardrail audit: `uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict`.
      7. Run Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.
      8. Run SDUI Semantic Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Execute full audit loop and all 43 orchestrator test files before completion.</constraint>
    <constraint invariant="anti_happy_path_mandate">Each test file must cover at least 2 negative partitions (missing required fields, validation error, AppException).</constraint>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test
    uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict
    uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
  </validation_gate>
</execution_protocol>
```

## Architectural Directives & Anti-Pattern Elimination Table

| Target File | Current Anti-Pattern / Violation | Modern Architectural SSOT | Remediation Step |
|---|---|---|---|
| `backend_v2/services/orchestrator/strategies/base.py` | `StrategyContext` missing strict config, `delta.pop("metadata")` | `ConfigDict(strict=True, extra='forbid')`, typed `HookDeltaDTO` | Step 1 |
| `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py` | 8x `isinstance`, 10x `getattr()`, 2x `.get()` on DTOs | Direct dot-notation on typed `StepOutputDTO` (`dto.block_id`, `dto.payload`, `dto.step_id`) | Step 2 |
| `backend_v2/services/orchestrator/strategies/llm.py` | 6x `isinstance`, 2x `getattr()`, `.get()` on blackboard | Direct typed `GlobalAtomBlackboard` and `ExecutionInputsDTO` | Step 2 |
| `backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py` | 4x nested `isinstance` and `.get()` chains | Direct typed access on `WorkflowInputs` / `ExecutionInputsDTO` | Step 2 |
| `backend_v2/services/orchestrator/prompt_compiler.py` | `model_dump()` to dict traversals in `build_xml_context` | Direct typed `I18nText.resolve()` on `ExpectedInput` models | Step 3 |
| `backend_v2/services/orchestrator/prompt_compiler_adapter.py` | `__getattr__` delegation (QGR001) | Explicit method delegation to wrapped `PromptCompiler` | Step 3 |
| `backend_v2/services/orchestrator/context_router.py` | `RoutingModeConfig` missing strict ConfigDict, `getattr(dto, "step_id")` | `ConfigDict(strict=True, extra='forbid')`, typed `dto.step_id` | Step 3 |
| `backend_v2/services/orchestrator/engines/tda_engine.py` | AppException without ErrorCodes, `.get()` on blackboard | `AppException(details={"error_code": ErrorCodes.CONFIGURATION_ERROR})`, typed blackboard | Step 4 |
| `backend_v2/services/orchestrator/engines/synthesis_engine.py` | AppException without ErrorCodes, 3x `.get()`, dict mutations | `AppException(details={"error_code": ErrorCodes.SYNTHESIS_ENGINE_ERROR})`, typed models | Step 4 |
| `backend_v2/services/orchestrator/synthesis_payload_compressor.py` | 3x `isinstance(..., dict)`, loose dictionary stripping | Polymorphic payload handling using `DistilledEvaluation` models | Step 4 |
| `backend_v2/services/orchestrator/synthesis_distiller.py` | 2x `isinstance`, `uid_to_alias.get()` | Direct dictionary lookup `uid_to_alias[uid]` with Fail-Fast | Step 4 |
| `backend_v2/services/orchestrator/matrix_explanation_service.py` | 6x `isinstance` branches | Typed `AtomResultDTO` and `StepOutputDTO` traversal | Step 4 |
| `backend_v2/services/orchestrator/matrix_reducer.py` | 2x `isinstance` + dict nesting | Direct iteration over typed `ReducedAtomDTO` and `QuoteEvidenceDTO` | Step 4 |
| `backend_v2/services/orchestrator/anchor_validation_service.py` | `model_dump() | {...}` dictionary merges | In-place immutable `model_copy(update={...})` | Step 4 |
| `backend_v2/services/orchestrator/dag_executor.py` | `getattr(b, "is_synthesis")`, `hasattr(e, "details")`, `.get("error_code")` | Typed `PromptBlockCategory`, `isinstance(e, AppException)`, `e.error_code` | Step 5 |
| `backend_v2/services/orchestrator/rag_preflight_service.py` | 2x `isinstance`, `.get("inputs")` | Direct typed extraction from `ExecutionInputsDTO` / `WorkflowInputs` | Step 5 |
| `backend_v2/services/orchestrator/localization_compiler.py` | 1x `isinstance` on I18n model | Typed `I18nText` polymorphism | Step 5 |
| `backend_v2/services/orchestrator/extraction_schema_factory.py` | `isinstance(data, dict)` in `canonicalise_nulls` | Pydantic V2 native field validators with `strict=True` | Step 5 |
| `backend_v2/services/orchestrator/atomizer.py` | `model_dump()` serialization cycles | Immutable `model_copy(update={...})` | Step 5 |

## Verification & Quality Gates Plan

### Automated Test Gates
1. **Orchestrator Unit Tests**:
   `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`
2. **AST Guardrail Verification**:
   `uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict`
3. **SDUI Cross-Domain Semantic Parity**:
   `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
4. **Full Backend Integration Gate**:
   `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/ --test`

