# Phase 1: Architecture Cleanup & SSOT Data Model (Clean Slate)

## Context
**Epic:** `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`

## Architectural Invariants
- **Rule 1:** The No-Legacy Mandate (`00-antigravity-core.md`). If data is missing, the system crashes. Fallbacks are banned.
- **Rule 2:** Opaque Stripe ID Mandate (`01-python-backend.md`). Use entropy for ephemeral IDs (e.g. nanoid) to avoid collision.
- **Rule 3:** Strict Pydantic V2 Rust (`01-python-backend.md`). `model_config = ConfigDict(extra='forbid', strict=True)`.
- **Rule 4:** Cross-Language Enum Parity. If Enums or Literals change in Pydantic, they MUST be mirrored in `client_app_v2/lib/core/models/enums.dart`.

## Targets (Modify)
- `c:\src\quorum\backend_v2\seed\atomization_cache.json` (DELETE)
- `c:\src\quorum\backend_v2\services\orchestrator\atomizer.py`
- `c:\src\quorum\backend_v2\models\v2_core.py`
- `c:\src\quorum\backend_v2\seed\run_seed.py`

## Context (Read-Only)
- `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Milestones
### 1. [x] Destroy `atomization_cache.json`
- Delete the file entirely from `backend_v2/seed/atomization_cache.json`.

### 2. [x] Neutralize `PromptAtomizer`
- File: `backend_v2/services/orchestrator/atomizer.py`
- Remove LLM API calls entirely.
- Replace logic with pure O(1) mapping that reads TDA assertions set by experts and creates ephemeral IDs using cryptic entropy (e.g., short UUID/nanoid) following the Opaque Stripe ID format (`tda_a1b2c3d4`). Do NOT use sequential indexes.

### 3. [x] Database Schema and Pydantic Models Update
- File: `backend_v2/models/v2_core.py`
- Purge the `micro_atoms` field from all models.
- Retain matrix-specific `ai_description` (str), but treat it purely as XML System Prompt / Agent Persona.
- Create new sub-model `TDAAssertion`:
  ```python
  class TDAAssertion(BaseModel):
      model_config = ConfigDict(extra='forbid', strict=True)
      tda_id: str
      ai_rule_description: str
      inverse_evidence: bool
      aggregation_mode: Literal['EXISTS', 'ALL_MUST_COMPLY']
      
      @model_validator(mode='after')
      def validate_math_logic(self):
          if self.inverse_evidence and self.aggregation_mode == 'ALL_MUST_COMPLY':
              raise ValueError("Käänteinen sääntö (myrkyn etsintä) vaatii EHDOTTOMASTI 'EXISTS' -aggregaation...")
          return self
  ```
- Update Cell's `Claim` model to use `tda_assertions: list[TDAAssertion] = Field(min_length=1)`.
- Ensure ALL Pydantic models have `model_config = ConfigDict(extra='forbid', strict=True)`. Remove any Pydantic on-the-fly corrections (like `alias` or `@model_validator(mode='before')` for hallucinated keys).
- **Two-Tier Firewall implementation:**
  - **Syntax Firewall (Pre-Pydantic):** Clean LLM Markdown wrappers (e.g. ```json) using a pure Python Regex pre-processor *before* feeding data to Pydantic to prevent Rust-core `JSONDecodeError` crashes.
  - **Schema Firewall (Pydantic V2):** Feed pure JSON directly to `DTO.model_validate_json()`. Ensure the DTO models officially define a `reasoning_trace: str` field so the LLM can "think out loud" without tripping the `extra='forbid'` rule.
- **Hydration Mandate:** Absolutely no `.get()` fallbacks. All incoming JSON must be hydrated using Pydantic's `.model_validate()` command.

### 4. [x] `run_seed.py` Lightening
- File: `backend_v2/seed/run_seed.py`
- Remove LLM client initializations. The seeder must load TDA-compatible clean test data from `seed_data.json` directly into the database without AI.

## Testing & Quality Gate Plan
- [x] **Unit Tests:** `tests/unit/test_atomizer.py`, `tests/unit/test_v2_core_validation.py` to test ID format and strictly forbid parameters.
- [x] **Execution:** Run `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi`
- [x] **Execution:** Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/atomizer.py backend_v2/seed/run_seed.py --test`

## Documentation Update
- [x] Note the data model and `TDAAssertion` replacement in `c:\src\quorum\docs\architecture\06_evaluation_and_scoring.md` (or relevant architecture document).

---
**Session Handover:**
To execute this plan, start a NEW chat session and run: `/tier2-hardening-backend @[c:\src\quorum\docs\epic\tasks_epic48\phase1_clean_slate.md]`
