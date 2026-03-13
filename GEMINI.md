System Context: Quorum (Python Backend V2 + Flutter Client V2)
STATUS: Phase 2 (Hardening & Standardization)

# PRIMARY DIRECTIVES
You are an expert functionality-first AI developer.
Your Single Sources of Truth for this project are:

1. FRONTEND / GENERAL: `c:\src\quorum\docs\flutterpromptohje.md`
2. BACKEND / AI: `c:\src\quorum\docs\Arkkitehtuurimäärittely_ AI-orkestraattori V2.md`
3. BACKEND / V2: `c:\src\quorum\docs\Architecture_Universal_Routing_and_Hooks_V2.md`
4`

🛑 MANDATORY: Before proposing or writing ANY code, you MUST read the relevant document above using your file reading tools to understand:
- The Strict V2 Architecture (SSOT, Event Sourcing, Fail-Fast).
- The Banned Patterns (No fallbacks, No hardcoding, No UI string literals).
- The Tech Stack (Python 3.14, Riverpod 3.0, Pydantic V2) or the corresponding frontend stack.

If you act contrary to these documents, you are failing the task.

## 📋 PRE-EXECUTION INSTRUCTIONS
When executing changes, strictly follow the Tier instructions in `docs\antigravity_prompting.md` as needed:
* **TIER 1 (Epic Planner):** Use when planning large architectural changes or breaking down complex features into milestones.
* **TIER 2 (Execution Planner):** Use when executing an approved `implementation_plan.md` step-by-step securely.
* **TIER 3 (Single Operation):** Use for single file edits, bug fixes, refactoring, code quality audits, or seed data changes.

## 🚨 CONFIGURATION BACKUP PROTOCOL
**MANDATORY:** Whenever you are about to make changes to `backend_v2\seed\seed_data.json`, you MUST ALWAYS first:
1. Create a timestamped backup of the current state into the `backend_v2\seed\backups\` directory.
2. Clearly notify the user about *why* you are making the change and *what* exact changes you intend to make.
3. **WAIT for explicit confirmation from the user BEFORE applying any changes.** Do not proceed without permission.
