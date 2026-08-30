# Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)

**Phase Title:** Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)
**Objective:** Eliminate ALL `isinstance(..., dict)`, `getattr()`, `hasattr()`, and `.get()` branches from the orchestration engine, strategy dispatchers, prompt compilers, and evaluation engines, updating state transitions to use strictly typed dot-notation and immutable `model_copy(update={...})` within `async with _update_lock:`, and modernizing orchestrator unit tests atomically.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L259-L286] (Phase 4: Orchestration & Strategy Core Refactoring & Tests)

**Target Files** (exhaustive — 24 production files + test suites):
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L299-L925] (`DAGExecutor`)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L61-L815] (`LLMNodeStrategy`)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L86-L330] (`NodeStrategy`)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L15-L392] (`ContextBuilder`)
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L128] (`ExecutionTimeResolver`)
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler.py#L36-L462] (`PromptCompiler`)
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L139] (`PromptCompilerAdapter`)
- `[MODIFY]` @[backend_v2/services/orchestrator/context_router.py#L47-L214] (`ContextRouter`)
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L287] (`SynthesisPayloadCompressor`)
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py#L168-L357] (`synthesis_distiller_hook`)
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L237] (`MatrixExplanationService`)
- `[MODIFY]` @[backend_v2/services/orchestrator/rag_preflight_service.py#L79-L230] (`RAGPreflightService`)
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py#L34-L243] (`LocalizationCompiler`)
- `[MODIFY]` @[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147] (`create_extraction_model`)
- `[MODIFY]` @[backend_v2/services/orchestrator/atomizer.py#L18-L94] (`PromptAtomizer`)
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py#L19-L401] (`AnchorValidationService`)
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154] (`MatrixReducer`)
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L218] (`TDAEngine`)
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L221] (`SynthesisEngine`)
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_compiler.py#L9-L185] (`DAGCompilerService`)
- `[MODIFY]` @[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L430] (`ExtractiveSensorService`)
- `[MODIFY]` @[backend_v2/services/orchestrator/result_projector.py#L17-L131] (`ResultProjector`)
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L30-L477] (`TwoPassAtomizer`)
- `[MODIFY]` @[backend_v2/services/orchestrator/enriched_dag_executor.py#L27-L181] (`EnrichedDagExecutor`)
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

  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUPS &amp; AST REMEDIATION">
    <action>Clean up pre-flight AST violations in peripheral orchestrator utilities:
      1. In @[backend_v2/services/orchestrator/dag_compiler.py#L9-L185]: replace `adj_list.get(node, [])` with membership-guarded lookup (`if node in adj_list: for neighbor in adj_list[node]:`).
      2. In @[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L430]: replace `tally.get(status, 0) + 1` with `tally[status] = (tally[status] + 1) if status in tally else 1`.
      3. In @[backend_v2/services/orchestrator/result_projector.py#L17-L131]: pass typed `ErrorCodes.VALIDATION_FAILED` to `AppException`.
      4. In @[backend_v2/services/orchestrator/two_pass_atomizer.py#L30-L477]: append `# noqa: QGR003 - DLQ Worker error isolation` to worker exception handler.
      5. In @[backend_v2/services/orchestrator/enriched_dag_executor.py#L27-L181]: append `# noqa: QGR003 - Best-effort cache teardown` to teardown handler.</action>
    <constraint invariant="the_duct_tape_ban">Eliminate all .get(key, default) lazy fallbacks in domain code.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">AppException instantiated with typed ErrorCodes enum members.</constraint>
  </step>

  <step id="2" name="STRATEGY BASE &amp; HOOK INTEGRATION MODERNIZATION">
    <action>Refactor @[backend_v2/services/orchestrator/strategies/base.py#L86-L330]:
      1. Enforce `model_config = ConfigDict(strict=True, extra='forbid')` on `StrategyContext`.
      2. Modernize `run_pre_hooks` and `run_post_hooks` to consume typed `HookDeltaDTO` (`res.state_delta`).
      3. Access `res.state_delta.metadata_updates` and `res.state_delta.delta` directly without `delta.pop("metadata")` or `isinstance(..., dict)` fallbacks.
      4. Access `context.metadata.target_locale` and `context.global_context_vars` via strict dot-notation.</action>
    <constraint invariant="zero_service_layer_fallbacks">No `.get()` or `getattr()` on StrategyContext or HookDeltaDTO.</constraint>
    <constraint invariant="rfc7807_dual_reporting_mandate">Pre/post-hook execution failures logged with structured context before raising.</constraint>
  </step>

  <step id="3" name="LLM EXECUTION &amp; CONTEXT BUILDER REFAC">
    <action>Refactor @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L15-L392], @[backend_v2/services/orchestrator/strategies/llm.py#L61-L815], and @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L128]:
      1. In `ContextBuilder`: replace `getattr(dto, "block_id", None)` and `getattr(dto, "payload", None)` with direct typed attribute access on `StepOutputDTO` (`dto.block_id`, `dto.payload`, `dto.step_id`).
      2. In `ContextBuilder._collect_rule_descriptions`: replace `getattr()` calls with direct model properties (`block.ai_description`, `block.scales`, `scale.claims`, `claim.tda_assertions`).
      3. In `ContextBuilder.apply_spatial_slicing` &amp; path resolution: replace `.get("steps")` with direct dictionary indexing or validated `StateProjector.snapshot` filtering.
      4. In `LLMNodeStrategy`: replace `inputs_payload.get("inputs")` and `hook_state.global_context_vars.get()` with direct keys or typed `GlobalContextVarsDTO` access.
      5. In `LLMNodeStrategy`: replace `getattr(step, "expected_sdui_type", "grid")` with `step.expected_sdui_type or "grid"`.
      6. In `ExecutionTimeResolver`: eliminate recursive `.get()` chains on `raw_inputs` and `dynamic_inputs`; use direct typed fields on `WorkflowInputs` / `ExecutionInputsDTO`.</action>
    <constraint invariant="strict_attribute_integrity">Never convert strict dot-notation attribute access into dynamic getattr() fallbacks.</constraint>
    <constraint invariant="the_duct_tape_ban">Eliminate all `isinstance(..., dict)` branches and `.get()` fallback chains.</constraint>
  </step>

  <step id="4" name="PROMPT COMPILER, ADAPTER &amp; CONTEXT ROUTER REFACTORING">
    <action>Refactor @[backend_v2/services/orchestrator/prompt_compiler.py#L36-L462], @[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L139], and @[backend_v2/services/orchestrator/context_router.py#L47-L214]:
      1. In `PromptCompiler`: replace `model_dump()` to dict traversals in `build_xml_context` with typed `I18nText` model access (`ei.label.resolve(target_locale)`).
      2. In `PromptCompilerAdapter`: wrap delegate calls explicitly rather than bare `__getattr__` reflection that violates QGR001.
      3. In `ContextRouter`: add `model_config = ConfigDict(strict=True, extra='forbid')` to `RoutingModeConfig` and `SnapshotState`.
      4. In `ContextRouter`: replace `getattr(dto, "step_id", None)` with typed `dto.step_id`.</action>
    <constraint invariant="xml_structural_sovereignty_mandate">Maintain strict XML tag generation just-in-time via PromptCompiler.</constraint>
    <constraint invariant="strict_pydantic_v2_rust">Enforce ConfigDict(strict=True, extra='forbid') on all context models.</constraint>
  </step>

  <step id="5" name="SYNTHESIS &amp; EVALUATION ENGINES REFAC">
    <action>Refactor @[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L218], @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L221], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L237], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L287], @[backend_v2/services/orchestrator/synthesis_distiller.py#L168-L357], @[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154], and @[backend_v2/services/orchestrator/anchor_validation_service.py#L19-L401]:
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

  <step id="6" name="DAG EXECUTOR &amp; REASONING ORCHESTRATION REFACTORING">
    <action>Refactor @[backend_v2/services/orchestrator/dag_executor.py#L299-L925], @[backend_v2/services/orchestrator/rag_preflight_service.py#L79-L230], @[backend_v2/services/orchestrator/localization_compiler.py#L34-L243], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147], and @[backend_v2/services/orchestrator/atomizer.py#L18-L94]:
      1. In `DAGExecutor._resolve_execution_engine`: eliminate `getattr(b, "is_synthesis", False)` by checking typed `PromptBlockCategory` and domain properties on `PromptBlock`.
      2. In `DAGExecutor` exception handler: replace `hasattr(e, "details")` and `e.details.get("error_code")` with typed `isinstance(e, AppException)` and `e.error_code`.
      3. In `DAGExecutor`: ensure all state mutations execute inside `async with _update_lock:` using `.model_copy(update=...)` with typed instances.
      4. In `RAGPreflightService`: eliminate `.get("inputs")` by extracting dynamic inputs from typed `ExecutionInputsDTO` / `WorkflowInputs`.
      5. In `ExtractionSchemaFactory`: eliminate `isinstance(data, dict)` in `canonicalise_nulls` validators by using strict model validation.</action>
    <constraint invariant="frozen_state_mutability">State transitions in DAGExecutor execute inside async with _update_lock: using .model_copy(update=...) with typed instances.</constraint>
    <constraint invariant="orchestrator_god_object_fragility">Full blast-radius evaluation and verification across topological flow.</constraint>
  </step>

  <step id="7" name="ATOMIC TEST SUITE MODERNIZATION &amp; QUALITY GATES">
    <action>Modernize all orchestrator and strategy test suites under @[backend_v2/tests/unit/services/orchestrator/]:
      1. Modernize @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]: replace raw dict mocks with typed `Workflow`, `Step`, `StepRule`, and `ExecutionMetadata` fixtures.
      2. Modernize @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]: replace legacy dictionary fixtures with `polyfactory` and typed `StrategyContext` models.
      3. Modernize @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]: test typed hook execution with `HookDeltaDTO`.
      4. Modernize @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]: verify typed `StepOutputDTO` pruning across 4 ISTQB partitions.
      5. Modernize @[backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py] and `test_synthesis_engine.py`: test typed execution with mock LLM outputs.
      6. Modernize @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py] and `test_synthesis_distiller_wiring.py`: update `HookState` initialization to typed `ExecutionInputsDTO`.
      7. Run AST Guardrail audit: `uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict`.
      8. Run Backend Audit Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.
      9. Run SDUI Semantic Parity: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Execute full audit loop and all 65 orchestrator test files before completion.</constraint>
    <constraint invariant="anti_happy_path_mandate">Each test file must cover at least 2 negative partitions (missing required fields, validation error, AppException).</constraint>
  </step>

  <dod_checklist>
    - [ ] All `isinstance(..., dict)`, `getattr()`, `hasattr()`, and `.get()` branches eliminated across all 24 orchestrator and strategy files.
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
    <backend>@[backend_v2/services/orchestrator/dag_executor.py#L299-L925]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py#L61-L815]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py#L86-L330]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L15-L392]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L128]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler.py#L36-L462]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L139]</backend>
    <backend>@[backend_v2/services/orchestrator/context_router.py#L47-L214]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L287]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py#L168-L357]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py#L28-L237]</backend>
    <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py#L79-L230]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py#L34-L243]</backend>
    <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147]</backend>
    <backend>@[backend_v2/services/orchestrator/atomizer.py#L18-L94]</backend>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py#L19-L401]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L218]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L221]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_compiler.py#L9-L185]</backend>
    <backend>@[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L430]</backend>
    <backend>@[backend_v2/services/orchestrator/result_projector.py#L17-L131]</backend>
    <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py#L30-L477]</backend>
    <backend>@[backend_v2/services/orchestrator/enriched_dag_executor.py#L27-L181]</backend>
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

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test
    uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict
    uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
  </validation_gate>
</execution_protocol>
```

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Strategy Base & Context**<br>@[backend_v2/services/orchestrator/strategies/base.py#L86-L330] | `StrategyContext` missing strict config, `delta.pop("metadata")` hacks, loose dict merging. | `ConfigDict(strict=True, extra='forbid')`, typed `HookDeltaDTO` (`delta.delta`, `delta.metadata_updates`). | Delete manual dictionary popping and shallow string mutations. | Unit tests in `test_base.py` passing 100%.<br>`uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/base.py --test` |
| **LLM Strategy & Context Builder**<br>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L15-L392]<br>@[backend_v2/services/orchestrator/strategies/llm.py#L61-L815]<br>@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L17-L128] | 8x `isinstance(..., dict)`, 10x `getattr()`, 2x `.get()` on DTOs, loose blackboard dictionaries. | Direct typed dot-notation on `StepOutputDTO` (`dto.block_id`, `dto.payload`, `dto.step_id`), typed `GlobalAtomBlackboard`, `ExecutionInputsDTO`. | Prune recursive dictionary traversal loops; rely on direct model attributes. | AST check: 0 reflection violations.<br>`test_context_builder.py`, `test_llm.py` passing 100%. |
| **Prompt Compiler, Adapter & Router**<br>@[backend_v2/services/orchestrator/prompt_compiler.py#L36-L462]<br>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L10-L139]<br>@[backend_v2/services/orchestrator/context_router.py#L47-L214] | `model_dump()` to dict traversals, `__getattr__` dynamic delegation (QGR001), missing `model_config`. | Direct typed `I18nText.resolve()` on `ExpectedInput`, explicit method proxying, `ConfigDict(strict=True, extra='forbid')`. | Cut dynamic `__getattr__` reflection; declare explicit delegation methods. | `test_prompt_compiler.py`, `test_prompt_compiler_adapter.py`, `test_context_router.py` passing 100%. |
| **Synthesis & Evaluation Engines**<br>@[backend_v2/services/orchestrator/engines/tda_engine.py#L29-L218]<br>@[backend_v2/services/orchestrator/engines/synthesis_engine.py#L27-L221]<br>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py#L22-L287]<br>@[backend_v2/services/orchestrator/synthesis_distiller.py#L168-L357]<br>@[backend_v2/services/orchestrator/matrix_reducer.py#L17-L154]<br>@[backend_v2/services/orchestrator/anchor_validation_service.py#L19-L401] | `AppException` without `ErrorCodes`, `.get()` on blackboard, `isinstance(..., dict)`, `model_dump() \| {...}` dictionary merges. | Typed `AppException(ErrorCodes.*)`, typed `GlobalAtomBlackboard`, `DistilledEvaluation`, immutable `model_copy(update={...})`. | Cut speculative dictionary fallback layers; enforce strict fail-fast on missing keys. | `test_tda_engine.py`, `test_synthesis_engine.py`, `test_synthesis_distiller.py` passing 100%. |
| **DAG Executor & Core Flow**<br>@[backend_v2/services/orchestrator/dag_executor.py#L299-L925]<br>@[backend_v2/services/orchestrator/rag_preflight_service.py#L79-L230]<br>@[backend_v2/services/orchestrator/localization_compiler.py#L34-L243]<br>@[backend_v2/services/orchestrator/extraction_schema_factory.py#L82-L147]<br>@[backend_v2/services/orchestrator/atomizer.py#L18-L94] | `getattr(b, "is_synthesis")`, `hasattr(e, "details")`, `.get("error_code")`, unsynchronized state mutations. | Typed `PromptBlockCategory`, `isinstance(e, AppException)`, `async with _update_lock:` with typed `.model_copy(update={...})`. | Eliminate duplicate execution state wrappers; enforce single-pass atomic commit. | `test_dag_executor.py`, `test_rag_preflight_service.py` passing 100%.<br>`test_sdui_semantic_parity.py` verified. |
| **Orchestrator Utilities & Sensors**<br>@[backend_v2/services/orchestrator/dag_compiler.py#L9-L185]<br>@[backend_v2/services/orchestrator/extractive_sensor_service.py#L62-L430]<br>@[backend_v2/services/orchestrator/result_projector.py#L17-L131]<br>@[backend_v2/services/orchestrator/two_pass_atomizer.py#L30-L477]<br>@[backend_v2/services/orchestrator/enriched_dag_executor.py#L27-L181] | `adj_list.get(node, [])`, `tally.get(status, 0)`, string error codes in `AppException`, unsuppressed broad `except:`. | Guarded key access, typed `ErrorCodes.VALIDATION_FAILED`, explicit `# noqa: QGR003` comments on worker fault domains. | Prune redundant consensus tallies; use direct membership testing. | `uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict` passes with 0 errors. |

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


