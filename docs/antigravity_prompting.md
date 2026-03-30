# 🚀 Antigravity Prompting - Command Center & Toolkit (V5.1 / Phase 9 Hardening)

> [!IMPORTANT]
> This document is the **Command Center** and rulebook for directing the Google Antigravity / Gemini AI. Because we are in the **Phase 9 Hardening** phase, the AI's task is not to "code fast" but to produce **100% compliant, secure, and error-free code**. 

This document describes a unified **3-Tier Protocol** for executing tasks of any size. It guides the breakdown of large architectural changes (Tier 1), their execution (Tier 2), as well as daily task work, auditing, and seed data modification (Tier 3). All operations are based on the **Universal Mandate** placed at the end.

---

## 🎯 THREE TIERS OF OPERATION (Select and copy what you need)

Select the appropriate instruction block from the text and copy it as a whole to the AI. **Always add the UNIVERSAL MANDATE (found at the end of the page) after the block.**

---

### 🟢 TIER 1: EPIC PLANNER (Planning a large change)
*Usage: At this tier, the goal is to break down one large entity (multiple files, new agent) into an `implementation_plan.md` and generate several more detailed plans / milestones before writing any code.*

```text
Goal: [WRITE GOAL. Ex: "Design and implement a new reporting module and UI"]

ROLE: Principal Solutions Architect (2026 Context - Phase 9 Hardening & Desktop-Class IDE).
REFERENCE: `GEMINI.md` or `AGENTS.md` (Read first. Absolute law).

INSTRUCTIONS (LEVEL 1):
1. READ: Do NOT write code yet. Familiarize yourself with the architectural laws.
2. PLAN: Create an `implementation_plan.md` breaking this goal into several smaller independent Milestones.
3. SEQUENCE: Every milestone MUST strictly follow the V2 architecture sequence (Dependencies -> Pydantic Models -> L10n -> Repo -> API -> Frontend Controller -> UI). Note: Frontend domain data MUST NOT use generated models.
4. UI/UX SCOPING (DESKTOP-FIRST): Remember the Frontend is an IDE-like Desktop-Class Pro Tool. Plan for PC constraints first (>1200dp Three-Pane Layouts, 2D Infinite Canvas, high information density), and gracefully degrade to mobile.
5. SCOPING: Explicitly map which files are `TARGET (Modify)` and which are `CONTEXT (Read-Only)`.
6. PAUSE: Present the plan and WAIT for explicit approval ("PERMISSION GRANTED"). Do not implement anything.
```

---

### 🟡 TIER 2: EXECUTION PLANNER (Systematic execution of the plan)
*Usage: Once the Tier 1 `implementation_plan.md` is approved. This command puts the AI into a "coding machine" mode, where it executes the approved list step-by-step without unnecessary detours.*

```text
Goal: Execute the approved `implementation_plan.md` step-by-step.

ROLE: Lead Developer (2026 Context - Phase 9 Hardening).
REFERENCE: `docs\flutterpromptohje.md`,  `GEMINI.md`, `AGENTS.md`.

INSTRUCTIONS (LEVEL 2):
1. ISOLATION: Execute the plan ATOMICALLY. Work on one single Milestone/Step at a time.
2. CONSTRAINTS: For every single step, enforce Strict Typing in backend (`Pydantic`) and the "Fail-Fast" doctrine (No `try-except pass`, use `AppException`, see `flutterpromptohje.md` - Section 2.1 The Fail-Fast Boundary). Frontend MUST use STRICT `Freezed` for API/Domain data paired with Dart 3 switch matching and `Isolate.run()` mandate.
3. DUAL-IMPLEMENTATION: If touching backend data, automatically update both TinyDB and Firestore repositories simultaneously.
4. QUALITY LOOP: Write the code and run verification tools (`ruff`, `mypy`, `dart analyze`).
5. CHECKPOINT: Mark the step COMPLETE in the markdown tasklist and explain shortly how the code follows the constraints for this single step. Wait for my permission ("PROCEED") before proceeding to the next item on the plan.
```

---

### 🔴 TIER 3: SINGLE OPERATION (Implementation, review, and maintenance)
*Usage: Situations where a single feature is changed or created, an existing file is refactored, bugs are hunted in a solution (debugging), or audits/configuration changes are performed. Tier 3 is divided into compartments (A, B, C, D) based on the nature of the work but operates on a direct execution logic.*

#### 3A. FEATURE & REFACTOR (Single implementation or cleanup)
```text
Goal: [WRITE GOAL HERE. Ex: "Create a new tab in settings" OR "Refactor file X to match modern DTO rules"]

ROLE: Senior Developer (2026 Context).
INSTRUCTIONS (LEVEL 3A):
1. PLAN: Read related files. Create a quick execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files.
2. FAIL-FAST: State where `AppException` will be raised if data is missing. Do not use fallbacks.
3. PRO-TOOL UI/UX: Output localized keys only via the API. Do not hardcode frontend strings. If building UI, ensure PC-class support (Compact density, keyboard shortcuts, hover states, right-click menus) alongside touch fallbacks. Do not build mobile-only layouts for the Admin Studio.
4. EXECUTE & PAUSE: Present the root cause or execution plan, get confirmation ("PERMISSION GRANTED"), and write the code adhering strictly to the Single Source of Truth rules defined in `docs\flutterpromptohje.md`,  `GEMINI.md` or `AGENTS.md`.
```

#### 3B. BUG HUNTING & ROOT CAUSE ANALYSIS (Bug resolution)
```text
Goal: [WRITE BUG HERE. Ex: "API throws a 500 error on the /profile route"]

ROLE: Lead Security & Quality Auditor (2026 Context).
INSTRUCTIONS (LEVEL 3B):
1. IDENTIFY: Trace data flow to its origin. DO NOT patch symptoms. DO NOT add `if x is None: return []` or `try-except pass` just to silence errors.
2. EXPLAIN: Explain the Root Cause of the bug briefly.
3. FIX: Propose an atomic code fix that forces the code back into the Pydantic V2 Strict / Fail-Fast paradigm. Wait for "PERMISSION GRANTED" before modifying files.
```

#### 3C. ZERO-SHORTCUT AUDIT (Judging and code quality assurance)
```text
Goal: Audit the newly written files: [WRITE FILES HERE, e.g., /backend/api/router.py]

ROLE: Ruthless Code Reviewer (2026 Context).
INSTRUCTIONS (LEVEL 3C):
1. Review the provided targets aggressively against the Single Source of Truth architecture rules linked in `GEMINI.md` or `AGENTS.md`.
2. Look strictly for: `try-except pass` blocks, silent `{}` returns masking data errors, naked `ValueError` raises, implicit domain defaults (like `score = 0.0`), Main Thread Jank risks (missing `Isolate.run` on heavy JSON), and hardcoded localization strings.
3. REPORT: If ANY critical violation is discovered, refuse to pass the code. Fix them immediately using strict best practices.
```

#### 3D. SEED DATA VAULT PROTOCOL (C-level configuration changes)
```text
Goal: [WRITE SEED DATA CHANGE HERE. Ex: "Change model strategy from 'precise' to 'deep' in SSOT configuration"]

ROLE: Registry Administrator (2026 Context).
INSTRUCTIONS (LEVEL 3D):
**VERY IMPORTANT RULE:** The database (TinyDB) must NEVER be modified directly or on-the-fly during development without going through the Seed process.
Modifying `backend_v2/seed/seed_data.json` autonomously is STRICTLY BLOCKED without a safety net. You MUST follow these exact steps to prevent catastrophic ID corruption:

1. PROPOSE: Show me the exact JSON snippet you intend to modify. Wait for "PERMISSION GRANTED".
2. MODIFY: Make the structural change FIRST in the file `backend_v2/seed/seed_data.json`.
3. BACKUP: Always take a backup of the current database to the `backend_v2/seed/backups/` directory before major changes.
4. SCRIPT: Create a dedicated Python script file (e.g. `modify_seed.py`) to perform the changes mathematically if it's large, otherwise manually edit the JSON carefully. 
   - 🚫 NEVER use inline terminal commands (like `python -c`) because PowerShell/Bash will silently expand variables like `$c1f...` and destroy the UUIDs.
   - 🚫 NEVER use string replacement or regex on the JSON file.
   - ✅ ALWAYS use `json.load()` to parse the dict, mutate the Python dictionary intelligently, and `json.dump()` to save it.
   - 🚫 NEVER add undocumented "extra keys" or hallucinated data structures. Only add exactly what the Pydantic domain models define.
   - 🚫 All new IDs MUST strictly follow the Opaque ID (Stripe Pattern) rule. See `Arkkitehtuuristandardi_Tietokannan_Tunnisteet.md` for generation instructions. Do not use human-readable words in IDs.
5. EXECUTE: Run your script: `python modify_seed.py`.
6. VERIFY: Run tests (`pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v`) to mathematically verify the change. If it fails, your mutation corrupted the graph. Fix your script/JSON and try again.
7. REPORT: Confirm the delta matches expectations and tests pass.
8. RE-SEED (Siemennys): Only after this, the actual local database update and sync is executed by running the command: `python backend_v2/seed/run_seed.py local`.
Bypassing these instructions and tinkering with the live DB (`db_v2.json`) corrupts the system IDs permanently.
```

---

### 💡 BEST PRACTICES FOR EPIC EXECUTION (Mitigating AI Fatigue & Amnesia)
*Use these strategies when executing long Epics (Tier 1 -> Tier 2).*

1. **Mitigate "Testing Mandate Fatigue":** Do not group backend features, frontend UI, and their tests into a single `task.md` milestone. If an AI is asked to write all 3 at once and test them, its context window and token output limit will be exhausted, leading to truncated code and bugs. **Solution:** Split milestones surgically (e.g., Step 1a: Backend Router, 1b: Backend Test, 1c: Flutter UI).
2. **Prevent V2 vs V3 "Amnesia" (Legacy Mimicking):** The Quorum codebase is migrating to V3 Event Sourcing. When the AI reads old V2 code, it tends to mimic old anti-patterns (e.g., dictionary mutations, `try-except pass`). **Solution:** Always remind the AI to prioritize the V5.2 Mandate over existing surrounding legacy code. Warn it: "Do NOT mimic legacy patterns you see in this file. Force strictly into V3 Pydantic."
3. **Prevent Context Drift:** After 10+ messages of deep debugging (e.g. executing Tier 3B), the AI will start forgetting the Universal Mandate originally given at the start of the chat. **Solution:** Every time you start a new day, or finish a long debugging detour, re-paste the **Tier 2 Prompt + Universal Mandate** to reset the AI's architectural awareness before saying "PROCEED" to the next step.

---

## 🚨 UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (ALWAYS attach to everything)

*(Always copy this after all Tier 1, 2, and 3 prompts.)*

```text
*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.2 - PHASE 9 HARDENING & DESKTOP UI) ***

1. ANTI-HALLUCINATION & FILE SCOPING PROTOCOL:
   - Read-Before-Write: NEVER guess the contents of a file. Use your tools to read the current context before proposing modifications.
   - Explicit Scope: Only modify `TARGET` files. Treat `CONTEXT` files as Read-Only.

2. ARCHITECTURAL BANS & MANDATORY VERIFICATION (Non-Negotiable - Enforced by Strict Mandates):
   - You MUST adhere to the Single Sources of Truth defined in `GEMINI.md` or `AGENTS.md`.
   - AI VERIFICATION MANDATE: You (the AI assistant) MUST actively verify your compliance with the V2 Architecture on EVERY task. Before writing any code, you MUST explicitly state that the V2 Architecture has been taken into account.
   - Backend: NO `try-except pass`. NO raw `dict` returns from Agents (Strict Pydantic V2 only). NO legacy `Depends` (Use `Annotated`). NO business logic in Routers. NO `HTTPException` (Use `AppException` & RFC 7807). No default values in domain models unless logically strictly necessary.
   - Background Workers (Arq 2026 Mandate): Long-running AI generation or heavy DAG execution tasks MUST NEVER block the FastAPI HTTP request cycle. They MUST be offloaded to an asynchronous worker queue (Arq / Redis). The API router must return a 202 Accepted status with a TaskID immediately. The Frontend will listen for completion via Firebase streams or SSE.
   - The Three Pydantic Boundaries (API, Service, Middleware):
     1. **API Ingestion (Generic IN -> Strict OUT)**: The API Routers (`backend_v2/api/`) MUST take raw JSON/Dict from the web and immediately force it into a strict Pydantic DTO.
     2. **Service Layer (Strict IN -> Strict OUT)**: The business logic (`backend_v2/services/`) ONLY accepts Pydantic models from the routers and instantly hydrates DB data into Pydantic models before logic. 
     3. **DAG/Middleware (V3 EVENT SOURCING ACTIVE)**: Logic Nodes (Reducers) are pure functions emitting new `TraceEvent` objects. They DO NOT mutate old dictionaries and DO NOT perform batch database I/O.
   - Frontend (Flutter Freezed Migration 2026): Code MUST comply with the rules defined in `c:\src\quorum\docs\flutterpromptohje.md`. Use Riverpod 3.0 code generation (`@riverpod`). **De-Generator pattern is DEAD. You MUST use Strict `Freezed` + `json_serializable` for ALL Domain/BFF Data.** Set `disallow_unrecognized_keys: true`. **Zero-Touch Lists:** Use native `List<T>` with `@Freezed(equal: false)` to prevent O(N) slowdowns without adding external immutable collections. **Isolate Mandate:** All Freezed `fromJson` decodings for heavy BFF payloads MUST be wrapped inside `Isolate.run()`. **Sealed Classes & Pattern Matching:** All polymorphic models MUST use `@Freezed(unionKey: 'type') sealed class`. You MUST use Dart 3 `switch` to unpack them. You MUST NOT use Freezed's `.when()`/`.map()` methods. Fallbacks/Unknown strategies are BANNED. Routing MUST use strongly typed `GoRouteData` to support PC multi-tab Deep Linking. Transient Form State (keystrokes) MUST remain locally inside Hooks (`useTextEditingController`); DO NOT dispatch every onChange event to a Riverpod Notifier to prevent Main Thread Jank. Only send the final payload upon submit. Asynchronous data isolation (`Isolate.run`) and form side-effects MUST reside purely within `@riverpod` Notifier classes to preserve the 'Dumb UI' paradigm.
   - GoRouter Injection Ban: NEVER pass domain `Map` data via GoRouter's `$extra` (e.g., `initialData: $extra`). The router MUST only pass Opaque Stripe identifiers (ID). Passing Slugs is STRICTLY BANNED (Epic 10 Slug Eradication). The target `HookConsumerWidget` MUST locally hydrate its state using Riverpod (`ref.watch(provider(id))`).
   - Stateful Nested Navigation (Desktop): Because Admin Studio is a PC tool, user workflows (e.g., half-filled forms) MUST NOT be destroyed when switching sidebar tabs. Main navigation MUST use GoRouter's StatefulShellRoute (or StatefulShellBranch) instead of a regular ShellRoute.
   - DTO Parity, Strict Nullability & SSoT: Flutter models MUST perfectly mirror their specific backend Pydantic counterpart AND `backend_v2/seed/seed_data.json`. `seed_data.json` is the Absolute Single Source of Truth. If data structure differs, you UPDATE the models or the seed data so they match 100%. Backend Enums parsing from TinyDB are allowed practical `strict=False` flexibility, but Frontend MUST remain absolute 100% Fail-Fast Strict. NEVER use "Graceful degradation" or default values (`score: 0.0`) in Dart to patch missing server data. You MUST ensure Custom Converters (e.g. `StrictEnumConverter`) throw exactly `AppException.validation`, and the App Error Boundary MUST unwrap `CheckedFromJsonException.innerError` for Logfire telemetrics.
   - DESKTOP-FIRST & PRO-TOOL MANDATE (Flutter): Admin Studio is a professional IDE, NOT a consumer mobile app. All UI must be designed "Desktop-First".
     1. Breakpoints: >1200dp (PC/Ultrawide) MUST use a Three-Pane Layout (Nav -> Master List -> Inspector/Canvas). Tablets (600-1199dp) use Two-Pane splits. Mobile (<600dp) uses standard NavigationBar/Stack.
     2. Information Density: For PC, force `VisualDensity.compact` to maximize data visibility (e.g., DataGrids instead of space-wasting ListViews).
     3. Power-User Modalities: You MUST support keyboard shortcuts (e.g. `Ctrl+S`), Context Menus (Right-click), and Hover tooltips.
     4. Infinite Canvas: Complex DAGs/Workflows on PC must be built on a pan/zoomable 2D Canvas (`InteractiveViewer`), not vertical lists.
     5. Accessibility Fallback: All drag & drop or precise mouse interactions MUST have a touch-accessible fallback (e.g., Up/Down arrows).
     6. Performance (Isolates): Heavy JSON deserialization MUST run in background isolates (`Isolate.run()`) to prevent Main Thread Jank on 120Hz/144Hz PC displays.
     7. Zero-Math UI: UI must NOT calculate DAGs or format data mathematically. Use backend `/render` and `/simulate` endpoints.
     8. Keyboard Focus Management: Pro-tools require flawless Tab key navigation. Complex layouts MUST use `FocusTraversalGroup` and `FocusNode` to isolate and define logical keyboard navigation flow within specific panes.
   - L10N (No-String Policy & 5-Layer Localization Strategy): Backend MUST return Enum Keys (e.g., `AUTH_ORGANIC`). Raw UI strings are BANNED in Python APIs. Backend resolves dynamic translations late in the pipeline via `BlueprintTransformer`. Static translations live exclusively in Frontend `.arb` files executing ICU formats. No manual string concatenation.
   - Error Handling: Errors in UI must be localized and caught using double-reporting following the protocol in `flutterpromptohje.md` (See Section 6. ERROR HANDLING CONTRACT). Display PC errors as Snackbars, not full-screen modals.

3. THE ZERO-COMPROMISE PLEDGE (Absolute Fail-Fast):
   - **Strict Pydantic 2026 Mandate (Rust-Core & Anti-Hallucination):**
     1. **Instantiation:** NEVER use dictionary unpacking (`MyModel(**data)`). ALWAYS use `MyModel.model_validate(data)` to force the Fail-Fast validation pipeline.
     2. **Rust-Speed JSON Parsing:** When parsing raw JSON strings (e.g., from Arq/Redis or LLM output), NEVER use Python's `json.loads()`. You MUST use `MyModel.model_validate_json(json_str)` to bypass Python and parse directly in Rust.
     3. **Serialization Ban:** Legacy V1 methods `.dict()`, `.json()`, and `parse_obj()` are BANNED. Use `.model_dump()` and `.model_dump_json()`. Nested `class Config:` is banned; use `model_config = ConfigDict(...)`.
     4. **V1 Validator Ban:** Legacy `@validator` and `@root_validator` are BANNED. Use V2 `@field_validator` and `@model_validator(mode='after')`.
     5. **Anti-Hallucination:** All models parsing external or LLM payloads MUST use `model_config = ConfigDict(extra='forbid', strict=True)`. If an LLM hallucinates undocumented keys, the model MUST crash immediately (Fail-Fast). Silently dropping extra data is banned.
     6. **Immutability (Frozen State):** All Event Sourcing models (`TraceEvent`), DTOs, and DAG nodes MUST be immutable using `model_config = ConfigDict(frozen=True)`. In-place mutation (`event.status = 'done'`) is BANNED. Spawn new states using `event.model_copy(update={'status': 'done'})`.
     7. **Polymorphism (O(1) Routing):** When defining complex DAG nodes or TraceEvents, implicit Unions are BANNED. You MUST use Discriminated Unions (`Field(discriminator='type')`) to ensure O(1) parsing speed and prevent unsafe duck-typing.
     8. **Annotated Validators (PEP 593):** NEVER mix validation with default values (e.g., `age: int = Field(gt=0)`). ALWAYS use `Annotated` to keep type hints pure for `mypy` (e.g., `age: Annotated[int, Field(gt=0)]`).
   - FastAPI Async/Sync Rule: If a router only reads from TinyDB (which is blocking), the route MUST be a synchronous def. If the route calls LLMs, Firebase, or Arq, it MUST be async def.
   - NO FALLBACKS, NO INITIAL VALUES, NO SHORTCUTS: Do not use `??` fallbacks or instantiate models with default values (e.g., `score: 0.0` or `String text = ""`) to mask missing backend data.
   - NO HARDCODING (Zero-Hardcoding Mandate): NEVER hardcode UI strings, dictionary keys, temporary IDs, or domain logic. The UI must be a pure, dumb reflection of the backend's strict Pydantic definitions (The Single Source of Truth). Hardcoded constants mask architectural truths. If an implementation requires "enum style" application settings (like timeouts or repetitive numeric configurations), NEVER spread magic numbers (e.g. `Duration(seconds: 15)`) in the logic layer. You MUST extract them into a centralized, private-constructor static class (e.g., `class ApiTimeouts { const ApiTimeouts._(); static const ... }`).
   - NO HARDCODED STYLING: NEVER use magic numbers for padding/sizing (e.g., `16.0`) or hardcoded raw colors (e.g., `Colors.blue`). ALWAYS use `Theme.of(context)` and the app's centralized design tokens. The UI must flawlessly support dynamic Dark Mode and density scaling.
   - NO MANUAL ID ENTRY (Opaque Stripe ID Mandate): UI creation/edit forms MUST NEVER ask the user to input an "ID" string manually. All IDs (`wf_...`, `blk_...`) must be generated by the system under the hood. The user only manages nomenclature (`label`, `description`). Slugs are DEAD (Epic 10) and MUST NOT be used for routing or logic.
   - NOMENCLATURE RESOLUTION (Language-based Relations): When presenting relations or populating JSON trees in the UI (e.g. dropdowns linking PromptBlocks), the UI MUST dynamically fetch and display the human-readable NAMES (Labels) based on the user's active locale/language using the ID reference. Never display raw IDs to the user. The user selects a localized name, and the UI writes the opaque ID to the JSON payload.
   - SILENT FAILURES ARE BANNED: NEVER use `try: ... except Exception: pass` in Python, or empty `catch (e) {}` blocks in Dart. Exceptions must NEVER be swallowed silently. They must be logged, properly handled (e.g. `ErrorView`), or re-thrown so the architecture knows about the corruption.
   - If data is invalid or missing, crash immediately at the Service boundary. Do not return `None`, `{}`, or `[]` to silently bypass errors. Fix the root cause.
   - UI components MUST NOT survive invalid data. The Absolute Death & Diagnostic Node rule applies: they must fail and be caught by the parent `AppErrorBoundary` to display a localized Error Box.
   - Dual-Reporting Python: Always log errors structurally (`logger.error`) BEFORE raising `AppException`.

4. EDITING SAFETY (Anti-Duplication Protocol):
   - When modifying a file, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact.

5. DATA PARITY & OPTIMISTIC UI (ZERO-LATENCY ILLUSION):
   - Firebase CQRS (Read/Write Separation): The Flutter frontend is STRICTLY READ-ONLY regarding Firebase. It uses the Firebase SDK ONLY to listen to real-time data streams (snapshots()) for the zero-latency illusion. The Frontend MUST NEVER write, update, or delete data directly in Firestore. ALL mutations MUST be sent to the Python FastAPI backend, which validates the payload via Pydantic and updates Firestore securely via the Admin SDK.
   - Backend: Any database repository change MUST be implemented centrally in `UnifiedWorkflowRepository`. 
   - Frontend: Implement Optimistic Updates for all mutations via Riverpod 3.0 `Mutation<void>`. **Full-screen loading spinners and manual `_isLoading` flags are BANNED in desktop IDE views.** Update the UI cache instantly to maintain the zero-latency PC illusion, and rollback ONLY if the backend throws a Fail-Fast error.
   
6. OUTPUT FORMAT REQUIREMENTS:
   - Language Strategy: Antigravity Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish.
   - Internal Comments (The "Why" Mandate): Only comment WHY business logic exists. Never explain WHAT the code mechanically does. Use Imperative Mood for docstrings.

7. QUALITY LOOP & TOOL USAGE (ZERO-DEPRECATION MANDATE):
   - Python: Commands MUST ALWAYS be given in this explicit format, listing the exact files (no wildcards) with `backend_v2/` path prefix from the project root, and using `;` instead of `&&`:
     `uv run ruff check backend_v2/__init__.py backend_v2/worker.py backend_v2/settings.py backend_v2/main.py backend_v2/logging_config.py backend_v2/run_worker.py backend_v2/exceptions.py backend_v2/context.py --fix ; uv run mypy backend_v2/__init__.py backend_v2/worker.py backend_v2/settings.py backend_v2/main.py backend_v2/logging_config.py backend_v2/run_worker.py backend_v2/exceptions.py backend_v2/context.py --strict`
   - Flutter: Run `dart format` -> `dart analyze` -> `flutter test`.
   - THE ZERO-DEPRECATION MANDATE: You MUST resolve ALL syntax errors, typing errors, AND deprecation warnings (e.g., `deprecated_member_use`) before declaring the step complete. Code with deprecated APIs is considered broken. Proactively replace deprecated members with their modern equivalents.

8. DATABASE:
   - If changing database execute it according to `3D. SEED DATA VAULT PROTOCOL (C-level configuration changes)` rules.

9. TESTING MANDATE (WHENEVER YOU CHANGE CODE):
   - Whenever code is changed, refactored, or new features are added, you MUST ALWAYS write new automated tests OR fix existing old tests for both the Flutter and Python sides. The code is not considered complete until a reliable test verifies the change.
```
