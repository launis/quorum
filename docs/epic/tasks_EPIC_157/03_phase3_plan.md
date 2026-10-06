# Phase 3: Test Persistence Migration — Hooks & LLM

**Overview:** Replace `InMemoryBlueprintTransformerRepository` return_value and side_effect seeding and `AsyncMock` repository fixtures with typed seeding of `InMemoryUnifiedWorkflowRepository` and `InMemorySystemRepository`, asserting roundtrip state across 30 hook and LLM test files. Eradicate 87 census A assignments, 13 census B attribute replacements, 12 census I fake imports, 379 census D keyword-injected mocks, 25 census K ad-hoc classes, and 792 census X `cast(Any, ...)` invocations.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L411-L447] Phase 3: Test Persistence Migration — Hooks & LLM

**Target Files:**
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_archival.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_atom_flattening.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_input_processing.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_integrity.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_matrix_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_passivity_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_scoring.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_interaction_hook.py#L24-L26]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_client.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_llm_client_tiers.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_handler.py#L31-L34]
- `[MODIFY]` @[backend_v2/tests/unit/test_llm_context_bounds.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_epic66_multi_provider.py#L12-L14]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_structured_retry.py]
- `[MODIFY]` @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_validation.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_linguistics.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_metadata.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_references.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_security.py]
- `[MODIFY]` @[backend_v2/tests/unit/hooks/test_dlq_guard.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_input_processing.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metadata.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metrics.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_references.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/core/test_hook_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/test_google_providers_separation.py]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Mock-Emulation Fake Usage & Dynamic Attribute Replacement**:
   - 87 census A assignments configuring `.return_value` or `.side_effect` on repository identifiers across 12 files.
   - 13 census B attribute replacements assigning `AsyncMock(...)` or `MagicMock(...)` to repository attributes in `backend_v2/tests/unit/hooks/test_matrix_hook.py`.
   - 12 census I files importing `InMemoryBlueprintTransformerRepository`, specifically 10 files with active census A assignments plus 2 zero-census-A files with active instantiation: `backend_v2/tests/unit/llm/test_structured_retry.py#L35-L37` (active repository fixture returning the fake) and `backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py#L171` (direct instantiation `mock_repo = InMemoryBlueprintTransformerRepository()`).
2. **Ad-Hoc Repository Classes & Cast(Any) Type Bypass**:
   - 25 census K ad-hoc repository classes returning raw untyped dictionaries: 15 in `backend_v2/tests/unit/hooks/test_scoring.py` (specifically: `MockRepository` at L146, `MockRepoTapa2` at L247, `MockRepoWaterfall` at L1111, `MockRepoWaterfallMixed` at L1772, `MockRepoWaterfallInverse` at L1775, L1844, L2060, `MockRepoWaterfallInverseNoOverrides` at L1922, `MockRepoWaterfallNoOverrides` at L1998, `MockRepoWaterfallSimulation` at L2224, `MockOutputProfileRepoWaterfallPropagates` at L2856, L2927, L2991, L3055, and `MockRepoWaterfallStrict` at L3093), 4 in `backend_v2/tests/unit/hooks/test_input_processing.py` (`MockInputProcessingRepo`, `ChatWFRepo`, `SmoothWFRepo`, `EmptyDescWFRepo`), 2 in `backend_v2/tests/unit/test_input_processing.py` (`MockRepository`, `FeatureFlagMockRepository`), 1 in `backend_v2/tests/unit/hooks/test_dlq_guard.py` (`DummyRepository`), 1 in `backend_v2/tests/unit/hooks/test_metadata.py` (`MockRepository`), 1 in `backend_v2/tests/unit/hooks/test_references.py` (`MockRepository`), and 1 in `backend_v2/tests/unit/hooks/test_security.py` (`MockRepository`).
   - 792 census X `cast(Any, ...)` type bypasses used exclusively to inject these ad-hoc classes into typed `HookDependencies` constructors: 688 in `backend_v2/tests/unit/hooks/test_scoring.py`, 41 in `backend_v2/tests/unit/hooks/test_security.py`, 25 in `backend_v2/tests/unit/hooks/test_metadata.py`, 25 in `backend_v2/tests/unit/hooks/test_references.py`, 8 in `backend_v2/tests/unit/hooks/test_input_processing.py`, 3 in `backend_v2/tests/unit/test_input_processing.py`, and 2 in `backend_v2/tests/unit/hooks/test_passivity_hook.py`.
3. **Keyword-Injected Repository Mocks**:
   - 379 census D keyword-injected repository mocks (`exec_repo=AsyncMock(...)`, `workflow_repo=MagicMock(...)`) across 13 files, specifically: `test_validation.py` (160), `hooks/test_input_processing.py` (56), `test_metadata.py` (48), `test_input_processing.py` (21), `test_synthesis_distiller_hook.py` (16), `test_hook_registry.py` (16), `test_source_verification_hook.py` (15), `hooks/test_interaction_hook.py` (14), `test_linguistics.py` (8), `test_metrics.py` (8), `test_references.py` (8), `test_matrix_hook.py` (5), and `test_google_providers_separation.py` (4).
4. **Fixture Repositories**:
   - 3 repository fixtures returning raw `AsyncMock()`: `backend_v2/tests/unit/test_epic66_multi_provider.py#L12-L14`, `backend_v2/tests/unit/test_handler.py#L31-L34`, and `backend_v2/tests/unit/hooks/test_interaction_hook.py#L24-L26`.


## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/unit/test_epic66_multi_provider.py#L12-L14]`, `@[backend_v2/tests/unit/test_handler.py#L31-L34]`, `@[backend_v2/tests/unit/hooks/test_interaction_hook.py#L24-L26]`, `@[backend_v2/tests/unit/llm/test_structured_retry.py]`, `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]` | Banned returning unconfigured `AsyncMock()` from repository fixtures. Banned instantiating `InMemoryBlueprintTransformerRepository` in test helpers and fixtures. | Define typed repository fixtures returning `InMemoryUnifiedWorkflowRepository` in provider and handler suites, and `InMemoryUnifiedWorkflowRepository` in interaction hook suite. Replace `InMemoryBlueprintTransformerRepository` instances in structured retry and CDATA hardening with `InMemoryUnifiedWorkflowRepository`. | Pruned redundant custom mock fixture wrappers; use canonical in-memory fakes. | Localized pytest suite passes. Census I matches decrease by 2. |
| `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`, `@[backend_v2/tests/unit/test_input_processing.py]`, `@[backend_v2/tests/unit/hooks/test_dlq_guard.py]`, `@[backend_v2/tests/unit/hooks/test_metadata.py]`, `@[backend_v2/tests/unit/hooks/test_references.py]`, `@[backend_v2/tests/unit/hooks/test_security.py]` | Banned 25 ad-hoc repository classes returning loose raw dictionaries. Banned 792 `cast(Any, ...)` bypasses injecting unverified fakes into `HookDependencies`. | Replace ad-hoc classes with `InMemoryUnifiedWorkflowRepository` or typed sub-repositories implementing `backend_v2/database/interfaces.py` protocols. Seed state with typed Pydantic V2 domain models. Remove all `cast(Any, ...)` calls. | Pruned 25 bespoke fake classes; consolidate state into canonical in-memory repository fakes. | Census K matches = 0 on target files. Census X matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/hooks/test_archival.py]`, `@[backend_v2/tests/unit/hooks/test_atom_flattening.py]`, `@[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`, `@[backend_v2/tests/unit/hooks/test_integrity.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/hooks/test_passivity_hook.py]` | Banned configuring `.return_value` and `.side_effect` on `InMemoryBlueprintTransformerRepository`. Banned dynamic attribute replacement `<repo>.<attr> = AsyncMock(...)`. | Seed test state using typed repository write methods (`create_workflow`, `save`, `create_step`, `save_prompt_block`). Simulate failure branches strictly via `repo.inject_fault()` and `async with repo.fault_context()`. Replace imports with `InMemoryUnifiedWorkflowRepository`. | Pruned dynamic attribute assignment; use deterministic in-memory snapshot stores. | Census A matches = 0 on target files. Census B matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/llm/test_client.py]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, `@[backend_v2/tests/unit/test_handler.py]`, `@[backend_v2/tests/unit/test_llm_context_bounds.py]` | Banned `.return_value` configuration on LLM client and handler repository parameters. Banned fake synthesis via `InMemoryBlueprintTransformerRepository`. | Seed `SystemSettingsDTO`, `SystemConfigModelRegistry`, and model profiles via typed repository fakes. Replace imports with `InMemoryUnifiedWorkflowRepository`. Assert roundtrip configuration retrieval. | Pruned monkeypatched repository methods in handler tests. | Census A matches = 0 on target files. Census I matches = 0 on target files. Localized pytest passes. |
| `@[backend_v2/tests/unit/hooks/test_validation.py]`, `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/hooks/test_linguistics.py]`, `@[backend_v2/tests/unit/test_metadata.py]`, `@[backend_v2/tests/unit/test_metrics.py]`, `@[backend_v2/tests/unit/test_references.py]`, `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`, `@[backend_v2/tests/unit/core/test_hook_registry.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]` | Banned 379 keyword mock injections (`exec_repo=AsyncMock(...)`, `workflow_repo=MagicMock(...)`) bypassing repository state management. | Inject canonical `InMemoryUnifiedWorkflowRepository` or `InMemorySystemRepository` instances into `HookDependencies` and execution constructors. | Pruned untyped `AsyncMock()` keyword arguments. | Census D matches = 0 on target files. Localized pytest passes. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT &amp; PERSISTENCE CENSUS PROBE">
    <action>Look backward: Verify Phase 1 and Phase 2 completed successfully, establishing typed AppException contracts, ProblemDetailDTO, CachingPayloadResultDTO, MatrixAggregationStateDTO, LinguisticAnalysisDTO, and clean mypy baseline.</action>
    <action>Baseline persistence census probe: Execute Census A, B, C, I, D, K, X across the 30 Phase 3 target files and verify exact baseline occurrences: A=87, B=13, C=0, I=12, D=379, K=25, X=792.</action>
    <action>Look forward: Verify that migrating hook and LLM persistence doubles to stateful in-memory fakes provides required typing covenants for service, studio, execution, and orchestrator migrations in Phases 4-6.</action>
    <constraint invariant="universal_fail_fast">If prior phase contracts fail or baseline census metrics mismatch, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/03_phase3_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="ASYNC MOCK FIXTURES &amp; REPOSITORY FAKE REPLACEMENT">
    <action>In @[backend_v2/tests/unit/test_epic66_multi_provider.py#L12-L14]: Replace def mock_repo() -> AsyncMock: with typed fixture returning InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/test_handler.py#L31-L34]: Replace def mock_repo() -> AsyncMock: with typed fixture returning InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_interaction_hook.py#L24-L26]: Replace def mock_repository() -> AsyncMock: with typed fixture returning InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/llm/test_structured_retry.py]: Replace def mock_repository() -> InMemoryBlueprintTransformerRepository: fixture and type annotations with InMemoryUnifiedWorkflowRepository. Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]: Replace mock_repo = InMemoryBlueprintTransformerRepository() with mock_repo = InMemoryUnifiedWorkflowRepository(). Replace import of InMemoryBlueprintTransformerRepository with InMemoryUnifiedWorkflowRepository.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/test_epic66_multi_provider.py backend_v2/tests/unit/test_handler.py backend_v2/tests/unit/hooks/test_interaction_hook.py backend_v2/tests/unit/llm/test_structured_retry.py backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Every modernized repository fixture MUST return a functional in-memory fake with state isolation rather than an unverified AsyncMock.</constraint>
  </step>

  <step id="2" name="AD-HOC REPOSITORY CLASSES &amp; CAST(ANY) ERADICATION (CENSUS K &amp; X)">
    <action>In @[backend_v2/tests/unit/hooks/test_scoring.py]: Eradicate all 15 ad-hoc classes (MockRepository, MockRepoTapa2, MockRepoWaterfall, MockRepoWaterfallMixed, MockRepoWaterfallInverse, MockRepoWaterfallInverseNoOverrides, MockRepoWaterfallNoOverrides, MockRepoWaterfallSimulation, MockOutputProfileRepoWaterfallPropagates, MockRepoWaterfallStrict). Replace with stateful typed in-memory repositories (InMemoryUnifiedWorkflowRepository, InMemoryPromptBlockRepository, InMemoryWorkflowRepository, InMemoryOutputProfileRepository) seeded with strongly typed domain models (Workflow, Step, PromptBlock, OutputProfile). Eradicate all 688 cast(Any, ...) calls used to inject these ad-hoc classes into HookDependencies.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_input_processing.py]: Eradicate 4 ad-hoc classes (MockInputProcessingRepo, ChatWFRepo, SmoothWFRepo, EmptyDescWFRepo) and 8 cast(Any, ...). Use InMemoryUnifiedWorkflowRepository seeded with valid typed workflows and expected inputs.</action>
    <action>In @[backend_v2/tests/unit/test_input_processing.py]: Eradicate 2 ad-hoc classes (MockRepository, FeatureFlagMockRepository) and 3 cast(Any, ...). Use InMemoryUnifiedWorkflowRepository seeded with typed workflow configurations.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_dlq_guard.py]: Eradicate DummyRepository. Replace with typed InMemoryUnifiedWorkflowRepository.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_metadata.py], @[backend_v2/tests/unit/hooks/test_references.py], and @[backend_v2/tests/unit/hooks/test_security.py]: Eradicate MockRepository in each file and their associated 25, 25, and 41 cast(Any, ...) calls. Pass typed in-memory repositories to HookDependencies without dynamic casts.</action>
    <action>Execute localized unit tests across all 7 modified files to verify all tests pass.</action>
    <constraint invariant="the_zero_compromise_pledge">Absolute zero cast(Any, ...) permitted in test suites. All repository doubles must satisfy typed database interfaces natively.</constraint>
  </step>

  <step id="3" name="HOOK PERSISTENCE EMULATION-FAKE MIGRATION (CENSUS A &amp; B)">
    <action>In @[backend_v2/tests/unit/hooks/test_archival.py]: Replace 6 InMemoryBlueprintTransformerRepository return_value assignments with typed seeding via InMemoryUnifiedWorkflowRepository.create_workflow() and save(). Replace import.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_atom_flattening.py]: Replace 16 return_value assignments with typed step and block seeding in InMemoryUnifiedWorkflowRepository. Replace import.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]: Replace 2 return_value assignments with typed workflow and block seeding in InMemoryUnifiedWorkflowRepository. Replace import.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_integrity.py]: Replace 2 return_value assignments with typed execution and step seeding.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_matrix_hook.py]: Replace 5 Census A return_value assignments and 13 Census B attribute replacements (repo.<method> = AsyncMock(...)) with typed state seeding and deterministic repo.inject_fault() and repo.fault_context() for simulated failure paths. Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_passivity_hook.py]: Replace 12 return_value assignments and 2 remaining cast(Any, ...) with typed seeding of InMemoryUnifiedWorkflowRepository and InMemorySystemRepository. Replace import.</action>
    <action>Execute localized unit tests across all 6 hook files to verify all tests pass.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">Banned attribute replacement on repository fakes. Fault injection must use BaseInMemoryRepository.inject_fault() or fault_context().</constraint>
  </step>

  <step id="4" name="LLM CLIENT &amp; HANDLER PERSISTENCE MIGRATION (CENSUS A)">
    <action>In @[backend_v2/tests/unit/llm/test_client.py]: Replace 4 repo.get_system_settings.return_value = ... and related assignments with typed SystemSettingsDTO seeding into InMemoryUnifiedWorkflowRepository or InMemorySystemRepository. Replace import of InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/llm/test_llm_client_tiers.py]: Replace 8 .return_value assignments on system and model profile repos with typed SystemConfigModelRegistry seeding in InMemoryUnifiedWorkflowRepository. Replace import.</action>
    <action>In @[backend_v2/tests/unit/test_handler.py]: Replace 14 .return_value assignments on mock_repo with typed seeding of InMemoryUnifiedWorkflowRepository (model profiles, system settings, gateways).</action>
    <action>In @[backend_v2/tests/unit/test_llm_context_bounds.py]: Replace 10 .return_value assignments with typed system config and tier seeding in InMemoryUnifiedWorkflowRepository. Replace import.</action>
    <action>Execute localized unit tests across all 4 LLM files to verify all tests pass.</action>
    <constraint invariant="repository_reconstitution_mandate">All repository lookups in client and handler tests must return strictly typed domain models from snapshot storage.</constraint>
  </step>

  <step id="5" name="KEYWORD-INJECTED REPOSITORY MOCKS ERADICATION (CENSUS D)">
    <action>In @[backend_v2/tests/unit/hooks/test_validation.py]: Eradicate 160 system_repo=AsyncMock(...), workflow_repo=AsyncMock(...) keyword mock injections in HookDependencies. Inject shared or test-scoped InMemoryUnifiedWorkflowRepository and InMemorySystemRepository fakes.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_input_processing.py] and @[backend_v2/tests/unit/test_input_processing.py]: Eradicate 56 and 21 keyword mock injections. Inject typed InMemoryUnifiedWorkflowRepository instances.</action>
    <action>In @[backend_v2/tests/unit/test_metadata.py], @[backend_v2/tests/unit/test_metrics.py], and @[backend_v2/tests/unit/test_references.py]: Eradicate 48, 8, and 8 keyword mock injections in HookDependencies.</action>
    <action>In @[backend_v2/tests/unit/test_synthesis_distiller_hook.py] and @[backend_v2/tests/unit/core/test_hook_registry.py]: Eradicate 16 and 16 keyword mock injections.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_source_verification_hook.py], @[backend_v2/tests/unit/hooks/test_interaction_hook.py], @[backend_v2/tests/unit/hooks/test_linguistics.py], @[backend_v2/tests/unit/hooks/test_matrix_hook.py], and @[backend_v2/tests/unit/llm/test_google_providers_separation.py]: Eradicate 15, 14, 8, 5, and 4 keyword mock injections.</action>
    <action>Execute localized unit tests across all 13 files to verify all tests pass.</action>
    <constraint invariant="the_duct_tape_ban">No naked AsyncMock instances passed as repository dependencies. All keyword-injected dependencies must be instances of BaseInMemoryRepository.</constraint>
  </step>

  <step id="6" name="TWO-STAGE TESTING PIPELINE &amp; ZERO-BYPASS VERIFICATION GATE">
    <action>Execute Census A, B, C, I check on Phase 3 targets asserting exactly 0 matches.</action>
    <action>Execute Census D, K, X check on Phase 3 targets asserting exactly 0 matches.</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Execute SDUI semantic parity gate: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Completion requires passing global backend audit loop and zero residual census matches across all 30 target files.</constraint>
  </step>

  <dod_checklist>
    <item>Census commands A, B, C, and I restricted to the 30 target files return 0 matches.</item>
    <item>Census commands D, K, and X restricted to the 30 target files return 0 matches.</item>
    <item>All 25 ad-hoc repository classes (Census K) across the 7 hook test files are completely deleted.</item>
    <item>All 792 cast(Any, ...) calls (Census X) across the 7 hook test files are completely eradicated.</item>
    <item>All 3 repository fixtures returning AsyncMock are replaced with typed in-memory repository instances.</item>
    <item>All 87 Census A .return_value and .side_effect assignments on repository fakes are replaced with typed seeding.</item>
    <item>All 13 Census B attribute replacements in test_matrix_hook.py are replaced with typed seeding or inject_fault().</item>
    <item>All 379 Census D keyword-injected repository mocks are replaced with stateful in-memory repository instances.</item>
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
    <anti_target>Do NOT delete DynamicRepoMethod or InMemoryBlueprintTransformerRepository during Phase 3 (quarantined strictly for Phase 7).</anti_target>
    <anti_target>Do NOT migrate worker test patches or orchestrator mocks during Phase 3 (quarantined strictly for Phases 4-6).</anti_target>
    <anti_target>Do NOT re-introduce cast(Any, ...) or raw dictionary return values to satisfy test fixtures.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census A, B, C, I check on Phase 3 targets asserting 0 matches.</action>
    <action>Execute Census D, K, X check on Phase 3 targets asserting 0 matches.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
