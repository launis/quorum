# SYSTEM ARCHITECTURE MANIFESTO (2026 Edition)
**PROJECT**: Google Antigravity (Monorepo: Python Backend + Flutter Client)
**STATUS**: Phase 2 (Hardening & Standardization)

---

## 🛑 PRE-FLIGHT CHECKLIST (MANDATORY)

### 1. Dependency Strategy (Latest Stable Mandate)
The dependencies listed below serve as the **MINIMUM BASELINE**.
**ALWAYS** use the latest stable compatible versions available.
**DO NOT** restrict upgrades unless a specific breaking change is identified.

#### Backend (Python 3.14.2+)
| Package | Baseline Version | Purpose |
| :--- | :--- | :--- |
| `fastapi` | `0.128.0+` | Core Framework |
| `uvicorn` | `0.40.0+` | ASGI Server |
| `pydantic` | `2.12.5+` | Data Validation (V2) |
| `firebase-admin` | `7.1.0+` | Auth & Firestore |
| `openai` | `1.60.0+` | LLM Client |
| `litellm` | `1.81.3+` | LLM Proxy |
| `tenacity` | `9.1.2+` | Retry Logic |
| `tiktoken` | `0.12.0+` | Token Counting |

#### Frontend (Flutter)
| Package | Baseline Version | Purpose |
| :--- | :--- | :--- |
| `flutter_riverpod` | `^3.1.0` | State Management |
| `flutter_hooks` | `^0.21.0` | Widget Lifecycle |
| `go_router` | `^17.0.1+` | Routing |
| `dio` | `^5.7.0` | Networking |
| `firebase_auth` | `^6.1.4` | Authentication |
| `freezed` | `^3.2.3` | Immutable Models |
| `flutter_markdown_plus` | `^1.0.7` | Markdown Rendering |
| `riverpod_annotation` | `^4.0.0` | Code Gen Annotations |
| `riverpod_generator` | `^4.0.0` | Riverpod Code Gen |
| `custom_lint` | `^0.8.1` | Linting Standards |
| `riverpod_lint` | `^3.1.0` | Riverpod Lints |
| `json_serializable` | `6.11.2` | Serialization (PINNED core conflict) |

### 2. Modern Standards Enforcement (Banned Patterns)
The versions listed above enabling specific **Modern Architectures**.
Using these versions with "Legacy Patterns" is a **STRICT VIOLATION**.

| Area | Modern Requirement (MANDATORY) | Legacy Pattern (BANNED) |
| :--- | :--- | :--- |
| **State** | Use `@riverpod` (Generator) + `ref.watch` | `ChangeNotifier`, `StateProvider`, manual `Provider` |
| **Routing** | Use `GoRouteData` (Type-safe classes) | Raw strings: `context.push('/home')` |
| **API** | Use `Annotated[Dep, Depends()]` | `params: Dep = Depends()` (Old syntax) |
| **Models** | Use `model_validate`, `model_dump` | `.parse_obj()`, `.dict()` |
| **Hooks** | Use `HookConsumerWidget` + `useEffect` | `StatefulWidget` + `initState`/`dispose` |
| **Data** | Use `@freezed` (Immutable Unions) | Mutable classes or plain `json_serializable` |
| **Retries** | Use `@retry` (Tenacity) decorators | `while` loops with `sleep()` |
| **AI** | Use `AsyncOpenAI()` (Instantiated Client) | Global `openai.ChatCompletion.create()` |
| **Auth** | Use `authStateChanges()` (Reactive Stream) | Manual `currentUser` checks / `setState` |
| **HTTP** | Use `Interceptors` for Auth/Error handling | Inline `try/catch` or token injection |

### 3. Routine Quality Gates (Definition of Done)
**ALWAYS** run these checks before marking a task as complete.

#### Process & Mindset
*   **Root Cause Analysis**: Did I find *why* the error happened upstream, or did I just patch the symptom? (Review Section 18.4)

#### Backend (Python)
*   **Lint**: `ruff check . --fix` (Enforce style & fix imports)
*   **Type Check**: `mypy .` (Strict typing, no `Any` leaks)

#### Frontend (Flutter)
*   **Analyze**: `flutter analyze` (Standard linting)
*   **Custom Lint**: `dart run custom_lint` (Riverpod rules)
*   **Code Gen**: `dart run build_runner build -d` (Ensure synced generated files)

#### Cleanup Safety (Crucial)
*   **Double-Check Imports**: Before removing "unused" imports, search the codebase (`grep`) to ensure they aren't used in dynamic lookups, legacy routes, or dependency injection configurations.
*   **Verify Dependencies**: Ensure removing a "helper" function doesn't break a Dependency Provider used elsewhere.

---

## 🏛️ PART 1: DYNAMIC ARCHITECTURE & SCALING

# 4. Single Source of Truth (SSOT) & Wiring
**CRITICAL ARCHITECTURAL MANDATE:**

The `seed_data.json` file MUST adhere to the **Single Source of Truth (SSOT)** principle for step definitions.

### 4.1. Contract vs. Wiring
- **The Registry (`steps` array):** This is the **CONTRACT**. It defines WHAT a step is (Task Key, Model Config, System Prompt). It lives in the top-level `steps` list.
- **The Workflow (`workflows` array):** This is the **WIRING**. It defines HOW a step is used (Input Data Flow). It lives in the `workflows` list and must **ONLY** reference steps by `id`.

**❌ FORBIDDEN (Inline Definition in Workflow):**
```json
// DO NOT DO THIS inside a workflow!
{
  "id": "step_analyst",
  "task_key": "backend.agents.step_analyst.analyst_step", // ❌ REDUNDANT
  "config": { ... }, // ❌ REDUNDANT
  "inputs": { ... }
}
```

**✅ REQUIRED (Reference by ID):
```json
// DO THIS inside a workflow:
{
  "id": "step_analyst", // ✅ REFERENCES Registry
  "inputs": {
    "history_text": "$history_text", // ✅ WIRING ONLY
    "product_text": "$product_text"
  }
}
```

### 4.2. Immutable Registry
- The top-level `steps` list is the **Master Registry**.
- Use the `seed_data.json` file's `steps` array to define the agent's "Character" (System Prompt, Model).
- Use the workflow's `steps` array to define the agent's "Context" (Inputs).
1.  **Philosophy: "Schema is King" (Contract-First)**:
    *   **Single Source of Truth**: Pydantic V2 models drive everything.
    *   **Auto-Gen**: API Specs and Frontend Entities must be generated from Pydantic models. No manual duplication.

2.  **Backend: The Generic Engine**:
    *   **BANNED**: Hardcoded step logic (e.g., `if step == 'guard'`).
    *   **REQUIRED**: Metadata-Driven execution via Task Registry.
    *   **Zero-Fallback**: System must fail fast if DB configuration is missing. No hardcoded prompts or model names in code.

3.  **AI Layer: Reliability**:
    *   **Tooling**: Use **LiteLLM Native Structured Output** (`response_format`).
    *   **Strict Mode**: Agents must return Pydantic models. `dict` returns are FORBIDDEN.
    *   **Self-Correction**: Pipeline must catch validation errors and feed them back to LLM.

4.  **Frontend: Hybrid Server-Driven UI (SDUI)**:
    *   **Default**: Use generic `DynamicFormWidget` based on `UI_Schema`.
    *   **Constraint**: Hardcoding *forms* is banned, but hardcoding *components* mapping to schema fields is allowed.

---

## 🐍 PART 2: PYTHON BACKEND MANDATES

1.  **Framework (FastAPI)**:
    *   **Lifespan**: Use `async contextmanager`. No `@app.on_event`.
    *   **Concurrency**: All I/O routes must be `async def`. CPU tasks go to `run_in_threadpool`.

2.  **Date Handling (Temporal Standard)**:
    *   **Storage**: Store as `datetime`. Repository handles DB-specifics.
    *   **Serialization**: ALWAYS use `.isoformat()` for JSON output (e.g., `2026-02-07T...`).
    *   **BANNED**: `str(datetime.now())` (undefined format) or `json.dumps()` on datetime objects without a custom default handler.
    *   **Timezone**: Always use `UTC` (`datetime.now(timezone.utc)`).

3.  **Logging (Unified Format)**:
    *   **Format**: `%(asctime)s | %(levelname)s | [%(execution_id)s] | ...`
    *   **Context**: `execution_id` must be present for traceability.

4.  **Data Passing Mandate (No Dictionaries)**:
    *   **The Rule**: All internal data exchange between Services, Hooks, and Agents MUST use Pydantic Models.
    *   **BANNED**: Passing `dict` or `dict[str, Any]` as a return value or argument for structured data.
    *   **EXCEPTION**:
        *   Raw JSON payloads at the **API Boundary** (e.g., `request.json()`).
        *   Low-level **Database Drivers** (serialization/deserialization).
    *   **Philosophy**: "If it has a shape, it must be a Model. Dictionaries are for unordered maps only."

5.  **Strict Pydantic Validation (Fail Fast)**:
    *   **The Rule**: ALL Domain Models MUST use `ConfigDict(strict=True)`.
    *   **Implication**: No implicit type coercion (e.g., string "1" -> int 1 is forbidden).
    *   **Why**: Data integrity is paramount. If the type is wrong, the upstream data source is broken and must be fixed.

6.  **API Boundary & Data Contracts (Schema-First)**:
    *   **Requests**: `body` MUST be a Pydantic Model. Using `dict` or `Request` to bypass validation is BANNED.
    *   **Responses**: MUST define `response_model` in the route decorator (e.g., `@router.post(..., response_model=MyResponse)`).
    *   **Return Values**: Return the Pydantic Model instance directly. Do NOT manually call `.model_dump()` or return a `dict`. Let FastAPI handle the serialization.
    *   **Null Safety**: API Responses should NOT contain `null` for list fields (use `[]`) or boolean fields (use `false`).

---

## ⚠️ PART 3: ERROR HANDLING CONTRACT (RFC 7807 & FAIL FAST)

**SINGLE SOURCE OF TRUTH**: `backend/exceptions.py`

### 3.1. The Protocol (RFC 7807)
All errors MUST follow the RFC 7807 Problem Details standard. The `AppException` class is the canonical implementation. 

### 3.2. Mandatory Fields
When raising an exception, you must provide:
1.  **message**: A technical English description for logs (NEVER shown to user).
2.  **status_code**: The appropriate HTTP status code (e.g., 400, 404, 500).
3.  **details**: A dictionary containing at least:
    *   `error_code`: A machine-readable Enum value from `backend.exceptions.ErrorCodes` (e.g., `VALIDATION_FAILED`).
    *   **NOTE**: This `error_code` is automatically promoted to `extensions.error_code` in the final JSON response.

### 3.3. Implementation Pattern (Fail Fast)
If an invalid state is detected, **CRASH IMMEDIATELY**. Do not pass `None` or return empty objects.

```python
    except Exception as e:
        from backend.exceptions import AppException, ErrorCodes, status

        # 1. Define Error Code (SSOT)
        error_code = ErrorCodes.INVALID_JSON_PAYLOAD

        # 2. Log the raw error with STRUCTURED FORMAT (Component + Error Code)
        logger.error(f"[GraphEngine] {error_code.value}: Invalid initial state: {e}", exc_info=True)

        # 3. Raise explicit AppException wrapping the original error
        raise AppException(
            message=f"Invalid initial state structure: {e}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": error_code, 
                "original_error": str(e) # Context for debugging
            },
        ) from e
```

### 3.4. Localizing Error Codes (Frontend Responsibility)
**THE CONTRACT (Split Responsibility):**
*   **Backend**: Sends the machine-readable code (e.g., `VALIDATION_FAILED`) and technical details (English).
*   **Frontend**: Maps the **Code** to a human-readable Title in `app_*.arb`.
*   **Result**: User sees "Validointivirhe" (FI) or "Validation Failed" (EN), followed by the technical detail.

#### Step 1: Define Key in ARB Config
```json
// client_app/lib/l10n/app_fi.arb
{
  "errValidationFailed": "Validointivirhe",
  "errInternalServerError": "Palvelinvirhe",
  "errorValidationMissing": "Puuttuvat kentät: {fields}"
}
```

#### Step 2: Map Code to Key (Dart)
Use the `AppErrorExt` extension in `client_app/lib/core/error/app_error_ext.dart`.

```dart
// client_app/lib/core/error/app_error_ext.dart
  static String _localizeErrorCode(String errorCode, AppLocalizations l10n) {
    return switch (errorCode) {
      'VALIDATION_FAILED' => l10n.errValidationFailed,
      'INTERNAL_SERVER_ERROR' => l10n.errInternalServerError,
      'RESOURCE_NOT_FOUND' => l10n.errResourceNotFound,
      _ => l10n.errorUnknown,
    };
  }
```

### 3.5. Specialized Exceptions (Domain Semantic)
Do not use raw `AppException` if a more specific semantic wrapper exists.

| Exception Class | Usage Scenario | Required Arguments |
| :--- | :--- | :--- |
| **`ResourceNotFoundError`** | When a DB item is missing (404) | `resource_type` (str), `resource_id` (str) |
| **`ConfigurationError`** | Missing API keys or bad config (500) | `message` (str) |
| **`PermissionDeniedError`** | RBAC failures (403) | `message` (str) |
| **`AuthenticationError`** | Invalid/Missing Token (401) | `message` (str) |
| **`SecurityViolationError`** | Guardrails/WAF block (400) | `message` (str) |
| **`ConflictError`** | State conflict/race condition (409) | `message` (str) |
| **`ServiceUnavailableError`** | External API/DB down (503) | `message` (str) |
| **`AgentExecutionError`** | Agent logic failure (500) | `detail` (code), `original_error` (Exception), `agent_name` (str) |
| **`WorkflowExecutionError`** | Step Engine failure (500) | `step_id` (str), `task_key` (str), `original_error` (Exception) |
| **`FatalInterruption`** | Stop workflow immediately (500) | `step_name` (str), `reason` (str) |


#### Example: Resource Not Found
```python
    # BAD: Generic 404
    raise AppException("Workflow missing", status_code=404)

    # GOOD: Semantic Wrapper
    from backend.exceptions import WorkflowNotFoundError
    raise WorkflowNotFoundError(workflow_id="wf-123") 
    # Auto-generates message: "Workflow with ID 'wf-123' not found"
```

#### Example: Agent Failure
```python
    try:
        result = await agent.run(...)
    except Exception as e:
        # Wraps error, preserves cause, auto-sets status 500
        raise AgentExecutionError(
            detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
            original_error=e,
            agent_name="Logician",
            step_id=step.id
        ) from e
```

### 3.6. Managed Fallbacks (Soft Failures) - USE RARELY
**DEFAULT RULE**: Raise an Exception (Fail Fast).

**USAGE FREQUENCY: RARE (< 5% of cases)**
Only use this pattern in the **View/BFF Layer** when a partial failure is strictly better than a total crash.

*   **Scenario by Preference**:
    1.  **Core Logic/Data Integrity**: ❌ NEVER (Must Fail Fast).
    2.  **Critical UI**: ❌ NEVER (User must know it failed).
    3.  **Composite Dashboard Widgets**: ✅ YES (One widget failing shouldn't blank the screen).
    4.  **Optional Decorations (LLM Hints)**: ✅ YES (Core data is valid, hints are optional).

#### Example: BFF Transformer (Resilience)
```python
    try:
        # Complex transformation that might fail on bad data
        chart_data = self._build_radar_chart(data)
    except Exception as e:
        # Only swallow error if chart is NON-CRITICAL
        logger.warning(f"Radar Chart generation failed (Returning empty): {e}")
        chart_data = {} 
```

### 3.7. Unified Client Error Presentation
**THE MANDATE:** All client-side errors, including `AsyncValue.error` states and screen-level failures, MUST be displayed using the standardized `ErrorView` widget.

*   **BANNED**: Ad-hoc implementations like `Center(child: Text('Error'))` or `Icon(Icons.error)`.
*   **REQUIRED**:
    ```dart
    // client_app/lib/core/ui/error_view.dart
    
    // Usage in AsyncValue.when
    error: (err, stack) => ErrorView(
      error: err,
      onRetry: () => ref.refresh(provider),
      retryLabel: l10n.retry,
      compact: false, // Use true for widgets/sections
    ),
    ```
*   **Localization**: `ErrorView` automatically handles `AppError` localization via `AppErrorExt`. This ensures backend error codes (e.g., `AGENT_EXECUTION_CRITICAL`) are displayed as localized, user-friendly messages.

### 3.8. Upstream Error Mapping (Vendor Failures)
**THE MANDATE:** Never expose raw Vendor/Upstream errors (e.g., `googleapiclient.errors.HttpError`) to the user.

*   **The Problem:** A generic "HttpError 403" tells the user *what* happened, but not *how to fix it*.
*   **The Rule:** You MUST catch known upstream errors and map them to semantic `AppException` types with **Actionable Instructions**.

#### Example: Google Search 403 (Configuration Error)
```python
    try:
        service.cse().list(...).execute()
    except HttpError as e:
        # 1. Analyze Root Cause (Don't just log 403)
        if e.resp.status == 403 and "Custom Search JSON API" in str(e):
            # 2. Map to Semantic Error (ConfigurationError)
            raise ConfigurationError(
                message="Google Custom Search API is not enabled in Cloud Console.",
                details={"action": "Enable 'Custom Search JSON API' in Google Cloud Console."}
            ) from e
        
        # 3. Default Fallback
        raise ServiceUnavailableError("Google Search failed upstream.") from e
```


## 💙 PART 4: FLUTTER CLIENT MANDATES

1.  **State (Riverpod 3.0)**:
    *   **Generator Only**: `@riverpod` syntax.
    *   **Declarative**: `ref.watch`. No manual subscriptions.
    *   **AsyncValue**: Use `.when()` for UI states.
    *   **Pattern**: "Optimistic + Invalidate" (Hybrid).
    *   **Mandate**: Mutations MUST:
        1. Capture `previousState`.
        2. Apply immediate **Optimistic Update** (AsyncData).
        3. Call API via Repository.
        4. **Silent Invalidation**: Call `ref.invalidateSelf()` on success to sync with server.
        5. **Rollback**: On error, restore `previousState` and rethrow.
        ```dart
        Future<void> addItem(Item item) async {
          final previousState = state.valueOrNull;
          if (previousState == null) return;
          // 1. Optimistic Update
          state = AsyncData([...previousState, item]);
          try {
            // 2. API Call
            await ref.read(repoProvider).addItem(item);
            // 3. Silent Sync
            ref.invalidateSelf();
          } catch (e) {
            // 4. Rollback
            state = AsyncData(previousState);
            rethrow;
          }
        }
        ```

2.  **Routing (GoRouter)**:
    *   **Type-Safe**: `HomeRoute().go(context)`. No raw strings.
    *   **Logic**: Guards belong in `redirect`, not `build()`.

3.  **Network (Dio)**:
    *   **Interceptors**: Centralized Auth & Error handling (RFC 7807 parsing).
    *   **Background**: JSON parsing must happen in `compute`.

4.  **UI/UX**:
    *   **Theming**: `FlexColorScheme`. No manual `ThemeData`.
    *   **Markdown**: Use `flutter_markdown_plus` (Strictly).
    *   **Localization**: `app_en.arb` is Source of Truth.

---

## ⏱️ PART 5: TIMEOUT & RELIABILITY STRATEGY

1.  **Philosophy**: "Fail Fast & Retry"
    *   **Zombie Processes**: Forbidden. All external calls must have explicit timeouts.
    *   **Retry**: Infrastructure (Tenacity/LiteLLM) handles retries, NOT the user.

2.  **Frontend Mandates**:
    *   **Visualization**: Operations > 10s must use Progress Bars (SSE).

---

## 💾 PART 6: DATA ARCHITECTURE & SEEDING PROTOCOLS

1.  **Repository Parity Mandate (Dual Backend)**:
    *   **Strict Requirement**: ANY database modification MUST be implemented in BOTH:
        -   `backend/database/repository.py` (TinyDB)
        -   `backend/database/firestore_repo.py` (Firebase/Firestore)
    *   **Constraint**: Maintain strict parity between Local and Cloud implementations.

2.  **Hybrid State Architecture (Event Log vs Blackboard)**:
    *   **Truth**: The `TraceEvent` log is the immutable history.
    *   **Performance**: The `WorkflowState.context_variables` (Blackboard) is the mutable current state.
    *   **Mandate**: All steps MUST write to the Blackboard and emit an Event. Verification replays Events to rebuild State.

3.  **Seeding Authority**:
    *   **Master Seed**: `backend/seed/seed_data.json` is the authoritative baseline.
    *   **Logic**: `backend/seed/run_seed.py` creates the state. **DO NOT MODIFY** seed data structure without approval.
    *   **SSOT Structure (Contract vs. Wiring)**:
        *   **Registry (`steps`)**: DECLARES the capability (Task Key, Config). This is the CONTRACT.
        *   **Workflow (`workflows`)**: WIRES the capability. Must reference steps by `id` ONLY.
        *   **BANNED**: Inline `task_key` or `config` definitions within `workflows`.
    *   **Derived Data (Ontology)**: The Seeder automatically extracts `Dimension` records from `evaluation_matrix` components. Do not manually seed the `dimensions` table.

3.  **Root Cause Fix Mandate**:
    *   **Principle**: Fix the source, don't patch the symptom.
    *   **BANNED**: Copying data between tables to fix sync issues.
    *   **REQUIRED**: Fix the reader to look at the correct source of truth.

---

## 🎨 PART 7: UI & UX STANDARDS (2026 MANDATE)

1.  **Responsive Layout**:
    *   **Breakpoint**: `600dp` (Mobile vs Desktop).
    *   **Desktop**: Use `NavigationRail` + `VerticalDivider`. Max content width `1000dp`.
    *   **Mobile**: Use `NavigationBar`.

2.  **Localization Authority**:
    *   **Source**: `client_app/lib/l10n/app_*.arb` only.
    *   **BANNED**: Hardcoded strings in widgets.
    *   **Keys**: camelCase (`dashboardTitle`).

3.  **Preferences**:
    *   **Scope**: Language (`fi`/`en`) & Theme (`system`/`light`/`dark`).
    *   **Sync**: Immediate UI update (Riverpod) + Local Persist (SharedPrefs) + Remote Patch.

---

## 🛠️ PART 8: ENVIRONMENT & TOOLING CONSTRAINTS

1.  **Windows 11 / PowerShell**:
    *   **Encoding**: Always specify `encoding="utf-8"` in Python scripts.
    *   **Pathing**: Use raw strings `r"c:\path"` or `pathlib`.
    *   **No Grep**: Use `python scripts/analyze_json.py` for data inspection.

2.  **Repository Method Protection**:
    *   **History**: On 2026-01-16, critical methods were deleted.

3.  **Debugging Protocols ("Silent Console, Verbose Log")**:
    *   **Console Output**: Terminals (`run_local.bat` windows) MUST remain minimal. Only print "Starting..." and "Check logs".
    *   **Source of Truth**: All debug data (Setup Config, Requests, Errors, State) MUST flow to:
        *   `backend_debug.log` (Python)
        *   `client_debug.log` (Flutter)
    *   **Agent Instruction**: If a user reports an error, **ALWAYS** read these two files first (`view_file`). Do not ask the user for console output.

4.  **Logic Integrity Mandate (workflow-step-logic)**:
    *   **Scope**: This includes `seed_data.json` structure, `GraphEngine` execution flow, and Agent `PRODUCES_KEYS` / `REQUIRES_KEYS`.
    *   **Reasoning**: "Fix the component, do not re-route the pipeline."
    *   **Exception**: Only bug fixes that restore documented behavior are allowed, but must be explicitly noted.

5.  **Architectural Integrity (Zero-Shortcut Policy)**:
    *   **Mandate**: NEVER bypass established services (e.g., `StorageService`, `repository.py`, `LocalizationService`) for "quick fixes", "experimental patches", or direct I/O.
    *   **Prohibition**: Ad-hoc implementations (including "temporary" file reads or hardcoded logic) are STRICTLY FORBIDDEN, even for testing.
    *   **Reason**: Quick fixes become technical debt, break environmental portability (Local vs Cloud), and bypass validation layers.
    *   **Enforcement**: If a Service exists, it MUST be used. If it doesn't fit, refactor the Service to handle the new case properly.

---

## 🗺️ PART 9: KNOWLEDGE BASE MAP (DEEP DIVES)

For detailed implementation logic, refer to these Knowledge Items:

1.  **Backend & AI**:
    *   `knowledge/backend_system_architecture` (Models, API, Schema)
    *   `knowledge/workflow_orchestration_and_reliability` (Engine Logic)
    *   `knowledge/seeding_and_data_lifecycle` (Data Integrity)

2.  **Frontend**:
    *   `knowledge/client_application_development` (Flutter Patterns)
    *   `knowledge/hybrid_sdui_strategy` (Dynamic UI Logic)
    *   `knowledge/identity_and_access_management` (Auth & Roles)

3.  **Environment**:
    *   `knowledge/development_environment_modernization` (Troubleshooting)

---

## 🌍 PART 10: INTERNATIONALIZATION (I18N) STANDARDS

1.  **Dual Sovereign Locations**:
    *   **Frontend**: `client_app/lib/l10n` (Standard .arb files).
    *   **Backend**: `backend/l10n` (JSON files `en.json`, `fi.json`).
    *   **Backend Service**: Use `backend.services.localization.LocalizationService.translate(key, **kwargs)` to separate code from content.
    *   **Context**: Language is determined automatically via `ContextVar` (from `Accept-Language` header). Do NOT pass `lang` explicitly.

2.  **Mandates**:
    *   **Separation**: Frontend and Backend maintain separate, independent localization trees.
    *   **Hardcoding**: STRICTLY BANNED. All user-facing strings must use the localization keys.
    *   **Parity**: Keys should be added to both English (`en`) and Finnish (`fi`) files immediately.
    *   **Interpolation**: Use `**kwargs` in `translate` for dynamic values.
        *   *JSON*: `"welcome": "Hello {name}"`
        *   *Python*: `LocalizationService.translate("welcome", name="User")`
        *   *Safety*: Service swallows `KeyError` if arguments are missing, returning the raw string.

## 🌍 PART 11:HYBRID SERVER-DRIVEN UI (SDUI) STANDARDS:
    * **Philosophy**: "Schema defines Data, Frontend defines Experience".
    * **Hybrid Implementation**: 
        * **Default**: Use generic `DynamicFormWidget` based on `UI_Schema`.
        * **Premium Override**: Frontend MAY implement custom, high-fidelity Widgets (e.g., Drag & Drop, Visual Selectors) for specific steps, provided they output the exact data structure required by the Schema.
    * **Constraint**: Hardcoding *forms* is banned, but hardcoding *components* that map to schema fields is allowed for UX.

## 🌍 PART 12: BACKEND LOCALIZATION PATTERNS (DOMAIN STANDARDIZATION)

When defining Domain Models that accept free-text input from LLMs (which may be in Finnish or English) but require standardized numeric or boolean values for logic, follow this **Enum Code Pattern** (formerly Fuzzy Match):

1.  **Dual Fields**: Define one field for the **Enum Code** (String/Enum) and one for the **Standardized Value** (Float/Bool).
2.  **Validator**: Use a `@model_validator(mode="after")` to map the Enum Code to the Standardized Value.

### Implementation Template

```python
class RiskLevel(str, Enum):
    LOW = "RISK_LOW"
    MEDIUM = "RISK_MEDIUM"
    HIGH = "RISK_HIGH"

class RiskAssessment(BaseModel):
    # 1. Enum Code (LLM outputs this specific string)
    risk_code: RiskLevel = Field(..., description="Risk level code (RISK_LOW, RISK_MEDIUM, RISK_HIGH).")
    
    # 2. Standardized Value (Logic uses this)
    risk_score: float = Field(default=0.0, description="Numeric score (1.0-3.0).")

    @model_validator(mode="after")
    def calculate_score(self, info: ValidationInfo) -> 'RiskAssessment':
        # 3. Define Mapping (Code -> Value)
        mapping = {
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 2.0,
            RiskLevel.HIGH: 3.0
        }
            
        # 4. Exact Match Logic
        if self.risk_score == 0.0 and self.risk_code:
            self.risk_score = mapping.get(self.risk_code, 0.0)
            
        return self
```

### Key Principles
*   **Determinism**: LLM is instructed to output exact codes (`RISK_HIGH`).
*   **Simplicity**: No fuzzy matching or language detection.
*   **SSOT**: The Enum definition is the single source of truth.
*   **Fail Fast**: If LLM outputs an invalid code, Pydantic validation fails immediately.

## 🏗️ PART 13: STUDIO & BUILDER LOCALIZATION SAFETY

The **Cognitive Studio** (Workflow Builder) operates in **Raw Mode**. It interacts directly with the `seed_data.json` / Registry structure key-values.

### 1. The Hazard
*   **What you see**: Inputs labeled `History Text`, `Product Text`, `Reflection Text`.
*   **What they are**: These are **Translation Keys** (lookups), NOT English defaults.
*   **The Risk**: If an Administrator renames `History Text` to `Historiateksti` in the Studio UI:
    1.  The **Key** in the database becomes `Historiateksti`.
    2.  The Backend `localize_schema` function looks for `Historiateksti` in `fi.json` / `en.json`.
    3.  It finds nothing.
    4.  **Result**: English users see "Historiateksti" (Broken Localization).

### 2. The Rule
> **"Edit Values, Never Keys"**

*   **Allowed**: Changing numerical weights, thresholds, prompts (if they are content).
*   **Forbidden**: Renaming generic UI labels in the Builder Config.
*   **Protocol**: To change a label, edit `backend/l10n/*.json` and `backend/seed/seed_data.json` instead. The Studio is for **Assembly**, not **Copywriting**.

## 🧩 PART 14: LOGIC & VALIDATION MANDATES (STRICT SCALE)

When implementing AI steps that must output specific numeric values (e.g., Scores 1-100 or 1-5), you must follow the **"Fail Fast & Explicit"** pattern.

### 1. The Hazard
*   **Silent Failure**: The AI outputs `0` or `101` when the scale is `1-100`.
*   **Soft Fail**: Code clamps the value (`max(1, min(100, val))`).
*   **Result**: Valid-looking data that is actually corrupt/hallucinated.

### 2. The Solution (Fail Fast)
*   **Code**: If a value is out of bounds, **CRASH** the step immediately (`raise ValueError`). Do not fix it silently.
*   **Why**: This forces the Prompt Engineer to fix the *instruction*, rather than hiding the problem in the code.

### 3. The Instruction (Explicit Prompting)
*   **Source of Truth**: The "Rule" must exist in the Database (Component), NOT just in Python code.
*   **Pattern**:
    1.  Define the instruction in `seed_data.json` as a reusable component (e.g., `INSTRUCTION_STRICT_SCALE`).
    2.  Inject this component into the `llm_prompts` list of the Agent.
    3.  **Do NOT hardcode** the prompt text ("Must be between 1-100") in Python.

### 4. Implementation Example (Seed Data)
```json
{
  "id": "INSTRUCTION_STRICT_SCALE",
  "type": "instruction",
  "content": "**TÄRKEÄÄ**: Kaikkien pisteiden ON oltava määritellyn asteikon (Scale) sisällä.\n\nSinun on noudatettava asteikon rajoja ehdottomasti. Pisteet alle asteikon minimin tai yli maksimin ovat kiellettyjä.",
  "description": "Pakottaa noudattamaan matriisin asteikkoa (Fail Fast)."
}
```
*   **Effect**: The Prompt aligns with the Code's strict validation. If the AI fails, the error log points to the prompt, and you fix the prompt.

## 🧬 PART 15: STRICT TYPING & SPECIALIST DATA (BFF MANDATE)

### 15.1. UiSection Contract
*   **Mandate**: The `UiSection` model (used for frontend rendering) strictly enforces `data: dict[str, Any]`.
*   **Forbidden**: passing `None` as data.
*   **Frontend Impact**: Pydantic will raise a `ValidationError` if `data` is missing, causing a 500 Internall Server Error for the entire report.
*   **Solution**: In the BFF Transformer, always default to an empty dictionary `{}` if the data source is missing or invalid.
    ```python
    # BAD (Crashes if logician_data is None)
    return UiSection(..., data=self._transform_logician_data(steps.get("step_logician")))

    # GOOD (Safe Fallback)
    data = self._transform_logician_data(...) or {}
    return UiSection(..., data=data)
    ```

### 15.2. Specialist Data Interchange Protocols (Strict Nesting Mandate)
The system enforces a **STRICT NESTED FORMAT** for all Specialist Agents.

1.  **Mandatory Wrapped Format**:
    *   **Requirement**: All Agents MUST return data nested under their specific model key.
    *   **Structure**: `{ "logician_data": { "toulmin_score": ... } }`
    *   **Reason**: Matches the `LogicianOutput` Pydantic model structure defined in `domain.py`.
    *   **Forbidden**: Returning flattened data (e.g., `{ "toulmin_score": ... }`) at the root level.
    *   **Enforcement**: The Backend `bff_transformer.py` will **FAIL FAST** (raise 500) if the nested key (`logician_data`, `falsifier_data`, etc.) is missing. Legacy "flat" data is **NOT SUPPORTED**.

2.  **Panel Agent Exception (Explicit Mapping)**:
    *   **Source**: The Consolidated Panel Agent (`step_panel`).
    *   **Structure**: The Panel Agent aggregates multiple outputs, but *internally* it must still map them to the correct nested fields (e.g., `panel.logician_data`).
    *   **Transformer Logic**: The BFF Transformer extracts these nested fields directly. It does NOT flatten them on input.

### 15.3. Transformer Implementation Pattern
When implementing `_transform_*` methods in `bff_transformer.py`, follow this **Robustness Pattern**:

```python
    # 3. Fail Safe (UI robustness)
    logger.warning("Specialist Data missing/invalid. Returning empty dict.")
    return {}

## 🗣️ PART 16: STRICT LOCALIZATION & HELP TEXTS (ENUM/KEY MANDATE)

### 16.1. The "No-String" Backend Policy
*   **Philosophy**: The Backend supplies **DATA** (Scores, Result Codes). The Frontend supplies **PRESENTATION** (Labels, Help Texts, Explanations).
*   **BANNED**: Sending localized strings or help text payloads from Python.
    *   ❌ `{"status": "Orgaaninen", "help": "Tämä tarkoittaa..."}`
*   **REQUIRED**: Sending Immutable Keys or Enums.
    *   ✅ `{"status": "AUTH_ORGANIC"}`

### 16.2. Implementation Pattern (Enum-Driven)

#### Backend (Python)
Define standard Enums in `view.py` or domain models.
```python
class Authenticity(str, Enum):
    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"

# usage in bff_transformer.py
raw["authenticity_assessment"] = Authenticity.ORGANIC.value 
```

#### Frontend (Flutter)
Map these keys immediately to `AppLocalizations` in the Widget.
```dart
// client_app/lib/l10n/app_fi.arb
"authOrganic": "Orgaaninen (Aito)",
"helpAuthenticity": "Aitous mittaa vastauksen luonnollisuutta..."

// components/specialist_section.dart
Widget _buildAuth(String key, BuildContext context) {
  final l10n = AppLocalizations.of(context)!;
  
  // 1. Lookup Label
  String label = l10n.authUnknown;
  if (key == 'AUTH_ORGANIC') label = l10n.authOrganic;
  
  // 2. Lookup Help Text (Static Key)
  return UnifiedMetricGauge(
    descriptionFi: l10n.helpAuthenticity, // ✅ Correct
    descriptionEn: l10n.helpAuthenticity, // ✅ Riverpod handles Locale
    ...
  );
}
```

### 16.3. Help Text & Tooltips
*   **Storage**: All detailed help texts (paragraphs) MUST live in `.arb` files.
*   **Keys**: Use semantic keys like `helpStrategicDepth`, `helpPerformativity`.
*   **Usage**: Pass the *Result* of the lookup (`l10n.helpStrategicDepth`) to widgets, never the raw string.

## 📝 PART 17: DOCUMENTATION & HYGIENE (STRICT MANDATE)

### 17.1. Language Policy
*   **English ONLY**: All code, variable names, comments, commit messages, and docstrings MUST be in English.
*   **Exceptions**:
    *   Content in `backend/l10n/fi.json` or `app_fi.arb`.
    *   Hardcoded configuration values (e.g., specific Finnish search terms in `seed_data.json`).

### 17.2. Python Documentation (Backend)
*   **Docstrings**: EVERY public module, class, and method MUST have a docstring.
*   **Style**: Use **Google Style** formatting.
    ```python
    def calculate_score(self, value: float) -> float:
        """Calculates the normalized score.

        Args:
            value: Raw input value (0-100).

        Returns:
            Normalized score (0.0-1.0).
            
        Raises:
            ValueError: If input is out of bounds.
        """
    ```
*   **Type Hits**: STRICTLY REQUIRED for all arguments and return values. `state: Any` is a smell; use specific types or `dict[str, Any]` if absolutely necessary.

### 17.3. Dart Documentation (Frontend)
*   **Public API**: Use `///` (triple slash) for all public Classes, Widgets, and Methods.
    ```dart
    /// Displays the detailed analysis for a specific agent.
    /// 
    /// Requires [data] to be populated with valid localization keys.
    class SpecialistSection extends ConsumerWidget { ... }
    ```
*   **Intention**: Explain *WHY* logic exists, not just *WHAT* it does.

### 17.4. Code Hygiene
*   **No Dead Code**: Do NOT leave commented-out code blocks ("zombie code"). Delete them. Version control is your history.
*   **No "TODO" without Ticket**: `TODO` comments must include a clear owner or objective.
*   **Clean Imports**: unused imports must be removed (use `ruff` / `dart fix`).

## 🛡️ PART 18: THE ZERO-COMPROMISE PLEDGE (QUALITY STANDARD)

**"Production Quality, Day One."**

### 18.1. NO Fallback Code (Fail Fast)
*   **The Rule**: If an error occurs (e.g., missing data, invalid state), the system MUST raise an exception immediately.
*   **Banned**: `try-except pass`, returning `None` silently, or patching with empty lists `[]` to keep the UI running.
*   **Why**: Silent failures hide bugs. A crash (500) is better than a lie.

### 18.2. NO Default Values (Strict Typing)
*   **The Rule**: Domain models MUST NOT have default values for required fields.
*   **Banned**: `score: float = 0.0` or `name: str = "Unknown"`.
*   **Exemption**: Optional fields (`score: float | None = None`) where `None` has a specific semantic meaning (e.g., "Not Run Yet").

### 18.3. NO Hardcoding (Configuration Sovereignty)
*   **The Rule**: Value that can change MUST exist in `seed_data.json` or `l10n`.
*   **Exception**: Standard Enums (e.g., `RiskLevel.HIGH`) are the **preferred** way to handle fixed sets of values in code.
*   **Banned**: Hardcoded prompts, thresholds (`if score > 0.5`), or UI strings in code.
*   **Validation**: If you see a "Magic Number" or "Magic String", extract it to a Constant or Enum.

### 18.4. NO Surface-Level Patches (Root Cause Mandate)
*   **The Rule**: **ALWAYS** search for and fix the root cause. **NEVER** patch just the surface symptom.
*   **Philosophy**: If a crash (e.g., `KeyError`, `NullPointerException`) occurs, the bug is **NOT** where the crash happened—it is upstream where the invalid data was created.
*   **Banned**: 
    - Adding "safety checks" that just hide the error (e.g., `if x is None: return ""`) without understanding *why* `x` is None.
    - Casting types blindly (`as String`) to silence the compiler.
    - Bypassing Services or duplication logic to "get it working".
*   **Protocol**: You must explain the *Root Cause* in your analysis before proposing a fix.
### 18.5. NO Backward Compatibility (Clean Break)
*   **The Rule**: Do not keep "Legacy Adapters" or "shims" for old data structures.
*   **Action**: If the schema changes, the old data is invalid. Wipe it or migrate it strictly.
*   **Why**: Supporting two versions doubles the testing surface and hides technical debt. We are in a "Hardening Phase", not a "Long-Term Support" phase.

### 18.6. NO Embedded Steps (Relational Mandate)
*   **The Rule**: Workflows must **NEVER** contain full Step definitions.
*   **Structure**:
    - **Registry (`steps`)**: The ONLY place where a Step is defined (ID, Task Key, Prompts, Models).
    - **Workflow (`workflows`)**: A list of **Links** only (`id`, `inputs`, `config` overrides).
*   **Banned**: Defining `task_key`, `description`, or `ui_schema` inside a Workflow's step list.
*   **Reason**: "System Level Error". Embedding creates duplicate sources of truth and desynchronizes the Registry.
*   **Enforcement**: Use `backend/scripts/analyze_seed_data.py` to audit for embedded steps. The Seeder will strip them, but the Source File must be clean.