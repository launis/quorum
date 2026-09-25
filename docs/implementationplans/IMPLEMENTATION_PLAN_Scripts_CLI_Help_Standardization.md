<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Standardizing CLI Help and Argument Parsing Across Quorum Scripts

## Problem Overview & Physical Codebase Verification

An empirical audit across all 25 Python scripts residing in @[scripts/] reveals significant architectural inconsistencies in Command Line Interface (CLI) argument handling, help documentation, and execution safety.

### Physical Audit Findings & Classification of Scripts

1. **Category A: High-Risk Premature Execution & Missing CLI Handlers (7 Scripts)**
   - @[scripts/backend_audit_loop.py]: Manual `sys.argv[1:]` parsing intercepts only `--openapi`, `--test`, `--strict`, and appends all other tokens to `targets`. When invoked with `--help` or `-h`, it interprets `--help` as a target file path and executes the entire 6-stage validation pipeline (`ruff check --help`, `ruff format --help`, `mypy --help`, seed verification), blocking execution and timing out after 5 seconds.
   - @[scripts/flutter_audit_loop.py]: Manual `sys.argv` parsing directly reads `target_dir = sys.argv[1]`. When passed `--help` or `-h`, it sets `target_dir = "--help"` and immediately executes Flutter and Dart build/format/analyze commands, resulting in build failures and terminal pollution.
   - @[scripts/migrate_seed_contrastive_pairs.py]: Completely lacks CLI argument parsing (`if __name__ == "__main__": migrate_seed_data()`). When passed `--help`, it immediately executes a live database migration on `backend_v2/seed/seed_data.json` and writes backup files to disk.
   - @[scripts/_ast_guardrails.py]: Manual `sys.argv[1:]` parsing intercepts `--strict` and appends all other arguments to `targets`. When passed `--help`, it scans a non-existent target named `--help`, silently reporting clean completion instead of displaying usage documentation.
   - @[scripts/audit_dict_eradication.py]: Manual argument parsing filters flags (`--strict`) and treats remaining tokens as directory paths. When invoked with `--help`, it attempts to scan `--help`, raises `FileNotFoundError: Path does not exist: --help`, and exits with code 1.
   - @[scripts/matrix_slice_engine.py]: Lacks workspace root injection into `sys.path`. When executed directly via `python scripts/matrix_slice_engine.py`, it crashes with `ModuleNotFoundError: No module named 'backend_v2'`. Furthermore, it lacks an executable `main()` entrypoint to expose its slice export, empirical contamination detection, and theory opponent card capabilities.
   - @[scripts/_ast_boundary_utils.py]: Library utility without an executable CLI entrypoint. Exits silently with code 0 on `--help` without providing documentation on AST extraction utilities.

2. **Category B: Core Quality Gates & Verification Scripts with Basic Argparse (5 Scripts)**
   - @[scripts/audit_database_atoms.py], @[scripts/sanitize_seed_vault.py], @[scripts/audit_markdown_boundaries.py], @[scripts/_dart_guardrails.py], @[scripts/audit_dto_parity.py]
   - These scripts implement `argparse.ArgumentParser`, but lack comprehensive descriptions, epilog examples, or clear documentation on exit codes and parameter constraints.

3. **Category C: Audit, Planning & Documentation Scripts (6 Scripts)**
   - @[scripts/audit_epic_coverage.py], @[scripts/audit_planner_output.py], @[scripts/audit_tracker_output.py], @[scripts/audit_plan_tracker_parity.py], @[scripts/audit_rules_staleness.py], @[scripts/convert_epic_to_hybrid.py]
   - These scripts possess partial CLI definitions that require uniform formatting, explicit parameter defaults, and concrete invocation examples.

4. **Category D: Matrix Hardening & Diagnostic Engines (7 Scripts)**
   - @[scripts/matrix_hardening_generator.py], @[scripts/matrix_hardening_loop.py], @[scripts/audit_matrix_auto_filler.py], @[scripts/audit_matrix_manager.py], @[scripts/diff_executions.py], @[scripts/reconcile_storage.py], @[scripts/run_e2e_variance_test.py]
   - Complex engines with multiple flags requiring standardized help formatters (`argparse.RawDescriptionHelpFormatter`), parameter grouping, and concrete execution epilogs.

---

## Architectural Directives Table

| Component & Boundary | Banned Architectural Patterns | Mandatory Modern Architecture | Pruned Premature Scope | Proven By Test Contracts |
| :--- | :--- | :--- | :--- | :--- |
| **CLI Argument Parsing Standard**<br>`scripts/` | Banned: Raw `sys.argv[1:]` loops without help handling; crashing or executing mutations on `-h`/`--help`; unformatted help text; missing exit codes. | Mandatory: Universal adoption of `argparse.ArgumentParser` configured with `formatter_class=argparse.RawDescriptionHelpFormatter`, explicit `description`, detailed `help` strings per argument, and rich PowerShell `epilog` examples. | Pruned: External CLI dependencies (specifically: Click, Typer, or Rich TUI frameworks). Use pure Python standard library `argparse`. | Proven via: `test_scripts_cli_help_zero_side_effects` asserting that all 25 scripts return exit code 0 on `--help` in under 1000ms. |
| **Execution Safety & Direct Runner Guard**<br>`scripts/` | Banned: Mutating disk files, writing database backups, running linters, or triggering child processes when invoked with `-h` or `--help`. | Mandatory: Pre-flight `argparse` resolution before executing any business logic, subprocess calls, or disk I/O. Workspace root resolution in `sys.path` and UTF-8 console output reconfiguration. | Pruned: Interactive CLI menus or cursor navigators. Pure non-blocking flag dispatching. | Proven via: `test_scripts_cli_help_does_not_mutate_disk` asserting clean `git status` after executing `--help` across all 25 scripts. |
| **Audit Loop CLI Safety**<br>`@[scripts/backend_audit_loop.py]`<br>`@[scripts/flutter_audit_loop.py]` | Banned: Treating `--help` as a target file or directory; executing `ruff`, `mypy`, `dart`, or `flutter` on `--help`. | Mandatory: Structured `argparse` parser exposing `targets` (positional, nargs="+"), optional flags (`--test`, `--openapi`, `--strict`, `--build`), and immediate `--help` display. | Pruned: Multi-threaded parallel linter dispatchers or custom shell runners. | Proven via: `test_backend_audit_loop_cli_help` and `test_flutter_audit_loop_cli_help` asserting immediate 0 exit with usage output. |
| **Seed Migration CLI Safety**<br>`@[scripts/migrate_seed_contrastive_pairs.py]` | Banned: Immediate unattended execution upon script import or invocation; creating disk backups or mutating `seed_data.json` when queried with `--help`. | Mandatory: Standard CLI interface supporting `--seed-path`, `--dry-run`, `--backup-dir`, and `-h`/`--help`. Writes to disk exclusively when executed without `--dry-run`. | Pruned: Interactive confirmation prompts (`y/n`). | Proven via: `test_migrate_seed_contrastive_pairs_cli_help` asserting exit 0 without file generation. |
| **Matrix Slice Engine Entrypoint**<br>`@[scripts/matrix_slice_engine.py]` | Banned: Missing workspace root in `sys.path` causing `ModuleNotFoundError`; uncallable library state without CLI entrypoint. | Mandatory: Top-level `sys.path.insert(0, _workspace_root)` and dedicated `main()` entrypoint exposing `--export`, `--audit-contamination`, `--audit-coherence`, `--theory-card`, `--patch`, `--explain`. | Pruned: Graphical matrix visualizers or web server runners. | Proven via: `test_matrix_slice_engine_cli_help` asserting clean execution and flag documentation. |

---

## Target Scope & Boundaries

### TARGET Files (To Modify / Create)
- `[MODIFY]` @[scripts/backend_audit_loop.py]: Refactor argument parsing to `argparse.ArgumentParser` with early `--help` display, documenting all 6 validation stages and target options.
- `[MODIFY]` @[scripts/flutter_audit_loop.py]: Refactor argument parsing to `argparse.ArgumentParser`, documenting all 5 Flutter audit stages, `--build`, `--test`, and `--strict`.
- `[MODIFY]` @[scripts/migrate_seed_contrastive_pairs.py]: Implement `argparse.ArgumentParser` with `--seed-path`, `--dry-run`, `--backup-dir`, and comprehensive help documentation.
- `[MODIFY]` @[scripts/_ast_guardrails.py]: Implement `argparse.ArgumentParser` with positional `targets`, `--strict`, and complete documentation of rules QGR000 through QGR020.
- `[MODIFY]` @[scripts/audit_dict_eradication.py]: Replace raw `sys.argv` parsing with `argparse.ArgumentParser`, documenting positional `targets`, `--strict`, and the 10 eradicated dict anti-patterns.
- `[MODIFY]` @[scripts/matrix_slice_engine.py]: Inject workspace root to `sys.path` to fix import errors, and add `main()` CLI entrypoint exposing matrix slice operations.
- `[MODIFY]` @[scripts/_ast_boundary_utils.py]: Add `main()` CLI entrypoint exposing `--file`, `--extract-targets`, `--extract-symbols`, and diagnostic AST verification.
- `[MODIFY]` @[scripts/audit_database_atoms.py]: Enrich parser description, argument help strings, and epilog examples.
- `[MODIFY]` @[scripts/sanitize_seed_vault.py]: Enrich description, document all options (`--seed-path`, `--dry-run`, `--reseed`, `--test`), add PowerShell epilog examples.
- `[MODIFY]` @[scripts/audit_markdown_boundaries.py]: Document all checked rules (MBD001-MBD009), clarify remediation workflow, and add concrete epilog examples.
- `[MODIFY]` @[scripts/_dart_guardrails.py]: Document DGR001-DGR004 rules, target paths, generated file immunity, and epilog examples.
- `[MODIFY]` @[scripts/audit_dto_parity.py]: Document Freezed vs Pydantic parity checks, cross-language field mapping, `--backend-dir`, `--frontend-dir`, `--fail-on-mismatch`, and epilog examples.
- `[MODIFY]` @[scripts/audit_epic_coverage.py]: Document `--epic`, `--phase`, `--workspace-root`, `--output-report` with concrete epilog examples.
- `[MODIFY]` @[scripts/audit_planner_output.py]: Document planner output fidelity verification against Epics, line boundary preservation, and epilog examples.
- `[MODIFY]` @[scripts/audit_tracker_output.py]: Document tracker synchronization modes (`plan`, `epic`, `all`), argument options, and epilog examples.
- `[MODIFY]` @[scripts/audit_plan_tracker_parity.py]: Enrich documentation of `--tracker`, `--plan`, `--all`, `--json`, `--strict` with CI and single-file examples.
- `[MODIFY]` @[scripts/audit_rules_staleness.py]: Document rule staleness scanning against codebase usage, `--rules-dir`, `--search-dirs`, and epilog examples.
- `[MODIFY]` @[scripts/convert_epic_to_hybrid.py]: Document hybrid Markdown+XML migration, `epic_path`, `--dry-run`, and epilog examples.
- `[MODIFY]` @[scripts/matrix_hardening_generator.py]: Document `--plan`, `--target-density`, `--all-gaps`, atom gap detection, and epilog examples.
- `[MODIFY]` @[scripts/matrix_hardening_loop.py]: Document all 10 CLI options (`--status`, `--inspect`, `--done`, `--reset`, `--slice`, `--theory-card`, `--patch`, `--explain`, `--audit-contamination`), and interactive TUI vs flag mode.
- `[MODIFY]` @[scripts/audit_matrix_auto_filler.py]: Document `--file`, `--target`, `--fail`, `--na`, matrix CSV generation, and epilog examples.
- `[MODIFY]` @[scripts/audit_matrix_manager.py]: Document `--type`, `--target`, `--ast-scan`, `--output`, `--file`, and epilog examples.
- `[MODIFY]` @[scripts/diff_executions.py]: Document `execution_ids`, `-o`, execution trace comparison, divergence calculation, and epilog examples.
- `[MODIFY]` @[scripts/reconcile_storage.py]: Document `--check`, `--fix`, `--db-path`, `--storage-dir`, CQRS consistency invariants, and epilog examples.
- `[MODIFY]` @[scripts/run_e2e_variance_test.py]: Document `inputs_target`, `--inputs`, `--workflow`, `--profile`, `--locale`, execution modes, and epilog examples.
- `[NEW]` @[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]: Automated pytest test suite executing `--help` and `-h` across all 25 scripts to assert zero side-effects, valid help text, and fast execution.

### CONTEXT Files (Read-Only)
- @[.agents/rules/00-antigravity-core.md]: Global orchestration, English language mandate, Windows PowerShell rules.
- @[.agents/rules/01-python-backend.md]: Python constraints, type safety, zero duct tape.
- @[.agents/rules/04_directory_reference.md]: Directory routing and boundaries.

---

## Pre-Implementation Technical Debt Cleanups (Phase 1 Prerequisite)

Before enhancing the existing argparse implementations in Categories B, C, and D, the critical anti-patterns in Category A scripts must be eliminated:
1. **Premature Subprocess Execution in Audit Loops**: Eliminate raw `sys.argv` processing in `backend_audit_loop.py` and `flutter_audit_loop.py` that causes `--help` to trigger long-running linting, typechecking, and testing pipelines.
2. **Unattended Mutation in Seed Migration**: Eliminate raw execution on import or bare invocation in `migrate_seed_contrastive_pairs.py`.
3. **Target File Name Fallbacks**: Eliminate the silent fallback in `_ast_guardrails.py` and `audit_dict_eradication.py` where `--help` is swallowed as a file path.
4. **Missing Workspace Path Resolution**: Resolve `ModuleNotFoundError` in `matrix_slice_engine.py` by adding top-level `sys.path.insert(0, _workspace_root)`.

---

```xml
<execution_protocol>
  <step id="1" name="PHASE 1: HIGH-RISK PREMATURE EXECUTION &amp; SAFETY FIXES">
    <action>Refactor argument parsing in @[scripts/backend_audit_loop.py] to use `argparse.ArgumentParser` with `formatter_class=argparse.RawDescriptionHelpFormatter`. Define positional argument `targets` (nargs="*", default=[]), `--test` (action="store_true"), `--openapi` (action="store_true"), and `--strict` / `--ast-strict` (action="store_true"). If no targets are provided and no help is requested, display usage and exit with code 1. Ensure passing `-h` or `--help` prints full documentation and exits immediately with code 0 without executing any subprocesses.</action>
    <action>Refactor argument parsing in @[scripts/flutter_audit_loop.py] to use `argparse.ArgumentParser`. Define positional argument `target_directory` (default="client_app_v2/lib"), `--build` (action="store_true"), `--test` (action="store_true"), and `--strict` (action="store_true"). Ensure passing `-h` or `--help` prints full documentation and exits immediately with code 0 without invoking `dart` or `flutter`.</action>
    <action>Refactor @[scripts/migrate_seed_contrastive_pairs.py] to wrap execution inside a safe `main()` function utilizing `argparse.ArgumentParser`. Add optional flags `--seed-path` (default="backend_v2/seed/seed_data.json"), `--dry-run` (action="store_true", default=False), and `--backup-dir` (default="backend_v2/seed/backups"). Ensure passing `--help` prints usage information and exits with code 0 without modifying files or creating backups.</action>
    <action>Refactor argument parsing in @[scripts/_ast_guardrails.py] to use `argparse.ArgumentParser`. Define positional argument `targets` (nargs="+"), and `--strict` / `--ast-strict` (action="store_true"). Document rules QGR000 through QGR020 in the description. Ensure passing `--help` displays rule descriptions and exits with code 0.</action>
    <action>Refactor argument parsing in @[scripts/audit_dict_eradication.py] to use `argparse.ArgumentParser`. Define positional argument `targets` (nargs="*", default=["backend_v2"]), and `--strict` / `--ast-strict` (action="store_true"). Document the 10 eradicated dict anti-patterns in the parser description. Ensure passing `--help` exits with code 0 without throwing FileNotFoundError.</action>
    <action>Inject workspace root path into `sys.path` at the top of @[scripts/matrix_slice_engine.py] before importing `backend_v2` modules. Implement a standard `main()` CLI entrypoint with `argparse.ArgumentParser` supporting `--export MATRIX_ID`, `--audit-contamination MATRIX_ID`, `--audit-coherence MATRIX_ID`, `--theory-card MATRIX_ID`, `--patch SLICE_PATH`, `--explain MATRIX_ID`, `--output OUTPUT_PATH`, and `--seed-path SEED_PATH`.</action>
    <action>Add a standard `main()` CLI entrypoint to @[scripts/_ast_boundary_utils.py] with `argparse.ArgumentParser` supporting `--file FILE_PATH`, `--extract-targets` (action="store_true"), and `--extract-symbols` (action="store_true"), documenting shared AST boundary extraction tools.</action>
    <constraint invariant="zero_side_effects_on_help">Invoking any script in scripts/ with -h or --help must execute in under 1000ms with zero filesystem mutations and zero database changes.</constraint>
    <constraint invariant="windows_powershell_syntax">All example commands in epilog strings must use Windows PowerShell syntax (uv run python scripts/...).</constraint>
  </step>

  <step id="2" name="PHASE 2: CORE QUALITY GATE &amp; BOUNDARY SCRIPTS ENRICHMENT">
    <action>Enrich CLI documentation in @[scripts/audit_database_atoms.py]: update `argparse.ArgumentParser` description with verified database invariants (atom uniqueness, scale bounds, schema conformance). Add explicit `help` strings for `--seed-path` and `--strict`. Add an `epilog` containing concrete PowerShell invocation examples.</action>
    <action>Enrich CLI documentation in @[scripts/sanitize_seed_vault.py]: update `argparse.ArgumentParser` description detailing vault sanitization, atom key sorting, and schema formatting. Document `--seed-path`, `--dry-run`, `--reseed`, `--test`. Add an `epilog` with concrete verification examples.</action>
    <action>Enrich CLI documentation in @[scripts/audit_markdown_boundaries.py]: update `argparse.ArgumentParser` description enumerating rules MBD001 through MBD009 (Ambiguity, XML Truncation, AST Line Bounds, Class Existence, Settings, Enums, Code Blocks, Table Parity). Add an `epilog` showing plan audit examples.</action>
    <action>Enrich CLI documentation in @[scripts/_dart_guardrails.py]: update `argparse.ArgumentParser` description enumerating rules DGR001 through DGR004. Document positional `targets` and `--strict`. Add an `epilog` with Flutter client scanning examples.</action>
    <action>Enrich CLI documentation in @[scripts/audit_dto_parity.py]: update `argparse.ArgumentParser` description explaining Freezed and Pydantic cross-domain model parity verification, field naming parity (snake_case to camelCase), and exit code semantics. Document `--backend-dir`, `--frontend-dir`, and `--fail-on-mismatch`.</action>
    <constraint invariant="english_language_mandate">All parser descriptions, argument help strings, and epilog examples must be written strictly in English.</constraint>
  </step>

  <step id="3" name="PHASE 3: AUDIT, PLANNING &amp; DOCUMENTATION SCRIPTS STANDARDIZATION">
    <action>Enrich CLI documentation in @[scripts/audit_epic_coverage.py]: document `--epic`, `--phase`, `--workspace-root`, and `--output-report` with parameter formats and verification targets.</action>
    <action>Enrich CLI documentation in @[scripts/audit_planner_output.py]: document planner output fidelity verification against Epics, line boundary preservation, and KI inheritance checks.</action>
    <action>Enrich CLI documentation in @[scripts/audit_tracker_output.py]: document tracker synchronization modes (`plan`, `epic`, `all`), `--tracker`, `--plan-dir`, `--plan-file`, and state machine invariants.</action>
    <action>Enrich CLI documentation in @[scripts/audit_plan_tracker_parity.py]: document `--tracker`, `--plan`, `--all`, `--json`, `--strict` with CI and single-file examples.</action>
    <action>Enrich CLI documentation in @[scripts/audit_rules_staleness.py]: document rule staleness scanning against codebase usage, `--rules-dir`, and `--search-dirs`.</action>
    <action>Enrich CLI documentation in @[scripts/convert_epic_to_hybrid.py]: document hybrid Markdown plus XML migration, positional `epic_path`, and `--dry-run`.</action>
    <constraint invariant="anti_ambiguity_mandate">Never use ambiguous phrasing in help texts. Use explicit closed enumerations or references to authoritative SSOT models.</constraint>
  </step>

  <step id="4" name="PHASE 4: MATRIX HARDENING &amp; DIAGNOSTIC ENGINES STANDARDIZATION">
    <action>Enrich CLI documentation in @[scripts/matrix_hardening_generator.py]: document `--plan`, `--target-density`, `--all-gaps`, atom gap detection, and batch generation.</action>
    <action>Enrich CLI documentation in @[scripts/matrix_hardening_loop.py]: document all 10 CLI options (`--status`, `--inspect`, `--done`, `--reset`, `--slice`, `--theory-card`, `--patch`, `--explain`, `--audit-contamination`), and distinguish between interactive mode and headless flag execution.</action>
    <action>Enrich CLI documentation in @[scripts/audit_matrix_auto_filler.py]: document `--file`, `--target`, `--fail`, `--na`, and matrix CSV auto-filling semantics.</action>
    <action>Enrich CLI documentation in @[scripts/audit_matrix_manager.py]: document `--type`, `--target`, `--ast-scan`, `--output`, `--file`, and matrix model registration workflows.</action>
    <action>Enrich CLI documentation in @[scripts/diff_executions.py]: document `execution_ids`, `-o`, execution trace comparison, divergence calculation, and report generation.</action>
    <action>Enrich CLI documentation in @[scripts/reconcile_storage.py]: document `--check`, `--fix`, `--db-path`, `--storage-dir`, and CQRS storage consistency reconciliation.</action>
    <action>Enrich CLI documentation in @[scripts/run_e2e_variance_test.py]: document `inputs_target`, `--inputs`, `--workflow`, `--profile`, `--locale`, execution modes, and telemetry gathering.</action>
    <constraint invariant="standard_exit_codes">All scripts must standardize exit codes: 0 for clean success, 1 for domain/validation failure, 2 for CLI syntax error.</constraint>
  </step>

  <step id="5" name="PHASE 5: COMPREHENSIVE AUTOMATED CLI VERIFICATION SUITE">
    <action>[NEW] Create @[backend_v2/tests/unit/scripts/test_scripts_cli_help.py] containing parameterized pytest test cases covering all 25 scripts in `scripts/`:
      1. `test_all_scripts_respond_to_help_flag`: Iterates through all 25 scripts and verifies that invoking with `--help` and `-h` returns exit code 0.
      2. `test_all_scripts_emit_usage_and_description`: Asserts that stdout from `--help` contains `usage:`, non-empty description, and `options:` or `optional arguments:`.
      3. `test_scripts_help_execution_latency`: Asserts that running `--help` on any script completes in under 1000 milliseconds.
      4. `test_scripts_cli_invalid_argument_fails`: Parameterized test asserting that passing unknown flags (specifically `--invalid-test-flag-xyz`) results in exit code 2.
      5. `test_scripts_cli_zero_side_effects`: Asserts that running `--help` does not produce unstaged git changes or new files in `data/`, `backend_v2/seed/backups/`, or root directory.</action>
    <action>Run the automated test suite: `uv run pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py -v`.</action>
    <action>Run the global backend audit loop on modified scripts: `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py scripts/flutter_audit_loop.py scripts/_ast_guardrails.py scripts/audit_dict_eradication.py scripts/migrate_seed_contrastive_pairs.py scripts/matrix_slice_engine.py scripts/_ast_boundary_utils.py --test`.</action>
    <constraint invariant="zero_tolerance_audit_loop">All modified Python files must pass ruff check, ruff format, mypy --strict, and AST guardrails cleanly.</constraint>
  </step>
</execution_protocol>
```

---

## Universal Quality Gates & Anti-Happy-Path Verification Plan

### Test Scenarios & Expected Behavior

1. **Scenario 1: Safe Help Request on Mutating Script (Success Path)**
   - *Input:* `uv run python scripts/migrate_seed_contrastive_pairs.py --help`
   - *Expected Output:* Exit code 0, prints comprehensive description, options (`--seed-path`, `--dry-run`, `--backup-dir`), zero backup files created in `backend_v2/seed/backups/`, `seed_data.json` hash unchanged.

2. **Scenario 2: Safe Help Request on Heavy Quality Gate (Success Path)**
   - *Input:* `uv run python scripts/backend_audit_loop.py --help`
   - *Expected Output:* Exit code 0, execution completes in <500ms, prints 6-stage validation sequence documentation, does NOT execute `ruff`, `mypy`, `pytest`, or seed verification.

3. **Scenario 3: Safe Help Request on Flutter Quality Gate (Success Path)**
   - *Input:* `uv run python scripts/flutter_audit_loop.py --help`
   - *Expected Output:* Exit code 0, execution completes in <500ms, prints 5-stage Flutter quality gate documentation, does NOT invoke `dart` or `flutter`.

4. **Scenario 4: Direct Invocation of Matrix Slice Engine (Success Path)**
   - *Input:* `uv run python scripts/matrix_slice_engine.py --help`
   - *Expected Output:* Exit code 0, zero import errors (`ModuleNotFoundError`), prints descriptions of `--export`, `--audit-contamination`, `--theory-card`, `--patch`, `--explain`.

5. **Scenario 5: Unknown Argument Rejection (Negative Failure Path 1)**
   - *Input:* `uv run python scripts/backend_audit_loop.py --unsupported-flag-test`
   - *Expected Output:* Exit code 2, prints `error: unrecognized arguments: --unsupported-flag-test`, does NOT execute child quality gates.

6. **Scenario 6: Missing Required Argument on Strict Audit (Negative Failure Path 2)**
   - *Input:* `uv run python scripts/audit_markdown_boundaries.py` (without `--file`)
   - *Expected Output:* Exit code 2, prints `error: the following arguments are required: --file`.

7. **Scenario 7: Missing Target Arguments on AST Guardrails (Negative Failure Path 3)**
   - *Input:* `uv run python scripts/_ast_guardrails.py` (with no arguments)
   - *Expected Output:* Exit code 2, prints usage and states that target files or directories are required.
