# Phase 3: Synthesis Hook & Blueprint Transformer Cleanup

Source: Epic 68 Phase 2.2 & 2.3

## Architectural Laws (from .agents/rules & hardening.xml)
- **Rule 47 (Zero DB Hardcoding Mandate):** Replace string checks with list membership checks against `workflow_ext_values`.
- **Rule 82 (Data Parsing Preservation):** NEVER modify existing data extraction or algorithms. Preserve the algorithmic logic of the `VarianceEngine` block entirely.
- **Rule 83 (Preservation of Inline Comments):** NEVER delete existing inline comments (e.g. `# ...`) as they document exceptions or states.
- **Rule 88 (Architecture Lock Mandate):** Code blocks preceded by `ARCHITECTURE LOCK` are protected from refactoring. Do NOT modify the control flow or logic within them.

## Target Files (Modify)
- `backend_v2/services/blueprint.py`
- `backend_v2/hooks/synthesis.py`
- `docs/architecture/01_backend_api_and_core.md`

## Tasks

1. **`backend_v2/services/blueprint.py`**:
   - Find L201: `visible_extensions = [v.value for v in ...]` -> split into `block_exts` and `workflow_exts` reading from `visible_block_extensions` and `visible_workflow_extensions`.
   - Find L287-291: Replace `if ext.get("extension_type") == "variance_validation"` with `if ext.get("extension_type") in workflow_ext_values`.
   - Find L294-324: Refactor the VarianceEngine block to iterate over `visible_workflow_extensions`. The calculation logic itself must be algorithmically preserved.
   - Find L589-590: Replace `if ext_key == "variance_validation": continue` with `if ext_key in workflow_ext_values: continue`.

2. **`backend_v2/hooks/synthesis.py`**:
   - Find L616: Change `active_exts = active_profile_dto.visible_extensions` to read **only** `visible_block_extensions`.
   - Find L745-756: Ensure XAI highlights fail-fast validation checks **only** `visible_block_extensions`.
   - Find L634-637: Ensure only `visible_block_extensions` is passed into the `<target_extensions_to_harvest>` XML directive.

3. **Documentation Update**:
   - Update `c:\src\quorum\docs\architecture\01_backend_api_and_core.md` to explain the Synthesis and Blueprint Transformer routing mechanism for separating block and workflow level extensions.

## Testing & Quality Gate Plan
- **Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/hooks/synthesis.py`

## Session Handover
To execute this phase, start a NEW chat session and run:
`/tier2-execute --target="c:\src\quorum\docs\epic\tasks_EPIC_68_Extension_Scope_Separation\phase3_synthesis_and_blueprint.md"`
