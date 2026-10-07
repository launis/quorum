# Phase 10: # type: ignore Eradication & Strict mypy Ignore Accounting

**Overview:** Eradicate Census T (409 historical `# type: ignore` comments in 155 files, currently 396 residual active comments across `backend_v2` and `scripts/` in 154 files); delete `[[tool.mypy.overrides]]` for `firestore_driver` and `factory` in `pyproject.toml` so `warn_unused_ignores = true` applies globally; remove the 5 dead entries in `per-file-ignores`; replace the 20 `[prop-decorator]` suppressions in `backend_v2/settings.py` (18) and `backend_v2/models/domain/overseer.py` (2) with ONE `disable_error_code = ["prop-decorator"]` entry in `[tool.mypy]` of `pyproject.toml`; extend the comment audit of `scripts/audit_dict_eradication.py` to reject `# type: ignore` at FATAL severity; and add the Config Suppression Ratchet in `scripts/audit_dict_eradication.py` to verify frozen approved sets in `pyproject.toml` and `analysis_options.yaml` via `tomllib`. Batch 10.1 covers 25 production files and 3 `scripts/` files (71 comments); Batch 10.2 covers 126 test files (325 comments). Negative tests construct invalid input through `Model.model_validate({...})` instead of suppressing `call-arg` / `arg-type`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md] Phase 10: # type: ignore Eradication & Strict mypy Ignore Accounting (Epic baseline lines: #L588-L601, #L226-L227, #L244, #L258, #L98-L101, #L131-L136).

**Target Files (35 Core Architectural Files + 126 Test Files):**
- `[MODIFY]` @[pyproject.toml#L98-L101]
- `[MODIFY]` @[pyproject.toml#L116]
- `[MODIFY]` @[pyproject.toml#L131-L136]
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/audit_warning_baseline.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/settings.py]
- `[MODIFY]` @[backend_v2/models/domain/overseer.py]
- `[MODIFY]` @[backend_v2/models/dtos/context_variables.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/utils/redis_patcher.py]
- `[MODIFY]` @[backend_v2/core/registry.py]
- `[MODIFY]` @[backend_v2/database/firestore_driver.py]
- `[MODIFY]` @[backend_v2/utils/alias_engine.py]
- `[MODIFY]` @[backend_v2/database/wrapper.py]
- `[MODIFY]` @[backend_v2/llm/handler.py]
- `[MODIFY]` @[backend_v2/logging_config.py]
- `[MODIFY]` @[backend_v2/models/state.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/logic.py]
- `[MODIFY]` @[backend_v2/utils/static_charts.py]
- `[MODIFY]` @[backend_v2/database/factory.py]
- `[MODIFY]` @[backend_v2/llm/client.py]
- `[MODIFY]` @[backend_v2/llm/provider.py]
- `[MODIFY]` @[backend_v2/models/dtos/prompt.py]
- `[MODIFY]` @[backend_v2/models/dtos/render.py]
- `[MODIFY]` @[backend_v2/services/matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/state_reducer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]
- `[MODIFY]` @[backend_v2/services/pdf_generator.py]
- `[MODIFY]` @[scripts/audit_dto_parity.py]
- `[MODIFY]` @[scripts/audit_matrix_auto_filler.py]
- `[MODIFY]` @[scripts/audit_matrix_manager.py]
- `[MODIFY]` Residual 126 Test Files enumerated in @[docs/epic/EPIC_157_residual_ledger.md]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Unused Ignore Overrides in `pyproject.toml`**:
   - In @[pyproject.toml], `[[tool.mypy.overrides]]` currently disables `warn_unused_ignores = false` for modules `backend_v2.database.firestore_driver` and `backend_v2.database.factory`. This creates a configuration hole where unused ignores accumulate silently. Deleting this override block and configuring `warn_unused_ignores = true` globally enforces strict typing across all database modules.
2. **Dead Entries in `per-file-ignores`**:
   - In @[pyproject.toml] under `[tool.ruff.lint.per-file-ignores]`, 5 file paths point to deleted or refactored files: `backend_v2/tasks/legacy_migration_tasks.py` (#L98), `backend_v2/tasks/analysis.py` (#L99), `backend_v2/tasks/critique.py` (#L100), `backend_v2/database/firestore_repo.py` (#L101), and `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py` (#L116). Removing these 5 dead entries eliminates configuration drift.
3. **Repetitive Pydantic Computed Field Suppressions**:
   - In @[backend_v2/settings.py] (18 occurrences) and @[backend_v2/models/domain/overseer.py] (2 occurrences), `@computed_field` lines carry inline `# type: ignore[prop-decorator]` suppressions because MyPy cannot type decorators stacked on `@property`. Configuring `disable_error_code = ["prop-decorator"]` centrally in `[tool.mypy]` allows deleting all 20 inline suppressions cleanly without relaxing value type checks.
4. **Missing `# type: ignore` Detection in Dict Eradication Audit**:
   - In @[scripts/audit_dict_eradication.py], `audit_file_comments` currently flags only `# noqa` tokens. Extending `audit_file_comments` to detect `# type: ignore` tokens (case-insensitive and whitespace-tolerant `r"#\s*type:\s*ignore"`) at FATAL severity under `unauthorized_suppressions` ensures that comment-based type escapes are completely blocked across all non-exempt files.
5. **Absence of Config Suppression Ratchet in Universal Audit**:
   - Neither Ruff ignores nor MyPy overrides nor Dart analyzer errors are currently ratcheted by static verification scripts. Implementing `check_config_suppression_ratchet` in @[scripts/audit_dict_eradication.py] using `tomllib` ensures that `pyproject.toml` and `client_app_v2/analysis_options.yaml` cannot introduce unapproved ignores or silent overrides.
6. **Negative Test Fixture Constructor Suppressions in Test Suites**:
   - In multiple unit tests across `backend_v2/tests/unit/models/`, tests verifying schema validation errors pass invalid arguments directly to model constructors while silencing MyPy with `# type: ignore[call-arg]` or `[arg-type]`. Replacing raw constructor calls with `Model.model_validate({...})` preserves strict type checking while properly asserting validation failure paths.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[pyproject.toml#L98-L101]`, `@[pyproject.toml#L116]`, and `@[pyproject.toml#L131-L136]` | Banned `warn_unused_ignores = false` overrides in `[[tool.mypy.overrides]]`, 5 dead `per-file-ignores` entries, and missing `disable_error_code = ["prop-decorator"]`. | Configure `warn_unused_ignores = true` globally in `[tool.mypy]`; delete `[[tool.mypy.overrides]]`; remove the 5 dead `per-file-ignores`; configure `disable_error_code = ["prop-decorator"]`. | Single centralized configuration; zero per-module override blocks. | `uv run mypy backend_v2` executes with global `warn_unused_ignores = true` reporting 0 errors. |
| `@[backend_v2/settings.py]` and `@[backend_v2/models/domain/overseer.py]` | Banned 20 inline `# type: ignore[prop-decorator]` comment suppressions on `@computed_field`. | Delete all 18 `# type: ignore[prop-decorator]` comments in `settings.py` and both 2 comments in `overseer.py`. | Rely strictly on central `disable_error_code = ["prop-decorator"]` in `pyproject.toml`. | Zero `# type: ignore` occurrences in `settings.py` and `overseer.py`. |
| `@[scripts/audit_dict_eradication.py]` | Banned unmonitored `# type: ignore` comments in source code and unverified config ignore creep. | Extend `audit_file_comments` to flag `# type: ignore` as FATAL `unauthorized_suppressions`; implement `check_config_suppression_ratchet` using `tomllib` validating `pyproject.toml` and `analysis_options.yaml` against frozen approved sets. | Native standard library `tomllib` parsing; zero external dependencies. | `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` flags synthetic `# type: ignore` comments and unapproved config entries. |
| `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]` | Banned missing unit test coverage for `# type: ignore` detection and Config Suppression Ratchet. | Add unit tests for `# type: ignore` detection and 4 ratchet partitions (unapproved Ruff ignore, unapproved per-file ignore, unapproved MyPy override/disabled code, unapproved Dart analyzer error). | Hermetic in-memory synthetic string and dictionary tests. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` passes 100%. |
| Batch 10.1 Production Files: `@[backend_v2/models/dtos/context_variables.py]`, `@[backend_v2/services/orchestrator/strategies/llm.py]`, `@[backend_v2/utils/redis_patcher.py]`, `@[backend_v2/core/registry.py]`, `@[backend_v2/database/firestore_driver.py]`, `@[backend_v2/utils/alias_engine.py]`, `@[backend_v2/database/wrapper.py]`, `@[backend_v2/llm/handler.py]`, `@[backend_v2/logging_config.py]`, `@[backend_v2/models/state.py]`, `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`, `@[backend_v2/services/orchestrator/strategies/logic.py]`, `@[backend_v2/utils/static_charts.py]`, `@[backend_v2/database/factory.py]`, `@[backend_v2/llm/client.py]`, `@[backend_v2/llm/provider.py]`, `@[backend_v2/models/dtos/prompt.py]`, `@[backend_v2/models/dtos/render.py]`, `@[backend_v2/services/matrix_domain_parser.py]`, `@[backend_v2/services/orchestrator/dag_executor.py]`, `@[backend_v2/services/orchestrator/state_reducer.py]`, `@[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]`, `@[backend_v2/services/pdf_generator.py]` | Banned 51 `# type: ignore` comments masking union narrowing, third-party library stubs, dynamic registry calls, negative type exclusions, and document conversions. | Apply typed narrowing, explicit type annotations, safe attribute access, platform-specific imports, and positive `isinstance(x, Mapping)` guards; delete all 51 comments. | Native Python 3.14 types and PEP 695 aliases; zero ad-hoc type laundering. | Census T returns 0 matches across all 25 production files; `uv run mypy backend_v2` clean. |
| Batch 10.1 Scripts Files: `@[scripts/audit_dto_parity.py]`, `@[scripts/audit_matrix_auto_filler.py]`, `@[scripts/audit_matrix_manager.py]` | Banned 4 `# type: ignore` comments in maintenance and audit scripts. | Apply clean typing and type annotations; delete all 4 comments. | Standard typed script patterns. | Census T returns 0 matches across `scripts/`. |
| Batch 10.2 Test Files: `@[backend_v2/tests/unit/test_xai_extensions.py]`, `@[backend_v2/tests/unit/models/dtos/test_synthesis.py]`, `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]`, `@[backend_v2/tests/unit/hooks/test_dlq_guard.py]`, `@[backend_v2/tests/unit/models/dtos/test_atom_result.py]`, `@[backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py]`, and 119 residual test files enumerated in `@[docs/epic/EPIC_157_residual_ledger.md]` | Banned 325 `# type: ignore` comments in test suites masking negative fixture construction, mock parameter types, and dictionary conversions. | In negative tests, construct invalid payloads via `Model.model_validate({...})` instead of suppressing `call-arg` / `arg-type`; provide typed signatures on test helpers and doubles; delete all 325 comments. | Native Pydantic V2 validation error testing. | Census T returns 0 matches across `backend_v2/tests/`; full test suite passes. |
| `@[scripts/audit_warning_baseline.py]` | Banned unratcheted Census T residual ceiling (`t=396`). | Ratchet `CURRENT_RESIDUAL_CEILINGS.t = 0` monotonically. | Deterministic integer ceiling assertion. | `uv run python scripts/audit_warning_baseline.py --verify-zero` passes with exit code 0. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; CENSUS T BASELINE PRE-CONDITION AUDIT">
    <action>Look backward: Verify Phase 9 successfully eradicated CommentSuppressor, all # noqa tokens, and all cast(Any, ...) calls with Census N=0 and Census X=0.</action>
    <action>Verify current baseline: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and confirm current ceilings (t=396, p=351, m=10, r=186).</action>
    <action>Verify live Census T: Run Census T regex search across `backend_v2` and `scripts` to verify the exact count of 396 `# type: ignore` occurrences across 25 production files (67 comments), 3 scripts files (4 comments), and 126 test files (325 comments).</action>
    <action>Look forward: Verify eradicating `# type: ignore` comments, enforcing global `warn_unused_ignores = true`, and adding the Config Suppression Ratchet permanently closes type-checker escape hatches before Phase 11 extended dict eradication.</action>
    <constraint invariant="universal_fail_fast">If unexpected type ignores exist outside the residual ledger boundaries, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/10_phase10_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="MYPY &amp; RUFF CONFIGURATION MODERNIZATION (pyproject.toml)">
    <action>In @[pyproject.toml]: Under `[tool.mypy]`, add `warn_unused_ignores = true` globally.</action>
    <action>In @[pyproject.toml]: Under `[tool.mypy]`, add `disable_error_code = ["prop-decorator"]` to configure centralized property decorator tolerance without relaxing value typing.</action>
    <action>In @[pyproject.toml#L131-L136]: Delete the entire `[[tool.mypy.overrides]]` block targeting `backend_v2.database.firestore_driver` and `backend_v2.database.factory`.</action>
    <action>In @[pyproject.toml#L98-L101] and @[pyproject.toml#L116]: Under `[tool.ruff.lint.per-file-ignores]`, remove the 5 dead entries: `"backend_v2/tasks/legacy_migration_tasks.py" = ["E501"]`, `"backend_v2/tasks/analysis.py" = ["E501"]`, `"backend_v2/tasks/critique.py" = ["E501"]`, `"backend_v2/database/firestore_repo.py" = ["E501"]`, and `"backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py" = ["E501"]`.</action>
    <action>Execute localized verification: Run `uv run ruff check pyproject.toml` to verify configuration syntax integrity.</action>
    <constraint invariant="the_zero_compromise_pledge">Global warn_unused_ignores = true must be enforced without per-module exception blocks.</constraint>
  </step>

  <step id="2" name="PROP-DECORATOR SUPPRESSION ERADICATION (settings.py &amp; overseer.py)">
    <action>In @[backend_v2/settings.py]: Delete all 18 inline `# type: ignore[prop-decorator]` comment suppressions on `@computed_field` lines (specifically lines 495, 548, 558, 568, 578, 588, 598, 608, 618, 628, 638, 648, 679, 815, 849, 861, 878, 888).</action>
    <action>In @[backend_v2/models/domain/overseer.py]: Delete both 2 inline `# type: ignore[prop-decorator]` comment suppressions on `@computed_field` lines (specifically lines 104 and 164).</action>
    <action>Execute localized verification: Run `uv run mypy backend_v2/settings.py backend_v2/models/domain/overseer.py` and verify 0 errors with 0 unused ignore warnings.</action>
    <constraint invariant="the_zero_compromise_pledge">All 20 prop-decorator suppressions must be deleted, relying strictly on central configuration.</constraint>
  </step>

  <step id="3" name="AUDIT HARDENING (COMMENT AUDIT &amp; CONFIG SUPPRESSION RATCHET IN audit_dict_eradication.py &amp; UNIT TESTS)">
    <action>In @[scripts/audit_dict_eradication.py]: In `audit_file_comments`, add detection for `# type: ignore` comment tokens using regex `re.search(r"#\s*type:\s*ignore", tok.string, re.IGNORECASE)`. If matched, append an `AuditViolation` with `metric="unauthorized_suppressions"` and message `Unauthorized '# type: ignore' comment suppression detected: {tok.string.strip()}`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: Define frozen constants: `FROZEN_APPROVED_RUFF_IGNORES: frozenset[str] = frozenset({"B008", "E402", "D100", "D101", "D102", "D103", "D107", "D205", "D417", "UP017"})`, `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS: frozenset[str]` containing the 20 approved paths, and `FROZEN_APPROVED_DART_ANALYZER_ERRORS: frozenset[str] = frozenset({"invalid_annotation_target"})`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: Implement `check_config_suppression_ratchet(repo_root: Path | None = None) -> list[AuditViolation]`. Use standard library `tomllib` to parse `pyproject.toml`. Assert that `tool.ruff.lint.ignore` contains no unapproved entries; assert `tool.ruff.lint.per-file-ignores` contains no unapproved paths; assert `tool.mypy.warn_unused_ignores` is True; assert `tool.mypy.disable_error_code` matches `["prop-decorator"]`; and assert `tool.mypy.overrides` is empty or absent. Read `client_app_v2/analysis_options.yaml` and assert that `analyzer.errors` contains only `invalid_annotation_target: ignore`. For any violation, emit an `AuditViolation` under `unauthorized_suppressions`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `audit_dict_eradication`, invoke `check_config_suppression_ratchet` and aggregate discovered config suppression violations into `report.unauthorized_suppressions`.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test verifying that `# type: ignore` with any error code (specifically: `[arg-type]`, `[attr-defined]`, or bare) triggers `unauthorized_suppressions` violation.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test verifying that string literals containing `"# type: ignore"` do not trigger violations.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit tests for Config Suppression Ratchet: verify unapproved Ruff ignore flags violation; verify unapproved per-file ignore path flags violation; verify missing `warn_unused_ignores = true` or unauthorized `disable_error_code` flags violation; verify unapproved Dart analyzer error flags violation; and verify production config files pass with 0 violations.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Dict eradication audit must fail-fast on every # type: ignore comment and every unapproved config ignore.</constraint>
  </step>

  <step id="4" name="BATCH 10.1: RESIDUAL PRODUCTION &amp; SCRIPTS # type: ignore ERADICATION (23 RESIDUAL PRODUCTION FILES &amp; 3 SCRIPTS FILES)">
    <action>In @[backend_v2/models/dtos/context_variables.py]: Eradicate all 6 `# type: ignore` comments (#L71, #L79, #L93, #L107, #L121, #L137) by refining union types and type narrowing for blackboard, reducer output, report context, step detector, and evaluated matrices.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py]: Eradicate all 4 `# type: ignore` comments (#L246, #L269, #L290, #L483) by replacing negative type checks with positive `isinstance(x, Mapping)` guards and typing retry counts and adapter payloads.</action>
    <action>In @[backend_v2/utils/redis_patcher.py]: Eradicate all 4 `# type: ignore` comments (#L22, #L60, #L68, #L77) by typing Arq worker logging methods, redis client parameters, and mock dispatch.</action>
    <action>In @[backend_v2/core/registry.py]: Eradicate all 3 `# type: ignore` comments (#L347, #L546, #L565) by typing dynamic class registration and using `types.GenericAlias(list, (FinalDocIdsType,))` for dynamic Pydantic model fields.</action>
    <action>In @[backend_v2/database/firestore_driver.py]: Eradicate all 3 `# type: ignore` comments (#L54, #L182, #L335) by using `from google.cloud import firestore`, typing document `to_dict()` conversion as `Mapping[str, Any]`, and annotating aggregate count queries.</action>
    <action>In @[backend_v2/utils/alias_engine.py]: Eradicate all 3 `# type: ignore` comments (#L42, #L69, #L78) by using `Literal.__getitem__(tuple(choices))` for dynamic string literal generation and typing alias collections.</action>
    <action>In @[backend_v2/database/wrapper.py]: Eradicate both 2 `# type: ignore` comments (#L54, #L76) by enclosing file lock handling in platform-aware checks (`if sys.platform == "win32": import msvcrt ... else: import fcntl`).</action>
    <action>In @[backend_v2/llm/handler.py]: Eradicate both 2 `# type: ignore` comments (#L219, #L365) by defining `class RefreshableCredentials(Protocol): def refresh(self, request: Any) -> None: ...` to type credentials refresh without `[no-untyped-call]`.</action>
    <action>In @[backend_v2/logging_config.py]: Eradicate both 2 `# type: ignore` comments (#L45, #L253) by annotating `logfire: types.ModuleType | None = None` and using `litellm._logging.set_verbose = False`.</action>
    <action>In @[backend_v2/models/state.py]: Eradicate both 2 `# type: ignore` comments (#L73, #L86) on state envelope resolution.</action>
    <action>In @[backend_v2/services/orchestrator/matrix_explanation_service.py]: Eradicate both 2 `# type: ignore` comments (#L167, #L187) by replacing negative exclusion checks with positive `isinstance(x, Mapping)` guards on matrix breakdown state.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/logic.py]: Eradicate both 2 `# type: ignore` comments (#L84, #L102) on logic strategy execution and payload dictionary resolution.</action>
    <action>In @[backend_v2/utils/static_charts.py]: Eradicate both 2 `# type: ignore` comments (#L414, #L415) by importing `PolarAxes` from `matplotlib.projections.polar` and narrowing via `if isinstance(ax, PolarAxes):` to access `set_theta_offset` and `set_theta_direction`.</action>
    <action>In @[backend_v2/database/factory.py]: Eradicate 1 `# type: ignore` comment (#L14) on firestore driver instantiation.</action>
    <action>In @[backend_v2/llm/client.py]: Eradicate 1 `# type: ignore` comment (#L657) by eliminating redundant `cast(T, parsed_json)` in favor of `validated_model = parsed_json`.</action>
    <action>In @[backend_v2/llm/provider.py]: Eradicate 1 `# type: ignore` comment (#L568) by importing `Router` directly from `litellm.router`.</action>
    <action>In @[backend_v2/models/dtos/prompt.py]: Eradicate 1 `# type: ignore` comment (#L56) on prompt mapping operations.</action>
    <action>In @[backend_v2/models/dtos/render.py]: Eradicate 1 `# type: ignore` comment (#L48) by deleting redundant `__iter__` override from `RenderExecutionResultDTO` in favor of standard attribute access.</action>
    <action>In @[backend_v2/services/matrix_domain_parser.py]: Eradicate 1 `# type: ignore` comment (#L112) on domain model parsing.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor.py]: Eradicate 1 `# type: ignore` comment (#L298) on node execution completion handler.</action>
    <action>In @[backend_v2/services/orchestrator/state_reducer.py]: Eradicate 1 `# type: ignore` comment (#L214) by replacing negative exclusion checks with positive `isinstance(x, Mapping)` guards on state reduction accumulator.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]: Eradicate 1 `# type: ignore` comment (#L142) by replacing negative exclusion checks with positive `isinstance(x, Mapping)` guards on document packing payload.</action>
    <action>In @[backend_v2/services/pdf_generator.py]: Eradicate 1 `# type: ignore` comment (#L16) by removing redundant `# type: ignore[import-untyped, unused-ignore]` on `import markdown`.</action>
    <action>In @[scripts/audit_dto_parity.py]: Eradicate both 2 `# type: ignore` comments (#L242, #L280) on model field inspection.</action>
    <action>In @[scripts/audit_matrix_auto_filler.py]: Eradicate 1 `# type: ignore` comment (#L168) on matrix auto-fill generator.</action>
    <action>In @[scripts/audit_matrix_manager.py]: Eradicate 1 `# type: ignore` comment (#L395) on rule AST inspection.</action>
    <action>Execute Batch 10.1 verification: Run `uv run mypy backend_v2 scripts` and verify 0 errors with global `warn_unused_ignores = true`. Verify Census T on all 25 production files and 3 scripts files returns 0 matches.</action>
    <constraint invariant="the_zero_compromise_pledge">Absolute zero # type: ignore comments across all production and scripts files.</constraint>
  </step>

  <step id="5" name="BATCH 10.2: TEST SUITES # type: ignore ERADICATION (126 TEST FILES)">
    <action>In @[backend_v2/tests/unit/test_xai_extensions.py] (15 comments), @[backend_v2/tests/unit/models/dtos/test_synthesis.py] (12 comments), @[backend_v2/tests/unit/services/test_execution.py] (10 comments), @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py] (9 comments), @[backend_v2/tests/unit/hooks/test_dlq_guard.py] (8 comments), @[backend_v2/tests/unit/models/dtos/test_atom_result.py] (8 comments), and @[backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py] (8 comments): Eradicate all 70 `# type: ignore` comments by constructing negative test payloads via `Model.model_validate({...})` and supplying typed fixtures.</action>
    <action>In @[backend_v2/tests/unit/models/domain/test_inputs.py] (7 comments), @[backend_v2/tests/unit/models/dtos/test_hook_delta.py] (7 comments), @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py] (7 comments), @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py] (7 comments), @[backend_v2/tests/unit/models/dtos/test_finops.py] (6 comments), @[backend_v2/tests/unit/models/dtos/test_mcp.py] (6 comments), @[backend_v2/tests/unit/models/dtos/test_sensor.py] (6 comments), @[backend_v2/tests/unit/models/dtos/test_studio.py] (6 comments), and @[backend_v2/tests/unit/test_usage.py] (6 comments): Eradicate all 58 `# type: ignore` comments by validating inputs through Pydantic V2 model validation and typing mock attributes.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_context_variables.py] (5 comments), @[backend_v2/tests/unit/models/dtos/test_flattened_atom.py] (5 comments), @[backend_v2/tests/unit/models/dtos/test_node_execution.py] (5 comments), @[backend_v2/tests/unit/models/test_v2_core.py] (5 comments), @[backend_v2/tests/conftest.py] (4 comments), @[backend_v2/tests/unit/hooks/test_scoring.py] (4 comments), @[backend_v2/tests/unit/models/domain/test_execution.py] (4 comments), @[backend_v2/tests/unit/models/dtos/test_base.py] (4 comments), @[backend_v2/tests/unit/models/dtos/test_dag_models.py] (4 comments), @[backend_v2/tests/unit/models/dtos/test_hook_state.py] (4 comments), @[backend_v2/tests/unit/models/dtos/test_schema_manifest.py] (4 comments), @[backend_v2/tests/unit/models/test_contrastive_pair_dto.py] (4 comments), @[backend_v2/tests/unit/models/test_prompt.py] (4 comments), @[backend_v2/tests/unit/services/ingress/test_smart_ingress_resolver.py] (4 comments), @[backend_v2/tests/unit/services/orchestrator/test_sliding_window_linker.py] (4 comments), @[backend_v2/tests/unit/services/sdui/adapters/test_base_adapter.py] (4 comments), and @[backend_v2/tests/unit/utils/scoring/test_variance_engine.py] (4 comments): Eradicate all 69 `# type: ignore` comments by refining test parameter types and typed fake methods.</action>
    <action>In remaining 93 test files enumerated in @[docs/epic/EPIC_157_residual_ledger.md]: Eradicate all remaining 128 `# type: ignore` comments (1 to 3 comments per file) across hooks, orchestrator, DTO, router, and database test suites.</action>
    <action>Execute live Census T test audit: Verify that regex search for `#\s*type:\s*ignore` returns exactly 0 occurrences across `backend_v2/tests/`.</action>
    <action>Execute full test suite: Run `uv run pytest backend_v2/tests/` and verify all tests pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Absolute zero # type: ignore comments across all test files.</constraint>
  </step>

  <step id="6" name="MONOTONIC RATCHET UPDATE &amp; UNIVERSAL TWO-STAGE VERIFICATION GATE">
    <action>In @[scripts/audit_warning_baseline.py]: In `CURRENT_RESIDUAL_CEILINGS`, update `t=0` (ratcheted down from 396 to 0), locking Census T ceiling at absolute zero.</action>
    <action>Execute warning baseline audit: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and verify exit code 0 with zero fatal violations and zero warnings.</action>
    <action>Execute dict eradication audit: Run `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` and verify `TOTAL VIOLATIONS: 0`.</action>
    <action>Execute strict MyPy audit: Run `uv run mypy backend_v2` and verify 0 errors with global `warn_unused_ignores = true`.</action>
    <action>Execute universal backend audit loop: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` and verify all 10 stages pass cleanly.</action>
    <action>Execute planner output audit: Run `uv run python scripts/audit_planner_output.py --epic docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md --plan-dir docs/epic/tasks_EPIC_157/`.</action>
    <constraint invariant="universal_fail_fast">Phase 10 completes only when all 10 stages of the universal backend audit pass cleanly with Census T=0 and zero unapproved config ignores.</constraint>
  </step>

  <demolish>
    `[[tool.mypy.overrides]]`
    `prop-decorator suppressions`
    `dead per-file-ignores`
  </demolish>

  <dod_checklist>
    <item>Census command T returns exactly 0 matches across backend_v2 and scripts.</item>
    <item>[[tool.mypy.overrides]] block for firestore_driver and factory deleted from pyproject.toml.</item>
    <item>Global warn_unused_ignores = true configured in pyproject.toml under [tool.mypy].</item>
    <item>disable_error_code = ["prop-decorator"] configured centrally in pyproject.toml under [tool.mypy].</item>
    <item>All 20 prop-decorator inline suppressions deleted from backend_v2/settings.py and overseer.py.</item>
    <item>All 5 dead entries removed from tool.ruff.lint.per-file-ignores in pyproject.toml.</item>
    <item>scripts/audit_dict_eradication.py rejects all # type: ignore comment tokens at FATAL severity.</item>
    <item>Config Suppression Ratchet in scripts/audit_dict_eradication.py verifies frozen approved sets via tomllib.</item>
    <item>Unit tests in backend_v2/tests/unit/scripts/test_audit_dict_eradication.py cover type ignore detection and all ratchet partitions.</item>
    <item>All 51 type ignore comments in Batch 10.1 production and scripts files eradicated.</item>
    <item>All 338 type ignore comments in Batch 10.2 test files eradicated.</item>
    <item>scripts/audit_warning_baseline.py ratchets t=0 with --verify-zero passing.</item>
    <item>uv run mypy backend_v2 passes with 0 errors under global warn_unused_ignores = true.</item>
    <item>Universal audit loop uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict passes 10/10 stages cleanly.</item>
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
    <anti_target>Do NOT retype test files or scripts for dict eradication in Phase 10 (quarantined strictly for Phase 11).</anti_target>
    <anti_target>Do NOT modify Dart files during Phase 10 (quarantined strictly for Phase 12).</anti_target>
    <anti_target>Do NOT alter repository persistence interfaces or database drivers during Phase 10 (completed in Phases 4-7).</anti_target>
    <anti_target>Do NOT loosen any MyPy error codes other than prop-decorator in pyproject.toml.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Live Census T Audit: `uv run python -c "import re, pathlib; root = pathlib.Path('.'); total = sum(len(re.findall(r'#\s*type:\s*ignore', p.read_text(encoding='utf-8', errors='ignore'))) for d in ['backend_v2', 'scripts'] for p in (root / d).rglob('*.py')); assert total == 0, f'Census T residual: {total}'"`</action>
    <action>Execute Strict Mypy: `uv run mypy backend_v2` reports 0 errors with global warn_unused_ignores = true.</action>
    <action>Execute Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 scripts --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Baseline Verification: `uv run python scripts/audit_warning_baseline.py --verify-zero` reports 0 fatal violations and 0 warnings.</action>
    <action>Execute 10-Stage Universal Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
