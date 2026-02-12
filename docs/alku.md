# PROMPT: AI-istunnon alustus
> Kopioi ja liitä tämä teksti uuden keskustelun ensimmäiseksi viestiksi. Se varmistaa, että tekoäly lukee oikeat ohjeet ja noudattaa projektin sääntöjä.

---

**SYSTEM INITIALIZATION (MANDATORY)**

You are working on the **Cognitive Quorum** project (Phase 2 Hardening).

**1. CRITICAL CONTEXT LOADER**
Before answering, you MUST read and internalize the following documentation files to understand the architecture, logic, and operational constraints:

*   **`docs/flutterpromptohje.md`** (The "System Architecture Manifesto" - **PRIMARY AUTHORITY**)
*   **`docs/structured_cognitive_architecture.md`** (Understanding the "Why": Logic, Agents, Hybrid Rubric)
*   **`docs/Execute ohje.md`** (The "How-To": Feature Implementation Steps & Output Format)
*   **`docs/api_models.md`** (The "Data": Pydantic Models & Schemas)

**2. CORE MANDATES (Non-Negotiable)**
*   **Tech Stack**: Python 3.14+ (FastAPI, Pydantic V2) & Flutter (Riverpod 3.0 Generator, GoRouter).
*   **SSOT Principle**: `backend/seed/seed_data.json` is the Single Source of Truth for logic. Never hardcode rules/steps in Python/Dart.
*   **State Management**: Use `@riverpod` annotations. Implement "Optimistic Update + Silent Invalidation".
*   **Error Handling**: Backend must raise typed `AppException` (RFC 7807). Fail fast; never swallow errors.
*   **Verification**: All changes must be verified against local Windows/PowerShell constraints.

**3. OUTPUT FORMAT (From `Execute ohje.md`)**
*   **Code**: Standard English.
*   **Explanations**: Finnish (Suomi).

**4. DEBUGGING RESOURCES (Local Development)**
*   **`backend_debug.log`** (Project Root): Contains full Backend logs (Uvicorn, FastAPI, Arq). Use this to debug startup crashes, 500 errors, and database queries.
*   **`client_debug.log`** (Project Root): Contains Flutter Client logs (Riverpod state changes, Navigation, HTTP errors). Use this to debug UI freezes or "Something went wrong" errors.
*   **Note**: `run_local.bat` clears these files on every fresh start to ensure clean traces.

**CONFIRMATION:**
State clearly that you have read the files and are ready to proceed under the Phase 2 Hardening standards.
