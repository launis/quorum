# Phase 7: Mock-Emulation Sunset & QGR014 FATAL Hardening

**Overview:** Delete `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository`, replace `inject_fault` reflection with a positive registry, and land the hardened `QGR014` detections (a)-(g) at FATAL severity.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] Phase 7: Mock-Emulation Sunset & QGR014 FATAL Hardening (Epic baseline lines: #L529-L547, #L128-L133, #L1747-L1835, #L1838-L1889, #L417-L831, #L1133-L1137, #L1319-L1360).

**Target Files (7 files):**
- `[MODIFY]` @[backend_v2/tests/fakes/in_memory_repositories.py]
- `[MODIFY]` @[backend_v2/tests/fakes/__init__.py]
- `[MODIFY]` @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Reflection Duck-Typing in Test Fake**:
   - `BaseInMemoryRepository.inject_fault` at lines 131-136 in `backend_v2/tests/fakes/in_memory_repositories.py` uses `getattr(self, method_name, None)` accompanied by `# noqa: QGR001 [REASON: ...]`. This inline suppression and reflection call must be eradicated in favor of positive method existence validation using `inspect.getattr_static(type(self), method_name, None)` (banning `base.__dict__` which triggers FATAL `QGR001`).
2. **Obsolete Mock-Emulation Subsystem**:
   - Class `DynamicRepoMethod` (lines 2048-2138) and class `InMemoryBlueprintTransformerRepository` (lines 2139-2204) in `backend_v2/tests/fakes/in_memory_repositories.py` provide a dynamic mocking facade that allows unverified attribute access and mock call assertions. Both classes must be permanently deleted.
3. **Dead Emulation Unit Tests**:
   - `backend_v2/tests/unit/fakes/test_in_memory_repositories.py` imports `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository` (lines 40, 43) and defines `test_in_memory_blueprint_transformer_repository_and_dynamic_method` (lines 765-838). This test function and its imports must be deleted.
4. **Decorator Repository Patches & Return Value Assignments in Worker Synthesis Tests**:
   - `backend_v2/tests/unit/test_worker_synthesis.py` (16 test functions at lines 67, 268, 322, 374, 399, 445, 479, 565, 685, 760, 845, 936, 1012, 1122, 1168, 1210) and `backend_v2/tests/unit/test_worker_synthesis_accumulation.py` (1 test function at line 119) declare `@patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` on function decorators and subsequently assign `mock_repo_class.return_value = mock_repo`. Under hardened QGR014 (b) and (f), both the un-bound decorator patch and the `.return_value =` assignment on a repository identifier will trigger FATAL violations. These 17 test sites must be migrated to `with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):` wrapping worker task execution.
5. **Under-Enforced QGR014 AST Guardrail**:
   - `scripts/_ast_guardrails.py` only inspects `spec=I*Repository` keyword arguments and `@patch` calls when `"service"` is present in the file path, permitting ad-hoc attribute assignments (`repo.get_user = AsyncMock()`), return value overrides (`repo.get_user.return_value = ...`), keyword mock injection (`HookDependencies(exec_repo=AsyncMock())`), and string-target patches outside services. QGR014 must be expanded to cover detections (a)-(g) at FATAL severity.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/fakes/in_memory_repositories.py]` | Banned reflection via `getattr(self, method_name, None)`. Banned `base.__dict__` access (violates QGR001). Banned `# noqa: QGR001` inline suppression. Banned mock-emulation classes `DynamicRepoMethod` and `InMemoryBlueprintTransformerRepository`. | Validate method existence via positive static inspection `inspect.getattr_static(type(self), method_name, None) is not None and callable(...)` with class-level `_BASE_EXCLUDED_METHODS`. Enforce stateful in-memory stores with zero dynamic mock wrappers. | Deleted 157 lines of dynamic mock emulation code; zero replacement wrapper classes. | `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod\|InMemoryBlueprintTransformerRepository" -Recurse` returns 0 matches. Unit tests pass cleanly. |
| `@[backend_v2/tests/fakes/__init__.py]` | Banned re-export of obsolete mock-emulation classes or deprecated test doubles. | Expose strictly strongly typed in-memory repository fakes implementing domain Protocol interfaces. | Clean `__all__` list with zero deprecated mock-emulation symbols. | Import scan confirms 0 references to eradicated symbols. |
| `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]` | Banned testing dynamic method synthesis, mock assertions (`assert_called_once`, `call_args`), or loose attribute injection. | Assert real in-memory persistence and deterministic fault injection via `inject_fault()`. | Deleted obsolete `test_in_memory_blueprint_transformer_repository_and_dynamic_method` test function. | `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py` passes 100%. |
| `@[backend_v2/tests/unit/test_worker_synthesis.py]` | Banned decorator `@patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` without fake binding. Banned `mock_repo_class.return_value = mock_repo` attribute assignments. | Scope repository patches via `with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):` wrapping worker task execution across all 16 test functions. | Eradicated 16 parameter-mock decorator pairs; unified into local context manager patches bound to typed fakes. | `uv run pytest backend_v2/tests/unit/test_worker_synthesis.py` passes 100%. |
| `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]` | Banned decorator `@patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` without fake binding. Banned `mock_repo_class.return_value = fake_repo` attribute assignment. | Scope repository patch via `with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=fake_repo):` wrapping worker task execution at line 119. | Eradicated 1 parameter-mock decorator pair; unified into local context manager patch bound to typed fake. | `uv run pytest backend_v2/tests/unit/test_worker_synthesis_accumulation.py` passes 100%. |
| `@[scripts/_ast_guardrails.py]` | Banned narrow `"service" in filepath` heuristics and substring target matching. Banned persistence mocks in test suites. | Implement shared `_is_repository_identifier` predicate and positive repository/method sets. Harden QGR014 with detections (a)-(g) at FATAL severity. | Pruned divergent regex patterns across visitor methods; unified into one shared identifier predicate and two cached positive sets. | `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict` reports 0 violations. |
| `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]` | Banned unverified guardrail rules lacking negative and positive false-positive immunity test fixtures. | Implement 7 negative test fixtures covering detections (a)-(g) and 4 positive test fixtures asserting immunity for non-repository mocks and legitimate driver patches. | Focused test assertions for each discrete QGR014 AST detection branch. | `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py` passes 100%. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; BASELINE PRE-CONDITION VERIFICATION">
    <action>Look backward: Verify Phase 6 completed successfully with Census A = 0, Census I = 0, Census D = 0, Census K = 0 across the entire codebase outside tests/unit/fakes/, and all 50/51 Census F worker patches bound to typed in-memory fakes.</action>
    <action>Baseline persistence census probe: Run Census I probe `Get-ChildItem backend_v2/tests -Recurse -Filter "*.py" | Where-Object { $_.FullName -notmatch "\\tests\\fakes\\|\\tests\\unit\\fakes\\" } | Select-String -Pattern "InMemoryBlueprintTransformerRepository"` and verify it returns exactly 0 matches.</action>
    <action>Look forward: Verify that deleting DynamicRepoMethod and InMemoryBlueprintTransformerRepository, removing inject_fault reflection, and hardening QGR014 at FATAL severity permanently locks the test suite against deceptive persistence mocks.</action>
    <constraint invariant="universal_fail_fast">If any file outside tests/fakes/ or tests/unit/fakes/ imports InMemoryBlueprintTransformerRepository, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/07_phase7_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="INJECT_FAULT REFLECTION ERADICATION IN BASE IN-MEMORY REPOSITORY">
    <action>In @[backend_v2/tests/fakes/in_memory_repositories.py]: Refactor BaseInMemoryRepository.inject_fault (lines 131-136) to eliminate getattr(self, method_name, None) and remove the `# noqa: QGR001 [REASON: ...]` comment token.</action>
    <action>Define class-level constant `_BASE_EXCLUDED_METHODS = frozenset({"inject_fault", "clear_faults", "fault_context", "get_call_count"})` on BaseInMemoryRepository.</action>
    <action>Validate method_name using positive static method existence inspection: import inspect at module level; verify method_name does not start with "_" and method_name is not in self._BASE_EXCLUDED_METHODS; evaluate `val = inspect.getattr_static(type(self), method_name, None)`; if val is None or not callable(val), raise ValueError(f"Method '{method_name}' does not exist on {type(self).__name__}"). (Strictly avoiding `base.__dict__` which triggers QGR001 FATAL).</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py`.</action>
    <constraint invariant="the_zero_compromise_pledge">Absolute zero getattr, hasattr, or reflection in BaseInMemoryRepository. Zero # noqa comment tokens.</constraint>
  </step>

  <step id="2" name="MOCK-EMULATION LAYER SUNSET &amp; DEAD TEST ELIMINATION">
    <action>In @[backend_v2/tests/fakes/in_memory_repositories.py]: Permanently delete class DynamicRepoMethod (lines 2048-2138) and class InMemoryBlueprintTransformerRepository (lines 2139-2204).</action>
    <action>In @[backend_v2/tests/fakes/__init__.py]: Verify __all__ and imports contain zero references to DynamicRepoMethod or InMemoryBlueprintTransformerRepository.</action>
    <action>In @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]: Remove imports of DynamicRepoMethod and InMemoryBlueprintTransformerRepository (lines 40, 43). Permanently delete the test function test_in_memory_blueprint_transformer_repository_and_dynamic_method (lines 765-838).</action>
    <action>Execute symbol probe: `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository" -Recurse` asserting 0 matches.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/fakes/test_in_memory_repositories.py`.</action>
    <constraint invariant="the_no_legacy_mandate">Zero backward-compatibility shims or retained aliases for eradicated mock-emulation classes.</constraint>
  </step>

  <step id="3" name="SYNTHESIS WORKER TEST DECORATOR PATCH MIGRATION">
    <action>In @[backend_v2/tests/unit/test_worker_synthesis.py]: For all 16 test functions declaring `@patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` (lines 67, 268, 322, 374, 399, 445, 479, 565, 685, 760, 845, 936, 1012, 1122, 1168, 1210): remove the `@patch` decorator and `mock_repo_class: AsyncMock` argument, remove `mock_repo_class.return_value = mock_repo`, and wrap the call to `generate_profile_synthesis_and_pdf_task` inside `with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):`.</action>
    <action>In @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]: At line 119, remove `@patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` and `mock_repo_class: AsyncMock` argument, remove `mock_repo_class.return_value = fake_repo`, and wrap the task call inside `with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=fake_repo):`.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/test_worker_synthesis.py backend_v2/tests/unit/test_worker_synthesis_accumulation.py` asserting 100% pass.</action>
    <constraint invariant="anti_ambiguity_mandate">All 17 worker synthesis test functions must bind return_value explicitly on patch(), eliminating mock_repo_class.return_value assignments.</constraint>
  </step>

  <step id="4" name="SHARED REPOSITORY PREDICATE &amp; POSITIVE REGISTRY RESOLUTION">
    <action>In @[scripts/_ast_guardrails.py]: Extract a shared module-level predicate `_is_repository_identifier(name: str) -> bool` that returns True if ("_repo" in name.lower() or "repo_" in name.lower() or name.lower().endswith("repo") or name.lower() == "repo") and not ("report" in name.lower() or "response" in name.lower()).</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement positive repository-class resolution function `_resolve_positive_repository_classes() -> frozenset[str]` scanning backend_v2/database/interfaces.py, backend_v2/database/repository.py, and backend_v2/database/repositories/ for classes ending with "Repository" or inheriting from repository protocols.</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement positive interface-method resolution function `_resolve_interface_repository_methods() -> frozenset[str]` extracting all public method names defined across Protocols in backend_v2/database/interfaces.py.</action>
    <action>Cache POSITIVE_REPOSITORY_CLASSES and INTERFACE_REPOSITORY_METHODS once per scan in GuardrailVisitor or module scope.</action>
    <constraint invariant="ban_heuristic_identifier_matching">No string prefix checks or ad-hoc keyword lists. Target resolution must use the shared predicate and positive protocol sets.</constraint>
  </step>

  <step id="5" name="HARDENED QGR014 VISITOR IMPLEMENTATIONS (DETECTIONS A-G)">
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (a) in `visit_Return`: Prohibit return of AsyncMock, MagicMock, or Mock instances from functions whose name satisfies _is_repository_identifier(fn.name) in test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (b) in `visit_Assign`: Prohibit `.return_value` and `.side_effect` assignments where the target root identifier satisfies _is_repository_identifier in test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (c) in `visit_Assign`: Prohibit attribute replacement assignments `<repo>.<attr> = AsyncMock(...)` / `MagicMock(...)` / `Mock(...)` where target root identifier satisfies _is_repository_identifier in test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (d) in `visit_Call`: Prohibit `patch.object(<repo>, ...)` and `monkeypatch.setattr(<repo>, ...)` where target root identifier satisfies _is_repository_identifier in test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (e) in `visit_Call`: Prohibit keyword arguments whose name satisfies _is_repository_identifier bound to AsyncMock, MagicMock, or Mock instances in test files.</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (f) in `visit_Call`: Prohibit `patch("<module>.<Class>")` where `<Class>` belongs to POSITIVE_REPOSITORY_CLASSES unless `return_value` or `new` is bound to an instance of an InMemory*Repository defined in backend_v2/tests/fakes/in_memory_repositories.py (completely replacing the "service" in filepath heuristic and substring target predicate).</action>
    <action>In @[scripts/_ast_guardrails.py]: Implement detection (g) in new `visit_ClassDef`: Prohibit class definitions in test files outside backend_v2/tests/fakes/ that define at least one method whose name belongs to INTERFACE_REPOSITORY_METHODS.</action>
    <action>Enforce all QGR014 detections at unconditional GuardrailSeverity.FATAL.</action>
    <constraint invariant="universal_fail_fast">QGR014 must fail fast at FATAL severity on any violation across all 7 detection branches.</constraint>
  </step>

  <step id="6" name="COMPREHENSIVE NEGATIVE &amp; POSITIVE TEST FIXTURES FOR QGR014">
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]: Add 7 negative test fixtures asserting QGR014 FATAL violations:
      1. (a) Fixture returning AsyncMock: `def repo_fixture(): return AsyncMock()` raises QGR014.
      2. (b) Return value assignment: `repo.get_step.return_value = {}` raises QGR014.
      3. (c) Attribute replacement: `exec_repo.get_execution = AsyncMock(return_value=rec)` raises QGR014.
      4. (d) Monkeypatch object: `monkeypatch.setattr(system_repo, "get_model_registry", AsyncMock())` raises QGR014.
      5. (e) Keyword injected mock: `HookDependencies(exec_repo=MagicMock())` raises QGR014.
      6. (f) String-target patch without fake: `patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository")` raises QGR014.
      7. (g) Ad-hoc repository class: class `MockRepoWaterfall` defining `get_output_profile_by_id` in a test module raises QGR014.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]: Add 4 positive test fixtures asserting immunity (0 violations):
      1. Non-repository mock: `mock_report_service.get_report.return_value = ReportDataDTO(...)` produces 0 violations.
      2. Legitimate settings patch: `monkeypatch.setattr("backend_v2.services.execution.stream_service.get_settings", factory)` produces 0 violations.
      3. Valid fake-bound patch: `patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=InMemoryUnifiedWorkflowRepository())` produces 0 violations.
      4. Legitimate driver patch: `patch("backend_v2.database.repositories.execution.get_storage_driver")` produces 0 violations.</action>
    <action>Execute localized unit tests: `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py`.</action>
    <constraint invariant="anti_ambiguity_mandate">All 7 negative fixtures and 4 positive fixtures must have deterministic assertions asserting exact rule_code == "QGR014" and severity == GuardrailSeverity.FATAL.</constraint>
  </step>

  <step id="7" name="UNIVERSAL TWO-STAGE VERIFICATION GATE &amp; RESIDUAL LEDGER AUDIT">
    <action>Execute symbol probe across backend_v2: `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` asserting exactly 0 matches.</action>
    <action>Execute full test AST guardrail scan: `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict` asserting 0 violations.</action>
    <action>Execute dict eradication audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` asserting TOTAL VIOLATIONS: 0.</action>
    <action>Execute global backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` asserting 100% pass rate across all stages.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Completion requires passing global backend audit loop, zero residual AST violations, and zero matches on eradicated symbols.</constraint>
  </step>

  <dod_checklist>
    <item>Select-String for DynamicRepoMethod, InMemoryBlueprintTransformerRepository, dict_to_obj returns 0 matches across backend_v2.</item>
    <item>BaseInMemoryRepository.inject_fault reflection is replaced with inspect.getattr_static positive method existence validation and # noqa: QGR001 suppression is eradicated.</item>
    <item>All 17 synthesis worker test functions in test_worker_synthesis.py and test_worker_synthesis_accumulation.py migrate from decorator patches and mock_repo_class.return_value to with patch(..., return_value=mock_repo).</item>
    <item>Hardened QGR014 with detections (a)-(g) enforced at unconditional FATAL severity.</item>
    <item>All 7 negative fixtures and 4 positive immunity fixtures pass in backend_v2/tests/unit/scripts/test_ast_guardrails.py.</item>
    <item>uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict reports 0 violations.</item>
    <item>uv run python scripts/audit_dict_eradication.py backend_v2 --strict reports TOTAL VIOLATIONS: 0.</item>
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
    <anti_target>Do NOT delete non-persistence service mocks (specifically router service mocks and LLM client doubles) governed by partial_mocking_srp_ban during Phase 7.</anti_target>
    <anti_target>Do NOT alter driver-level patches (specifically get_driver and get_storage_driver) recorded in the Out-of-Scope Register.</anti_target>
    <anti_target>Do NOT touch Stage 10 audit_dict_eradication.py integration or Flutter client models during Phase 7 (scheduled for Phase 8).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Symbol Scan: `Select-String -Path backend_v2 -Pattern "DynamicRepoMethod|InMemoryBlueprintTransformerRepository|dict_to_obj" -Recurse` returns 0 matches.</action>
    <action>Execute AST Guardrails on tests: `uv run python scripts/_ast_guardrails.py backend_v2/tests/ --strict`.</action>
    <action>Execute Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
