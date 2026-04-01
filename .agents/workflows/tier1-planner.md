---
description: Tier 1 (Epic Planner) - Creates a detailed milestone breakdown and implementation_plan.md for large architectural changes without writing code.
---

### 🟢 TIER 1: EPIC PLANNER (Planning a large change)
*Usage: At this tier, the goal is to break down one large entity (multiple files, new agent) into an `implementation_plan.md` and generate several more detailed plans / milestones before writing any code.*

```text
Goal: [WRITE GOAL. Ex: "Design and implement a new reporting module and UI"]

ROLE: Principal Solutions Architect
REFERENCE: Only read the rules inside `c:\src\quorum\.agents\rules\` (00, 01, 02, 03). These are the absolute law. Do not rely on legacy `.md` files.

INSTRUCTIONS (LEVEL 1):
1. READ: Do NOT write code yet. Familiarize yourself with the architectural laws from `c:\src\quorum\.agents\rules\`.
2. PLAN: Create an `implementation_plan.md` breaking this goal into several smaller independent Milestones.
3. SEQUENCE: Every milestone MUST strictly follow the V2 architecture sequence (Dependencies -> Pydantic Models -> L10n -> Repo -> API -> Frontend Controller -> UI). Note: Frontend domain data MUST NOT use generated models.
4. UI/UX SCOPING (DESKTOP-FIRST): Remember the Frontend is an IDE-like Desktop-Class Pro Tool. Plan for PC constraints first (>1200dp Three-Pane Layouts, 2D Infinite Canvas, high information density), and gracefully degrade to mobile.
5. SCOPING: Explicitly map which files are `TARGET (Modify)` and which are `CONTEXT (Read-Only)`.
6. VERIFICATION PLAN: You MUST include a "Verification & Quality Gate Plan" at the end of the `implementation_plan.md`. Explicitly list which new unit test files (pytest/flutter test) will be created, and state that the correct Universal Quality Gate tools (Ruff/Mypy/OpenAPI/Dart/build_runner) will be executed for these changes.
7. PAUSE: Present the plan and WAIT for explicit approval ("PERMISSION GRANTED"). Do not implement anything.
```