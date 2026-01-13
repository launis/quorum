# 🗺️ Cognitive Quorum - Product Roadmap (2026)

This document outlines the strategic roadmap for evolving Cognitive Quorum from a prototype into a scalable, multi-tenant B2B SaaS platform.

## 📌 Status Legend
- [x] **Done**: Completed and integrated into `main`.
- [ ] **Pending**: To be implemented.
- [~] **In Progress**: Currently under active development.

---

## 🏁 Phase 0: Core Intelligence & Engine (✅ Completed)
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

## 📍 Phase 1: SaaS Foundation (Backend Hardening)
**Objective:** Secure the backend, enforce multi-tenancy, and ensure the system is "Cloud Ready".
**Milestone:** Jan 13, 2026 - Absolute Triple Green (Ruff/Mypy/Tests) & V2.9 Standards enforced.

### 1.1 Authentication & Identity (✅ Completed)
- [x] **Hybrid Auth Service**: Support for both Firebase Auth (Production) and Local Mock Auth (Dev).
- [x] **RBAC Implementation**: Defined Roles (`ROOT`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`).
- [x] **Organization Entity**: Implemented `Organization` model to support Multi-tenancy.
- [x] **User Management API**: Endpoints to create and list users within scope.
- [x] **System Admin UI**: Dashboard for ROOT to list/create organizations.
- [x] **Org Admin UI**: Dashboard for ADMIN to manage organization settings.
- [x] **Organization Deletion**: Implemented in API with safety checks for active jobs (Manual UI trigger pending).
- [x] **Last Admin Protection**: Prevent deletion of the last ADMIN in an organization (Implemented in `AuthService`).
- [x] **Primary Root Protection**: Prevent deletion of the `root_master` system account (Implemented in `AuthService`).

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
- [x] **Regional Compliance**: Implemented strict Regional Model Validation (Model Garden Master List -> Regional Intersection).
- [x] **Operational Hardening**: Implemented URL Safety (SSRF), Quota Checks, and Integrity Audits.
- [x] **Crash Recovery**: Established standardized DB Reset protocols (`seed_prod.py`) and Integrity Checks.
- [x] **Containerization**: Full Docker support (Virtual Environment Parity, Strict `.dockerignore`, Multi-stage Builds).
- [x] **Config SSOT**: Refactor `docker-compose.yml` to use `.env` interpolation (Single Source of Truth) via `env_file`.
- [x] **Worker Environment Parity**: Worker successfully verified in Local (TinyDB), Local (Firestore), and Docker (Firestore) environments.

### 1.4 Scalability Architecture (Future)
- [x] **Distribute Task Queue**: `Arq` with Redis implementation (`backend/worker.py`) for durable job execution.
- [x] **Decoupled Workers**: Initial separation of `execute_workflow_task` accessible via `worker.py`.

### 1.5 Reliability Hardening (Zero-Fallback & Seeding) (✅ Completed)
- [x] **Zero-Fallback Architecture**: Removed default models; system now fails fast if configuration is missing.
- [x] **Seed Synchronization**: Standardized `db.json` -> `seed_data.json` migration, making Seed Data the authoritative source of truth.
- [x] **UI Step Synchronization**: Fixed race conditions in `PipelineRunner` ensuring "Pallukat" (UI indicators) update correctly.
- [x] **Linting & Hygiene**: Achieved 100% pass rate on `ruff` checks across the entire backend codebase.

---

## 📍 Phase 2: The Pilot App (Flutter MVP) (✅ Completed)
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

### 2.3 Dashboard & Monitoring
- [x] **Dashboard UI**: Grid view of System Workflows fetching data via `AsyncValue` providers.
- [x] **Report Viewer**: Render final HTML/Markdown results using `webview_flutter` or generic markdown renderers.

### 2.4 Workflow Data Layer (Foundation)
- [x] **Models**: Ensure `Execution`, `ExecutionStep`, and `ExecutionInput` match the backend Pydantic models (JSON serialization).
- [x] **Repository**: Update `ExecutionRepository` to support `createExecution()` (POST) and `streamExecution()` (SSE/Polling) calls.

### 2.5 Workflow State Management (Controller)
- [x] **Controller**: Implement `executionControllerProvider` to manage analysis initiation, validation logic, and polling state.
- [x] **Validation**: Dedicated logic for validating inputs before API calls.

### 2.6 Workflow UI (Wizard & Feedback)
- [x] **Creation Wizard**: Multi-step form view for configuring and starting a new analysis (replaces Audit Wizard).
- [x] **Live Execution View**: Real-time progress UI with polling integration (Progress Bar, Step Indicator).
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

## 📍 Phase 3: The Business Layer (Billing & Compliance)

**Objective:** Turn usage into revenue and ensure enterprise compliance.

### 3.1 Usage Tracking & Cost Attribution (✅ Completed)
- [x] **Usage Service**: Track Token Usage (Input/Output) per Execution.
- [x] **Cost Calculation**: Real-time cost checking via LiteLLM.
- [x] **Quota Management**: Enforce Organization-level spend limits.
- [x] **Visual Reporting**: Visual usage stats in Client App Settings.

### 3.2 BYOK (Bring Your Own Key)
- [ ] **Secret Management**: Encrypted storage for Tenant API Keys.
- [ ] **LLM Provider Update**: Update `LLMFactory` to check Tenant Context before falling back to System Key.

### 3.3 Audit Logs (✅ Completed)
- [x] **Audit Service**: Standardized logging for critical actions (Org/User lifecycle, Settings).
- [x] **RBAC Enforcement**: Strict visibility rules (Root=All, Admin=Org, Member=None).
- [ ] **Audit UI**: Dedicated frontend view for filtering and export (Basic table exists).

### 3.4 Enterprise Architecture (Best Practices)
- [ ] **Invitation Flow**: Replace direct user creation with Email Invitation + Password Set flow.
- [ ] **Soft Deletes**: Implement `deleted_at` timestamps instead of hard deletions for data recovery.
- [ ] **Billing Limits**: Enforce User/Workflow quotas based on Organization Tier.

---

## 📍 Phase 4: Power Users (Platform Features, ROOT and MANAGER users)
**Objective:** Enable deep customization for Enterprise clients.

### 4.1 Custom Workflow Management (Builder & CRUD)
- [x] **Clone Capability**: Allow Tenants to "Clone" a System Workflow (Implemented in `builder_router.py`).
- [ ] **Workflow CRUD**: Full Create/Read/Update/Delete management for Tenant-specific workflows.
- [ ] **Tenant Repository**: Enable saving modified JSON configurations linked to `organization_id`.
- [ ] **Builder UI**: (Long term) A visual editor for modifying prompts and steps.

### 4.2 Advanced Collaboration
- [ ] **Comments & Flagging**: Allow Viewers to comment on specific parts of a report.
- [ ] **Approval Flow**: Manager must "Approve" an audit result before it is finalized.

---

## 📍 Phase 5: Self-Service & Refinement (✅ Completed)
**Objective:** Empower users to manage their own identity and streamline Admin workflows.

### 5.1 User Self-Service
- [x] **Profile Editing**: Users can update their own Display Name and basic settings (`SettingsScreen` / `profile_view.py`).
- [x] **RBAC Hardening**: Strict enforcement of Organization boundaries (Root-only moves).

### 5.2 Admin Experience
- [x] **Workflow Builder Access**: Admins granted access to Workflow Builder (inherited from Manager) for template management.
- [x] **Simplified Verification**: Implemented single-file verification strategy (`tests/test_rbac_simple.py`) for rapid CI/CD checks.

---

## 🔮 Future Findings (Q1 2026)
**New requirements identified during Phase 1-3 implementation:**

1.  **Recovery UI**:
    *   Current recovery relies on CLI tools (`reset_db_from_seed.py`).
    *   **Need**: A "Factory Reset" button in the Root Admin Dashboard for non-technical recovery.
2.  **SaaS Billing Integration**:
    *   Backend has `billing_id` and `subscription_status`, but no payment gateway connection.
    *   **Need**: Stripe/Paddle integration to automate status updates via Webhooks.

3.  **Hyper-Dynamic Artifact Architecture**:
    *   **Concept**: Shift from rigid "Slot-Based" inputs (`History`, `Product`) to a "Tag-Based Artifact Collection" (`List[Artifact]`).
    *   **Enablement**: Allows arbitrary number of files, auto-routing via semantic tags, and mass-scale case law analysis.
    *   **Effort**: High (Core Engine & Prompt Logic Refactor).

4.  **Database-Driven Workflow Definitions**:
    *   **Current State**: Hardcoded logic in `execution_router.py` handles specific workflow cases (e.g., "Audit" expects 3 specific files).
    *   **Interim Strategy**: Continue using hardcoded "Case Logic" where `audit = 3 files` is defined in code but executed via DB-stored steps.
    *   **Future Goal**: Fully dynamic definition where the Database stores the *File Requirements* (input schema) alongside the steps, removing hardcoded logic from the router.
