# Simplified Verification Strategy (V3.2 - Phase 8 Standards)

**Philosophy**: "Zero-Magic". We avoid complex test runners and implicit states in favor of clear, readable, single-file verification scripts.
**Principle**: "Fail Fast". Verification should halt immediately upon detecting invalid configuration or state.

---

## 1. Backend Verification (Data Integrity)

We verify the backend primarily by ensuring the **Database** matches the **Seed Data** (SSOT) and that strict schemas are enforced.

### A. Sync Verification (`verify_sync.py`)
This script performs a deep comparison between `seed_data.json` and all active databases (Local, Mock, Firestore).

*   **Command**: `python backend/seed/verify_sync.py` (Requires Python 3.14.2+)
*   **Success Criteria**: Output must read **"ALL SYSTEMS SYNCED"**.
*   **What it checks**:
    *   **Entity Counts**: Users, Orgs, Workflows, *Components*.
    *   **Content Hashing**: Checks if prompt content has drifted.
    *   **Schema Validation**: Ensures DB records match **Strict Pydantic V2** models.
    *   **System Config**: Verifies `model_registry` and Agent Strategies (e.g., `PanelAgent` -> `deep`).

### B. Count Verification (`check_counts.py`)
A fast, high-level sanity check to compare record counts across environments.

*   **Command**: `python backend/seed/check_counts.py`
*   **Output**: A table showing counts for SEED, PROD, MOCK, and FIRE.
*   **Use Case**: Quick check after running a migration or seeding operation.

### C. Hybrid State Audit (Event Consistency)
We verify the **Hybrid State Architecture** by ensuring the Event Log (`trace`) matches the Snapshot (`context`).

*   **Mechanism**: `backend/seed/verifier.py`
*   **Logic**:
    1.  Replay all `TraceEvent`s from `execution_trace`.
    2.  Compare the derived state against the stored `context_variables`.
    3.  If they diverge, the state is corrupted.

---

## 2. Logic Verification (Unit Tests)

### Backend (Python)
We use `pytest` with a "Service-First" approach. We instantiate Services directly with Mock Repositories, avoiding the need to spin up the full FastAPI app.

*   **Pattern**: Dependency Injection with `MagicMock`.
*   **Fail-Fast Validation**: Tests must assert that `AppException` (RFC 7807) is raised for invalid inputs.
*   **DTO Verification**: Tests must verify that Agents return strict DTOs (e.g., `PanelOutputDTO`) which are then promoted to Domain Models (e.g., `PanelOutput`) by the Engine.
*   **Output Generation (SDUI/PDF) Verification**: Tests must verify that the `ReportCoreTransformer` strictly rejects legacy/corrupted data that fails schema validation (avoiding fallback data presentation).
*   **Location**: `backend/tests/`
*   **Command**: `uv run pytest`

```python
def test_security_hook_fail_fast():
    # 1. Setup Mock Repo returning empty rules
    repo = MagicMock()
    repo.get_banned_phrases.return_value = []
    
    # 2. Action & Assert
    with pytest.raises(AppException) as exc:
        # Zero-Fallback: Must crash if DB is empty
        run_security_hook(..., repository=repo)
    
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.SECURITY_DB_ERROR

def test_sdui_output_validation_rejects_legacy_data():
    # 1. Provide an ExecutionRecord missing strict DTO fields (e.g., PerformativityOutput)
    broken_execution = build_legacy_execution_missing_fields()
    
    # 2. Action & Assert
    with pytest.raises(AppException) as exc:
        # Zero-Fallback: SDUI transformation must crash instead of rendering "Ei perusteluja"
        ReportCoreTransformer().transform(broken_execution)
        
    assert exc.value.status_code == 500
    assert "validation errors" in str(exc.value.details.get("original_error", ""))
```

### Frontend (Flutter)
We use `flutter_test` with **Mocktail**. We strictly avoid code generation (`build_runner`) for tests to keep CI fast.

*   **Pattern**: Repository Pattern Verification.
*   **Location**: `client_app/test/`
*   **Command**: `flutter test`

---

## 3. Pre-Flight Checklist (The "Go/No-Go")

Before pushing any code, run this manual checklist:

1.  **Seed Integrity**: `python backend/seed/verify_sync.py` -> PASS.
2.  **Linting**: `uv run ruff check .` -> PASS.
3.  **Frontend Build**: `cd client_app && flutter analyze` -> PASS.
4.  **Clean Start**: `run_full_docker.bat` -> System starts without "Address in use" errors.

---

## 4. CI/CD Enforcement

GitHub Actions (`.github/workflows/main.yml`) enforces these standards on every push:
1.  **Backend**: Runs `ruff` and `mypy` (Strict Typing).
2.  **Frontend**: Runs `flutter analyze` and `flutter test`.
3.  **Docs**: Builds MkDocs site.
