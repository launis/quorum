# Phase 2: Polyfactory Strictness & Global Test Hardening [PLACEHOLDER]

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L66-L77] Phase 2

## Objective

Harden all Polyfactory test fixtures by:
1. Removing `factory_use_construct=True` bypasses.
2. Removing legacy field references (`evaluative_matrices`, `content_blocks`, `penalties_applied`) from test data.
3. Injecting `MATRIX_SCORECARD_TABLE` and `MARKDOWN_BLOCK` layout schemas into `ReportDataDTOFactory.layouts`.
4. Implementing `@post_generated` hooks for mathematical coherence.

## Expected Target Files (Test Blast Radius)

1. @[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py#L54] — `factory_use_construct=True` removal
2. @[c:\src\quorum\backend_v2\tests\unit\test_flattener.py#L31] — `evaluative_matrices` in test data
3. @[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py#L422-L423] — `evaluative_matrices`/`informational_matrices` mock assignment
4. @[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py#L78] — `content_blocks` in test data
5. @[c:\src\quorum\backend_v2\tests\unit\services\test_execution_render_bug.py#L57-L58] — Legacy field mock
6. @[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py#L524-L562] — `content_blocks` / `penalties_applied` test fixtures
7. @[c:\src\quorum\backend_v2\tests\integration\test_epic_chain_e2e.py#L68-L77] — Legacy field fixtures

## Expected Verification Commands

- `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- **MANDATORY Final E2E**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

> [!NOTE]
> **PLACEHOLDER**: This plan requires detailed generation by re-invoking the Tier 1 Planner after all Phase 1 plans are completed, based on the updated codebase state.
