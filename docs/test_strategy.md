# Cognitive Quorum Testing Strategy (V2.9)

## Core Philosophy: "Zero-Magic"
We prioritize **speed** and **readability** over complex tooling.
1.  **Backend**: Use standard `unittest.mock` over complex pytest plugins.
2.  **Frontend**: Use `mocktail` over `mockito` to avoid code generation (`build_runner`).
3.  **Isolation**: Unit tests must never hit the database or external APIs.

---

## 1. Backend Testing (Python)
*   **Framework**: `pytest`
*   **Location**: `backend/tests/`
*   **Command**: `uv run pytest`

### Structure
*   `backend/tests/unit/`: Service-level logic verification.
*   `backend/tests/integration/`: Component interaction verifications (e.g. `test_config_integrity.py`).
*   `backend/tests/api/`: FastAPI route verification (Response codes, Schemas).

### Implementation Pattern
We use **Dependency Injection** with `AsyncMock`.

```python
# backend/tests/unit/test_pdf_generator.py
from unittest.mock import AsyncMock, MagicMock
import pytest

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.mark.asyncio
async def test_generate_pdf(mock_repo):
    # Arrange
    service = PdfService(mock_repo)
    mock_repo.get_execution.return_value = MagicMock()
    
    # Act
    await service.generate(123)
    
    # Assert
    assert mock_repo.get_execution.called
```

### Run Scripts
*   **Regression (Fast)**: `.\tests\run_regression_tests.bat` (Mocks everything).
*   **Live (Costly)**: `.\tests\run_live_tests.bat` (Hits real Gemini API).

---

## 2. Frontend Testing (Flutter)
*   **Framework**: `flutter_test`
*   **Location**: `client_app/test/`
*   **Command**: `flutter test`

### Structure
*   `client_app/test/features/`: Feature-sliced tests (Unit & Widget).
    *   e.g. `features/studio/presentation/providers/studio_controller_test.dart`
*   `client_app/integration_test/`: End-to-End flows.

### Implementation Pattern (No Code Gen)
We explicitly use **Mocktail** to avoid the slow `build_runner` cycle.

```dart
// client_app/test/features/studio/providers/studio_controller_test.dart
import 'package:mocktail/mocktail.dart';

class MockRepo extends Mock implements StudioRepository {}

test('loads workflow', () async {
  // Arrange
  final repo = MockRepo();
  when(() => repo.getWorkflow('1')).thenAnswer((_) async => WorkflowDef(id: '1'));
  
  // Act
  final container = ProviderContainer(overrides: [
    studioRepositoryProvider.overrideWithValue(repo)
  ]);
  await container.read(controller.notifier).loadWorkflow('1');
  
  // Assert
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
