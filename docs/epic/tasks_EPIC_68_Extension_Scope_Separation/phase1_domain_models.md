# Phase 1: Enum Scope Classification & Domain Model Refactoring

Source: Epic 68 Phase 1

## Architectural Laws (from .agents/rules & hardening.xml)
- **Rule 2 (Strict Pydantic V2 Rust):** `XaiExtensionScope` inherits `(str, Enum)`, Output Profile DTOs must use `V2CoreBase`'s strict validation. All new classes need `model_config = ConfigDict(strict=True, extra="forbid")`.
- **Rule 24 (Python 3.14 Modern Syntax):** Use modern bitwise unions (`X | None`), not `Optional[X]`. Use PEP 695 generics.
- **Rule 47 (Zero DB Hardcoding Mandate):** The `XAI_EXTENSION_SCOPE` dict will replace all hardcoded string comparisons.
- **Rule 55-59 (PEP 257 Google Style):** All new/modified classes and functions must include Summary, Attributes, Args, Returns, Raises.
- **Rule 78 & 85 Exception:** Note that EPIC 68 explicitly mandates renaming `visible_extensions` to `visible_block_extensions` and `visible_workflow_extensions`. This is a human-approved architectural change that supersedes the typical Zero Field Renaming/Schema Freeze rules.

## Target Files (Modify)
- `backend_v2/models/enums.py`
- `backend_v2/models/v2_core.py`
- `backend_v2/models/dtos/output_profile.py`
- `backend_v2/models/dtos/lightweight_matrix.py`
- `docs/architecture/01_backend_api_and_core.md`

## Context Files (Read-Only)
- `backend_v2/api/routers/system/workflow.py`
- `docs/epic/EPIC_68_Extension_Scope_Separation.md`

## Tasks

1. **`backend_v2/models/enums.py`**:
   - Introduce `XaiExtensionScope` class inheriting from `str, Enum`. Include `BLOCK = "block"` and `WORKFLOW = "workflow"`.
   - Add a module-level dictionary `XAI_EXTENSION_SCOPE: dict[XaiExtensionType, XaiExtensionScope]`.
   - Map `VARIANCE_VALIDATION` to `XaiExtensionScope.WORKFLOW`. Map all others (`CITATION`, `JUSTIFICATION`, `FALSIFICATION`, `THEORY_LINK`, `RISK_FLAG`, `COACHING`, `MISSING_CONTEXT`, `REMEDIATION_STEPS`, `EMOTIONAL_SENTIMENT`, `CONFIDENCE`, `SOURCE_ID`, `CONTEXTUAL_OVERRIDE`) to `XaiExtensionScope.BLOCK`.
   - Add PEP 257 Google-style docstrings.

2. **`backend_v2/models/v2_core.py`**:
   - In `OutputProfile` and `EmbeddedOutputProfile`, replace the `visible_extensions` field with:
     ```python
     visible_block_extensions: list[LaxXaiExtensionType] = Field(
         default_factory=list,
         description="Block-level XAI extensions (per-matrix, LLM-produced).",
     )
     visible_workflow_extensions: list[LaxXaiExtensionType] = Field(
         default_factory=list,
         description="Workflow-level global extensions (mathematical engines).",
     )
     ```

3. **`backend_v2/models/dtos/output_profile.py`**:
   - In `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`, and `OutputProfileResponseDTO`, replace `visible_extensions` with `visible_block_extensions` and `visible_workflow_extensions` just like in `v2_core.py`.

4. **`backend_v2/models/dtos/lightweight_matrix.py`**:
   - In `OutputProfileConfig`, replace `visible_extensions` with `visible_block_extensions` and `visible_workflow_extensions` in the same way.

5. **Documentation Update**:
   - Update `c:\src\quorum\docs\architecture\01_backend_api_and_core.md` to document the new `XaiExtensionScope` separation and the dual-list schema on `OutputProfile` variants.

## Testing & Quality Gate Plan
- **Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/models/ --openapi`

## Session Handover
To execute this phase, start a NEW chat session and run:
`/tier2-execute --target="c:\src\quorum\docs\epic\tasks_EPIC_68_Extension_Scope_Separation\phase1_domain_models.md"`
