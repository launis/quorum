# Implementation Plan: Headless CLI Hardening Runner (Overnight Multi-Process Pipeline)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

## Objective
Implement an autonomous, multi-process CLI runner [NEW] @[scripts/auto_hardening_runner.py] that orchestrates unattended "overnight" Post-Implementation Hardening (Tier 2 Backend and Frontend). By decoupling file queue discovery via native tracker markdown checklist extraction, clean-process subagent invocation with Windows process tree termination, deterministic audit loop quality gates, persistent JSON state synchronization per @[ki_deterministic_hardening_state.md], and atomic git checkpointing, this pipeline eliminates Context Amnesia and token saturation across massive multi-file queues (specifically EPIC 158's 45 backend and 11 frontend files) with zero human intervention and 100% fail-fast circuit breaking.

## Proposed Changes

### Target Boundaries
| Action | File Path | Scope Description |
| :--- | :--- | :--- |
| `[NEW]` | [NEW] @[scripts/auto_hardening_runner.py] | Single Source of Truth (SSOT) CLI runner orchestrating unattended overnight hardening across isolated subagent processes with audit verification, circuit breaking, and atomic git checkpointing. |
| `[NEW]` | [NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py] | Comprehensive unit and ISTQB negative test suite verifying target queue discovery, audit verification loops, retry circuit breakers, git commit checkpointing, and dry-run safety. |

### Context Boundaries (Read-Only SSOT References)
| Role | File Path | Purpose |
| :--- | :--- | :--- |
| `[CONTEXT]` | @[scripts/_script_base.py#L19-L25] | Base infrastructure function `get_repo_root` resolving the repository root directory. |
| `[CONTEXT]` | @[scripts/_script_base.py#L28-L51] | Base infrastructure function `setup_script_environment` configuring UTF-8 standard streams and `sys.path`. |
| `[CONTEXT]` | @[scripts/_script_base.py#L61-L69] | Base infrastructure class `ANSIColors` providing standardized terminal escape codes. |
| `[CONTEXT]` | @[scripts/backend_audit_loop.py#L359-L577] | Universal Quality Gate entrypoint `main` for backend Python targets enforcing Ruff formatting, MyPy strict typing, and AST strict guardrails. |
| `[CONTEXT]` | @[scripts/flutter_audit_loop.py#L25-L170] | Universal Quality Gate entrypoint `main` for Flutter client targets enforcing Dart formatting, analysis, and Freezed model generation. |
| `[CONTEXT]` | @[scripts/_ast_guardrails.py#L2305-L2333] | AST static guardrail scanner `scan_files_for_guardrails` enforcing structural domain rules (`QGR000`-`QGR029`) and fault isolation across `scripts/`. |
| `[CONTEXT]` | @[.agents/rules/04_directory_reference.md] | Architectural directory map and script indexing governance. |
| `[CONTEXT]` | @[ki_deterministic_hardening_state.md] | Knowledge Item governing file-granular hardening checklists and state persistence. |
| `[CONTEXT]` | @[ki_god_code_prevention.md] | Knowledge Item governing Single Responsibility Principle and modular script architecture. |
| `[CONTEXT]` | @[ki_epic_lifecycle_workflow.md] | Knowledge Item governing Epic and Standalone Plan tracker lifecycles. |

### 5-Column Architectural Directive Table
| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **[NEW] @[scripts/auto_hardening_runner.py]** | Banned phantom external script dependencies (`scripts/tracker_manager.py`), anonymous state tuples (`tuple[bool, str]`, `tuple[bool, bool]`), shell command concatenation in subprocess (`shell=True`), hardcoded numeric literal `timeout=30` keyword arguments in `subprocess` calls (triggers fatal `QGR008`), `json.loads` combined with `isinstance(..., dict)` duck-typing checks (triggers fatal `QGR012`), duplicate `= Field(...)` assignments on PEP 593 `Annotated` fields (triggers fatal `QGR020` and `audit_dict_eradication.py`), broad `except Exception:` blocks without re-raising or returning a typed DTO (triggers fatal `QGR003`), orphaned dangling child processes on Windows 11 after timeout, partial rollbacks ignoring dirty collateral test files or touching `data/db_v2.json` or `hardening_state.json`, unannotated dictionary mutation accumulators (`state = {}`), ad-hoc `.get()` calls without schema validation, silent `except Exception: pass` error suppression on audit failures, and untracked bulk git commits (`git add .`). | Enforce 100% Pydantic V2 DTOs (creating `HardeningRunnerArgsDTO`, `HardeningIterationResultDTO`, `HardeningRunSummaryDTO`, `QualityGateResultDTO`, `CheckpointResultDTO`, `WorkspaceSnapshotDTO`, `HardeningStateFileDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated[T, Field(...)]` syntax without duplicate `= Field(...)`, plus `HardeningGate(StrEnum)` and explicit module-level `__all__` export list). Reuse `setup_script_environment`, `get_repo_root`, and `ANSIColors` from `@[scripts/_script_base.py#L19-L25]`, `@[scripts/_script_base.py#L28-L51]`, and `@[scripts/_script_base.py#L61-L69]`. Pass named timeout constants (`GIT_SUBPROCESS_TIMEOUT_SECONDS: Final[int] = 30`, `TASKKILL_TIMEOUT_SECONDS: Final[int] = 15`, `FORMATTER_TIMEOUT_SECONDS: Final[int] = 60`, `DEFAULT_AUDIT_TIMEOUT_SECONDS: Final[int] = 600`) or `args.timeout_seconds` to satisfy `QGR008`. Parse JSON state file (`hardening_state.json`) via `HardeningStateFileDTO.model_validate_json()` to satisfy `QGR012` and `ki_deterministic_hardening_state.md`. Direct argument vectors without shell concatenation (`shell=False`). Fail-Fast when neither `--tracker` nor `--targets` nor `--state-file` is specified. Native markdown checklist discovery (`parse_tracker_unhardened_targets`) and in-place checkbox marking (`mark_tracker_target_done`). Windows process tree termination helper (`execute_subprocess_with_tree_kill`) executing `taskkill /F /T /PID` before parent teardown on timeout. Workspace snapshot diff restoration restoring all tracked files modified during the attempt (strictly excluding `data/db_v2.json` and `hardening_state.json`) and cleaning untracked files. Execute atomic git commits (`git add <target> [<tracker>] ; git commit -m "refactor(hardening): tighten <basename>"`) strictly upon verified exit code 0. | Prune speculative external companion script `scripts/tracker_manager.py` and intermediate IPC hops in favor of pure, single-responsibility native tracker parsing functions (`parse_tracker_unhardened_targets`, `mark_tracker_target_done`). Prune multiprocessing process pools or Celery background queues in favor of deterministic sequential subprocess execution (`subprocess.Popen`). Prune complex custom IPC protocols in favor of standard CLI argument passing and JSON serialization. Prune interactive TTY subagent prompts; maintain strict non-interactive execution templates. | `uv run python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py --test --ast-strict` proving zero Ruff errors, zero MyPy strict errors, zero `audit_dict_eradication.py` findings, and AST guardrail compliance (`QGR000`-`QGR029`). Exit code 1 on quality gate failure. |
| **[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]** | Banned tautological mocking asserting static return values, happy-path-only testing omitting negative partitions, unverified file mutations without isolated `tmp_path` fixtures, and omitting dirty workspace rollback tests. | Comprehensive unit test suite using pytest, `unittest.mock.patch("subprocess.Popen")`, and `tmp_path` fixture. Verifies native tracker discovery, successful audit mark-done loops, retry exhaustion with Circuit Breaker workspace rollback, gate routing (`backend` vs `frontend`), max-files batch capping, timeout process tree termination via `taskkill`, and dry-run safety. Full ISTQB negative boundary partition testing covering missing tracker files, missing targets fail-fast, invalid gate arguments, malformed JSON state payloads, subprocess timeouts, and non-zero exit codes. | Prune live external agent CLI calls during unit tests in favor of deterministic `subprocess.Popen` mocks asserting command line structures, stdout/stderr parsing, and exit code handling. | `uv run pytest backend_v2/tests/unit/scripts/test_auto_hardening_runner.py -v` asserting 100% pass across positive and negative contracts (`TC-AHR-001` through `TC-AHR-014`). |

---

```xml
<execution_protocol>
  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  </required_context_rules>

  <test_contracts>
    <contract id="TC-AHR-001" type="positive" name="test_fetch_unhardened_targets_from_tracker_markdown">
      <description>Verify that fetch_unhardened_targets parses unchecked checklist items from tracker markdown file for the specified gate via parse_tracker_unhardened_targets.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Returns matching list of target relative paths.</expected>
    </contract>
    <contract id="TC-AHR-002" type="positive" name="test_fetch_explicit_targets_override">
      <description>Verify that explicit targets passed via CLI override tracker discovery without reading the tracker file.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Returns explicit targets list directly.</expected>
    </contract>
    <contract id="TC-AHR-003" type="positive" name="test_successful_backend_audit_marks_tracker_and_commits">
      <description>Verify that an iteration with backend_audit_loop returning exit code 0 triggers mark_tracker_target_done in-place and atomic git commit.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>git commit and tracker checkmark executed, iteration result marked success=True.</expected>
    </contract>
    <contract id="TC-AHR-004" type="positive" name="test_failed_audit_triggers_retry_and_circuit_breaker">
      <description>Verify that when audit loop fails across all retries, the Circuit Breaker executes workspace rollback and marks success=False.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Workspace snapshot rollback executed, zero commits made, fail-fast halts execution.</expected>
    </contract>
    <contract id="TC-AHR-005" type="positive" name="test_frontend_gate_invokes_flutter_audit_loop">
      <description>Verify that specifying gate=HardeningGate.FRONTEND invokes flutter_audit_loop.py instead of backend_audit_loop.py.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Subprocess executes flutter_audit_loop with --build flag.</expected>
    </contract>
    <contract id="TC-AHR-006" type="positive" name="test_dry_run_mode_produces_zero_side_effects">
      <description>Verify that --dry-run prints target queue and planned audit commands without executing subprocesses or mutating git state.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Zero mutation subprocess calls, exit code 0.</expected>
    </contract>
    <contract id="TC-AHR-007" type="positive" name="test_max_files_batch_capping">
      <description>Verify that --max-files 2 processes exactly 2 targets from a queue of 10 remaining targets and stops cleanly.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Processed count equals 2, 8 targets remaining un-executed.</expected>
    </contract>
    <contract id="TC-AHR-008" type="negative" name="test_nonexistent_tracker_file_fails_fast">
      <description>Verify that providing a nonexistent tracker file path triggers immediate validation failure and exit code 1.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Exit code 1 with descriptive error message.</expected>
    </contract>
    <contract id="TC-AHR-009" type="negative" name="test_invalid_gate_argument_rejected">
      <description>Verify that passing an unsupported gate string triggers argparse or Pydantic validation error.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>CLI argument parsing error with nonzero exit code.</expected>
    </contract>
    <contract id="TC-AHR-010" type="positive" name="test_custom_agent_command_template_formatting">
      <description>Verify that providing --agent-cmd template formats target and executes clean agent sub-process prior to audit loop.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Subprocess executes custom agent command with target substituted.</expected>
    </contract>
    <contract id="TC-AHR-011" type="negative" name="test_missing_targets_fails_fast">
      <description>Verify that invoking the runner without --tracker, --targets, or --state-file triggers immediate fail-fast with exit code 1 and actionable diagnostic guidance.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Exit code 1 with descriptive missing targets error message.</expected>
    </contract>
    <contract id="TC-AHR-012" type="negative" name="test_subprocess_timeout_triggers_tree_kill_and_circuit_breaker">
      <description>Verify that a subprocess timeout triggers process tree termination via taskkill on Windows, records failure in iteration result, and initiates workspace rollback.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Subprocess timeout handled cleanly without orphaned processes, iteration result marked failure.</expected>
    </contract>
    <contract id="TC-AHR-013" type="positive" name="test_workspace_snapshot_restores_collateral_modifications">
      <description>Verify that when an attempt introduces collateral modifications to companion files, the Circuit Breaker restores all tracked files in the snapshot diff while strictly preserving data/db_v2.json and hardening_state.json.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Working directory restored to pre-attempt clean state with data/db_v2.json and hardening_state.json untouched.</expected>
    </contract>
    <contract id="TC-AHR-014" type="positive" name="test_state_file_discovery_and_persistence">
      <description>Verify that providing --state-file reads hardening_state.json, computes REMAINING = TARGETS - DONE, and persists completed files upon successful audit verification.</description>
      <target>[NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]</target>
      <expected>Remaining targets computed correctly, state file updated atomically upon completion.</expected>
    </contract>
  </test_contracts>

  <step id="1" name="Phase 1: Pre-Implementation Cleanups">
    <action>In [NEW] @[scripts/auto_hardening_runner.py]: Execute pre-flight technical debt audit via uv run python scripts/audit_technical_debt.py --targets scripts/_script_base.py --include-one-hop to verify clean 1-hop dependency foundations before writing code.</action>
    <action>In [NEW] @[scripts/auto_hardening_runner.py]: Verify that @[scripts/_script_base.py#L19-L25] (get_repo_root), @[scripts/_script_base.py#L28-L51] (setup_script_environment), and @[scripts/_script_base.py#L61-L69] (ANSIColors) are imported cleanly without circular dependencies.</action>
    <action>In [NEW] @[scripts/auto_hardening_runner.py]: Verify fail-fast boundary enforcement: when neither --tracker, --targets, nor --state-file is specified, runner halts fail-fast with exit code 1.</action>
    <constraint invariant="zero_backward_compatibility_planning_ban">No legacy fallback logic or deprecated path parsing allowed.</constraint>
  </step>

  <step id="2" name="Phase 2: Domain DTOs &amp; Argument Architecture">
    <action>
      In [NEW] @[scripts/auto_hardening_runner.py]:
      Declare module-level __all__ export list and named timeout constants (GIT_SUBPROCESS_TIMEOUT_SECONDS: Final[int] = 30, TASKKILL_TIMEOUT_SECONDS: Final[int] = 15, FORMATTER_TIMEOUT_SECONDS: Final[int] = 60, DEFAULT_AUDIT_TIMEOUT_SECONDS: Final[int] = 600) to comply with QGR008 and audit_dict_eradication.py.
      Define typed Pydantic V2 state models using PEP 593 Annotated[T, Field(...)] syntax without duplicate = Field(...) assignments (QGR020):
      1. HardeningGate(StrEnum): BACKEND = "backend", FRONTEND = "frontend".
      2. HardeningRunnerArgsDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating tracker, state_file, gate, targets, max_files, max_retries, timeout_seconds, agent_cmd, no_auto_fix, fail_fast, continue_on_failure, dry_run, and verbose fields.
      3. HardeningIterationResultDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating target_file, gate, success, attempts, duration_seconds, error_message, git_committed, and tracker_marked fields.
      4. HardeningRunSummaryDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating total_targets, processed_count, success_count, failure_count, skipped_count, and iterations fields.
      5. QualityGateResultDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating success, output, and exit_code fields (eradicating anonymous tuple[bool, str]).
      6. CheckpointResultDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating tracker_marked, state_file_updated, and git_committed fields (eradicating anonymous tuple[bool, bool]).
      7. WorkspaceSnapshotDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating modified_files and untracked_files lists for deterministic rollback diffs.
      8. HardeningStateFileDTO(BaseModel): ConfigDict(strict=True, extra="forbid", frozen=True) encapsulating targets and done string lists per ki_deterministic_hardening_state.md schema.
    </action>
    <constraint invariant="the_zero_compromise_pledge">All models must enforce 100% strict Pydantic V2 typing with ConfigDict(strict=True, extra="forbid", frozen=True), PEP 593 Annotated fields (QGR020), and zero naked dictionaries or anonymous state tuples.</constraint>
  </step>

  <step id="3" name="Phase 3: Queue Discovery &amp; Execution Pipeline Implementation">
    <action>
      In [NEW] @[scripts/auto_hardening_runner.py]:
      Implement core operational pipeline functions with zero literal timeout kwargs (pass named constants GIT_SUBPROCESS_TIMEOUT_SECONDS, TASKKILL_TIMEOUT_SECONDS, FORMATTER_TIMEOUT_SECONDS, or args.timeout_seconds per QGR008) and specific typed exception handlers (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError, ValidationError per QGR003):
      1. parse_tracker_unhardened_targets(tracker_content: str, gate: HardeningGate) -> list[str]: parses unchecked checklist items under the gate section (Tier 2 Hardening (Backend) or Tier 2 Hardening (Frontend)) directly using regex without external dependencies.
      2. mark_tracker_target_done(tracker_path: Path, target_file: str) -> bool: replaces the unchecked markdown checkbox with checked status in-place, updating the parent section checkbox if all child items are verified.
      3. fetch_unhardened_targets(args: HardeningRunnerArgsDTO) -> list[str]: resolves targets from explicit overrides, or parses tracker markdown checklist via parse_tracker_unhardened_targets, or reads hardening_state.json computing REMAINING = TARGETS - DONE.
      4. execute_subprocess_with_tree_kill(cmd: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]: invokes subprocess.Popen with shell=False, and upon TimeoutExpired, deterministically terminates the Windows process tree via taskkill /F /T /PID before parent cleanup.
      5. execute_subagent_pass(target_file: str, args: HardeningRunnerArgsDTO) -> bool: executes optional headless agent subprocess via shlex.split with shell=False or pre-audit automated formatting passes (ruff check --fix, ruff format for backend; dart format for frontend).
      6. run_quality_gate(target_file: str, gate: HardeningGate, timeout_seconds: int) -> QualityGateResultDTO: executes @[scripts/backend_audit_loop.py#L359-L577] (--test --ast-strict) or @[scripts/flutter_audit_loop.py#L25-L170] (--build) with timeout=timeout_seconds, capturing exit status and handling timeout process tree termination.
      7. capture_workspace_snapshot() -> WorkspaceSnapshotDTO: queries git status --porcelain with timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS to capture baseline modified and untracked file state before an attempt.
      8. execute_circuit_breaker_rollback(snapshot: WorkspaceSnapshotDTO, target_file: str) -> None: executes git restore on target and all collateral files modified during the attempt (strictly excluding data/db_v2.json and hardening_state.json) and removes newly introduced untracked files to guarantee workspace cleanliness.
      9. mark_tracker_and_checkpoint(target_file: str, tracker_path: Path | None, state_file: Path | None) -> CheckpointResultDTO: updates tracker markdown in-place, updates state_file JSON if provided, and executes atomic git commit (git add <target> [<tracker>] ; git commit -m "refactor(hardening): tighten <basename>") using direct argument vectors without shell concatenation (shell=False).
      10. process_target_with_retries(target_file: str, args: HardeningRunnerArgsDTO) -> HardeningIterationResultDTO: orchestrates retry loop, timeout handling, and snapshot rollback.
      11. run_hardening_pipeline(args: HardeningRunnerArgsDTO) -> HardeningRunSummaryDTO: main orchestrator processing the queue and printing ANSI summary tables.
      12. main(argv: list[str] | None = None) -> int: CLI entrypoint parsing arguments and invoking pipeline.
    </action>
    <constraint invariant="atomic_checkpoint_mandate">Atomic git commit must be executed per verified target file strictly upon quality gate pass.</constraint>
    <constraint invariant="single_pipeline_invariant_mandate">All executions flow through the single sovereign pipeline with zero branching into permissive fallback paths.</constraint>
  </step>

  <step id="4" name="Phase 4: Comprehensive Unit Test Suite">
    <action>
      In [NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]:
      Implement comprehensive unit and ISTQB negative test suite:
      1. Positive tests for native tracker discovery via parse_tracker_unhardened_targets, backend audit loop pass, flutter audit loop pass, atomic git commit, tracker mark-done, max-files capping, and workspace snapshot restoration preserving data/db_v2.json and hardening_state.json.
      2. Negative tests for audit failure retry exhaustion, Circuit Breaker rollback, nonexistent tracker paths, missing targets fail-fast, unsupported gate enums, malformed JSON state payloads, and subprocess timeouts with process tree termination.
      3. Dry-run safety test asserting zero side effects on git and tracker files.
      4. State file persistence test verifying REMAINING = TARGETS - DONE computation and atomic state file updates.
    </action>
    <constraint invariant="anti_happy_path_mandate">At least 4 negative and boundary test cases must be implemented with concrete assertions on failure handling.</constraint>
  </step>

  <step id="5" name="Phase 5: Quality Gate Verification">
    <action>In [NEW] @[scripts/auto_hardening_runner.py]: Run uv run python scripts/backend_audit_loop.py scripts/auto_hardening_runner.py --test --ast-strict to verify strict AST guardrail compliance (QGR000-QGR029), zero audit_dict_eradication.py violations, zero Ruff errors, and zero MyPy strict errors.</action>
    <action>In [NEW] @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]: Run uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/scripts/test_auto_hardening_runner.py --test --ast-strict to verify 100% test pass rate and test file AST compliance across positive and negative contracts.</action>
    <constraint invariant="zero_tolerance_audit_loop">100% of quality gate checks must pass without warnings or type suppressions.</constraint>
  </step>
</execution_protocol>
