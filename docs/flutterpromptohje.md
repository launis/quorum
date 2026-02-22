# **SYSTEM ARCHITECTURE MANIFESTO (2026 Edition)**

**PROJECT**: Google Antigravity (Monorepo: Python Backend \+ Flutter Client)

**STATUS**: Phase 2 (Hardening & Standardization)

## ---

**🛑 PART 0: PRE-FLIGHT CHECKLIST (MANDATORY)**

### **0.1. Dependency Strategy (Latest Stable Mandate)**

The dependencies listed below serve as the **MINIMUM BASELINE**.

**ALWAYS** use the latest stable compatible versions available.

**DO NOT** restrict upgrades unless a specific breaking change is identified.

#### **Backend (Python 3.14.2+ & FastAPI 0.128+)**

* **Enabled Features**: 
  * Leveraging Python 3.14's deferred evaluation (`from __future__ import annotations`), native `ExceptionGroup` handling, and advanced structural pattern matching (`match/case`) for complex domain routing.
  * Extensively utilizing **FastAPI 0.128+ annotations**: You MUST use `Annotated[T, Depends()]` for all Dependency Injections to guarantee strict IDE type-hinting and cleaner swagger generation. Do not use the legacy `param: T = Depends()` syntax.

| Package | Baseline Version | Purpose |
| :---- | :---- | :---- |
| fastapi | 0.128.0+ | Core Framework |
| uvicorn | 0.40.0+ | ASGI Server |
| pydantic | 2.12.5+ | Data Validation (V2) |
| firebase-admin | 7.1.0+ | Auth & Firestore |
| openai | 1.60.0+ | LLM Client |
| litellm | 1.81.3+ | LLM Proxy |
| tenacity | 9.1.2+ | Retry Logic |
| tiktoken | 0.12.0+ | Token Counting |

#### **Frontend (Flutter)**

* **Enabled Features**: Dart 3.11 for true background concurrency (`Isolate.run`), explicit Records/Tuples `()`, and advanced Pattern Matching `switch()`. Riverpod 3.10 strictly enforces `Notifier` architecture replacing legacy state providers. GoRouter 17.1+ demands `GoRouteData` absolutely for Type-Safe routes.

| Package | Baseline Version | Purpose |
| :---- | :---- | :---- |
| flutter\_riverpod | ^3.1.0 | State Management |
| flutter\_hooks | ^0.21.0 | Widget Lifecycle |
| go\_router | ^17.0.1+ | Routing |
| dio | ^5.7.0 | Networking |
| firebase\_auth | ^6.1.4 | Authentication |
| freezed | ^3.2.3 | Immutable Models |
| flutter\_markdown\_plus | ^1.0.7 | Markdown Rendering |
| riverpod\_annotation | ^4.0.0 | Code Gen Annotations |
| riverpod\_generator | ^4.0.0 | Riverpod Code Gen |
| custom\_lint | ^0.8.1 | Linting Standards |
| riverpod\_lint | ^3.1.0 | Riverpod Lints |
| json\_serializable | 6.11.2 | Serialization (PINNED core conflict) |

### **0.2. Modern Standards Enforcement (Banned Patterns)**

The versions listed above enable specific **Modern Architectures**.

Using these versions with "Legacy Patterns" is a **STRICT VIOLATION**.

| Area | Modern Requirement (MANDATORY) | Legacy Pattern (BANNED) |
| :---- | :---- | :---- |
| **State** | Use @riverpod (Generator) \+ ref.watch | ChangeNotifier, StateProvider, manual Provider |
| **Routing** | Use GoRouteData (Type-safe classes) | Raw strings: context.push('/home') |
| **API** | Use Annotated\[Dep, Depends()\] | params: Dep \= Depends() (Old syntax) |
| **Models** | Use model\_validate, model\_dump | .parse\_obj(), .dict() |
| **Hooks** | Use HookConsumerWidget \+ useEffect | StatefulWidget \+ initState/dispose |
| **Data** | Use @freezed (Immutable Unions) | Mutable classes or plain json\_serializable |
| **Retries** | Use @retry (Tenacity) decorators | while loops with sleep() |
| **AI** | Use AsyncOpenAI() (Instantiated Client) | Global openai.ChatCompletion.create() |
| **Auth** | Use authStateChanges() (Reactive Stream) | Manual currentUser checks / setState |
| **HTTP** | Use Interceptors for Auth/Error handling | Inline try/catch or token injection |

### **0.3. Routine Quality Gates (Definition of Done)**

**ALWAYS** run these checks before marking a task as complete.

* **Process \- Root Cause Analysis**: Did I find *why* the error happened upstream, or did I just patch the symptom? (Review Section 18.4)  
* **Backend (Python)**: ruff check . \--fix (Lint & enforce style) AND mypy . (Strict typing, no Any leaks).  
* **Frontend (Flutter)**: dart run custom\_lint (Riverpod rules) AND dart run build\_runner build \-d (Ensure synced generated files).  
* **Cleanup Safety (Crucial)**: Before removing "unused" imports or functions, search the codebase (via IDE global search) to ensure they aren't used in dynamic lookups, legacy routes, or Dependency Injection configurations.

## ---

**🏛️ PART 1: DYNAMIC ARCHITECTURE & SCALING**

### **1.1. Single Source of Truth (SSOT) & Wiring**

**CRITICAL ARCHITECTURAL MANDATE:**

The seed\_data.json file MUST adhere to the **Single Source of Truth (SSOT)** principle for step definitions.

* **The Registry (steps array):** This is the **CONTRACT**. It defines WHAT a step is (Task Key, Model Config, System Prompt). It lives in the top-level steps list.  
* **The Workflow (workflows array):** This is the **WIRING**. It defines HOW a step is used (Input Data Flow). It lives in the workflows list and must **ONLY** reference steps by id.

**❌ FORBIDDEN (Inline Definition in Workflow):**

JSON

// DO NOT DO THIS inside a workflow\!  
{  
  "id": "step\_analyst",  
  "task\_key": "backend.agents.step\_analyst.analyst\_step", // ❌ REDUNDANT (Violates SSOT)  
  "config": { "model": "gpt-4" }, // ❌ REDUNDANT  
  "inputs": { "history\_text": "$history\_text" }  
}

**✅ REQUIRED (Reference by ID):**

JSON

// DO THIS inside a workflow:  
{  
  "id": "step\_analyst", // ✅ REFERENCES Registry Contract  
  "inputs": {  
    "history\_text": "$history\_text", // ✅ WIRING ONLY  
    "product\_text": "$product\_text"  
  }  
}

### **1.2. Architectural Principles**

1. **Philosophy: "Schema is King" (Contract-First)**:  
   * **Single Source of Truth**: Pydantic V2 models drive everything.  
   * **Auto-Gen**: API Specs and Frontend Entities must be generated from Pydantic models. No manual duplication.  
2. **Backend: The Generic Engine**:  
   * **BANNED**: Hardcoded step logic (e.g., if step \== 'guard').  
   * **REQUIRED**: Metadata-Driven execution via Task Registry.  
   * **Zero-Fallback**: System must fail fast if DB configuration is missing. No hardcoded prompts or model names in code.  
3. **AI Layer: Reliability**:  
   * **Tooling**: Use **LiteLLM Native Structured Output** (response\_format).  
   * **Strict Mode**: Agents must return Pydantic models. dict returns are FORBIDDEN.  
   * **Self-Correction**: Pipeline must catch validation errors and feed them back to LLM.  
4. **Frontend: Hybrid Server-Driven UI (SDUI)**:  
   * **Default**: Use generic DynamicFormWidget based on UI\_Schema.  
   * **Constraint**: Hardcoding *forms* is banned, but hardcoding *components* mapping to schema fields is allowed for UX fidelity.

## ---

**🐍 PART 2: PYTHON BACKEND MANDATES**

### **2.1. Framework (FastAPI 0.128+)**

* **Lifespan (ASGI)**: Always use the modern `async contextmanager` for application startup and shutdown events (`lifespan=...`). The legacy `@app.on_event("startup")` approach is BANNED.
* **Dependency Injection (Annotated)**: Strict mandate to use `Annotated[DependencyType, Depends()]`. This ensures Pydantic V2 schemas generate flawlessly and Type Checkers (`mypy`) can explicitly trace injection dependencies.
* **Concurrency**: I/O routes reading asynchronous sources MUST be `async def`. However, routes accessing purely synchronous blocking drivers (like `TinyDBDriver`) MUST be defined as basic `def`, forcing FastAPI to safely execute them in a background threadpool to prevent Event Loop freezing!

### **2.2. Date Handling (Temporal Standard)**

* **Storage**: Store as datetime. Repository handles DB-specifics.  
* **Serialization**: ALWAYS use .isoformat() for JSON output (e.g., 2026-02-07T...).  
* **BANNED**: str(datetime.now()) (undefined format) or json.dumps() on datetime objects without a custom default handler.  
* **Timezone**: Always use UTC (datetime.now(timezone.utc)).

### **2.3. Logging (Unified Format)**

* **Format**: %(asctime)s | %(levelname)s | \[%(execution\_id)s\] | ...  
* **Context**: execution\_id must be present for traceability.

### **2.4. Data Passing Mandate (No Dictionaries)**

* **The Rule**: All internal data exchange between Services, Hooks, and Agents MUST use Pydantic Models.  
* **BANNED**: Passing dict or dict\[str, Any\] as a return value or argument for structured data.  
* **EXCEPTION**:  
  1. Raw JSON payloads at the **API Boundary** (e.g., request.json()).  
  2. Low-level **Database Drivers**.  
  3. UI Composites generated in the **BFF Layer** for rendering (See Part 15).  
* **Philosophy**: "If it has a shape, it must be a Model. Dictionaries are for unordered maps only."

### **2.5. Strict Pydantic Validation (Fail Fast)**

* **The Rule**: ALL Domain Models MUST use ConfigDict(strict=True).  
* **Implication**: No implicit type coercion (e.g., string "1" \-\> int 1 is forbidden).  
* **Why**: Data integrity is paramount. If the type is wrong, the upstream data source is broken and must be fixed.

### **2.6. API Boundary & Data Contracts (Schema-First)**

* **Requests**: body MUST be a Pydantic Model. Using dict or Request to bypass validation is BANNED.  
* **Responses**: MUST define response\_model in the route decorator. Return the Pydantic Model instance directly (let FastAPI handle serialization).  
* **Null Safety (Pydantic 2.12)**: API Responses should NOT contain null for list fields. Use `Field(default_factory=list)` directly in Pydantic V2 definitions to guarantee empty array structures robustly, avoiding manual try-catches.

### **2.7. Agent Output Authority (Python-Side Healing)**

* **The Problem**: LLMs are non-deterministic (Math errors, random sorting, hallucinations).
* **The Solution**: The `BaseAgent.post_process()` method is the **Python Authority Layer**.
* **Mandate**:
    *   **Math**: NEVER trust LLM calculations. Recalculate scores in `post_process`.
    *   **Sorting**: NEVER trust LLM ordering. Sort lists deterministically in `post_process`.
    *   **Deduplication**: NEVER trust LLM uniqueness. Deduplicate lists in `post_process`.
    *   **Structure**: Enforce IDs and strict types in `post_process`.

### **2.8. No-ORM Pydantic Datastore Mandate**

* **The Rule**: The project uses **100% Pydantic V2** as the Absolute Single Source of Truth (SSOT). Using traditional Object-Relational Mappers (ORMs) like SQLAlchemy, Prisma, or Django ORM is **STRICTLY FORBIDDEN**.
* **Implication**: Any new database field, configuration option, or API parameter MUST be defined exclusively as a field in a Pydantic model inside `backend/models/`.
* **Symbiosis**: Because the database layer relies on NoSQL document stores (TinyDB / Firestore), Pydantic's `model_dump()` directly translates to the database schema. Adding a new field to a Pydantic model automatically ensures the Seeder (`run_seed.py`), API Router, and Database recognize it instantly—without requiring schema migration scripts.

## ---

**⚠️ PART 3: ERROR HANDLING CONTRACT (RFC 7807 & FAIL FAST)**

> [!CRITICAL]
> **THE ZERO-LAZINESS MANDATE (FOR AI AGENTS & DEVELOPERS)**
> LLM Agents frequently become "lazy", skip steps, or fail to modernize existing error handlers when updating files. **THIS IS UNACCEPTABLE.** 
> * **NO SHORTCUTS**: Whenever you create OR update a module, you MUST fully refactor ANY existing naked `ValueError`, `raise Exception`, or simple `HTTPException` into the complete structured `AppException` pattern defined below. 
> * **100% COMPLIANCE**: You are not allowed to say "the scope was too large", to leave generic `except Exception as e: raise e`, or to skip applying `ErrorCodes` enums.
> * If a user asks you to "update error handling," you MUST read and follow THIS ENTIRE SECTION down to the exact syntax and localization requirements.

**SINGLE SOURCE OF TRUTH**: backend/exceptions.py

### **3.1. The Protocol (RFC 7807\)**

All errors MUST follow the RFC 7807 Problem Details standard. The AppException class is the canonical implementation.

### **3.2. Mandatory Fields**

When raising an exception, you must provide:

1. **message**: A technical English description for logs (NEVER shown to user).  
   * **⚠️ SECURITY WARNING**: Do NOT inject sensitive information (like API keys, raw database queries, or PII) into the `message` string! While the UI should not display this string, the RFC 7807 `detail` field (which Maps to `message`) is often returned to the client in the HTTP response.
2. **status\_code**: The appropriate HTTP status code (e.g., 400, 404, 500). Produced via ENUM.  
3. **details**: A dictionary containing at least an error\_code from backend.exceptions.ErrorCodes. This error\_code is automatically promoted to extensions.error\_code in the final JSON response.

### **3.3. Implementation Pattern (Fail Fast Domain Logic)**

**REFERENCE:** See **Section 18.1** for the strict "Zero-Compromise" rules regarding Fail Fast and Data Integrity.

> [!WARNING]
> **BOILERPLATE ALERT & COPY-PASTE RISKS (For AI and Human Developers)**
> The following 5-6 line `try...except` block pattern is intentionally verbose to enforce strictness and traceability. This is the price paid for clarity.
> When copying this pattern:
> 1. **Change the `[Component]` tag** in the logger to exactly match your current module (e.g., `[ReportTransformer]`, `[JudgeAgent]`). Don't leave old names!
> 2. **Update the `ErrorCodes` enum** to the correctly matching scenario. Do not reuse generic codes if a specific one exists.
> 3. **DO NOT use shortcuts.** Writing simply `raise e` or skipping the structured `AppException` is **STRICTLY FORBIDDEN**, especially when tired, as it permanently breaks the RFC 7807 contract and UI localization mapping.
> 4. **DUAL-REPORTING MANDATE**: Every single error that is caught and re-raised (or newly raised) MUST be explicitly printed to the server logs (e.g., `logger.error(...)`) IN ADDITION to raising the exception. You cannot just raise the exception, and you cannot just log it. Both must happen together.

**The Code Pattern:**
When correctly identified (per Section 18.1), raises must be structured as follows:

```python
    # 1. Enforce Data Integrity (See Rule 18.1.1)
    if not execution.completed_at and execution.status == "completed":
        raise ValueError(f"Execution {execution.id} is completed but missing timestamp.")

    try:
        # 2. Strict Type Conversion
        result = some_operation()
    except pydantic.ValidationError as e:  
        from backend.exceptions import AppException, ErrorCodes, status

        # 3. Define Error Code (SSOT)  
        error_code = ErrorCodes.VALIDATION_FAILED

        # 4. Log with STRUCTURED FORMAT  
        logger.error(f"[AgentEngine] {error_code.name}: Output validation failed: {e}", exc_info=True)

        # 5. Raise explicit AppException wrapping the original error  
        raise AppException(  
            message=f"Agent output validation failed: {e}",  
            status_code=status.HTTP_400_BAD_REQUEST,  
            details={  
                "error_code": error_code.value,   
                "original_error": str(e) # Context for debugging  
            },  
        ) from e
```


### **3.4. Localizing Error Codes (Frontend Responsibility)**

**THE CONTRACT (Split Responsibility):**

* **Backend**: Sends the machine-readable code (e.g., VALIDATION\_FAILED) and technical details (English).  
* **Frontend**: Maps the **Code** to a human-readable Title via app\_\*.arb.

#### **Step 1: Define Key in ARB Config (Actionable Hints Mandate)**

**THE HINT RULE**: Never provide end-users with generic, dead-end error messages like "Server Error". The translated string MUST contextualize the failure and offer a clear "Next Step" or "Hint" for the user. Since the specific technical reason (e.g., `Timeout` or `KeyError`) is kept hidden in the logs, the UI message must guide the user on how to recover or what just failed broadly.

JSON

// client\_app/lib/l10n/app\_fi.arb  
{  
  "errValidationFailed": "Tietojen validointi epäonnistui. Varmista, että kaikki vaaditut kentät on täytetty oikein ja yritä tallentaa uudelleen.",  
  "errInternalServerError": "Järjestelmässä tapahtui odottamaton virhe. Toimintoa ei voitu suorittaa loppuun. Yritä päivittää sivu hetken kuluttua uudelleen."  
}

#### **Step 2: Map Code to Key (Dart)**

Use the AppErrorExt extension in client\_app/lib/core/error/app\_error\_ext.dart.

Dart

// client\_app/lib/core/error/app\_error\_ext.dart  
  static String \_localizeErrorCode(String errorCode, AppLocalizations l10n) {  
    return switch (errorCode) {  
      'VALIDATION\_FAILED' \=\> l10n.errValidationFailed,  
      'INTERNAL\_SERVER\_ERROR' \=\> l10n.errInternalServerError,  
      \_ \=\> l10n.errorUnknown,  
    };  
  }

### **3.5. Specialized Exceptions (Domain Semantic)**

Do not use raw AppException if a more specific semantic wrapper exists. These wrappers auto-inject status codes and preserve execution context.

| Exception Class | Usage Scenario | Required Arguments |
| :---- | :---- | :---- |
| **ResourceNotFoundError** | When a DB item is missing (404) | resource\_type, resource\_id |
| **ConfigurationError** | Missing API keys or bad config (500) | message |
| **AgentExecutionError** | Agent logic failure (500) | error\_code, original\_error, agent\_name |
| **WorkflowExecutionError** | Step Engine failure (500) | step\_id, task\_key, original\_error |

#### **Example: Semantic Agent Failure**

Python

    if not input_data.target_text:
        # FAIL FAST: Do not attempt to process empty input
        raise AgentExecutionError(
            detail=ErrorCodes.EMPTY_INPUT,
            original_error=ValueError("Target text is missing."),
            agent_name="Logician"
        )


### **3.6. Managed Fallbacks (BFF Boundary Exception)**

**DEFAULT RULE**: Raise an Exception (Fail Fast).

**USAGE FREQUENCY: RARE (\< 5% of cases)**

Only use the "Managed Fallback" pattern (returning {} or empty data) in the **View/BFF (Backend-For-Frontend) Layer** when isolating a UI failure is strictly necessary.

* **Core Logic/Data Integrity**: ❌ NEVER (Must Fail Fast).  
* **Critical UI**: ❌ NEVER (User must know it failed).  
* **Composite Dashboard Widgets**: ✅ ALLOWED (One broken chart shouldn't blank the entire screen. See Part 15.1).

### **3.7. Unified Client Error Presentation**

**THE MANDATE:** All client-side errors MUST be displayed using the standardized ErrorView widget. Banned: Ad-hoc implementations like Center(child: Text('Error')).

### **3.8. Upstream Error Mapping (Vendor Failures)**

**THE MANDATE:** Never expose raw Vendor/Upstream errors (e.g., googleapiclient.errors.HttpError) to the user. You MUST catch known upstream errors and map them to semantic AppException types with **Actionable Instructions**.

## ---

**💙 PART 4: FLUTTER CLIENT MANDATES**

### **4.1. State (Riverpod 3.0 & Optimistic Updates)**

* **Generator Only**: @riverpod syntax.  
* **Declarative**: ref.watch. No manual subscriptions.  
* **AsyncValue**: Use .when() for UI states.  
* **Mandate**: Mutations MUST use the "Optimistic Update \+ Silent Sync \+ Rollback" pattern:  
  Dart  
  Future\<void\> addItem(Item item) async {  
    final previousState \= state.valueOrNull;  
    if (previousState \== null) return;

    // 1\. Optimistic Update  
    state \= AsyncData(\[...previousState, item\]);  
    try {  
      // 2\. API Call  
      await ref.read(repoProvider).addItem(item);  
      // 3\. Silent Sync  
      ref.invalidateSelf();  
    } catch (e) {  
      // 4\. Rollback  
      state \= AsyncData(previousState);  
      rethrow;  
    }  
  }

### **4.2. Routing (GoRouter)**

* **Type-Safe**: HomeRoute().go(context). No raw strings.  
* **Logic**: Guards belong in redirect, not build().

### **4.3. Network (Dio)**

* **Interceptors**: Centralized Auth & Error handling (RFC 7807 parsing).  
* **Background Tasks (Dart 3.11)**: Intensive API JSON parsing MUST happen off the main UI thread using modern `Isolate.run(...)`. The legacy `compute` function is deprecated.

### **4.4. UI/UX**

* **Theming**: FlexColorScheme. No manual ThemeData.  
* **Markdown**: Use flutter\_markdown\_plus (Strictly).  
* **Localization**: app\_en.arb is the Source of Truth.

## ---

**⏱️ PART 5: TIMEOUT & RELIABILITY STRATEGY**

### **5.1. Philosophy**

* "Fail Fast & Retry"  
* **Zombie Processes**: Forbidden. All external calls must have explicit timeouts.  
* **Retry**: Infrastructure (Tenacity/LiteLLM) handles retries, NOT the user.

### **5.2. Frontend Mandates**

* **Visualization**: Operations \> 10s must use Progress Bars (SSE).

## ---

**💾 PART 6: DATA ARCHITECTURE & SEEDING PROTOCOLS**

### **6.1. Repository Parity Mandate (Dual Backend)**

* **Strict Requirement**: ANY database modification MUST be implemented in BOTH backend/database/repository.py (TinyDB) AND backend/database/firestore\_repo.py (Firebase/Firestore). Maintain strict parity.

### **6.2. Hybrid State Architecture (Event Log vs Blackboard)**

* **Truth**: The TraceEvent log is the immutable history.  
* **Performance**: The WorkflowState.context\_variables (Blackboard) is the mutable current state.  
* **Mandate**: All steps MUST write to the Blackboard and emit an Event. Verification replays Events to rebuild State.

### **6.3. Seeding Authority**

* **Master Seed**: backend/seed/seed\_data.json is the authoritative baseline.  
* **Logic**: backend/seed/run\_seed.py creates the state. **DO NOT MODIFY** database tables manually to bypass seed rules.  
* **Derived Data (Ontology)**: The Seeder automatically extracts Dimension records from evaluation\_matrix components. Do not manually seed the dimensions table.

### **6.4. Root Cause Fix Mandate**

* **Principle**: Fix the source, don't patch the symptom.  
* **BANNED**: Copying data between tables to fix sync issues.  
* **REQUIRED**: Fix the reader to look at the correct source of truth.

## ---

**🎨 PART 7: UI & UX STANDARDS (2026 MANDATE)**

### **7.1. Responsive Layout**

* **Breakpoint**: 600dp (Mobile vs Desktop).  
* **Desktop**: Use NavigationRail \+ VerticalDivider. Max content width 1000dp.  
* **Mobile**: Use NavigationBar.

### **7.2. Localization Authority**

* **Source**: client\_app/lib/l10n/app\_\*.arb only.  
* **BANNED**: Hardcoded strings in widgets.  
* **Keys**: camelCase (dashboardTitle).

### **7.3. Preferences**

* **Scope**: Language (fi/en) & Theme (system/light/dark).  
* **Sync**: Immediate UI update (Riverpod) \+ Local Persist (`SharedPreferencesAsync` via modern concurrent API) \+ Remote Patch.

## ---

**🛠️ PART 8: ENVIRONMENT & TOOLING CONSTRAINTS**

### **8.1. Windows 11 / PowerShell**

* **Encoding**: Always specify encoding="utf-8" in Python scripts.  
* **Pathing**: Use raw strings r"c:\\path" or pathlib.  
* **Code Search**: Unix commands like grep are not universally reliable here. Use IDE global search or python analysis scripts.

### **8.2. Repository Method Protection**

* **History**: On 2026-01-16, critical methods were deleted. Protect core methods and review deletions carefully.

### **8.3. Debugging Protocols ("Silent Console, Verbose Log")**

* **Console Output**: Terminals (run\_local.bat) MUST remain minimal. Only print "Starting..." and "Check logs".  
* **Source of Truth**: All debug data flows to backend\_debug.log and client\_debug.log.  
* **Agent Instruction**: If a user reports an error, **ALWAYS** read these files first (view\_file). Do not ask the user for console output.

### **8.4. Logic Integrity Mandate (workflow-step-logic)**

* **Scope**: This includes seed\_data.json structure, GraphEngine execution flow, and Agent PRODUCES\_KEYS / REQUIRES\_KEYS.  
* **Reasoning**: "Fix the component, do not re-route the pipeline."  
* **Exception**: Only bug fixes that restore documented behavior are allowed, but must be explicitly noted.

### **8.5. Architectural Integrity (Zero-Shortcut Policy)**

* **Mandate**: NEVER bypass established services (e.g., StorageService, LocalizationService) for direct I/O or "quick fixes".  
* **Prohibition**: Ad-hoc implementations (including "temporary" file reads) are STRICTLY FORBIDDEN.

## ---

**🗺️ PART 9: KNOWLEDGE BASE MAP (DEEP DIVES)**

For detailed implementation logic, refer to these Knowledge Items:

1. **Backend & AI**: knowledge/backend\_system\_architecture, knowledge/workflow\_orchestration\_and\_reliability, knowledge/seeding\_and\_data\_lifecycle  
2. **Frontend**: knowledge/client\_application\_development, knowledge/hybrid\_sdui\_strategy, knowledge/identity\_and\_access\_management  
3. **Environment**: knowledge/development\_environment\_modernization

## ---

**🌍 PART 10: INTERNATIONALIZATION (I18N) STANDARDS**

### **10.1. Dual Sovereign Locations**

* **Frontend**: client\_app/lib/l10n (Standard .arb files).  
* **Backend**: backend/l10n (JSON files en.json, fi.json).  
* **Execution**: Context Language is auto-detected via ContextVar (from Accept-Language headers). Do NOT pass lang explicitly.

### **10.2. Backend Localization Scope (Strict Rule)**

* **Usage Scope**: The backend LocalizationService.translate is STRICTLY reserved for Server-Side Rendering (e.g., generating PDFs or prompt injections).  
* **API Payload Ban**: The backend must NEVER send translated "System Labels" or UI texts to the UI via the API. All UI-bound logic must use Enum Keys (See Part 16).
* **EXCEPTION (Dynamic LLM Content)**: Text natively generated by the LLM in the user's language (e.g., localized essays, dynamic reports) is treated as raw data payloads, not System Labels, and thus freely traverses the API boundaries.

### **10.3. Interpolation Security & Formatting**

* **BANNED**: Backend must NEVER format strings for UI (e.g., `"Welcome, " + user.name`). This breaks language-specific grammar and structure.
* **REQUIRED**: Backend sends raw variables `{ "event": "WELCOME", "user": "Matti" }`. Frontend `.arb` handles the interpolation using ICU format (e.g., `"welcomeUser": "Tervetuloa, {user}!"`).

### **10.4. Pluralization & Grammar**

* **BANNED**: Manual `if/else` checks for plurals in Dart code (e.g., `if (count == 1)`). This will break completely when localizing to languages with complex plural rules (e.g., Arabic, Polish).
* **REQUIRED**: Use Flutter's native ICU Plural support exclusively inside `.arb` files (e.g., `"{count, plural, =0{Ei tuotteita} =1{1 Tuote} other{ {count} Tuotetta}}"`).

### **10.5. Semantic Markup (Markdown)**

* **The Rule**: Do not bake UI visual styles (`TextStyle`, `<b>` elements) around partial translations.
* **Implementation**: The `.arb` file should use lightweight markdown tokens (e.g., `"pressButton": "Paina **Tallenna**-nappia"`), and the UI must parse these using `flutter_markdown_plus` or rich text extensions to preserve translation coherence.

## ---

**🖥️ PART 11: HYBRID SERVER-DRIVEN UI (SDUI) STANDARDS**

### **11.1. Philosophy**

* "Schema defines Data, Frontend defines Experience".

### **11.2. Hybrid Implementation**

* **Default**: Use generic DynamicFormWidget based on UI\_Schema.  
* **Premium Override**: Frontend MAY implement custom, high-fidelity Widgets (e.g., Drag & Drop) for specific steps, provided they output the exact data structure required by the Schema.  
* **Constraint**: Hardcoding *forms* is banned, but hardcoding *components* that map to schema fields is allowed for UX.

## ---

**⚙️ PART 12: BACKEND LOCALIZATION PATTERNS (DOMAIN STANDARDIZATION)**

When defining Domain Models that accept free-text input from LLMs (which may be in FI/EN) but require standardized numeric values for logic, follow the **Enum Code Pattern**.

To comply with the strict "No Default Values" rule (Part 18.2), do NOT use fake initial numbers (0.0). Instead, use Pydantic V2 @computed\_field to calculate the value strictly based on the Enum constraint.

### **12.1. Implementation Template (Computed Field)**

Python

from enum import Enum  
from pydantic import BaseModel, Field, computed\_field

class RiskLevel(str, Enum):  
    LOW \= "RISK\_LOW"  
    MEDIUM \= "RISK\_MEDIUM"  
    HIGH \= "RISK\_HIGH"

class RiskAssessment(BaseModel):  
    \# 1\. Enum Code (LLM outputs this specific string deterministically)  
    risk\_code: RiskLevel \= Field(..., description="Risk level code (RISK\_LOW, RISK\_MEDIUM, RISK\_HIGH).")  
      
    \# 2\. Standardized Value (Calculated safely, NO explicit default values needed)  
    @computed\_field  
    def risk\_score(self) \-\> float:  
        mapping \= {  
            RiskLevel.LOW: 1.0,  
            RiskLevel.MEDIUM: 2.0,  
            RiskLevel.HIGH: 3.0  
        }  
        \# Fail Fast: If risk\_code is somehow invalid, crash immediately.  
        return mapping\[self.risk\_code\]

### **12.2. Key Principles**

* **Determinism**: LLM is instructed to output exact codes (RISK\_HIGH).  
* **SSOT**: The Enum definition is the single source of truth.  
* **Fail Fast**: If LLM outputs an invalid code, Pydantic validation fails immediately.

## ---

**🏗️ PART 13: STUDIO & BUILDER LOCALIZATION SAFETY**

The **Cognitive Studio** (Workflow Builder) operates in **Raw Mode**. It interacts directly with the seed\_data.json / Registry structure key-values.

### **13.1. The Hazard**

* **What you see**: Inputs labeled History Text, Product Text.  
* **What they are**: These are **Translation Keys** (lookups), NOT English defaults.  
* **The Risk**: If an Administrator renames History Text to Historiateksti in the Studio UI, the **Key** in the database becomes Historiateksti. The Backend translation lookup breaks, and English users will see "Historiateksti".

### **13.2. The Rule**

**"Edit Values, Never Keys"**

* **Allowed**: Changing numerical weights, thresholds, prompts.  
* **Forbidden**: Renaming generic UI labels in the Builder Config. The Studio is for **Assembly**, not **Copywriting**.

## ---

**🧩 PART 14: LOGIC & VALIDATION MANDATES (STRICT SCALE)**

When implementing AI steps that must output specific numeric values (e.g., Scores 1-100 or 1-5), you must follow the **"Fail Fast & Explicit"** pattern.

### **14.1. The Hazard**

* **Silent Failure**: The AI outputs 0 or 101 when the scale is 1-100.  
* **Soft Fail**: Code clamps the value (max(1, min(100, val))). Valid-looking data is actually hallucinated.

### **14.2. The Solution (Fail Fast)**

* **Code**: If a value is out of bounds, **CRASH** the step immediately (raise ValueError). Do not fix it silently. This forces the Prompt Engineer to fix the instruction.

### **14.3. The Instruction (Explicit Prompting)**

* **Pattern**: Define the strict rule in seed\_data.json (e.g., INSTRUCTION\_STRICT\_SCALE) and inject it into the llm\_prompts list of the Agent. Do NOT hardcode the prompt text in Python.

## ---

**🧬 PART 15: STRICT TYPING & SPECIALIST DATA (BFF MANDATE)**

### **15.1. UiSection Contract & BFF Resilience**

While the Core Domain MUST fail fast (Part 3.3, Part 14), the **BFF (Backend-for-Frontend) Transformer** layer has a different mandate: **UI Resilience** (as defined in Part 3.6).

* **Mandate**: The UiSection model strictly enforces data: dict\[str, Any\]. Passing None causes a 500 error for the *entire* screen.  
* **Solution**: In the BFF Transformer, always default to an empty dictionary {} if a specific agent's data is missing. This gracefully degrades that single widget while preserving the rest of the UI report.  
* **DEVELOPER VISIBILITY MANDATE (BFF & Flutter)**: Graceful degradation protects the end-user, but it MUST NOT hide bugs from developers. 
  * **In BFF (Python)**: If the BFF catches missing data, it MUST log a `logger.warning(...)`.
  * **In Frontend (Flutter)**: If a UI component catches an error or falls back to an `ErrorView` / `SizedBox.shrink()`, it MUST log a `debugPrint('🔴 UI GRACEFUL DEGRADATION: ...')` to the console.
  Python  
  \# BAD (Crashes entire page if logician\_data is None)  
  return UiSection(..., data=self.\_transform\_logician\_data(steps.get("step\_logician")))

  \# GOOD (Safe BFF Fallback for UI Compositing)  
  data \= self.\_transform\_logician\_data(...) or {}  
  return UiSection(..., data=data)

### **15.2. Specialist Data Interchange Protocols (Strict Nesting)**

* **Requirement**: All Agents MUST return data nested under their specific model key (e.g., { "logician\_data": { "toulmin\_score": ... } }).  
* **Forbidden**: Returning flattened data (e.g., { "toulmin\_score": ... }) at the root level. Legacy "flat" data is **NOT SUPPORTED**.

### **15.3. Transformer Implementation Pattern**

When implementing \_transform\_\* methods in bff\_transformer.py, follow this **Robustness Pattern**:

Python

    def \_transform\_specialist(self, raw\_step\_output: dict | None) \-\> dict:  
        if not raw\_step\_output:  
            return {} \# 1\. Fallback for entirely missing step  
              
        specialist\_data \= raw\_step\_output.get("specialist\_data")  
          
        if not specialist\_data:  
            \# 2\. Applying BFF Exception: Graceful UI Degradation  
            logger.warning("Specialist data missing. Returning empty dict.")  
            return {}  
              
        return specialist\_data

## ---

**🗣️ PART 16: STRICT LOCALIZATION & HELP TEXTS (ENUM/KEY MANDATE)**

### **16.1. The "No-String" API Policy**

* **Philosophy**: The Backend API supplies **DATA** (Scores, Result Codes). The Frontend supplies **PRESENTATION** (Labels, Help Texts).  
* **BANNED**: Sending localized strings or help text payloads from Python over the API (e.g., {"status": "Orgaaninen", "help": "..."}).  
* **REQUIRED**: Sending Immutable Keys or Enums (e.g., {"status": "AUTH\_ORGANIC"}).

### **16.2. Implementation Pattern (Enum-Driven & Dart Switch)**

Map the Backend Key to an .arb file translation immediately within the Flutter Widget logic. Riverpod handles the Locale natively.

Dart

// components/specialist\_section.dart  
Widget \_buildAuth(String key, BuildContext context) {  
  final l10n \= AppLocalizations.of(context)\!;  
    
  // 1\. Lookup Label via Dart 3 Switch  
  final label \= switch (key) {  
    'AUTH\_ORGANIC' \=\> l10n.authOrganic,  
    'AUTH\_PERFORMATIVE' \=\> l10n.authPerformative,  
    \_ \=\> l10n.authUnknown,  
  };  
    
  // 2\. Pass Resolved Strings to UI  
  return UnifiedMetricGauge(  
    label: label,  
    description: l10n.helpAuthenticity, // Resolves correctly per device language  
    // ...  
  );  
}

### **16.3. Help Text & Tooltips**

* **Storage**: All detailed help texts (paragraphs) MUST live in .arb files.  
* **Keys**: Use semantic keys like helpStrategicDepth.  
* **Usage**: Pass the *Result* of the lookup (l10n.helpStrategicDepth) to widgets, never the raw string.

## ---

**📝 PART 17: DOCUMENTATION & HYGIENE (STRICT MANDATE)**

### **17.1. Language Policy**

* **English ONLY**: All code, variable names, comments, commit messages, and docstrings MUST be in English.  
* **Exceptions**: Content in backend/l10n/fi.json or app\_fi.arb.

### **17.2. Python & Dart Docstrings (Imperative AI-Standard)**

* **Google Style (Python)**: EVERY public module, class, and method MUST have a docstring using Google Style formatting.
* **Triple Slash (Dart)**: Use `///` exclusively for all public Classes, Widgets, and Methods.
* **Imperative Mood**: Write function summaries as commands, not descriptions.
  * ❌ *BANNED*: "Returns the calculated score" or "This calculates the score."
  * ✅ *REQUIRED*: "Calculate the risk score based on the enum mapping."
* **Contract-Driven Comments (AI Compatibility)**: If a class or method contains an architectural workaround, an intentional strict-rule override, or complex constraint logic, you MUST start the docstring body with a bolded warning (e.g., `NOTE (Architecture): ...`). This prevents future developers or AI agents from "refactoring it broken" thinking it was an oversight.
* **Structured Deprecation**: If code is pending removal but active, it MUST use language-native decorators (`@deprecated` / `@Deprecated()`) AND the docstring MUST contain `Migrate to: [FunctionName]`.

### **17.3. Inline Comments (The "Why" Mandate)**

* **BANNED (Narrative "What")**: Inline comments that narrate what the code is doing (e.g., `# Loop through the items` or `// Increment counter`) are strictly forbidden. If the code requires narrative to be readable, you MUST refactor and rename the variables/functions (`Clean Code` principle).
* **REQUIRED (The "Why")**: Inline comments are reserved strictly for explaining non-obvious business logic, mathematical constants, or edge-case handling that cannot be expressed purely via naming.

### **17.4. Code Hygiene & Ownership**

* **No Dead Code**: Do NOT leave commented-out code blocks ("zombie code" or "just in case" logic). Delete them immediately. Version control is your history.
* **No Orphaned TODOs**: A `TODO` or `FIXME` comment MUST include an owner, ticket number, or specific date (e.g., `TODO(risto) [2026-03]: Remove after V2 rollout`). Floating TODOs are forbidden.
* **Clean Imports**: Unused imports must be removed (use `ruff check --fix` / `dart fix`).

## ---

**🛡️ PART 18: THE ZERO-COMPROMISE PLEDGE (QUALITY STANDARD)**

**"Production Quality, Day One."**

### **18.1. NO Fallback Code in Core Logic (Fail Fast Boundary)**

*   **The Rule**: In Core Engine, Database, and Domain logic, the system MUST raise an exception immediately on invalid state or missing dependencies.
*   **BANNED**: 
    *   `try-except pass` blocks.
    *   Returning `None` silently when data is expected.
    *   **Patching with empty values** (e.g., `knowledge_base = {}` or `return []`) to suppress errors. This "defensive programming" hides upstream bugs and makes debugging impossible.
*   **STRICT DATA INTEGRITY**:
    *   **Validate Fields**: If a record represents a completed state, all associated data (timestamps, results) MUST be present. Raise `ValueError` or `AppException` if missing.
    *   **Enforce Types**: Use `isinstance` checks if the data structure is ambiguous.
    *   **No Dict.get() Patches**: Do not use `.get('field', default)` to patch missing data that *should* be there.
*   **EXCEPTION**: Managed fallbacks (Graceful Degradation) are *only* permitted at the Presentation/BFF layer (See Part 3.6 & 15.1) to prevent whole-screen UI crashes.

### **18.2. NO Default Values (Strict Typing)**

* **The Rule**: Domain models MUST NOT have implicit default values for required fields.  
* **BANNED**: score: float = 0.0 or name: str = "Unknown".  
* **EXCEPTION**: Computed properties (@computed_field) or explicitly optional fields initialized to None (score: float | None = None).

### **18.3. NO Hardcoding (Configuration Sovereignty)**

* **The Rule**: Values that can change MUST exist in seed_data.json or l10n.
* **Infrastructure Mandate**: Infrastructure Wrappers (LLM Providers, DB Clients) MUST NOT inject default configuration values (e.g., `TPM=10000`) if the upstream configuration is missing. They MUST raise `ConfigurationError`.
* **BANNED**: Hardcoded prompts, magic numbers (if score > 0.5), defaults in Provider constructors, or UI strings in Python/Dart code. Extract "Magic Numbers" to Constants or Enums.

### **18.4. NO Surface-Level Patches (Root Cause Mandate)**

* **The Rule**: **ALWAYS** search for and fix the root cause. **NEVER** patch the symptom.  
* **Philosophy**: If a crash occurs (e.g., KeyError), the bug is upstream where the invalid data was created. You must explain the Root Cause before fixing. Do not add if x is None: return just to silence an error.

### **18.5. NO Backward Compatibility (Clean Break)**

* **The Rule**: Do not keep "Legacy Adapters" or shims. If the schema changes, migrate or wipe the data. We are in a Hardening Phase, not Long-Term Support.

### **18.6. Enforced Workflow Mapping (SSOT Integrity)**

* **Structure**: The Registry (steps) defines the Step. The Workflow (workflows) contains **Links** only (id, inputs). Defining task\_key or config inside a workflow is a System Level Error.

### **18.7. Deterministic Execution Mandate (Python Authority)**

* **The Rule**: If a logic operation can be done deterministically in Python, it MUST NOT be delegated to the LLM.
* **Scope**: Math, Sorting, Deduplication, ID generation, Date formatting.
* **Why**: LLMs are probabilistic engines (Creative). Python is a deterministic engine (Logical). Use the right tool.
* **Compliance**: Verify all Agent `post_process` methods enforce this mandate.