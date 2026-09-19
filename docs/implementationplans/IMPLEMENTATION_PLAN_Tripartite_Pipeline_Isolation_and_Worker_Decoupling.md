<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

> **STATUS: AUDITED & ENRICHED — PASS 11 (PASS 10 Hallucination Reversal & Physical Codebase Verification 2026-09-19 — Physical Line Counts Restored: v2_core.py 1,920L, worker.py 2,037L, execution.py 1,511L, blueprint.py 589L; 8 Falsely Pre-Resolved Debt Items Restored to Active Scope)**

> [!IMPORTANT]
> **MANDATORY PRE-READ CONTRACT (FLUTTER DESKTOP PRO TOOL UX & DUAL-AXIS LOCALIZATION)**:
> Before implementing, reviewing, or modifying ANY Flutter window, modal, dialog, view, card, or widget (`CreateReportDialog`, `ExecutionReportsView`, `ReportArtifactCard`, `NewExecutionView`, `ExecutionView`), or developing document export/synthesis services:
> 1. **`@[ki_desktop_pro_tool_studio_ux.md]` MUST be physically loaded and read into active context first**: All 16 architectural pillars of Desktop Pro Tool UX MUST be implemented 100% in full without compromise, shortcuts, or omissions.
> 2. **`@[ki_dual_axis_localization_architecture.md]` MUST be physically loaded and read into active context first**: The strict boundary between Axis 1 (Flutter compile-time `.arb` chrome) and Axis 2 (Backend dynamic `I18nText` domain strings) MUST be enforced 100%. Backend opening of `.arb` files (`open("client_app_v2/lib/l10n/app_{locale}.arb")`) is permanently eradicated. All new Flutter UI keys MUST have 1:1 bilingual parity across both `app_fi.arb` and `app_en.arb`, and Phase 2 synthesis MUST enforce Split-Cognitive Translation (`STATIC_LINGUISTIC_PROTOCOL` and `build_linguistic_parameters`).

# IMPLEMENTATION PLAN: Tripartite Pipeline Isolation, Worker Decoupling & Report Artifact CRUD

## Overview & Objective

This implementation plan establishes full structural compliance with the Tripartite Pipeline Architecture as codified in @[ki_tripartite_pipeline_architecture.md] and the Desktop-Class Pro Tool UX as codified in @[ki_desktop_pro_tool_studio_ux.md]. It decouples Phase 1 (Execution & Evaluation DAG), Phase 2 (Synthesis & Reporting), and Phase 3 (Dumb Painter SDUI/PDF Rendering), eliminating inter-phase chatter, synthetic execution step injections, database mutation from presentation transformers, and failure cascade pollution.

Furthermore, this plan formalizes the **Materialized Report Artifact Architecture**: all rendered presentation outputs (`report.pdf`, `report.sdui.json`, `report.xlsx`, tabular row data) are elevated into first-class, immutable, and independently versioned `ReportArtifact` records with full-lifecycle CRUD operations across the Database, REST API, Background Worker, and Flutter Desktop Studio UI.

### Core Architectural Mandates Addressed
1. **Phase 1 Execution Lifecycle Sovereignty**: DAG execution status transitions directly to `ExecutionStatus.PASSED` immediately upon completion of analytical reasoning and scoring. The artificial execution step (`sys_render_{profile_id}`) is eradicated from execution state history.
2. **Failure Isolation (Zero Reverse Pollution)**: PDF rendering and synthesis failures in Phase 2/3 must NEVER mutate `ExecutionRecord.status` to `ExecutionStatus.FAILED`. A presentation layout or file-system error remains quarantined in the rendering response or cache.
3. **Ingress Decoupling**: Executions must be executable without specifying a presentation profile. `output_profile_id` becomes strictly optional at execution ingress.
4. **Read-Only Presentation Transformers**: `BlueprintTransformer.build_report_dto` becomes 100% read-only and side-effect-free, eradicating database mutation calls (`update_execution`) during presentation rendering.
5. **Ghost Field Purge & Studio Parameterization Governance**: Completely purges the dead-weight ghost field `allowed_exports` from `Workflow` (Python `v2_core.py`), Studio services (`workflow_service.py#L319`), test factories (`model_factories.py#L45`), master seed vault (`seed_data.json` across 6 workflows: `wf_9d68c573802341db`, `wf_01a1d71000000001`, `wf_02a1d71000000002`, `wf_03a1d71000000003`, `wf_04a1d71000000004`, `wf_05a1d71000000005`), and Flutter (`workflow.dart`). Forensic audit revealed that `allowed_exports` had 0 usages in background workers or Flutter UI views/widgets, but existed as legacy schema remnants in draft creation and seed data that would crash `extra="forbid"` Pydantic V2 validation if not purged concurrently. In strict compliance with the `ban_heuristic_identifier_matching` mandate (`AGENTS.md`) and `studio_driven_parameterization_mandate` (`05_llm_architecture.md`), explicit prompt block selectors (`OutputProfile.variance_target_block` and `user_role_target_block`) are strictly preserved and enforced as typed Studio UI parameters, banning any heuristic backend guessing or keyword-based matrix discovery.
6. **CQRS Export Extraction**: Extracts document export and Excel compilation from `ExecutionService` into a dedicated `ExportService`, eliminating backend reads of Flutter `.arb` files.
7. **Materialized Report Artifacts & Full-Lifecycle Output CRUD**: Elevates generated outputs into independent, first-class `ReportArtifact` domain models. A single execution run (Phase 1) can spawn multiple distinct report artifacts (Phase 2 & 3) tailored to different audiences (specifically: Board, Executive Coach, Forensic Auditor) and languages (FI, EN). Pre-compiled SDUI JSON, PDF, and Excel files are stored as immutable artifacts served with $O(1)$ latency without re-evaluating the DAG or reparsing atomic traces. Complete CRUD (Create, Read, Update/Regenerate, Delete, List) is supported across Backend Repository, REST API, and Flutter Desktop Studio UI adhering strictly to @[ki_desktop_pro_tool_studio_ux.md].
8. **REST-API-Only Pipeline Boundary (Absolute Decoupling Mandate)**: Phase 1 (DAG execution) and Phase 2/3 (report generation) MUST NEVER be connected via in-process memory calls, direct worker queue-chaining, or backdoor worker-to-worker auto-triggers. The REST API (`POST /api/v2/executions/{execution_id}/reports`) is the SOLE legitimate gateway through which report compilation can be initiated across the entire system. Both the Flutter UI (reacting to `status == PASSED` when `[x] Aja tulosteeksi saakka` is checked) and external B2B clients connect the runs strictly across this HTTP REST boundary. Static import firewalls and automated AST-level tests mathematically enforce that the execution engine contains zero imports, references, or job-enqueues targeting reporting services or queues.
9. **Database Bounded Context & Schema Segregation Invariant**: The database layer enforces strict microservice-spirit schema segregation between Phase 1 and Phase 2/3. Phase 1 computational execution records reside exclusively in the `executions` collection (`ExecutionRecord`), strictly append-only and immutable upon reaching `status == PASSED`. Phase 2/3 presentation outputs reside exclusively in the dedicated `report_artifacts` collection (`ReportArtifact`), connected only via a loose foreign key (`execution_id: str`). Database access is quarantined into dedicated repository implementations: `ExecutionRepositoryImpl` operates strictly against `executions`, while `ReportArtifactRepositoryImpl` operates strictly against `report_artifacts`. Large physical files (PDF, SDUI JSON, Excel, CSV) are offloaded to Cloud-Native Object Storage (`artifacts/reports/{id}/`), leaving only lightweight metadata in the database.
10. **Four-Tier Strict Pydantic V2 Model Invariant**: All domain models and DTOs across the pipeline are strictly partitioned into four non-overlapping tiers: 1) Analytical Execution Models (`ExecutionRecord`, `AtomResultDTO`), 2) Materialized Artifact Lifecycle DTOs (`ReportArtifact`, `ReportArtifactCreateDTO`), 3) Dumb Painter Presentation DTOs (`ReportDataDTO`, `ReportRowItemDTO`), and 4) Studio Profile Definitions (`OutputProfile`). Every single model without exception enforces `ConfigDict(strict=True, extra="forbid")`, banning loose dictionaries (`no_naked_dicts_in_state`), legacy ghost fields, and accidental cross-tier field bleed. Full-Duplex Serialization Parity guarantees 1:1 typed parity with Dart Freezed models in Flutter.
11. **Module-Specific Responsibility Allocation (SRP Invariant)**: Each subsystem is strictly quarantined according to the Single Responsibility Principle: ExecutionService is solely responsible for calculation lifecycle, ReportService solely for report artifacts, ExportService solely for format conversions, BlueprintTransformer solely for read-only SDUI projection, background workers for isolated Arq execution, and API routers for their specific bounded contexts.
12. **God Code Decomposition & Subpackage Isolation (/tier3-god-code-decomposition)**: Monolithic files exceeding 500 lines (`backend_v2/worker.py` with 1,823 lines and `backend_v2/services/execution.py` with 1,307 lines) are proactively decomposed into clean subdirectories (`backend_v2/workers/` and `backend_v2/services/`). The Strangler Fig Proxy Pattern with PEP 484 explicit re-exports (`__all__` and redundant aliases) provides a structured migration facade and satisfies `mypy --strict` during phased consumer migration.
13. **Preservation of Sovereign Model Stack Architecture, Cognitive Tiers & Google Providers Decoupling**: The codebase has implemented three foundational architectural enhancements that post-date this plan's initial conception:
    - *Google Providers Decoupling*: Sovereign `VERTEX_AI = "vertex_ai"` and `AI_STUDIO = "ai_studio"`, complete eradication of the merged `"google"` pseudo-provider, typed relations (`provider_type: LLMProvider`), and live model discovery via Google Model Garden hub and AI Studio Client.
    - *Option A Sovereign Model Stack Architecture*: Workflows bind to a dedicated 4-tier model stack via `Workflow.model_registry_id` (100% dynamic DB resolution, zero code-level default registry IDs). `SystemConfigModelRegistry` houses `name: str`, `default_provider: LaxLLMProvider`, and flat `tier_definitions: dict[CognitiveTier, ModelProfile]`.
    - *Provider-Agnostic Cognitive Tiers*: Workflow steps author abstract cognitive tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`) via `Step.cognitive_tier: CognitiveTier`. `LLMClient.from_tier()` resolves clients in $O(1)$ time, and `ExecutionMetadata` / `ExecutionCreate` carry `provider_override: LLMProvider | None` and `model_registry_id: str | None`.
    The Tripartite decomposition MUST strictly preserve, respect, and integrate these architectures across all decomposed domain modules (`domain/system_config.py`, `domain/step.py`, `domain/workflow.py`, `domain/execution.py`), background workers (`workers/execution_worker.py`, `workers/report_worker.py`), and execution services (`services/execution/ingress_service.py`, `services/report_service.py`). Report workers and `ReportService` invoke `LLMClient.from_tier(CognitiveTier.BALANCED, ...)` using the execution's bound `model_registry_id` and `provider_override`, with zero regression to legacy string strategies or merged pseudo-providers.
14. **Physical Codebase Baseline & True AST Line Verification (2026-09-19 PASS 11 Verification)**: Rigorous MCP verification confirms that the previous PASS 10 session hallucinated file reductions: the physical codebase on branch `main` stands at `backend_v2/models/v2_core.py` (**1,920 lines**), `backend_v2/worker.py` (**2,037 lines**), `backend_v2/services/execution.py` (**1,511 lines**), `backend_v2/services/blueprint.py` (**589 lines**), and `backend_v2/services/orchestrator/dag_executor.py` (**1,245 lines**). The plan's structural line ranges (e.g. `start_execution` at #L401-L644, `create_execution_record` at #L100-L156, `execute_workflow_job` at #L139-L566, `sys_render` at #L487-L499) match the physical codebase precisely. Before every extraction step, the executing agent must verify exact node ranges with `uv run python scripts/_ast_boundary_utils.py <target_file>`.
15. **Context Amnesia Phasing & Handover Governance**: To prevent context amnesia across 60+ touched files, execution of this plan MUST be structured into three sequential phases separated by explicit `/tier5-session-handover` checkpoints:
    - *Phase A: God Code Decomposition & Ghost Field Purge (Steps 1–2)* -> Handover A->B
    - *Phase B: Worker & Service Decoupling (Steps 3–7)* -> Handover B->C
    - *Phase C: REST API, Flutter UI & Documentation (Steps 8–12)*
    All architectural features (specifically: B2B Public API, per-report model overrides, 4-format compilation, and extended telemetry) are 100% retained and executed as planned.
16. **Dual-Axis Localization & Export Boundary Sovereignty (@[ki_dual_axis_localization_architecture.md])**:
    The pipeline strictly enforces the Dual-Axis Localization Architecture:
    - *Axis 1 (Structural Localization - Flutter Chrome)*: ALL UI chrome, modal titles, field labels, tooltips, validation messages, and alert dialogs resolve exclusively from compile-time `.arb` files via `AppLocalizations.of(context)!` with 1:1 Finnish/English parity. Zero hardcoded UI strings in Dart widgets.
    - *Axis 2 (Semantic Domain Localization - Backend I18nText)*: Dynamic labels, workflow titles, and rubric descriptions resolve strictly from database `I18nText` models, NEVER from client `.arb` files.
    - *Export Boundary Firewall*: Backend services (`ExportService`) are strictly forbidden from reading client `.arb` files (`open("client_app_v2/lib/l10n/app_{locale}.arb")` in `execution.py#L850-L855` is permanently eradicated). Column headers and export labels are resolved via backend `I18nText` or static Python translation tables within `ExportService`.
    - *Split-Cognitive Translation in Phase 2 Synthesis*: When synthesizing reports (`ReportService`), LLM execution adheres to `STATIC_LINGUISTIC_PROTOCOL` and `build_linguistic_parameters(target_locale)` from `linguistic_directives.py`: internal `<reasoning_trace>` generated in English, user-facing text generated in the target locale (FI/EN), and verbatim evidence quotes preserved in their original source language.
    - *Strict Enum Adapter*: Python Enums (specifically `ReportStatus`) implement `@property def l10n_key(self) -> str:` mapping uppercase enums to Flutter camelCase ARB keys (`reportStatusPending`, `reportStatusGenerating`, `reportStatusReady`, `reportStatusFailed`), banning runtime string manipulation.

---

## Architectural Synthesis: The Tripartite Model & Delivery Engine

### 1. Three-Tier Separation Model
The end-to-end lifecycle is decoupled into three sovereign tiers:
1. **Tier 1: Authoring & Definitions (Studio OutputProfile SSOT)**:
   - Expert consultants define reusable "report recipes" in Quorum Studio: audience designation, dynamic tone instructions (`tone_instruction`), per-section synthesis directives (`executive_summary_directive`, `variance_synthesis_directive`), and polymorphic SDUI component sequences (`target_block_order`).
   - Profiles are workflow-agnostic lenses that contain zero execution plumbing or DAG step bindings.
2. **Tier 2: Synthesis Engine (Phase 2 Worker)**:
   - The worker ingests Phase 1's finalized, immutable evaluation state (`ExecutionRecord.execution_trace`) alongside the selected `OutputProfile` and optional execution preface.
   - LLM generation produces structured, section-mapped markdown syntheses strictly downstream of analytical scoring.
3. **Tier 3: Serving & Artifact Presentation (Phase 3 Dumb Painter & Serving Layer)**:
   - The `ReportService` bundles rendered SDUI component trees (`report.sdui.json`), paginated PDF files (`report.pdf`), multi-tab workbooks (`report.xlsx`), and flattened row records into a materialized `ReportArtifact`.
   - Serving endpoints query pre-compiled files directly with $O(1)$ latency, requiring zero re-evaluation of LLM prompts or DAG nodes.

### 2. Profile vs. Format Governance (Simplicity Invariant)
To prevent $N \times M$ matrix explosion, the architecture maintains a strict distinction between Profiles and Formats:
- **Profile = Perspective / Audience (Semantic Content)**: Represents *what* is communicated and to *whom* (specifically: Board of Directors, Executive Coach, Forensic Auditor). Typically 1 to 3 profiles per execution.
- **Format = Projection / Delivery Channel (Physical Rendering)**: Represents *how* the exact same semantic content is consumed. Every `ReportArtifact` encapsulates four concurrent delivery projections:
  1. *Interactive Screen*: Native Flutter SDUI rendering via pre-compiled `report.sdui.json`.
  2. *Printable Document*: Paginated vector document via `report.pdf`.
  3. *Tabular Spreadsheet*: Two-tab workbook (Summary + Raw Data) via `report.xlsx`.
  4. *Flat Relational Rows*: Machine-readable tabular rows via CSV and JSON API (`/api/v2/reports/{id}/rows`).

### 3. Enterprise B2B Data Delivery & Public API Integration
Enterprise consumers require structured row-level data to feed internal databases and analytics suites. Quorum exposes two distinct granularity tiers:
- **Tier A: Aggregated Metric Rows**: High-level dimensional scores (specifically: Strategic Vision 4.5/5.0, Operational Focus 3.2/5.0) for PowerBI and executive KPI dashboards.
- **Tier B: Atomic Forensic Evidence Rows**: Granular claim-level records linking evaluated criteria, scores, exact verbatim quotes, and LLM causal justifications for legal, audit, and HR compliance pipelines.
- **External REST API**: Secure multi-tenant endpoints authenticated via API keys (`X-API-Key`) scoped to the client's `organization_id`, delivering clean `PublicReportDTO` envelopes with zero leakage of internal prompt templates or intermediate worker tokens.

### 4. Desktop-Class Pro Tool UX & Studio Input Architecture (Flutter Client)
The Execution Reports View (`ExecutionReportsView`), creation modal (`CreateReportDialog`), card widgets (`ReportArtifactCard`), and host execution views implement the complete 16-pillar desktop interaction ergonomics codified in @[ki_desktop_pro_tool_studio_ux.md], @[ki_workflow_context_governance.md], and @[ki_dual_axis_localization_architecture.md]:
- **Mandatory Pre-Read Requirement**:
  Before touching, creating, or modifying any Flutter window, modal, dialog, view, card, or widget, `@[ki_desktop_pro_tool_studio_ux.md]` MUST be read into active context. All UI implementations MUST adhere to its 16 architectural pillars:
- **1. Adaptive Master Selector Standard (`LayoutBuilder`)**:
  - *Wide Viewports (`maxWidth >= 900px`)*: Lateral Master-Detail layout with a sticky 260px sidebar (`ReportArtifactCard` list rendered via virtualized `ListView.builder` with `prototypeItem`, live status badges, profile pills, and locale tags) flanking the active detail canvas.
  - *Compact Viewports (`maxWidth < 900px`)*: Adaptive Top-Bar Selector (`SingleChildScrollView(scrollDirection: Axis.horizontal)` with `ChoiceChip` selectors and an inline `+ Uusi tuloste` button) mounted directly above the focused detail canvas.
  - *Sub-900px Graceful Degradation*: When viewport width drops below 900px, the Master pane transitions gracefully into top-bar chips or modal Navigation Drawer. It MUST NEVER implicitly revert to unbounded vertical scroll.
- **2. Single Cognitive Unit Isolation**:
  Regardless of viewport width, the editing and viewing canvas renders exactly ONE selected report artifact at a time. Unbounded vertical stacking of multiple reports is strictly prohibited.
- **3. State Retention Invariance**:
  Wide and compact layouts share a unified state and controller pool. Layout transitions triggered by desktop window resizing, tiling, or snapping must NEVER unmount the active `Form`, reset selected report index, or discard in-flight text buffers.
- **4. Progressive Disclosure**:
  Multi-tab detail canvas partitioning output consumption into four distinct tabs: "Interaktiivinen näkymä" (native SDUI rendering via `SduiRenderer`), "PDF-esikatselu" (vector preview), "Rividata & Taulukot" (structured metric and forensic evidence rows), and "Metatiedot & Todisteet" (runtime duration, token metrics, LLM provider).
- **5. Universal Horizontal Overflow Immunity & Header Containment**:
  - All title and metadata labels adjacent to action controls inside a horizontal `Row` are enclosed in `Expanded(child: Text(..., overflow: TextOverflow.ellipsis))` or `Flexible(child: Text(..., overflow: TextOverflow.ellipsis))` to eliminate `RenderFlex` overflow on desktop window snapping.
  - All dropdown selectors (`DropdownButtonFormField` for profile and locale selection) specify `isExpanded: true` to prevent localized text overflow outside the form canvas.
- **6. Internal Horizontal Overflow Protection & Responsive Detail Stacking Guard**:
  - In compound controls and side-by-side action bars, elements stack vertically as a `Column` when local detail pane width `< 520px`, and render side-by-side as a `Row` when `>= 520px`. Input prefix rows stack vertically when local width `< 400px`.
  - Header action clusters isolate controls using `Row(mainAxisSize: MainAxisSize.min, children: [...])` separated from title text by an inflexible `AppSpacing.w16` gutter.
- **7. Dual-Shield FormField Architecture & Modal Dismissal Protocol**:
  - `CreateReportDialog` intercepts `Esc`, AppBar close button, and barrier dismissal via `PopScope(canPop: false, onPopInvokedWithResult: ...)`, routing to a unified `_handleDismiss()` routine. Direct un-intercepted `Navigator.pop()` calls on close buttons are strictly prohibited.
  - **Post-Frame Blur Flush**: `_handleDismiss()` synchronously executes `FocusScope.of(context).unfocus()` to trigger controller focus-loss listeners, and evaluates composite dirty state inside `WidgetsBinding.instance.addPostFrameCallback((_) { if (!mounted) return; ... })`.
  - **Serialization-Based Model Dirty Checking (Zero Fallbacks)**: Because Quorum domain entities are annotated with `@Freezed(equal: false)` per the `o1_lists` mandate, naive reference inequality (`!=`) evaluates reference identity and triggers false positives. `_isModelDirty()` evaluates state differences strictly by comparing serialized JSON snapshots:
    `jsonEncode(_editableModel.toJson()) != _initialModelJson`.
  - **Localized Discard Confirmation**: If dirty, displays an `AlertDialog` with localized strings (`l10n.discardChangesConfirmTitle`). Selecting "Jatka muokkausta" retains modal focus and input buffers; selecting "Hylkää muutokset" dismisses with `null`.
  - **Graceful Focus Preservation on Discard Cancellation**: When discard confirmation is cancelled, parent modal focus is restored without disruptive scroll jumps.
- **8. Modal-Internal Error Surface (Absolute SnackBar Ban)**:
  - All validation errors, prerequisite rejections, and submission failures inside `CreateReportDialog` MUST render strictly within the modal dialog canvas (via inline `FormField.validator` error text or inline banners using `colorScheme.errorContainer`).
  - Calling `ScaffoldMessenger.of(context).showSnackBar()` inside modal dialogs is STRICTLY PROHIBITED, preventing invisible toasts behind modal barriers.
- **9. Auto-Scroll to First Invalid Field**:
  - When form validation fails in `CreateReportDialog`, modal orchestration automatically scrolls the viewport via `Scrollable.ensureVisible` to bring the first invalid input into view and requests focus.
- **10. Cross-Entity Error Navigation**:
  - In Master-Detail layouts where sub-entities are partitioned, if validation fails on an unselected item, the UI switches selection to the first invalid entity and scrolls to its error before halting save.
- **11. Atomic In-Flight Submission Guard (Save Debounce)**:
  - Modal save routines implement an atomic in-flight submission lock (`bool _isSaving = false;`): checks `if (_isSaving) return; _isSaving = true;`, disables the save action button, and resets `_isSaving = false;` synchronously if validation fails.
- **12. Keyboard-First Desktop Interaction & Cursor Ergonomics**:
  - Supports `Ctrl + S` / `Cmd + S` for atomic modal submission and `Esc` for clean dismissal.
  - Explicit `SystemMouseCursors.click` on all interactive cards, chips, buttons, and tab headers.
  - Complete keyboard navigation support via `FocusTraversalGroup` and `FocusNode`.
- **13. Anti-Stringification Input Architecture**:
  - Collections of criteria, tags, or options MUST be managed via discrete chips or card collections with bounded chip width (`maxWidth: 240px`), `TextOverflow.ellipsis`, and hover `Tooltip(message: fullText)`. Delimiter splitting on `\n` or `,` is permanently banned.
- **14. Scalable List Browsing & Virtualization Standard**:
  - Master list of report artifacts in `ExecutionReportsView` MUST use virtualized rendering (`ListView.builder` with `prototypeItem`).
  - Sticky Header & Action Bar: Top bar containing view title, real-time instant search input with `Icons.clear` action (when items > 10), active count indicator (`X / Y raporttia`), and primary creation trigger (`+ Uusi tuloste`) remains pinned at the top during scrolling.
  - Compact vertical density: targeting ~72-88px per card to prevent excessive empty scrolling.
- **15. Wide and Ultrawide Canvas Containment**:
  - Single-column detail views and form canvases enforce bounded containment via `Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), child: ...))` to prevent 2000px+ horizontal sprawl on 1440p and 4K displays.
  - Modal dialogs enforce `ConstrainedBox(constraints: const BoxConstraints(minWidth: 480, maxWidth: 800, minHeight: 400, maxHeight: 720))`.
- **16. AppErrorBoundary Wrapping, Design System & Axis 1 Localization Parity**:
  - `AppErrorBoundary` wraps `ExecutionReportsView`, all 4 detail tabs, and `CreateReportDialog` body to isolate rendering crashes.
  - Studio visual design tokens: card containers (`elevation: 2, BorderRadius.circular(12), padding: EdgeInsets.all(16)`), section headers (`fontSize: 20, fontWeight: FontWeight.bold`), status badges (`colorScheme.primaryContainer`), action triggers (`OutlinedButton.icon`), and destructive actions (`IconButton(icon: Icon(Icons.delete, color: colorScheme.error))`).
  - 100% of UI chrome resolves exclusively from compile-time `.arb` files via `AppLocalizations.of(context)!` with 1:1 Finnish and English parity. Zero hardcoded UI strings.

### 4.1 Dual-Axis Localization Architecture & Multi-Language Parity (Flutter & Backend)
Adhering strictly to @[ki_dual_axis_localization_architecture.md], the Tripartite Pipeline and Report Artifact ecosystem enforce five non-negotiable localization invariants:
1. **Axis 1 (Compile-Time UI Chrome)**:
   - 100% of UI chrome in `ExecutionReportsView`, `CreateReportDialog`, `ReportArtifactCard`, and `NewExecutionView` resolves via `AppLocalizations.of(context)!`.
   - Every single newly introduced key is declared with identical parameter signatures in both `client_app_v2/lib/l10n/app_fi.arb` and `client_app_v2/lib/l10n/app_en.arb`.
   - Hardcoded strings in Dart files are strictly prohibited.
2. **Axis 2 (Dynamic Semantic Domain Content)**:
   - Report contents, workflow names, step descriptions, and rubric criteria are delivered as dynamic strings already resolved according to the target report's `locale` parameter (`fi` or `en`). Flutter acts as a pure Dumb Painter, displaying the DTO's text without client-side translation matrices.
3. **Absolute CQRS Export Firewall (Ban on Backend `.arb` Reads)**:
   - Forensic audit revealed that `backend_v2/services/execution.py#L850-L855` read `client_app_v2/lib/l10n/app_{locale}.arb` using `open()`. This violates layer isolation.
   - In `ExportService`, this is completely eradicated. Excel worksheets ('Summary' and 'Raw Data') and flat CSV column headers resolve strictly from backend `I18nText` database instances or static Python localization dictionaries defined within `ExportService`. The backend never accesses `client_app_v2/lib/l10n/`.
4. **Split-Cognitive Translation in Phase 2 Synthesis (`ReportService`)**:
   - Synthesis tasks (Executive Summary, Variance Narrative, Observation Summaries) invoke `LLMTaskExecutor` with prompts compiled through `linguistic_directives.py`:
     - System Instruction includes `STATIC_LINGUISTIC_PROTOCOL` forcing internal reasoning in English.
     - User message tail injects `build_linguistic_parameters(target_locale=report.locale)`.
     - Raw evidence quotes (`exact_quotes`) remain in their source language.
5. **Strict Enum L10n Adapter**:
   - `ReportStatus` in `backend_v2/models/enums.py` implements `@property def l10n_key(self) -> str:` providing a typed bridge to Flutter ARB keys (`reportStatusPending`, `reportStatusGenerating`, `reportStatusReady`, `reportStatusFailed`).

### 5. Pure REST-API-Only Pipeline Boundary Invariant
When launching an analysis, users can toggle `[x] Generoi tuloste heti ajon valmistuttua (Aja tulosteeksi saakka)` (enabled by default when a profile is selected). This produces the **Dual-Phase Optical Illusion**:
- **User Perception**: A single unified operation ("Run analysis and show report on screen").
- **Physical Reality**: Two completely decoupled, sovereign transactions:
  1. **Phase 1 Transaction (`exe_xxx` / `ExecutionRecord`)**: Heavy LLM DAG evaluation, fact extraction, and topological scoring. Costs tokens, takes 1–3 minutes, and terminates permanently with status `PASSED`.
  2. **Phase 2 & 3 Transaction (`rep_xxx` / `ReportArtifact`)**: Fast deterministic presentation projection (SDUI, PDF, Excel, tabular rows). Costs near zero, takes seconds, and operates purely on the completed immutable Phase 1 snapshot.

#### The REST-API-Only Boundary Mandate (Zero In-Process or Worker Auto-Chaining)
To guarantee the highest degree of architectural decoupling, **there is mathematically NO WAY to connect Phase 1 and Phase 2/3 except across the HTTP REST API**:
1. **The Sole Bridge is the REST API (`POST /api/v2/executions/{execution_id}/reports`)**:
   - The backend execution engine (`worker.py` / `execute_workflow_job`, `execution.py`, `topological_evaluator.py`) is completely blind to `ReportService`, PDF generators, and report queueing.
   - When Phase 1 DAG completes, `execute_workflow_job` sets `status = ExecutionStatus.PASSED`, persists the record, emits an SSE status update, and **immediately terminates**. It NEVER enqueues report generation tasks or triggers Phase 2/3.
2. **Frontend-Driven REST Orchestration**:
   - The Flutter UI acts as the client-side conductor:
     1. User clicks "Käynnistä ajo" with `[x] Aja tulosteeksi saakka`.
     2. UI calls `POST /api/v2/executions` (Phase 1).
     3. UI listens to live SSE progress events on `executionControllerProvider` ("Vaihe 1: Matriisianalyysi käynnissä...").
     4. Upon receiving `ExecutionStatus.PASSED`, the UI controller physically issues an HTTP request:
        `POST /api/v2/executions/{id}/reports` (passing `profile_id` and `locale`).
     5. The UI displays a seamless phase transition: *"Laskenta valmis (100%). Luodaan tulostetta..."*.
     6. Once the report transitions to `READY`, the UI automatically transitions to `ExecutionReportsView` showing the finished report canvas.
3. **Headless & External Client Parity**:
   - If an external enterprise system, B2B integration, or headless test runner executes an analysis, it MUST follow the exact same two-step REST protocol:
     - Step 1: `POST /api/v2/executions` $\rightarrow$ wait for `status == PASSED` (via webhook, SSE, or polling).
     - Step 2: `POST /api/v2/executions/{id}/reports` $\rightarrow$ receive `ReportArtifactSummaryDTO` and download outputs.
   - Zero backdoor worker-to-worker auto-triggers exist.
4. **Architectural Enforcement via Automated AST Tests**:
   - Automated test suite [NEW] @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py] enforces this invariant at the AST level:
     - Verifies that `worker.py`'s `execute_workflow_job` contains ZERO AST references or imports of `ReportService`, `export_service`, or report queue tasks.
     - Verifies that `execute_workflow_job` enqueues 0 report jobs in Redis.
     - Verifies that calling `ReportService` directly or via API fails fast with `409 Conflict` (`ErrorCodes.EXECUTION_NOT_READY`) if `execution.status != ExecutionStatus.PASSED`.

### 6. Database & Storage Architecture in Microservices Spirit
The database layer enforces strict bounded context separation, eliminating the shared-entity anti-pattern where presentation fields were previously crammed into the execution table:
1. **Schema Segregation (`executions` vs `report_artifacts`)**:
   - `executions/`: Authoritative, append-only repository for Phase 1 analytical computation (`ExecutionRecord`). Records are marked `status = ExecutionStatus.PASSED`, timestamped, and rendered permanently immutable. Zero presentation layout or file path fields exist in this collection.
   - `report_artifacts/`: Autonomous collection for Phase 2 & 3 presentation artifacts (`ReportArtifact`). Each record possesses its own unique primary key (`id: rep_...`), its own lifecycle state (`PENDING`, `GENERATING`, `READY`, `FAILED`), and links to Phase 1 solely via a loose foreign identifier (`execution_id: str`).
2. **Dedicated Repository Implementations (Interface Segregation)**:
   - Data access is segregated into dedicated, single-responsibility repositories:
     - `IExecutionRepository` / `ExecutionRepositoryImpl` (`database/repositories/execution.py`): Operates strictly against `executions`. Completely blind to reports.
     - `IReportArtifactRepository` / `ReportArtifactRepositoryImpl` (`database/repositories/report_artifact.py` [NEW]): Operates strictly against `report_artifacts`.
   - Neither repository can access or mutate the other's collection.
3. **Cloud-Native Object Storage (Metadata in DB, Heavy Blobs in Storage)**:
   - To prevent database bloat, the database stores exclusively lightweight metadata (IDs, title, profile, locale, duration, tokens, timestamps, file URIs).
   - Heavy serialized presentation blobs and rendered binaries are persisted to Cloud-Native Object Storage via `StorageDriver`:
     - `artifacts/reports/{report_id}/report.sdui.json` (Pre-compiled SDUI tree, served at $O(1)$ latency)
     - `artifacts/reports/{report_id}/report.pdf` (Paginated vector PDF)
     - `artifacts/reports/{report_id}/report.xlsx` (Multi-tab Excel workbook)
     - `artifacts/reports/{report_id}/report.csv` (Flat relational row export)
4. **$1\text{-to-}N$ Scalability & Clean Purge Lifecycle**:
   - A single `ExecutionRecord` can spawn an arbitrary number of `ReportArtifact` records (specifically: Executive Summary in FI, Technical Audit in EN, Board Briefing) without altering the parent execution record.
   - Invoking `DELETE /api/v2/reports/{id}` cleanly purges the database metadata and associated disk files from object storage with zero cascading mutation to Phase 1 data.

### 7. Four-Tier Pydantic V2 Domain & DTO Model Topology
To eradicate loose dictionaries (`dict[str, Any]`), untyped state tuples, and silent field mutations, the model architecture is strictly partitioned into four non-overlapping Pydantic V2 tiers:
1. **Tier 1: Analytical Execution Models (`models/execution_core.py`, `models/dtos/trace.py`)**:
   - `ExecutionRecord`, `ExecutionCreateDTO`, `ExecutionUpdateDTO`, `AtomResultDTO`, `MCPAuditTrace`, `QuoteEvidenceDTO`, `ExecutionMetricsDTO`.
   - *Responsibility*: Model pure analytical reasoning, DAG state transitions, factual quotes, and statistical metrics (Cohen's Kappa, Shannon Entropy). Completely agnostic of presentation themes, profiles, or PDF layouts.
2. **Tier 2: Materialized Artifact Lifecycle DTOs (`models/dtos/report_artifact.py` [NEW])**:
   - `ReportArtifact`, `ReportArtifactCreateDTO`, `ReportArtifactUpdateDTO`, `ReportArtifactSummaryDTO`, `ReportStoragePathsDTO`, `ReportMetadataDTO`.
   - *Responsibility*: Contract envelope for report generation, storage tracking, and asynchronous generation state.
3. **Tier 3: Dumb Painter Presentation & Row Delivery Models (`models/v2_core.py`, `models/view/sdui.py`)**:
   - `ReportDataDTO`, `list[AnySduiBlock]`, `ReportRowItemDTO`, `PublicReportDTO`.
   - *Responsibility*: Immutable presentation projections consumed by Flutter SDUI renderers, WeasyPrint PDF templates, and B2B tabular consumers.
4. **Tier 4: Studio Output Profile Definitions (`models/domain/output_profile.py`)**:
   - `OutputProfile`, `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`.
   - *Responsibility*: SSOT configuration recipes (synthesis directives, tone instructions, SDUI component sequences). Enforces explicit Studio configuration selectors (`variance_target_block`, `user_role_target_block`) adhering strictly to `studio_driven_parameterization_mandate`.
5. **Architectural Enforcement & Invariants**:
   - **`extra="forbid"` Everywhere**: Every model without exception configures `model_config = ConfigDict(strict=True, extra="forbid")`. Passing an execution field to a report DTO or vice versa raises an audible `ValidationError`.
   - **Zero Naked Dicts**: `dict[str, Any]` and `TypedDict` are banned from domain state transit. Every nested structure is an explicit, immutable Pydantic V2 model.
   - **Full-Duplex Serialization Parity**: Every Python Pydantic V2 model has a 1:1 typed Dart Freezed counterpart in Flutter (`@Freezed(equal: false)`) with matching `snake_case` $\leftrightarrow$ `camelCase` `@JsonKey` mappings.

### 7.1 Lifecycle Ontology & Pipeline Streamlining: ReportArtifact vs. ReportDataDTO vs. ReportRowItemDTO

To guarantee a streamlined, high-performance pipeline that completely eliminates redundant computations across multi-channel rendering, the architecture enforces the **"Compute Once, Project Many"** paradigm across three distinct model roles:

```
[Phase 1: ExecutionRecord] (Authoritative raw analytical computation & atom scores)
             │
             ▼
[Phase 2: LLM Synthesis] (Section-mapped markdown syntheses for profile & locale)
             │
             ▼
[Phase 3: BlueprintTransformer]
   │
   └─► ASSEMBLED ONCE: ReportDataDTO  (Immutable SSOT Presentation Envelope)
            │
            ├──────────────────────┬──────────────────────┐
            ▼                      ▼                      ▼
      report.sdui.json        report.pdf            ReportRowItemDTO (Pure Map)
      (Screen rendering)     (WeasyPrint)                 │
                                                          ├─► report.xlsx (Excel workbook)
                                                          ├─► report.csv (Flat CSV export)
                                                          └─► GET /api/v2/reports/{id}/rows
```

1. **Model Ontologies & Operational Roles**:
   - **`ReportArtifact` (Lifecycle Entity & Database Record)**:
     - The parent container entity residing in the `report_artifacts` database collection (`id: rep_...`).
     - Tracks generation state (`PENDING`, `GENERATING`, `READY`, `FAILED`), associated metadata (duration, token cost, active LLM model/provider), and physical storage paths (`report.sdui.json`, `report.pdf`, `report.xlsx`, `report.csv`).
     - Created *first* upon receipt of `POST /api/v2/executions/{id}/reports`.
   - **`ReportDataDTO` (Presentation Payload & Content SSOT)**:
     - The internal, intelligent presentation payload assembled by `BlueprintTransformer`.
     - Synthesizes Phase 1 analytical atoms (`results: list[AtomResultDTO]`), $O(1)$ reference lookups (`hydrated_references: dict[str, HydratedAtomDTO]`), forensic evidence (`mcp_tool_audit: list[MCPAuditTrace]`), and pre-compiled visual SDUI components (`inner_sdui_blocks: list[AnySduiBlock]`).
     - Created *second* inside the background worker and serialized directly to `artifacts/reports/{id}/report.sdui.json`.
   - **`ReportRowItemDTO` (Tabular Row Projection)**:
     - A lightweight, flat data contract optimized for relational databases, BI tools (PowerBI), and tabular spreadsheet consumers.
     - Created *third* as a pure $O(N)$ projection directly from `ReportDataDTO.results` and `ReportDataDTO.hydrated_references` via a deterministic mapper function (`extract_report_rows(report_dto)`). It NEVER re-parses execution traces or issues database queries.

2. **Streamlined Pipeline & Anti-Redundancy Invariants (Compute Once, Project Many)**:
   - **Single Transformer Invariant**: `BlueprintTransformer` executes exactly once per report generation request. It performs all topological sorting, score rounding, and visual block composition in memory, outputting the canonical `ReportDataDTO`.
   - **Zero Redundant Parsing**: WeasyPrint PDF compilation, Excel workbook compilation (`ExportService.export_excel`), and CSV generation (`ExportService.export_flat_csv`) consume the already-assembled `ReportDataDTO` (and its projected `ReportRowItemDTO` list) directly. No downstream sink ever reads `ExecutionRecord.execution_trace` or re-calculates metrics.
   - **Eager Materialization to Object Storage**: All four output projections (`report.sdui.json`, `report.pdf`, `report.xlsx`, `report.csv`) are generated and persisted concurrently during the background job. All subsequent client retrieval endpoints (`GET /sdui`, `GET /pdf`, `GET /excel`, `GET /csv`, `GET /rows`) operate as instantaneous $O(1)$ file or JSON streams with zero server-side computation.

### 7.2 UI Value Hydration Lifecycle & Cross-Platform Semantic Parity (Screen ↔ PDF)

1. **Two-Phase UI Hydration Lifecycle**:
   - **Phase 1 Execution Tracking**: When the user launches an analysis, Flutter's `ExecutionView` binds to the real-time Server-Sent Events (SSE) status stream (`stream_status`). It renders live DAG progression ("Matrix analysis running...", step completion nodes). The UI displays zero report cards or output canvases during this phase because analytical reasoning is strictly in-flight.
   - **Phase Transition**: Upon DAG conclusion, `worker.py` transitions the execution directly to `ExecutionStatus.PASSED`. If "Run until output" (`[x] Aja tulosteeksi saakka`) was selected, the UI controller automatically issues `POST /api/v2/executions/{id}/reports`.
   - **Phase 2 & 3 Background Compilation**: `ReportService` and `report_worker` compile `ReportDataDTO` and the 4 physical files, updating `ReportArtifact.status = READY`.
   - **O(1) Instantaneous UI Hydration**:
     1. Flutter receives the `READY` status event and calls `GET /api/v2/reports/{id}/sdui`.
     2. The backend streams the pre-compiled `report.sdui.json` payload directly from disk with $O(1)$ latency.
     3. Flutter deserializes the payload into the client `@Freezed ReportDataDTO` model.
     4. Flutter's `SduiRenderer` traverses `inner_sdui_blocks` and maps each polymorphic block (`HeroInsightBlock`, `VarianceBlock`, `DataGridBlock`, `MarkdownBlock`) directly into corresponding native Flutter widgets.

2. **Cross-Platform Semantic Parity Mandate (Screen ↔ PDF Parity)**:
   - **The Architectural Parity Invariant**:
     `ReportDataDTO` encapsulates `inner_sdui_blocks` precisely because Flutter is designed as a **Dumb Painter**. The client application does not contain heuristic rules or layout algorithms; layout topology is governed 100% by the server-side Studio definition (`OutputProfile.target_block_order`). Because the exact same `ReportDataDTO` and `inner_sdui_blocks` are supplied to both Flutter (`SduiRenderer`) and WeasyPrint (`PdfReportService`), Semantic Parity Drift is architecturally prevented.
   - **Mathematical Parity Proof via Automated E2E Testing (`test_sdui_semantic_parity.py`)**:
     Cross-domain parity between the Flutter canvas and generated PDF is mathematically verified by the automated integration test `backend_v2/tests/integration/test_sdui_semantic_parity.py`:
     1. *Dynamic Mock Generation*: Generates a comprehensive `ReportDataDTO` instance encompassing matrix tables, contextual overrides, and dimensional scores.
     2. *Physical Flutter Engine Execution*: Executes `flutter test test/features/execution/sdui_semantic_parity_test.dart`, rendering the real Flutter widget tree and extracting all visible text, headers, and numbers into a structured semantic token stream (`SduiSemanticTokenDTO`).
     3. *Physical WeasyPrint PDF Generation*: Compiles the identical DTO into an actual vector PDF using `PdfReportService`.
     4. *PDF Forensic Text Extraction*: Extracts rendered document text using `pymupdf4llm`.
     5. *Mathematical Assertion*: Cross-references every semantic token extracted from Flutter against the PDF text stream, enforcing that 100% of text and scores visible on the Flutter screen exist identically in the generated PDF. Any semantic omission or mismatch immediately fails the Universal Quality Gate.

---

### 8. Module-Specific Responsibility Allocation & God Code Decomposition Architecture (SRP & DDD)

To eradicate monolithic God Files and prevent cross-cutting architectural entanglement, the entire execution and reporting subsystem is partitioned according to the Single Responsibility Principle (SRP) and Domain-Driven Design (DDD) bounded contexts.

#### 1. Single Responsibility Principle (SRP) Responsibility Matrix

| Osa-alue | Vanha monoliitti | Uusi Tripartite-rakenne | Vastuu ja eristys |
| :--- | :--- | :--- | :--- |
| **Laskentapalvelut** | `ExecutionService` (1 511 riviä monoliitti) | `backend_v2/services/execution/` (Mikropalvelut, jokainen <180 riviä) | **Pilkotut elinkaaripalvelut**:<br>1. `ExecutionLifecycleService` (~180 riviä, `lifecycle_service.py`): Elinkaaren hallinta ja koordinointi (`list_executions`, `get_execution`, `delete_execution`, `cancel_execution`).<br>2. `ExecutionIngressService` (~180 riviä, `ingress_service.py`): Syötteiden validointi (`SmartIngressResolver`), dokumenttiliitteet, SDUI-vihjeet ja `create_execution_record`.<br>3. `ExecutionResumptionService` (~120 riviä, `resumption_service.py`): Ajon jatkamiskelpoisuus (`check_resumability`), FinOps-tarkistus ja uudelleenkäynnistys.<br>4. `ExecutionOverrideService` (~140 riviä, `override_service.py`): Ihmiskorjaukset (`override_atom`), todisteiden hylkäys ja pisteiden uudelleenlaskenta.<br>5. `ExecutionStreamService` (~80 riviä, `stream_service.py`): SSE-tilavirran striimaus (`stream_status`).<br>6. `FrozenContextService` (~50 riviä, `context_service.py`): Oikeusforensiikan jäädytetyn kontekstin luku.<br>*(Juuren `services/execution.py` säilyy <80 rivin Strangler Fig -julkisivuna explicit re-exportilla).* |
| **Ydintietomallit** | `v2_core.py` (1 920 riviä megamonoliitti) | `backend_v2/models/domain/` (DDD-alueet, jokainen <300 riviä) | **Tripartite-jaetut domain-mallit**:<br>1. `domain/matrix.py` (~260 riviä): Phase 1 matriisit ja väitteet.<br>2. `domain/execution.py` (~250 riviä): Phase 1 laskennan tila ja elinkaari.<br>3. `dtos/atom_result.py` (~110 riviä): Phase 1 atomien tulokset.<br>4. `domain/synthesis.py` (~160 riviä): Phase 2 synteesit ja XAI.<br>5. `domain/output_profile.py` (~300 riviä): Phase 3 esitysprofiili.<br>6. `domain/report_artifact.py` (~90 riviä): Phase 3 raporttientiteetti.<br>7. `dtos/report_data.py` (~80 riviä): Phase 3 SDUI-kuori.<br>8. `domain/workflow.py` (~160 riviä) & `domain/step.py` (~260 riviä): Studio-mallit.<br>9. `domain/system_config.py` (~140 riviä): FinOps ja MCP.<br>*(Juuren `v2_core.py` säilyy <90 rivin Strangler Fig -julkisivuna explicit re-exportilla).* |
| **Tulostuspalvelu** | Sekaisin `execution.py` ja `worker.py` | `ReportService` [NEW] (~250 riviä) | **Vain raporttien elinkaari**: Luo ja hallinnoi `ReportArtifact`-tietueita, koordinoi taustagenerointia, hakee pre-compiloidut tiedostot levyltä/oliolevyltä, B2B-taulukkorivien generointi ja uudelleengenerointi. |
| **Tiedostovienti** | Piilotettu `execution.py`:hyn | `ExportService` [NEW] (~150 riviä) | **Vain tiedostomuunnokset**: Puhdas konvertteri: `ReportDataDTO` $\rightarrow$ monivälilehtinen Excel ja flat CSV backendin omalla `I18nText`-kielistyksellä. Ei koskaan lue frontendin `.arb`-tiedostoja. |
| **Esitysmuunnin** | `BlueprintTransformer` (kirjoitti kantaan!) | `BlueprintTransformer` (Puhdas funktio) | **Vain SDUI-näkymä**: 100 % read-only. Muuntaa lasketut matriisit ja faktat visuaalisiksi näkymälohkoiksi tallentamatta kantaan yhtään mitään (`update_execution` poistettu täysin). |
| **Taustatyöt** | `worker.py` (2 037 riviä) | Eristetyt Arq-tehtävät (`backend_v2/workers/`) | `execute_workflow_job` ajaa vain Phase 1:n ja sulkeutuu. `generate_report_artifact_job` suorittaa vain raportoinnin. `worker.py` toimii ohuena Strangler Fig -julkisivuna (<150 riviä). |
| **API-rajapinnat** | Kaikki `/executions`-reitittimessä | `executions.py` and `reports.py` [NEW] | **Selkeä jako**: `/api/v2/executions` käsittelee laskentaa, `/api/v2/reports` käsittelee tulosteita ja B2B-rividataa. |
| **Käyttöliittymä** | `ExecutionView` (kaikki samassa ruudussa) | `ExecutionView` + `ExecutionReportsView` [NEW] | Käyttäjä katsoo ajon aikana laskennan edistymistä, ja tuloste avataan erilliseen Pro Tool -raportointinäkymään Adaptive Master Selector -standardin mukaisesti. |

#### 2. God Code Decomposition Protocol (/tier3-god-code-decomposition Style)

Adhering strictly to @[ki_god_code_prevention.md] and `/tier3-god-code-decomposition`, the decomposition of the system's monoliths (`backend_v2/worker.py` with 2,037 lines, `backend_v2/services/execution.py` with 1,511 lines, and `backend_v2/models/v2_core.py` with 1,920 lines) follows the Strangler Fig Pattern:

1. **Worker Decomposition (`backend_v2/workers/`)**:
   - **`[NEW] backend_v2/workers/__init__.py`**: Subpackage initialization and explicit export facade.
   - **`[NEW] backend_v2/workers/execution_worker.py` (~400 lines)**:
     - Extracted strictly from `worker.py` lines 139–568.
     - Houses `execute_workflow_job`.
     - Operates strictly on Phase 1 DAG execution, topological scoring, token usage accumulation, and transitions directly to `ExecutionStatus.PASSED`.
     - Completely blind to `ReportService`, PDF engines, and report jobs. Zero AST imports or task enqueues targeting Phase 2/3.
   - **`[NEW] backend_v2/workers/report_worker.py` (~450 lines)**:
     - Extracted strictly from `worker.py` lines 569–1942.
     - Houses `generate_report_artifact_job`, `generate_pdf_task`, `render_profile_job`, and `generate_profile_synthesis_and_pdf_task`.
     - Handles Phase 2 LLM synthesis (executive summaries, cognitive variance explanations, XAI highlights, Harvard citations) and Phase 3 WeasyPrint PDF compilation.
     - Enforces Failure Isolation: presentation and synthesis errors update `ReportArtifact.status = ReportStatus.FAILED`, never polluting `ExecutionRecord.status`.
   - **`[MODIFY] backend_v2/worker.py` (Strangler Fig Facade & Entrypoint, <150 lines)**:
     - Retains Arq lifecycle functions: `startup` (#L1943-L1996), `shutdown` (#L1997-L2005), `health_check` (#L2006-L2017), and `WorkerSettings` (#L2018-L2036).
     - Imports `execute_workflow_job` from `backend_v2.workers.execution_worker` and report tasks from `backend_v2.workers.report_worker`.
     - **MyPy Strict Re-Export Enforcement**: Explicitly re-exports all legacy public symbols via `__all__ = [...]` and redundant aliases (`from backend_v2.workers.execution_worker import execute_workflow_job as execute_workflow_job`) to satisfy PEP 484 and prevent `[attr-defined]` / `implicit re-export` errors in CI/CD quality gates.
     - Ensures downstream entry points specifically `backend_v2/run_worker.py` continue functioning without disruption.

2. **Execution Service Decomposition (`backend_v2/services/execution/`)**:
   To eradicate the 1,510-line monolith and guarantee that no single service exceeds the 200-line limit mandated in @[ki_god_code_prevention.md], the execution service layer is decomposed into a dedicated `backend_v2/services/execution/` subpackage composed of single-responsibility micro-services:
   - **`[NEW] backend_v2/services/execution/__init__.py`**: Subpackage initialization and explicit export facade.
   - **`[NEW] backend_v2/services/execution/lifecycle_service.py` (~180 lines)**:
     - Encapsulates tenant-isolated execution lifecycle operations: `list_executions` (#L197-L236; with concurrent resumability evaluation), `get_execution` (#L237-L275; with permission checks), and `delete_execution` (#L347-L400; with storage cleanup).
   - **`[NEW] backend_v2/services/execution/ingress_service.py` (~180 lines)**:
     - Encapsulates execution startup: workflow validation, FinOps quota verification (`usage_service.check_quota`), dynamic input slot resolution via `SmartIngressResolver`, document attachment extraction via `DocumentExtractionService`, dynamic synchronous SDUI hint generation (`DataDictionaryField`), and type-safe record factory instantiation (`create_execution_record` #L100-L158 cleansed of `**extra_persistence_fields`). Enqueues `execute_workflow_job` in Arq Redis (`start_execution` #L401-L645).
   - **`[NEW] backend_v2/services/execution/resumption_service.py` (~120 lines)**:
     - Encapsulates execution resumption: `check_resumability` (evaluates FAILED state, checkpoint history, DAG version parity, and FinOps quota #L646-L707, with duck-typing cleansed) and `resume_execution` (#L708-L764; re-enqueues job into worker pool).
   - **`[NEW] backend_v2/services/execution/override_service.py` (~140 lines)**:
     - Encapsulates human-in-the-loop modifications: `override_atom` (#L1059-L1147; updates `scorecard_atoms` and `step_states`, triggers hook recalculation via `recalculate()`, and appends `evidence_override` trace event) and `reject_evidence_quote` (#L1148-L1171).
   - **`[NEW] backend_v2/services/execution/stream_service.py` (~80 lines)**:
     - Encapsulates Server-Sent Events (SSE) status streaming: `stream_status` with connection authorization, JSON formatting (`data: ...`), retry backoff, and error event emission (#L276-L346).
   - **`[NEW] backend_v2/services/execution/context_service.py` (~50 lines)**:
     - Encapsulates forensic snapshot access: `get_frozen_context_bytes` (reads from `StorageDriver` or in-memory snapshot, formats JSON for audit #L765-L800).
   - **`[MODIFY] backend_v2/services/execution.py` (Strangler Fig Facade, <80 lines)**:
     - Composes the decomposed services into a unified `ExecutionService` class and provides explicit PEP 484 re-exports (`__all__ = ["ExecutionService", "create_execution_record", ...]`) and redundant aliases (`from backend_v2.services.execution.ingress_service import create_execution_record as create_execution_record`), providing an invariant migration facade for all existing callers and unit tests.

3. **Reporting and Export Services (`backend_v2/services/`)**:
   - **`[NEW] backend_v2/services/report_service.py` (~250 lines)**:
     - Ingests `IReportArtifactRepository`, `IExecutionRepository`, `IOutputProfileRepository`, and `StorageDriver`.
     - Implements complete `ReportArtifact` lifecycle: `create_report_artifact_entry`, `process_artifact_compilation`, `get_report_sdui`, `get_report_pdf_bytes`, `get_report_excel_bytes`, `get_report_csv_bytes`, `get_report_rows`, `delete_report_artifact`, and `regenerate_report_artifact`.
     - Operates strictly downstream of completed Phase 1 executions.
   - **`[NEW] backend_v2/services/export_service.py` (~150 lines)**:
     - Pure functional converter converting `ReportDataDTO` into multi-tab Excel workbooks (`Summary` and `Raw Data`) and flat CSV bytes (extracted from `execution.py#L787-L965`).
     - Resolves column headers strictly from backend `I18nText` database records and static dictionaries, eliminating all client `.arb` reads (#L836-L838).

4. **Core Domain Model Decomposition (`backend_v2/models/v2_core.py` -> `backend_v2/models/domain/`)**:
   Adhering to @[ki_tripartite_pipeline_architecture.md], @[ki_god_code_prevention.md], and @[.agents/workflows/tier3-god-code-decomposition.md], the 1,919-line `backend_v2/models/v2_core.py` monolith is decomposed across the 3 Tripartite Phases and Studio Bounded Contexts:
   - **Phase 1 (Execution & Matrix Engine)**:
     - `[NEW] backend_v2/models/domain/matrix.py` (~260 lines): `TheoryGrounding` (#L121), `AcceptanceCriterion` (#L137), `AntiPattern` (#L146), `ContrastivePairDTO` (#L162), `TDAAssertion` (#L197), `MatrixClaim` (#L329), `MatrixRow` (#L347), `MatrixScale` (#L361).
     - `[NEW] backend_v2/models/domain/execution.py` (~250 lines): `FrozenContext` (#L1548), `ExecutionCreate` (#L1564), `ExecutionStep` (#L1608), `ExecutionSummarySnapshot` (#L1649), `EvaluatedMatrixContextDTO` (#L1662), `ExecutionRecord` (#L1722), `JobAcceptedDTO` (#L1799), `EvidenceRejectionRequest` (#L1809).
     - `[NEW] backend_v2/models/dtos/atom_result.py` (~110 lines): `ErrorDetailsDTO` (#L830), `HydratedAtomDTO` (#L836), `ExtractedValueDTO` (#L847), `AtomResultDTO` (#L853), `ExecutionMetricsDTO` (#L920), `ExtensionMetricsDTO` (#L1676).
   - **Phase 2 (Synthesis & XAI)**:
     - `[MODIFY] backend_v2/models/domain/synthesis.py` (~160 lines): Consolidates `MatrixSynthesisGroup` (#L1008-L1065), `RenderedSynthesisCache` (#L1689), `BaseMatrixXAI` (#L1820), `BaseTDAExtraction` (#L1831).
   - **Phase 3 (SDUI & Presentation / Reports)**:
     - `[MODIFY] backend_v2/models/domain/output_profile.py` (~300 lines): Elevates from a 10-line re-export stub to the authoritative `OutputProfile` domain model (#L1066-L1379), strictly preserving explicit block selectors (`variance_target_block`, `user_role_target_block`) in compliance with `studio_driven_parameterization_mandate`.
     - `[NEW] backend_v2/models/domain/report_artifact.py` (~90 lines): Dedicated domain entity for `ReportArtifact` with storage paths, metadata, and status.
     - `[NEW] backend_v2/models/dtos/report_data.py` (~80 lines): Pure presentation envelope `ReportDataDTO` (#L928-L1007).
   - **Studio & Platform Bounded Contexts**:
     - `[NEW] backend_v2/models/domain/workflow.py` (~160 lines): `Workflow` domain model (#L1380-L1547; cleansed of dead-weight `allowed_exports`).
     - `[NEW] backend_v2/models/domain/step.py` (~260 lines): `Step` (#L542), `StepRule` (#L632), `Role` (#L674), `QuestionnaireItem` (#L687), `ExpectedInput` (#L700).
     - `[NEW] backend_v2/models/domain/system_config.py` (~140 lines): `ChatMessageDTO` (#L383), `ChatHistoryDTO` (#L397), `DataDictionaryField` (#L409), `ProviderExtraParamsDTO` (#L420), `ModelProfile` (#L433), `SystemConfigModelRegistry` (#L465), `AllowedMCPTool` (#L492), `MCPAuditTrace` (#L505), `SystemConfigMCPGateways` (#L529).
   - **Strangler Fig Proxy Facade (`[MODIFY] backend_v2/models/v2_core.py`, <90 lines)**:
     - Imports all extracted models from `backend_v2.models.domain.*` and `backend_v2.models.dtos.*`.
     - Explicitly exports all 43 symbols via `__all__ = [...]` and redundant aliases (`from backend_v2.models.domain.execution import ExecutionRecord as ExecutionRecord`), guaranteeing seamless import resolution for all 250+ existing callers and satisfying PEP 484 and `mypy --strict`.

5. **API Router Segregation (`backend_v2/api/routers/execution/`)**:
   - **`[MODIFY] backend_v2/api/routers/execution/executions.py`**: Handles calculation endpoints (`POST /api/v2/executions`, `GET /api/v2/executions`, `GET /api/v2/executions/{id}`, `POST /api/v2/executions/{id}/override_atom`, `POST /api/v2/executions/{id}/cancel`).
   - **`[NEW] backend_v2/api/routers/execution/reports.py`**: Handles report artifact endpoints (`POST /api/v2/executions/{id}/reports`, `GET /api/v2/executions/{id}/reports`, `GET /api/v2/reports/{id}`, `GET /api/v2/reports/{id}/sdui`, `GET /api/v2/reports/{id}/pdf`, `GET /api/v2/reports/{id}/excel`, `GET /api/v2/reports/{id}/csv`, `GET /api/v2/reports/{id}/rows`, `DELETE /api/v2/reports/{id}`, `POST /api/v2/reports/{id}/regenerate`, `GET /api/v1/external/reports/{id}`).

6. **Flutter UI Segregation (`client_app_v2`)**:
   - **`ExecutionView` (`lib/features/execution/views/execution_view.dart`)**: Solely displays Phase 1 DAG progress and node completion in real time.
   - **`ExecutionReportsView` [NEW] (`lib/features/reports/views/execution_reports_view.dart`)**: Dedicated Desktop Pro Tool interface for managing and viewing pre-compiled report artifacts across profiles and locales.

7. **Strangler Fig Safety Invariants**:
   - **Mathematical AST Boundary Verification**: All node boundary slices are mapped using `ast.parse` via `scripts/_ast_boundary_utils.py` prior to code extraction.
   - **Zero Behavioral Change**: Refactoring is purely structural. Existing business logic, score calculations, and trace schemas remain 100% invariant.
   - **Zero Circular Dependencies**: All shared models reside in `backend_v2/models/dtos/` and `backend_v2/models/domain/`. Decomposed models, workers, and services never import each other circularly.

---

## Target and Context Boundaries

### Target Files (Files to Modify or Create)
- `[NEW]` @[backend_v2/workers/__init__.py] - Subpackage initialization and explicit export facade for background workers.
- `[NEW]` @[backend_v2/workers/execution_worker.py] - Extracted from `worker.py` lines 139–566; Phase 1 DAG execution background task (`execute_workflow_job`), <400 lines.
- `[NEW]` @[backend_v2/workers/report_worker.py] - Extracted from `worker.py` lines 569–1937; Phase 2 & 3 report artifact compilation (`generate_report_artifact_job`, `generate_pdf_task`, `render_profile_job`, `generate_profile_synthesis_and_pdf_task`), <450 lines.
- `[MODIFY]` @[backend_v2/worker.py] - Strangler Fig entrypoint & facade (<150 lines); configures `WorkerSettings` (#L2018-L2036), lifecycle functions (`startup` #L1943-L1994, `shutdown` #L1997-L2003, `health_check` #L2006-L2015), registers Arq tasks, and explicitly re-exports all public symbols via `__all__` to satisfy PEP 484 and `mypy --strict`.
- `[NEW]` @[backend_v2/services/execution/__init__.py] - Subpackage initialization and explicit export facade for calculation services.
- `[NEW]` @[backend_v2/services/execution/lifecycle_service.py] - Tenant-isolated execution lifecycle operations (`list_executions` #L197-L235, `get_execution` #L237-L274, `delete_execution` #L347-L399), ~180 lines.
- `[NEW]` @[backend_v2/services/execution/ingress_service.py] - Execution startup: `SmartIngressResolver`, document attachments, dynamic SDUI hints generation, `create_execution_record` (#L100-L156 cleansed of `**extra_persistence_fields`), and Arq job enqueuing (`start_execution` #L401-L644), ~180 lines.
- `[NEW]` @[backend_v2/services/execution/resumption_service.py] - Resumption and checkpoint validation: `check_resumability` (#L646-L706, duck-typing cleansed) and `resume_execution` (#L708-L763), ~120 lines.
- `[NEW]` @[backend_v2/services/execution/override_service.py] - Human-in-the-loop modifications: `override_atom` (#L1059-L1146), `reject_evidence_quote` (#L1148-L1170), and scoring hook recalculation, ~140 lines.
- `[NEW]` @[backend_v2/services/execution/stream_service.py] - Server-Sent Events (SSE) status streaming (`stream_status` #L276-L345), ~80 lines.
- `[NEW]` @[backend_v2/services/execution/context_service.py] - Forensic snapshot retrieval (`get_frozen_context_bytes` #L765-L799), ~50 lines.
- `[MODIFY]` @[backend_v2/services/execution.py] - Strangler Fig facade (<80 lines) composing execution services and providing explicit PEP 484 re-exports (`__all__`) for seamless caller migration; extracts legacy report rendering blocks (`render_execution` #L1172-L1391, `get_report_dto` #L1393-L1420, `enqueue_pdf_generation` #L1449-L1489) into `ReportService`.
- `[NEW]` @[backend_v2/services/export_service.py] - Extracted from `execution.py` lines 801–1004 (~150 lines); pure converter from `ReportDataDTO` to multi-tab Excel and flat CSV using backend `I18nText` SSOT, eliminating direct `.arb` reads (#L850-L855).
- `[NEW]` @[backend_v2/services/report_service.py] - Core reporting service (~250 lines); manages full `ReportArtifact` lifecycle, Cloud-Native Object Storage coordination, row-level data extraction, and regeneration.
- `[MODIFY]` @[backend_v2/services/blueprint.py#L62-L588] - Make `BlueprintTransformer` 100% read-only; eradicate `update_execution` (#L360) and recursive dict scraping in `extract_evidence_ids` (#L461-L477).
- `[MODIFY]` @[backend_v2/models/dtos/trace.py#L40-L57] - Update `ExecutionCreateDTO` to declare `output_profile_id: Annotated[str | None, Field(default=None)] = None`.
- `[MODIFY]` @[backend_v2/models/dtos/studio.py] - Purge dead-weight `_default_allowed_exports()` (#L95-L96), `WorkflowCreateDTO.allowed_exports` (#L125-L128), and `WorkflowUpdateDTO.allowed_exports` (#L598).
- `[MODIFY]` @[backend_v2/services/studio/workflow_service.py#L319] - Purge `allowed_exports=["pdf"]` from `create_draft`.
- `[MODIFY]` @[backend_v2/tests/factories/model_factories.py#L45] - Purge `allowed_exports` parameter from `create_workflow` factory.
- `[MODIFY]` @[backend_v2/seed/seed_data.json] - Purge `allowed_exports` from the 6 workflow records (`wf_9d68c573802341db`, `wf_01a1d71000000001`, `wf_02a1d71000000002`, `wf_03a1d71000000003`, `wf_04a1d71000000004`, `wf_05a1d71000000005`) adhering to `03_seed_vault.md`.
- `[MODIFY]` @[backend_v2/models/v2_core.py] - Decompose 1,919-line monolith into single-responsibility domain models; refactor into a thin Strangler Fig Facade (<90 lines) with PEP 484 explicit re-exports (`__all__` and redundant aliases) to ensure zero broken imports codebase-wide.
- `[NEW]` @[backend_v2/models/domain/workflow.py] (~160 lines) - Houses `Workflow` domain model (#L1380-L1545; cleansed of dead-weight `allowed_exports`, with `default_profile_id` optional).
- `[NEW]` @[backend_v2/models/domain/step.py] (~260 lines) - Houses `Step` (#L542-L629), `StepRule` (#L632-L671), `Role` (#L674-L684), `QuestionnaireItem` (#L687-L694), `ExpectedInput` (#L700-L815).
- `[NEW]` @[backend_v2/models/domain/matrix.py] (~260 lines) - Tripartite Phase 1 evaluation models: `TheoryGrounding` (#L121-L134), `AcceptanceCriterion` (#L137-L143), `AntiPattern` (#L146-L152), `ContrastivePairDTO` (#L162-L194), `TDAAssertion` (#L197-L326), `MatrixClaim` (#L329-L344), `MatrixRow` (#L347-L358), `MatrixScale` (#L361-L380).
- `[NEW]` @[backend_v2/models/domain/execution.py] (~250 lines) - Tripartite Phase 1 runtime models: `FrozenContext` (#L1548-L1561), `ExecutionCreate` (#L1564-L1605), `ExecutionStep` (#L1608-L1643), `ExecutionSummarySnapshot` (#L1649-L1659), `EvaluatedMatrixContextDTO` (#L1662-L1673), `ExecutionRecord` (#L1722-L1796), `JobAcceptedDTO` (#L1799-L1806), `EvidenceRejectionRequest` (#L1809-L1814).
- `[NEW]` @[backend_v2/models/dtos/atom_result.py] (~110 lines) - Tripartite Phase 1 atom evaluation DTOs: `ErrorDetailsDTO` (#L830-L833), `HydratedAtomDTO` (#L836-L844), `ExtractedValueDTO` (#L847-L850), `AtomResultDTO` (#L853-L917), `ExecutionMetricsDTO` (#L920-L925), `ExtensionMetricsDTO` (#L1676-L1686).
- `[MODIFY]` @[backend_v2/models/domain/synthesis.py] (~160 lines) - Tripartite Phase 2 synthesis models: Consolidates `MatrixSynthesisGroup` (#L1008-L1063), `RenderedSynthesisCache` (#L1689-L1719), `BaseMatrixXAI` (#L1820-L1828), `BaseTDAExtraction` (#L1831-L1876).
- `[MODIFY]` @[backend_v2/models/domain/output_profile.py] (~300 lines) - Tripartite Phase 3 presentation profile: Elevate from 10-line re-export stub to canonical `OutputProfile` domain model (#L1066-L1377), strictly preserving explicit block selectors (`variance_target_block`, `user_role_target_block`) adhering to `studio_driven_parameterization_mandate`.
- `[NEW]` @[backend_v2/models/domain/report_artifact.py] (~90 lines) - Tripartite Phase 3 report entity: Declare `ReportArtifact` domain entity with storage paths, metadata, and status (instead of polluting `v2_core.py`).
- `[NEW]` @[backend_v2/models/dtos/report_data.py] (~80 lines) - Tripartite Phase 3 SDUI envelope: Houses canonical `ReportDataDTO` (#L928-L1005).
- `[NEW]` @[backend_v2/models/domain/system_config.py] (~140 lines) - Platform & FinOps configurations: `ChatMessageDTO` (#L383-L394), `ChatHistoryDTO` (#L397-L406), `DataDictionaryField` (#L409-L417), `ProviderExtraParamsDTO` (#L420-L430), `ModelProfile` (#L433-L462), `SystemConfigModelRegistry` (#L465-L489), `AllowedMCPTool` (#L492-L502), `MCPAuditTrace` (#L505-L526), `SystemConfigMCPGateways` (#L529-L539).
- `[NEW]` @[backend_v2/models/dtos/report_artifact.py] - Declare strict Pydantic V2 DTOs: `ReportArtifactCreateDTO`, `ReportArtifactUpdateDTO`, `ReportArtifactSummaryDTO`, `ReportStoragePathsDTO`, `ReportRowItemDTO`, `PublicReportDTO`.
- `[MODIFY]` @[backend_v2/models/enums.py#L185-L198] - Declare `EntityPrefix.REPORT = "rep"` to guarantee canonical Opaque Stripe IDs (`rep_...`) for all `ReportArtifact` records across backend and database persistence.
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L487-L499] - Eradicate virtual rendering step injection (`sys_render_{profile_id}`).
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L39-L263] - Synchronize `OutputProfileCreateDTO` with decoupled fields.
- `[MODIFY]` @[backend_v2/models/dtos/output_profile.py#L266-L478] - Synchronize `OutputProfileUpdateDTO` with decoupled fields.
- `[MODIFY]` @[backend_v2/database/interfaces.py] - Declare `IReportArtifactRepository` CRUD contracts and mount onto `IUnifiedWorkflowRepository`.
- `[NEW]` @[backend_v2/database/repositories/report_artifact.py] - Implement `ReportArtifactRepositoryImpl` operating strictly against `report_artifacts` collection.
- `[MODIFY]` @[backend_v2/database/repository.py] - Mount `ReportArtifactRepositoryImpl` onto `UnifiedWorkflowRepository` facade.
- `[MODIFY]` @[backend_v2/api/dependencies.py] - Wire dependency providers `get_export_service` and `get_report_service`.
- `[NEW]` @[backend_v2/api/routers/execution/reports.py] - Create dedicated REST API router for report artifact CRUD and row data (`/api/v2/executions/{id}/reports`, `/api/v2/reports/{id}`, `/api/v2/reports/{id}/rows`).
- `[MODIFY]` @[backend_v2/api/routers/execution/executions.py] - Cleaned of report generation logic; mount `reports` sub-router and delegate render requests to `ReportService`.
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart] - Completely eradicate `allowedExports` from Dart Freezed model.
- `[NEW]` @[client_app_v2/lib/features/reports/models/report_artifact.dart] - Create Freezed model for `ReportArtifact` and `ReportArtifactSummary` (`@Freezed(equal: false)`).
- `[NEW]` @[client_app_v2/lib/features/reports/views/execution_reports_view.dart] - Desktop-class Pro Tool view managing execution reports adhering to @[ki_desktop_pro_tool_studio_ux.md].
- `[NEW]` @[client_app_v2/lib/features/reports/views/widgets/report_artifact_card.dart] - Adaptive Master selector card component for individual report artifacts.
- `[NEW]` @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart] - Pro Tool modal with Dual-Shield FormField architecture and dirty-check PopScope protocol.
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/new_execution_view.dart] - Add "Run until output" checkbox (`auto_generate_report`), profile selector binding, and automatic routing to reports.
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/execution_view.dart] - Provide seamless two-phase progress visualization ("Phase 1: Analysis" -> "Phase 2: Report generation") and direct transition to `ExecutionReportsView`.
- `[MODIFY]` @[backend_v2/tests/unit/test_worker.py] - Unit tests for decoupled worker lifecycle and failure isolation.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py] - Unit tests verifying zero database writes during report generation.
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution.py] - Unit tests verifying execution ingress without output profile.
- `[NEW]` @[backend_v2/tests/unit/services/test_report_service.py] - Unit tests for report artifact CRUD, file storage, row extraction, and regeneration.
- `[NEW]` @[backend_v2/tests/unit/api/test_reports_api.py] - Unit tests for report artifact REST API endpoints.
- `[NEW]` @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py] - AST-level import inspection and mock tests enforcing zero queue-level or in-process coupling between execution and report generation.
- `[MODIFY]` @[ki_tripartite_pipeline_architecture.md] - Synchronize Tripartite Pipeline KI with Phase 1 lifecycle sovereignty, failure isolation, ingress decoupling, read-only transformers, materialized report artifacts, and B2B row data.
- `[MODIFY]` @[ki_dual_axis_localization_architecture.md] - Document eradication of backend `.arb` reads and establish backend `I18nText` export SSOT.
- `[MODIFY]` @[ki_god_code_prevention.md] - Document CQRS export extraction from `ExecutionService` into `ExportService` and `ReportService`.
- `[MODIFY]` @[ki_desktop_pro_tool_studio_ux.md] - Document Adaptive Master Selector and Dual-Shield FormField integration for Execution Report Artifacts.
- `[MODIFY]` @[.agents/rules/04_directory_reference.md] - Register `backend_v2/services/export_service.py`, `backend_v2/services/report_service.py`, and `backend_v2/api/routers/execution/reports.py`.
- `[MODIFY]` @[docs/architecture/01_system_context_and_invariants.md] - Synchronize system invariants for Tripartite isolation, ingress decoupling, failure containment, and report artifacts via `/tier7-describe-architecture`.
- `[MODIFY]` @[docs/architecture/03_cognitive_orchestration_engine.md] - Synchronize worker lifecycle and execution status invariants via `/tier7-describe-architecture`.
- `[MODIFY]` @[docs/architecture/04_server_driven_ui_and_presentation.md] - Synchronize SDUI Dumb Painter read-only invariance, dynamic variance resolution, and report artifact CRUD via `/tier7-describe-architecture`.
- `[MODIFY]` @[docs/architecture/00_README_META_ARCHITECTURE.md] - Verify and synchronize meta-architecture overview.

### Context Files (Read-Only Architectural References)
- `[CONTEXT]` @[backend_v2/models/state.py] - State projector and trace event envelopes.
- `[CONTEXT]` @[backend_v2/models/enums.py] - `ExecutionStatus`, `TargetBlockType`, and `DisplayScale`.
- `[CONTEXT]` @[backend_v2/settings.py] - Central configuration SSOT.
- `[CONTEXT]` @[backend_v2/database/interfaces.py] - Repository interfaces.
- `[CONTEXT]` @[backend_v2/database/driver.py] - Storage driver interface (`StorageDriver`).
- `[CONTEXT]` @[backend_v2/services/flattener.py] - Flat file flattening service.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **@[backend_v2/models/v2_core.py#L121-L1876]**<br>Domain & DTO Decomposition | Monolithic 1,919-line God Model. Ghost field `Workflow.allowed_exports`. Unused legacy mappings. Naked dict typing. | Decomposed domain subpackage `backend_v2/models/domain/` (<350 lines per file). Strangler Fig facade in `v2_core.py` (<90 lines) with PEP 484 explicit re-exports (`__all__` and redundant aliases). `ConfigDict(strict=True, extra="forbid")` on all models. Explicit block selectors (`variance_target_block`, `user_role_target_block`) preserved. | Speculative compatibility wrappers or duplicate shadow models banned. One concept = One schema. | `test_v2_core_proxy.py` verifying all 43 symbols; AST test checking `v2_core.py` line count < 90 lines; `backend_audit_loop.py` strict typing. |
| **@[backend_v2/models/dtos/trace.py#L40-L57]**<br>`ExecutionCreateDTO` Boundary | Hardcoded required `output_profile_id: Annotated[str, Field(min_length=1)]` forcing profile coupling at calculation start. | `output_profile_id: Annotated[str | None, Field(default=None, description="Optional presentation profile identifier")] = None`. | Banned fake/dummy profile fallback instantiation or auto-creating shadow profiles. | Pydantic validation test with `output_profile_id=None`; AST inspection in `test_rest_only_pipeline_boundary.py`. |
| **@[backend_v2/services/execution.py#L401-L644]**<br>`ExecutionService.start_execution` & Decomposition | Mandatory profile resolution raising 400 if `profile_id` missing. Monolithic 1,510-line God Service mixing ingress, lifecycle, resumption, overrides, streaming, and export. | Ingress decoupling: `resolved_profile_id = payload.profile_id or workflow.default_profile_id` (allows `None`). Decomposition into `backend_v2/services/execution/` subpackage (6 micro-services, each <180 lines). Strangler Fig facade in `execution.py` (<80 lines). | Speculative middleware interceptors or synthetic default profiles pruned. | Unit test `test_start_execution_without_profile` passing `profile_id=None`; AST line count validation on all decomposed services. |
| **@[backend_v2/services/execution.py#L100-L156]**<br>`create_execution_record` Factory Invariant | Unvalidated reflection `# noqa: QGR012` using `isinstance(resolved_metadata, dict)` (#L136) and raw kwargs spreading `**extra_persistence_fields` (#L107, L134, L146). | Strict Pydantic validation via `TypeAdapter(ExecutionMetadata).validate_python(resolved_metadata)` and typed parameter enforcement with zero duck-typing or QGR suppressions. Explicit signature declaring `output_profile_id: str | None = None` and complete eradication of `**extra_persistence_fields: Any`. | Speculative metadata auto-wrapping layers or dictionary normalization helpers pruned. | AST guardrail `test_ast_guardrails.py` verifying zero QGR suppressions and strict model instantiation. |
| **@[backend_v2/services/orchestrator/dag_executor.py#L487-L499]**<br>`DAGExecutor.execute_workflow` | Synthetic virtual step injection `sys_render_{profile_id}` with dummy label `"system.virtual.rendering"` and hardcoded `output_profile_id` requirement. | Absolute removal of `sys_render_*` step injection from `steps` and `step_states`. Pure analytical DAG evaluation pipeline. DAG executor operates purely on workflow steps. | Pruned virtual step state mapping, synthetic execution steps, and post-DAG render flags. | Unit test verifying `exec_record.steps` contains zero `sys_render_*` steps; AST guardrail in `test_execution_worker.py`. |
| **@[backend_v2/worker.py#L139-L566]**<br>& **[NEW] @[backend_v2/workers/execution_worker.py]**<br>Phase 1 Execution Worker | Automatic queuing of `render_profile_job` upon DAG completion. Setting status to RUNNING to wait for PDF rendering. `v_step_id = f"sys_render_{profile_id}"` step mutation. Monolithic 2,036-line God Worker. | Transition directly to `ExecutionStatus.PASSED` upon topological scoring and telemetry completion. Zero background worker auto-enqueuing of report jobs. Extraction to `backend_v2/workers/execution_worker.py` (<400 lines). Thin facade `worker.py` (<150 lines). | Pruned worker-to-worker auto-triggers and intermediate `RUNNING` status hacks. | `test_execution_worker.py` asserting `status == PASSED` and 0 jobs enqueued in Redis; AST boundary test in `test_rest_only_pipeline_boundary.py`. |
| **@[backend_v2/worker.py#L569-L1937]**<br>& **[NEW] @[backend_v2/workers/report_worker.py]**<br>Phase 2/3 Report Worker | PDF/synthesis errors mutating `ExecutionRecord.status = ExecutionStatus.FAILED`. Overwriting Phase 1 analytical score with presentation failure. Loose exception catching with string formatting. | Presentation failure isolation: synthesis or WeasyPrint errors update ONLY `ReportArtifact.status = ReportStatus.FAILED`. `ExecutionRecord.status` remains `PASSED`. Extracted to `report_worker.py` (<450 lines) with RFC 7807 structured logging. | Pruned cross-entity error cascade logic and recursive failure updates. | Unit test in `test_report_worker.py` injecting WeasyPrint crash and asserting `execution.status == PASSED` and `report.status == FAILED`. |
| **@[backend_v2/services/blueprint.py#L62-L588]**<br>`BlueprintTransformer` | Presentation transformer mutating DB via `await self.exec_repo.update_execution(execution.id, ExecutionUpdateDTO(step_states=new_step_states))` (#L360). Recursive dict traversal in `extract_evidence_ids` (#L461-L477). Loose dictionary scraping. | 100% Read-Only Dumb Painter. Delete DB write completely. Typed extraction of MCP evidence from `MCPAuditTrace` and `AtomResultDTO.used_evidence_ids`. Deterministic variance validation anchored to `OutputProfile.variance_target_block`. | Pruned repository write access in `BlueprintTransformer`. Transformer takes snapshot and outputs pure `ReportDataDTO`. | `test_blueprint_read_only.py` asserting `exec_repo.update_execution` call count is 0; test variance block rendering adhering to explicit block selector. |
| **[NEW] @[backend_v2/services/export_service.py]**<br>& **@[backend_v2/services/execution.py#L801-L1004]**<br>CQRS Export Extraction | Backend opening frontend `.arb` files via `open("client_app_v2/lib/l10n/app_{locale}.arb")` (`#L850-L855`). Export logic embedded in `ExecutionService`. | Dedicated `ExportService` (<150 lines) using backend `I18nText` database SSOT and static localization tables. Multi-tab Excel ('Summary' and 'Raw Data') and flat CSV generation. | Pruned cross-repository file-system reads and frontend localization coupling. | Unit test `test_export_service.py` asserting no file handles to `.arb` files; verifies 2-tab Excel output bytes. |
| **[NEW] @[backend_v2/database/repositories/report_artifact.py]**<br>& **[NEW] @[backend_v2/models/domain/report_artifact.py]**<br>Materialized Report Artifact CRUD | Packing PDF paths, SDUI blobs, and export paths into `ExecutionRecord` root document. Single report per execution limitation. | First-class `ReportArtifact` domain entity with storage paths (`report.pdf`, `report.sdui.json`, `report.xlsx`, `report.csv`), lifecycle status (`PENDING`, `GENERATING`, `READY`, `FAILED`), and dedicated repository `ReportArtifactRepositoryImpl` operating on `report_artifacts`. | Pruned monolithic execution record inflation. Heavy files offloaded to `StorageDriver`. | Unit test `test_report_artifact_repository.py` verifying CRUD operations, foreign key isolation, and storage cleanup. |
| **[NEW] @[backend_v2/api/routers/execution/reports.py]**<br>REST-API-Only Boundary Router | Implicit in-process chaining or worker auto-queuing. Calculate and report coupled in single HTTP transaction. | Sovereign REST API router: `POST /api/v2/executions/{id}/reports` is the EXCLUSIVE trigger for report generation. Enforces `execution.status == PASSED` (raising 409 Conflict if not ready). Complete CRUD endpoints (`/reports/{id}`, `/reports/{id}/sdui`, `/reports/{id}/pdf`, `/reports/{id}/excel`, `/reports/{id}/rows`). | Pruned backdoor worker auto-triggers and in-process execution chaining. | `test_rest_only_pipeline_boundary.py` AST inspection and 409 conflict test; `test_reports_api.py` endpoint integration suite. |
| **[NEW] @[client_app_v2/lib/features/reports/]**<br>& **@[client_app_v2/lib/features/execution/views/execution_view.dart]**<br>Desktop Pro Tool Studio UX | Unbounded vertical stacking. Mixing live DAG tracking with finished report viewing. Using SnackBar inside modals. Naive `!=` equality dirty checks on `@Freezed(equal: false)` models causing false-positive discard loops. Un-debounced double-click save triggers. Uncontained horizontal row text. Raw widgets outside `AppErrorBoundary`. | `ExecutionReportsView` adhering to @[ki_desktop_pro_tool_studio_ux.md]: Adaptive Master Selector (wide >=900px lateral 260px sidebar with `ListView.builder` virtualization vs compact <900px top-bar chips). Single Cognitive Unit. Progressive Disclosure (4 tabs). Wide canvas containment (`maxWidth: 1200px`). `CreateReportDialog` with Dual-Shield FormField, `PopScope` dismissal, serialization-based dirty checking (`jsonEncode`), Post-Frame blur flush (`addPostFrameCallback`), Modal-Internal Error Surface (Absolute SnackBar Ban), auto-scroll to invalid input (`Scrollable.ensureVisible`), save debounce (`_isSaving = false`), and `isExpanded: true` on dropdowns. All detail canvases wrapped in `AppErrorBoundary`. | Pruned monolithic multi-report stacked views, brittle ad-hoc tab controllers, and background SnackBar rendering. | Widget tests verifying lateral layout at 1200px width, top-bar chips at 800px width, `AppErrorBoundary` coverage, `PopScope` serialization dirty check without false positives, save debounce, and zero `RenderFlex` warnings under Finnish locale down to 360px. |
| **@[client_app_v2/lib/features/studio/models/workflow.dart#L169-L171]**<br>& **@[backend_v2/models/dtos/studio.py#L95-L128, #L598]**<br>& **@[backend_v2/services/studio/workflow_service.py#L319]**<br>& **@[backend_v2/seed/seed_data.json]**<br>& **[NEW] @[backend_v2/models/domain/workflow.py]**<br>Ghost Field Purge | Dead-weight field `allowed_exports` / `allowedExports` in model, draft factory, seed vault (6 workflows), and DTOs. | Complete eradication from Python `Workflow`, `WorkflowCreateDTO`, `WorkflowUpdateDTO`, `seed_data.json`, `workflow_service.py#L319`, `model_factories.py#L45`, and Dart `Workflow` Freezed model. Zero replacement needed. | Pruned dead schema weight and redundant serialization fields. | Pytest model validation, `seed_data.json` preflight seeding (`run_seed.py local`), and Dart `flutter gen-l10n` / Freezed build runner compilation. |
| **[NEW] @[backend_v2/models/domain/system_config.py]**<br>& **[NEW] @[backend_v2/models/domain/step.py]**<br>& **[NEW] @[backend_v2/workers/report_worker.py]**<br>Model Stack & Cognitive Tier Invariant Preservation | Reverting flat `tier_definitions` to nested maps, re-introducing merged `"google"` pseudo-provider, reviving heuristic `startswith` string matching, hardcoding default registry IDs (`sys_e26807f3bfa3454d`), or hardcoding legacy string strategies (`"synthesis"`, `"fast"`). | 100% preservation of: 1) `SystemConfigModelRegistry` flat mapping `tier_definitions: dict[CognitiveTier, ModelProfile]` with `validate_tier_completeness()`, 2) `Step.cognitive_tier: CognitiveTier` and `validate_step_consistency()`, 3) `Workflow.model_registry_id` dynamic DB binding, 4) `ExecutionMetadata.model_registry_id` and `provider_override`, 5) `LLMClient.from_tier()` resolution in `report_worker.py` and `ReportService` using execution metadata parameters. | Pruned speculative multi-provider fallback loaders and dynamic tier synthesis shims. Single sovereign 4-tier stack per registry. | `test_google_providers_separation.py`, `test_model_registry_discovery.py`, and `test_llm_client_tiers.py` run in quality gate and pass 100%. |
| **@[backend_v2/models/enums.py#L185-L198]**<br>Canonical Opaque Stripe ID Taxonomy | Arbitrary prefix strings (`"report_"`, `"rpt_"`) or ad-hoc UUID generation for report artifacts bypassing canonical taxonomy. | Strict enumeration `EntityPrefix.REPORT = "rep"` bound to `generate_opaque_id(EntityPrefix.REPORT)`. Enforces regex `pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"` on `ReportArtifact.id`. | Pruned custom ID generator wrappers or ad-hoc prefix dictionaries. | `test_core_base.py` asserting `EntityPrefix.REPORT` passes `OPAQUE_STRIPE_ID_REGEX` roundtrip validation. |
| **@[backend_v2/services/execution.py#L347-L399]**<br>& **[NEW] @[backend_v2/services/report_service.py]**<br>Execution Cascade Deletion & Storage Cleanup | Orphaned physical disk/object storage files (`report.pdf`, `report.sdui.json`) and orphaned database records remaining after parent execution record deletion. | Deterministic cascade cleanup: `delete_execution` queries all associated reports via `list_report_artifacts_by_execution(execution_id)` and deletes both DB records and physical files via `report_service.delete_report_artifact(rep.id)` before deleting the execution record. | Pruned asynchronous garbage collection daemons or orphan scavenger sweeps. | Unit test in `test_lifecycle_service.py` asserting zero orphan records or storage files remain on disk post-deletion. |
| **[NEW] @[backend_v2/services/report_service.py]**<br>& **[NEW] @[backend_v2/api/routers/execution/reports.py]**<br>Idempotency & Concurrent Generation Shield | Race conditions from rapid duplicate report requests causing parallel worker compiles to write concurrently to the same storage paths (`artifacts/reports/{id}/report.pdf`). | Idempotency guard: Each compilation request issues a unique report ID (`rep_...`); on re-generation requests (`POST /reports/{id}/regenerate`), if status is already `GENERATING`, service raises HTTP 409 Conflict (`ErrorCodes.RESOURCE_CONFLICT`), rejecting concurrent compilation. | Pruned distributed locks or complex mutex state machines. Pure status-based state machine guard. | Unit test asserting HTTP 409 Conflict on duplicate simultaneous generation trigger. |

---

## Pre-Implementation Technical Debt Cleanups (Scoped Boy Scout)

1. **[ACTIVE DEBT - TARGET] Eradicate Database Write in Blueprint Transformer**:
   In @[backend_v2/services/blueprint.py#L360], `BlueprintTransformer.build_report_dto` executes `await self.exec_repo.update_execution(execution.id, ExecutionUpdateDTO(step_states=new_step_states))`. This violates the Dumb Painter invariant and presentation read-only guarantee. Must be completely removed.
2. **[ACTIVE DEBT - TARGET] Eradicate Recursive Sanity Traversal & Dict Duck-Typing in Blueprint Transformer**:
   In @[backend_v2/services/blueprint.py#L161-L475], eradicate all 12 occurrences of `isinstance(..., dict)` and 8 occurrences of `# noqa: QGR012 [REASON: Polymorphic DAG payload validation]`, replacing them with structured typed extraction from `AtomResultDTO` and `MCPAuditTrace`.
3. **[ACTIVE DEBT - TARGET] Eradicate Direct Frontend `.arb` Reading in Execution Export**:
   In @[backend_v2/services/execution.py#L850-L855], backend code reads `client_app_v2/lib/l10n/app_{locale}.arb` using `open()`. This violates the Dual-Axis Localization boundary. Must be extracted into `ExportService` resolving headers strictly from backend `I18nText` or static Python tables.
4. **[ACTIVE DEBT - TARGET] Purge Dead-Weight Ghost Field `allowed_exports` Across Code, Seed Vault, and DTOs**:
   Eradicate `allowed_exports` / `allowedExports` across all touched boundaries:
   - Python domain: `Workflow.allowed_exports` in @[backend_v2/models/domain/workflow.py]
   - Python DTOs: `_default_allowed_exports` (#L95-L96), `WorkflowCreateDTO.allowed_exports` (#L125-L128), and `WorkflowUpdateDTO.allowed_exports` (#L598) in @[backend_v2/models/dtos/studio.py]
   - Studio service: `workflow_service.py#L319` (`allowed_exports=["pdf"]`)
   - Test factory: `model_factories.py#L45` (`allowed_exports`)
   - Seed Vault: 6 workflow records in @[backend_v2/seed/seed_data.json#L18578,L18753,L19013,L19257,L19474,L19693] (`wf_9d68c573802341db`, `wf_01a1d71000000001`, `wf_02a1d71000000002`, `wf_03a1d71000000003`, `wf_04a1d71000000004`, `wf_05a1d71000000005`)
   - Flutter domain: `Workflow.allowedExports` in @[client_app_v2/lib/features/studio/models/workflow.dart#L170]
   - Test fixtures: Cleanse ~50+ occurrences across test suites (e.g. `test_blueprint.py#L179-L3162`).
5. **[ACTIVE DEBT - TARGET] Eradicate Synthetic Step Injection in DAG Executor**:
   In @[backend_v2/services/orchestrator/dag_executor.py#L487-L499], `DAGExecutor` injects `v_step_id = f"sys_render_{exec_record.output_profile_id}"` into `steps` and `step_states`. This must be removed completely. Phase 1 DAG executor must only execute and track workflow steps defined in the workflow definition.
6. **[ACTIVE DEBT - TARGET] Eradicate Synthetic Virtual Step Resumption Exceptions**:
   In @[backend_v2/services/execution.py#L680-L685] and @[backend_v2/tests/unit/services/test_execution_resumability.py#L85-L125], remove custom filtering (`k.startswith("sys_")`) and test hacks that exist solely to tolerate virtual `sys_render_*` steps during resumption validation.
7. **[ACTIVE DEBT - TARGET] Eradicate Reflection, Duck-Typing and QGR012 in Factory and Resumption**:
   In @[backend_v2/services/execution.py#L108-L144], eradicate `**extra_persistence_fields: Any` from `create_execution_record`. Enforce strict Pydantic V2 validation with zero duck-typing or QGR suppressions. Cleanse duck-typing from `check_resumability` (#L690-L696).
8. **[ACTIVE DEBT - TARGET] Eradicate Loose Dictionary Signatures and Catch-All Handlers in Background Workers**:
   In @[backend_v2/worker.py#L460-L484] and worker task definitions, eradicate worker auto-enqueue of `render_profile_job` from `execute_workflow_job`, eliminate `status=ExecutionStatus.RUNNING` wait hacks (#L462), and eliminate loose `inputs: dict[str, Any]` argument transit in favor of typed `ExecutionInputsDTO`. Replace generic multi-type exception handling with typed `AppException` mapping and RFC 7807 structured errors with explicit `ErrorCodes`.
9. **[ACTIVE TARGET] Preserve Explicit Prompt Block Selectors in Output Profile DTOs**:
   In @[backend_v2/models/dtos/output_profile.py#L39-L263] and @[backend_v2/models/dtos/output_profile.py#L266-L478], strictly preserve `variance_target_block` and `user_role_target_block` with strict typed Pydantic V2 validation in compliance with `ban_heuristic_identifier_matching` and `studio_driven_parameterization_mandate`, ensuring zero heuristic string guessing or identifier matching.
10. **[ACTIVE TARGET] Enforce Complete 16-Pillar Desktop Pro Tool UX, Modal Dismissal Protocol & AppErrorBoundary Architecture**:
    Across ALL Flutter windows, dialogs, cards, and views (`ExecutionReportsView`, `CreateReportDialog`, `ReportArtifactCard`, `NewExecutionView`, `ExecutionView`), **`@[ki_desktop_pro_tool_studio_ux.md]` MUST be read first as mandatory pre-execution contract**. The implementation MUST enforce: 1) Adaptive Master Selector Standard (`LayoutBuilder` wide >=900px lateral 260px sidebar with `ListView.builder` virtualization vs compact <900px top-bar horizontal chips), 2) Single Cognitive Unit Isolation (exactly ONE report displayed at a time, banning unbounded vertical stacking), 3) State Retention Invariance across window resizes, 4) Modal window bounds (`ConstrainedBox(minWidth: 480, maxWidth: 800, minHeight: 400, maxHeight: 720)` for dialogs, `maxWidth: 1200px` for detail bodies), 5) Dual-Shield FormField Architecture with modern `PopScope(canPop: false, onPopInvokedWithResult: ...)` routing to unified `_handleDismiss()` (direct `Navigator.pop()` strictly banned), 6) Post-Frame Blur Flush (`FocusScope.of(context).unfocus()` synchronously followed by dirty check inside `WidgetsBinding.instance.addPostFrameCallback((_) { if (!mounted) return; ... })`), 7) Serialization-Based Model Dirty Checking (`jsonEncode(_editableModel.toJson()) != _initialModelJson` banning naive `!=` on `@Freezed(equal: false)`), 8) Localized Discard Confirmation (`AlertDialog` with focus preservation on cancel), 9) Modal-Internal Error Surface (Absolute SnackBar Ban: all errors rendered inline on canvas, `ScaffoldMessenger.showSnackBar` strictly prohibited inside dialogs), 10) Auto-Scroll to First Invalid Field via `Scrollable.ensureVisible`, 11) Atomic In-Flight Submission Guard (`bool _isSaving = false;` debounce), 12) Keyboard-First Desktop Interaction (`Ctrl + S` / `Cmd + S`, `Esc`, `SystemMouseCursors.click`, `FocusTraversalGroup`), 13) Anti-Stringification Input Architecture (discrete tokenized chips, delimiter splitting banned), 14) Scalable List Browsing & Virtualization Standard (`ListView.builder`, `prototypeItem`, sticky header with count badge `X / Y raporttia`, instant search field with `Icons.clear` for >10 items, compact vertical density ~72-88px), 15) Universal Horizontal Overflow Immunity (all titles in `Row` wrapped in `Expanded(child: Text(..., overflow: TextOverflow.ellipsis))`, all dropdowns specify `isExpanded: true`, hazard-stripe-free down to 360px), and 16) `AppErrorBoundary` wrapping on every detail canvas and dialog body alongside 100% Axis 1 compile-time `.arb` localization parity (`AppLocalizations.of(context)!`).
11. **[ACTIVE TARGET] Eradicate Broad Exception Handlers in Execution Service and Worker**:
    Replace silent or untyped `except Exception as e:` blocks across `backend_v2/services/execution.py` and `backend_v2/worker.py` with specific, typed exceptions (`AppException`, `ValidationError`, `OSError`, `RedisError`) and structured RFC 7807 error logging (`logger.error(..., extra={"error_code": ...})`).
12. **[ACTIVE TARGET] Audit and Validate `model_copy(update=...)` Mutations**:
    Audit and eradicate unvalidated `model_copy(update=...)` calls in `backend_v2/services/execution.py` (specifically: `is_resumable` calculation and execution state mutations) to ensure state transitions pass through strict Pydantic V2 validation without field smuggling.
13. **[ACTIVE TARGET] Decouple Ingress Profile Requirements in Domain and DTO Contracts**:
    Update `ExecutionRecord.output_profile_id` and `Workflow.default_profile_id` from required strings (`Annotated[str, Field(min_length=1)]`) to optional strings (`Annotated[str | None, Field(default=None)] = None`) in domain models and DTOs to enforce complete phase decoupling from the first line of code.
14. **[ACTIVE TARGET] Add EntityPrefix.REPORT to Canonical Taxonomy**:
    In @[backend_v2/models/enums.py#L185-L198], declare `REPORT = "rep"` to enforce strict Opaque Stripe ID generation (`generate_opaque_id(EntityPrefix.REPORT)`) and ban arbitrary prefix strings.
15. **[ACTIVE TARGET] Enforce Execution Cascade Deletion Storage Cleanup**:
    In @[backend_v2/services/execution.py#L347-L399] and decomposed `lifecycle_service.py`, ensure `delete_execution` queries all associated `ReportArtifact` records via `list_report_artifacts_by_execution` and deletes both database records and physical files on disk/storage before deleting the execution record.
16. **[ACTIVE TARGET] Idempotency & Concurrent Generation Guard**:
    In @[backend_v2/services/report_service.py] and @[backend_v2/api/routers/execution/reports.py], enforce state check on regeneration and creation: if a report artifact for the target execution and profile is currently in `GENERATING` status, reject concurrent generation with HTTP 409 Conflict (`ErrorCodes.RESOURCE_CONFLICT`), preventing race conditions on disk writes.
17. **[ACTIVE DEBT - TARGET] Fix Test Fixtures Missing `model_registry_id` and Passing `allowed_exports` in `test_blueprint.py`**:
    In @[backend_v2/tests/unit/services/test_blueprint.py#L3024] and @[backend_v2/tests/unit/services/test_blueprint.py#L3162], `Workflow(...)` fixtures lack `model_registry_id="cfg_model_registry_01"` causing 2 validation failures, and pass dead `allowed_exports=["pdf"]`. Add `model_registry_id="cfg_model_registry_01"` and remove `allowed_exports`.
18. **[ACTIVE DEBT - TARGET] Eradicate Duck-Typing `.get("tda_id")` in `override_atom`**:
    In @[backend_v2/services/execution.py#L1117], `target_atom.metadata.get("tda_id")` duck-types dictionary access on `metadata`. Replace with typed extraction against `AtomResultDTO.metadata` or typed DTO fields.
19. **[ACTIVE DEBT - TARGET] Implement Strict Enum Adapter `ReportStatus.l10n_key` (ki_dual_axis_localization_architecture.md)**:
    In @[backend_v2/models/enums.py], declare `ReportStatus` with `@property def l10n_key(self) -> str:` mapping `PENDING -> reportStatusPending`, `GENERATING -> reportStatusGenerating`, `READY -> reportStatusReady`, `FAILED -> reportStatusFailed`. Banning runtime string manipulation (`split('_')`, `.lower()`) in compliance with `strict_enum_l10n_adapter`.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS_CORE_MODEL_DECOMPOSITION_AND_DTO_LOCK">
    <action>Modify @[backend_v2/models/dtos/trace.py#L40-L57] to make output_profile_id optional:
      - Change output_profile_id to Annotated[str | None, Field(default=None, description="Optional presentation profile identifier")].
      - Ensure ConfigDict(strict=True, extra="forbid") is preserved.
    </action>
    <action>Decompose monolithic @[backend_v2/models/v2_core.py] (1,919 actual physical lines) into cohesive domain models under backend_v2/models/domain/ and backend_v2/models/dtos/. To prevent Context Amnesia during the 43-symbol extraction, execute strictly in 7 atomic sub-batches, verifying each with `uv run python scripts/backend_audit_loop.py backend_v2 --test` before proceeding:
      - Sub-batch 1: Create [NEW] @[backend_v2/models/domain/matrix.py] (~260 lines) as a leaf dependency: Extract TheoryGrounding, AcceptanceCriterion, AntiPattern, ContrastivePairDTO, TDAAssertion, MatrixClaim, MatrixRow, MatrixScale (#L121-L380).
      - Sub-batch 2: Create [NEW] @[backend_v2/models/domain/system_config.py] (~160 lines) for platform models: Extract ChatMessageDTO, ChatHistoryDTO, DataDictionaryField, ProviderExtraParamsDTO, ModelProfile, SystemConfigModelRegistry, AllowedMCPTool, MCPAuditTrace, SystemConfigMCPGateways (#L383-L539). Preserves Option A Sovereign Model Stack contracts: SystemConfigModelRegistry.name, default_provider (defaulting to LLMProvider.AI_STUDIO), flat tier_definitions: Annotated[dict[LaxCognitiveTier, ModelProfile], ...], and validate_tier_completeness() enforcing 4 canonical tiers.
      - Sub-batch 3: Create [NEW] @[backend_v2/models/domain/step.py] (~260 lines): Extract Step, StepRule, Role, QuestionnaireItem, ExpectedInput (#L542-L815). Preserves cognitive_tier: CognitiveTier and validate_step_consistency() (banning legacy string model_strategy).
      - Sub-batch 4: Create [NEW] @[backend_v2/models/domain/workflow.py] (~160 lines): Extract Workflow (#L1380-L1545). Completely purge allowed_exports (#L1459-L1462). Make default_profile_id optional (Annotated[str | None, Field(default=None)]). Preserves dynamic model_registry_id (pattern=r"^(sys_[a-fA-F0-9]{16,32}|cfg_model_registry_\d{2})$", zero code-level default ID), default_strictness_level=50, and security/passivity penalties. Concurrently:
        * Delete allowedExports completely from Workflow in @[client_app_v2/lib/features/studio/models/workflow.dart#L169-L171].
        * Delete _default_allowed_exports (#L95-L96), WorkflowCreateDTO.allowed_exports (#L125-L128), and WorkflowUpdateDTO.allowed_exports (#L598) in @[backend_v2/models/dtos/studio.py].
        * Purge allowed_exports=["pdf"] from create_draft in @[backend_v2/services/studio/workflow_service.py#L319].
        * Purge allowed_exports parameter from create_workflow in @[backend_v2/tests/factories/model_factories.py#L45].
        * Purge allowed_exports from the 6 workflow entries in @[backend_v2/seed/seed_data.json] following 03_seed_vault.md protocol with backup, run in-memory preflight validation (uv run python backend_v2/seed/run_seed.py local --dry-run), and synchronize local database (uv run python backend_v2/seed/run_seed.py local).
      - Sub-batch 5: Create [NEW] @[backend_v2/models/domain/execution.py] (~250 lines): Extract FrozenContext (#L1548), ExecutionCreate (#L1564), ExecutionStep (#L1608), ExecutionSummarySnapshot (#L1649), EvaluatedMatrixContextDTO (#L1662), ExecutionRecord (#L1722), JobAcceptedDTO (#L1799), EvidenceRejectionRequest (#L1809). Preserves ExecutionCreate.provider_override (LLMProvider | None) and ExecutionCreate.model_registry_id (str | None).
      - Sub-batch 6: Create remaining DTOs and presentation models:
        * Create [NEW] @[backend_v2/models/dtos/atom_result.py] (~110 lines): Extract ErrorDetailsDTO (#L830), HydratedAtomDTO (#L836), ExtractedValueDTO (#L847), AtomResultDTO (#L853), ExecutionMetricsDTO (#L920), ExtensionMetricsDTO (#L1676).
        * Modify @[backend_v2/models/domain/synthesis.py] (~160 lines): Consolidate MatrixSynthesisGroup (#L1008-L1063), RenderedSynthesisCache (#L1689-L1719), BaseMatrixXAI (#L1820-L1828), BaseTDAExtraction (#L1831-L1876).
        * Modify @[backend_v2/models/domain/output_profile.py] (~300 lines): Elevate from 10-line stub to canonical OutputProfile domain model (#L1066-L1377). Strictly preserve explicit Studio UI selectors `variance_target_block` and `user_role_target_block` with strict Pydantic validation adhering to `studio_driven_parameterization_mandate` and `ban_heuristic_identifier_matching`.
        * Synchronize @[backend_v2/models/dtos/output_profile.py#L39-L263] and @[backend_v2/models/dtos/output_profile.py#L266-L478]: Maintain strict typed validation for `variance_target_block` and `user_role_target_block` on OutputProfileCreateDTO and OutputProfileUpdateDTO.
        * Create [NEW] @[backend_v2/models/dtos/report_data.py] (~80 lines): Extract ReportDataDTO (#L928-L1005).
      - Sub-batch 7: Refactor @[backend_v2/models/v2_core.py] into a thin Strangler Fig Facade (<90 lines): Re-exports all 43 public symbols with explicit __all__ = [...] and redundant aliases (specifically: from backend_v2.models.domain.workflow import Workflow as Workflow) to satisfy PEP 484 and mypy --strict.
    </action>
    <constraint invariant="zero_permissive_typing">
      DTO models must enforce ConfigDict(strict=True, extra="forbid"). No naked dictionaries, legacy ghost fields, or loose optional bypasses.
    </constraint>
    <constraint invariant="god_code_prevention">
      Every decomposed domain model file is strictly under 350 lines adhering to ki_god_code_prevention.md. Root v2_core.py is a thin Strangler Fig facade under 90 lines.
    </constraint>
  </step>

  <step id="2" name="INGRESS_DECOUPLING_IN_EXECUTION_SERVICE">
    <action>Modify @[backend_v2/services/execution.py#L401-L644] in start_execution:
      - Remove the fail-fast exception that halts execution if workflow.default_profile_id and payload.profile_id are absent.
      - If payload.profile_id is provided, resolve and validate it against repository. If absent, fallback to workflow.default_profile_id if present; otherwise resolve to None.
      - If resolved_profile_id is None, skip profile validation and create ExecutionCreateDTO with output_profile_id=None.
      - Ensure initial ExecutionRecord creates cleanly without requiring an OutputProfile instance when profile is None.
      - Maintain dynamic model registry resolution: resolved_registry_id = payload.model_registry_id or workflow.model_registry_id. Validate resolved_registry_id strictly against system repository (get_model_registry(resolved_registry_id)), raising AppException with ErrorCodes.RESOURCE_NOT_FOUND if missing or non-existent.
      - Maintain provider_override=payload.provider_override and model_registry_id=resolved_registry_id in ExecutionMetadata.
    </action>
    <action>Modify @[backend_v2/services/orchestrator/dag_executor.py#L487-L499]:
      - Delete lines injecting v_step_id = f"sys_render_{exec_record.output_profile_id}" or f"sys_render_{workflow.default_profile_id}".
      - Pass output_profile_id=exec_record.output_profile_id directly to create_execution_record without injecting virtual rendering steps into steps or step_states.
      - Ensure DAG execution continues to instantiate StrategyContext strictly with cognitive_tier=step_def.cognitive_tier.
    </action>
    <action>Execute /tier5-session-handover to checkpoint Phase A completion and transition cleanly to Phase B, preventing context amnesia before worker and service extraction.</action>
    <constraint invariant="universal_fail_fast">
      If a specific profile_id is explicitly provided by the caller but not found in the database, raise AppException with ErrorCodes.RESOURCE_NOT_FOUND. Do NOT fall back silently.
    </constraint>
  </step>

  <step id="3" name="WORKER_DECOMPOSITION_AND_LIFECYCLE_ISOLATION">
    <action>Execute Golden Master characterization test to record baseline test coverage before worker decomposition per @[ki_god_code_prevention.md]: uv run pytest backend_v2/tests/ --cov=backend_v2.worker --cov-report=term-missing</action>
    <action>Execute AST boundary analysis on @[backend_v2/worker.py] (2,036 actual lines) via scripts/_ast_boundary_utils.py to verify exact physical node bounds of execute_workflow_job, generate_pdf_job, generate_pdf_task, render_profile_job, and generate_profile_synthesis_and_pdf_task.</action>
    <action>Create [NEW] subpackage @[backend_v2/workers/__init__.py] with public worker exports.</action>
    <action>Create [NEW] file @[backend_v2/workers/execution_worker.py] (<400 lines):
      - Extract execute_workflow_job from worker.py lines 139–566.
      - Upon completion of DAG execution and topological scoring, calculate duration_ms and finalize telemetry metrics (prompt_tokens, completion_tokens, cached_tokens, reasoning_tokens, cost_estimate, models_used).
      - Set execution status directly: update_dto = ExecutionUpdateDTO(status=ExecutionStatus.PASSED, completed_at=datetime.now(UTC), ...).
      - Delete lines injecting v_step_id = f"sys_render_{profile_id}" and label="Generating Output Report" into updated_exec_record.steps and step_states.
      - Eradicate worker-to-worker auto-enqueuing: execute_workflow_job MUST NEVER enqueue render_profile_job or generate_report_artifact_job. It purely sets status=ExecutionStatus.PASSED, updates the execution record in the repository, publishes the execution_status_changed event to Redis pubsub/SSE, and immediately terminates.
      - Enforce Zero-Import Boundary: execute_workflow_job contains 0 imports and 0 calls referencing ReportService, export_service, or report queue tasks.
      - Persist ExecutionStatus.PASSED immediately. The execution is finished from Phase 1 perspective.
    </action>
    <action>Create [NEW] file @[backend_v2/workers/report_worker.py] (<450 lines):
      - Extract generate_pdf_job, generate_pdf_task, render_profile_job, and generate_profile_synthesis_and_pdf_task from worker.py lines 569–1937.
      - Register generate_report_artifact_job(ctx, report_id: str) delegating directly to report_service.process_artifact_compilation.
      - Maintain sovereign cognitive tier resolution for synthesis tasks:
        1. Executive summary synthesis: Invoke LLMClient.from_tier(CognitiveTier.BALANCED, repository=repo, provider=execution.metadata.provider_override, registry_id=execution.metadata.model_registry_id).
        2. Row explanation synthesis: Invoke LLMClient.from_tier(CognitiveTier.FAST, repository=repo, provider=execution.metadata.provider_override, registry_id=execution.metadata.model_registry_id).
        3. Variance synthesis: Invoke LLMClient.from_tier(CognitiveTier.DEEP, repository=repo, provider=execution.metadata.provider_override, registry_id=execution.metadata.model_registry_id).
      - Eradicate all legacy string strategies ("synthesis", "strict", "fast") and ensure provider routing supports sovereign "vertex_ai" and "ai_studio" without merged "google" shims.
      - In generate_pdf_task and profile synthesis error handling, quarantine failures: log error with ErrorCodes.PDF_GENERATION_FAILED, update only ReportArtifact.status=ReportStatus.FAILED, and delete the database update that stamped ExecutionRecord.status = ExecutionStatus.FAILED.
    </action>
    <action>Refactor @[backend_v2/worker.py] into a thin Strangler Fig Facade & Entrypoint (<150 lines):
      - Retain Arq lifecycle functions: startup (#L1943-L1994), shutdown (#L1997-L2003), health_check (#L2006-L2015), and WorkerSettings (#L2018-L2036).
      - Import execute_workflow_job from backend_v2.workers.execution_worker.
      - Import generate_report_artifact_job, generate_pdf_job, generate_pdf_task, render_profile_job, generate_profile_synthesis_and_pdf_task from backend_v2.workers.report_worker.
      - Enforce PEP 484 and MyPy Strict explicit re-exports: declare __all__ = ["execute_workflow_job", "generate_report_artifact_job", "generate_pdf_job", "generate_pdf_task", "render_profile_job", "generate_profile_synthesis_and_pdf_task", "WorkerSettings", "startup", "shutdown", "health_check"] and redundant aliases (from ... import func as func).
    </action>
    <action>Execute Arq Worker smoke test after extraction to verify task registration survives extraction: uv run python -c "from backend_v2.worker import WorkerSettings; print([f.name for f in WorkerSettings.functions])"</action>
    <constraint invariant="tripartite_phase_isolation">
      Phase 3 rendering failures MUST NEVER mutate Phase 1 ExecutionRecord.status to FAILED. An analytical run remains PASSED once DAG evaluations succeed.
    </constraint>
    <constraint invariant="god_code_prevention">
      No worker file may exceed 500 lines. The root worker.py acts purely as an Arq entry point and migration re-export facade under 150 lines.
    </constraint>
  </step>

  <step id="4" name="MAKE_BLUEPRINT_TRANSFORMER_READ_ONLY">
    <action>Modify @[backend_v2/services/blueprint.py#L62-L588]:
      - Delete lines where new_step_states are updated and exec_repo.update_execution is invoked (#L345-L360).
      - Remove self.exec_repo write access from build_report_dto. The transformer must only read execution data.
      - Replace extract_evidence_ids (#L461-L477) recursive dictionary search and isinstance(payload_data, dict) with direct iteration over structured mcp_audit_data items and AtomResultDTO used_evidence_ids.
      - Replace token re-summing trace iteration fallback with strict consumption of execution.prompt_tokens, completion_tokens, and reasoning_tokens.
      - In variance block resolution, strictly preserve typed extraction from the profile's explicit selector (`profile.variance_target_block`), ensuring deterministic execution without heuristic identifier guessing.
    </action>
    <constraint invariant="dumb_painter_invariance">
      Presentation transformers must be 100% idempotent, read-only functions mapping (ExecutionRecord, OutputProfile) to ReportDataDTO without side effects.
    </constraint>
  </step>

  <step id="5" name="EXTRACT_EXPORT_SERVICE_AND_ELIMINATE_ARB_LEAK">
    <action>Create [NEW] file @[backend_v2/services/export_service.py] (~150 lines) defining ExportService per @[ki_dual_axis_localization_architecture.md]:
      - Implement ExportService with methods export_excel(execution: ExecutionRecord, report_dto: ReportDataDTO, locale: str) -> tuple[bytes, str].
      - Configure two dedicated Excel worksheets:
        1. 'Summary': High-level dimensional scores, global scores, and executive summary text.
        2. 'Raw Data': Tabular list of every evaluated atom, score, weight, quote, and causal reasoning.
      - Implement export_flat_csv(execution: ExecutionRecord, report_dto: ReportDataDTO) -> tuple[bytes, str] using FlatFileService.
      - Define static column header dictionaries in English and Finnish within the service or reference backend I18nText SSOT.
      - Eradicate open(client_app_v2/lib/l10n/app_{locale}.arb) (#L850-L855 in execution.py). Backend export services must NEVER read client-side .arb files.
    </action>
    <action>Refactor @[backend_v2/services/execution.py#L801-L1004]:
      - Purge legacy export logic and direct .arb reading from ExecutionService.
      - Inject ExportService into ExecutionService if temporary proxy delegation is required during migration, marking delegating methods with @deprecated.
    </action>
    <constraint invariant="god_code_prevention">
      Export logic must reside in a dedicated export module under 200 lines, keeping ExecutionService focused on calculation lifecycle.
    </constraint>
    <constraint invariant="dual_axis_localization_architecture">
      ExportService must resolve headers strictly from backend I18nText database instances or static Python dictionaries. Opening client .arb files from Python is permanently prohibited.
    </constraint>
  </step>

  <step id="6" name="REPORT_ARTIFACT_DOMAIN_MODEL_AND_REPOSITORY_CRUD">
    <action>Create [NEW] file @[backend_v2/models/dtos/report_artifact.py]:
      - Define ReportStatus(StrEnum): PENDING = "pending", GENERATING = "generating", READY = "ready", FAILED = "failed" with @property def l10n_key(self) -> str: mapping to camelCase ARB keys (reportStatusPending, reportStatusGenerating, reportStatusReady, reportStatusFailed) per @[ki_dual_axis_localization_architecture.md].
      - Define ReportStoragePathsDTO(V2CoreBase): pdf_path: str | None = None, sdui_json_path: str | None = None, excel_path: str | None = None, csv_path: str | None = None.
      - Define ReportMetadataDTO(V2CoreBase): cost_usd: float | None = None, duration_ms: int | None = None, tokens_used: int | None = None, llm_model: str | None = None, provider: str | None = None, cognitive_tier: CognitiveTier | None = None, model_registry_id: str | None = None, thinking_tokens: int | None = None.
      - Define ReportRowItemDTO(V2CoreBase): execution_id: StrictStr, report_id: StrictStr, metric_key: StrictStr, metric_label: StrictStr, score: float, max_scale: float, weight: float, reasoning: str | None = None, quote: str | None = None.
      - Define PublicReportDTO(V2CoreBase): report_id: StrictStr, created_at: datetime, title: StrictStr, target_audience: StrictStr | None, overall_score: float | None, metrics: dict[str, float], executive_summary_markdown: str | None, downloads: dict[str, str].
      - Define ReportArtifactCreateDTO(V2CoreBase): execution_id: StrictStr, profile_id: StrictStr, locale: StrictStr = "fi", custom_preface_md: str | None = None, model_registry_id: str | None = None, provider_override: LLMProvider | None = None.
      - Define ReportArtifactUpdateDTO(V2CoreBase): status: ReportStatus | None = None, storage_paths: ReportStoragePathsDTO | None = None, metadata: ReportMetadataDTO | None = None, error_message: str | None = None.
      - Define ReportArtifactSummaryDTO(V2CoreBase): id: StrictStr, execution_id: StrictStr, profile_id: StrictStr, locale: StrictStr, title: str, status: ReportStatus, created_at: datetime, updated_at: datetime.
    </action>
    <action>Create [NEW] file @[backend_v2/models/domain/report_artifact.py] (~90 lines):
      - Declare ReportArtifact(V2CoreBase):
        id: StrictStr (prefixed 'rep_')
        execution_id: StrictStr
        workflow_id: StrictStr
        profile_id: StrictStr
        locale: StrictStr
        title: StrictStr
        status: ReportStatus
        storage_paths: ReportStoragePathsDTO
        metadata: ReportMetadataDTO
        error_message: str | None = None
        created_at: datetime
        updated_at: datetime
      - Re-export ReportArtifact in @[backend_v2/models/domain/__init__.py] and @[backend_v2/models/v2_core.py].
    </action>
    <action>Modify @[backend_v2/database/interfaces.py], create [NEW] @[backend_v2/database/repositories/report_artifact.py], and modify @[backend_v2/database/repository.py]:
      - In interfaces.py: Declare IReportArtifactRepository protocol with methods:
        create_report_artifact(report: ReportArtifact) -> ReportArtifact
        get_report_artifact(report_id: str) -> ReportArtifact | None
        list_report_artifacts_by_execution(execution_id: str) -> list[ReportArtifact]
        update_report_artifact(report_id: str, update_dto: ReportArtifactUpdateDTO) -> ReportArtifact
        delete_report_artifact(report_id: str) -> bool
        Mount IReportArtifactRepository onto IUnifiedWorkflowRepository facade.
      - In [NEW] repositories/report_artifact.py: Implement ReportArtifactRepositoryImpl inheriting BaseRepository and implementing IReportArtifactRepository strictly against the 'report_artifacts' collection.
      - In repository.py: Mount ReportArtifactRepositoryImpl onto UnifiedWorkflowRepository.
    </action>
    <constraint invariant="zero_permissive_typing">
      All DTOs and models MUST declare ConfigDict(strict=True, extra="forbid"). Naked dictionaries and loose typings are strictly banned.
    </constraint>
  </step>

  <step id="7" name="DECOMPOSE_EXECUTION_SERVICES_AND_CREATE_REPORT_SERVICE">
    <action>Execute Golden Master characterization test to record baseline test coverage before execution service decomposition per @[ki_god_code_prevention.md]: uv run pytest backend_v2/tests/ --cov=backend_v2.services.execution --cov-report=term-missing</action>
    <action>Execute AST boundary analysis on @[backend_v2/services/execution.py] (1,510 actual lines) via scripts/_ast_boundary_utils.py to verify exact physical node ranges before extraction.</action>
    <action>Create [NEW] file @[backend_v2/services/report_service.py] (~250 lines) defining ReportService:
      - Coordinate full report artifact lifecycle:
        1. create_report_artifact_entry(payload: ReportArtifactCreateDTO) -> ReportArtifact
        2. compile_and_persist_artifact(report_id: str, arq_pool: ArqRedis) -> None (dispatches background compilation to generate_report_artifact_job)
        3. process_artifact_compilation(report_id: str) -> None:
           - Ingest execution and profile.
           - In Phase 2 synthesis calls (executive summary, variance, row explanations), resolve LLMClient strictly via await LLMClient.from_tier(tier, repository=repo, provider=execution.metadata.provider_override, registry_id=execution.metadata.model_registry_id) using sovereign provider routing ("vertex_ai", "ai_studio", "openai", "anthropic"). Enforce Split-Cognitive Translation per @[ki_dual_axis_localization_architecture.md]: inject STATIC_LINGUISTIC_PROTOCOL and build_linguistic_parameters(target_locale=report.locale) so reasoning executes in English while user-facing summaries are delivered in target_locale.
           - Build ReportDataDTO via BlueprintTransformer (Phase 3).
           - Serialize ReportDataDTO to JSON and persist to storage driver at 'artifacts/reports/{report_id}/report.sdui.json'.
           - Generate PDF bytes via PdfReportService and persist at 'artifacts/reports/{report_id}/report.pdf'.
           - Generate Excel bytes via ExportService and persist at 'artifacts/reports/{report_id}/report.xlsx'.
           - Generate Flat CSV bytes via ExportService and persist at 'artifacts/reports/{report_id}/report.csv'.
           - Update ReportArtifact record with status=READY, storage paths, and populated ReportMetadataDTO (including real provider name, tokens, and model).
        4. get_report_sdui(report_id: str) -> ReportDataDTO: fetch from storage driver, model_validate to ReportDataDTO.
        5. get_report_pdf_bytes(report_id: str) -> bytes: stream from storage driver.
        6. get_report_excel_bytes(report_id: str) -> bytes: stream from storage driver.
        7. get_report_csv_bytes(report_id: str) -> bytes: stream from storage driver.
        8. get_report_rows(report_id: str) -> list[ReportRowItemDTO]: extract typed metric and atomic rows for B2B consumers.
        9. delete_report_artifact(report_id: str) -> None: delete database record AND all physical storage files via storage driver.
        10. regenerate_report_artifact(report_id: str, arq_pool: ArqRedis) -> None: reset status to GENERATING and re-enqueue worker job.
    </action>
    <action>Decompose @[backend_v2/services/execution.py] (1,510 actual lines) into dedicated subpackage backend_v2/services/execution/:
      - Create [NEW] @[backend_v2/services/execution/__init__.py]: Package export facade.
      - Create [NEW] @[backend_v2/services/execution/lifecycle_service.py] (~180 lines): Tenant-isolated execution lifecycle (list_executions #L197-L235, get_execution #L237-L274, delete_execution #L347-L399).
      - Create [NEW] @[backend_v2/services/execution/ingress_service.py] (~180 lines): Execution startup, SmartIngressResolver slot mapping, document attachment extraction, dynamic SDUI hints generation, model_registry_id dynamic validation against system repository, create_execution_record (#L100-L156 cleansed of `**extra_persistence_fields` with explicit `output_profile_id: str | None = None` and `isinstance(resolved_metadata, dict)` eradicated), and Arq job dispatch (start_execution #L401-L644).
      - Create [NEW] @[backend_v2/services/execution/resumption_service.py] (~120 lines): Checkpoint history validation, DAG version parity, FinOps quota check, and resume_execution (#L708-L763). Refactor check_resumability (#L646-L706, specifically #L690-L696) to strict typed ExecutionMetadata access, eradicating duck-typing and # noqa: QGR012.
      - Create [NEW] @[backend_v2/services/execution/override_service.py] (~140 lines): Human override handling (override_atom #L1059-L1146, reject_evidence_quote #L1148-L1170), scorecard_atoms update, and hook recalculation.
      - Create [NEW] @[backend_v2/services/execution/stream_service.py] (~80 lines): SSE status streaming (stream_status #L276-L345) with retry backoff and error event emission.
      - Create [NEW] @[backend_v2/services/execution/context_service.py] (~50 lines): Forensic context retrieval (get_frozen_context_bytes #L765-L799).
      - Refactor @[backend_v2/services/execution.py] into a thin Strangler Fig Facade (<80 lines): Composes the sub-services into ExecutionService and provides explicit PEP 484 re-exports (__all__) for seamless caller migration.
      - Wire ReportService, ExportService, and ExecutionService in @[backend_v2/api/dependencies.py].
    </action>
    <action>Execute /tier5-session-handover to checkpoint Phase B completion and transition cleanly to Phase C, preserving context budget for API router, Flutter UI, and documentation.</action>
    <constraint invariant="tripartite_phase_isolation">
      ReportService is 100% downstream of Phase 1. Artifact generation failures MUST update only the ReportArtifact.status to FAILED, with zero mutation to ExecutionRecord.status.
    </constraint>
    <constraint invariant="god_code_prevention">
      Every decomposed execution service is strictly under 200 lines adhering to ki_god_code_prevention.md. Root execution.py is a thin Strangler Fig facade under 80 lines. ReportService is under 300 lines.
    </constraint>
  </step>

  <step id="8" name="REPORT_ARTIFACT_REST_API_ENDPOINTS">
    <action>Create [NEW] file @[backend_v2/api/routers/execution/reports.py]:
      - POST /api/v2/executions/{execution_id}/reports -> The SOLE gateway to initiate report artifact compilation in the system. Enforces execution.status == ExecutionStatus.PASSED (raising HTTP 409 Conflict with ErrorCodes.EXECUTION_NOT_READY if execution is PENDING, RUNNING, or FAILED). Creates ReportArtifact record with status=GENERATING, enqueues generate_report_artifact_job to the worker pool, and returns HTTP 202 Accepted with ReportArtifactSummaryDTO.
      - GET /api/v2/executions/{execution_id}/reports -> Returns list[ReportArtifactSummaryDTO].
      - GET /api/v2/reports/{report_id} -> Returns ReportArtifact.
      - GET /api/v2/reports/{report_id}/sdui -> Returns ReportDataDTO (streamed from pre-compiled storage).
      - GET /api/v2/reports/{report_id}/pdf -> Returns Response(content=pdf_bytes, media_type="application/pdf").
      - GET /api/v2/reports/{report_id}/excel -> Returns Response(content=excel_bytes, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet").
      - GET /api/v2/reports/{report_id}/csv -> Returns Response(content=csv_bytes, media_type="text/csv").
      - GET /api/v2/reports/{report_id}/rows -> Returns list[ReportRowItemDTO] for B2B pipeline ingestion.
      - GET /api/v1/external/reports/{report_id} -> Returns PublicReportDTO (B2B sanitized integration format).
      - DELETE /api/v2/reports/{report_id} -> Deletes report artifact and storage files (returns HTTP 204 No Content).
      - POST /api/v2/reports/{report_id}/regenerate -> Re-enqueues Phase 2/3 compilation (returns HTTP 202 Accepted).
    </action>
    <action>Modify @[backend_v2/api/routers/execution/executions.py]:
      - Mount reports router under execution namespace.
      - In existing /render endpoint, transparently resolve or redirect to pre-compiled ReportArtifact if available.
    </action>
    <constraint invariant="rfc7807_dual_reporting_mandate">
      All endpoints must validate authentication, check resource existence, and emit structured logger.error with ErrorCodes before raising AppException.
    </constraint>
  </step>

  <step id="9" name="DESKTOP_PRO_TOOL_STUDIO_UX_FOR_REPORT_ARTIFACTS">
    <action>MANDATORY PRE-READ CONTRACT: Before creating or modifying any Flutter file in this step, execute view_file to physically load and read @[ki_desktop_pro_tool_studio_ux.md] into the active context window, ensuring all 16 UX invariants are enforced in the implementations below.</action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/models/report_artifact.dart]:
      - Define Freezed model ReportArtifact (@Freezed(equal: false)):
        id, executionId, workflowId, profileId, locale, title, status, storagePaths, errorMessage, createdAt, updatedAt.
      - Define Freezed model ReportArtifactSummary (@Freezed(equal: false)).
      - Ensure 1:1 serialization parity with Python DTOs via @JsonKey(name: 'snake_case').
    </action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/views/widgets/report_artifact_card.dart]:
      - Build adaptive report card adhering to Studio visual design system: Card container (elevation: 2, BorderRadius.circular(12), padding: EdgeInsets.all(16)), compact vertical density (~72-88px per card).
      - Pill-shaped status badge: Container(padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2), decoration: BoxDecoration(color: colorScheme.primaryContainer for READY, tertiaryContainer for GENERATING, errorContainer for FAILED, borderRadius: BorderRadius.circular(12))).
      - Profile pill and locale tag (FI/EN) in surfaceContainerHigh.
      - Enforce Header Containment: wrap title in Expanded(child: Text(..., overflow: TextOverflow.ellipsis)).
      - Action cluster isolation: wrap quick action buttons ("Näytä ruudulla", "Lataa PDF", "Lataa Excel", "Päivitä", "Poista") in Row(mainAxisSize: MainAxisSize.min, children: [...]) separated from title by AppSpacing.w16 gutter. Destructive delete action uses IconButton(icon: Icon(Icons.delete, color: colorScheme.error)) with localized AlertDialog confirmation.
      - Enforce SystemMouseCursors.click on all interactive cards and action buttons.
      - Wrap in AppErrorBoundary.
    </action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]:
      - Modal Window Bounds: Enclose dialog in ConstrainedBox(constraints: const BoxConstraints(minWidth: 480, maxWidth: 800, minHeight: 400, maxHeight: 720)).
      - Wrap dialog body in AppErrorBoundary.
      - Form controls: OutputProfile dropdown selector, Locale dropdown selector (FI/EN), and optional custom preface text area.
      - Enforce Dropdown Containment: all DropdownButtonFormField widgets specify isExpanded: true to prevent text clipping.
      - Implement Dual-Shield FormField Architecture & Modal Dismissal Protocol:
        1. Intercept Esc, AppBar close button, and barrier dismiss with PopScope(canPop: false, onPopInvokedWithResult: (didPop, result) { if (!didPop) _handleDismiss(); }). Direct un-intercepted Navigator.pop() calls are strictly prohibited.
        2. In _handleDismiss(), synchronously execute FocusScope.of(context).unfocus() and schedule dirty state evaluation inside WidgetsBinding.instance.addPostFrameCallback((_) { if (!mounted) return; ... }).
        3. Enforce Serialization-Based Model Dirty Checking: evaluate jsonEncode(_editableState.toJson()) != _initialStateJson. Banned naive != checks on @Freezed(equal: false) models to eliminate false-positive discard loops.
        4. If dirty, prompt with localized AlertDialog confirmation ("Hylkää muutokset" vs "Jatka muokkausta"). If "Jatka muokkausta", retain dialog focus and input state without disruptive scroll jumps. If "Hylkää muutokset", dismiss with null.
        5. Support Ctrl + S / Cmd + S keyboard shortcuts for atomic submission and Esc for dismissal.
      - Implement Modal-Internal Error Surface (Absolute SnackBar Ban):
        1. All validation errors, missing prerequisite alerts, or API failures must render strictly on the modal canvas (via FormField.validator error text or inline banners using colorScheme.errorContainer). Calling ScaffoldMessenger.of(context).showSnackBar() inside modal dialogs is strictly prohibited.
      - Auto-Scroll to First Invalid Field:
        1. On form validation failure, modal orchestration calls Scrollable.ensureVisible on the invalid input's FocusNode or GlobalKey to bring it into view and request focus.
      - Implement Atomic In-Flight Submission Guard (Save Debounce):
        1. Guard save routine with bool _isSaving = false: check if (_isSaving) return; _isSaving = true;, disable save button, and reset _isSaving = false synchronously if validation fails.
      - Focus and Cursor Ergonomics: SystemMouseCursors.click on buttons; full FocusTraversalGroup support.
    </action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/views/execution_reports_view.dart]:
      - Implement Adaptive Master Selector Standard (LayoutBuilder):
        1. Wide Viewports (maxWidth >= 900px): Lateral Master-Detail layout. Left pane: sticky 260px sidebar listing ReportArtifactCard items using virtualized ListView.builder with prototypeItem, sticky header with active count badge ('X / Y raporttia'), instant search field with Icons.clear action when reports > 10, and top '+ Uusi tuloste' OutlinedButton.icon. Right pane: focused detail canvas showing the active report.
        2. Compact Viewports (maxWidth < 900px): Adaptive Top-Bar Selector (SingleChildScrollView(scrollDirection: Axis.horizontal)) with ChoiceChip items for each report artifact and an inline '+ Uusi tuloste' button mounted directly above detail canvas.
        3. Sub-900px Graceful Degradation: Never implicitly revert to unbounded vertical scroll.
        4. Single Cognitive Unit Isolation: Exactly ONE report artifact is displayed in the main viewing canvas at a time. Banned unbounded vertical stacking.
        5. State Retention Invariance: Wide and compact layouts share unified state and controller pool. Window resizing or desktop snapping must NEVER unmount the active Form or reset selection.
        6. Ultrawide Bounded Canvas Containment: Wrap single-column detail bodies in Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), child: ...)) to prevent input/text sprawl on 1440p/4K monitors.
        7. Responsive Detail Stacking Guard: In compound controls and action bars, stack vertically as Column when local width < 520px and render side-by-side as Row when >= 520px. Input prefix rows stack when < 400px.
        8. Header Containment: All title and metadata labels in Row wrapped in Expanded(child: Text(..., overflow: TextOverflow.ellipsis)).
        9. Progressive Disclosure Detail Canvas: Render four distinct tabs: "Interaktiivinen näkymä" (loads pre-compiled SDUI into SduiRenderer), "PDF-esikatselu", "Rividata & Taulukot" (shows metric and forensic evidence rows), "Metatiedot & Todisteet" (runtime duration, tokens, model stack).
        10. Wrap all detail canvases and tabs in AppErrorBoundary.
        11. Action Bar: Isolated Row(mainAxisSize: MainAxisSize.min, children: [...]) separated by AppSpacing.w16: "Lataa PDF", "Lataa Excel", "Lataa CSV", "Päivitä tuloste" (re-run Phase 2/3), "Poista tuloste" (with AlertDialog confirmation).
        12. Cursors: SystemMouseCursors.click on all cards, chips, and buttons.
    </action>
    <action>Modify @[client_app_v2/lib/features/execution/views/new_execution_view.dart]:
      - Add CheckboxListTile for autoGenerateReport: "[x] Generoi tuloste automaattisesti ajon valmistuttua (Aja tulosteeksi saakka)".
      - Default to true whenever _selectedProfileId is selected or workflow has default_profile_id.
      - Ensure profile selector dropdown specifies isExpanded: true.
      - Enforce wide canvas containment (maxWidth: 1200px) and progressive disclosure.
      - Pass autoGenerateReport flag to controller/router context.
    </action>
    <action>Modify @[client_app_v2/lib/features/execution/views/execution_view.dart]:
      - When executionState reaches PASSED and autoGenerateReport is enabled:
        1. Show smooth progress transition: "Laskenta valmis (100%). Luodaan tulostetta...".
        2. Invoke POST /api/v2/executions/{id}/reports to trigger report compilation across REST API.
        3. Upon report generation (READY), auto-navigate or display the report canvas in ExecutionReportsView.
        4. If report compilation fails, preserve execution PASSED state and show actionable inline alert banner on canvas (no SnackBars!): "Tulosteen generointi epäonnistui, voit yrittää uudelleen".
        5. Eradicate legacy embedded ReportRendererV2Widget (#L291-L299) from ExecutionView: ExecutionView purely renders Phase 1 DAG progress and node timeline. All report viewing, interaction, and multi-tab rendering is strictly quarantined within the dedicated ExecutionReportsView.
        6. Enforce wide canvas containment (maxWidth: 1200px) and AppErrorBoundary wrapping.
    </action>
    <action>Update @[client_app_v2/lib/l10n/app_fi.arb] and @[client_app_v2/lib/l10n/app_en.arb] to achieve 1:1 bilingual parity for all Report Artifact UI chrome per @[ki_dual_axis_localization_architecture.md]:
      - Add keys to both files:
        * reportsTitle ("Tulosteet ja raportit" / "Reports & Outputs")
        * reportsCountSubtitle ("{count} raporttia saatavilla" / "{count} reports available", with placeholders: {count: int})
        * createReportButtonLabel ("Uusi tuloste" / "New Report")
        * createReportDialogTitle ("Luo uusi tuloste" / "Create New Report")
        * outputProfileSelectLabel ("Valitse esitysprofiili" / "Select Output Profile")
        * localeSelectLabel ("Tulosteen kieli" / "Report Language")
        * customPrefaceLabel ("Muokattu esipuhe (Valinnainen)" / "Custom Preface (Optional)")
        * saveReportButtonLabel ("Generoi tuloste" / "Generate Report")
        * downloadPdfTooltip ("Lataa PDF-tiedosto" / "Download PDF file")
        * downloadExcelTooltip ("Lataa Excel-tiedosto" / "Download Excel file")
        * downloadCsvTooltip ("Lataa CSV-tiedosto" / "Download CSV file")
        * regenerateReportTooltip ("Päivitä ja generoi uudelleen" / "Refresh and regenerate")
        * deleteReportTooltip ("Poista tuloste" / "Delete report")
        * deleteReportConfirmTitle ("Poistetaanko tuloste?" / "Delete Report?")
        * deleteReportConfirmMessage ("Haluatko varmasti poistaa tämän tulosteen? Toimintoa ei voi perua." / "Are you sure you want to delete this report? This action cannot be undone.")
        * discardChangesConfirmTitle ("Hylätäänkö muutokset?" / "Discard changes?")
        * discardChangesConfirmMessage ("Lomakkeella on tallentamattomia tietoja. Haluatko hylätä muutokset?" / "There are unsaved changes. Do you want to discard them?")
        * keepEditingButtonLabel ("Jatka muokkausta" / "Continue Editing")
        * discardButtonLabel ("Hylkää muutokset" / "Discard Changes")
        * tabInteractiveView ("Interaktiivinen näkymä" / "Interactive View")
        * tabPdfPreview ("PDF-esikatselu" / "PDF Preview")
        * tabTabularRows ("Rividata & Taulukot" / "Row Data & Tables")
        * tabTelemetryMetadata ("Metatiedot & Todisteet" / "Metadata & Evidence")
        * reportStatusPending ("Jonossa" / "Pending")
        * reportStatusGenerating ("Generoidaan..." / "Generating...")
        * reportStatusReady ("Valmis" / "Ready")
        * reportStatusFailed ("Epäonnistui" / "Failed")
        * autoGenerateReportLabel ("Generoi tuloste heti ajon valmistuttua (Aja tulosteeksi saakka)" / "Generate report immediately upon completion (Run until output)")
      - Run: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports --build
    </action>
    <constraint invariant="cognitive_ergonomics_and_dual_pane_standard">
      Layout transitions between wide and compact must preserve selected report index and scroll positions. Banned unbounded vertical stacking is strictly forbidden. Exactly ONE report rendered at a time.
    </constraint>
    <constraint invariant="uncommitted_state_loss_prevention_mandate">
      CreateReportDialog must evaluate dirty state via serialized JSON comparison inside addPostFrameCallback after focus-loss flush. Modal-internal error surfaces must be used exclusively; SnackBars inside dialogs are banned.
    </constraint>
    <constraint invariant="universal_horizontal_overflow_immunity_mandate">
      All titles and headers in Row layouts must be enclosed in Expanded(child: Text(..., overflow: TextOverflow.ellipsis)). Dropdowns must specify isExpanded: true. Layouts must remain 100% hazard-stripe-free down to 360px width.
    </constraint>
    <constraint invariant="modal_window_bounds_and_error_boundary">
      Dialogs must be bounded by ConstrainedBox(minWidth: 480, maxWidth: 800, minHeight: 400, maxHeight: 720). Detail canvases must enforce maxWidth: 1200px. All views, tabs, and modals must be enclosed in AppErrorBoundary.
    </constraint>
    <constraint invariant="dual_axis_localization_parity">
      100% of UI chrome resolves exclusively from compile-time .arb files via AppLocalizations.of(context)! with 1:1 Finnish and English parity. Zero hardcoded UI strings in Dart widgets.
    </constraint>
  </step>

  <step id="10" name="AUTOMATED_REGRESSION_VERIFICATION_AND_QUALITY_GATES">
    <action>Update and expand unit test suites:
      - In [NEW] @[backend_v2/tests/unit/workers/test_execution_worker.py]:
        1. Test that successful DAG execution immediately sets status=ExecutionStatus.PASSED with completed_at populated.
        2. Test that execution.steps contains zero synthetic sys_render steps.
        3. Test that execute_workflow_job enqueues 0 report or render jobs upon completion.
      - In [NEW] @[backend_v2/tests/unit/workers/test_report_worker.py]:
        1. Test that generate_report_artifact_job delegates compilation to ReportService.
        2. Test that when PDF generation or synthesis fails, execution.status remains ExecutionStatus.PASSED.
      - In [NEW] @[backend_v2/tests/unit/test_worker_proxy.py]:
        1. Test that root worker.py exports all symbols in __all__ matching PEP 484 and satisfies mypy --strict.
        2. Test that run_worker.py imports WorkerSettings cleanly from worker.py.
      - In [NEW] @[backend_v2/tests/unit/test_v2_core_proxy.py]:
        1. Test that root v2_core.py re-exports all 43 symbols matching PEP 484 and satisfies mypy --strict.
        2. Test that each re-exported domain model validates correctly with ConfigDict(strict=True, extra="forbid").
      - In @[backend_v2/tests/unit/services/test_blueprint.py]:
        1. Test that build_report_dto invokes zero update methods on exec_repo.
        2. Test that variance validation block renders correctly adhering to OutputProfile.variance_target_block.
      - In [NEW] @[backend_v2/tests/unit/services/execution/]:
        1. test_lifecycle_service.py: Test list_executions, get_execution, delete_execution with tenant isolation and storage cleanup.
        2. test_ingress_service.py: Test start_execution with optional profile_id, SmartIngressResolver integration, and dynamic SDUI hints.
        3. test_resumption_service.py: Test check_resumability (status, checkpoint, DAG parity, quota) and resume_execution.
        4. test_override_service.py: Test override_atom scorecard mutation and scoring hook recalculation.
        5. test_stream_service.py: Test SSE stream_status authorization and retry backoff.
      - In [NEW] @[backend_v2/tests/unit/services/test_execution_proxy.py]:
        1. Test that root services/execution.py re-exports ExecutionService and create_execution_record matching PEP 484 and satisfies mypy --strict.
      - In [NEW] @[backend_v2/tests/unit/services/test_export_service.py]:
        1. Test export_excel generates two-tab workbook (Summary and Raw Data) without reading client .arb files.
        2. Test export_flat_csv generates valid CSV structure with backend I18nText headers.
      - In [NEW] @[backend_v2/tests/unit/services/test_report_service.py]:
        1. Test report artifact creation, storage file persistence, and pre-compiled SDUI loading.
        2. Test delete_report_artifact cleans up both DB record and disk files.
        3. Test regeneration updates status and re-generates bundles without DAG re-execution.
        4. Test get_report_rows returns typed metric and atomic row structures.
      - In [NEW] @[backend_v2/tests/unit/api/test_reports_api.py]:
        1. Test POST /api/v2/executions/{id}/reports enqueues artifact creation.
        2. Test GET /api/v2/executions/{id}/reports returns summary list.
        3. Test GET /api/v2/reports/{id}/sdui returns cached ReportDataDTO JSON.
        4. Test GET /api/v2/reports/{id}/rows returns structured tabular rows.
        5. Test GET /api/v1/external/reports/{id} returns sanitized PublicReportDTO.
        6. Test DELETE /api/v2/reports/{id} deletes artifact.
      - In [NEW] @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]:
        1. Test AST import analysis: verify that backend_v2/workers/execution_worker.py, backend_v2/services/execution/, and backend_v2/evaluators/topological_evaluator.py contain zero imports, function calls, or queue enqueues referencing ReportService, export_service, or report compilation tasks.
        2. Test zero side-effects: verify that running execute_workflow_job with mocked Redis enqueues 0 report/render jobs and creates 0 report records.
        3. Test REST-only entrypoint: verify that POST /api/v2/executions/{id}/reports is the exclusive trigger that creates ReportArtifact and enqueues worker generation.
        4. Test precondition gate: verify that calling POST /api/v2/executions/{id}/reports when execution is RUNNING or FAILED raises HTTP 409 Conflict with ErrorCodes.EXECUTION_NOT_READY.
        5. Test Dual-Axis Localization AST compliance: verify that backend_v2 contains zero occurrences of open() opening files with '.arb' extension or paths targeting client_app_v2/lib/l10n/.
        6. Test Strict Enum Adapter: verify ReportStatus.l10n_key maps 1:1 to Flutter ARB camelCase translation keys.
      - Cleanse test fixtures in backend_v2/tests/ passing dummy allowed_exports to Workflow.
    </action>
    <action>Execute automated quality gates:
      - Run localized unit tests: uv run pytest backend_v2/tests/unit/workers/ backend_v2/tests/unit/test_worker_proxy.py backend_v2/tests/unit/services/execution/ backend_v2/tests/unit/services/test_execution_proxy.py backend_v2/tests/unit/services/test_blueprint.py backend_v2/tests/unit/services/test_export_service.py backend_v2/tests/unit/services/test_report_service.py backend_v2/tests/unit/api/test_reports_api.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py -v
      - Run model discovery, provider decoupling, and cognitive tier regression tests: uv run pytest backend_v2/tests/unit/test_model_registry_discovery.py backend_v2/tests/unit/test_google_providers_separation.py backend_v2/tests/unit/llm/test_llm_client_tiers.py backend_v2/tests/unit/database/repositories/test_system_model_registry.py -v
      - Run global backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2 --test
      - Regenerate Freezed models: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/models/report_artifact.dart --build
      - Run Flutter frontend audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports --build
    </action>
    <constraint invariant="anti_happy_path_compliance">
      All new tests must explicitly test failure partitions: 1) missing profile, 2) nonexistent profile, 3) PDF generation failure, 4) non-existent report artifact deletion, 5) invalid API key on external row endpoint, 6) execution not in PASSED state when requesting report creation, 7) invalid model registry override during report creation.
    </constraint>
  </step>

  <step id="11" name="KNOWLEDGE_BASE_DOCUMENTATION_AND_KI_SYNCHRONIZATION">
    <action>Update @[ki_tripartite_pipeline_architecture.md] to codify the expanded tripartite invariants:
      - Add rule_block id="phase1_lifecycle_sovereignty": Phase 1 execution transitions directly to ExecutionStatus.PASSED immediately upon conclusion of analytical evaluation and scoring. Eradicate synthetic execution step injection (sys_render_{profile_id}) from execution history.
      - Add rule_block id="presentation_failure_isolation": Phase 2 synthesis or Phase 3 rendering crashes must NEVER mutate ExecutionRecord.status to ExecutionStatus.FAILED. Layout or rendering failures remain quarantined in ReportArtifact or RenderedSynthesisCache without backward cascade.
      - Add rule_block id="execution_ingress_decoupling": output_profile_id is strictly optional at execution start (ExecutionCreateDTO). Execution completes Phase 1 successfully when output_profile_id is None.
      - Add rule_block id="read_only_presentation_transformers": BlueprintTransformer must be 100% side-effect-free and read-only. Database update calls (update_execution) are strictly banned during presentation rendering.
      - Add rule_block id="materialized_report_artifacts": Elevate generated outputs into independent ReportArtifact entities. Multiple reports can be spawned from a single execution run across profiles and locales.
      - Add rule_block id="b2b_tabular_row_delivery": Document dual-tier row data delivery (Metric Rows and Forensic Evidence Rows) across multi-tab Excel, CSV, and REST API.
      - Add rule_block id="cqrs_export_isolation": Document and flat-file exports are decoupled into ExportService, isolated from ExecutionService.
      - Update Mermaid sequence diagram to reflect decoupled lifecycle, optional profile ID, and materialized report artifact CRUD.
    </action>
    <action>Update @[ki_dual_axis_localization_architecture.md]:
      - Enforce strict Axis 1 vs Axis 2 boundary for export generation: backend export services must NEVER read client-side .arb files (client_app_v2/lib/l10n/app_{locale}.arb).
      - Mandate that ExportService and ReportService resolve export headers strictly from backend I18nText database records or static backend translation dictionaries.
    </action>
    <action>Update @[ki_god_code_prevention.md]:
      - Document SRP and CQRS decomposition: extracting worker.py into backend_v2/workers/ (execution_worker.py and report_worker.py with thin worker.py Strangler Fig facade) and decomposing ExecutionService into backend_v2/services/execution/ subpackage (lifecycle, ingress, resumption, override, stream, context services each <180 lines, root execution.py facade <80 lines), ExportService (<150 lines), and ReportService (<250 lines).
    </action>
    <action>Update @[ki_desktop_pro_tool_studio_ux.md]:
      - Document Adaptive Master Selector and Dual-Shield FormField integration for Execution Report Artifacts.
    </action>
    <constraint invariant="knowledge_base_primacy">
      All updated KIs must be persisted in their respective metadata and artifact locations, providing the authoritative theoretical foundation before architectural documentation sync.
    </constraint>
  </step>

  <step id="12" name="TIER_7_AS_BUILT_ARCHITECTURE_SYNCHRONIZATION">
    <action>Execute /tier7-describe-architecture audit and synchronize the physical codebase with the authoritative architecture pillar documents:
      - In @[docs/architecture/01_system_context_and_invariants.md]:
        1. Update Section 2.15 (Tripartite Pipeline Isolation & Evaluation Score Sovereignty) to document Phase 1 lifecycle sovereignty (immediate transition to PASSED), execution ingress decoupling (output_profile_id: str | None = None), presentation failure isolation (zero reverse pollution), and Materialized Report Artifacts.
        2. Document complete eradication of allowed_exports from Workflow and strict typed preservation of variance_target_block and user_role_target_block on OutputProfile.
        3. Document B2B row-level tabular delivery and Public REST API integration.
        4. Document God Code decomposition of backend workers and execution services into subpackages according to SRP.
      - In @[docs/architecture/03_cognitive_orchestration_engine.md]:
        1. Update Section 2.7 (Asynchronous Background Workers & Non-Blocking Handshake) to document worker lifecycle completion setting ExecutionStatus.PASSED directly upon DAG topological sort finish and telemetry finalization.
        2. Document elimination of synthetic sys_render step injection from ExecutionRecord.steps and step_states.
        3. Document independent background enqueue of report artifact compilation jobs and subpackage decomposition into backend_v2/workers/execution_worker.py and backend_v2/workers/report_worker.py.
      - In @[docs/architecture/04_server_driven_ui_and_presentation.md]:
        1. Update Section 2.1 (Dumb Painter Pipeline) to document BlueprintTransformer 100% read-only dumb painter invariance with zero database mutation calls (update_execution).
        2. Update Section 2.4 (Database-Driven Target Block Dispatching) to document variance validation anchored strictly to explicit OutputProfile.variance_target_block configuration.
        3. Document ReportService and ExportService CQRS export generation anchored to backend I18nText SSOT without reading client .arb files.
        4. Document Desktop-Class Pro Tool UI for Execution Report Artifact management adhering to Adaptive Master Selector standard.
      - In @[.agents/rules/04_directory_reference.md]:
        Register backend_v2/workers/ (subpackage), backend_v2/workers/execution_worker.py, backend_v2/workers/report_worker.py, backend_v2/services/execution/ (subpackage with lifecycle, ingress, resumption, override, stream, context services), backend_v2/services/export_service.py, backend_v2/services/report_service.py, and backend_v2/api/routers/execution/reports.py.
      - In @[docs/architecture/00_README_META_ARCHITECTURE.md]:
        Verify and synchronize high-level meta-architecture overview.
    </action>
    <constraint invariant="timeless_as_built_mandate">
      All theoretical descriptions in the architecture pillars MUST be strictly timeless and read as cohesive narratives. Updates MUST describe purely and exclusively current system state in present tense.
    </constraint>
  </step>
</execution_protocol>
```

---

## Anti-Happy-Path & ISTQB Failure Partitions

### Partition 1: Execution Ingress without Output Profile
- **Scenario A (Success Path)**: Caller starts execution on a workflow with `profile_id=None` and `workflow.default_profile_id=None`.
  - *Input*: `ExecutionCreate(workflow_id="wor_123", raw_inputs={...}, profile_id=None)`
  - *Expected Result*: Execution creates cleanly with `status=PENDING`, `output_profile_id=None`. DAG completes with `status=PASSED`.
- **Scenario B (Negative Path - Nonexistent Profile)**: Caller passes an unknown profile ID.
  - *Input*: `ExecutionCreate(workflow_id="wor_123", raw_inputs={...}, profile_id="prof_nonexistent")`
  - *Expected Result*: `AppException` raised with status 404, `ErrorCodes.RESOURCE_NOT_FOUND`. Execution record is NOT created.

### Partition 2: Presentation Rendering Failure Isolation
- **Scenario A (Success Path)**: DAG finishes, PDF renders successfully.
  - *Input*: Completed execution record with `output_profile_id="prof_default"`.
  - *Expected Result*: `execution.status == ExecutionStatus.PASSED`, `execution.pdf_report_path == "executions/.../report.pdf"`.
- **Scenario B (Negative Path - PDF Engine Crash)**: `PdfReportService` throws an unhandled `RuntimeError("Weasyprint syntax error")`.
  - *Input*: `generate_pdf_task(execution_id="exe_test", profile_id="prof_default")` with broken PDF engine mock.
  - *Expected Result*: `execution.status` remains `ExecutionStatus.PASSED`. `pdf_report_path` remains `None`. Error logged with `ErrorCodes.PDF_GENERATION_FAILED`. No `ExecutionStatus.FAILED` mutation occurs.

### Partition 3: Blueprint Transformer Read-Only Invariance
- **Scenario A (Success Path)**: Report DTO assembled for execution with human overrides.
  - *Input*: `build_report_dto(execution_id="exe_test", profile_id="prof_default")`.
  - *Expected Result*: Returns strictly typed `ReportDataDTO`. `exec_repo.update_execution` call count is exactly 0.
- **Scenario B (Negative Path - Read-Only Enforcement)**: `exec_repo` passed to `BlueprintTransformer` is wrapped in a proxy raising on any write method.
  - *Input*: `build_report_dto` executed against read-only repository.
  - *Expected Result*: Completes without raising any write exception.

### Partition 4: Report Artifact CRUD & File Lifecycle
- **Scenario A (Success Path - Full Lifecycle)**: User creates report artifact with profile "prof_board", views SDUI, downloads PDF, and deletes artifact.
  - *Input*: `POST /api/v2/executions/exe_1/reports (profile_id="prof_board", locale="en")` -> worker compiles -> `GET /api/v2/reports/rep_1/sdui` -> `DELETE /api/v2/reports/rep_1`.
  - *Expected Result*: Artifact record created, storage files generated at `artifacts/reports/rep_1/report.pdf` and `report.sdui.json`, SDUI served without re-evaluating DAG. Upon DELETE, database record and all storage files are deleted cleanly.
- **Scenario B (Negative Path - Nonexistent Report)**: Caller requests SDUI or PDF for invalid report ID.
  - *Input*: `GET /api/v2/reports/rep_nonexistent/pdf`
  - *Expected Result*: `AppException` raised with status 404, `ErrorCodes.RESOURCE_NOT_FOUND`.
- **Scenario C (Negative Path - Desktop Modal Dirty State Dismiss Interception & Error Surface)**: User changes profile/locale in `CreateReportDialog` and presses Esc, or triggers validation failure.
  - *Input*: User edits dialog and presses Esc or clicks close icon; user clicks save with missing required selection; user clicks save rapidly twice.
  - *Expected Result*: 1) `PopScope` intercepts dismissal, executes `unfocus()`, evaluates dirty state via serialized JSON comparison (`jsonEncode`) inside `addPostFrameCallback`, and shows localized `AlertDialog` ("Hylkää muutokset" vs "Jatka muokkausta"). Clean dismissal without edits closes immediately without prompting (verifying zero false positives from `@Freezed(equal: false)`). 2) Validation failure renders inline error text and scrolls to invalid input via `Scrollable.ensureVisible`, verifying that `ScaffoldMessenger.of(context).showSnackBar()` is called 0 times. 3) Save debounce lock (`_isSaving = true`) blocks second tap and prevents concurrent REST dispatches.
- **Scenario D (Negative Path - B2B Row Extraction on Failed Artifact)**: External consumer requests row data on report artifact whose generation failed.
  - *Input*: `GET /api/v2/reports/rep_failed/rows`
  - *Expected Result*: `AppException` raised with status 409 Conflict, indicating artifact compilation did not conclude successfully.

### Partition 5: REST-API-Only Boundary & Anti-Coupling Invariant
- **Scenario A (Success Path - Pure REST-Initiated Report Generation)**: Caller finishes Phase 1, then issues `POST /api/v2/executions/{id}/reports`.
  - *Input*: Execution in `status=PASSED`. Request: `POST /api/v2/executions/{id}/reports` with `profile_id="prof_default"`.
  - *Expected Result*: HTTP 202 Accepted, `ReportArtifact` record created in `GENERATING` state, `generate_report_artifact_job` enqueued in worker pool.
- **Scenario B (Negative Path - Precondition Gate on Non-Passed Execution)**: Caller attempts to create report artifact while execution is still `RUNNING` or `FAILED`.
  - *Input*: `POST /api/v2/executions/{id_running}/reports`.
  - *Expected Result*: `AppException` raised with HTTP 409 Conflict (`ErrorCodes.EXECUTION_NOT_READY`). Zero report records created, zero worker jobs enqueued.
- **Scenario C (Negative Path - AST Anti-Coupling Guardrail)**: AST analyzer inspects `worker.py` (`execute_workflow_job`), `services/execution.py`, and `evaluators/topological_evaluator.py`.
  - *Input*: AST visitor traverses all import statements and call nodes in execution domain.
  - *Expected Result*: Exactly 0 references to `ReportService`, `export_service`, or report queue tasks. Test fails if any backdoors exist.

### Partition 6: Sovereign Model Stack & Cognitive Tier Resolution in Reporting
- **Scenario A (Success Path - Dynamic Registry & Sovereign Provider Resolution)**: Report compilation generates executive synthesis using the bound model stack and cognitive tier (`BALANCED`), querying `LLMClient.from_tier` without error.
  - *Input*: `ReportArtifactCreateDTO(execution_id="exe_1", profile_id="prof_default")` on an execution bound to `model_registry_id="sys_e26807f3bfa3454d"` with `provider_override="ai_studio"`.
  - *Expected Result*: `LLMClient.from_tier(CognitiveTier.BALANCED, ...)` resolves the active model profile from the bound registry, generates synthesis, and stamps `ReportMetadataDTO(provider="Google AI Studio", cognitive_tier="balanced", llm_model="gemini/gemini-3.8-flash")`.
- **Scenario B (Negative Path - Nonexistent Model Registry on Report Override)**: Caller passes an invalid `model_registry_id` override during report creation.
  - *Input*: `ReportArtifactCreateDTO(execution_id="exe_1", profile_id="prof_default", model_registry_id="sys_invalid_nonexistent")`.
  - *Expected Result*: `AppException` raised with status 404 (`ErrorCodes.RESOURCE_NOT_FOUND`). Zero report records created.

### Partition 7: Idempotency & Concurrent Report Generation Shield
- **Scenario A (Success Path - Sequential Compilation & Distinct Report IDs)**: User triggers two distinct reports for different profiles sequentially.
  - *Input*: `POST /api/v2/executions/{id}/reports (profile_id="prof_board")`, followed by `POST /api/v2/executions/{id}/reports (profile_id="prof_coach")`.
  - *Expected Result*: Two distinct `ReportArtifact` records created (`rep_1` and `rep_2`), each compiled to its own isolated storage directory with status `READY`.
- **Scenario B (Negative Path - Race Prevention on Regeneration)**: Caller attempts to trigger regeneration on an artifact that is already actively generating.
  - *Input*: `POST /api/v2/reports/{id_generating}/regenerate`.
  - *Expected Result*: `AppException` raised with HTTP 409 Conflict (`ErrorCodes.RESOURCE_CONFLICT`). Job is NOT enqueued a second time.

### Partition 8: Execution Cascade Deletion & Physical Storage Cleanup
- **Scenario A (Success Path - Full Cascade Purge)**: User deletes an execution that has 2 generated report artifacts.
  - *Input*: `DELETE /api/v2/executions/{execution_id}` where `rep_1` and `rep_2` exist with physical files (`report.pdf`, `report.sdui.json`, `report.xlsx`, `report.csv`).
  - *Expected Result*: HTTP 204 No Content. Physical directories `artifacts/reports/rep_1/` and `artifacts/reports/rep_2/` are physically deleted from storage. Database records for both reports are removed.
- **Scenario B (Negative Path - Missing Physical File During Deletion)**: A report artifact database record exists, but its physical PDF was already deleted manually from disk.
  - *Input*: `DELETE /api/v2/reports/{report_id}` where physical file is absent.
  - *Expected Result*: Operation succeeds idempotently without raising `FileNotFoundError`, logging a warning and deleting the database metadata cleanly.

---

## Verification Plan

### Automated Test Commands
0. **Pre-Execution AST Boundary Verification & Characterization Baselines**:
   ```powershell
   uv run python scripts/_ast_boundary_utils.py backend_v2/models/v2_core.py
   uv run python scripts/_ast_boundary_utils.py backend_v2/worker.py
   uv run python scripts/_ast_boundary_utils.py backend_v2/services/execution.py
   uv run python scripts/_ast_boundary_utils.py backend_v2/services/orchestrator/dag_executor.py
   uv run pytest backend_v2/tests/ --cov=backend_v2.worker --cov=backend_v2.services.execution --cov-report=term-missing
   ```
1. **Targeted Unit Tests & Smoke Tests**:
   ```powershell
   # Post-Step 3 Arq Worker smoke test:
   uv run python -c "from backend_v2.worker import WorkerSettings; print([f.name for f in WorkerSettings.functions])"

   # Targeted domain and unit tests:
   uv run pytest backend_v2/tests/unit/workers/ -v
   uv run pytest backend_v2/tests/unit/test_worker_proxy.py -v
   uv run pytest backend_v2/tests/unit/services/test_blueprint.py -k "test_blueprint_read_only" -v
   uv run pytest backend_v2/tests/unit/services/test_execution.py -k "test_ingress_decoupled" -v
   uv run pytest backend_v2/tests/unit/services/test_export_service.py -v
   uv run pytest backend_v2/tests/unit/services/test_report_service.py -v
   uv run pytest backend_v2/tests/unit/api/test_reports_api.py -v
   uv run pytest backend_v2/tests/unit/test_rest_only_pipeline_boundary.py -v
   uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py -v
   ```
2. **Model Discovery & Cognitive Tier Regression Suites**:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_model_registry_discovery.py -v
   uv run pytest backend_v2/tests/unit/test_google_providers_separation.py -v
   uv run pytest backend_v2/tests/unit/llm/test_llm_client_tiers.py -v
   uv run pytest backend_v2/tests/unit/database/repositories/test_system_model_registry.py -v
   ```
3. **Full Domain Test Suite**:
   ```powershell
   uv run pytest backend_v2/tests/unit/workers/ backend_v2/tests/unit/test_worker_proxy.py backend_v2/tests/unit/services/test_blueprint.py backend_v2/tests/unit/services/test_execution.py backend_v2/tests/unit/services/test_export_service.py backend_v2/tests/unit/services/test_report_service.py backend_v2/tests/unit/api/test_reports_api.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py -v
   ```
4. **Universal Quality Gate (Linting, Formatting, Strict Typing, Pytest)**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2 --test
   ```
5. **Frontend Code Generation & Quality Gate**:
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/models/report_artifact.dart --build
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports --build
   ```

---

## Post-Implementation Documentation & As-Built Synchronization (/tier7-describe-architecture)

Following successful quality gate completion (Step 10), the implementation protocol mandates updating the Knowledge Base and executing `/tier7-describe-architecture` to keep architectural documentation in 1:1 parity with the codebase.

### 1. Knowledge Item (KI) Artifact Updates
- **@[ki_tripartite_pipeline_architecture.md]**:
  - Incorporate `phase1_lifecycle_sovereignty`: Formalize that DAG execution transitions directly to `ExecutionStatus.PASSED` immediately upon topological evaluation completion, eradicating synthetic `sys_render_{profile_id}` steps.
  - Incorporate `presentation_failure_isolation`: Mandate zero reverse pollution; Phase 2 synthesis or Phase 3 PDF rendering crashes are quarantined and must never mutate `ExecutionRecord.status` to `ExecutionStatus.FAILED`.
  - Incorporate `execution_ingress_decoupling`: Specify that `output_profile_id` is strictly optional at execution start (`ExecutionCreateDTO`).
  - Incorporate `read_only_presentation_transformers`: Codify that `BlueprintTransformer` is 100% side-effect-free and read-only, prohibiting `update_execution` database mutations during presentation rendering.
  - Incorporate `materialized_report_artifacts`: Formalize that generated outputs are independent `ReportArtifact` records with independent lifecycles.
  - Incorporate `b2b_tabular_row_delivery`: Formalize two-tier row delivery (Metric Rows and Forensic Evidence Rows) via Excel, CSV, and REST API.
  - Incorporate `cqrs_export_isolation`: Formalize decoupling of file and Excel export generation into `ExportService`.
  - Update Mermaid sequence diagram to reflect decoupled worker lifecycle and failure containment.
- **@[ki_dual_axis_localization_architecture.md]**:
  - Codify Axis 1 vs Axis 2 boundary enforcement for exports: backend export services must NEVER read client-side `.arb` files (`client_app_v2/lib/l10n/app_{locale}.arb`).
  - Mandate that `ExportService` and `ReportService` resolve export headers strictly from backend `I18nText` database records or static backend translation dictionaries.
- **@[ki_god_code_prevention.md]**:
  - Document CQRS extraction of export and report compilation from `ExecutionService` into dedicated `ExportService` (<200 lines) and `ReportService` (<300 lines).
- **@[ki_desktop_pro_tool_studio_ux.md]**:
  - Document Adaptive Master Selector and Dual-Shield FormField integration for Execution Report Artifacts.

### 2. Architectural Pillar Synchronization via /tier7-describe-architecture
The architectural pillar documents must be updated in accordance with the Dual-Axis Documentation Paradigm and the `timeless_as_built_mandate`:
- **@[docs/architecture/01_system_context_and_invariants.md]**:
  - Update Section 2.15 (Tripartite Pipeline Isolation & Evaluation Score Sovereignty):
    - Document Phase 1 lifecycle sovereignty (immediate transition to `PASSED`).
    - Document execution ingress decoupling (`output_profile_id: str | None = None`).
    - Document zero reverse pollution (presentation layout and export crashes quarantined in Phase 3 without altering execution status).
    - Document Materialized Report Artifacts and full-lifecycle CRUD.
    - Document B2B row-level tabular delivery and Public REST API integration.
    - Document complete eradication of `allowed_exports` from `Workflow` and strict typed preservation of `variance_target_block` / `user_role_target_block` on `OutputProfile`.
- **@[docs/architecture/03_cognitive_orchestration_engine.md]**:
  - Update Section 2.7 (Asynchronous Background Workers & Non-Blocking Handshake):
    - Document worker lifecycle completion setting `ExecutionStatus.PASSED` directly upon DAG topological sort finish and telemetry finalization.
    - Document elimination of synthetic `sys_render` step injection from `ExecutionRecord.steps` and `step_states`.
    - Document independent background enqueue of report artifact compilation jobs.
- **@[docs/architecture/04_server_driven_ui_and_presentation.md]**:
  - Update Section 2.1 (Dumb Painter Pipeline):
    - Document `BlueprintTransformer` 100% read-only dumb painter invariance with zero database mutation calls (`update_execution`).
  - Update Section 2.4 (Database-Driven Target Block Dispatching):
    - Document variance validation anchored strictly to explicit `OutputProfile.variance_target_block` configuration.
    - Document dedicated `ExportService` for multi-tab Excel and flat-file export compilation anchored to backend `I18nText` SSOT without reading client `.arb` files.
    - Document dedicated `ReportService` and REST API for Materialized Report Artifact CRUD and row-level data delivery.
    - Document Desktop-Class Pro Tool UI for Execution Report Artifact management adhering to Adaptive Master Selector standard.
- **@[.agents/rules/04_directory_reference.md]**:
  - Register `backend_v2/services/export_service.py`, `backend_v2/services/report_service.py`, and `backend_v2/api/routers/execution/reports.py`.
- **@[docs/architecture/00_README_META_ARCHITECTURE.md]**:
  - Verify and synchronize high-level meta-architecture overview.

### 3. Execution Mandate & Verification
The synchronization will be performed following Step 10 using `/tier7-describe-architecture`:
- The auditor will verify that all physical files match the theoretical documentation.
- The auditor will verify that zero legacy anti-patterns or historical markers exist in the updated pillars.
- Documentation must describe purely and exclusively current system state in present tense.
