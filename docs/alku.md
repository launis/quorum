# FAILFAST, NO FALLBACK, EI OLETUSARVOJA, EI KOVAKOODUSTA, EI QUICK FIXEJÄ, EI OIKOPOLKUJA

# COGNITIVE QUORUM - SESSION INITIALIZATION PROTOCOL
> **KÄYTTÄJÄLLE:** Aloittaaksesi uuden istunnon, pyydä tekoälyä lukemaan tämä tiedosto (esim. "Lue docs/alku.md"). Tämä lataa automaattisesti projektin kontekstin ja säännöt.

---

## TO THE AI ASSISTANT:
You have been activated to work on the **Cognitive Quorum** project (Phase 2 Hardening). Your immediate task is to **BOOTSTRAP** your context by following these steps strictly.

### 1. CRITICAL CONTEXT LOADER
**ACTION:** You MUST read and internalize the following documentation files immediately to understand the architecture, logic, and operational constraints:

*   **`docs/flutterpromptohje.md`** (The "System Architecture Manifesto" - **PRIMARY AUTHORITY**)
*   **`docs/documentation_strategy.md`** (The "Map": Explains roles of all docs)
*   **`docs/structured_cognitive_architecture.md`** (Understanding the "Why": Logic, Agents, Hybrid Rubric)
*   **`docs/Execute ohje.md`** (The "How-To": Feature Implementation Steps & Output Format)
*   **`docs/reference.md`** (The "Blueprints": Directory Structure, API & CLI Commands)
*   **`docs/api_models.md`** (The "Data": Pydantic Models & Schemas)

### 2. CORE MANDATES (Non-Negotiable)
*   **Tech Stack**: Python 3.14+ (FastAPI, Pydantic V2) & Flutter (Riverpod 3.0 Generator, GoRouter).
*   **SSOT Principle**: `backend/seed/seed_data.json` is the Single Source of Truth for logic. Never hardcode rules/steps in Python/Dart.
*   **State Management**: Use `@riverpod` annotations. Implement "Optimistic Update + Silent Invalidation".
*   **Error Handling**: Backend must raise typed `AppException` (RFC 7807). Fail fast; never swallow errors.
*   **Verification**: All changes must be verified against local Windows/PowerShell constraints.
*   **Code Generation**: Use `dart run build_runner build --delete-conflicting-outputs` for Riverpod/Freezed/JsonSerializable. **Do not use** deprecated `flutter pub run`.

### 3. OUTPUT FORMAT
*   **Code**: Standard English.
*   **Explanations**: Finnish (Suomi).

### 4. DEBUGGING RESOURCES (Local Development)
*   **`backend_debug.log`** (Project Root): Contains full Backend logs (Uvicorn, FastAPI, Arq). Use this to debug startup crashes, 500 errors, and database queries.
*   **`client_debug.log`** (Project Root): Contains Flutter Client logs (Riverpod state changes, Navigation, HTTP errors). Use this to debug UI freezes or "Something went wrong" errors.
*   **Note**: `run_local.bat` clears these files on every fresh start to ensure clean traces.

**5. DATABASE INITIALIZATION (Seeding)**
To reset the database state (workflows, users, configs) to the official "Seed State":

*   **Local (Default)**: `python backend/seed/run_seed.py local`
    *   *Effect*: Resets `data/db.json` (used by `run_local.bat` for prod-like simulation).
*   **Mock (Testing)**: `python backend/seed/run_seed.py mock`
    *   *Effect*: Resets `backend/database/db_mock.json` (used for unit tests and rapid prototyping).
*   **Firestore (Cloud)**: `python backend/seed/run_seed.py firestore`
    *   *Effect*: Resets the Google Cloud Firestore database (Live Environment). **Use with extreme caution.**

**CONFIRMATION:**
State clearly that you have read the files and are ready to proceed under the Phase 2 Hardening standards.
