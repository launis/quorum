# Phase 1: Database and Seeding Refactoring (Persistence Layer)

This sub-plan covers the database and seeding updates to support universal decoupled provider parameters.

## Architectural Invariants (From Rules)
1. **Rule 1: Strict Pydantic V2 Rust Parsing (`extra='forbid'`)** - Kaikki taulukot on pidettävä matemaattisesti puhtaina.
2. **Rule 2: No Naked Dicts in State** - Datan siirron rajat on suojattava Pydantic `.model_validate()` -validoinnilla ennen persistoimista.
3. **Rule 3: Live Database Mutation Ban** - Tietokantaa `db_v2.json` ei koskaan muokata suoraan. Kaikki muutokset tehdään `seed_data.json` -tiedostoon.

## Proposed Changes

### Target Files (Modify)
- [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)
- [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

### Context Files (Read-Only)
- [database_systems_and_maintenance.md](file:///c:/src/quorum/docs/architecture/09_data_persistence.md)

---

## Milestones

### Milestone 1: Update ModelProfile Pydantic Schema
* **Source**: Epic Phase 1, Step 1
* **Files**: [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)
* **Instructions**: Add `additional_params` dict field to `ModelProfile` with a default factory to match the backend's strict `LLMProviderConfig` schema:
```python
class ModelProfile(V2CoreBase):
    ...
    caching_strategy: str | None = Field(
        default=None, description="Cache strategy identifier (e.g. 'anthropic_ephemeral')"
    )
    additional_params: dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific parameters."
    )
    is_active: bool = Field(default=True, description="Whether the model is actively available")
```

### Milestone 2: Refactor seed_data.json to Decouple Provider Config
* **Source**: Epic Phase 1, Step 1
* **Files**: [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)
* **Instructions**: Locate the `google` provider configurations under the model registry in `seed_data.json`. Remove the hardcoded region fields and instead put them inside the generic `additional_params` map using environment variable dynamic interpolation syntax `"${VERTEX_LOCATION}"`:
```json
"additional_params": {
  "vertex_location": "${VERTEX_LOCATION}"
}
```

### Milestone 3: Perform Seed Sync & Schema Validation
* **Source**: Epic Phase 1, Step 2
* **Instructions**: Run the database seeder to verify that the modified seed data aligns 100% with the updated Pydantic `ModelProfile` schema.
* **Commands**:
  ```powershell
  uv run python backend_v2/seed/run_seed.py local
  ```

---

## Testing & Quality Gate Plan

### Automated Tests
1. Run the seed schema alignment checks:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_seed_architectural_guardrails.py -v
   ```
2. Verify all models parse cleanly.

---

## Session Handover
To proceed, start a new session and invoke the next step via the Master Tracker:
```powershell
To execute this Epic iteratively, start a NEW chat session and run: /tier5-resume --target docs/epic/EPIC_62_tracker.md
```
