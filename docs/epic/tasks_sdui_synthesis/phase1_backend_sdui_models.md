# Epic SDUI Synthesis - Phase 1: Backend SDUI Models
Source: Epic Phase 1, Step 1-3

Tavoite on korvata vapaamuotoinen Markdown strukturoiduilla SDUI-komponenteilla backendin päässä. Tämä estää rekursiiviset ja arvaamattomat LLM-tuotokset.

## Proposed Changes
### Backend V2 Models
#### [MODIFY] [sdui.py](file:///c:/src/quorum/backend_v2/models/view/sdui.py)
- Inherit `SduiBlockBase` to create `ParagraphBlock`, `BulletListItem` (helper), `BulletListBlock`, and `AlertBlock`.
- `ParagraphBlock`: `block_type: Literal["paragraph"]`, `text: str`, `citations: list[int]`
- `BulletListItem`: `text: str`, `citations: list[int]`
- `BulletListBlock`: `block_type: Literal["bullet_list"]`, `items: list[BulletListItem]`
- `AlertBlock`: `block_type: Literal["alert_box"]`, `severity: Literal["info", "warning"]`, `text: str`, `citations: list[int]`
- Add these into `AnySduiBlock` Discriminator Union.
- Ensure `model_config = ConfigDict(frozen=True, strict=True, extra="forbid")` is enforced.

#### [MODIFY] [synthesis.py](file:///c:/src/quorum/backend_v2/models/dtos/synthesis.py)
- In `SynthesisSectionDTO` and `SynthesisOutputDTO`, replace the `synthesized_markdown` string field completely with `content_blocks: list[AnySduiBlock]`.

## Architectural Rules Implemented
- **Hardening Rule 1 & 2 (Pydantic V2 Strictness)**: No default fallbacks allowed, `extra="forbid"` must be set on all models.
- **Hardening Rule 37 (Namespace Collisions)**: All Pydantic models must be maintained in the `models/` directory.
- **Epic Core Constraint (Flat Architecture)**: Recursive blocks are banned. No block can contain a nested list of `AnySduiBlock`.

## Testing & Quality Gate Plan
### Unit Tests
- Add unit tests for successful and failed parsing of new models in `tests/unit/models/view/test_sdui.py`.
- Run automated tests: `uv run python scripts/backend_audit_loop.py backend_v2/models --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_sdui_synthesis_tracker.md`
