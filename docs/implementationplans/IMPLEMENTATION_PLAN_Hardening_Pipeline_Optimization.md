<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Autonomous Hardening Pipeline & Audit Loop Performance Optimization (`IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md`)

## 1. Executive Summary & Objective

The current autonomous post-implementation hardening pipeline (`scripts/auto_hardening_runner.py`) requires approximately 12–18 minutes (750s–1080s) per target file. In a typical 5-target queue, this accumulates to 60–90 minutes of execution time.

Forensic runtime profiling identifies three primary latency bottlenecks:
1. **Ultra-Heavy AI Model Default**: `DEFAULT_BACKEND_AGENT_TEMPLATE` hardcodes `--model gemini-4-argon-high`. This ultra-high reasoning model generates thousands of deep chain-of-thought tokens per turn, consuming 60–70% (8–12 minutes) of total iteration duration on routine docstring, typing, and `__all__` export fixes.
2. **Double Universal Quality Gate Execution**: The 10-stage universal audit loop (`scripts/backend_audit_loop.py`) is executed twice per file (once by the subagent, once by the runner). Stages 6–10 (`audit_database_atoms.py`, `audit_clean_imports.py`, `audit_dto_parity.py`, `audit_warning_baseline.py`, and `audit_dict_eradication.py`) perform expensive repository-wide AST scans (~90–120 seconds per run) for every single isolated file.
3. **Logfire Network Telemetry in Local Unit Tests**: Unit test passes in `backend_audit_loop.py` default to `--logfire`, sending OpenTelemetry spans over the network on every test assertion during automated batch execution.

### Target Performance Goal
Reduce per-target hardening duration from **12–18 minutes down to 2–3.5 minutes** (a **5x speedup**) while preserving 100% of the Universal Quality Gate rigor, AST guardrails, and automated AI fixing.

---

## 2. 5-Column Architectural Directives Table & Pre-Implementation Debt Audit

### Pre-Implementation Technical Debt Audit (`scripts/audit_technical_debt.py`)
Deterministic technical debt scan across `@[scripts/auto_hardening_runner.py]`, `@[scripts/backend_audit_loop.py]`, and 1-hop callers returned **0 findings** (`Status: PASSED`). No pre-existing `getattr`/`hasattr`, `.get()`, silent `except:`, unvalidated `model_copy`, or untyped dict violations exist in the target files.

### 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **[MODIFY] `@[scripts/backend_audit_loop.py#L359-L593]`** | Running expensive whole-repository AST and seed scans (Stages 5–10) and network Logfire span exports on every isolated single-file iteration | Add `--micro` (`--fast`) flag to `main`; wrap Stages 5–10 in `if not args.micro:`; resolve `use_logfire = args.logfire if args.logfire is not None else (not args.micro)` so `--micro` suppresses Logfire by default while honoring explicit `--logfire` | Do NOT alter `run_tests_with_strict_coverage` signature or create a separate audit script; reuse `logfire: bool` parameter already present on `run_tests_with_strict_coverage` | `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --test --ast-strict` |
| **[MODIFY] `@[scripts/auto_hardening_runner.py#L131-L177]`** | Hardcoding `--model gemini-4-argon-high` in `DEFAULT_BACKEND_AGENT_TEMPLATE` and `DEFAULT_FRONTEND_AGENT_TEMPLATE` without CLI or DTO parameterization | Parameterize both `DEFAULT_BACKEND_AGENT_TEMPLATE` and `DEFAULT_FRONTEND_AGENT_TEMPLATE` with `--model {model}`; extend HardeningRunnerArgsDTO (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `model: str = "gemini-4-argon-medium"` and `micro_audit: bool = True` | Prune speculative model routing tables or dynamic token-counting heuristics; use a single deterministic `--model` CLI choice list | `ValidationError` on invalid DTO types; `test_default_model_selection_medium` and `test_cli_model_override` |
| **[MODIFY] `@[scripts/auto_hardening_runner.py#L584-L669]`** | Referencing undeclared `args` inside `run_quality_gate` or omitting `{model}` interpolation in `execute_subagent_pass` | Interpolate `model=args.model` in `execute_subagent_pass`; add `micro_audit: bool = False` keyword parameter to `run_quality_gate` and pass `micro_audit=args.micro_audit` from `process_target_with_retries` | Prune speculative dirty-check pre-format skipping; `ruff check --fix` and `ruff format` on a single target take <0.2s and guarantee clean formatting post-subagent | `test_micro_audit_dispatch_and_flags` and `mypy --strict` verification |
| **[MODIFY] `@[scripts/auto_hardening_runner.py#L979-L1103]`** | Skipping repository-wide checks (Stages 5–10) during per-file micro-audits without a final completion gate, risking cross-file regressions | Implement `run_macro_quality_gate` (exported in `__all__`) and invoke it once across all hardened `.py` targets at the end of `run_hardening_pipeline` when `args.micro_audit` is `True`; expose `--model` and `--no-micro` in `main` | Do NOT re-run macro-audit per file or when 0 backend targets succeeded | If `run_macro_quality_gate` returns `success=False`, increment `failure_count` so `main` exits with code `1` (`test_macro_audit_completion_gate_failure`) |
| **[MODIFY] `@[scripts/auto_hardening_runner.py#L290-L344]`** | Brittle regex in `parse_tracker_unhardened_targets` and `mark_tracker_target_done` failing when backticks wrap `[NEW]` or `[MODIFY]` tags (`- [ ] \`[NEW] @[...]\``) | Update regex patterns in `parse_tracker_unhardened_targets` and `mark_tracker_target_done` to accept optional backticks before and after `[NEW\|MODIFY\|DELETE]` tags | Do NOT add a third-party Markdown AST parser dependency | Fail-Fast `ValueError` in `fetch_unhardened_targets` on unparseable pending items; `test_resilient_backtick_tracker_parsing` |
| **[MODIFY] `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L843-L888]`** | Leaving unit test mocks unaligned with `run_macro_quality_gate` or testing only happy-path CLI flags | Mock `run_macro_quality_gate` in pipeline unit tests and add positive and negative ISTQB boundary tests across both `test_auto_hardening_runner.py` and `test_backend_audit_loop.py` | Zero external subprocess calls in unit tests; 100% hermetic `monkeypatch` / `unittest.mock.patch` | `>=90%` line coverage enforced by `backend_audit_loop.py --test --ast-strict` |

---

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Add Micro-Audit Mode to backend_audit_loop.py">
    <constraint invariant="universal_quality_gate">Micro-audit mode MUST strictly enforce Ruff lint, Ruff format, MyPy strict typing, AST codebase guardrails, and target unit tests with >=90% line coverage; only repository-wide scans (Stages 5-10) are deferred to the macro-gate.</constraint>
    <action>
      1. In `@[scripts/backend_audit_loop.py#L359-L593]`, add `--micro` (alias: `--fast`) argument to `argparse`:
         `parser.add_argument("--micro", "--fast", dest="micro", action="store_true", default=False, help="Execute fast targeted audit loop for single-file iterations (Stages 1-4 + unit tests), deferring whole-repository scans (Stages 5-10) to the macro completion gate.")`
      2. In `@[scripts/backend_audit_loop.py#L359-L593]`, change the `--logfire` argument `default` from `True` to `None` and compute `use_logfire = args.logfire if args.logfire is not None else (not args.micro)` so `--micro` automatically disables Logfire network telemetry unless `--logfire` is explicitly passed on the CLI. Pass `logfire=use_logfire` into `run_tests_with_strict_coverage(target, logfire=use_logfire)`.
      3. In `@[scripts/backend_audit_loop.py#L359-L593]`, wrap Stages 5 through 10 in `if not args.micro:`:
         - Stage 5: Jinja Dumb Painter template validation
         - Stage 6: Seed data dry-run and atom audit
         - Stage 7: Clean imports audit
         - Stage 8: DTO parity audit
         - Stage 9: Warning baseline ledger audit
         - Stage 10: Dict eradication audit
         When `args.micro` is `True`, print a clear status line: `print("\n⚡ Micro-audit mode active (--micro): Skipping whole-repository Stages 5-10.")`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --micro` and verify it completes in under 5 seconds with 0 errors.</verification>
  </step>

  <step id="2" name="Add Model Selection and Two-Tier Auditing to auto_hardening_runner.py">
    <constraint invariant="circuit_breaker">Every target iteration MUST retain git snapshot rollback and atomic checkpointing invariants, and the queue MUST execute a final macro-audit across all hardened backend files when micro_audit is enabled.</constraint>
    <action>
      1. In `@[scripts/auto_hardening_runner.py]`, update both `DEFAULT_BACKEND_AGENT_TEMPLATE` and `DEFAULT_FRONTEND_AGENT_TEMPLATE` to use the `{model}` placeholder, and export `"run_macro_quality_gate"` in `__all__`:
         - `DEFAULT_BACKEND_AGENT_TEMPLATE: Final[str] = 'agy --model {model} --dangerously-skip-permissions --print "/tier2-hardening-backend @" + "[{target}]"'`
         - `DEFAULT_FRONTEND_AGENT_TEMPLATE: Final[str] = 'agy --model {model} --dangerously-skip-permissions --print "/tier2-hardening-frontend @" + "[{target}]"'`
      2. In `@[scripts/auto_hardening_runner.py#L131-L177]`, update HardeningRunnerArgsDTO:
         - Add `model: Annotated[str, Field(default="gemini-4-argon-medium", description="AI model identifier for subagent hardening iterations.")] = "gemini-4-argon-medium"`
         - Add `micro_audit: Annotated[bool, Field(default=True, description="Use fast micro-audit during per-target iterations and run macro-audit at completion.")] = True`
      3. In `@[scripts/auto_hardening_runner.py#L584-L669]`, update `execute_subagent_pass` to format `subagent_template` with `model=args.model, target=target_file, target_file=target_file`.
      4. In `@[scripts/auto_hardening_runner.py#L672-L717]`, add `micro_audit: bool = False` keyword parameter to `run_quality_gate`:
         When `micro_audit` is `True` on a backend target, append `["--micro", "--no-logfire"]` to the `backend_audit_loop.py` command.
         Also define `run_macro_quality_gate(targets: list[str], timeout_seconds: int, repo_root: Path | None = None)` (`#L720-L752`) returning QualityGateResultDTO immediately after `run_quality_gate` to run `["uv", "run", "python", "scripts/backend_audit_loop.py", *targets, "--test", "--ast-strict"]` via `execute_subprocess_with_tree_kill`.
      5. In `@[scripts/auto_hardening_runner.py#L919-L976]`, update `process_target_with_retries` to pass `micro_audit=args.micro_audit` into `run_quality_gate`.
      6. In `@[scripts/auto_hardening_runner.py#L979-L1103]`, update `run_hardening_pipeline`:
         - In `--dry-run` output, include `--micro --no-logfire` in the planned backend command when `args.micro_audit` is `True`.
         - After the target iteration loop finishes, collect `successful_backend_targets = [it.target_file for it in iterations if it.success and it.target_file.endswith(".py")]`.
         - If `args.micro_audit and successful_backend_targets and (failure_count == 0 or args.continue_on_failure)`: execute `macro_res = run_macro_quality_gate(successful_backend_targets, args.timeout_seconds, repo_root=root)`. If `not macro_res.success`, increment `failure_count` by 1 and print diagnostic error output so `main` exits with code 1.
      7. In `@[scripts/auto_hardening_runner.py#L1106-L1263]`, add CLI arguments in `main` and pass them into HardeningRunnerArgsDTO:
         - `--model`: choices `["gemini-4-argon-medium", "gemini-4-argon-high", "gemini-3.8-flash-high", "gemini-3.8-flash"]`, default `"gemini-4-argon-medium"`
         - `--no-micro`: `action="store_false"`, `dest="micro_audit"`, default `True`
    </action>
    <verification>Run `uv run python scripts/auto_hardening_runner.py --targets scripts/auto_hardening_runner.py --dry-run` and inspect planned commands.</verification>
  </step>

  <step id="3" name="Make Tracker Target Parsing Resilient to Backticks and Quoting">
    <constraint invariant="deterministic_hardening_state">Target resolution MUST correctly parse checklist items regardless of whether backticks wrap the tag, the path, or both.</constraint>
    <action>
      1. In `@[scripts/auto_hardening_runner.py#L290-L344]`, update `item_pattern` regex in `parse_tracker_unhardened_targets` to tolerate backticks preceding or wrapping `[NEW]`, `[MODIFY]`, or `[DELETE]`:
         `r"^\s+-\s*\[ \]\s*(?:`?\[(?:NEW|MODIFY|DELETE)\]\s*`?)?`?(?:@\[?([a-zA-Z0-9_/\\.-]+?)(?:#[^`\]\n]+)?\]|([a-zA-Z0-9_.-]+(?:[/\\][a-zA-Z0-9_.-]+)*\.[a-zA-Z0-9]+(?:#[^`\]\n]+)?))`?"`
      2. In `@[scripts/auto_hardening_runner.py#L380-L425]`, update `pattern` in `mark_tracker_target_done`:
         `rf"^(\s+-\s*)\[ \](\s*(?:`?\[(?:NEW|MODIFY|DELETE)\]\s*`?)?`?@?\[?{escaped_target}(?:#[^`\]\n]+)?\]?`?.*)$"`
    </action>
    <verification>Run unit test `test_resilient_backtick_tracker_parsing_and_marking` in `backend_v2/tests/unit/scripts/test_auto_hardening_runner.py`.</verification>
  </step>

  <step id="4" name="Expand Unit Test Suites in test_auto_hardening_runner.py and test_backend_audit_loop.py">
    <constraint invariant="test_directory_isolation">All unit tests MUST reside under backend_v2/tests/unit/scripts/ with >=90% line coverage and zero unmocked subprocess executions.</constraint>
    <action>
      1. In `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L843-L888]`, monkeypatch `run_macro_quality_gate` to return a passing QualityGateResultDTO (`success=True, output="Macro OK", exit_code=0`) so hermetic pipeline tests do not spawn real subprocesses.
      2. In `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L943-L994]`, add unit tests covering positive and negative partitions:
         - `test_default_model_selection_medium_and_cli_override`: Verifies default `model="gemini-4-argon-medium"` and `--model gemini-3.8-flash-high` formatting in `execute_subagent_pass`.
         - `test_micro_audit_dispatch_and_no_micro_flag`: Verifies `run_quality_gate` appends `--micro --no-logfire` when `micro_audit=True` and omits them when `micro_audit=False` (`--no-micro`).
         - `test_macro_audit_completion_gate_success_and_failure`: Verifies `run_macro_quality_gate` runs once across hardened backend targets at queue completion, and increments `failure_count` when macro-audit fails or times out (negative case).
         - `test_resilient_backtick_tracker_parsing_and_marking`: Verifies parsing and in-place `[x]` marking of backtick-wrapped items with tags and anchors.
      3. In `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py#L674-L690]`, add unit tests for `--micro` mode:
         - `test_backend_audit_loop_micro_mode_skips_stages_5_to_10_and_disables_logfire`: Verifies `--micro` executes Stages 1-4 and `run_tests_with_strict_coverage(..., logfire=False)` while skipping Stages 5-10.
         - `test_backend_audit_loop_micro_mode_explicit_logfire_override`: Verifies `--micro --logfire` preserves `logfire=True`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py scripts/backend_audit_loop.py --test --ast-strict`.</verification>
  </step>
</execution_protocol>
```

---

## 4. Test Scenarios & Quality Gates

### Scenario 1 (Positive): Fast Single-Target Hardening with Medium Model
- **Input**: `uv run python scripts/auto_hardening_runner.py --targets scripts/auto_hardening_runner.py --model gemini-4-argon-medium --dry-run`
- **Expected Output**:
  - Subagent template formats with `--model gemini-4-argon-medium`.
  - Audit command formats with `--micro --no-logfire`.
  - Exit code: 0.

### Scenario 2 (Negative / Boundary): Subagent Startup Error Retry Loop
- **Input**: Subagent fails with transient error `"connection refused"`.
- **Expected Output**:
  - `_is_transient_subagent_startup_error` returns True.
  - Subagent retries with exponential backoff up to 3 attempts.
  - Circuit breaker preserves working tree if non-transient failure occurs.

### Scenario 3 (Negative / Invariant): Universal Macro-Audit Failure Gate
- **Input**: Micro-audits pass on individual targets, but global cross-file check (specifically: circular import or seed dry-run) fails during final macro-audit.
- **Expected Output**:
  - Macro-audit exits with non-zero code.
  - `run_hardening_pipeline` marks run summary with failure.
  - Error diagnostic instructions printed clearly.

---

## 5. Verification Commands

1. **Local Micro-Audit Verification**:
   ```powershell
   uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --micro
   ```
2. **Full Test Suite & Quality Gate**:
   ```powershell
   uv run python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py --test --ast-strict
   uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --test --ast-strict
   ```
3. **Markdown Boundary Verification**:
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md
   ```
