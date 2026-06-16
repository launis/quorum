# Epic SDUI Synthesis - Phase 4a: Enum Parity Automation
Source: Epic Phase 4

Backendin ja Frontendin koodikantojen on noudatettava samaa tiukkaa SDUI-terminologiaa (`block_type`). Yksikin poikkeama voi kaataa käyttöliittymän purkuprosessin. Tästä syystä enum_parity-testin automatisointi on pakollista.

## Proposed Changes
### Architecture Tests
#### [MODIFY] [test_enum_parity.py](file:///c:/src/quorum/backend_v2/tests/architecture/test_enum_parity.py)
- Refactor the test from using hardcoded checks to dynamically parse `backend_v2/models/view/sdui.py`.
- Programmatically read all `block_type` Literal values inside `AnySduiBlock`.
- Assert that every detected `block_type` exists exactly in `client_app_v2/lib/core/models/enums.dart` mapped with `@JsonEnum("...")`.

## Architectural Rules Implemented
- **Hardening Rule 44 (Cross Language Enum Parity)**: The test MUST crash Pytest immediately if Flutter fails to mirror a Backend Literal/Enum, preventing silent data loss in the UI.

## Testing & Quality Gate Plan
### Unit Tests
- Execute `uv run pytest backend_v2/tests/architecture/test_enum_parity.py`. It should verify the Enums effectively.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_sdui_synthesis_tracker.md`
