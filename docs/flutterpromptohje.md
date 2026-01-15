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

3.  **AI Layer: Reliability & Structure**:
    * **Tooling**: Use `instructor` library (Python) for all LLM interactions.
    * **Pattern**: `Structured Output` only. No regex parsing of raw text.
    * **Self-Correction**: Pipeline must catch Pydantic validation errors and feed them back to the LLM for auto-correction.

4.  **Frontend: Server-Driven UI (SDUI)**:
    * **Dynamic Forms**: Client never hardcodes form fields for steps.
    * **Protocol**: Backend sends a `UI_Schema` (JSON) defining inputs.
    * **Implementation**: Flutter implements a generic `DynamicFormWidget` that maps schema types (`text`, `file`, `select`) to Riverpod-controlled Widgets.

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

--------------------------------------------------------------------------------

PART 3: ERROR HANDLING CONTRACT (The "One Truth")

1.  **Backend -> Frontend Protocol**:
    * **Status Code**: Use HTTP standards (400, 401, 403, 404, 429, 500).
    * **Body Format**:
        ```json
        {
          "error_code": "DOMAIN_REASON_DETAIL", // e.g. "AUTH_TOKEN_EXPIRED"
          "message": "Human readable debug message",
          "details": { ... } // Optional context
        }
        ```

2.  **Handling Flow**:
    * **Backend Raise** (MANDATORY PATTERN):
        ```python
        from backend.exceptions import AppException
        from fastapi import status
        
        error_code = "DOMAIN_REASON_DETAIL"  # e.g. "RAW_DATA_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e
        ```
    * **BANNED**: `raise HTTPException(status_code=..., detail=str(e))` - This loses error_code!
    * **Frontend Catch**: `DioException` -> `AppError` (mapped by `error_code` from `details`).
    * **UI Display**: Map `AppError.code` to `AppLocalizations` key.

3.  **Strict Rule**: NEVER show the raw `message` from Backend to the User. Always map `error_code` to a localized string.

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
    * **Interceptors**: Centralized auth token injection.
    * **Transformers**: Background JSON parsing (`compute`).
    * **Exceptions**: Catch `DioException` and map to Domain Failures.

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
    
# 🛑 STOP! READ THIS CAREFULLY 🛑
**THIS DOCUMENT IS A CONTEXT REFERENCE ONLY.**
**DO NOT START ANY IMPLEMENTATION OR GENERATE CODE BASED ON THIS FILE YET.**
**STORE THIS CONTEXT IN YOUR MEMORY AND AWAIT FURTHER INSTRUCTIONS.**