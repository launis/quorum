# Implementation Plan: AST & Quality Gate Extensions (QGR020, QGR031–QGR033), Dynamic Script Scanning & Content-Addressed SHA-256 Hardening Cache

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

## 1. Objective & Architectural Context

Following the completion of the Backend Targeted Hardening Waves 1–4 (`133/133` files across `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`, and `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`) and the 32-hex `PrefixedUUID7` & `UUIDv4` eradication cutovers (`15/15` in `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]` and `31/31` in `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]`), this plan implements five permanent quality gate and autonomous hardening improvements for Step 3.4 of `@[docs/KATTAVA TUOTANTOARKITEHTUURIN IMPLEMENTO.md]`:

1. **`QGR031` — Query Filter & `FilterOperator` Static AST Guardrail (`@[scripts/_ast_guardrails.py#L573-L586]`):**
   Inspects all `Filter(...)` and `QueryCondition(...)` call sites across `backend_v2/`, `scripts/`, and tests to ban invalid operator string literals (`"eq"`, `"ne"`, `"gt"`, `"lt"`, `"="`, `"LIKE"`, `"ILIKE"`), empty `field=""` arguments, and string literals passed as the `value` of `FilterOperator` (`IN` / `"in"`) queries.
2. **Dynamic `scripts/*.py` Macro-Gate Discovery (`@[scripts/backend_audit_loop.py#L68-L78]` & `@[scripts/backend_audit_loop.py#L422-L682]`):**
   Replaces hardcoded script whitelisting with a deterministic `discover_authoritative_scripts()` function scanning `sorted(Path("scripts").glob("*.py"))` so newly created scripts can never bypass Ruff, MyPy `--strict`, `QGR000`–`QGR033`, or `audit_dict_eradication.py`.
3. **`QGR032` — Polyfactory `ModelFactory` 32-Hex `UUIDv7` Invariant Guard & Dynamic Reflection Meta-Test (`@[scripts/_ast_guardrails.py#L589-L609]` & `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]`):**
   Enforces at the AST level in `backend_v2/tests/factories/model_factories.py` that every `ModelFactory[T]` class routes entity ID fields through `Use(generate_opaque_id, EntityPrefix.<TYPE>)`, and upgrades `test_model_factories.py` to dynamically discover all `ModelFactory` subclasses via `__subclasses__()`.
4. **`QGR020` PEP 593 `Annotated[..., Field(...)]` Extension & `QGR033` Static Docstring / RFC 7807 Dual-Reporting Guardrail (`@[scripts/_ast_guardrails.py#L573-L586]` & `@[scripts/_ast_guardrails.py#L589-L609]`):**
   Shifts high-frequency LLM hardening checks directly into `scripts/_ast_guardrails.py` so violations are caught deterministically in milliseconds during `/tier2-execute`:
   - **Check 20B (`pydantic_annotated_fields_mandate` in `QGR020`)**: Bans bare `field: T = Field(...)` assignments on `BaseModel` / `BaseSettings` subclasses where the type annotation is not wrapped in `Annotated[T, ...]` (with self-verifying `RESIDUAL_BARE_FIELD_FILES` protecting the 25 pre-existing files until touched).
   - **Check 33A (`docstring_fail_fast_ban` in `QGR033`)**: Bans `Raises: None` across all module, class, and function docstrings (`0` existing violations repo-wide).
   - **Check 33B (`pep257_google_style_docstrings` in `QGR033`)**: Requires PEP 257 docstrings on all production `backend_v2/` modules and top-level public classes (with self-verifying `RESIDUAL_MISSING_DOCSTRING_FILES` for the 4 pre-existing module-docstring files).
   - **Check 33C (`rfc7807_dual_reporting_mandate` in `QGR033`)**: Requires every production domain function or method raising `AppException(...)` to invoke a structured error log (`logger.error`, `logger.critical`, `logger.exception`, or `_log_`) within the enclosing function scope (with `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` for `backend_v2/logging_config.py`, `backend_v2/exceptions.py`, and `backend_v2/services/auth/repositories.py`).
5. **Deterministic Content-Addressed SHA-256 Hardening Cache & Completed Tracker Seeding (`@[scripts/auto_hardening_runner.py#L133-L179]`, `@[scripts/auto_hardening_runner.py#L182-L196]`, `@[scripts/auto_hardening_runner.py#L340-L394]`, `@[scripts/auto_hardening_runner.py#L970-L1027]`, `@[scripts/auto_hardening_runner.py#L1030-L1173]`, `@[scripts/auto_hardening_runner.py#L1176-L1336]`):**
   Implements a persistent, strongly typed SHA-256 cache (`data/hardening_cache.json` governed by newly defined `HardeningCacheEntryDTO` and `HardeningCacheManifestDTO` models) in `scripts/auto_hardening_runner.py` that computes the composite SHA-256 digest of `(target_file + resolved unit test file(s) + .agents/rules/*.md)`. Automatically seeds completed `- [x]` targets from `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md]`, `@[docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md]`, `@[docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md]`, and `@[docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md]`. When a target's composite SHA-256 is unchanged since its last successful hardening commit, `auto_hardening_runner.py` marks the target `- [x]` in **0 seconds** (`⚡ CACHE HIT`) without launching an LLM subagent.

---

## 2. Scope & 5-Column Directives Table

| Target Scope | Action | Architectural Layer | Key Symbols / Boundaries Modified | Verification Gate |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY]` `@[scripts/_ast_guardrails.py#L573-L586]`<br>`[MODIFY]` `@[scripts/_ast_guardrails.py#L589-L609]` | `MODIFY` | Automated AST Guardrails Engine | `RESIDUAL_BARE_FIELD_FILES`, `RESIDUAL_MISSING_DOCSTRING_FILES`, `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`, `_is_annotated_subscript`, `_function_has_error_log`, `visit_Module` (`QGR033`), `_check_qgr031_filter_call` / `visit_Call` (`QGR031`), `visit_ClassDef` (`QGR032`, `QGR033`), `visit_FunctionDef` / `visit_AsyncFunctionDef` (`QGR033`), `visit_AnnAssign` (`QGR020` bare `Field()` ban), `main` | `uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict` |
| `[MODIFY]` `@[scripts/backend_audit_loop.py#L68-L78]`<br>`[MODIFY]` `@[scripts/backend_audit_loop.py#L422-L682]` | `MODIFY` | Universal Backend Quality Gate | `discover_authoritative_scripts`, `_MACRO_AUTHORITATIVE_SCRIPTS`, `main` | `uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --test --ast-strict` |
| `[MODIFY]` `@[scripts/auto_hardening_runner.py#L133-L179]`<br>`[MODIFY]` `@[scripts/auto_hardening_runner.py#L182-L196]`<br>`[MODIFY]` `@[scripts/auto_hardening_runner.py#L340-L394]`<br>`[MODIFY]` `@[scripts/auto_hardening_runner.py#L970-L1027]`<br>`[MODIFY]` `@[scripts/auto_hardening_runner.py#L1030-L1173]`<br>`[MODIFY]` `@[scripts/auto_hardening_runner.py#L1176-L1336]` | `MODIFY` | Autonomous Hardening Runner & SHA-256 Cache | `DEFAULT_HARDENING_CACHE_PATH`, `HISTORICAL_COMPLETED_TRACKERS`, `HardeningCacheEntryDTO`, `HardeningCacheManifestDTO`, `HardeningRunnerArgsDTO`, `HardeningIterationResultDTO`, `compute_file_sha256`, `resolve_target_unit_test_files`, `compute_rules_sha256`, `compute_target_cache_entry`, `parse_tracker_hardened_targets`, `load_or_seed_hardening_cache`, `save_hardening_cache`, `process_target_with_retries`, `run_hardening_pipeline`, `main` | `uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py --test --ast-strict` |
| `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2413-L2423]`<br>`[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2564-L2576]` | `MODIFY` | Guardrail Unit Tests | `test_boundary_and_residual_exemption_sets_exist_on_disk`, `test_qgr020_bare_field_without_annotated_raises_fatal`, `test_qgr031_*`, `test_qgr032_*`, `test_qgr033_*`, `test_discover_authoritative_scripts_dynamic_glob` | `uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict` |
| `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1179-L1199]` | `MODIFY` | Hardening Runner Unit Tests | `test_sha256_cache_hit_skips_subagent_and_marks_tracker_zero_seconds`, `test_sha256_cache_invalidates_on_target_test_or_rule_mutation`, `test_seed_cache_from_completed_wave_and_uuidv7_trackers`, `test_no_cache_flag_bypasses_sha256_cache` | `uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py --test --ast-strict` |
| `[MODIFY]` `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]` | `MODIFY` | Polyfactory Meta-Test Suite | `discover_all_model_factories`, `ALL_FACTORIES`, `test_dynamic_discovery_matches_registered_factories`, `test_polyfactory_build_succeeds` | `uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/factories/test_model_factories.py --test --ast-strict` |

---

## 3. Phase 1: Pre-Implementation Technical Debt Cleanups

Pre-flight execution of `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets scripts/auto_hardening_runner.py scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --include-one-hop` returned **0 technical debt findings** (`PASSED (Clean)`).

Furthermore, an AST pre-flight scan across all 403 production `.py` files in `backend_v2/` and all scripts in `scripts/` confirmed:
- `Raises: None` in docstrings (`QGR033` Check 33A): **0 existing violations**.
- Missing top-level public class docstrings (`QGR033` Check 33B): **0 existing violations**.
- Missing module-level docstrings (`QGR033` Check 33B): Exactly **4 residual files** (`backend_v2/models/dtos/variance.py`, `backend_v2/services/orchestrator/extraction_schema_factory.py`, `backend_v2/services/orchestrator/rag_preflight_service.py`, `backend_v2/services/orchestrator/schema_factory.py`), locked in `RESIDUAL_MISSING_DOCSTRING_FILES`.
- `raise AppException` without `logger.error` (`QGR033` Check 33C): Exactly **1 domain file** (`backend_v2/services/auth/repositories.py`, scheduled for `EPIC 160` IAM rewrite) plus logger/exception bootstrap files (`backend_v2/logging_config.py`, `backend_v2/exceptions.py`), locked in `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`.
- Bare `Field(...)` without `Annotated[...]` (`QGR020` Check 20B): Exactly **25 pre-existing files**, locked in `RESIDUAL_BARE_FIELD_FILES` and verified by `test_boundary_and_residual_exemption_sets_exist_on_disk` so zero new bare `Field(...)` declarations can ever be introduced and no already-hardened Wave 1–4 or UUIDv7 file regresses.

---

## 4. Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <phase id="1" name="Static AST Guardrails QGR020, QGR031, QGR032, QGR033 &amp; Dynamic Script Discovery">
    <step id="1" name="Implement QGR020 Bare Field Ban, QGR031 Filter Guard, QGR032 Factory Guard &amp; QGR033 Docstring/RFC7807 Guard in scripts/_ast_guardrails.py">
      <target>@[scripts/_ast_guardrails.py#L573-L586]</target>
      <target>@[scripts/_ast_guardrails.py#L589-L609]</target>
      <constraint invariant="ast_guardrail_mandate">Enforce QGR020 bare Field() ban, QGR031 Filter/QueryCondition discipline, QGR032 Polyfactory Use(generate_opaque_id, ...) invariant, and QGR033 PEP 257 / Raises: None / RFC 7807 logger.error before raise AppException at FATAL severity.</constraint>
      <constraint invariant="pydantic_annotated_fields_mandate">Ban bare type annotations combined with = Field(...) on Pydantic classes unless wrapped in PEP 593 Annotated[T, ...].</constraint>
      <constraint invariant="rfc7807_dual_reporting_mandate">Require structured logger.error / logger.critical / logger.exception in any domain function or method that raises AppException.</constraint>
      <constraint invariant="docstring_fail_fast_ban">Ban 'Raises: None' in all docstrings across production and script modules.</constraint>
      <action>
        1. In `@[scripts/_ast_guardrails.py#L573-L586]` and `@[scripts/_ast_guardrails.py#L589-L609]`, define the self-verifying residual sets, `QGR031` operator constants, and pure AST helpers (and export the residual sets in `__all__`):
           - `RESIDUAL_BARE_FIELD_FILES: frozenset[str]` containing the exact closed list of 25 pre-existing files with legacy `= Field(...)` assignments (specifically and exhaustively: `"backend_v2/core/hook_registry.py"`, `"backend_v2/core/registry.py"`, `"backend_v2/exceptions.py"`, `"backend_v2/models/domain/execution.py"`, `"backend_v2/models/domain/inputs.py"`, `"backend_v2/models/domain/matrix.py"`, `"backend_v2/models/domain/output_profile.py"`, `"backend_v2/models/domain/prompt_blocks.py"`, `"backend_v2/models/domain/step.py"`, `"backend_v2/models/domain/system_config.py"`, `"backend_v2/models/domain/workflow.py"`, `"backend_v2/models/dtos/engine.py"`, `"backend_v2/models/dtos/hook_state.py"`, `"backend_v2/models/dtos/quote_evidence.py"`, `"backend_v2/models/dtos/report_data.py"`, `"backend_v2/models/dtos/theory_manifest.py"`, `"backend_v2/models/llm.py"`, `"backend_v2/models/view/sdui.py"`, `"backend_v2/services/chat_parser.py"`, `"backend_v2/services/execution/ingress_service.py"`, `"backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py"`, `"scripts/ablation_live_executor.py"`, `"scripts/audit_database_atoms.py"`, `"scripts/diff_executions.py"`, `"scripts/reconcile_storage.py"`).
           - `RESIDUAL_MISSING_DOCSTRING_FILES: frozenset[str]` containing the exact closed list of 4 pre-existing module-docstring files (specifically and exhaustively: `"backend_v2/models/dtos/variance.py"`, `"backend_v2/services/orchestrator/extraction_schema_factory.py"`, `"backend_v2/services/orchestrator/rag_preflight_service.py"`, `"backend_v2/services/orchestrator/schema_factory.py"`).
           - `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES: frozenset[str]` containing the exact closed list of 3 files (specifically and exhaustively: `"backend_v2/exceptions.py"`, `"backend_v2/logging_config.py"`, `"backend_v2/services/auth/repositories.py"`).
           - `_QGR031_VALID_OPERATOR_LITERALS: frozenset[str] = frozenset({"==", "!=", ">", ">=", "<", "<=", "in", "array_contains", "array-contains"})` and `_QGR031_VALID_ENUM_ATTRS: frozenset[str] = frozenset({"EQ", "NE", "GT", "GTE", "LT", "LTE", "IN", "CONTAINS"})`.
           - `_RAISES_NONE_REGEX: re.Pattern[str] = re.compile(r"Raises:\s*(?:\n\s*)?None\b")`.
           - `_is_annotated_subscript(annotation: ast.AST | None) -> bool`: Returns `True` if `annotation` is an `ast.Subscript` whose `value` is `ast.Name(id="Annotated")` or `ast.Attribute(attr="Annotated")`.
           - `_function_has_error_log(fn_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool`: Walks `fn_node` (excluding nested `FunctionDef`/`AsyncFunctionDef`/`ClassDef` scopes) and returns `True` if any `ast.Call` invokes `logger.error`, `logger.critical`, `logger.exception`, `log.error`, `logging.error`, or a helper function whose identifier contains `log_error` or `_log_`.
           - `_find_direct_app_exception_raises(fn_node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.Raise]`: Collects `ast.Raise` nodes directly inside `fn_node` (excluding nested function definitions) where `node.exc` is a call to `AppException`.
        2. In `QuorumGuardrailVisitor.visit_Module` in `scripts/_ast_guardrails.py`:
           - **QGR033 Check 33A (`Raises: None` Ban)**: If `not self.is_guardrail_self`, inspect `ast.get_docstring(node)` and emit `FATAL` `QGR033` if `_RAISES_NONE_REGEX.search(doc)` matches.
           - **QGR033 Check 33B (Module Docstring Guard)**: If `not self._is_test_file and self._is_domain_code` and `norm_path` is not in `RESIDUAL_MISSING_DOCSTRING_FILES`, emit `FATAL` `QGR033` if `not ast.get_docstring(node)`.
        3. In `QuorumGuardrailVisitor._check_qgr031_filter_call` and `visit_Call` in `scripts/_ast_guardrails.py`:
           - **QGR031 (`Filter` / `QueryCondition` Static Discipline)**: When `node.func` is `Name(id="Filter" | "QueryCondition")` or `Attribute(attr="Filter" | "QueryCondition")` (and not `is_guardrail_self`), resolve `field_arg`, `op_arg`, and `value_arg` from positional (`args[0..2]`) or keyword (`field=`, `operator=`, `op=`, `value=`) arguments and emit `FATAL` `QGR031` if:
             a) `field_arg` is `ast.Constant(value=str(s))` with `s.strip() == ""`,
             b) `op_arg` is `ast.Constant(value=str(op_s))` not in `_QGR031_VALID_OPERATOR_LITERALS` or `ast.Attribute(value=ast.Name(id="FilterOperator"), attr=attr_s)` not in `_QGR031_VALID_ENUM_ATTRS`,
             c) `op_arg` resolves to `"in"` or `FilterOperator` (`IN`) and `value_arg` is `ast.Constant(value=str() | bytes())`.
        4. In `QuorumGuardrailVisitor.visit_ClassDef` in `scripts/_ast_guardrails.py`:
           - **QGR033 Check 33A &amp; 33B**: Check `ast.get_docstring(node)` for `_RAISES_NONE_REGEX` (when `not self.is_guardrail_self`), and if `not self._is_test_file and self._is_domain_code and self._function_depth == 0 and not node.name.startswith("_")`, emit `FATAL` `QGR033` if `not ast.get_docstring(node)`.
           - **QGR032 (Polyfactory `ModelFactory` 32-Hex `UUIDv7` Invariant)**: When `norm_path.endswith("backend_v2/tests/factories/model_factories.py")` (or `not self.is_guardrail_self` and class inherits from `ModelFactory[...]`), inspect class body assignments (`ast.Assign` / `ast.AnnAssign`) targeting `"id"`, `"organization_id"`, `"node_id"`, `"execution_id"`, `"workflow_id"`, or `"profile_id"`, and emit `FATAL` `QGR032` unless the assigned value is a `Use(generate_opaque_id, ...)` call.
        5. In `QuorumGuardrailVisitor.visit_FunctionDef` and `visit_AsyncFunctionDef` in `scripts/_ast_guardrails.py`:
           - Add helper `self._check_qgr033_function_contracts(node)`:
             a) If `not self.is_guardrail_self`, inspect `ast.get_docstring(node)` and emit `FATAL` `QGR033` if `_RAISES_NONE_REGEX.search(doc)` matches.
             b) If `self._is_domain_code and not self._is_test_file` and `norm_path` is not in `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES`, check `_find_direct_app_exception_raises(node)`. If non-empty and `not _function_has_error_log(node)`, emit `FATAL` `QGR033` on each unlogged `raise AppException(...)` statement.
        6. In `QuorumGuardrailVisitor.visit_AnnAssign` in `scripts/_ast_guardrails.py`:
           - **QGR020 Check 20B (`pydantic_annotated_fields_mandate`)**: When `self._current_class_name in self._pydantic_base_classes_in_file and self._function_depth == 0 and node.value is not None and _is_field_call(node.value) and not _is_annotated_subscript(node.annotation)` and `norm_path` is not in `RESIDUAL_BARE_FIELD_FILES`, emit `FATAL` `QGR020` instructing to wrap the field in `Annotated[T, Field(...)]`.
        7. Update the CLI help table in `main` in `scripts/_ast_guardrails.py` to list `QGR031`, `QGR032`, and `QGR033`.
      </action>
    </step>

    <step id="2" name="Replace Hardcoded Script Tuple with Dynamic scripts/*.py Discovery in scripts/backend_audit_loop.py">
      <target>@[scripts/backend_audit_loop.py#L68-L78]</target>
      <target>@[scripts/backend_audit_loop.py#L422-L682]</target>
      <constraint invariant="universal_ssot_and_normalization_mandate">Eliminate manual script whitelist maintenance by dynamically resolving all scripts/*.py files at runtime.</constraint>
      <action>
        1. In `@[scripts/backend_audit_loop.py#L68-L78]`, verify `discover_authoritative_scripts(scripts_dir: Path = Path("scripts")) -> tuple[str, ...]` returns `tuple(p.as_posix() for p in sorted(scripts_dir.glob("*.py")) if p.is_file())`, is exported in `__all__`, and binds `_MACRO_AUTHORITATIVE_SCRIPTS: tuple[str, ...] = discover_authoritative_scripts()`.
        2. In `@[scripts/backend_audit_loop.py#L422-L682]`, call `discover_authoritative_scripts()` dynamically when `is_macro_backend_gate` is `True`.
      </action>
    </step>

    <step id="3" name="Add ISTQB Unit Tests for QGR020, QGR031, QGR032, QGR033 &amp; Dynamic Script Discovery and Upgrade Polyfactory Meta-Test">
      <target>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2413-L2423]</target>
      <target>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2564-L2576]</target>
      <target>@[backend_v2/tests/factories/test_model_factories.py#L71-L90]</target>
      <constraint invariant="anti_happy_path_mandate">Include positive valid tests and at least 2 negative boundary/violation tests per new AST guardrail rule and meta-test.</constraint>
      <action>
        1. In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2413-L2423]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2564-L2576]`:
           - Import `RESIDUAL_BARE_FIELD_FILES`, `RESIDUAL_MISSING_DOCSTRING_FILES`, and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` and register them in `test_boundary_and_residual_exemption_sets_exist_on_disk`.
           - Add unit tests for `QGR020` Check 20B (`test_qgr020_bare_field_without_annotated_raises_fatal`, `test_qgr020_annotated_field_and_residual_exemption_allowed`).
           - Add unit tests for `QGR031` (`test_qgr031_invalid_filter_operators_raise_fatal`, `test_qgr031_empty_filter_field_raises_fatal`, `test_qgr031_in_operator_with_string_literal_raises_fatal`, `test_qgr031_valid_filter_calls_pass`).
           - Add unit tests for `QGR032` (`test_qgr032_model_factory_hardcoded_or_uuid4_id_raises_fatal`, `test_qgr032_model_factory_use_generate_opaque_id_allowed`).
           - Add unit tests for `QGR033` (`test_qgr033_raises_none_in_docstring_raises_fatal`, `test_qgr033_missing_module_or_public_class_docstring_raises_fatal`, `test_qgr033_unlogged_app_exception_in_domain_function_raises_fatal`, `test_qgr033_logged_app_exception_and_valid_docstrings_allowed`).
           - Add `test_discover_authoritative_scripts_dynamic_glob` verifying `discover_authoritative_scripts` in `scripts/backend_audit_loop.py`.
        2. In `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]`:
           - Add `discover_all_model_factories() -> tuple[type[ModelFactory[Any]], ...]` using recursive `ModelFactory.__subclasses__()` traversal across `backend_v2.tests.factories.model_factories`.
           - Add `test_dynamic_discovery_matches_registered_factories` asserting `set(discover_all_model_factories()) == set(ALL_FACTORIES)`.
           - Expand `test_polyfactory_build_succeeds` to check all `*_id` string fields (`id`, `organization_id`, `node_id`, `execution_id`, `workflow_id`, `profile_id`) against `OPAQUE_STRIPE_ID_REGEX`.
      </action>
    </step>
  </phase>

  <phase id="2" name="Content-Addressed SHA-256 Hardening Cache &amp; Completed Tracker Seeding in auto_hardening_runner.py">
    <step id="4" name="Implement SHA-256 Hardening Cache DTOs, Tracker Seeding (Waves 1-4 &amp; UUIDv7) &amp; 0s Short-Circuit in scripts/auto_hardening_runner.py">
      <target>@[scripts/auto_hardening_runner.py#L133-L179]</target>
      <target>@[scripts/auto_hardening_runner.py#L182-L196]</target>
      <target>@[scripts/auto_hardening_runner.py#L340-L394]</target>
      <target>@[scripts/auto_hardening_runner.py#L970-L1027]</target>
      <target>@[scripts/auto_hardening_runner.py#L1030-L1173]</target>
      <target>@[scripts/auto_hardening_runner.py#L1176-L1336]</target>
      <constraint invariant="strict_pydantic_v2_rust">All cache entries and manifests must be validated via frozen Pydantic V2 DTOs with ConfigDict(strict=True, extra='forbid', frozen=True) and serialized via model_validate_json / model_dump_json.</constraint>
      <constraint invariant="no_naked_dicts_in_state">Never pass raw untyped dicts for cache state transit.</constraint>
      <action>
        1. In `@[scripts/auto_hardening_runner.py#L133-L179]` and `@[scripts/auto_hardening_runner.py#L182-L196]`:
           - Import `hashlib` at the top of `scripts/auto_hardening_runner.py`.
           - Define `DEFAULT_HARDENING_CACHE_PATH: Path = Path("data/hardening_cache.json")` and `HISTORICAL_COMPLETED_TRACKERS: tuple[str, ...] = ("docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md", "docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md", "docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md", "docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md", "docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md", "docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md")`.
           - Create and define `HardeningCacheEntryDTO(BaseModel)` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` containing:
             * `target_file: Annotated[str, Field(description="Normalized POSIX relative path of the hardened target.")]`
             * `target_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$", description="SHA-256 hex digest of target file content.")]`
             * `unit_test_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$", description="Composite SHA-256 hex digest of resolved unit test file(s).")]`
             * `rules_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$", description="Composite SHA-256 hex digest of .agents/rules/ files.")]`
             * `composite_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$", description="Combined SHA-256 hex digest of target, unit tests, and rules.")]`
             * `source_tracker: Annotated[str | None, Field(default=None, description="Tracker markdown path where target was hardened.")]` = None
           - Create and define `HardeningCacheManifestDTO(BaseModel)` with `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` containing `entries: Annotated[dict[str, HardeningCacheEntryDTO], Field(default_factory=dict, description="Map of target relative path to cache entry.")]`.
           - Add `no_cache: Annotated[bool, Field(default=False, description="Bypass SHA-256 hardening cache and force execution.")] = False` and `cache_file: Annotated[Path, Field(default=DEFAULT_HARDENING_CACHE_PATH, description="Path to SHA-256 hardening cache JSON.")] = DEFAULT_HARDENING_CACHE_PATH` to `HardeningRunnerArgsDTO`.
           - Add `cache_hit: Annotated[bool, Field(default=False, description="Whether target was satisfied via 0s SHA-256 cache hit.")] = False` to `HardeningIterationResultDTO`.
        2. In `@[scripts/auto_hardening_runner.py#L340-L394]`, add deterministic SHA-256 and tracker seeding functions (and export them in `__all__`):
           - `parse_tracker_hardened_targets(tracker_content: str, gate: HardeningGate) -> list[str]`: Extracts checked `- [x] @[...]` target paths under `Tier 2 Hardening (Backend)` and `Tier 2 Hardening (Frontend)`.
           - `compute_file_sha256(file_path: Path) -> str`: Returns `hashlib.sha256(file_path.read_bytes()).hexdigest()`.
           - `resolve_target_unit_test_files(target_file: str, repo_root: Path) -> list[Path]`: Resolves existing unit test files for `backend_v2/.../*.py`, `scripts/*.py`, and `client_app_v2/lib/.../*.dart`.
           - `compute_rules_sha256(repo_root: Path) -> str`: Computes a composite SHA-256 digest over sorted `(repo_root / ".agents" / "rules").glob("*.md")`.
           - `compute_target_cache_entry(target_file: str, repo_root: Path, rules_sha256: str | None = None, source_tracker: str | None = None) -> HardeningCacheEntryDTO | None`: Computes `target_sha256`, `unit_test_sha256`, `rules_sha256`, and `composite_sha256` for `target_file` if it exists on disk.
           - `load_or_seed_hardening_cache(cache_path: Path, repo_root: Path) -> HardeningCacheManifestDTO`: Loads `HardeningCacheManifestDTO` from `cache_path` if present, then scans `HISTORICAL_COMPLETED_TRACKERS` (and `docs/implementationplans/TRACKER_*.md` + `docs/epic/*_tracker.md`) for `- [x]` targets; for any target not yet in `entries` (or whose `rules_sha256` matches current rules and has zero uncommitted git working-tree changes), populates its `HardeningCacheEntryDTO` and persists the manifest to `cache_path`.
           - `save_hardening_cache(cache_path: Path, manifest: HardeningCacheManifestDTO, repo_root: Path) -> None`: Writes `manifest.model_dump_json(indent=2)` to `cache_path` (creating parent directories if needed).
        3. In `@[scripts/auto_hardening_runner.py#L970-L1027]`, `@[scripts/auto_hardening_runner.py#L1030-L1173]`, and `@[scripts/auto_hardening_runner.py#L1176-L1336]`:
           - Update `process_target_with_retries` to check `load_or_seed_hardening_cache` when `not args.no_cache`: if `existing_entry.composite_sha256 == current_entry.composite_sha256`, print `⚡ CACHE HIT: {target_file} (SHA-256 unchanged, 0.0s — skipped LLM subagent)`, call `mark_tracker_and_checkpoint(target_file, args.tracker, args.state_file, repo_root=root)`, and return `HardeningIterationResultDTO(target_file=target_file, gate=args.gate, success=True, attempts=0, duration_seconds=0.0, git_committed=checkpoint.git_committed, tracker_marked=checkpoint.tracker_marked, cache_hit=True)`.
           - When a target executes and passes `run_quality_gate`, update the cache entry in `args.cache_file` before returning `HardeningIterationResultDTO`.
           - In `run_hardening_pipeline`, filter `successful_backend_targets` for the final macro-audit completion gate to `[it.target_file for it in iterations if it.success and not it.cache_hit and it.target_file.endswith(".py")]` so 100% cache-hit runs finish instantaneously.
           - In `main`, expose `--no-cache` / `--force-agent` (`dest="no_cache"`, `action="store_true"`) and `--cache-file` (`type=Path`, `default=DEFAULT_HARDENING_CACHE_PATH`).
      </action>
    </step>

    <step id="5" name="Add Comprehensive ISTQB Unit Tests for SHA-256 Hardening Cache &amp; Tracker Seeding in test_auto_hardening_runner.py">
      <target>@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1179-L1199]</target>
      <constraint invariant="anti_happy_path_mandate">Test positive 0s cache hit, historical tracker seeding from Waves 1-4 &amp; UUIDv7, and negative cache invalidation when target, unit test, or .agents/rules/ file changes or --no-cache is passed.</constraint>
      <action>
        1. In `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1179-L1199]`, import the new SHA-256 cache symbols (`HardeningCacheEntryDTO`, `HardeningCacheManifestDTO`, `compute_file_sha256`, `compute_rules_sha256`, `compute_target_cache_entry`, `load_or_seed_hardening_cache`, `parse_tracker_hardened_targets`, `resolve_target_unit_test_files`, `save_hardening_cache`) and add unit tests:
           - `test_sha256_cache_hit_skips_subagent_and_marks_tracker_zero_seconds`: Verifies that when a target's composite SHA-256 (`target + unit_test + rules`) matches the cached entry, `process_target_with_retries` never calls `execute_subagent_pass` or `run_quality_gate`, marks `- [x]` in the tracker, and returns `cache_hit=True` with `attempts=0`.
           - `test_sha256_cache_invalidates_on_target_test_or_rule_mutation`: Verifies that modifying 1 byte in either (a) the target `.py` file, (b) its unit test `test_*.py` file, or (c) any `.agents/rules/*.md` file changes `composite_sha256`, causing a cache miss that runs the full hardening pass and updates the cache entry.
           - `test_seed_cache_from_completed_wave_and_uuidv7_trackers`: Verifies `parse_tracker_hardened_targets` and `load_or_seed_hardening_cache` automatically seed `- [x]` targets from completed Wave 1–4 and UUIDv7 trackers into `hardening_cache.json`.
           - `test_no_cache_flag_bypasses_sha256_cache`: Verifies `--no-cache` / `--force-agent` forces subagent execution even when a valid cache entry exists.
      </action>
    </step>
  </phase>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Equivalence Partitions)

### 5.1 Positive & Negative Test Scenarios

| Test Case ID | Target Rule / Component | Partition Type | Input Scenario | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **TC-QGR020-POS-01** | `QGR020` Check 20B | Positive (Valid) | `class MyDTO(BaseModel): x: Annotated[int, Field(ge=0)] = 1` | `0` violations |
| **TC-QGR020-NEG-01** | `QGR020` Check 20B | Negative (Bare `Field`) | `class MyDTO(BaseModel): x: int = Field(default=1)` in non-residual file | `1` `FATAL` `QGR020` violation |
| **TC-QGR031-POS-01** | `QGR031` | Positive (Valid) | `Filter(field="status", op="in", value=["PASSED"])` | `0` violations |
| **TC-QGR031-NEG-01** | `QGR031` | Negative (Invalid Operator & Empty Field) | `Filter(field="", op="eq", value="x")` and `QueryCondition(field="a", op="LIKE", value="b")` | `2` `FATAL` `QGR031` violations |
| **TC-QGR031-NEG-02** | `QGR031` | Negative (`IN` String Value) | `Filter(field="id", op="in", value="wf_123")` | `1` `FATAL` `QGR031` violation |
| **TC-QGR032-POS-01** | `QGR032` | Positive (Valid Factory) | `class WorkflowFactory(ModelFactory[Workflow]): id = Use(generate_opaque_id, EntityPrefix.WORKFLOW)` | `0` violations |
| **TC-QGR032-NEG-01** | `QGR032` | Negative (Hardcoded / Lambda ID) | `id = "wf_0195f3a0000070008000000000000001"` or `id = Use(lambda: "wf_123")` in `ModelFactory` | `FATAL` `QGR032` violation |
| **TC-QGR033-POS-01** | `QGR033` | Positive (Valid Docstrings & Logged `AppException`) | Module + class + function with PEP 257 docstrings and `logger.error(...)` preceding `raise AppException(ErrorCodes.VALIDATION_FAILED, ...)` | `0` violations |
| **TC-QGR033-NEG-01** | `QGR033` Check 33A/33B | Negative (`Raises: None` & Missing Docstring) | Function docstring containing `Raises:\n        None` or domain class missing docstring | `FATAL` `QGR033` violations |
| **TC-QGR033-NEG-02** | `QGR033` Check 33C | Negative (Unlogged `AppException`) | Domain function raising `AppException(ErrorCodes.NOT_FOUND, "Missing")` without `logger.error` | `1` `FATAL` `QGR033` violation |
| **TC-AHR-CACHE-POS-01** | `auto_hardening_runner.py` SHA-256 Cache | Positive (Cache Hit & Tracker Seeding) | Target hardened in `TRACKER_Backend_Targeted_Hardening_Wave2.md` with unchanged file, test, and `.agents/rules/` SHA-256 | Marked `- [x]` in `0.0s`, `cache_hit=True`, `attempts=0`, LLM subagent skipped |
| **TC-AHR-CACHE-NEG-01** | `auto_hardening_runner.py` SHA-256 Cache | Negative (Target / Test / Rule Mutation) | Target `.py` file, unit test `test_*.py`, or `.agents/rules/01-python-backend.md` modified by 1 byte | Cache miss detected (`composite_sha256` mismatch); full hardening pass runs and updates cache |
| **TC-AHR-CACHE-NEG-02** | `auto_hardening_runner.py` `--no-cache` | Negative (Forced Execution) | `--no-cache` / `--force-agent` passed on cached target | Cache bypassed; subagent and quality gate execute normally |

### 5.2 Verification Gate Commands

#### 1. Targeted Development Quality Gates (Windows PowerShell)
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_ast_guardrails.py scripts/backend_audit_loop.py scripts/auto_hardening_runner.py backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py backend_v2/tests/factories/test_model_factories.py --test --ast-strict
```

#### 2. Global Completion Gate (Windows PowerShell)
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test
```

#### 3. Global Completion Gate (Unix / Bash CI Reference)
```bash
UV_NO_SYNC=1 UV_OFFLINE=1 uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test
```
