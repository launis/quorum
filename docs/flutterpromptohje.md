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
    * **Date Handling Mandate (Temporal Representation Standard)**:
        * **Format**: All timestamps MUST be Python `datetime` objects.
        * **Storage**: Store as `datetime` (Pydantic handles ISO-8601 string conversion for JSON/Firestore automatically).
        * **BANNED**: Do NOT use `str(datetime.now())` or `.isoformat()` manually in routers or models unless specifically required for legacy text-injection.
        * **Timezone**: Always use `UTC` (e.g. `datetime.now(timezone.utc)`).

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

**SINGLE SOURCE OF TRUTH**: `backend/exceptions.py`

⚠️ **STRICT MANDATE**:
1.  **RFC 7807**: All errors MUST follow the Problem Details standard.
2.  **PATTERN**: You MUST ALWAYS implement both:
    *   **Logger**: `logger.error(f"{error_code}: {e}", exc_info=True)`
    *   **Exception**: `raise AppException(...)`
3.  **SOURCE**: Refer to the docstring in `backend/exceptions.py` for the complete Usage Guide, Banned Patterns, and Error Code list.

**DO NOT** improvise error handling. **DO NOT** use `HTTPException` directly.

**Reference Implementation**:
```python
from backend.exceptions import AppException, ErrorCodes
# ...
except Exception as e:
    error_code = ErrorCodes.INTERNAL_SERVER_ERROR
    logger.error(f"{error_code}: {e}", exc_info=True)
    raise AppException(
        message="Detailed message for logs",
        status_code=500,
        details={"error_code": error_code}
    ) from e
```

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
    
--------------------------------------------------------------------------------

PART 5: ERROR HANDLING & TIMEOUT STRATEGY (2026 STANDARDS)

1.  **Philosophy: "Fail Fast & Retry"**:
    * **Zombie Processes**: It is unacceptable for a process to hang indefinitely. Timeouts must be explicit.
    * **Retry Logic**: Transient network errors (timeouts, 503s) must be retried automatically by the infrastructure (Backend/LiteLLM), NOT the user.

2.  **Backend Mandates**:
    * **LLM Clients**: strictly enforce `timeout` (e.g., 120s) on all external API class.
    * **Worker Jobs**: Jobs must not exceed global limits (e.g., 900s). `TimeoutError` in workers must be caught, logged, and marked as `FAILED` to release resources.
    * **No Infinite Waits**: Never use `await future` without `asyncio.wait_for(...)` or equivalent lower-level timeouts definition.

3.  **Frontend/UX Mandates**:
    * **Long-Running Operations**:
        * **Visualization**: Reports/Audits taking > 10s must use **Progress Bars** (SSE/WebSockets), not infinite "Loading..." spinners.
        * **Optimistic UI**: Do not block the UI for heavy generation. Background the task and notify completion.
    * **Timeout Handling**:
        * If a specific request times out (408/504), display a specific "Server Busy" message allowing a manual retry.
        * Do not auto-retry indefinitely in the UI (batteries/data usage).

--------------------------------------------------------------------------------

# 🛑 STOP! READ THIS CAREFULLY 🛑
**THIS DOCUMENT IS A CONTEXT REFERENCE ONLY.**
**DO NOT START ANY IMPLEMENTATION OR GENERATE CODE BASED ON THIS FILE YET.**
**STORE THIS CONTEXT IN YOUR MEMORY AND AWAIT FURTHER INSTRUCTIONS.**