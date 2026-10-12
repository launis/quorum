# Phase 3: Autonomous Causal Discovery Engine Implementation & Tests

**Overview:** Implement the autonomous `CausalDiscoveryEngine` complying strictly with the `ExecutionEngine` Protocol. Build pre-flight ingress validation enforcing Fail-Fast on empty documents (`ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT`) and extraction starvation (`ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION`), Four-Layer Clean Stack prompt compilation with static caching topology, exact lexical quote anchoring via `str.find`, two-pass claim extraction, explicit parameter injection into `SlidingWindowLinker`, and wave-based graph evaluation via `TopologicalEvaluator` with thread-isolated cycle defense and bounded $O(V+E)$ traversal guards. Re-export `CausalDiscoveryEngine` in `backend_v2/services/orchestrator/engines/__init__.py` and build comprehensive ISTQB unit tests in `backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py`.

**Source:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md] Section 3, Phase 3: Engine Implementation & Orchestrator Wiring (Standalone & Optional Fusion)

**Target Files:**
- `[NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/engines/__init__.py]`
- `[NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`, `@[backend_v2/services/orchestrator/engines/__init__.py]` | Reading `request.payload` instead of `request.global_source_text`. Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, or mutating existing step execution states in-place. Calling `linker.link_graph(extracted_atoms, paragraph_blocks)` with invalid parameters. Unquarantined cycle traversals causing recursion stack overflow. Fuzzy string matching (RapidFuzz, Levenshtein, regex) for quotes. Permitting phantom edges violating `CausalGraphPayloadDTO` referential integrity. Dropping sub-step token usage counts. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` cleanly implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult`, re-exported in `__all__`. Pre-flight validation on `request.global_source_text` raising `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)` on empty or whitespace text. Four-Layer Clean Stack prompt compilation. Exact physical quote anchoring via `str.find` against indexed paragraph blocks `[B0]...[Bn]` (dropping invalid claims; raising `CAUSAL_DISCOVERY_DATA_STARVATION` if 0 valid claims remain). Explicit settings parameter injection into `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. Wave execution via `TopologicalEvaluator`: detecting cycles, setting `cycle_detected=True`, marking cyclic nodes `SYSTEM_ERROR` with `CYCLIC_DEPENDENCY_DETECTED`, quarantining cyclic nodes from blame propagation, and enforcing `visited: set[str]` accumulators terminating in O(V+E) time with recursion depth bounded by `len(self.nodes)`. Token usage aggregated across all phases. Return `EngineExecutionResult(results=[], hydrated_references={}, synthesis_output=payload, usage=total_usage)`. | Persistent graph database engines (Neo4j, NetworkX), speculative actor frameworks, and branching fallback methods. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops, empty documents, and extraction starvation; `backend_audit_loop.py`. |
| `[NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]` | Happy-path-only tests, unverified mocks, theater mocks (`mock.execute.return_value = X; assert res == X`), raw dictionary test fixtures violating AST guardrail `QGR029`, and blanket `# noqa` or `# type: ignore` suppressions. | Comprehensive ISTQB test suite: equivalence partitioning, boundary value analysis, negative partitions (empty document, whitespace-only, claim extraction starvation, circular argument loops A->B->A, single isolated atom, disconnected subgraphs, exact quote match, hallucinated quote mismatch). All test fixtures use strongly typed Pydantic V2 DTOs with zero raw dictionaries. | Flaky live LLM calls in unit test suite. Uses typed mock responses via `LLMClient` and mocked task executor. | `backend_audit_loop.py` exiting 0 with 100% test pass rate across all test partitions. |

## Pre-Implementation Cleanups

1. `[CLEANUP]` Verify prerequisite contracts from Phase 2: `CausalNodeDTO` in `@[backend_v2/models/dtos/causal_discovery.py#L28-L51]`, `CausalGraphPayloadDTO` in `@[backend_v2/models/dtos/causal_discovery.py#L64-L108]`, `StepType.CAUSAL_DISCOVERY` in `@[backend_v2/models/enums.py]`, `ErrorCodes` in `@[backend_v2/exceptions.py]`, and settings in `@[backend_v2/settings.py]`.
2. `[CLEANUP]` Eradicate hallucinated `request.payload` attribute reference; bind strictly to `request.global_source_text` from `@[backend_v2/models/dtos/engine.py#L60-L116]`.
3. `[CLEANUP]` Align `SlidingWindowLinker.link_graph` calling contract: pass `(executor=llm_executor, client=request.bound_client, atoms=extracted_atoms, ontology_map=ontology, progress_callback=...)` and unpack `(linked_nodes, usage_linking)` per `@[backend_v2/services/orchestrator/sliding_window_linker.py#L121-L347]`.
4. `[CLEANUP]` Mandate explicit `@property def telemetry_strategy_label(self) -> str: return "causal"` on `CausalDiscoveryEngine` to satisfy `ExecutionEngine` protocol in `@[backend_v2/services/orchestrator/engines/base.py#L11-L36]`.
5. `[CLEANUP]` Enforce referential integrity in `CausalGraphPayloadDTO` construction by filtering out phantom edges referencing unextracted node IDs before instantiating the DTO.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; PRE-IMPLEMENTATION CLEANUPS">
    <action>Look backward: Read the actual codebase state left by Phase 2. Verify `backend_v2/models/dtos/causal_discovery.py#L28-L51` exists with all 8 DTOs, `StepType.CAUSAL_DISCOVERY` is registered in `backend_v2/models/enums.py`, explicit causal error codes exist in `backend_v2/exceptions.py`, and settings are defined in `backend_v2/settings.py`.</action>
    <action>Look forward: Verify if standalone `CausalDiscoveryEngine` execution produces defined `CausalGraphPayloadDTO` that can be directly consumed by Phase 4 DAG router and Phase 5 SDUI adapter.</action>
    <action>Pre-implementation cleanups: Verify that `request.global_source_text` is used (never `request.payload`), `SlidingWindowLinker.link_graph` is called with exact typed arguments `(executor, client, atoms, ontology_map)`, `TDAEngine` is never imported or subclassed, and all mock fixtures in tests use typed Pydantic V2 DTOs with zero raw dictionaries.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]) and the Tracker document (@[docs/epic/EPIC_154_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_154/03_phase3_plan.md] @[docs/epic/EPIC_154_tracker.md]`.</directive>
  </step>

  <dod_checklist>
    <item>CausalDiscoveryEngine implemented in backend_v2/services/orchestrator/engines/causal_discovery_engine.py complying with ExecutionEngine Protocol.</item>
    <item>telemetry_strategy_label property implemented returning "causal".</item>
    <item>Pre-flight check verifies text is non-empty, raising AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT) on empty/whitespace text.</item>
    <item>Four-Layer Clean Stack prompt compilation enforces static prefix, dynamic theory context, step protocol, and dynamic user payload at tail.</item>
    <item>Exact lexical anchoring enforced via str.find against indexed paragraph blocks [B0]...[Bn] (zero fuzzy matching).</item>
    <item>Claim extraction starvation check raises AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION) if TwoPassAtomizer extracts 0 claims from non-empty text.</item>
    <item>SlidingWindowLinker constructed with explicit settings parameters: window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap.</item>
    <item>TopologicalEvaluator wave execution detects circular reasoning, setting cycle_detected=True, marking cyclic nodes ExecutionStatus.SYSTEM_ERROR with CYCLIC_DEPENDENCY_DETECTED, quarantining cyclic nodes from blame propagation, and enforcing visited: set[str] accumulators terminating in O(V+E) time.</item>
    <item>CausalDiscoveryEngine re-exported in backend_v2/services/orchestrator/engines/__init__.py in __all__.</item>
    <item>ISTQB unit tests pass 100% in backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
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
    <forbidden>Do not import or subclass TDAEngine in CausalDiscoveryEngine.</forbidden>
    <forbidden>Do not use fuzzy string matching (RapidFuzz, Levenshtein, regex) for quote validation.</forbidden>
    <forbidden>Do not allow infinite recursion in cycle traversal; mandate visited set and depth bound.</forbidden>
    <forbidden>Do not exceed 250 lines in causal_discovery_engine.py.</forbidden>
    <forbidden>Do not access request.payload; access request.global_source_text strictly.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <backend>[NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/__init__.py]</backend>
    <backend>[NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]</backend>
  </touched_artifacts>

  <step id="3.1" name="PRE_FLIGHT_INGRESS_AND_ALIAS_ENGINE">
    <action>In [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py], implement CausalDiscoveryEngine(ExecutionEngine). In execute(request: EngineExecutionRequest), extract document text from request.global_source_text (strictly banning request.payload). Implement @property def telemetry_strategy_label(self) -> str: return "causal". Verify len(text.strip()) > 0; if empty or whitespace only, log structured error and raise AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT, "Causal discovery cannot execute on an empty text document.", status_code=status.HTTP_422_UNPROCESSABLE_CONTENT). Initialize AliasEngine and index paragraph blocks [B0]...[Bn].</action>
    <constraint invariant="universal_fail_fast">Fail-Fast immediately before calling LLM or tokenization.</constraint>
  </step>

  <step id="3.2" name="FOUR_LAYER_CLEAN_STACK_PROMPT_COMPILATION">
    <action>In [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py], compile prompts through the Four-Layer Clean Stack hierarchy: Layer 1 static system directives prefix for 100% caching efficiency; Layer 2 dynamic theory context in &lt;theory_context&gt; compiled from configured PromptBlocks; Layer 3 step extraction protocol; Layer 4 dynamic user payload with atom aliasing (a0, a1) and paragraph indices [B0]...[Bn] at the tail.</action>
    <constraint invariant="high_fidelity_prompting_and_caching">Prefix must remain 100% static across runs for context caching efficiency.</constraint>
  </step>

  <step id="3.3" name="TWO_PASS_ATOMIZATION_AND_LEXICAL_ANCHORING">
    <action>In [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py], instantiate LLMTaskExecutor(self._compiler, default_validation_context={"execution_id": request.context.execution_id, "step_id": request.step.id}). Instantiate TwoPassAtomizer(llm_executor). Execute TwoPassAtomizer.execute_phase_0 to construct GlobalOntologyMap and capture usage_p0, then execute TwoPassAtomizer.execute_phase_1 to generate independent ExtractedAtom instances and capture usage_p1. Validate every extracted quote strictly via str.find against indexed paragraph blocks [B0]...[Bn] (or request.global_source_text); fuzzy matching is strictly banned. Drop invalid claims that fail lexical verification. If extraction yields 0 valid argument claims from non-empty text, raise AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION, "Causal discovery extracted 0 valid argument propositions from non-empty text.", status_code=status.HTTP_422_UNPROCESSABLE_CONTENT).</action>
    <constraint invariant="strict_physical_anchoring_mandate">Exact lexical validation via str.find; fuzzy matching is strictly banned.</constraint>
  </step>

  <step id="3.4" name="SLIDING_WINDOW_GRAPH_CONSTRUCTION">
    <action>In [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py], construct SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap). Call await linker.link_graph(executor=llm_executor, client=request.bound_client, atoms=extracted_atoms, ontology_map=ontology, progress_callback=...) to generate directed LinkedAtomGraph nodes and capture usage_linking.</action>
    <constraint invariant="the_zero_compromise_pledge">Preserve default parameters of SlidingWindowLinker for TDA callers.</constraint>
  </step>

  <step id="3.5" name="TOPOLOGICAL_WAVE_EXECUTION_AND_CYCLE_DEFENSE">
    <action>In [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py], pass LinkedAtomGraph nodes to TopologicalEvaluator for wave evaluation, short-circuit cascades, and thread-isolated cycle detection. If circular dependency is detected, set cycle_detected=True, mark cyclic nodes with ExecutionStatus.SYSTEM_ERROR and reason CYCLIC_DEPENDENCY_DETECTED, quarantine cyclic nodes from blame propagation, and enforce visited: set[str] accumulators terminating in O(V+E) time with absolute recursion depth bounded by len(self.nodes) across all graph traversals.</action>
    <action>Aggregate total token usage: total_usage = usage_p0 + usage_p1 + usage_linking.</action>
    <action>Construct and return EngineExecutionResult wrapping CausalGraphPayloadDTO, strictly verifying referential integrity by omitting phantom edges referencing unextracted nodes.</action>
    <action>In [MODIFY] @[backend_v2/services/orchestrator/engines/__init__.py], import CausalDiscoveryEngine and re-export in __all__.</action>
    <constraint invariant="topological_engine">Reuses TopologicalEvaluator SSOT; cycle detection must never trigger infinite loop or deadlock.</constraint>
  </step>

  <step id="3.6" name="ISTQB_UNIT_TEST_IMPLEMENTATION">
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py], create comprehensive ISTQB test suite verifying: test_causal_discovery_empty_document_raises_app_exception, test_causal_discovery_data_starvation_raises_app_exception, test_causal_discovery_circular_graph_marks_system_error, test_causal_discovery_single_atom_zero_edges, test_causal_discovery_exact_quote_anchoring_passes, test_causal_discovery_inexact_quote_fails_validation, test_causal_discovery_telemetry_strategy_label, test_causal_discovery_token_usage_aggregated, test_causal_discovery_phantom_edges_filtered.</action>
    <constraint invariant="universal_fail_fast">All test fixtures must use typed Pydantic V2 DTOs; zero naked dictionaries.</constraint>
  </step>

  <test_contracts>
    <test name="test_causal_discovery_empty_document_raises_app_exception" category="error_path">
      <input>EngineExecutionRequest with empty or whitespace document text</input>
      <expected>raises AppException with ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT</expected>
    </test>
    <test name="test_causal_discovery_data_starvation_raises_app_exception" category="error_path">
      <input>EngineExecutionRequest with text that yields 0 extracted claims</input>
      <expected>raises AppException with ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION</expected>
    </test>
    <test name="test_causal_discovery_circular_graph_marks_system_error" category="boundary">
      <input>Graph linking resulting in directed cycle (A -&gt; B -&gt; A)</input>
      <expected>cycle_detected == True, cyclic nodes marked SYSTEM_ERROR with CYCLIC_DEPENDENCY_DETECTED, zero unhandled recursion</expected>
    </test>
    <test name="test_causal_discovery_single_atom_zero_edges" category="boundary">
      <input>Text yielding exactly 1 extracted claim</input>
      <expected>returns CausalGraphPayloadDTO with 1 node, 0 edges, cycle_detected == False, node in isolated_node_ids</expected>
    </test>
    <test name="test_causal_discovery_exact_quote_anchoring_passes" category="positive">
      <input>Extracted claim with quote exactly matching source paragraph</input>
      <expected>quote validates via str.find and node is successfully constructed</expected>
    </test>
    <test name="test_causal_discovery_inexact_quote_fails_validation" category="error_path">
      <input>Extracted claim with hallucinated quote not in source text</input>
      <expected>raises SemanticEvidenceError or drops invalid proposition</expected>
    </test>
    <test name="test_causal_discovery_telemetry_strategy_label" category="positive">
      <input>CausalDiscoveryEngine instance inspection</input>
      <expected>telemetry_strategy_label == 'causal'</expected>
    </test>
    <test name="test_causal_discovery_token_usage_aggregated" category="positive">
      <input>Engine execution with mocked phases returning TokenUsage</input>
      <expected>result.usage matches sum of Phase 0, Phase 1, and linking token counts</expected>
    </test>
    <test name="test_causal_discovery_phantom_edges_filtered" category="boundary">
      <input>Linker producing edge with target or source not in extracted nodes</input>
      <expected>phantom edge is pruned before CausalGraphPayloadDTO construction, preserving referential integrity</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/causal_discovery_engine.py --test</action>
    <action>Execute: uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test</action>
    <action>Execute: grep_search for "TDAEngine" in backend_v2/services/orchestrator/engines/causal_discovery_engine.py confirming zero coupling</action>
  </validation_gate>
</execution_protocol>

