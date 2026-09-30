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
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# SYSTEM 2 ARCHITECTURAL AUDIT REPORT: EPIC 154
**Target Document:** @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]  
**Auditor:** Principal Enterprise Architect & System Red Team  
**Audit Tier:** Tier 0 (Epic Research, Falsification & Architectural Hardening)  
**Status:** ARCHITECTURALLY VERIFIED & HARDENED (READY FOR TIER 1 PLANNING)

---

## 1. Executive Summary & Verdict

EPIC 154 specifies the **Dynamic Causal Discovery Engine** (`CausalDiscoveryEngine`), establishing an autonomous, neuro-symbolic argument mining and causal discovery framework within Quorum. The engine operates in 100% standalone mode on free-form unstructured documents (without criteria matrices) or as an upstream structural feeder (Phase 1A Discovery -> Phase 1B TDA Normative Evaluation) via Studio-driven chaining (`Step.causal_source_step_id`).

### Audit Summary:
1. **Mathematical Invariant Compliance:** 100% verified. The architecture adheres to Kahn's wave-based topological evaluation, Local Causal Markov conditions, thread-isolated cycle detection, and strict Fail-Fast error semantics.
2. **Tripartite Pipeline Sovereignty:** Fully preserved. Phase 1 produces immutable Pydantic V2 DTOs (`CausalGraphPayloadDTO`, `CausalTdaFusionResultDTO`), Phase 2 synthesizes presentation models without mutating graph state, and Phase 3 projects Dumb Painter Server-Driven UI cards (`SduiCausalGraphBlock`) identically across Flutter and A4 PDF surfaces.
3. **Zero Permissive Typing & Anti-Tuple Enforcement:** 8 dedicated Pydantic V2 DTOs replace all prospective dictionary passing and anonymous tuples. Pre-existing technical debt in `TwoPassAtomizer._calculate_packets` (returning anonymous 3-tuples) is quarantined and resolved in Phase 1 before new logic is implemented.
4. **Studio-Driven Parameterization:** Granular micro-toggles have been pruned in favor of a single SSOT selector (`causal_display_mode: CausalDisplayMode` = `EXECUTIVE` / `DETAILED`), preserving streamlined Quorum Studio UX.
5. **Architectural Hardening Mutation:** Section 2.1 has been updated with an exact Quantitative Scope Validation Table (42 target files: 8 new, 34 modified, plus 5 context files), and Section 4.1 was corrected to reference `BlueprintTransformer` (replaces outdated `BlueprintAssembler`).

---

## 2. Five-Axis System 2 Deconstruction Findings

### Axis 1: Target Scope & Boundary (Scope Inquisitor)
- **Target Boundary Isolation:** The Epic touches 42 discrete target files categorized into 9 architectural archetypes. The blast radius is strictly confined to:
  1. `services/orchestrator/engines/causal_discovery_engine.py` (New Engine)
  2. `models/dtos/causal_discovery.py` (New DTOs)
  3. `services/sdui/adapters/causal_graph_adapter.py` (New SDUI Adapter)
  4. DAG Orchestrator integration points (`dag_executor.py`, `step.py`, `settings.py`, `strategies/registry.py`, `strategies/llm.py`)
  5. Presentation and Export surfaces (`report_template.jinja2`, `sdui_causal_graph_widget.dart`, `causal_inspector_modal.dart`, `export_service.py`, `flattener.py`)
- **Blast Radius Quarantine:** `TDAEngine` execution paths are completely quarantined. `SlidingWindowLinker` constructor defaults (`window_size = 4, overlap = 2`) remain untouched; `CausalDiscoveryEngine` passes its settings explicitly (`SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`).

### Axis 2: Eradicated Duct-Tape (Duct-Tape Prosecutor - Under-Engineering Ban)
- **Elimination of Anonymous State Tuples:** `TwoPassAtomizer._calculate_packets` currently returns `list[tuple[str, str, list[str]]]`. This violates `ban_anonymous_state_tuples`. In Phase 1, it is refactored to return `list[ChunkPacketDTO]`.
- **Eradication of Magic Integers:** Hardcoded `packet_size = 50` in `two_pass_atomizer.py` is extracted to `Settings.two_pass_atomizer_packet_size`.
- **Strict Enum Hydration:** `Step.validate_step_consistency` comparisons `self.type == "llm"` and `self.type == "logic"` are replaced with typed enum comparisons `self.type == StepType.LLM` and `self.type == StepType.LOGIC`.
- **Zero Fallback Chaining:** If upstream discovery produces 0 valid nodes, the DAG executor raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)` rather than silently falling back to ungrounded raw text evaluation.

### Axis 3: Approved Best Practice (Type Constitutionalist - Sovereign Target)
- **Pydantic V2 Strictness:** All 8 causal DTOs enforce `ConfigDict(strict=True, extra="forbid", frozen=True)`.
- **Full-Duplex Serialization Parity:** `CausalDisplayMode` is synchronously mirrored across `backend_v2/models/enums.py` and `client_app_v2/lib/core/models/enums.dart` (`@JsonEnum()`).
- **Dynamic Theory Independence:** Theory grounding matrices (Toulmin, Walton, custom criteria) remain 100% dynamic domain entities configured in Quorum Studio and persisted in `seed_data.json`, with zero hardcoded backend rules.
- **Topological Evaluation SSOT:** Reuses `TopologicalEvaluator` with Kahn's wave-based topological sort, thread-isolated cycle detection via `asyncio.to_thread(list, nx.simple_cycles(g))`, and local causal Markov condition evaluation.

### Axis 4: Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
- **Pruned Speculative Domain Subclasses:** A separate `CausalStep` subclass was evaluated and pruned; the existing `Step` domain model is reused with a `StepType.CAUSAL_DISCOVERY` validation branch.
- **Pruned External Infrastructure:** Persistent graph databases (Neo4j, persistent NetworkX instances) were evaluated and pruned in favor of in-memory transient `LinkedAtomGraph` representations projected directly to DTOs.
- **Pruned Studio Micro-Toggles:** Four isolated micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) were pruned in favor of a single `causal_display_mode: CausalDisplayMode` selector.

### Axis 5: Fail-Fast Proof Anchor (Incorruptible Judge - Deterministic Verification)
- **Explicit ErrorCodes:** System crashes deterministically with `CAUSAL_DISCOVERY_EMPTY_DOCUMENT`, `CAUSAL_DISCOVERY_CYCLE_DETECTED`, and `CAUSAL_DISCOVERY_DATA_STARVATION`.
- **Exact Lexical Anchoring:** Quotes validate strictly via `str.find` on normalized paragraph blocks `[B0]...[Bn]`; fuzzy string matching is strictly forbidden.
- **Automated AST Quality Gates:** Verified via `scripts/audit_dict_eradication.py`, `scripts/audit_markdown_boundaries.py`, `scripts/backend_audit_loop.py`, and `scripts/flutter_audit_loop.py`.

---

## 3. Panel of Architects Evaluation

### 3.1 Global System Architect
- **Verdict:** APPROVED.
- **Rationale:** The Epic strictly respects the Single Source of Truth (SSOT), enforces the Zero-Fallback rule, prohibits legacy compatibility modes, and ensures that all operations are driven deterministically by typed DTO contracts. The caution box designating the Epic as `DISTANT FUTURE ROADMAP ONLY` safeguards active production branches from premature activation.

### 3.2 Backend & Data Architect
- **Verdict:** APPROVED.
- **Rationale:** The 8 new causal DTOs in `models/dtos/causal_discovery.py` adhere to strict Rust-based Pydantic V2 typing (`ConfigDict(strict=True, extra="forbid", frozen=True)`). No naked dictionaries leak into state. Pre-implementation cleanup in `TwoPassAtomizer` eliminates anonymous tuples, ensuring compliance with `ban_anonymous_state_tuples`.

### 3.3 SDUI & Frontend Architect
- **Verdict:** APPROVED.
- **Rationale:** The Dumb Painter contract is 100% honored. Client widgets perform zero semantic inference. Flutter and A4 PDF share identical presentation structures through `SduiCausalGraphBlock` (rendering the compact Unified Causal Action Card). Complex graph exploration is cleanly decoupled into `CausalInspectorModal`. All Dart 3 switch expressions in `BlockCardRegistry` and `sdui_blocks_renderer.dart` are accounted for.

### 3.4 AI & Orchestration Architect
- **Verdict:** APPROVED.
- **Rationale:** Prompt compilation strictly adheres to the Four-Layer Clean Stack hierarchy. Static ontology instructions are pinned to the prefix for 100% prompt caching efficiency. Epistemic theory context is loaded dynamically from configured PromptBlocks. User payloads and atom aliases (`a0`, `a1`) reside strictly at the tail. Evidence extraction enforces exact lexical `str.find` matching.

---

## 4. Anti-Happy-Path Falsification & Red-Teaming (Failure Modes)

### Failure Mode 1: Empty or Argument-Starved Input Document
- **Attack Scenario:** An evaluator submits a document containing purely descriptive text, tables, or empty whitespace with zero argument premises or claims.
- **Red-Team Failure Risk:** A naive implementation might execute LLM extraction passes, hallucinate empty atom lists, and pass an empty graph to downstream synthesis, causing division-by-zero errors in scoring engines or generating empty, broken SDUI cards.
- **Enforced Fail-Fast Defense:** `CausalDiscoveryEngine` performs pre-flight text validation. If the extracted premises count is 0 or input text length is below minimum thresholds, execution aborts immediately with structured logging and raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT, status_code=400)`.

### Failure Mode 2: Circular Argument Deadlock (Topological Deadlock)
- **Attack Scenario:** A persuasive or deceptive document contains circular reasoning (specifically: Claim A justifies Premise B, which in turn claims validity based on Claim A: A -> B -> A).
- **Red-Team Failure Risk:** A standard Kahn's algorithm or recursive topological traversal without cycle isolation deadlocks or hangs in an infinite loop, freezing worker threads.
- **Enforced Fail-Fast Defense:** `TopologicalEvaluator` runs thread-isolated cycle detection (`await asyncio.to_thread(list, nx.simple_cycles(g))`). If any cycle is detected, participating nodes are marked `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED`, setting `cycle_detected=True` in `CausalGraphPayloadDTO`. The wave loop completes gracefully without event loop stalls.

### Failure Mode 3: Downstream Fusion Starvation
- **Attack Scenario:** A workflow configures Phase 1A Causal Discovery followed by Phase 1B TDA Normative Evaluation via `causal_source_step_id`. Upstream discovery fails or yields 0 valid argument nodes.
- **Red-Team Failure Risk:** TDA engine executes against empty `shuffled_atoms`, generating a phantom scorecard with 0 scores.
- **Enforced Fail-Fast Defense:** `DAGExecutor` checks upstream node counts before dispatching Phase 1B. If upstream nodes are empty or upstream step status is failed, it triggers immediate Fail-Fast with `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION, status_code=422)`.

---

## 5. Scoped Boy Scout Technical Debt Inventory (Phase 1 Cleanups)

The following pre-existing technical debt items were identified in touched target files and MUST be resolved in Phase 1 before new business logic is introduced:

1. **`TwoPassAtomizer._calculate_packets` Anonymous Tuples:**
   - *File:* `backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71`
   - *Debt:* Returns `list[tuple[str, str, list[str]]]`, violating `ban_anonymous_state_tuples`.
   - *Resolution:* Encapsulate in `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`.
2. **`TwoPassAtomizer` Magic Number:**
   - *File:* `backend_v2/services/orchestrator/two_pass_atomizer.py#L50`
   - *Debt:* Default parameter `packet_size: int = 50` hardcodes chunk sizes.
   - *Resolution:* Bind to `get_settings().two_pass_atomizer_packet_size`.
3. **`Step.validate_step_consistency` String Literal Checks:**
   - *File:* `backend_v2/models/domain/step.py#L102, L115`
   - *Debt:* Evaluates `self.type == "llm"` and `self.type == "logic"`.
   - *Resolution:* Replace with typed enum comparisons `self.type == StepType.LLM` and `self.type == StepType.LOGIC`. Add branch for `StepType.CAUSAL_DISCOVERY`.
4. **`dag_executor.py` Heuristic Pre-Hook Inspection:**
   - *File:* `backend_v2/services/orchestrator/dag_executor.py#L184`
   - *Debt:* String check `"atom_flattening_hook" in step_def.pre_hooks` violates `ban_heuristic_identifier_matching`.
   - *Resolution:* Insert `StepType.CAUSAL_DISCOVERY` priority guard clause as the very first branch in `_resolve_execution_engine`.
5. **Blueprint Service Nomenclature Alignment:**
   - *File:* `backend_v2/services/blueprint.py#L52`
   - *Debt:* Epic Section 4.1 incorrectly referenced `BlueprintAssembler`.
   - *Resolution:* Synchronized to authoritative `BlueprintTransformer` in Epic text.

---

## 6. Authoritative 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Settings Configuration**<br>`@[backend_v2/settings.py#L54-L910]` | Magic constants in sliding window loops, hardcoded window sizes, fallback `getattr(settings, ...)` access. | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. Injected explicitly into `SlidingWindowLinker`. | Speculative per-domain sliding window overrides and dynamic runtime reload factories. | `Settings.model_validate({})` strict type validation in unit tests; `test_settings.py`. |
| **SSOT Enums & Parity**<br>`@[backend_v2/models/enums.py#L111-L115]`<br>`@[backend_v2/models/enums.py#L272-L285]`<br>`@[client_app_v2/lib/core/models/enums.dart#L354-L390]`<br>`@[backend_v2/tests/unit/test_enum_parity.py#L110-L112]` | Untyped string comparisons (`self.type == "llm"`), heuristic string matching, ad-hoc string literals for block types. | `StepType.CAUSAL_DISCOVERY = "causal_discovery"`. `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`, and `CausalDisplayMode(StrEnum)` strictly: `EXECUTIVE = "executive"`, `DETAILED = "detailed"`. Explicit ErrorCodes: `CAUSAL_DISCOVERY_EMPTY_DOCUMENT`, `CAUSAL_DISCOVERY_CYCLE_DETECTED`, `CAUSAL_DISCOVERY_DATA_STARVATION`. 1:1 Dart `@JsonEnum` parity. | Granular display mode permutations (isolated anti-fluff toggles, remediations toggles). | `test_enum_parity.py` verifying `TargetBlockType` and `CausalDisplayMode` parity; Dart compile-time enum switch exhaustion. |
| **Pre-Implementation Atomizer Cleanups**<br>`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]`<br>`@[backend_v2/models/dtos/dag_models.py#L18-L57]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]` | Returning anonymous 3-tuples (`tuple[str, str, list[str]]`) in `_calculate_packets` ("Tuple Hell"), hardcoded magic window sizes (`packet_size = 50`). | Encapsulate chunk packet bounds into typed immutable `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`. Bind `packet_size` to `get_settings().two_pass_atomizer_packet_size`. | Intermediate packet wrapper classes or custom iterator protocols. | `uv run python scripts/audit_dict_eradication.py` passing AST guardrails; unit tests in `test_two_pass_atomizer.py`. |
| **SlidingWindowLinker Isolation**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` | Hardcoded `window_size=4, overlap=2` constructor defaults mutating shared caller behavior. | **DO NOT** mutate constructor defaults in `SlidingWindowLinker.__init__`. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. | Binding constructor defaults to causal-specific settings. | Regression tests for existing `SlidingWindowLinker` callers; unit tests in `test_causal_discovery_engine.py`. |
| **Step Consistency & Strategy Registry**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]` | Raw string literal comparisons (`self.type == "llm"`, `self.type == "logic"`), duck-typing missing criteria blocks. | Explicit `StepType.LLM` and `StepType.LOGIC` enum comparisons. `StepType.CAUSAL_DISCOVERY` branch allowing empty `criteria_block_ids` while enforcing `extraction_protocol_block_id` and `cognitive_tier`. `NODE_STRATEGY_REGISTRY` maps `StepType.CAUSAL_DISCOVERY -> _build_llm_strategy`. | Separate `CausalStep` domain model subclass or parallel step validation pipeline. | Unit tests asserting `AppException` when `extraction_protocol_block_id` is missing; `backend_audit_loop.py`. |
| **`_resolve_execution_engine` Cleanup**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]` | **Pre-existing debt:** `"atom_flattening_hook" in step_def.pre_hooks` heuristic string matching (L184) violating `ban_heuristic_identifier_matching`. | `StepType.CAUSAL_DISCOVERY` guard clause placed as FIRST branch (before L179 block category check). | N/A | Unit test asserting `CausalDiscoveryEngine` returned for `StepType.CAUSAL_DISCOVERY` steps. |
| **LLM Strategy Telemetry & Dispatch**<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]` | Permissive model strategy fallback defaulting to `"prompt"`, ignoring engine ontology for causal discovery steps. | Set `meta_dict["model_strategy"] = "causal"` when `isinstance(self._engine, CausalDiscoveryEngine)`, recording exact telemetry metadata without string guessing. | Dynamic strategy router subclasses or parallel LLM execution strategies. | Unit tests verifying `_step_metadata.model_strategy == "causal"`. |
| **Causal Discovery DTOs**<br>[NEW] `@[backend_v2/models/dtos/causal_discovery.py]`<br>`@[backend_v2/models/dtos/step_output.py#L57-L71]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `StepPayloadValue` extended with `CausalGraphPayloadDTO` and `CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrails passing in audit loop. |
| **Fusion Chaining Contract**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]` | Heuristic step-order detection, runtime flag branching, unmapped document passing. | Studio-driven parameterization: explicit first-class field `Step.causal_source_step_id: str \| None = None` referencing upstream causal discovery step. DAG executor transforms upstream `CausalGraphPayloadDTO.nodes` to `ExtractedAtom` via `transform_causal_nodes_to_atoms` and feeds `request.shuffled_atoms`. | Nondeterministic engine picking, automatic graph merging without declared contracts. | Integration test in `test_causal_tda_fusion.py`. |
| **OutputProfile & Studio UX**<br>`@[backend_v2/models/domain/output_profile.py#L35-L346]`<br>`@[backend_v2/models/dtos/output_profile.py#L36-L260]`<br>`@[backend_v2/models/dtos/output_profile.py#L263-L475]`<br>`@[backend_v2/models/dtos/output_profile.py#L478-L621]`<br>`@[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]`<br>`@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]`<br>[NEW] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]`<br>`@[client_app_v2/lib/l10n/app_en.arb]`<br>`@[client_app_v2/lib/l10n/app_fi.arb]` | Micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`), missing Dart 3 switch branches in `BlockCardRegistry`, missing `.arb` localization keys, partial DTO mutation violating serialization parity. | Full-Duplex Serialization Parity: single SSOT field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` (create/update DTOs) and `causal_display_mode: CausalDisplayMode = CausalDisplayMode.EXECUTIVE` (domain/response DTOs). Exhaustive Dart 3 switch matching in `BlockCardRegistry`. Compile-time `.arb` localization. | Multi-tab studio configuration wizards and custom per-node styling controls. | `flutter_audit_loop.py` build runner verification; compile-time Freezed serialization tests. |
| **Causal Discovery Engine & Execution**<br>[NEW] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`<br>`@[backend_v2/services/orchestrator/engines/__init__.py]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]` | Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, mutating existing step states in-place without DTOs, routing through fallback branches. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` cleanly implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult`, re-exported in `__all__`. `NodeExecutor._resolve_execution_engine` routes via `step_def.type == StepType.CAUSAL_DISCOVERY` as FIRST branch. Sequential DAG chaining strictly via immutable DTOs and `causal_source_step_id`. | Dual execution buses, speculative actor frameworks, and persistent graph database storage engines. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops and empty documents; `test_causal_tda_fusion.py`. |
| **SDUI Model, Adapter & Blueprint**<br>`@[backend_v2/models/view/sdui.py#L563-L569, L797-L817]`<br>[NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`<br>`@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`<br>`@[backend_v2/services/blueprint.py#L52-L608]`<br>`@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]` | Client-side graph semantic calculation, client inferring root causes, generic raw JSON passing, missing `SduiBlockBase` polymorphism. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union. `AdapterContext` extended with typed `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` (in-memory only). `CausalGraphAdapter` transforms `causal_result` into `SduiCausalGraphBlock` adhering to `causal_display_mode`. 1:1 Freezed `@Freezed(unionKey: 'block_type')` Dart model. | Dynamic client-side layout calculators, SVG graph vector serialization over HTTP, multi-pass SDUI transformers. | `test_sdui_template_parity.py` and `test_sdui_semantic_parity.py` passing 100%. |
| **1:1 Presentation Parity (Flutter & PDF)**<br>`@[backend_v2/templates/report_template.jinja2#L87-L550]`<br>[NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`<br>[NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]` | Sprawling unreadable node graphs in PDF, inconsistent layout between PDF and screen, embedding heavy canvas tools into report print templates. | Identical Unified Causal Action Card in both Flutter and PDF: executive half-page critical causal path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote, prescriptive remediation. Deep interactive exploration decoupled strictly into `CausalInspectorModal`. | Embedded interactive JavaScript canvas in PDF, duplicate styling engines across platforms. | `test_sdui_semantic_parity.py` validating identical token and quote rendering across HTML/PDF and Flutter widgets. |
| **Tabular Export & Flat CSV Symmetry**<br>`@[backend_v2/services/export_service.py#L82-L301]`<br>`@[backend_v2/services/flattener.py#L24-L76]`<br>`@[backend_v2/models/dtos/flat_record.py#L17-L55]` | Multi-row hierarchical CSV headers, ragged nested Excel rows, missing causal columns in flat exports. | Excel sheets `Causal Graph` and `Causal Diagnostics` in `ExportService`. `FlatExecutionRecordDTO` receives typed scalar causal fields (`causal_node_count`, `causal_root_cause_count`, `causal_raw_penalty`, `causal_deduplicated_penalty`). `FlatFileService` outputs strictly 2-line flat CSV (line 1 = header names, line 2 = scalar values). | Pivot table generators, dynamic CSV dialect negotiation, secondary XLSX macro formatting. | Unit tests in `test_export_service.py` asserting exact column headers and row counts. |
| **Regression & Integration Testing**<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]`<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`<br>`@[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]`<br>`@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]`<br>`@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` | Happy-path-only tests, mocking persistence with static dummy dicts, unasserted mock calls. | Comprehensive ISTQB tests: equivalence partitioning, boundary value analysis, negative partitions (at least 2 negative tests per feature: empty text, single atom, circular dependency, disconnected subgraph). Integration tests for Phase 1A -> Phase 1B sequential chaining. | Flaky network integration tests, long-running end-to-end browser tests for unit logic. | `uv run python scripts/backend_audit_loop.py` exiting 0 with Ruff, MyPy, and Pytest all green. |

---

## 7. Context Rules & KI Governance Audit
- **Rules Verified (6):** `00-antigravity-core.md`, `01-python-backend.md`, `02_flutter_desktop.md`, `03_seed_vault.md`, `04_directory_reference.md`, `05_llm_architecture.md`.
- **Knowledge Items Verified (18):** `ki_god_code_prevention.md`, `ki_context_enriched_decompose_verify.md`, `ki_tripartite_pipeline_architecture.md`, `ki_topological_engine.md`, `ki_execution_engine_protocol.md`, `ki_zero_permissive_typing.md`, `ki_dumb_painter_sdui.md`, `ki_prompt_orchestration_and_matrix_evaluation.md`, `ki_unified_matrix_scoring_strictness.md`, `ki_desktop_pro_tool_studio_ux.md`, `ki_shared_storage_driver_architecture.md`, `ki_dag_engine_dto_projection_rules.md`, `ki_python_314_concurrency_strictness.md`, `ki_dual_axis_localization_architecture.md`, `ki_workflow_context_governance.md`, `ki_execution_record_ssot.md`, `ki_llm_extraction_architecture.md`, `ki_epic_lifecycle_workflow.md`.
- **Audit Conclusion:** Canonical `<required_context_rules>` block covers 100% of all affected domains. Zero missing KIs detected.

---

## 8. Final Recommendations & Transition to Tier 1

The Epic is **100% hardened, verified, and ready for breakdown into an architectural Implementation Plan**. 

**Mandatory Next Step:**  
Due to the heavy context consumption of this System 2 deconstruction, start a brand NEW chat session and execute:
```text
/tier1-planner @[c:\src\quorum\docs\epic\EPIC_154_Dynamic_Causal_Discovery_Engine.md]
```
