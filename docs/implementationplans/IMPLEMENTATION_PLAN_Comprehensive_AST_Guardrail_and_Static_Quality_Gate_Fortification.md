<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
</required_context_rules>

# Comprehensive AST Guardrail & Static Quality Gate Fortification (Python & Dart)

## Objective

Fortify Quorum's static quality gates and AST guardrail engine by eliminating critical architectural blind spots across both the Python Backend and Flutter Client:
1. Bridging syntax and type awareness by discriminating dictionary `.get()` lookups (both single-argument and two-argument) from network/storage clients, with complete exemption for 0-argument `ContextVar.get()`.
2. Eliminating type laundering and reflection bypasses via `TypeAdapter(dict[...])`, `vars()`, `__dict__`, and `operator.attrgetter`.
3. Eradicating silent exception swallowing in `except` blocks lacking explicit `raise` statements or typed Dead-Letter Queue (DLQ) dispatches.
4. Enforcing absolute zero-tolerance for `# noqa: QGR*` comment suppressions in domain code outside physical boundary files.
5. Preserving the 4-driver physical boundary exemption (`tinydb_driver.py`, `firestore_driver.py`, `provider.py`, `logging_config.py`) as permanent SSOT contracts until EPIC 151 clean-slate PostgreSQL migration.
6. Bridging the client-side surveillance vacuum by engineering `_dart_guardrails.py` for `client_app_v2` (DGR001–DGR004) with complete generated code immunity (`*.freezed.dart`, `*.g.dart`), establishing WARNING severity in baseline mode and escalating to FATAL under `--strict` to prevent premature build crashes before Phase 4 client migrations, and integrating it into `scripts/flutter_audit_loop.py`.

---

## Target Scope & File Boundaries

### Target Files (Modifications & Creations)

- `[MODIFY]` `@[scripts/_ast_guardrails.py#L1-L1126]` — Fortify QGR000, QGR001, QGR002, QGR003, and introduce QGR018 (spanning `CommentSuppressor` #L90-L161, `QuorumGuardrailVisitor` #L163-L931, `scan_source_code_for_guardrails` #L933-L1007, `scan_files_for_guardrails` #L1052-L1080, `main` #L1099-L1123) while strictly preserving the 4-driver physical boundary exemption.
- `[NEW]` `@[scripts/_dart_guardrails.py]` — Client-side static guardrail analyzer for Flutter/Dart architecture (enforcing DGR001–DGR004) with complete generated file exclusion (`*.freezed.dart`, `*.g.dart`).
- `[MODIFY]` `@[scripts/backend_audit_loop.py#L1-L371]` — Python 2 exception syntax fix (#L59-L65) and Stage 4 AST guardrail stage integration (#L303-L321).
- `[MODIFY]` `@[scripts/flutter_audit_loop.py#L1-L123]` — Reflection fix (#L41-L44), English localization (#L46-L119), relative path normalization (#L105), workspace root resolution before os.chdir (#L54-L62), and `_dart_guardrails.py` automated gate insertion (#L77-L119).
- `[MODIFY]` `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1-L1058]` — ISTQB test suite expansion for QGR000, QGR001, QGR002, QGR003, QGR018, comment suppression domain partitioning (#L470-L545), and driver exemption verification.
- `[NEW]` `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]` — Comprehensive unit test suite for Dart guardrails engine.

### Context Files (Strictly Read-Only)

- `@[scripts/audit_dict_eradication.py]`
- `@[scripts/audit_markdown_boundaries.py]`
- `@[scripts/audit_matrix_manager.py]`
- `@[backend_v2/models/enums.py]`
- `@[docs/epic/EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md]`
- `@[docs/epic/EPIC_152_audit_report.md]`

---

## Pre-Implementation Technical Debt Cleanups (Scoped Boy Scout Boundary)

Before introducing new guardrail rules or analyzer features, the following discovered technical debt items in target files must be resolved in Phase 1:

1. **Python 2 Comma Syntax Rectification in Target Scripts:**
   - In `@[scripts/_ast_guardrails.py#L40]`: Replace `except AttributeError, io.UnsupportedOperation:` with parenthesized tuple syntax `except (AttributeError, io.UnsupportedOperation):`.
   - In `@[scripts/_ast_guardrails.py#L148]`: Replace `except tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError:` with parenthesized tuple syntax `except (tokenize.TokenError, IndentationError, UnicodeDecodeError, SyntaxError):`.
   - In `@[scripts/backend_audit_loop.py#L63]`: Replace `except AttributeError, io.UnsupportedOperation:` with parenthesized tuple syntax `except (AttributeError, io.UnsupportedOperation):`.
2. **Reflection Anti-Pattern & Stderr Type Narrowing in Flutter Audit Script:**
   - In `@[scripts/flutter_audit_loop.py#L41-L44]`: Replace dynamic reflection check `if hasattr(sys.stdout, "reconfigure"):` with concrete type narrowing `if isinstance(sys.stdout, io.TextIOWrapper):`. Apply identical type narrowing for `sys.stderr` and delete `# type: ignore`.
3. **English Language & Modern Architecture Rectification in Flutter Audit Script:**
   - In `@[scripts/flutter_audit_loop.py#L46-L119]`: Translate all Finnish console strings to professional English per `english_language_mandate`.
   - In `@[scripts/flutter_audit_loop.py#L105]`: Replace hardcoded local absolute path with workspace-relative `.agents/rules` per `absolute_path_context_amnesia_ban`.
   - In `@[scripts/flutter_audit_loop.py#L118]`: Remove historical development phase reference ("Phase 9") per `documentation_present_tense_mandate`.
4. **Working Directory Resilience in Flutter Audit Script:**
   - In `@[scripts/flutter_audit_loop.py#L54-L62]`: Resolve repository root path (`root_dir = current_dir if current_dir.name != "client_app_v2" else current_dir.parent`) before `os.chdir` so that Python helper scripts in `scripts/` (including `_dart_guardrails.py`) can be invoked deterministically via `sys.executable` and `root_dir / "scripts" / "_dart_guardrails.py"`.

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[scripts/_ast_guardrails.py#L90-L161]`**<br>`CommentSuppressor`<br>(Rule QGR000) | Banned inline `# noqa: QGR*` and blanket `# noqa` comment suppressions in domain code. Banned short/placeholder reasons in non-domain code. | `CommentSuppressor` evaluates `_is_domain_code`. In domain code outside `BOUNDARY_EXEMPTION_FILES`, any QGR suppression emits FATAL `QGR000`. Non-domain test fakes require substantive reason (`len(reason) >= 10`). | Do not build complex parser AST tokens for comments; use standard `tokenize.tokenize` stream directly. | `test_qgr000_domain_suppression_fatal()`<br>Asserts exit code 1 on `# noqa: QGR001` in domain code. |
| **`@[scripts/_ast_guardrails.py#L224-L250]`**<br>`visit_Call` & `visit_Attribute`<br>(Rule QGR001) | Banned dynamic reflection bypasses: `vars()`, `.__dict__`, `operator.attrgetter`, and `attrgetter()`. Banned bypassing reflection checks in test files. | Detect `ast.Name(id="vars")`, `ast.Attribute(attr="__dict__")`, and `attrgetter` calls. Severity: `FATAL` in domain code, `WARNING` in tests (FATAL under `--strict`). | Reject speculative full dataflow taint analysis; pure AST node pattern matching via `ast.match`. | `test_qgr001_vars_dict_attrgetter()`<br>Asserts FATAL violations on `vars(u)`, `u.__dict__`, `attrgetter("id")`. |
| **`@[scripts/_ast_guardrails.py#L251-L290]`**<br>`visit_Call`<br>(Rule QGR002) | Banned 1-argument `.get(key)` and 2-argument `.get(key, default)` dictionary lookups in domain code. Banned silent defaults. | Detect `.get()` with 1 or 2 arguments. Exempt network/storage clients (`client`, `httpx`, `driver`, `environ`, `headers`, `*_MAP`) and network kwargs (`params`, `timeout`, `headers`). 0-arg `ContextVar.get()` permitted. | Do not maintain expansive string allowlists; rely on closed SSOT receiver set and keyword signature inspection. | `test_qgr002_single_and_two_arg_get()`<br>Asserts FATAL on `data.get("k")` and `data.get("k", "")`; passes `client.get(url)`. |
| **`@[scripts/_ast_guardrails.py#L483-L514]`**<br>`visit_ExceptHandler`<br>(Rule QGR003) | Banned silent exception swallowing: `except Exception:` or typed handlers returning fallback literals (`return None`, `return []`, `return {}`, `pass`, `continue`) without `raise`. | Handlers in domain code must contain an `ast.Raise` node or explicit DLQ dispatch. Severity: `FATAL` in domain code outside boundary exemptions. | Do not implement control-flow graph execution simulation; inspect AST statement nodes directly within handler body. | `test_qgr003_swallowed_exception_fatal()`<br>Asserts FATAL on `except Exception: return None`; passes on `raise AppException`. |
| **`@[scripts/_ast_guardrails.py#L415-L450]`**<br>`visit_Call`<br>(Rule QGR018) | Banned type laundering: `TypeAdapter(dict[str, Any])`, `TypeAdapter(list[dict])`, or TypeAdapter wrapping untyped dictionaries to evade typing gates. | Detect `TypeAdapter` calls where type argument is `dict`, `Dict`, `list[dict]`, or Union containing `dict`. Severity: `FATAL` in domain code. | Reject recursive generic type resolver; inspect root AST slice and union elements directly. | `test_qgr018_type_adapter_dict_laundering()`<br>Asserts FATAL on `TypeAdapter(dict[str, Any])`; passes on `TypeAdapter(UserDTO)`. |
| **`@[scripts/_ast_guardrails.py#L82-L87]`**<br>`BOUNDARY_EXEMPTION_FILES` | Banned unauthorized expansion of boundary exemptions. Banned premature deletion of driver exemptions prior to EPIC 151. | Strictly preserve the 4 physical boundary files: `{"tinydb_driver.py", "firestore_driver.py", "provider.py", "logging_config.py"}` per `ki_zero_permissive_typing.md`. | Prune speculative zero-exemption refactor until PostgreSQL driver replaces TinyDB in EPIC 151. | `test_boundary_exemption_files_contract()`<br>Asserts exactly the 4 canonical boundary files are exempt. |
| **`@[scripts/_dart_guardrails.py]`**<br>(Rules DGR001–DGR004) | Banned loose Map returns in API clients (`Future<Map<String, dynamic>>`), `SizedBox.shrink()` concealment, hardcoded `Text("...")`, and unauthorized `// ignore:`. | Pure Python 3.14 analyzer parsing Dart files. 100% excludes generated files (`*.freezed.dart`, `*.g.dart`). Severity: DGR001–DGR004 emit WARNING by default in baseline audits and escalate to FATAL under `--strict`. | Do not install third-party Dart AST packages; implement high-speed regex token scanner with line-bounded tracking. | `uv run pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py -v`<br>Verifies DGR001–DGR004 detection and generated file immunity. |
| **`@[scripts/backend_audit_loop.py#L303-L321]`**<br>Stage 4 AST Gate | Banned skipping AST validation or tolerating fatal violations in backend audit pipeline. | Execute `scan_files_for_guardrails` across target files. Halt build with exit code 1 if any FATAL violation is detected. | Prune full-codebase forced rescan when running localized file audits. | `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py`<br>Confirms clean execution. |
| **`@[scripts/flutter_audit_loop.py#L40-L122]`**<br>Stage 3 Dart Gate | Banned bypassing client architectural rules or tolerating Finnish strings/absolute paths in build tools. | Insert `_dart_guardrails.py` gate following code generation. Halt with status code 1 if unsuppressed FATAL violations exist. | Prune manual build execution loops; integrate seamlessly into existing audit loop steps. | `uv run python scripts/flutter_audit_loop.py client_app_v2`<br>Confirms clean execution with English output. |

---

## Red-Team Falsification & Adversarial Analysis

The following critical failure modes were discovered and pre-emptively addressed during Tier 0 adversarial analysis:

1. **Failure Point 1: Premature FATAL Severity on Dart Rules Breaking Client Audit Loop**
   - *Vulnerability:* `client_app_v2` contains 27 existing usages of `SizedBox.shrink()` (in `shared/widgets/` and `features/execution/views/widgets/`) and 49 methods returning `Future<Map<String, dynamic>>` in `studio_client.dart`, `reports_client.dart`, and `execution_client.dart` that are scheduled for complete migration in Phase 4 of EPIC 152. If DGR001 or DGR002 were configured as FATAL by default, running `flutter_audit_loop.py client_app_v2` would immediately crash with exit code 1, halting CI/CD and developer workflows.
   - *Resolution & Invariant:* In `scripts/_dart_guardrails.py`, rules DGR001, DGR002, DGR003, and DGR004 MUST emit `WARNING` severity by default during baseline audits, reporting all architectural defects in a structured table without failing the build. They escalate to `FATAL` severity (and return non-zero exit codes) *strictly* when the explicit `--strict` flag is supplied.
2. **Failure Point 2: Existing Comment Suppression Unit Tests in `test_ast_guardrails.py` Failing**
   - *Vulnerability:* In `backend_v2/tests/unit/scripts/test_ast_guardrails.py` (lines 470–545), the helper `_scan_snippet` defaults to `filepath="backend_v2/services/sample.py"`. If QGR000 is modified to make any suppression in domain code an immediate FATAL QGR000 violation, all existing valid suppression unit tests will fail because they test suppressions against a domain filepath.
   - *Resolution & Invariant:* The test suite in `test_ast_guardrails.py` MUST be partitioned:
     - Domain code tests (`backend_v2/services/...`) assert that `# noqa: QGR*` triggers FATAL `QGR000` regardless of reason.
     - Non-domain code tests (`backend_v2/tests/fakes/...` or `scripts/...`) assert that valid `# noqa: QGR* [REASON: ...]` comments succeed (`is_suppressed is True`).
     - Non-domain code tests assert that missing or placeholder reasons trigger FATAL `QGR000`.
3. **Failure Point 3: Working Directory Traversal (`os.chdir`) Breaking `_dart_guardrails.py` Invocation**
   - *Vulnerability:* `flutter_audit_loop.py` line 58 executes `os.chdir(client_app_dir)`. If the script subsequently calls `python scripts/_dart_guardrails.py`, the execution fails with `FileNotFoundError` because the working directory has changed to `client_app_v2`.
   - *Resolution & Invariant:* `flutter_audit_loop.py` MUST resolve the workspace root path before changing directory (`root_dir = current_dir if current_dir.name != "client_app_v2" else current_dir.parent`) and execute `_dart_guardrails.py` via `sys.executable` and `root_dir / "scripts" / "_dart_guardrails.py"`.
4. **Failure Point 4: TypeAdapter(dict) False Positives on Substring Matches**
   - *Vulnerability:* Naive string search for `"dict"` in `TypeAdapter` arguments could flag legitimate DTOs whose class names happen to contain "dict" (specifically the class identifier `PredictiveDictionaryDTO`).
   - *Resolution & Invariant:* Rule QGR018 MUST perform exact AST node structural pattern matching: detecting `ast.Name(id="dict" | "Dict")`, `ast.Subscript(value=ast.Name(id="dict" | "Dict"))`, `ast.Subscript(value=ast.Name(id="list" | "List"), slice=...)` containing dict, or union types containing dict nodes. Substring matching is strictly banned.

---

```xml
<execution_protocol>
  <step id="1" name="PRE-IMPLEMENTATION TECHNICAL DEBT CLEANUP">
    <action>Resolve all itemized Python 2 comma exception tuples, reflection anti-patterns, and localized strings in target scripts.</action>
    <target>@[scripts/_ast_guardrails.py#L36-L161]</target>
    <target>@[scripts/backend_audit_loop.py#L59-L65]</target>
    <target>@[scripts/flutter_audit_loop.py#L40-L122]</target>
    <constraint invariant="scoped_boy_scout_boundary">Clean technical debt exclusively in touched target files before introducing new features.</constraint>
    <verification>Run `uv run python -m py_compile scripts/_ast_guardrails.py scripts/backend_audit_loop.py scripts/flutter_audit_loop.py` to confirm clean compilation with zero syntax defects.</verification>
  </step>

  <step id="2" name="EXPAND AST GUARDRAILS ENGINE (PYTHON BACKEND)">
    <action>Implement new guardrail rules and zero-tolerance invariants in `scripts/_ast_guardrails.py`.</action>
    <target>@[scripts/_ast_guardrails.py#L90-L931]</target>
    <constraint invariant="the_zero_compromise_pledge">Enforce 100% typed domain transit and zero reflection in guardrail enforcement.</constraint>
    <substeps>
      <substep id="2.1" name="RULE QGR000: DOMAIN SUPPRESSION ZERO-TOLERANCE">
        Enforce absolute prohibition of `# noqa: QGR*` and blanket `# noqa` suppressions in domain code (`self._is_domain_code` outside `BOUNDARY_EXEMPTION_FILES`).
        When an inline suppression targeting a QGR rule is found in domain code, emit a FATAL `QGR000` violation:
        "QGR comment suppressions are strictly prohibited in domain code. Resolve the underlying architectural violation instead of suppressing it."
        For non-domain code (specifically and exhaustively: test fakes and low-level test fixtures), retain mandatory minimum 10-character `[REASON: ...]` validation without banned placeholders.
      </substep>
      <substep id="2.2" name="RULE QGR001 EXPANSION: VARS, __DICT__, ATTRGETTER &amp; TEST ENFORCEMENT">
        Expand `QGR001` to detect:
        1. Calls to `vars(...)` via `ast.Name(id="vars")`.
        2. Attribute access to `.__dict__` via `ast.Attribute(attr="__dict__")` in [NEW] `visit_Attribute`.
        3. Calls to `operator.attrgetter` or imported `attrgetter(...)` via `ast.Name(id="attrgetter")` or `ast.Attribute(value=ast.Name(id="operator"), attr="attrgetter")`.
        Enforce FATAL severity for `QGR001` in domain code outside boundary exemptions; retain WARNING severity in test files (upgraded to non-zero exit code when `--strict` is explicitly passed).
      </substep>
      <substep id="2.3" name="RULE QGR002 EXPANSION: DISCRIMINATED .GET() ERADICATION">
        Fortify `QGR002` to detect both 1-argument `.get(key)` and 2-argument `.get(key, default)` calls on dictionaries in domain code:
        1. Receiver Exclusion: Exempt legitimate network and storage clients whose receiver is named or attributed specifically and exhaustively: `client`, `http`, `requests`, `session`, `httpx`, `driver`, `os.environ`, `headers`, `_LABEL_MAP`, `LABEL_MAP`, `_VALUE_MAP`, `_NAME_MAP`, `_L10N_MAP`, `L10N_MAP`.
        2. Signature Exclusion: Exempt calls containing network keyword arguments (specifically and exhaustively: `params=`, `headers=`, `timeout=`, `auth=`, `cookies=`).
        3. Standard Library Exclusion: 0-argument `.get()` (specifically ContextVar `.get()`) is exempt.
        4. All other `.get()` calls in domain code outside boundary exemptions are flagged as FATAL `QGR002` violations.
      </substep>
      <substep id="2.4" name="RULE QGR003 EXPANSION: EXCEPTION SWALLOWING ERADICATION">
        Fortify `QGR003` to eliminate silent exception swallowing:
        1. Inspect all `ExceptHandler` nodes in domain code (both broad `except Exception:` and typed handlers, specifically and exhaustively: `except (ValidationError, TypeError):`).
        2. Require that the handler body contains at least one `ast.Raise` statement (`raise` or `raise AppException(...) from e`), OR an explicit call to a dead-letter queue / typed error dispatcher (`dlq_service.push(...)` or returning a typed failure result DTO).
        3. Explicitly flag handlers that log and return a fallback literal (specifically and exhaustively: `return None`, `return []`, `return {}`, `return False`, `pass`, `continue`) as FATAL `QGR003` violations in domain code.
      </substep>
      <substep id="2.5" name="RULE QGR018: TYPE LAUNDERING VIA TYPEADAPTER BAN">
        Implement new rule `QGR018` banning dictionary type laundering via Pydantic `TypeAdapter`:
        Detect `Call(func=Name(id="TypeAdapter"))` or `Call(func=Attribute(attr="TypeAdapter"))` where the first argument specifies a dictionary type (specifically and exhaustively: `ast.Subscript` with slice or value `dict` or `Dict`, `list[dict]`, `list[Dict]`, or Union containing `dict`/`Dict`).
        Severity: FATAL in domain code.
      </substep>
      <substep id="2.6" name="PRESERVE 4-DRIVER BOUNDARY_EXEMPTION_FILES">
        Strictly maintain `BOUNDARY_EXEMPTION_FILES` locked to the 4 physical boundary files: `tinydb_driver.py`, `firestore_driver.py`, `provider.py`, and `logging_config.py` per `ki_zero_permissive_typing.md` line 45 and `EPIC_152_Deep_Dict_Leakage_and_Lazy_Get_Eradication.md` line 43.
      </substep>
    </substeps>
    <verification>Execute unit tests via `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v`.</verification>
  </step>

  <step id="3" name="DEVELOP DART GUARDRAILS ENGINE (FLUTTER CLIENT)">
    <action>Create `scripts/_dart_guardrails.py` to enforce static architectural rules across `client_app_v2/lib/`.</action>
    <target>[NEW] @[scripts/_dart_guardrails.py]</target>
    <constraint invariant="the_no_legacy_mandate">Prevent permissive typing and duct-tape UI patterns in the Flutter client.</constraint>
    <substeps>
      <substep id="3.1" name="RULE DGR001: BANNED LOOSE MAP RETURNS IN API CLIENTS">
        Scan Dart files under `client_app_v2/lib/core/api/` and `client_app_v2/lib/features/*/models/`:
        Flag all method signatures returning `Future<Map<String, dynamic>>`, `Future<List<Map<String, dynamic>>>`, or raw `Map<String, dynamic>`.
        Methods must return strongly typed Freezed DTOs or domain models. Severity: WARNING (FATAL under `--strict`).
      </substep>
      <substep id="3.2" name="RULE DGR002: BANNED SIZEDBOX.SHRINK CONCEALMENT">
        Scan Dart files under `client_app_v2/lib/features/` and `client_app_v2/lib/shared/`:
        Flag all occurrences of `SizedBox.shrink()` used to conceal broken layouts or swallow rendering errors.
        Enforce usage of `AppErrorBoundary` or explicit typed fallback widgets. Severity: WARNING (FATAL under `--strict`).
      </substep>
      <substep id="3.3" name="RULE DGR003: BANNED HARDCODED UI STRING LITERALS">
        Scan Dart widget files under `client_app_v2/lib/features/`:
        Flag direct raw string literals passed into `Text("...")` widgets that bypass `AppLocalizations.of(context)` or `.arb` localization keys. Severity: WARNING (FATAL under `--strict`).
      </substep>
      <substep id="3.4" name="RULE DGR004: BANNED DART LINT SUPPRESSIONS">
        Scan Dart source files for unauthorized `// ignore:` or `// ignore_for_file:` comments in handwritten code. Severity: WARNING (FATAL under `--strict`).
      </substep>
      <substep id="3.5" name="GENERATED FILE IMMUNITY &amp; CLI REPORTING">
        100% exclude generated files (`*.freezed.dart`, `*.g.dart`, `.dart_tool/`, `build/`). Implement CLI interface accepting target directories with `--strict` flag, returning non-zero exit codes on FATAL or strict violations, and emitting structured console violation tables.
      </substep>
    </substeps>
    <verification>Execute unit tests via `uv run pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py -v`.</verification>
  </step>

  <step id="4" name="INTEGRATE QUALITY GATES INTO AUDIT SCRIPTS">
    <action>Wire expanded guardrails into `scripts/backend_audit_loop.py` and `scripts/flutter_audit_loop.py`.</action>
    <target>@[scripts/backend_audit_loop.py#L303-L321]</target>
    <target>@[scripts/flutter_audit_loop.py#L40-L122]</target>
    <constraint invariant="fragmented_quality_gates_prevention">Ensure audit scripts execute complete, un-fragmented quality gates across both production and test suites.</constraint>
    <substeps>
      <substep id="4.1" name="BACKEND AUDIT LOOP INTEGRATION">
        In `@[scripts/backend_audit_loop.py]`:
        1. Ensure `QGR000`, `QGR001`, `QGR002`, `QGR003`, and `QGR018` run with FATAL enforcement on domain code.
        2. Retain advisory reporting on warnings unless `--strict` or `--ast-strict` is supplied.
      </substep>
      <substep id="4.2" name="FLUTTER AUDIT LOOP INTEGRATION">
        In `@[scripts/flutter_audit_loop.py]`:
        1. Resolve workspace root before `os.chdir` and execute `_dart_guardrails.py` as an automated gate step immediately following code generation (`build_runner`) and before `dart format`.
        2. Halt the pipeline with status code 1 if `_dart_guardrails.py` discovers any unsuppressed FATAL violations in `client_app_v2/lib`.
      </substep>
    </substeps>
    <verification>Run `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py` and verify clean execution.</verification>
  </step>

  <step id="5" name="ISTQB UNIT TEST SUITE EXPANSION &amp; FALSE-POSITIVE IMMUNITY">
    <action>Develop comprehensive ISTQB boundary value and equivalence partition unit tests for all new rules.</action>
    <target>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1-L1058]</target>
    <target>[NEW] @[backend_v2/tests/unit/scripts/test_dart_guardrails.py]</target>
    <constraint invariant="universal_quality_gates">Enforce 90%+ strict TDD coverage on all guardrail scripts.</constraint>
    <substeps>
      <substep id="5.1" name="PYTHON AST GUARDRAIL TEST EXPANSION">
        In `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`:
        - Partition QGR000-A: Clean code with zero suppressions -> PASS.
        - Partition QGR000-B: Domain code with `# noqa: QGR001 [REASON: valid text]` -> FAIL with FATAL QGR000.
        - Partition QGR000-C: Non-domain test fake (`tests/fakes/...`) with valid reason -> PASS.
        - Partition QGR000-D: Non-domain test fake with placeholder reason -> FAIL with FATAL QGR000.
        - Partition QGR001-A: Domain code calling `vars(obj)` -> FAIL with FATAL QGR001.
        - Partition QGR001-B: Domain code accessing `obj.__dict__` -> FAIL with FATAL QGR001.
        - Partition QGR001-C: Domain code calling `operator.attrgetter("field")` -> FAIL with FATAL QGR001.
        - Partition QGR001-D: Test file calling `getattr(obj, "field")` -> WARNING (or FATAL with strict=True).
        - Partition QGR002-A: Domain code calling `data.get("key")` -> FAIL with FATAL QGR002.
        - Partition QGR002-B: Domain code calling `data.get("key", default)` -> FAIL with FATAL QGR002.
        - Partition QGR002-C: Domain code calling `client.get("https://api.example.com", headers=h)` -> PASS (exempt network client).
        - Partition QGR002-D: Domain code calling `_last_response_var.get()` -> PASS (0-arg ContextVar get).
        - Partition QGR003-A: Domain code with `except Exception: raise AppException(ErrorCodes.SYSTEM_ERROR)` -> PASS.
        - Partition QGR003-B: Domain code with `except Exception as e: logger.warning(e); return None` -> FAIL with FATAL QGR003.
        - Partition QGR003-C: Domain code with `except (ValidationError, TypeError) as e: logger.error(e); return []` -> FAIL with FATAL QGR003.
        - Partition QGR018-A: Domain code with `TypeAdapter(dict[str, Any]).validate_python(m)` -> FAIL with FATAL QGR018.
        - Partition QGR018-B: Domain code with `TypeAdapter(WorkflowResponseDTO).validate_python(m)` -> PASS.
        - Partition EXEMPT-A: `tinydb_driver.py`, `firestore_driver.py`, `provider.py`, `logging_config.py` preserve exemption.
      </substep>
      <substep id="5.2" name="DART GUARDRAIL TEST SUITE CREATION">
        In [NEW] `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py]`:
        - Partition DGR001-A: API client declaring `Future<WorkflowDto> getWorkflow()` -> PASS.
        - Partition DGR001-B: API client declaring `Future<Map<String, dynamic>> getWorkflow()` -> DGR001 violation emitted (WARNING in default, FATAL in strict).
        - Partition DGR002-A: Widget rendering `const Text("valid")` or `AppErrorBoundary` -> PASS.
        - Partition DGR002-B: Widget rendering `return const SizedBox.shrink();` -> DGR002 violation emitted.
        - Partition DGR003-A: Widget rendering `Text(l10n.title)` -> PASS.
        - Partition DGR003-B: Widget rendering `Text("Hardcoded String")` -> DGR003 violation emitted.
        - Partition DGR004-A: Dart file with standard code -> PASS.
        - Partition DGR004-B: Dart file with `// ignore_for_file: invalid_annotation_target` in handwritten code -> DGR004 violation emitted.
        - Partition DGR-GEN-A: Generated file `sample.freezed.dart` with `// ignore:` and `SizedBox.shrink()` -> 100% IGNORED / PASS.
      </substep>
    </substeps>
    <verification>Run `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py backend_v2/tests/unit/scripts/test_dart_guardrails.py -v`.</verification>
  </step>

  <step id="6" name="KNOWLEDGE BASE SYNCHRONIZATION">
    <action>Update `ki_zero_permissive_typing.md` and project rules to record the new guardrail rules and zero-tolerance invariants.</action>
    <target>@[ki_zero_permissive_typing.md]</target>
    <constraint invariant="knowledge_base_primacy">Document new guardrail rules and boundaries as permanent SSOT contracts.</constraint>
    <verification>Verify KI integrity and formatting.</verification>
  </step>
</execution_protocol>
```

---

## Explicit Concrete Test Scenarios (Anti-Happy-Path Compliance)

Every feature implemented in this plan includes mandatory positive and negative test partitions:

### Feature 1: Domain Suppression Zero-Tolerance (`QGR000`)
- **Positive Scenario:**
  - *Input:* File `backend_v2/services/order_service.py` with standard typed Pydantic code containing zero `# noqa` comments.
  - *Expected Output:* `scan_source_code_for_guardrails` returns zero violations; exit code 0.
- **Negative Scenario 1 (Domain QGR Suppression with Reason):**
  - *Input:* File `backend_v2/services/order_service.py` containing `x = getattr(obj, "id")  # noqa: QGR001 [REASON: Third-party LiteLLM model attribute]`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR000` violation: "QGR comment suppressions are strictly prohibited in domain code."
- **Negative Scenario 2 (Domain Blanket Suppression):**
  - *Input:* File `backend_v2/services/order_service.py` containing `x = getattr(obj, "id")  # noqa [REASON: Temporary bypass]`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR000` violation: "QGR comment suppressions are strictly prohibited in domain code."

### Feature 2: Reflection & Dynamic Attribute Access Ban (`QGR001`)
- **Positive Scenario:**
  - *Input:* File `backend_v2/services/user_service.py` accessing attributes via static dot notation `user.id` and `user.name`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns zero violations; exit code 0.
- **Negative Scenario 1 (`vars()` Call):**
  - *Input:* File `backend_v2/services/user_service.py` containing `payload = vars(user)`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR001` violation: "Banned `vars()` call in domain code."
- **Negative Scenario 2 (`__dict__` Access):**
  - *Input:* File `backend_v2/services/user_service.py` containing `payload = user.__dict__["name"]`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR001` violation: "Banned `.__dict__` access in domain code."
- **Negative Scenario 3 (Test Suite Reflection):**
  - *Input:* File `backend_v2/tests/unit/test_sample.py` containing `val = getattr(response, "status_code")`.
  - *Expected Output:* `scan_source_code_for_guardrails` with `strict=True` returns non-zero exit code on reflection in test suite.

### Feature 3: Syntactic & Semantic `.get()` Eradication (`QGR002`)
- **Positive Scenario 1 (Network Client):**
  - *Input:* File `backend_v2/services/web_service.py` containing `response = await client.get("https://api.example.com/v1/data", headers=req_headers, timeout=10)`.
  - *Expected Output:* `scan_source_code_for_guardrails` recognises network client keywords and returns zero violations; exit code 0.
- **Positive Scenario 2 (ContextVar):**
  - *Input:* File `backend_v2/utils/redis_patcher.py` containing `return _last_response_var.get()`.
  - *Expected Output:* `scan_source_code_for_guardrails` recognises 0-argument ContextVar lookup and returns zero violations; exit code 0.
- **Negative Scenario 1 (Single-Argument Dict `.get()`):**
  - *Input:* File `backend_v2/services/web_service.py` containing `val = data.get("some_key")`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR002` violation: "Banned lazy fallback call: `.get(key)` in domain code."
- **Negative Scenario 2 (Two-Argument Dict `.get()` with Default):**
  - *Input:* File `backend_v2/services/web_service.py` containing `val = data.get("some_key", "default_val")`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR002` violation: "Banned lazy fallback call: `.get(key, default)` in domain code."

### Feature 4: Silent Exception Swallowing Eradication (`QGR003`)
- **Positive Scenario:**
  - *Input:* File `backend_v2/services/task_service.py` containing `try: do_work() except Exception as exc: logger.error("Failed", extra={"error_code": ErrorCodes.SYSTEM_ERROR.name}); raise AppException(ErrorCodes.SYSTEM_ERROR) from exc`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns zero violations; exit code 0.
- **Negative Scenario 1 (Logger Warning and Return None):**
  - *Input:* File `backend_v2/services/task_service.py` containing `try: do_work() except Exception as exc: logger.warning(f"Failed: {exc}"); return None`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR003` violation: "Broad `except Exception:` handler lacking `raise` detected."
- **Negative Scenario 2 (Typed Exception Catch and Return Empty List):**
  - *Input:* File `backend_v2/services/task_service.py` containing `try: do_work() except (ValidationError, TypeError) as exc: logger.error(exc); return []`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR003` violation: "Exception handler lacking `raise` or typed failure dispatch detected."

### Feature 5: Type Laundering via `TypeAdapter(dict)` Ban (`QGR018`)
- **Positive Scenario:**
  - *Input:* File `backend_v2/services/model_service.py` containing `adapter = TypeAdapter(UserProfileResponseDTO)`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns zero violations; exit code 0.
- **Negative Scenario 1 (`TypeAdapter(dict[str, Any])`):**
  - *Input:* File `backend_v2/services/model_service.py` containing `raw = TypeAdapter(dict[str, Any]).validate_python(model)`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR018` violation: "Banned type laundering: TypeAdapter instantiated with dictionary type."
- **Negative Scenario 2 (`TypeAdapter(list[dict[str, object]])`):**
  - *Input:* File `backend_v2/services/model_service.py` containing `raw = TypeAdapter(list[dict[str, object]]).validate_python(model)`.
  - *Expected Output:* `scan_source_code_for_guardrails` returns FATAL `QGR018` violation: "Banned type laundering: TypeAdapter instantiated with dictionary type."

### Feature 6: Dart Quality Gate (`DGR001` - `DGR004`)
- **Positive Scenario 1 (Typed API Client):**
  - *Input:* File `client_app_v2/lib/core/api/profile_client.dart` declaring `Future<UserProfileDto> getProfile(String id)`.
  - *Expected Output:* `scan_dart_source_code` returns zero violations; exit code 0.
- **Positive Scenario 2 (Generated Code Immunity):**
  - *Input:* File `client_app_v2/lib/shared/models/sample.freezed.dart` containing `// ignore_for_file: type=lint` and `return const SizedBox.shrink();`.
  - *Expected Output:* `scan_dart_source_code` completely ignores generated file; exit code 0.
- **Negative Scenario 1 (`Map<String, dynamic>` in API Client under `--strict`):**
  - *Input:* File `client_app_v2/lib/core/api/profile_client.dart` declaring `Future<Map<String, dynamic>> getProfile(String id)`.
  - *Expected Output:* `scan_dart_source_code --strict` returns `DGR001` violation: "Banned loose `Map<String, dynamic>` return in API client."
- **Negative Scenario 2 (`SizedBox.shrink()` Concealment under `--strict`):**
  - *Input:* File `client_app_v2/lib/features/studio/views/test_view.dart` containing `if (data == null) return const SizedBox.shrink();`.
  - *Expected Output:* `scan_dart_source_code --strict` returns `DGR002` violation: "Banned `SizedBox.shrink()` concealment detected."

---

## Verification Plan

### Automated Test Gates

1. **Python AST Guardrail Unit Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py -v
   ```
2. **Dart Guardrail Unit Tests:**
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py -v
   ```
3. **Backend Audit Loop Execution:**
   ```powershell
   uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py
   ```
4. **Flutter Audit Loop Execution:**
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2
   ```
