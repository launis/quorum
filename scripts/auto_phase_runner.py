"""Autonomous Headless CLI Phase Orchestrator (Multi-Phase Pipeline Runner).

Orchestrates unattended sequential execution of multi-phase implementation trackers
across isolated Antigravity CLI (agy) subagent processes with live console streaming,
Universal Quality Gate verification loops, atomic git checkpointing, and post-implementation
hardening handoff.

Architectural Workflow & Lifecycle:
-----------------------------------
1. Tracker Discovery & Parsing:
   - Supports Multi-Phase Epic Trackers (`docs/epic/EPIC_XXX_tracker.md`, `*_decomposition_tracker.md`)
     and Standalone Implementation Plan Trackers (`docs/implementationplans/TRACKER_*.md`).
   - Identifies phase sections (`### Phase N`), plan references (`**Plan:** @[...]`),
     and `/tier2-execute` execution commands.
2. Subagent Isolation (Context Amnesia Prevention):
   - Dispatches each phase to an isolated Antigravity CLI (`agy`) subprocess.
   - Provides each phase with a pristine context window, eliminating token budget exhaustion,
     cognitive drift, and context amnesia across long multi-hour implementations.
3. Windows Process Tree Watchdog:
   - Monitored by a watchdog timer (`--timeout`, default: 3600s).
   - In case of timeout or abort, uses Windows `taskkill /F /T /PID` to terminate the entire
     process tree, preventing orphaned node/python background processes.
4. Universal Quality Gate Audit:
   - Automatically executes `scripts/backend_audit_loop.py` and `scripts/flutter_audit_loop.py`
     verifying Ruff, MyPy strict typing, AST guardrails, and unit tests on changed files.
5. Atomic Checkpoint & In-Place Tracker Marking:
   - Stages modified source files and commits them with Conventional Commits messages
     (`feat(phaseN): complete <title>`).
   - Updates tracker markdown in-place, marking checkboxes `- [x]` with the commit hash.
6. Post-Implementation Hardening Handoff:
   - On completion of all phases, hands off to `scripts/auto_hardening_runner.py` to harden
     every modified file against Tier 2 hardening quality gates.

CLI Usage Examples for Autonomous AI Agents:
--------------------------------------------
# 1. Standard unattended execution across all pending phases:
uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md

# 2. Resume execution starting from a specific phase (e.g., Phase 3):
uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --from-phase 3

# 3. Targeted execution of a single phase (e.g., Phase 2 only):
uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --only-phase 2

# 4. Dry-run inspection to preview discovered phases and commands without execution:
uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --dry-run

# 5. Full unattended run with AI-driven per-file hardening subagents:
uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --hardening-agent
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from scripts._script_base import ANSIColors, get_repo_root, setup_script_environment
from scripts.auto_hardening_runner import HardeningGate, parse_tracker_unhardened_targets

GIT_SUBPROCESS_TIMEOUT_SECONDS: Final[int] = 30
TASKKILL_TIMEOUT_SECONDS: Final[int] = 15
DEFAULT_AUDIT_TIMEOUT_SECONDS: Final[int] = 1800
DEFAULT_SUBAGENT_TIMEOUT_SECONDS: Final[int] = 3600
DEFAULT_SUBAGENT_MAX_RETRIES: Final[int] = 3
DEFAULT_SUBAGENT_RETRY_BACKOFF_SECONDS: Final[float] = 3.0
SUBAGENT_STARTUP_GRACE_SECONDS: Final[float] = 45.0

__all__ = [
    "DEFAULT_AUDIT_TIMEOUT_SECONDS",
    "DEFAULT_SUBAGENT_MAX_RETRIES",
    "DEFAULT_SUBAGENT_RETRY_BACKOFF_SECONDS",
    "DEFAULT_SUBAGENT_TIMEOUT_SECONDS",
    "GIT_SUBPROCESS_TIMEOUT_SECONDS",
    "SUBAGENT_STARTUP_GRACE_SECONDS",
    "TASKKILL_TIMEOUT_SECONDS",
    "AutoPhaseRunSummaryDTO",
    "AutoPhaseRunnerArgsDTO",
    "PhaseExecutionResultDTO",
    "PhaseItemDTO",
    "QualityGateResultDTO",
    "SubagentExecutionResultDTO",
    "clean_path_arg",
    "commit_phase_checkpoint",
    "execute_phase_subagent",
    "filter_phases",
    "main",
    "mark_phase_completed_in_tracker",
    "parse_tracker_phases",
    "resolve_agy_binary",
    "run_phase_pipeline",
    "run_phase_quality_gate",
    "run_post_hardening_gate",
]


class PhaseItemDTO(BaseModel):
    """Specification of an execution phase extracted from a tracker document."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    phase_num: Annotated[int, Field(description="Numerical index of the phase (1-based).")]
    title: Annotated[str, Field(description="Human-readable title of the phase.")]
    plan_path: Annotated[Path, Field(description="Resolved workspace-relative path to implementation plan .md.")]
    is_completed: Annotated[bool, Field(description="Whether execution checkbox is already marked [x].")]
    command: Annotated[str, Field(description="Extracted or default /tier2-execute slash command.")]


class AutoPhaseRunnerArgsDTO(BaseModel):
    """Strict configuration parameters for the autonomous phase runner pipeline."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tracker: Annotated[Path, Field(description="Path to target tracker file.")]
    model: Annotated[str, Field(default="gemini-4-argon-high", description="CLI model name.")] = "gemini-4-argon-high"
    from_phase: Annotated[int | None, Field(default=None, description="Start execution from phase N.")] = None
    only_phase: Annotated[int | None, Field(default=None, description="Execute only phase N.")] = None
    skip_commit: Annotated[bool, Field(default=False, description="Skip automated git commit after phase.")] = False
    skip_hardening: Annotated[bool, Field(default=False, description="Skip post-implementation hardening handoff.")] = (
        False
    )
    hardening_agent: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "Dispatch AI-driven /tier2-hardening-backend or /tier2-hardening-frontend "
                "subagents per target file during hardening."
            ),
        ),
    ] = True
    hardening_model: Annotated[
        str | None,
        Field(
            default=None,
            description="LLM model override for hardening subagent; defaults to main model if None.",
        ),
    ] = None
    max_retries: Annotated[
        int,
        Field(
            default=DEFAULT_SUBAGENT_MAX_RETRIES,
            ge=1,
            description="Max automatic retry attempts for transient subagent startup failures.",
        ),
    ] = DEFAULT_SUBAGENT_MAX_RETRIES
    timeout: Annotated[
        int, Field(default=DEFAULT_SUBAGENT_TIMEOUT_SECONDS, description="Per-phase timeout in seconds.")
    ] = DEFAULT_SUBAGENT_TIMEOUT_SECONDS
    dry_run: Annotated[bool, Field(default=False, description="Simulate without executing agy subprocesses.")] = False
    verbose: Annotated[bool, Field(default=False, description="Enable verbose log output.")] = False


class SubagentExecutionResultDTO(BaseModel):
    """Captured result of an agy subagent execution."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    exit_code: Annotated[int, Field(description="Subprocess return code.")]
    output: Annotated[str, Field(description="Captured stdout and stderr combined log.")]
    duration_seconds: Annotated[float, Field(description="Elapsed wall-clock execution time.")]
    is_timeout: Annotated[
        bool, Field(default=False, description="Whether execution was terminated due to timeout.")
    ] = False


class PhaseExecutionResultDTO(BaseModel):
    """Execution outcome for a single phase in the pipeline."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    phase_num: Annotated[int, Field(description="Phase index.")]
    title: Annotated[str, Field(description="Phase title.")]
    success: Annotated[bool, Field(description="Whether execution and quality gates passed.")]
    duration_seconds: Annotated[float, Field(description="Wall-clock elapsed execution time.")]
    error_message: Annotated[str | None, Field(default=None, description="Error reason if failed.")] = None


class AutoPhaseRunSummaryDTO(BaseModel):
    """Cumulative summary report of an entire phase runner execution run."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tracker_path: Annotated[Path, Field(description="Target tracker path.")]
    total_phases: Annotated[int, Field(description="Total phases discovered in tracker.")]
    executed_phases: Annotated[int, Field(description="Count of executed phases in this run.")]
    succeeded_phases: Annotated[int, Field(description="Count of successfully executed phases.")]
    failed_phases: Annotated[int, Field(description="Count of failed phases.")]
    results: Annotated[
        list[PhaseExecutionResultDTO],
        Field(default_factory=list, description="Per-phase execution results."),
    ]


class QualityGateResultDTO(BaseModel):
    """Result of running Universal Quality Gate audit checks."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    success: Annotated[bool, Field(description="Whether quality gate succeeded with code 0.")]
    output: Annotated[str, Field(description="Combined stdout and stderr log.")]
    exit_code: Annotated[int, Field(description="Process exit code.")]


def clean_path_arg(val: str | Path | None) -> Path | None:
    """Normalize raw path arguments, stripping quotes and markdown `@-reference` brackets."""
    if val is None:
        return None
    raw_str = str(val).strip().strip("`").strip("'").strip('"')
    if raw_str.startswith("@"):
        raw_str = raw_str[1:]
    raw_str = raw_str.strip().strip("[").strip("]").strip()
    if not raw_str:
        return None
    return Path(raw_str)


def parse_tracker_phases(tracker_path: Path, repo_root: Path | None = None) -> list[PhaseItemDTO]:
    """Parse phase definitions from a tracker document supporting Epic and Standalone topologies.

    Args:
        tracker_path: Path to the target tracker markdown file.
        repo_root: Optional repository root for path resolution. Defaults to get_repo_root().

    Returns:
        List of PhaseItemDTO items parsed from the tracker.

    Raises:
        FileNotFoundError: If the tracker or any referenced plan file does not exist on disk.
        ValueError: If no phases can be parsed from the document.
    """
    root = repo_root or get_repo_root()
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None:
        raise ValueError("Invalid tracker path argument: path is empty.")

    resolved_tracker = cleaned_tracker if cleaned_tracker.is_absolute() else (root / cleaned_tracker)
    if not resolved_tracker.exists():
        raise FileNotFoundError(f"Tracker file not found: {tracker_path}")

    content = resolved_tracker.read_text(encoding="utf-8")
    phases: list[PhaseItemDTO] = []

    # Topology 1: Multi-Phase Epic Topology
    # Extracts sequential phases from Epic trackers formatted as:
    #   ### Phase 1: Foundation Setup
    #   - **Plan:** @[docs/implementationplans/phase_1.md]
    #   - [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[...] @[...]`
    #     - [ ] Step 1.1: Models & DTOs
    # Bounded by ### Phase N up to next ### Phase, ### Integration Checkpoint, or ### Post-Implementation
    epic_phase_pattern = re.compile(
        r"### Phase\s+(\d+)[:\-]?\s*([^\n]*)\n([\s\S]*?)"
        r"(?=(?:### Phase\s+\d+|### Integration Checkpoint|### Post-Implementation|\Z))",
        re.IGNORECASE,
    )
    plan_pattern = re.compile(r"(?m)^(?:\s*-\s*)?\*\*Plan:\*\*\s*@?\[?([^\],\n`]+)\]?")
    exec_pattern = re.compile(
        r"-\s*\[([ xX])\]\s*(?:\([a-f0-9]+\)\s*)?\*\*\[(?:OK|NOK)\]\s*Execution(?:\s*\([^\)]+\))?:\*\*\s*"
        r"(?:`?(/tier2-execute[^\n`]+)`?|[^\n]*)",
        re.IGNORECASE,
    )
    substep_pattern = re.compile(r"^\s+-\s*\[([ xX])\]\s*Step", re.MULTILINE)

    matches = list(epic_phase_pattern.finditer(content))
    if matches:
        for m in matches:
            phase_num = int(m.group(1))
            title = m.group(2).strip()
            section_body = m.group(3)

            plan_m = plan_pattern.search(section_body)
            if not plan_m:
                continue

            raw_plan = plan_m.group(1).replace("\\", "/").strip()
            plan_path = Path(raw_plan)
            resolved_plan = plan_path if plan_path.is_absolute() else (root / plan_path)
            if not resolved_plan.exists():
                raise FileNotFoundError(f"Referenced plan file not found on disk: {plan_path} (in Phase {phase_num})")

            # Extract execution command & completion status
            exec_m = exec_pattern.search(section_body)
            is_completed = False
            command = ""
            if exec_m:
                is_completed = exec_m.group(1).lower() == "x"
                raw_cmd = exec_m.group(2)
                if raw_cmd:
                    # Strip enclosing backticks and trailing parenthesized hashes: (`hash`) or (hash)
                    cleaned_cmd = raw_cmd.strip().strip("`").strip()
                    cleaned_cmd = re.sub(r"\s*\(`?[a-f0-9]+`?\)$", "", cleaned_cmd, flags=re.IGNORECASE).strip()
                    command = cleaned_cmd

            if not command:
                rel_plan_posix = plan_path.as_posix()
                rel_tracker_posix = cleaned_tracker.as_posix()
                command = f"/tier2-execute --full-auto @[{rel_plan_posix}] @[{rel_tracker_posix}]"

            # Cross-verify: if all substeps are checked, consider completed
            substeps = substep_pattern.findall(section_body)
            if substeps and all(s.lower() == "x" for s in substeps):
                is_completed = True

            phases.append(
                PhaseItemDTO(
                    phase_num=phase_num,
                    title=title or f"Phase {phase_num}",
                    plan_path=plan_path,
                    is_completed=is_completed,
                    command=command,
                )
            )

    # Topology 2: Single-Phase Standalone Plan Topology
    # Extracts the single execution step from standalone plan trackers formatted as:
    #   ## Step Execution Status
    #   - **Plan:** @[docs/implementationplans/plan_xxx.md]
    #   - [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[...] @[...]`
    #     - [ ] Step 1: Implementation Details
    # Bounded up to next ### Post-Implementation or EOF
    if not phases:
        standalone_pattern = re.compile(
            r"## Step Execution Status\n([\s\S]*?)(?=(?:### Post-Implementation|\Z))",
            re.IGNORECASE,
        )
        s_match = standalone_pattern.search(content)
        if s_match:
            section_body = s_match.group(1)
            # Find Plan reference in section or top of file
            plan_m = plan_pattern.search(section_body) or plan_pattern.search(content)
            if plan_m:
                raw_plan = plan_m.group(1).replace("\\", "/").strip()
                plan_path = Path(raw_plan)
                resolved_plan = plan_path if plan_path.is_absolute() else (root / plan_path)
                if not resolved_plan.exists():
                    raise FileNotFoundError(f"Referenced plan file not found on disk: {plan_path}")

                exec_m = exec_pattern.search(section_body)
                is_completed = False
                command = ""
                if exec_m:
                    is_completed = exec_m.group(1).lower() == "x"
                    raw_cmd = exec_m.group(2)
                    if raw_cmd:
                        cleaned_cmd = raw_cmd.strip().strip("`").strip()
                        cleaned_cmd = re.sub(r"\s*\(`?[a-f0-9]+`?\)$", "", cleaned_cmd, flags=re.IGNORECASE).strip()
                        command = cleaned_cmd

                if not command:
                    rel_plan_posix = plan_path.as_posix()
                    rel_tracker_posix = cleaned_tracker.as_posix()
                    command = f"/tier2-execute --full-auto @[{rel_plan_posix}] @[{rel_tracker_posix}]"

                substeps = substep_pattern.findall(section_body)
                if substeps and all(s.lower() == "x" for s in substeps):
                    is_completed = True

                phases.append(
                    PhaseItemDTO(
                        phase_num=1,
                        title="Step Execution",
                        plan_path=plan_path,
                        is_completed=is_completed,
                        command=command,
                    )
                )

    if not phases:
        raise ValueError(f"No execution phases discovered in tracker: {tracker_path}")

    # Return ordered by phase_num
    return sorted(phases, key=lambda p: p.phase_num)


def filter_phases(
    phases: list[PhaseItemDTO],
    from_phase: int | None = None,
    only_phase: int | None = None,
) -> list[PhaseItemDTO]:
    """Filter phases based on execution constraints (only_phase, from_phase, completion).

    Args:
        phases: List of parsed PhaseItemDTO objects.
        from_phase: Optional lowest phase index to include.
        only_phase: Optional single phase index to execute.

    Returns:
        Filtered list of phases ready for execution.
    """
    if only_phase is not None:
        return [p for p in phases if p.phase_num == only_phase]

    filtered: list[PhaseItemDTO] = []
    for p in phases:
        if p.is_completed:
            continue
        if from_phase is not None and p.phase_num < from_phase:
            continue
        filtered.append(p)

    return filtered


def resolve_agy_binary() -> Path:
    """Resolve the Antigravity CLI (agy) binary path.

    Returns:
        Resolved Path to agy executable.

    Raises:
        FileNotFoundError: If agy cannot be found in PATH or standard installation directories.
    """
    which_bin = shutil.which("agy")
    if which_bin:
        return Path(which_bin)

    candidates: list[Path] = [
        Path.home() / "AppData/Local/agy/bin/agy.exe",
        Path.home() / "AppData/Roaming/npm/agy.cmd",
        Path("C:/Program Files/agy/bin/agy.exe"),
    ]
    for c in candidates:
        if c.exists():
            return c

    raise FileNotFoundError("Antigravity CLI (agy) not found in PATH or standard installation directories.")


def _tree_kill(pid: int) -> None:
    """Terminate a process and its entire child process tree."""
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                timeout=TASKKILL_TIMEOUT_SECONDS,
                check=False,
                shell=False,
            )
        except subprocess.SubprocessError, OSError:
            pass
    else:
        try:
            os.killpg(os.getpgid(pid), 9)
        except OSError, ProcessLookupError:
            pass


def _is_transient_subagent_startup_failure(result: SubagentExecutionResultDTO) -> bool:
    """Detect whether a subagent execution failure was caused by a transient startup or network glitch.

    Args:
        result: Subagent execution outcome.

    Returns:
        True if the failure appears to be a transient startup or network error eligible for retry.
    """
    if result.is_timeout or result.exit_code <= 0:
        return False

    transient_indicators: tuple[str, ...] = (
        "is not recognized as a known model or custom model in settings",
        "invalid model selection",
        "no model configuration is available for this account",
        "error: authentication required",
        "connection refused",
        "tls: peer",
        "transport: set send compressor",
        "handshake failure",
        "i/o timeout",
        "failed to fetch account identity",
        "context deadline exceeded",
        "service unavailable",
        "bad gateway",
        "temporary failure in name resolution",
    )
    output_lower = result.output.lower()
    for indicator in transient_indicators:
        if indicator.lower() in output_lower:
            return True

    # If the subagent exited immediately with zero output, it crashed during CLI startup
    if result.duration_seconds < 15.0 and not result.output.strip():
        return True

    return False


def _execute_single_subagent_attempt(
    cmd: list[str],
    repo_root: Path,
    timeout: int,
) -> SubagentExecutionResultDTO:
    """Execute a single attempt of an agy subagent subprocess with streaming and watchdog."""
    start_time = time.monotonic()
    collected_output: list[str] = []
    is_timeout_triggered = False

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        shell=False,
    )

    def _on_timeout() -> None:
        nonlocal is_timeout_triggered
        is_timeout_triggered = True
        _tree_kill(proc.pid)

    timer = threading.Timer(timeout, _on_timeout)
    timer.daemon = True
    timer.start()

    try:
        if proc.stdout:
            while True:
                try:
                    line = proc.stdout.readline()
                except OSError, ValueError:
                    break
                if not line:
                    break
                collected_output.append(line)
                try:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                except UnicodeEncodeError:
                    sys.stdout.buffer.write(line.encode("utf-8", errors="replace"))
                    sys.stdout.buffer.flush()
    finally:
        timer.cancel()

    proc.wait()
    duration = time.monotonic() - start_time
    full_log = "".join(collected_output)

    if is_timeout_triggered:
        return SubagentExecutionResultDTO(
            exit_code=-1,
            output=full_log,
            duration_seconds=duration,
            is_timeout=True,
        )

    return SubagentExecutionResultDTO(
        exit_code=proc.returncode,
        output=full_log,
        duration_seconds=duration,
        is_timeout=False,
    )


def execute_phase_subagent(
    phase: PhaseItemDTO,
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path,
) -> SubagentExecutionResultDTO:
    """Spawn an agy CLI subagent process for the designated phase with streaming output and retry loop.

    Retries transient startup glitches (such as remote model catalog fetch failures or network timeouts)
    up to args.max_retries attempts with linear backoff before reporting failure.

    Args:
        phase: Phase to execute.
        args: Pipeline runner arguments.
        repo_root: Repository root path for working directory.

    Returns:
        SubagentExecutionResultDTO capturing returncode, output, duration, and timeout status.
    """
    agy_bin = resolve_agy_binary()

    # Construct instruction prompt ensuring continuous full-auto authorization.
    prompt = phase.command
    if "PERMISSION GRANTED" not in prompt:
        prompt = (
            f"{phase.command}. PERMISSION GRANTED for continuous full-auto execution across all steps. "
            f"Proceed autonomously through all steps without intermediate confirmations."
        )

    # Wrap .cmd / .bat invocation on Windows via cmd.exe /c to prevent Win32 application execution errors.
    if sys.platform == "win32" and str(agy_bin).lower().endswith((".cmd", ".bat")):
        cmd = [
            "cmd.exe",
            "/c",
            str(agy_bin),
            "--model",
            args.model,
            "--dangerously-skip-permissions",
            "--print",
            prompt,
        ]
    else:
        cmd = [str(agy_bin), "--model", args.model, "--dangerously-skip-permissions", "--print", prompt]

    max_attempts = args.max_retries
    last_res: SubagentExecutionResultDTO | None = None

    for attempt in range(1, max_attempts + 1):
        res = _execute_single_subagent_attempt(cmd, repo_root, args.timeout)
        last_res = res

        if res.exit_code == 0 or res.is_timeout:
            return res

        # Check if the failure was transient startup/network issue
        if _is_transient_subagent_startup_failure(res):
            if attempt < max_attempts:
                backoff = DEFAULT_SUBAGENT_RETRY_BACKOFF_SECONDS * attempt
                print(
                    f"\n{ANSIColors.YELLOW}[RETRY] Transient subagent startup error detected "
                    f"(exit code {res.exit_code}, duration {res.duration_seconds:.1f}s). "
                    f"Retrying attempt {attempt + 1}/{max_attempts} in {backoff:.1f}s...{ANSIColors.RESET}\n",
                    flush=True,
                )
                time.sleep(backoff)
                continue

        # If non-transient failure, do not retry
        break

    assert last_res is not None
    return last_res


def run_phase_quality_gate(phase: PhaseItemDTO, repo_root: Path) -> QualityGateResultDTO:
    """Execute the Universal Quality Gate audit checks on modified domains.

    Args:
        phase: Executed phase being audited.
        repo_root: Root directory of repository.

    Returns:
        QualityGateResultDTO with audit exit code and combined output.
    """
    # Detect any dirty python files in scripts/ to audit alongside backend_v2
    dirty_proc = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
    )
    dirty_scripts: list[str] = []
    if dirty_proc.returncode == 0:
        for line in dirty_proc.stdout.splitlines():
            line_str = line[3:].strip()
            if line_str.startswith("scripts/") and line_str.endswith(".py") and Path(repo_root / line_str).exists():
                dirty_scripts.append(line_str)

    targets = ["backend_v2/"] + sorted(dirty_scripts)
    audit_cmd = ["uv", "run", "python", "scripts/backend_audit_loop.py"] + targets + ["--test", "--no-logfire"]

    proc = subprocess.run(
        audit_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
        timeout=DEFAULT_AUDIT_TIMEOUT_SECONDS,
    )

    combined_output = f"{proc.stdout}\n{proc.stderr}".strip()
    return QualityGateResultDTO(
        success=(proc.returncode == 0),
        output=combined_output,
        exit_code=proc.returncode,
    )


def commit_phase_checkpoint(
    phase: PhaseItemDTO,
    tracker_path: Path,
    repo_root: Path,
) -> str | None:
    """Commit completed phase modifications atomically using Conventional Commits.

    Args:
        phase: Completed phase item.
        tracker_path: Path to tracker markdown file.
        repo_root: Root directory of repository.

    Returns:
        Short commit hash if a commit was executed, None if working tree was clean.
    """
    status_proc = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
    )
    if status_proc.returncode != 0:
        return None

    raw_lines = status_proc.stdout.splitlines()
    if not raw_lines:
        return None

    # Filter files: exclude scratch, tmp, and system generated paths
    staged_candidates: list[str] = []
    for line in raw_lines:
        file_path = line[3:].strip()
        # Handle rename arrow "A -> B"
        if " -> " in file_path:
            file_path = file_path.split(" -> ")[1].strip()

        # Exclude ephemeral/scratch paths
        if any(file_path.startswith(prefix) for prefix in (".gemini/", ".system_generated/", "scratch/", "tmp/")):
            continue
        staged_candidates.append(file_path)

    if not staged_candidates:
        return None

    tracker_rel = clean_path_arg(tracker_path)
    try:
        tracker_str = (tracker_path.resolve()).relative_to(repo_root.resolve()).as_posix()
    except ValueError, RuntimeError:
        tracker_str = tracker_rel.as_posix() if tracker_rel else str(tracker_path).replace("\\", "/")

    # Check if only tracker changed
    only_tracker = all(f == tracker_str for f in staged_candidates)

    if only_tracker:
        commit_msg = f"docs(tracker): mark phase {phase.phase_num} complete in {Path(tracker_str).name}"
        subprocess.run(["git", "add", tracker_str], cwd=repo_root, check=False)
    else:
        # Sanitize title removing redundant "Phase N:" prefix
        title_cleaned = re.sub(r"^Phase\s+\d+[:\-]?\s*", "", phase.title, flags=re.IGNORECASE).strip()
        commit_msg = f"feat(phase{phase.phase_num}): complete {title_cleaned}"
        # Stage filtered candidates and tracker
        add_cmd = ["git", "add"] + staged_candidates
        if tracker_str not in staged_candidates:
            add_cmd.append(tracker_str)
        subprocess.run(add_cmd, cwd=repo_root, check=False)

    commit_proc = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
    )
    if commit_proc.returncode != 0:
        return None

    rev_proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
    )
    if rev_proc.returncode == 0:
        return rev_proc.stdout.strip()
    return None


def mark_phase_completed_in_tracker(
    tracker_path: Path,
    phase_num: int,
    commit_hash: str | None = None,
) -> None:
    """Mark a phase execution and its sub-steps as completed ([x]) in tracker markdown in-place.

    Args:
        tracker_path: Path to tracker markdown file.
        phase_num: Index of phase to mark completed.
        commit_hash: Optional short git commit hash to record on execution line.
    """
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None or not cleaned_tracker.exists():
        return

    content = cleaned_tracker.read_text(encoding="utf-8")

    # Topology 1: Multi-Phase Epic Topology
    phase_header_pattern = re.compile(rf"^### Phase\s+{phase_num}[:\-]?", re.MULTILINE | re.IGNORECASE)
    match = phase_header_pattern.search(content)

    if match:
        start_idx = match.start()
        # Find next section boundary
        next_boundary = re.search(
            r"(?m)^(?:### Phase\s+\d+|### Integration Checkpoint|### Post-Implementation|\Z)",
            content[match.end() :],
        )
        end_idx = match.end() + next_boundary.start() if next_boundary else len(content)

        section_slice = content[start_idx:end_idx]

        # In-place replace execution line to - [x] **[OK] Execution:** <cmd> (`{commit_hash}`)
        def _replace_exec(m: re.Match[str]) -> str:
            cmd = m.group(1).strip()
            cmd_clean = re.sub(r"\s*\(`?[a-f0-9]+`?\)$", "", cmd, flags=re.IGNORECASE).strip().strip("`").strip()
            if commit_hash:
                return f"- [x] **[OK] Execution:** `{cmd_clean}` (`{commit_hash}`)"
            return f"- [x] **[OK] Execution:** `{cmd_clean}`"

        # Regex supporting both - [ ] **[NOK] Execution:** `cmd` and unbackticked commands
        exec_line_re = re.compile(
            r"-\s*\[[ xX]\]\s*(?:\([a-f0-9]+\)\s*)?\*\*\[(?:OK|NOK)\]\s*Execution(?:\s*\([^\)]+\))?:\*\*\s*"
            r"`?([^`\n]+)`?(?:\s*\(`?[a-f0-9]+`?\))?",
            re.IGNORECASE,
        )
        updated_slice = exec_line_re.sub(_replace_exec, section_slice)

        # Mark all indented sub-steps in this slice as - [x]
        updated_slice = re.sub(r"^( +-\s*)\[ \](\s*Step\s+\d+)", r"\1[x]\2", updated_slice, flags=re.MULTILINE)

        updated_content = content[:start_idx] + updated_slice + content[end_idx:]
        cleaned_tracker.write_text(updated_content, encoding="utf-8")
        return

    # Topology 2: Single-Phase Standalone Plan Topology
    standalone_header = re.search(r"^## Step Execution Status", content, re.MULTILINE | re.IGNORECASE)
    if standalone_header:
        start_idx = standalone_header.start()
        next_boundary = re.search(r"(?m)^(?:### Post-Implementation|\Z)", content[standalone_header.end() :])
        end_idx = standalone_header.end() + next_boundary.start() if next_boundary else len(content)

        section_slice = content[start_idx:end_idx]

        def _replace_standalone_exec(m: re.Match[str]) -> str:
            cmd = m.group(1).strip()
            cmd_clean = re.sub(r"\s*\(`?[a-f0-9]+`?\)$", "", cmd, flags=re.IGNORECASE).strip().strip("`").strip()
            if commit_hash:
                return f"- [x] **[OK] Execution:** `{cmd_clean}` (`{commit_hash}`)"
            return f"- [x] **[OK] Execution:** `{cmd_clean}`"

        exec_line_re = re.compile(
            r"-\s*\[[ xX]\]\s*(?:\([a-f0-9]+\)\s*)?\*\*\[(?:OK|NOK)\]\s*Execution(?:\s*\([^\)]+\))?:\*\*\s*"
            r"`?([^`\n]+)`?(?:\s*\(`?[a-f0-9]+`?\))?",
            re.IGNORECASE,
        )
        updated_slice = exec_line_re.sub(_replace_standalone_exec, section_slice)
        updated_slice = re.sub(r"^( +-\s*)\[ \](\s*Step\s+\d+)", r"\1[x]\2", updated_slice, flags=re.MULTILINE)

        updated_content = content[:start_idx] + updated_slice + content[end_idx:]
        cleaned_tracker.write_text(updated_content, encoding="utf-8")


def run_post_hardening_gate(
    tracker_path: Path,
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path,
) -> int:
    """Execute post-implementation hardening handoff via auto_hardening_runner.py.

    Discovers unhardened target files across both backend and frontend hardening
    gates in the tracker and executes the respective hardening pipelines.

    Args:
        tracker_path: Path to tracker markdown file.
        args: Pipeline runner arguments.
        repo_root: Repository root directory.

    Returns:
        Exit code of the hardening runner subprocess (0 on success, non-zero on failure).
    """
    if args.skip_hardening:
        return 0

    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None:
        return 0

    resolved_tracker = cleaned_tracker if cleaned_tracker.is_absolute() else (repo_root / cleaned_tracker)
    if not resolved_tracker.exists():
        print(f"{ANSIColors.RED}[ERROR] Tracker file not found for hardening: {tracker_path}{ANSIColors.RESET}")
        return 1

    tracker_content = resolved_tracker.read_text(encoding="utf-8")
    backend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.BACKEND)
    frontend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.FRONTEND)

    if not backend_targets and not frontend_targets:
        print(
            f"\n{ANSIColors.GREEN}--- No unhardened targets discovered in tracker for backend or frontend gates. ---{ANSIColors.RESET}"
        )
        return 0

    h_model = args.hardening_model or args.model

    # 1. Backend Hardening Gate
    if backend_targets:
        print(
            f"\n{ANSIColors.CYAN}--- Handing off to Post-Implementation Hardening Runner "
            f"(Backend: {len(backend_targets)} targets) ---{ANSIColors.RESET}"
        )
        backend_cmd = [
            "uv",
            "run",
            "python",
            "scripts/auto_hardening_runner.py",
            "--tracker",
            str(cleaned_tracker),
            "--gate",
            "backend",
        ]
        if args.hardening_agent:
            agent_cmd_template = (
                f'agy --model {h_model} --dangerously-skip-permissions --print "/tier2-hardening-backend {{target}}"'
            )
            backend_cmd.extend(["--agent-cmd", agent_cmd_template])
        if args.dry_run:
            backend_cmd.append("--dry-run")
        if args.verbose:
            backend_cmd.append("--verbose")

        proc_backend = subprocess.run(backend_cmd, cwd=repo_root, check=False)
        if proc_backend.returncode != 0:
            print(
                f"{ANSIColors.RED}[FAILED] Backend post-implementation hardening failed "
                f"with code {proc_backend.returncode}. Halting pipeline.{ANSIColors.RESET}"
            )
            return proc_backend.returncode

    # 2. Frontend Hardening Gate
    if frontend_targets:
        print(
            f"\n{ANSIColors.CYAN}--- Handing off to Post-Implementation Hardening Runner "
            f"(Frontend: {len(frontend_targets)} targets) ---{ANSIColors.RESET}"
        )
        frontend_cmd = [
            "uv",
            "run",
            "python",
            "scripts/auto_hardening_runner.py",
            "--tracker",
            str(cleaned_tracker),
            "--gate",
            "frontend",
        ]
        if args.hardening_agent:
            agent_cmd_template = (
                f'agy --model {h_model} --dangerously-skip-permissions --print "/tier2-hardening-frontend {{target}}"'
            )
            frontend_cmd.extend(["--agent-cmd", agent_cmd_template])
        if args.dry_run:
            frontend_cmd.append("--dry-run")
        if args.verbose:
            frontend_cmd.append("--verbose")

        proc_frontend = subprocess.run(frontend_cmd, cwd=repo_root, check=False)
        if proc_frontend.returncode != 0:
            print(
                f"{ANSIColors.RED}[FAILED] Frontend post-implementation hardening failed "
                f"with code {proc_frontend.returncode}. Halting pipeline.{ANSIColors.RESET}"
            )
            return proc_frontend.returncode

    return 0


def run_phase_pipeline(
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path | None = None,
) -> AutoPhaseRunSummaryDTO:
    """Execute the full autonomous headless multi-phase pipeline.

    Args:
        args: Configuration arguments.
        repo_root: Optional repository root path.

    Returns:
        AutoPhaseRunSummaryDTO summarizing execution statistics.
    """
    root = repo_root or get_repo_root()
    all_phases = parse_tracker_phases(args.tracker, repo_root=root)
    pending_phases = filter_phases(all_phases, from_phase=args.from_phase, only_phase=args.only_phase)

    print(
        f"\n{ANSIColors.BOLD}{ANSIColors.CYAN}"
        f"Autonomous Headless CLI Phase Orchestrator (Multi-Phase Pipeline Runner)\n"
        f"Tracker: {args.tracker}\n"
        f"Discovered Phases: {len(all_phases)} total, {len(pending_phases)} pending execution\n"
        f"Model: {args.model} | Timeout: {args.timeout}s"
        f"{ANSIColors.RESET}\n"
    )

    if args.dry_run:
        print(
            f"{ANSIColors.YELLOW}[DRY-RUN] Simulating phase execution without launching subprocesses:{ANSIColors.RESET}"
        )
        for p in pending_phases:
            print(f"  - Phase {p.phase_num}: {p.title} -> {p.command}")
        return AutoPhaseRunSummaryDTO(
            tracker_path=args.tracker,
            total_phases=len(all_phases),
            executed_phases=0,
            succeeded_phases=0,
            failed_phases=0,
            results=[],
        )

    results: list[PhaseExecutionResultDTO] = []
    executed_count = 0
    succeeded_count = 0
    failed_count = 0

    for phase in pending_phases:
        executed_count += 1
        print(
            f"\n{ANSIColors.BOLD}{ANSIColors.GREEN}"
            f"=== Starting Phase {phase.phase_num}: {phase.title} ==="
            f"{ANSIColors.RESET}\n"
            f"Command: {phase.command}\n"
        )

        subagent_res = execute_phase_subagent(phase, args, root)

        if subagent_res.is_timeout:
            print(
                f"\n{ANSIColors.RED}[TIMEOUT] Phase {phase.phase_num} timed out after "
                f"{subagent_res.duration_seconds:.1f}s. Subprocess tree killed.{ANSIColors.RESET}"
            )
            failed_count += 1
            results.append(
                PhaseExecutionResultDTO(
                    phase_num=phase.phase_num,
                    title=phase.title,
                    success=False,
                    duration_seconds=subagent_res.duration_seconds,
                    error_message=f"Timeout after {subagent_res.duration_seconds:.1f}s",
                )
            )
            break

        if subagent_res.exit_code != 0:
            print(
                f"\n{ANSIColors.RED}[FAILED] Phase {phase.phase_num} failed with exit code "
                f"{subagent_res.exit_code}. Halting pipeline immediately (circuit breaker).{ANSIColors.RESET}"
            )
            failed_count += 1
            results.append(
                PhaseExecutionResultDTO(
                    phase_num=phase.phase_num,
                    title=phase.title,
                    success=False,
                    duration_seconds=subagent_res.duration_seconds,
                    error_message=f"Subagent exited with code {subagent_res.exit_code}",
                )
            )
            break

        print(f"\n{ANSIColors.CYAN}Verifying Phase {phase.phase_num} Universal Quality Gate...{ANSIColors.RESET}")
        qg_res = run_phase_quality_gate(phase, root)

        if not qg_res.success:
            print(
                f"\n{ANSIColors.RED}[QUALITY GATE FAILED] Phase {phase.phase_num} audit loops failed "
                f"with code {qg_res.exit_code}. Halting pipeline immediately.{ANSIColors.RESET}"
            )
            failed_count += 1
            results.append(
                PhaseExecutionResultDTO(
                    phase_num=phase.phase_num,
                    title=phase.title,
                    success=False,
                    duration_seconds=subagent_res.duration_seconds,
                    error_message=f"Quality gate audit failed with exit code {qg_res.exit_code}",
                )
            )
            break

        # Checkpoint git commit and update tracker
        commit_hash: str | None = None
        if not args.skip_commit:
            commit_hash = commit_phase_checkpoint(phase, args.tracker, root)

        mark_phase_completed_in_tracker(args.tracker, phase.phase_num, commit_hash=commit_hash)

        succeeded_count += 1
        results.append(
            PhaseExecutionResultDTO(
                phase_num=phase.phase_num,
                title=phase.title,
                success=True,
                duration_seconds=subagent_res.duration_seconds,
            )
        )
        print(
            f"{ANSIColors.BOLD}{ANSIColors.GREEN}"
            f"=== Successfully Completed Phase {phase.phase_num}: {phase.title} "
            f"({subagent_res.duration_seconds:.1f}s) ==="
            f"{ANSIColors.RESET}"
        )

    # If all pending phases succeeded, run post-implementation hardening handoff
    if failed_count == 0 and executed_count > 0 and not args.skip_hardening:
        hardening_code = run_post_hardening_gate(args.tracker, args, root)
        if hardening_code != 0:
            print(
                f"{ANSIColors.YELLOW}[WARNING] Post-implementation hardening gate "
                f"exited with code {hardening_code}.{ANSIColors.RESET}"
            )

    return AutoPhaseRunSummaryDTO(
        tracker_path=args.tracker,
        total_phases=len(all_phases),
        executed_phases=executed_count,
        succeeded_phases=succeeded_count,
        failed_phases=failed_count,
        results=results,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Autonomous Headless CLI Phase Orchestrator."""
    setup_script_environment()

    parser = argparse.ArgumentParser(
        prog="auto_phase_runner.py",
        description="Autonomous Headless CLI Phase Orchestrator (Multi-Phase Pipeline Runner).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Autonomous AI Subagent Execution Examples:
------------------------------------------
1. Execute all pending phases in an Epic tracker unattended:
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md

2. Resume pipeline starting from Phase 3:
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --from-phase 3

3. Execute strictly Phase 2 (for targeted verification):
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --only-phase 2

4. Dry-run simulation (inspect discovered phases and commands without spawning subprocesses):
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --dry-run

5. Execute all phases and automatically run AI-driven Tier 2 hardening per file upon completion:
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --hardening-agent

Key Behavioral Invariants for Autonomous AI Agents:
- Subagent Isolation: Each phase spawns an independent `agy` CLI subagent process with a fresh context.
- Zero Context Drift: Eliminates token degradation across long multi-phase implementations.
- Universal Quality Gate: Automatically runs backend and flutter audit loops after each phase.
- Circuit Breaker: Halts immediately if any phase subagent or quality gate fails.
- Atomic Checkpoint: Commits phase changes and checks tracker markdown boxes in-place with commit hashes.
""",
    )
    parser.add_argument(
        "--tracker",
        type=Path,
        required=True,
        help="Path to target implementation tracker markdown file.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-4-argon-high",
        help="Model name for agy subagent execution (default: gemini-4-argon-high).",
    )
    parser.add_argument(
        "--from-phase",
        type=int,
        default=None,
        help="Start execution from phase N (skipping lower phase numbers).",
    )
    parser.add_argument(
        "--only-phase",
        type=int,
        default=None,
        help="Execute strictly phase N regardless of prior completion.",
    )
    parser.add_argument(
        "--skip-commit",
        action="store_true",
        default=False,
        help="Skip automated git commit after phase completion.",
    )
    parser.add_argument(
        "--skip-hardening",
        action="store_true",
        default=False,
        help="Skip post-implementation hardening handoff after phase execution.",
    )
    parser.add_argument(
        "--hardening-agent",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Dispatch AI-driven /tier2-hardening-backend or /tier2-hardening-frontend "
            "subagents per target file during hardening (enabled by default; use --no-hardening-agent to disable)."
        ),
    )
    parser.add_argument(
        "--hardening-model",
        type=str,
        default=None,
        help="LLM model override for hardening subagent; defaults to main model if None.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_SUBAGENT_TIMEOUT_SECONDS,
        help=f"Per-phase subagent timeout in seconds (default: {DEFAULT_SUBAGENT_TIMEOUT_SECONDS}).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_SUBAGENT_MAX_RETRIES,
        help=f"Max automatic retries for transient subagent startup failures (default: {DEFAULT_SUBAGENT_MAX_RETRIES}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simulate phase discovery and planned execution without launching subprocesses.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output logging.",
    )

    try:
        parsed = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        args_dto = AutoPhaseRunnerArgsDTO(
            tracker=parsed.tracker,
            model=parsed.model,
            from_phase=parsed.from_phase,
            only_phase=parsed.only_phase,
            skip_commit=parsed.skip_commit,
            skip_hardening=parsed.skip_hardening,
            hardening_agent=parsed.hardening_agent,
            hardening_model=parsed.hardening_model,
            max_retries=parsed.max_retries,
            timeout=parsed.timeout,
            dry_run=parsed.dry_run,
            verbose=parsed.verbose,
        )
    except (ValidationError, ValueError) as exc:
        print(f"{ANSIColors.RED}Configuration error: {exc}{ANSIColors.RESET}", file=sys.stderr)
        return 2

    try:
        summary = run_phase_pipeline(args_dto)
    except (FileNotFoundError, ValueError) as exc:
        print(f"{ANSIColors.RED}Execution error: {exc}{ANSIColors.RESET}", file=sys.stderr)
        return 1

    if summary.failed_phases > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
