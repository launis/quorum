# Phase 3: Self-Healing Optimization (Epic 60)

Source: Epic 60, ACTION-2

## 1. Goal
Optimize the Self-Healing process by injecting the `strictness_level` directly into the schema healing prompt. This reduces retry loops when strictness is >= 100 by explicitly naming banned fields (like `contextual_override`).

## 2. Target Files
- `TARGET (Modify)`: `backend_v2/services/orchestrator/prompt_compiler.py`
- `TARGET (Modify)`: `backend_v2/services/llm_task_executor.py`
- `CONTEXT (Read-Only)`: `c:\src\quorum\docs\epic\epic_60_system2_reliability_audit.md`

## 3. Architectural Invariants & Hardening Mandates
- **[01-python-backend.md - prompt_compiler_immutability]**: "The Prompt Compiler is a frozen architectural cornerstone. Do NOT touch this file. If a change is absolutely necessary, you must explicitly flag it and seek USER CONFIRMATION..." **Note:** User confirmation was granted in the Epic ("Arkkitehtuuripoikkeus: prompt_compiler_immutability -säännön mukainen muokkauslupa myönnetty").
- **[hardening.xml - Rule 20 (the_self_healing_ban)]**: "Attempting to dynamically patch AI-generated quotes or JSON formatting errors on-the-fly using Regex is STRICTLY PROHIBITED." (This confirms we use the prompt-based self-healing instead of regex patching).

## 4. Implementation Steps

### Step 1: Update `PromptCompiler`
- Open `backend_v2/services/orchestrator/prompt_compiler.py`.
- Add `strictness_level: int | None = None` to the signature of `get_schema_healing_prompt()`.
- Inject the strictness override text if `strictness_level is not None and strictness_level >= 100`, explicitly banning 'contextual_override' and 'override_reason'. Follow the exact code snippet provided in ACTION-2.

### Step 2: Update `LLMTaskExecutor`
- Open `backend_v2/services/llm_task_executor.py`.
- In the schema error branch (around line 367), extract `strictness_level` from `validation_context` and pass it to `get_schema_healing_prompt()`.
- In the logical error branch (around line 419), extract `strictness_level` from `validation_context` and pass it to `get_schema_healing_prompt()`.

### Step 3: Documentation Update
- Update `c:\src\quorum\docs\architecture\05_llm_and_hooks.md` to document the new `strictness_level` awareness in the Self-Healing feedback loop.

## 5. Testing & Quality Gate Plan
- **Unit Tests:** Mock a validation error with `strictness_level=100` and assert the banned fields are present in the healing prompt string.
- **Universal Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`.

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/epic_60_tracker.md`
