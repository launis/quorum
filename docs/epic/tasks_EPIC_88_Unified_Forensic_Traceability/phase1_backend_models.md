# Phase 1: Backend DTO Models & CoT

Source: Epic Phase 1 & 3.1

## Target Files (Modify)
- `backend_v2/models/dtos/v2_core.py`
- `backend_v2/models/domain/mcp.py`

## Context Files (Read-Only)
- `backend_v2/models/dtos/lightweight_matrix.py`

## Requirements
1. **EvidenceQuoteDTO**: In `v2_core.py`, implement `EvidenceQuoteDTO` inheriting from `V2CoreBase`.
   - `id`: Opaque Stripe ID `evq_xxxx`.
   - `text`: str
   - `source_reference`: str | None
   - `user_rejected`: bool = False
   - `rejection_reason`: str | None
   - `is_mcp_verified`: bool = False
   - `used_evidence_ids`: list[str] | None (use `@field_validator(mode="before")` to sanitize `None` to `[]` and `str` to `[str]`).
2. **LevelQuotesDTO & RowForensicsDTO**: In `v2_core.py`, implement `LevelQuotesDTO` and `RowForensicsDTO`.
   - `LevelQuotesDTO`: `quotes: list[EvidenceQuoteDTO] | None` (Evidence-First Forcing: place BEFORE `level`), `level: int`, `level_name: str`. Use `@field_validator("quotes", mode="before")` to sanitize `None` to `[]`.
   - `RowForensicsDTO`: `level_quotes: list[LevelQuotesDTO] = Field(...)`. Add `@computed_field all_evidence_rejected` (returns True if len > 0 and all quotes have `user_rejected == True`).
   - *Note: Remember Rule 85: `@computed_field` must be placed ABOVE `@property` with `# type: ignore[prop-decorator]`.*
3. **MCPAuditTrace & CitationExtractionItemDTO**: In `mcp.py`, update these models to include structural CoT:
   - `knowledge_gap`: str
   - `search_rationale`: str
   - *This forces the LLM to justify the external tool call before executing it.*

## Architectural Invariants & Hardening Mandate
- **Rule 25 (opaque_stripe_id_mandate)**: Use opaque `evq_xxxx` ID.
- **Rule 2 (strict_pydantic_v2_rust)**: Use `ConfigDict(strict=True, extra="forbid")` for new classes.
- **Rule 24 (python_314_modern_syntax)**: Use `list[str] | None` instead of `Optional[List[str]]`.
- **Rule 85 (pydantic_v2_computed_field_order)**: `@computed_field` above `@property`.

## Documentation Update
Update `docs/architecture/02_domain_models.md` to document the new `EvidenceQuoteDTO` and its role in Forensic Traceability.

## Testing & Quality Gate Plan
- **Unit Tests**: Add tests in `tests/unit/models/dtos/test_v2_core.py` to verify `EvidenceQuoteDTO` ID generation, `all_evidence_rejected` logic, and `None` sanitization via field validators.
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/v2_core.py backend_v2/models/domain/mcp.py --test`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
