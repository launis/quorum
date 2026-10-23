# IMPLEMENTATION PLAN: Admin Studio Steps Filter & Causal Discovery Harmonization

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
Establish a clean, fully backend-driven separation of concerns in Quorum Admin Studio V2 between configurable specialist step blueprints (`is_system_core: false`) and immutable foundational pipeline anchors (`is_system_core: true`). Consolidate six redundant, static causal discovery step records (`sp_01b1d7100000ca01` through `sp_06b1d7100000ca06`) into a single canonical universal blueprint (`sp_c4a5a1d15c00438a`) leveraging `CausalDiscoveryEngine` dynamic document topology agnosticism. Implement Option A (Pure Backend-Driven / Dumb Painter): define a shared `StepFilterScope` enum (`specialists`, `system_core`, `all`) with full cross-language parity, enforce server-side filtering in `StudioWorkflowService.list_steps` and `GET /studio/steps/?scope=...`, wire `StepsController` and `StudioClient` to pass the selected scope, and render blueprints in `StudioDashboardView` directly from the backend response via an interactive `SegmentedButton` while resolving existing `DGR003` technical debt.

## Target & Context Scope

### TARGET Boundaries
- `[MODIFY] @[backend_v2/models/enums.py#L1031-L1041]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart#L475-L495]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py#L171-L173]`
- `[MODIFY] @[backend_v2/api/routers/studio/steps.py#L57-L79]`
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L452-L475]`
- `[MODIFY] @[client_app_v2/lib/core/api/studio_client.dart#L150-L165]`
- `[MODIFY] @[client_app_v2/lib/features/studio/controllers/studio_controller.dart#L285-L315]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L185-L205]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L310-L325]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L420-L530]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L550-L565]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb#L1715-L1735]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb#L1085-L1105]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L22198-L22471]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_steps.py#L77-L88]`
- `[MODIFY] @[backend_v2/tests/integration/test_causal_discovery_seed_integration.py#L71-L88]`
- `[MODIFY] @[client_app_v2/test/features/studio/models/workflow_test.dart#L360-L405]`
- `[NEW] @[client_app_v2/test/features/studio/views/studio_dashboard_steps_tab_test.dart]`

### CONTEXT Boundaries (Read-Only)
- `@[backend_v2/services/orchestrator/engines/causal_discovery_engine.py#L42-L394]`
- `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart#L45-L85]`
- `@[backend_v2/models/domain/step.py#L33-L161]`

---

### Pre-Implementation Technical Debt Cleanups
A pre-flight technical debt audit via `uv run python scripts/audit_technical_debt.py` detected 6 violations across touched targets:
1. **Rule `DGR003` (`flutter_dart_anti_patterns`)** in `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart`:
   - Lines 192, 316, 439, 555 contain raw unlocalized string literals: `"Failed to mint: $e"`.
   - Remediation: Introduce a strongly typed, parameterized localization entry `studioViewsMintDraftError(String error)` into `app_en.arb` and `app_fi.arb` and replace all 4 call sites prior to introducing new feature code.
2. **Rule `TD_ISTQB_NEGATIVE` (`istqb_test_partitions`)** in `backend_v2/tests/unit/api/routers/studio/test_steps.py` and `backend_v2/tests/unit/test_enum_parity.py`:
   - `test_steps.py` Line 1: Touched unit test file lacks ISTQB negative/edge-case partitions (`test_*_not_found`, `test_*_failure`, `test_*_invalid`).
     Remediation: Add negative test functions exercising 404 (missing step), 403 (protected system core step deletion attempt), and 422 (invalid simulation input payload) before concluding Step 1.
   - `test_enum_parity.py` Line 1: Test file lacks negative partition.
     Remediation: Add negative test `test_enum_parity_missing_member_failure` exercising `pytest.raises(AssertionError)` when enum members diverge.

---

### Five-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`backend_v2/models/enums.py`, `client_app_v2/lib/core/models/enums.dart`, & `backend_v2/tests/unit/test_enum_parity.py`** | Banned ad-hoc string query parameters (`"specialists"`); banned uncoordinated cross-language enum mutations; banned untyped fallback filters. | Shared SSOT enum `StepFilterScope` (`specialists`, `system_core`, `all`) with `@JsonEnum()` and `@JsonValue` annotations in Dart and `StrEnum` in Python; verified via bidirectional AST parity test. | Single unified enum definition; zero redundant secondary mapper classes or intermediate string conversion tables. | `uv run pytest backend_v2/tests/unit/test_enum_parity.py` asserts 100% parity between Python and Dart enum definitions. |
| **`backend_v2/api/routers/studio/steps.py` & `backend_v2/services/studio/workflow_service.py`** | Banned anemic router violations (inline step filtering); banned client-side filtering burden; banned untyped boolean flags (`include_system_core: bool`). | PEP 593 `Annotated[StepFilterScope, Query(description="...")]` defaulting to `specialists` on router; service method `list_steps(initiator, scope: StepFilterScope)` using exhaustive Python 3.12+ `match scope:`. | Direct list comprehension filtering within service domain boundary; zero secondary filter pipelines or database index overhead. | `test_steps.py` unit test asserting `scope` query param forwarding to service; `backend_audit_loop.py` with `--ast-strict`. |
| **`client_app_v2/lib/core/api/studio_client.dart` & `client_app_v2/lib/features/studio/controllers/studio_controller.dart`** | Banned in-memory list filtering in UI layer; banned discarding server-filtered payloads; banned unhandled loading states during scope transitions. | `StudioClient.getSteps({StepFilterScope scope})` passing wire query parameter `scope.backendValue`; `StepsController` managing `StepFilterScope _scope` with `setScope(StepFilterScope scope)` method triggering backend re-fetch. | Single controller managing step lifecycle; zero secondary family provider proliferation or redundant cache tiers. | Unit and controller tests verifying `setScope` triggers `getSteps` with expected query parameters; `flutter_audit_loop.py`. |
| **`client_app_v2/lib/features/studio/views/studio_dashboard_view.dart` & `client_app_v2/lib/l10n/app_*.arb`** | Banned raw string literals (`"Failed to mint: $e"`) violating `DGR003`; banned in-memory `.where()` filtering; banned `if-else` cascades for view filtering. | Pure Dumb Painter rendering `blueprints` directly from `stepsControllerProvider`; `SegmentedButton<StepFilterScope>` bound to `StepsController.currentScope`; parameterized `.arb` key `studioViewsMintDraftError(String error)`. | Frontend renders backend results directly without local list manipulation; zero state desynchronization between UI and server. | `uv run python scripts/audit_technical_debt.py` reports 0 `DGR003` violations; widget test `studio_dashboard_steps_tab_test.dart` verifies Dumb Painter rendering across all 3 scopes. |
| **`backend_v2/seed/seed_data.json`** | Banned six redundant duplicate blueprints (`sp_01b1d7100000ca01` through `sp_06b1d7100000ca06`) hardcoding input pairings (`product_text`, `chat_log`, `source_evidence`). | Single canonical universal blueprint `sp_c4a5a1d15c00438a` with slug `step_causal_discovery`, `is_system_core: true`, `engine_type: "causal_discovery"`, and dynamic input agnosticism via `expected_inputs: ["product_text", "chat_log", "reflection_text"]`. | Complete eradication of 6 specialized blueprint clones; zero fallback steps or legacy compatibility bridges. | `uv run python backend_v2/seed/run_seed.py local --dry-run`, `uv run python scripts/audit_database_atoms.py --strict`, and integration test `test_causal_discovery_seed_integration.py`. |
| **`backend_v2/tests/unit/api/routers/studio/test_steps.py`** | Banned `TD_ISTQB_NEGATIVE` violation (absence of negative boundary/error partitions); banned untested default vs explicit scope query parameter forwarding. | Comprehensive test suite with positive partitions (`scope=specialists`, `scope=system_core`, `scope=all`) AND at least 2 negative ISTQB partitions (`test_get_step_not_found_error` for 404, `test_delete_system_core_step_failure` for 403, `test_simulate_step_invalid_input_error` for 422). | Tautological mock asserts eliminated; assertions verify explicit Mock call arguments and HTTP status code mappings. | `uv run python scripts/audit_technical_debt.py --targets backend_v2/tests/unit/api/routers/studio/test_steps.py` reports zero `TD_ISTQB_NEGATIVE` findings; Pytest execution passes 100%. |
| **`backend_v2/tests/integration/test_causal_discovery_seed_integration.py` & `client_app_v2/test/features/studio/models/workflow_test.dart`** | Banned stale slug references (`step_causal_discovery_kokonaisvaltainen`) and stale input specifications in integration/model tests. | Synchronized SSOT slug `step_causal_discovery` across Python and Dart test suites; assert canonical blueprint `sp_c4a5a1d15c00438a`. | Zero duplicate tests for pruned blueprints `sp_01`..`sp_06`. | `uv run pytest backend_v2/tests/integration/test_causal_discovery_seed_integration.py` and `dart test client_app_v2/test/features/studio/models/workflow_test.dart`. |
| **`client_app_v2/test/features/studio/views/studio_dashboard_steps_tab_test.dart`** | Banned untested UI interaction flows; banned unverified SegmentedButton state transitions. | Widget test verifying default selection of `specialists`, clicking `systemCore` and `all` invokes `StepsController.setScope`, and empty state rendering. | Targeted widget test verifying Dumb Painter behavior without mocking heavy application shells. | `flutter test client_app_v2/test/features/studio/views/studio_dashboard_steps_tab_test.dart` passes 100%. |

---

```xml
<execution_protocol>
  <step id="1" name="TECHNICAL DEBT ERADICATION & ARB LOCALIZATION">
    <action>Add localized entries to `client_app_v2/lib/l10n/app_en.arb` and `client_app_v2/lib/l10n/app_fi.arb`.</action>
    <action>Include keys: `studioViewsMintDraftError`, `studioStepFilterSpecialists`, `studioStepFilterSystemCore`, `studioStepFilterAll`.</action>
    <action>Replace all 4 instances of `"Failed to mint: $e"` in `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart` (lines 192, 316, 439, 555) with `l10n.studioViewsMintDraftError(e.toString())`.</action>
    <action>Add negative test partitions to `backend_v2/tests/unit/api/routers/studio/test_steps.py` covering 404 (`test_get_step_not_found_error`), 403 (`test_delete_system_core_step_failure`), and 422 (`test_simulate_step_invalid_input_error`) to eradicate `TD_ISTQB_NEGATIVE` debt.</action>
    <action>Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/studio_dashboard_view.dart` to regenerate Freezed/l10n bindings.</action>
    <action>Execute `uv run python scripts/audit_technical_debt.py --targets backend_v2/tests/unit/api/routers/studio/test_steps.py client_app_v2/lib/features/studio/views/studio_dashboard_view.dart` to verify zero remaining debt.</action>
    <constraint invariant="dgr003_anti_hardcoded_strings">Zero raw hardcoded English/Finnish strings in Text widgets.</constraint>
    <constraint invariant="anti_happy_path_mandate">Every test file must maintain both positive and negative boundary partitions.</constraint>
    <constraint invariant="english_language_mandate">All variable names, comments, and identifiers must remain exclusively in English.</constraint>
  </step>

  <step id="2" name="SSOT ENUM DEFINITION & CROSS-LANGUAGE PARITY">
    <action>Define `StepFilterScope(StrEnum)` in `backend_v2/models/enums.py#L1029-L1039` with members:
      - `SPECIALISTS = "specialists"`
      - `SYSTEM_CORE = "system_core"`
      - `ALL = "all"`
    </action>
    <action>Define `enum StepFilterScope` in `client_app_v2/lib/core/models/enums.dart#L475-L495` with members:
      - `@JsonValue('specialists') specialists('specialists')`
      - `@JsonValue('system_core') systemCore('system_core')`
      - `@JsonValue('all') all('all')`
      - Enhanced enum constructor `const StepFilterScope(this.backendValue); final String backendValue;`
    </action>
    <action>Add parity test `test_step_filter_scope_parity()` to `backend_v2/tests/unit/test_enum_parity.py#L171-L173` asserting exact match between Python and Dart enum values.</action>
    <action>Add negative test `test_enum_parity_missing_member_failure()` to `backend_v2/tests/unit/test_enum_parity.py#L171-L173` asserting `pytest.raises(AssertionError)` when enum members diverge between languages to eliminate `TD_ISTQB_NEGATIVE` debt.</action>
    <action>Execute `uv run pytest backend_v2/tests/unit/test_enum_parity.py` to verify full-duplex cross-language parity.</action>
    <constraint invariant="anti_semantic_drift_renaming">Enum members and wire strings must remain 100% identical across Python and Dart.</constraint>
    <constraint invariant="anti_happy_path_mandate">Every test file must maintain both positive and negative boundary partitions.</constraint>
  </step>

  <step id="3" name="SEED VAULT CAUSAL BLUEPRINT CONSOLIDATION">
    <action>Create a backup of `backend_v2/seed/seed_data.json` inside `backend_v2/seed/backups/`.</action>
    <action>Harmonize canonical Causal Discovery step blueprint `sp_c4a5a1d15c00438a` in `backend_v2/seed/seed_data.json` lines 22198-22230:
      - Name Finnish: "Kausaalipäättelyn ja Argumentaation Louhinta"
      - Name English: "Dynamic Causal Discovery & Argument Mining"
      - Description Finnish: "Louhii kausaaliväitteet, ohjausinterventiot, riippuvuussuhteet ja evidenssin syötedokumenteista."
      - Description English: "Mines causal claims, steering interventions, dependencies, and evidence from input documents."
      - slug: "step_causal_discovery"
      - is_system_core: true
      - engine_type: "causal_discovery"
      - expected_inputs: ["product_text", "chat_log", "reflection_text"]
    </action>
    <action>Prune redundant causal discovery duplicate steps from `backend_v2/seed/seed_data.json`:
      - Specifically and exhaustively remove `sp_01b1d7100000ca01` (lines 22231-22263), `sp_02b1d7100000ca02` (lines 22264-22296), `sp_03b1d7100000ca03` (lines 22297-22329), `sp_04b1d7100000ca04` (lines 22330-22362), `sp_05b1d7100000ca05` (lines 22363-22395), and `sp_06b1d7100000ca06` (lines 22438-22470).
      - Retain HACM Evaluator `sp_06c1d71000000001` intact.
    </action>
    <action>Execute in-memory validation: `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict`.</action>
    <action>Execute seed synchronization: `uv run python backend_v2/seed/run_seed.py local`.</action>
    <action>Update integration test `backend_v2/tests/integration/test_causal_discovery_seed_integration.py` (`DEDICATED_BLUEPRINTS` slug to `step_causal_discovery` and `expected_inputs` to `["product_text", "chat_log", "reflection_text"]`).</action>
    <action>Update unit test `client_app_v2/test/features/studio/models/workflow_test.dart` to assert the harmonized slug `step_causal_discovery` and expected inputs.</action>
    <constraint invariant="live_database_mutation">All modifications must originate in seed_data.json followed by automated validation before syncing to local database.</constraint>
    <constraint invariant="ban_heuristic_identifier_matching">Never identify or filter blueprints by substring matching; resolve strictly through opaque ID `sp_c4a5a1d15c00438a` and `engine_type: EngineType.CAUSAL_DISCOVERY`.</constraint>
  </step>

  <step id="4" name="BACKEND SERVICE & ROUTER SERVER-SIDE FILTERING">
    <action>Update `backend_v2/services/studio/workflow_service.py#L452-L466`:
      - Update signature to `list_steps(self, initiator: TokenData, scope: StepFilterScope = StepFilterScope.SPECIALISTS) -> list[Step]`.
      - Implement exhaustive `match scope:`:
        * `case StepFilterScope.SPECIALISTS: return [s for s in steps if not s.is_system_core]`
        * `case StepFilterScope.SYSTEM_CORE: return [s for s in steps if s.is_system_core]`
        * `case StepFilterScope.ALL: return steps`
    </action>
    <action>Update `backend_v2/api/routers/studio/steps.py#L56-L69`:
      - Add query parameter `scope: Annotated[StepFilterScope, Query(description="Filter steps by scope: specialists, system_core, or all.")] = StepFilterScope.SPECIALISTS` to `get_steps`.
      - Forward `scope` to `studio_workflow_service.list_steps(current_user, scope=scope)`.
    </action>
    <action>Update `backend_v2/tests/unit/api/routers/studio/test_steps.py#L68-L76`:
      - Verify `GET /steps/` defaults `scope` to `StepFilterScope` specialist partition.
      - Verify `GET /steps/?scope=specialists` passes `specialists` scope to service.
      - Verify `GET /steps/?scope=system_core` passes `system_core` scope to service.
      - Verify `GET /steps/?scope=all` passes `all` scope to service.
    </action>
    <constraint invariant="anemic_routers">API router handles parameter extraction and delegates filtering to StudioWorkflowService.</constraint>
    <constraint invariant="zero_service_layer_fallbacks">No naked dictionaries; typed Step entities returned with strict Pydantic V2 validation.</constraint>
  </step>

  <step id="5" name="FLUTTER CLIENT, CONTROLLER & DUMB PAINTER VIEW">
    <action>Update `client_app_v2/lib/core/api/studio_client.dart#L150-L165`:
      - Update `getSteps({StepFilterScope scope = StepFilterScope.specialists}) async`.
      - Pass `queryParameters: {'scope': scope.backendValue}` in `_dio.get('studio/steps')`.
    </action>
    <action>Update `client_app_v2/lib/features/studio/controllers/studio_controller.dart#L285-L315`:
      - In `StepsController`, add field `StepFilterScope _scope = StepFilterScope.specialists;`.
      - Update `build()` to return `_fetchSteps(_scope)`.
      - Add getter `StepFilterScope get currentScope => _scope;`.
      - Add method `Future<void> setScope(StepFilterScope scope)` which sets `_scope`, transitions state to `const AsyncValue.loading()`, fetches `_fetchSteps(_scope)`, and updates state.
      - Update `refresh()` to re-fetch `_fetchSteps(_scope)`.
    </action>
    <action>In `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L420-L530`:
      - In `_buildStepsTab`, add a `SegmentedButton<StepFilterScope>` above the step list with 3 segments:
        * `StepFilterScope.specialists`: label `Text(l10n.studioStepFilterSpecialists)`.
        * `StepFilterScope.systemCore`: label `Text(l10n.studioStepFilterSystemCore)`.
        * `StepFilterScope.all`: label `Text(l10n.studioStepFilterAll)`.
      - Bind `selected` to `{ref.watch(stepsControllerProvider.notifier).currentScope}`.
      - On `onSelectionChanged`, call `ref.read(stepsControllerProvider.notifier).setScope(newSelection.first)`.
      - Render `blueprints` directly from `blueprintsState` without local in-memory `.where()` filtering (Pure Dumb Painter).
      - Render empty state when `blueprints.isEmpty` using `l10n.studioViewsNoStepsDefined`.
    </action>
    <action>Create `[NEW] @[client_app_v2/test/features/studio/views/studio_dashboard_steps_tab_test.dart]`:
      - Test default filter renders specialist blueprints returned by backend.
      - Test selecting `StepFilterScope.systemCore` calls `setScope` and displays returned items.
      - Test selecting `StepFilterScope.all` calls `setScope`.
      - Test empty state rendered when backend returns an empty list.
    </action>
    <constraint invariant="freezed_when_ban">Use Dart 3 switch expressions for enum pattern matching; no Freezed .when() or if-else cascades.</constraint>
    <constraint invariant="studio_unified_visual_design_mandate">Adhere to Theme.of(context).colorScheme, rounded borders, and standard SegmentedButton styling.</constraint>
  </step>

  <step id="6" name="TWO-STAGE QUALITY GATE AUDIT & PERSISTENCE VERIFICATION">
    <action>Execute backend audit loop with strict AST guardrails: `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/studio/steps.py backend_v2/services/studio/workflow_service.py backend_v2/models/enums.py backend_v2/tests/unit/api/routers/studio/test_steps.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict`.</action>
    <action>Execute integration seed verification: `uv run python scripts/backend_audit_loop.py backend_v2/tests/integration/test_causal_discovery_seed_integration.py --test`.</action>
    <action>Execute Flutter audit loop with Freezed/l10n build: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/studio_dashboard_view.dart client_app_v2/lib/features/studio/controllers/studio_controller.dart client_app_v2/lib/core/api/studio_client.dart client_app_v2/lib/core/models/enums.dart client_app_v2/test/features/studio/views/studio_dashboard_steps_tab_test.dart client_app_v2/test/features/studio/models/workflow_test.dart --build`.</action>
    <action>Re-run technical debt audit to confirm zero remaining violations: `uv run python scripts/audit_technical_debt.py --targets backend_v2/api/routers/studio/steps.py backend_v2/services/studio/workflow_service.py backend_v2/tests/unit/api/routers/studio/test_steps.py client_app_v2/lib/features/studio/views/studio_dashboard_view.dart client_app_v2/lib/features/studio/controllers/studio_controller.dart client_app_v2/lib/core/api/studio_client.dart --include-one-hop`.</action>
    <action>Re-run markdown boundary verification: `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Studio_Steps_Filter_and_Causal_Discovery_Harmonization.md`.</action>
    <constraint invariant="zero_tolerance_audit_loop">All automated quality gates must pass with 100% test coverage before completion.</constraint>
  </step>
</execution_protocol>
```


---

## ISTQB Test Matrix & Boundary Scenarios

| Test ID | Scenario | Input | Expected Output | ErrorCode / Assertion |
| :--- | :--- | :--- | :--- | :--- |
| `TST-STP-001` | Backend `GET /steps/` default | No query params (defaults to `scope=specialists`) | Returns exclusively specialist steps (`is_system_core == false`) | `status_code == 200`, all items have `is_system_core == false` |
| `TST-STP-002` | Backend `GET /steps/?scope=system_core` | `scope=system_core` | Returns exclusively system core foundational steps | `status_code == 200`, all items have `is_system_core == true` |
| `TST-STP-003` | Backend `GET /steps/?scope=all` | `scope=all` | Returns complete union of steps | `status_code == 200`, contains both `sp_c4a5a1d15c00438a` and specialist steps |
| `TST-STP-004` | Backend `GET /steps/{id}` missing step | Non-existent step ID `sp_missing00000000` | Returns 404 Not Found with RFC 7807 error payload | `status_code == 404`, `ErrorCodes.RESOURCE_NOT_FOUND` |
| `TST-STP-005` | Backend `DELETE /steps/{id}` system core protection | System core step ID `sp_c4a5a1d15c00438a` | Returns 403 Forbidden preventing mutation of core anchors | `status_code == 403`, `ErrorCodes.SYSTEM_PROTECTED_RESOURCE` |
| `TST-STP-006` | Backend `POST /steps/simulate` invalid input | Malformed body `{}` missing required step definition | Returns 422 Unprocessable Entity fail-fast schema rejection | `status_code == 422`, Pydantic `ValidationError` |
| `TST-STP-007` | Cross-language enum parity | `test_step_filter_scope_parity()` | `StepFilterScope` members match identically between Python and Dart | Parity assertion passes with zero missing members |
| `TST-STP-008` | Seed Vault integrity after consolidation | `validate_all_seed_collections(raw_seed)` | Seed validates cleanly in memory | Zero duplicate IDs, `sp_c4a5a1d15c00438a` exists, `sp_01`..`sp_06` absent |
| `TST-STP-009` | Flutter default view state | `StudioDashboardView` rendered | `SegmentedButton` selected `StepFilterScope.specialists` | Step cards display only specialist blueprints returned by backend |
| `TST-STP-010` | Flutter filter switch to system core | Click segment `systemCore` | Invokes `setScope(StepFilterScope.systemCore)`, triggers backend fetch | Only system core blueprints rendered |
| `TST-STP-011` | Flutter filter switch to all | Click segment `all` | Invokes `setScope(StepFilterScope.all)`, triggers backend fetch | Complete union of blueprints rendered |
| `TST-STP-012` | Flutter empty state | Backend returns empty list for selected scope | Renders `l10n.studioViewsNoStepsDefined` placeholder | Empty state widget rendered; zero layout exceptions |

