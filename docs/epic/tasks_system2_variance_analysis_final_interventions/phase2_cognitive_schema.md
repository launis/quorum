# Implementation Plan: Phase 2 - Unified Cognitive Schema & Provenance Forcing

## Goal
Restructure the evaluation steps in the Pydantic schemas to align with the autoregressive cognitive pipeline, and implement dynamic runtime validation that limits `source_document_ids` strictly to the documents present in the active workspace.

## User Review Required
> [!IMPORTANT]
> **Rule 84 Override Activated:** This plan alters the fields and structural signatures of `StepDTOStrict` and `StepDTOSemantic` in `evaluation_steps.py`, which is locked under Rule 84 (`pydantic_schema_freeze_mandate`). This override is authorized by Section 7.1 of the Epic because the variance analysis requires restructuring these schemas to prevent LLM cognitive collapse.

## Proposed Changes

---

### Component: Pydantic Evaluation DTOs

#### [MODIFY] [evaluation_steps.py](file:///c:/src/quorum/backend_v2/models/dtos/evaluation_steps.py)
- **Changes**:
  - Restructure `StepDTOStrict` to inherit from `BaseExtractionDTO` and define only the following fields in this exact order:
    1. `rule_internalization: str` - Brief internalization of criteria.
    2. `source_document_ids: list[str]` - Dynamic literals corresponding to available documents.
    3. `exact_quotes: list[str]` - Verbatim quotes in original language.
    4. `reasoning_steps: str` - Step-by-step mechanical trace.
    5. `falsification_argument: str` - Counter-argument validation.
    6. `decision: bool` - Strict binary compliance decision.
    7. `semantic_reasoning: str` - Short summary statement.
  - Define `StepDTOSemantic` to inherit from `StepDTOStrict`, adding only the contextual override fields at the end:
    - `contextual_override: bool = Field(default=False, ...)`
    - `override_reason: str | None = Field(default=None, ...)`
  - Delete all legacy unused fields (`structural_location`, `localized_anchors_found`, `counter_quote`).
  - *(Source: Epic Section 2.11, 2.13)*

---

### Component: Dynamic Schema Factory

#### [MODIFY] [schema_factory.py](file:///c:/src/quorum/backend_v2/services/orchestrator/schema_factory.py)
- **Changes**:
  - Update `build_dynamic_schema` signature to accept `source_document_ids: list[str] | None = None`.
  - In `build_dynamic_schema`, include `source_document_ids` in the `cache_key` formatting (e.g. by sorting and joining them) to avoid cache collisions.
  - During dynamic model construction (`_build_dynamic_schema_internal`), if `source_document_ids` is provided, create a dynamic `Literal` type representing the document choices:
    ```python
    from typing import Literal
    # Ensure there is at least one choice (e.g. fallback to "N/A" if empty)
    choices = list(set(source_document_ids or []))
    if not choices:
        choices = ["N/A"]
    elif "N/A" not in choices:
        choices.append("N/A")
    DocIdsLiteral = Literal[tuple(choices)]
    ```
  - Use `pydantic.create_model` to generate dynamic subclasses of `StepDTOStrict` or `StepDTOSemantic`, overriding `source_document_ids` with type `list[DocIdsLiteral]` to force Vertex AI JSON Schema enum constraints.
  - *(Source: Epic Section 2.8)*

## Hardening Constraints
- **Rule 2 (`strict_pydantic_v2_rust`)**: Ensure all schemas run with strict Pydantic V2 configurations.
- **Rule 54 (`pep257_google_style_docstrings`)**: Ensure clear Google-style docstrings for all modifications.

## Verification Plan

### Automated Tests
Execute the schema factory and evaluation steps unit tests:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/schema_factory.py backend_v2/models/dtos/evaluation_steps.py --test
```
*Note: If existing test assertions check for deleted fields (like `structural_location` or `counter_quote`), rewrite the test files in accordance with the TDD/Anti-Trap mandate.*

### Documentation Update
Update [docs/architecture/sdui_and_display_tier.md](file:///c:/src/quorum/docs/architecture/sdui_and_display_tier.md) to explain the dynamic Literal validation constraint on `source_document_ids`.

## Session Handover
To execute this plan in the next session:
```powershell
/tier2-execute --target docs/epic/tasks_system2_variance_analysis_final_interventions/phase2_cognitive_schema.md
```
