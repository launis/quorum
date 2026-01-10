# Cognitive Quorum Testing Strategy

This document outlines the comprehensive testing strategy for the Cognitive Quorum platform, covering both the Python Backend and the Flutter Client App. It serves as the single source of truth for verification protocols.

## 1. Backend Testing (Python)

The backend test suite is located in `tests/` and focuses on API integrity, Multi-Agent logic, and Security verification.

### Test Runners (Backend)

We provide batch scripts in `tests/` to make running tests easy and reproducible.

#### 1. Full Regression Suite (SAFE)
*   **Script**: `tests\run_regression_tests.bat`
*   **Command**: `.\tests\run_regression_tests.bat`
*   **What it does**: Runs **ALL** tests in the library (>45 files).
*   **Mock Mode**: Uses **Mock LLM** (zero cost) and **Mock DB** (temporary file).
*   **Use Case**: Run before every commit to ensure system stability.

#### 2. Live LLM Integration Tests (COSTS MONEY)
*   **Script**: `tests\run_live_tests.bat`
*   **Command**: `.\tests\run_live_tests.bat`
*   **What it does**: Runs specific integration tests that hit real Vertex AI / Gemini APIs.
*   **Use Case**: Run sparingly to verify LLM connection and prompt schemas.

### Manual Execution
You can use `pytest` to target specific files:
```powershell
uv run pytest tests/test_api.py -v
```

### Key Test Categories
| File Prefix | Description |
| :--- | :--- |
| `test_api_*.py` | Tests for FastAPI endpoints and routes. |
| `test_fusion_*.py` | Tests for the core Multi-Agent System (Fusion) logic. |
| `test_iam_*.py` | Tests for Identity & Access Management (RBAC). |
| `test_guard_*.py` | Tests for the GuardRails and Safety mechanisms. |
| `test_live_*.py` | **Live** tests requiring real API credentials. |

---

## 2. Client App Testing (Flutter)

The Flutter client test suite ensures UI logic, state management, and end-to-end flows work as expected.

### Test Structure
*   **`client_app/test/`**: Contains Unit and Widget tests.
*   **`client_app/integration_test/`**: Contains full End-to-End tests.

### 2.1 Unit Tests
Focus on testing business logic, Repositories, and Riverpod Providers in isolation.
*   **Models**: Verify JSON deserialization (e.g., `execution_test.dart`).
*   **Repositories**: Mock API calls using `mockito` to verify data handling (e.g., `auth_repository_test.dart`).
*   **Providers**: Verify state changes in Notifiers (e.g., `usage_stats_provider_test.dart`).

**Command:**
```bash
cd client_app
flutter test
```

### 2.2 Widget Tests
Focus on testing individual UI components in isolation.
*   **Usage**: Verifies that widgets render correctly given specific state overrides.
*   **Example**: `analysis_wizard_screen_test.dart` checks that validation errors appear when submission is attempted with empty inputs.

### 2.3 Integration Tests (End-to-End)
Runs the app on a real device or emulator to verify critical user flows.
*   **Scope**: Login -> Dashboard -> Create Analysis -> Verify Result.
*   **File**: `client_app/integration_test/app_test.dart`.

**Command:**
```bash
cd client_app
flutter test integration_test/app_test.dart
```
*Note: This requires a running emulator or connected device.*

---

## 3. Test Data Management

Understanding where test data comes from is critical for reproducible testing.

### Backend Seeding
See [Seed Data Documentation](seed_data.md) for details on `seed_data.json` and how to reset the database.

*   **Mock DB**: Used by default in regression tests (`USE_MOCK_DB=true`).
*   **Prod DB**: Used in local development but never in automated tests.

---

## 4. Output Logs

All backend test runners redirect output to:
*   `tests/output/regression_results.txt`
*   `tests/output/live_test_results.txt`

Client app test results are displayed in the terminal.
