# Epic 37: Phase 2 - Synthesis Core Strictness

## 1. Goal Description
Enforce the "Zero-Compromise" Fail-Fast architecture in the synthesis engine hooks (`synthesis_hook` and helpers) within `backend_v2/hooks/synthesis.py`. The goal is to eradicate legacy dictionary parsing (`hook_metadata.get("target_locale")`, `isinstance(step_data, dict)`) by introducing strict Pydantic models like `SynthesisMetadataDTO`.

## 2. Scope
**TARGET (Modify):**
- `c:\src\quorum\backend_v2\hooks\synthesis.py`
- `c:\src\quorum\backend_v2\models\domain\synthesis.py` (or equivalent models file)

**CONTEXT (Read-Only):**
- `c:\src\quorum\docs\epic\epic37_hook_directory_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## 3. Sequence & Implementation Steps
1. **Pydantic Models:** 
   - Define `SynthesisMetadataDTO` (and related internal structures for synthesis blocks) in the models directory.
   - Enforce `model_config = ConfigDict(extra='forbid', frozen=True)`.
2. **API/Hook Implementation (`synthesis.py`):**
   - Refactor `synthesis_hook` and all helper extraction loops.
   - Rip out `isinstance(step_data, dict)` checks.
   - Replace dynamic `.get()` lookups with strict Pydantic model validation.
   - Ensure internal state tracking uses O(1) hashing/maps rather than heavy nested list iterations where applicable.
3. **Fail-Fast Enforcement:**
   - Remove manual `if not isinstance` defensive programming. If data is malformed, the hook must crash immediately via `AppException`.

## 4. Verification & Quality Gate Plan
- **Tools to execute:**
  - `uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py`
  - Ensure 100% Type safety and 0 Ruff warnings.
- **Unit Tests:**
  - Update `tests/backend_v2/hooks/test_synthesis.py` to test the new strict typing and the fail-fast behavior when `SynthesisMetadataDTO` validation fails.
