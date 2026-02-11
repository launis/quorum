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

When defining Domain Models that accept free-text input from LLMs (which may be in Finnish or English) but require standardized numeric or boolean values for logic, follow this **Validation Pattern**:

1.  **Dual Fields**: Define one field for the **Raw Input** (String) and one for the **Standardized Value** (Float/Bool).
2.  **Validator**: Use a `@model_validator(mode="after")` to map the Raw Input to the Standardized Value using `_map_l10n_values`.

### Implementation Template

```python
def _map_l10n_values(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Helper to create a mapping from (TranslatedKey -> Value) for all supported languages."""
    mapping = {}
    for key, val in pairs:
        # Add English (Fallbacks)
        mapping[LocalizationService.translate(key, "en")] = val
        # Add Finnish (Primary)
        mapping[LocalizationService.translate(key, "fi")] = val
        # Add Raw Key (Failsafe)
        mapping[key] = val
    return mapping

class RiskAssessment(BaseModel):
    # 1. Raw Input (LLM generates this, potentially in Finnish)
    risk_level: str = Field(..., description="Risk level (Low/Medium/High).")
    
    # 2. Standardized Value (Logic uses this)
    risk_score: float = Field(default=0.0, description="Numeric score (1.0-3.0).")

    @model_validator(mode="after")
    def calculate_score(self, info: ValidationInfo) -> 'RiskAssessment':
        # 3. Define Mapping (Key -> Standard Value)
        mapping = _map_l10n_values([
            ("Risk.Low", 1.0),
            ("Risk.Medium", 2.0),
            ("Risk.High", 3.0)
        ])
            
        # 4. Fuzzy Match Logic
        if self.risk_score == 0.0 and self.risk_level:
            for k, v in mapping.items():
                if k.lower() in self.risk_level.lower():
                    self.risk_score = v
                    break
        return self
```

### Key Principles
*   **Resilience**: logic works regardless of whether the LLM outputs "High Risk" (EN) or "Korkea Riski" (FI).
*   **SSOT**: The `l10n/*.json` files remain the single source of truth for the string values.
*   **Failsafe**: If exact match fails, fuzzy matching (`in`) ensures robustness against minor LLM variations.

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

### 15.2. Specialist Data Interchange Protocols (Wrapped vs. Unwrapped)
The system supports two distinct data formats for Specialist Agents, and the BFF Layer **MUST** support both.

1.  **Wrapped Format (Standard Agents)**:
    *   **Source**: Standalone Agents (e.g., `step_logician`, `step_falsifier`).
    *   **Structure**: `{ "logician_data": { "compliance_score": ... } }`
    *   **Reason**: Matches the `LogicianOutput` Pydantic model structure.

2.  **Unwrapped Format (Panel Agent)**:
    *   **Source**: The Consolidated Panel Agent (`step_panel`).
    *   **Structure**: `{ "compliance_score": ... }` (The inner data directly).
    *   **Reason**: The Panel Agent aggregates multiple outputs, and inside its own structure, the fields are already named (e.g., `panel.logician_data`). When extracted, it looks like raw data.

### 15.3. Transformer Implementation Pattern
When implementing `_transform_*` methods in `bff_transformer.py`, follow this **Robustness Pattern**:

```python
def _transform_specialist_data(self, data: dict) -> dict:
    # 1. Try Wrapped (Standard)
    if "specialist_data" in data:
        return data["specialist_data"].copy()

    # 2. Try Unwrapped (Panel/Direct)
    if data and isinstance(data, dict):
        return data.copy()

    # 3. Fail Safe (UI robustness)
    logger.warning("Specialist Data missing/invalid. Returning empty dict.")
    return {}
```