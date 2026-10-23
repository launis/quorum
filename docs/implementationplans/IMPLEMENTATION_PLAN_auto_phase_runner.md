<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Autonomous Headless CLI Phase Orchestrator (`scripts/auto_phase_runner.py`)

## 1. Executive Summary & Objective
Create an autonomous headless phase orchestrator `[NEW] @[scripts/auto_phase_runner.py]` that automates the unattended, sequential execution of multi-phase implementation trackers (`docs/epic/EPIC_XXX_tracker.md`, `docs/epic/*_decomposition_tracker.md`, and `docs/implementationplans/TRACKER_*.md`). 

The orchestrator:
1. Discovers and parses phase definitions from the tracker document (supporting both multi-phase Epic topology and single-phase Standalone Plan topology).
2. Iterates through pending (`[ ]`) phases, launching an isolated `agy` CLI subagent process for each phase with Gemini 4 Argon (High) and continuous full-auto permission authorization.
3. Streams live execution logs and thought telemetry directly to the console.
4. Executes the mandatory Universal Quality Gate (`backend_audit_loop.py`) upon phase completion, failing fast on any regression.
5. Performs atomic git checkpoint commits per completed phase, updating tracker checkmarks in-place.
6. Seamlessly hands off to `scripts/auto_hardening_runner.py` upon completion of all phases for Epoch 2 post-implementation hardening (supporting optional `--hardening-agent` to dispatch full AI-driven `/tier2-hardening-backend` subagents per target file).

---

## 2. Target Boundaries & Scope

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[scripts/auto_phase_runner.py]` | Core autonomous headless CLI phase orchestrator executable. |
| `[MODIFY]` | `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]` | Register `auto_phase_runner.py` in `ALL_SCRIPTS` list and update total script assertion count from 35 to 36 in `test_script_count_is_exhaustive`. |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/scripts/test_auto_phase_runner.py]` | Comprehensive unit test suite with mock `agy` subprocesses, tracker parsing fixtures, circuit breaking, and dry-run validation. |
| `[CONTEXT]` | `@[scripts/auto_hardening_runner.py]` | Reference implementation for subprocess tree killing, workspace snapshots, and tracker checkbox updates. |
| `[CONTEXT]` | `@[scripts/audit_tracker_output.py]` | Reference implementation for tracker phase regex extraction and structural validation. |
| `[CONTEXT]` | `@[docs/epic/matrix_domain_parser_decomposition_tracker.md]` | Test fixture target for multi-phase God Code decomposition tracker. |

---

## 3. Pre-Implementation Technical Debt Cleanups
- `audit_technical_debt.py` scanned `test_scripts_cli_help.py` and reported **0 technical debt items**. Clean baseline confirmed.

---

## 4. Five-Axis System 2 Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`[NEW] @[scripts/auto_phase_runner.py]` (Data Models & CLI Args)** | Banned naked dictionaries (`dict[str, Any]`), loose kwargs, anonymous state tuples (`tuple[int, str]`), bare mutable defaults, and unannotated fields. | Strictly typed, immutable Pydantic V2 DTOs (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with PEP 593 `Annotated` syntax: `PhaseItemDTO`, `AutoPhaseRunnerArgsDTO`, `SubagentExecutionResultDTO`, `PhaseExecutionResultDTO`, `AutoPhaseRunSummaryDTO`, `QualityGateResultDTO`. | Zero speculative generic worker abstractions or dynamic plugin architectures. Single-purpose DTOs strictly scoped to headless phase orchestration. | `scripts/audit_dict_eradication.py scripts/auto_phase_runner.py --strict`, AST strict guardrails (`QGR007`, `QGR020`). |
| **`[NEW] @[scripts/auto_phase_runner.py]` (`parse_tracker_phases`, `filter_phases`)** | Banned fragile regex failing when commit hashes `(hash)` precede or follow `**[OK] Execution:` or when `**Plan:**` lacks a leading hyphen, banned ignoring Standalone Plan topologies (`## Step Execution Status`), and banned relative path guessing. | Dual-topology parser detecting Multi-Phase Epic vs Standalone Plan topologies with robust regex `(?m)^(?:\s*-\s*)?\*\*Plan:\*\*\s*@?\[?([^\],\n`]+)\]?` and execution regex supporting optional commit hashes either preceding `**[OK]` `(?:\([a-f0-9]+\)\s*)?` or following execution command `(?:\s*\(`?[a-f0-9]+`?\))?`, stripping command backticks and trailing parenthesized hashes, normalizing all paths to POSIX forward slashes, bounded to specific phase section boundaries (`### Phase\s+\d+`), and asserting referenced `plan_path` physical existence on disk against `repo_root`. Dedicated pure `filter_phases` function handling `--only-phase` and `--from-phase`. | Zero AST markdown tree compilation; use compiled regex slice scanning bounded by section markers (`### Phase`, `## Step Execution Status`, `### Post-Implementation`). | Fail-fast with `FileNotFoundError` if tracker or referenced plan file does not exist; unit tests `test_parse_tracker_phases_epic_topology`, `test_parse_tracker_phases_standalone_topology`, `test_parse_tracker_with_commit_hash`, `test_filter_phases_only_phase`, `test_filter_phases_from_phase`. |
| **`[NEW] @[scripts/auto_phase_runner.py]` (`resolve_agy_binary`, `execute_phase_subagent`)** | Banned synchronous blocking on `proc.stdout.readline()` without watchdog timeout (can hang indefinitely if process deadlocks without writing output), banned silent orphan zombie CLI processes, banned duplicate prompt injection when tracker already includes `PERMISSION GRANTED`, banned returning anonymous tuples (`tuple[int, str]`), and banned unshielded `.cmd` invocation crashing on Windows without shell interpreter. | Resolve `agy` via `shutil.which` and standard installation paths. If binary suffix is `.cmd` or `.bat` on Windows, wrap invocation via `cmd.exe /c` to prevent Win32 application execution errors. Check if `PERMISSION GRANTED` is already present before formatting instruction. Stream output live to `sys.stdout` (with `UnicodeEncodeError` fallback to buffer writes). Enforce deterministic timeout via `threading.Timer` with atomic `is_timeout_triggered` flag and Windows `taskkill /F /T /PID` to cleanly terminate child CLI process tree and break pipe reads. Return typed `SubagentExecutionResultDTO`. | Zero asynchronous event loops or complex IPC pipes; rely on native standard library `subprocess.Popen` with streaming stdout and `threading.Timer` watchdog. | Non-zero exit code stops pipeline immediately (circuit breaker); unit tests `test_execute_phase_subagent_success_mocked`, `test_execute_phase_subagent_timeout_triggers_tree_kill`, `test_execute_phase_subagent_failure_stops_pipeline`, `test_execute_subagent_cmd_wrapper_on_windows`, `test_execute_subagent_returns_typed_subagent_execution_result_dto`. |
| **`[NEW] @[scripts/auto_phase_runner.py]` (`run_phase_quality_gate`, `commit_phase_checkpoint`)** | Banned blind `git commit` when working tree is clean (which crashes with exit code 1), banned `git add .` staging untracked scratch artifacts, banned staging `.system_generated/` or `scratch/` files, and banned committing when audit loops fail. | Execute Universal Quality Gate `uv run python scripts/backend_audit_loop.py <resolved_targets> --test` (dynamically resolving `backend_v2/` alongside any dirty `.py` files in `scripts/`). Inspect `git status --porcelain`. If dirty files exist, specifically filter and stage only modified/untracked files in `backend_v2/`, `client_app_v2/`, `scripts/`, `docs/`, and the tracker with Conventional Commits `feat(phase{N}): complete {title}`. If only tracker changed, commit `docs(tracker): ...`. If clean, skip commit gracefully. | Zero complex interactive git rebasing or cherry-picking; strictly atomic commit of current phase state. | If quality gate fails, abort commit immediately, output failure diagnostics, and exit with code 1; unit tests `test_quality_gate_failure_aborts_commit`, `test_commit_phase_checkpoint_clean_working_tree`, `test_commit_phase_checkpoint_dirty_files_staged`. |
| **`[NEW] @[scripts/auto_phase_runner.py]` (`mark_phase_completed_in_tracker`, `run_post_hardening_gate`)** | Banned global untargeted search-and-replace that marks unrelated phases, banned placing commit hash between checkbox and marker which violates TRK002, and banned omitting short commit hash when recording completion. | In-place bounded section regex replacement targeting the exact `### Phase N` slice up to the next phase boundary, updating `- [ ] **[NOK] Execution:** <command>` to `- [x] **[OK] Execution:** <command> (`{short_hash}`)` (or `- [x] **[OK] Execution:** <command>`) and checking indented sub-step checkboxes within the phase's section. When all phases complete and `not args.skip_hardening`, execute `uv run python scripts/auto_hardening_runner.py --tracker <tracker_path> --gate backend` (passing `--agent-cmd` with `/tier2-hardening-backend {target}` when `--hardening-agent` is set). | Direct file manipulation via `Path.read_text(encoding="utf-8")` and `write_text()`; zero heavy markdown parser AST libraries. | Unit tests `test_mark_phase_completed_in_tracker_in_place`, `test_mark_phase_completed_bounded_to_exact_phase_section`, `test_run_post_hardening_gate_handoff`, `test_run_post_hardening_gate_with_hardening_agent`. |
| **`@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]` (Inventory Registration & Count Parity)** | Banned out-of-order registration, missing script entries, or ignoring exhaustive inventory counts. | Insert `"auto_phase_runner.py"` into sorted `ALL_SCRIPTS` list and update total script count assertion from 35 to 36 in `test_script_count_is_exhaustive`. | Zero custom script testing harnesses; leverage parameterized `pytest` fixtures asserting help output, description lines, sub-second execution latency, and zero filesystem side-effects. | `uv run pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py -v`. |
| **`[NEW] @[backend_v2/tests/unit/scripts/test_auto_phase_runner.py]` (Comprehensive Unit & Mock Suite)** | Banned tautological mocks asserting static return values without logic execution, and banned happy-path-only testing. | Full test pyramid coverage covering both positive paths and ISTQB negative boundary partitions (missing tracker, missing plan, agy crash, timeout tree kill, quality gate rejection, dry-run zero mutation, Windows cmd wrapping, scratch filtering, bounded section replacement). | Zero network or real LLM calls; pure subprocess and filesystem mock testing with `tmp_path` fixtures. | `uv run pytest backend_v2/tests/unit/scripts/test_auto_phase_runner.py -v` achieving >90% line coverage. |

---

## 5. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Define Immutable Configuration &amp; Telemetry DTOs in scripts/auto_phase_runner.py">
    <constraint invariant="zero_permissive_typing">All data structures MUST be immutable Pydantic V2 DTOs with ConfigDict(strict=True, extra="forbid", frozen=True) and PEP 593 Annotated fields. Zero naked dictionaries or anonymous tuples.</constraint>
    <action>In `[NEW] @[scripts/auto_phase_runner.py]`, define and create new core data models:
      1. Define and create new [NEW] `PhaseItemDTO`:
         - `phase_num: Annotated[int, Field(description="Numerical index of the phase (1-based)")]`
         - `title: Annotated[str, Field(description="Human-readable title of the phase")]`
         - `plan_path: Annotated[Path, Field(description="Resolved workspace-relative path to implementation plan .md")]`
         - `is_completed: Annotated[bool, Field(description="Whether execution checkbox is already marked [x]")]`
         - `command: Annotated[str, Field(description="Extracted or default /tier2-execute slash command")]`
      2. Define and create new [NEW] `AutoPhaseRunnerArgsDTO`:
         - `tracker: Annotated[Path, Field(description="Path to target tracker file")]`
         - `model: Annotated[str, Field(default="gemini-4-argon-high", description="CLI model name")]`
         - `from_phase: Annotated[int | None, Field(default=None, description="Start execution from phase N")]` = None
         - `only_phase: Annotated[int | None, Field(default=None, description="Execute only phase N")]` = None
         - `skip_commit: Annotated[bool, Field(default=False, description="Skip automated git commit after phase")]` = False
         - `skip_hardening: Annotated[bool, Field(default=False, description="Skip post-implementation hardening handoff")]` = False
         - `hardening_agent: Annotated[bool, Field(default=False, description="Dispatch AI-driven /tier2-hardening-backend subagents per target file during post-implementation hardening")]` = False
         - `hardening_model: Annotated[str | None, Field(default=None, description="LLM model override for hardening subagent; defaults to main model if None")]` = None
         - `timeout: Annotated[int, Field(default=3600, description="Per-phase timeout in seconds")]` = 3600
         - `dry_run: Annotated[bool, Field(default=False, description="Simulate without executing agy subprocesses")]` = False
         - `verbose: Annotated[bool, Field(default=False, description="Enable verbose log output")]` = False
      3. Define and create new [NEW] `SubagentExecutionResultDTO`:
         - `exit_code: Annotated[int, Field(description="Subprocess return code")]`
         - `output: Annotated[str, Field(description="Captured stdout and stderr combined log")]`
         - `duration_seconds: Annotated[float, Field(description="Elapsed wall-clock execution time")]`
         - `is_timeout: Annotated[bool, Field(default=False, description="Whether execution was terminated due to timeout")]` = False
      4. Define and create new [NEW] `PhaseExecutionResultDTO`:
         - `phase_num: Annotated[int, Field(description="Phase index")]`
         - `title: Annotated[str, Field(description="Phase title")]`
         - `success: Annotated[bool, Field(description="Whether execution and quality gates passed")]`
         - `duration_seconds: Annotated[float, Field(description="Wall-clock elapsed execution time")]`
         - `error_message: Annotated[str | None, Field(default=None, description="Error reason if failed")]` = None
      5. Define and create new [NEW] `AutoPhaseRunSummaryDTO`:
         - `tracker_path: Annotated[Path, Field(description="Target tracker path")]`
         - `total_phases: Annotated[int, Field(description="Total phases discovered in tracker")]`
         - `executed_phases: Annotated[int, Field(description="Count of executed phases in this run")]`
         - `succeeded_phases: Annotated[int, Field(description="Count of successfully executed phases")]`
         - `failed_phases: Annotated[int, Field(description="Count of failed phases")]`
         - `results: Annotated[list[PhaseExecutionResultDTO], Field(default_factory=list, description="Per-phase execution results")]`
      6. Define and create new [NEW] `QualityGateResultDTO`:
         - `success: Annotated[bool, Field(description="Whether quality gate succeeded with code 0")]`
         - `output: Annotated[str, Field(description="Combined stdout and stderr log")]`
         - `exit_code: Annotated[int, Field(description="Process exit code")]`
    </action>
  </step>

  <step id="2" name="Implement Tracker Discovery &amp; Phase Parsing Engine">
    <constraint invariant="universal_fail_fast">Raise explicit AppException or ValueError with structured ErrorCodes when tracker is unreadable or contains invalid phase formatting.</constraint>
    <action>In `[NEW] @[scripts/auto_phase_runner.py]`, implement `parse_tracker_phases(tracker_path: Path, repo_root: Path | None = None) -> list[PhaseItemDTO]` and `filter_phases(phases: list[PhaseItemDTO], from_phase: int | None = None, only_phase: int | None = None) -> list[PhaseItemDTO]`:
      1. Read tracker content with UTF-8 encoding. Resolve `root = repo_root or get_repo_root()`.
      2. Detect topology:
         - **Multi-Phase Epic Topology**: Scan for `### Phase\s+(\d+)[:\-]?\s*([^\n]*)\n([\s\S]*?)(?=(?:### Phase\s+\d+|### Integration Checkpoint|### Post-Implementation|\Z))`.
           Extract plan path via `(?m)^(?:\s*-\s*)?\*\*Plan:\*\*\s*@?\[?([^\],\n`]+)\]?`.
           Extract execution line via `-\s*\[([ xX])\]\s*(?:\([a-f0-9]+\)\s*)?\*\*\[(?:OK|NOK)\]\s*Execution(?:\s*\([^\)]+\))?:\*\*\s*(?:`?(/tier2-execute[^\n`]+)`?|[^\n]*)`.
           Clean slash command by stripping enclosing backticks and any trailing parenthesized commit hashes `(?:\s*\(`?[a-f0-9]+`?\))?`.
           If no execution command is explicitly found, default deterministically to `f'/tier2-execute --full-auto @<{plan_path}> @<{tracker_path}>'`.
           Determine completion strictly from `[x]` checkbox on execution line or all sub-steps checked.
         - **Single-Phase Standalone Plan Topology**: Scan for `## Step Execution Status\n([\s\S]*?)(?=(?:### Post-Implementation|\Z))`.
           Extract single plan path via `(?m)^(?:\s*-\s*)?\*\*Plan:\*\*\s*@?\[?([^\],\n`]+)\]?` and execution command, cleaning backticks and trailing parenthesized hashes.
           If no execution command is found, default deterministically to `f'/tier2-execute --full-auto @<{plan_path}> @<{tracker_path}>'`.
      3. Verify each referenced `plan_path` physically exists on disk (checking `plan_path.exists()` or `(root / plan_path).exists()`). If missing, fail-fast with `FileNotFoundError`.
      4. Implement `filter_phases(phases: list[PhaseItemDTO], from_phase: int | None = None, only_phase: int | None = None) -> list[PhaseItemDTO]`:
         - If `only_phase is not None`: return `[p for p in phases if p.phase_num == only_phase]` regardless of prior `is_completed` state.
         - Otherwise, filter out phases where `p.is_completed is True`, and if `from_phase is not None`, filter out phases where `p.phase_num < from_phase`.
      5. Return an ordered list of `PhaseItemDTO` objects.
    </action>
  </step>

  <step id="3" name="Implement agy Subagent Spawner with Streaming &amp; Tree Killing">
    <constraint invariant="async_background_execution_mandate">Subprocess execution must support cross-platform Windows 11 tree termination (taskkill /F /T /PID) on timeouts or cancellations to prevent orphaned zombie LLM CLI processes.</constraint>
    <action>In `[NEW] @[scripts/auto_phase_runner.py]`, implement `resolve_agy_binary() -> Path` and `execute_phase_subagent(phase: PhaseItemDTO, args: AutoPhaseRunnerArgsDTO, repo_root: Path) -> SubagentExecutionResultDTO`:
      1. Binary resolution:
         - Check `shutil.which("agy")`.
         - If None, check Windows paths `Path.home() / "AppData/Local/agy/bin/agy.exe"`, `Path.home() / "AppData/Roaming/npm/agy.cmd"`, `C:/Program Files/agy/bin/agy.exe`.
         - If unfound, raise `FileNotFoundError("Antigravity CLI (agy) not found in PATH or standard installation directories.")`.
      2. Command formulation:
         - Inspect `phase.command`. If `"PERMISSION GRANTED"` is not already present, construct:
           `f'{phase.command}. PERMISSION GRANTED for continuous full-auto execution across all steps. Proceed autonomously through all steps without intermediate confirmations.'`
         - If already present, use `phase.command` directly.
         - Build arguments list:
           If `sys.platform == "win32"` and str(agy_bin).lower().endswith((".cmd", ".bat")):
             `cmd = ["cmd.exe", "/c", str(agy_bin), "--model", args.model, "--dangerously-skip-permissions", "-i", prompt]`
           Else:
             `cmd = [str(agy_bin), "--model", args.model, "--dangerously-skip-permissions", "-i", prompt]`
      3. Subprocess execution with watchdog tree killing:
         - Launch with `subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", cwd=repo_root)`.
         - Set `is_timeout_triggered = False`. Record `start_time = time.monotonic()`.
         - Define watchdog callback:
           `def _on_timeout(): nonlocal is_timeout_triggered; is_timeout_triggered = True; _tree_kill(proc.pid)`
         - Start `threading.Timer(args.timeout, _on_timeout)` to enforce deterministic timeout without blocking pipe reads.
         - Stream stdout directly to terminal (`sys.stdout.write(line); sys.stdout.flush()`), catching `UnicodeEncodeError` on Windows consoles and falling back to `sys.stdout.buffer.write(line.encode("utf-8", errors="replace"))`, while accumulating lines into in-memory buffer. Wrap read in `try...except (OSError, ValueError): break`.
         - In `finally:` block, cancel the watchdog timer.
         - If `is_timeout_triggered` is True:
           Wait for child tree termination, compute `elapsed = time.monotonic() - start_time`, and return `SubagentExecutionResultDTO(exit_code=-1, output="".join(collected_output), duration_seconds=elapsed, is_timeout=True)`.
         - Wait for process termination via `proc.wait()`. Compute `elapsed = time.monotonic() - start_time`.
         - Return `SubagentExecutionResultDTO(exit_code=proc.returncode, output="".join(collected_output), duration_seconds=elapsed, is_timeout=False)`.
    </action>
  </step>

  <step id="4" name="Implement Quality Gate Verification &amp; Atomic Git Checkpointing">
    <constraint invariant="atomic_checkpoint_mandate">Never commit if quality gates fail. Always stage explicit target files and tracker using Conventional Commits syntax.</constraint>
    <action>In `[NEW] @[scripts/auto_phase_runner.py]`, implement `run_phase_quality_gate(phase: PhaseItemDTO, repo_root: Path) -> QualityGateResultDTO` and `commit_phase_checkpoint(phase: PhaseItemDTO, tracker_path: Path, repo_root: Path) -> str | None`:
      1. Quality Gate:
         - Inspect working tree via `git status --porcelain` to identify dirty files in `scripts/`.
         - Dynamically resolve quality gate targets: `targets = ["backend_v2/"] + [f for f in dirty_files if f.startswith("scripts/") and f.endswith(".py")]`.
         - Run `uv run python scripts/backend_audit_loop.py <resolved_targets> --test`.
         - Return `QualityGateResultDTO(success=(proc.returncode == 0), output=stdout, exit_code=proc.returncode)`.
         - If exit code non-zero, log error banner and halt pipeline immediately (circuit breaker).
      2. Git Checkpoint:
         - Inspect dirty files using `git status --porcelain`.
         - If working tree is clean: log "Working tree clean, no commit required" and return None.
         - Parse modified and untracked files from porcelain output, strictly filtering out scratch/ephemeral directories (`.gemini/`, `.system_generated/`, `scratch/`, `tmp/`).
         - If only tracker is modified: stage tracker via `git add <tracker_path>` and commit `git commit -m "docs(tracker): mark phase {phase.phase_num} complete in {tracker_path.name}"`.
         - If domain files are dirty: sanitize title via `title_cleaned = re.sub(r"^Phase\s+\d+[:\-]?\s*", "", phase.title, flags=re.IGNORECASE).strip()`, stage verified domain files and tracker via `git add <filtered_files> <tracker_path>`, and commit `git commit -m "feat(phase{phase.phase_num}): complete {title_cleaned}"`.
         - Return short commit hash extracted via `git rev-parse --short HEAD`.
    </action>
  </step>

  <step id="5" name="Implement In-Place Tracker Marking &amp; Post-Implementation Hardening Handoff">
    <constraint invariant="deterministic_hardening_state">Synchronize tracker checkboxes in-place. Execute auto_hardening_runner.py upon pipeline completion.</constraint>
    <action>In `[NEW] @[scripts/auto_phase_runner.py]`, implement `mark_phase_completed_in_tracker(tracker_path: Path, phase_num: int, commit_hash: str | None = None) -> None` and `run_post_hardening_gate(tracker_path: Path, args: AutoPhaseRunnerArgsDTO, repo_root: Path) -> int`:
      1. Tracker update:
         - Read tracker file content.
         - Slice target section: For target Phase N (in Multi-Phase Epic topology bounded by `### Phase {phase_num}` up to the next `### Phase` or section marker) or the execution section (in Single-Phase Standalone Plan topology `## Step Execution Status` up to `### Post-Implementation`), perform in-place replacement strictly within that slice.
         - Within the target slice, replace `- [ ] **[NOK] Execution:** <command>` with TRK002-compliant formatted line preserving standard bold colon:
           `- [x] **[OK] Execution:** <command> (`{commit_hash}`)` if `commit_hash` is present, or `- [x] **[OK] Execution:** <command>` otherwise.
         - Replace indented `- [ ] Step` with `- [x] Step` within the target section slice.
         - Reassemble and save updated tracker with UTF-8 encoding.
      2. Post-Implementation Hardening handoff:
         - If `not args.skip_hardening`:
           - Construct command: `cmd = ["uv", "run", "python", "scripts/auto_hardening_runner.py", "--tracker", str(tracker_path), "--gate", "backend"]`.
           - If `args.hardening_agent`:
             - Determine hardening model: `h_model = args.hardening_model or args.model`.
             - Format agent command template: `agent_template = f'agy --model {h_model} --dangerously-skip-permissions -i "/tier2-hardening-backend {{target}}"'`.
             - Append `["--agent-cmd", agent_template]` to `cmd`.
           - Execute subprocess with output streaming. Pass through exit code and log summary banner.
    </action>
  </step>

  <step id="6" name="CLI Argument Parser, Main Entrypoint &amp; test_scripts_cli_help.py Registration">
    <constraint invariant="windows_powershell_mandate">CLI must support standard flags (--tracker, --model, --from-phase, --only-phase, --skip-commit, --skip-hardening, --hardening-agent, --hardening-model, --dry-run) and output clean help text.</constraint>
    <action>In `[NEW] @[scripts/auto_phase_runner.py]`, implement `run_phase_pipeline(args: AutoPhaseRunnerArgsDTO, repo_root: Path | None = None) -> AutoPhaseRunSummaryDTO`, CLI argument parsing, and `main(argv: list[str] | None = None) -> int`; and update `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]`:
      1. In `scripts/auto_phase_runner.py`:
         - Implement `run_phase_pipeline(args: AutoPhaseRunnerArgsDTO, repo_root: Path | None = None) -> AutoPhaseRunSummaryDTO`:
           - Parse phases via `parse_tracker_phases(args.tracker, repo_root=root)` and filter via `filter_phases(all_phases, from_phase=args.from_phase, only_phase=args.only_phase)`.
           - If `args.dry_run` is True: print planned phases and commands without spawning subprocesses or mutating git/tracker, and return `AutoPhaseRunSummaryDTO`.
           - For each pending phase: execute `execute_phase_subagent`, verify `exit_code == 0` and `not is_timeout` (halting immediately on failure), run `run_phase_quality_gate` (halting immediately on failure), mark phase complete via `mark_phase_completed_in_tracker(args.tracker, phase.phase_num)`, and if `not args.skip_commit`, commit via `commit_phase_checkpoint(phase, args.tracker, root)`.
           - If all phases succeed and `not args.skip_hardening`, invoke `run_post_hardening_gate(args.tracker, args, root)`.
         - Configure `argparse.ArgumentParser(description="Autonomous Headless CLI Phase Orchestrator (Multi-Phase Pipeline Runner).")`.
         - Add all flags defined in `AutoPhaseRunnerArgsDTO` (including `--hardening-agent` and `--hardening-model`).
         - Wire `main(argv: list[str] | None = None) -> int` with proper exit codes (0 for full success, 1 for failure, 2 for CLI arg error).
      2. In `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]`:
         - Insert `"auto_phase_runner.py"` into sorted `ALL_SCRIPTS` list.
         - Update assertion count from 35 to 36 in `test_script_count_is_exhaustive`.
    </action>
  </step>

  <step id="7" name="Comprehensive Unit &amp; Mock Verification Suite in test_auto_phase_runner.py">
    <constraint invariant="anti_happy_path_compliance">Test both success and negative failure paths: invalid tracker, missing plan, agy crash, timeout tree kill, quality gate rejection.</constraint>
    <action>In `[NEW] @[backend_v2/tests/unit/scripts/test_auto_phase_runner.py]`, implement the comprehensive unit test suite:
      1. `test_parse_tracker_phases_epic_topology`: Verify phase extraction against `docs/epic/matrix_domain_parser_decomposition_tracker.md`.
      2. `test_parse_tracker_phases_standalone_topology`: Verify phase extraction against `docs/implementationplans/TRACKER_auto_phase_runner.md`.
      3. `test_parse_tracker_with_commit_hash`: Verify regex parses `- [x] (hash) **[OK] Execution:` correctly.
      4. `test_parse_tracker_missing_file_raises`: Verify `FileNotFoundError` on non-existent tracker.
      5. `test_parse_tracker_missing_plan_file_raises`: Verify `FileNotFoundError` when referenced plan does not exist.
      6. `test_resolve_agy_binary_found_and_missing`: Mock `shutil.which` and path lookups to verify both success and clean error reporting.
      7. `test_dry_run_mode_prints_phases_without_subprocess`: Verify `--dry-run` discovers phases and exits 0 without calling `agy`.
      8. `test_phase_failure_triggers_circuit_breaker`: Mock failed `agy` return code (1) and assert pipeline stops immediately without committing.
      9. `test_quality_gate_failure_stops_pipeline`: Mock successful `agy` but failed quality gate, verifying git commit is aborted.
      10. `test_mark_phase_completed_in_tracker_in_place`: Verify regex in-place replacement of checkboxes and commit hash insertion.
      11. `test_execute_subagent_timeout_tree_kill`: Mock watchdog timer firing and verifying `taskkill /F /T /PID` is dispatched.
      12. `test_commit_phase_checkpoint_clean_working_tree`: Verify clean working tree skips commit without error.
      13. `test_full_pipeline_success_mocked`: Mock successful 2-phase execution with git commit and hardening handoff.
      14. `test_filter_phases_only_phase`: Verify `--only-phase` filters down execution to the designated single phase.
      15. `test_filter_phases_from_phase`: Verify `--from-phase` skips all phases with index lower than the threshold.
      16. `test_run_post_hardening_gate_with_hardening_agent`: Verify `--hardening-agent` appends `--agent-cmd` with `/tier2-hardening-backend {target}` template to `auto_hardening_runner.py`.
      17. `test_execute_subagent_cmd_wrapper_on_windows`: Verify `.cmd` / `.bat` binary wrapping via `cmd.exe /c` on Windows platforms.
      18. `test_commit_phase_checkpoint_dirty_files_staged`: Verify specific staging of modified domain files excluding scratch and system files.
      19. `test_mark_phase_completed_bounded_to_exact_phase_section`: Verify bounded section replacement updates only the targeted phase without cross-phase marker pollution.
      20. `test_execute_subagent_returns_typed_subagent_execution_result_dto`: Verify `execute_phase_subagent` encapsulates returncode, captured output, and duration into `SubagentExecutionResultDTO`.
    </action>
  </step>
</execution_protocol>
```

---

## 6. Architectural Safeguards & Verification Plan

### Automated Audit Loop Gates
1. **Script CLI & Help Parity Verification:**
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py -v
   ```
2. **Dedicated Unit Test Verification:**
   ```powershell
   uv run pytest backend_v2/tests/unit/scripts/test_auto_phase_runner.py -v
   ```
3. **Backend Audit Loop & AST Strict Verification:**
   ```powershell
   uv run python scripts/backend_audit_loop.py scripts/auto_phase_runner.py --test --ast-strict
   ```
4. **Markdown Boundaries Self-Healing Audit:**
   ```powershell
   uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md
   ```
5. **Dry-Run Functional Verification:**
   ```powershell
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/matrix_domain_parser_decomposition_tracker.md --dry-run
   ```

---

## 7. User Guidance & Next Steps

1. **Pre-Execution Analysis (Recommended)**:
   Run Five-Axis System 2 Deconstruction:
   ```powershell
   /tier0-research-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md]
   ```
2. **Double-Entry Bookkeeping Tracker Generation**:
   Generate the dedicated plan tracker:
   ```powershell
   /tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md]
   ```
3. **Autonomous Execution**:
   Launch execution via Antigravity CLI or interactive session:
   ```powershell
   /tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]
   ```
