# Phase 4: Seed Data Update & Tests Refactoring

Source: Epic 68 Phase 3 & Phase 5

## Architectural Laws (from .agents/rules & hardening.xml)
- **The Anti-TDD Trap Mandate:** Rewrite tests to use strictly typed Pydantic models. Do not use MagicMock loosely for Pydantic models.
- **Rule 2 (Strict Pydantic):** Ensure test data fixtures strictly conform to the new dual-list schema.
- **Seeding Command Mandate:** Run the seeder with `local` target environment.

## Target Files (Modify)
- `backend_v2/seed/seed_data.json`
- `tests/unit/services/orchestrator/test_context_router.py`
- `tests/unit/models/dtos/test_output_profile.py`
- `tests/unit/models/dtos/test_lightweight_matrix.py`
- `tests/unit/services/test_blueprint.py`
- `tests/integration/test_xai_reporter_integration.py`
- `tests/unit/models/test_xai_extension_scope.py` (New File)
- `docs/architecture/01_backend_api_and_core.md`

## Tasks

1. **`backend_v2/seed/seed_data.json`**:
   - Update L7184-7190 (Embedded profile): Replace `visible_extensions` array with:
     ```json
     "visible_block_extensions": ["falsification", "coaching", "remediation_steps", "emotional_sentiment"],
     "visible_workflow_extensions": ["variance_validation"]
     ```
   - Update L8239-8245 (output_profiles): Replace `visible_extensions` array with:
     ```json
     "visible_block_extensions": ["justification", "coaching", "falsification", "remediation_steps"],
     "visible_workflow_extensions": ["variance_validation"]
     ```

2. **Update Existing Tests**:
   - In all mentioned test files, update instantiations of `OutputProfileConfig`, `OutputProfileCreateDTO`, etc., to use `visible_block_extensions` and `visible_workflow_extensions`.
   - Update integration assertions.

3. **Create `tests/unit/models/test_xai_extension_scope.py`**:
   - Add a new meta-test `test_xai_extension_scope_completeness` that verifies every `XaiExtensionType` enum member has an entry in `XAI_EXTENSION_SCOPE`.

4. **Run Seeder**:
   - Instruct the user to run: `uv run python backend_v2/seed/run_seed.py local`

5. **Documentation Update**:
   - Update `c:\src\quorum\docs\architecture\01_backend_api_and_core.md` to document the new seed data structure and the meta-test pattern for extension scopes.

## Testing & Quality Gate Plan
- **Unit Tests:** Execute `uv run pytest tests/unit/`
- **Integration Tests:** Execute `uv run pytest tests/integration/test_xai_reporter_integration.py`

## Session Handover
To execute this phase, start a NEW chat session and run:
`/tier2-execute --target="c:\src\quorum\docs\epic\tasks_EPIC_68_Extension_Scope_Separation\phase4_seed_and_tests.md"`
