# Implementation Plan: Phase 1 - Micro-CoT & Polymorphic Schema (EPIC 56)

## 1. Goal
Implement the core `BaseTDAExtraction` Pydantic model to enforce the new Micro-CoT (Chain of Thought) structure.

## 2. Architectural Rules & Invariants
- **Rule 1: No Naked Dicts / The Zero Compromise Pledge**: Strict Pydantic V2 validation must be enforced (`ConfigDict(strict=True, extra='forbid')`). No `.get("default")` fallbacks.
- **Rule 2: Fail-Fast Hydration**: Pydantic models must instantly throw a `ValidationError` if data is malformed.
- **Rule 3: TDD Mandate**: Strict unit testing is required before marking this complete. Tests must use `backend_audit_loop.py`.
- **Source**: Epic Phase 1 & Phase 5 (Test 4).

## 3. Implementation Steps

### Step 1: Implement `BaseTDAExtraction`
**Target File**: `backend_v2/models/v2_core.py` (or appropriate model file)
- Implement `BaseTDAExtraction` inheriting from `BaseModel`.
- Set `model_config = ConfigDict(frozen=True, strict=True, extra='forbid')`.
- Define the following fields exactly as mandated:
  - `step_1_evidence_scan: str = Field(description="Listaa havainnot ja lainaukset, jotka tukevat säännön täyttymistä (dokumentin kielellä).")`
  - `step_2_mitigating_context: str = Field(description="Listaa havainnot, jotka kumoavat säännön tai ovat poikkeuksia (dokumentin kielellä).")`
  - `contextual_override: bool = Field(description="Aseta True VAIN, jos fyysistä sanatarkkaa lainausta ei ole olemassa, mutta asiayhteys absoluuttisesti todistaa säännön. Älä käytä laiskuuden takia.")`
  - `exact_quote: str | None = Field(max_length=1500, description="Sanatarkka lainaus alkuperäisestä tekstistä. Pakko olla Null, jos override on True.")`
  - `extracted_data: Any = Field(description="Spesifit poimitut arvot (boolean, taulukko, päivämäärä).")`
- Add `@model_validator(mode='after')` named `validate_override_logic`:
  - Must raise `ValueError("Cross-validation failed: exact_quote MUST be null if contextual_override is True.")` if `contextual_override` is True and `exact_quote` is not None.

### Step 2: System Instructions Update
**Target File**: `backend_v2/services/orchestrator/prompt_compiler.py` (or where the instruction is defined)
- Update generation instructions to mandate that the model produces `step_1` and `step_2` in the target document's original language, while keys remain in English.

### Step 3: TDD Tests
**Target File**: `tests/unit/models/test_micro_cot_override.py` (New file)
- **`test_contextual_override_cross_validation`**: 
  - Provide a JSON payload with `contextual_override=True` and `exact_quote="Löytyi lainaus"`.
  - Assert that `.model_validate()` throws a `ValidationError` / `ValueError` because of the cross-validation failure.

### Step 4: Documentation Update
**Target File**: `docs/architecture/domain/api_models_and_schemas.md`
- Document the new `BaseTDAExtraction` schema and its Fail-Fast cross-validation rules.

## 4. Scoping
**TARGET (Modify)**: `backend_v2/models/v2_core.py`, `tests/unit/models/test_micro_cot_override.py`
**CONTEXT (Read-Only)**: `backend_v2/services/orchestrator/prompt_compiler.py`

## 5. Testing & Quality Gate Plan
- **UNIT TESTS**: Execute `test_contextual_override_cross_validation` via `pytest`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test`.

---
*Session Handover: To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_56_vaihtoehtob_tracker.md`*
