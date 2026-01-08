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
- [x] **Web Interface v1**: Initial Streamlit frontend for launching audits and viewing results.

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
**Objective:** Secure the backend, enforce multi-tenancy, and ensure the system is "Cloud Ready" before building the client apps.

### 1.1 Authentication & Identity (✅ Completed)
- [x] **Hybrid Auth Service**: Support for both Firebase Auth (Production) and Local Mock Auth (Dev).
- [x] **RBAC Implementation**: Defined Roles (`ROOT`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`).
- [x] **Organization Entity**: Implemented `Organization` model to support Multi-tenancy.
- [x] **User Management API**: Endpoints to create and list users within scope.
- [x] **System Admin UI**: Dashboard for ROOT to list/create organizations.
- [x] **Org Admin UI**: Dashboard for ADMIN to manage organization settings.
- [x] **Organization Deletion**: Implemented in API with safety checks for active jobs (Manual UI trigger pending).
- [x] **Last Admin Protection**: Prevent deletion/demotion of the last ADMIN in an organization (Implemented in `AuthService`).
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

### 1.4 Scalability Architecture (Future)
- [x] **Distributed Task Queue**: `Arq` with Redis implementation (`backend/worker.py`) for durable job execution.
- [x] **Decoupled Workers**: Initial separation of `execute_workflow_task` accessible via `worker.py`.

---

## 📍 Phase 2: The Pilot App (Flutter MVP)
**Objective:** Enable end-users (Testers) to perform audits via a mobile/web interface using modern Flutter 3.38+ standards.

### 2.1 Foundation & Architecture (Critical Path)
- [x] **Scaffold & Theme**: Configure `FlexColorScheme` (Deep Purple #673AB7) and `google_fonts` (Inter) for Light/Dark modes.
- [x] **Localization Engine**: Setup `flutter_localizations` with `app_en.arb` and `app_fi.arb` (Mandatory FI/EN support).
- [x] **Riverpod & State**: Initialize `ProviderScope` and setup `json_serializable` / `riverpod_generator` build runners.
- [x] **Router Architecture**: Implement `GoRouter` with `StatefulShellRoute` (Nested Navigation) and Type-safe Routes (`GoRouteData`).

### 2.2 Connectivity & Auth
- [x] **Secure HTTP Client**: Implement `Dio` with a generic `AuthInterceptor` to inject Firebase Tokens into Backend requests.
- [x] **Authentication State**: Build `auth_provider` (StreamProvider) using `firebase_auth` to drive Reactive Redirection (Guard).
- [x] **Environment Config**: Use `flutter_dotenv` to manage Backend URL (`http://localhost:8000` vs Cloud) via `.env`.

### 2.3 Dashboard & Monitoring
- [ ] **Dashboard UI**: Grid view of System Workflows fetching data via `AsyncValue` providers.
- [ ] **Report Viewer**: Render final HTML/Markdown results using `webview_flutter` or generic markdown renderers.

### 2.4 Workflow Data Layer (Foundation)
- [ ] **Models**: Ensure `Execution`, `ExecutionStep`, and `ExecutionInput` match the backend Pydantic models (JSON serialization).
- [ ] **Repository**: Update `ExecutionRepository` to support `createExecution()` (POST) and `streamExecution()` (SSE/Polling) calls.

### 2.5 Workflow State Management (Controller)
- [ ] **Controller**: Implement `executionControllerProvider` to manage analysis initiation, validation logic, and polling state.
- [ ] **Validation**: Dedicated logic for validating inputs before API calls.

### 2.6 Workflow UI (Wizard & Feedback)
- [ ] **Creation Wizard**: Multi-step form view for configuring and starting a new analysis (replaces Audit Wizard).
- [ ] **Live Execution View**: Real-time progress UI with polling integration (Progress Bar, Step Indicator).

---

## 📍 Phase 3: The Business Layer (Billing & Compliance)

**Objective:** Turn usage into revenue and ensure enterprise compliance.

### 3.1 Usage Tracking & Cost Attribution (✅ Completed)
- [x] **Usage Service**: Track Token Usage (Input/Output) per Execution.
- [x] **Cost Calculation**: Real-time cost checking via LiteLLM.
- [x] **Quota Management**: Enforce Organization-level spend limits.
- [ ] **Visual Reporting**: Admin API to fetch usage stats per month (Backend Ready).

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

## 📍 Phase 4: Power Users (Platform Features)
**Objective:** Enable deep customization for Enterprise clients.

### 4.1 Custom Workflow Builder
- [x] **Clone Capability**: Allow Tenants to "Clone" a System Workflow (Implemented in `builder_router.py`).
- [ ] **Tenant Repository**: Enable saving modified JSON configurations linked to `organization_id`.
- [ ] **Builder UI**: (Long term) A visual editor for modifying prompts and steps.

### 4.2 Advanced Collaboration
- [ ] **Comments & Flagging**: Allow Viewers to comment on specific parts of a report.
- [ ] **Approval Flow**: Manager must "Approve" an audit result before it is finalized.

---

## 🔮 Future Findings (Q1 2026)
**New requirements identified during Phase 1-3 implementation:**

1.  **Recovery UI**:
    *   Current recovery relies on CLI tools (`reset_db_from_seed.py`).
    *   **Need**: A "Factory Reset" button in the Root Admin Dashboard for non-technical recovery.
2.  **SaaS Billing Integration**:
    *   Backend has `billing_id` and `subscription_status`, but no payment gateway connection.
    *   **Need**: Stripe/Paddle integration to automate status updates via Webhooks.
    *   **Need**: Stripe/Paddle integration to automate status updates via Webhooks.
4.  **Test Data Management**:
    *   `seed_data.json` is the source of truth but fragile.
    *   **Need**: A dedicated Test Data Factory or Fixture system to generate comprehensive scenarios without manual JSON editing.
5.  **Python 3.14 & Modern Pydantic**:
    *   Currently downgraded to Python 3.13 due to `pydantic-core` build issues and required `from __future__` hacks.
6.  **Advanced Execution Strategies (On Demand)**:
    *   **Parallel Execution**: Implement DAG-based concurrent step execution (utilizing `execute_workflow_task` separation) for high-volume analysis.
    *   **Microservice Decoupling**: Transition from Python Direct Call hooks to network-based service calls only when scaling demands strict separation.
