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
- [ ] **Dynamic Rules Engine UI**: Admin interface for `step_logic` customization (Reasoning Rules).
- [ ] **Banned Phrases Management UI**: Admin interface to add/edit Banned Phrases in the database (replace hardcoded defaults).
- [ ] **Linguistics Pattern UI**: Admin interface to manage Performative Patterns.
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
- [x] **LiteLLM Usage Extraction**: Refactored `LiteLLMProvider` to correctly extract token usage from Instructor's structured responses (Fixes "0 tokens" visibility issue).
- [ ] **Firestore Seed Parity**: Add missing collections (`executions`, `usage`, `usage_aggregates`, `audit_logs`) to `seeder.py`'s `_seed_firestore()` deletion loop so old token usage resets identically to TinyDB.

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
- [x] **Platform Upgrade**: Enforced **Python 3.14.2** strictness.
- [x] **Hybrid State Audit**: Verified Event Log (Truth) vs Blackboard (Performance) consistency.
- [x] **Sitra Integration Test**: Validated real-world data processing with strict zero-fallback limits.
- [x] **Strict JSON File Transfer (Y-Funnel)**: Replaced brittle `multipart/form-data` handlers with Pydantic-validated Base64 JSON encapsulation for bulletproof file ingestion.

### 1.7 API Modernization (The Modular Core)
**Objective:** Break down massive routers and prepare for SDUI architecture.

- [x] **Directory Structure Refactor**:
    - `backend/api/routes/execution/`: (`lifecycle.py`, `monitor.py`, `artifacts.py`, `views.py`)
    - `backend/api/routes/config/`: (`components.py`, `workflows.py`, `ontology.py`)
- [x] **Service Layer Extraction**:
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
- [x] **Critical Auth Fix**: Remove temporary auth bypass in `workflow_controller.dart`.

### 2.3 Dashboard & Monitoring
- [x] **Dashboard UI**: Grid view of System Workflows.
- [x] **Report Viewer**: Render final HTML/Markdown results.
- [x] **PDF Download (One Truth)**: Implemented using `FileSaver`.

### 2.4 Workflow Data Layer (Foundation)
- [x] **Models**: Dart models match Pydantic schemas.
- [x] **Repository**: unified `ExecutionRepository`.
- [x] **Data Migration**: Establish `StorageDriver` pattern for standardized file system abstractions (Local/Cloud parity).

### 2.5 Workflow State Management (Controller)
- [x] **Controller**: `executionControllerProvider` manages state and polling.
- [x] **Validation**: Client-side input validation.

### 2.6 Workflow UI (Wizard & Feedback)
- [x] **Creation Wizard**: Multi-step configuration form.
- [x] **Live Execution View**: Real-time progress UI with polling.
- [x] **Localization**: Full EN/FI support.
- [x] **Strict Validation**: Fail-fast input validation.
- [x] **Dynamic Input Rendering**: Forms generated from `ui_schema`.
- [x] **OmniInputBox**: Consolidated copy-paste text and file drag-and-drop into a single unified widget for history, logic, and self-evaluation fields.

### 2.7 Administration & Governance (The Admin Portal)
- [x] **Admin Portal Separation**: Distinct `/admin` route and theme.
- [x] **Advanced User Management**: Access granting/revoking, Role Matrix.
- [x] **Organization Governance**: CRUD for Organizations, RBAC enforcement.
- [ ] **Live Operations Dashboard**: Concurrent execution monitoring.

### 2.8 Knowledge & Retrieval (The Second Brain) (✅ Completed)
- [x] **Knowledge Base Service**: Async ingestion pipeline (`text-embedding-3-small` ready).
- [x] **Dynamic Model Strategy**: Runtime resolution of LLM models per-request (Fast/Deep strategies).
- [x] **Google Search Integration**: "Sidebar Pattern" implementation (`OverseerAgent`) for external fact-checking.
- [x] **Fail-Fast Architecture**: Strict SSOT error handling (`SERVICE_DEPENDENCY_MISSING`) for critical dependencies.
- [x] **Ingestion UI**: Flutter-based drag-and-drop upload with real-time progress tracking.
- [x] **Bibliography Awareness**: Intelligent parsing of reference lists to prevent context loss.

---

## 🧠 Phase 2.6: Cognitive Layer Upgrade (✅ Completed)
**Objective:** Upgrade the "Mind" of the system to support dynamic evaluation criteria.

### 2.6.1 Dynamic Evaluation System (BARS)
- [x] **Configuration-Driven Matrix**: `JudgeAgent` input schema accepts `matrix_id`.
- [x] **Strict BARS Injection**: `MatrixFormatter` generates high-fidelity Markdown rubrics (Fail-Fast).
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

### 3.3 Localization & Culture Awareness
- [ ] **Culturally Aware Security**: Refactor `backend/core/security.py` to support locale-specific PII detection (e.g. Finnish HETU vs US SSN).
- [ ] **Localized Banned Phrases**: Admin interface to manage banned phrases per language.

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
- [ ] **Dynamic Settings (Penalty & Thresholds)**: Migrate hardcoded `settings.py` values (e.g., scoring penalties, passivity thresholds) to Database.
    - *Goal*: Allow Admins/Managers to tune algorithm sensitivity via UI without redeployment.

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
- [x] **Domain Refactor**: Modularized `domain.py` into `backend/models/domain/` package.
- [x] **Delete**: `backend/components/` (Removed).

---

## 🔨 3. Immediate Action Steps (Refactoring Status)

### Step 1: Backend API Refactor (✅ Done)
- [x] Created `backend/api/routes/config/`.
- [x] Split `config_router.py` into `components.py`, `workflows.py`, `ontology.py`.

### Step 2: SDUI Schemas (Backend) (Moved to Future Roadmap)
- [~] **Deferred**: Moved to Phase 2.6 (Advanced SDUI & Meta-Programming).

### Step 3: Flutter Router Refactor (Client) (✅ Done)
- [x] Created `client_app/lib/router/`.
- [x] Separated `admin_routes.dart` and `dashboard_routes.dart`.

### Step 4: Dynamic Form Widget (Client) (✅ Done)
- [x] Implemented `DynamicConfigForm` and `DynamicStepForm`.
- [x] Tested in `WorkflowStudioScreen`.

### Step 5: Prefixed UUID Normalization (Current Focus)
- [x] Refactor `generate_unique_id` to enforce mandatory system prefixes (e.g., `wf-`, `matrix-`).
- [~] Introduce `NewType` strictly typed IDs (`WorkflowID`, `ExecutionID`) to all Pydantic schemas, permanently replacing loose `str` matching.
- [ ] Migrate the `seed_data.json` database constraints to use the new typed IDs exclusively.

---

---

## 🪝 Phase 2.5: Refactoring Hooks (Incremental) (✅ Completed)
**Objective:** Transition backend hooks to Strict Pydantic and RFC 7807 Fail Fast standards.

- [x] **Scoring Hook Refactor**: 
    - Converted `scoring.py` to use `state.get_context(model=JudgeOutput)`.
    - Enforced **Relative Penalties** (Settings-driven) instead of hardcoded logic.
    - Added **Safety Clamp** (`max(new_score, scale_min)`) to prevent score collapse.
- [x] **Critical Hooks Hardening**:
    - **Validation & Integrity**: Enforced Strict Inflation and explicit `AppException`.
    - **XAI Reporter**: Fixed `JudgeScoreCard` schema mismatch (0.0 -> 1.0 validation error).
    - **Security & Linguistics**: Standardized error codes and Fail Fast logic.

---

## ️ Phase 2.9: Advanced SDUI & Meta-Programming (Q2 2026)
**Objective:** Enable the frontend to dynamically construct interfaces from Backend Pydantic Schemas.

- [ ] **Schema Registry API**: Implement `GET /api/v1/meta/schema/{model_type}` to expose Pydantic JSON Schemas.
- [ ] **Tenant Repository**: Enable saving modified JSON configurations linked to `organization_id` (Git-like versioning).
- [ ] **Live Operations Dashboard**: Real-time visualization of concurrent workflow executions.
- [ ] **Recovery UI**: "Factory Reset" button in Admin Dashboard for catastrophic state recovery.
- [ ] **Semantic Document Model (SDUI Refactoring)**: Transition from a visual UI model to an agnostic content model. The backend must return semantic blocks (`type`, `label`, `value`, `intent`) instead of visual components, guaranteeing WYSIWYG parity between Flutter (Screen) and Jinja2 (PDF).
    - *Action 1*: Strip UI/CSS references from Backend DTOs (`models/view/sdui.py` -> `semantic_models.py`).
    - *Action 2*: Refactor `bff_transformer.py` to assemble semantic blocks instead of defining explicit UI views.
    - *Action 3*: Refactor Frontend router (`schema_mapper.dart`) to act as a semantic interpreter mapping types to existing native widgets.
    - *Action 4*: Unify PDF generation on the backend using `report_template.jinja2` driven by the identical semantic block list, removing the duplicated Flutter-side PDF generation.

---

## 🔮 Phase 3: The Business Layer (Future)
**Objective:** Turn usage into revenue and ensure enterprise compliance.

- [ ] **Billing & Token Quotas**: Implementation of per-organization budget limits and Stripe/billing integration.
- [ ] **Multi-Team Organizations**: Hierarchical structure for large organizations (Departments, Groups).
- [ ] **Compliance Export Suite**: Automated generation of ISO/Audit compliance reports from execution traces.
- [ ] **Advanced IAM**: SAML/SSO integration for enterprise tenants.
- [ ] **Organization Onboarding Wizard**: Self-service flow for creating and configuring new tenants.
- [ ] **BYOK (Bring Your Own Key)**: Encrypted storage for Tenant API Keys and fallback logic.

---

## 🚀 Phase 4: Power Users (Manager Configuration)
**Objective:** Deep customization for Enterprise clients. Empowers Managers to own their reasoning strategy.

### 4.1 Component Management
- [ ] **Component CRUD API**: Create/Read/Update/Delete reusable text components.
- [ ] **Prompt Library UI**: Flutter view for Manager-controlled system prompts.
- [ ] **Dynamic Injection**: Fetch Prompts from DB at runtime.

### 4.2 Step Configuration
- [ ] **Custom Step Builder**: UI for creating new Steps from base Agents.
- [ ] **Step Testing**: Isolation testing for individual steps.
- [ ] **High-Fidelity Embeddings**: Integration of `text-embedding-3-small` or Vertex `gecko` for semantic search.

### 4.3 Governance & Collaboration
- [ ] **Scope Isolation**: Ensure Org-level isolation for components.
- [ ] **Approval Gates**: Admin locking for critical System Prompts.
- [ ] **Shared Workspaces**: Collaborative execution tracing.
- [ ] **Panel Step Parity Verification**: Ensure `PanelAgent` configuration matches replaced steps to prevent drift.

---

## 📉 Technical Debt & Optimization (Backlog)
- [ ] **Dynamic Agent Orchestration (Workflow Engine)**: Refactor the current linear/static execution pipeline into a dynamic system (e.g., DAG or Router/Supervisor Agent pattern) to allow dynamic agent ordering and execution paths. This is a recognized future infrastructure need to optimize Python-heavy asynchronous logic.
- [ ] **Banned Phrases Seed Restoration**: Re-merge `banned_phrases` into `seed_data.json`.
- [ ] **Dynamic Hook Orchestration**: Refactor architecture to allow runtime selection of Hook Implementations via UI (e.g., swapping `SearchHook` vs `VertexSearchHook`).
- [ ] **Rate Limiting**: Implement `slowapi` on key endpoints.
- [x] **Data Migration**: Establish `StorageDriver` pattern for standardized file system abstractions (Local/Cloud parity).
- [ ] **Database Identifier Migration**: Update all existing database rows to use strict `backend/utils/identifiers.py` compliance (Fail Fast validation).
- [ ] **Panel Agent Component Architecture**: Refactor `search_section` and `context_section` to be injected components (Data-Driven) instead of hardcoded f-strings in `panel.py`.
- [ ] **RetrievalAgent Limits**: Implement stricter limits (top-k=5) or Vector Search (V3) to prevent context overflow from broad queries (e.g. "tekoäly").
- [ ] **Internal Knowledge Base Vectorization**: Upgrade `knowledge_base_service.py` (`retrieve_context`) from in-memory string matching MVP to Vector Semantic Search (Embeddings) for internal document retrieval (e.g. Brand Books).
- [ ] **Reference Hook Engine Integration**: Modernize `backend/hooks/references.py` to seamlessly integrate with `GraphEngine` dynamic retrieval loops instead of evaluating plain strings, ensuring robust Domain Compliance validation.
- [ ] **Eliminate Magic Strings (Data-Driven Configuration)**: Refactor `seed_data.json` step configs to define explicit roles (e.g., `core_template`, `dynamic_tasks`) mapping to prompt slugs rather than blindly injecting an array. This enables true strict Pydantic Dependency Injection into Agents, eliminating the need to hardcode `execution_context.get("PANEL_PROMPT_TEMPLATE")` inside Python files.
- [ ] **Dynamic Provider Parsing Modes**: Upgrade `backend/llm/provider.py` and `LLMProviderConfig` to support configuring the structured parsing strategy dynamically from the database (e.g., `GEMINI_JSON` vs `JSON_SCHEMA` vs `MD_JSON`). Currently, Instructor parsing modes are hardcoded heuristics in the client, but the system should natively support a switch/case block inside `provider.py` reading directly from the database's `model_registry` config block (`case "google": mode = GEMINI_JSON`, `case "openai": mode = JSON_SCHEMA`).
- [ ] **Strict Pydantic Type Validation in Editor (ValidationService)**: Upgrade `backend/services/validation_service.py` (`validate_flow_configuration`) to check strict Pydantic `output_model` and `InputModel` compatibilities between connected agents, rather than just matching legacy string keys (`REQUIRES_KEYS` vs `PRODUCES_KEYS`). This prevents runtime inflation errors by catching type mismatches in the Studio Editor.

---

## 🛡️ Phase 8: Bulletproof Agencies (Agent Type Safety)
**Objective:** Replace loose dictionary inputs with Strict Pydantic Models for Agent Execution (`BaseAgent`).

- [x] **Strict Input Models**: Define `JudgeInput`, `ProfilerInput`, etc.
- [x] **Engine Validation**: Update `GraphEngine` to validate agent inputs using `state.get_context(..., InputModel)` **before** execution.
- [x] **Fail Fast (Pre-Flight)**: Prevent LLM calls if required inputs (e.g., `history_text`) are missing or invalid type.
- [x] **Benefit**: Reduces cost (no wasted API calls) and improves developer experience (IDE Autocomplete).


## 🧬 Phase 9: Agent DTO/Domain Separation (The Panel Pattern) (✅ Completed)
**Objective:** Eliminate LLM-hallucinated system metadata by strictly separating "LLM Content" from "System Authority".
**Owner:** @antigravity
**Status:** [x] Done. Pydantic V2 strictly separates Domain from Output DTOs, culminating in the BFF Transformer View Models for SDUI rendering.

### 9.1 Strict DTO Architecture
- [x] **DTO Definition**: All Agents MUST define a `*DTO` Pydantic model containing *only* the fields the LLM is responsible for.
- [x] **Domain Model Inheritance**: The full Domain Model MUST inherit from the DTO and add system-managed fields.
- [x] **BaseAgent Enforcement**: Update `BaseAgent` to enforce `DTO_SCHEMA` property.
- [x] **Authority Injection**: Python code (not LLM) is the sole authority for timestamps, versions, and agent identity.

### 9.2 Migration Plan
- [x] **Logician**: Split `LogicianOutput` -> `LogicianOutputDTO`.
- [x] **Falsifier**: Split `FalsifierData` -> `FalsifierDTO`.
- [x] **Causal**: Split `CausalAnalysis` -> `CausalDTO`.
- [x] **Profiler**: Split `ProfilerAnalysis` -> `ProfilerDTO`.
- [x] **Analyst**: Split `AnalystOutput` -> `AnalystDTO`.
- [x] **Judge**: Split `JudgeOutput` -> `JudgeDTO`.
- [x] **Critics**: Split `CritiqueResult` -> `CritiqueDTO`.

**Benefit:**
1.  **Zero Hallucination**: LLMs strictly cannot overwrite system timestamps or versions.
2.  **Schema Evolution**: We can change internal metadata structures without retraining LLMs.
3.  **Type Safety**: `BaseAgent` guarantees that `execute()` returns a fully hydrated Domain Object, empowering the BFF Transformers to map them fearlessly to SDUI View Models.
