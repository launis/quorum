# FAILFAST, NO FALLBACK, EI OLETUSARVOJA, EI KOVAKOODUSTA, EI QUICK FIXEJÄ, EI OIKOPOLKUJA

# COGNITIVE QUORUM - SESSION INITIALIZATION PROTOCOL (V3.2)
> **KÄYTTÄJÄLLE:** Aloittaaksesi uuden istunnon, pyydä tekoälyä lukemaan tämä tiedosto (esim. "Lue docs/alku.md"). Tämä lataa automaattisesti projektin kontekstin ja säännöt.

---

## TO THE AI ASSISTANT:
You have been activated to work on the **Cognitive Quorum** project (Phase 8/9 Hardening). Your immediate task is to **BOOTSTRAP** your context by following these steps strictly.

### 1. CRITICAL CONTEXT LOADER
**ACTION:** You MUST read and internalize the following documentation files immediately to understand the architecture, logic, and operational constraints:

*   **`docs/index.md`** (The "Master Index": Entry point for V3.2 Architecture)
*   **`docs/flutterpromptohje.md`** (The "System Architecture Manifesto" - **PRIMARY AUTHORITY**)
*   **`docs/documentation_strategy.md`** (The "Map": Explains roles of all docs)
*   **`docs/structured_cognitive_architecture.md`** (The "Mind": Panel Fusion, Strict DTOs)
*   **`docs/workflow_data_architecture.md`** (The "Data Flow": Fan-Out Pattern)
*   **`docs/reference.md`** (The "Blueprints": Directory Structure, Env Vars)
*   **`docs/api_models.md`** (The "Data": Pydantic Models & Schemas)

### 2. CORE MANDATES (Non-Negotiable)
*   **Tech Stack**: Python 3.14+ (FastAPI, Pydantic V2 Strict) & Flutter (Riverpod 3.0 Generator).
*   **SSOT Principle**: `backend/seed/seed_data.json` is the Single Source of Truth for logic, including **System Config** (Agent Strategies). Never hardcode rules/models/prompts in Python.
*   **Zero-Fallback**: Logic must Fail Fast (`AppException`) if configuration is missing in the DB. Do not use hardcoded defaults.
*   **Strict DTO Pattern**: LLMs generate `*OutputDTO` (Content). Python generates `*Output` (Domain Authority). Never mix them.
*   **Error Handling**: Backend must raise typed `AppException` (RFC 7807). Fail fast; never swallow errors.

### 3. OUTPUT FORMAT
*   **Code**: Standard English.
*   **Explanations**: Finnish (Suomi).

### 4. DEBUGGING RESOURCES (Local Development)
*   **`backend_debug.log`** (Project Root): Contains full Backend logs (Uvicorn, FastAPI, Arq). Use this to debug startup crashes, 500 errors, and database queries.
*   **`client_debug.log`** (Project Root): Contains Flutter Client logs.
*   **Note**: `run_local.bat` clears these files on every fresh start to ensure clean traces.

**5. DATABASE INITIALIZATION (Seeding)**
To reset the database state to the official "Seed State":

*   **Local (Default)**: `python backend/seed/run_seed.py local`
    *   *Effect*: Resets `data/db.json` from `seed_data.json`.
*   **Mock (Testing)**: `python backend/seed/run_seed.py mock`
    *   *Effect*: Resets `backend/database/db_mock.json`.
*   **Firestore (Cloud)**: `python backend/seed/run_seed.py firestore`
    *   *Effect*: Resets the Google Cloud Firestore database. **Use with extreme caution.**

**CONFIRMATION:**
State clearly that you have read the files and are ready to proceed under the Phase 8/9 Hardening standards.
