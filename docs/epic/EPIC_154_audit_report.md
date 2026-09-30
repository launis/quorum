# SYSTEM 2 ARCHITECTURAL RESEARCH & RED-TEAM AUDIT REPORT: EPIC 154
## Dynamic Causal Discovery Engine (Autonomous Empiric Root Cause Analysis)

**Audit Target:** `@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]`  
**Audit Protocol:** `/tier0-research-epic` (System 2 Deep Deconstruction, Red-Team Falsification & In-Place Hardening)  
**Evaluator:** Principal Enterprise Architect & System Red Team  
**Evaluation Date:** 2026-09-30  
**Overall Verdict:** 🟢 **PASSED & HARDENED FOR IMPLEMENTATION PLANNING**

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
</required_context_rules>

---

## 1. Executive Summary & Epic Classification

### 1.1 Executive Summary
A comprehensive System 2 architectural pre-implementation audit and red-teaming falsification was conducted on `@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]`. EPIC 154 specifies the architecture for an **Autonomous Dynamic Causal Discovery Engine** in Quorum. The engine ingests unstructured corporate documents, discovers empiric cause-and-effect relationships directly from evidence without requiring pre-compiled normative matrices, assembles an in-memory directed causal graph, isolates genuine root causes via topological wave evaluation, audits anti-fluff compliance, calculates prescriptive remediations, and dampens cascading secondary fault penalties.

The audit verified and hardened the architectural boundaries, eliminated agentic ambiguity, eradicated under-engineering duct-tape patterns, pruned speculative over-engineering, synchronized AST line ranges against the physical codebase, and locked strict 1:1 cross-language contracts between the Python backend (`backend_v2`) and Flutter client (`client_app_v2`).

### 1.2 Epic Classification & Architectural Sovereignty
- **Classification:** **Feature Epic (Roadmap Extension)** with strict **Phase 1 Scoped Boy Scout Refactoring**.
- **Architectural Boundary:** The Epic introduces a new autonomous execution engine (`CausalDiscoveryEngine`) adhering strictly to the `ExecutionEngine` protocol (`ki_execution_engine_protocol.md`). It functions either as a standalone Phase 1 engine OR as an upstream feeder to the existing normative `TDAEngine`.
- **Roadmap Isolation Invariant:** The Epic preserves existing production workflows intact. Zero modifications to `TDAEngine`'s strict `shuffled_atoms` contract are permitted. Existing execution paths retain byte-for-byte behavioral stability.

### 1.3 Pre-Flight Boundary Verification
| Verification Tool | Command Executed | Required Standard | Result |
| :--- | :--- | :--- | :--- |
| **Markdown Boundary Linter** | `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md` | 0 boundary, ambiguity, AST, or tag findings | 🟢 **PASS (0 findings)** |
| **Context & KI Coverage Audit** | Cross-reference `<required_context_rules>` against knowledge base | 100% domain-relevant rules and KIs registered | 🟢 **PASS (5 rules, 10 KIs verified)** |

---

## 2. Five-Axis System 2 Deconstruction

### Axis 1: Target Scope & Boundaries (Scope Inquisitor)
The blast radius of EPIC 154 was scrutinized across all layers of the Quorum stack:
1. **Physical Target File Inventory:**
   - **New Backend Services & DTOs:** `causal_discovery_engine.py`, `causal_discovery.py`, `causal_graph_adapter.py`.
   - **Modified Backend Domain & Pipeline:** `settings.py`, `enums.py`, `step.py`, `registry.py`, `llm.py`, `dag_models.py`, `two_pass_atomizer.py`, `sliding_window_linker.py`, `output_profile.py`, `step_output.py`, `sdui.py`, `base_adapter.py`, `blueprint.py`, `dag_executor.py`, `export_service.py`, `flattener.py`, `flat_record.py`, `report_template.jinja2`.
   - **Modified Client Models & Studio Views:** `enums.dart`, `output_profile.dart`, `profile_editor_view.dart`, `block_card_registry.dart`, `profile_structure_tab.dart`, `profile_section_config_tab.dart`, `sdui_block_dto.dart`, `sdui_blocks_renderer.dart`.
   - **New Client Widgets & Presentation:** `causal_block_card.dart`, `sdui_causal_graph_widget.dart`, `causal_inspector_modal.dart`.
   - **Localization:** `app_en.arb`, `app_fi.arb`.
   - **Tests:** `test_enum_parity.py`, `sdui_golden_master.json`, `test_sdui_semantic_parity.py`, `test_sdui_template_parity.py`, `test_two_pass_atomizer.py`, `test_causal_discovery_engine.py` (new), `test_causal_tda_fusion.py` (new).
2. **Scoped Boy Scout Boundary:** Pre-existing technical debt in touched files (`two_pass_atomizer.py`, `step.py`, `dag_executor.py`) is isolated into Phase 1 pre-implementation cleanups before any causal feature logic is introduced.

### Axis 2: Eradicated Duct-Tape (Duct-Tape Prosecutor)
The audit identified and eradicated five critical under-engineering anti-patterns:
1. **Tuple Hell in `TwoPassAtomizer`:** `_calculate_packets` returned anonymous 3-tuples (`list[tuple[str, str, list[str]]]`) with positional index access. Replaced with immutable `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`.
2. **Hardcoded Magic Constant in Atomizer:** `packet_size = 50` was hardcoded inside `_calculate_packets`. Bound strictly to centralized `Settings.two_pass_atomizer_packet_size`.
3. **Duck-Typing String Checks in `Step`:** `validate_step_consistency` performed raw string checks (`self.type == "llm"`, `self.type == "logic"`). Upgraded to typed enum checks (`self.type == StepType.LLM`).
4. **SlidingWindowLinker Shared Parameter Contamination:** Hardcoded constructor defaults (`window_size=4, overlap=2`) in `SlidingWindowLinker.__init__` must NOT be altered for causal discovery, as doing so would mutate shared behavior for existing `TDAEngine` execution paths. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit causal settings.
5. **Heuristic String Matching in `_resolve_execution_engine`:** Pre-existing `"atom_flattening_hook" in step_def.pre_hooks` heuristic string check flagged in debt register; `StepType.CAUSAL_DISCOVERY` routing placed FIRST in `_resolve_execution_engine` to guarantee zero heuristic interference.

### Axis 3: Approved Best Practice (Type Constitutionalist)
1. **Central Config Sovereignty:** Centralized in Pydantic V2 `Settings` with strict type bounds (`causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`).
2. **SSOT Enums & Cross-Language Wire Contracts:**
   - Python backend adds `StepType.CAUSAL_DISCOVERY = "causal_discovery"` (internal execution taxonomy). In Dart, step strategies are modeled via the sealed `NodeStrategy` Freezed class in `workflow.dart`, so `StepType` is NOT serialized across the wire.
   - `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"` and `CausalDisplayMode` (values strictly `EXECUTIVE = "executive"`, `DETAILED = "detailed"`) enforce strict 1:1 `@JsonEnum` parity in `client_app_v2/lib/core/models/enums.dart` and `test_enum_parity.py`.
3. **ExecutionEngine Protocol Decoupling:** `CausalDiscoveryEngine` implements the unified `ExecutionEngine` protocol (`execute(request: EngineExecutionRequest) -> EngineExecutionResult`) cleanly without subclassing or depending on `TDAEngine`.
4. **Full-Duplex Serialization Parity on OutputProfile:** `causal_display_mode` added symmetrically across all DTO variants (`OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, `OutputProfileResponseDTO`, `OutputProfileDTO`, and Dart `OutputProfile` Freezed model) with `disallowUnrecognizedKeys: true`.
5. **Dumb Painter SDUI & Multi-Surface Parity:** `SduiCausalGraphBlock` rendered identically across Flutter (`SduiCausalGraphWidget`) and PDF (`report_template.jinja2`) as a Unified Causal Action Card (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`). Deep node exploration is decoupled into client-side `CausalInspectorModal`.

### Axis 4: Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
The 30% deletion test was applied to all proposed architectural components:
1. **Dropped `CausalStep` Domain Subclass:** Proposing a separate `CausalStep` domain model subclass would pollute repository schemas, require polymorphic DAL tables, and break database seeder validation. Reused `Step` domain model by adding `StepType.CAUSAL_DISCOVERY` and the optional `causal_source_step_id: str | None = None` fusion anchor.
2. **Dropped Persistent Graph Database:** Proposing Neo4j or persistent NetworkX storage engines was rejected. Causal discovery operates statelessly per run: in-memory transient `LinkedAtomGraph` evaluates topological waves and serializes directly to `CausalGraphPayloadDTO` and SDUI blocks, preserving zero external infrastructure dependencies.
3. **Dropped Micro-Toggle Clutter:** Replaced speculative individual toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) with a single, elegant SSOT selector: `causal_display_mode: CausalDisplayMode` (`executive` / `detailed`).

### Axis 5: Fail-Fast Proof Anchor (Incorruptible Judge)
1. **Automated AST Guardrails:** Mandatory compliance with `QGR001` (zero naked dicts in domain transit), `QGR002` (`extra="forbid"` on all DTOs), `QGR018` (Pydantic V2 `@model_validator`), and `MBD001-MBD009` (markdown boundaries).
2. **ISTQB Equivalence Partitioning & Negative Tests:** Required >= 2 negative test cases per feature:
   - Empty input document (`CAUSAL_DISCOVERY_EMPTY_DOCUMENT`).
   - Circular causality input (`CAUSAL_DISCOVERY_CYCLE_DETECTED`).
   - Empty upstream graph in fusion chaining (`CAUSAL_DISCOVERY_DATA_STARVATION`).
3. **RFC 7807 ErrorCodes:** Explicit error codes defined in `backend_v2/models/enums.py` with structured dual-reporting logger output before raising `AppException`.

---

## 3. Red-Team Falsification & Anti-Happy-Path Analysis

The Red Team analyzed three concrete, high-severity failure modes that could compromise system stability:

### Failure Mode 1: Cycle Loops & Infinite Recursion during Topological Evaluation
- **Attack Vector:** An input document contains circular statements (specifically: "Poor communication caused project delays, which led to high stress, which further degraded communication"). If `SlidingWindowLinker` introduces cyclic edges ($A \rightarrow B \rightarrow C \rightarrow A$), a naive topological sort will enter an infinite loop or raise an unhandled exception.
- **Root Cause:** Graph construction without cycle detection before wave evaluation.
- **Fail-Fast Defense:** `CausalDiscoveryEngine` invokes `TopologicalEvaluator.detect_cycles()` immediately after edge extraction. If a cycle is detected, the engine raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_CYCLE_DETECTED, ...)` with RFC 7807 parameters listing the exact cycle node IDs. A fallback Tarjan SCC condensation sub-routine is strictly banned to prevent nondeterministic DAG mutation.

### Failure Mode 2: TDA Normative Engine Contract Pollution & Data Starvation
- **Attack Vector:** When running a combined workflow where Step 1 is Causal Discovery and Step 2 is TDA Matrix Evaluation, an unmapped document or malformed causal payload results in 0 atoms being transformed. If Step 2 executes with an empty atom set, it either silently produces 0-score reports or crashes deep in matrix math.
- **Root Cause:** Implicit chaining without typed DTO validation between Phase 1A and Phase 1B.
- **Fail-Fast Defense:** Step 2 declares `causal_source_step_id` pointing to Step 1. In `dag_executor.py`, if `causal_source_step_id` is specified but the referenced step output payload is missing, empty, or not of type `CausalGraphPayloadDTO`, the executor fails fast immediately with `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION, ...)`. `TDAEngine` receives guaranteed non-empty `request.shuffled_atoms`.

### Failure Mode 3: SDUI Jinja vs Flutter Template Drift & Unlocalized Chrome
- **Attack Vector:** A new SDUI block `SduiCausalGraphBlock` is created on the backend and rendered in Flutter, but Jinja2 PDF macro mapping is omitted or lags behind, resulting in runtime template rendering crashes (`jinja2.exceptions.UndefinedError`) or silent omissions during PDF export.
- **Root Cause:** Bypassing the Dumb Painter 4-Layer SDUI Extension Protocol (`ki_dumb_painter_sdui.md`).
- **Fail-Fast Defense:** The SDUI template parity test `test_all_sdui_blocks_handled_in_jinja_and_dart` in `@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` requires registering `SduiCausalGraphBlock` in both `PYDANTIC_BLOCK_MODELS` and `DART_UNION_TYPE_MAP`, asserting exactly 19 block types. The integration test `@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]` renders the block through both surfaces and asserts byte-level semantic parity.

---

## 4. Architectural Directives Table (5-Column Synthesis)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Fail-Fast Proof Anchor (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Settings Configuration**<br>`@[backend_v2/settings.py#L54-L910]` | Magic constants in sliding window loops, hardcoded window sizes, fallback `getattr(settings, ...)`. | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. Existing TDA linker settings (`tda_linker_window_size: int = 4`, `tda_linker_overlap: int = 2`) in `settings.py` kept strictly separated from causal settings. | Speculative per-domain sliding window overrides and dynamic runtime reload factories. | `Settings.model_validate({})` strict type validation in unit tests; `test_settings.py`. |
| **SSOT Enums & Parity**<br>`@[backend_v2/models/enums.py#L111-L115]`<br>`@[backend_v2/models/enums.py#L272-L285]`<br>`@[client_app_v2/lib/core/models/enums.dart#L354-L390]`<br>`@[backend_v2/tests/unit/test_enum_parity.py#L110-L112]` | Untyped string comparisons (`self.type == "llm"`), heuristic string matching, ad-hoc string literals for block types. | `StepType.CAUSAL_DISCOVERY = "causal_discovery"` (Python backend only; Dart uses `NodeStrategy` sealed class). `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`, and `CausalDisplayMode(StrEnum)` with values strictly: `EXECUTIVE = "executive"`, `DETAILED = "detailed"`. Explicit ErrorCodes. 1:1 Dart `@JsonEnum` parity for `TargetBlockType` and `CausalDisplayMode`. | Granular display mode permutations (isolated anti-fluff toggles, remediations toggles). | `test_enum_parity.py` verifying `TargetBlockType` and `CausalDisplayMode` parity; Dart compile-time enum switch exhaustion. |
| **Pre-Implementation Atomizer Cleanups**<br>`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]`<br>`@[backend_v2/models/dtos/dag_models.py#L18-L57]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]` | Returning anonymous 3-tuples (`tuple[str, str, list[str]]`) in `_calculate_packets` ("Tuple Hell"), hardcoded magic window sizes (`packet_size = 50`). | Encapsulate chunk packet bounds into typed immutable `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`. Bind `packet_size` to `get_settings().two_pass_atomizer_packet_size`. | Intermediate packet wrapper classes or custom iterator protocols. | `uv run python scripts/audit_dict_eradication.py` passing AST guardrails; unit tests in `test_two_pass_atomizer.py`. |
| **SlidingWindowLinker Isolation**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` | Hardcoded `window_size=4, overlap=2` constructor defaults mutating shared caller behavior. | **DO NOT** mutate constructor defaults in `SlidingWindowLinker.__init__`. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. Existing `TDAEngine` callers retain current behavior without parameter contamination. | Binding constructor defaults to causal-specific settings. | Regression tests for existing `SlidingWindowLinker` callers; unit tests in `test_causal_discovery_engine.py`. |
| **Step Consistency & Strategy Registry**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]` | Raw string literal comparisons (`self.type == "llm"`, `self.type == "logic"`) bypassing `StepType` enum, duck-typing missing criteria block IDs. | Explicit `StepType.LLM` and `StepType.LOGIC` enum comparisons. New `StepType.CAUSAL_DISCOVERY` branch allowing empty `criteria_block_ids` while enforcing `extraction_protocol_block_id` and `cognitive_tier`. `NODE_STRATEGY_REGISTRY` maps `StepType.CAUSAL_DISCOVERY -> _build_llm_strategy`, verified in `NodeStrategyFactory.create_strategy`. | Separate `CausalStep` domain model subclass or parallel step validation pipeline. | Unit tests asserting `AppException` when `extraction_protocol_block_id` is missing; `backend_audit_loop.py`. |
| **`_resolve_execution_engine` Cleanup**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]` | **Pre-existing debt:** `"atom_flattening_hook" in step_def.pre_hooks` heuristic string matching (L184) violating `ban_heuristic_identifier_matching`. | `StepType.CAUSAL_DISCOVERY` guard clause placed as FIRST branch (before L179 block category check). Flag L184 hook heuristic for replacement with typed step ontology resolution. | N/A | Unit test asserting `CausalDiscoveryEngine` returned for `StepType.CAUSAL_DISCOVERY` steps. |
| **LLM Strategy Telemetry & Dispatch**<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]` | Permissive model strategy fallback defaulting to `"prompt"`, ignoring engine ontology for causal discovery steps. | Set `meta_dict["model_strategy"] = "causal"` when `isinstance(self._engine, CausalDiscoveryEngine)`, recording exact telemetry metadata without string guessing. | Dynamic strategy router subclasses or parallel LLM execution strategies. | Unit tests verifying `_step_metadata.model_strategy == "causal"`. |
| **Causal Discovery DTOs**<br>[NEW] `@[backend_v2/models/dtos/causal_discovery.py]`<br>`@[backend_v2/models/dtos/step_output.py#L57-L71]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `StepPayloadValue` extended with `CausalGraphPayloadDTO` and `CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrail passing in audit loop. |
| **Fusion Chaining Contract**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]` | Heuristic step-order detection, runtime flag branching, unmapped document passing. | Studio-driven parameterization: explicit first-class field `Step.causal_source_step_id: str \| None = None` referencing upstream causal discovery step. DAG executor transforms upstream `CausalGraphPayloadDTO.nodes` to `ExtractedAtom` via `transform_causal_nodes_to_atoms` and feeds `request.shuffled_atoms`. | Nondeterministic engine picking, automatic graph merging without declared contracts. | Integration test in `test_causal_tda_fusion.py`. |
| **OutputProfile & Studio UX**<br>`@[backend_v2/models/domain/output_profile.py#L35-L346]`<br>`@[backend_v2/models/dtos/output_profile.py#L36-L260]`<br>`@[backend_v2/models/dtos/output_profile.py#L263-L475]`<br>`@[backend_v2/models/dtos/output_profile.py#L478-L621]`<br>`@[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]`<br>`@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]`<br>[NEW] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]`<br>`@[client_app_v2/lib/l10n/app_en.arb]`<br>`@[client_app_v2/lib/l10n/app_fi.arb]` | Micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`), missing Dart 3 switch branches in `BlockCardRegistry`, missing `.arb` localization keys, partial DTO mutation violating serialization parity. Flutter wiring placed prematurely in Phase 1 before enums exist. | Full-Duplex Serialization Parity: single SSOT field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` (create/update DTOs) and `causal_display_mode: CausalDisplayMode = CausalDisplayMode.EXECUTIVE` (domain/response DTOs). Exhaustive Dart 3 switch matching in `BlockCardRegistry` (housed in Phase 2 alongside enum definitions). Compile-time `.arb` localization. | Multi-tab studio configuration wizards and custom per-node styling controls. | `flutter_audit_loop.py` build runner verification; compile-time Freezed serialization tests. |
| **Causal Discovery Engine & Execution**<br>[NEW] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`<br>`@[backend_v2/services/orchestrator/engines/__init__.py]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]` | Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, mutating existing step execution states in-place without DTOs, routing through fallback branches in `_resolve_execution_engine`. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` cleanly implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult`, re-exported in `__all__`. `NodeExecutor._resolve_execution_engine` routes via `step_def.type == StepType.CAUSAL_DISCOVERY`. StepType.CAUSAL_DISCOVERY check MUST be placed FIRST in `_resolve_execution_engine`, before block category and pre-hook inspection branches. Sequential DAG chaining strictly via immutable DTOs and `causal_source_step_id`. | Dual execution buses, speculative actor frameworks, and persistent graph database storage engines. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops and empty documents; `test_causal_tda_fusion.py`. |
| **SDUI Model, Adapter & Blueprint**<br>`@[backend_v2/models/view/sdui.py#L563-L569, L797-L817]`<br>[NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`<br>`@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`<br>`@[backend_v2/services/blueprint.py#L52-L608]`<br>`@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]` | Client-side graph semantic calculation, client inferring root causes, generic raw JSON passing, missing `SduiBlockBase` polymorphism. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union. `AdapterContext` extended with typed `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` (in-memory only, never serialized across boundaries). `CausalGraphAdapter` transforms `causal_result` into `SduiCausalGraphBlock` strictly adhering to `causal_display_mode`. 1:1 Freezed `@Freezed(unionKey: 'block_type')` Dart model. | Dynamic client-side layout calculators, SVG graph vector serialization over HTTP, multi-pass SDUI transformers. | `test_sdui_template_parity.py` and `test_sdui_semantic_parity.py` passing 100%. |
| **1:1 Presentation Parity (Flutter & PDF)**<br>`@[backend_v2/templates/report_template.jinja2#L87-L550]`<br>[NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`<br>[NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]` | Sprawling unreadable node graphs in PDF, inconsistent layout between PDF and screen, embedding heavy canvas tools into report print templates. | Identical Unified Causal Action Card in both Flutter and PDF: executive half-page critical causal path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote, prescriptive remediation. Deep interactive exploration decoupled strictly into `CausalInspectorModal`. | Embedded interactive JavaScript canvas in PDF, duplicate styling engines across platforms. | `test_sdui_semantic_parity.py` validating identical token and quote rendering across HTML/PDF and Flutter widgets. |
| **Tabular Export & Flat CSV Symmetry**<br>`@[backend_v2/services/export_service.py#L82-L301]`<br>`@[backend_v2/services/flattener.py#L24-L76]`<br>`@[backend_v2/models/dtos/flat_record.py#L17-L55]` | Multi-row hierarchical CSV headers, ragged nested Excel rows, missing causal columns in flat exports. | Excel sheets `Causal Graph` and `Causal Diagnostics` in `ExportService`. `FlatExecutionRecordDTO` receives typed scalar causal fields (`causal_node_count`, `causal_root_cause_count`, `causal_raw_penalty`, `causal_deduplicated_penalty`). `FlatFileService` outputs strictly 2-line flat CSV (line 1 = header names, line 2 = scalar values). | Pivot table generators, dynamic CSV dialect negotiation, secondary XLSX macro formatting. | Unit tests in `test_export_service.py` asserting exact column headers and row counts. |
| **Regression & Integration Testing**<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]`<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`<br>`@[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]`<br>`@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]`<br>`@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` | Happy-path-only tests, mocking persistence with static dummy dicts, unasserted mock calls. | Comprehensive ISTQB tests: equivalence partitioning, boundary value analysis, negative partitions (at least 2 negative tests per feature: empty text, single atom, circular dependency, disconnected subgraph). Integration tests for Phase 1A -> Phase 1B sequential chaining. | Flaky network integration tests, long-running end-to-end browser tests for unit logic. | `uv run python scripts/backend_audit_loop.py` exiting 0 with Ruff, MyPy, and Pytest all green. |

---

## 5. Deprecations & Sunset List (`What We Will REMOVE`)

| Item to Deprecate / Sunset | Replacement / Target Destination | Destructive Operation Classification | Rationale |
| :--- | :--- | :--- | :--- |
| `list[tuple[str, str, list[str]]]` in `TwoPassAtomizer._calculate_packets` | `list[ChunkPacketDTO]` in `@[backend_v2/models/dtos/dag_models.py]` | Eradicate anonymous 3-tuple return type ("Tuple Hell") | Violates `ban_anonymous_state_tuples` in `00-antigravity-core.md`. |
| Hardcoded default `packet_size = 50` in `TwoPassAtomizer._calculate_packets` | Centralized `Settings.two_pass_atomizer_packet_size` | Remove hardcoded magic integer | Violates `Central Config Sovereignty` in `01-python-backend.md`. |
| Raw string comparisons `self.type == "llm"` and `self.type == "logic"` in `Step.validate_step_consistency` | Typed enum comparisons `self.type == StepType.LLM` and `self.type == StepType.LOGIC` | Eradicate string literal checks | Violates strict typing contracts and `01-python-backend.md`. |
| Speculative `CausalStep` domain model subclass | Reused `Step` domain model with validation branching on `StepType.CAUSAL_DISCOVERY` | INTENTIONALLY DROPPED | Prevents polymorphic class explosion; adheres to Axis 4 pruning. |
| Persistent graph database storage (Neo4j / NetworkX persistence) | In-memory transient `LinkedAtomGraph` projected directly to `CausalGraphPayloadDTO` and SDUI blocks | INTENTIONALLY DROPPED | Preserves stateless execution and zero external infrastructure dependencies. |
| Granular Studio micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) | Single SSOT selector `causal_display_mode: CausalDisplayMode` (Executive / Detailed) | Eradicate micro-toggle clutter | Adheres to `studio_driven_parameterization_mandate` and Axis 4 pruning. |

---

## 6. Implementation Readiness & Handoff Recommendation

The audit concludes that `docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md` is **100% hardened, mathematically bounded, and ready for implementation breakdown**:
1. All AST node bounds match physical Python AST spans (`StepType` L111-L115, `TargetBlockType` L272-L285, `StepOutputDTO` L57-L71, `test_sdui_semantic_parity` L109-L380, `test_sdui_template_parity` L111-L148).
2. The Dart `StepType` wire hallucination has been completely purged; Dart models step strategies exclusively via the sealed `NodeStrategy` class, with 1:1 enum parity strictly enforced for `TargetBlockType` and `CausalDisplayMode`.
3. The 5-axis deconstruction and 3 concrete failure modes provide exhaustive guidance for `/tier1-planner`.
4. When scheduled on the roadmap, implementation planning can proceed via `/tier1-planner @[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]`.
