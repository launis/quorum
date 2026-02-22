# Data Management & Databases (V3.2)

The engine is **data-driven**: logic definitions are stored in JSON (the "Mind"), but strict data contracts are enforced via Python/Dart code (the "Body").

> [!IMPORTANT]
> **V3.2 Standard (Strict Pydantic & Zero-Compromise)**
> All internal state management MUST use **Pydantic V2 Models**. Dictionary passing (`dict[str, Any]`) is strictly forbidden for inter-component communication. If a field is missing, the system **Fail Fasts** with `AppException`.

---

## 1. The Blueprint Authority Pattern

The system treats `backend/seed/seed_data.json` as the absolute **Single Source of Truth** for all configuration, organizations, users, and cognitive templates.

*   **Zero-Fallback Mandate**: Hardcoded defaults in code are strictly forbidden. If data is missing from the database, the system must **raise an error** rather than guessing.
*   **Directionality**:
    *   **Source**: `seed_data.json`
    *   **Target**: Runtime Databases (Mock, Local, Cloud).
    *   **Reverse Sync**: Use `scripts/migrate_to_seed.py` to promote high-fidelity runtime data (`db.json`) back to the blueprint structure properly. This script handles the complex transformation from flat lists to the seeded `components` structure.

---

## 2. The 3-Tier Data Model

The system utilizes a 3-tier hierarchy to differentiate between development speeds and production fidelity.

### Tier 1: Local Mock (`backend/database/db_mock.json`)
*   **Purpose**: Rapid offline development, unit tests, and "clean slate" logic verification.
*   **Inference**: Uses `USE_MOCK_LLM=true` (Zero-Cost).
*   **Storage**: `TinyDB`.
*   **Seeding**: `python backend/seed/run_seed.py mock`

### Tier 2: Local Production (`data/db.json`)
*   **Purpose**: High-fidelity verification with **Live Vertex AI** models but local storage.
*   **Inference**: Uses Real LLMs (Cost incurred). Perspectives persist across restarts.
*   **Storage**: `TinyDB` (mimicking Firestore document structure).
*   **Seeding**: `python backend/seed/run_seed.py local`

### Tier 3: Cloud Production (Firestore)
*   **Purpose**: Multi-tenant SaaS operations in Google Cloud (`europe-north1`).
*   **Inference**: Real LLMs.
*   **Storage**: Google Cloud Firestore (Native).
*   **Seeding**: `python backend/seed/run_seed.py firestore`

---

## 3. Backend Data Layer (`backend/`)

### 3.0. The "No-ORM" Pydantic Architecture
The Cognitive Quorum backend is uniquely designed **without any traditional Object-Relational Mappers (ORMs)**. There is no SQLAlchemy, Django ORM, Prisma, or isolated database schema definitions. 

**Pydantic V2 is the Absolute Single Source of Truth (SSOT).**
*   **Validation**: Pydantic validates incoming API requests.
*   **Datastore**: Pydantic defines the structure written to the database (TinyDB/Firestore).
*   **Documentation**: Pydantic generates the OpenAPI specifications.
*   **Seeding**: Pydantic dictates what the seeder scripts accept.

Because NoSQL document stores (TinyDB / Firestore) are used, the system avoids "Object-Relational Impedance Mismatch." Adding a new field to a Pydantic model instantly propagates it throughout the entire slice of the application—from the database to the REST API—without requiring explicitly coded database migrations.

### Unified Workflow Repository & Storage Drivers
The system abstracts data access via the **Storage Driver Pattern**, enabling a single repository implementation to support multiple backends with identical business logic.

#### 1. The Protocol (`backend/database/driver.py`)
The `StorageDriver` protocol defines the contract for all CRUD and Query operations.
*   **Methods**: `get`, `upsert`, `update`, `delete`, `query`, `count`.
*   **Filters**: Abstract `Filter` objects (field, operator, value) are translated by the driver into native queries.

#### 2. The Repository (`backend/database/repository.py`)
*   **Class**: `UnifiedWorkflowRepository`
*   **Role**: Contains all business logic (e.g., aggregating metrics, complex filtering, schema hydration).
*   **Behavior**: Distinctly separates I/O (Driver) from Logic (Repository).

#### 3. Driver Implementations
*   **TinyDBDriver** (`backend/database/tinydb_driver.py`):
    *   **Backend**: Local JSON file (`TinyDB`).
    *   **Behavior**: Serializes datetime/UUIDs to JSON strings.
*   **FirestoreDriver** (`backend/database/firestore_driver.py`):
    *   **Backend**: Google Cloud Firestore (Native).
    *   **Behavior**: Uses `google-cloud-firestore` AsyncClient.

### Strict Pydantic V2 & Agent Typing (Phase 8)
The system utilizes **Pydantic V2** for all internal state management.

1.  **Strict Models**: All Agents and Hooks must accept and return Pydantic models (e.g., `JudgeInput`, `JudgeOutput`).
2.  **Generic Typing**: Agents inherit from `BaseAgent[InputT, OutputT]`. This enforces compile-time type checking for the `execute` method signature.
    *   *Violation*: Passing a `dict` to an agent expecting `PanelInput` raises a static type error and a runtime validation error.
3.  **Inflation / Deflation**:
    *   **Inflate**: `backend.utils.pydantic_utils.inflate(data, Model)` converts DB/Dict data to strict Models. Raises `AppException(500)` on failure.
    *   **Deflate**: `model.model_dump()` converts Models to Dicts for storage/serialization.
4.  **Strict Enums Only**: Data must match Enum values exactly.
5.  **Modular Domain**: Models are organized in `backend/models/domain/` to enforce strict separation of concerns.
6.  **The Hybrid Dict/Model Pattern (Internal Resilience)**:
    *   **Concept**: While agents *must* return Pydantic models to the Engine, they accept `dict` inputs internally during the `post_process` phase.
    *   **Reasoning (The Healing Pattern)**: LLMs often return JSON with minor structural defects (e.g., missing IDs). By keeping data as a `dict` until the late validation phase, the agent's `post_process` hook can sanitize and fix the data before strict Pydantic enforcement kicks in.
    *   **Testing**: This simplifies testing by allowing developers to pass simple dicts instead of constructing complex nested objects.

### 3.1. The Domain-DTO Dual Architecture
To strictly separate "Content" from "System Authority", the system employs a **Domain(DTO)** inheritance pattern.

1.  **DTOs (`backend/models/dtos/`)**:
    *   **Role**: The **Content Contract**.
    *   **Definition**: Represents data in transit (LLM Input/Output, API Requests).
    *   **Constraint**: MUST NOT contain system-managed fields (e.g., `id`, `timestamp`, `cost`, `metadata`). This prevents the LLM from hallucinating authoritative data.
    *   **Example**: `AnalystDTO` contains only `hypotheses` and `rag_evidence`.

2.  **Domain Models (`backend/models/domain/`)**:
    *   **Role**: The **System Authority** (Single Source of Truth).
    *   **Definition**: Represents the full, persisted state of an entity.
    *   **Inheritance**: `class AnalystOutput(AnalystDTO, ReasoningTrace): ...`
    *   **Mechanism**: The Backend accepts a DTO (Content), validates it, generating necessary Metadata (Authority), and fuses them into a Domain Object.
    *   **Usage**: The Pipeline *only* reads Domain Models. DTOs are never persisted directly as state.

---

## 4. Client-Side Data Layer (Flutter)

The Flutter client mirrors the backend's strictness but uses a distinct architectural pattern tailored for mobile/web resilience.

### Feature-Scoped Repositories
Repositories are distributed by feature (e.g., `client_app/lib/features/studio/data/studio_repository.dart`).

### Error Handling Standard
*   **Pattern**: Repositories **throw** exceptions (`AppError`), they do NOT return `Either<L, R>`.
*   **Rationale**: Simplifies `Riverpod` wiring (`AsyncValue.guard`).
*   **Mapping**:
    *   `DioException` (400/500) -> `AppError.server` or `AppError.validation`.
    *   `Code 422` -> `AppError.validation` with broken constraints.

### DTOs and Serialization
*   **Strict Typing**: All API responses are mapped to rigid Dart classes using `json_serializable`.
*   **Parity**: Dart models must exactly match the Pydantic schemas. A mismatch causes a crash (Fail-Fast).

---

## 5. Schema Hygiene

*   **Run-at-Boot**: All core workflows must be fully defined and runnable immediately after seeding.
*   **WorkflowInputs**: The `inputs` field in `WorkflowState` is a strict `WorkflowInputs` object.
*   **Ontology Registry**: Evaluation matrices (`evaluation_matrix`) are stored in the `components` table but reference dimensions from the `ontology` configuration.

---

## 6. File Storage Strategy

The system abstracts file operations via the **File Driver Pattern** (`backend/services/file_driver.py`).

### Driver Implementations
1.  **LocalFileDriver**: Local file system (`data/files/`).
2.  **GCSFileDriver**: Google Cloud Storage (`europe-north1`).

### Dependency Injection
The `StorageService` factory (`backend/services/storage.py`) determines the active driver based on environment settings.

---

## 7. Specialist Data Interchange Protocols

To ensure robust UI rendering across different backend configurations (Standalone Agents vs. Consolidated Panel), the system mandates a strict data interchange protocol.

### 7.1. Fused Data Hydration (Panel Agent)
The Panel Agent represents a "Fusion" of multiple critical roles (`Logician`, `Falsifier`, `Causal`, `Detector`, `Overseer`).

1.  **Strict Inputs**: The `PanelInput` model strictly defines fields for `step_analyst` (AnalystOutput) and `step_profiler` (ProfilerAnalysis).
2.  **Fail Fast**: If these dependencies are missing, the Panel Agent raises `AgentExecutionError`.
3.  **Template Injection**: These models are serialized and injected into the `PANEL_PROMPT_TEMPLATE`.

### 7.2. The "Wrapped vs. Unwrapped" Dual Standard
The BFF Layer (`bff_transformer.py` / SDUI Domain Transformers) must structurally support two distinct payload formats without relaxing the strict Pydantic validation:

1.  **Wrapped (Standalone Output - e.g. `PerformativityOutput`)**:
    *   **Source**: A standalone specialist agent (e.g., LogicianAgent natively running).
    *   **Structure**: Contains the full `ReasoningTrace` (e.g., `thought_process`, `conclusion`) wrapping the core domain logic.
    *   **Validation**: Must pass complete Pydantic validation.

2.  **Unwrapped (Panel Consolidation - e.g. `PerformativityAnalysis`)**:
    *   **Source**: The `PanelAgent`, which strips away external metadata and only outputs the deeply nested *core domain object* for maximum LLM context efficiency.
    *   **Structure**: Contains *only* the inner data (e.g., `LogicianData`, `PerformativityAnalysis`).
    *   **Pipeline Action (Dynamic Reconstruction)**: Custom Transformer logic (e.g., within `_extract_detector_section`) MUST actively detect if it only received the inner data. If so, it must construct the outer shell (e.g., `PerformativityOutput(...)`) *on the fly*, injecting default reasoning traces to satisfy strict schema requirements before continuing the SDUI translation.

### 7.3. UI Safety Mandate (UiSection)
*   The `UiSection.data` field is strictly typed as `dict[str, Any]`.
*   **Prohibition**: Never pass `None`.
*   **Requirement**: Data Transformers must return an empty dictionary `{}` if the input data is missing or invalid.

---

## 9. Component & Configuration Architecture (V3.2)

### 9.1. Component Registry & Prompt Resolution
The system decouples "Instructions" (Prompts) from "Logic" (Agents).
*   **Storage**: Prompts are stored as `Component` records in the database (`seed_data.json` -> `db.json`).
*   **Resolution**: The `TaskRegistry` automatically fetches prompts defined in a Task's `llm_prompts` configuration list.
*   **Injection**: Resolved prompts are injected into the Agent's `execution_context`. The Agent uses these keys (e.g., `PANEL_PROMPT_TEMPLATE`) to structure its LLM call.

### 9.2. External Integrations (Search & Gating)
External tools (like `VertexAISearchTool`) are gated via strict configuration toggles to ensure environment portability.
*   **Flag**: `enable_vertex_search` (Settings).
*   **Behavior**: If disabled (`False`), the tool gracefully degrades (returns empty results) rather than crashing.
*   **ConfigurationError**: If enabled but missing credentials (e.g., Model ID), the system raises a specific `ConfigurationError` to prevent silent failures during startup.

---

## 8. Case Studies and Patterns

### 8.1. Lazy Dictionary Inflation Pattern (Resilience vs. Strictness)

**The Problem:**
Strict Schema Enforcement (e.g., `results: WorkflowState`) in storage models creates a brittle system. If the `WorkflowState` schema evolves (e.g., a field is renamed), older records in the database immediately fail validation during bulk read operations (e.g., listing history), causing the entire application to crash.

**The Solution:**
We employ a **Lazy Dictionary Inflation** pattern for historical data.
*   **Storage Model**: `results: WorkflowState | Dict[str, Any] | None`. This allows Pydantic to load old/mismatched records as raw Dictionaries without crashing.
*   **Logic Layer**: Agents accessing this data MUST implement **Just-In-Time Inflation**.

**Case Study: The RetrievalAgent Incident (Feb 2026)**
The `RetrievalAgent` crashed because it attempted to access `wf_state.execution_trace` (dot notation) on a historical record that had been loaded as a `dict` (due to the safe storage union). It was the only agent proactively fetching raw history from the DB.

**The Fix:**
The agent was patched to detect `dict` types and force inflation *before* usage:
```python
# RECOVERY: If Pydantic loaded results as strict Dict, inflate it here.
if isinstance(wf_state, dict):
     try:
         wf_state = WorkflowState.model_validate(wf_state)
     except Exception as e:
         logger.warning(f"Failed to auto-inflate execution: {e}")
         # Fallthrough to Fail-Fast
```
This ensures resilience (DB doesn't crash on load) and integrity (Logic layer verifies schema before use).

---

## 10. Model Strategy Architecture (V3.2)

The system employs a specific architectural pattern to decouple **Semantic Intent** from **Operational Constraints**. This ensures the system's "Deep" reasoning capabilities are defined correctly, even if operational limits (e.g., Google Quotas) require temporary downgrades.

### 10.1. Semantic Strategies (Definitions)
Strategies define *what* a model class represents in the system architecture, regardless of the underlying provider model.

*   **`deep` / `precise`**:
    *   **Intent**: High-Reasoning capability (PRO Tier). Used for complex analysis, judging, archiving, and causal inference.
    *   **Target Model**: Typically `vertex_ai/gemini-2.5-pro` (or equivalent high-intelligence model).
*   **`fast` / `strict`**:
    *   **Intent**: High-Throughput / Low-Latency capability (FLASH Tier). Used for reporting, interaction, and initial filtering.
    *   **Target Model**: `vertex_ai/gemini-2.5-flash`.

### 10.2. Operational Mapping (Agent Assignment)
While strategies are defined globally, the `system_config` table maps specific Agents to these strategies.

*   **Default State**:
    *   `AnalystAgent` -> `deep` (Pro).
    *   `JudgeAgent` -> `precise` (Pro).
*   **Operational Mitigation (The "Flash Override" Pattern)**:
    *   **Problem**: In high-concurrency environments, Pro models often hit `429 Resource Exhausted` errors due to low quotas (e.g., 5 RPM).
    *   **Solution**: We can **re-map** specific Agents to lighter strategies (e.g., `fast` / Flash) in the database *without changing the semantic definition of "Deep"*.
    *   **Mechanism**: Change `models["AnalystAgent"] = "fast"` in `db.json`.
    *   **Result**: The Agent runs successfully using the lighter model to bypass rate limits, while the system still conceptually understands that `deep` generally refers to the Pro tier for future scalability.

### 10.3. Rate Limit Management
Limits are enforced at the **Strategy Definition** level in the database (`limits` object).
*   **Pro Bucket**: Shared by all agents using `deep`/`precise`. (e.g., 500k TPM).
*   **Flash Bucket**: Shared by all agents using `fast`/`strict`. (e.g., 2M TPM).
*   **Tuning**: When re-mapping agents to Flash, ensure the Flash strategy has sufficient TPM/RPM limits (e.g., `max_tokens: 65536` to match Flash limits) to handle the increased load.

---

## 11. Database Schema & Firestore Deployment Strategy

The Cognitive Quorum database architecture operates fundamentally under NoSQL best practices. The transition from local `db.json` to Google Cloud Firestore dictates how collections are segregated to guarantee infinite scalability and high-performance querying without relational `JOIN` penalties.

### 11.1. Polymorphic Collections (The Components Table)
In a relational model, UI Components, Evaluation Matrices, and Output Configurations might live in distinct SQL tables. In our NoSQL architecture, these are purposefully **consolidated into a single `components` collection** leveraging a polymorphic "type" discriminator.

*   **The NoSQL Join Penalty:** Firestore does not support relational JOINs. If matrices and text inputs were separated, rendering a single Dashboard `Step` would require multiple independent HTTP round-trips to the database. By consolidating them, the frontend retrieves the entire UI layout in one continuous stream or a single queried batch (`O(1)` request efficiency).
*   **Polymorphic Reconstruction:** The backend Pydantic tier seamlessly reconstructs these grouped objects back into their native strongly-typed DTOs (e.g., `EvaluationMatrix`, `OutputConfig`) locally parsing the `"type"` field during API egress.
*   **Seeder Integrity (`seed_registry.py`)**: Our centralized seeder extracts these from `seed_data.json` visually segregated lists but forcefully pushes them back into the unified `components` collection, abstracting the NoSQL complexity from developers.

### 11.2. Isolated Entities (Users & Organizations)
Unlike polymorphic data units, Core Entities (like `users` and `organizations`) are strictly isolated into their own dedicated collections.

*   **Security & Granular Permissions (Firestore Rules):** Firestore Security Rules (`firestore.rules`) are enforced path-dependently. Keeping `users` and `organizations` separated allows the system to enforce explicit ACL boundary rules (e.g., `match /users/{userId}` allows self-read, whereas `match /organizations/{id}` requires an `admin` role cache verification).
*   **Hierarchical Scaling:** Core entities represent independent hierarchies rather than bundled presentation parts. The system queries an Organization's configuration uniquely to enforce quotas long before user-level inputs or component layouts are even evaluated. Attempting to group structural entities limits database-level index efficiencies.

### 11.3. Knowledge Base Decoupling (Strict SSO Separation)
Previously, the system utilized a polymorphic "One Big Table" approach (`knowledge_base`) to store concepts, references, and claims. To align with the strict Domain-DTO isolation and ensure higher query performance, this was forcefully decoupled.
*   **Separation of Concerns**: The monolithic `knowledge_base` array is entirely deleted. It has been replaced by three completely independent, strict SSOT physical collections: `concepts`, `references`, and `claims`.
*   **Metadata Stripping**: During this transition, unauthorized data bags (`metadata`, `hoist_keys`) were stripped completely out of the domain models and the underlying database documents. The NoSQL backend now guarantees type-pure collections without any ghost data fields.