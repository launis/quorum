# ANTIGRAVITY AGENT CONFIGURATION (1.21.6+)
System Context: Quorum (Python Backend V2 + Flutter Client V2)
Host Environment: **Windows 11 (PowerShell)**
STATUS: Phase 9 (Hardening & Standardization)

## 🖥️ 1. ENVIRONMENT & TOOLING CONSTRAINTS
As an autonomous agent operating in Antigravity 1.21.6+, you must strictly adhere to the host restrictions:
* **Windows 11 Host:** The system lacks native Linux sandboxing. **DO NOT** attempt to use internal sandboxed cascade terminal execution features.
* **Linux Command Ban:** You are strictly forbidden from proposing Linux shell commands (`ls`, `cat`, `grep`, `rm -rf`, `export`). You must ONLY propose and execute native PowerShell commands (`Get-ChildItem`, `Get-Content`, `Remove-Item -Recurse -Force`, `$env:`).
* **Command Execution Protocol (Windows 11):** The `run_command` tool functions as a native PowerShell interface. You **MAY AND SHOULD** use it to automatically execute routine system tasks (`dart run build_runner build -d`, `dart format`, `dart analyze`, `uv run`), but note that the Human User must approve them first.
  - For file operations and project traversal: Exclusively leverage native agent tools (`list_dir`, `grep_search`, `view_file`, `replace_file_content`) as they bypass terminal latency completely.
  - `c:\src\quorum\backend_debug.log` (FastAPI routing, CPU hooks, Pydantic validation errors)
  - `c:\src\quorum\client_debug.log` (Flutter Riverpod states, GoRouter navigation, and HTTP requests)

## 📋 2. TIERED EXECUTION PROTOCOL
When planning or executing any changes, defer to `docs\antigravity_prompting.md` to assess the operation tier:
* **TIER 1 (Epic Planner):** Deep research and milestone breakdown for major architectural alterations.
* **TIER 2 (Execution Planner):** Strict, step-by-step implementation of an approved `implementation_plan.md`.
* **TIER 3 (Single Operation):** Direct atomic executions for bug fixes, code audits, or localized file tweaks.

## 🚨 3. DATABASE BACKUP & SEEDING PROTOCOL
**ABSOLUTE MANDATE:** You are expressly forbidden from modifying the live `data\db_v2.json` database directly during development.
If system configuration, steps, or workflow seed data must be altered:
1. Target the original `backend_v2\seed\seed_data.json` file.
2. Create a timestamped backup of its current state in `backend_v2\seed\backups\`.
3. Notify the user exactly *why* and *what* changes you intend to incorporate.
4. Verify structural integrity locally.
5. **WAIT for explicit confirmation from the user.** Only after receiving permission, instruct the user to execute the command: `uv run python backend_v2\seed\run_seed.py local`.

## 📖 4. KNOWLEDGE RESOLUTION
Always run a `grep_search` or cross-reference the `<knowledge_item>` artifacts dynamically before touching the backend orchestrator or client display logic. The system rules evolve drastically based on the current Epic Phase.
