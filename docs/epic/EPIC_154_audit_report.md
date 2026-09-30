# Architectural Audit & Research Report: EPIC 154 (Dynamic Causal Discovery Engine)

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

---

## Executive Summary & Context Verification

- **Target Document:** `@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]`
- **Audit Workflow:** `/tier0-research-epic`
- **Role:** Principal Enterprise Architect & System Red Team
- **Boundary Audit Result:** `SUCCESS: Audit passed for docs\epic\EPIC_154_Dynamic_Causal_Discovery_Engine.md`
- **Context & KI Coverage Audit:** 6 Rules verified, 18 Knowledge Items verified.

---

## 1. Five-Axis System 2 Deconstruction

### Axis 1: Target Scope & Boundaries (Scope Inquisitor)
- **Target File Verification:** All 42 physical files, modules, templates, and tests listed in Chapter 2.1 were verified against the workspace.
- **Scope Creep Elimination:**
  - Avoided creating a polymorphic `CausalStep` subclass; reused domain model `Step` with `StepType.CAUSAL_DISCOVERY` validation branching.
  - Eliminated persistent Neo4j/NetworkX graph databases; graph execution operates strictly in-memory on transient `LinkedAtomGraph` and projects directly into immutable Pydantic V2 DTOs (`CausalGraphPayloadDTO`).
  - Eradicated 4 speculative micro-toggles in `OutputProfile` (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) in favor of a single SSOT selector (`causal_display_mode: CausalDisplayMode`).

### Axis 2: Eradicated Duct-Tape (Duct-Tape Prosecutor)
- **Eliminated Anti-Patterns:**
  - Eradicated anonymous 3-tuple return type `list[tuple[str, str, list[str]]]` in `TwoPassAtomizer._calculate_packets` ("Tuple Hell"), creating and defining immutable `[NEW] ChunkPacketDTO`.
  - Replaced hardcoded magic integer `packet_size = 50` with centralized setting `two_pass_atomizer_packet_size`.
  - Replaced raw string comparisons (`self.type == "llm"`, `self.type == "logic"`) in `Step.validate_step_consistency` with strict typed enum comparisons (`StepType.LLM`, `StepType.LOGIC`).
  - Fixed false assumption regarding pre-existing `tda_linker_*` settings in `settings.py`: isolated `SlidingWindowLinker` constructor defaults and ensured causal settings are explicitly injected without modifying shared defaults.
  - Resolved `NodeExecutor.execute` (line 295) engine resolution gate to ensure `StepType.CAUSAL_DISCOVERY` steps instantiate `CausalDiscoveryEngine` rather than passing `engine=None` into `LLMNodeStrategy`.

### Axis 3: Approved Best Practice (Type Constitutionalist)
- **SSOT Enforcement:**
  - 8 immutable Pydantic V2 DTOs enforcing `ConfigDict(strict=True, extra="forbid", frozen=True)`.
  - Full-Duplex Serialization Parity across Python DTOs and Flutter Freezed models with 1:1 `@JsonEnum` contracts for `TargetBlockType` and `CausalDisplayMode`.
  - Four-Layer Clean Stack hierarchy with static prefix caching in LLM prompt compilation.
  - Exact physical quote validation via `str.find` lexical verification against indexed paragraph blocks `[B0]...[Bn]`, strictly banning fuzzy string matching.

### Axis 4: Pruned Over-Engineering (Complexity Slayer - 30% Deletion Test)
- **Pruned Speculative Abstractions:**
  - Speculative domain model subclass `CausalStep`: **PRUNED**.
  - Secondary Neo4j / NetworkX graph persistence: **PRUNED**.
  - Isolated OutputProfile micro-toggles: **PRUNED**.
  - Intermediate packet wrapper classes: **PRUNED**.

### Axis 5: Fail-Fast Proof Anchors (Incorruptible Judge)
- **Mathematical Fail-Fast Verification:**
  - Empty or non-argument document raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)`.
  - Circular reasoning detected without event loop deadlock: sets `cycle_detected=True` and marks cyclic nodes `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED`.
  - Downstream fusion data starvation raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)`.
  - Unmapped SDUI blocks in Jinja2 PDF generator trigger `raise_unrecognized_sdui_block`.
  - Automated quality gate audit loops (`backend_audit_loop.py` and `flutter_audit_loop.py`).

---

## 2. Panel of Architects Evaluation

### Global System Architect
- **Single Pipeline Invariant:** `CausalDiscoveryEngine` executes autonomously as an independent `ExecutionEngine`. In fusion mode, chaining occurs sequentially at the DAG layer (Phase 1A Discovery -> Phase 1B TDA) without branching inside `TDAEngine`.
- **Fail-Fast Compliance:** No fallback defaults, silent dictionary conversions, or permissive error catching.

### Backend/Data Architect
- **Strict Typing:** All payload transit across step boundaries uses immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`).
- **Opaque Stripe IDs:** Relational pointers utilize Opaque Stripe IDs with canonical prefix patterns.
- **Repository Isolation:** Transient graphs reside in-memory; outputs serialize directly to standard execution trace snapshots.

### SDUI & Frontend Architect
- **1:1 Presentation Parity:** Identical Unified Causal Action Card layout in Flutter (`SduiCausalGraphWidget`) and PDF (`render_causal_graph_block` in `report_template.jinja2`), occupying at most half an A4 page in PDF.
- **Pro-Tool Decoupling:** Deep interactive graph exploration, pan/zoom, and remediation simulation are decoupled into `CausalInspectorModal`.
- **Dumb Painter Compliance:** Zero client-side semantic inference or graph layout re-computation.

### AI & Orchestration Architect
- **Prompt Architecture:** Static prompt prefixes with unbroken instructions maximize context caching; dynamic variables and atom aliases (`a0`, `a1`) reside at the tail.
- **Theory Grounding:** Argumentation matrices (Toulmin, Walton, or custom enterprise criteria) are 100% dynamic domain entities loaded from PromptBlocks, never hardcoded in source code.
- **Quote Verification:** Tier 1 physical lexical anchoring via `str.find` prevents hallucinated or chimera quotes.

---

## 3. Falsification & Red-Teaming (Concrete Failure Modes)

### Failure Mode 1: Hallucinated Pre-Existing Settings Parameter Assumption
- **Condition:** The original draft assumed `tda_linker_window_size` and `tda_linker_overlap` already existed in `settings.py`.
- **Physical Reality:** `settings.py` does not contain linker settings; `SlidingWindowLinker` has hardcoded constructor defaults (`window_size = 4, overlap = 2`).
- **Hazard:** Executing agent attempts to reference nonexistent settings fields or mutates constructor defaults, contaminating existing callers.
- **Hardened Fix:** The Epic was surgically updated to state that `SlidingWindowLinker` constructor defaults are preserved without mutation, and `CausalDiscoveryEngine` explicitly injects `causal_discovery_window_size` and `causal_discovery_overlap` from `settings.py`.

### Failure Mode 2: Silent Engine Resolution Failure in `NodeExecutor.execute`
- **Condition:** In `backend_v2/services/orchestrator/dag_executor.py` (line 295), engine resolution only evaluated `if step_def.type == StepType.LLM:`.
- **Physical Reality:** For `step_def.type == StepType.CAUSAL_DISCOVERY`, line 295 evaluated to `False`, leaving `engine = None` when constructing `LLMNodeStrategy`.
- **Hazard:** `LLMNodeStrategy.execute()` crashed with an unhandled runtime error when attempting to invoke `self._engine`.
- **Hardened Fix:** The Epic mandates updating `NodeExecutor.execute` (line 295) to resolve the execution engine when `step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY)`.

### Failure Mode 3: Unbound SDUI Rendering Exception in PDF Generation
- **Condition:** `backend_v2/templates/report_template.jinja2` enforces Fail-Fast via `raise_unrecognized_sdui_block(block.block_type)` (line 556).
- **Hazard:** Generating a report with `causal_graph` blocks without synchronous Jinja2 macro updates immediately crashes PDF generation for all end-users.
- **Hardened Fix:** Phase 4 explicitly binds the Jinja2 macro `render_causal_graph_block` and AST validation test `test_sdui_template_parity.py` (verifying 19 blocks) atomically alongside the Python SDUI model.

### Failure Mode 4: Context Rules & KI Registry Omissions
- **Condition:** Header `<required_context_rules>` omitted `03_seed_vault.md`, `ki_llm_extraction_architecture.md`, and `ki_epic_lifecycle_workflow.md`.
- **Hazard:** Subsequent planner and execution sessions suffered from context amnesia regarding prompt extraction rules and seed data invariants.
- **Hardened Fix:** All missing rules and Knowledge Items were surgically injected into the Epic header.

---

## 4. 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Settings Configuration**<br>`@[backend_v2/settings.py#L54-L910]` | Magic constants in sliding window loops, hardcoded window sizes, fallback `getattr(settings, ...)` access. | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. Causal discovery settings are explicitly injected into `SlidingWindowLinker` without mutating existing constructor defaults (`window_size = 4, overlap = 2`). | Speculative per-domain sliding window overrides and dynamic runtime reload factories. | `Settings.model_validate({})` strict type validation in unit tests; `test_settings.py`. |
| **SSOT Enums & Parity**<br>`@[backend_v2/models/enums.py#L111-L115]`<br>`@[backend_v2/models/enums.py#L272-L285]`<br>`@[client_app_v2/lib/core/models/enums.dart#L354-L390]`<br>`@[backend_v2/tests/unit/test_enum_parity.py#L110-L112]` | Untyped string comparisons (`self.type == "llm"`), heuristic string matching, ad-hoc string literals for block types. | `StepType.CAUSAL_DISCOVERY = "causal_discovery"` (Python backend only; Dart uses `NodeStrategy` sealed class). `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`, and `CausalDisplayMode(StrEnum)` with values strictly: `EXECUTIVE = "executive"`, `DETAILED = "detailed"`. Explicit ErrorCodes: `CAUSAL_DISCOVERY_EMPTY_DOCUMENT`, `CAUSAL_DISCOVERY_CYCLE_DETECTED`, `CAUSAL_DISCOVERY_DATA_STARVATION`. 1:1 Dart `@JsonEnum` parity for `TargetBlockType` and `CausalDisplayMode`. | Granular display mode permutations (isolated anti-fluff toggles, remediations toggles). | `test_enum_parity.py` verifying `TargetBlockType` and `CausalDisplayMode` parity; Dart compile-time enum switch exhaustion. |
| **Pre-Implementation Atomizer Cleanups**<br>`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]`<br>`@[backend_v2/models/dtos/dag_models.py#L18-L57]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]` | Returning anonymous 3-tuples (`tuple[str, str, list[str]]`) in `_calculate_packets` ("Tuple Hell"), hardcoded magic window sizes (`packet_size = 50`). | Create and encapsulate chunk packet bounds into typed immutable `[NEW] ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`. Bind `packet_size` to `get_settings().two_pass_atomizer_packet_size`. | Intermediate packet wrapper classes or custom iterator protocols. | `uv run python scripts/audit_dict_eradication.py` passing AST guardrails; unit tests in `test_two_pass_atomizer.py`. |
| **SlidingWindowLinker Isolation**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` | Hardcoded `window_size=4, overlap=2` constructor defaults mutating shared caller behavior. | **DO NOT** mutate constructor defaults in `SlidingWindowLinker.__init__`. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. Existing `TDAEngine` callers retain current behavior without parameter contamination. | Binding constructor defaults to causal-specific settings. | Regression tests for existing `SlidingWindowLinker` callers; unit tests in `test_causal_discovery_engine.py`. |
| **Step Consistency & Strategy Registry**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]` | Raw string literal comparisons (`self.type == "llm"`, `self.type == "logic"`) bypassing `StepType` enum, duck-typing missing criteria block IDs. | Explicit `StepType.LLM` and `StepType.LOGIC` enum comparisons. New `StepType.CAUSAL_DISCOVERY` branch allowing empty `criteria_block_ids` while enforcing `extraction_protocol_block_id` and `cognitive_tier`. `NODE_STRATEGY_REGISTRY` (L63-L66) maps `StepType.CAUSAL_DISCOVERY -> _build_llm_strategy`, verified in `NodeStrategyFactory.create_strategy` (L73). | Separate `CausalStep` domain model subclass or parallel step validation pipeline. | Unit tests asserting `AppException` when `extraction_protocol_block_id` is missing; `backend_audit_loop.py`. |
| **`_resolve_execution_engine` Cleanup**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]` | **Pre-existing debt:** `"atom_flattening_hook" in step_def.pre_hooks` heuristic string matching (L184) violating `ban_heuristic_identifier_matching`. | `StepType.CAUSAL_DISCOVERY` guard clause placed as FIRST branch (before L179 block category check). Flag L184 hook heuristic for replacement with typed step ontology resolution. | N/A | Unit test asserting `CausalDiscoveryEngine` returned for `StepType.CAUSAL_DISCOVERY` steps. |
| **LLM Strategy Telemetry & Dispatch**<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]` | Permissive model strategy fallback defaulting to `"prompt"`, ignoring engine ontology for causal discovery steps. | Set `meta_dict["model_strategy"] = "causal"` when `isinstance(self._engine, CausalDiscoveryEngine)`, recording exact telemetry metadata without string guessing. | Dynamic strategy router subclasses or parallel LLM execution strategies. | Unit tests verifying `_step_metadata.model_strategy == "causal"`. |
| **Causal Discovery DTOs**<br>[NEW] @[backend_v2/models/dtos/causal_discovery.py]<br>`@[backend_v2/models/dtos/step_output.py#L57-L71]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `StepPayloadValue` (L30-L54) extended with `CausalGraphPayloadDTO` and `CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrail passing in audit loop. |
| **Fusion Chaining Contract**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]` | Heuristic step-order detection, runtime flag branching, unmapped document passing. | Studio-driven parameterization: explicit first-class field `Step.causal_source_step_id: str \| None = None` referencing upstream causal discovery step. DAG executor transforms upstream `CausalGraphPayloadDTO.nodes` to `ExtractedAtom` via `transform_causal_nodes_to_atoms` and feeds `request.shuffled_atoms`. | Nondeterministic engine picking, automatic graph merging without declared contracts. | Integration test in `test_causal_tda_fusion.py`. |
| **OutputProfile & Studio UX**<br>`@[backend_v2/models/domain/output_profile.py#L35-L346]`<br>`@[backend_v2/models/dtos/output_profile.py#L36-L260]`<br>`@[backend_v2/models/dtos/output_profile.py#L263-L475]`<br>`@[backend_v2/models/dtos/output_profile.py#L478-L621]`<br>`@[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]`<br>`@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]`<br>[NEW] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]`<br>`@[client_app_v2/lib/l10n/app_en.arb]`<br>`@[client_app_v2/lib/l10n/app_fi.arb]` | Micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`), missing Dart 3 switch branches in `BlockCardRegistry`, missing `.arb` localization keys, partial DTO mutation violating serialization parity. Flutter wiring placed prematurely in Phase 1 before enums exist. | Full-Duplex Serialization Parity: single SSOT field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` (create/update DTOs) and `causal_display_mode: CausalDisplayMode = CausalDisplayMode.EXECUTIVE` (domain/response DTOs). Exhaustive Dart 3 switch matching in `BlockCardRegistry` (housed in Phase 2 alongside enum definitions). Compile-time `.arb` localization. | Multi-tab studio configuration wizards and custom per-node styling controls. | `flutter_audit_loop.py` build runner verification; compile-time Freezed serialization tests. |
| **Causal Discovery Engine & Execution**<br>[NEW] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`<br>`@[backend_v2/services/orchestrator/engines/__init__.py]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]` | Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, mutating existing step execution states in-place without DTOs, routing through fallback branches in `_resolve_execution_engine`. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` cleanly implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult`, re-exported in `__all__`. `NodeExecutor._resolve_execution_engine` routes via `step_def.type == StepType.CAUSAL_DISCOVERY`. StepType.CAUSAL_DISCOVERY check MUST be placed FIRST in `_resolve_execution_engine`, before block category and pre-hook inspection branches. Sequential DAG chaining strictly via immutable DTOs and `causal_source_step_id`. | Dual execution buses, speculative actor frameworks, and persistent graph database storage engines. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops and empty documents; `test_causal_tda_fusion.py`. |
| **SDUI Model, Adapter & Blueprint**<br>`@[backend_v2/models/view/sdui.py#L563-L569, L797-L817]`<br>[NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`<br>`@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`<br>`@[backend_v2/services/blueprint.py#L52-L608]`<br>`@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]` | Client-side graph semantic calculation, client inferring root causes, generic raw JSON passing, missing `SduiBlockBase` polymorphism. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union (L797-L817). `AdapterContext` extended with typed `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` (in-memory only, never serialized across boundaries). `CausalGraphAdapter` transforms `causal_result` into `SduiCausalGraphBlock` strictly adhering to `causal_display_mode`. 1:1 Freezed `@Freezed(unionKey: 'block_type')` Dart model. | Dynamic client-side layout calculators, SVG graph vector serialization over HTTP, multi-pass SDUI transformers. | `test_sdui_template_parity.py` and `test_sdui_semantic_parity.py` passing 100%. |
| **1:1 Presentation Parity (Flutter & PDF)**<br>`@[backend_v2/templates/report_template.jinja2#L87-L550]`<br>[NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`<br>[NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]` | Sprawling unreadable node graphs in PDF, inconsistent layout between PDF and screen, embedding heavy canvas tools into report print templates. | Identical Unified Causal Action Card in both Flutter and PDF: executive half-page critical causal path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote, prescriptive remediation. Deep interactive exploration decoupled strictly into `CausalInspectorModal`. | Embedded interactive JavaScript canvas in PDF, duplicate styling engines across platforms. | `test_sdui_semantic_parity.py` validating identical token and quote rendering across HTML/PDF and Flutter widgets. |
| **Tabular Export & Flat CSV Symmetry**<br>`@[backend_v2/services/export_service.py#L82-L301]`<br>`@[backend_v2/services/flattener.py#L24-L76]`<br>`@[backend_v2/models/dtos/flat_record.py#L17-L55]` | Multi-row hierarchical CSV headers, ragged nested Excel rows, missing causal columns in flat exports. | Excel sheets `Causal Graph` and `Causal Diagnostics` in `ExportService`. `FlatExecutionRecordDTO` receives typed scalar causal fields (`causal_node_count`, `causal_root_cause_count`, `causal_raw_penalty`, `causal_deduplicated_penalty`). `FlatFileService` outputs strictly 2-line flat CSV (line 1 = header names, line 2 = scalar values). | Pivot table generators, dynamic CSV dialect negotiation, secondary XLSX macro formatting. | Unit tests in `test_export_service.py` asserting exact column headers and row counts. |
| **Regression & Integration Testing**<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]`<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`<br>`@[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]`<br>`@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]`<br>`@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` | Happy-path-only tests, mocking persistence with static dummy dicts, unasserted mock calls. | Comprehensive ISTQB tests: equivalence partitioning, boundary value analysis, negative partitions (at least 2 negative tests per feature: empty text, single atom, circular dependency, disconnected subgraph). Integration tests for Phase 1A -> Phase 1B sequential chaining. | Flaky network integration tests, long-running end-to-end browser tests for unit logic. | `uv run python scripts/backend_audit_loop.py` exiting 0 with Ruff, MyPy, and Pytest all green. |

---

## 5. Certification & Handover

The architectural analysis of `@[docs/epic/EPIC_154_Dynamic_Causal_Discovery_Engine.md]` is complete and verified against all Quorum 2026 invariants:
- **Zero Duct-Tape Code:** All temporary shims and anonymous tuples removed.
- **Fail-Fast Boundary Invariants:** Ingress and execution starvation triggers explicit typed `AppException`.
- **Dumb Painter SDUI:** Presentation remains 100% data-driven and identical across Flutter and Jinja2 PDF.
- **Next Step:** Start a brand new conversation session and invoke `/tier1-planner @[c:\src\quorum\docs\epic\EPIC_154_Dynamic_Causal_Discovery_Engine.md]`.
