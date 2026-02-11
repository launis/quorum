# Data Management & Databases (V2.9/V2026)

The engine is **data-driven**: logic definitions are stored in JSON (the "Mind"), but strict data contracts are enforced via Python/Dart code (the "Body").

---

## 1. The Blueprint Authority Pattern

The system treats `backend/seed/seed_data.json` as the absolute **Single Source of Truth** for all configuration, organizations, users, and cognitive templates.

*   **Zero-Fallback Mandate**: Hardcoded defaults in code are strictly forbidden. If data is missing from the database, the system must **fail fast** rather than guessing.
*   **Directionality**:
    *   **Source**: `seed_data.json`
    *   **Target**: Runtime Databases (Mock, Local, Cloud).
    *   **Reverse Sync**: Use `sync_db_to_seed.py` to promote high-fidelity runtime data back to the blueprint.

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
*   **Behavior**: It delegates raw I/O to the injected `StorageDriver`. This ensures that logic like "fetch all steps for a workflow" is written once and works everywhere.

#### 3. Driver Implementations
*   **TinyDBDriver** (`backend/database/tinydb_driver.py`):
    *   **Backend**: Local JSON file (`TinyDB`).
    *   **Behavior**: Serializes datetime/UUIDs to JSON strings. Implements in-memory filtering for complex queries.
*   **FirestoreDriver** (`backend/database/firestore_driver.py`):
    *   **Backend**: Google Cloud Firestore (Native).
    *   **Behavior**: Uses `google-cloud-firestore` AsyncClient. Maps abstract filters to native `where()` clauses.
    *   **Parity**: Enforces strict serialization parity with TinyDB (e.g., storing Datetime as ISO strings if needed for consistency).

### Strict Pydantic V2
The system utilizes **Pydantic V2** for all internal state management.
1.  **Strict Mode**: Models use `ConfigDict(extra="ignore")` to silently strip unknown fields during ingestion, but validation is rigid on required fields.
2.  **Validation Trap**: If `seed_data.json` contains a field (e.g., `ui_schema`) but the Pydantic model does not define it, the data will be lost during seeding. Both must be kept in sync.
3.  **Strict Enums Only**: Data must match Enum values exactly (e.g., "RISK_HIGH", not "High Risk"). Fuzzy logic is deprecated.
3.  **Storage Abstraction**: The `get_db_client()` factory (`backend/database/wrapper.py`) dynamically returns a `TinyDBClient` or `FirestoreClient` based on the `STORAGE_BACKEND` env var.

---

## 4. Client-Side Data Layer (Flutter)

The Flutter client mirrors the backend's strictness but uses a distinct architectural pattern tailored for mobile/web resilience.

### Feature-Scoped Repositories
Repositories are no longer monolithic. They are distributed by feature (e.g., `client_app/lib/features/studio/data/studio_repository.dart`).

### Error Handling Standard
*   **Pattern**: Repositories **throw** exceptions (`AppError`), they do NOT return `Either<L, R>`.
*   **Rationale**: This simplifies the `Provider`/`Riverpod` wiring, allowing the UI to catch errors via `AsyncValue.guard`.
*   **Mapping**:
    *   `DioException` (400/500) -> `AppError.server` or `AppError.validation`.
    *   `Code 422` -> `AppError.validation` with broken constraints.
    *   Network Failure -> `AppError.network`.

### DTOs and Serialization
*   **Strict Typing**: All API responses are mapped to rigid Dart classes using `json_serializable`.
*   **Parity**: Dart models must exactly match the Pydantic schemas. A mismatch in a required field (e.g., `name` vs `title`) causes a crash, enforcing the **Fail-Fast** principle.

---

## 5. Schema Hygiene

*   **Run-at-Boot**: All core workflows (e.g., `sequential_audit_chain`) must be fully defined and runnable immediately after seeding.
*   **UI Schema**: The Frontend renders inputs based on the `ui_schema` field in `WorkflowDefinition`. If this component is missing or empty in the seed, the UI will render an empty form (Zero-Fallback).
*   **Ontology Registry**: Evaluation matrices (`evaluation_matrix`) are stored in the `components` table but reference dimensions from the `ontology` configuration.

---

## 6. File Storage Strategy

The system abstracts file operations via the **File Driver Pattern** (`backend/services/file_driver.py`), ensuring parity between local development and cloud production.

### The Protocol (`FileDriver`)
The `FileDriver` protocol defines the ASYNC contract for file I/O:
*   **Methods**: `save`, `read`, `delete`, `exists`, `get_url`.
*   **Async-First**: All operations are non-blocking (`await driver.save(...)`), critical for high-throughput API endpoints.

### Driver Implementations
1.  **LocalFileDriver** (`backend/services/drivers/local_file_driver.py`):
    *   **Backend**: Local file system (`data/files/`).
    *   **Implementation**: Uses `aiofiles` for asynchronous I/O.
    *   **Usage**: Default for development and testing.

2.  **GCSFileDriver** (`backend/services/drivers/gcs_file_driver.py`):
    *   **Backend**: Google Cloud Storage.
    *   **Implementation**: Wraps `google-cloud-storage` sync client in `asyncio.to_thread` (or uses AsyncClient if available).
    *   **Usage**: Production (`STORAGE_BACKEND=FIRESTORE` implies GCS for files).

### Dependency Injection
The `get_storage_client()` factory (`backend/services/storage.py`) determines the active driver based on environment settings, ensuring code agnostic of the underlying storage mechanism.

---

## 7. Specialist Data Interchange Protocols

To ensure robust UI rendering across different backend configurations (Standalone Agents vs. Consolidated Panel), the system mandates a strict data interchange protocol.

### 7.1. The "Wrapped vs. Unwrapped" Dual Standard
The BFF Layer (`bff_transformer.py`) must support two formats for specialist data (Logician, Falsifier, Causal, Detector, Overseer):

1.  **Wrapped (Standard)**: Output from standalone agents matches the Pydantic definition exactly.
    *   Example: `LogicianOutput(logician_data={...})` -> JSON `{ "logician_data": {...} }`.
2.  **Unwrapped (Panel)**: Output from the Panel Agent is "flattened" when extracted.
    *   Example: `PanelOutput(logician_data={...})` -> extracted as `{...}` directly.

### 7.2. UI Safety Mandate (UiSection)
*   The `UiSection.data` field is strictly typed as `dict[str, Any]`.
*   **Prohibition**: Never pass `None`.
*   **Requirement**: Data Transformers must return an empty dictionary `{}` if the input data is missing or invalid, ensuring the UI component renders (as empty/hidden) rather than crashing the report generation with a 500 error.
