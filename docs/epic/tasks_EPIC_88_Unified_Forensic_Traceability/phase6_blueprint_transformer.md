# Phase 6: Blueprint Transformer & RowForensicsDTO

Source: Epic Phase 3 & Appendix E, Appendix F.1

## Target Files (Modify)
- `backend_v2/services/blueprint.py`

## Requirements
1. **Evidence ID Extraction (`extract_evidence_ids`)**: 
   - Expand `extract_evidence_ids()` (around line 1055) to search for both `used_evidence_ids` and `used_mcp_ids` keys, ensuring robust extraction.
2. **Build Report DTO (`build_report_dto`)**:
   - Replace the legacy flat `quotes_list` concatenation logic with the new hierarchical `RowForensicsDTO` logic.
   - For each Matrix row, iterate through the execution state to gather the raw quotes.
   - Look up the pre-calculated `is_mcp_verified` and `source_reference` (from Phase 5).
   - Look up the `evidence_override` events from the `execution_trace`. If an override exists for the quote's ID, set `user_rejected = True`.
   - **ID Stability**: Read the opaque Stripe ID `evq_xxxx` from the execution trace (it MUST have been generated and persisted during the worker phase, not calculated on-the-fly here, to prevent Soft Delete hash collisions).
   - Group the quotes into `LevelQuotesDTO` arrays and assign them to `RowForensicsDTO.level_quotes`.
   - Apply the Legacy Adapter: if an old execution lacks these objects, gracefully leave `RowForensicsDTO` null or parse legacy quotes into `quotes_list` without crashing.

## Architectural Invariants & Hardening Mandate
- **Rule 49 (execution_synthesis_tier_decoupling)**: The Blueprint Transformer is strictly a data projection layer. It must not execute network requests, heavy regex, or state mutation.
- **Rule 45 (schema_driven_routing)**: Do not use blind duck typing. Read the JSON strictly utilizing Pydantic structural loading when transforming the payload.
- **Rule 22 (zero_legacy_fallback_hacks)**: The "Legacy Adapter" is specifically approved here solely for Read-Only viewing of historical reports, but ALL new validations must be strictly V2.

## Documentation Update
Update `docs/architecture/08_dynamic_rendering_sdui.md` with the new hierarchical `RowForensicsDTO` output structure.

## Testing & Quality Gate Plan
- **Unit Tests**: Ensure `build_report_dto()` correctly projects `EvidenceQuoteDTO` and applies the `user_rejected` flag when provided with a mock `evidence_override` trace event.
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
