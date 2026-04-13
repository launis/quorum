# TIER 2 EXECUTION PLAN: Phase 1 - Scoring Calibration & The Lenient Shift

## Objective
Implement phase 1 of Epic 23. Focus on adding mathematical "Benefit of the Doubt" relaxation to the Prompt Compiler and fixing the excessive multiplication punishment (Double Jeopardy) in `scoring.py` using O(1) determinism via strict `max()` floors and `min()` caps.

## Target & Context Files
- **TARGET (Modify):** `backend_v2/models/enums.py` - Add `ScoringCalibrationThresholds` enum.
- **TARGET (Modify):** `backend_v2/hooks/scoring.py` - Update DINA cascade mathematics.
- **TARGET (Modify):** `backend_v2/services/orchestrator/prompt_compiler.py` - Add "Constructive Leniency" to System Injunction. (Surgical exception granted by Epic 23).
- **CONTEXT (Read-Only):** `backend_v2/models/dto.py` (or similar schema paths), `.agents/rules/01-python-backend.md`, `.agents/rules/05_llm_architecture.md`

## Architectural Sequence
1. **Dependencies:** Ensure Python 3.10+ native math built-ins are utilized (`min`, `max`), no heavy libraries.
2. **Pydantic/Enums:** Add `ScoringCalibrationThresholds` to `enums.py` (`DINA_FLOOR = 0.30`, `PENALTY_CAP = 0.25`).
3. **API/Hooks (Logic):** Apply O(1) threshold constraints in `scoring.py` without looping conditionals.
4. **Prompt Compiler:** Inject explicit "Benefit of the Doubt" instructions into the `_SYSTEM_INSTRUCTION` safely without creating dynamic caching invalidations. 

## Strict Constraints
- **Zero-Service-Layer-Fallbacks:** We do not compensate for legacy dictionaries.
- **Frozen State Mutability:** Arq state objects must not be mutated in place inside `scoring.py`.
- **Zero-Math UI (From rules):** The backend does the O(1) floor/cap mapping; UI is just for rendering.

## Verification & Quality Gate Plan
- Build new Unit Tests in `tests/backend_v2/hooks/test_scoring.py` to assert that:
    - Combined penalties do not exceed `PENALTY_CAP`.
    - DINA calculations never fall below `DINA_FLOOR`.
- Run Pytest script: `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py` 
- Ensure Ruff/Mypy validation passes with NO arbitrary `# type: ignore`.
