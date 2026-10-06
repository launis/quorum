# Phase 4: Test Persistence Migration — Services, Studio, Execution & Database

**Overview:** Migrate 419 census A assignments, 45 census B attribute replacements, 7 census C object patches, 6 fixtures, 269 census D keyword-injected repository mocks, migrate 2 import-only files (`test_dependencies.py`, `test_override_service.py`), delete `dict_to_obj`, replace the 3 `repo._increment_version = MagicMock(...)` partial mocks with version roundtrip assertions over a real `TinyDBDriver` on `tmp_path`, and replace the driver-level mock in `test_repositories_v2.py` with a real `TinyDBDriver` over `tmp_path` across 23 target files.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L449-L478] Phase 4: Test Persistence Migration — Services, Studio, Execution & Database

**Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py#L141-L164]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_execution_resumability.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_report_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_chat_parser.py#L20-L23]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_ingress_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_lifecycle_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L18-L20]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L42-L44]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L47-L49]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L52-L54]
- `[MODIFY]` @[backend_v2/tests/unit/test_auth.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_security.py#L20-L22]
- `[MODIFY]` @[backend_v2/tests/unit/test_usage_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_repo_deletion.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_repositories_v2.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dependencies.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_override_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_stream_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_system_config_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_agent.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Mock-Emulation Fake Usage & Dynamic Attribute Replacement**:
   - 419 census A assignments configuring `.return_value` or `.side_effect` on repository identifiers across 9 files: `test_blueprint.py` (118), `test_execution.py` (87), `test_auth.py` (71), `test_workflow_service.py` (47), `test_report_service.py` (40), `test_ingress_service.py` (30), `test_output_profile_service.py` (10), `test_execution_resumability.py` (8), and `test_usage_service.py` (8).
   - 45 census B attribute replacements assigning `AsyncMock(...)` or `MagicMock(...)` to repository attributes across 6 files: `test_override_service.py` (21), `test_lifecycle_service.py` (18), `test_stream_service.py` (3), `test_agent.py` (1), `test_prompt_block.py` (1), and `test_task_blueprint.py` (1).
   - 7 census C object patches (`patch.object` / `monkeypatch.setattr`) on repository instances across 3 files: `test_system_config_service.py` (5), `test_repo_deletion.py` (1), and `test_prompt_block_service.py` (1).
   - 9 census I files importing `InMemoryBlueprintTransformerRepository`: specifically 7 files with active census A assignments (`test_blueprint.py`, `test_execution.py`, `test_report_service.py`, `test_ingress_service.py`, `test_auth.py`, `test_usage_service.py`, `test_execution_resumability.py`) plus 2 import-only files (`test_dependencies.py` and `test_override_service.py`).
2. **Duck-Typing Helper Elimination**:
   - 8 occurrences of `dict_to_obj` in `backend_v2/tests/unit/services/test_blueprint.py` (definition at lines 141-164, and 5 call sites at lines 170, 420, 580, 862, 1152), converting untyped dictionaries into `SimpleNamespace` objects to bypass Pydantic model validation.
3. **Keyword-Injected Repository Mocks**:
   - 269 census D keyword-injected repository mocks (`exec_repo=AsyncMock(...)`, `workflow_repo=AsyncMock(...)`, `system_repo=AsyncMock(...)`) across 3 files: `test_execution.py` (182), `test_security.py` (80), and `test_legacy_render_service.py` (7).
4. **Unverified AsyncMock Fixtures & Driver Mocks**:
   - 6 repository fixtures returning unverified `AsyncMock`: `test_chat_parser.py#L20-L23` (`mock_repository`), `test_output_profile_service.py#L18-L20` (`mock_output_profile_repo`), `test_workflow_service.py#L42-L44` (`mock_workflow_repo`), `#L47-L49` (`mock_output_profile_repo`), `#L52-L54` (`mock_prompt_block_repo`), and `test_security.py#L20-L22` (`mock_repository`).
   - 1 driver-level mock fixture `mock_driver: AsyncMock` in `test_repositories_v2.py` asserting mock calls across 7 tests rather than verifying real stateful database persistence.
   - 3 partial mocks `repo._increment_version = MagicMock(...)` in component repository test suites (`test_agent.py#L70`, `test_prompt_block.py#L80`, `test_task_blueprint.py#L80`) bypassing version calculation.


## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/unit/services/test_chat_parser.py#L20-L23]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L18-L20]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L42-L44]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L47-L49]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py#L52-L54]`, `@[backend_v2/tests/unit/test_security.py#L20-L22]`, `@[backend_v2/tests/unit/services/test_blueprint.py#L141-L164]`, `@[backend_v2/tests/unit/test_dependencies.py]` | Banned returning unconfigured `AsyncMock()` from repository fixtures. Banned duck-typing helper `dict_to_obj` converting dictionaries to `SimpleNamespace`. Banned importing `InMemoryBlueprintTransformerRepository` in import-only files. | Define typed repository fixtures returning `InMemoryUnifiedWorkflowRepository`, `InMemoryWorkflowRepository`, `InMemoryOutputProfileRepository`, and `InMemoryPromptBlockRepository`. Seed real `Workflow` domain models natively and delete `dict_to_obj`. Replace `InMemoryBlueprintTransformerRepository` in `test_dependencies.py` with `InMemoryUnifiedWorkflowRepository`. | Pruned duck-typing `dict_to_obj` helper and redundant mock wrappers; instantiate canonical in-memory repository fakes. | Localized pytest passes. `Select-String -Path backend_v2/tests -Pattern "dict_to_obj" -Recurse` returns 0. |
| `@[backend_v2/tests/unit/test_repositories_v2.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_agent.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]` | Banned mocking `StorageDriver` via `AsyncMock(spec=StorageDriver)` in repository test suites. Banned partial mocking `repo._increment_version = MagicMock(...)` in component repository updates. | Use a real `TinyDBDriver` initialized over pytest `tmp_path` fixture (`TinyDBDriver(str(tmp_path / "test_repo.json"))`) for all 7 repository tests in `test_repositories_v2.py`. Verify actual stateful roundtrip persistence (`save`, then `get`, assert updated state). Let `_increment_version` execute its real logic and assert incremented version numbers in database files. | Pruned unverified driver mocks and partial mock method overrides; execute real database driver operations in ephemeral isolation. | Unit tests verify real persistence mutations on disk; zero `AsyncMock` driver interactions. |
| `@[backend_v2/tests/unit/services/execution/test_lifecycle_service.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/execution/test_stream_service.py]`, `@[backend_v2/tests/unit/test_repo_deletion.py]`, `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]`, `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]` | Banned 45 Census B attribute replacements (`<repo>.<attr> = AsyncMock(...)`). Banned 7 Census C object patches (`patch.object(<repo>, ...)`, `monkeypatch.setattr(<repo>, ...)`). | Seed test records into `InMemoryExecutionRepository` via `create_execution` and `save`. Seed test entities into `InMemorySystemRepository` and `InMemoryPromptBlockRepository`. Simulate failure paths strictly via unseeded IDs (natural `ResourceNotFoundError`) or deterministic `repo.inject_fault()` and `async with repo.fault_context()`. | Pruned dynamic attribute assignment and runtime monkeypatching; rely on stateful in-memory stores and built-in fault injection. | Census B matches = 0 on target files. Census C matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/test_report_service.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`, `@[backend_v2/tests/unit/test_auth.py]`, `@[backend_v2/tests/unit/test_usage_service.py]` | Banned 419 Census A assignments configuring `.return_value` and `.side_effect` on `InMemoryBlueprintTransformerRepository` instances. Banned Census I imports of the deprecated fake. | Seed test entities using typed repository write methods (`create_workflow`, `save_workflow`, `create_execution`, `save_output_profile`, `create_organization`, `create_user`). Replace all imports with `InMemoryUnifiedWorkflowRepository` or typed sub-repositories. | Pruned mock method synthesizers; use Rust-accelerated Pydantic snapshot stores. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/test_security.py]`, `@[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]` | Banned 269 Census D keyword-injected repository mocks (`exec_repo=AsyncMock(...)`, `workflow_repo=MagicMock(...)`) in service constructors and `HookDependencies`. | Pass typed instances of `InMemoryExecutionRepository` and `InMemoryUnifiedWorkflowRepository` into service constructors and `HookDependencies`. | Pruned untyped `AsyncMock()` keyword arguments. | Census D matches = 0 on target files. Localized pytest passes. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; PERSISTENCE CENSUS PROBE">
    <action>Look backward: Verify Phase 1, Phase 2, and Phase 3 completed successfully with 100% test contracts passed, zero AST violations, Census A=0, B=0, C=0, I=0, D=0, K=0, X=0 across 30 Phase 3 target files, and residual ceilings ratcheted down in scripts/audit_warning_baseline.py.</action>
    <action>Baseline persistence census probe: Execute Census A, B, C, I, D across the 23 Phase 4 target files and verify exact baseline occurrences: Census A=419, Census B=45, Census C=7, Census I=9 files, Census D=269, Fixtures=6 returning AsyncMock, Driver Mocks=1 file (7 tests), Increment Version Mocks=3 files, dict_to_obj=8 occurrences.</action>
    <action>Look forward: Verify that migrating service, studio, execution, and database test persistence doubles to stateful in-memory fakes and real TinyDB storage drivers isolates remaining mocks strictly to DAG Orchestrator (Phase 5) and Workers (Phase 6).</action>
    <constraint invariant="universal_fail_fast">If prior phase contracts fail or baseline census metrics mismatch, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/04_phase4_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="REPOSITORY FIXTURES MODERNIZATION &amp; DICT_TO_OBJ DELETION">
    <action>In @[backend_v2/tests/unit/services/test_chat_parser.py#L20-L23]: Replace def mock_repository() -> AsyncMock: with typed fixture returning InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L18-L20]: Replace def mock_output_profile_repo() -> AsyncMock: with typed fixture returning InMemoryOutputProfileRepository.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L42-L44], @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L47-L49], @[backend_v2/tests/unit/services/studio/test_workflow_service.py#L52-L54]: Replace mock_workflow_repo, mock_output_profile_repo, and mock_prompt_block_repo fixtures returning AsyncMock with typed fixtures returning InMemoryWorkflowRepository, InMemoryOutputProfileRepository, and InMemoryPromptBlockRepository.</action>
    <action>In @[backend_v2/tests/unit/test_security.py#L20-L22]: Replace def mock_repository() -> AsyncMock: with typed fixture returning InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/test_blueprint.py#L141-L164]: Delete def dict_to_obj(d: Any) -> Any: helper function entirely. Migrate all 5 call sites across test_blueprint.py (L170, L420, L580, L862, L1152) to construct and seed strongly typed Workflow domain models via Workflow.model_validate(...) or Workflow(...) directly into InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_dependencies.py]: Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository, and update fixture fake_repo to return InMemoryUnifiedWorkflowRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/test_chat_parser.py backend_v2/tests/unit/services/studio/test_output_profile_service.py backend_v2/tests/unit/services/studio/test_workflow_service.py backend_v2/tests/unit/test_security.py backend_v2/tests/unit/test_dependencies.py backend_v2/tests/unit/services/test_blueprint.py`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Every modernized repository fixture MUST return a functional in-memory fake with state isolation rather than an unverified AsyncMock.</constraint>
    <constraint invariant="the_duct_tape_ban">dict_to_obj duck-typing helper must be completely deleted; all test workflows must pass root Pydantic V2 schema validation.</constraint>
  </step>

  <step id="2" name="DATABASE REPOSITORIES &amp; REAL TINYDB DRIVER MIGRATION">
    <action>In @[backend_v2/tests/unit/test_repositories_v2.py]: Replace @pytest.fixture def mock_driver() -> AsyncMock: with a real StorageDriver backed by TinyDBDriver(str(tmp_path / "test_repo_v2.json")). Convert all 7 test cases (test_execution_repo, test_identity_repo, test_workflow_repo, test_component_repo, test_knowledge_repo, test_system_repo, test_audit_repo) from mock assertion verifications (mock_driver.delete.assert_called_with) to real stateful persistence roundtrip assertions (save/upsert, then get/fetch, asserting actual persisted state survival).</action>
    <action>In @[backend_v2/tests/unit/database/repositories/components/test_agent.py]: Replace mock_driver: AsyncMock with real TinyDBDriver(str(tmp_path / "test_agent.json")). Eradicate repo._increment_version = MagicMock(...) at line 70, allowing the real AppendOnlyRepository._increment_version method to execute and asserting that the updated agent receives a valid incremented version and new ID in storage.</action>
    <action>In @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]: Replace mock_driver: AsyncMock with real TinyDBDriver(str(tmp_path / "test_pb.json")). Eradicate repo._increment_version = MagicMock(...) at line 80, asserting real version incrementation and stateful persistence roundtrip.</action>
    <action>In @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]: Replace mock_driver: AsyncMock with real TinyDBDriver(str(tmp_path / "test_tb.json")). Eradicate repo._increment_version = MagicMock(...) at line 80, asserting real version incrementation and stateful persistence roundtrip.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/test_repositories_v2.py backend_v2/tests/unit/database/repositories/components/test_agent.py backend_v2/tests/unit/database/repositories/components/test_prompt_block.py backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py`.</action>
    <constraint invariant="preflight_schema_assertion_mandate">All persisted and reconstituted database documents must pass root domain model validation against the real TinyDB storage engine without static mock interception.</constraint>
    <constraint invariant="deceptive_persistence_mocking_ban">Zero MagicMock method assignments allowed on _increment_version; version incrementing must be verified via actual roundtrip database records.</constraint>
  </step>

  <step id="3" name="CENSUS B ATTRIBUTE REPLACEMENTS &amp; CENSUS C OBJECT PATCHES">
    <action>In @[backend_v2/tests/unit/services/execution/test_lifecycle_service.py]: Eradicate all 18 Census B attribute replacements (mock_exec_repo.<method> = AsyncMock(...), mock_wf_repo.<method> = AsyncMock(...)). Seed test execution records and workflows into InMemoryExecutionRepository and InMemoryUnifiedWorkflowRepository via create_execution and save.</action>
    <action>In @[backend_v2/tests/unit/services/execution/test_override_service.py]: Eradicate all 21 Census B attribute replacements (exec_repo.<method> = AsyncMock(...)). Replace InMemoryBlueprintTransformerRepository instances in _create_mock_service with InMemoryExecutionRepository and InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository. Seed test executions directly into exec_repo via create_execution.</action>
    <action>In @[backend_v2/tests/unit/services/execution/test_stream_service.py]: Eradicate all 3 Census B attribute replacements (exec_repo.get_execution = AsyncMock(...)). Seed test records via await exec_repo.create_execution(rec).</action>
    <action>In @[backend_v2/tests/unit/test_repo_deletion.py]: Eradicate Census C patch.object(repo, "get_prompt_block_by_id", new_callable=AsyncMock) at line 23. Initialize PromptBlockRepositoryImpl over a real TinyDBDriver on tmp_path, seed the block and referencing step into the database, and verify actual deletion block and blocked-by-usage exceptions natively.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_system_config_service.py]: Eradicate all 5 Census C monkeypatch.setattr calls on system_repo at lines 185, 261, 279, 282, 313. For not-found tests, query non-existent IDs against the unseeded in-memory store. For simulated failures, use system_repo.inject_fault() or system_repo.fault_context().</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]: Eradicate Census C monkeypatch.setattr(prompt_block_repo, "get_prompt_block_by_id", AsyncMock(return_value=None)) at line 164. Query an unseeded block ID or use prompt_block_repo.inject_fault().</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/services/execution/test_lifecycle_service.py backend_v2/tests/unit/services/execution/test_override_service.py backend_v2/tests/unit/services/execution/test_stream_service.py backend_v2/tests/unit/test_repo_deletion.py backend_v2/tests/unit/services/studio/test_system_config_service.py backend_v2/tests/unit/services/studio/test_prompt_block_service.py`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Zero attribute replacements or monkeypatched repository methods permitted. Fault injection must strictly use BaseInMemoryRepository.inject_fault() or fault_context().</constraint>
  </step>

  <step id="4" name="SERVICE &amp; STUDIO PERSISTENCE EMULATION-FAKE MIGRATION (CENSUS A &amp; I)">
    <action>In @[backend_v2/tests/unit/services/test_blueprint.py]: Migrate 118 Census A return_value and side_effect assignments on repository fakes to typed seeding of InMemoryUnifiedWorkflowRepository (create_workflow, save_workflow, save_output_profile). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/test_execution.py]: Migrate 87 Census A return_value assignments to typed seeding in InMemoryExecutionRepository and InMemoryUnifiedWorkflowRepository (create_execution, create_workflow, save_output_profile). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/services/test_execution_resumability.py]: Migrate 8 Census A return_value assignments to typed seeding in InMemoryExecutionRepository and InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/services/test_report_service.py]: Migrate 40 Census A return_value and side_effect assignments to typed seeding in InMemoryUnifiedWorkflowRepository (create_execution, save_output_profile, create_report_artifact). Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/services/execution/test_ingress_service.py]: Migrate 30 Census A return_value assignments to typed seeding in InMemoryUnifiedWorkflowRepository (create_workflow, save_output_profile). Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_output_profile_service.py#L18-L20]: Migrate 10 Census A return_value assignments to typed seeding in InMemoryOutputProfileRepository (create_output_profile, save).</action>
    <action>In @[backend_v2/tests/unit/services/studio/test_workflow_service.py]: Migrate 47 Census A return_value assignments to typed seeding in InMemoryWorkflowRepository, InMemoryOutputProfileRepository, and InMemoryPromptBlockRepository.</action>
    <action>In @[backend_v2/tests/unit/test_auth.py]: Migrate 71 Census A return_value assignments to typed seeding in InMemoryUnifiedWorkflowRepository (create_organization, create_user). Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/test_usage_service.py]: Migrate 8 Census A return_value assignments to typed seeding in InMemoryUnifiedWorkflowRepository (create_organization, log_usage). Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>Execute localized unit tests across all 9 modified files to verify all tests pass cleanly.</action>
    <constraint invariant="repository_reconstitution_mandate">All repository lookups in service, studio, and auth tests must return strictly typed domain models from snapshot storage.</constraint>
    <constraint invariant="the_no_legacy_mandate">Zero imports of InMemoryBlueprintTransformerRepository allowed across Phase 4 target files.</constraint>
  </step>

  <step id="5" name="KEYWORD-INJECTED REPOSITORY MOCKS ERADICATION (CENSUS D)">
    <action>In @[backend_v2/tests/unit/services/test_execution.py]: Eradicate all 182 keyword-injected repository mocks (exec_repo=AsyncMock(...), workflow_repo=AsyncMock(...), system_repo=AsyncMock(...), prompt_block_repo=AsyncMock(...), output_profile_repo=AsyncMock(...), identity_repo=AsyncMock(...), comp_repo=AsyncMock(...)) across ExecutionService and helper instantiations. Pass typed instances of InMemoryExecutionRepository and InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_security.py#L20-L22]: Eradicate all 80 keyword-injected repository mocks across the 10 test functions in HookDependencies (exec_repo=MagicMock(), workflow_repo=MagicMock(), comp_repo=MagicMock(), prompt_block_repo=AsyncMock(), output_profile_repo=AsyncMock(), identity_repo=MagicMock(), audit_repo=MagicMock(), system_repo=MagicMock()). Pass shared or test-scoped InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/services/execution/test_legacy_render_service.py]: Eradicate all 7 keyword-injected repository mocks at lines 508-514 in HookDependencies (exec_repo=AsyncMock(), workflow_repo=AsyncMock(), comp_repo=AsyncMock(), prompt_block_repo=AsyncMock(), output_profile_repo=AsyncMock(), identity_repo=AsyncMock(), system_repo=AsyncMock()). Pass typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>Execute localized unit tests across all 3 files to verify all tests pass cleanly.</action>
    <constraint invariant="the_duct_tape_ban">No naked AsyncMock or MagicMock instances passed as repository dependencies. All keyword-injected dependencies must be instances of BaseInMemoryRepository.</constraint>
  </step>

  <step id="6" name="TWO-STAGE TESTING PIPELINE &amp; ZERO-BYPASS VERIFICATION GATE">
    <action>Execute Census A probe on the 23 Phase 4 target files, asserting exactly 0 matches.</action>
    <action>Execute Census B probe on the 23 Phase 4 target files, asserting exactly 0 matches.</action>
    <action>Execute Census C probe on the 23 Phase 4 target files, asserting exactly 0 matches.</action>
    <action>Execute Census I probe on the 23 Phase 4 target files, asserting exactly 0 matches.</action>
    <action>Execute Census D probe on the 23 Phase 4 target files, asserting exactly 0 matches.</action>
    <action>Execute dict_to_obj elimination verification across tests: `Select-String -Path backend_v2/tests -Pattern "dict_to_obj" -Recurse` asserting exactly 0 matches.</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Ratchet down CURRENT_RESIDUAL_CEILINGS in scripts/audit_warning_baseline.py to reflect eradicated Census D matches (lowering ceiling by 269 from 442 to 173).</action>
    <constraint invariant="fragmented_quality_gates_prevention">Completion requires passing global backend audit loop, SDUI semantic parity, and zero residual census matches across all 23 target files.</constraint>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, I, and D restricted to the 23 target files return 0 matches.</item>
    <item>dict_to_obj helper is deleted and Select-String reports 0 occurrences across backend_v2/tests.</item>
    <item>Real TinyDBDriver over tmp_path verifies repository persistence in test_repositories_v2.py.</item>
    <item>Real TinyDBDriver over tmp_path verifies version incrementation and stateful persistence in test_agent.py, test_prompt_block.py, and test_task_blueprint.py.</item>
    <item>All 6 repository fixtures returning AsyncMock are replaced with typed in-memory repository instances.</item>
    <item>All 419 Census A .return_value and .side_effect assignments on repository fakes are replaced with typed seeding.</item>
    <item>All 45 Census B attribute replacements across the 6 target files are replaced with typed seeding or inject_fault().</item>
    <item>All 7 Census C object patches across the 3 target files are replaced with typed seeding or inject_fault().</item>
    <item>All 269 Census D keyword-injected repository mocks are replaced with stateful in-memory repository instances.</item>
    <item>Residual debt ceilings in scripts/audit_warning_baseline.py are ratcheted down monotonically (Census D ceiling lowered by 269).</item>
    <item>Universal audit loop uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes cleanly with 0 AST violations and 0 MyPy issues.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
    <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
    <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 4 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT modify orchestrator or worker persistence doubles during Phase 4 (quarantined strictly for Phases 5-6).</anti_target>
    <anti_target>Do NOT re-introduce cast(Any, ...) or raw dictionary return values to satisfy test fixtures.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A, B, C, I, D check on Phase 4 targets asserting 0 matches.</action>
    <action>Execute dict_to_obj elimination verification across tests asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
