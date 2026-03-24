# Unified Naming Strategy (V5.1 - Phase 9 Hardening)

This document defines the strict naming conventions for the Cognitive Quorum system. In a system where data traverses from Database -> Pydantic Domain -> Riverpod State (SafeCast) -> Flutter UI, inconsistent naming causes serialization errors, null pointer exceptions, and type mapping failures.

## 1. Core Principle: "Backend is the Authority"

The database (TinyDB/Firestore) and the Pydantic Domain models dictate the actual state of the system. The naming convention must always **originate from the Backend** and flow down to Flutter. Flutter developers should never have to guess or manually remap field names.

**The Golden Rule:** If a field is named `dimension_id` in the Pydantic model, it must be exactly `dimension_id` in the JSON payload, and the Flutter JSON deserialization.

## 2. JSON Data Exchange Standard (Snake Case)

The system transfers data in JSON format. The universal standard for JSON—and the native format for Python—is **snake_case** (lowercase letters, words separated by underscores). All data moving across the network MUST adhere to this standard.

*   **Pydantic (Python Backend):** `dimension_id: str`
*   **JSON DTO (Network Layer):** `{"dimension_id": "logic"}`
*   **Freezed (Dart Frontend):** `@JsonKey(name: 'dimension_id') required String dimensionId`

> [!IMPORTANT]
> **Dart Implementation Note:** Dart code must always use `camelCase` internally (e.g., `dimensionId`). However, at the integration boundary (JSON parsing), the `@JsonKey` annotation MUST explicitly map to the backend's `snake_case` name. Manual `Map['field_name']` parsing in UI components is strictly prohibited.

## 3. Field Naming Guidelines

Names must be explicit and unambiguous.

*   **Avoid Generic Names (`id`, `name`, `type`):**
    *   *Bad:* `id` (ID of what?)
    *   *Good:* `dimension_id`, `agent_id`, `step_id`, `execution_id`.
*   **Avoid "Frontend Leaks" in Backend Logic (`key`, `label`, `display`):**
    *   If a field contains a localization key, name it clearly: `name_l10n_key` or `label_key`.
    *   If it is a directly translated text value, name it: `dimension_name` or `dimension_label`.
*   **Be Explicit with Booleans:**
    *   *Bad:* `proven: bool` (What is proven?)
    *   *Good:* `is_evidence_found: bool` or `is_verified: bool`.

## 4. Function and Method Naming Synchronization

Naming consistency applies beyond data models; it extends to the operational functions and methods across both the Backend (Python) and Frontend (Dart) codebases.

*   **Symmetrical Operations:** If the backend provides an endpoint or service method named `get_execution_report()`, the corresponding repository method in Flutter should be named `getExecutionReport()`.
    *   *Backend:* `def fetch_user_profile(user_id: UUID) -> UserProfile:`
    *   *Frontend:* `Future<UserProfile> fetchUserProfile(String userId)`
*   **Clear Action Verbs:**
    *   Use `get` for retrieving data without side-effects.
    *   Use `fetch` for operations that explicitly reach out to an external service or database.
    *   Use `create`, `update`, `delete` for CRUD operations.
    *   Use `execute` or `run` for triggering complex workflows (`execute_workflow`).
*   **Avoid Synonyms for the Same Action:** Do not mix `retrieve`, `fetch`, and `get` for the same type of operation within the same context. Pick one and stick to it universally.

## 5. Implementation Workflow for New Features

When building a new feature or model, follow this exact sequence:

1.  **Define Pydantic Domain Model (Backend Python)**
    *   Create strict Pydantic models in `backend/models/domain/*.py`.
    *   Use strict `snake_case` naming.
    *   *Example:* `class LogicianOutput(BaseModel): argument_score: float`
2.  **Verify Omni-Channel Endpoints (Backend Python)**
    *   Ensure the rendered outputs mirror the strict naming convention before data crosses the API boundary into UI hints.
3.  **Create Dart Freezed Model (Frontend Flutter)**
    *   Create a Dart class that perfectly matches the Pydantic schema.
    *   Apply `@JsonKey(name: 'snake_case_name')` annotations to **every single field** received from the backend to guarantee correct JSON-to-Dart mapping.
    *   Run code generation: `dart run build_runner build -d`.

By following these rules, the pipeline `Agent -> Database -> Riverpod State -> Flutter UI` remains unbroken, type-safe, and highly predictable.
