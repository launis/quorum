# IMPLEMENTATION PLAN: Workflow Steps Dumb Painter & System Core Classification

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Establish the Server-Driven UI (SDUI) Dumb Painter architecture for the "Stepit & Riippuvuudet" (Workflow Steps & Dependencies) tab in Quorum Admin Studio V2. Eradicate all client-side index heuristics (`index == 0`, `index > 0 && isSystemCoreStep`) and negative engine-type exclusions (`bp.engineType != EngineType.causalDiscovery`). Introduce a shared SSOT enum `StepZone` (`zone_a`, `zone_b`, `zone_c`) with 100% cross-language parity, embed `zone` directly into backend `Step` domain models and `NodeStrategy` Freezed definitions, configure explicit zones across seed blueprints, decouple `WorkflowBuilderView` blueprint resolution from the Studio Dashboard's filtered `stepsControllerProvider` by introducing `allBlueprintsProvider` (fetching `StepFilterScope.all`), and ensure that protected system core steps (specifically: Causal Discovery `sp_c4a5a1d15c00438a`) display the locked system core badge (`l10n.studioSystemCoreBadge`) and action locks while rendering in their proper functional zone (Zone B specialist controls rather than Zone C funnel anchor boxes).

---

## Target & Context Scope

### TARGET Boundaries
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L25-L95]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart#L50-L75]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart#L318-L330]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart#L455-L470]`
- `[MODIFY] @[backend_v2/models/enums.py#L247-L262]`
- `[MODIFY] @[backend_v2/models/enums.py#L346-L379]`
- `[MODIFY] @[backend_v2/models/enums.py#L755-L778]`
- `[MODIFY] @[backend_v2/models/enums.py#L1047-L1052]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart#L478-L491]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py#L176-L178]`
- `[MODIFY] @[backend_v2/models/domain/step.py#L33-L161]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/workflow.dart#L95-L165]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L21385-L22232]`
- `[MODIFY] @[client_app_v2/lib/features/studio/controllers/studio_controller.dart#L20-L45]`
- `[MODIFY] @[client_app_v2/lib/features/studio/controllers/studio_controller.dart#L330-L455]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L45-L85]`
- `[MODIFY] @[client_app_v2/test/features/studio/models/workflow_test.dart#L180-L255]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L20-L80]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L525-L570]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart#L25-L95]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart#L190-L215]`
- `[NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_dumb_painter_test.dart]`

### CONTEXT Boundaries (Read-Only)
- `@[backend_v2/api/routers/studio/steps.py#L57-L79]`
- `@[backend_v2/services/studio/workflow_service.py#L452-L475]`
- `@[client_app_v2/lib/core/api/studio_client.dart#L150-L166]`
- `@[client_app_v2/lib/features/studio/controllers/studio_controller.dart#L285-L325]`
- `@[backend_v2/models/dtos/studio.py#L291-L302]`

---

### Pre-Implementation Technical Debt Cleanups
A pre-flight technical debt audit via `uv run python scripts/audit_technical_debt.py` detected 8 violations across touched targets:
1. **Rule `DGR008` (`flutter_dart_anti_patterns`)** in `client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart`:
   - Line 47: Manual string clipping via `.substring(0, 16)` during UUID prefix truncation in `_addStep()`.
   - Line 78: Manual string clipping via `.substring(0, 16)` during UUID prefix truncation in `_copyStep()`.
   - Remediation: Replace `.substring(0, 16)` with safe character bounding `uuidHex.characters.take(16).toString()` to eliminate manual clipping anti-patterns.
2. **Rule `DGR007` (`flutter_dart_anti_patterns`)** in `client_app_v2/lib/features/studio/views/workflow_builder_view.dart`:
   - Line 324: Banned hardcoded hex color `Color(0xFF2E7D32)` in SnackBar background.
   - Line 460: Banned hardcoded hex color `Color(0xFFE8F5E9)` in MaterialBanner background.
   - Line 464: Banned hardcoded hex color `Color(0xFF2E7D32)` in MaterialBanner text style.
   - Remediation: Replace hardcoded colors with theme tokens `Theme.of(context).colorScheme.primary`, `Theme.of(context).colorScheme.primaryContainer`, and `Theme.of(context).colorScheme.onPrimaryContainer`.
3. **Rule `TD_DICT_GET` (`python_ast_dict_fallbacks`)** in `backend_v2/models/enums.py`:
   - Line 262: Permissive `.get()` lookup on domain state in `DisplayScale.l10n_key`: `_L10N_MAP.get(self, '')`.
   - Line 379: Permissive `.get()` lookup on domain state in `XaiExtensionType.l10n_key`: `_L10N_MAP.get(self, '')`.
   - Line 778: Permissive `.get()` lookup on domain state in `TitleKey.l10n_key`: `_L10N_MAP.get(self, '')`.
   - Remediation: Replace `_L10N_MAP.get(self, '')` with positive membership access `_L10N_MAP[self] if self in _L10N_MAP else ''` to eliminate dictionary `.get()` fallbacks.

---

### Five-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`backend_v2/models/enums.py`, `client_app_v2/lib/core/models/enums.dart`, & `backend_v2/tests/unit/test_enum_parity.py`** | Banned heuristic client-side index math (`index == 0`, `index > 0 && isSystemCoreStep`); banned cross-language enum divergence; banned permissive dictionary `.get()` lookups (`_L10N_MAP.get(self, '')` under `TD_DICT_GET`). | Shared SSOT enum `StepZone` (`zone_a`, `zone_b`, `zone_c`) with `@JsonEnum()` and `@JsonValue` annotations in Dart and `StrEnum` in Python; positive membership access `_L10N_MAP[self] if self in _L10N_MAP else ''`; verified via bidirectional AST parity test. | Single unified enum; zero secondary mapping structures or intermediate string converters. | `uv run pytest backend_v2/tests/unit/test_enum_parity.py` asserts 100% parity across all enum members. |
| **`backend_v2/models/domain/step.py` & `client_app_v2/lib/features/studio/models/workflow.dart`** | Banned untyped step role guessing; banned client-side blueprint assumptions; banned omitting `zone` in domain schemas. | Strongly typed `zone: StepZone = StepZone.ZONE_B` on `Step` (Python) and `@Default(StepZone.zoneB) StepZone zone` on `NodeStrategy` (Dart, across all 3 unions: `llm`, `logic`, `causalDiscovery`). | Direct model field with default; zero runtime reflection or dynamic duck-typing inspection. | `backend_audit_loop.py` strict AST checks; `flutter_audit_loop.py --build` generating Freezed models. |
| **`backend_v2/seed/seed_data.json`** | Banned implicit step zone assumptions in seed vault; banned missing `zone` keys on protected foundational anchors. | Explicit `"zone": "zone_a"` on `sp_db849f9790984585` (Input Processing); `"zone": "zone_b"` on `sp_c4a5a1d15c00438a` (Causal Discovery); `"zone": "zone_c"` on `sp_192910b5f5a34c79`, `sp_d245365e4a274b9e`, `sp_7a8b9c0d1e2f3a4b`. | Direct JSON properties on existing step objects; zero duplicate step records or shadow seed files. | `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`. |
| **`client_app_v2/lib/features/studio/controllers/studio_controller.dart` & `client_app_v2/lib/features/studio/views/workflow_builder_view.dart`** | Banned hardcoded hex colors `Color(0xFF2E7D32)` and `Color(0xFFE8F5E9)` (`DGR007`); banned leaking Studio Dashboard filter scope into workflow authoring; banned missing blueprints when dashboard scope is `specialists`; banned omitting `NodeStrategyCausalDiscovery` in `deleteStep`. | Theme tokens `Theme.of(context).colorScheme.primary` and `primaryContainer`; dedicated `@riverpod Future<List<NodeStrategy>> allBlueprints(Ref ref)` fetching `scope: StepFilterScope.all`; `WorkflowBuilderView` watches `allBlueprintsProvider`; unified deletion `currentList.removeWhere((m) => m.id == id);`. | Single shared provider for authoring; zero state pollution between dashboard view mode and workflow canvas. | Unit and controller tests verifying `allBlueprintsProvider` calls `getSteps(scope: StepFilterScope.all)`. |
| **`client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart`** | Banned client-side index heuristics (`index == 0`, `index > 0 && isSystemCoreStep`); banned rendering Causal Discovery as Zone C automatic anchor box. | Pure Dumb Painter: `isSystemCoreStep` derived purely from `currentBlueprint?.isSystemCore ?? false`; `isZoneA` derived from `currentBlueprint?.zone == StepZone.zoneA`; `isZoneC` derived from `currentBlueprint?.zone == StepZone.zoneC`. | Frontend strictly renders backend metadata; Causal Discovery renders locked system core badge with Zone B specialist controls. | Widget test `workflow_step_card_dumb_painter_test.dart` verifies Dumb Painter layout across all zones. |
| **`client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart`** | Banned manual string clipping via `.substring(0, 16)` (`DGR008`); banned negative engine-type exclusion (`bp.engineType != EngineType.causalDiscovery`); banned skipping step index 0. | Character-based safe taking `uuidHex.characters.take(16).toString()`; typed positive matching in `_findFirstZoneCIndex`: returns first index where `bp?.zone == StepZone.zoneC`. | Direct single-condition loop; zero engine-type branching or negative heuristic checks. | Unit test `workflow_steps_tab_test.dart` asserting correct insertion index before the first Zone C step. |

---

```xml
<execution_protocol>
  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUP">
    <action>In `client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart` lines 47 and 78, replace `.substring(0, 16)` with `uuidHex.characters.take(16).toString()` to eliminate `DGR008` violations.</action>
    <action>In `client_app_v2/lib/features/studio/views/workflow_builder_view.dart` line 324, replace `backgroundColor: const Color(0xFF2E7D32)` with `backgroundColor: Theme.of(context).colorScheme.primary` to resolve `DGR007`.</action>
    <action>In `client_app_v2/lib/features/studio/views/workflow_builder_view.dart` lines 460 and 464, replace `const Color(0xFFE8F5E9)` and `const Color(0xFF2E7D32)` with `Theme.of(context).colorScheme.primaryContainer` and `Theme.of(context).colorScheme.onPrimaryContainer` to resolve `DGR007`.</action>
    <action>In `backend_v2/models/enums.py` lines 262, 379, and 778, replace `_L10N_MAP.get(self, "")` with `_L10N_MAP[self] if self in _L10N_MAP else ""` to eliminate `TD_DICT_GET` warnings.</action>
    <action>Execute `uv run python scripts/audit_technical_debt.py --targets client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart client_app_v2/lib/features/studio/views/workflow_builder_view.dart backend_v2/models/enums.py` to verify zero remaining violations.</action>
    <constraint invariant="dgr008_anti_substring">Never use manual substring clipping on strings; use Characters taking or safe utilities.</constraint>
    <constraint invariant="dgr007_anti_hardcoded_colors">Never hardcode hex colors or direct Colors constants in feature widgets; strictly use Theme.of(context).colorScheme tokens.</constraint>
    <constraint invariant="english_language_mandate">All variable names, comments, and identifiers must remain exclusively in English.</constraint>
  </step>

  <step id="2" name="SSOT ENUM DEFINITION & CROSS-LANGUAGE PARITY">
    <action>Define `StepZone(StrEnum)` in `backend_v2/models/enums.py#L1047-L1052` with members:
      - `ZONE_A = "zone_a"`
      - `ZONE_B = "zone_b"`
      - `ZONE_C = "zone_c"`
      - Annotated type alias `LaxStepZone = Annotated[StepZone, Field(strict=False)]`
    </action>
    <action>Define `enum StepZone` in `client_app_v2/lib/core/models/enums.dart#L478-L491` with members:
      - `@JsonValue('zone_a') zoneA('zone_a')`
      - `@JsonValue('zone_b') zoneB('zone_b')`
      - `@JsonValue('zone_c') zoneC('zone_c')`
      - Enhanced enum constructor `const StepZone(this.backendValue); final String backendValue;`
    </action>
    <action>In `backend_v2/tests/unit/test_enum_parity.py#L176-L178`, add test function `test_step_zone_parity()` validating 100% bidirectional member parity for `StepZone`.</action>
    <action>Execute `uv run pytest backend_v2/tests/unit/test_enum_parity.py` to confirm parity validation passes.</action>
    <constraint invariant="ban_semantic_drift_renaming">Enum member identifiers and wire values must match 1:1 between Python and Dart.</constraint>
    <constraint invariant="zero_backward_compatibility_planning_ban">No fallback zones or defensive string defaults; all zone values must resolve to valid StepZone enum members.</constraint>
  </step>

  <step id="3" name="DOMAIN MODEL & DTO INTEGRATION">
    <action>In `backend_v2/models/domain/step.py#L33-L161`, import `LaxStepZone, StepZone` from `backend_v2.models.enums` and add the `zone` field to `Step`:
      ```python
      zone: Annotated[
          LaxStepZone,
          Field(
              default=StepZone.ZONE_B,
              description="Functional workflow zone classification (Zone A Ingestion, Zone B Specialists, Zone C Funnel Anchors).",
          ),
      ] = StepZone.ZONE_B
      ```
    </action>
    <action>In `client_app_v2/lib/features/studio/models/workflow.dart#L95-L165`, add `@JsonKey(name: 'zone') @Default(StepZone.zoneB) StepZone zone` to all three `NodeStrategy` factory constructors:
      - `NodeStrategy.llm`
      - `NodeStrategy.logic`
      - `NodeStrategy.causalDiscovery`
    </action>
    <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build` to re-generate Freezed and JsonSerializable code.</action>
    <action>In `client_app_v2/test/features/studio/models/workflow_test.dart#L180-L255`, update test assertions to verify `zone` serialization and deserialization for all three `NodeStrategy` unions.</action>
    <constraint invariant="the_zero_compromise_pledge">Enforce strict Pydantic V2 and Dart 3 Freezed schemas with zero unrecognized keys.</constraint>
    <constraint invariant="ban_drive_by_schema_mutations">Schema modifications are restricted strictly to the planned zone field on Step and NodeStrategy.</constraint>
  </step>

  <step id="4" name="SEED VAULT HARMONIZATION">
    <action>In `backend_v2/seed/seed_data.json#L21385-L22232`, add explicit `"zone"` properties to all foundational system core steps:
      - `sp_db849f9790984585` (Input Processing): `"zone": "zone_a"`
      - `sp_c4a5a1d15c00438a` (Causal Discovery): `"zone": "zone_b"`
      - `sp_192910b5f5a34c79` (XAI Reporter): `"zone": "zone_c"`
      - `sp_d245365e4a274b9e` (Scoring Engine): `"zone": "zone_c"`
      - `sp_7a8b9c0d1e2f3a4b` (Synthesis Generation): `"zone": "zone_c"`
    </action>
    <action>Verify all specialist steps implicitly default to or explicitly carry `"zone": "zone_b"`.</action>
    <action>Execute dry-run seed verification: `uv run python backend_v2/seed/run_seed.py local --dry-run`.</action>
    <action>Execute database atom audit: `uv run python scripts/audit_database_atoms.py --strict`.</action>
    <action>Execute database re-seeding: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <constraint invariant="database_schema_hallucination">Never alter root persistence collections; update strictly step object properties in seed_data.json.</constraint>
    <constraint invariant="database_persistence_git_ban">Never roll back data/db_v2.json; synchronize local database with seed updates.</constraint>
  </step>

  <step id="5" name="DECOUPLED WORKFLOW BLUEPRINTS PROVIDER">
    <action>In `client_app_v2/lib/features/studio/controllers/studio_controller.dart#L20-L45`, define a dedicated riverpod provider:
      ```dart
      /// Fetches all step blueprints (specialists and system core) unconditionally for workflow authoring.
      @riverpod
      Future<List<NodeStrategy>> allBlueprints(Ref ref) async {
        ref.cacheFor(AppDurations.cacheTimeout);
        final client = ref.watch(studioClientProvider);
        return await client.getSteps(scope: StepFilterScope.all);
      }
      ```
    </action>
    <action>In `client_app_v2/lib/features/studio/controllers/studio_controller.dart#L330-L455`:
      - Ensure that `saveStep`, `deleteStep`, and `cloneStep` in `StepsController` invalidate `allBlueprintsProvider` alongside `stepsControllerProvider` to maintain complete cache coherence across all authoring mutations.
      - In `deleteStep`, update step removal logic to `currentList.removeWhere((m) => m.id == id);` ensuring all `NodeStrategy` variants (including `causalDiscovery`) are cleaned up without union omission bugs.
    </action>
    <action>In `client_app_v2/lib/features/studio/views/workflow_builder_view.dart#L50-L75`:
      - Replace `final stepsAsync = ref.watch(stepsControllerProvider);` with `final stepsAsync = ref.watch(allBlueprintsProvider);`.
      - Update error onRetry handler to `ref.invalidate(allBlueprintsProvider);`.
    </action>
    <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/controllers/studio_controller.dart --build` to generate Riverpod bindings.</action>
    <constraint invariant="frontend_feature_isolation">Controllers handle networking and caching; views consume providers passively.</constraint>
    <constraint invariant="single_pipeline_invariant_mandate">Workflow authoring must always resolve blueprints from the unified all-blueprints provider, never from transient view filter scopes.</constraint>
  </step>

  <step id="6" name="FRONTEND DUMB PAINTER REFACTORING">
    <action>In `client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L45-L85`:
      - Eradicate `index == 0` and `index > 0 && isSystemCoreStep` heuristics entirely.
      - Refactor classification variables to read purely from `currentBlueprint`:
        ```dart
        final currentBlueprint = blueprints
            .where((b) => b.id == stepDef.taskBlueprint)
            .firstOrNull;

        final bool isSystemCoreStep = currentBlueprint?.isSystemCore ?? false;
        final bool isZoneA = currentBlueprint?.zone == StepZone.zoneA;
        final bool isZoneC = currentBlueprint?.zone == StepZone.zoneC;
        ```
      - Preserve the locked system core badge (`l10n.studioSystemCoreBadge`) and action lock based strictly on `isSystemCoreStep`.
      - Retain Zone A card layout for `isZoneA`.
      - Retain Zone C automated anchor box for `isZoneC`.
      - Retain Zone B controls (execution order, dependencies, causal source selector) for non-Zone A and non-Zone C steps.
    </action>
    <action>In `client_app_v2/lib/features/studio/views/widgets/workflow/workflow_steps_tab.dart#L25-L42`:
      - Refactor `_findFirstZoneCIndex` to eliminate negative engine-type exclusion:
        ```dart
        int _findFirstZoneCIndex(List<StepRule> steps) {
          for (int i = 0; i < steps.length; i++) {
            final step = steps[i];
            final bp = blueprints
                .where((b) => b.id == step.taskBlueprint)
                .firstOrNull;
            if (bp?.zone == StepZone.zoneC) {
              return i;
            }
          }
          return -1;
        }
        ```
    </action>
    <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart` to verify Dart compilation and lint passes.</action>
    <constraint invariant="ban_heuristic_identifier_matching">Never identify or partition steps by array index or engine type exclusions; use positive StepZone enum matching.</constraint>
    <constraint invariant="studio_engine_symmetry_and_causal_source_governance">Causal discovery steps in Zone B must render with full first-class controls while maintaining system core protections.</constraint>
  </step>

  <step id="7" name="TEST EXPANSION & QUALITY GATES">
    <action>In `client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L20-L80`:
      - Update mock blueprints to declare explicit `zone: StepZone.zoneA` on `sp_db849f9790984585`, `zone: StepZone.zoneB` on `sp_causal_discovery_1`, and `zone: StepZone.zoneC` on `sp_192910b5f5a34c79`.
    </action>
    <action>In `client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart#L525-L570`:
      - Update Zone C tests to assert that `currentBlueprint.zone == StepZone.zoneC` renders the automated anchor box and suppresses deletion buttons.
    </action>
    <action>Create `[NEW] @[client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_dumb_painter_test.dart]` containing:
      - Test: Protected system core step in Zone B (specifically: Causal Discovery `sp_c4a5a1d15c00438a`) renders `studioSystemCoreBadge`, hides delete and clone buttons, locks task profile selector, BUT renders Zone B execution order/dependencies instead of Zone C automatic anchor box.
      - Test: Protected system core step in Zone A (Input Processing) renders `studioSystemCoreBadge` and Zone A input ingestion box.
      - Test: Protected system core step in Zone C (XAI Reporter) renders `studioSystemCoreBadge` and Zone C automated anchor box.
      - Test: Unmapped or missing blueprint fails gracefully without throwing unhandled index assertion errors.
    </action>
    <action>In `client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart#L190-L215`:
      - Verify `_findFirstZoneCIndex` matches strictly on `StepZone.zoneC` and places newly added specialist steps before the first Zone C step, regardless of whether prior steps have `isSystemCore: true` in Zone B.
    </action>
    <action>Execute full test suites:
      - `uv run pytest backend_v2/tests/unit/test_enum_parity.py`
      - `flutter test client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_dumb_painter_test.dart`
      - `flutter test client_app_v2/test/features/studio/views/widgets/workflow/workflow_step_card_test.dart`
      - `flutter test client_app_v2/test/features/studio/views/widgets/workflow/workflow_steps_tab_test.dart`
    </action>
    <action>Execute universal audit loops:
      - `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`
      - `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`
    </action>
    <action>Execute mandatory E2E gate:
      - PowerShell (Windows): `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_causal_discovery_seed_integration.py`
      - Bash (Unix): `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_causal_discovery_seed_integration.py`
    </action>
    <constraint invariant="anti_happy_path_compliance">Test suites must cover positive rendering, protected mutation lockouts, and graceful handling of missing blueprints.</constraint>
    <constraint invariant="zero_tolerance_audit_loop">Universal audit scripts must pass with 0 errors before sign-off.</constraint>
  </step>
</execution_protocol>
```

---

### ISTQB Anti-Happy-Path Test Scenarios

| Test ID | Test Target | Input Condition | Expected Behavior | Verification Proof |
| :--- | :--- | :--- | :--- | :--- |
| `TST-ZON-001` | `StepZone` cross-language parity | Bidirectional comparison of Python `StepZone` and Dart `StepZone` | Enum members (`zone_a`, `zone_b`, `zone_c`) match 100% | `test_step_zone_parity()` exits with 0 assertion errors |
| `TST-ZON-002` | `WorkflowStepCard` Zone B System Core | Step blueprint with `is_system_core: true, zone: StepZone.zoneB` (Causal Discovery) placed at index 1 | Displays locked badge `l10n.studioSystemCoreBadge`; delete/clone hidden; profile selector locked; renders Zone B controls, NOT Zone C automatic anchor box | `workflow_step_card_dumb_painter_test.dart` finds badge and Zone B headers; finds zero Zone C widgets |
| `TST-ZON-003` | `WorkflowStepCard` Zone A System Core | Step blueprint with `is_system_core: true, zone: StepZone.zoneA` (Input Processing) placed at index 0 | Displays locked badge; delete/clone hidden; renders Zone A input ingestion box | `workflow_step_card_dumb_painter_test.dart` finds `studioWorkflowStep1IngestionTitle` |
| `TST-ZON-004` | `WorkflowStepCard` Zone C System Core | Step blueprint with `is_system_core: true, zone: StepZone.zoneC` (XAI Reporter) placed at index 3 | Displays locked badge; delete/clone hidden; renders Zone C automated anchor box | `workflow_step_card_dumb_painter_test.dart` finds `studioWorkflowZoneCAutoTitle` |
| `TST-ZON-005` | Negative: Missing or Unmapped Blueprint | StepRule with `taskBlueprint: "sp_nonexistent"` | Evaluates `isSystemCoreStep == false`, `isZoneA == false`, `isZoneC == false`; renders standard fallback card without crashing | Widget test asserts zero unhandled exceptions |
| `TST-ZON-006` | Negative: Enum Parity Divergence | Simulated missing enum member in Dart definition | `assert_enum_parity` raises `AssertionError` | `test_enum_parity_missing_member_failure` verifies fail-fast assertion |
| `TST-ZON-007` | `WorkflowStepsTab` Zone C index resolution | Workflow containing Zone A (0), Zone B System Core (1), Zone B Specialists (2..3), Zone C Anchors (4..6) | `_findFirstZoneCIndex` returns index 4 (first Zone C step), ignoring Zone B system core step at index 1 | Unit test asserts insertion of new step occurs at index 4 |
| `TST-ZON-008` | `WorkflowBuilderView` Blueprint Isolation | Dashboard steps controller scope set to `StepFilterScope.specialists` while opening `WorkflowBuilderView` | `WorkflowBuilderView` uses `allBlueprintsProvider` and successfully resolves system core blueprints (`sp_db849f...`, `sp_c4a5a1...`) | Widget/integration test asserts blueprints list contains all core anchors |
