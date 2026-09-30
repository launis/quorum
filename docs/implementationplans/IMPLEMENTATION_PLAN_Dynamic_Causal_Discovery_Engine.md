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
> - **Dynamic Matrix Independence & Extensibility:** All evaluation matrices and argumentation frameworks (referencing dynamic PromptBlocks including Toulmin, Walton, or custom enterprise criteria) are 100% dynamic domain entities configured in Quorum Studio and persisted in `seed_data.json`. Matrices are never hardcoded in source code: workflows can configure zero, one, or multiple dynamic matrices; matrices can be added, updated, or removed dynamically without modifying backend code.
> 1. **Pipeline Chaining (Discovery extracts -> TDA evaluates):**
>    The workflow does not pick engines nondeterministically; rather, they are chained at the DAG layer into two deterministic phases:
>    - **Phase 1A (`CausalDiscoveryEngine`):** The engine analyzes free-form text and constructs a directed argument graph (`LinkedAtomGraph`), isolating premises, claims, and conclusions into discrete atom nodes without requiring any evaluation matrix.
>    - **Phase 1B (`TDAEngine`):** The TDA engine does not evaluate the raw text corpus randomly; rather, it takes these discovered causal nodes as direct input (`ExtractedAtom` -> `shuffled_atoms`) and evaluates them against whichever dynamic criteria matrix is configured for that step (verifying: Warrant linkage, Backing evidence, dogmatic quantifiers, and matrix score scales).
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
> - **`CausalStep` Domain Subclass: PRUNED.** Rejected in favor of the existing `Step` domain model with validation branching, avoiding class hierarchy explosion.
> - **Persistent Graph Database: PRUNED.** Rejected in favor of in-memory transient graph representation (`LinkedAtomGraph`) projected directly to SDUI `SduiCausalGraphBlock` and trace JSON.
> - **Granular OutputProfile Micro-Toggles: PRUNED.** Isolated toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`) are eradicated in favor of a single SSOT selector `causal_display_mode: CausalDisplayMode`.
> - **8 Dedicated Pydantic V2 DTOs: RETAINED.** `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, and `CausalTdaFusionResultDTO` are retained as irreducible domain contracts.

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
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]
- `[MODIFY]` @[backend_v2/models/dtos/dag_models.py#L18-L57]
- `[MODIFY]` @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]
- `[MODIFY]` @[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]
- `[MODIFY]` @[backend_v2/models/domain/output_profile.py#L35-L346]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L36-L260]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L263-L475]
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L478-L621]
- `[MODIFY]` @[backend_v2/models/dtos/step_output.py#L57-L71]
- `[MODIFY]` @[backend_v2/models/view/sdui.py#L563-L569, L797-L817]
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
| **Settings Configuration**<br>`@[backend_v2/settings.py#L54-L910]` | Magic constants in sliding window loops, hardcoded window sizes, fallback `getattr(settings, ...)` access. | Centralized Pydantic V2 `Settings` fields: `causal_discovery_window_size: int = 4`, `causal_discovery_overlap: int = 2`, `causal_discovery_max_atoms_per_window: int = 25`, `causal_discovery_max_total_atoms: int = 100`, `causal_secondary_fault_dampening: float = 0.25`, `two_pass_atomizer_packet_size: int = 50`. General linker defaults (`linker_window_size: int = 4`, `linker_overlap: int = 2`) kept separate from causal settings. | Speculative per-domain sliding window overrides and dynamic runtime reload factories. | `Settings.model_validate({})` strict type validation in unit tests; `test_settings.py`. |
| **SSOT Enums & Parity**<br>`@[backend_v2/models/enums.py#L111-L115]`<br>`@[backend_v2/models/enums.py#L272-L285]`<br>`@[client_app_v2/lib/core/models/enums.dart#L354-L390]`<br>`@[backend_v2/tests/unit/test_enum_parity.py#L110-L112]` | Untyped string comparisons (`self.type == "llm"`), heuristic string matching, ad-hoc string literals for block types. | `StepType.CAUSAL_DISCOVERY = "causal_discovery"`, `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`, and `CausalDisplayMode(StrEnum)` with values strictly: `EXECUTIVE = "executive"`, `DETAILED = "detailed"`. Explicit ErrorCodes: `CAUSAL_DISCOVERY_EMPTY_DOCUMENT`, `CAUSAL_DISCOVERY_CYCLE_DETECTED`, `CAUSAL_DISCOVERY_DATA_STARVATION`. 1:1 Dart `@JsonEnum` parity. | Granular display mode permutations (isolated anti-fluff toggles, remediations toggles). | `test_enum_parity.py` verifying `TargetBlockType` and `CausalDisplayMode` parity; Dart compile-time enum switch exhaustion. |
| **Pre-Implementation Atomizer Cleanups**<br>`@[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71]`<br>`@[backend_v2/models/dtos/dag_models.py#L18-L57]`<br>`@[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]` | Returning anonymous 3-tuples (`tuple[str, str, list[str]]`) in `_calculate_packets` ("Tuple Hell"), hardcoded magic window sizes (`packet_size = 50`). | Encapsulate chunk packet bounds into typed immutable `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])` in `dag_models.py`. Bind `packet_size` to `get_settings().two_pass_atomizer_packet_size`. | Intermediate packet wrapper classes or custom iterator protocols. | `uv run python scripts/audit_dict_eradication.py` passing AST guardrails; unit tests in `test_two_pass_atomizer.py`. |
| **SlidingWindowLinker Isolation**<br>`@[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]` | Hardcoded `window_size=4, overlap=2` constructor defaults mutating shared caller behavior. | **DO NOT** mutate constructor defaults in `SlidingWindowLinker.__init__`. `CausalDiscoveryEngine` constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`. Existing `TDAEngine` callers retain current behavior without parameter contamination. | Binding constructor defaults to causal-specific settings. | Regression tests for existing `SlidingWindowLinker` callers; unit tests in `test_causal_discovery_engine.py`. |
| **Step Consistency & Strategy Registry**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]` | Raw string literal comparisons (`self.type == "llm"`, `self.type == "logic"`) bypassing `StepType` enum, duck-typing missing criteria block IDs. | Explicit `StepType.LLM` and `StepType.LOGIC` enum comparisons. New `StepType.CAUSAL_DISCOVERY` branch allowing empty `criteria_block_ids` while enforcing `extraction_protocol_block_id` and `cognitive_tier`. `NODE_STRATEGY_REGISTRY` (L63-L66) maps `StepType.CAUSAL_DISCOVERY -> _build_llm_strategy`, verified in `NodeStrategyFactory.create_strategy` (L73). | Separate `CausalStep` domain model subclass or parallel step validation pipeline. | Unit tests asserting `AppException` when `extraction_protocol_block_id` is missing; `backend_audit_loop.py`. |
| **`_resolve_execution_engine` Cleanup**<br>`@[backend_v2/services/orchestrator/dag_executor.py#L160-L187]` | **Pre-existing debt:** `"atom_flattening_hook" in step_def.pre_hooks` heuristic string matching (L184) violating `ban_heuristic_identifier_matching`. | `StepType.CAUSAL_DISCOVERY` guard clause placed as FIRST branch (before L179 block category check). Flag L184 hook heuristic for replacement with typed step ontology resolution. | N/A | Unit test asserting `CausalDiscoveryEngine` returned for `StepType.CAUSAL_DISCOVERY` steps. |
| **LLM Strategy Telemetry & Dispatch**<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]` | Permissive model strategy fallback defaulting to `"prompt"`, ignoring engine ontology for causal discovery steps. | Set `meta_dict["model_strategy"] = "causal"` when `isinstance(self._engine, CausalDiscoveryEngine)`, recording exact telemetry metadata without string guessing. | Dynamic strategy router subclasses or parallel LLM execution strategies. | Unit tests verifying `_step_metadata.model_strategy == "causal"`. |
| **Causal Discovery DTOs**<br>[NEW] @[backend_v2/models/dtos/causal_discovery.py]<br>`@[backend_v2/models/dtos/step_output.py#L57-L71]` | Naked dictionaries (`dict[str, Any]`, `TypedDict`), anonymous state tuples ("Tuple Hell"), optional fallback keys. | Immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `CausalNodeDTO`, `CausalEdgeDTO`, `CausalGraphPayloadDTO`, `CausalRootCauseDiagnosisDTO`, `AntiFluffAuditDTO`, `PrescriptiveRemediationDTO`, `FairScoringBreakdownDTO`, `CausalTdaFusionResultDTO`. `StepPayloadValue` (L30-L54) extended with `CausalGraphPayloadDTO` and `CausalTdaFusionResultDTO`. | Polymorphic node inheritance hierarchies, recursive graph wrapper classes, intermediate DTO converter factories. | `QGR001` (no naked dicts) and `QGR002` (extra="forbid") automated AST guardrail passing in audit loop. |
| **Fusion Chaining Contract**<br>`@[backend_v2/models/domain/step.py#L32-L119]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]` | Heuristic step-order detection, runtime flag branching, unmapped document passing. | Studio-driven parameterization: explicit first-class field `Step.causal_source_step_id: str \| None = None` referencing upstream causal discovery step. DAG executor transforms upstream `CausalGraphPayloadDTO.nodes` to `ExtractedAtom` via `transform_causal_nodes_to_atoms` and feeds `request.shuffled_atoms`. | Nondeterministic engine picking, automatic graph merging without declared contracts. | Integration test in `test_causal_tda_fusion.py`. |
| **OutputProfile & Studio UX**<br>`@[backend_v2/models/domain/output_profile.py#L35-L346]`<br>`@[backend_v2/models/dtos/output_profile.py#L36-L260]`<br>`@[backend_v2/models/dtos/output_profile.py#L263-L475]`<br>`@[backend_v2/models/dtos/output_profile.py#L478-L621]`<br>`@[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123]`<br>`@[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart#L1-L140]`<br>`@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart#L1-L259]`<br>[NEW] `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart]`<br>`@[client_app_v2/lib/l10n/app_en.arb]`<br>`@[client_app_v2/lib/l10n/app_fi.arb]` | Micro-toggles (`show_causal_anti_fluff`, `show_causal_remediations`, `show_causal_fair_scoring`, `causal_max_nodes_rendered`), missing Dart 3 switch branches in `BlockCardRegistry`, missing `.arb` localization keys, partial DTO mutation violating serialization parity. Flutter wiring placed prematurely in Phase 1 before enums exist. | Full-Duplex Serialization Parity: single SSOT field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` added across Domain Model, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`. Exhaustive Dart 3 switch matching in `BlockCardRegistry` (housed in Phase 2 alongside enum definitions). Compile-time `.arb` localization. | Multi-tab studio configuration wizards and custom per-node styling controls. | `flutter_audit_loop.py` build runner verification; compile-time Freezed serialization tests. |
| **Causal Discovery Engine & Execution**<br>[NEW] `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py]`<br>`@[backend_v2/services/orchestrator/engines/__init__.py]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L136-L372]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]` | Subclassing `TDAEngine`, branching inside `TDAEngine` based on missing `shuffled_atoms`, mutating existing step execution states in-place without DTOs, routing through fallback branches in `_resolve_execution_engine`. | Autonomous `CausalDiscoveryEngine(ExecutionEngine)` cleanly implementing `execute(request: EngineExecutionRequest) -> EngineExecutionResult`, re-exported in `__all__`. `NodeExecutor._resolve_execution_engine` routes via `step_def.type == StepType.CAUSAL_DISCOVERY`. StepType.CAUSAL_DISCOVERY check MUST be placed FIRST in `_resolve_execution_engine`, before block category and pre-hook inspection branches. Sequential DAG chaining strictly via immutable DTOs and `causal_source_step_id`. | Dual execution buses, speculative actor frameworks, and persistent graph database storage engines. | Unit tests in `test_causal_discovery_engine.py` asserting Fail-Fast on cycle loops and empty documents; `test_causal_tda_fusion.py`. |
| **SDUI Model, Adapter & Blueprint**<br>`@[backend_v2/models/view/sdui.py#L563-L569, L797-L817]`<br>[NEW] `@[backend_v2/services/sdui/adapters/causal_graph_adapter.py]`<br>`@[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47]`<br>`@[backend_v2/services/blueprint.py#L52-L608]`<br>`@[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]` | Client-side graph semantic calculation, client inferring root causes, generic raw JSON passing, missing `SduiBlockBase` polymorphism. | `SduiCausalGraphBlock(SduiBlockBase)` added to `AnySduiBlock` discriminated union (L797-L817). `AdapterContext` extended with typed `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` (in-memory only, never serialized across boundaries). `CausalGraphAdapter` transforms `causal_result` into `SduiCausalGraphBlock` strictly adhering to `causal_display_mode`. 1:1 Freezed `@Freezed(unionKey: 'block_type')` Dart model. | Dynamic client-side layout calculators, SVG graph vector serialization over HTTP, multi-pass SDUI transformers. | `test_sdui_template_parity.py` and `test_sdui_semantic_parity.py` passing 100%. |
| **1:1 Presentation Parity (Flutter & PDF)**<br>`@[backend_v2/templates/report_template.jinja2#L87-L550]`<br>[NEW] `@[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]`<br>[NEW] `@[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]`<br>`@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L40-L100]` | Sprawling unreadable node graphs in PDF, inconsistent layout between PDF and screen, embedding heavy canvas tools into report print templates. | Identical Unified Causal Action Card in both Flutter and PDF: executive half-page critical causal path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote, prescriptive remediation. Deep interactive exploration decoupled strictly into `CausalInspectorModal`. | Embedded interactive JavaScript canvas in PDF, duplicate styling engines across platforms. | `test_sdui_semantic_parity.py` validating identical token and quote rendering across HTML/PDF and Flutter widgets. |
| **Tabular Export & Flat CSV Symmetry**<br>`@[backend_v2/services/export_service.py#L82-L301]`<br>`@[backend_v2/services/flattener.py#L24-L76]`<br>`@[backend_v2/models/dtos/flat_record.py#L17-L55]` | Multi-row hierarchical CSV headers, ragged nested Excel rows, missing causal columns in flat exports. | Excel sheets `Causal Graph` and `Causal Diagnostics` in `ExportService`. `FlatExecutionRecordDTO` receives typed scalar causal fields (`causal_node_count`, `causal_root_cause_count`, `causal_raw_penalty`, `causal_deduplicated_penalty`). `FlatFileService` outputs strictly 2-line flat CSV (line 1 = header names, line 2 = scalar values). | Pivot table generators, dynamic CSV dialect negotiation, secondary XLSX macro formatting. | Unit tests in `test_export_service.py` asserting exact column headers and row counts. |
| **Regression & Integration Testing**<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py]`<br>[NEW] `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`<br>`@[backend_v2/tests/fixtures/sdui_golden_master.json#L470-L482]`<br>`@[backend_v2/tests/integration/test_sdui_semantic_parity.py#L109-L380]`<br>`@[backend_v2/tests/unit/test_sdui_template_parity.py#L111-L148]` | Happy-path-only tests, mocking persistence with static dummy dicts, unasserted mock calls. | Comprehensive ISTQB tests: equivalence partitioning, boundary value analysis, negative partitions (at least 2 negative tests per feature: empty text, single atom, circular dependency, disconnected subgraph). Integration tests for Phase 1A -> Phase 1B sequential chaining. | Flaky network integration tests, long-running end-to-end browser tests for unit logic. | `uv run python scripts/backend_audit_loop.py` exiting 0 with Ruff, MyPy, and Pytest all green. |

---

## Proposed Changes

### Phase 1: Pre-Implementation Cleanups & Architectural Alignment (Python Backend Only)

#### [MODIFY] @[backend_v2/services/orchestrator/two_pass_atomizer.py#L50-L71] & @[backend_v2/models/dtos/dag_models.py#L18-L57]
- Resolve technical debt: replace the anonymous 3-tuple `list[tuple[str, str, list[str]]]` in `TwoPassAtomizer._calculate_packets` with a strictly typed and immutable Pydantic V2 model `ChunkPacketDTO(start_block: str, end_block: str, block_keys: list[str])`.
- Update all three calling sites to unpack `ChunkPacketDTO` via explicit field access (`packet.start_block`, `packet.end_block`, `packet.block_keys`) instead of positional tuple unpacking:
  1. `execute_phase_0` (line 128)
  2. `execute_phase_1` (line 236)
  3. `execute_phase_1_drafts` (line 413)
- Replace the hardcoded `packet_size = 50` default in `_calculate_packets` by binding directly to centralized settings `get_settings().two_pass_atomizer_packet_size`.

#### [MODIFY] @[backend_v2/services/orchestrator/sliding_window_linker.py#L122-L353]
- Parameter Isolation Mandate: In `CausalDiscoveryEngine`, construct `SlidingWindowLinker` with explicit settings parameters: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`.
- DO NOT modify `SlidingWindowLinker.__init__` default parameters (`window_size = 4, overlap = 2`), preventing parameter contamination of existing `TDAEngine` execution paths.

#### [MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186]
- Update `test_calculate_packets_empty` and add packet unit tests asserting `ChunkPacketDTO` fields (`start_block`, `end_block`, `block_keys`).

#### [MODIFY] @[backend_v2/models/domain/step.py#L32-L119]
- Update `Step.validate_step_consistency`:
  - Correct string literal checks `if self.type == "llm":` and `if self.type == "logic":` to evaluate against typed enums `StepType.LLM` and `StepType.LOGIC` directly.
  - Add explicit validation branch for `StepType.CAUSAL_DISCOVERY`: criteria blocks (`criteria_block_ids`) are not required because arguments are mined dynamically from free-form text.
  - Enforce Fail-Fast validation ensuring `extraction_protocol_block_id` and `cognitive_tier` are non-null.

#### [MODIFY] @[backend_v2/services/orchestrator/strategies/registry.py#L69-L99]
- Register `StepType.CAUSAL_DISCOVERY -> _build_llm_strategy` in `NODE_STRATEGY_REGISTRY` dictionary (L63-L66) and verify `NodeStrategyFactory.create_strategy` (L73) dispatch mapping.

#### [MODIFY] @[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010]
- In `LLMNodeStrategy`, update line 973: when `isinstance(self._engine, CausalDiscoveryEngine)`, record `meta_dict["model_strategy"] = "causal"` in `_step_metadata` instead of defaulting to `"prompt"`.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L160-L187]
- Pre-existing debt cleanup: In `_resolve_execution_engine`, place `StepType.CAUSAL_DISCOVERY` as the FIRST guard clause before the L179 block category check. Flag heuristic string matching at L184 (`"atom_flattening_hook" in step_def.pre_hooks`) for replacement with typed step ontology resolution.
- In `NodeExecutor.execute` (line 295), ensure `engine = self._resolve_execution_engine(step_def, loaded_prompt_blocks)` is called when `step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY)`.

---

### Phase 2: Configuration, DTOs, Studio Foundation & Parity

#### [MODIFY] @[backend_v2/settings.py#L54-L910]
- Add centralized settings for sliding window boundaries, dynamic extraction limits, and packet sizing:
  - `causal_discovery_window_size: int = 4`
  - `causal_discovery_overlap: int = 2`
  - `causal_discovery_max_atoms_per_window: int = 25`
  - `causal_discovery_max_total_atoms: int = 100`
  - `causal_secondary_fault_dampening: float = 0.25`
  - `two_pass_atomizer_packet_size: int = 50`
  - General linker settings preserved independently: `linker_window_size: int = 4`, `linker_overlap: int = 2`.

#### [MODIFY] @[backend_v2/models/enums.py#L111-L115] & @[backend_v2/models/enums.py#L272-L285] & @[client_app_v2/lib/core/models/enums.dart#L354-L390] & @[backend_v2/tests/unit/test_enum_parity.py#L110-L112]
- Add `StepType.CAUSAL_DISCOVERY = "causal_discovery"`.
- Add `TargetBlockType.CAUSAL_GRAPH_BLOCK = "causal_graph_block"`.
- Add `CausalDisplayMode(StrEnum)` and `LaxCausalDisplayMode` with values defined exhaustively as:
  - `EXECUTIVE = "executive"`
  - `DETAILED = "detailed"`
- Add explicit causal engine error codes in `ErrorCodes`:
  - `CAUSAL_DISCOVERY_EMPTY_DOCUMENT = "CAUSAL_DISCOVERY_EMPTY_DOCUMENT"`
  - `CAUSAL_DISCOVERY_CYCLE_DETECTED = "CAUSAL_DISCOVERY_CYCLE_DETECTED"`
  - `CAUSAL_DISCOVERY_DATA_STARVATION = "CAUSAL_DISCOVERY_DATA_STARVATION"`
- Add verification in `test_enum_parity.py` asserting 1:1 parity for `CausalDisplayMode` and `TargetBlockType` between Python and Dart.

#### [MODIFY] @[backend_v2/models/domain/step.py#L32-L119]
- Declare Studio-driven fusion chaining field: `causal_source_step_id: str | None = None` on `Step` (Opaque Stripe ID referencing the upstream causal discovery step). When set on a downstream step (specifically a `StepType.LLM` TDA step), instructs the DAG executor to inject upstream causal graph nodes into `shuffled_atoms`.

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
- Extend `StepPayloadValue` type union (lines 30-54) to include `CausalGraphPayloadDTO | CausalTdaFusionResultDTO`.
- Extend `StepOutputDTO.data_type` literal to include `"causal"` to guarantee 100% typed deserialization of causal discovery step execution outputs.

#### [MODIFY] @[backend_v2/models/domain/output_profile.py#L35-L346] & @[backend_v2/models/dtos/output_profile.py#L36-L260] & @[backend_v2/models/dtos/output_profile.py#L263-L475] & @[backend_v2/models/dtos/output_profile.py#L478-L621]
- Enforce Full-Duplex Serialization Parity by adding control field `causal_display_mode: LaxCausalDisplayMode = CausalDisplayMode.EXECUTIVE` across Domain Model, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`.

#### [MODIFY] @[client_app_v2/lib/features/studio/models/output_profile.dart#L30-L123] & @[client_app_v2/lib/features/studio/views/profile_editor_view.dart#L1-L693]
- Update Freezed models in `client_app_v2` to match Python fields 1:1 (`causal_display_mode`).
- Add a single selector in Quorum Studio `ProfileEditorView` (`CausalDisplayMode`: Executive / Detailed) and block positioning in the `target_block_order` list with zero micro-toggle clutter.

#### [MODIFY] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart#L28-L180]
- Extend Dart 3 switch expressions to handle `TargetBlockType.causalGraphBlock` exhaustively (now that enums exist):
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
  - The engine is completely standalone with zero `TDAEngine` dependencies.
  - Constructs `SlidingWindowLinker` with explicit settings: `SlidingWindowLinker(window_size=get_settings().causal_discovery_window_size, overlap=get_settings().causal_discovery_overlap)`.
  - `execute(request: EngineExecutionRequest) -> EngineExecutionResult`:
    1. **Pre-flight Ingress & Hydration**: Verifies document input is non-empty; if empty or containing 0 argument premises, raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)`. Initializes `AliasEngine` and indexes paragraphs (`[B0]...[Bn]`).
    2. **Four-Layer Clean Stack Prompt Compilation**: Enforces static ontology instructions in system prompt prefix for 100% context caching, dynamic theory grounding in `<theory_context>` compiled from configured PromptBlocks (ensuring matrices including Toulmin, Walton, or custom frameworks remain 100% dynamic, pluggable, and omittable), step-level extraction protocol, and dynamic text payload with atom aliasing (`a0`, `a1`) at the tail.
    3. **Phase 0 (Global Ontology)**: Executes `TwoPassAtomizer.execute_phase_0` to construct `GlobalOntologyMap`.
    4. **Phase 1 (Chunked Claim Extraction)**: Executes `TwoPassAtomizer.execute_phase_1` to generate independent `ExtractedAtom` instances with exact physical quote anchoring via `str.find` lexical validation against indexed paragraphs.
    5. **Sliding Window Linking**: Executes `SlidingWindowLinker.link_graph` to connect atoms into a directed `LinkedAtomGraph`.
    6. **Topological Wave Execution**: Passes the graph through `EnrichedDagExecutor` / `TopologicalEvaluator` with wave evaluation, short-circuit cascades, and fault attribution. Reuses thread-isolated cycle detection: if a circular dependency is detected, sets `cycle_detected=True` and marks cyclic nodes with `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED` without event loop deadlock.
    7. **Standalone Result Projection**: Projects standalone causal graph states returning an `EngineExecutionResult`.

#### [MODIFY] @[backend_v2/services/orchestrator/engines/__init__.py]
- Re-export `CausalDiscoveryEngine` in `backend_v2/services/orchestrator/engines/__init__.py` and add it to `__all__` adhering strictly to `explicit_reexport_mandate`.

#### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L136-L372] & @[backend_v2/services/orchestrator/dag_executor.py#L375-L1347]
- Extend `_resolve_execution_engine` routing to support `step_def.type == StepType.CAUSAL_DISCOVERY`. The `StepType.CAUSAL_DISCOVERY` guard clause MUST be inserted as the very FIRST branch in `_resolve_execution_engine`, before the `PromptBlockCategory.MATRIX` block category check and pre-hook inspection branches, preventing ambiguous routing.
- **Fusion Chaining Execution (Phase 1A -> Phase 1B)**:
  - When a downstream step defines `step_def.causal_source_step_id is not None`, the DAG executor resolves the completed upstream step's output (`CausalGraphPayloadDTO`).
  - Calls typed transformer `transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -> list[ExtractedAtom]` mapping node IDs, claims, and paragraph references into `ExtractedAtom` models.
  - Injects the resulting atoms directly into `request.shuffled_atoms` for `TDAEngine`. If the upstream step produced 0 valid nodes or failed, Fail-Fast triggers with `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)`.
- Execute five stakeholder benefit pipelines in the orchestrator: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI data projection, and Fair Scoring Deduplication.

---

### Phase 4: Presentation Parity, Studio Dispatch & Export Symmetry

#### [MODIFY] @[backend_v2/models/view/sdui.py#L563-L569, L797-L817] & @[client_app_v2/lib/shared/models/sdui_block_dto.dart#L10-L171]
- Define `SduiCausalGraphBlock(SduiBlockBase)` (at L563-L569) and append it to the polymorphic discriminated union `AnySduiBlock` (at L797-L817):
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
- Add typed field `causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None` to `AdapterContext` to provide direct, fail-fast DTO access for `CausalGraphAdapter` without ad-hoc dictionary searches over `execution.step_states`. This field functions strictly as an in-memory execution context envelope and is NEVER serialized across network or storage boundaries.

#### [MODIFY] @[backend_v2/templates/report_template.jinja2#L87-L550]
- Implement Jinja2 macro `render_causal_graph_block`:
  - In `EXECUTIVE` mode: renders a compact Unified Causal Action Card: linear critical root cause path (`[Root Cause]` -> `[Cascading Fault]` -> `[Score Loss]`), lexical quote card with `paragraph_ref`, prescriptive remediation card, and intact claims count chip (`"X other claims verified logically sound"`), occupying at most half an A4 page in PDF.
  - In `DETAILED` mode: renders the complete argument graph and comprehensive evidentiary table.
  - Adheres strictly to `profile.causal_display_mode` with zero micro-toggles.

#### [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart]
- Implement Flutter component rendering the identical visual Unified Causal Action Card matching the Jinja2 macro:
  - Linear critical root cause path matching identical color schemes and layout tokens.
  - Identical lexical fault quote and prescriptive remediation card.
  - Includes a subtle action button `[ 🔍 Open Interactive Inspector ]` for unconstrained full-graph exploration.
  - Wrapped strictly with `AppErrorBoundary` to isolate widget-level rendering errors from the parent viewport.

#### [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart]
- Dedicated pro-tool inspector modal for interactive exploration (pan, zoom, side-by-side source text citation highlighting, remediation simulation), decoupled strictly from the primary report presentation and wrapped with `AppErrorBoundary`.

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
    <action>Refactor @[backend_v2/services/orchestrator/two_pass_atomizer.py] _calculate_packets to return list[ChunkPacketDTO] and remove magic numbers, updating execute_phase_0, execute_phase_1, and execute_phase_1_drafts.</action>
    <action>Update @[backend_v2/tests/unit/services/orchestrator/test_two_pass_atomizer.py#L180-L186] to assert on ChunkPacketDTO fields.</action>
    <action>Enforce parameter isolation in @[backend_v2/services/orchestrator/sliding_window_linker.py]: preserve constructor defaults unchanged; construct SlidingWindowLinker in CausalDiscoveryEngine with explicit causal_discovery_* settings.</action>
    <action>Update @[backend_v2/models/domain/step.py] validate_step_consistency to evaluate StepType.LLM and StepType.LOGIC enums directly, and allow StepType.CAUSAL_DISCOVERY without criteria blocks while enforcing extraction_protocol_block_id.</action>
    <action>Update @[backend_v2/services/orchestrator/strategies/registry.py#L69-L99] NODE_STRATEGY_REGISTRY to map StepType.CAUSAL_DISCOVERY to _build_llm_strategy, verified in NodeStrategyFactory.create_strategy.</action>
    <action>Update @[backend_v2/services/orchestrator/strategies/llm.py#L82-L1010] to record model_strategy="causal" in _step_metadata when self._engine is CausalDiscoveryEngine.</action>
    <action>Clean up @[backend_v2/services/orchestrator/dag_executor.py#L160-L187] _resolve_execution_engine to insert StepType.CAUSAL_DISCOVERY as FIRST guard clause before category checks.</action>
    <action>Update @[backend_v2/services/orchestrator/dag_executor.py#L136-L372] NodeExecutor.execute (line 295) to resolve execution engine when step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY).</action>
    <constraint invariant="universal_fail_fast">Enforce exhaustive switch expressions and fail-fast validation across domain models.</constraint>
  </step>

  <step id="2" name="SETTINGS_AND_DTO_FOUNDATION">
    <action>Add causal discovery configuration parameters and two_pass_atomizer_packet_size to @[backend_v2/settings.py] including causal_secondary_fault_dampening, preserving general linker settings.</action>
    <action>Add StepType.CAUSAL_DISCOVERY, TargetBlockType.CAUSAL_GRAPH_BLOCK, and CausalDisplayMode enum to @[backend_v2/models/enums.py] and @[client_app_v2/lib/core/models/enums.dart], and define explicit CAUSAL_DISCOVERY_* ErrorCodes.</action>
    <action>Declare causal_source_step_id field on Step in @[backend_v2/models/domain/step.py] to enable typed Studio-driven fusion chaining.</action>
    <action>Create strictly typed immutable [NEW] @[backend_v2/models/dtos/causal_discovery.py] (CausalNodeDTO, CausalEdgeDTO, CausalGraphPayloadDTO, CausalRootCauseDiagnosisDTO, AntiFluffAuditDTO, PrescriptiveRemediationDTO, FairScoringBreakdownDTO, and CausalTdaFusionResultDTO).</action>
    <action>Extend StepPayloadValue (lines 30-54) in @[backend_v2/models/dtos/step_output.py#L57-L71] to include CausalGraphPayloadDTO and CausalTdaFusionResultDTO with data_type="causal".</action>
    <action>Add causal_display_mode field to @[backend_v2/models/domain/output_profile.py] and all serialization DTOs in @[backend_v2/models/dtos/output_profile.py].</action>
    <action>Update Freezed models in @[client_app_v2/lib/features/studio/models/output_profile.dart] and selector in @[client_app_v2/lib/features/studio/views/profile_editor_view.dart].</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/block_card_registry.dart] to exhaustively handle TargetBlockType.causalGraphBlock in all Dart 3 switch expressions.</action>
    <action>Update @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart] and @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart] to integrate Causal Graph block ordering and section settings.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/causal_block_card.dart] rendering causal display mode selector.</action>
    <action>Add Axis 1 localization keys for Causal Graph block title, subtitle, and display modes to @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb].</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce ConfigDict(strict=True, extra='forbid', frozen=True) on all DTOs with zero naked dicts.</constraint>
  </step>

  <step id="3" name="STANDALONE_ENGINE_IMPLEMENTATION">
    <action>Implement [NEW] @[backend_v2/services/orchestrator/engines/causal_discovery_engine.py] as a standalone engine without any TDAEngine dependencies.</action>
    <action>Update @[backend_v2/services/orchestrator/engines/__init__.py] to re-export CausalDiscoveryEngine in __all__.</action>
    <action>Enforce Four-Layer Clean Stack prompt compilation: static ontology instruction prefix for 100% caching efficiency, dynamic theory context supporting pluggable argumentation matrices (Toulmin, Walton, or custom matrices loaded dynamically from PromptBlocks), step extraction protocol, and dynamic user payload with atom aliasing (a0, a1) at the tail.</action>
    <action>Enforce exact physical quote validation via str.find against indexed paragraph blocks, prohibiting fuzzy matching.</action>
    <action>Enforce Fail-Fast on empty input text: raise AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT) when 0 argument premises exist.</action>
    <action>Wire TwoPassAtomizer and SlidingWindowLinker (instantiated with explicit causal_discovery_* settings) sequentially with progress reporting callbacks.</action>
    <action>Pass generated LinkedAtomGraph to TopologicalEvaluator for wave-based topological evaluation, blame cascading, and thread-isolated cycle detection (marking cyclic nodes SYSTEM_ERROR with CYCLIC_DEPENDENCY_DETECTED).</action>
    <constraint invariant="single_pipeline_invariant_mandate">Keep CausalDiscoveryEngine completely separate from TDAEngine with zero shared fallback branches.</constraint>
    <constraint invariant="anti_god_file_dumping">Isolate engine logic strictly in its own file under 200 lines.</constraint>
  </step>

  <step id="4" name="DAG_ROUTER_AND_OPTIONAL_FUSION">
    <action>Mount CausalDiscoveryEngine in @[backend_v2/services/orchestrator/dag_executor.py] NodeExecutor and DAGExecutor under StepType.CAUSAL_DISCOVERY as the FIRST routing branch in _resolve_execution_engine before block category checks.</action>
    <action>Wire sequential DAG chaining: when step_def.causal_source_step_id is set, extract upstream CausalGraphPayloadDTO and transform nodes via transform_causal_nodes_to_atoms into ExtractedAtom instances feeding downstream TDAEngine shuffled_atoms.</action>
    <action>Enforce data starvation Fail-Fast: if upstream step produced 0 valid nodes or failed, raise AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION).</action>
    <action>Implement five stakeholder benefit pipelines: Root Cause Attribution, Anti-Fluff Shield, Prescriptive Remediation, Visual XAI data projection, and Fair Scoring Deduplication.</action>
    <constraint invariant="engine_override_ban">Ensure routing resolves dynamically and deterministically from step blueprint StepType without heuristic string parsing.</constraint>
  </step>

  <step id="5" name="SDUI_MODEL_AND_BLUEPRINT_DISPATCH">
    <action>Add SduiCausalGraphBlock to @[backend_v2/models/view/sdui.py#L563-L569, L797-L817], append to AnySduiBlock union (lines 797-817), and add Dart Freezed DTOs in @[client_app_v2/lib/shared/models/sdui_block_dto.dart].</action>
    <action>Add causal_result to AdapterContext in @[backend_v2/services/sdui/adapters/base_adapter.py#L18-L47] as strictly an in-memory execution context envelope, and hydrate it in @[backend_v2/services/blueprint.py#L52-L608].</action>
    <action>Implement [NEW] @[backend_v2/services/sdui/adapters/causal_graph_adapter.py] respecting OutputProfile causal display settings.</action>
    <action>Update @[backend_v2/services/blueprint.py] to assemble SduiCausalGraphBlock dynamically based on OutputProfile target_block_order.</action>
    <constraint invariant="sdui_contract_fracture_prevention">Ensure 100% semantic parity between Python SDUI model and Flutter Freezed representation.</constraint>
  </step>

  <step id="6" name="PRESENTATION_PARITY_AND_EXPORT_SYMMETRY">
    <action>Implement Jinja2 macro in @[backend_v2/templates/report_template.jinja2] rendering the streamlined Unified Causal Action Card matching CausalDisplayMode (occupying at most half an A4 page in PDF).</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/execution/views/widgets/sdui_causal_graph_widget.dart] in Flutter rendering the identical visual layout matching Jinja2 PDF output, wrapped with AppErrorBoundary.</action>
    <action>Implement [NEW] @[client_app_v2/lib/features/execution/presentation/causal_inspector_modal.dart] in Flutter as an explicitly decoupled supplementary pro-tool modal wrapped with AppErrorBoundary.</action>
    <action>Register SduiCausalGraphBlock handler in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart].</action>
    <action>Extend @[backend_v2/services/export_service.py] to generate Causal Graph and Causal Diagnostics sheets in Excel exports.</action>
    <action>Extend @[backend_v2/services/flattener.py] to project causal metrics into @[backend_v2/models/dtos/flat_record.py].</action>
    <constraint invariant="sdui_contract_fracture_prevention">Run test_sdui_semantic_parity.py and test_sdui_template_parity.py to mathematically verify 1:1 parity.</constraint>
  </step>

  <step id="7" name="UNIT_TESTING_AND_VERIFICATION">
    <action>Create comprehensive ISTQB unit tests in [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_causal_discovery_engine.py] asserting CAUSAL_DISCOVERY_EMPTY_DOCUMENT on empty inputs, and CYCLIC_DEPENDENCY_DETECTED on circular inputs.</action>
    <action>Create integration test [NEW] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py] asserting CAUSAL_DISCOVERY_DATA_STARVATION on empty upstream graph, and verifying the five stakeholder benefits.</action>
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

### Falsification & Red-Teaming Matrix (Axis 5)

| Invariant / Potential Failure Point | Verification Mechanism | Expected Fail-Fast Behavior |
|:---|:---|:---|
| **Empty or Starved Document:** Document text has 0 argument premises or empty string. | `test_causal_discovery_engine.py` | Raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT)`. |
| **Circular Argument Deadlock:** Arguments form a directed cycle (A -> B -> A). | `test_causal_discovery_engine.py` | `TopologicalEvaluator` thread-isolated cycle detection catches cycle, sets `cycle_detected=True`, marks nodes `ExecutionStatus.SYSTEM_ERROR` with reason `CYCLIC_DEPENDENCY_DETECTED`. |
| **Downstream Fusion Starvation:** Upstream discovery produces 0 nodes, but downstream TDA step expects atoms. | `test_causal_tda_fusion.py` | DAG executor raises `AppException(ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION)` instead of silently evaluating empty text. |
| **KI Contract Parity:** Decoupling rules in `ki_execution_engine_protocol` and `ki_tripartite_pipeline_architecture`. | Architectural Review | Engine implements `ExecutionEngine(Protocol)` with zero cross-engine state leakage or shared mutable memory. |
| **Persistence Verification:** Repository operations assert real state mutation. | Unit & Integration Tests | Test suite tests real DTO state transitions and `ConfigDict(strict=True, extra="forbid")` validation roundtrips. |
| **SDUI Cross-Platform Parity:** Token, font, and quote divergence between PDF and Flutter. | `test_sdui_semantic_parity.py` | Validates identical DOM/Widget tokens; Jinja2 macro and Flutter widget share design tokens. |
| **Context Amnesia Prevention:** Refactoring across multiple directories exceeding session budget. | Implementation Governance | Standalone plan is divided into 7 discrete, atomic steps with explicit file lists and verification gates. |
| **Single Pipeline Invariant:** Coexistence of legacy permissive and new strict modes. | Architectural Review | Zero fallback branches; all execution flows deterministically via `StepType.CAUSAL_DISCOVERY`. |
| **Roadmap Isolation:** Premature activation into production workflows. | Documentation Gate | Explicit caution box locks plan as `DISTANT FUTURE ROADMAP ONLY`, preventing accidental production seeder activation. |
