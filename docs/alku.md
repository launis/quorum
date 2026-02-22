# COGNITIVE QUORUM - ANTIGRAVITY SYSTEM BOOTSTRAP (V5.0)

## TO THE AI AGENT:
You are operating within the **Cognitive Quorum** monorepo (Python 3.14+ Backend, Flutter/Riverpod Client). This is a highly mature **Phase 9 Hardening** environment. 

Your operational mandate is to strictly enforce pre-established architectural laws. Do not invent new patterns. Do not guess.

### 1. INITIALIZATION PROTOCOL (MUST DO FIRST)
1. **Check KI Summaries**: You have access to Knowledge Items (KIs). **ALWAYS** scan them first for architectural patterns before writing implementation plans.
2. **Read the Manifesto**: Read `docs/flutterpromptohje.md`. For Data management, read `docs/data_management.md`.
3. **Verify via Logs**: Use your terminal capabilities (`cat backend_debug.log` or running `pytest`) before making assumptions about crashes.

### 2. CORE ARCHITECTURAL LAWS (NEVER VIOLATE)
* **The Strict DTO Pattern**: Pydantic models must be isolated. LLM input/output relies exclusively on pure DTOs without system metadata. Domain models inherit from DTOs. `id` fields must use strict types (e.g. `UUID` or `NewType`), never loose strings.
* **Fail Fast (RFC 7807)**: Never use `try-except pass` or return `None` to silence core domain errors. Raise an `AppException` immediately.
* **Database SSOT**: `backend/seed/seed_data.json` is the Single Source of Truth for models, config, and workflows. Do not hardcode configurations in Python classes.
* **BFF/UI Resilience (Dual-Reporting)**: While the Domain MUST fail fast, the BFF (Transformers) and Frontend MUST gracefully degrade (e.g., render empty widgets). **CRITICAL:** Every silent UI recovery MUST be logged via `logger.warning` or `debugPrint` for developer visibility.
* **Client (Flutter)**: Strictly `Riverpod 3.0` (Generator), Hooks, and Immutable models. `ChangeNotifier` and manual routing are banned.

### 3. YOUR WORKFLOW
1. **Analyze**: Use `grep_search` and `find_by_name` to map the codebase.
2. **Plan**: Write your strategy to `implementation_plan.md` and use the `notify_user` tool to request my approval for structural changes.
3. **Execute & Test**: Write the code, run standard tests (`pytest backend/tests/`), and ensure 0 regressions.

**CONFIRMATION:**
Reply in Finnish: "Ymmärretty. Antigravity V5.0 säännöt ladattu. Mikä on tämän istunnon tavoite?"
