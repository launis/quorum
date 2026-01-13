SYSTEM CONTEXT & ARCHITECTURE MANDATE (2026 Edition)

PROJECT: Google Antigravity (Monorepo: Python Backend + Flutter Client)
CURRENT DATE: 2026-01-13
STATUS: Phase 2 (Hardening Architecture & Standardization)

--------------------------------------------------------------------------------
⚠️ STRICT DEPENDENCY & PATTERN PROTOCOL
The dependencies listed below are ALREADY DEFINED in the project's configuration.
DO NOT ask to install them again unless they are missing.

YOUR CORE TASK:
Use the **LATEST FEATURES** and **MODERN BEST PRACTICES** associated with these specific versions.
Legacy patterns (e.g., `ChangeNotifier`, manual providers, `dict` responses, `setState` for logic) are STRICTLY FORBIDDEN.
--------------------------------------------------------------------------------

PART 1: FLUTTER CLIENT MANDATES

1.  **Framework & Core**:
    * **Flutter 3.38+** (Stable): Use latest Material 3 widgets, Adaptive Scaffold.
    * **Breaking Changes**: Strictly adhere to breaking changes documentation.

2.  **State Management (Riverpod ^3.0.0)**:
    * **Generator Only**: Use `@riverpod`. No manual `Provider` definitions.
    * **Declarative**: `ref.watch` everything. No manual `.listen()` inside Notifiers.
    * **AsyncValue**: Use `.when()`/`.value` for UI. No custom `isLoading` bools.

3.  **Routing (GoRouter ^17.0.1)**:
    * Type-safe `GoRouteData`.
    * `StatefulShellRoute` for persistent navigation.
    * Auth Guard must use `ref.watch` (Reactive Redirection).

4.  **UI & Localization**:
    * **FlexColorScheme**: Use distinct themes for Light/Dark modes.
    * **Visual Identity**: Deep Purple (#673AB7). Font: Inter.
    * **Localization (Intl)**: All strings in `.arb` files.
    * **Error Hygiene**: NEVER display raw backend strings. Map errors to `AppLocalizations`.

5.  **Client-Side Exception Handling (Dart)**:
    Do not just catch backend errors. You must handle client-side transport/logic errors proactively.
    * **Sealed Class Strategy (Best Practice)**:
        * Define `sealed class Failure` (e.g., `NetworkFailure`, `ServerFailure`).
        * **Benefit**: Forces the UI code to use exhaustive `switch` statements. If a new error type is added, the code won't compile until it's handled in the UI.
    * **Layer Strategy**: Catch exceptions in the **Repository** layer and convert them to a Domain `Failure` subclass.
    * **Mapping Rules**:
        * `SocketException` / `OSError` → Return `NetworkFailure()`
        * `TimeoutException` → Return `TimeoutFailure()`
        * `FormatException` → Return `ParseFailure()`
        * `RangeError` / `TypeError` → Return `LogicFailure()`

--------------------------------------------------------------------------------
PART 2: BACKEND ARCHITECTURE & API STANDARDS (AAS-2026)
--------------------------------------------------------------------------------
**Objective:** Maintain absolute structural and functional consistency across all FastAPI routers in `backend/routers/`.

6.  **DEFINITION ORDER (Avoid NameErrors)**:
    Python parses top-to-bottom. Follow this strict order in every Router file to prevent runtime crashes:
    1.  **Imports**:
        * Group 1: StdLib (`os`, `logging`) -> Sorted alphabetically.
        * Group 2: 3rd Party (`fastapi`, `pydantic`) -> Sorted alphabetically.
          * **REQUIRED**: `from fastapi import APIRouter, HTTPException, status` (Use `status` constants).
        * Group 3: Local. **CRITICAL**: `from backend.schemas.error import APIError` and `backend.exceptions` MUST be the first local imports.
    2.  **Logger & Router Instantiation**:
        * `logger = logging.getLogger(__name__)`
        * `router = APIRouter(...)`
    3.  **Pydantic Models**:
        * Define ALL request/response schemas HERE.
        * *Reasoning*: Models must be defined before they are referenced in Endpoints or Dependencies.
    4.  **Dependencies**:
        * Define local dependency overrides or `Annotated` aliases here.
    5.  **Helpers**:
        * Private helper functions (prefixed with `_`).
    6.  **Endpoints**:
        * The route handlers (CRUD or functional grouping).

7.  **Coding Standards (Python 3.12+)**:
    * **No Magic Numbers**: usage of raw integers for HTTP codes (e.g., `404`) is **FORBIDDEN**. You must use `status.HTTP_404_NOT_FOUND`.
    * **Strict Typing**: Use `typing.Annotated` for all FastAPI dependencies.
    * **Response Models**: Never return `dict`. Always use Pydantic models.
    * **Tooling**: Code must pass `ruff check`, `ruff format`, and `mypy`.

8.  **Universal Error Handling Strategy (The "Safety Net")**:
    Errors are not just HTTP responses; they are data structures. We use a unified approach for both synchronous API failures and asynchronous background task failures.

    * **A. The Universal Schema (`APIError`)**:
        * ALL structural errors must conform to `backend.schemas.error.APIError`.
        * **Usage in Endpoints**: Raised via `HTTPException(detail="CODE")`.
        * **Usage in Background Tasks**: Serialize exceptions into an `APIError` model and store in DB.

    * **B. The "Echo Protocol" (Log-First Mandate)**:
        The Error Code Term used in `logger` calls IS the binding contract for the entire stack.
        
        * **STRICT RULE**: You are FORBIDDEN from raising an exception without **immediately preceding it** with a log entry (`logger.error`, `logger.warning`).
        * **SYNC CHECK**: The string code used in the logger MUST match the exception code exactly.

        * ❌ **Bad (Silent Failure / Magic Numbers)**:
            ```python
            # Missing log, Magic Number 400
            raise HTTPException(400, detail="PAYMENT_ERROR") 
            ```
        * ✅ **Required Standard**:
            ```python
            # 1. Define the Truth
            error_code = "STRIPE_PAYMENT_DECLINED"
            
            # 2. LOG FIRST (Mandatory)
            logger.error(f"{error_code}: Card rejected. Details: {str(e)}", exc_info=True)
            
            # 3. RAISE SECOND (With CONSTANTS and SAME Code)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_code
            )
            ```

    * **C. Exception Mapping Protocol (Non-HTTP Errors)**:
        You must catch standard Python exceptions and map them to HTTP Status Codes + Domain Error Codes. Do not let 500 Internal Server Errors happen for predictable logic errors.

        *Example Flow:*
        ```python
        try:
            perform_logic()
        except ValueError as e:
            # LOG before Raising!
            logger.error(f"DOMAIN_INVALID_VALUE: Logic failed - {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="DOMAIN_INVALID_VALUE"
            )
        ```

        | Python Exception | Reason | Mapped Status Constant | Example Code |
        | :--- | :--- | :--- | :--- |
        | `ValueError` | Invalid Argument | `status.HTTP_400_BAD_REQUEST` | `DOMAIN_INVALID_VALUE` |
        | `KeyError` / `IndexError` | Missing Resource | `status.HTTP_404_NOT_FOUND` | `DOMAIN_RESOURCE_NOT_FOUND` |
        | `TypeError` | Contract Violation | `status.HTTP_422_UNPROCESSABLE_ENTITY` | `DOMAIN_DATA_CONTRACT_VIOLATION` |
        | `json.JSONDecodeError` | Bad Payload | `status.HTTP_400_BAD_REQUEST` | `REQUEST_MALFORMED_JSON` |
        | `TimeoutError` | Latency | `status.HTTP_504_GATEWAY_TIMEOUT` | `SYSTEM_OPERATION_TIMEOUT` |
        | `NotImplementedError` | WIP Feature | `status.HTTP_501_NOT_IMPLEMENTED` | `SYSTEM_FEATURE_NOT_IMPLEMENTED` |
        | `PermissionError` | Security | `status.HTTP_403_FORBIDDEN` | `AUTH_PERMISSION_DENIED` |

--------------------------------------------------------------------------------
PART 3: SHARED PROTOCOLS & INTEGRATION
--------------------------------------------------------------------------------

9.  **Global API Error Contract (The Bridge)**:
    * **The Chain of Truth**:
        1.  **Backend Log**: `logger.error("USER_SYNC_FAILED: ...")`
        2.  **API Response**: `{ "error_code": "USER_SYNC_FAILED", ... }` (via `APIError`).
        3.  **Flutter Client**: `if (failure.code == 'USER_SYNC_FAILED')`
        4.  **UI Text**: `l10n.userSyncFailed`
    * **Frontend Consumption**:
        * **BANNED**: Regex-matching the `message` string.
        * **REQUIRED**: Logic MUST switch on the `error_code` (The One Truth).

10. **Error Code Taxonomy (Naming Standard)**:
    * **Format**: `SCREAMING_SNAKE_CASE`
    * **Structure**: `DOMAIN_ACTION_REASON`
    * **Examples**: `AUTH_LOGIN_BAD_CREDENTIALS`, `BILLING_INVOICE_GENERATION_FAILED`.
    * **Forbidden**: Generic codes like `ERROR`, `FAILED`, or `ValueError`.

11. **Refactoring Checklist**:
    1.  [ ] **Reorder**: Verify Definition Order matches Section 6 exactly.
    2.  [ ] **Imports**: Ensure `from fastapi import status` is used.
    3.  [ ] **No Magic Numbers**: Search for raw integers (400, 404, 500) and replace with `status.HTTP_...`.
    4.  [ ] **Log-First Rule**: **CRITICAL**. Verify that NO exception is raised without a preceding `logger` call.
    5.  [ ] **Dart Sealed Classes**: Verify `Failure` class is sealed and UI uses `switch`.

# 🛑 STOP! READ THIS CAREFULLY 🛑
**THIS DOCUMENT IS A CONTEXT REFERENCE ONLY.**
**DO NOT START ANY IMPLEMENTATION OR GENERATE CODE BASED ON THIS FILE YET.**
**STORE THIS CONTEXT IN YOUR MEMORY AND AWAIT FURTHER INSTRUCTIONS.**