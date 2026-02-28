# COGNITIVE QUORUM - ANTIGRAVITY SYSTEM BOOTSTRAP (V5.1)

## TO THE AI AGENT:
You are operating within the **Cognitive Quorum** monorepo (Python 3.14+ Backend, Flutter/Riverpod Client). This is a highly mature **Phase 9 Hardening** environment built on strict **Clean Architecture**.

Your operational mandate is to strictly enforce pre-established architectural laws. Do not invent new patterns. Do not guess.

### 1. INITIALIZATION PROTOCOL (MUST DO FIRST)
1. **Check KI Summaries**: You have access to Knowledge Items (KIs). **ALWAYS** scan them first for architectural patterns before writing implementation plans.
2. **Read the Manifesto**: Read `docs/flutterpromptohje.md`. For Data management, read `docs/data_management.md`.
3. **Verify via Logs**: Use your terminal capabilities (`get-content backend_debug.log`, `pytest`) before making assumptions about crashes.

### 2. CORE ARCHITECTURAL LAWS (LINK LIST & MANDATES)
These are absolute, non-negotiable rules. If you break these, the system will fail.

* **[System Architecture](architecture.md)**: "Zero-Magic", Strict DTOs, RFC 7807 Fail Fast error handling.
* **[Backend Mandates](STRICT MANDATES & ARCHITECTURE PRINCIPLES.md)**: Python 3.14+, FastAPI, SSOT (seed_data.json), Service/Repository layers, Pydantic `extra="ignore"`. 
* **[Frontend Mandates](STRICT FRONTEND MANDATES & ARCHITECTURE PRINCIPLES.md)**: Riverpod 3.0, Matrix UI Approach, SDUI (Server-Driven UI) Graceful Degradation.
  * **Routing**: Only `GoRouteData` type-safe routes allowed. No string-based `context.go()`.
  * **I18N No-String Mandate**: UI translations happen ONLY in `.arb` files using ICU syntax. Zero backend translations, zero Dart string concatenations.
* **[API Models & SDUI](api_models.md)**: The Backend provides data and enums. The Frontend provides presentation and translation.
* **[Flutter Prompts](flutterpromptohje.md)**: Overarching constraints and deep-dive links.

### 3. YOUR WORKFLOW
1. **Analyze**: Use `grep_search` and `find_by_name` to map the codebase.
2. **Plan**: Write your step-by-step strategy to `implementation_plan.md` and use the `notify_user` tool to request my approval for structural changes.
3. **Execute & Test**: Write the code, run standard tests (`pytest backend/tests/`, `flutter analyze`), and ensure 0 regressions.

**CONFIRMATION:**
Reply in Finnish: "Ymmärretty. Antigravity V5.1 säännöt ladattu. Mikä on tämän istunnon tavoite?"
