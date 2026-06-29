# Phase 1: Backend DTO Modernization & Clustering Foundation

Source: Epic 88, Steps 1 and 5.

## Proposed Changes

### Target Files
- `backend_v2/models/v2_core.py`
- `backend_v2/models/dtos/report.py`

### Context Files
- `backend_v2/models/state.py` (For ReasoningStepDTO)

### Task Details
1. **Remove Legacy DTOs**: 
   - [DELETE] `EvidenceQuoteDTO`, `LevelQuotesDTO`, and `RowForensicsDTO` from `backend_v2/models/v2_core.py` (or their current location).
2. **DTO Firewall (Explicit Inclusion)**:
   - [NEW] Create `ScorecardAtomDTO(V2CoreBase)` in `v2_core.py` (or appropriate DTO file). This acts as a firewall, only including presentation fields:
     ```python
     class ScorecardAtomDTO(V2CoreBase):
         atom_id: str
         level: int                   
         level_name: str              
         claim_label: str             
         extracted_facts: dict[str, str | None]
         exact_quotes: list[str]
         internal_logic_en: ReasoningStepDTO
         status: str | None
         semantic_reasoning: str
         contextual_override: bool
         structural_location: str
     ```
3. **MatrixScorecardRowDTO Update & Purity Paradox Resolution**:
   - [MODIFY] In `v2_core.py`, update `MatrixScorecardRowDTO` to remove V1 fields (`quotes_list`, `row_forensics`) and replace them with:
     ```python
     evaluated_atoms: list[ScorecardAtomDTO] = Field(default_factory=list)
     clustered_row_sources: list[MCPAuditTrace] = Field(default_factory=list)
     ```
   - This explicitly resolves the Purity Paradox (Epic 89) by extracting cluster arrays out of the Atom and into the Row.

## Architectural Mandates & Hardening
- **the_zero_compromise_pledge**: No `.get("default")` fallbacks permitted. Strict Pydantic validation is absolutely mandatory.
- **strict_pydantic_v2_rust**: Enforce `.model_validate()`, NEVER use legacy `parse_obj()`.
- **data_leak_prevention_firewall**: `ScorecardAtomDTO` specifically enforces the DTO Firewall so underlying database model elements do not bleed to the client.

## Testing & Quality Gate Plan
- **Unit Tests**: Update Pydantic model serialization tests in `tests/unit/models/` to verify `ScorecardAtomDTO` strips all non-presentation fields if initialized from a larger trace object.
- **Verification Command**:
  `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py backend_v2/models/dtos/report.py --test`

<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target c:\src\quorum\docs\epic\EPIC_88_Zero_Middleware_Implementation_Plan_tracker.md`
