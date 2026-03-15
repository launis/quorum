# 🚀 Antigravity Prompting - Command Center & Toolkit (V5.1 / Phase 9 Hardening)

> [!IMPORTANT]
> This document is the **Command Center** and rulebook for directing the Google Antigravity / Gemini AI. Because we are in the **Phase 9 Hardening** phase, the AI's task is not to "code fast" but to produce **100% compliant, secure, and error-free code**. 

This document describes a unified **3-Tier Protocol** for executing tasks of any size. It guides the breakdown of large architectural changes (Tier 1), their execution (Tier 2), as well as daily task work, auditing, and seed data modification (Tier 3). All operations are based on the **Universal Mandate** placed at the end.

---

## 🎯 THREE TIERS OF OPERATION (Select and copy what you need)

Select the appropriate instruction block from the text and copy it as a whole to the AI. **Always add the UNIVERSAL MANDATE (found at the end of the page) after the block.**

---

### 🟢 TIER 1: EPIC PLANNER (Planning a large change)
*Usage: At this tier, the goal is to break down one large entity (multiple files, new agent) into an `implementation_plan.md` or, based on it, generate several more detailed plans before writing any code.*

```text
Goal: [WRITE GOAL. Ex: "Design and implement a new reporting module and UI"]

ROLE: Principal Solutions Architect (2026 Context - Phase 9 Hardening).
REFERENCE: `GEMINI.md` or `AGENTS.md` (Read first. Absolute law).

INSTRUCTIONS (LEVEL 1):
1. READ: Do NOT write code yet. Familiarize yourself with the architectural laws.
2. PLAN: Create an `implementation_plan.md` breaking this goal into 4-6 independent Milestones.
3. SEQUENCE: Every milestone MUST strictly follow the V2 architecture sequence (Dependencies -> Pydantic Models -> L10n -> Repo -> API -> Frontend Controller -> UI). Note: Frontend domain data MUST NOT use generated models.
4. SCOPING: Explicitly map which files are `TARGET (Modify)` and which are `CONTEXT (Read-Only)`.
5. PAUSE: Present the plan and WAIT for explicit approval ("PERMISSION GRANTED"). Do not implement anything.
```

---

### 🟡 TIER 2: EXECUTION PLANNER (Systematic execution of the plan)
*Usage: Once the Tier 1 `implementation_plan.md` is approved. This command puts the AI into a "coding machine" mode, where it executes the approved list step-by-step without unnecessary detours.*

```text
Goal: Execute the approved `implementation_plan.md` step-by-step.

ROLE: Lead Developer (2026 Context - Phase 9 Hardening).
REFERENCE: `GEMINI.md` or `AGENTS.md`.

INSTRUCTIONS (LEVEL 2):
1. ISOLATION: Execute the plan ATOMICALLY. Work on one single Milestone/Step at a time.
2. CONSTRAINTS: For every single step, enforce Strict Typing in backend (`Pydantic`) and the "Fail-Fast" doctrine (No `try-except pass`, use `AppException`). Frontend MUST NOT use `Freezed` for API/Domain data.
3. DUAL-IMPLEMENTATION: If touching backend data, automatically update both TinyDB and Firestore repositories simultaneously.
4. QUALITY LOOP: Write the code and run verification tools (`ruff`, `mypy`, `dart analyze`).
5. CHECKPOINT: Mark the step COMPLETE in the markdown tasklist and explain shortly how the code follows the constraints for this single step. Wait for my permission ("PROCEED") before proceeding to the next item on the plan.
```

---

### 🔴 TIER 3: SINGLE OPERATION (Implementation, review, and maintenance)
*Usage: Situations where a single feature is changed or created, a legacy file is refactored, bugs are hunted in a solution (debugging), or audits/configuration changes are performed. Tier 3 is divided into compartments (A, B, C, D) based on the nature of the work but operates on a direct execution logic.*

#### 3A. FEATURE & REFACTOR (Single implementation or cleanup)
```text
Goal: [WRITE GOAL HERE. Ex: "Create a new tab in settings" OR "Refactor file X to match modern DTO rules"]

ROLE: Senior Developer (2026 Context).
INSTRUCTIONS (LEVEL 3A):
1. PLAN: Read related files. Create a quick execution plan containing specific `TARGET (Modify)` and `CONTEXT (Read-Only)` files.
2. FAIL-FAST: State where `AppException` will be raised if data is missing. Do not use fallbacks.
3. UI/UX: Output localized keys only via the API. Do not hardcode frontend strings.
4. EXECUTE & PAUSE: Present the root cause or execution plan, get confirmation ("PERMISSION GRANTED"), and write the code adhering strictly to the Single Source of Truth rules defined in `GEMINI.md` or `AGENTS.md`.
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
2. Look strictly for: `try-except pass` blocks, silent `{}` returns masking data errors, naked `ValueError` raises, implicit domain defaults (like `score = 0.0`), and hardcoded localization strings in the backend.
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
5. EXECUTE: Run your script: `python modify_seed.py`.
6. VERIFY: Run tests (`pytest backend_v2/tests/unit/test_seed_schema_alignment.py -v`) to mathematically verify the change. If it fails, your mutation corrupted the graph. Fix your script/JSON and try again.
7. REPORT: Confirm the delta matches expectations and tests pass.
8. RE-SEED (Siemennys): Only after this, the actual local database update and sync is executed by running the command: `python backend_v2/seed/run_seed.py local`.
Bypassing these instructions and tinkering with the live DB (`db_v2.json`) corrupts the system IDs permanently.
```

---

## 🚨 UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (ALWAYS attach to everything)

*(Always copy this after all Tier 1, 2, and 3 prompts.)*

```text
*** UNIVERSAL MANDATE & ARCHITECTURE CONSTRAINTS (V5.1 - PHASE 9 HARDENING) ***

1. ANTI-HALLUCINATION & FILE SCOPING PROTOCOL:
   - Read-Before-Write: NEVER guess the contents of a file. Use your tools to read the current context before proposing modifications.
   - Explicit Scope: Only modify `TARGET` files. Treat `CONTEXT` files as Read-Only.

2. ARCHITECTURAL BANS & MANDATORY VERIFICATION (Non-Negotiable - Enforced by Strict Mandates):
   - You MUST adhere to the Single Sources of Truth defined in `GEMINI.md` or `AGENTS.md`.
   - AI VERIFICATION MANDATE: You (the AI assistant) MUST actively verify your compliance with the V2 Architecture on EVERY task. Before writing any code, you MUST explicitly state that the V2 Architecture has been taken into account and briefly explain how your proposed solution complies with its core tenets (e.g., Pydantic schemas, Zero-Deploy logic, SDUI, Riverpod state).
   - Backend: NO `try-except pass`. NO raw `dict` returns from Agents (Strict Pydantic V2 only). NO legacy `Depends` (Use `Annotated`). NO business logic in Routers. NO `HTTPException` (Use `AppException` & RFC 7807). No default values in domain models unless logically strictly necessary.
   - The Three Pydantic Boundaries (API, Service, Middleware):
     1. **API Ingestion (Generic IN -> Strict OUT)**: The API Routers (`backend_v2/api/`) MUST take raw JSON/Dict from the web and immediately force it into a strict Pydantic DTO before handing it to the Service layer. Services never accept raw dicts from routers.
     2. **Service Layer (Strict IN -> Strict OUT)**: The business logic (`backend_v2/services/`) is the absolute gatekeeper. It ONLY accepts Pydantic models from the routers, and any data it fetches from the `repository` (TinyDB/Firestore) MUST be instantly hydrated into a Pydantic model (`Model.model_validate(data)`) before any logic is applied. 
     3. **DAG/Middleware (Strict IN -> Generic OUT)**: The Execution engine (`DAGExecutor`), Post-Hooks (`backend_v2/hooks/`), and Data Pipelines MUST NEVER accept or check for Pydantic models (e.g., `hasattr(item, "model_dump")`). Agents enforce strict Pydantic V2 on generation (Fail-Fast), but immediately hand off `.model_dump(mode="json")` dictionaries to the rest of the internal engine. Middleware flow is always 100% dictionary-based.
   - Frontend: Use Riverpod 3.0 code generation (`@riverpod`). **Use Freezed ONLY for static local UI state (e.g. User, Settings). Dynamic SDUI API Payloads and Blueprints MUST use raw `Map<String, dynamic>` (De-Generator Policy)** to maintain Zero-Deploy flexibility. Data management is kept small and concise. All asynchronous data must be rendered in the UI following the formal model. Routing MUST use `GoRouteData`. NO manual `if(isLoading)` checks (Use `.when()`). NO `Future.wait` monoliths for State.
   - L10N (No-String Policy): Backend MUST return Enum Keys (e.g., `AUTH_ORGANIC`). Raw UI strings are BANNED in Python APIs. Translations live exclusively in Frontend `.arb` files executing ICU formats. No manual string concatenation.

3. THE ZERO-COMPROMISE PLEDGE (Fail Fast & Root Cause):
   - If data is invalid or missing, crash immediately at the Service boundary. Do not return `None` or `{}` to silently bypass errors. Fix the root cause.
   - Exception: The Omni-Channel Rendering layer MUST use graceful degradation (e.g., returning `{}` or `SizedBox.shrink()` on UI) for missing specialist data to prevent total UI crashes, but must log an explicit warning (`logger.warning(...)` / `debugPrint(...)`).
   - Dual-Reporting Python: Always log errors structurally (`logger.error`) BEFORE raising `AppException`.

4. EDITING SAFETY (Anti-Duplication Protocol):
   - When modifying a file, explicitly DELETE or OVERWRITE the old version. NEVER append the new version to the end of the file while leaving the old one intact.

5. DATA PARITY & OPTIMISTIC UI:
   - Backend: Any database repository change MUST be implemented in BOTH `repository.py` (TinyDB) and `firestore_repo.py` (Cloud) to maintain strict dual-backend parity.
   - Frontend: Implement Optimistic Updates for all mutations (update cache before network call, rollback if error).
   
6. OUTPUT FORMAT REQUIREMENTS:
   - Language Strategy: Antigravity Prompts / Code Blocks MUST be in English. Explanations/Context MUST be in Finnish.
   - Internal Comments (The "Why" Mandate): Only comment WHY business logic exists. Never explain WHAT the code mechanically does. Use Imperative Mood for docstrings.

7. QUALITY LOOP & TOOL USAGE (MANDATORY VERIFICATION):
   - Python: Run `ruff check <files> --fix` -> `mypy <files> --strict` -> `pytest`.
   - Flutter: Run `dart format` -> `dart analyze` -> `flutter test`.
   - Resolve ALL syntax and typing errors before declaring the step or ticket complete.

8. DATABASE:
   - If changing database execute it according to `docs/antigravity_prompting.md` / `3D. SEED DATA VAULT PROTOCOL (C-level configuration changes)` rules.

9. TESTING MANDATE (WHENEVER YOU CHANGE CODE):
   - Whenever code is changed, refactored, or new features are added, you MUST ALWAYS write new automated tests OR fix existing old tests for both the Flutter and Python sides. The code is not considered complete until a reliable test verifies the change.
```