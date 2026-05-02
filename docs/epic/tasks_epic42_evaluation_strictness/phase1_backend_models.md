# Epic 42: Phase 1 - Backend Models & Cache Hashing

## Tavoite
Enforce "Zero Defaults" strategy for strictness_level in DTOs and Database models. Define the strict Zero-Trust `AtomResponse` Pydantic schema with Anti-Laziness mandates. Update Execution Cache key generation.

## Architectural Laws (Must Follow)
- **Rule 1: The Zero Compromise Pledge.** Enforce strict Pydantic V2 schemas. Zero Tolerance for silent bypasses or guessing.
- **Rule 2: No Legacy Fallbacks.** NEVER bypass Pydantic `extra='forbid'` strictness. Do not use optional union types `| None` to silently appease old data.
- **Rule 3: Opaque Stripe ID Mandate.** Enforce `wor_...`, `usr_...` identifiers.

## Proposed Changes

### 1. `backend_v2/models/v2_core.py`
**TARGET (Modify)**

#### `ExecutionCreate` DTO
- [NEW] Add `strictness_level: int = Field(..., ge=0, le=100)`
- Ensure no defaults are provided (Fail-Fast Hydration).

#### `ExecutionRecord` Model
- [NEW] Add `strictness_level: int = Field(...)` (Must be non-nullable)

#### `ReportDataDTO` Model
- [NEW] Add `strictness_level: int = Field(...)` (Must be non-nullable)

### 2. `backend_v2/services/orchestrator/prompt_compiler.py`
**TARGET (Modify)**

#### `EvidenceType` Enum
- [NEW] Create `EvidenceType(str, Enum)` with values `EXPLICIT_QUOTE`, `IMPLIED_INTENT`, `NO_EVIDENCE` inside `prompt_compiler.py` (top level).

#### `AtomResponse` Schema Redefinition
- Inside `build_blind_evaluation_schema` and `_cached_build_dynamic_schema` (where `AtomResponse` is dynamically defined):
  - Replace `quote`, `reasoning`, `boolean` with the Zero-Trust Alphabetical keys:
    - `step_1_evidence_type: EvidenceType = Field(..., description="CRITICAL: You MUST choose your strategy first.")`
    - `step_2_quote: str | None = Field(default=None, description="Required if evidence_type is EXPLICIT_QUOTE. The exact verbatim quote.")`
    - `step_3_implicit_justification: str | None = Field(default=None, description="Required ONLY if evidence_type is IMPLIED_INTENT. Provide an exhaustive 20+ word justification to prove the implied intent.")`
    - `step_4_reasoning: str = Field(..., description="Final cognitive friction and evaluation reasoning.")`
    - `step_5_boolean: bool = Field(..., description="The final True/False decision.")`
  - Ensure `atom_id` remains unchanged.
  - [NEW] Add `@model_validator(mode='after')` inside `AtomResponse`:
    - Validates that if `step_1_evidence_type == EXPLICIT_QUOTE`, `step_2_quote` is not empty.
    - If `step_1_evidence_type == IMPLIED_INTENT`, `step_3_implicit_justification` must not be empty AND `len(step_3_implicit_justification.split()) >= 20` (Raise `ValueError("ANTI-LAZINESS MANDATE: Justification too short...")`).
    - Also inside `IMPLIED_INTENT`: Check if `info.context` (ValidationInfo context) has `strictness_level >= 70`, if so, raise `ValueError("Strictness >= 70 ei salli implisiittistä logiikkaa")`.
    - If `step_1_evidence_type == NO_EVIDENCE`, ensure `step_5_boolean` is `False`.

### 3. Execution Cache Hashing
**TARGET (Modify)**
- Find the `execution_cache` module (e.g., `backend_v2/services/execution_cache.py` or similar). If not found, locate where caching is implemented and ensure `strictness_level` is a mandatory component of the cache key hash. Note: Since we haven't found the file yet, during execution the agent must use `grep_search` to find "execution_cache" and update the hash generation logic to `hash(document_id + atom_id + prompt_version + strictness_level)`.

## Verification & Quality Gate Plan
- Verify new fields are required in Pydantic.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/[TARGET_FILES] --openapi`
- Run Pytest. Fix any tests that fail due to missing `strictness_level` in test mocks.
