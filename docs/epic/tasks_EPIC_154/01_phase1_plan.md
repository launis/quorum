# Phase 1: Pre-Implementation Technical Debt Cleanups (Scoped Boy Scout)

**Overview:** Verify that `ChunkPacketDTO` is already completed in `dag_models.py` and consumed in `two_pass_atomizer.py`, isolate `SlidingWindowLinker` constructor parameter defaults, modernize step consistency validation to use `StepType.LLM` and `StepType.LOGIC` enum checks with `AppException(ErrorCodes.VALIDATION_FAILED)`, define `EngineType(StrEnum)` in Python and Dart, establish the typed `ENGINE_REGISTRY` and `build_execution_engine` factory in `registry.py`, eliminate heuristic pre-hook string checks (`"atom_flattening_hook"` and `"synthesis_distiller_hook"`) from `dag_executor.py`, add `telemetry_strategy_label` property to the `ExecutionEngine` Protocol and all engine implementations, and eradicate duck-typing cascades and unannotated dictionary mutation accumulators from `LLMNodeStrategy`.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 1: Pre-Implementation Technical Debt Cleanups (Scoped Boy Scout)

**Target Files:**
- `[ALREADY COMPLETED] @[backend_v2/models/dtos/dag_models.py]`
- `[ALREADY COMPLETED] @[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `[ALREADY COMPLETED] @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py]`
- `[MODIFY] @[backend_v2/models/domain/step.py]`
- `[NEW] @[backend_v2/services/orchestrator/engines/registry.py]`
- `[NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_engine_registry.py]`
- `[MODIFY] @[backend_v2/models/enums.py]`
- `[MODIFY] @[backend_v2/seed/seed_data.json]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/workflow.dart]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/base.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/tda_engine.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/prompt_engine.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/synthesis_engine.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/__init__.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/dtos/dag_models.py]`, `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]` | Returning anonymous 3-tuples (`tuple[str, str, list[str]]`) in `_calculate_packets` ("Tuple Hell"), hardcoded magic window sizes (`packet_size = 50`). | **ALREADY COMPLETED IN CODEBASE:** Encapsulated chunk packet bounds into typed immutable `ChunkPacketDTO(start_block: str, end_block: str, packet_keys: list[str])` in `dag_models.py`. Calling sites unpack canonical `packet.packet_keys`. Zero DTO code changes required for Phase 1.1; binding `packet_size` to `get_settings().two_pass_atomizer_packet_size` executes atomically when `settings.py` is extended in Phase 2.1. | Speculative packet wrapper classes or mutating canonical `packet_keys` field. | Physical verification via `view_file` on `dag_models.py` and unit tests in `test_two_pass_atomizer.py`. |
| `@[backend_v2/services/orchestrator/sliding_window_linker.py]` | Hardcoded `window_size=4, overlap=2` constructor defaults mutating shared caller behavior. | **DO NOT** mutate constructor defaults in `SlidingWindowLinker.__init__`. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. | Binding constructor defaults to causal-specific settings. | Regression tests for existing `SlidingWindowLinker` callers; unit tests in `test_causal_discovery_engine.py`. |
| `@[backend_v2/models/domain/step.py]`, `@[backend_v2/models/enums.py]`, `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[backend_v2/seed/seed_data.json]` | Raw string literal comparisons (`self.type == "llm"`, `self.type == "logic"`) bypassing `StepType` enum, duck-typing missing criteria block IDs. Casing mismatch between backend snake_case and Dart camelCase. | Explicit `StepType.LLM` and `StepType.LOGIC` enum comparisons. Declare `engine_type: EngineType = Field(default=EngineType.PROMPT, description="Explicit ExecutionEngine responsible for computing this step.")` on `Step`. Mirror in Dart `enums.dart` with `@JsonValue('causal_discovery') causalDiscovery`. All step blueprints in `seed_data.json` updated with explicit `engine_type`. | Separate `CausalStep` domain model subclass or parallel step validation pipeline. | Unit tests asserting `AppException` when validation fails; `backend_audit_loop.py` and `test_enum_parity.py`. |
| [NEW] `@[backend_v2/services/orchestrator/engines/registry.py]`, `@[backend_v2/services/orchestrator/dag_executor.py]` | `"atom_flattening_hook" in step_def.pre_hooks` heuristic string matching and criteria block category guessing violating `ban_heuristic_identifier_matching`. | Eradicate all heuristic string parsing and category inspection loops in `_resolve_execution_engine`. Introduce typed `ENGINE_REGISTRY: dict[EngineType, Callable[[PromptCompiler], ExecutionEngine]]` and factory `build_execution_engine(engine_type, prompt_compiler)` in `registry.py`. `NodeExecutor._resolve_execution_engine` resolves deterministically via `build_execution_engine(step_def.engine_type, self.deps.prompt_compiler)` in O(1) time with Fail-Fast `AppException(ErrorCodes.VALIDATION_FAILED)`. | Heuristic substring matches, hardcoded hook tuple markers, and if-elif branching cascades. | Unit tests in `test_engine_registry.py` proving deterministic resolution and zero heuristic hook parsing. |
| `@[backend_v2/services/orchestrator/strategies/llm.py]`, `@[backend_v2/services/orchestrator/engines/base.py]`, `@[backend_v2/services/orchestrator/engines/tda_engine.py]`, `@[backend_v2/services/orchestrator/engines/prompt_engine.py]`, `@[backend_v2/services/orchestrator/engines/synthesis_engine.py]` | Permissive model strategy fallback defaulting to `"prompt"`, ignoring engine ontology for causal discovery steps. `isinstance()` runtime type-check heuristic for strategy string selection. Duck-typing `isinstance(existing_meta, BaseModel|Mapping)` cascade and untyped `meta_dict = {}` dictionary key mutation accumulator. | Add `telemetry_strategy_label: str` property to `ExecutionEngine` Protocol in `base.py`. Each engine self-reports its label (`TDAEngine` returns `"tda"`, `PromptEngine` returns `"prompt"`, `SynthesisEngine` returns `"synthesis"`, `CausalDiscoveryEngine` returns `"causal"`). In `LLMNodeStrategy`, replace `isinstance` branching and untyped duck-typing by reconstituting `_step_metadata` directly via typed `StepTraceMetadataDTO` and reading `self._engine.telemetry_strategy_label`. | Dynamic strategy router subclasses or parallel LLM execution strategies. `isinstance` cascade branches and untyped dictionary accumulators. | Unit tests verifying `engine.telemetry_strategy_label == "causal"`, `_step_metadata.model_strategy == "causal"`, and `StepTraceMetadataDTO` validation roundtrip. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state. Verify `two_pass_atomizer.py`, `dag_models.py`, `sliding_window_linker.py`, `step.py`, `dag_executor.py`, and `strategies/llm.py` exist and are accessible.</action>
    <action>Look forward: Verify that resolving technical debt in step consistency, engine resolution, and strategy telemetry establishes a clean foundation for Phase 2 DTO and enum foundation.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/01_phase1_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>Verify ChunkPacketDTO in dag_models.py and TwoPassAtomizer._calculate_packets (already completed in codebase with canonical packet_keys field).</item>
    <item>SlidingWindowLinker constructor defaults (window_size=4, overlap=2) preserved unchanged.</item>
    <item>Step.validate_step_consistency migrated to StepType.LLM and StepType.LOGIC enum checks, raising AppException(ErrorCodes.VALIDATION_FAILED).</item>
    <item>EngineType(StrEnum) defined in backend_v2/models/enums.py with members TDA, SYNTHESIS, PROMPT, CAUSAL_DISCOVERY.</item>
    <item>Step domain model in step.py extended with engine_type: EngineType = Field(default=EngineType.PROMPT).</item>
    <item>Step blueprints in seed_data.json updated with explicit engine_type across all steps.</item>
    <item>EngineType mirrored in client_app_v2/lib/core/models/enums.dart and NodeStrategy in workflow.dart extended with engine_type, passing flutter_audit_loop.py --build.</item>
    <item>Typed ENGINE_REGISTRY and build_execution_engine factory implemented in backend_v2/services/orchestrator/engines/registry.py and re-exported in engines/__init__.py.</item>
    <item>Heuristic pre-hook string matching ("atom_flattening_hook" and "synthesis_distiller_hook") and category inspection loops 100% eradicated from dag_executor.py.</item>
    <item>telemetry_strategy_label property added to ExecutionEngine Protocol and implemented on TDAEngine, PromptEngine, and SynthesisEngine.</item>
    <item>Duck-typing cascade isinstance(existing_meta, BaseModel|Mapping) and untyped meta_dict = {} accumulator eradicated from LLMNodeStrategy.execute, reconstituting _step_metadata via StepTraceMetadataDTO.</item>
    <item>Unit tests in test_engine_registry.py pass 100% proving deterministic engine dispatch.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_synthesis_payload_compression.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do not modify constructor defaults in SlidingWindowLinker.__init__.</forbidden>
    <forbidden>Do not create speculative CausalStep domain subclasses.</forbidden>
    <forbidden>Do not mutate canonical packet_keys field name in ChunkPacketDTO.</forbidden>
    <forbidden>Do not introduce fallback branches or permissive defaults in build_execution_engine.</forbidden>
    <forbidden>Do not add untyped dictionary mutation loops in LLMNodeStrategy.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/sliding_window_linker.py]</backend>
    <backend>@[backend_v2/models/domain/step.py]</backend>
    <backend>[NEW] @[backend_v2/services/orchestrator/engines/registry.py]</backend>
    <backend>@[backend_v2/models/enums.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/prompt_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/__init__.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart]</frontend>
  </touched_artifacts>

  <step id="1.1" name="VERIFY_CHUNK_PACKET_DTO_COMPLETION">
    <action>[ALREADY_IMPLEMENTED] - Skip execution. Verified at: @[backend_v2/models/dtos/dag_models.py#L273-L286] and @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77]. ChunkPacketDTO is fully implemented with canonical fields start_block: str, end_block: str, and packet_keys: Annotated[list[str], Field(...)], enforcing ConfigDict(strict=True, extra="forbid", frozen=True). Calling sites in TwoPassAtomizer unpack attributes directly. Verified covered by tests in @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py]. In Phase 2.1, upon adding two_pass_atomizer_packet_size to settings.py, TwoPassAtomizer dynamically binds its packet size parameter via get_settings().two_pass_atomizer_packet_size.</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve immutable ChunkPacketDTO contract without modifications.</constraint>
  </step>

  <step id="1.2" name="ISOLATE_SLIDING_WINDOW_LINKER_CONSTRUCTOR">
    <action>In @[backend_v2/services/orchestrator/sliding_window_linker.py], verify and preserve constructor default arguments in SlidingWindowLinker.__init__ (window_size=4, overlap=2) without mutation, preventing parameter contamination of existing callers. Mandate that CausalDiscoveryEngine constructs SlidingWindowLinker with explicit settings parameters: SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap).</action>
    <constraint invariant="zero_service_layer_fallbacks">Do not inject causal-specific settings as default parameters in SlidingWindowLinker.__init__.</constraint>
  </step>

  <step id="1.3" name="MODERNIZE_STEP_CONSISTENCY_VALIDATION_ENUMS">
    <action>In @[backend_v2/models/domain/step.py], locate validate_step_consistency. Replace raw string literal comparisons if self.type == "llm": and if self.type == "logic": with typed enum checks if self.type == StepType.LLM: and if self.type == StepType.LOGIC:. Replace ValueError(msg) with AppException(ErrorCodes.VALIDATION_FAILED, msg) across all step consistency validation failures, strictly adhering to RFC 7807 Fail-Fast standards.</action>
    <demolish>REMOVE: raw string comparisons if self.type == "llm": and if self.type == "logic": at @[backend_v2/models/domain/step.py]. REPLACE WITH: if self.type == StepType.LLM: and if self.type == StepType.LOGIC: raising AppException(ErrorCodes.VALIDATION_FAILED).</demolish>
    <constraint invariant="universal_fail_fast">Never raise generic ValueError for domain validation in Step model.</constraint>
  </step>

  <step id="1.4" name="DEFINE_ENGINE_TYPE_ENUM_AND_CROSS_LANGUAGE_PARITY">
    <action>In @[backend_v2/models/enums.py], define EngineType(StrEnum) with members: TDA = "tda", SYNTHESIS = "synthesis", PROMPT = "prompt", CAUSAL_DISCOVERY = "causal_discovery".</action>
    <action>In @[backend_v2/models/domain/step.py], declare engine_type: Annotated[EngineType, Field(default=EngineType.PROMPT, description="Explicit ExecutionEngine responsible for computing this step.")] on the Step domain model.</action>
    <action>In @[client_app_v2/lib/core/models/enums.dart], mirror EngineType with @JsonEnum() annotations: @JsonValue('tda') tda, @JsonValue('synthesis') synthesis, @JsonValue('prompt') prompt, @JsonValue('causal_discovery') causalDiscovery.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart], add @JsonKey(name: 'engine_type') @Default(EngineType.prompt) EngineType engineType to NodeStrategy.llm and NodeStrategy.logic.</action>
    <action>Run flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build ensuring Freezed model generation passes cleanly without unrecognized key errors.</action>
    <action>In @[backend_v2/seed/seed_data.json], update all step blueprints under "steps" with explicit "engine_type": "tda" for matrix evaluation steps, "synthesis" for intermediate synthesis steps, "prompt" for non-matrix LLM steps.</action>
    <constraint invariant="cross_language_enum_parity">Enforce 1:1 parity between Python EngineType and Dart EngineType enums.</constraint>
  </step>

  <step id="1.5" name="IMPLEMENT_TYPED_ENGINE_REGISTRY">
    <contract_freeze>
      def build_execution_engine(engine_type: EngineType, prompt_compiler: PromptCompiler) -> ExecutionEngine
    </contract_freeze>
    <action>Create [NEW] @[backend_v2/services/orchestrator/engines/registry.py] defining ENGINE_REGISTRY: dict[EngineType, Callable[[PromptCompiler], ExecutionEngine]] and factory function build_execution_engine(engine_type: EngineType, prompt_compiler: PromptCompiler) -> ExecutionEngine mapping EngineType members: TDA -> TDAEngine(prompt_compiler), SYNTHESIS -> SynthesisEngine(LLMTaskExecutor(prompt_compiler)), PROMPT -> PromptEngine(LLMTaskExecutor(prompt_compiler)), and CAUSAL_DISCOVERY -> CausalDiscoveryEngine(prompt_compiler) (to be registered in Phase 3). If engine_type is unknown, raise AppException(ErrorCodes.VALIDATION_FAILED, f"Unsupported engine type: {engine_type}").</action>
    <action>Re-export ENGINE_REGISTRY and build_execution_engine in @[backend_v2/services/orchestrator/engines/__init__.py] within __all__.</action>
    <action>Create unit tests in [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_engine_registry.py] asserting deterministic resolution across all registered EngineType members and Fail-Fast on invalid engine types.</action>
    <constraint invariant="ban_heuristic_identifier_matching">Resolve compute engines strictly via typed EngineType enum in O(1) time without string parsing.</constraint>
  </step>

  <step id="1.6" name="ERADICATE_PRE_HOOK_HEURISTIC_MATCHING_IN_DAG_EXECUTOR">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], locate _resolve_execution_engine. Completely eradicate pre-hook string checks ("atom_flattening_hook" in step_def.pre_hooks and "synthesis_distiller_hook" in step_def.pre_hooks) and criteria block category inspection loops. Refactor _resolve_execution_engine to delegate directly: return build_execution_engine(step_def.engine_type, self.deps.prompt_compiler).</action>
    <demolish>REMOVE: "atom_flattening_hook" in step_def.pre_hooks check, "synthesis_distiller_hook" check, and criteria block category inspection loop in _resolve_execution_engine at @[backend_v2/services/orchestrator/dag_executor.py]. REPLACE WITH: deterministic return build_execution_engine(step_def.engine_type, self.deps.prompt_compiler).</demolish>
    <constraint invariant="single_pipeline_invariant_mandate">All step engine resolutions must flow through the single deterministic build_execution_engine factory.</constraint>
  </step>

  <step id="1.7" name="ADD_TELEMETRY_STRATEGY_LABEL_AND_PURGE_LLM_STRATEGY_DUCK_TYPING">
    <action>In @[backend_v2/services/orchestrator/engines/base.py], add telemetry_strategy_label: str property to the ExecutionEngine Protocol.</action>
    <action>In @[backend_v2/services/orchestrator/engines/tda_engine.py], implement telemetry_strategy_label returning "tda".</action>
    <action>In @[backend_v2/services/orchestrator/engines/prompt_engine.py], implement telemetry_strategy_label returning "prompt".</action>
    <action>In @[backend_v2/services/orchestrator/engines/synthesis_engine.py], implement telemetry_strategy_label returning "synthesis".</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py], actively eradicate the duck-typing isinstance(existing_meta, BaseModel|Mapping) cascade and untyped dictionary accumulator meta_dict = {}. Refactor to reconstitute _step_metadata strictly via StepTraceMetadataDTO: unpack pre-existing step metadata via StepTraceMetadataDTO.model_validate(existing_meta) if present, record model_strategy = self._engine.telemetry_strategy_label using the Protocol property instead of isinstance(self._engine, SynthesisEngine) branching, and assign the serialized DTO back into the output event without unannotated dict mutation loops.</action>
    <demolish>REMOVE: isinstance(existing_meta, BaseModel|Mapping) checks and untyped meta_dict = {} accumulator in LLMNodeStrategy.execute at @[backend_v2/services/orchestrator/strategies/llm.py]. REPLACE WITH: typed StepTraceMetadataDTO reconstitution and self._engine.telemetry_strategy_label.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Zero naked dictionaries in state transit; enforce StepTraceMetadataDTO validation.</constraint>
  </step>

  <test_contracts>
    <test name="test_build_execution_engine_tda_returns_tda_engine" category="positive">
      <input>EngineType.TDA, mock PromptCompiler</input>
      <expected>returns TDAEngine instance with telemetry_strategy_label == "tda"</expected>
    </test>
    <test name="test_build_execution_engine_synthesis_returns_synthesis_engine" category="positive">
      <input>EngineType.SYNTHESIS, mock PromptCompiler</input>
      <expected>returns SynthesisEngine instance with telemetry_strategy_label == "synthesis"</expected>
    </test>
    <test name="test_build_execution_engine_prompt_returns_prompt_engine" category="positive">
      <input>EngineType.PROMPT, mock PromptCompiler</input>
      <expected>returns PromptEngine instance with telemetry_strategy_label == "prompt"</expected>
    </test>
    <test name="test_build_execution_engine_unsupported_raises_app_exception" category="error_path">
      <input>Invalid string cast to EngineType, mock PromptCompiler</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED</expected>
    </test>
    <test name="test_step_consistency_invalid_llm_raises_app_exception" category="error_path">
      <input>Step with type=StepType.LLM but criteria_block_ids empty</input>
      <expected>raises AppException with ErrorCodes.VALIDATION_FAILED (not ValueError)</expected>
    </test>
    <test name="test_llm_node_strategy_metadata_uses_telemetry_label" category="positive">
      <input>LLMNodeStrategy executed with TDAEngine</input>
      <expected>_step_metadata.model_strategy == "tda" reconstituted via StepTraceMetadataDTO</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/registry.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test</action>
    <action>Execute: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build</action>
    <action>Execute: grep_search for "atom_flattening_hook" in backend_v2/services/orchestrator/dag_executor.py confirming zero residual matches</action>
    <action>Execute: grep_search for "meta_dict" in backend_v2/services/orchestrator/strategies/llm.py confirming zero residual matches</action>
  </validation_gate>
</execution_protocol>
```
