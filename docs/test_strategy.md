# Cognitive Quorum Testing Strategy (V5.1 - Phase 9 Hardening)

## Core Philosophy: "Zero-Magic" & The Testing Mandate
We prioritize **speed**, **readability**, and **absolute compliance** over complex tooling.
1.  **THE TESTING MANDATE**: Whenever code is changed, refactored, or new features are added, you MUST ALWAYS write new automated tests or fix existing ones for both the Flutter and Python sides. A feature is incomplete without a reliable test.
2.  **Fail Fast**: Tests must assert that the system crashes (raises `AppException` / validation error) cleanly on invalid input or configuration right at the boundary.
3.  **Strict Typing**: We verify Pydantic V2 schemas at every boundary.
4.  **Isolation**: Unit tests must never hit the database or external APIs (e.g., Gemini) unless explicitly tagged as integration/live.

---

## 1. Backend Testing (Python)
*   **Framework**: `pytest`
*   **Location**: `backend_v2/tests/`
*   **Command**: `uv run pytest`

### Structure
*   `backend_v2/tests/unit/`: Service-level logic, Hook executions, and Data Model validation.
*   `backend_v2/tests/integration/`: Component interaction (e.g., `seed_data.json` integrity tests and GraphEngine flows).
*   **Specialized Verification (Phase 9)**:
    *   **Hook Validations**: Ensure that hooks (like `input_processing`, `sanitize_text`) process inputs deterministically and raise exceptions (e.g., `INVALID_OUTPUT_SCHEMA`) if the payload lacks required dictionary structures (like `inputs`, `sanitization_result`).
    *   **DAG Resolution**: Verify `workflow_courtroom_20_full_audit` paths and nodes execute chronologically and pass dependencies without GraphEngine failures.
    *   **Fail Fast Protocol**: Verify `AppException` (RFC 7807) is raised properly over silent `try-except pass` logic.

### Implementation Pattern
We use **Dependency Injection** alongside `AsyncMock` to isolate logic.

```python
# backend_v2/tests/unit/test_security_hooks.py
from unittest.mock import AsyncMock
import pytest
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.security import sanitize_text_hook

@pytest.mark.asyncio
async def test_sanitize_text_fail_fast_missing_inputs():
    # Arrange: Invalid structure missing dict
    invalid_data = {"raw_inputs": "random_text"}
    
    # Act & Assert: Must strictly raise AppException (INVALID_OUTPUT_SCHEMA)
    with pytest.raises(AppException) as exc:
         sanitize_text_hook(invalid_data)
    
    assert exc.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA
```

### Script Testing
We actively use manual execution scripts to audit complete end-to-end setups deterministically:
*   `python backend_v2/scripts/test_audit_cli.py`: Evaluates the current seed configuration with live inputs and reports characters extracted from real files.

---

## 2. Frontend Testing (Flutter)
*   **Framework**: `flutter_test`
*   **Location**: `client_app_v2/test/`
*   **Command**: `flutter test`

### Implementation Pattern (No Code Gen)
We explicitly use **Mocktail** to avoid the slow `build_runner` cycle for simple state tests. However, we rely heavily on **Riverpod's ProviderContainer** for testing controller states effectively.

```dart
test('loads workflow and handles Optimistic Updates', () async {
  final repo = MockRepo();
  final container = ProviderContainer(
    overrides: [
       workflowsRepositoryProvider.overrideWithValue(repo),
    ]
  );
  when(() => repo.getWorkflow('1')).thenAnswer((_) async => WorkflowDef(id: '1'));
  // ...
  verify(() => repo.getWorkflow('1')).called(1);
});
```

---

## 3. Test Data Management

### Backend: Pydantic Factories
We do not use messy JSON fixtures. We instantiate Pydantic models directly in tests.
*   *Bad*: `json.load("mock_user.json")`
*   *Good*: `User(id="1", role="ADMIN")`

### Frontend: Hardcoded Constants
Define test data (e.g., mock UI UUIDs for Login bypassing during tests) at the top of the test file to keep it close to the execution.

---

## 4. CI/CD Enforcement
All PRs must pass:
1.  `uv run pytest` (Backend)
2.  `flutter test` (Frontend)
3.  `ruff check` (Linting)
4.  `mypy .` (Strict Typing)

