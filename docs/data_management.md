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
The BFF Layer (`bff_transformer.py`) supports two formats:

1.  **Wrapped (Standard)**: Output from standalone agents matches the Pydantic definition exactly.
2.  **Unwrapped (Panel)**: Output from the Panel Agent is "flattened" when extracted.

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
