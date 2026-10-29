<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: AST & Quality Gate Extensions (`QGR031` Query Filter Guard, Dynamic `scripts/*.py` Discovery & `QGR032` Polyfactory Invariant Guard)

## 1. Objective & Architectural Background

Following the completion of Hardening Waves 2–4 and the Universal `PrefixedUUID7` Cutover (Step 3.3), Quorum locks the codebase's static AST and quality-gate invariants via the three architectural extensions defined in `@[docs/arkkitehtuurin_parannuskohteet.md#L196-L202]` Chapter 3:

1. **AST Guardrail `QGR031` — Static Query Filter Validation (`@[scripts/_ast_guardrails.py#L874-L1440]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]`):**
   - `Filter(field, operator, value)` in `@[backend_v2/database/driver.py]` validates `field` and `operator` at runtime (`_VALID_OPERATORS = {"==", "!=", "<", "<=", ">", ">=", "in", "array-contains"}`).
   - `QGR031` enforces query-filter discipline statically at AST time inside `QuorumGuardrailVisitor.visit_Call` (`@[scripts/_ast_guardrails.py#L874-L1440]`):
     - Rejects `Filter(...)` or `QueryCondition(...)` calls with an empty or whitespace-only string literal `field` (`""`, `"   "`).
     - Rejects invalid operator string literals outside `{"==", "!=", "<", "<=", ">", ">=", "in", "array-contains"}` (specifically catching SQL/ORM drift operators `"="`, `"eq"`, `"LIKE"`, `"ILIKE"`, `"NEQ"`, `"IN"`).
     - Rejects `Filter(..., operator="in", value="...")` when `value` is a string literal (`ast.Constant(value=str)`), preventing accidental character-iteration bugs when an `"in"` filter requires a collection (`list`, `tuple`, `set`, `frozenset`).
2. **Dynamic `scripts/*.py` Auto-Discovery in the Macro Quality Gate (`@[scripts/backend_audit_loop.py#L430-L690]`):**
   - Currently, `@[scripts/backend_audit_loop.py#L430-L690]` relies on a static `_MACRO_AUTHORITATIVE_SCRIPTS` tuple of 24 scripts, leaving newly created or auxiliary scripts in `scripts/*.py` outside the automatic macro gate unless manually registered.
   - Replace the hardcoded `_MACRO_AUTHORITATIVE_SCRIPTS` tuple with a deterministic dynamic discovery helper `discover_authoritative_scripts() -> tuple[str, ...]` using `sorted(p.as_posix() for p in Path("scripts").glob("*.py") if p.is_file())`, ensuring 100% of `scripts/*.py` files are automatically linted by Ruff, type-checked by `mypy --strict`, and audited by `scripts/_ast_guardrails.py` during the macro completion gate.
3. **AST Guardrail `QGR032` — Polyfactory 32-Hex `UUIDv7` Invariant Guard & Meta-Test Suite (`@[scripts/_ast_guardrails.py#L1566-L1708]`, `@[backend_v2/tests/factories/model_factories.py#L107-L188]`, `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]`):**
   - Add `QGR032` in `QuorumGuardrailVisitor.visit_ClassDef` (`@[scripts/_ast_guardrails.py#L1566-L1708]`) to statically verify every `ModelFactory` subclass in `backend_v2/tests/factories/model_factories.py`:
     - Any attribute assignment on a `ModelFactory` subclass targeting `id` or ending with `_id` (when non-`None`) MUST be routed through `Use(generate_opaque_id, EntityPrefix.<MEMBER>)` or a factory `@classmethod` helper delegating to `generate_opaque_id`, and MUST NEVER assign a hardcoded string literal or `uuid.uuid4()` expression.
   - Expand `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]` (`test_polyfactory_build_succeeds`) to introspect `backend_v2.tests.factories.model_factories` dynamically (verifying that `ALL_FACTORIES` covers 100% of `ModelFactory` subclasses defined in `model_factories.py`) and assert that every `id` and `*_id` string field on every `.build()` instance matches the 32-hex `OPAQUE_STRIPE_ID_REGEX` (`r"^([a-z]{2,5})_[a-fA-F0-9]{32}$"`).

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[docs/arkkitehtuurin_parannuskohteet.md#L196-L202]`
- `@[backend_v2/database/driver.py]`
- `@[backend_v2/models/core_base.py]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1: AST Guardrail `QGR031` (Static Query Filter Validation)**<br>`[MODIFY] @[scripts/_ast_guardrails.py#L614-L2907]`<br>`[MODIFY] @[scripts/_ast_guardrails.py#L874-L1440]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]` | Runtime-only discovery of malformed `Filter` / `QueryCondition` operators (`"eq"`, `"LIKE"`, `"="`), empty field names (`""`), or string literal values passed to `"in"` filters. | Enforce `QGR031` (FATAL) in `QuorumGuardrailVisitor.visit_Call` across all `Filter(...)` and `QueryCondition(...)` AST call nodes, validating non-empty `field`, valid `Operator` literals (`"=="`, `"!="`, `"<"`, `"<="`, `">"`, `">="`, `"in"`, `"array-contains"`), and non-string collection values for `"in"` filters. | Zero external SQL parser dependencies: pure stdlib `ast.Call` positional and keyword argument inspection inside `QuorumGuardrailVisitor`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict` |
| **Phase 2: Dynamic `scripts/*.py` Discovery in `backend_audit_loop.py`**<br>`[MODIFY] @[scripts/backend_audit_loop.py#L430-L690]` | Hardcoded `_MACRO_AUTHORITATIVE_SCRIPTS` tuple in `scripts/backend_audit_loop.py` that can silently omit newly added scripts in `scripts/*.py` from Ruff, MyPy, and AST Guardrail checks. | Replace static script list with `discover_authoritative_scripts()` scanning `sorted(p.as_posix() for p in Path("scripts").glob("*.py") if p.is_file())` and ensure every script in `scripts/*.py` passes strict Ruff, MyPy, and AST guardrails. | Pruned manual maintenance of `_MACRO_AUTHORITATIVE_SCRIPTS`; filesystem `Path("scripts").glob("*.py")` is the single source of truth. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --test --ast-strict` |
| **Phase 3: AST Guardrail `QGR032` (Polyfactory 32-Hex `UUIDv7` Invariant Guard)**<br>`[MODIFY] @[scripts/_ast_guardrails.py#L1566-L1708]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L107-L188]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L191-L256]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L259-L365]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L368-L460]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L463-L495]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L498-L633]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L636-L700]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L739-L768]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L771-L809]`<br>`[MODIFY] @[backend_v2/tests/factories/model_factories.py#L812-L897]`<br>`[MODIFY] @[backend_v2/tests/factories/test_model_factories.py#L71-L90]`<br>`[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]` | Risk of new `ModelFactory` classes omitting `Use(generate_opaque_id, EntityPrefix.<TYPE>)` on `id` or `*_id` fields or omitting a newly created factory from `ALL_FACTORIES` in `test_model_factories.py`. | Enforce `QGR032` (FATAL) in `QuorumGuardrailVisitor.visit_ClassDef` verifying that all `ModelFactory` subclasses route `id` and `*_id` fields through `Use(generate_opaque_id, EntityPrefix.<TYPE>)`, and assert 100% factory registry completeness and 32-hex `OPAQUE_STRIPE_ID_REGEX` compliance in `test_model_factories.py`. | Zero runtime reflection overhead in production code: static AST verification in `scripts/_ast_guardrails.py` paired with hermetic unit tests in `test_model_factories.py`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/factories/model_factories.py backend_v2/tests/factories/test_model_factories.py scripts/_ast_guardrails.py --test --ast-strict` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

1. **`scripts/audit_technical_debt.py` Baseline Verification:**
   - Pre-flight execution of `scripts/audit_technical_debt.py` across `scripts/_ast_guardrails.py`, `scripts/backend_audit_loop.py`, `backend_v2/tests/factories/model_factories.py`, `backend_v2/tests/factories/test_model_factories.py`, and `backend_v2/tests/unit/scripts/test_ast_guardrails.py` passed with `0` technical debt findings (`Status: PASSED`).
2. **Elimination of Hardcoded `_MACRO_AUTHORITATIVE_SCRIPTS` Tuple in `@[scripts/backend_audit_loop.py#L430-L690]`:**
   - Remove the manual 24-element `_MACRO_AUTHORITATIVE_SCRIPTS` tuple so `scripts/backend_audit_loop.py` dynamically discovers all `scripts/*.py` files.

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: AST Guardrail QGR031 (Static Query Filter Validation)">
    <targets>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L614-L2907]</target>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L874-L1440]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]</target>
    </targets>
    <constraint invariant="ast_guardrail_mandate">
      Enforce architectural query filter rules statically via the Python ast module before unit tests execute.
    </constraint>
    <constraint invariant="anti_happy_path_mandate">
      Write positive and at least 2 negative unit tests in test_ast_guardrails.py covering invalid operators, empty fields, and string literal 'in' filter values.
    </constraint>
    <action>
      1. In `@[scripts/_ast_guardrails.py#L614-L2907]` and `@[scripts/_ast_guardrails.py#L874-L1440]` (`QuorumGuardrailVisitor.visit_Call`), implement rule `QGR031` (`GuardrailSeverity.FATAL`) inspecting every call to `Filter(...)` or `QueryCondition(...)`:
         - Extract `field` (positional arg `0` or keyword `field`), `operator` (positional arg `1` or keyword `operator`), and `value` (positional arg `2` or keyword `value`).
         - If `field` is an `ast.Constant` with a `str` value that is empty or whitespace-only (`not field_node.value.strip()`), record a `QGR031` fatal violation.
         - If `operator` is an `ast.Constant` with a `str` value not in `{"==", "!=", "<", "<=", ">", ">=", "in", "array-contains"}` (or is neither a valid literal nor a `FilterOperator` enum attribute), record a `QGR031` fatal violation.
         - If `operator` resolves to `"in"` and `value` is an `ast.Constant` with a `str` or `bytes` value, record a `QGR031` fatal violation preventing accidental character-wise iteration.
      2. In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]`, add positive unit tests (`Filter("organization_id", "==", org_id)`, `Filter("id", "in", [id_1, id_2])`) and negative unit tests (`Filter("", "==", val)`, `Filter("id", "LIKE", "%x%")`, `Filter("id", "=", val)`, `Filter("id", "in", "wf_0195f3a0000070008000000000000001")`) asserting `QGR031`.
    </action>
  </step>

  <step id="2" name="Phase 2: Dynamic scripts/*.py Auto-Discovery in backend_audit_loop.py">
    <targets>
      <target>[MODIFY] @[scripts/backend_audit_loop.py#L430-L690]</target>
    </targets>
    <constraint invariant="universal_ssot_and_normalization_mandate">
      Eliminate secondary shadow script lists; derive the authoritative scripts collection directly from Path('scripts').glob('*.py').
    </constraint>
    <action>
      1. In `@[scripts/backend_audit_loop.py#L430-L690]`, replace the static `_MACRO_AUTHORITATIVE_SCRIPTS` tuple with `discover_authoritative_scripts(scripts_dir: Path = Path("scripts")) -> tuple[str, ...]` returning `tuple(sorted(p.as_posix() for p in scripts_dir.glob("*.py") if p.is_file()))` and export `discover_authoritative_scripts` in `__all__`.
      2. In `@[scripts/backend_audit_loop.py#L430-L690]` (`main`), call `discover_authoritative_scripts()` when `is_macro_backend_gate` is `True` so every Python script in `scripts/*.py` is included in `stage_targets` for Ruff linting, Ruff formatting, `mypy --strict`, and `scan_files_for_guardrails`.
      3. Run `scan_files_for_guardrails` and `mypy --strict` across all discovered `scripts/*.py` files and resolve any latent formatting, typing, or guardrail discrepancies in `scripts/*.py` so the full dynamic scan passes with 0 warnings and 0 errors.
    </action>
  </step>

  <step id="3" name="Phase 3: AST Guardrail QGR032 (Polyfactory 32-Hex UUIDv7 Invariant Guard &amp; Meta-Tests)">
    <targets>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L1566-L1708]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L107-L188]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L191-L256]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L259-L365]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L368-L460]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L463-L495]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L498-L633]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L636-L700]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L739-L768]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L771-L809]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/model_factories.py#L812-L897]</target>
      <target>[MODIFY] @[backend_v2/tests/factories/test_model_factories.py#L71-L90]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]</target>
    </targets>
    <constraint invariant="hermetic_test_fixtures_mandate">
      All Polyfactory ModelFactory classes MUST generate canonical 32-hex hexadecimal Opaque Stripe IDs via generate_opaque_id(EntityPrefix.&lt;TYPE&gt;).
    </constraint>
    <action>
      1. In `@[scripts/_ast_guardrails.py#L1566-L1708]` (`QuorumGuardrailVisitor.visit_ClassDef`), implement rule `QGR032` (`GuardrailSeverity.FATAL`) inspecting classes that inherit from `ModelFactory` (`ModelFactory[...]`):
         - Verify that any class-body attribute assignment targeting `id` or a field ending in `_id` (unless assigned `None`) uses `Use(generate_opaque_id, EntityPrefix.<MEMBER>)` (or `Use(<cls>._build_...)` where the helper delegates to `generate_opaque_id`), and forbid raw string literals (`ast.Constant(value=str)`), `uuid.uuid4()`, or `lambda` expressions returning static strings.
      2. Audit `WorkflowFactory` (`@[backend_v2/tests/factories/model_factories.py#L107-L188]`), `SystemRulePromptBlockFactory` (`@[backend_v2/tests/factories/model_factories.py#L191-L256]`), `OutputProfileFactory` (`@[backend_v2/tests/factories/model_factories.py#L259-L365]`), `MatrixPromptBlockFactory` (`@[backend_v2/tests/factories/model_factories.py#L368-L460]`), `ExecutionStepFactory` (`@[backend_v2/tests/factories/model_factories.py#L463-L495]`), `ExecutionRecordFactory` (`@[backend_v2/tests/factories/model_factories.py#L498-L633]`), `ReportArtifactFactory` (`@[backend_v2/tests/factories/model_factories.py#L636-L700]`), `GlobalContextVarsDTOFactory` (`@[backend_v2/tests/factories/model_factories.py#L739-L768]`), `CausalNodeDTOFactory` (`@[backend_v2/tests/factories/model_factories.py#L771-L809]`), and `CausalGraphPayloadDTOFactory` (`@[backend_v2/tests/factories/model_factories.py#L812-L897]`) against `QGR032` and ensure every factory class produces 32-hex RFC 9562 `UUIDv7` identifiers.
      3. Expand `@[backend_v2/tests/factories/test_model_factories.py#L71-L90]` (`test_polyfactory_build_succeeds`) to:
         - Dynamically verify that every `ModelFactory` subclass in `backend_v2.tests.factories.model_factories` is registered in `ALL_FACTORIES`.
         - Recursively inspect every string field named `id` or ending with `_id` (and list items in `*_ids` fields) in `instance.model_dump()` and assert `re.match(OPAQUE_STRIPE_ID_REGEX, val) is not None`.
      4. Add positive and negative unit tests for `QGR032` in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2470-L2479]`.
    </action>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — Valid `Filter` Calls, Dynamic `scripts/*.py` Discovery & Valid `ModelFactory` Definitions):**
  - `Filter("organization_id", "==", org_id)` and `Filter("id", "in", [id_1, id_2])` pass `QGR031` with zero violations.
  - `discover_authoritative_scripts()` returns all `scripts/*.py` files in sorted POSIX order.
  - A `ModelFactory[Workflow]` routing `id = Use(generate_opaque_id, EntityPrefix.WORKFLOW)` passes `QGR032`, and `test_polyfactory_build_succeeds` passes for all registered factories.
- **Scenario 2 (Negative Path 1 — Invalid `Filter` Operator, Empty Field & String Literal `"in"` Target):**
  - `Filter("", "==", "val")`, `Filter("id", "LIKE", "%x%")`, `Filter("id", "eq", "val")`, and `Filter("id", "in", "wf_0195f3a0000070008000000000000001")` each trigger a fatal `QGR031` violation in `scan_code_for_guardrails`.
- **Scenario 3 (Negative Path 2 — Polyfactory Hardcoded ID or `uuid4` Violation under `QGR032`):**
  - A `ModelFactory` subclass assigning `id = "wf_0195f3a0000070008000000000000001"`, `organization_id = Use( lambda: f"org_{uuid.uuid4().hex[:16]}" )`, or `workflow_id = "wf_123"` triggers a fatal `QGR032` violation in `scan_code_for_guardrails`.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
