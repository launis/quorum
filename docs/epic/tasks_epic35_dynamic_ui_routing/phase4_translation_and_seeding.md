# Epic 35 Phase 4: Translation Hook & The English-Only Mandate

## Context vs Target
*   **TARGET (Modify):** 
    *   `backend_v2/hooks/translation_hook.py` (New)
    *   `backend_v2/api/routers/synthesis.py` (Or wherever GET rendering triggers)
    *   `backend_v2/seed/seed_data.json`
*   **CONTEXT (Read-Only):**
    *   `c:\src\quorum\.agents\rules\00-antigravity-core.md`

## Tasks

1.  **[x] English-Only System Prompt Refactoring**
    *   Modify `seed_data.json`: Translate any Finnish `<system_directive>` prompts (e.g., Output Profiles) to 100% English.

2.  **[x] Immutable Translation Hook (`translation_hook.py`)**
    *   Implement an isolated hook that translates English SDUI string fields into the target UI language (e.g., Finnish).
    *   Must adhere to frozen Pydantic models:
        1. Parse to dict: `raw = obj.model_dump()`
        2. Recursively translate string values (utilizing AI or deterministic dictionary).
        3. Rehydrate: `SduiBlockBase.model_validate(raw)`
    *   *Direct property mutation is banned.*

3.  **[x] API Pipeline Splicing**
    *   Apply `translation_hook` ONLY inside the HTTP response pipeline (e.g. just before sending to Flutter).
    *   Never save translated SDUI back into the TinyDB `ExecutionRecord.profile_syntheses` ground truth.

4. **[x] Verification & Quality Gate Plan**
    *   **Seeding Test:** Run `uv run python backend_v2/seed/run_seed.py` and verify `seed_data.json` loads flawlessly.
    *   **Unit Tests:** Test the translation hook specifically against immutability violations (verify it doesn't crash on frozen constraints).
    *   **Audit Loop:** `uv run python scripts/backend_audit_loop.py backend_v2/hooks/translation_hook.py --test`
