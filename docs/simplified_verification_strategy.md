# Simplified Verification Strategy (Zero-Dependency)

**Date**: 2026-01-13
**Context**: Moving away from complex, generated test suites towards clear, readable, single-file verification scripts.

## Core Philosophy
1.  **Zero-Magic**: Avoid `build_runner`, complex DI containers, or implicit state in verification scripts.
2.  **Single-File Authority**: A test should "tell the whole story" in one file.
3.  **Strictly Mocked**: External systems (Firebase, Databases) must be explicitly mocked to test logic in isolation.

## Backend Verification (`tests/test_rbac_simple.py`)
Used for verifying RBAC rules and Business Logic without spinning up the full FastAPI app.
-   **Pattern**: Direct Service Instantiation with `MagicMock`.
-   **Key Benefit**: Runs in <1s, no DB setup required.
-   **Structure**:
    ```python
    def test_rbac_simple():
        # 1. Setup Mock Repo
        service = AuthService(db=MagicMock())
        # 2. Define Scenarios (Root, Admin, Member)
        # 3. Assert Permissions
    ```

## Client Verification (`simple_repo_test.dart`)
Used for verifying Riverpod Repositories and Logic.
-   **Standard**: **Mocktail** (Strictly Preferred over Mockito/Manual Fakes).
-   **Key Benefit**: No code generation (`flutter pub run build_runner`) needed. Type-safe.
-   **Structure**:
    ```dart
    class MockDio extends Mock implements Dio {}
    
    test('scenario', () {
      final mock = MockDio();
      when(() => mock.get(...)).thenAnswer(...);
      // Act & Assert
    });
    ```

## Mandate
Adhere to this simplified structure for all future feature verification to reduce CI overhead and cognitive load.
