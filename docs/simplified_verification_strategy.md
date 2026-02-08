# Simplified Verification Strategy (V2.9)

**Philosophy**: "Zero-Magic". We avoid complex test runners and implicit states in favor of clear, readable, single-file verification scripts.

---

## 1. Backend Verification (Data Integrity)

We verify the backend primarily by ensuring the **Database** matches the **Seed Data** (SSOT).

### A. Sync Verification (`verify_sync.py`)
This script performs a deep comparison between `seed_data.json` and all active databases (Local, Mock, Firestore).

*   **Command**: `python backend/seed/verify_sync.py`
*   **Success Criteria**: Output must read **"ALL SYSTEMS SYNCED"**.
*   **What it checks**:
    *   Entity Counts (Users, Orgs, Workflows).
    *   Content Hashing (Checks if prompt content has drifted).
    *   Schema Validation (Ensures DB records match Pydantic models).

### B. Count Verification (`check_counts.py`)
A fast, high-level sanity check to compare record counts across environments.

*   **Command**: `python backend/seed/check_counts.py`
*   **Output**: A table showing counts for SEED, PROD, MOCK, and FIRE.
*   **Use Case**: Quick check after running a migration or seeding operation.

---

## 2. Logic Verification (Unit Tests)

### Backend (Python)
We use `pytest` with a "Service-First" approach. We instantiate Services directly with Mock Repositories, avoiding the need to spin up the full FastAPI app or Docker container.

*   **Pattern**: Dependency Injection with `MagicMock`.
*   **Location**: `backend/tests/`
*   **Command**: `uv run pytest`

```python
def test_rbac_rules():
    # 1. Setup Mock Repo
    auth_service = AuthService(db=MagicMock(), ...)
    
    # 2. Action
    user = auth_service.create_user(...)
    
    # 3. Assert
    assert user.role == "MEMBER"
```

### Frontend (Flutter)
We use `flutter_test` with **Mocktail**. We strictly avoid code generation (`build_runner`) for tests to keep CI fast.

*   **Pattern**: Repository Pattern Verification.
*   **Location**: `client_app/test/`
*   **Command**: `flutter test`

```dart
class MockAuthRepository extends Mock implements AuthRepository {}

test('User can login', () async {
  final repo = MockAuthRepository();
  when(() => repo.signIn(...)).thenAnswer((_) async => User(...));
  
  final controller = AuthController(repo);
  await controller.login();
  
  verify(() => repo.signIn(any())).called(1);
});
```

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
1.  **Backend**: Runs `ruff` and `pygame` (if applicable).
2.  **Frontend**: Runs `flutter analyze` and `flutter test`.
3.  **Docs**: Builds MkDocs site.
