# Phase 2: Backend Context Mappers & Blueprint Hydration (Placeholder)

Source: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md#L206-L216] Phase 2: Backend Context Mappers & Blueprint Hydration

## Targets
- `@[c:\src\quorum\backend_v2\services\orchestrator\context_mapper.py]`
- `@[c:\src\quorum\backend_v2\services\blueprint.py]`
- `@[c:\src\quorum\backend_v2\models\enums.py]`
- `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`

## Objective
Implement `context_mapper.py` logic to hydrate `execution_id`, and implement the `TARGET_BLOCK_HYDRATORS` Strategy Pattern registry in `blueprint.py` for new layout target blocks (Global Score, Penalties, Audit Trail, Jargon Ratio, Printable Sources). Add `normalized_score` conditional rendering to `report_template.jinja2`.

> [!NOK]
> Invoke the Tier 1 Planner again to generate detailed plans for the remaining phases based on the updated codebase state.
