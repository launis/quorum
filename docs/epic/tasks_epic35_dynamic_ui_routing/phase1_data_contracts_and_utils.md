# Epic 35 Phase 1: Data Contracts and Utils

## Context vs Target
*   **TARGET (Modify):** 
    *   `backend_v2/models/view/sdui.py`
    *   `backend_v2/models/dto/lightweight_matrix.py` (New)
    *   `backend_v2/utils/dict_utils.py`
    *   `tests/unit/utils/test_dict_utils.py` (New/Modify)
*   **CONTEXT (Read-Only):**
    *   `c:\src\quorum\docs\epic\epic35_dynamic_ui_routing.md`
    *   `.agents/rules/01-python-backend.md`

## Tasks

1.  **Strict Pydantic UI Contracts (`sdui.py`)**
    *   Update `sdui.py` to enforce `SduiBlockBase` with `block_type: str` discriminator.
    *   Implement `HeroInsightBlock` with `block_type: Literal["hero_insight"]`.
    *   Define polymorphic type `AnySduiBlock = Annotated[Union[HeroInsightBlock], Field(discriminator="block_type")]`.
    *   Ensure all models use `ConfigDict(frozen=True, strict=True, extra="forbid")`.

2.  **Lightweight Matrix DTO (`lightweight_matrix.py`)**
    *   Create `OutputProfileConfig` with `visible_extensions: list[XaiExtensionType]`.
    *   Create `LightweightMatrixOutput` mirroring the Phase 2 strict schema:
        *   `normalized_score: float = Field(ge=0.0, le=1.0)`
        *   `level_breakdown: str`
        *   `justification: str`
        *   `evaluated_atoms: dict[str, bool]`
        *   `extensions: dict[XaiExtensionType, str]`
    *   Strict config applied.

3.  **Safe Dot-Notation Parser (`dict_utils.py`)**
    *   Implement `resolve_dot_notation(state: Any, path: str) -> Any`.
    *   Must use strictly iterative lookup: `curr[part]` or `getattr(curr, part)`.
    *   Must catch `KeyError`, `AttributeError`, `IndexError` and raise `MissingInputMappingError` (RFC 7807) natively.
    *   **Prohibited:** `eval()`, `exec()`, `hasattr()`, `dict.get()`, `return None`. Zero duct tape allowed.

## Verification & Quality Gate Plan
*   **Unit Tests:** Implement robust testing in `test_dict_utils.py` verifying that invalid paths reliably crash with `MissingInputMappingError`.
*   **Audit Loop:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/models/view/sdui.py backend_v2/utils/dict_utils.py backend_v2/models/dto/lightweight_matrix.py --openapi --test`.
