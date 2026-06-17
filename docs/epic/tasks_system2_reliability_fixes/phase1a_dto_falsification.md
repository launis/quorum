# Epic: System 2 Reliability Fixes - Phase 1A: DTO Falsification

**Source:** Epic Phase 1, Step 1

## Goal
Implement the "Devil's Advocate" (Falsification Attempt) within the evaluation DTOs to force the LLM into System 2 cognition and mitigate "Yes Man" bias (False Positives).

## Target Files
- `[MODIFY] c:\src\quorum\backend_v2\models\dtos\evaluation_steps.py`

## Context Files
- `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py`

## Architectural Invariants & Hardening Mandates
- **Zero-Compromise Pledge:** Strict Pydantic validation is absolutely mandatory.
- **Fail-Fast Hydration:** Models must enforce `strict=True` and `extra="forbid"`.
- **System 2 Cognition & Yes-Man Bias Destruction (from Context Handover):** Forcing a `falsification_argument` JUST BEFORE the final decision-boolean forces System 2 cognition and destroys False Positives at the logit level autoregressively.
- **Rule 2 from hardening.xml:** Enforce `.model_validate()`. All NEW classes MUST define `model_config = ConfigDict(strict=True, extra="forbid")`. (Note: for existing classes, don't break existing configs per Rule 85).
- **Rule 77 from hardening.xml:** Zero Field Renaming Mandate. NEVER autonomously rename existing Pydantic model fields.

## Implementation Steps

### 1. Update DTO Models (`evaluation_steps.py`)
Modify `StepDTOStrict` and `StepDTOSemantic` to include the new falsification field.
- **Field:** `falsification_argument: str`
- **Location:** Must be placed exactly BEFORE the `decision: bool` field.
- **Pydantic Description:** "Why this evidence might NOT satisfy the strict causal requirement of the rule."

### 2. Update Documentation
- **Target:** `c:\src\quorum\docs\architecture\system_quality_standards.md` (or relevant architecture doc)
- Add documentation about the System 2 Cognitive Falsification field and how it prevents LLM bias by forcing negative tokens to be generated before the boolean decision.

## Testing & Quality Gate Plan
- **Unit Tests:** No new unit tests strictly required for DTO property addition, but must run the backend audit loop to ensure Pydantic parsing isn't broken.
- **Quality Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/evaluation_steps.py --test`
- **OpenAPI Schema Gen:** Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/evaluation_steps.py --openapi` if required.

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_system2_reliability_fixes_tracker.md`
