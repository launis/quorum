# 🔥 COGNITIVE QUORUM - ANTIGRAVITY BOOTSTRAP (V4.0) 🔥
> **KÄYTTÄJÄLLE:** Aloita uusi istunto sanomalla: "Lue docs/alku.md ja [kerro tämän päivän tavoite]". Tämä tiedosto toimii päävirtakytkimenä tekoälyn kontekstiin.

---

## TO THE ANTIGRAVITY AGENT (GEMINI 3.1+):
You are activating within the **Cognitive Quorum** monorepo (Python Backend + Flutter Client). This is a highly mature **Phase 8/9 Hardening** environment.

Your goal is NOT to guess how things work. Your goal is to strictly follow the pre-established architectural mandates.

### 1. 🚨 MANDATORIES BEFORE CODING (The "Think First" Protocol) 🚨
Before you write any code or propose solutions, you MUST perform these actions:
1. **Check KI Summaries**: You have access to Knowledge Items (KIs) from previous sessions. **ALWAYS** scan them first (e.g., SDUI standards, Seeding protocols) if the task touches complex logic.
2. **Review the Manifesto**: If you are unsure about a rule, use `view_file` on `docs/flutterpromptohje.md`. That is the **Absolute Authority** (The "System Architecture Manifesto").
3. **Verify the State**: Check the `backend_debug.log` and `client_debug.log` using standard log analysis tools before asking the user why something crashed.

### 2. CORE ARCHITECTURAL LAWS (Non-Negotiable)
Violating any of these will result in an immediate architectural failure.

*   **Pydantic V2 Strict (No dicts)**: Every data structure moving between backend services/agents MUST be a strongly typed Pydantic Domain Model (`ConfigDict(strict=True)`). Return types of `dict` are banned.
*   **Fail Fast (RFC 7807)**: Never use `try-except pass` or return `None` to silence errors in core logic. If data is dirty or missing, raise an `AppException` immediately.
*   **SSOT (Single Source of Truth)**: `backend/seed/seed_data.json` defines ALL models, limits (tokens), and workflows. NEVER hardcode limits or configs directly in Python classes. Use `run_seed.py` to reset the database.
*   **Zero-Fallback**: Downstream code must trust the structure. If the AI returns 101 on a 1-100 scale, the backend must CRASH, not clamp the value silently.
*   **Client (Flutter)**: Strictly `Riverpod 3.0` (Generator), Hooks, and Immutable models. `ChangeNotifier` and manual routing are banned.

### 3. YOUR WORKFLOW IN THIS PROJECT
When given a task:
1.  **Analyze**: Use your file search tools (`grep`, `list_dir`) to find where the logic lives. Read the corresponding `docs/*.md` file if you encounter a new domain (e.g. `docs/workflow_data_architecture.md`).
2.  **Plan**: Propose your fix in `implementation_plan.md` and wait for user approval if the change touches core schemas.
3.  **Execute & Verify**: Make the change, and verify via logs or local tests.

**CONFIRMATION:**
Acknowledge that you have internalized these Phase 8/9 constraints and wait for the user's specific objective. Respond in Finnish (Suomi).
