> **STATUS: PENDING IMPLEMENTATION (Distant Future Roadmap / Future Extension)**

```xml
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
```

# Implementation Plan - Dynamic Causal Discovery Engine (Exploratory Text DAG & Argument Mapping)

> [!CAUTION]
> **DISTANT FUTURE ROADMAP ONLY**
> This implementation plan is filed in reserve for a future extension and does not belong to the active development cycle. The plan describes an optional and experimental open-text causal discovery workflow (*Exploratory Causal Discovery Engine*) that analyzes free-form documents without a pre-configured evaluation matrix. This MUST NOT be activated as part of the current normative evaluation core, and it must not compromise the deterministic execution or strict `shuffled_atoms` contract of `TDAEngine`.

---

## User Review Required

> [!IMPORTANT]
> **Complete Standalone and Decoupled Mode (Standalone Engine Mandate):**
> `CausalDiscoveryEngine` is implemented and maintained strictly as a **100% standalone and decoupled analysis engine**.
> - The engine executes completely independently without any dependency on `TDAEngine`, without a pre-configured evaluation matrix, and without criteria blocks.
> - It does not require a `request.shuffled_atoms` input; instead, it autonomously extracts argument structures from free-form text, constructs a directed argument graph (`LinkedAtomGraph`), executes topological evaluation, and produces a complete visualizable report block (`SduiCausalGraphBlock`).
> - In standalone mode, node colors and states directly reflect the topological validity of arguments (defined exhaustively as: Green = validated claim, Red = refuted/failed claim, Orange = cascading fault, Grey = orphaned concept).
>
> **Macro Strategy vs. Compute Engine Category Error Resolution:**
> In accordance with `ki_execution_engine_protocol.md`, `StepType` strictly governs the macro execution strategy layer (specifically and exhaustively: `StepType.LLM` and `StepType.LOGIC`). `CausalDiscoveryEngine` is an `ExecutionEngine` executed within `LLMNodeStrategy`, NOT a parallel macro step type. Introducing `StepType.CAUSAL_DISCOVERY` is strictly forbidden because it corrupts the macro taxonomy. Causal discovery steps preserve `StepType.LLM` and resolve `CausalDiscoveryEngine` orthogonally via `PromptBlockCategory.CAUSAL_DISCOVERY` or explicit step configuration `step_def.is_causal_discovery`.
>
> **Pure Compute Engine Law & Concurrency Purification (Post-Commit `03c4e91b5`):**
> In compliance with commit `03c4e91b5`, `ki_execution_engine_protocol.md`, and `ki_python_314_concurrency_strictness.md`, `EngineExecutionRequest` is a 100% pure computational data structure with zero concurrency semaphores or cancellation events. `CausalDiscoveryEngine` is a stateless, pure compute pipeline that executes without event or semaphore locks, returning `EngineExecutionResult(synthesis_output=CausalGraphPayloadDTO)`. Concurrency throttling is governed exclusively by dynamic semaphores within `LiteLLMProvider`.
>
> **Single Pipeline Invariant & Zero-Fallback Compliance:**
> `CausalDiscoveryEngine` and `TDAEngine` remain completely decoupled `ExecutionEngine` implementations. `CausalDiscoveryEngine` binds to workflow steps strictly via typed step ontology resolution in `_resolve_execution_engine`. It MUST NOT function as a fallback branch inside `TDAEngine`, and the engines must never be merged into a monolithic class. `TDAEngine` preserves its 100% strict Fail-Fast contract (requiring `request.shuffled_atoms`).
>
> **Optional Causal Graph and TDA Matrix Fusion (Two Separate Engines -> One Unified Result):**
> When a workflow combines normative criteria evaluation with an exploratory causal graph, they are not executed as disconnected parallel reports; instead, they are chained into a two-phase deterministic analysis pipeline:
> - **Dynamic Matrix Independence & Extensibility:** All evaluation matrices and argumentation frameworks (referencing dynamic PromptBlocks including Toulmin, Walton, or custom enterprise criteria) are 100% dynamic domain entities configured in Quorum Studio and persisted in `seed_data.json`. Matrices are never hardcoded in source code: workflows configure zero, one, or multiple dynamic matrices; matrices are added, updated, or removed dynamically without modifying backend code.
> 1. **Pipeline Chaining (Discovery extracts -> TDA evaluates):**
>    The workflow chains the two engines at the DAG layer into two deterministic phases:
>    - **Phase 1A (`CausalDiscoveryEngine`):** The engine analyzes free-form text and constructs a directed argument graph (`LinkedAtomGraph`), isolating premises, claims, and conclusions into discrete atom nodes without requiring any evaluation matrix.
>    - **Phase 1B (`TDAEngine`):** The TDA engine does not evaluate the raw text corpus randomly; rather, it takes these discovered causal nodes as direct input (`ExtractedAtom` -> `shuffled_atoms`) and evaluates them against whichever dynamic criteria matrix is configured for that step (verifying: Warrant linkage, Backing evidence, dogmatic quantifiers, and matrix score scales).
>    - **Outcome:** A single analysis pipeline where causal discovery structures the document topology and TDA acts as the qualitative normative judge.
> 2. **Semantic Overlay in the User Interface:**
>    The user interface renders a single unified interactive graph (`SduiCausalGraphBlock`):
>    - Directed edges between nodes depict the logical progression and causal relationships extracted by the Discovery engine.
>    - In fusion mode, node colors and levels originate directly from the TDA matrix (defined exhaustively as: Green = grounded claim, Red = dogmatic assumption lacking backing).
>    - **Outcome:** The evaluator inspects the logical structure of the text and the qualitative rigor of each argument in a single visual node representation.
> 3. **Causal Root Cause Attribution in Scoring:**
>    Causal Discovery fault attribution (`blame_parent_ids`) binds directly to TDA score deductions and verbal rationale:
>    - When an author loses points under the criteria "Claim Grounding", the system reports the causal path: *"Conclusion B failed because it relies on the refuted assumption in node A in paragraph [B2]"*.
>    - **Outcome:** Total score computations and qualitative justifications form a single non-disputable and transparent evaluation audit trail.
>
> **Flutter UI & PDF 1:1 Presentation Parity & 19-Block Parity Gate:**
> The interactive on-screen report view (`ReportRendererV2Widget`) and the generated A4 PDF (`report_template.jinja2`) represent the exact same document.
> - **19-Block SDUI Extension Parity:** Adding `SduiCausalGraphBlock` expands `AnySduiBlock` from 18 to 19 blocks. In compliance with `ki_dumb_painter_sdui.md`, this mandates synchronous 5-point parity enforced by `test_sdui_template_parity.py` (`assert len(pydantic_block_types) == 19`), `test_sdui_semantic_parity.py`, `sdui_golden_master.json`, Jinja2 `render_sdui_blocks` macro branch, and Flutter `SduiBlocksRenderer`.
> - **Identical Output Representation:** In both Flutter and PDF, `SduiCausalGraphBlock` renders an identical, compact, and readable **Unified Causal Action Card**, occupying at most half an A4 page in the PDF artifact.
> - **Critical Causal Path Principle:** The output renders a streamlined left-to-right error chain: `[Root Cause]` -> caused -> `[Cascading Fault]` -> resulted in -> `[Score Loss]`, accompanied by the lexical quote and prescriptive remediation. Validated passing claims are summarized in a single compact metric (defined exhaustively as: "X other claims verified logically sound").
> - **Supplementary Inspection Decoupling:** Free-form graph exploration, pan-and-zoom navigation, and in-depth inspection are strictly decoupled into a dedicated modal (`CausalInspectorModal`), opened via an explicit inspection action button. The primary printed and on-screen report layout remains 100% clean, standardized, and identical across screen and paper.
>
> **Streamlined Studio-Driven OutputProfile in `OutputProfileCrudView`:**
> Adhering to `studio_driven_parameterization_mandate` and `ki_desktop_pro_tool_studio_ux.md`, OutputProfile controls are housed in `OutputProfileCrudView` across `ProfileStructureTab` and `ProfileSectionConfigTab` (with legacy monolithic `ProfileEditorView` completely excluded):
> - **Block Selection and Order (`target_block_order`):** The typed enum value `TargetBlockType.CAUSAL_GRAPH_BLOCK`. If the block appears in the list, it renders at that exact position; if omitted, the report generates compactly without the causal block.
> - **Display Mode (`causal_display_mode: CausalDisplayMode`):** A single selector with values defined exhaustively as:
>   - `EXECUTIVE = "executive"` (Default: Compact half-page Unified Causal Action Card – rendering only the critical root cause path, lexical fault quote, and prescriptive remediation).
>   - `DETAILED = "detailed"` (Technical audit mode: complete argument graph and exhaustive evidentiary table for domain experts).
> - **Micro-Toggle Elimination:** Isolated micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) are eradicated, preserving a streamlined profile editor.
>
> **Forensic Excel & Denormalized CSV Export via `ReportHeaderResolver`:**
> In accordance with `ki_god_code_prevention.md` and `ki_dual_axis_localization_architecture.md`, monolithic flatteners (legacy `flattener.py`, flat file services, and flat execution record DTOs) have been completely eradicated from Quorum. All tabular data exports flow through `ExportService` and `ReportHeaderResolver`:
> - **Worksheet "Causal Graph":** Registered under `ReportSheetKey.CAUSAL_GRAPH` in `ReportHeaderResolver`, rendering a relational table of nodes, claims, paragraph citations `[Bx]`, statuses, parent IDs, child IDs, root cause pointers, and remediations.
> - **Worksheet "Causal Diagnostics":** Registered under `ReportSheetKey.CAUSAL_DIAGNOSTICS` in `ReportHeaderResolver`, tabulating root cause diagnoses, Anti-Fluff findings, and deduplicated fair scoring breakdowns.
> - **Normative "Raw Data" Worksheet Enrichment:** In fusion mode, TDA atom rows are enriched with scalar columns: `causal_status`, `blame_parent_id`, and `dependent_count`.
> - **Denormalized CSV Export:** Extended via typed columns in `ExportDenormalizedFlatRowDTO` resolved strictly through `ReportHeaderResolver.get_all_denormalized_csv_headers`. Legacy 2-line CSV generation is permanently forbidden.
>
> **Five Core Stakeholder Benefits:**
> 1. **Root Cause Attribution:** The topological blame cascade (`blame_parent_ids`) isolates the foundational origin of an error chain.
> 2. **Anti-Fluff Shield:** Detects orphaned concepts and circular reasoning (`cycle_detected`), deducting points when an argumentative chain is missing.
> 3. **Prescriptive Feedback:** Surgical remediation recommendations indicating which corrections unlock downstream assertions.
> 4. **Visual XAI Overlay:** A unified argument map where node color reflects operational status and lexical citations expand on demand.
> 5. **Fair & Deduplicated Scoring:** Decouples independent root causes from cascading secondary errors, preventing repetitive scoring penalties for a single underlying fault.
>
> **SSOT and Pydantic V2 Contracts:**
> All domain models (`LinkedAtomGraph`, `CausalEdgeDTO`, `CausalNodeDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `SduiCausalGraphBlock`, `OutputProfile`) adhere strictly to `ConfigDict(strict=True, extra='forbid', frozen=True)` with zero naked dictionaries.
>
> **Four-Layer Clean Stack & High-Fidelity Prompting:**
> LLM prompts in `CausalDiscoveryEngine` are compiled strictly through the Four-Layer Clean Stack hierarchy:
> 1. **Layer 1: Static System Directives & Mandates:** Static ontology instructions placed in the system prompt prefix for 100% context caching efficiency.
> 2. **Layer 2: Theory Grounding & Epistemic Context:** Dynamically loaded theory grounding and argumentation schemes (referencing dynamic PromptBlocks including Toulmin, Walton, or custom argumentation frameworks authored in Quorum Studio) injected into `<theory_context>`. Matrices are never hardcoded in source code: all matrices and criteria schemes are dynamic domain entities that can be added, modified, or removed in Quorum Studio with zero backend code changes.
> 3. **Layer 3: Extraction Protocol:** Step-level argument extraction and linking behavior.
> 4. **Layer 4: Dynamic User Payload & Execution Variables:** Dynamic text blocks indexed as `[B0]...[Bn]` and atom aliasing (`a0`, `a1`) placed at the tail.
> - **Exact Physical Anchoring:** Extracted quotes (`source_quote`) must strictly match source text via `str.find` lexical validation; fuzzy string matching is prohibited.
>
> **Pruned Over-Engineering & 30% Deletion Verification (Axis 4):**
> - **`StepType.CAUSAL_DISCOVERY` Enum Pollution: PRUNED.** Rejected in favor of preserving macro `StepType.LLM` and resolving `CausalDiscoveryEngine` via prompt block category or step ontology.
> - **`CausalStep` Domain Subclass: PRUNED.** Rejected in favor of the existing `Step` domain model with validation branching, avoiding class hierarchy explosion.
> - **Persistent Graph Database: PRUNED.** Rejected in favor of in-memory transient graph representation (`LinkedAtomGraph`) projected directly to SDUI `SduiCausalGraphBlock` and trace JSON.
> - **Granular OutputProfile Micro-Toggles: PRUNED.** Isolated toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) are eradicated in favor of a single SSOT selector `causal_display_mode: CausalDisplayMode`.
> - **Dead Legacy Flattener CSV Generator: PRUNED.** Eradicated in favor of existing typed denormalized CSV export in `ExportService`.
> - **Re-implementation of ChunkPacketDTO: PRUNED.** Recognized as already completed in active production (`dag_models.py` line 21, `two_pass_atomizer.py` line 50).
> - **8 Dedicated Pydantic V2 DTOs: RETAINED.** `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, and `CausalTdaFusionResultDTO` are retained as irreducible domain contracts.

---

## Scope & Boundaries

### Target Files:
- `[NEW]` @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- `[NEW]` @[backend_v2/models/dtos/causal_discovery.py]
- `[NEW]` @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- `[MODIFY]` @[backend_v2/settings.py#L54-L924]
- `[MODIFY]` @[backend_v2/models/enums.py#L253-L262]
- `[MODIFY]` @[backend_v2/models/enums.py#L275-L288]
- `[MODIFY]` @[backend_v2/models/enums.py#L945-L954]
- `[MODIFY]` @[backend_v2/models/domain/step.py#L32-L119]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L80-L988]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L121-L347]
- `[MODIFY]` @[backend_v2/models/domain/output_profile.py#L36-L353]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L37-L268]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L271-L492]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L495-L645]
- `[MODIFY]` @[backend_v2/models/dtos/step_output.py#L59-L73]
- `[MODIFY]` @[backend_v2/models/dtos/export.py#L73-L94]
- `[MODIFY]` @[backend_v2/services/localization.py#L382-L488]
- `[MODIFY]` @[backend_v2/l10n/en.json]
- `[MODIFY]` @[backend_v2/l10n/fi.json]
- `[MODIFY]` @[backend_v2/models/view/sdui.py#L559-L565]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]
- `[MODIFY]` @[backend_v2/services/blueprint.py#L63-L618]
- `[MODIFY]` @[backend_v2/templates/report_template.jinja2]
- `[MODIFY]` @[backend_v2/services/export_service.py#L53-L892]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L136-L366]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/__init__.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_enum_parity.py#L110-L112]
- `[MODIFY]` @[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]
- `[MODIFY]` @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]
- `[MODIFY]` @[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]
- `[MODIFY]` @[client_app_v2/lib/core/models/enums.dart#L354-L390]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb]
- `[MODIFY]` @[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]
- `[NEW]` @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]
- `[NEW]` @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]

### Dead Target Files Eradicated (Do Not Modify):
- `backend_v2/services/flattener.py` (File deleted from repository; legacy flat file service eradicated).
- `backend_v2/models/dtos/flat_record.py` (File deleted from repository; legacy flat record DTO eradicated).
- `client_app_v2/lib/features/studio/views/profile_editor_view.dart` (Decomposed into `output_profile_crud_view.dart`).

### Context / Read-Only Files:
- `@[backend_v2/services/orchestrator/engines/base.py]`
- `@[backend_v2/services/orchestrator/engines/tda_engine.py]`
- `@[backend_v2/services/orchestrator/topological_evaluator.py]`
- `@[backend_v2/services/orchestrator/result_projector.py]`
- `@[client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart]`

### Architectural Directives (5-Column Synthesis):

| Target Scope & Boundaries | Eradicated Duct-Tape (Under-Engineering Ban) | Approved Best Practice (Target Invariant) | Pruned Over-Engineering (Complexity Slayer) | Fail-Fast Proof Anchor (Deterministic Verification) |
| :--- | :--- | :--- | :--- | :--- |
| **Engine Resolution & Dispatch**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]`<br>`@[backend_v2/models/enums.py#L253-L262]` | Adding `StepType.CAUSAL_DISCOVERY` (pollutes macro strategy enum). Heuristic string matching in `_resolve_execution_engine` (`"atom_flattening_hook" in step_def.pre_hooks`). Raw string literal comparisons (`self.type == "llm"`). | Step preserves `StepType.LLM`. Resolved via `PromptBlockCategory.CAUSAL_DISCOVERY` or step attribute `step_def.is_causal_discovery`. Typed enum comparisons `self.type == StepType.LLM`. | Pruned `StepType.CAUSAL_DISCOVERY` from `enums.py` and `NODE_STRATEGY_REGISTRY`. Strategy registry dispatches `StepType.LLM` deterministically. | `test_dag_executor.py` asserting `CausalDiscoveryEngine` resolved; AST guardrail `QGR016` (no heuristic matching). |
| **Settings & Packet Sizing**<br>`@[backend_v2/settings.py#L54-L924]`<br>`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77]` | Magic constants in sliding window loops, hardcoded window sizes, re-implementing `ChunkPacketDTO` (already completed in production). | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. Bind `packet_size` in `_calculate_packets` to `get_settings().two_pass_atomizer_packet_size`. General linker defaults kept separate. | Pruned speculative per-domain sliding window overrides and redundant packet DTO refactoring tasks. | `Settings.model_validate({})` strict type validation in unit tests; `test_two_pass_atomizer.py` passing 100%. |
| **SlidingWindowLinker Isolation**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L121-L347]` | Mutating constructor defaults in `SlidingWindowLinker.__init__` (`window_size=4, overlap=2`), contaminating shared caller behavior. | **DO NOT** mutate constructor defaults in `SlidingWindowLinker.__init__`. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. Existing callers retain current behavior. | Binding constructor defaults to causal-specific settings. | Regression tests for existing `SlidingWindowLinker` callers; unit tests in `test_causal_discovery_engine.py`. |
| **Strategy Telemetry Labeling**<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L80-L988]` | Defaulting strategy metadata to `"prompt"` or using runtime `isinstance` cascades. Untyped dictionary mutations in `final_dict["_step_metadata"]`. | When `isinstance(self._engine, CausalDiscoveryEngine)`, record `meta_dict["model_strategy"] = "causal"` in `_step_metadata`. | Speculative dynamic strategy routing plugins. | Unit test verifying `_step_metadata["model_strategy"] == "causal"` in `test_causal_discovery_engine.py`. |
| **Pure Compute Causal Engine**<br>[NEW] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`<br>`@[backend_v2/services/orchestrator/engines/__init__.py]` | Concurrency primitives in engine request/result (violating Pure Compute Engine Law). Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, mutating DAG executor state. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult` as a 100% pure computational pipeline with zero semaphores or events. Returns payload in `EngineExecutionResult(synthesis_output=CausalGraphPayloadDTO)`. Re-exported in `__all__`. | Pruned local semaphores, cancellation events, dual execution buses, and persistent graph database storage engines. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops and empty documents; `test_causal_tda_fusion.py`. |
| **Causal Discovery DTOs**<br>[NEW] @[backend_v2/models/dtos/causal_discovery.py]<br>`@[backend_v2/models/dtos/step_output.py#L59-L73]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys, legacy union syntax. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `StepPayloadValue` extended with `CausalGraphPayloadDTO | CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrail passing in audit loop. |
| **Fusion Chaining Contract**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L366]` | Heuristic step-order detection, runtime flag branching, unmapped document passing. | Studio-driven parameterization: explicit first-class field `Step.causal_source_step_id: str | None = None` referencing upstream causal discovery step. DAG executor transforms upstream `CausalGraphPayloadDTO.nodes` to `ExtractedAtom` via `transform_causal_nodes_to_atoms` and feeds `request.shuffled_atoms`. | Nondeterministic engine picking, automatic graph merging without declared contracts. | Integration test in `test_causal_tda_fusion.py`. |
| **SDUI Model & 19-Block Parity**<br>`@[backend_v2/models/view/sdui.py#L559-L565]`<br>[NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`<br>`@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`<br>`@[backend_v2/services/blueprint.py#L63-L618]`<br>`@[backend_v2/templates/report_template.jinja2]`<br>`@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]`<br>`@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` | Client-side graph semantic calculation, standalone Jinja macros outside SDUI loop, expanding SDUI blocks without updating all 5 parity layers. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union (expanding union to 19 blocks). Handled in Jinja `render_sdui_blocks` macro branch and Dart `SduiBlocksRenderer`. `AdapterContext` extended with typed `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` (in-memory only). `CausalGraphAdapter` transforms `causal_result` into `SduiCausalGraphBlock`. | Standalone Jinja template macros, client-side layout calculators, SVG graph vector serialization over HTTP. | `test_sdui_template_parity.py` asserting exactly 19 blocks; `test_sdui_semantic_parity.py` passing 100%. |
| **1:1 Presentation Parity (Flutter & PDF)**<br>[NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`<br>[NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]` | Sprawling unreadable node graphs in PDF, inconsistent layout between PDF and screen, embedding heavy canvas tools into report print templates. | Identical Unified Causal Action Card in both Flutter and PDF: executive half-page critical causal path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote, prescriptive remediation. Deep interactive exploration decoupled strictly into `CausalInspectorModal`. | Embedded interactive JavaScript canvas in PDF, duplicate styling engines across platforms. | `test_sdui_semantic_parity.py` validating identical token and quote rendering across HTML/PDF and Flutter widgets. |
| **Tabular & Denormalized CSV Export**<br>`@[backend_v2/services/export_service.py#L53-L892]`<br>`@[backend_v2/models/dtos/export.py#L73-L94]`<br>`@[backend_v2/services/localization.py#L382-L488]`<br>`@[backend_v2/l10n/en.json]`<br>`@[backend_v2/l10n/fi.json]` | Modifying dead legacy files `flattener.py` / `flat_record.py`. Producing 2-line legacy CSV. Missing localized sheet keys in translation files. | Add `ReportSheetKey.CAUSAL_GRAPH` and `ReportSheetKey.CAUSAL_DIAGNOSTICS` to `ReportHeaderResolver` with corresponding JSON keys in `en.json` and `fi.json`. Add typed causal columns to `ExportDenormalizedFlatRowDTO`. Worksheets generated natively in `ExportService`. | Eradicated all references to legacy flattener files. | Unit tests in `test_export_service.py` and `test_report_headers_l10n_parity.py` asserting exact column headers and row counts. |
| **Studio UI & Profile Tabs**<br>`@[backend_v2/models/domain/output_profile.py#L36-L353]`<br>`@[backend_v2/models/dtos/output_profile.py#L37-L268]`<br>`@[client_app_v2/lib/core/models/enums.dart#L354-L390]`<br>`@[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]`<br>`@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]`<br>[NEW] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]`<br>`@[client_app_v2/lib/l10n/app_en.arb]`<br>`@[client_app_v2/lib/l10n/app_fi.arb]` | Modifying legacy `ProfileEditorView`. Adding granular micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`). Missing Dart 3 switch branches in `BlockCardRegistry`. Partial DTO mutation. | Full-Duplex Serialization Parity: single SSOT field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` added across Domain Model, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, `OutputProfileResponseDTO`, and Freezed Dart models. Exhaustive Dart 3 switch matching in `BlockCardRegistry`. Compile-time `.arb` localization. | 4 micro-toggles pruned in favor of `CausalDisplayMode(EXECUTIVE, DETAILED)`. Multi-tab configuration wizards. | `flutter_audit_loop.py` build runner verification; compile-time Freezed serialization tests. |

---

## Proposed Changes

### Phase 1: Pre-Implementation Cleanups & Architectural Alignment (Python Backend Only)

#### [ALREADY COMPLETE] ChunkPacketDTO Implementation
- `ChunkPacketDTO(start_block: str, end_block: str, packet_keys: list[str])` has already been fully implemented and verified in active production in `backend_v2/models/dtos/dag_models.py` (line 273) and `backend_v2/services/orchestrator/two_pass_atomizer.py` (line 50).
- No new packet DTO creation or calling site refactoring is required.

#### [MODIFY] @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L77] & @[backend_v2/settings.py#L54-L924]
- Replace the hardcoded `packet_size: int = 50` default parameter in `_calculate_packets` by binding to centralized settings: `packet_size: int = get_settings().two_pass_atomizer_packet_size`.

#### [MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py#L121-L347]
- Parameter Isolation Mandate: In `CausalDiscoveryEngine`, construct `SlidingWindowLinker` with explicit settings parameters: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`.
- DO NOT modify `SlidingWindowLinker.__init__` default parameters (`window_size = 4, overlap = 2`), preventing parameter contamination of existing `TDAEngine` execution paths.

#### [MODIFY] @[backend_v2/models/domain/step.py#L32-L119]
- Modernize `Step.validate_step_consistency`:
  - Correct string literal checks `if self.type == "llm":` and `if self.type == "logic":` to evaluate against typed enums `StepType.LLM` and `StepType.LOGIC` directly.
  - Replace naked `ValueError` with `AppException(ErrorCodes.VALIDATION_FAILED, msg)` in accordance with universal fail-fast laws and RFC 7807 logging.
  - Preserve `StepType.LLM` as macro taxonomy. Add explicit validation branch for causal discovery steps (identified via `is_causal_discovery: bool = False` or criteria blocks containing `PromptBlockCategory.CAUSAL_DISCOVERY`): criteria blocks are not required because arguments are mined dynamically from free-form text.
  - Enforce Fail-Fast validation ensuring `extraction_protocol_block_id` and `cognitive_tier` are non-null.

#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py#L80-L988]
- In `LLMNodeStrategy`, update lines 946-950: when `isinstance(self._engine, CausalDiscoveryEngine)`, record `meta_dict["model_strategy"] = "causal"` in `_step_metadata` instead of defaulting to `"prompt"`.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L160-L187]
- Pre-existing debt cleanup: In `_resolve_execution_engine`, place `PromptBlockCategory.CAUSAL_DISCOVERY` / `step_def.is_causal_discovery` resolution as the FIRST guard clause before the line 179 matrix block category check.
- Remove pre-existing heuristic string matching at line 184 (`"atom_flattening_hook" in step_def.pre_hooks`) and replace with typed step ontology checks.

#### [MODIFY] @[backend_v2/l10n/en.json] & @[backend_v2/l10n/fi.json]
- Pre-Implementation Localization Parity: Register `export_sheet_causal_graph` and `export_sheet_causal_diagnostics` translations in `en.json` and `fi.json` to prevent `test_report_headers_l10n_parity.py` failures when `ReportSheetKey` is extended.

---

### Phase 2: Configuration, DTOs, Studio Foundation & Parity

#### [MODIFY] @[backend_v2/settings.py#L54-L924]
- Add centralized settings for sliding window boundaries, dynamic extraction limits, and packet sizing:
  - `causal_discovery_window_size: int = 4`
  - `causal_discovery_overlap: int = 2`
  - `causal_discovery_max_atoms_per_window: int = 25`
  - `causal_discovery_max_total_atoms: int = 100`
  - `causal_secondary_fault_dampening: float = 0.25`
  - `two_pass_atomizer_packet_size: int = 50`
  - General linker settings preserved independently: `linker_window_size: int = 4`, `linker_overlap: int = 2`.

#### [MODIFY] @[backend_v2/models/enums.py#L253-L262] & @[backend_v2/models/enums.py#L275-L288] & @[backend_v2/models/enums.py#L945-L954] & @[client_app_v2/lib/core/models/enums.dart#L354-L390] & @[backend_v2/tests/unit/test_enum_parity.py#L110-L112]
- Add `PromptBlockCategory.CAUSAL_DISCOVERY = "causal_discovery"` to `enums.py#L253-L262`.
- Add `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"` to `enums.py#L275-L288` and `enums.dart`.
- Add `ReportSheetKey.CAUSAL_GRAPH = "causal_graph"` and `ReportSheetKey.CAUSAL_DIAGNOSTICS = "causal_diagnostics"` to `enums.py#L945-L954`.
- Add `CausalDisplayMode(StrEnum)` and `LaxCausalDisplayMode` with values defined exhaustively as:
  - `EXECUTIVE = "executive"`
  - `DETAILED = "detailed"`
- Add explicit causal engine error codes in `ErrorCodes`:
  - `CAUSAL_DISCOVERY_EMPTY_DOCUMENT = "CAUSAL_DISCOVERY_EMPTY_DOCUMENT"`
  - `CAUSAL_DISCOVERY_CYCLE_DETECTED = "CAUSAL_DISCOVERY_CYCLE_DETECTED"`
  - `CAUSAL_DISCOVERY_DATA_STARVATION = "CAUSAL_DISCOVERY_DATA_STARVATION"`
- Add verification in `test_enum_parity.py` asserting 1:1 parity for `CausalDisplayMode` and `TargetBlockType` between Python and Dart.

#### [MODIFY] @[backend_v2/models/domain/step.py#L32-L119]
- Declare Studio-driven fusion chaining field: `causal_source_step_id: str | None = None` on `Step` (Opaque ID referencing the upstream causal discovery step). When set on a downstream step (specifically a `StepType.LLM` TDA step), instructs the DAG executor to inject upstream causal graph nodes into `shuffled_atoms`.
- Declare `is_causal_discovery: bool = False` to provide explicit step ontology identification.

#### [NEW] @[backend_v2/models/dtos/causal_discovery.py]
- Define strictly typed Pydantic V2 DTO models adhering to `ConfigDict(strict=True, extra="forbid", frozen=True)`:
  - `CausalNodeDTO(BaseModel)`: fields `node_id: str`, `claim: str`, `source_quote: str | None`, `paragraph_ref: str | None`, `status: ExecutionStatus`, `blame_parent_ids: list[str]`, `dependent_child_ids: list[str]`, `tda_score: float | None = None`, `tda_level_key: str | None = None`, `tda_color: str | None = None`.
  - `CausalEdgeDTO(BaseModel)`: fields `source_id: str`, `target_id: str`, `reasoning: str`.
  - `CausalGraphPayloadDTO(BaseModel)`: fields `nodes: list[CausalNodeDTO]`, `edges: list[CausalEdgeDTO]`, `root_cause_node_ids: list[str]`, `cycle_detected: bool`, `isolated_node_ids: list[str]`.
  - `CausalRootCauseDiagnosisDTO(BaseModel)`: fields `failing_node_id: str`, `root_cause_parent_id: str`, `paragraph_ref: str`, `explanation: str`, `penalty_points: float`.
  - `AntiFluffAuditDTO(BaseModel)`: fields `isolated_concept_count: int`, `cycle_detected: bool`, `unsupported_claims_count: int`, `logical_cohesion_score: float`, `detected_hollow_terms: list[str]`.
  - `PrescriptiveRemediationDTO(BaseModel)`: fields `target_node_id: str`, `required_action: str`, `unlocks_node_ids: list[str]`, `potential_score_impact: float`.
  - `FairScoringBreakdownDTO(BaseModel)`: fields `independent_error_count: int`, `cascading_fault_count: int`, `raw_penalty_points: float`, `deduplicated_penalty_points: float`, `dampened_savings_points: float`.
  - `CausalTdaFusionResultDTO(BaseModel)`: fields `graph: CausalGraphPayloadDTO`, `root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO]`, `anti_fluff_audit: AntiFluffAuditDTO`, `prescriptive_remediations: list[PrescriptiveRemediationDTO]`, `fair_scoring: FairScoringBreakdownDTO`.

#### [MODIFY] @[backend_v2/models/dtos/step_output.py#L59-L73]
- Extend `StepPayloadValue` type union to include `CausalGraphPayloadDTO | CausalTdaFusionResultDTO`.
- Extend `StepOutputDTO.data_type` literal to include `"causal"` to guarantee 100% typed deserialization of causal discovery step execution outputs.

#### [MODIFY] @[backend_v2/models/domain/output_profile.py#L36-L353] & @[backend_v2/models/dtos/output_profile.py#L37-L268] & @[backend_v2/models/dtos/output_profile.py#L271-L492] & @[backend_v2/models/dtos/output_profile.py#L495-L645]
- Enforce Full-Duplex Serialization Parity by adding control field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` across Domain Model, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.

#### [MODIFY] @[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123] & @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]
- Update Freezed models in `client_app_v2` to match Python fields 1:1 (`causal_display_mode`).
- Add a single selector in Quorum Studio `OutputProfileCrudView` (`CausalDisplayMode`: Executive / Detailed) and block positioning in the `target_block_order` list with zero micro-toggle clutter.

#### [MODIFY] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]
- Extend Dart 3 switch expressions to handle `TargetBlockType.causalGraphBlock` exhaustively:
  - `detailedBlockTypes` -> append `TargetBlockType.causalGraphBlock`
  - `getBlockTitle` -> `l10n.blockCausalGraphTitle`
  - `getBlockSubtitle` -> `l10n.blockCausalGraphSubtitle`
  - `getBlockIcon` -> `Icons.account_tree_outlined`
  - `getBlockCard` -> `CausalBlockCard`

#### [MODIFY] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140] & @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]
- Wire `TargetBlockType.causalGraphBlock` into Studio tab block ordering and section configuration controls.

#### [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]
- Create dedicated `CausalBlockCard` component providing a streamlined `causal_display_mode` selector (Executive / Detailed) with zero micro-toggle clutter.

#### [MODIFY] @[client_app_v2/lib/l10n/app_en.arb] & @[client_app_v2/lib/l10n/app_fi.arb]
- Add Axis 1 localization keys: `blockCausalGraphTitle`, `blockCausalGraphSubtitle`, `causalDisplayModeExecutive`, `causalDisplayModeDetailed`, `causalCriticalPathTitle`, `causalLexicalQuoteTitle`, `causalRemediationTitle`.

---

### Phase 3: Engine Implementation & Orchestrator Wiring (Standalone & Optional Fusion)

#### [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- Implement `CausalDiscoveryEngine(ExecutionEngine)`:
  - Injects `prompt_compiler: PromptCompiler`.
  - Pure Compute Engine Law: Operates strictly as a pure computational pipeline with zero semaphore or event dependencies.
  - The engine is completely standalone with zero `TDAEngine` dependencies.
  - Constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`.
  - `execute(request: EngineExecutionRequest) -> EngineExecutionResult`:
    1. **Pre-flight Ingress & Hydration**: Verifies document input is non-empty; if empty or containing 0 argument premises, raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)`. Initializes `AliasEngine` and indexes paragraphs (`[B0]...[Bn]`).
    2. **Four-Layer Clean Stack Prompt Compilation**: Enforces static ontology instructions in system prompt prefix for 100% context caching, dynamic theory grounding in `<theory_context>` compiled from configured PromptBlocks (ensuring matrices including Toulmin, Walton, or custom frameworks remain 100% dynamic, pluggable, and omittable), step-level extraction protocol, and dynamic text payload with atom aliasing (`a0`, `a1`) at the tail.
    3. **Phase 0 (Global Ontology)**: Executes `TwoPassAtomizer.execute_phase_0` to construct `GlobalOntologyMap`.
    4. **Phase 1 (Chunked Claim Extraction)**: Executes `TwoPassAtomizer.execute_phase_1` to generate independent `ExtractedAtom` instances with exact physical quote anchoring via `str.find` lexical validation against indexed paragraphs.
    5. **Sliding Window Linking**: Executes `SlidingWindowLinker.link_graph` to connect atoms into a directed `LinkedAtomGraph`.
    6. **Topological Wave Execution**: Passes the graph through `TopologicalEvaluator` with wave evaluation, short-circuit cascades, and fault attribution. Reuses thread-isolated cycle detection: if a circular dependency is detected, sets `cycle_detected=True` and marks cyclic nodes with `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED` without event loop deadlock.
    7. **Pure Compute Result Projection**: Projects standalone causal graph states returning `EngineExecutionResult(synthesis_output=CausalGraphPayloadDTO)`.

#### [MODIFY] @[backend_v2/services/orchestrator/engines/__init__.py]
- Re-export `CausalDiscoveryEngine` in `backend_v2/services/orchestrator/engines/__init__.py` and add it to `__all__` adhering strictly to `explicit_reexport_mandate`.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L136-L366]
- Route to `CausalDiscoveryEngine` in `_resolve_execution_engine` when step prompt blocks contain `PromptBlockCategory.CAUSAL_DISCOVERY` or `step_def.is_causal_discovery` is True. This check is placed FIRST, before the matrix category check.
- **Fusion Chaining Execution (Phase 1A -> Phase 1B)**:
  - When a downstream step defines `step_def.causal_source_step_id is not None`, the DAG executor resolves the completed upstream step's output (`CausalGraphPayloadDTO`).
  - Calls typed transformer `transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -> list[ExtractedAtom]` mapping node IDs, claims, and paragraph references into `ExtractedAtom` models.
  - Injects the resulting atoms directly into `request.shuffled_atoms` for `TDAEngine`. If the upstream step produced 0 valid nodes or failed, Fail-Fast triggers with `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)`.
- Execute five stakeholder benefit pipelines in the orchestrator: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI data projection, and Fair Scoring Deduplication.

---

### Phase 4: Presentation Parity, Studio Dispatch & Export Symmetry

#### [MODIFY] @[backend_v2/models/view/sdui.py#L559-L565] & @[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]
- Define `SduiCausalGraphBlock(SduiBlockBase)` and append it to the polymorphic discriminated union `AnySduiBlock` (expanding the block union from 18 to 19 blocks):
  - `critical_path_nodes: list[CausalNodeDTO]`
  - `critical_edges: list[CausalEdgeDTO]`
  - `root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO]`
  - `anti_fluff_audit: AntiFluffAuditDTO`
  - `prescriptive_remediations: list[PrescriptiveRemediationDTO]`
  - `fair_scoring: FairScoringBreakdownDTO | None = None`
  - `display_mode: CausalDisplayMode = CausalDisplayMode.EXECUTIVE`
  - `intact_claims_count: int`
  - `total_claims_count: int`
  - `summary: I18nText`

#### [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- Transform `EngineExecutionResult` and workflow execution state into `SduiCausalGraphBlock` adhering directly to `OutputProfile.causal_display_mode`.

#### [MODIFY] @[backend_v2/services/blueprint.py#L63-L618]
- Update blueprint assembly: when `TargetBlockType.CAUSAL_GRAPH_BLOCK` appears in profile `target_block_order`, invoke `CausalGraphAdapter` and place the block at that exact sequence position.
- Extract causal step execution results and pass them directly into `AdapterContext.causal_result`.

#### [MODIFY] @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]
- Add typed field `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` to `AdapterContext` to provide direct, fail-fast DTO access for `CausalGraphAdapter` without ad-hoc dictionary searches over `execution.step_states`. This field functions strictly as an in-memory execution context envelope and is NEVER serialized across network or storage boundaries.

#### [MODIFY] @[backend_v2/templates/report_template.jinja2]
- Extend the `render_sdui_blocks` macro branch in `report_template.jinja2` to handle `causal_graph_block`:
  - In `EXECUTIVE` mode: renders a compact Unified Causal Action Card: linear critical root cause path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote card with `paragraph_ref`, prescriptive remediation card, and intact claims count chip (`"X other claims verified logically sound"`), occupying at most half an A4 page in PDF.
  - In `DETAILED` mode: renders the complete argument graph and comprehensive evidentiary table.
  - Adheres strictly to `profile.causal_display_mode` with zero micro-toggles.

#### [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]
- Implement Flutter component rendering the identical visual Unified Causal Action Card matching the Jinja2 PDF layout:
  - Linear critical root cause path matching identical color schemes and layout tokens.
  - Identical lexical fault quote and prescriptive remediation card.
  - Includes a subtle action button `[ 🔍 Open Interactive Inspector ]` for unconstrained full-graph exploration.
  - Wrapped strictly with `AppErrorBoundary` to isolate widget-level rendering errors from the parent viewport.

#### [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]
- Dedicated pro-tool inspector modal for interactive exploration (pan, zoom, side-by-side source text citation highlighting, remediation simulation), decoupled strictly from the primary report presentation and wrapped with `AppErrorBoundary`.

#### [MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]
- Register `SduiCausalGraphBlock` handler in the Dart 3 switch expression binding directly to `SduiCausalGraphWidget`.

#### [MODIFY] @[backend_v2/services/localization.py#L382-L488] & @[backend_v2/services/export_service.py#L53-L892] & @[backend_v2/models/dtos/export.py#L73-L94] & @[backend_v2/l10n/en.json] & @[backend_v2/l10n/fi.json]
- Extend `ReportHeaderResolver` with sheet keys `ReportSheetKey.CAUSAL_GRAPH = "causal_graph"` and `ReportSheetKey.CAUSAL_DIAGNOSTICS = "causal_diagnostics"`.
- Extend `backend_v2/l10n/en.json` and `backend_v2/l10n/fi.json` with localized sheet names for `export_sheet_causal_graph` and `export_sheet_causal_diagnostics`.
- Extend `ExportService` to generate worksheets:
  - Worksheet `Causal Graph` (argument nodes, parent IDs, child IDs, citations, root cause pointers, prescriptive remediations).
  - Worksheet `Causal Diagnostics` (root cause diagnoses, anti-fluff findings, deduplicated fair scoring breakdowns).
  - In fusion mode, enrich `Raw Data` worksheet rows with columns `causal_status`, `blame_parent_id`, and `dependent_count`.
- Extend `ExportDenormalizedFlatRowDTO` in `export.py` with typed causal scalar fields (`causal_node_count: int | None = None`, `causal_root_cause_count: int | None = None`, `causal_raw_penalty: float | None = None`, `causal_deduplicated_penalty: float | None = None`), resolved strictly via `ReportHeaderResolver.get_all_denormalized_csv_headers`.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="ARCHITECTURAL_ALIGNMENT_AND_SETTINGS">
    <action>Bind packet_size default in @[backend_v2/services/orchestrator/two_pass_atomizer.py] _calculate_packets to centralized settings get_settings().two_pass_atomizer_packet_size.</action>
    <action>Enforce parameter isolation in @[backend_v2/services/orchestrator/sliding_window_linker.py]: preserve constructor defaults unchanged; construct SlidingWindowLinker in CausalDiscoveryEngine with explicit causal_discovery_* settings.</action>
    <action>Modernize @[backend_v2/models/domain/step.py] validate_step_consistency to evaluate StepType.LLM and StepType.LOGIC enums directly; allow causal discovery steps without criteria blocks while enforcing extraction_protocol_block_id and cognitive_tier.</action>
    <action>Update @[backend_v2/services/orchestrator/strategies/llm.py] to record model_strategy="causal" in _step_metadata when self._engine is CausalDiscoveryEngine.</action>
    <action>Clean up @[backend_v2/services/orchestrator/dag_executor.py] _resolve_execution_engine to insert causal discovery engine resolution as FIRST guard clause before category checks, and eliminate pre_hooks heuristic string matching.</action>
    <constraint invariant="universal_fail_fast">Enforce exhaustive switch expressions and fail-fast validation across domain models.</constraint>
  </step>

  <step id="2" name="SETTINGS_AND_DTO_FOUNDATION">
    <action>Add causal discovery configuration parameters and two_pass_atomizer_packet_size to @[backend_v2/settings.py] including causal_secondary_fault_dampening, preserving general linker settings.</action>
    <action>Add PromptBlockCategory.CAUSAL_DISCOVERY, TargetBlockType.CAUSAL_GRAPH_BLOCK, and CausalDisplayMode enum to @[backend_v2/models/enums.py] and @[client_app_v2/lib/core/models/enums.dart], and define explicit CAUSAL_DISCOVERY_* ErrorCodes.</action>
    <action>Declare causal_source_step_id and is_causal_discovery fields on Step in @[backend_v2/models/domain/step.py] to enable typed Studio-driven fusion chaining.</action>
    <action>Create strictly typed immutable [NEW] @[backend_v2/models/dtos/causal_discovery.py] (CausalNodeDTO, CausalEdgeDTO, CausalGraphPayloadDTO, CausalRootCauseDiagnosisDTO, AntiFluffAuditDTO, PrescriptiveRemediationDTO, FairScoringBreakdownDTO, and CausalTdaFusionResultDTO).</action>
    <action>Extend StepPayloadValue in @[backend_v2/models/dtos/step_output.py] to include CausalGraphPayloadDTO and CausalTdaFusionResultDTO with data_type="causal".</action>
    <action>Add causal_display_mode field to @[backend_v2/models/domain/output_profile.py] and all serialization DTOs in @[backend_v2/models/dtos/output_profile.py].</action>
    <action>Update Freezed models in @[client_app_v2/lib/features/studio/models/output_profile.dart] and selector in @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart].</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart] to exhaustively handle TargetBlockType.causalGraphBlock in all Dart 3 switch expressions.</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart] and @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart] to integrate Causal Graph block ordering and section settings.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart] rendering causal display mode selector.</action>
    <action>Add Axis 1 localization keys for Causal Graph block title, subtitle, and display modes to @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb].</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce ConfigDict(strict=True, extra='forbid', frozen=True) on all DTOs with zero naked dicts.</constraint>
  </step>

  <step id="3" name="STANDALONE_ENGINE_IMPLEMENTATION">
    <action>Implement [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py] as a standalone pure compute engine without any TDAEngine dependencies or concurrency primitives.</action>
    <action>Update @[backend_v2/services/orchestrator/engines/__init__.py] to re-export CausalDiscoveryEngine in __all__.</action>
    <action>Enforce Four-Layer Clean Stack prompt compilation: static ontology instruction prefix for 100% caching efficiency, dynamic theory context supporting pluggable argumentation matrices, step extraction protocol, and dynamic user payload with atom aliasing (a0, a1) at the tail.</action>
    <action>Enforce exact physical quote validation via str.find against indexed paragraph blocks, prohibiting fuzzy matching.</action>
    <action>Enforce Fail-Fast on empty input text: raise AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT) when 0 argument premises exist.</action>
    <action>Wire TwoPassAtomizer and SlidingWindowLinker (instantiated with explicit causal_discovery_* settings) sequentially with progress reporting callbacks.</action>
    <action>Pass generated LinkedAtomGraph to TopologicalEvaluator for wave-based topological evaluation, blame cascading, and thread-isolated cycle detection (marking cyclic nodes SYSTEM_ERROR with CYCLIC_DEPENDENCY_DETECTED).</action>
    <constraint invariant="single_pipeline_invariant_mandate">Keep CausalDiscoveryEngine completely separate from TDAEngine with zero shared fallback branches.</constraint>
    <constraint invariant="pure_compute_engine_law">Operate 100% as a pure computational pipeline with zero semaphore or event dependencies.</constraint>
  </step>

  <step id="4" name="DAG_ROUTER_AND_OPTIONAL_FUSION">
    <action>Mount CausalDiscoveryEngine in @[backend_v2/services/orchestrator/dag_executor.py] NodeExecutor as the FIRST routing branch in _resolve_execution_engine before block category checks.</action>
    <action>Wire sequential DAG chaining: when step_def.causal_source_step_id is set, extract upstream CausalGraphPayloadDTO and transform nodes via transform_causal_nodes_to_atoms into ExtractedAtom instances feeding downstream TDAEngine shuffled_atoms.</action>
    <action>Enforce data starvation Fail-Fast: if upstream step produced 0 valid nodes or failed, raise AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION).</action>
    <action>Implement five stakeholder benefit pipelines: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI data projection, and Fair Scoring Deduplication.</action>
    <constraint invariant="engine_override_ban">Ensure routing resolves dynamically and deterministically from step ontology without heuristic string parsing.</constraint>
  </step>

  <step id="5" name="SDUI_MODEL_AND_BLUEPRINT_DISPATCH">
    <action>Add SduiCausalGraphBlock to @[backend_v2/models/view/sdui.py], append to AnySduiBlock union (expanding union to 19 blocks), and add Dart Freezed DTOs in @[client_app_v2/lib/shared/models/sdui_block_dto.dart].</action>
    <action>Add causal_result to AdapterContext in @[backend_v2/services/sdui/adapters/base_adapter.py] as strictly an in-memory execution context envelope, and hydrate it in @[backend_v2/services/blueprint.py].</action>
    <action>Implement [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py] respecting OutputProfile causal display settings.</action>
    <action>Update @[backend_v2/services/blueprint.py] to assemble SduiCausalGraphBlock dynamically based on OutputProfile target_block_order.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure 100% semantic parity between Python SDUI model and Flutter Freezed representation.</constraint>
  </step>

  <step id="6" name="PRESENTATION_PARITY_AND_EXPORT_SYMMETRY">
    <action>Extend render_sdui_blocks macro branch in @[backend_v2/templates/report_template.jinja2] rendering the streamlined Unified Causal Action Card matching CausalDisplayMode (occupying at most half an A4 page in PDF).</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart] in Flutter rendering the identical visual layout matching Jinja2 PDF output, wrapped with AppErrorBoundary.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart] in Flutter as an explicitly decoupled supplementary pro-tool modal wrapped with AppErrorBoundary.</action>
    <action>Register SduiCausalGraphBlock handler in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart].</action>
    <action>Extend @[backend_v2/services/localization.py] ReportHeaderResolver with sheet keys CAUSAL_GRAPH and CAUSAL_DIAGNOSTICS, and add causal columns to ExportDenormalizedFlatRowDTO in @[backend_v2/models/dtos/export.py].</action>
    <action>Register export_sheet_causal_graph and export_sheet_causal_diagnostics localization strings in @[backend_v2/l10n/en.json] and @[backend_v2/l10n/fi.json].</action>
    <action>Extend @[backend_v2/services/export_service.py] to generate Causal Graph and Causal Diagnostics sheets in Excel exports and stream denormalized CSV rows.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Run test_sdui_semantic_parity.py and test_sdui_template_parity.py to mathematically verify 19-block 1:1 parity.</constraint>
  </step>

  <step id="7" name="UNIT_TESTING_AND_VERIFICATION">
    <action>Create comprehensive ISTQB unit tests in [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py] asserting CAUSAL_DISCOVERY_EMPTY_DOCUMENT on empty inputs, and CYCLIC_DEPENDENCY_DETECTED on circular inputs.</action>
    <action>Create integration test [NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py] asserting CAUSAL_DISCOVERY_DATA_STARVATION on empty upstream graph, and verifying the five stakeholder benefits.</action>
    <action>Add valid populated SduiCausalGraphBlock instance to @[backend_v2/tests/fixtures/sdui_golden_master.json].</action>
    <action>Update @[backend_v2/tests/unit/test_sdui_template_parity.py] to register SduiCausalGraphBlock in PYDANTIC_BLOCK_MODELS and DART_UNION_TYPE_MAP, updating block count assertion to 19.</action>
    <action>Update @[backend_v2/tests/integration/test_sdui_semantic_parity.py] to verify 1:1 cross-platform SDUI parity.</action>
    <action>Update @[backend_v2/tests/unit/test_enum_parity.py] to assert 1:1 enum parity for TargetBlockType and CausalDisplayMode.</action>
    <constraint invariant="backend_audit_execution">Run uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test.</constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Standalone Engine Unit & Equivalence Tests**:
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py --test`
   - Verifies autonomous 2-pass extraction and linking on free-form text without evaluation matrices or `TDAEngine`.
   - Verifies standalone fault attribution cascade and short-circuit propagation.
   - Verifies circular dependency isolation and orphaned concept detection (`cycle_detected=True`).
   - ISTQB negative boundary tests: empty text document (asserting `AppException`), single isolated node (0 edges), and malformed payloads.
2. **Optional Chained Fusion Integration Tests**:
   - `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py --test`
   - Verifies optional sequential pipeline chaining across two discrete engines (Phase 1A -> Phase 1B).
   - Verifies five core stakeholder benefits (Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI Data Projection, Fair Scoring Deduplication).
3. **Frontend UI & PDF Parity Gate (19-Block Parity)**:
   - `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
   - Verifies that every text token, color token, and citation rendered by Flutter `SduiCausalGraphWidget` matches 1:1 with generated PDF output.
   - `uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py`
   - Verifies via static AST inspection that `SduiCausalGraphBlock` exists across the Jinja2 template, Pydantic discriminated union (19 blocks), and Dart block renderer.
4. **Export Service & Denormalized CSV Tests**:
   - `uv run pytest backend_v2/tests/unit/services/test_export_service.py`
   - Verifies Excel export generates worksheets `Causal Graph` and `Causal Diagnostics`, enriches `Raw Data` with causal columns during fusion runs, and asserts that denormalized CSV output streams typed causal columns resolved via `ReportHeaderResolver`.
5. **Frontend Audit Loop**:
   - `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`
   - Verifies Freezed models and SDUI block definitions achieve 1:1 parity and compiles Quorum Studio UI cleanly.

### Manual Verification
1. **Studio Configuration:** In Quorum Studio `OutputProfileCrudView`, create two profiles: one without `CAUSAL_GRAPH_BLOCK` and one with it (testing `EXECUTIVE` and `DETAILED` modes). Verify on-screen report and PDF reflect configuration immediately.
2. **1:1 Output Parity:** Compare on-screen `SduiCausalGraphWidget` side-by-side with downloaded A4 PDF. Verify the compact Unified Causal Action Card, lexical fault quote, and prescriptive remediation card are identical.
3. **Supplementary Inspection Decoupling:** Click the on-screen action button `[ 🔍 Open Interactive Inspector ]`. Verify the modal opens independently without altering or cluttering the primary report output.
4. **Excel & CSV Verification:** Open the generated `.xlsx` artifact and verify worksheets `Causal Graph` and `Causal Diagnostics` represent argument nodes and root cause diagnoses accurately. Open the `.csv` export and verify typed causal headers match `ReportHeaderResolver`.

### Falsification & Red-Teaming Matrix (Axis 5)

| Invariant / Potential Failure Point | Verification Mechanism | Expected Fail-Fast Behavior |
|:---|:---|:---|
| **Empty or Starved Document:** Document text has 0 argument premises or empty string. | `test_causal_discovery_engine.py` | Raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)`. |
| **Circular Argument Deadlock:** Arguments form a directed cycle (A -> B -> A). | `test_causal_discovery_engine.py` | `TopologicalEvaluator` thread-isolated cycle detection catches cycle, sets `cycle_detected=True`, marks nodes `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED`. |
| **Downstream Fusion Starvation:** Upstream discovery produces 0 nodes, but downstream TDA step expects atoms. | `test_causal_tda_fusion.py` | DAG executor raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)` instead of silently evaluating empty text. |
| **Pure Compute Engine Law:** Request containing semaphores or events or engines mutating executor state. | Architectural Review & Unit Tests | `EngineExecutionRequest` has zero semaphores or events (`ConfigDict(extra='forbid')`); `CausalDiscoveryEngine` executes purely computational transforms. |
| **SDUI 19-Block Parity Gate:** Discrepancy in block count between Pydantic, Jinja2, Dart, or golden master. | `test_sdui_template_parity.py` | Fails fast with `AssertionError: Expected 19 SDUI block types` if any layer is omitted. |
| **Dead Flattener Mutation:** Trying to import or modify deleted `flattener.py` or `flat_record.py`. | Build & Linter Gate | Eradicated from target scope; CSV flows through `ExportDenormalizedFlatRowDTO` and `ReportHeaderResolver`. |
| **Persistence Verification:** Repository operations assert real state mutation. | Unit & Integration Tests | Test suite tests real DTO state transitions and `ConfigDict(strict=True, extra="forbid")` validation roundtrips. |
| **SDUI Cross-Platform Parity:** Token, font, and quote divergence between PDF and Flutter. | `test_sdui_semantic_parity.py` | Validates identical DOM/Widget tokens; Jinja2 macro and Flutter widget share design tokens. |
| **Context Amnesia Prevention:** Refactoring across multiple directories exceeding session budget. | Implementation Governance | Standalone plan is divided into 7 discrete, atomic steps with explicit file lists and verification gates. |
| **Single Pipeline Invariant:** Coexistence of legacy permissive and new strict modes. | Architectural Review | Zero fallback branches; all execution flows deterministically via step ontology resolution. |
| **Roadmap Isolation:** Premature activation into production workflows. | Documentation Gate | Explicit caution box locks plan as `DISTANT FUTURE ROADMAP ONLY`, preventing accidental production seeder activation. |
