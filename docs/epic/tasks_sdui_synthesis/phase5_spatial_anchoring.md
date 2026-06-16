# Epic SDUI Synthesis - Phase 5: Spatial Anchoring Determinism
Source: Epic Phase 5

Spatiaalinen Ankkurointi vaatii poikkeuksetonta determinismiä. `fuzz.partial_ratio`-funktiot voivat sivuuttaa hallusinaatiot. Korvataan ne puhtaalla, `O(N)` kompleksisuuden indeksikartoitetulla normalisoinnilla.

## Proposed Changes
### Backend V2 Orchestrator
#### [MODIFY] [anchor_validation_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/anchor_validation_service.py)
- Completely remove fuzzy matching libraries (e.g. `RapidFuzz` / `fuzz.partial_ratio`).
- Enforce strict `O(N)` physical anchoring utilizing `AnchorValidationService.normalize_text_with_mapping()`.
- Map the LLM's `exact_quote` against the normalized `source_text` utilizing a pure `str.find()`. Use the index map to retrieve the exact physical coordinates for the client without altering the raw text source.

## Architectural Rules Implemented
- **LLM Rule 130 (Strict Physical Anchoring Mandate)**: Kieltää fuzzy-matchingin. Lähdeviittaukset on löydyttävä fyysisesti `str.find()`-haulla, jotta SSOT-vakuus säilyy.
- **Backend Rule 81 (Data Parsing Preservation)**: Maintain accurate data mappings and error bounds without masking failures.

## Testing & Quality Gate Plan
### Unit Tests
- Create test cases where the LLM hallucinated the quote by a few characters -> Must fail deterministic validation.
- Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_sdui_synthesis_tracker.md`
