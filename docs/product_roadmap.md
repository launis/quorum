# 🗺️ Cognitive Quorum - Product Roadmap (2026)

This document outlines the strategic roadmap for evolving Cognitive Quorum from a prototype into a scalable, multi-tenant B2B SaaS platform.

## 📌 Status Legend
- [x] **Done**: Completed and integrated into `main`.
- [ ] **Pending**: To be implemented.
- [~] **In Progress**: Currently under active development.

---

## 🏗️ Phase 0: Core Intelligence & Engine (✅ Completed)
**Objective:** Build a robust, scientific-grade analysis engine capable of multi-agent reasoning.

### 0.0 Core Foundations (The "Brain")
- [x] **LLM Integration**: Implemented flexible `LLMProvider` (Gemini 1.5 support) with structured JSON output enforcement.
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

## 🧱 Phase 1: SaaS Foundation (Backend Hardening)
**Objective:** Secure the backend, enforce multi-tenancy, and ensure the system is "Cloud Ready".
**Milestone:** Jan 13, 2026 - Absolute Triple Green (Ruff/Mypy/Tests) & V2.9 Standards enforced.

### 1.1 Authentication & Identity (✅ Completed)
- [x] **Hybrid Auth Service**: Support for both Firebase Auth (Production) and Local Mock Auth (Dev).
- [x] **RBAC Implementation**: Defined Roles (`ROOT`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`).
- [x] **Organization Entity**: Implemented `Organization` model to support Multi-tenancy.
- [x] **User Management API**: Endpoints to create and list users within scope.
- [x] **System Admin UI**: Dashboard for ROOT to list/create organizations.
- [x] **Org Admin UI**: Dashboard for ADMIN to manage organization settings.
- [x] **Organization Deletion**: Implemented in API with safety checks for active jobs.
- [x] **Last Admin Protection**: Prevent deletion of the last ADMIN in an organization.
- [x] **Primary Root Protection**: Prevent deletion of the `root_master` system account.

### 1.2 Data Isolation & Security (✅ Completed)
- [x] **Repository Scoping**: Update `AbstractWorkflowRepository` to filter data by `organization_id`.
    - *System Workflows*: Visible to all (Read-Only).
    - *Tenant Workflows*: Visible only to owning Organization.
- [x] **API Versioning**: Prefix all endpoints with `/api/v1` to prevent future breaking changes.
- [ ] **Rate Limiting**: Implement `slowapi` to protect key endpoints.
- [x] **CORS Configuration**: Finalize CORSMiddleware settings (Enabled for all origins in `main.py`).

### 1.3 Infrastructure Readiness
- [x] **Storage Abstraction**: Support for switching between Local File System and Firebase Storage.
- [x] **Database Abstraction**: Support for switching between TinyDB (Local) and Firestore (Cloud).
- [x] **Regional Compliance**: Implemented strict Regional Model Validation.
- [x] **Operational Hardening**: Implemented URL Safety (SSRF), Quota Checks, and Integrity Audits.
- [x] **Crash Recovery**: Established standardized DB Reset protocols (`seed_prod.py`) and Integrity Checks.
- [x] **Containerization**: Full Docker support (Virtual Environment Parity, Strict `.dockerignore`).
- [x] **Config SSOT**: Refactor `docker-compose.yml` to use `.env` interpolation.
- [x] **Worker Environment Parity**: Worker successfully verified in Local (TinyDB), Local (Firestore), and Docker (Firestore) environments.

### 1.4 Cognitive Configuration Studio (Server-Driven UI)
**Objective:** Build a Flutter UI that adapts to backend changes without app updates.

- [x] **SDUI Engine (Flutter)**: Implemented `DynamicConfigForm` and `DynamicStepForm` widgets.
    - *Input:* JSON Schema from API.
    - *Mapping:* `string` -> `TextField`, `enum` -> `Dropdown`, `boolean` -> `Switch`.
- [x] **Workspace Navigation**: Refactored `router.dart` into specialized routes (`admin_routes.dart`, `dashboard_routes.dart`).
- [x] **Visual Workflow Builder**: Implemented `WorkflowStudioScreen` with drag-and-drop or list-based step ordering.

### 1.5 Scalability Architecture (Future)
- [x] **Distribute Task Queue**: `Arq` with Redis implementation (`backend/worker.py`) for durable job execution.
- [x] **Decoupled Workers**: Initial separation of `execute_workflow_task` accessible via `worker.py`.

### 1.6 Reliability Hardening (Zero-Fallback & Seeding) (✅ Completed)
- [x] **Zero-Fallback Architecture**: Removed default models; system now fails fast if configuration is missing.
- [x] **Seed Synchronization**: Standardized `seed_data.json` as the Single Source of Truth.
- [x] **UI Step Synchronization**: Fixed race conditions in `PipelineRunner`.
- [x] **Linting & Hygiene**: Achieved 100% pass rate on `ruff` checks.
- [x] **Sitra Integration Test**: Validated real-world data processing with strict zero-fallback limits.

### 1.7 API Modernization (The Modular Core)
**Objective:** Break down massive routers and prepare for SDUI architecture.

- [x] **Directory Structure Refactor**:
    - `backend/api/routes/execution/`: (`lifecycle.py`, `monitor.py`, `artifacts.py`, `views.py`)
    - `backend/api/routes/config/`: (`components.py`, `workflows.py`, `ontology.py`)
- [ ] **Service Layer Extraction**:
    - Move heavy logic (e.g., `validate_flow`) to `ValidationService`.
- [ ] **Schema Registry API**:
    - Implement `GET /api/v1/meta/schema/{model_type}` for Frontend usage.

### 1.8 Cognitive Configuration Studio (Flutter SDUI)
**Objective:** Build a dynamic control panel adapting to backend schemas.

- [x] **SDUI Core Widget**:
    - Implemented `DynamicConfigForm` (`client_app/lib/features/studio/presentation/widgets/`).
    - Supports `string`, `bool`, `enum`, `array`.
- [x] **Studio Shell**:
    - Implemented `/studio` route with distinct navigation structure.
- [x] **Workflow Editor**:
    - Implemented `WorkflowStudioScreen` using backend `WorkflowDefinition` schema.

---

## 📱 Phase 2: The Pilot App (Flutter MVP) (✅ Completed)
**Objective:** Enable end-users (Testers) to perform audits via a mobile/web interface.

### 2.1 Foundation & Architecture (Critical Path)
- [x] **Scaffold & Theme**: configured `FlexColorScheme` and `google_fonts`.
- [x] **Localization Engine**: Setup `flutter_localizations` with `app_en.arb` and `app_fi.arb`.
- [x] **Riverpod & State**: `ProviderScope` and code generation pipelines established.
- [x] **Router Architecture**: `GoRouter` with `StatefulShellRoute` (Nested Navigation).
- [x] **Adaptive Layout**: Responsive design for Mobile/Tablet/Desktop.
- [x] **Adaptive Design Mandate**: Strict "Write once, adapt everywhere" policy.

### 2.2 Connectivity & Auth
- [x] **Secure HTTP Client**: `Dio` with `AuthInterceptor`.
- [x] **Authentication State**: `auth_provider` driving Reactive Redirection.
- [x] **Environment Config**: `flutter_dotenv` for environment management.
- [x] **Seeding Consolidation**: Unified `backend/seed/run_seed.py`.
- [ ] **Critical Auth Fix**: Remove temporary auth bypass in `workflow_controller.dart`. (**PENDING**)

### 2.3 Dashboard & Monitoring
- [x] **Dashboard UI**: Grid view of System Workflows.
- [x] **Report Viewer**: Render final HTML/Markdown results.
- [x] **PDF Download (One Truth)**: Implemented using `FileSaver`.

### 2.4 Workflow Data Layer (Foundation)
- [x] **Models**: Dart models match Pydantic schemas.
- [x] **Repository**: unified `ExecutionRepository`.

### 2.5 Workflow State Management (Controller)
- [x] **Controller**: `executionControllerProvider` manages state and polling.
- [x] **Validation**: Client-side input validation.

### 2.6 Workflow UI (Wizard & Feedback)
- [x] **Creation Wizard**: Multi-step configuration form.
- [x] **Live Execution View**: Real-time progress UI with polling.
- [x] **Localization**: Full EN/FI support.
- [x] **Strict Validation**: Fail-fast input validation.
- [x] **Dynamic Input Rendering**: Forms generated from `ui_schema`.

### 2.7 Administration & Governance (The Admin Portal)
- [x] **Admin Portal Separation**: Distinct `/admin` route and theme.
- [x] **Advanced User Management**: Access granting/revoking, Role Matrix.
- [x] **Organization Governance**: CRUD for Organizations, RBAC enforcement.
- [ ] **Live Operations Dashboard**: Concurrent execution monitoring.

---

## 🧠 Phase 2.6: Cognitive Layer Upgrade (✅ Completed)
**Objective:** Upgrade the "Mind" of the system to support dynamic evaluation criteria.

### 2.6.1 Dynamic Evaluation System (BARS)
- [x] **Configuration-Driven Matrix**: `JudgeAgent` input schema accepts `matrix_id`.
- [x] **Dynamic Component Loading**: Runtime fetching of Matrix definitions.
- [x] **Prompt Injection**: `matrix_formatter.py` for on-the-fly prompt generation.
- [x] **Polymorphic Reporting**: Dynamic rendering of audit dimensions.

### 2.6.2 Autonomous Evidence Discovery
- [x] **Configuration-Driven Discovery**: `JudgeAgent` reads `monitored_steps`.
- [x] **Blindness Fix**: Judge sees all upstream steps defined in config.
- [x] **Universal Context Gathering**: Serializes findings into "Courtroom Evidence".

---

## 💰 Phase 3: The Business Layer (Billing & Compliance)
**Objective:** Turn usage into revenue and ensure enterprise compliance.

### 3.1 Usage Tracking & Cost Attribution (✅ Completed)
- [x] **Usage Service**: Track Token Usage.
- [x] **Cost Calculation**: Real-time cost checking.
- [x] **Quota Management**: Organization-level limits.
- [x] **Visual Reporting**: Usage stats in Settings.

### 3.2 BYOK (Bring Your Own Key)
- [ ] **Secret Management**: Encrypted storage for Tenant API Keys.
- [ ] **LLM Provider Update**: logic for Tenant Key fallback.

### 3.3 Audit Logs (✅ Completed)
- [x] **Audit Service**: Standardized logging.
- [x] **RBAC Enforcement**: Strict visibility rules.
- [ ] **Audit UI**: Dedicated frontend view.

---

## 🛠️ Phase 4: Power Users (Manager Configuration Suite)
**Objective:** Enable deep customization for Enterprise clients.

### 4.1 Component Management (Prompts & Rules)
- [x] **Component CRUD API**: Endpoints in `backend/api/routes/config/components.py`.
- [ ] **Prompt Library UI**: Flutter view for Prompt management.
- [ ] **Dynamic Injection**: Runtime fetching of Prompts from DB.

### 4.2 Step Configuration (The Workbench)
- [ ] **Custom Step Builder**: UI for creating new Steps.
- [x] **Step Cloning**: Backend capability to fork Steps.
- [ ] **Step Testing**: Isolation testing for steps.

### 4.3 Workflow Studio (The Assembly)
- [x] **Clone Capability**: Workflows can be cloned.
- [x] **Workflow CRUD**: Endpoints in `backend/api/routes/config/workflows.py`.
- [x] **Visual Editor**: `WorkflowStudioScreen` (Flutter).
- [ ] **Tenant Repository**: Saving modified JSON configurations.
- [ ] **Simulation Mode**: Dry-run verification.
- [ ] **Version History**: Workflow versioning.

---

## 🧹 Phase 7: Cleanup (Siivous)
**Objective:** Remove Legacy code and finalize dynamic architecture.

### 7.1 Legacy Removal
- [x] **Refactored**: `backend/agents/base.py` (Modernized to Pydantic V2 & LLMFactory).
- [x] **Delete**: `backend/components/` (Removed).

---

## 🔨 3. Immediate Action Steps (Refactoring Status)

### Step 1: Backend API Refactor (✅ Done)
- [x] Created `backend/api/routes/config/`.
- [x] Split `config_router.py` into `components.py`, `workflows.py`, `ontology.py`.

### Step 2: SDUI Schemas (Backend) (🚧 Pending)
- [ ] Create `backend/api/routes/meta.py`.
- [ ] Implement `GET /api/v1/meta/schema/{model_type}` endpoint.
- [ ] Ensure Enum field dynamic updates.

### Step 3: Flutter Router Refactor (Client) (✅ Done)
- [x] Created `client_app/lib/router/`.
- [x] Separated `admin_routes.dart` and `dashboard_routes.dart`.

### Step 4: Dynamic Form Widget (Client) (✅ Done)
- [x] Implemented `DynamicConfigForm` and `DynamicStepForm`.
- [x] Tested in `WorkflowStudioScreen`.

---

## 🔮 Future Findings (Q1 2026)
**New requirements identified:**

1.  **Recovery UI**: "Factory Reset" button in Admin Dashboard.
2.  **SaaS Billing Integration**: Stripe/Paddle integration.
3.  **Hyper-Dynamic Artifact Architecture**: Shift to "Tag-Based Artifact Collection".
