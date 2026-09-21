<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
  <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# Phase 5: LLM Context Orchestration, Dynamic Input Merging & Prompt Compiler Hardening

**Overview:** Hardening prompt compilation, dynamic input merging, context orchestration, and DAG execution to eliminate dictionary mutations, string-based context lookups, and silent exception swallowing. Establishes immutable, strongly typed Pydantic V2 DTOs across the prompt compilation layer (`PromptMappingDTO`, `LLMContextDataDTO`), state reduction layer (`merge_execution_inputs` in `state_reducer.py` eliminating 3 `# noqa: QGR012` suppressions), and DAG execution layer (`ContextVariablesDTO`, `NodeExecutionUpdateDTO`, `LogicNodeStateDTO`, `LogicEvaluationContextDTO`, `SensorValidationContextDTO`, `FinOpsMonitorSummaryDTO`, `FinOpsFinalizeSummaryDTO`, `TavilySearchRequestDTO`, `MCPToolDeclarationDTO`). Eradicates `model.model_dump()` dictionary laundering in `prompt_compiler.py` in favor of direct dot-notation traversal via `math_utils.resolve_dot_notation`. Eradicates silent exception swallowing across orchestrator helpers (`context_router.py`, `extraction_schema_factory.py`, `matrix_explanation_service.py`, `rag_preflight_service.py`). Replaces dynamic `create_model` field name synthesis in `registry.py` and `extraction_schema_factory.py` with static typed collections, and modernizes co-located unit test suites by eliminating `getattr` and `hasattr` dynamic reflection.
**Source:** @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] Phase 5: LLM Context Orchestration, Dynamic Input Merging & Prompt Compiler Hardening

## Five-Axis Architectural Directives Table

| Target Scope & Boundaries | Eradicated Duct-Tape | Approved Best Practice | Pruned Over-Engineering (30% Deletion Test) | Verification & Fail-Fast (Proof Anchor) |
|---|---|---|---|---|
| `backend_v2/services/orchestrator/prompt_compiler.py` & `prompt_compiler_adapter.py` | `current = current.model_dump()[part]` dictionary laundering and `except AttributeError, TypeError:` fallback to `json.dumps()`. | Delegate dot-notation traversal directly to `math_utils.resolve_dot_notation(state_data, path)`. Package input mappings into frozen `PromptMappingDTO`. Raise structured `AppException(ErrorCodes.VALIDATION_FAILED)`. | Prune duplicate recursive dictionary traversal and string parsing routines. | Unit tests in `test_prompt_compiler.py` and `test_prompt_compiler_adapter.py` asserting exact prompt variable extraction without dictionary serialization. |
| `backend_v2/services/orchestrator/strategies/llm_execution/` (`execution_time_resolver.py`, `context_builder.py`, `source_document_packer.py`, `prompt_factory.py`) | Chained `.get()` calls, 4 `except AttributeError, TypeError: pass` blocks, and line 310 `except TypeError, ValueError: text_content = ""` lazy empty string fallback. | Accept `ExecutionInputsDTO`, `ExecutionMetadata`, `PromptMappingDTO`, and return `LLMContextDataDTO`. Enforce Fail-Fast on serialization errors. | Prune multi-tier defensive `.get()` chaining and nested exception catch blocks. | Unit tests in `test_context_builder.py` asserting strongly typed `LLMContextDataDTO` output and Fail-Fast on corrupted payloads. |
| `backend_v2/services/orchestrator/state_reducer.py` & `dag_executor.py` | `merge_dynamic_inputs()` with 3 `# noqa: QGR012` suppressions, recursive dictionary merges with `__replace__` directives, and 8 naked `dict[str, Any]` containers. | Implement `merge_execution_inputs(base: ExecutionInputsDTO, delta: ExecutionInputsDTO) -> ExecutionInputsDTO` using `.model_copy(update=...)`. Type DAG executor parameters with `ContextVariablesDTO` and `NodeExecutionUpdateDTO`. | Delete dictionary deep-copy mutation loops and legacy `__replace__` magic directives. | Unit tests in `test_state_reducer.py` asserting immutable Pydantic V2 state merging. |
| `backend_v2/services/orchestrator/strategies/` (`base.py`, `logic.py`, `llm.py`) & `extractive_sensor_service.py` | `StrategyContext.global_context_vars: dict[str, Any]`, `context_variables: dict[str, Any]`, `current_state: dict[str, Any]`, and `validation_context: dict[str, Any]`. | Encapsulate strategy context into strongly typed `GlobalContextVarsDTO`, `ContextVariablesDTO`, `LogicNodeStateDTO`, `LogicEvaluationContextDTO`, and `SensorValidationContextDTO`. | Delete untyped dictionary packing and unpacking across strategy boundaries. | Strategy unit tests asserting typed context execution and clean state propagation. |
| Orchestrator Helpers (`context_router.py`, `extraction_schema_factory.py`, `matrix_explanation_service.py`, `rag_preflight_service.py`) | Silent exception swallowing `except TypeError, KeyError: pass` and `except (AttributeError, TypeError): pass`. | Catch specific expected validation errors, log RFC 7807 structured diagnostics, and raise `AppException(ErrorCodes.VALIDATION_FAILED)`. | Prune defensive fallback blocks that conceal malformed trace events or corrupted data schemas. | Unit tests asserting Fail-Fast `AppException` propagation upon malformed payloads. |
| Ingress, Evaluator, FinOps & MCP Tools (`ast_evaluator.py`, `finops_trace_analyzer.py`, `tavily_search_client.py`, `tools/tavily.py`, `simulation_service.py`, `workflow_service.py`) | Naked `dict[str, Any]` return signatures, `declaration -> dict[str, Any]`, `payload: dict[str, Any]`, and untyped evaluation facts. | Define frozen Pydantic V2 DTOs: `FinOpsMonitorSummaryDTO`, `FinOpsFinalizeSummaryDTO`, `TavilySearchRequestDTO`, `MCPToolDeclarationDTO`. Type facts as `Mapping[str, bool | str | State]`. | Eradicate manual dictionary unpacking routines across CLI scripts and MCP client adapters. | Unit tests in `test_finops_trace_analyzer.py` asserting typed DTO validation. |
| Dynamic Schema Factory & Registry (`core/registry.py`, `extraction_schema_factory.py`) | Synthesizing dynamic field names via `create_model(f"MatrixExtraction_{matrix_id}", ...)` forcing callers to use `getattr(matrices, matrix_id)`. | Replace dynamic chameleon field synthesis with static Pydantic schemas using typed collections: `records: list[MatrixEvaluationRecordDTO]` or `dict[str, MatrixEvaluationDTO]`. | Delete runtime dynamic model generation for fixed matrix extraction structures. | Unit tests in `test_schema_matrix_bug.py` and `test_schema_factory_alias.py` verifying static attribute access without dynamic reflection. |
| Unit Test Suites (`test_schema_matrix_bug.py`, `test_llm_hallucination_repro.py`, `test_llm_context_bounds.py`, `test_client.py`) | Dynamic reflection calls `getattr(matrices, matrix_block_raw["id"])`, `getattr(result, "blk_...", None)`, 6 `getattr`/`hasattr` on trace events, and `hasattr(last_msg, "content")`. | Direct static access to model attributes, typed dictionary lookups on validated collections, and direct dot-notation access to `TraceEvent.execution_trace` and `last_msg.content`. | Delete reflection helper patterns across unit test fixtures. | Unit tests passing 100% with zero AST guardrail violations (QGR001/QGR018). |

**Target Files:**
- `[NEW]` @[backend_v2/models/dtos/prompt.py]
- `[NEW]` @[backend_v2/models/dtos/context_variables.py]
- `[NEW]` @[backend_v2/models/dtos/node_execution.py]
- `[NEW]` @[backend_v2/models/dtos/sensor.py]
- `[NEW]` @[backend_v2/models/dtos/finops.py]
- `[NEW]` @[backend_v2/models/dtos/mcp.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler.py#L197-L409]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L77-L93]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L20-L153]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L112-L305]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#L255-L330]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L59-L225]
- `[MODIFY]` @[backend_v2/services/orchestrator/state_reducer.py#L12-L55]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L84-L310]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py#L43-L77]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py#L28-L218]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L90-L645]
- `[MODIFY]` @[backend_v2/services/orchestrator/extractive_sensor_service.py#L480-L510]
- `[MODIFY]` @[backend_v2/services/orchestrator/context_router.py#L70-L105]
- `[MODIFY]` @[backend_v2/services/orchestrator/extraction_schema_factory.py#L24-L181]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py#L215-L230]
- `[MODIFY]` @[backend_v2/services/orchestrator/rag_preflight_service.py#L60-L87]
- `[MODIFY]` @[backend_v2/services/orchestrator/ast_evaluator.py#L58-L75]
- `[MODIFY]` @[backend_v2/utils/finops_trace_analyzer.py#L59-L170]
- `[MODIFY]` @[backend_v2/services/mcp/tavily_search_client.py#L74-L95]
- `[MODIFY]` @[backend_v2/services/mcp/tools/tavily.py#L25-L54]
- `[MODIFY]` @[backend_v2/services/studio/simulation_service.py#L335-L360]
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L355-L375]
- `[MODIFY]` @[backend_v2/core/registry.py#L510-L545]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py#L1-L100]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py#L1-L150]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py#L1-L100]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py#L15-L79]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_llm_hallucination_repro.py#L5-L32]
- `[MODIFY]` @[backend_v2/tests/unit/test_schema_factory_alias.py#L6-L34]
- `[MODIFY]` @[backend_v2/tests/unit/test_llm_context_bounds.py#L140-L284]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_client.py#L81-L144]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py#L1-L120]
- `[MODIFY]` @[backend_v2/tests/unit/utils/test_finops_trace_analyzer.py#L1-L94]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 4 established typed hook deltas, GlobalContextVarsDTO, and ResultProjector segregation with zero emojis.</action>
    <action>Look forward: Verify that Phase 6 SDUI presentation layers receive strictly typed step outputs without intermediate naked dictionary representations.</action>
    <action>Note pre-flight state reconciliation: Ingress models (ResolvedIngressDTO, IngressInputValue, DomainInputValue in smart_ingress_resolver.py and inputs.py) were hardened in Phase 2; verify live state before modifying.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_152_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication/05_placeholder_phase5.md] @[docs/epic/EPIC_152_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Prompt compiler in @[backend_v2/services/orchestrator/prompt_compiler.py] operates with PromptMappingDTO and LLMContextDataDTO, delegating dot-notation resolution to math_utils.resolve_dot_notation with zero model_dump dictionary conversions.</item>
    <item>Execution time resolver in @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py] accepts ExecutionInputsDTO and ExecutionMetadata, resolving timestamps without chained .get calls or exception swallowing.</item>
    <item>Context builder in @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py] returns typed LLMContextDataDTO without raw_inputs dictionary fallbacks.</item>
    <item>Source document packer in @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py] raises structured AppException on serialization errors, eradicating line 310 empty string fallback.</item>
    <item>State reducer in @[backend_v2/services/orchestrator/state_reducer.py] implements merge_execution_inputs with zero # noqa: QGR012 suppressions, replacing merge_dynamic_inputs.</item>
    <item>DAG executor in @[backend_v2/services/orchestrator/dag_executor.py] utilizes ContextVariablesDTO, GlobalContextVarsDTO, and NodeExecutionUpdateDTO, eradicating 8 naked dict instances and unchecked dictionary spreads.</item>
    <item>StrategyContext in @[backend_v2/services/orchestrator/strategies/base.py] encapsulates typed GlobalContextVarsDTO and ContextVariablesDTO.</item>
    <item>Logic strategy in @[backend_v2/services/orchestrator/strategies/logic.py] operates with LogicNodeStateDTO and LogicEvaluationContextDTO without naked dictionaries.</item>
    <item>Sensor validation context in @[backend_v2/services/orchestrator/extractive_sensor_service.py] is encapsulated into frozen SensorValidationContextDTO.</item>
    <item>Silent exception swallowing is eradicated across context_router.py, extraction_schema_factory.py, matrix_explanation_service.py, and rag_preflight_service.py in favor of RFC 7807 Fail-Fast exceptions.</item>
    <item>FinOps trace analyzer in @[backend_v2/utils/finops_trace_analyzer.py] returns FinOpsMonitorSummaryDTO and FinOpsFinalizeSummaryDTO.</item>
    <item>MCP client and tools in @[backend_v2/services/mcp/tavily_search_client.py] and @[backend_v2/services/mcp/tools/tavily.py] utilize TavilySearchRequestDTO and MCPToolDeclarationDTO.</item>
    <item>Studio services @[backend_v2/services/studio/simulation_service.py] and @[backend_v2/services/studio/workflow_service.py] operate with ExecutionInputsDTO and dict[str, str] mappings.</item>
    <item>Dynamic create_model field synthesis in @[backend_v2/core/registry.py] and @[backend_v2/services/orchestrator/extraction_schema_factory.py] is replaced with static schemas utilizing typed collections.</item>
    <item>Unit test suites (@[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py], @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py], @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py], @[backend_v2/tests/unit/services/test_llm_hallucination_repro.py], @[backend_v2/tests/unit/test_schema_factory_alias.py], @[backend_v2/tests/unit/test_llm_context_bounds.py], @[backend_v2/tests/unit/llm/test_client.py]) eradicate getattr and hasattr dynamic reflection calls in favor of direct dot-notation access.</item>
    <item>Automated quality gates pass: uv run python scripts/backend_audit_loop.py on all touched modules with greater than 90% coverage and zero fatal AST guardrail violations.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_structured_forensic_quotes.md]</knowledge_item>
    <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
    <knowledge_item>@[ki_cartesian_variance_and_authenticity.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tda_best_of_three_flash.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_transient_error_resilience.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <forbidden>Do NOT modify SDUI mapper services, SDUI presentation models, or legacy render services during Phase 5 (strictly quarantined for Phase 6).</forbidden>
    <forbidden>Do NOT modify flattener.py during Phase 5 (strictly quarantined for Phase 6).</forbidden>
    <forbidden>Do NOT modify Flutter client dart models during Phase 5 (strictly quarantined for Phase 6).</forbidden>
    <forbidden>Do NOT alter TinyDB locking logic in wrapper.py (quarantined for EPIC 151 PostgreSQL migration).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/models/dtos/prompt.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/context_variables.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/node_execution.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/sensor.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/finops.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/mcp.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler.py#L197-L409]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py#L77-L93]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L20-L153]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py#L112-L305]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#L255-L330]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py#L59-L225]</backend>
    <backend>@[backend_v2/services/orchestrator/state_reducer.py#L12-L55]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py#L84-L310]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py#L43-L77]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/logic.py#L28-L218]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py#L90-L645]</backend>
    <backend>@[backend_v2/services/orchestrator/extractive_sensor_service.py#L480-L510]</backend>
    <backend>@[backend_v2/services/orchestrator/context_router.py#L70-L105]</backend>
    <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py#L24-L181]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py#L215-L230]</backend>
    <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py#L60-L87]</backend>
    <backend>@[backend_v2/services/orchestrator/ast_evaluator.py#L58-L75]</backend>
    <backend>@[backend_v2/utils/finops_trace_analyzer.py#L59-L170]</backend>
    <backend>@[backend_v2/services/mcp/tavily_search_client.py#L74-L95]</backend>
    <backend>@[backend_v2/services/mcp/tools/tavily.py#L25-L54]</backend>
    <backend>@[backend_v2/services/studio/simulation_service.py#L335-L360]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py#L355-L375]</backend>
    <backend>@[backend_v2/core/registry.py#L510-L545]</backend>
  </touched_artifacts>

  <step id="5.1" name="Prompt Compiler, Adapter &amp; Prompt Mapping DTO Hardening">
    <action>Create [NEW] @[backend_v2/models/dtos/prompt.py] defining PromptMappingDTO and LLMContextDataDTO under ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>In PromptMappingDTO, encapsulate mappings: Annotated[dict[str, str], Field(default_factory=dict, description="Map of logical input names to state paths")].</action>
    <action>In LLMContextDataDTO, define typed attributes: raw_inputs: dict[str, IngressInputValue] | None = None, metadata: ExecutionMetadata | None = None, execution_time: datetime.datetime | None = None, inputs: dict[str, DomainInputValue] | None = None.</action>
    <action>In @[backend_v2/services/orchestrator/prompt_compiler.py], refactor _extract_value_from_state: eradicate current = current.model_dump()[part] and delegate dot-notation traversal directly to math_utils.resolve_dot_notation(state_data, path).</action>
    <action>In @[backend_v2/services/orchestrator/prompt_compiler.py], eradicate defensive exception fallback blocks (lines 389, 399, 405) in favor of Fail-Fast validation raising AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>In @[backend_v2/services/orchestrator/prompt_compiler.py] and @[backend_v2/services/orchestrator/prompt_compiler_adapter.py], update build_xml_context signature to accept input_mappings: PromptMappingDTO | dict[str, str] and state_data: ExecutionInputsDTO | dict[str, Any].</action>
    <constraint invariant="zero_service_layer_fallbacks">Never convert Pydantic models to dictionaries solely to traverse paths. Rely strictly on math_utils.resolve_dot_notation.</constraint>
  </step>

  <step id="5.2" name="LLM Execution Time Resolver, Context Builder, Source Document Packer &amp; Prompt Factory Hardening">
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py], accept ExecutionInputsDTO, ExecutionMetadata, and LLMContextDataDTO. Resolve timestamp strictly via inputs.document_date without fallback loops. Eradicate all 4 except AttributeError, TypeError: pass blocks and chained .get calls.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py], accept typed HookState and return tuple[LLMContextDataDTO, PromptMappingDTO]. Access dynamic inputs via static dot-notation on HookState.inputs. Eradicate lines 252-259 raw_inputs dictionary fallbacks and line 137 except AttributeError, TypeError.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py], eradicate line 310 except TypeError, ValueError: text_content = "" fallback. Enforce Fail-Fast raising AppException(ErrorCodes.VALIDATION_FAILED) upon serialization error.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py], update PromptFactory.build to accept input_mappings: PromptMappingDTO | dict[str, str], llm_context_data: LLMContextDataDTO, and global_context_vars: GlobalContextVarsDTO | None.</action>
    <constraint invariant="universal_fail_fast">Never silently assign an empty string upon payload serialization failure in source document packer.</constraint>
  </step>

  <step id="5.3" name="State Reducer Modernization &amp; DAG Executor DTO Hardening">
    <action>Create [NEW] @[backend_v2/models/dtos/context_variables.py] defining ContextVariablesDTO with frozen strict immutability, encapsulating typed fields: global_atom_blackboard, matrix_reducer_output, report_context, step_detector, evaluated_matrices, and variables: dict[str, DomainInputValue].</action>
    <action>Create [NEW] @[backend_v2/models/dtos/node_execution.py] defining NodeExecutionUpdateDTO, LogicNodeStateDTO, and LogicEvaluationContextDTO under ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>In @[backend_v2/services/orchestrator/state_reducer.py], eradicate merge_dynamic_inputs() and delete the 3 # noqa: QGR012 AST suppressions. Implement pure immutable merge_execution_inputs(base: ExecutionInputsDTO, delta: ExecutionInputsDTO) -> ExecutionInputsDTO using .model_copy(update=...).</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], refactor commit_trace and execute to accept context_variables: ContextVariablesDTO | None and global_context_vars: GlobalContextVarsDTO | None.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], eradicate 8 naked dict instances: update_data -> NodeExecutionUpdateDTO, resolved_global_vars -> GlobalContextVarsDTO, resolved_context_vars -> ContextVariablesDTO, delta_content -> StepOutputContentDTO, step_generated_schemas -> GeneratedSchemaManifestDTO.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], eradicate unchecked dictionary spread operations in node execution preparation, updating context variables via ContextVariablesDTO.with_update.</action>
    <constraint invariant="no_naked_dicts_in_state">Never use raw dictionary bags for intermediate execution variables in DAGExecutor.</constraint>
  </step>

  <step id="5.4" name="Node Execution Strategies, Logic Strategy &amp; Extractive Sensor Service Refactoring">
    <action>Create [NEW] @[backend_v2/models/dtos/sensor.py] defining SensorValidationContextDTO with fields: sub_task: str, execution_id: str, step_id: str.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/base.py], update StrategyContext: global_context_vars: GlobalContextVarsDTO = Field(default_factory=GlobalContextVarsDTO) and context_variables: ContextVariablesDTO = Field(default_factory=ContextVariablesDTO). Replace merge_dynamic_inputs calls with merge_execution_inputs.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/logic.py], replace current_state: dict[str, Any] with LogicNodeStateDTO, replace merge_dynamic_inputs with merge_execution_inputs, and replace safe_context: dict[str, Any] with LogicEvaluationContextDTO.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py], eradicate duck-typing unpacking of hook_state.inputs and global_vars. Eradicate except (TypeError, ValueError): pass and except (AttributeError, TypeError): pass (lines 117, 126, 155, 604); raise structured AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>In @[backend_v2/services/orchestrator/extractive_sensor_service.py], line 486, replace validation_context: dict[str, Any] with strongly typed SensorValidationContextDTO.</action>
    <constraint invariant="universal_fail_fast">Never silently pass on TypeError or ValueError during LLM strategy execution.</constraint>
  </step>

  <step id="5.5" name="Orchestrator Helper &amp; Factory Exception Hardening">
    <action>In @[backend_v2/services/orchestrator/context_router.py], eradicate except TypeError, KeyError: pass (line 87) and duck-typing checks on trace events. Enforce Fail-Fast validation raising AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>In @[backend_v2/services/orchestrator/extraction_schema_factory.py], eradicate except (AttributeError, TypeError): pass (lines 40, 69); raise AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>In @[backend_v2/services/orchestrator/matrix_explanation_service.py], eradicate except (AttributeError, TypeError): pass (line 227); raise AppException(ErrorCodes.VALIDATION_FAILED).</action>
    <action>In @[backend_v2/services/orchestrator/rag_preflight_service.py], eradicate except (AttributeError, TypeError, ValueError): pass (line 84). Inspect validated ExecutionInputsDTO directly.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every exception raised must be preceded by structured logging with ErrorCodes and parameter context.</constraint>
  </step>

  <step id="5.6" name="Ingress, Evaluator, FinOps &amp; MCP Tool DTO Modernization">
    <action>Create [NEW] @[backend_v2/models/dtos/finops.py] defining FinOpsMonitorSummaryDTO (total_duration_ms: int, total_calls: int, alerts: list[str]) and FinOpsFinalizeSummaryDTO (structural_warnings: list[str], mcp_warnings: list[str], hashing_warnings: list[str], healing_cost_events: list[dict[str, str | float]], total_usd_cost: float).</action>
    <action>Create [NEW] @[backend_v2/models/dtos/mcp.py] defining TavilySearchRequestDTO and MCPToolDeclarationDTO under ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>In @[backend_v2/services/orchestrator/ast_evaluator.py], type facts parameter as Mapping[str, bool | str | State].</action>
    <action>In @[backend_v2/utils/finops_trace_analyzer.py], update analyze_monitor_state and finalize_execution signatures to return FinOpsMonitorSummaryDTO and FinOpsFinalizeSummaryDTO.</action>
    <action>In @[backend_v2/services/mcp/tavily_search_client.py], line 81, construct TavilySearchRequestDTO and serialize via .model_dump(mode="json") at the HTTP boundary.</action>
    <action>In @[backend_v2/services/mcp/tools/tavily.py], line 25, return MCPToolDeclarationDTO.</action>
    <action>In @[backend_v2/services/studio/simulation_service.py], update simulate_step to accept mock_inputs: ExecutionInputsDTO.</action>
    <action>In @[backend_v2/services/studio/workflow_service.py], line 361, type new_mappings: dict[str, str].</action>
    <action>Reconciliation check: verify that smart_ingress_resolver.py was pre-resolved in Phase 2 with ResolvedIngressDTO.</action>
    <constraint invariant="strict_pydantic_v2_rust">Enforce frozen strict Pydantic V2 models on all MCP tool definitions and FinOps analytics.</constraint>
  </step>

  <step id="5.7" name="Dynamic Schema Factory &amp; Registry Reflection Eradication">
    <action>In @[backend_v2/core/registry.py], lines 526-540, replace dynamic create_model(f"MatrixExtraction_{matrix_id}", ...) field synthesis with static schemas utilizing typed collections: records: list[MatrixEvaluationRecordDTO] or dict[str, MatrixEvaluationDTO].</action>
    <action>In @[backend_v2/services/orchestrator/extraction_schema_factory.py], line 146, eradicate create_model(extracted_facts_dto_name, ...) in favor of static typed extraction facts models.</action>
    <constraint invariant="ban_heuristic_identifier_matching">Eradicate runtime chameleon classes with dynamic field names that force callers to use getattr reflection.</constraint>
  </step>

  <step id="5.8" name="Unit Test Suite Migration &amp; Co-Located Orchestration Reflection Eradication">
    <action>Update @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py] to test merge_execution_inputs with ExecutionInputsDTO instances instead of raw dictionaries.</action>
    <action>Update @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py] and @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py] to test PromptMappingDTO and dot-notation resolution with zero reflection.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_schema_matrix_bug.py], line 77, eradicate getattr(matrices, matrix_block_raw["id"]); assert directly via typed model access.</action>
    <action>In @[backend_v2/tests/unit/services/test_llm_hallucination_repro.py], line 26, eradicate getattr(result, "blk_2cbe96bffde04571", None).</action>
    <action>In @[backend_v2/tests/unit/test_schema_factory_alias.py], eradicate dynamic getattr reflection calls.</action>
    <action>In @[backend_v2/tests/unit/test_llm_context_bounds.py], lines 190-208 and 260-274, eradicate 6 getattr/hasattr calls on trace events; assert directly via TraceEvent.execution_trace and error_trace.error_code.</action>
    <action>In @[backend_v2/tests/unit/llm/test_client.py], line 138, eradicate hasattr(last_msg, "content"); access last_msg.content directly.</action>
    <action>Update @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py] and @[backend_v2/tests/unit/utils/test_finops_trace_analyzer.py] to assert typed DTO outputs.</action>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test</action>
    <constraint invariant="anti_tdd_trap">Never preserve legacy test assertions expecting raw dictionaries or dynamic getattr reflection.</constraint>
  </step>

  <pre_implementation_technical_debt_cleanups>
    <cleanup id="DEBT-5.1">Remove 3 # noqa: QGR012 suppressions in @[backend_v2/services/orchestrator/state_reducer.py#L42-L54].</cleanup>
    <cleanup id="DEBT-5.2">Remove line 310 empty string fallback in @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py#L307-L312].</cleanup>
    <cleanup id="DEBT-5.3">Remove all 4 silent except AttributeError, TypeError: pass blocks in @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py#L41-L151].</cleanup>
    <cleanup id="DEBT-5.4">Remove silent except blocks in @[backend_v2/services/orchestrator/context_router.py#L77-L88], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L31-L59], @[backend_v2/services/orchestrator/matrix_explanation_service.py#L215-L228], @[backend_v2/services/orchestrator/rag_preflight_service.py#L62-L83], and @[backend_v2/services/orchestrator/strategies/llm.py#L117-L137,L627-L636].</cleanup>
    <cleanup id="DEBT-5.5">Eradicate getattr and hasattr reflection in test files: test_schema_matrix_bug.py#L75-L77, test_llm_hallucination_repro.py#L26, test_schema_factory_alias.py#L33, test_llm_context_bounds.py#L190-L208,L260-L278, and test_client.py#L138.</cleanup>
    <cleanup id="DEBT-5.6">Eradicate model_dump() dictionary laundering and fallback json.dumps() in @[backend_v2/services/orchestrator/prompt_compiler.py#L327-L407].</cleanup>
    <cleanup id="DEBT-5.7">Eradicate current_state: dict[str, Any] and naked dictionary returns in @[backend_v2/services/orchestrator/strategies/logic.py#L73-L75], @[backend_v2/services/orchestrator/ast_evaluator.py#L60], @[backend_v2/utils/finops_trace_analyzer.py#L59,L116], @[backend_v2/services/mcp/tavily_search_client.py#L81], @[backend_v2/services/mcp/tools/tavily.py#L25], @[backend_v2/services/studio/simulation_service.py#L339], and @[backend_v2/services/studio/workflow_service.py#L361].</cleanup>
  </pre_implementation_technical_debt_cleanups>

  <atomic_git_commit>
    <command>git add backend_v2/models/dtos/prompt.py backend_v2/models/dtos/context_variables.py backend_v2/models/dtos/node_execution.py backend_v2/models/dtos/sensor.py backend_v2/models/dtos/finops.py backend_v2/models/dtos/mcp.py backend_v2/services/orchestrator/ backend_v2/utils/finops_trace_analyzer.py backend_v2/services/mcp/ backend_v2/services/studio/ backend_v2/core/registry.py backend_v2/tests/unit/</command>
    <message>feat(orchestrator): harden prompt compiler, state reducer, and dag executor dtos</message>
    <description>
- Add frozen DTOs: PromptMappingDTO, LLMContextDataDTO, ContextVariablesDTO, NodeExecutionUpdateDTO, LogicNodeStateDTO, LogicEvaluationContextDTO, SensorValidationContextDTO, FinOpsMonitorSummaryDTO, FinOpsFinalizeSummaryDTO, TavilySearchRequestDTO, MCPToolDeclarationDTO.
- Eradicate model_dump dictionary laundering in prompt_compiler.py; delegate to math_utils.resolve_dot_notation.
- Replace merge_dynamic_inputs and 3 QGR012 suppressions in state_reducer.py with typed merge_execution_inputs.
- Eradicate 8 naked dict instances in dag_executor.py and type StrategyContext with GlobalContextVarsDTO and ContextVariablesDTO.
- Eradicate silent exception swallowing across execution_time_resolver.py, source_document_packer.py, context_router.py, extraction_schema_factory.py, matrix_explanation_service.py, and rag_preflight_service.py.
- Modernize unit test suites by eliminating getattr and hasattr dynamic reflection in test_schema_matrix_bug.py, test_llm_hallucination_repro.py, test_schema_factory_alias.py, test_llm_context_bounds.py, and test_client.py.
    </description>
  </atomic_git_commit>

  <validation_gate>
    <action>Run backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test</action>
    <action>Run unit test suites: uv run pytest backend_v2/tests/unit/services/orchestrator/ backend_v2/tests/unit/utils/test_finops_trace_analyzer.py backend_v2/tests/unit/test_llm_context_bounds.py backend_v2/tests/unit/llm/test_client.py -v</action>
    <action>Run AST guardrail scan: uv run python scripts/audit_dict_eradication.py</action>
  </validation_gate>
</execution_protocol>
