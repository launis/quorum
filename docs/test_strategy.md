# Cognitive Quorum Testing Strategy (V3.2 - Phase 8 Standards)

## Core Philosophy: "Zero-Magic"
We prioritize **speed** and **readability** over complex tooling.
1.  **Fail Fast**: Tests must assert that the system crashes (raises `AppException`) on invalid input or configuration.
2.  **Strict Typing**: We verify Pydantic V2 schemas at every boundary (DTO -> Domain Model).
3.  **Isolation**: Unit tests must never hit the database or external APIs.

---

## 1. Backend Testing (Python)
*   **Framework**: `pytest`
*   **Location**: `backend/tests/`
*   **Command**: `uv run pytest`

### Structure
*   `backend/tests/unit/`: Service-level logic verification.
*   `backend/tests/integration/`: Component interaction (e.g., `seed_data.json` integrity).
*   **Specialized Verification (Phase 8)**:
    *   **DTO Promotion**: Verify that `BaseAgent` correctly promotes `*OutputDTO` (LLM Content) to `*Output` (Domain Model with Metadata).
    *   **System Config**: Verify that Agents respect `model_strategy` (e.g., `deep` vs `fast`) from DB configuration.
    *   **Fail Fast**: Verify `AppException` (RFC 7807) is raised for missing config or invalid schemas.

### Implementation Pattern
We use **Dependency Injection** with `AsyncMock`.

```python
# backend/tests/unit/test_panel_agent.py
from unittest.mock import AsyncMock, MagicMock
import pytest
from backend.exceptions import AppException, ErrorCodes

@pytest.mark.asyncio
async def test_panel_agent_fail_fast_no_config(mock_repo):
    # Arrange: Mock DB returning NO system_config
    mock_repo.get_system_config.return_value = None
    agent = PanelAgent(repository=mock_repo)
    
    # Act & Assert: Must raise SECURITY_CONFIG_ERROR or internal equivalent
    with pytest.raises(AppException) as exc:
         await agent.run(...)
    
    assert exc.value.details["error_code"] == ErrorCodes.SECURITY_CONFIG_ERROR
```

### Run Scripts
*   **Regression (Fast)**: `.\tests\run_regression_tests.bat` (Mocks everything).
*   **Live (Costly)**: `.\tests\run_live_tests.bat` (Hits real Gemini API).

---

## 2. Frontend Testing (Flutter)
*   **Framework**: `flutter_test`
*   **Location**: `client_app/test/`
*   **Command**: `flutter test`

### Implementation Pattern (No Code Gen)
We explicitly use **Mocktail** to avoid the slow `build_runner` cycle.

```dart
test('loads workflow', () async {
  final repo = MockRepo();
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
Define test data (e.g. `testWorkflow`) at the top of the test file. Keep it close to the usage.

---

## 4. CI/CD Enforcement
All PRs must pass:
1.  `uv run pytest` (Backend)
2.  `flutter test` (Frontend)
3.  `ruff check` (Linting)
4.  `mypy .` (Strict Typing)
