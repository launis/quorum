**FEATURE REQUEST:**
> [KIRJOITA TÄHÄN MITÄ HALUAT TEHDÄ. Esim: "Tee uusi asetussivu, jossa käyttäjä voi vaihtaa sovelluksen teemaa ja kieltä."]

---

**ROLE:** Senior Solutions Architect & Antigravity Specialist (2026 Context).

**GOAL:** Create a sequential, step-by-step execution plan to implement the feature request above using Google Antigravity, strictly adhering to the project's architecture mandates.

**REFERENCE MATERIAL:**
- **Primary Source of Truth:** `@docs/flutterpromptohje.md` (Read this file first to understand the architecture).

**OUTPUT FORMAT REQUIREMENTS:**
1.  **Language Strategy:**
    -   **Antigravity Prompts (Code Blocks):** MUST be in **English**.
    -   **Your Explanations/Context:** MUST be in **Finnish** (Suomi).

2.  **Granularity (Atomic Strikes):**
    -   Break the task into small, isolated prompts (approx. 5-10 mins of AI work each).
    -   **Standard Sequence:**
        1.  Backend Dependencies (if any).
        2.  Backend Core/Models (Pydantic).
        3.  Backend API/Router.
        4.  Frontend Models (Freezed) & Repository.
        5.  Frontend Controller (Riverpod).
        6.  Frontend UI (Widgets/Screens).

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

3.  **ARCHITECTURAL BANS (Non-Negotiable - per `flutterpromptohje.md`):**
    -   **General:** NEVER delete repository methods or modify `requirements.txt`/`pubspec.yaml` versions without explicit approval.
    -   **Backend (Python):**
        -   NO `HTTPException` (Use `backend/exceptions.py` & RFC 7807).
        -   NO raw `dict` returns (Use Pydantic V2 models).
        -   NO hardcoded logic/prompts (Use Metadata/DB-driven execution).
        -   NO "Fallback" values (Fail fast if DB config missing).
    -   **Frontend (Flutter):**
        -   NO `ChangeNotifier` or manual `Provider` (Use `@riverpod` Generator ONLY).
        -   NO `setState` for business logic (UI state only).
        -   NO mutable data classes (Use `@freezed` models ONLY).
        -   NO raw string navigation (Use `GoRouter` & type-safe `GoRouteData`).
        -   NO hardcoded strings (Use `.arb` localization).

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