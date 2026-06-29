# Phase 2: Backend Middleware Gutting & Explicit Skipped States

Source: Epic 88, Steps 2, 4, and 5.

## Proposed Changes

### Target Files
- `backend_v2/services/blueprint.py`
- `backend_v2/services/pdf_generator.py`

### Context Files
- `backend_v2/models/v2_core.py`

### Task Details
1. **Gut Legacy Middleware in Blueprint**:
   - [MODIFY] `backend_v2/services/blueprint.py` (specifically `_generate_v2_scorecard()` or `_extract_matrices_and_extensions`).
   - Remove ALL legacy quote flattening, UUID generation for `EvidenceQuoteDTO`, and manual string concatenations.
   - The function should simply iterate over valid `AtomEvaluationItemDTO` trace outputs and hydrate `ScorecardAtomDTO` objects directly.
2. **Explicit Skipped States**:
   - If an evaluation is short-circuited (e.g. Level 0 failed, so Levels 1 & 2 are missing), deduce the missing levels from the schema (`PromptBlock.scales`).
   - For missing levels, instantiate a `ScorecardAtomDTO` with `status=None` or an explicit skipped indicator to guarantee 100% Flutter/PDF parity. 
3. **Clustered Row Sources**:
   - For a given row, extract all `used_evidence_ids` from its constituent atoms. Map these IDs to the full `MCPAuditTrace` list, and store the *unique* traces in `MatrixScorecardRowDTO.clustered_row_sources`.
4. **PDF Engine Output Parity**:
   - [MODIFY] `backend_v2/services/pdf_generator.py`.
   - Update Jinja template logic to iterate directly over `evaluated_atoms` flat list. Implement Python-side logic matching Flutter's "smart getter" to group these flat atoms by level for rendering.
   - Since missing levels are explicitly provided as "Skipped", the PDF engine requires zero guesswork.

## Architectural Mandates & Hardening
- **tripartite_rendering_boundary**: The Backend MUST NOT hardcode or generate pre-rendered Markdown tables. The Backend produces purely raw DTO data. The PDF engine generates reports strictly from the identical DTO structure as Flutter.
- **strict_math_display_isolation**: Algorithmic scoring must not be conflated with missing atom status logic.
- **the_duct_tape_ban**: "God Blocks" and returning empty dicts `{}` on failure are forbidden. Missing data must be handled explicitly through the schema.

## Testing & Quality Gate Plan
- **Integration Tests**: Verify `BlueprintTransformer` end-to-end trace mapping to ensure `ScorecardAtomDTO` correctly receives trace data and groups `MCPAuditTrace` into `clustered_row_sources`.
- **Verification Command**:
  `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/services/pdf_generator.py --test`

<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target c:\src\quorum\docs\epic\EPIC_88_Zero_Middleware_Implementation_Plan_tracker.md`
