> **STATUS: PENDING IMPLEMENTATION (Distant Future Roadmap / Future Extension)**

```xml
<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_context_enriched_decompose_verify.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_topological_engine.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_prompt_orchestration_and_matrix_evaluation.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
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
> `CausalDiscoveryEngine` is implemented and maintained primarily as a **100% standalone and decoupled analysis engine**.
> - The engine executes completely independently without any dependency on `TDAEngine`, without a pre-configured evaluation matrix, and without criteria blocks.
> - It does not require a `request.shuffled_atoms` input; instead, it autonomously extracts argument structures from free-form text, constructs a directed argument graph (`LinkedAtomGraph`), executes topological evaluation, and produces a complete visualizable report block (`SduiCausalGraphBlock`).
> - In standalone mode, node colors and states directly reflect the topological validity of arguments (defined exhaustively as: Green = validated claim, Red = refuted/failed claim, Orange = cascading fault, Grey = orphaned concept).
>
> **Single Pipeline Invariant & Zero-Fallback Compliance:**
> `CausalDiscoveryEngine` and `TDAEngine` remain completely decoupled `ExecutionEngine` implementations. `CausalDiscoveryEngine` binds to workflow steps strictly via the `step_def.type == StepType.CAUSAL_DISCOVERY` identifier. It MUST NOT function as a fallback branch inside `TDAEngine`, and the engines must never be merged into a monolithic class. `TDAEngine` preserves its 100% strict Fail-Fast contract (requiring `request.shuffled_atoms`).
>
> **Optional Causal Graph and TDA Matrix Fusion (Two Separate Engines -> One Unified Result):**
> When a workflow combines normative criteria evaluation with an exploratory causal graph, they are not executed as disconnected parallel reports; instead, they are chained into a two-phase deterministic analysis pipeline:
> 1. **Pipeline Chaining (Discovery extracts -> TDA evaluates):**
>    The workflow does not pick engines nondeterministically; rather, they are chained at the DAG layer into two deterministic phases:
>    - **Phase 1A (`CausalDiscoveryEngine`):** The engine analyzes free-form text and constructs a directed argument graph (`LinkedAtomGraph`), isolating premises, claims, and conclusions into discrete atom nodes.
>    - **Phase 1B (`TDAEngine`):** The TDA engine does not evaluate the raw text corpus randomly; rather, it takes these discovered causal nodes as direct input (`ExtractedAtom` -> `shuffled_atoms`) and evaluates them against normative matrix criteria (verifying: Warrant linkage, Backing evidence, dogmatic quantifiers, and matrix score scales).
>    - **Outcome:** A single analysis pipeline where causal discovery structures the document topology and TDA acts as the qualitative normative judge.
> 2. **Semantic Overlay in the User Interface:**
>    The user interface does not present disjointed parallel tabs or separate duplicate reports; instead, the Flutter SDUI layer renders a single unified interactive graph (`SduiCausalGraphBlock`):
>    - Directed edges between nodes depict the logical progression and causal relationships extracted by the Discovery engine.
>    - In fusion mode, node colors and levels originate directly from the TDA matrix (defined exhaustively as: Green = grounded claim, Red = dogmatic assumption lacking backing).
>    - **Outcome:** The evaluator inspects the logical structure of the text and the qualitative rigor of each argument in a single visual node representation.
> 3. **Causal Root Cause Attribution in Scoring:**
>    Causal Discovery fault attribution (`blame_parent_ids`) binds directly to TDA score deductions and verbal rationale:
>    - When an author loses points under the criteria "Claim Grounding", the system avoids generic feedback and instead reports the causal path: *"Conclusion B failed because it relies on the refuted assumption in node A in paragraph [B2]"*.
>    - **Outcome:** Total score computations and qualitative justifications form a single non-disputable and transparent evaluation audit trail.
>
> **Flutter UI & PDF 1:1 Presentation Parity & Streamlined Output:**
> The interactive on-screen report view (`ReportRendererV2Widget`) and the generated A4 PDF (`report_template.jinja2`) represent the exact same document.
> - **Identical Output Representation:** In both Flutter and PDF, `SduiCausalGraphBlock` renders an identical, compact, and readable **Unified Causal Action Card**, occupying at most half an A4 page in the PDF artifact.
> - **Critical Causal Path Principle:** The output avoids rendering an illegible spaghetti graph of dozens of passing claims. Instead, the output renders a streamlined left-to-right error chain: `[Root Cause]` -> caused -> `[Cascading Fault]` -> resulted in -> `[Score Loss]`, accompanied by the lexical quote and prescriptive remediation. Validated passing claims are summarized in a single compact metric (defined exhaustively as: "X other claims verified logically sound").
> - **Supplementary Inspection Decoupling:** Free-form graph exploration, pan-and-zoom navigation, and in-depth inspection are strictly decoupled into a dedicated modal (`CausalInspectorModal`), opened via an explicit inspection action button. The primary printed and on-screen report layout remains 100% clean, standardized, and identical across screen and paper.
>
> **Streamlined Studio-Driven OutputProfile (Zero-Toggle Model):**
> Adhering to `studio_driven_parameterization_mandate`, the report generator never guesses output layout. In place of complex micro-toggles, `OutputProfile` exposes exactly two clear controls:
> - **Block Selection and Order (`target_block_order`):** The typed enum value `TargetBlockType.CAUSAL_GRAPH_BLOCK`. If the block appears in the list, it renders at that exact position; if omitted, the report generates compactly without the causal block.
> - **Display Mode (`causal_display_mode: CausalDisplayMode`):** A single selector with values defined exhaustively as:
>   - `EXECUTIVE = "executive"` (Default: Compact half-page Unified Causal Action Card – rendering only the critical root cause path, lexical fault quote, and prescriptive remediation).
>   - `DETAILED = "detailed"` (Technical audit mode: complete argument graph and exhaustive evidentiary table for domain experts).
> - **Micro-Toggle Elimination:** Isolated micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) are eradicated, preserving a streamlined profile editor.
>
> **Forensic Excel & Flat CSV Symmetry:**
> Output parity extends directly to tabular data exports (`ExportService`):
> - **Worksheet "Causal Graph":** Relational table of nodes, claims, paragraph citations `[Bx]`, statuses, parent IDs, child IDs, root cause pointers, and remediations.
> - **Worksheet "Causal Diagnostics":** Tabulation of root cause diagnoses, Anti-Fluff findings, and deduplicated fair scoring breakdowns.
> - **Normative "Raw Data" Worksheet Enrichment:** In fusion mode, TDA atom rows are enriched with scalar columns: `causal_status`, `blame_parent_id`, and `dependent_count`.
> - **Flat CSV (`FlatFileService`):** `FlatExecutionRecordDTO` is extended with centralized scalar causal metrics. The output is strictly a two-line flat CSV artifact (line 1 = comma-delimited column headers, line 2 = scalar values), containing zero nested group headers or multi-level hierarchies.
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

---

## Scope & Boundaries

### Target Files:
- `[NEW]` @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- `[NEW]` @[backend_v2/models/dtos/causal_discovery.py]
- `[NEW]` @[backend_v2/services/sdui/adapters/causal_graph_adapter.py]
- `[MODIFY]` @[backend_v2/settings.py#L54-L910]
- `[MODIFY]` @[backend_v2/models/enums.py#L111-L115]
- `[MODIFY]` @[backend_v2/models/enums.py#L272-L285]
- `[MODIFY]` @[backend_v2/models/domain/step.py#L32-L119]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]
- `[MODIFY]` @[backend_v2/models/dtos/dag_models.py#L18-L57]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]
- `[MODIFY]` @[backend_v2/models/domain/output_profile.py#L35-L346]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L36-L260]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L263-L475]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L478-L621]
- `[MODIFY]` @[backend_v2/models/dtos/step_output.py#L57-L71]
- `[MODIFY]` @[backend_v2/models/view/sdui.py#L563-L569]
- `[MODIFY]` @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]
- `[MODIFY]` @[backend_v2/services/blueprint.py#L52-L608]
- `[MODIFY]` @[backend_v2/templates/report_template.jinja2#L87-L550]
- `[MODIFY]` @[backend_v2/services/export_service.py#L82-L301]
- `[MODIFY]` @[backend_v2/services/flattener.py#L24-L76]
- `[MODIFY]` @[backend_v2/models/dtos/flat_record.py#L17-L55]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L136-L372]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/__init__.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_enum_parity.py#L110-L112]
- `[MODIFY]` @[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]
- `[MODIFY]` @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]
- `[MODIFY]` @[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]
- `[MODIFY]` @[client_app_v2/lib/core/models/enums.dart#L354-L390]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]
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

### Context / Read-Only Files:
- `@[backend_v2/services/orchestrator/engines/base.py]`
- `@[backend_v2/services/orchestrator/engines/tda_engine.py]`
- `@[backend_v2/services/orchestrator/topological_evaluator.py]`
- `@[backend_v2/services/orchestrator/result_projector.py]`
- `@[client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart]`

### Architectural Directives (5-Column Synthesis):

| Target Scope & Boundaries | Eradicated Duct-Tape (Under-Engineering Ban) | Approved Best Practice (Target Invariant) | Pruned Over-Engineering (Complexity Slayer) | Fail-Fast Proof Anchor (Deterministic Verification) |
| :--- | :--- | :--- | :--- | :--- |
| **Settings Configuration**<br>`@[backend_v2/settings.py#L54-L910]` | Magic constants in sliding window loops, hardcoded window sizes, fallback `getattr(settings, ...)` access. | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. | Speculative per-domain sliding window overrides and dynamic runtime reload factories. | `Settings.model_validate({})` strict type validation in unit tests; `test_settings.py`. |
| **SSOT Enums & Parity**<br>`@[backend_v2/models/enums.py#L111-L115]`<br>`@[backend_v2/models/enums.py#L272-L285]`<br>`@[client_app_v2/lib/core/models/enums.dart#L354-L390]`<br>`@[backend_v2/tests/unit/test_enum_parity.py#L110-L112]` | Untyped string comparisons (`model_strategy == "causal_discovery"`), heuristic string matching, ad-hoc string literals for block types. | `StepType.CAUSAL_DISCOVERY = "causal_discovery"`, `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`, and `CausalDisplayMode(StrEnum)` with values strictly: `EXECUTIVE = "executive"`, `DETAILED = "detailed"`. 1:1 Dart `@JsonEnum` parity. | Granular display mode permutations (isolated anti-fluff toggles, remediations toggles, fair-scoring toggles). | `test_sdui_template_parity.py` AST enum validation; `test_enum_parity.py` verifying TargetBlockType and CausalDisplayMode parity; Dart compile-time enum switch exhaustion. |
| **Pre-Implementation Atomizer Cleanups**<br>`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]`<br>`@[backend_v2/models/dtos/dag_models.py#L18-L57]`<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]` | Returning anonymous 3-tuples (`tuple[str, str, list[str]]`) in `_calculate_packets` ("Tuple Hell"), hardcoded magic window sizes (`window_size = 4, overlap = 2`) in constructor. | Encapsulate chunk packet bounds into typed immutable `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`. In `SlidingWindowLinker`, bind default arguments directly to `get_settings().causal_discovery_window_size` and `causal_discovery_overlap`. | Intermediate packet wrapper classes or custom iterator protocols. | `uv run python scripts/audit_dict_eradication.py` passing AST guardrails; unit tests in `test_two_pass_atomizer.py` and `test_causal_discovery_engine.py`. |
| **Step Consistency & Strategy Registry**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]` | Bypassing `validate_step_consistency` by hacking `StepType.LLM` with empty criteria blocks, using raw string literals (`"llm"`, `"logic"`), or duck-typing missing criteria block IDs. | Explicit `Step.validate_step_consistency` branch for `StepType.CAUSAL_DISCOVERY` allowing empty criteria blocks while enforcing `extraction_protocol_block_id` and `cognitive_tier`, with all type checks bound to `StepType` enums. `NODE_STRATEGY_REGISTRY` and `NodeStrategyFactory.get_strategy` strictly map `StepType.CAUSAL_DISCOVERY` to `LLMNodeStrategy`. | Separate `CausalStep` domain model subclass or parallel step validation pipeline. | Unit tests asserting `AppException` when `extraction_protocol_block_id` is missing; `backend_audit_loop.py`. |
| **Causal Discovery DTOs**<br>[NEW] @[backend_v2/models/dtos/causal_discovery.py]<br>`@[backend_v2/models/dtos/step_output.py#L57-L71]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `StepPayloadValue` extended with `CausalGraphPayloadDTO` and `CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrail passing in audit loop. |
| **OutputProfile & Studio UX**<br>`@[backend_v2/models/domain/output_profile.py#L35-L346]`<br>`@[backend_v2/models/dtos/output_profile.py#L36-L260]`<br>`@[backend_v2/models/dtos/output_profile.py#L263-L475]`<br>`@[backend_v2/models/dtos/output_profile.py#L478-L621]`<br>`@[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]`<br>`@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]`<br>[NEW] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]`<br>`@[client_app_v2/lib/l10n/app_en.arb]`<br>`@[client_app_v2/lib/l10n/app_fi.arb]` | Micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`), missing Dart 3 switch branches in `BlockCardRegistry`, missing `.arb` localization keys, partial DTO mutation violating serialization parity. | Full-Duplex Serialization Parity: single SSOT field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` added across Domain Model, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`. Exhaustive Dart 3 switch matching across `getBlockTitle`, `getBlockSubtitle`, `getBlockIcon`, `getBlockCard` in `BlockCardRegistry`. Compile-time `.arb` localization. | Multi-tab studio configuration wizards and custom per-node styling controls. | `flutter_audit_loop.py` build runner verification; compile-time Freezed serialization tests. |
| **Causal Discovery Engine & Execution**<br>[NEW] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`<br>`@[backend_v2/services/orchestrator/engines/__init__.py]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]` | Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, mutating existing step execution states in-place without DTOs, routing through fallback branches in `_resolve_execution_engine`. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` cleanly implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult`, re-exported in `__all__`. `NodeExecutor._resolve_execution_engine` routes via `step_def.type == StepType.CAUSAL_DISCOVERY`. Sequential DAG chaining (Step 1A nodes hydrate Step 1B `shuffled_atoms`) strictly via immutable DTOs. | Dual execution buses, speculative actor frameworks, and persistent graph database storage engines. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops and empty documents; `test_causal_tda_fusion.py`. |
| **SDUI Model, Adapter & Blueprint**<br>`@[backend_v2/models/view/sdui.py#L563-L569]`<br>[NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`<br>`@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`<br>`@[backend_v2/services/blueprint.py#L52-L608]`<br>`@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]` | Client-side graph semantic calculation, client inferring root causes, generic raw JSON passing, missing `SduiBlockBase` polymorphism. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union. `AdapterContext` extended with typed `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None`. `CausalGraphAdapter` transforms `causal_result` into `SduiCausalGraphBlock` strictly adhering to `causal_display_mode`. 1:1 Freezed `@Freezed(unionKey: 'block_type')` Dart model. | Dynamic client-side layout calculators, SVG graph vector serialization over HTTP, multi-pass SDUI transformers. | `test_sdui_template_parity.py` and `test_sdui_semantic_parity.py` passing 100%. |
| **1:1 Presentation Parity (Flutter & PDF)**<br>`@[backend_v2/templates/report_template.jinja2#L87-L550]`<br>[NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`<br>[NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]` | Sprawling unreadable node graphs in PDF, inconsistent layout between PDF and screen, embedding heavy canvas tools into report print templates. | Identical Unified Causal Action Card in both Flutter and PDF: executive half-page critical causal path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote, prescriptive remediation. Deep interactive exploration decoupled strictly into `CausalInspectorModal`. | Embedded interactive JavaScript canvas in PDF, duplicate styling engines across platforms. | `test_sdui_semantic_parity.py` validating identical token and quote rendering across HTML/PDF and Flutter widgets. |
| **Tabular Export & Flat CSV Symmetry**<br>`@[backend_v2/services/export_service.py#L82-L301]`<br>`@[backend_v2/services/flattener.py#L24-L76]`<br>`@[backend_v2/models/dtos/flat_record.py#L17-L55]` | Multi-row hierarchical CSV headers, ragged nested Excel rows, missing causal columns in flat exports. | Excel sheets `Causal Graph` and `Causal Diagnostics` in `ExportService`. `FlatExecutionRecordDTO` receives typed scalar causal fields (`causal_node_count`, `causal_root_cause_count`, `causal_raw_penalty`, `causal_deduplicated_penalty`). `FlatFileService` outputs strictly 2-line flat CSV (line 1 = header names, line 2 = scalar values). | Pivot table generators, dynamic CSV dialect negotiation, secondary XLSX macro formatting. | Unit tests in `test_export_service.py` asserting exact column headers and row counts. |
| **Regression & Integration Testing**<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]`<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`<br>`@[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]`<br>`@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]`<br>`@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` | Happy-path-only tests, mocking persistence with static dummy dicts, unasserted mock calls. | Comprehensive ISTQB tests: equivalence partitioning, boundary value analysis, negative partitions (at least 2 negative tests per feature: empty text, single atom, circular dependency, disconnected subgraph). Integration tests for Phase 1A -> Phase 1B sequential chaining. | Flaky network integration tests, long-running end-to-end browser tests for unit logic. | `uv run python scripts/backend_audit_loop.py` exiting 0 with Ruff, MyPy, and Pytest all green. |

---

## Proposed Changes

### Phase 1: Pre-Implementation Cleanups & Architectural Alignment

#### [MODIFY] @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71] & @[backend_v2/models/dtos/dag_models.py#L18-L57]
- Resolve technical debt: replace the anonymous 3-tuple `list[tuple[str, str, list[str]]]` in `TwoPassAtomizer._calculate_packets` with a strictly typed and immutable Pydantic V2 model `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])`.
- Update `execute_phase_0`, `execute_phase_1`, and `execute_phase_1_drafts` to unpack `ChunkPacketDTO` via explicit field access instead of positional tuple unpacking.
- Replace the hardcoded `packet_size = 50` default by binding directly to centralized settings.

#### [MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]
- Replace hardcoded default parameters in `SlidingWindowLinker.__init__` (`window_size = 4, overlap = 2`) by binding default values directly to centralized configuration `get_settings().causal_discovery_window_size` and `get_settings().causal_discovery_overlap`.

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]
- Update `test_calculate_packets_empty` and add packet unit tests asserting `ChunkPacketDTO` fields (`start_block`, `end_block`, `block_keys`).

#### [MODIFY] @[backend_v2/models/domain/step.py#L32-L119]
- Update `Step.validate_step_consistency`:
  - Correct string literal checks `if self.type == "llm":` and `if self.type == "logic":` to evaluate against typed enums `StepType.LLM` and `StepType.LOGIC` directly.
  - Add explicit validation branch for `StepType.CAUSAL_DISCOVERY`: criteria blocks (`criteria_block_ids`) are not required because arguments are mined dynamically from free-form text.
  - Enforce Fail-Fast validation ensuring `extraction_protocol_block_id` and `cognitive_tier` are non-null.

#### [MODIFY] @[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]
- Register `StepType.CAUSAL_DISCOVERY -> LLMNodeStrategy` in `NodeStrategyFactory.get_strategy` dispatch mapping and `NODE_STRATEGY_REGISTRY` dictionary.

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

### Phase 2: Configuration, DTOs & Studio OutputProfile Foundation

#### [MODIFY] @[backend_v2/settings.py#L54-L910]
- Add centralized settings for sliding window boundaries, dynamic extraction limits, and packet sizing:
  - `causal_discovery_window_size: int = 4`
  - `causal_discovery_overlap: int = 2`
  - `causal_discovery_max_atoms_per_window: int = 25`
  - `causal_discovery_max_total_atoms: int = 100`
  - `causal_secondary_fault_dampening: float = 0.25`
  - `two_pass_atomizer_packet_size: int = 50`

#### [MODIFY] @[backend_v2/models/enums.py#L111-L115] & @[backend_v2/models/enums.py#L272-L285] & @[client_app_v2/lib/core/models/enums.dart#L354-L390] & @[backend_v2/tests/unit/test_enum_parity.py#L110-L112]
- Add `StepType.CAUSAL_DISCOVERY = "causal_discovery"`.
- Add `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`.
- Add `CausalDisplayMode(StrEnum)` and `LaxCausalDisplayMode` with values defined exhaustively as:
  - `EXECUTIVE = "executive"`
  - `DETAILED = "detailed"`
- Add verification in `test_enum_parity.py` asserting 1:1 parity for `CausalDisplayMode` and `TargetBlockType` between Python and Dart.

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

#### [MODIFY] @[backend_v2/models/dtos/step_output.py#L57-L71]
- Extend `StepPayloadValue` type union to include `CausalGraphPayloadDTO | CausalTdaFusionResultDTO`.
- Extend `StepOutputDTO.data_type` literal to include `"causal"` to guarantee 100% typed deserialization of causal discovery step execution outputs.

#### [MODIFY] @[backend_v2/models/domain/output_profile.py#L35-L346] & @[backend_v2/models/dtos/output_profile.py#L36-L260] & @[backend_v2/models/dtos/output_profile.py#L263-L475] & @[backend_v2/models/dtos/output_profile.py#L478-L621]
- Enforce Full-Duplex Serialization Parity by adding control field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` across Domain Model, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.

#### [MODIFY] @[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123] & @[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]
- Update Freezed models in `client_app_v2` to match Python fields 1:1 (`causal_display_mode`).
- Add a single selector in Quorum Studio `ProfileEditorView` (`CausalDisplayMode`: Executive / Detailed) and block positioning in the `target_block_order` list with zero micro-toggle clutter.

---

### Phase 3: Engine Implementation & Orchestrator Wiring (Standalone & Optional Fusion)

#### [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]
- Implement `CausalDiscoveryEngine(ExecutionEngine)`:
  - Injects `prompt_compiler: PromptCompiler`.
  - The engine is completely standalone with zero `TDAEngine` dependencies.
  - `execute(request: EngineExecutionRequest) -> EngineExecutionResult`:
    1. **Pre-flight Ingress & Hydration**: Initializes `AliasEngine`, indexes paragraphs (`[B0]...[Bn]`).
    2. **Phase 0 (Global Ontology)**: Executes `TwoPassAtomizer.execute_phase_0` to construct `GlobalOntologyMap`.
    3. **Phase 1 (Chunked Claim Extraction)**: Executes `TwoPassAtomizer.execute_phase_1` to generate independent `ExtractedAtom` instances.
    4. **Sliding Window Linking**: Executes `SlidingWindowLinker.link_graph` to connect atoms into a directed `LinkedAtomGraph`.
    5. **Topological Wave Execution**: Passes the graph through `EnrichedDagExecutor` / `TopologicalEvaluator` with wave evaluation, short-circuit cascades, and fault attribution.
    6. **Standalone Result Projection**: Projects standalone causal graph states returning an `EngineExecutionResult`.

#### [MODIFY] @[backend_v2/services/orchestrator/engines/__init__.py]
- Re-export `CausalDiscoveryEngine` in `backend_v2/services/orchestrator/engines/__init__.py` and add it to `__all__` adhering strictly to `explicit_reexport_mandate`.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L136-L372] & @[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]
- Extend `_resolve_execution_engine` routing to support `step_def.type == StepType.CAUSAL_DISCOVERY`.
- Optional sequential chaining (Phase 1A -> Phase 1B): Phase 1A generated nodes pass as typed extracted atoms to feed Phase 1B inputs when the workflow is explicitly configured.
- Execute five stakeholder benefit pipelines in the orchestrator: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, and Fair Scoring Deduplication.

---

### Phase 4: Presentation Parity, Studio Dispatch & Export Symmetry

#### [MODIFY] @[backend_v2/models/view/sdui.py#L563-L569] & @[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]
- Define `SduiCausalGraphBlock(SduiBlockBase)` in the polymorphic SDUI block union `AnySduiBlock`:
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

#### [MODIFY] @[backend_v2/services/blueprint.py#L52-L608]
- Update blueprint assembly: when `TargetBlockType.CAUSAL_GRAPH_BLOCK` appears in profile `target_block_order`, invoke `CausalGraphAdapter` and place the block at that exact sequence position.
- Extract causal step execution results and pass them directly into `AdapterContext.causal_result`.

#### [MODIFY] @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]
- Add typed field `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` to `AdapterContext` to provide direct, fail-fast DTO access for `CausalGraphAdapter` without ad-hoc dictionary searches over `execution.step_states`.

#### [MODIFY] @[backend_v2/templates/report_template.jinja2#L87-L550]
- Implement Jinja2 macro `render_causal_graph_block`:
  - In `EXECUTIVE` mode: renders a compact Unified Causal Action Card (critical root cause path from left to right, lexical fault quote, prescriptive remediation, and confirmation of intact claims) occupying at most half an A4 page.
  - In `DETAILED` mode: renders the complete argument graph and comprehensive evidentiary table.
  - Adheres strictly to `profile.causal_display_mode` with zero micro-toggles.

#### [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]
- Implement Flutter component rendering the identical visual Unified Causal Action Card matching the Jinja2 macro:
  - Linear critical root cause path matching identical color schemes and layout tokens.
  - Identical lexical fault quote and prescriptive remediation card.
  - Includes a subtle action button `[ 🔍 Open Interactive Inspector ]` for unconstrained full-graph exploration.

#### [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]
- Dedicated pro-tool inspector modal for interactive exploration (pan, zoom, side-by-side source text citation highlighting, remediation simulation), decoupled strictly from the primary report presentation.

#### [MODIFY] @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]
- Register `SduiCausalGraphBlock` handler binding directly to `SduiCausalGraphWidget`.

#### [MODIFY] @[backend_v2/services/export_service.py#L82-L301]
- Add Excel export support for causal graphs:
  - Worksheet `Causal Graph` (argument nodes, parent IDs, child IDs, citations, root cause pointers, prescriptive remediations).
  - Worksheet `Causal Diagnostics` (root cause diagnoses, anti-fluff findings, deduplicated fair scoring breakdowns).
  - In fusion mode, enrich `Raw Data` worksheet rows with columns `causal_status`, `blame_parent_id`, and `dependent_count`.

#### [MODIFY] @[backend_v2/services/flattener.py#L24-L76] & @[backend_v2/models/dtos/flat_record.py#L17-L55]
- Add scalar fields to `FlatExecutionRecordDTO`: `causal_node_count`, `causal_edge_count`, `causal_validated_count`, `causal_root_cause_count`, `causal_cascading_fault_count`, `causal_orphan_count`, `causal_cycle_detected`, `causal_cohesion_score`, `causal_raw_penalty`, `causal_deduplicated_penalty`, `causal_dampened_savings`, `causal_primary_root_cause_node`, `causal_primary_root_cause_ref`.
- Export outputs a strictly 2-line flat CSV artifact (line 1 = header names, line 2 = scalar values). The file contains zero column group headers, intermediate subheaders, or multi-level hierarchies, consisting strictly of comma-separated scalar values.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUP_AND_REGISTRATION">
    <action>Create ChunkPacketDTO in @[backend_v2/models/dtos/dag_models.py] to replace anonymous 3-tuples.</action>
    <action>Refactor @[backend_v2/services/orchestrator/two_pass_atomizer.py] _calculate_packets to return list[ChunkPacketDTO] and remove magic numbers.</action>
    <action>Update @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186] to assert on ChunkPacketDTO fields.</action>
    <action>Refactor @[backend_v2/services/orchestrator/sliding_window_linker.py] constructor to read defaults directly from Settings.</action>
    <action>Update @[backend_v2/models/domain/step.py] validate_step_consistency to allow StepType.CAUSAL_DISCOVERY without criteria blocks while enforcing extraction_protocol_block_id.</action>
    <action>Update @[backend_v2/services/orchestrator/strategies/registry.py] NodeStrategyFactory and NODE_STRATEGY_REGISTRY to map StepType.CAUSAL_DISCOVERY to LLMNodeStrategy.</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart] to exhaustively handle TargetBlockType.causalGraphBlock in all Dart 3 switch expressions.</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart] to integrate Causal Graph block ordering.</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart] to integrate Causal Graph section settings.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart] rendering causal display mode selector.</action>
    <action>Add Axis 1 localization keys for Causal Graph block title, subtitle, and display modes to @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb].</action>
    <constraint invariant="universal_fail_fast">Enforce exhaustive switch expressions and fail-fast validation across domain models.</constraint>
  </step>

  <step id="2" name="SETTINGS_AND_DTO_FOUNDATION">
    <action>Add causal discovery configuration parameters and two_pass_atomizer_packet_size to @[backend_v2/settings.py] including causal_secondary_fault_dampening.</action>
    <action>Add StepType.CAUSAL_DISCOVERY, TargetBlockType.CAUSAL_GRAPH_BLOCK, and CausalDisplayMode enum to @[backend_v2/models/enums.py] and @[client_app_v2/lib/core/models/enums.dart].</action>
    <action>Create strictly typed immutable [NEW] @[backend_v2/models/dtos/causal_discovery.py] (CausalNodeDTO, CausalEdgeDTO, CausalGraphPayloadDTO, CausalRootCauseDiagnosisDTO, AntiFluffAuditDTO, PrescriptiveRemediationDTO, FairScoringBreakdownDTO, and CausalTdaFusionResultDTO).</action>
    <action>Extend StepPayloadValue in @[backend_v2/models/dtos/step_output.py#L57-L71] to include CausalGraphPayloadDTO and CausalTdaFusionResultDTO with data_type="causal".</action>
    <action>Add causal_display_mode field to @[backend_v2/models/domain/output_profile.py] and all serialization DTOs in @[backend_v2/models/dtos/output_profile.py].</action>
    <action>Update Freezed models in @[client_app_v2/lib/features/studio/models/output_profile.dart] and selector in @[client_app_v2/lib/features/studio/views/profile_editor_view.dart].</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce ConfigDict(strict=True, extra='forbid', frozen=True) on all DTOs with zero naked dicts.</constraint>
  </step>

  <step id="3" name="STANDALONE_ENGINE_IMPLEMENTATION">
    <action>Implement [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py] as a standalone engine without any TDAEngine dependencies.</action>
    <action>Update @[backend_v2/services/orchestrator/engines/__init__.py] to re-export CausalDiscoveryEngine in __all__.</action>
    <action>Wire TwoPassAtomizer and SlidingWindowLinker sequentially with progress reporting callbacks.</action>
    <action>Pass generated LinkedAtomGraph to TopologicalEvaluator for wave-based topological evaluation, blame cascading, and anti-fluff checks.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Keep CausalDiscoveryEngine completely separate from TDAEngine with zero shared fallback branches.</constraint>
    <constraint invariant="anti_god_file_dumping">Isolate engine logic strictly in its own file under 200 lines.</constraint>
  </step>

  <step id="4" name="DAG_ROUTER_AND_OPTIONAL_FUSION">
    <action>Mount CausalDiscoveryEngine in @[backend_v2/services/orchestrator/dag_executor.py] NodeExecutor and DAGExecutor under StepType.CAUSAL_DISCOVERY supporting standalone execution.</action>
    <action>Wire optional sequential DAG chaining allowing Step 1A (CausalDiscoveryEngine) outputs to feed directly into Step 1B (TDAEngine) shuffled_atoms input when configured.</action>
    <action>Implement five stakeholder benefit pipelines: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI data projection, and Fair Scoring Deduplication.</action>
    <constraint invariant="engine_override_ban">Ensure routing resolves dynamically and deterministically from step blueprint StepType without heuristic string parsing.</constraint>
  </step>

  <step id="5" name="SDUI_MODEL_AND_BLUEPRINT_DISPATCH">
    <action>Add SduiCausalGraphBlock to @[backend_v2/models/view/sdui.py#L563-L569] and Dart Freezed DTOs in @[client_app_v2/lib/shared/models/sdui_block_dto.dart].</action>
    <action>Add causal_result to AdapterContext in @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47] and hydrate it in @[backend_v2/services/blueprint.py#L52-L608].</action>
    <action>Implement [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py] respecting OutputProfile causal display settings.</action>
    <action>Update @[backend_v2/services/blueprint.py] to assemble SduiCausalGraphBlock dynamically based on OutputProfile target_block_order.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure 100% semantic parity between Python SDUI model and Flutter Freezed representation.</constraint>
  </step>

  <step id="6" name="PRESENTATION_PARITY_AND_EXPORT_SYMMETRY">
    <action>Implement Jinja2 macro in @[backend_v2/templates/report_template.jinja2] rendering the streamlined Unified Causal Action Card matching CausalDisplayMode.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart] in Flutter rendering the identical visual layout matching Jinja2 PDF output.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart] in Flutter as an explicitly decoupled supplementary pro-tool modal.</action>
    <action>Register SduiCausalGraphBlock handler in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart].</action>
    <action>Extend @[backend_v2/services/export_service.py] to generate Causal Graph and Causal Diagnostics sheets in Excel exports.</action>
    <action>Extend @[backend_v2/services/flattener.py] to project causal metrics into @[backend_v2/models/dtos/flat_record.py].</action>
    <constraint invariant="sdui_contract_fracture_prevention">Run test_sdui_semantic_parity.py and test_sdui_template_parity.py to mathematically verify 1:1 parity.</constraint>
  </step>

  <step id="7" name="UNIT_TESTING_AND_VERIFICATION">
    <action>Create comprehensive ISTQB unit tests in [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py] covering standalone execution, cycle detection, and empty document boundaries.</action>
    <action>Create integration test [NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py] verifying optional sequential pipeline chaining, the five stakeholder benefits, and OutputProfile toggles.</action>
    <action>Add valid populated SduiCausalGraphBlock instance to @[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482].</action>
    <action>Update @[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148] to register SduiCausalGraphBlock in PYDANTIC_BLOCK_MODELS and DART_UNION_TYPE_MAP.</action>
    <action>Update @[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380] to verify 1:1 cross-platform SDUI parity.</action>
    <action>Update @[backend_v2/tests/unit/test_enum_parity.py#L110-L112] to assert 1:1 enum parity for TargetBlockType and CausalDisplayMode.</action>
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
3. **Frontend UI & PDF Parity Gate**:
   - `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`
   - Verifies that every text token, color token, and citation rendered by Flutter `SduiCausalGraphWidget` matches 1:1 with generated PDF output.
   - `uv run pytest backend_v2/tests/unit/test_sdui_template_parity.py`
   - Verifies via static AST inspection that `SduiCausalGraphBlock` exists across the Jinja2 template, Pydantic discriminated union, and Dart block renderer.
4. **Export Service & Flat CSV Tests**:
   - `uv run pytest backend_v2/tests/unit/services/test_export_service.py`
   - Verifies Excel export generates worksheets `Causal Graph` and `Causal Diagnostics`, and enriches `Raw Data` with causal columns during fusion runs.
5. **Frontend Audit Loop**:
   - `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`
   - Verifies Freezed models and SDUI block definitions achieve 1:1 parity and compiles Quorum Studio UI cleanly.

### Manual Verification
1. **Studio Configuration:** In Quorum Studio, create two profiles: one without `CAUSAL_GRAPH_BLOCK` and one with it (testing `EXECUTIVE` and `DETAILED` modes). Verify on-screen report and PDF reflect configuration immediately.
2. **1:1 Output Parity:** Compare on-screen `SduiCausalGraphWidget` side-by-side with downloaded A4 PDF. Verify the compact Unified Causal Action Card, lexical fault quote, and prescriptive remediation card are identical.
3. **Supplementary Inspection Decoupling:** Click the on-screen action button `[ 🔍 Open Interactive Inspector ]`. Verify the modal opens independently without altering or cluttering the primary report output.
4. **Excel Verification:** Open the generated `.xlsx` artifact and verify worksheets `Causal Graph` and `Causal Diagnostics` represent argument nodes and root cause diagnoses accurately.
