<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Tripartite Pipeline Isolation, Worker Decoupling & Report Artifact CRUD

## Overview & Objective

This implementation plan establishes full structural compliance with the Tripartite Pipeline Architecture as codified in @[ki_tripartite_pipeline_architecture.md] and the Desktop-Class Pro Tool UX as codified in @[ki_desktop_pro_tool_studio_ux.md]. It decouples Phase 1 (Execution & Evaluation DAG), Phase 2 (Synthesis & Reporting), and Phase 3 (Dumb Painter SDUI/PDF Rendering), eliminating inter-phase chatter, synthetic execution step injections, database mutation from presentation transformers, and failure cascade pollution.

Furthermore, this plan formalizes the **Materialized Report Artifact Architecture**: all rendered presentation outputs (`report.pdf`, `report.sdui.json`, `report.xlsx`, tabular row data) are elevated into first-class, immutable, and independently versioned `ReportArtifact` records with full-lifecycle CRUD operations across the Database, REST API, Background Worker, and Flutter Desktop Studio UI.

### Core Architectural Mandates Addressed
1. **Phase 1 Execution Lifecycle Sovereignty**: DAG execution status transitions directly to `ExecutionStatus.PASSED` immediately upon completion of analytical reasoning and scoring. The artificial execution step (`sys_render_{profile_id}`) is eradicated from execution state history.
2. **Failure Isolation (Zero Reverse Pollution)**: PDF rendering and synthesis failures in Phase 2/3 must NEVER mutate `ExecutionRecord.status` to `ExecutionStatus.FAILED`. A presentation layout or file-system error remains quarantined in the rendering response or cache.
3. **Ingress Decoupling**: Executions must be executable without specifying a presentation profile. `output_profile_id` becomes strictly optional at execution ingress.
4. **Read-Only Presentation Transformers**: `BlueprintTransformer.build_report_dto` becomes 100% read-only and side-effect-free, eradicating database mutation calls (`update_execution`) during presentation rendering.
5. **Schema De-Infiltration & Ghost Field Purge**: Eradicates raw prompt block IDs (`variance_target_block`, `user_role_target_block`) from `OutputProfile` in favor of dynamic semantic matrix resolution. Completely purges the ghost field `allowed_exports` from `Workflow` (Python `v2_core.py`) and Flutter (`workflow.dart`). Forensic audit verified that `allowed_exports` has 0 usages across all backend services, workers, and Flutter UI views/widgets, and 0 occurrences in `seed_data.json`.
6. **CQRS Export Extraction**: Extracts document export and Excel compilation from `ExecutionService` into a dedicated `ExportService`, eliminating backend reads of Flutter `.arb` files.
7. **Materialized Report Artifacts & Full-Lifecycle Output CRUD**: Elevates generated outputs into independent, first-class `ReportArtifact` domain models. A single execution run (Phase 1) can spawn multiple distinct report artifacts (Phase 2 & 3) tailored to different audiences (specifically: Board, Executive Coach, Forensic Auditor) and languages (FI, EN). Pre-compiled SDUI JSON, PDF, and Excel files are stored as immutable artifacts served with $O(1)$ latency without re-evaluating the DAG or reparsing atomic traces. Complete CRUD (Create, Read, Update/Regenerate, Delete, List) is supported across Backend Repository, REST API, and Flutter Desktop Studio UI adhering strictly to @[ki_desktop_pro_tool_studio_ux.md].
8. **REST-API-Only Pipeline Boundary (Absolute Decoupling Mandate)**: Phase 1 (DAG execution) and Phase 2/3 (report generation) MUST NEVER be connected via in-process memory calls, direct worker queue-chaining, or backdoor worker-to-worker auto-triggers. The REST API (`POST /api/v2/executions/{execution_id}/reports`) is the SOLE legitimate gateway through which report compilation can be initiated across the entire system. Both the Flutter UI (reacting to `status == PASSED` when `[x] Aja tulosteeksi saakka` is checked) and external B2B clients connect the runs strictly across this HTTP REST boundary. Static import firewalls and automated AST-level tests mathematically enforce that the execution engine contains zero imports, references, or job-enqueues targeting reporting services or queues.
9. **Database Bounded Context & Schema Segregation Invariant**: The database layer enforces strict microservice-spirit schema segregation between Phase 1 and Phase 2/3. Phase 1 computational execution records reside exclusively in the `executions` collection (`ExecutionRecord`), strictly append-only and immutable upon reaching `status == PASSED`. Phase 2/3 presentation outputs reside exclusively in the dedicated `report_artifacts` collection (`ReportArtifact`), connected only via a loose foreign key (`execution_id: str`). Database access is quarantined into dedicated repository implementations: `ExecutionRepositoryImpl` operates strictly against `executions`, while `ReportArtifactRepositoryImpl` operates strictly against `report_artifacts`. Large physical files (PDF, SDUI JSON, Excel, CSV) are offloaded to Cloud-Native Object Storage (`artifacts/reports/{id}/`), leaving only lightweight metadata in the database.
10. **Four-Tier Strict Pydantic V2 Model Invariant**: All domain models and DTOs across the pipeline are strictly partitioned into four non-overlapping tiers: 1) Analytical Execution Models (`ExecutionRecord`, `AtomResultDTO`), 2) Materialized Artifact Lifecycle DTOs (`ReportArtifact`, `ReportArtifactCreateDTO`), 3) Dumb Painter Presentation DTOs (`ReportDataDTO`, `ReportRowItemDTO`), and 4) Studio Profile Definitions (`OutputProfile`). Every single model without exception enforces `ConfigDict(strict=True, extra="forbid")`, banning loose dictionaries (`no_naked_dicts_in_state`), legacy ghost fields, and accidental cross-tier field bleed. Full-Duplex Serialization Parity guarantees 1:1 typed parity with Dart Freezed models in Flutter.
11. **Module-Specific Responsibility Allocation (SRP Invariant)**: Each subsystem is strictly quarantined according to the Single Responsibility Principle: ExecutionService is solely responsible for calculation lifecycle, ReportService solely for report artifacts, ExportService solely for format conversions, BlueprintTransformer solely for read-only SDUI projection, background workers for isolated Arq execution, and API routers for their specific bounded contexts.
12. **God Code Decomposition & Subpackage Isolation (/tier3-god-code-decomposition)**: Monolithic files exceeding 500 lines (`backend_v2/worker.py` with 1,915 lines and `backend_v2/services/execution.py` with 1,468 lines) are proactively decomposed into clean subdirectories (`backend_v2/workers/` and `backend_v2/services/`). The Strangler Fig Proxy Pattern with PEP 484 explicit re-exports (`__all__` and redundant aliases) preserves 100% backward compatibility and satisfies `mypy --strict` during phased consumer migration.

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

### 4. Desktop-Class Pro Tool UX (Flutter Client)
The Execution Reports View (`ExecutionReportsView`) implements the desktop interaction ergonomics codified in @[ki_desktop_pro_tool_studio_ux.md]:
- **Adaptive Master Selector Standard**:
  - *Wide Viewports (`maxWidth >= 900px`)*: Lateral Master-Detail layout with a sticky 260px sidebar (`ReportArtifactCard` list with live status badges, profile pills, and locale tags) flanking the active detail canvas.
  - *Compact Viewports (`maxWidth < 900px`)*: Adaptive Top-Bar Selector (`SingleChildScrollView(scrollDirection: Axis.horizontal)` with `ChoiceChip` selectors and an inline `+ Uusi tuloste` button).
- **Single Cognitive Unit Isolation**: The main viewing canvas renders exactly ONE selected report artifact at a time.
- **Progressive Disclosure**: Multi-tab detail canvas: "Interaktiivinen näkymä" (SDUI), "PDF-esikatselu", "Rividata & Taulukot", "Metatiedot & Todisteet".
- **Header Containment**: All title and metadata labels wrapped in `Expanded(child: Text(..., overflow: TextOverflow.ellipsis))` to eliminate `RenderFlex` overflow on window resize.
- **Dual-Shield FormField Architecture & Modal Dismissal Protocol**: `CreateReportDialog` intercepts `Esc` and close buttons via `PopScope`, evaluates serialized dirty state inside `addPostFrameCallback`, and prompts with localized `AlertDialog` confirmation, supporting `Ctrl + S` / `Cmd + S` rapid submission.

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
   - *Responsibility*: SSOT configuration recipes (synthesis directives, tone instructions, SDUI component sequences). Fully cleansed of raw prompt block IDs (`variance_target_block`, `user_role_target_block`).
5. **Architectural Enforcement & Invariants**:
   - **`extra="forbid"` Everywhere**: Every model without exception configures `model_config = ConfigDict(strict=True, extra="forbid")`. Passing an execution field to a report DTO or vice versa raises an audible `ValidationError`.
   - **Zero Naked Dicts**: `dict[str, Any]` and `TypedDict` are banned from domain state transit. Every nested structure is an explicit, immutable Pydantic V2 model.
   - **Full-Duplex Serialization Parity**: Every Python Pydantic V2 model has a 1:1 typed Dart Freezed counterpart in Flutter (`@Freezed(equal: false)`) with matching `snake_case` $\leftrightarrow$ `camelCase` `@JsonKey` mappings.

---

### 8. Module-Specific Responsibility Allocation & God Code Decomposition Architecture (SRP & DDD)

To eradicate monolithic God Files and prevent cross-cutting architectural entanglement, the entire execution and reporting subsystem is partitioned according to the Single Responsibility Principle (SRP) and Domain-Driven Design (DDD) bounded contexts.

#### 1. Single Responsibility Principle (SRP) Responsibility Matrix

| Osa-alue | Vanha monoliitti | Uusi Tripartite-rakenne | Vastuu ja eristys |
| :--- | :--- | :--- | :--- |
| **Laskentapalvelut** | `ExecutionService` (1 468 riviä monoliitti) | `backend_v2/services/execution/` (Mikropalvelut, jokainen <180 riviä) | **Pilkotut elinkaaripalvelut**:<br>1. `ExecutionLifecycleService` (~180 riviä, `lifecycle_service.py`): Elinkaaren hallinta ja koordinointi (`list_executions`, `get_execution`, `delete_execution`, `cancel_execution`).<br>2. `ExecutionIngressService` (~180 riviä, `ingress_service.py`): Syötteiden validointi (`SmartIngressResolver`), dokumenttiliitteet, SDUI-vihjeet ja `create_execution_record`.<br>3. `ExecutionResumptionService` (~120 riviä, `resumption_service.py`): Ajon jatkamiskelpoisuus (`check_resumability`), FinOps-tarkistus ja uudelleenkäynnistys.<br>4. `ExecutionOverrideService` (~140 riviä, `override_service.py`): Ihmiskorjaukset (`override_atom`), todisteiden hylkäys ja pisteiden uudelleenlaskenta.<br>5. `ExecutionStreamService` (~80 riviä, `stream_service.py`): SSE-tilavirran striimaus (`stream_status`).<br>6. `FrozenContextService` (~50 riviä, `context_service.py`): Oikeusforensiikan jäädytetyn kontekstin luku.<br>*(Juuren `services/execution.py` säilyy <80 rivin Strangler Fig -julkisivuna explicit re-exportilla).* |
| **Ydintietomallit** | `v2_core.py` (1 845 riviä megamonoliitti) | `backend_v2/models/domain/` (DDD-alueet, jokainen <300 riviä) | **Tripartite-jaetut domain-mallit**:<br>1. `domain/matrix.py` (~260 riviä): Phase 1 matriisit ja väitteet.<br>2. `domain/execution.py` (~250 riviä): Phase 1 laskennan tila ja elinkaari.<br>3. `dtos/atom_result.py` (~110 riviä): Phase 1 atomien tulokset.<br>4. `domain/synthesis.py` (~160 riviä): Phase 2 synteesit ja XAI.<br>5. `domain/output_profile.py` (~300 riviä): Phase 3 esitysprofiili.<br>6. `domain/report_artifact.py` (~90 riviä): Phase 3 raporttientiteetti.<br>7. `dtos/report_data.py` (~80 riviä): Phase 3 SDUI-kuori.<br>8. `domain/workflow.py` (~160 riviä) & `domain/step.py` (~260 riviä): Studio-mallit.<br>9. `domain/system_config.py` (~140 riviä): FinOps ja MCP.<br>*(Juuren `v2_core.py` säilyy <90 rivin Strangler Fig -julkisivuna explicit re-exportilla).* |
| **Tulostuspalvelu** | Sekaisin `execution.py` ja `worker.py` | `ReportService` [NEW] (~250 riviä) | **Vain raporttien elinkaari**: Luo ja hallinnoi `ReportArtifact`-tietueita, koordinoi taustagenerointia, hakee pre-compiloidut tiedostot levyltä/oliolevyltä, B2B-taulukkorivien generointi ja uudelleengenerointi. |
| **Tiedostovienti** | Piilotettu `execution.py`:hyn | `ExportService` [NEW] (~150 riviä) | **Vain tiedostomuunnokset**: Puhdas konvertteri: `ReportDataDTO` $\rightarrow$ monivälilehtinen Excel ja flat CSV backendin omalla `I18nText`-kielistyksellä. Ei koskaan lue frontendin `.arb`-tiedostoja. |
| **Esitysmuunnin** | `BlueprintTransformer` (kirjoitti kantaan!) | `BlueprintTransformer` (Puhdas funktio) | **Vain SDUI-näkymä**: 100 % read-only. Muuntaa lasketut matriisit ja faktat visuaalisiksi näkymälohkoiksi tallentamatta kantaan yhtään mitään (`update_execution` poistettu täysin). |
| **Taustatyöt** | `worker.py` (1 915 riviä sekasotkua) | Eristetyt Arq-tehtävät (`backend_v2/workers/`) | `execute_workflow_job` ajaa vain Phase 1:n ja sulkeutuu. `generate_report_artifact_job` suorittaa vain raportoinnin. `worker.py` toimii ohuena Strangler Fig -julkisivuna (<150 riviä). |
| **API-rajapinnat** | Kaikki `/executions`-reitittimessä | `executions.py` and `reports.py` [NEW] | **Selkeä jako**: `/api/v2/executions` käsittelee laskentaa, `/api/v2/reports` käsittelee tulosteita ja B2B-rividataa. |
| **Käyttöliittymä** | `ExecutionView` (kaikki samassa ruudussa) | `ExecutionView` + `ExecutionReportsView` [NEW] | Käyttäjä katsoo ajon aikana laskennan edistymistä, ja tuloste avataan erilliseen Pro Tool -raportointinäkymään Adaptive Master Selector -standardin mukaisesti. |

#### 2. God Code Decomposition Protocol (/tier3-god-code-decomposition Style)

Adhering strictly to @[ki_god_code_prevention.md] and `/tier3-god-code-decomposition`, the decomposition of the system's monoliths (`backend_v2/worker.py` with 1,915 lines, `backend_v2/services/execution.py` with 1,468 lines, and `backend_v2/models/v2_core.py` with 1,845 lines) follows the Strangler Fig Pattern:

1. **Worker Decomposition (`backend_v2/workers/`)**:
   - **`[NEW] backend_v2/workers/__init__.py`**: Subpackage initialization and explicit export facade.
   - **`[NEW] backend_v2/workers/execution_worker.py` (~400 lines)**:
     - Extracted strictly from `worker.py` lines 136–544.
     - Houses `execute_workflow_job`.
     - Operates strictly on Phase 1 DAG execution, topological scoring, token usage accumulation, and transitions directly to `ExecutionStatus.PASSED`.
     - Completely blind to `ReportService`, PDF engines, and report jobs. Zero AST imports or task enqueues targeting Phase 2/3.
   - **`[NEW] backend_v2/workers/report_worker.py` (~450 lines)**:
     - Extracted strictly from `worker.py` lines 547–1816.
     - Houses `generate_report_artifact_job`, `generate_pdf_task`, `render_profile_job`, and `generate_profile_synthesis_and_pdf_task`.
     - Handles Phase 2 LLM synthesis (executive summaries, cognitive variance explanations, XAI highlights, Harvard citations) and Phase 3 WeasyPrint PDF compilation.
     - Enforces Failure Isolation: presentation and synthesis errors update `ReportArtifact.status = ReportStatus.FAILED`, never polluting `ExecutionRecord.status`.
   - **`[MODIFY] backend_v2/worker.py` (Strangler Fig Facade & Entrypoint, <150 lines)**:
     - Retains Arq lifecycle functions: `startup`, `shutdown`, `health_check`, and `WorkerSettings`.
     - Imports `execute_workflow_job` from `backend_v2.workers.execution_worker` and report tasks from `backend_v2.workers.report_worker`.
     - **MyPy Strict Re-Export Enforcement**: Explicitly re-exports all legacy public symbols via `__all__ = [...]` and redundant aliases (`from backend_v2.workers.execution_worker import execute_workflow_job as execute_workflow_job`) to satisfy PEP 484 and prevent `[attr-defined]` / `implicit re-export` errors in CI/CD quality gates.
     - Ensures downstream entry points specifically `backend_v2/run_worker.py` continue functioning without disruption.

2. **Execution Service Decomposition (`backend_v2/services/execution/`)**:
   To eradicate the 1,468-line monolith and guarantee that no single service exceeds the 200-line limit mandated in @[ki_god_code_prevention.md], the execution service layer is decomposed into a dedicated `backend_v2/services/execution/` subpackage composed of single-responsibility micro-services:
   - **`[NEW] backend_v2/services/execution/__init__.py`**: Subpackage initialization and explicit export facade.
   - **`[NEW] backend_v2/services/execution/lifecycle_service.py` (~180 lines)**:
     - Encapsulates tenant-isolated execution lifecycle operations: `list_executions` (with concurrent resumability evaluation), `get_execution` (with permission checks), `delete_execution` (with storage cleanup), and `cancel_execution`.
   - **`[NEW] backend_v2/services/execution/ingress_service.py` (~180 lines)**:
     - Encapsulates execution startup: workflow validation, FinOps quota verification (`usage_service.check_quota`), dynamic input slot resolution via `SmartIngressResolver`, document attachment extraction via `DocumentExtractionService`, dynamic synchronous SDUI hint generation (`DataDictionaryField`), and type-safe record factory instantiation (`create_execution_record`). Enqueues `execute_workflow_job` in Arq Redis.
   - **`[NEW] backend_v2/services/execution/resumption_service.py` (~120 lines)**:
     - Encapsulates execution resumption: `check_resumability` (evaluates FAILED state, checkpoint history, DAG version parity, and FinOps quota) and `resume_execution` (re-enqueues job into worker pool).
   - **`[NEW] backend_v2/services/execution/override_service.py` (~140 lines)**:
     - Encapsulates human-in-the-loop modifications: `override_atom` (updates `scorecard_atoms` and `step_states`, triggers hook recalculation via `recalculate()`, and appends `evidence_override` trace event) and `reject_evidence_quote`.
   - **`[NEW] backend_v2/services/execution/stream_service.py` (~80 lines)**:
     - Encapsulates Server-Sent Events (SSE) status streaming: `stream_status` with connection authorization, JSON formatting (`data: ...`), retry backoff, and error event emission.
   - **`[NEW] backend_v2/services/execution/context_service.py` (~50 lines)**:
     - Encapsulates forensic snapshot access: `get_frozen_context_bytes` (reads from `StorageDriver` or in-memory snapshot, formats JSON for audit).
   - **`[MODIFY] backend_v2/services/execution.py` (Strangler Fig Facade, <80 lines)**:
     - Composes the decomposed services into a unified `ExecutionService` class and provides explicit PEP 484 re-exports (`__all__ = ["ExecutionService", "create_execution_record", ...]`) and redundant aliases (`from backend_v2.services.execution.ingress_service import create_execution_record as create_execution_record`), ensuring 100% backward compatibility for all existing callers and unit tests.

3. **Reporting and Export Services (`backend_v2/services/`)**:
   - **`[NEW] backend_v2/services/report_service.py` (~250 lines)**:
     - Ingests `IReportArtifactRepository`, `IExecutionRepository`, `IOutputProfileRepository`, and `StorageDriver`.
     - Implements complete `ReportArtifact` lifecycle: `create_report_artifact_entry`, `process_artifact_compilation`, `get_report_sdui`, `get_report_pdf_bytes`, `get_report_excel_bytes`, `get_report_csv_bytes`, `get_report_rows`, `delete_report_artifact`, and `regenerate_report_artifact`.
     - Operates strictly downstream of completed Phase 1 executions.
   - **`[NEW] backend_v2/services/export_service.py` (~150 lines)**:
     - Pure functional converter converting `ReportDataDTO` into multi-tab Excel workbooks (`Summary` and `Raw Data`) and flat CSV bytes.
     - Resolves column headers strictly from backend `I18nText` database records and static dictionaries, eliminating all client `.arb` reads.

4. **Core Domain Model Decomposition (`backend_v2/models/v2_core.py` -> `backend_v2/models/domain/`)**:
   Adhering to @[ki_tripartite_pipeline_architecture.md], @[ki_god_code_prevention.md], and @[.agents/workflows/tier3-god-code-decomposition.md], the 1,845-line `backend_v2/models/v2_core.py` monolith is decomposed across the 3 Tripartite Phases and Studio Bounded Contexts:
   - **Phase 1 (Execution & Matrix Engine)**:
     - `[NEW] backend_v2/models/domain/matrix.py` (~260 lines): `TheoryGrounding`, `AcceptanceCriterion`, `AntiPattern`, `ContrastivePairDTO`, `TDAAssertion`, `MatrixClaim`, `MatrixRow`, `MatrixScale`.
     - `[NEW] backend_v2/models/domain/execution.py` (~250 lines): `ExecutionRecord`, `ExecutionStep`, `ExecutionSummarySnapshot`, `ExecutionCreate`, `FrozenContext`, `JobAcceptedDTO`, `EvidenceRejectionRequest`.
     - `[NEW] backend_v2/models/dtos/atom_result.py` (~110 lines): `AtomResultDTO`, `ExtractedValueDTO`, `HydratedAtomDTO`, `ErrorDetailsDTO`, `ExecutionMetricsDTO`, `ExtensionMetricsDTO`.
   - **Phase 2 (Synthesis & XAI)**:
     - `[MODIFY] backend_v2/models/domain/synthesis.py` (~160 lines): Consolidates `MatrixSynthesisGroup`, `RenderedSynthesisCache`, `BaseMatrixXAI`, `BaseTDAExtraction`.
   - **Phase 3 (SDUI & Presentation / Reports)**:
     - `[MODIFY] backend_v2/models/domain/output_profile.py` (~300 lines): Elevates from a 10-line re-export stub to the authoritative `OutputProfile` domain model (cleansed of `variance_target_block` and `user_role_target_block`).
     - `[NEW] backend_v2/models/domain/report_artifact.py` (~90 lines): Dedicated domain entity for `ReportArtifact` with storage paths, metadata, and status.
     - `[NEW] backend_v2/models/dtos/report_data.py` (~80 lines): Pure presentation envelope `ReportDataDTO`.
   - **Studio & Platform Bounded Contexts**:
     - `[NEW] backend_v2/models/domain/workflow.py` (~160 lines): `Workflow` domain model (cleansed of dead-weight `allowed_exports`).
     - `[NEW] backend_v2/models/domain/step.py` (~260 lines): `Step`, `StepRule`, `Role`, `QuestionnaireItem`, `ExpectedInput`.
     - `[NEW] backend_v2/models/domain/system_config.py` (~140 lines): `ModelProfile`, `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `AllowedMCPTool`, `MCPAuditTrace`, `ChatMessageDTO`, `ChatHistoryDTO`, `DataDictionaryField`, `ProviderExtraParamsDTO`.
   - **Strangler Fig Proxy Facade (`[MODIFY] backend_v2/models/v2_core.py`, <90 lines)**:
     - Imports all extracted models from `backend_v2.models.domain.*` and `backend_v2.models.dtos.*`.
     - Explicitly exports all 42 symbols via `__all__ = [...]` and redundant aliases (`from backend_v2.models.domain.execution import ExecutionRecord as ExecutionRecord`), guaranteeing 100% backward compatibility for all 250+ existing callers and satisfying PEP 484 and `mypy --strict`.

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
- `[NEW]` @[backend_v2/workers/execution_worker.py] - Extracted from `worker.py` lines 136–544; Phase 1 DAG execution background task (`execute_workflow_job`), <400 lines.
- `[NEW]` @[backend_v2/workers/report_worker.py] - Extracted from `worker.py` lines 547–1816; Phase 2 & 3 report artifact compilation (`generate_report_artifact_job`, `generate_pdf_task`, `render_profile_job`, `generate_profile_synthesis_and_pdf_task`), <450 lines.
- `[MODIFY]` @[backend_v2/worker.py] - Strangler Fig entrypoint & facade (<150 lines); configures `WorkerSettings`, registers Arq tasks, and explicitly re-exports all public symbols via `__all__` to satisfy PEP 484 and `mypy --strict`.
- `[NEW]` @[backend_v2/services/execution/__init__.py] - Subpackage initialization and explicit export facade for calculation services.
- `[NEW]` @[backend_v2/services/execution/lifecycle_service.py] - Tenant-isolated execution lifecycle operations (`list_executions`, `get_execution`, `delete_execution`, `cancel_execution`), ~180 lines.
- `[NEW]` @[backend_v2/services/execution/ingress_service.py] - Execution startup: `SmartIngressResolver`, document attachments, dynamic SDUI hints generation, `create_execution_record`, and Arq job enqueuing, ~180 lines.
- `[NEW]` @[backend_v2/services/execution/resumption_service.py] - Resumption and checkpoint validation: `check_resumability` and `resume_execution`, ~120 lines.
- `[NEW]` @[backend_v2/services/execution/override_service.py] - Human-in-the-loop modifications: `override_atom`, `reject_evidence_quote`, and scoring hook recalculation, ~140 lines.
- `[NEW]` @[backend_v2/services/execution/stream_service.py] - Server-Sent Events (SSE) status streaming (`stream_status`), ~80 lines.
- `[NEW]` @[backend_v2/services/execution/context_service.py] - Forensic snapshot retrieval (`get_frozen_context_bytes`), ~50 lines.
- `[MODIFY]` @[backend_v2/services/execution.py] - Strangler Fig facade (<80 lines) composing execution services and providing explicit PEP 484 re-exports (`__all__`) for 100% backward compatibility.
- `[NEW]` @[backend_v2/services/export_service.py] - Extracted from `execution.py` lines 769–965 (~150 lines); pure converter from `ReportDataDTO` to multi-tab Excel and flat CSV using backend `I18nText` SSOT.
- `[NEW]` @[backend_v2/services/report_service.py] - Extracted from `execution.py` lines 1130–1348 (~250 lines); manages full `ReportArtifact` lifecycle, Cloud-Native Object Storage coordination, row-level data extraction, and regeneration.
- `[MODIFY]` @[backend_v2/services/blueprint.py#L62-L588] - Make `BlueprintTransformer` 100% read-only; eradicate `update_execution` and recursive dict scraping.
- `[MODIFY]` @[backend_v2/models/dtos/trace.py#L40-L57] - Update `ExecutionCreateDTO` to declare `output_profile_id: Annotated[str | None, Field(default=None)] = None`.
- `[MODIFY]` @[backend_v2/models/v2_core.py] - Decompose 1,845-line monolith into single-responsibility domain models; refactor into a thin Strangler Fig Facade (<90 lines) with PEP 484 explicit re-exports (`__all__` and redundant aliases) to ensure zero broken imports codebase-wide.
- `[NEW]` @[backend_v2/models/domain/workflow.py] (~160 lines) - Houses `Workflow` domain model; completely cleansed of `allowed_exports`, with `default_profile_id` optional.
- `[NEW]` @[backend_v2/models/domain/step.py] (~260 lines) - Houses `Step`, `StepRule`, `Role`, `QuestionnaireItem`, `ExpectedInput`.
- `[NEW]` @[backend_v2/models/domain/matrix.py] (~260 lines) - Tripartite Phase 1 evaluation models: `TheoryGrounding`, `AcceptanceCriterion`, `AntiPattern`, `ContrastivePairDTO`, `TDAAssertion`, `MatrixClaim`, `MatrixRow`, `MatrixScale`.
- `[NEW]` @[backend_v2/models/domain/execution.py] (~250 lines) - Tripartite Phase 1 runtime models: `ExecutionRecord`, `ExecutionStep`, `ExecutionSummarySnapshot`, `ExecutionCreate`, `FrozenContext`, `JobAcceptedDTO`, `EvidenceRejectionRequest`.
- `[NEW]` @[backend_v2/models/dtos/atom_result.py] (~110 lines) - Tripartite Phase 1 atom evaluation DTOs: `AtomResultDTO`, `ExtractedValueDTO`, `HydratedAtomDTO`, `ErrorDetailsDTO`, `ExecutionMetricsDTO`, `ExtensionMetricsDTO`.
- `[MODIFY]` @[backend_v2/models/domain/synthesis.py] (~160 lines) - Tripartite Phase 2 synthesis models: Consolidates `MatrixSynthesisGroup`, `RenderedSynthesisCache`, `BaseMatrixXAI`, `BaseTDAExtraction`.
- `[MODIFY]` @[backend_v2/models/domain/output_profile.py] (~300 lines) - Tripartite Phase 3 presentation profile: Elevate from 10-line re-export stub to canonical `OutputProfile` domain model; cleansed of `variance_target_block` and `user_role_target_block`.
- `[NEW]` @[backend_v2/models/domain/report_artifact.py] (~90 lines) - Tripartite Phase 3 report entity: Declare `ReportArtifact` domain entity with storage paths, metadata, and status (instead of polluting `v2_core.py`).
- `[NEW]` @[backend_v2/models/dtos/report_data.py] (~80 lines) - Tripartite Phase 3 SDUI envelope: Houses canonical `ReportDataDTO`.
- `[NEW]` @[backend_v2/models/domain/system_config.py] (~140 lines) - Platform & FinOps configurations: `ModelProfile`, `SystemConfigModelRegistry`, `SystemConfigMCPGateways`, `AllowedMCPTool`, `MCPAuditTrace`, `ChatMessageDTO`, `ChatHistoryDTO`, `DataDictionaryField`, `ProviderExtraParamsDTO`.
- `[NEW]` @[backend_v2/models/dtos/report_artifact.py] - Declare strict Pydantic V2 DTOs: `ReportArtifactCreateDTO`, `ReportArtifactUpdateDTO`, `ReportArtifactSummaryDTO`, `ReportStoragePathsDTO`, `ReportRowItemDTO`, `PublicReportDTO`.
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

## Pre-Implementation Technical Debt Cleanups (Scoped Boy Scout)

1. **Eradicate Database Write in Blueprint Transformer**:
   In @[backend_v2/services/blueprint.py#L62-L588] (`build_report_dto`), `BlueprintTransformer.build_report_dto` mutates `execution.step_states` via `await self.exec_repo.update_execution(...)`. This must be removed completely. The transformer receives an immutable snapshot and returns a pure `ReportDataDTO`. Any state adjustments for human overrides must happen in `ExecutionService.override_atom`, never inside a presentation builder.
2. **Eradicate Recursive Sanity Traversal**:
   In @[backend_v2/services/blueprint.py#L62-L588] (`build_report_dto`), `extract_evidence_ids` uses recursive `isinstance(payload_data, dict)` traversal. This must be replaced with typed extraction against `MCPAuditTrace` and `AtomResultDTO` structures.
3. **Eradicate Direct Frontend `.arb` Reading**:
   In @[backend_v2/services/execution.py] (`get_execution_export_bytes`), the backend opens `client_app_v2/lib/l10n/app_{locale}.arb` directly using `json.load`. This breaks architectural layer isolation and must be replaced with backend translation dictionaries or `I18nText` keys.
4. **Purge Dead-Weight Ghost Field `allowed_exports`**:
   Forensic audit confirmed that `Workflow.allowed_exports` is accessed 0 times across backend business logic, 0 times in background workers, and 0 times in Flutter UI widgets or screens. It is not stored in `seed_data.json`. It is dead weight that must be deleted from `v2_core.py` and Flutter `workflow.dart` without being relocated anywhere.

---

## Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PRE_IMPLEMENTATION_CLEANUPS_CORE_MODEL_DECOMPOSITION_AND_DTO_LOCK">
    <action>Modify @[backend_v2/models/dtos/trace.py#L40-L57] to make output_profile_id optional:
      - Change output_profile_id to Annotated[str | None, Field(default=None, description="Optional presentation profile identifier")].
      - Ensure ConfigDict(strict=True, extra="forbid") is preserved.
    </action>
    <action>Decompose monolithic @[backend_v2/models/v2_core.py] (1,845 lines) into cohesive domain models under backend_v2/models/domain/ and backend_v2/models/dtos/:
      - Create [NEW] @[backend_v2/models/domain/workflow.py] (~160 lines): Extract Workflow. Completely purge allowed_exports. Make default_profile_id optional (Annotated[str | None, Field(default=None)]).
      - Delete allowedExports completely from Workflow in @[client_app_v2/lib/features/studio/models/workflow.dart].
      - Create [NEW] @[backend_v2/models/domain/step.py] (~260 lines): Extract Step, StepRule, Role, QuestionnaireItem, ExpectedInput.
      - Create [NEW] @[backend_v2/models/domain/matrix.py] (~260 lines): Extract TheoryGrounding, AcceptanceCriterion, AntiPattern, ContrastivePairDTO, TDAAssertion, MatrixClaim, MatrixRow, MatrixScale.
      - Create [NEW] @[backend_v2/models/domain/execution.py] (~250 lines): Extract ExecutionRecord, ExecutionStep, ExecutionSummarySnapshot, ExecutionCreate, FrozenContext, JobAcceptedDTO, EvidenceRejectionRequest.
      - Create [NEW] @[backend_v2/models/dtos/atom_result.py] (~110 lines): Extract AtomResultDTO, ExtractedValueDTO, HydratedAtomDTO, ErrorDetailsDTO, ExecutionMetricsDTO, ExtensionMetricsDTO.
      - Modify @[backend_v2/models/domain/synthesis.py] (~160 lines): Consolidate MatrixSynthesisGroup, RenderedSynthesisCache, BaseMatrixXAI, BaseTDAExtraction.
      - Modify @[backend_v2/models/domain/output_profile.py] (~300 lines): Elevate from 10-line stub to canonical OutputProfile domain model. Purge variance_target_block, user_role_target_block, and validate_variance_target_block_coherence.
      - Synchronize @[backend_v2/models/dtos/output_profile.py]: Remove variance_target_block and user_role_target_block from OutputProfileCreateDTO and OutputProfileUpdateDTO.
      - Create [NEW] @[backend_v2/models/dtos/report_data.py] (~80 lines): Extract ReportDataDTO.
      - Create [NEW] @[backend_v2/models/domain/system_config.py] (~140 lines): Extract ModelProfile, SystemConfigModelRegistry, SystemConfigMCPGateways, AllowedMCPTool, MCPAuditTrace, ChatMessageDTO, ChatHistoryDTO, DataDictionaryField, ProviderExtraParamsDTO.
      - Refactor @[backend_v2/models/v2_core.py] into a thin Strangler Fig Facade (<90 lines): Re-exports all 42 public symbols with explicit __all__ = [...] and redundant aliases (specifically: from backend_v2.models.domain.workflow import Workflow as Workflow) to satisfy PEP 484 and mypy --strict.
    </action>
    <constraint invariant="zero_permissive_typing">
      DTO models must enforce ConfigDict(strict=True, extra="forbid"). No naked dictionaries, legacy ghost fields, or loose optional bypasses.
    </constraint>
    <constraint invariant="god_code_prevention">
      Every decomposed domain model file is strictly under 350 lines adhering to ki_god_code_prevention.md. Root v2_core.py is a thin Strangler Fig facade under 90 lines.
    </constraint>
  </step>

  <step id="2" name="INGRESS_DECOUPLING_IN_EXECUTION_SERVICE">
    <action>Modify @[backend_v2/services/execution.py#L385-L614] in start_execution:
      - Remove the fail-fast exception that halts execution if workflow.default_profile_id and payload.profile_id are absent.
      - If payload.profile_id is provided, resolve and validate it against repository. If absent, fallback to workflow.default_profile_id if present; otherwise resolve to None.
      - Instantiate ExecutionCreateDTO with output_profile_id=resolved_profile_id (which may be None).
      - Ensure initial ExecutionRecord creates cleanly without requiring an OutputProfile instance when profile is None.
    </action>
    <constraint invariant="universal_fail_fast">
      If a specific profile_id is explicitly provided by the caller but not found in the database, raise AppException with ErrorCodes.RESOURCE_NOT_FOUND. Do NOT fall back silently.
    </constraint>
  </step>

  <step id="3" name="WORKER_DECOMPOSITION_AND_LIFECYCLE_ISOLATION">
    <action>Execute AST boundary analysis on @[backend_v2/worker.py] to verify exact line bounds of execute_workflow_job, generate_pdf_job, generate_pdf_task, render_profile_job, and generate_profile_synthesis_and_pdf_task.</action>
    <action>Create [NEW] subpackage @[backend_v2/workers/__init__.py] with public worker exports.</action>
    <action>Create [NEW] file @[backend_v2/workers/execution_worker.py] (<400 lines):
      - Extract execute_workflow_job from worker.py lines 136–544.
      - Upon completion of DAG execution and topological scoring, calculate duration_ms and finalize telemetry metrics.
      - Set execution status directly: update_dto = ExecutionUpdateDTO(status=ExecutionStatus.PASSED, completed_at=datetime.now(UTC), ...).
      - Delete lines injecting v_step_id = f"sys_render_{profile_id}" and label="Generating Output Report" into updated_exec_record.steps and step_states.
      - Eradicate worker-to-worker auto-enqueuing: execute_workflow_job MUST NEVER enqueue render_profile_job or generate_report_artifact_job. It purely sets status=ExecutionStatus.PASSED, updates the execution record in the repository, publishes the execution_status_changed event to Redis pubsub/SSE, and immediately terminates.
      - Enforce Zero-Import Boundary: execute_workflow_job contains 0 imports and 0 calls referencing ReportService, export_service, or report queue tasks.
      - Persist ExecutionStatus.PASSED immediately. The execution is finished from Phase 1 perspective.
    </action>
    <action>Create [NEW] file @[backend_v2/workers/report_worker.py] (<450 lines):
      - Extract generate_pdf_job, generate_pdf_task, render_profile_job, and generate_profile_synthesis_and_pdf_task from worker.py lines 547–1816.
      - Register generate_report_artifact_job(ctx, report_id: str) delegating directly to report_service.process_artifact_compilation.
      - In generate_pdf_task and profile synthesis error handling, quarantine failures: log error with ErrorCodes.PDF_GENERATION_FAILED, update only ReportArtifact.status=ReportStatus.FAILED, and delete the database update that stamped ExecutionRecord.status = ExecutionStatus.FAILED.
    </action>
    <action>Refactor @[backend_v2/worker.py] into a thin Strangler Fig Facade & Entrypoint (<150 lines):
      - Retain Arq lifecycle functions: startup, shutdown, health_check, and WorkerSettings.
      - Import execute_workflow_job from backend_v2.workers.execution_worker.
      - Import generate_report_artifact_job, generate_pdf_job, generate_pdf_task, render_profile_job, generate_profile_synthesis_and_pdf_task from backend_v2.workers.report_worker.
      - Enforce PEP 484 and MyPy Strict explicit re-exports: declare __all__ = ["execute_workflow_job", "generate_report_artifact_job", "generate_pdf_job", "generate_pdf_task", "render_profile_job", "generate_profile_synthesis_and_pdf_task", "WorkerSettings", "startup", "shutdown", "health_check"] and redundant aliases (from ... import func as func).
    </action>
    <constraint invariant="tripartite_phase_isolation">
      Phase 3 rendering failures MUST NEVER mutate Phase 1 ExecutionRecord.status to FAILED. An analytical run remains PASSED once DAG evaluations succeed.
    </constraint>
    <constraint invariant="god_code_prevention">
      No worker file may exceed 500 lines. The root worker.py acts purely as an Arq entry point and backwards-compatible re-export facade under 150 lines.
    </constraint>
  </step>

  <step id="4" name="MAKE_BLUEPRINT_TRANSFORMER_READ_ONLY">
    <action>Modify @[backend_v2/services/blueprint.py#L62-L588]:
      - Delete lines where new_step_states are updated and exec_repo.update_execution is invoked.
      - Remove self.exec_repo write access from build_report_dto. The transformer must only read execution data.
      - Replace extract_evidence_ids recursive dictionary search with direct iteration over structured mcp_audit_data items and AtomResultDTO used_evidence_ids.
      - Replace token re-summing trace iteration fallback with strict consumption of execution.prompt_tokens, completion_tokens, and reasoning_tokens.
      - In dynamic variance block resolution, if variance validation is requested in target_block_order, dynamically select the primary evaluative matrix block from parsed matrices instead of requiring static variance_target_block on the profile.
    </action>
    <constraint invariant="dumb_painter_invariance">
      Presentation transformers must be 100% idempotent, read-only functions mapping (ExecutionRecord, OutputProfile) to ReportDataDTO without side effects.
    </constraint>
  </step>

  <step id="5" name="EXTRACT_EXPORT_SERVICE_AND_ELIMINATE_ARB_LEAK">
    <action>Create [NEW] file @[backend_v2/services/export_service.py] (~150 lines) defining ExportService:
      - Implement ExportService with methods export_excel(execution: ExecutionRecord, report_dto: ReportDataDTO, locale: str) -> tuple[bytes, str].
      - Configure two dedicated Excel worksheets:
        1. 'Summary': High-level dimensional scores, global scores, and executive summary text.
        2. 'Raw Data': Tabular list of every evaluated atom, score, weight, quote, and causal reasoning.
      - Implement export_flat_csv(execution: ExecutionRecord, report_dto: ReportDataDTO) -> tuple[bytes, str] using FlatFileService.
      - Define static column header dictionaries in English and Finnish within the service or reference backend I18nText SSOT.
      - Eradicate open(client_app_v2/lib/l10n/app_{locale}.arb).
    </action>
    <action>Refactor @[backend_v2/services/execution.py#L769-L965]:
      - Purge legacy export logic and direct .arb reading from ExecutionService.
      - Inject ExportService into ExecutionService if temporary proxy delegation is required during migration, marking delegating methods with @deprecated.
    </action>
    <constraint invariant="god_code_prevention">
      Export logic must reside in a dedicated export module under 200 lines, keeping ExecutionService focused on calculation lifecycle.
    </constraint>
  </step>

  <step id="6" name="REPORT_ARTIFACT_DOMAIN_MODEL_AND_REPOSITORY_CRUD">
    <action>Create [NEW] file @[backend_v2/models/dtos/report_artifact.py]:
      - Define ReportStatus(StrEnum): PENDING, GENERATING, READY, FAILED.
      - Define ReportStoragePathsDTO(V2CoreBase): pdf_path: str | None = None, sdui_json_path: str | None = None, excel_path: str | None = None, csv_path: str | None = None.
      - Define ReportMetadataDTO(V2CoreBase): cost_usd: float | None = None, duration_ms: int | None = None, tokens_used: int | None = None, llm_model: str | None = None.
      - Define ReportRowItemDTO(V2CoreBase): execution_id: StrictStr, report_id: StrictStr, metric_key: StrictStr, metric_label: StrictStr, score: float, max_scale: float, weight: float, reasoning: str | None = None, quote: str | None = None.
      - Define PublicReportDTO(V2CoreBase): report_id: StrictStr, created_at: datetime, title: StrictStr, target_audience: StrictStr | None, overall_score: float | None, metrics: dict[str, float], executive_summary_markdown: str | None, downloads: dict[str, str].
      - Define ReportArtifactCreateDTO(V2CoreBase): execution_id: StrictStr, profile_id: StrictStr, locale: StrictStr = "fi", custom_preface_md: str | None = None.
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
    <action>Create [NEW] file @[backend_v2/services/report_service.py] (~250 lines) defining ReportService:
      - Coordinate full report artifact lifecycle:
        1. create_report_artifact_entry(payload: ReportArtifactCreateDTO) -> ReportArtifact
        2. compile_and_persist_artifact(report_id: str, arq_pool: ArqRedis) -> None (dispatches background compilation to generate_report_artifact_job)
        3. process_artifact_compilation(report_id: str) -> None:
           - Ingest execution and profile.
           - Build ReportDataDTO via BlueprintTransformer (Phase 3).
           - Serialize ReportDataDTO to JSON and persist to storage driver at 'artifacts/reports/{report_id}/report.sdui.json'.
           - Generate PDF bytes via PdfReportService and persist at 'artifacts/reports/{report_id}/report.pdf'.
           - Generate Excel bytes via ExportService and persist at 'artifacts/reports/{report_id}/report.xlsx'.
           - Generate Flat CSV bytes via ExportService and persist at 'artifacts/reports/{report_id}/report.csv'.
           - Update ReportArtifact record with status=READY and storage paths.
        4. get_report_sdui(report_id: str) -> ReportDataDTO: fetch from storage driver, model_validate to ReportDataDTO.
        5. get_report_pdf_bytes(report_id: str) -> bytes: stream from storage driver.
        6. get_report_excel_bytes(report_id: str) -> bytes: stream from storage driver.
        7. get_report_csv_bytes(report_id: str) -> bytes: stream from storage driver.
        8. get_report_rows(report_id: str) -> list[ReportRowItemDTO]: extract typed metric and atomic rows for B2B consumers.
        9. delete_report_artifact(report_id: str) -> None: delete database record AND all physical storage files via storage driver.
        10. regenerate_report_artifact(report_id: str, arq_pool: ArqRedis) -> None: reset status to GENERATING and re-enqueue worker job.
    </action>
    <action>Decompose @[backend_v2/services/execution.py] (1,468 lines) into dedicated subpackage backend_v2/services/execution/:
      - Create [NEW] @[backend_v2/services/execution/__init__.py]: Package export facade.
      - Create [NEW] @[backend_v2/services/execution/lifecycle_service.py] (~180 lines): Tenant-isolated execution lifecycle (list_executions, get_execution, delete_execution, cancel_execution).
      - Create [NEW] @[backend_v2/services/execution/ingress_service.py] (~180 lines): Execution startup, SmartIngressResolver slot mapping, document attachment extraction, dynamic SDUI hints generation, create_execution_record, and Arq job dispatch.
      - Create [NEW] @[backend_v2/services/execution/resumption_service.py] (~120 lines): Checkpoint history validation, DAG version parity, FinOps quota check, and resume_execution.
      - Create [NEW] @[backend_v2/services/execution/override_service.py] (~140 lines): Human override handling (override_atom, reject_evidence_quote), scorecard_atoms update, and hook recalculation.
      - Create [NEW] @[backend_v2/services/execution/stream_service.py] (~80 lines): SSE status streaming (stream_status) with retry backoff and error event emission.
      - Create [NEW] @[backend_v2/services/execution/context_service.py] (~50 lines): Forensic context retrieval (get_frozen_context_bytes).
      - Refactor @[backend_v2/services/execution.py] into a thin Strangler Fig Facade (<80 lines): Composes the sub-services into ExecutionService and provides explicit PEP 484 re-exports (__all__) for 100% backward compatibility.
      - Wire ReportService, ExportService, and ExecutionService in @[backend_v2/api/dependencies.py].
    </action>
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
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/models/report_artifact.dart]:
      - Define Freezed model ReportArtifact (@Freezed(equal: false)):
        id, executionId, workflowId, profileId, locale, title, status, storagePaths, errorMessage, createdAt, updatedAt.
      - Define Freezed model ReportArtifactSummary (@Freezed(equal: false)).
    </action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/views/widgets/report_artifact_card.dart]:
      - Build adaptive report card with profile badge, locale pill (FI/EN), creation timestamp, and status indicator (READY/GENERATING/FAILED).
      - Include quick action buttons: "Näytä ruudulla", "Lataa PDF", "Lataa Excel", "Päivitä", "Poista".
      - Adhere to Header Containment: wrap titles in Expanded(child: Text(..., overflow: TextOverflow.ellipsis)).
    </action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]:
      - Enclose in ConstrainedBox(constraints: BoxConstraints(minWidth: 480, maxWidth: 800, minHeight: 400)).
      - Include OutputProfile dropdown selector, Locale dropdown selector (FI/EN), and optional custom preface text area.
      - Implement Dual-Shield FormField Architecture & Modal Dismissal Protocol:
        1. Intercept Esc and close button with PopScope(canPop: false, onPopInvokedWithResult: ...).
        2. In _handleDismiss(), execute FocusScope.of(context).unfocus() and evaluate dirty state inside addPostFrameCallback.
        3. If dirty, prompt with localized AlertDialog confirmation ("Hylkää muutokset" vs "Jatka muokkausta").
        4. Support Ctrl + S / Cmd + S keyboard shortcut to trigger creation.
    </action>
    <action>Create [NEW] file @[client_app_v2/lib/features/reports/views/execution_reports_view.dart]:
      - Implement Adaptive Master Selector Standard (LayoutBuilder):
        1. Wide Viewports (maxWidth >= 900px): Lateral Master-Detail layout. Left pane: sticky 260px sidebar listing all ReportArtifactCard items for this execution, with a top '+ Uusi tuloste' action button. Right pane: focused detail canvas showing the active report.
        2. Compact Viewports (maxWidth < 900px): Adaptive Top-Bar Selector (SingleChildScrollView(scrollDirection: Axis.horizontal)) with ChoiceChip items for each report artifact and an inline '+ Uusi tuloste' button.
        3. Single Cognitive Unit Isolation: Exactly ONE report artifact is displayed in the main viewing canvas at a time.
        4. Progressive Disclosure Detail Canvas: Render tabs for "Interaktiivinen näkymä" (loads pre-compiled SDUI into SduiRenderer), "PDF-esikatselu", "Rividata & Taulukot" (shows metric rows), "Metatiedot & Todisteet".
        5. Action Bar: "Lataa PDF", "Lataa Excel", "Lataa CSV", "Päivitä tuloste" (re-run Phase 2/3), "Poista tuloste" (with AlertDialog confirmation).
    </action>
    <action>Modify @[client_app_v2/lib/features/execution/views/new_execution_view.dart]:
      - Add CheckboxListTile for autoGenerateReport: "[x] Generoi tuloste automaattisesti ajon valmistuttua (Aja tulosteeksi saakka)".
      - Default to true whenever _selectedProfileId is selected or workflow has default_profile_id.
      - Pass autoGenerateReport flag to controller/router context.
    </action>
    <action>Modify @[client_app_v2/lib/features/execution/views/execution_view.dart]:
      - When executionState reaches PASSED and autoGenerateReport is enabled:
        1. Show smooth progress transition: "Laskenta valmis (100%). Luodaan tulostetta...".
        2. Invoke POST /api/v2/executions/{id}/reports to trigger report compilation.
        3. Upon report generation (READY), auto-navigate or display the report canvas.
        4. If report compilation fails, preserve execution PASSED state and show actionable alert: "Tulosteen generointi epäonnistui, voit yrittää uudelleen".
    </action>
    <constraint invariant="cognitive_ergonomics_and_dual_pane_standard">
      Layout transitions between wide and compact must preserve selected report index and scroll positions. Banned unbounded vertical stacking is strictly forbidden.
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
        1. Test that root v2_core.py re-exports all 42 symbols matching PEP 484 and satisfies mypy --strict.
        2. Test that each re-exported domain model validates correctly with ConfigDict(strict=True, extra="forbid").
      - In @[backend_v2/tests/unit/services/test_blueprint.py]:
        1. Test that build_report_dto invokes zero update methods on exec_repo.
        2. Test that variance validation block renders without variance_target_block configured on profile.
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
      - Cleanse test fixtures in backend_v2/tests/ passing dummy allowed_exports to Workflow.
    </action>
    <action>Execute automated quality gates:
      - Run localized unit tests: uv run pytest backend_v2/tests/unit/workers/ backend_v2/tests/unit/test_worker_proxy.py backend_v2/tests/unit/services/execution/ backend_v2/tests/unit/services/test_execution_proxy.py backend_v2/tests/unit/services/test_blueprint.py backend_v2/tests/unit/services/test_export_service.py backend_v2/tests/unit/services/test_report_service.py backend_v2/tests/unit/api/test_reports_api.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py -v
      - Run global backend audit loop: uv run python scripts/backend_audit_loop.py backend_v2 --test
      - Regenerate Freezed models: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports/models/report_artifact.dart --build
      - Run Flutter frontend audit loop: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/reports --build
    </action>
    <constraint invariant="anti_happy_path_compliance">
      All new tests must explicitly test failure partitions: 1) missing profile, 2) nonexistent profile, 3) PDF generation failure, 4) non-existent report artifact deletion, 5) invalid API key on external row endpoint, 6) execution not in PASSED state when requesting report creation.
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
        2. Document complete eradication of allowed_exports from Workflow and variance_target_block / user_role_target_block from OutputProfile.
        3. Document B2B row-level tabular delivery and Public REST API integration.
        4. Document God Code decomposition of backend workers and execution services into subpackages according to SRP.
      - In @[docs/architecture/03_cognitive_orchestration_engine.md]:
        1. Update Section 2.7 (Asynchronous Background Workers & Non-Blocking Handshake) to document worker lifecycle completion setting ExecutionStatus.PASSED directly upon DAG topological sort finish and telemetry finalization.
        2. Document elimination of synthetic sys_render step injection from ExecutionRecord.steps and step_states.
        3. Document independent background enqueue of report artifact compilation jobs and subpackage decomposition into backend_v2/workers/execution_worker.py and backend_v2/workers/report_worker.py.
      - In @[docs/architecture/04_server_driven_ui_and_presentation.md]:
        1. Update Section 2.1 (Dumb Painter Pipeline) to document BlueprintTransformer 100% read-only dumb painter invariance with zero database mutation calls (update_execution).
        2. Update Section 2.4 (Database-Driven Target Block Dispatching) to document dynamic primary matrix resolution for variance validation without requiring static variance_target_block on OutputProfile.
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
- **Scenario C (Negative Path - Desktop Modal Dirty State Dismiss Interception)**: User changes profile/locale in `CreateReportDialog` and presses Esc.
  - *Input*: User edits dialog and presses Esc or clicks close icon.
  - *Expected Result*: `PopScope` intercepts dismissal, detects dirty state, and shows localized `AlertDialog`. If user chooses "Keep Editing", dialog remains mounted with intact form state.
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

---

## Verification Plan

### Automated Test Commands
1. **Targeted Unit Tests**:
   ```powershell
   uv run pytest backend_v2/tests/unit/workers/ -v
   uv run pytest backend_v2/tests/unit/test_worker_proxy.py -v
   uv run pytest backend_v2/tests/unit/services/test_blueprint.py -k "test_blueprint_read_only" -v
   uv run pytest backend_v2/tests/unit/services/test_execution.py -k "test_ingress_decoupled" -v
   uv run pytest backend_v2/tests/unit/services/test_export_service.py -v
   uv run pytest backend_v2/tests/unit/services/test_report_service.py -v
   uv run pytest backend_v2/tests/unit/api/test_reports_api.py -v
   uv run pytest backend_v2/tests/unit/test_rest_only_pipeline_boundary.py -v
   ```
2. **Full Domain Test Suite**:
   ```powershell
   uv run pytest backend_v2/tests/unit/workers/ backend_v2/tests/unit/test_worker_proxy.py backend_v2/tests/unit/services/test_blueprint.py backend_v2/tests/unit/services/test_execution.py backend_v2/tests/unit/services/test_export_service.py backend_v2/tests/unit/services/test_report_service.py backend_v2/tests/unit/api/test_reports_api.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py -v
   ```
3. **Universal Quality Gate (Linting, Formatting, Strict Typing, Pytest)**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2 --test
   ```
4. **Frontend Code Generation & Quality Gate**:
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
    - Document complete eradication of `allowed_exports` from `Workflow` and `variance_target_block` / `user_role_target_block` from `OutputProfile`.
- **@[docs/architecture/03_cognitive_orchestration_engine.md]**:
  - Update Section 2.7 (Asynchronous Background Workers & Non-Blocking Handshake):
    - Document worker lifecycle completion setting `ExecutionStatus.PASSED` directly upon DAG topological sort finish and telemetry finalization.
    - Document elimination of synthetic `sys_render` step injection from `ExecutionRecord.steps` and `step_states`.
    - Document independent background enqueue of report artifact compilation jobs.
- **@[docs/architecture/04_server_driven_ui_and_presentation.md]**:
  - Update Section 2.1 (Dumb Painter Pipeline):
    - Document `BlueprintTransformer` 100% read-only dumb painter invariance with zero database mutation calls (`update_execution`).
  - Update Section 2.4 (Database-Driven Target Block Dispatching):
    - Document dynamic primary matrix resolution for variance validation without requiring static `variance_target_block` on `OutputProfile`.
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
