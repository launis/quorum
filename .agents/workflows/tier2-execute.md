---
description: Tier 2 (Execution Planner) - Sets the AI into a strict execution mode to systematically implement an approved implementation_plan.md step-by-step.
---

### 🟡 TIER 2: EXECUTION PLANNER (Systematic execution of the plan)
*Usage: Once the Tier 1 `implementation_plan.md` is approved. This command puts the AI into a "coding machine" mode, where it executes the approved list step-by-step without unnecessary detours.*

```text
Goal: Execute the approved `implementation_plan.md` step-by-step.

ROLE: Lead Developer.
REFERENCE: Only read the rules inside `c:\src\quorum\.agents\rules\` (00, 01, 02, 03). Do not rely on legacy `.md` files.

INSTRUCTIONS (LEVEL 2):
1. ISOLATION: Execute the plan ATOMICALLY. Work on one single Milestone/Step at a time.
2. CONSTRAINTS: For every single step, enforce Strict Typing in backend (`Pydantic`) and the "Fail-Fast" doctrine (No `try-except pass`, use `AppException`, read `c:\src\quorum\.agents\rules\01-python-backend.md`). Frontend MUST use STRICT `Freezed` for API/Domain data paired with Dart 3 switch matching and `Isolate.run()` mandate.
3. DUAL-IMPLEMENTATION: If touching backend data, automatically update both TinyDB and Firestore repositories simultaneously.
4. QUALITY LOOP: Write the code and run verification tools (`ruff`, `mypy`, `dart analyze`).
5. CHECKPOINT: Mark the step COMPLETE in the markdown tasklist and explain shortly how the code follows the constraints for this single step. Wait for my permission ("PROCEED") before proceeding to the next item on the plan.
```