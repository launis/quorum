# Phase 2: Theoretical Anchoring & Inverse Logic

## Context
**Epic:** `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`

## Architectural Invariants
- **Rule 1:** Zero-Legacy Mandate (`00-antigravity-core.md`). Do not create migration scripts. Replace the file entirely.
- **Rule 2:** PromptCompiler Immutability (`01-python-backend.md`). The file `prompt_compiler.py` is a frozen architectural cornerstone. **USER CONFIRMATION IS MANDATORY** before making modifications.
- **Rule 3:** No Naked Dicts (`01-python-backend.md`). Always use strict Pydantic V2 schemas.

## Targets (Modify)
- `c:\src\quorum\backend_v2\seed\seed_data.json`
- `c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler.py`

## Context (Read-Only)
- `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Milestones
### 1. [x] New `seed_data.json`
- File: `backend_v2/seed/seed_data.json`
- Replace `micro_atoms` structures with new `tda_assertions` structures according to the `TDAAssertion` model defined in Phase 1. 

### 2. [x] Matrix-Level System Prompt
- Enforce `PromptBlock.ai_description` usage exclusively as a static System Prompt via Hybrid Prompting.

### 3. [x] Inverse Logic Injection in PromptCompiler
- File: `backend_v2/services/orchestrator/prompt_compiler.py`
- **WARNING:** Before altering `prompt_compiler.py`, the executing agent MUST ask the user for permission.
- Read the `inverse_evidence` flag. If true, inject the rule: *"This is an inverse rule (Vice). If rule_satisfied = True (no issues found), evidence_found MUST be False and you must return an empty string "" for exact_quote. If rule_satisfied = False (violation found), evidence_found MUST be True and you MUST quote the exact violation."*

## Testing & Quality Gate Plan
- [x] **Integration Tests:** `tests/integration/test_prompt_compiler.py` to ensure inverse logic is correctly injected based on flag.
- [x] **Execution:** Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/prompt_compiler.py --test`

## Documentation Update
- [x] Note the structural changes to Seed data and PromptCompiler in architectural docs, specifically `c:\src\quorum\docs\architecture\09_data_persistence.md`.

---
**Session Handover:**
To execute this plan, start a NEW chat session and run: `/tier2-hardening-backend @[c:\src\quorum\docs\epic\tasks_epic48\phase2_theoretical_anchoring.md]`
