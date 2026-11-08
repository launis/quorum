<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# EPIC 163 - Phase 7: Non-Residual Static Guardrail Modernization (`DGR013`, `DGR014`, `QGR013`, `QGR033` Check 33B) & Tier 2 Hardening Rules Synchronization

## 1. Executive Summary & Architectural Directives

Following the eradication of all 10 transitional `RESIDUAL_*` exemption ledgers across Phases 1–6, Phase 7 closes the remaining non-residual static guardrail enforcement gaps between `.agents/rules/` and `scripts/` before the `Post-Implementation Gates (Tier 2 Hardening)` stage executes:

1. **Pre-Implementation Docstring & Test Fixture Cleanups (`Step 7.1`)**: Add a PEP 257 Google-style docstring (`Args:` and `Returns:`) to `ValidationHookPayloadDTO.model_validate` in `@[backend_v2/models/domain/validation.py#L34-L85]` (the single undocumented public classmethod in `backend_v2/`) and migrate `test_dgr010_guarded_async_value_allowed` in `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L737-L751]` from `state.when(...)` to a Dart 3 `switch (state)` expression.
2. **Dart 3.11+ Freezed Switch (`DGR013`) & Riverpod 3.1 (`DGR014`) Guardrails (`Step 7.2`)**: Enforce `freezed_when_ban` (`DGR013`), `manual_riverpod_providers` (`DGR014` Check 14A), and `riverpod_read_vs_watch_ban` (`DGR014` Check 14B) at `GuardrailSeverity.FATAL` in `@[scripts/_dart_guardrails.py#L764-L857]` via dedicated helpers with McCabe complexity $\le 10$.
3. **Python 3.14 PEP 695 `TypeAlias` (`QGR013`) & Public Function / Module Docstring Ordering (`QGR033` Check 33B) Guardrails (`Step 7.3`)**: Extend `QGR013` in `@[scripts/_ast_guardrails.py#L1175-L1221]` to reject legacy PEP 613 `from typing import TypeAlias` imports and `: TypeAlias = ...` annotations in favor of PEP 695 `type Alias = ...`, extend `QGR033` Check 33B (`@[scripts/_ast_guardrails.py#L2716-L2760]`) to require PEP 257 docstrings on top-level public functions and public class methods (`_function_depth == 0`, non-`Protocol` ellipsis stubs), and explicitly diagnose misplaced module docstrings appearing after `from __future__ import annotations`.
4. **Tier 2 Hardening Skills, Phase 1 Learnings & `auto_hardening_runner.py` `.agents/rules/` Enforcement (`Step 7.4`)**: Synchronize `@[.agents/skills/tier2-hardening-backend/SKILL.md#L72-L136]`, `@[.agents/skills/tier2-hardening-frontend/SKILL.md#L66-L130]`, and `@[scripts/auto_hardening_runner.py#L637-L665]` so every interactive and headless Tier 2 hardening subagent pass receives domain-scoped `.agents/rules/` directives (`resolve_target_rule_files`), enforces `QGR013`, `QGR030`, `QGR033`, `DGR013`, and `DGR014` alongside Phase 1 learnings, decomposes `execute_subagent_pass` to McCabe complexity $\le 10$, and invalidates SHA-256 hardening cache entries (`compute_rules_sha256` at `@[scripts/auto_hardening_runner.py#L637-L665]`) whenever `AGENTS.md` or Tier 2 hardening `SKILL.md` playbooks change.

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/domain/validation.py#L34-L85]`, `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L737-L751]` | Undocumented public classmethod `ValidationHookPayloadDTO.model_validate` and legacy `state.when(...)` snippet in `test_dgr010_guarded_async_value_allowed`. | Add PEP 257 Google-style docstring (`Args:` and `Returns:`) to `ValidationHookPayloadDTO.model_validate` and migrate `test_dgr010_guarded_async_value_allowed` to Dart 3 `switch (state)`. | Zero runtime logic changes to `ValidationHookPayloadDTO.model_validate`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/validation.py backend_v2/tests/unit/scripts/test_dart_guardrails.py --test --ast-strict` |
| `@[scripts/_dart_guardrails.py#L764-L857]`, `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L849-L860]` | Unenforced Freezed `.when()` / `.maybeWhen()` / `.maybeMap()` / `.map(data: ...)` usage and unenforced manual Riverpod providers or `ref.read` in `build()` / `ref.watch` in callbacks. | Add `DGR013` (`freezed_when_ban`) and `DGR014` (`manual_riverpod_providers` & `riverpod_read_vs_watch_ban`) in dedicated `_check_freezed_and_riverpod_rules` and `_check_dgr014_build_method_body` helpers invoked from `scan_dart_source` at `GuardrailSeverity.FATAL`. | Enforce Phase 1 `C901 <= 10` decomposition standard on all new helpers with zero `per-file-ignores`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_dart_guardrails.py backend_v2/tests/unit/scripts/test_dart_guardrails.py --test --ast-strict` |
| `@[scripts/_ast_guardrails.py#L3267-L3285]`, `@[scripts/_ast_guardrails.py#L3267-L3285]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2809-L2832]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2983-L3007]` | Legacy PEP 613 `TypeAlias` imports/annotations unguarded by `QGR013`, public domain functions/methods unguarded by `QGR033` Check 33B, and `from __future__ import annotations` preceding module docstrings not explicitly diagnosed in `QGR033` Check 33B. | Extend `QGR013` via `_check_qgr013_import_from` and `_check_qgr013_ann_assign` to reject `TypeAlias`, extend `QGR033` Check 33B in `_check_qgr033_function_contracts` to require PEP 257 docstrings on public domain functions/methods (`_function_depth == 0`, non-`Protocol` ellipsis stubs), and diagnose misplaced module docstrings after `from __future__ import annotations` in `visit_Module`. | Preserve zero `RESIDUAL_*` sets in `@[scripts/_ast_guardrails.py]` and keep all new helpers at `C901 <= 10`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict` |
| `@[.agents/skills/tier2-hardening-backend/SKILL.md#L72-L136]`, `@[.agents/skills/tier2-hardening-frontend/SKILL.md#L66-L130]`, `@[scripts/auto_hardening_runner.py#L1350-L1400]`, `@[scripts/auto_hardening_runner.py#L1350-L1400]`, `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1202-L1316]` | Subagent prompt in `execute_subagent_pass` (`C901 = 15`) omitting explicit target-scoped `.agents/rules/` enforcement directives, `compute_rules_sha256` omitting `AGENTS.md` and `.agents/skills/tier2-hardening-*/SKILL.md`, and `SKILL.md` playbooks missing `QGR013`/`QGR030`/`QGR033`/`DGR013`/`DGR014` and Phase 1 learnings. | Add `resolve_target_rule_files(target_file: str) -> tuple[str, ...]`, decompose `execute_subagent_pass` (`<= 10` `C901` complexity) via `_run_subagent_auto_fix_prepass` and `_inject_subagent_context_rules`, extend `compute_rules_sha256` to hash `AGENTS.md` and Tier 2 hardening `SKILL.md` playbooks, and synchronize both Tier 2 hardening `SKILL.md` files. | Pure deterministic path-prefix resolution with `C901 <= 10` per helper and full compatibility with hermetic `tmp_path` cache tests. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py --test --ast-strict` |

---

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that all 6 preceding phases of `@[docs/epic/EPIC_163_tracker.md]` are complete, that zero `RESIDUAL_*` exemption sets exist in `@[scripts/_ast_guardrails.py]`, and that `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS = frozenset()` in `@[scripts/audit_dict_eradication.py#L99-L113]` remains locked.</action>
  </step>

  <dod_checklist>
    <item>`ValidationHookPayloadDTO.model_validate` in `@[backend_v2/models/domain/validation.py#L34-L85]` has a complete PEP 257 Google-style docstring (`Args:` and `Returns:`), and `test_dgr010_guarded_async_value_allowed` in `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L737-L751]` uses a Dart 3 `switch (state)` expression.</item>
    <item>`DGR013` (`freezed_when_ban`) and `DGR014` (`manual_riverpod_providers` &amp; `riverpod_read_vs_watch_ban`) are enforced at `GuardrailSeverity.FATAL` in `@[scripts/_dart_guardrails.py#L764-L857]`, and `uv run python scripts/_dart_guardrails.py client_app_v2/lib --strict` exits with code 0.</item>
    <item>`QGR013` (banning legacy PEP 613 `TypeAlias` imports and annotations) and `QGR033` Check 33B (requiring PEP 257 docstrings on top-level public functions and public class methods and diagnosing misplaced module docstrings after `from __future__ import annotations`) are enforced at `GuardrailSeverity.FATAL` in `@[scripts/_ast_guardrails.py#L1175-L1221]` and `@[scripts/_ast_guardrails.py#L2716-L2760]` with zero `RESIDUAL_*` exemptions.</item>
    <item>`@[.agents/skills/tier2-hardening-backend/SKILL.md#L72-L136]`, `@[.agents/skills/tier2-hardening-frontend/SKILL.md#L66-L130]`, and `@[scripts/auto_hardening_runner.py#L637-L665]` enforce target-scoped `.agents/rules/` loading (`resolve_target_rule_files`), `execute_subagent_pass` achieves McCabe complexity $\le 10$, `compute_rules_sha256` (`@[scripts/auto_hardening_runner.py#L637-L665]`) hashes `AGENTS.md` and Tier 2 hardening `SKILL.md` playbooks, and `uv run python scripts/audit_skills_architecture.py` exits with code 0.</item>
  </dod_checklist>

  <anti_targets>
    <file>@[backend_v2/seed/seed_data.json]</file>
    <file>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</file>
    <file>@[pyproject.toml]</file>
  </anti_targets>

  <touched_artifacts>
    <file>@[backend_v2/models/domain/validation.py]</file>
    <file>@[scripts/_dart_guardrails.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]</file>
    <file>@[scripts/_ast_guardrails.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</file>
    <file>@[.agents/skills/tier2-hardening-backend/SKILL.md]</file>
    <file>@[.agents/skills/tier2-hardening-frontend/SKILL.md]</file>
    <file>@[scripts/auto_hardening_runner.py]</file>
    <file>@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</file>
  </touched_artifacts>

  <step id="7.1" name="Pre-Implementation Docstring (ValidationHookPayloadDTO.model_validate) &amp; Dart Test Fixture (test_dgr010_guarded_async_value_allowed) Cleanups">
    <context>
      `ValidationHookPayloadDTO.model_validate` in `@[backend_v2/models/domain/validation.py#L34-L85]` is the single public classmethod in `backend_v2/` without a PEP 257 docstring, and `test_dgr010_guarded_async_value_allowed` in `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L737-L751]` uses legacy `state.when(...)` syntax.
    </context>
    <demolish>
      Remove the undocumented method header on `ValidationHookPayloadDTO.model_validate` and remove the `state.when(...)` call in `test_dgr010_guarded_async_value_allowed`.
    </demolish>
    <action>
      1. `[MODIFY]` `@[backend_v2/models/domain/validation.py#L34-L85]`: Add a PEP 257 Google-style docstring with `Args:` and `Returns:` sections to `ValidationHookPayloadDTO.model_validate`.
      2. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L737-L751]`: Replace `state.when(...)` in `test_dgr010_guarded_async_value_allowed` with a Dart 3 `switch (state)` expression matching `AsyncData(:final value)`, `AsyncLoading()`, and `AsyncError(:final error)`.
    </action>
    <constraint>
      Do not alter the runtime validation logic of `ValidationHookPayloadDTO.model_validate`.
    </constraint>
    <test_contracts>
      <contract name="test_validation_hook_payload_dto_model_validate_has_pep257_docstring" category="positive">
        <input>Scan `backend_v2/models/domain/validation.py` with `scan_file_for_guardrails`.</input>
        <expected>Returns 0 `QGR001` and 0 `QGR033` violations.</expected>
      </contract>
      <contract name="test_dgr010_guarded_async_value_allowed_uses_dart3_switch" category="positive">
        <input>Execute `test_dgr010_guarded_async_value_allowed` in `test_dart_guardrails.py`.</input>
        <expected>Returns 0 `DGR010` and 0 `DGR013` violations.</expected>
      </contract>
      <contract name="test_validation_hook_payload_dto_rejects_extra_fields" category="negative">
        <input>Pass an unrecognized key to `ValidationHookPayloadDTO.model_validate`.</input>
        <expected>Raises Pydantic `ValidationError` fail-fast.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/validation.py backend_v2/tests/unit/scripts/test_dart_guardrails.py --test --ast-strict`
    </validation_gate>
  </step>

  <step id="7.2" name="Dart 3.11+ Freezed Switch (DGR013) &amp; Riverpod 3.1 (DGR014) Guardrails">
    <context>
      `@[scripts/_dart_guardrails.py#L764-L857]` currently enforces `DGR001` through `DGR012` but does not statically enforce `freezed_when_ban` (`DGR013`), `manual_riverpod_providers` (`DGR014` Check 14A), or `riverpod_read_vs_watch_ban` (`DGR014` Check 14B) from `@[.agents/rules/02_flutter_desktop.md#L31-L37]` and `@[.agents/rules/02_flutter_desktop.md#L55-L57]`.
    </context>
    <demolish>
      Eliminate the static analysis blind spot allowing Freezed `.when()` / `.maybeWhen()` / `.maybeMap()` / `.map(data: ...)`, manual `StateProvider` / `ChangeNotifier` declarations, top-level `ref.read(...)` calls in `Widget build(...)`, or `ref.watch(...)` calls inside UI event callbacks.
    </demolish>
    <action>
      1. `[MODIFY]` `@[scripts/_dart_guardrails.py#L716-L761]`: Define compiled patterns `DGR013_FREEZED_WHEN_PATTERN`, `DGR014_LEGACY_PROVIDER_PATTERN`, `DGR014_CALLBACK_REF_WATCH_PATTERN`, and `_WIDGET_BUILD_HEADER_PATTERN`; implement low-complexity (`C901 &lt;= 10`) helpers `_check_dgr014_build_method_body` and `_check_freezed_and_riverpod_rules(filepath: str, source_text: str, uncommented_text: str, *, is_test_scope: bool) -&gt; list[DartViolation]`; and wire `_check_freezed_and_riverpod_rules` into `scan_dart_source`.
      2. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L849-L860]`: Add Partition 13 unit tests covering `DGR013` positive immunity for Dart 3 `switch` and `Iterable.map((e) =&gt; ...)`, `DGR013` fatal detection of `.when(`, `.maybeWhen(`, `.maybeMap(`, and `.map(data: ...)`, `DGR014` positive immunity for `@riverpod`, `ref.watch` in `build()`, and `ref.read` inside `onPressed:` callbacks / `.notifier` / `loggerServiceProvider`, and `DGR014` fatal detection of `StateProvider` / `ChangeNotifier`, top-level `ref.read(workflowProvider)` inside `Widget build(...)`, and `ref.watch(workflowProvider)` inside `onPressed:` callbacks.
    </action>
    <constraint>
      Keep every new helper function in `@[scripts/_dart_guardrails.py]` at McCabe cyclomatic complexity $\le 10$ and ensure `Iterable.map((item) =&gt; ...)` produces zero false positives.
    </constraint>
    <test_contracts>
      <contract name="test_dgr013_allows_dart3_switch_and_iterable_map" category="positive">
        <input>Dart widget using `switch (state) { AsyncData(:final value) =&gt; ... }` and `items.map((item) =&gt; Text(item.id)).toList()`.</input>
        <expected>Returns 0 `DGR013` violations.</expected>
      </contract>
      <contract name="test_dgr013_flags_freezed_when_maybe_when_and_named_map_as_fatal" category="negative">
        <input>Non-test Dart widget invoking `state.when(...)`, `state.maybeWhen(...)`, `block.maybeMap(...)`, and `state.map(data: ...)`.</input>
        <expected>Emits 4 `DGR013` violations with `GuardrailSeverity.FATAL`.</expected>
      </contract>
      <contract name="test_dgr014_flags_legacy_providers_build_ref_read_and_callback_ref_watch" category="boundary">
        <input>Dart file declaring `StateProvider`, `ChangeNotifier`, top-level `ref.read(workflowProvider)` in `Widget build`, and `onPressed: () { ref.watch(workflowProvider); }`, alongside valid `onPressed: () =&gt; ref.read(workflowProvider.notifier).save()`.</input>
        <expected>Flags the 4 invalid usages as `GuardrailSeverity.FATAL` `DGR014` violations and permits the valid callback `ref.read`.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_dart_guardrails.py backend_v2/tests/unit/scripts/test_dart_guardrails.py --test --ast-strict; uv run --no-sync --offline python scripts/_dart_guardrails.py client_app_v2/lib --strict`
    </validation_gate>
  </step>

  <step id="7.3" name="Python 3.14 PEP 695 TypeAlias (QGR013) &amp; Public Function / Module Docstring Ordering (QGR033 Check 33B) Guardrails">
    <context>
      `QGR013` in `@[scripts/_ast_guardrails.py#L1311-L1906]` currently checks `TypeVar()` calls in `visit_Call` but does not check `from typing import TypeAlias` (`visit_ImportFrom`) or `x: TypeAlias = ...` (`visit_AnnAssign`). Furthermore, `QGR033` Check 33B (`@[scripts/_ast_guardrails.py#L1311-L1906]`) checks module and public class docstrings in `backend_v2/` but omits top-level public functions/methods (`_function_depth == 0`) and does not explicitly diagnose misplaced module docstrings placed after `from __future__ import annotations`.
    </context>
    <demolish>
      Close the `QGR013` PEP 613 `TypeAlias` loophole and the `QGR033` Check 33B public function/method and `from __future__ import annotations` module docstring ordering gaps.
    </demolish>
    <action>
      1. `[MODIFY]` `@[scripts/_ast_guardrails.py#L775-L789]` and `@[scripts/_ast_guardrails.py#L775-L789]`: Add low-complexity (`C901 &lt;= 10`) helpers `_is_type_alias_annotation(node: ast.AST) -&gt; bool`, `_is_ellipsis_stub_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -&gt; bool`, `_has_misplaced_docstring_after_future_import(node: ast.Module) -&gt; bool`, `_check_qgr013_import_from(self, node: ast.ImportFrom) -&gt; None`, and `_check_qgr013_ann_assign(self, node: ast.AnnAssign) -&gt; None`; invoke them from `visit_Module`, `visit_ImportFrom`, `visit_AnnAssign`, and `_check_qgr033_function_contracts`.
      2. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2868-L2881]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2868-L2881]`: Update `test_qgr033_missing_module_or_public_class_docstring_raises_fatal` (`L2820-L2832`) to assert all 3 `QGR033` violations (module, undocumented test class, and public method `run()`), and add unit tests verifying `QGR013` `TypeAlias` rejection vs. PEP 695 `type X = ...` acceptance, `QGR033` public function docstring enforcement vs. private `_helper` / `Protocol` ellipsis stub exemption, and `QGR033` detection when `from __future__ import annotations` precedes the module docstring on line 1.
    </action>
    <constraint>
      Do not introduce any `RESIDUAL_*` exemption sets in `@[scripts/_ast_guardrails.py]`, and keep all new AST helper methods at McCabe complexity $\le 10$.
    </constraint>
    <test_contracts>
      <contract name="test_qgr013_and_qgr033_allow_pep695_type_alias_and_documented_public_functions" category="positive">
        <input>Domain module with docstring at line 1 before `from __future__ import annotations`, `type MatrixMap = list[str]`, a documented public function, an undocumented private `_helper()`, and a `Protocol` ellipsis stub `def fetch(self) -&gt; str: ...`.</input>
        <expected>Returns 0 `QGR013` and 0 `QGR033` violations.</expected>
      </contract>
      <contract name="test_qgr013_rejects_legacy_typing_type_alias_import_and_ann_assign" category="negative">
        <input>Module containing `from typing import TypeAlias` and `MatrixMap: TypeAlias = list[str]`.</input>
        <expected>Emits 2 `GuardrailSeverity.FATAL` `QGR013` violations.</expected>
      </contract>
      <contract name="test_qgr033_flags_undocumented_public_function_and_misplaced_module_docstring" category="boundary">
        <input>Domain module starting with `from __future__ import annotations\n"""Misplaced module docstring."""` and defining an undocumented public function `def process_data() -&gt; int:`.</input>
        <expected>Emits 2 `GuardrailSeverity.FATAL` `QGR033` violations diagnosing line-1 docstring ordering and missing public function docstring.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_ast_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict; uv run --no-sync --offline python scripts/_ast_guardrails.py backend_v2 scripts --strict`
    </validation_gate>
  </step>

  <step id="7.4" name="Tier 2 Hardening Skills, Phase 1 Learnings &amp; auto_hardening_runner.py .agents/rules/ Enforcement">
    <context>
      `@[.agents/skills/tier2-hardening-backend/SKILL.md#L72-L136]`, `@[.agents/skills/tier2-hardening-frontend/SKILL.md#L66-L130]`, and `@[scripts/auto_hardening_runner.py#L1350-L1400]` govern the `Post-Implementation Gates (Tier 2 Hardening)` stage that runs immediately after Phase 7. Currently, `execute_subagent_pass` (`C901 = 15`) does not inject target-scoped `.agents/rules/` references into subagent prompts, and `compute_rules_sha256` (`@[scripts/auto_hardening_runner.py#L1350-L1400]`) hashes only `.agents/rules/*.md` without `AGENTS.md` or the Tier 2 hardening `SKILL.md` playbooks.
    </context>
    <demolish>
      Eliminate implicit rule loading in headless Tier 2 hardening subagents, decompose `execute_subagent_pass` (`C901 = 15` -&gt; $\le 10$), and eliminate stale SHA-256 hardening cache hits when `AGENTS.md` or Tier 2 hardening `SKILL.md` playbooks are updated.
    </demolish>
    <action>
      1. `[MODIFY]` `@[.agents/skills/tier2-hardening-backend/SKILL.md#L72-L136]`: Update `EVIDENCE_BASED_INSPECTION_MANDATE` Invariant 2 (`QuorumUnitOfWork` / `InMemoryUnitOfWork` and `TypedCacheService` persistence with Fail-Fast `ConfigurationError`, zero `_local_*` / `_memory_*` shadow dicts under `QGR030`), Invariant 4 (`QGR033` Check 33A &amp; Check 33B including line-1 module docstring before `from __future__ import annotations`, public class/function/method docstrings, and `QGR013` PEP 695 `[T]` generics and `type Alias = ...`), Invariant 6 (module-scoped `os.chdir` patching in multi-file `scripts/` pytest runs), and `SESSION LIMIT &amp; HANDOVER` (workspace-relative `@[...]` paths).
      2. `[MODIFY]` `@[.agents/skills/tier2-hardening-frontend/SKILL.md#L66-L130]`: Update `TWO_PROFILE_INSPECTION_MANDATE` Profile A (`L72-L73`) and Profile B (`L82`) to enforce `DGR013` (`freezed_when_ban`) and `DGR014` (`manual_riverpod_providers` &amp; `riverpod_read_vs_watch_ban`) alongside `DGR010`, `DGR011`, and `DGR012`, and update `SESSION LIMIT &amp; HANDOVER` to use workspace-relative `@[...]` paths.
      3. `[MODIFY]` `@[scripts/auto_hardening_runner.py#L637-L665]` and `@[scripts/auto_hardening_runner.py#L637-L665]`: Implement `resolve_target_rule_files(target_file: str) -&gt; tuple[str, ...]`, decompose `execute_subagent_pass` via `_run_subagent_auto_fix_prepass` and `_inject_subagent_context_rules` so its McCabe complexity is $\le 10$ while injecting domain-scoped `.agents/rules/` directives into every subagent prompt, and extend `compute_rules_sha256` to hash `AGENTS.md`, `.agents/skills/tier2-hardening-backend/SKILL.md`, and `.agents/skills/tier2-hardening-frontend/SKILL.md` alongside `.agents/rules/*.md`.
      4. `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1202-L1316]`: Add unit tests verifying `resolve_target_rule_files` across backend, seed/database, LLM/orchestrator, script, and Flutter targets, `.agents/rules/` prompt injection in `execute_subagent_pass`, and SHA-256 cache invalidation when `AGENTS.md` or Tier 2 hardening `SKILL.md` files mutate.
    </action>
    <constraint>
      Maintain McCabe complexity $\le 10$ across all modified functions in `@[scripts/auto_hardening_runner.py]` and verify `audit_skills_architecture.py` passes with 0 findings.
    </constraint>
    <test_contracts>
      <contract name="test_resolve_target_rule_files_and_subagent_prompt_injection" category="positive">
        <input>Invoke `resolve_target_rule_files` and `execute_subagent_pass` for backend, seed/database, LLM/orchestrator, script, and Flutter targets.</input>
        <expected>Injects the exact domain-scoped `.agents/rules/` references into the subagent command prompt.</expected>
      </contract>
      <contract name="test_compute_rules_sha256_invalidates_cache_on_skill_or_agents_md_mutation" category="negative">
        <input>Mutate `.agents/skills/tier2-hardening-backend/SKILL.md`, `.agents/skills/tier2-hardening-frontend/SKILL.md`, or `AGENTS.md` in a `tmp_path` repository fixture.</input>
        <expected>`compute_rules_sha256(repo_root)` produces a distinct SHA-256 digest and invalidates prior cached entries.</expected>
      </contract>
      <contract name="test_audit_skills_architecture_passes_with_updated_tier2_skills" category="boundary">
        <input>Run `scripts/audit_skills_architecture.py` across `.agents/skills/`.</input>
        <expected>Exits with code 0 and reports 0 `SKL001`–`SKL005` violations.</expected>
      </contract>
    </test_contracts>
    <validation_gate>
      `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py --test --ast-strict; uv run --no-sync --offline pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py backend_v2/tests/unit/scripts/test_flutter_audit_loop.py`
    </validation_gate>
  </step>
</execution_protocol>
```
