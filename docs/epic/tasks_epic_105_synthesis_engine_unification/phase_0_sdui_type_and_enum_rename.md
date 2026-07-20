# Phase 0: `expected_sdui_type` Field Addition & Enum Rename

> **Source**: Epic 105, Phase 0 — Prerequisite
> **Domain**: Backend (Python) ONLY
> **Max Target Files**: 3

## Goal

Resolve the Epic 104 Phase 0.5 deferral by adding `expected_sdui_type` to `StepRule` and atomically renaming the legacy `PRE_HYDRATED_SYNTHESIS` enum value to `SYNTHESIS`. Update `seed_data.json` to reflect both changes.

## Architectural Invariants (Injected)

- **`00-antigravity-core.md`**: `zero_compromise_pledge` — No `"unknown"` SDUI type. Fail-Fast if unconfigured.
- **`01-python-backend.md`**: `pydantic_annotated_fields_mandate` — Use `Annotated[..., Field(...)]` syntax.
- **`01-python-backend.md`**: `strict_pydantic_v2_rust` — `ConfigDict(extra='forbid', strict=True)`.
- **`03_seed_vault.md`**: Vault Mutation Protocol — Modify `seed_data.json` then wipe DB via `uv run python backend_v2/seed/run_seed.py local`.

## Proposed Changes

### TARGET (Modify): [enums.py](file:///c:/src/quorum/backend_v2/models/enums.py)

**Milestone 0.1**: Rename enum value.

```diff
 class EngineOverrideStrategy(StrEnum):
     """Execution strategy overrides for the engine."""
-    PRE_HYDRATED_SYNTHESIS = "PRE_HYDRATED_SYNTHESIS"
+    SYNTHESIS = "SYNTHESIS"
     DYNAMIC_TOOL_AGENT = "DYNAMIC_TOOL_AGENT"
```

The `LaxEngineOverrideStrategy` alias on line 543 remains unchanged (it uses `Annotated[EngineOverrideStrategy, Field(strict=False)]` which is generic).

---

### TARGET (Modify): [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py)

**Milestone 0.2**: Add `expected_sdui_type` to `StepRule` (class at line 766).

Add the field immediately after `engine_override` (line 783):

```python
expected_sdui_type: Annotated[
    Literal["markdown", "hero_insight"] | None,
    Field(description="Declares the expected SDUI output schema for schema compilation."),
] = None
```

> **Design Decision**: The `| None` default is permitted ONLY because existing non-synthesis steps (TDA/Logic) do not use this field yet. Synthesis steps MUST have this set to `"markdown"` in seed_data. The engine MUST crash if this is `None` when the synthesis path is entered (enforced in Phase 1's `LLMNodeStrategy` synthesis compilation branch).

---

### TARGET (Modify): [seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)

**Milestone 0.3**: Atomic seed data update.

1. **Rename all `"engine_override": "PRE_HYDRATED_SYNTHESIS"`** → `"engine_override": "SYNTHESIS"` (13 occurrences at lines: 7613, 7626, 7653, 7666, 7679, 7705, 7718, 7731, 7744, 7758, 7771, 7791, 7813).
2. **Add `"expected_sdui_type": "markdown"`** to every `steps[]` entry that has `"engine_override": "SYNTHESIS"`.

Example transformation for a single step:
```diff
 {
   "id": "sr_f0a26d17cc9b48a7",
   "task_blueprint": "sp_db849f9790984585",
   "depends_on": [],
   "input_mappings": { ... },
-  "engine_override": "PRE_HYDRATED_SYNTHESIS"
+  "engine_override": "SYNTHESIS",
+  "expected_sdui_type": "markdown"
 }
```

---

### TARGET (Modify): [enums.dart](file:///c:/src/quorum/client_app_v2/lib/core/models/enums.dart)

**Milestone 0.4**: Update `EngineOverrideStrategy` enum for Cross-Domain Parity.

```diff
 enum EngineOverrideStrategy {
-  @JsonValue('PRE_HYDRATED_SYNTHESIS')
-  preHydratedSynthesis,
+  @JsonValue('SYNTHESIS')
+  synthesis,
   @JsonValue('DYNAMIC_TOOL_AGENT')
   dynamicToolAgent,
 }
```

---

### TARGET (Modify): [workflow.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/workflow.dart)

**Milestone 0.5**: Update `StepRule` Freezed model for Cross-Domain Parity.

Add the `expectedSduiType` field:

```dart
   const factory StepRule({
     @StrictOpaqueIdConverter() required String id,
     @StrictOpaqueIdConverter() required String taskBlueprint,
     @Default([]) List<String> dependsOn,
     @Default({}) Map<String, String> inputMappings,
     @JsonKey(name: 'engine_override') EngineOverrideStrategy? engineOverride,
     @JsonKey(name: 'expected_sdui_type') SduiBlockType? expectedSduiType,
     @Default(0.0) double uiPosX,
     @Default(0.0) double uiPosY,
   }) = _StepRule;
```

---

## CONTEXT (Read-Only)

| File | Reason |
|------|--------|
| [base.py (engines)](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/base.py) | Verify `ExecutionEngine` Protocol is unchanged |
| [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py) | Reference for routing chain using `EngineOverrideStrategy` |

## Destructive Operation Inventory

| Symbol | Action | New Location |
|--------|--------|-------------|
| `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS` | RENAMED | `EngineOverrideStrategy.SYNTHESIS` |

**Blast Radius (enum rename consumers)**:
- `dag_executor.py` lines 242, 667, 821 — All reference `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS`. MUST be updated to `.SYNTHESIS`.
- `test_dag_executor_preflight.py` lines 6, 94, 147, 203 — MUST be updated.
- `test_dag_executor_atom_ceiling.py` lines 8, 65 — MUST be updated.
- `seed_data.json` — 13 occurrences (listed above).

## Testing & Quality Gate Plan

1. **BASELINE**: Before modifying any code, run `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test` and record passing test count + coverage.
2. **After modifications**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` (full backend).
3. **Frontend Codegen**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/core/models/ --build` and `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/ --build`
4. **Frontend Audit**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --test`
5. **Seed validation**: Run `uv run python backend_v2/seed/run_seed.py local` to verify the seed data parses cleanly.

## Documentation Update

- Update `.agents/rules/04_directory_reference.md` if any structural directory changes occur (none expected in Phase 0).

---

## Session Handover

```
Phase 0 complete. StepRule now has expected_sdui_type field and EngineOverrideStrategy.SYNTHESIS enum.
Seed data updated with 13 engine_override renames and expected_sdui_type additions.
Frontend Dart models (StepRule, EngineOverrideStrategy) updated to match for SDUI Parity.
Next: Execute Phase 1 (SynthesisEngine extraction).
```
