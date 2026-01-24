# ðŸ—ºï¸ Cognitive Quorum - Product Roadmap (2026)

This document outlines the strategic roadmap for evolving Cognitive Quorum from a prototype into a scalable, multi-tenant B2B SaaS platform.

## ðŸ“Œ Status Legend
- [x] **Done**: Completed and integrated into `main`.
- [ ] **Pending**: To be implemented.
- [~] **In Progress**: Currently under active development.

---

## ðŸ Phase 0: Core Intelligence & Engine (âœ… Completed)
**Objective:** Build a robust, scientific-grade analysis engine capable of multi-agent reasoning.

### 0.0 Core Foundations (The "Brain")
- [x] **LLM Integration**: Implemented flexible `LLMProvider` (Gemini support) with structured JSON output enforcement.
- [x] **Workflow Engine**: Built the core sequential execution logic handling inputs, outputs, and step transitions.
- [x] **Step Architecture**: Defined modular step definitions (`step_judge`, `step_profiler`) in `seed_data.json`.
- [x] **Legacy UI**: (Deprecated) Initial Streamlit frontend used for prototyping. Replaced by Client App.

### 0.1 Async-First Architecture
- [x] **V3 Engine Refactor**: Transitioned from Synchronous to Asynchronous Blackboard Architecture.
- [x] **State Management**: Implemented `WorkflowState` with Pydantic V2 for type-safe data passing.
- [x] **Persistence Layer**: Created `AbstractWorkflowRepository` supporting both TinyDB and Firestore.

### 0.2 Intelligent Agent System
- [x] **Agent Registry**: Dynamic loading of AI Agents (Judge, Profiler, Extractor).
- [x] **Stereoscopic Vision**: Implemented "Dual Matrix" evaluation (Standard + Cognitive bias checks).
- [x] **Prompt Engineering**: Built a Jinja2-based dynamic prompt builder with "Baton" context passing.
- [x] **Reference Manager**: Automated citation and bibliography generation.

### 0.3 Backend Consolidation
- [x] **Router Refactoring**: Standardized API with `Annotated` dependencies (`EngineDep`, `DatabaseDep`).
- [x] **Strict DI**: Refactored `WorkflowEngine` to enforce manual dependency injection (Removed auto-wiring).
- [x] **Engine Generalization**: Removed business logic (Matrix limit, Bibliographies) from core Engine.
- [x] **Execution Separation**: Extracted `execute_workflow_task` from `run_execution` to prepare for Workers.
- [x] **Legacy Cleanup**: Removed deprecated synchronous routes and V2 artifacts.

---

## ðŸ“ Phase 1: SaaS Foundation (Backend Hardening)
**Objective:** Secure the backend, enforce multi-tenancy, and ensure the system is "Cloud Ready".
**Milestone:** Jan 13, 2026 - Absolute Triple Green (Ruff/Mypy/Tests) & V2.9 Standards enforced.

### 1.1 Authentication & Identity (âœ… Completed)
- [x] **Hybrid Auth Service**: Support for both Firebase Auth (Production) and Local Mock Auth (Dev).
- [x] **RBAC Implementation**: Defined Roles (`ROOT`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`).
- [x] **Organization Entity**: Implemented `Organization` model to support Multi-tenancy.
- [x] **User Management API**: Endpoints to create and list users within scope.
- [x] **System Admin UI**: Dashboard for ROOT to list/create organizations.
- [x] **Org Admin UI**: Dashboard for ADMIN to manage organization settings.
- [x] **Organization Deletion**: Implemented in API with safety checks for active jobs (Manual UI trigger pending).
- [x] **Last Admin Protection**: Prevent deletion of the last ADMIN in an organization (Implemented in `AuthService`).
- [x] **Primary Root Protection**: Prevent deletion of the `root_master` system account (Implemented in `AuthService`).

### 1.2 Data Isolation & Security (âœ… Completed)
- [x] **Repository Scoping**: Update `AbstractWorkflowRepository` to filter data by `organization_id`.
    - *System Workflows*: Visible to all (Read-Only).
    - *Tenant Workflows*: Visible only to owning Organization.
- [x] **API Versioning**: Prefix all endpoints with `/api/v1` to prevent future breaking changes.
- [ ] **Rate Limiting**: Implement `slowapi` to protect key endpoints.
- [x] **CORS Configuration**: Finalize CORSMiddleware settings (Enabled for all origins in `main.py`).

### 1.3 Infrastructure Readiness
- [x] **Storage Abstraction**: Support for switching between Local File System and Firebase Storage.
- [x] **Database Abstraction**: Support for switching between TinyDB (Local) and Firestore (Cloud).
- [x] **Regional Compliance**: Implemented strict Regional Model Validation (Model Garden Master List -> Regional Intersection).
- [x] **Operational Hardening**: Implemented URL Safety (SSRF), Quota Checks, and Integrity Audits.
- [x] **Crash Recovery**: Established standardized DB Reset protocols (`seed_prod.py`) and Integrity Checks.
- [x] **Containerization**: Full Docker support (Virtual Environment Parity, Strict `.dockerignore`, Multi-stage Builds).
- [x] **Config SSOT**: Refactor `docker-compose.yml` to use `.env` interpolation (Single Source of Truth) via `env_file`.
- [x] **Worker Environment Parity**: Worker successfully verified in Local (TinyDB), Local (Firestore), and Docker (Firestore) environments.

### 1.4 Cognitive Configuration Studio (The "Architect" UI)
**Objective:** Replace legacy chaotic configuration screens with a structured, visual workflow editor in Flutter. Enable "No-Code" strategy adjustments.

#### Backend: Dynamic Core (Priority Shift from Future Findings)
- [ ] **Database-Driven Definitions**: Refactor `execution_router.py` to load pipeline steps dynamically from `WorkflowDefinition` models in DB, replacing hardcoded "Case Logic".
- [ ] **Component API**: New endpoints (`GET /components/matrices`, `PUT /components/prompts`) to allow frontend modification of reasoning strategies.
- [ ] **Validation Layer**: Implement `DryRunValidator` to test modified workflows without executing expensive LLM calls.

#### Frontend: The Studio Module
- [ ] **Visual Pipeline Builder**: A specialized Flutter view using a "Stepper" or "Graph" visualization to show agent flow (e.g., `Ingest -> Guard -> Analyst -> Judge`).
    - *Feature:* Reorder agents via drag-and-drop (if backend logic permits) or toggle specific agents on/off.
- [ ] **Matrix Editor (BARS)**: A structured DataGrid UI for editing Evaluation Matrices (`Criteria`, `Score 1-5 Descriptions`).
    - *UX:* Prevents invalid JSON errors by using form fields instead of raw text editors.
- [ ] **Prompt Registry UI**: A "System Instruction" editor with version history.
    - *Safety:* Allows Admins to tweak the "Persona" of the Judge or Analyst without redeploying the backend.

### 1.5 Scalability Architecture (Future)
- [x] **Distribute Task Queue**: `Arq` with Redis implementation (`backend/worker.py`) for durable job execution.
- [x] **Decoupled Workers**: Initial separation of `execute_workflow_task` accessible via `worker.py`.

### 1.6 Reliability Hardening (Zero-Fallback & Seeding) (âœ… Completed)
- [x] **Zero-Fallback Architecture**: Removed default models; system now fails fast if configuration is missing.
- [x] **Seed Synchronization**: Standardized `db.json` -> `seed_data.json` migration, making Seed Data the authoritative source of truth.
- [x] **UI Step Synchronization**: Fixed race conditions in `PipelineRunner` ensuring "Pallukat" (UI indicators) update correctly.
- [x] **Linting & Hygiene**: Achieved 100% pass rate on `ruff` checks across the entire backend codebase.

---

## ðŸ“ Phase 2: The Pilot App (Flutter MVP) (âœ… Completed)
**Objective:** Enable end-users (Testers) to perform audits via a mobile/web interface using modern Flutter 3.27+ standards.

### 2.1 Foundation & Architecture (Critical Path)
- [x] **Scaffold & Theme**: Configure `FlexColorScheme` (Deep Purple #673AB7) and `google_fonts` (Inter) for Light/Dark modes.
- [x] **Localization Engine**: Setup `flutter_localizations` with `app_en.arb` and `app_fi.arb` (Mandatory FI/EN support).
- [x] **Riverpod & State**: Initialize `ProviderScope` and setup `json_serializable` / `riverpod_generator` build runners.
- [x] **Router Architecture**: Implement `GoRouter` with `StatefulShellRoute` (Nested Navigation) and Type-safe Routes (`GoRouteData`).
- [x] **Adaptive Layout**: Implemented NavigationRail/Bar switching and max-width constraints for Desktop/Web support.
- [x] **Adaptive Design Mandate**: Strict "Write once, adapt everywhere" policy (ConstrainedBox, SliverGrid, Responsive Shell).

### 2.2 Connectivity & Auth
- [x] **Secure HTTP Client**: Implement `Dio` with a generic `AuthInterceptor` to inject Firebase Tokens into Backend requests.
- [x] **Authentication State**: Build `auth_provider` (StreamProvider) using `firebase_auth` to drive Reactive Redirection (Guard).
- [x] **Environment Config**: Use `flutter_dotenv` to manage Backend URL (`http://localhost:8000` vs Cloud) via `.env`.
- [x] **Seeding Consolidation (Jan 17)**: Replaced fragmented scripts (`seed_all`, `seed_mock`, `seed_prod`) with unified `backend/seed/run_seed.py` CLI supporting explicit `local`, `mock`, and `firestore` targets. Verified Zero-Fallback behavior.
- [ ] **Critical Auth Fix**: Remove temporary auth bypass in `workflow_controller.dart` and implement robust checking before Production.

### 2.3 Dashboard & Monitoring
- [x] **Dashboard UI**: Grid view of System Workflows fetching data via `AsyncValue` providers.
- [x] **Report Viewer**: Render final HTML/Markdown results using `webview_flutter` or generic markdown renderers.
- [x] **PDF Download (One Truth)**: Replaced `Printing` with `FileSaver` to ensure cross-platform file download without print dialogs.

### 2.4 Workflow Data Layer (Foundation)
- [x] **Models**: Ensure `Execution`, `ExecutionStep`, and `ExecutionInput` match the backend Pydantic models (JSON serialization).
- [x] **Repository**: Update `ExecutionRepository` to support `createExecution()` (POST) and `streamExecution()` (SSE/Polling) calls.

### 2.5 Workflow State Management (Controller)
- [x] **Controller**: Implement `executionControllerProvider` to manage analysis initiation, validation logic, and polling state.
- [x] **Validation**: Dedicated logic for validating inputs before API calls.

### 2.6 Workflow UI (Wizard & Feedback)
- [x] **Creation Wizard**: Multi-step form view for configuring and starting a new analysis (replaces Audit Wizard).
- [x] **Live Execution View**: Real-time progress UI with polling integration (Progress Bar, Step Indicator). (Fix: Unified Timeline keys)
- [x] **Localization**: Full EN/FI support for Analysis Wizard and Execution Monitor.
- [x] **Strict Validation**: Client-side enforcement of Audit workflow requirements (Fail-Fast).
- [x] **Dynamic Input Rendering**: Forms generated purely from Backend `ui_schema`, removing client-side hardcoding.

### 2.8 Quality Assurance & Hygiene (Strict Mandate)
- [x] **Localization Hygiene**: Refactored `AppError` to enforce `ValidationErrorReason` enum (No raw strings).
- [x] **Error Contract**: `AuthRepository` strictly maps backend errors to typed exceptions.
- [x] **Hook Configuration**: Standardized `pre_hooks` in `seed_data.json` and re-seeded all environments.

### 2.7 Administration & Governance (The Admin Portal)
**Objective:** Port existing `frontend/main.py` admin capabilities to Flutter with a premium, "Best Practice" UX.

- [x] **Admin Portal Separation**:
    - **Workflow vs. Admin**: Strict visual and navigational separation between *Technical Configuration* (Workflow Builder, Matrix) and *Governance* (Users, Org, System).
    - **Dedicated Admin Route**: `/admin` dashboard with a distinct visual theme (ShellRoute + NavigationRail/NavigationBar Adaptive).
- [x] **Advanced User Management**:
    - **Access Lifecycle**: UI strategies for Granting, Renewing, and Revoking access (`UserManagementScreen`).
    - **Role Matrix**: Interactive permission table for assigning Roles (Viewer, Member, Manager, Admin).
    - **Organization Roster**: Searchable, filterable list of all Users within the Organization.
- [x] **Organization Governance**:
    - **Organization Management**: Full CRUD (Create, List, Delete) for Root Users.
    - **Safe Deletion**: Two-step verification with "Force Delete" for non-empty organizations.
    - **Access Control**: Strict RBAC enforcement (Root-only access to Org Management).
- [ ] **Live Operations Dashboard**:
    - **Concurrent Execution Monitor**: "Mission Control" view for Managers/Root to see all active jobs across their scope (Org vs System).
    - **Queue Visibility**: Insight into the task queue to manage future high-load concurrency.

---

## ðŸ“ Phase 2.6: Cognitive Layer Upgrade (Jan 2026) (âœ… Completed)
**Objective:** Upgrade the "Mind" of the system to support dynamic evaluation criteria and autonomous evidence discovery without code changes.

### 2.6.1 Dynamic Evaluation System (BARS)
- [x] **Configuration-Driven Matrix**: `JudgeAgent` input schema now accepts `matrix_id` (e.g., `matrix_standard_v1`) from `db.json`.
- [x] **Dynamic Component Loading**: `JudgeAgent` fetches Matrix definitions (Instructions, Criteria, Anchors) from `components` registry at runtime.
- [x] **Prompt Injection**: `matrix_formatter.py` converts JSON-based matrices into human-readable System Prompts on the fly.
- [x] **Polymorphic Reporting**: `StatePresenter` and `XAIReporter` dynamically extract and render dimensions from `EvaluationResult`, supporting arbitrary audit frameworks (Standard, Cognitive, etc.).

### 2.6.2 Autonomous Evidence Discovery
- [x] **Configuration-Driven Discovery**: `JudgeAgent` no longer has hardcoded upstream dependencies. It reads `monitored_steps` from `execution_config`.
- [x] **Blindness Fix**: Solved legacy issue where Judge could not see `step_panel` or sequential critics in Fused Workflows.
- [x] **Universal Context Gathering**: `JudgeAgent` iterates through configured `monitored_steps` (e.g., Profiler, Logician, Panel) and serializes their findings into the "Courtroom Evidence" block.

---

## ðŸ“ Phase 3: The Business Layer (Billing & Compliance)

**Objective:** Turn usage into revenue and ensure enterprise compliance.

### 3.1 Usage Tracking & Cost Attribution (âœ… Completed)
- [x] **Usage Service**: Track Token Usage (Input/Output) per Execution.
- [x] **Cost Calculation**: Real-time cost checking via LiteLLM.
- [x] **Quota Management**: Enforce Organization-level spend limits.
- [x] **Visual Reporting**: Visual usage stats in Client App Settings.

### 3.2 BYOK (Bring Your Own Key)
- [ ] **Secret Management**: Encrypted storage for Tenant API Keys.
- [ ] **LLM Provider Update**: Update `LLMFactory` to check Tenant Context before falling back to System Key.

### 3.3 Audit Logs (âœ… Completed)
- [x] **Audit Service**: Standardized logging for critical actions (Org/User lifecycle, Settings).
- [x] **RBAC Enforcement**: Strict visibility rules (Root=All, Admin=Org, Member=None).
- [ ] **Audit UI**: Dedicated frontend view for filtering and export (Basic table exists).

### 3.4 Enterprise Architecture (Best Practices)
- [ ] **Invitation Flow**: Replace direct user creation with Email Invitation + Password Set flow.
- [ ] **Soft Deletes**: Implement `deleted_at` timestamps instead of hard deletions for data recovery.
- [ ] **Billing Limits**: Enforce User/Workflow quotas based on Organization Tier.

---

## ðŸ“ Phase 4: Power Users (Manager Configuration Suite)
**Objective:** Enable deep customization for Enterprise clients. Empower Managers to define *how* the AI works, not just *when* it works.

### 4.1 Component Management (Prompts & Rules)
- [ ] **Component CRUD API**: Endpoints to Create/Read/Update/Delete reusable text components (Prompts, Instructions).
- [ ] **Prompt Library UI**: A Flutter view for Managers to write and version-control their own system prompts.
- [ ] **Dynamic Injection**: Update `WorkflowEngine` to fetch Prompts from DB at runtime instead of relying solely on `seed_data.json`.

### 4.2 Step Configuration (The Workbench)
- [ ] **Custom Step Builder**: UI where Managers create a new "Step" by combining a base Agent (e.g., *Judge*) with specific Prompts from their Library.
- [x] **Step Cloning**: Backend capability to fork a System Step into a Tenant Step (Existing `clone_step`).
- [ ] **Step Testing**: A "Test This Step" button to run a single step in isolation with sample input.

### 4.3 Workflow Studio (The Assembly)
- [x] **Clone Capability**: Allow Tenants to "Clone" a System Workflow (Implemented in `builder_router.py`).
- [x] **Workflow CRUD**: Full Create/Read/Update/Delete management for Tenant-specific workflows.
- [ ] **Visual Editor**: Flutter-based drag-and-drop or reorderable list interface for chaining Steps.
- [ ] **Tenant Repository**: Enable saving modified JSON configurations linked to `organization_id`.
- [ ] **Simulation Mode (Sandbox)**: Run a workflow transiently (`dry_run=True`) to verify outputs before publishing.
- [ ] **Version History**: Track changes to Workflows so Managers can rollback to a previous configuration.

### 4.4 Governance
- [ ] **Scope Isolation**: Ensure Manager A cannot modify Manager B's components (Org-level isolation).
- [ ] **Approval Gates**: (Optional) Allow Admin to "Lock" certain critical System Prompts so Managers cannot edit them.

### 4.5 Advanced Collaboration
- [ ] **Comments & Flagging**: Allow Viewers to comment on specific parts of a report.
- [ ] **Approval Flow**: Manager must "Approve" an audit result before it is finalized.

---

## ðŸ“ Phase 5: Self-Service & Refinement (âœ… Completed)
**Objective:** Empower users to manage their own identity and streamline Admin workflows.

### 5.1 User Self-Service
- [x] **Profile Editing**: Users can update their own Display Name and basic settings (`SettingsScreen` / `profile_view.py`).
- [x] **RBAC Hardening**: Strict enforcement of Organization boundaries (Root-only moves).

### 5.2 Admin Experience
- [x] **Workflow Builder Access**: Admins granted access to Workflow Builder (inherited from Manager) for template management.
- [x] **Simplified Verification**: Implemented single-file verification strategy (`tests/test_rbac_simple.py`) for rapid CI/CD checks.

---

## ðŸ“ Phase 6: Flutter Frontend (The Face)
**Objective:** Modernization (Riverpod 3.0, GoRouter, SDUI).

### 6.1 Data Models (Freezed)
- [ ] **Model Parity**: Varmista, ettÃ¤ Dart-mallit vastaavat 1:1 backendin Pydantic-malleja.
- [ ] **Code Gen**: `dart run build_runner build -d`.

### 6.2 Server-Driven Form Widget
- [ ] **DynamicForm Widget**: Implement `client_app/lib/features/orchestration/presentation/widgets/dynamic_form.dart`.
    - Logic: Parse JSON Schema from backend.
    - `type == 'string' && format == 'binary'` -> `FileUploader`
    - `type == 'string'` -> `TextFormField`
    - `enum` -> `DropdownButton`

### 6.3 Riverpod Orchestration
- [ ] **WorkflowExecutionProvider**: Implement `client_app/lib/features/orchestration/providers/workflow_execution_provider.dart`.
    - Use `@riverpod` annotation.
    - Handle `DioException` and map to `AppException`.

---

## ðŸ“ Phase 7: Cleanup (Siivous)
**Objective:** Poista Legacy-koodi ja siirry tÃ¤ysin dynaamiseen arkkitehtuuriin.

### 7.1 Legacy Removal
- [ ] **Delete**: `backend/agents/base.py` (Old BaseAgent).
- [ ] **Delete**: `backend/core/runner.py` (Old Runner).
- [ ] **Delete**: `backend/hooks/` directory (Moved to `lib/`, `core/`, `tools/`).
- [ ] **Delete**: `backend/components/` (If unused).

---

## ðŸ”® Future Findings (Q1 2026)
**New requirements identified during Phase 1-3 implementation:**

1.  **Recovery UI**:
    * Current recovery relies on CLI tools (`reset_db_from_seed.py`).
    * **Need**: A "Factory Reset" button in the Root Admin Dashboard for non-technical recovery.
2.  **SaaS Billing Integration**:
    * Backend has `billing_id` and `subscription_status`, but no payment gateway connection.
    * **Need**: Stripe/Paddle integration to automate status updates via Webhooks.

3.  **Hyper-Dynamic Artifact Architecture**:
    * **Concept**: Shift from rigid "Slot-Based" inputs (`History`, `Product`) to a "Tag-Based Artifact Collection" (`List[Artifact]`).
    * **Enablement**: Allows arbitrary number of files, auto-routing via semantic tags, and mass-scale case law analysis.
    * **Effort**: High (Core Engine & Prompt Logic Refactor).

