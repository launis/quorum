# Phase 2: Orchestration, Registry & Prompt Compiler Updates
Source: Epic Phase 2

## Objective
Add the `is_synthesis_enabled` property to Pydantic models to enforce cross-domain SDUI parity and maintain dynamic localization capabilities.

## Target Files (Modify)
- @[c:\src\quorum\backend_v2\models\v2_core.py]
- @[c:\src\quorum\backend_v2\services\blueprint.py]

## Context Files (Read-Only)
- @[c:\src\quorum\backend_v2\services\orchestrator\prompt_compiler.py]

## Implementation Steps
1. In `v2_core.py`:
   - Add `is_synthesis_enabled: bool = Field(default=True, description="Toggle for UI section-level synthesis.")` to `OutputLayoutBlock`.
   - Add `is_synthesis_enabled: bool = Field(default=True)` to `ReportLayoutDTO`.
2. In `blueprint.py`:
   - Delete the legacy `@staticmethod def _resolve_i18n_str` entirely.
   - In `_build_layouts`, explicitly map `is_synthesis_enabled=layout_def.is_synthesis_enabled` to `ReportLayoutDTO`.
   - Ensure that `title` and `description` are passed as native `I18nText` objects to the DTOs rather than prematurely forcing `I18nText.resolve(target_locale)`.

## Destructive Operation Inventory
- DELETED: `_resolve_i18n_str` from `blueprint.py`. Reason: Violates the strict `I18nText` object pattern (naked dictionary parsing).

## Testing & Quality Gate Plan
- Strict unit tests: Verify layout extraction in blueprint test.
- Run Universal Quality Gate:
  `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`

## Documentation & Knowledge Item Mandate
- Instruct the execution agent to create a Knowledge Item (KI) on Cross-Domain SDUI Parity if one doesn't exist, to document the `I18nText` object passing behavior.
