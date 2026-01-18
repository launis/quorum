SYSTEM CONTEXT & ARCHITECTURE MANDATE (2026 Edition)

PROJECT: Google Antigravity (Monorepo: Python Backend + Flutter Client)
CURRENT DATE: 2026-01-16
STATUS: Phase 2 (Hardening Architecture & Standardization)

--------------------------------------------------------------------------------
⚠️ STRICT DEPENDENCY & PATTERN PROTOCOL
The dependencies listed below are ALREADY DEFINED in the project's configuration.
DO NOT ask to install them again unless they are missing.

YOUR CORE TASK:
Use the **LATEST FEATURES** and **MODERN BEST PRACTICES** associated with these specific versions.
Legacy patterns (e.g., `ChangeNotifier`, manual providers, `dict` responses, `setState` for logic) are STRICTLY FORBIDDEN.

⚠️ **CRITICAL: NO UNILATERAL CHANGES MANDATE** ⚠️
- **NEVER** modify existing architectural patterns, data structures, or resolution logic without explicit user approval.
- **NEVER** simplify or "improve" code that follows established conventions (e.g., chained model resolution, hook systems).
- **NEVER** remove or modify existing repository methods (e.g., `get_organization`, `list_users`) - these are critical API contracts.
- **NEVER** make large-scale refactoring (50+ lines changed) without explicit user approval.
- **ALWAYS** ask before changing seed_data.json structure, model resolution logic, or agent configurations.
- **ALWAYS** ask before modifying `repository.py`, `firestore_repo.py`, or any database abstraction layer.
- If you encounter code that seems redundant or overly complex, **ASK FIRST** - it may be intentional design.

> 🚨 **Repository Method Protection**: On 2026-01-16, 150+ lines of organization management methods were accidentally deleted during a refactor commit. This broke the entire application. NEVER delete repository methods without explicit approval.
--------------------------------------------------------------------------------

PART 1: FUTURE-PROOFING & DYNAMIC ARCHITECTURE (2026 STANDARDS)
*Applies to all new "Greenfield" modules and Refactoring efforts.*

1.  **Philosophy: "Schema is King" (Contract-First Design)**:
    * **Single Source of Truth**: Pydantic V2 models drive everything.
    * **Code Generation**: Backend Pydantic models MUST auto-generate:
        * OpenAPI/Swagger specs.
        * Frontend entities (via `openapi-generator` or equivalent).
        * No manual duplication of data classes between Python and Dart.

2.  **Backend: The Generic Engine**:
    * **BANNED**: Hardcoded step logic (e.g., `if step == 'guard'`).
    * **REQUIRED**: Metadata-Driven execution.
        * **Workflow Definition**: Stored as JSON in DB.
        * **Task Registry**: A decorator-based registry mapping string keys to Pydantic Schemas & Handlers.
        * **Generic Executor**: A single loop that looks up the handler by string key and executes it.
    * **Zero-Fallback Rule**: 
        * **BANNED**: Hardcoded default values or fallbacks in code (e.g., `prompts = [...]` if DB is empty).
        * **REQUIRED**: System must fail fast if configuration is missing in the database. All logic, prompts, and configurations MUST be fetched dynamically from the database.
        * **SPECIFIC BANS** (Examples of violations):
            1. **Model Name Duplication**: NEVER duplicate model names (e.g., `"gemini-2.5-flash"`) in multiple places. Only `deep` and `fast` configs contain actual model names. Other configs reference these aliases.
            2. **Removing Indirection**: NEVER "simplify" chained resolution (e.g., `guard` → `fast` → actual model). This indirection is intentional Single Source of Truth.
            3. **Hardcoding in Code**: NEVER put `model="gemini-2.0-flash"` directly in Python code. Always resolve from DB via `registry.resolve_model_config()`.
            4. **Removing Recursive Lookups**: NEVER remove recursive/chained lookups from `resolve_model_config()` or similar resolution functions.
            5. **Flattening Seed Data**: NEVER "flatten" hierarchical seed_data.json structures that use references.

3.  **AI Layer: Reliability & Structure**:
    * **Tooling**: Use **LiteLLM Native Structured Output** (`response_format`). The `instructor` library is available but the primary architecture leverages LiteLLM directly for a more streamlined adherence to Strict Mode.
    * **Pattern**: `Structured Output` only. No regex parsing of raw text.
    * **Modern or Bust (Strict Mode)**: 
        * All Agents MUST return specific Pydantic Models. 
        * `dict` returns are FORBIDDEN in final output. 
        * **NO FALLBACKS**: If `LLMProvider` fails to hydrate an object, the Agent MUST crash (`AGENT_STRICT_MODE_VIOLATION`) rather than attempting to parse a dictionary.
        * `LLMProvider` ensures auto-hydration of legacy dicts, so trust the objects.
    * **Self-Correction**: Pipeline must catch Pydantic validation errors and feed them back to the LLM for auto-correction.

4.  **Frontend: Hybrid Server-Driven UI (SDUI)**:
    * **Philosophy**: "Schema defines Data, Frontend defines Experience".
    * **Hybrid Implementation**: 
        * **Default**: Use generic `DynamicFormWidget` based on `UI_Schema`.
        * **Premium Override**: Frontend MAY implement custom, high-fidelity Widgets (e.g., Drag & Drop, Visual Selectors) for specific steps, provided they output the exact data structure required by the Schema.
    * **Constraint**: Hardcoding *forms* is banned, but hardcoding *components* that map to schema fields is allowed for UX.

5.  **Self-Documentation**:
    * **Code as Docs**: All Pydantic fields must have `description="..."` (populates Swagger).
    * **Visuals**: CI/CD must generate Mermaid.js diagrams from class relationships.

--------------------------------------------------------------------------------

PART 2: PYTHON BACKEND MANDATES

1.  **Framework (FastAPI 0.115+)**:
    * **Lifespan**: Use `async contextmanager` for startup/shutdown. No `@app.on_event`.
    * **Annotated**: Use `Annotated[Dep, Depends()]` for everything.
    * **Pydantic V2**: Use `model_validate`, `model_dump`. No `.dict()`, no `.parse_obj()`.

2.  **Async & Concurrency**:
    * **Async/Await**: ALL I/O bound routes must be `async def`.
    * **Blocking Code**: Run CPU-heavy tasks in `run_in_threadpool` or background workers.

3.  **Database (TinyDB / Firestore)**:
    * **Abstraction**: Use `AbstractRepository` pattern. No direct DB calls in routers.
    * **Dependency Injection**: Inject repositories via `Depends()`.

4.  **Testing (Pytest + AsyncIO)**:
    * **Fixtures**: Use `conftest.py` for shared resources.
    * **Async Tests**: `@pytest.mark.asyncio` for all async code.

5.  **Logging (Unified Format)**:
    * **Format**: `%(asctime)s | %(levelname)s | [%(execution_id)s] | %(name)s | %(message)s`
    * **Example**: `2026-01-16 19:10:00 | INFO | [SYSTEM] | backend.main | Server started`
    * **Uvicorn**: Uses `--log-config backend/uvicorn_logging.yaml` for unified format
    * **Context**: `execution_id` from `ContextFilter` (shows execution UUID or `SYSTEM`)
    * **Levels**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
    * **Config**: `backend/logging_config.py` controls all logging

--------------------------------------------------------------------------------

PART 3: ERROR HANDLING CONTRACT (RFC 7807 Problem Details)

**Standard**: https://tools.ietf.org/html/rfc7807

### 3.1 Quick Reference (Backend)

```python
error_code = "DOMAIN_REASON_DETAIL"
logger.error(f"{error_code}: {e}", exc_info=True)
raise AppException(
    message=str(e),
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    details={"error_code": error_code}
) from e
```

### 3.2 Mandatory Pattern (Backend)

```python
from backend.exceptions import AppException
from fastapi import status
import logging

logger = logging.getLogger(__name__)

@router.get("/{execution_id}")
async def get_execution(execution_id: str, ...):
    try:
        execution = await repository.get_execution(execution_id)
        if not execution:
            raise ResourceNotFoundError(f"Execution '{execution_id}' not found.")
        return execution

    except ResourceNotFoundError as e:
        error_code = "EXECUTION_NOT_FOUND"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": error_code}
        ) from e

    except Exception as e:
        error_code = "EXECUTION_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e

### 3.2.1 Real-World Example (ChatLogParser) - 2026 Standardization

Use the `ErrorCodes` Enum for type safety and a variable for the message string:

**Definition (`backend/exceptions.py`):**
```python
from enum import Enum

class ErrorCodes(str, Enum):
    EMPTY_INPUT = "EMPTY_INPUT"
    EXECUTION_NOT_FOUND = "EXECUTION_NOT_FOUND"
    # ...
```

**Usage:**
```python
from backend.exceptions import AppException, ErrorCodes

# ...

error_code = ErrorCodes.EMPTY_INPUT
message_code = "ChatLogParser received empty input."

logger.error(f"{error_code}: {message_code}")
raise AppException(
    message=message_code,
    status_code=status.HTTP_400_BAD_REQUEST,
    details={"error_code": error_code}
)
```
```

### 3.3 Error Code Naming Convention

Format: `DOMAIN_REASON_DETAIL`

| Code | Status | Description |
|------|--------|-------------|
| `EXECUTION_NOT_FOUND` | 404 | Requested execution doesn't exist |
| `WORKFLOW_NOT_FOUND` | 404 | Requested workflow doesn't exist |
| `WORKFLOW_EXECUTION_FAILED` | 500 | Workflow step failed during execution |
| `INVALID_JSON_PAYLOAD` | 400 | Request body has invalid JSON |
| `MISSING_WORKFLOW_ID` | 400 | Required workflowId not provided |
| `AUTH_TOKEN_EXPIRED` | 401 | JWT token has expired |
| `PERMISSION_DENIED` | 403 | User lacks permission |
| `UNSUPPORTED_CONTENT_TYPE` | 400 | Request has unsupported Content-Type |

### 3.4 Field Purposes

| Field | Purpose | Consumer | Show to User? |
|-------|---------|----------|---------------|
| `error_code` | Machine-readable key | Flutter `AppLocalizations` | ❌ (for lookup) |
| `message` | Debug info | Logs, DevTools | ❌ NEVER |
| `status_code` | HTTP standard | HTTP layer | ❌ |
| `detail` (RFC 7807) | Debug context | Logs | ❌ NEVER |
| `title` (RFC 7807) | Error type name | Reference | ❌ |

### 3.5 RFC 7807 Response Format

API returns RFC 7807 Problem Details with `Content-Type: application/problem+json`:

```json
{
  "type": "https://api.quorum.fi/errors/execution-not-found",
  "title": "Execution Not Found",
  "status": 404,
  "detail": "Execution 'abc-123' not found.",
  "instance": "/executions/abc-123",
  "extensions": {
    "step_id": "step_analyst"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | ✅ | URI identifying error type (can link to docs) |
| `title` | ❌ | Human-readable title (from error_code) |
| `status` | ❌ | HTTP status code (mirrors header) |
| `detail` | ❌ | Specific error message for this instance |
| `instance` | ❌ | URI identifying this specific occurrence |
| `extensions` | ❌ | Additional context (step_id, cause, etc.) |

### 3.6 Exception Handler (main.py)

```python
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )
```

### 3.7 Banned Patterns

```python
# ❌ BANNED: Loses error_code, breaks frontend localization
raise HTTPException(status_code=404, detail=str(e))

# ❌ BANNED: No structured error code
raise HTTPException(status_code=500, detail="Something went wrong")

# ❌ BANNED: Exposing internal details to user
return {"error": str(e)}  # Could leak stack traces
```

### 3.8 Error Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. EXCEPTION RAISED                                                  │
│    raise AppException(message, status_code, details={error_code})   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. EXCEPTION HANDLER (main.py)                                       │
│    exc.to_problem_detail(instance=request.url.path)                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼ JSON Response
┌─────────────────────────────────────────────────────────────────────┐
│ 3. HTTP RESPONSE                                                     │
│ Content-Type: application/problem+json                               │
│ {"type": "...", "title": "...", "status": 404, "detail": "..."}     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼ Dio catches
┌─────────────────────────────────────────────────────────────────────┐
│ 4. FLUTTER CLIENT                                                    │
│    ProblemDetail.fromJson() -> AppError(code: problem.errorCode)    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼ switch(code)
┌─────────────────────────────────────────────────────────────────────┐
│ 5. LOCALIZED UI                                                      │
│    l10n.executionNotFound -> "Suoritusta ei löytynyt"               │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.9 Flutter Client Integration

**ProblemDetail Model** (`lib/core/error/problem_detail.dart`):
```dart
@JsonSerializable()
class ProblemDetail {
  final String type;
  final String title;
  final int status;
  final String detail;
  final String? instance;
  final Map<String, dynamic>? extensions;

  /// Extract error code from type URI
  /// "https://api.quorum.fi/errors/execution-not-found" -> "EXECUTION_NOT_FOUND"
  String get errorCode => type.split('/').last.replaceAll('-', '_').toUpperCase();
}
```

**Error Interceptor** (`lib/api/error_interceptor.dart`):
```dart
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.data is Map<String, dynamic>) {
      final data = err.response!.data as Map<String, dynamic>;
      if (data.containsKey('type') && data.containsKey('status')) {
        final problem = ProblemDetail.fromJson(data);
        final appError = AppError.fromProblemDetail(problem);
        handler.reject(DioException(..., error: appError));
        return;
      }
    }
    handler.next(err);
  }
}
```

**Error Localization** (`lib/core/error/app_error_ext.dart`):
```dart
static String _localizeErrorCode(String errorCode, AppLocalizations l10n) {
  return switch (errorCode) {
    'EXECUTION_NOT_FOUND' => l10n.errorNotFound,
    'WORKFLOW_NOT_FOUND' => l10n.errorNotFound,
    'WORKFLOW_EXECUTION_FAILED' => l10n.errorServer,
    'AUTH_TOKEN_EXPIRED' => l10n.errorUnauthorized,
    'PERMISSION_DENIED' => l10n.errorUnauthorized,
    _ => l10n.errorUnknown,
  };
}
```

### 3.10 ⚠️ Adding New Error Codes

When adding a new error code in backend:

1. **Backend**: Add to `AppException` raise with `details={"error_code": "NEW_CODE"}`
2. **Flutter**: Add to `_localizeErrorCode()` in `lib/core/error/app_error_ext.dart`
3. **ARB Files**: Add localized strings to:
   - `lib/l10n/app_en.arb`
   - `lib/l10n/app_fi.arb`
4. **Run**: `flutter gen-l10n` to regenerate `AppLocalizations`

Example:
```dart
// 1. app_error_ext.dart
'NEW_ERROR_CODE' => l10n.newErrorMessage,

// 2. app_en.arb
"newErrorMessage": "Something specific went wrong",

// 3. app_fi.arb  
"newErrorMessage": "Jotain meni pieleen",
```

### 3.11 Implementation Status ✅

RFC 7807 is fully implemented:

- [x] `backend/exceptions.py` - `AppException.to_problem_detail()` method
- [x] `backend/main.py` - Exception handlers use RFC 7807 format
- [x] `backend/schemas/error.py` - `ProblemDetail` Pydantic model
- [x] `client_app/lib/core/error/problem_detail.dart` - Flutter ProblemDetail
- [x] `client_app/lib/api/error_interceptor.dart` - Dio interceptor for RFC 7807
- [x] `client_app/lib/core/error/app_error.dart` - `AppError.fromProblemDetail()`
- [x] `client_app/lib/core/error/app_error_ext.dart` - Error code localization
- [x] `client_app/lib/api/api_client.dart` - ErrorInterceptor added

--------------------------------------------------------------------------------

PART 4: FLUTTER CLIENT MANDATES

1.  **Framework & Core**:
    * **Flutter 3.38+** (Stable): Use latest Material 3 widgets, Adaptive Scaffold.
    * **Breaking Changes**: Strictly adhere to breaking changes documentation.

2.  **State Management (Riverpod ^3.0.0)**:
    * **Generator Only**: Use `@riverpod`. No manual `Provider` definitions.
    * **Declarative**: `ref.watch` everything. No manual `.listen()` inside Notifiers.
    * **AsyncValue**: Use `.when()`/`.value` for UI. No custom `isLoading` bools.

3.  **Routing (GoRouter ^17.0.1)**:
    * Type-safe `GoRouteData`. No raw string paths (`/home`).
    * **ShellRoute**: For persistent navigation bars.
    * **Guards**: Redirect logic inside `redirect` callback, not `build()`.

4.  **Network (Dio ^5.7.0)**:
    * **Interceptors**: Centralized auth token injection + RFC 7807 error parsing.
    * **Transformers**: Background JSON parsing (`compute`).
    * **Exceptions**: `ErrorInterceptor` catches `DioException` and maps to `AppError`.

5.  **Data Modeling (Freezed ^2.5.0 + JsonSerializable)**:
    * **Unions**: Use Freezed unions for States (`Initial`, `Loading`, `Success`, `Error`).
    * **Immutability**: All domain models must be `@freezed`.
    * **Methods**: No logic in data classes. Pure data holders.

6.  **UI/UX (FlexColorScheme ^8.0.0 + Google Fonts)**:
    * **Theming**: Use `FlexColorScheme.light` / `.dark`. No manual `ThemeData` construction.
    * **Typography**: `GoogleFonts.inter()` as default.

7.  **Localization (Flutter Localizations)**:
    * **ARB Files**: `app_en.arb` is the Source of Truth.
    * **Code Gen**: Use `AppLocalizations.of(context)`. No hardcoded strings.
    * **Error Codes**: All backend error codes MUST have localized strings in ARB files.
    
# 🛑 STOP! READ THIS CAREFULLY 🛑
**THIS DOCUMENT IS A CONTEXT REFERENCE ONLY.**
**DO NOT START ANY IMPLEMENTATION OR GENERATE CODE BASED ON THIS FILE YET.**
**STORE THIS CONTEXT IN YOUR MEMORY AND AWAIT FURTHER INSTRUCTIONS.**