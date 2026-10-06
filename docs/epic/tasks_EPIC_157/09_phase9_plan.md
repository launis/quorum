# Phase 9: Suppression & Cast Eradication (# noqa, cast(Any, ...))

**Overview:** Delete the `[REASON: ...]` comment suppression authorization so that every `# noqa` comment token is a FATAL violation; delete the AST inline suppressor (`CommentSuppressor`) from `scripts/_ast_guardrails.py`, `scripts/backend_audit_loop.py`, `scripts/audit_warning_baseline.py`, and align 1-hop callers; add `cast(Any, ...)` detection (Metric 12: `permissive_casts`) to the call audit in `scripts/audit_dict_eradication.py`; align `QGR012` with `BOUNDARY_EXEMPTION_FILES` in `scripts/_ast_guardrails.py`; and eradicate Census N (73 comment tokens in 29 files) and Census X (11 calls in 5 files, plus 2 comment/docstring occurrences in `scripts/audit_warning_baseline.py`). Third-party attribute reads in `backend_v2/llm/provider.py` and `backend_v2/llm/adapters/base_adapter.py` move to `inspect.getattr_static` and typed Pydantic V2 adapter DTOs validated with `model_validate(obj, from_attributes=True)`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L562-L587] Phase 9: Suppression & Cast Eradication (# noqa, cast(Any, ...)) (Epic baseline lines: #L562-L587, #L205-L322, #L282-L477).

**Target Files (42 files):**
- `[MODIFY]` @[scripts/audit_dict_eradication.py]
- `[MODIFY]` @[scripts/_ast_guardrails.py]
- `[MODIFY]` @[scripts/backend_audit_loop.py]
- `[MODIFY]` @[scripts/audit_warning_baseline.py]
- `[MODIFY]` @[scripts/audit_matrix_manager.py]
- `[MODIFY]` @[scripts/audit_markdown_boundaries.py]
- `[MODIFY]` @[scripts/audit_epic_coverage.py]
- `[MODIFY]` @[scripts/audit_planner_output.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_audit_matrix_manager.py]
- `[MODIFY]` @[backend_v2/llm/provider.py]
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py]
- `[MODIFY]` @[backend_v2/database/firestore_driver.py]
- `[MODIFY]` @[backend_v2/database/tinydb_driver.py]
- `[MODIFY]` @[backend_v2/logging_config.py]
- `[MODIFY]` @[backend_v2/main.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/tests/conftest.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_caching_integration.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_e2e_orchestration.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_init.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_blueprint.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_output_profile_studio_parity.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_bug_synthesis_hook.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_context_mapper.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_dag_taskgroup.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_executions.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_metrics.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_v2_core_models.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_web_fetcher.py]
- `[MODIFY]` @[backend_v2/tests/unit/test_xai_extensions.py]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **CommentSuppressor & Inline Suppression Parser in AST Guardrails**:
   - In @[scripts/_ast_guardrails.py], `CommentSuppressor` parses inline comment suppressions (`# noqa: QGRxxx [REASON: ...]`) and flags violations as `is_suppressed=True`. In @[scripts/backend_audit_loop.py] and @[scripts/audit_warning_baseline.py], violations are filtered via `[v for v in violations if not v.is_suppressed]`, creating an unauthorized escape hatch that evades static analysis. Eradicating `CommentSuppressor`, deleting the `is_suppressed` field from `GuardrailViolation`, and removing suppression filtering restores absolute invariant enforcement.
2. **1-Hop Caller Blast Radius on `is_suppressed` Field Removal**:
   - In @[scripts/audit_matrix_manager.py] line 392, `unsuppressed_violations = [v for v in rule.ast_violations if not v.is_suppressed]` accesses `v.is_suppressed`. In @[scripts/audit_markdown_boundaries.py] line 475, `if v.is_suppressed:` accesses `v.is_suppressed`. In @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py], @[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py], and @[backend_v2/tests/unit/scripts/test_audit_matrix_manager.py], multiple fixtures instantiate `GuardrailViolation(..., is_suppressed=False)`. Because `GuardrailViolation` enforces `extra="forbid"`, removing `is_suppressed` requires synchronously updating these callers to prevent runtime `AttributeError` and `ValidationError` crashes.
3. **Missing Boundary Exemption in QGR012 isinstance Check**:
   - In @[scripts/_ast_guardrails.py] line 878, the `QGR012` `isinstance(..., dict | Mapping)` check omits `not self._is_boundary_exempt and self._is_domain_code`. This forced historical `# noqa: QGR012` comments inside locked boundary files (`tinydb_driver.py`, `firestore_driver.py`, `logging_config.py`, `base_adapter.py`, `provider.py`) that legitimately serialize raw database payloads and JSON schemas. Adding `not self._is_boundary_exempt and self._is_domain_code` to line 878 aligns `_ast_guardrails.py` with `BOUNDARY_EXEMPTION_FILES` and unblocks complete eradication of those 9 `# noqa: QGR012` comment tokens.
4. **Permissive `[REASON: ...]` Authorization in Dict Eradication Audit**:
   - In @[scripts/audit_dict_eradication.py], `audit_file_comments` currently authorizes `# noqa: QGR` comment suppressions if followed by a reason block of ten or more characters. Removing the authorization logic so that any `# noqa` comment token unconditionally triggers a FATAL `unauthorized_suppressions` violation guarantees zero comment escape hatches.
5. **Missing `cast(Any, ...)` AST Detection in Dict Eradication Audit (Metric 12)**:
   - In @[scripts/audit_dict_eradication.py], `visit_Call` detects reflection and duck typing, but does not flag permissive `cast(Any, ...)` calls. Adding explicit detection for `ast.Name(id="cast")` and `ast.Attribute(value=ast.Name(id="typing"), attr="cast")` with first argument `Any` or `typing.Any` as Metric 12 (`permissive_casts`) in `DictEradicationReport` enforces programmatic eradication of Census X.
6. **Self-Referential Baseline Ledger Ceilings in audit_warning_baseline.py**:
   - In @[scripts/audit_warning_baseline.py], `re.findall(r"cast\(\s*Any\b", text)` scans `scripts/` and matches line 59 and line 127 in `audit_warning_baseline.py` itself, yielding 2 false positive counts above the true 11 `cast(Any, ...)` call sites in `backend_v2`. Furthermore, line 171 contains `# Census N: # noqa comment tokens`, matching tokenize checks. Rephrasing lines 59, 127, and 171 eliminates self-referential matches and enables clean ratchet down to `x=0` and `n=0`.
7. **Third-Party Reflection in LLM Provider & Base Adapter**:
   - In @[backend_v2/llm/provider.py] and @[backend_v2/llm/adapters/base_adapter.py], 32 `# noqa` comment suppressions mask dynamic attribute inspections on third-party LiteLLM exception objects, HTTP response headers, model metadata, and token usage objects. Replacing dynamic attribute indexing and reflection with `inspect.getattr_static` and typed Pydantic V2 adapter DTOs hydrated via `model_validate(obj, from_attributes=True)` eliminates dynamic reflection natively.
8. **Duct-Tape State Casting in LLM Orchestration Strategy**:
   - In @[backend_v2/services/orchestrator/strategies/llm.py], line 969 uses `exec_record = cast(Any, exec_record_raw)` to unpack the execution record after an anomaly retry. `self.exec_repo.get_execution` already returns `ExecutionRecord | None`. Inspecting `if exec_record is not None and step.id in exec_record.step_states:` directly eliminates the permissive cast without changing runtime behavior.
9. **Permissive Mock and Fixture Casts in Integration and Unit Tests**:
   - In @[backend_v2/tests/integration/test_caching_integration.py], @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py], and @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py], nine instances of `sys.modules[...] = cast(Any, MockModule)` bypass module typing. In @[backend_v2/tests/unit/test_context_mapper.py], `all_blocks=cast(Any, [{"id": "blk_1"}])` bypasses PromptBlockDTO typing. Supplying typed `types.ModuleType` instances or valid Pydantic DTO instances removes all remaining Census X calls.
10. **Residual Ruff `# noqa` Comments in Production, Scripts, and Test Files**:
   - Twenty-nine files contain 73 active `# noqa` comment tokens masking long lines (`E501`), unused imports (`F401`), star imports (`F403`), and misplaced imports (`E402`). Formatting lines cleanly under 120 characters, deleting dead imports, using explicit import names, consuming side-effect imports via `_ = _hooks`, and hoisting imports to module top level eradicates Census N completely.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]` | Banned inline `# noqa: QGRxxx [REASON: ...]` comment suppressors, `is_suppressed` boolean flags, and missing boundary exemption on line 878 QGR012. | Eradicate `CommentSuppressor` class; remove `is_suppressed` attribute from `GuardrailViolation`; add `not self._is_boundary_exempt and self._is_domain_code` to QGR012. All AST violations in domain code are unconditionally fatal. | Zero tokenization overhead for comment parsing during AST inspection; direct visitor traversal. | `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` passes with zero suppressions. |
| `@[scripts/backend_audit_loop.py]` | Banned filtering `[v for v in violations if not v.is_suppressed]` in Stage 4 quality gate. | Inspect raw `violations` list directly in Stage 4. Any detected violation immediately triggers `sys.exit(1)`. | Direct list length check; zero filtering comprehension overhead. | `uv run python scripts/backend_audit_loop.py backend_v2/ --ast-strict` passes Stage 4 without suppression bypasses. |
| `@[scripts/audit_warning_baseline.py]` | Banned suppression filtering in baseline calculation, self-referential docstring/comment matches, and outdated residual debt ceilings (`n=73`, `x=13`). | Remove `v.is_suppressed` filter from AST check; update `CURRENT_RESIDUAL_CEILINGS.n = 0` and `CURRENT_RESIDUAL_CEILINGS.x = 0`; rephrase lines 59, 127, 171 to prevent self-matches. | Hardcoded exact integer equality ratchet. | `uv run python scripts/audit_warning_baseline.py --verify-zero` asserts zero residual suppressions and casts. |
| `@[scripts/audit_matrix_manager.py]` | Banned filtering `[v for v in rule.ast_violations if not v.is_suppressed]`. | Inspect `rule.ast_violations` directly without `v.is_suppressed` attribute lookup. | Direct list access; zero comprehension overhead. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_matrix_manager.py` passes cleanly. |
| `@[scripts/audit_markdown_boundaries.py]` | Banned filtering `if v.is_suppressed: continue` in embedded code block scanner. | Process all embedded codeblock violations directly without `is_suppressed` check. | Direct violation iteration. | `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/tasks_EPIC_157/09_phase9_plan.md` passes. |
| `@[scripts/audit_dict_eradication.py]` | Banned `[REASON: ...]` authorization for `# noqa` and unmonitored `cast(Any, ...)` calls. | Reject every `# noqa` comment token in `audit_file_comments`; detect `cast(Any, ...)` and `typing.cast(typing.Any, ...)` in `visit_Call` as Metric 12 `permissive_casts`. | Pure string search for `# noqa` in comment tokens and direct AST call matching. | `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports zero violations. |
| `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`, `@[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]`, `@[backend_v2/tests/unit/scripts/test_audit_matrix_manager.py]` | Banned test assertions asserting `v.is_suppressed` or instantiating `GuardrailViolation(..., is_suppressed=False)`. | Assert violations directly; instantiate `GuardrailViolation` without removed `is_suppressed` parameter. | Clean Pydantic model construction with `extra="forbid"`. | Unit test suites for audit scripts pass 100% with exit code 0. |
| `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]` | Banned missing unit test coverage for Metric 12 `permissive_casts` and unconditional `# noqa` rejection. | Add test verifying `# noqa` with any reason raises `unauthorized_suppressions`; add test verifying `cast(Any, ...)` raises `permissive_casts`. | Direct synthetic file assertion. | `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` passes 100%. |
| `@[backend_v2/llm/provider.py]` | Banned 27 `# noqa: QGR001` and `QGR012` suppressions masking third-party LiteLLM object inspections. | Inspect third-party attributes via `inspect.getattr_static` and hydrate LiteLLM response/exception attributes into typed Pydantic V2 adapter DTOs. | Static attribute inspection and direct Pydantic model validation; zero ad-hoc attribute reflection. | Zero `# noqa` tokens in `provider.py`; passes strict AST guardrail audit. |
| `@[backend_v2/llm/adapters/base_adapter.py]` | Banned 5 `# noqa: QGR012` suppressions on recursive JSON schema normalization. | Eradicate `# noqa: QGR012` comments; schema stripping functions under boundary exemption contract. | Explicit traversal of JSON schema dictionaries under boundary exemption. | Zero `# noqa` tokens in `base_adapter.py`. |
| `@[backend_v2/database/firestore_driver.py]`, `@[backend_v2/database/tinydb_driver.py]`, `@[backend_v2/logging_config.py]` | Banned residual `# noqa: QGR012` comments in boundary drivers. | Eradicate `# noqa: QGR012` comments; boundary drivers function under boundary exemption contract. | Clean boundary implementations without inline suppressions. | Zero `# noqa` tokens across drivers and logging config. |
| `@[backend_v2/main.py]` | Banned `# noqa: F401` masking unused hooks import. | Consume side-effect hooks import via `import backend_v2.hooks as _hooks; _ = _hooks`. | Explicit symbol utilization without lint suppression. | Ruff check passes with zero suppression tokens. |
| `@[scripts/audit_epic_coverage.py]`, `@[scripts/audit_planner_output.py]` | Banned `# noqa: E402` masking out-of-order imports. | Hoist imports to top of file using root package path `from scripts._ast_boundary_utils import ...`. | Standard PEP 8 top-level module imports. | Scripts execute cleanly with zero E402 suppressions. |
| `@[backend_v2/services/orchestrator/strategies/llm.py]` | Banned `cast(Any, exec_record_raw)` duct-tape casting. | Check `if exec_record is not None and step.id in exec_record.step_states:` directly using native `ExecutionRecord` domain type; delete `cast` import. | Native type narrowing; zero typing module import overhead. | Static typing verified by MyPy strict mode without `cast(Any)`. |
| `@[backend_v2/tests/integration/test_caching_integration.py]`, `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`, `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]` | Banned `sys.modules[...] = cast(Any, ...)` module mocking casts. | Instantiate strongly typed `types.ModuleType` instances and assign directly to `sys.modules`; delete `cast` and `Any` imports. | Standard Python standard library module mocking. | Tests pass cleanly with zero `cast(Any, ...)` invocations. |
| `@[backend_v2/tests/unit/test_context_mapper.py]` | Banned `all_blocks=cast(Any, [{"id": "blk_1"}])`. | Pass invalid payload via typed raw collection `raw_blocks: list[Any] = [{"id": "blk_1"}]` or negative fixture; delete `cast` import. | Strongly typed negative test invocation. | Context mapper tests pass with zero permissive casts. |
| Residual 17 test files | Banned `# noqa: E501`, `# noqa: F401`, and `# noqa: F403` suppression comments. | Wrap long lines under 120 characters, eliminate unused imports, and replace star imports with explicit named symbols. | Standard automated Ruff formatting and import hygiene. | Ruff checks pass cleanly across all test files with zero suppression tokens. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK &amp; BASELINE PRE-CONDITION AUDIT">
    <action>Look backward: Verify Phase 8 successfully integrated Stage 10 dict eradication in `scripts/backend_audit_loop.py` and synchronized Flutter Studio models.</action>
    <action>Verify execution pre-condition: Confirm user statement "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" (EPIC 157 Section 2.4 item 5) before touching `backend_v2/services/orchestrator/strategies/llm.py`.</action>
    <action>Verify current baseline: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and confirm current ceilings (n=73, x=13).</action>
    <action>Verify live Census N: Run Census N tokenizer check across `backend_v2` and `scripts` to verify exactly 73 active `# noqa` tokens exist across 29 files.</action>
    <action>Verify live Census X: Run Census X check across `backend_v2` and `scripts` to verify exactly 11 `cast(Any, ...)` calls exist across 5 files in `backend_v2` plus 2 self-referential docstring/comment matches in `scripts/audit_warning_baseline.py`.</action>
    <action>Look forward: Verify eradicating `CommentSuppressor`, `# noqa` tokens, and `cast(Any, ...)` calls completes Suppression &amp; Cast Eradication and establishes the invariant foundation for `# type: ignore` eradication in Phase 10.</action>
    <constraint invariant="universal_fail_fast">If unexpected suppression tokens or cast calls exist outside the residual ledger boundaries, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/09_phase9_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="1" name="AST INLINE SUPPRESSOR ERADICATION &amp; 1-HOP CALLER ALIGNMENT">
    <action>In @[scripts/_ast_guardrails.py]: Delete the `CommentSuppressor` class entirely (lines 404 to 522) and remove `"CommentSuppressor"` from `__all__`.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `GuardrailViolation` (lines 62 to 75), remove the field `is_suppressed: Annotated[bool, Field(description="Whether violation is suppressed via inline comment")]`.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `QuorumGuardrailVisitor.__init__` (line 527), remove the `suppressor: CommentSuppressor` parameter and remove `self.suppressor` assignment.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `QuorumGuardrailVisitor._add_violation` (lines 620 to 635), remove `is_suppressed = self.suppressor.is_suppressed(...)` and record violations directly without suppression attributes.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `scan_source_code_for_guardrails` and `scan_file_for_guardrails` (lines 1993 to 2065), remove `CommentSuppressor` instantiation, remove `is_suppressed=False` arguments from synthetic violations, and remove `unsuppressed = [v for v in violations if not v.is_suppressed]` filtering. Collect all violations directly from `visitor.violations`.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `scan_files_for_guardrails` (lines 2124 to 2154), replace `unsuppressed = [v for v in all_violations if not v.is_suppressed]` with direct evaluation of `all_violations`.</action>
    <action>In @[scripts/_ast_guardrails.py]: In `visit_Call` for QGR012 (line 878), prepend `not self._is_boundary_exempt and self._is_domain_code and ` to ensure boundary exemption files are properly recognized without inline suppressions.</action>
    <action>In @[scripts/backend_audit_loop.py]: In Stage 4 (lines 405 to 423), replace `unsuppressed = [v for v in violations if not v.is_suppressed]` with `unsuppressed = violations`. If `unsuppressed` is non-empty, print violations and call `sys.exit(1)`.</action>
    <action>In @[scripts/audit_warning_baseline.py]: In `scan_baseline_warnings` (line 292), replace `unsuppressed = [v for v in violations if not v.is_suppressed]` with direct inspection of `violations`.</action>
    <action>In @[scripts/audit_matrix_manager.py]: At line 392, replace `unsuppressed_violations = [v for v in rule.ast_violations if not v.is_suppressed]` with `unsuppressed_violations = rule.ast_violations`.</action>
    <action>In @[scripts/audit_markdown_boundaries.py]: At line 475, remove the `if v.is_suppressed: continue` check so all embedded codeblock violations are processed directly.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]: Update test assertions that inspect `v.is_suppressed` or filter `not v.is_suppressed` to assert violations directly, reflecting that all AST violations are unconditionally fatal.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]: Remove `is_suppressed=False` keyword arguments from `GuardrailViolation` test instantiations (lines 178, 201, 222, 247).</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]: Remove `is_suppressed=False` keyword arguments from `GuardrailViolation` test instantiations (lines 65, 87, 97, 107, 132, 153, 246).</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_matrix_manager.py]: Remove `is_suppressed=False` keyword argument from `GuardrailViolation` test instantiation (line 238).</action>
    <action>Execute localized verification: Run `uv run python scripts/_ast_guardrails.py scripts/ --strict` to verify AST guardrails execute cleanly without `CommentSuppressor`.</action>
    <constraint invariant="universal_fail_fast">Zero suppression mechanisms permitted in AST guardrails. Every detected violation is immediately fatal.</constraint>
  </step>

  <step id="2" name="CALL &amp; COMMENT AUDIT HARDENING IN audit_dict_eradication.py">
    <action>In @[scripts/audit_dict_eradication.py]: In `DictEradicationReport` (lines 85 to 133), add Metric 12 field `permissive_casts: int = 0`, include it in `total_violations` property, and format it in `format_console_report`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `DictEradicationVisitor.visit_Call` (lines 550 to 600), add check for permissive cast calls: inspect `node.func` matching `ast.Name(id="cast")` or `ast.Attribute(value=ast.Name(id="typing"), attr="cast")`. If the first argument is `ast.Name(id="Any")` or `ast.Attribute(value=ast.Name(id="typing"), attr="Any")`, append an `AuditViolation` with `metric="permissive_casts"` and message `Banned permissive cast(Any, ...) call: {ast.unparse(node)}`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `audit_dict_eradication` (lines 830 to 853), add handling for `v.metric == "permissive_casts"`: increment `report.permissive_casts += 1`.</action>
    <action>In @[scripts/audit_dict_eradication.py]: In `audit_file_comments` (lines 722 to 780), delete the regex reason check `match.group(2)` and `[REASON: ...]` authorization. Inspect every comment token for `# noqa` (case-insensitive); if present, unconditionally append an `AuditViolation` with `metric="unauthorized_suppressions"` and message `Unauthorized '# noqa' comment suppression detected: {tok.string.strip()}`.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test verifying that `# noqa` with any reason string raises an `unauthorized_suppressions` violation.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]: Add unit test verifying that `cast(Any, x)` and `typing.cast(typing.Any, x)` raise `permissive_casts` violations.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_audit_dict_eradication.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Dict eradication audit must fail-fast on every # noqa comment and cast(Any, ...) call without exception.</constraint>
  </step>

  <step id="3" name="PROVIDER &amp; ADAPTER DTO RECONSTITUTION (THIRD-PARTY ATTRIBUTES)">
    <action>In @[backend_v2/llm/provider.py]: Identify all 27 `# noqa: QGR001` and `QGR012` suppression sites. Encapsulate third-party LiteLLM exception inspecting (`e.status_code`, `e.original_exception`, `e.response`), response metadata (`response.model_extra`, `response.usage`), and token details (`usage.prompt_tokens`, `usage.completion_tokens`) using `inspect.getattr_static` and strongly typed Pydantic V2 adapter DTOs (using `model_validate(obj, from_attributes=True)` or explicit typed helper extractors). Delete all 27 `# noqa` comment tokens.</action>
    <action>In @[backend_v2/llm/adapters/base_adapter.py]: Delete all 5 `# noqa: QGR012` suppression sites on JSON schema stripping and discriminator inspection. With `QGR012` aligned with `BOUNDARY_EXEMPTION_FILES`, verify schema normalization executes cleanly without comment tokens.</action>
    <action>In @[backend_v2/database/firestore_driver.py] and @[backend_v2/database/tinydb_driver.py]: Delete the 1 `# noqa: QGR012` comment token per file on recursive document serialization.</action>
    <action>In @[backend_v2/logging_config.py]: Delete the 1 `# noqa: QGR012` comment token on logging record details mapping normalization.</action>
    <action>Execute localized AST scan: Run `uv run python scripts/_ast_guardrails.py backend_v2/llm/provider.py backend_v2/llm/adapters/base_adapter.py backend_v2/database/tinydb_driver.py backend_v2/database/firestore_driver.py backend_v2/logging_config.py --strict` asserting 0 violations and 0 suppressions.</action>
    <constraint invariant="provider_abstraction_mandate">All third-party SDK and LiteLLM data reads must be encapsulated in typed adapter DTOs with zero suppression comments.</constraint>
  </step>

  <step id="4" name="CENSUS N (# noqa) COMMENT TOKEN ERADICATION (29 FILES)">
    <action>In @[backend_v2/main.py]: Replace `# noqa: F401` comment on line 30 with explicit side-effect consumption: `import backend_v2.hooks as _hooks; _ = _hooks`.</action>
    <action>In @[scripts/audit_epic_coverage.py] and @[scripts/audit_planner_output.py]: Remove `sys.path.insert` and hoist imports to top of file using root package path `from scripts._ast_boundary_utils import ...`, deleting all `# noqa: E402` comments.</action>
    <action>In @[scripts/audit_warning_baseline.py]: Rephrase comment on line 171 from `# Census N: # noqa comment tokens` to `# Census N: Inline suppression comment tokens`, deleting the token.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler.py] (5 comments), @[backend_v2/tests/unit/services/test_blueprint.py] (4 comments: lines 276, 364, 399, 589), @[backend_v2/tests/unit/test_executions.py] (3 comments: lines 69, 75, 121), @[backend_v2/tests/unit/test_metrics.py] (2 comments: lines 180, 211), @[backend_v2/tests/unit/test_dag_taskgroup.py] (2 comments: lines 70, 151), @[backend_v2/tests/integration/test_e2e_orchestration.py] (1 comment: line 92), @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py] (1 comment: line 152), @[backend_v2/tests/unit/test_web_fetcher.py] (1 comment: line 61), @[backend_v2/tests/unit/test_xai_extensions.py] (1 comment: line 83), and @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py] (1 comment: line 33): Break long lines cleanly across multiple lines or parentheses, and delete all `# noqa: E501` comments.</action>
    <action>In @[backend_v2/tests/conftest.py] (2 comments: lines 13, 14), @[backend_v2/tests/unit/test_bug_synthesis_hook.py] (2 comments: lines 3, 4), @[backend_v2/tests/unit/services/test_matrix_domain_parser.py] (1 comment: line 26), @[backend_v2/tests/unit/services/test_output_profile_studio_parity.py] (1 comment: line 5), @[backend_v2/tests/unit/services/sdui/adapters/test_matrix_graphs_adapter.py] (1 comment: line 3), @[backend_v2/tests/unit/services/sdui/adapters/test_matrix_summary_table_adapter.py] (1 comment: line 3), @[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_init.py] (1 comment: line 6), and @[backend_v2/tests/unit/test_v2_core_models.py] (1 comment: line 9): Remove unused imports or register fixture exports explicitly via `__all__` or `_ = import_symbol`, and delete all `# noqa: F401` comments.</action>
    <action>In @[backend_v2/tests/unit/services/test_blueprint.py] (1 comment: line 17): Replace star import `from backend_v2.models.view.sdui import *` with explicit named symbol imports, and delete `# noqa: F403, F401`.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py] (1 comment: line 14) and @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py] (1 comment: line 45): Hoist imports to module top level and delete `# noqa: E402` comments.</action>
    <action>Execute live Census N audit: Verify that tokenize search finds exactly 0 `# noqa` comment tokens across `backend_v2` and `scripts`.</action>
    <constraint invariant="the_zero_compromise_pledge">Absolute zero # noqa comment tokens across backend_v2 and scripts.</constraint>
  </step>

  <step id="5" name="CENSUS X (cast(Any, ...)) ERADICATION (5 FILES + BASELINE LEDGER CLEANUP)">
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py]: At line 969, replace `exec_record = cast(Any, exec_record_raw)` with `exec_record = exec_record_raw` and check `if exec_record is not None and step.id in exec_record.step_states:` directly under typed `ExecutionRecord` semantics. Delete `cast` from module imports at line 15.</action>
    <action>In @[backend_v2/tests/integration/test_caching_integration.py]: At lines 35 to 37, replace `sys.modules[...] = cast(Any, ...)` with typed `types.ModuleType` assignments (specifically: `mod = types.ModuleType("vertexai"); mod.preview = MockPreview; sys.modules["vertexai"] = mod`). Delete `cast` and `Any` imports from module top level.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]: At lines 41 to 43, replace `sys.modules[...] = cast(Any, ...)` with typed `types.ModuleType` assignments. Delete `cast` and `Any` imports.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]: At lines 57, 59, 60, replace `sys.modules[...] = cast(Any, ...)` with typed `types.ModuleType` assignments. Delete `cast` and `Any` imports.</action>
    <action>In @[backend_v2/tests/unit/test_context_mapper.py]: At line 22, replace `all_blocks=cast(Any, [{"id": "blk_1"}])` with raw typed collection `raw_blocks: list[Any] = [{"id": "blk_1"}]` passed to `all_blocks` without `cast`. Delete `cast` from module imports.</action>
    <action>In @[scripts/audit_warning_baseline.py]: Rephrase line 59 from `description="Census X: cast(Any, ...) ceiling."` to `description="Census X: Permissive typing cast to Any call ceiling."` and line 127 from `# Census X: cast(Any, ...)` to `# Census X: permissive cast to Any`, eliminating self-referential regex matches.</action>
    <action>Execute live Census X audit: Verify that regex search for `cast(\s*Any\b` returns exactly 0 occurrences across `backend_v2` and `scripts`.</action>
    <constraint invariant="the_zero_compromise_pledge">Absolute zero cast(Any, ...) calls across backend_v2 and scripts.</constraint>
  </step>

  <step id="6" name="MONOTONIC RATCHET UPDATE &amp; UNIVERSAL TWO-STAGE VERIFICATION GATE">
    <action>In @[scripts/audit_warning_baseline.py]: In `CURRENT_RESIDUAL_CEILINGS` (lines 69 to 80), update `n=0` (from 73) and `x=0` (from 13), locking Census N and Census X ceilings at absolute zero.</action>
    <action>Execute warning baseline audit: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and verify exit code 0 with zero fatal violations and zero warnings.</action>
    <action>Execute dict eradication audit: Run `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` and verify `TOTAL VIOLATIONS: 0`.</action>
    <action>Execute AST guardrails audit: Run `uv run python scripts/_ast_guardrails.py backend_v2/ --strict` and verify zero unsuppressed violations.</action>
    <action>Execute universal backend audit loop: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` and verify all 10 stages pass cleanly.</action>
    <action>Execute planner output audit: Run `uv run python scripts/audit_planner_output.py --epic docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md --plan-dir docs/epic/tasks_EPIC_157/`.</action>
    <constraint invariant="universal_fail_fast">Phase 9 completes only when all 10 stages of the universal backend audit pass cleanly with Census N=0 and Census X=0.</constraint>
  </step>

  <demolish>
    `CommentSuppressor`
  </demolish>

  <dod_checklist>
    <item>CommentSuppressor class and is_suppressed field removed from scripts/_ast_guardrails.py.</item>
    <item>Stage 4 of scripts/backend_audit_loop.py inspects raw violations without is_suppressed filtering.</item>
    <item>1-hop callers scripts/audit_matrix_manager.py and scripts/audit_markdown_boundaries.py aligned with is_suppressed removal.</item>
    <item>Test fixtures in test_ast_guardrails.py, test_backend_audit_loop.py, test_audit_warning_baseline.py, and test_audit_matrix_manager.py aligned with is_suppressed removal.</item>
    <item>scripts/audit_dict_eradication.py rejects all # noqa comment tokens at FATAL severity.</item>
    <item>scripts/audit_dict_eradication.py detects all cast(Any, ...) calls as Metric 12 permissive_casts at FATAL severity.</item>
    <item>Third-party attributes in backend_v2/llm/provider.py and base_adapter.py reconstituted via inspect.getattr_static and typed adapter DTOs.</item>
    <item>backend_v2/services/orchestrator/strategies/llm.py line 969 cast(Any, exec_record_raw) eradicated.</item>
    <item>Census N returns exactly 0 matches across backend_v2 and scripts.</item>
    <item>Census X returns exactly 0 matches across backend_v2 and scripts.</item>
    <item>scripts/audit_warning_baseline.py ratchets n=0 and x=0 with --verify-zero passing.</item>
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
    <anti_target>Do NOT eradicate # type: ignore comments during Phase 9 (quarantined strictly for Phase 10).</anti_target>
    <anti_target>Do NOT expand dict eradication to test files during Phase 9 (quarantined strictly for Phase 11).</anti_target>
    <anti_target>Do NOT mutate client_app_v2 Flutter execution models during Phase 9 (quarantined strictly for Phase 12).</anti_target>
    <anti_target>Do NOT alter repository persistence interfaces or database drivers during Phase 9 (completed in Phases 4-7).</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Live Census N Audit: `uv run python -c "import io, tokenize, pathlib; root = pathlib.Path('.'); total = sum(sum(1 for tok in tokenize.tokenize(io.BytesIO(p.read_bytes()).readline) if tok.type == tokenize.COMMENT and '# noqa' in tok.string.lower()) for d in ['backend_v2', 'scripts'] for p in (root / d).rglob('*.py')); assert total == 0, f'Census N residual: {total}'"`</action>
    <action>Execute Live Census X Audit: `uv run python -c "import re, pathlib; root = pathlib.Path('.'); total = sum(len(re.findall(r'cast\(\s*Any\b', p.read_text(encoding='utf-8', errors='ignore'))) for d in ['backend_v2', 'scripts'] for p in (root / d).rglob('*.py')); assert total == 0, f'Census X residual: {total}'"`</action>
    <action>Execute Dict Audit: `uv run python scripts/audit_dict_eradication.py backend_v2 --strict` reports TOTAL VIOLATIONS: 0.</action>
    <action>Execute Baseline Verification: `uv run python scripts/audit_warning_baseline.py --verify-zero` reports 0 fatal violations and 0 warnings.</action>
    <action>Execute 10-Stage Universal Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```

