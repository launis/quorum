# Phase 2: Backend Models (Pydantic-tason Mallit)

This sub-plan addresses **Phase 2: Pydantic-tason Mallit (Backend Schema Evolution)** from Epic 60. It updates the Pydantic schemas in the backend to support decoupled compositional fields, ensuring absolute Pydantic V2 type-safety and immediate fail-fast constraint execution.

## System Invariants & Rules
* **Rule 1: The Zero-Compromise Pledge (00-antigravity-core.md)**: Fallback logic, default union types (`| None`) to appease dirty DB states, and language-level defaults are banned. If configurations are incorrect, let the system CRASH loudly and early.
* **Rule 2: Pydantic Centralized Namespaces (01-python-backend.md)**: Class definitions and schemas must be centralized in `backend_v2/models/v2_core.py` to prevent OpenAPI generator naming collisions and Flutter compilation crashes.
* **Rule 3: Native Field Constraints Priority (01-python-backend.md)**: Prefer native `Field(pattern=...)` regex and structural validations in Rust (pydantic-core) rather than writing heavy Python-level field validators.

---

## Proposed Changes

### [Component: Backend Models]
We will modify the core `Step` class to replace the dynamic `prompt_blocks` list with segregated architecture references.

#### [MODIFY] [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)
* **Step 1 (Source: Epic Section 4.1)**: Refactor the fields in `class Step(V2CoreBase):` and replace `prompt_blocks: list[str]` with strictly typed decoupled composition fields.
  ```python
  # Targets c:\src\quorum\backend_v2\models\v2_core.py
  # Old:
  # prompt_blocks: list[str] = Field(
  #     default_factory=list, description="List of PromptBlock IDs containing directives and matrices for this step."
  # )
  # New:
  role_block_id: str | None = Field(
      default=None,
      pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
      description="Reference to role block (e.g. blk_role_critic)"
  )
  extraction_protocol_block_id: str | None = Field(
      default=None,
      pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
      description="Reference to global evidence extraction protocol block"
  )
  criteria_block_ids: list[str] = Field(
      default_factory=list,
      description="References to matrix or text blocks"
  )
  ```
* **Step 2 (Source: Epic Section 4.1)**: Refactor the `validate_step_consistency` model validator on `Step` to enforce strict zero-fallback constraints.
  ```python
  # Targets c:\src\quorum\backend_v2\models\v2_core.py
  @model_validator(mode="after")
  def validate_step_consistency(self) -> Step:
      """Strict fail-fast validation to ensure Step is structurally complete."""
      if self.type == "llm":
          if not self.model_strategy:
              msg = f"LLM Step '{self.slug}' must declare an explicit model_strategy (Zero-Fallback Rule)."
              raise ValueError(msg)
          if not self.criteria_block_ids:
              msg = f"LLM Step '{self.slug}' must define at least one criteria_block_id."
              raise ValueError(msg)
          if not self.extraction_protocol_block_id:
              msg = f"LLM Step '{self.slug}' must define a valid extraction_protocol_block_id."
              raise ValueError(msg)
      if self.type == "logic" and not self.hook:
          msg = f"Logic Step '{self.slug}' must define a native 'hook' execution target."
          raise ValueError(msg)
      return self
  ```

#### [MODIFY] [studio.py](file:///c:/src/quorum/backend_v2/models/dtos/studio.py)
* **Step 3 (Source: Epic Section 4.1)**: Ensure any subclass or DTO extending `Step` (such as `StepResponseDTO`) inherits the updated attributes correctly without schema drift or namespace collision.

---

## Testing & Quality Gate Plan

### Automated Verification
1. **Pydantic Validation Unit Tests**:
   Write/execute a test case verifying that creating an LLM step without `criteria_block_ids` or without an `extraction_protocol_block_id` triggers a strict Pydantic `ValidationError`.
   ```powershell
   uv run pytest backend_v2/tests/unit/test_api_seed_mutations.py -v
   ```
2. **OpenAPI and Audit Loop**:
   Run the centralized Python audit loop script to regenerate schemas and verify formatting alignment:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi --test
   ```

---

## Session Handover
To proceed, start a new chat session and run the following command to load the tracking context:
```powershell
/tier5-resume --target="docs/epic/EPIC_60_tracker.md"
```
