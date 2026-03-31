# ANTIGRAVITY AGENT CONFIGURATION & DIRECTIVES (1.21.6+)
System Context: Quorum (Python Backend V2 + Flutter Client V2)
Host Environment: **Windows 11 (PowerShell)**

<CRITICAL_WIN11_CONSTRAINTS>
You are operating in a Windows 11 environment where the Antigravity 1.21.6+ native Linux sandboxing is unsupported. STRICT COMPLIANCE is mandatory to prevent cascade crashes:

1. **ABSOLUTE BAN ON `run_command`:** You MUST NEVER call the `run_command` tool. It fundamentally fails in this environment with: "failed to set up sandbox". Do NOT attempt to modify `SafeToAutoRun` to bypass this.
2. **DELEGATE EXECUTION TO USER:** For tasks requiring an active runtime engine (e.g., tests, DB migrations, `dart run build_runner build`, local servers), output the exact command in a Markdown `powershell` code block and EXPLICITLY ASK THE USER to execute it in their terminal.
3. **POWERSHELL SYNTAX MANDATE:**
   - NEVER propose Linux shell commands (`ls`, `cat`, `grep`, `rm -rf`, `export`). Use ONLY native PowerShell (`Get-ChildItem`, `Remove-Item -Recurse -Force`, `$env:`).
   - NEVER use the `&&` operator. Chain commands using semicolons (`;`) or execute them on separate lines.
   - EXPLICIT TARGETING: When running linters (`ruff`, `mypy`), list ALL target files explicitly by name (e.g., `uv run ruff check main.py utils.py --fix`). NEVER use wildcards like `*.py`.
4. **DEPRECATED COMMANDS:** `flutter pub run` is banned. ALWAYS use `dart run`.
</CRITICAL_WIN11_CONSTRAINTS>

## 🛠️ 1. NATIVE FILE READING & MCP TOOL MANDATE
Antigravity 1.21.6 features enhanced MCP capabilities. ALWAYS use your built-in internal tools (`view_file`, `grep_search`, `list_dir`, `replace_file_content`) to read files, code, and logs. NEVER ask the user to run Python or shell scripts just to print text or logs. Your internal tools instantly bypass the broken Windows terminal sandbox.

## 📚 2. PRIMARY DIRECTIVES & SOURCES OF TRUTH
You are an expert functionality-first AI developer. The ultimate architecture rules have been consolidated into the Agentic Configuration Center. Before writing code, you MUST dynamically read the relevant documents from `c:\src\quorum\.agents\rules\`:
1. `00-antigravity-core.md` (Global IDE Protocol)
2. `01-python-backend.md` (Backend Architecture)
3. `02_flutter_desktop.md` (Frontend Architecture)
4. `03_seed_vault.md` (Database Maintenance)
5. `04_directory_reference.md` (System Directory Map & Services)

**Architectural Mandates (Violating these means failing the task):**
- Strict V2/V3 Architecture: Event Sourcing, The Opaque Stripe ID Pattern, Fail-Fast Pydantic.
- Serverless Tool Loop: Tavily AI Fact Check Injection.
- Flat MVC Mandate: NO SDUI, JSON Parsing exclusively via Dart `Isolate.run()`.
- Banned Patterns: No fallbacks, No hardcoding UUIDs, No UI string literals.
- Tech Stack: Python 3.14, Riverpod 3.0, Pydantic V2.

## 📡 3. LIVE LOGGING (Runtime Truth)
Always check these logs directly with your internal MCP file-reading tools before diagnosing issues:
- **BACKEND LOGS:** `c:\src\quorum\backend_debug.log` (FastAPI routing, CPU hooks, Pydantic validation errors, Worker tasks). Check first for backend failures.
- **CLIENT LOGS:** `c:\src\quorum\client_debug.log` (Flutter Riverpod states, GoRouter navigation, HTTP requests). Check first for UI/Network failures.

## 📋 4. TIERED EXECUTION PROTOCOL
You must follow strict operation tiers relying on the natively supported workflows in `c:\src\quorum\.agents\workflows\`. You can execute or refer to these protocols to assess operations:
* **/tier1-planner:** Epic Planner for generating `implementation_plan.md` for major architectural alterations.
* **/tier2-execute:** Strict, step-by-step implementation of an approved `implementation_plan.md`.
* **/tier2-hardening-backend:** Tier 2 (Backend Hardening) - Step-by-step auditing loop for Python backend directories against Phase 9 standards.
* **/tier2-hardening-frontend:** Tier 2 (Frontend Hardening) - Step-by-step auditing loop for Flutter frontend directories against Phase 9 standards.
* **/tier3-database-reset:** Single-operation database resets and scaling tweaks.
* **/tier3-feature-refactor:** Single feature implementation or existing file cleanup.
* **/tier4-bug-hunting:** Deep root cause analysis and resolution of a specific bug.
* **/tier5-zero-shortcut-audit:** Ruthless code review against IDE Protocol constraints.

## 💾 5. DATABASE BACKUP & SEEDING PROTOCOL
**ABSOLUTE MANDATE:** You are expressly forbidden from modifying the live `data\db_v2.json` database directly.
If system configurations, steps, or workflow seed data must be altered:
1. Target the original `backend_v2\seed\seed_data.json` file.
2. Create a timestamped backup of its current state in `backend_v2\seed\backups\`.
3. Notify the user exactly *why* and *what* changes you intend to incorporate.
4. Verify structural integrity locally (check array length/row counts).
5. **WAIT FOR EXPLICIT CONFIRMATION FROM THE USER.** 
6. Only after receiving permission, instruct the user to execute:
   ```powershell
   uv run python backend_v2\seed\run_seed.py local