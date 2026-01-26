**FEATURE REQUEST:**
> [WRITE HERE WHAT YOU WANT TO DO. E.g., "Create a new settings page where the user can change the application theme and language."]

---

**ROLE:** Senior Solutions Architect & Antigravity Specialist (2026 Context).

**GOAL:** Create a sequential, step-by-step execution plan to implement the feature request above using Google Antigravity, strictly adhering to the project's architecture mandates.

**REFERENCE MATERIAL:**
- **Primary Source of Truth:** `@docs/flutterpromptohje.md` (Read this file first).

**UX & ARCHITECTURE STANDARDS (MANDATORY):**

1.  **UX Principles:**
    -   **Optimistic UI:** UI updates state *immediately* upon user action. Saving happens in the background.
    -   **Fail Fast & Retry:** If an API call fails, revert the state, show a clear Toast/Snackbar, and offer a "Retry" button. Never block the UI.
    -   **Master-Detail Navigation:** -   **Left:** Navigation/List.
        -   **Center:** Editor/Main Content.
        -   **Right:** Contextual Help/Preview (if applicable).

2.  **Server-Driven Localization (Quorum System):**
    -   **Concept:** The Backend dictates UI text/labels based on the `Accept-Language` header sent by the Frontend.
    -   **Frontend:** `ApiClient` automatically handles the header. Do NOT hardcode strings. Use labels provided by the API schema.
    -   **Backend (Pydantic):** Use `x-ui-label` in `json_schema_extra` for default English labels.
        ```python
        # Example (domain.py):
        class MyModel(BaseModel):
            id: str
            json_schema_extra={
                "properties": {
                    "id": {"x-ui-label": "ID"}, # Default (EN)
                    "instruction": {"x-ui-label": "Instruction"} 
                }
            }
        ```
    -   **Backend (Translation):** Map English keys to target languages in `backend/l10n/{lang}.json`.
        ```json
        // backend/l10n/fi.json
        {
            "Instruction": "Ohjeistus",
            "Description": "Kuvaus"
        }
        ```
    -   **Frontend (Standard Translations):**
        -   Use `client_app/lib/l10n/app_{lang}.arb` for static app labels (Buttons, Titles, Menus) that are NOT driven by the backend.
        -   Run `flutter gen-l10n` after updates.
        ```json
        // client_app/lib/l10n/app_fi.arb
        {
            "loginBtn": "Kirjaudu",
            "settings": "Asetukset"
        }
        ```

**OUTPUT FORMAT REQUIREMENTS:**
1.  **Language Strategy:**
    -   **Antigravity Prompts (Code Blocks):** MUST be in **English**.
    -   **Your Explanations/Context:** MUST be in **Finnish** (Suomi).

2.  **Granularity (Atomic Strikes):**
    -   Break the task into small, isolated prompts (approx. 5-10 mins of AI work each).
    -   **Standard Sequence:**
        1.  Backend Dependencies (if any).
        2.  Backend Core/Models (Pydantic + x-ui-label).
        3.  Backend L10n Updates (JSON files).
        4.  Backend API/Router.
        5.  Frontend Models (Freezed) & Repository.
        6.  Frontend Controller (Riverpod + Optimistic Logic).
        7.  Frontend UI (Widgets/Screens - Master/Detail).

3.  **Strict File Scoping (Anti-Hallucination):**
    -   Each prompt header MUST explicitly list files in two categories:
        -   `TARGET (Modify):` Files the AI is allowed to edit.
        -   `CONTEXT (Read-Only):` Files the AI needs to read but **MUST NOT** touch.

4.  **Universal Mandate:** Every single prompt generated MUST end with the "UNIVERSAL MANDATE & CONSTRAINTS" block (provided below).

---

**APPEND THIS TO EVERY GENERATED PROMPT:**

**UNIVERSAL MANDATE & CONSTRAINTS (2026-01-24):**

1.  **ANTIGRAVITY CONTEXT:**
    -   Context: Jan 24, 2026. Phase 2 Hardening.
    -   Reference: `@docs/flutterpromptohje.md`.
    -   Execute this request as a single, isolated step.

2.  **STRICT FILE SCOPING:**
    -   **MODIFY ONLY** the files listed under `TARGET`.
    -   **READ ONLY** the files listed under `CONTEXT`.
    -   **DO NOT** create new files unless explicitly instructed.

3.  **ARCHITECTURAL BANS (Non-Negotiable):**
    -   **General:** NEVER delete repository methods or modify `requirements.txt`/`pubspec.yaml` versions without explicit approval.
    -   **Backend (Python):**
        -   NO `HTTPException` (Use `backend/exceptions.py` & RFC 7807).
        -   NO raw `dict` returns (Use Pydantic V2 models).
        -   **L10N ENFORCEMENT:** MUST use `json_schema_extra` with `x-ui-label` for all user-facing fields. MUST add corresponding keys to `backend/l10n/fi.json`.
    -   **Frontend (Flutter):**
        -   NO `ChangeNotifier` or manual `Provider` (Use `@riverpod` Generator ONLY).
        -   NO `setState` for business logic (UI state only).
        -   NO mutable data classes (Use `@freezed` models ONLY).
        -   NO hardcoded strings (Use API-provided labels or `.arb` for static system text).
        -   **UX ENFORCEMENT:** Implement Optimistic UI for mutations. Implement Retry logic for failures.

4.  **EDITING SAFETY (ANTI-DUPLICATION PROTOCOL):**
    -   **Strict Replacement:** When modifying an existing function/class, you MUST explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one.
    -   **Verification Check:** Before marking a step complete, scan the file structure. Ensure that `class MyClass` or `def my_function` does not appear twice.

5.  **DOCUMENTATION:**
    -   Language: **English Only** (Code, Comments, Logs).
    -   Style: Follow patterns in `@docs/flutterpromptohje.md`.

6.  **QUALITY LOOP (MANDATORY):**
    -   **Python:** `ruff check <target_files> --fix` -> `mypy <target_files>` -> `pytest <test_file>`.
    -   **Flutter:** `dart format <target_files>` -> `dart analyze <target_files>` -> `flutter test <test_file>`.
    -   **Rule:** Fix ALL errors before marking the step as complete.