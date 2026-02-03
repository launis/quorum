# SYSTEM ARCHITECTURE MANIFESTO (2026 Edition)
**PROJECT**: Google Antigravity (Monorepo: Python Backend + Flutter Client)
**STATUS**: Phase 2 (Hardening & Standardization)

---

## 🛑 PRE-FLIGHT CHECKLIST (MANDATORY)

### 1. Dependency Strategy (Latest Stable Mandate)
The dependencies listed below serve as the **MINIMUM BASELINE**.
**ALWAYS** use the latest stable compatible versions available.
**DO NOT** restrict upgrades unless a specific breaking change is identified.

#### Backend (Python)
| Package | Baseline Version | Purpose |
| :--- | :--- | :--- |
| `fastapi` | `0.128.0+` | Core Framework |
| `uvicorn` | `0.40.0+` | ASGI Server |
| `pydantic` | `2.12.5+` | Data Validation (V2) |
| `firebase-admin` | `7.1.0+` | Auth & Firestore |
| `openai` | `2.16.0+` | LLM Client |
| `litellm` | `1.81.3+` | LLM Proxy |
| `sse-starlette` | `3.2.0+` | Real-time Events |
| `arq` | `0.26.3+` | Async Task Queue |
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

#### Backend (Python)
*   **Lint**: `ruff check . --fix` (Enforce style & fix imports)
*   **Type Check**: `mypy .` (Strict typing, no `Any` leaks)

#### Frontend (Flutter)
*   **Analyze**: `flutter analyze` (Standard linting)
*   **Custom Lint**: `dart run custom_lint` (Riverpod rules)
*   **Code Gen**: `dart run build_runner build -d` (Ensure synced generated files)

---

## 🏛️ PART 1: DYNAMIC ARCHITECTURE & SCALING

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
    *   **BANNED**: `str(datetime.now())` or manual `.isoformat()`.
    *   **Timezone**: Always use `UTC` (`datetime.now(timezone.utc)`).

3.  **Logging (Unified Format)**:
    *   **Format**: `%(asctime)s | %(levelname)s | [%(execution_id)s] | ...`
    *   **Context**: `execution_id` must be present for traceability.

---

## ⚠️ PART 3: ERROR HANDLING CONTRACT (RFC 7807)

**SINGLE SOURCE OF TRUTH**: `backend/exceptions.py`

1.  **Protocol**: All errors MUST follow RFC 7807 Problem Details.
2.  **Implementation**:
    *   Log: `logger.error(..., exc_info=True)`
    *   Raise: `AppException` (Never `HTTPException` directly).

---

## 💙 PART 4: FLUTTER CLIENT MANDATES

1.  **State (Riverpod 3.0)**:
    *   **Generator Only**: `@riverpod` syntax.
    *   **Declarative**: `ref.watch`. No manual subscriptions.
    *   **AsyncValue**: Use `.when()` for UI states.
    *   **Pattern**: "Engine vs Driver" (Controller = AsyncNotifier, Data = StreamProvider).

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

1.  **Repository Parity Mandate**:
    *   **Dual Repos**: `firestore_repo.py` (Truth) and `repository.py` (Dev) MUST be strictly synchronized.
    *   **Feature Parity**: Any method added to one MUST be added to the other.

2.  **Seeding Authority**:
    *   **Master Seed**: `backend/seed/seed_data.json` is the authoritative baseline.
    *   **Logic**: `backend/seed/run_seed.py` creates the state. **DO NOT MODIFY** seed data structure without approval.

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

    *   **History**: On 2026-01-16, critical methods were deleted.

3.  **Debugging Protocols ("Silent Console, Verbose Log")**:
    *   **Console Output**: Terminals (`run_local.bat` windows) MUST remain minimal. Only print "Starting..." and "Check logs".
    *   **Source of Truth**: All debug data (Setup Config, Requests, Errors, State) MUST flow to:
        *   `backend_debug.log` (Python)
        *   `client_debug.log` (Flutter)
    *   **Agent Instruction**: If a user reports an error, **ALWAYS** read these two files first (`view_file`). Do not ask the user for console output.

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
    *   **Backend**: `backend/l10n` (Standard translation files).

2.  **Mandates**:
    *   **Separation**: Frontend and Backend maintain separate, independent localization trees.
    *   **Hardcoding**: STRICTLY BANNED. All user-facing strings must use the localization keys.
    *   **Parity**: Keys should be added to both English (`en`) and Finnish (`fi`) files immediately.