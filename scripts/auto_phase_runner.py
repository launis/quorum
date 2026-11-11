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
   - Monitored by a watchdog timer (`--timeout`, default: 86400s).
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
from scripts.auto_hardening_runner import (
    HardeningGate,
    acquire_windows_wake_lock,
    check_tracker_has_unparsed_hardening_items,
    parse_tracker_unhardened_targets,
    release_windows_wake_lock,
)

GIT_SUBPROCESS_TIMEOUT_SECONDS: Final[int] = 120
TASKKILL_TIMEOUT_SECONDS: Final[int] = 30
DEFAULT_AUDIT_TIMEOUT_SECONDS: Final[int] = 14400
DEFAULT_SUBAGENT_TIMEOUT_SECONDS: Final[int] = 86400
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
    "PostLifecycleStageDTO",
    "QualityGateResultDTO",
    "SubagentExecutionResultDTO",
    "clean_path_arg",
    "commit_lifecycle_stage_checkpoint",
    "commit_phase_checkpoint",
    "execute_lifecycle_prompt_subagent",
    "execute_phase_subagent",
    "filter_phases",
    "main",
    "mark_phase_completed_in_tracker",
    "mark_red_teaming_completed_in_tracker",
    "mark_section_completed_in_tracker",
    "parse_tracker_phases",
    "parse_tracker_post_stage",
    "resolve_agy_binary",
    "run_integration_checkpoint_gate",
    "run_phase_pipeline",
    "run_phase_quality_gate",
    "run_post_hardening_gate",
    "run_tier7_documentation_gate",
    "run_tier8_final_audit_gate",
    "unquote_git_path",
]


class PhaseItemDTO(BaseModel):
    """Specification of an execution phase extracted from a tracker document."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    phase_num: Annotated[int, Field(description="Numerical index of the phase (1-based).")]
    title: Annotated[str, Field(description="Human-readable title of the phase.")]
    plan_path: Annotated[Path, Field(description="Resolved workspace-relative path to implementation plan .md.")]
    is_completed: Annotated[bool, Field(description="Whether execution checkbox is already marked [x].")]
    command: Annotated[str, Field(description="Extracted or default /tier2-execute slash command.")]
    red_team_command: Annotated[
        str | None,
        Field(default=None, description="Extracted /tier0-research-plan slash command if present."),
    ] = None
    is_red_teamed: Annotated[
        bool,
        Field(default=False, description="Whether Red-Teaming checkbox is already marked [x]."),
    ] = False


class PostLifecycleStageDTO(BaseModel):
    """Extracted state and slash command for a post-implementation lifecycle section."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    section_title: Annotated[str, Field(description="Markdown section title.")]
    is_completed: Annotated[bool, Field(description="Whether section checkbox is already marked [x].")]
    command: Annotated[str | None, Field(default=None, description="Extracted slash command if present.")] = None


class AutoPhaseRunnerArgsDTO(BaseModel):
    """Strict configuration parameters for the autonomous phase runner pipeline."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tracker: Annotated[Path, Field(description="Path to target tracker file.")]
    model: Annotated[str, Field(default="gemini-4-carbon-high", description="CLI model name.")] = "gemini-4-carbon-high"
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
            default="gemini-4-carbon-medium",
            description="LLM model for hardening subagent; defaults to gemini-4-carbon-medium.",
        ),
    ] = "gemini-4-carbon-medium"
    max_retries: Annotated[
        int,
        Field(
            default=DEFAULT_SUBAGENT_MAX_RETRIES,
            ge=1,
            description="Max automatic retry attempts for transient subagent startup failures.",
        ),
    ] = DEFAULT_SUBAGENT_MAX_RETRIES
    timeout: Annotated[
        int,
        Field(
            default=DEFAULT_SUBAGENT_TIMEOUT_SECONDS,
            ge=1,
            description="Per-phase and per-subagent timeout in seconds.",
        ),
    ] = DEFAULT_SUBAGENT_TIMEOUT_SECONDS
    full_lifecycle: Annotated[
        bool,
        Field(
            default=False,
            description=(
                "Execute complete start-to-finish lifecycle: Tier 0 Red-Teaming, Tier 2 Phase Execution, "
                "Full-Stack Integration Checkpoint, Tier 2 AI Hardening, Tier 7 Describe Architecture, "
                "and Tier 8 Final Epic/Plan Audit."
            ),
        ),
    ] = False
    with_live_e2e: Annotated[
        bool,
        Field(
            default=False,
            description="Include Live LLM E2E pytest verification during Integration Checkpoint.",
        ),
    ] = False
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
    """Normalize and strip markdown link wrappers, quotes, line bounds, and whitespace from a path argument."""
    if val is None:
        return None
    raw_str = str(val).strip().strip("`").strip("'").strip('"')
    if raw_str.startswith("@"):
        raw_str = raw_str[1:]
    raw_str = raw_str.strip().strip("[").strip("]").strip()
    if "#" in raw_str:
        raw_str = raw_str.split("#")[0].strip()
    raw_str = raw_str.strip().strip("`").strip("'").strip('"')
    if not raw_str:
        return None
    return Path(raw_str)


def unquote_git_path(raw_path: str) -> str:
    """Unquote and decode C-escaped octal/escaped file paths from git status --porcelain.

    Args:
        raw_path: Raw path extracted from a git status --porcelain line.

    Returns:
        Decoded UTF-8 file path with surrounding quotes stripped.
    """
    cleaned = raw_path.strip()
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ")[1].strip()
    if not (cleaned.startswith('"') and cleaned.endswith('"') and len(cleaned) >= 2):
        return cleaned
    inner = cleaned[1:-1]
    out_bytes = bytearray()
    idx = 0
    length = len(inner)
    while idx < length:
        ch = inner[idx]
        if ch == "\\" and idx + 1 < length:
            nxt = inner[idx + 1]
            if idx + 3 < length and all(c in "01234567" for c in inner[idx + 1 : idx + 4]):
                out_bytes.append(int(inner[idx + 1 : idx + 4], 8))
                idx += 4
                continue
            escape_map = {"\\": ord("\\"), '"': ord('"'), "t": ord("\t"), "n": ord("\n"), "r": ord("\r")}
            if nxt in escape_map:
                out_bytes.append(escape_map[nxt])
                idx += 2
                continue
        out_bytes.extend(ch.encode("utf-8"))
        idx += 1
    return out_bytes.decode("utf-8", errors="replace")


def _has_invalid_git_path_chars(path_str: str) -> bool:
    """Check whether a decoded path contains control or Private Use Area characters invalid on Windows."""
    return any(ord(c) < 32 or (0xE000 <= ord(c) <= 0xF8FF) or c in '<>:"|?*' for c in path_str)


_CARRIAGE_AND_ERASE_RE: Final[re.Pattern[str]] = re.compile(r"\r(?!\n)|\x1b\[[0-9;]*[GK]")


def _sanitize_stream_line(line: str) -> str:
    """Remove bare carriage returns and ANSI cursor-horizontal/line-erase codes that overwrite console lines."""
    return _CARRIAGE_AND_ERASE_RE.sub("", line)


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
    red_team_pattern = re.compile(
        r"-\s*\[([ xX])\]\s*(?:\([a-f0-9]+\)\s*)?\*\*\[(?:OK|NOK)\]\s*Red-Teaming(?:\s*\([^\)]+\))?:\*\*\s*"
        r"(?:`?(/tier0-research-plan[^\n`]+)`?|[^\n]*)",
        re.IGNORECASE,
    )
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

            # Extract Red-Teaming command & completion status
            rt_m = red_team_pattern.search(section_body)
            is_red_teamed = False
            red_team_cmd: str | None = None
            if rt_m:
                is_red_teamed = rt_m.group(1).lower() == "x"
                raw_rt = rt_m.group(2)
                if raw_rt:
                    cleaned_rt = raw_rt.strip().strip("`").strip()
                    cleaned_rt = re.sub(r"\s*\(`?[a-f0-9]+`?\)$", "", cleaned_rt, flags=re.IGNORECASE).strip()
                    red_team_cmd = cleaned_rt
                else:
                    rel_plan_posix = plan_path.as_posix()
                    rel_tracker_posix = cleaned_tracker.as_posix()
                    red_team_cmd = f"/tier0-research-plan @[{rel_plan_posix}] @[{rel_tracker_posix}]"

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
                    red_team_command=red_team_cmd,
                    is_red_teamed=is_red_teamed,
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
                sanitized_line = _sanitize_stream_line(line)
                collected_output.append(sanitized_line)
                try:
                    sys.stdout.write(sanitized_line)
                    sys.stdout.flush()
                except UnicodeEncodeError:
                    sys.stdout.buffer.write(sanitized_line.encode("utf-8", errors="replace"))
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


def execute_lifecycle_prompt_subagent(
    prompt: str,
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path,
) -> SubagentExecutionResultDTO:
    """Spawn an agy CLI subagent process for an arbitrary lifecycle prompt with streaming and retry loop.

    Args:
        prompt: Instruction prompt string to pass via `--print`.
        args: Pipeline runner arguments.
        repo_root: Repository root path for working directory.

    Returns:
        SubagentExecutionResultDTO capturing returncode, output, duration, and timeout status.

    Raises:
        FileNotFoundError: If the agy CLI binary cannot be resolved on the host system.
    """
    agy_bin = resolve_agy_binary()

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

    Raises:
        FileNotFoundError: If the agy CLI binary cannot be resolved on the host system.
    """
    prompt = phase.command
    if "PERMISSION GRANTED" not in prompt:
        prompt = (
            f"{phase.command}. PERMISSION GRANTED for continuous full-auto execution across all steps, "
            f"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem, and PERMISSION GRANTED for structural "
            f"seed_data.json schema updates with 100% coaching prompt preservation. "
            f"Proceed autonomously through all steps without intermediate confirmations."
        )
    return execute_lifecycle_prompt_subagent(prompt, args, repo_root)


def run_phase_quality_gate(phase: PhaseItemDTO, repo_root: Path) -> QualityGateResultDTO:
    """Execute the Universal Quality Gate audit checks on modified domains.

    Args:
        phase: Executed phase being audited.
        repo_root: Root directory of repository.

    Returns:
        QualityGateResultDTO with audit exit code and combined output.

    Raises:
        subprocess.SubprocessError: If audit subprocess invocation encounters an unexpected OS error.
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
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    dirty_scripts: list[str] = []
    if dirty_proc.returncode == 0:
        for line in dirty_proc.stdout.splitlines():
            if len(line) < 4:
                continue
            line_str = unquote_git_path(line[3:])
            if (
                not _has_invalid_git_path_chars(line_str)
                and line_str.startswith("scripts/")
                and line_str.endswith(".py")
                and Path(repo_root / line_str).exists()
            ):
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


def commit_lifecycle_stage_checkpoint(
    commit_msg: str,
    tracker_path: Path,
    repo_root: Path,
) -> str | None:
    """Commit completed lifecycle stage modifications atomically using Conventional Commits.

    Args:
        commit_msg: Conventional Commit message string.
        tracker_path: Path to tracker markdown file.
        repo_root: Root directory of repository.

    Returns:
        Short commit hash if a commit was executed, None if working tree was clean.

    Raises:
        subprocess.SubprocessError: If git subprocess execution encounters an OS error.
    """
    status_proc = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    if status_proc.returncode != 0:
        return None

    raw_lines = status_proc.stdout.splitlines()
    if not raw_lines:
        return None

    staged_candidates: list[str] = []
    for line in raw_lines:
        if len(line) < 4:
            continue
        status_code = line[:2]
        file_path = unquote_git_path(line[3:])
        if not file_path or _has_invalid_git_path_chars(file_path):
            continue
        if any(file_path.startswith(prefix) for prefix in (".gemini/", ".system_generated/", "scratch/", "tmp/")):
            continue
        if "D" not in status_code and (repo_root / ".git").exists() and not (repo_root / file_path).exists():
            continue
        staged_candidates.append(file_path)

    if not staged_candidates:
        return None

    tracker_rel = clean_path_arg(tracker_path)
    try:
        tracker_str = (tracker_path.resolve()).relative_to(repo_root.resolve()).as_posix()
    except ValueError, RuntimeError:
        tracker_str = tracker_rel.as_posix() if tracker_rel else str(tracker_path).replace("\\", "/")

    add_cmd = ["git", "add"] + staged_candidates
    if tracker_str not in staged_candidates and (
        not (repo_root / ".git").exists() or (repo_root / tracker_str).exists()
    ):
        add_cmd.append(tracker_str)

    subprocess.run(
        add_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
    )

    commit_proc = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
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
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    if rev_proc.returncode == 0:
        return rev_proc.stdout.strip()
    return None


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

    Raises:
        subprocess.SubprocessError: If git subprocess execution encounters an OS error.
    """
    status_proc = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    if status_proc.returncode != 0:
        return None

    raw_lines = status_proc.stdout.splitlines()
    if not raw_lines:
        return None

    # Filter files: exclude scratch, tmp, system generated, and corrupt/invalid pathspecs
    staged_candidates: list[str] = []
    for line in raw_lines:
        if len(line) < 4:
            continue
        status_code = line[:2]
        file_path = unquote_git_path(line[3:])
        if not file_path or _has_invalid_git_path_chars(file_path):
            continue

        # Exclude ephemeral/scratch paths
        if any(file_path.startswith(prefix) for prefix in (".gemini/", ".system_generated/", "scratch/", "tmp/")):
            continue
        # Skip non-existent untracked/corrupt paths unless marked as a tracked deletion
        if "D" not in status_code and (repo_root / ".git").exists() and not (repo_root / file_path).exists():
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
        subprocess.run(
            ["git", "add", tracker_str],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_root,
            check=False,
            timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
        )
    else:
        # Sanitize title removing redundant "Phase N:" prefix
        title_cleaned = re.sub(r"^Phase\s+\d+[:\-]?\s*", "", phase.title, flags=re.IGNORECASE).strip()
        commit_msg = f"feat(phase{phase.phase_num}): complete {title_cleaned}"
        # Stage filtered candidates and tracker
        add_cmd = ["git", "add"] + staged_candidates
        if tracker_str not in staged_candidates and (
            not (repo_root / ".git").exists() or (repo_root / tracker_str).exists()
        ):
            add_cmd.append(tracker_str)
        subprocess.run(
            add_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_root,
            check=False,
            timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
        )

    commit_proc = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=repo_root,
        check=False,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
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
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
    )
    if rev_proc.returncode == 0:
        return rev_proc.stdout.strip()
    return None


def mark_red_teaming_completed_in_tracker(
    tracker_path: Path,
    phase_num: int,
    commit_hash: str | None = None,
) -> None:
    """Mark a phase Red-Teaming row as completed ([x] **[OK] Red-Teaming:**) in tracker markdown in-place.

    Args:
        tracker_path: Path to tracker markdown file.
        phase_num: Index of phase to mark red-teamed.
        commit_hash: Optional short git commit hash to record on Red-Teaming line.

    Raises:
        OSError: If reading or writing the tracker file fails.
    """
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None or not cleaned_tracker.exists():
        return

    content = cleaned_tracker.read_text(encoding="utf-8")
    phase_header_pattern = re.compile(rf"^### Phase\s+{phase_num}[:\-]?", re.MULTILINE | re.IGNORECASE)
    match = phase_header_pattern.search(content)
    if not match:
        return

    start_idx = match.start()
    next_boundary = re.search(
        r"(?m)^(?:### Phase\s+\d+|### Integration Checkpoint|### Post-Implementation|\Z)",
        content[match.end() :],
    )
    end_idx = match.end() + next_boundary.start() if next_boundary else len(content)
    section_slice = content[start_idx:end_idx]

    def _replace_rt(m: re.Match[str]) -> str:
        cmd = m.group(1).strip()
        cmd_clean = re.sub(r"\s*\(`?[a-f0-9]+`?\)$", "", cmd, flags=re.IGNORECASE).strip().strip("`").strip()
        if commit_hash:
            return f"- [x] **[OK] Red-Teaming:** `{cmd_clean}` (`{commit_hash}`)"
        return f"- [x] **[OK] Red-Teaming:** `{cmd_clean}`"

    rt_line_re = re.compile(
        r"-\s*\[[ xX]\]\s*(?:\([a-f0-9]+\)\s*)?\*\*\[(?:OK|NOK)\]\s*Red-Teaming(?:\s*\([^\)]+\))?:\*\*\s*"
        r"`?([^`\n]+)`?(?:\s*\(`?[a-f0-9]+`?\))?",
        re.IGNORECASE,
    )
    updated_slice = rt_line_re.sub(_replace_rt, section_slice)
    updated_content = content[:start_idx] + updated_slice + content[end_idx:]
    cleaned_tracker.write_text(updated_content, encoding="utf-8")


def parse_tracker_post_stage(
    tracker_content: str,
    section_header_regex: str,
    slash_prefix: str,
) -> PostLifecycleStageDTO:
    """Extract completion status and slash command from a post-implementation tracker section.

    Args:
        tracker_content: Raw markdown text of tracker file.
        section_header_regex: Regex matching the target markdown section heading.
        slash_prefix: Expected slash command prefix (such as `/tier7-describe-architecture`).

    Returns:
        PostLifecycleStageDTO containing section title, completion status, and extracted command.
    """
    sec_match = re.search(section_header_regex, tracker_content, re.MULTILINE | re.IGNORECASE)
    if not sec_match:
        return PostLifecycleStageDTO(section_title=slash_prefix, is_completed=True, command=None)

    section_title = sec_match.group(0).lstrip("#").strip()
    next_boundary = re.search(
        r"(?m)^(?:###\s+|##\s+|#\s+|\Z)",
        tracker_content[sec_match.end() :],
    )
    end_idx = sec_match.end() + next_boundary.start() if next_boundary else len(tracker_content)
    section_slice = tracker_content[sec_match.start() : end_idx]

    checkboxes = re.findall(r"^-\s*\[([ xX])\]", section_slice, re.MULTILINE)
    is_completed = bool(checkboxes) and all(c.lower() == "x" for c in checkboxes)

    cmd_re = re.compile(rf"({re.escape(slash_prefix)}[^\n`]*)", re.IGNORECASE)
    cmd_match = cmd_re.search(section_slice)
    command = cmd_match.group(1).strip() if cmd_match else None

    return PostLifecycleStageDTO(
        section_title=section_title,
        is_completed=is_completed,
        command=command,
    )


def mark_section_completed_in_tracker(
    tracker_path: Path,
    section_header_regex: str,
) -> None:
    """Mark all top-level checkboxes (`- [ ] **[NOK]`) inside a tracker section as completed (`- [x] **[OK]`).

    Args:
        tracker_path: Path to tracker markdown file.
        section_header_regex: Regex matching the target section header.

    Raises:
        OSError: If reading or writing the tracker file fails.
    """
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None or not cleaned_tracker.exists():
        return

    content = cleaned_tracker.read_text(encoding="utf-8")
    sec_match = re.search(section_header_regex, content, re.MULTILINE | re.IGNORECASE)
    if not sec_match:
        return

    start_idx = sec_match.start()
    next_boundary = re.search(r"(?m)^(?:###\s+|##\s+|#\s+|\Z)", content[sec_match.end() :])
    end_idx = sec_match.end() + next_boundary.start() if next_boundary else len(content)

    section_slice = content[start_idx:end_idx]
    updated_slice = re.sub(
        r"^(-\s*)\[[ xX]\](\s*\*\*)\[(?:OK|NOK)\]",
        r"\1[x]\2[OK]",
        section_slice,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    updated_slice = re.sub(
        r"^(-\s*)\[ \]",
        r"\1[x]",
        updated_slice,
        flags=re.MULTILINE,
    )
    updated_content = content[:start_idx] + updated_slice + content[end_idx:]
    cleaned_tracker.write_text(updated_content, encoding="utf-8")


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
        print(
            f"{ANSIColors.RED}[ERROR] Tracker file not found for hardening: {tracker_path}{ANSIColors.RESET}",
            flush=True,
        )
        return 1

    tracker_content = resolved_tracker.read_text(encoding="utf-8")
    backend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.BACKEND)
    frontend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.FRONTEND)

    if not backend_targets and not frontend_targets:
        has_unparsed_backend = check_tracker_has_unparsed_hardening_items(tracker_content, HardeningGate.BACKEND)
        has_unparsed_frontend = check_tracker_has_unparsed_hardening_items(tracker_content, HardeningGate.FRONTEND)
        if has_unparsed_backend or has_unparsed_frontend:
            unparsed_gates: list[str] = []
            if has_unparsed_backend:
                unparsed_gates.append("Backend")
            if has_unparsed_frontend:
                unparsed_gates.append("Frontend")
            print(
                f"{ANSIColors.RED}[ERROR] Tracker {tracker_path} has pending Tier 2 Hardening "
                f"({', '.join(unparsed_gates)}) checklist items, but zero targets could be parsed "
                f"into valid file paths. Check markdown formatting!{ANSIColors.RESET}",
                flush=True,
            )
            return 1

        print(
            f"\n{ANSIColors.GREEN}--- No unhardened targets discovered in tracker for backend or frontend gates. ---{ANSIColors.RESET}",
            flush=True,
        )
        return 0

    h_model = args.hardening_model or "gemini-4-carbon-medium"

    # 1. Backend Hardening Gate
    if backend_targets:
        print(
            f"\n{ANSIColors.CYAN}--- Handing off to Post-Implementation Hardening Runner "
            f"(Backend: {len(backend_targets)} targets) ---{ANSIColors.RESET}",
            flush=True,
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
            "--model",
            h_model,
        ]
        if args.hardening_agent:
            agent_cmd_template = (
                f'agy --model {h_model} --dangerously-skip-permissions --print "/tier2-hardening-backend @[{{target}}]"'
            )
            backend_cmd.extend(["--agent-cmd", agent_cmd_template])
        else:
            backend_cmd.append("--no-agent")
        if args.dry_run:
            backend_cmd.append("--dry-run")
        if args.verbose:
            backend_cmd.append("--verbose")

        proc_backend = subprocess.run(backend_cmd, cwd=repo_root, check=False)
        if proc_backend.returncode != 0:
            print(
                f"{ANSIColors.RED}[FAILED] Backend post-implementation hardening failed "
                f"with code {proc_backend.returncode}. Halting pipeline.{ANSIColors.RESET}",
                flush=True,
            )
            return proc_backend.returncode

    # 2. Frontend Hardening Gate
    if frontend_targets:
        print(
            f"\n{ANSIColors.CYAN}--- Handing off to Post-Implementation Hardening Runner "
            f"(Frontend: {len(frontend_targets)} targets) ---{ANSIColors.RESET}",
            flush=True,
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
            "--model",
            h_model,
        ]
        if args.hardening_agent:
            agent_cmd_template = f'agy --model {h_model} --dangerously-skip-permissions --print "/tier2-hardening-frontend @[{{target}}]"'
            frontend_cmd.extend(["--agent-cmd", agent_cmd_template])
        else:
            frontend_cmd.append("--no-agent")
        if args.dry_run:
            frontend_cmd.append("--dry-run")
        if args.verbose:
            frontend_cmd.append("--verbose")

        proc_frontend = subprocess.run(frontend_cmd, cwd=repo_root, check=False)
        if proc_frontend.returncode != 0:
            print(
                f"{ANSIColors.RED}[FAILED] Frontend post-implementation hardening failed "
                f"with code {proc_frontend.returncode}. Halting pipeline.{ANSIColors.RESET}",
                flush=True,
            )
            return proc_frontend.returncode

    return 0


def run_integration_checkpoint_gate(
    tracker_path: Path,
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path,
) -> int:
    """Execute Full-Stack Integration Checkpoint gates (Seed Vault, Zero-ORM, DTO Parity, Audits, optional Live E2E).

    Args:
        tracker_path: Path to tracker markdown file.
        args: Pipeline runner arguments.
        repo_root: Repository root directory.

    Returns:
        Exit code (0 on success, non-zero on first gate failure).

    Raises:
        subprocess.SubprocessError: If any integration gate subprocess encounters an OS execution failure.
    """
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None:
        return 0
    resolved_tracker = cleaned_tracker if cleaned_tracker.is_absolute() else (repo_root / cleaned_tracker)

    commands: list[tuple[str, list[str]]] = [
        (
            "Seed Vault Dry-Run",
            ["uv", "run", "--no-sync", "--offline", "python", "backend_v2/seed/run_seed.py", "local", "--dry-run"],
        ),
        (
            "Database Atoms Strict Audit",
            ["uv", "run", "--no-sync", "--offline", "python", "scripts/audit_database_atoms.py", "--strict"],
        ),
        (
            "Seed Vault Local Execution",
            ["uv", "run", "--no-sync", "--offline", "python", "backend_v2/seed/run_seed.py", "local"],
        ),
        (
            "Zero-ORM Strictness Gate",
            ["uv", "run", "--no-sync", "--offline", "python", "scripts/audit_zero_orm_strictness.py"],
        ),
        (
            "Cross-Language DTO Parity Gate",
            ["uv", "run", "--no-sync", "--offline", "python", "scripts/audit_dto_parity.py", "--fail-on-mismatch"],
        ),
        (
            "Skills Architecture Gate",
            ["uv", "run", "--no-sync", "--offline", "python", "scripts/audit_skills_architecture.py"],
        ),
        (
            "Global Backend Audit Loop",
            [
                "uv",
                "run",
                "--no-sync",
                "--offline",
                "python",
                "scripts/backend_audit_loop.py",
                "backend_v2/",
                "--test",
                "--ast-strict",
            ],
        ),
        (
            "Global Flutter Audit Loop",
            [
                "uv",
                "run",
                "--no-sync",
                "--offline",
                "python",
                "scripts/flutter_audit_loop.py",
                "client_app_v2/",
                "--build",
            ],
        ),
    ]
    if args.with_live_e2e:
        commands.append(
            (
                "Live E2E REST API Verification Gate",
                [
                    "uv",
                    "run",
                    "--no-sync",
                    "--offline",
                    "pytest",
                    "backend_v2/tests/integration/test_integration_real_llm.py",
                ],
            )
        )

    env = os.environ.copy()
    env["UV_NO_SYNC"] = "1"
    env["UV_OFFLINE"] = "1"
    if args.with_live_e2e:
        env["RUN_LIVE_E2E"] = "true"

    print(
        f"\n{ANSIColors.CYAN}=== Executing Full-Stack Integration Checkpoint ({len(commands)} gates) ==={ANSIColors.RESET}",
        flush=True,
    )
    for label, cmd in commands:
        print(f"  -> Running Integration Gate: {label}", flush=True)
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            env=env,
            check=False,
            timeout=DEFAULT_AUDIT_TIMEOUT_SECONDS,
        )
        if proc.returncode != 0:
            print(
                f"{ANSIColors.RED}[FAILED] Integration Gate '{label}' failed with exit code {proc.returncode}.{ANSIColors.RESET}",
                flush=True,
            )
            return proc.returncode

    if resolved_tracker.exists():
        mark_section_completed_in_tracker(resolved_tracker, r"^###\s+Integration\s+Checkpoint")
        if not args.skip_commit:
            commit_lifecycle_stage_checkpoint(
                "chore(integration): complete full-stack integration checkpoint gates",
                resolved_tracker,
                repo_root,
            )
    return 0


def run_tier7_documentation_gate(
    tracker_path: Path,
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path,
) -> int:
    """Execute Tier 7 As-Built Architectural & Knowledge Item Sync gate from tracker.

    Args:
        tracker_path: Path to tracker markdown file.
        args: Pipeline runner arguments.
        repo_root: Repository root directory.

    Returns:
        Exit code (0 on success or already completed, non-zero on failure).

    Raises:
        FileNotFoundError: If the agy binary cannot be resolved when executing the subagent.
    """
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None:
        return 0
    resolved_tracker = cleaned_tracker if cleaned_tracker.is_absolute() else (repo_root / cleaned_tracker)
    if not resolved_tracker.exists():
        return 1

    stage = parse_tracker_post_stage(
        resolved_tracker.read_text(encoding="utf-8"),
        r"^###\s+Documentation\s*&\s*Knowledge\s+Item\s+Update",
        "/tier7-describe-architecture",
    )
    if stage.is_completed or not stage.command:
        return 0

    print(
        f"\n{ANSIColors.CYAN}=== Executing Tier 7 As-Built Architectural & KI Sync ==={ANSIColors.RESET}\n"
        f"Command: {stage.command}\n",
        flush=True,
    )
    prompt = (
        f"{stage.command}. PERMISSION GRANTED for continuous full-auto execution. "
        f"Synchronize all listed Knowledge Items, .agents/rules/04_directory_reference.md, "
        f"and docs/architecture/ narratives in timeless present tense without intermediate confirmations."
    )
    res = execute_lifecycle_prompt_subagent(prompt, args, repo_root)
    if res.is_timeout or res.exit_code != 0:
        return res.exit_code if res.exit_code != 0 else 1

    mark_section_completed_in_tracker(resolved_tracker, r"^###\s+Documentation\s*&\s*Knowledge\s+Item\s+Update")
    if not args.skip_commit:
        commit_lifecycle_stage_checkpoint(
            "docs(arch): synchronize as-built architecture and knowledge items",
            resolved_tracker,
            repo_root,
        )
    return 0


def run_tier8_final_audit_gate(
    tracker_path: Path,
    args: AutoPhaseRunnerArgsDTO,
    repo_root: Path,
) -> int:
    """Execute Tier 8 Final System 2 Reverse Epic/Plan Audit gate from tracker.

    Args:
        tracker_path: Path to tracker markdown file.
        args: Pipeline runner arguments.
        repo_root: Repository root directory.

    Returns:
        Exit code (0 on success or already completed, non-zero on failure).

    Raises:
        FileNotFoundError: If the agy binary cannot be resolved when executing the subagent.
    """
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker is None:
        return 0
    resolved_tracker = cleaned_tracker if cleaned_tracker.is_absolute() else (repo_root / cleaned_tracker)
    if not resolved_tracker.exists():
        return 1

    tracker_text = resolved_tracker.read_text(encoding="utf-8")
    stage = parse_tracker_post_stage(
        tracker_text,
        r"^###\s+Final\s+Epic\s+Audit",
        "/tier8-audit-epic",
    )
    if stage.command is None:
        stage = parse_tracker_post_stage(
            tracker_text,
            r"^###\s+Final\s+Plan\s+Audit",
            "/tier8-audit-plan",
        )
    if stage.is_completed or not stage.command:
        return 0

    print(
        f"\n{ANSIColors.CYAN}=== Executing Tier 8 Final System 2 Audit ==={ANSIColors.RESET}\n"
        f"Command: {stage.command}\n",
        flush=True,
    )
    prompt = (
        f"{stage.command}. PERMISSION GRANTED for continuous full-auto System 2 audit execution. "
        f"Proceed autonomously without intermediate confirmations."
    )
    res = execute_lifecycle_prompt_subagent(prompt, args, repo_root)
    if res.is_timeout or res.exit_code != 0:
        return res.exit_code if res.exit_code != 0 else 1

    mark_section_completed_in_tracker(resolved_tracker, r"^###\s+Final\s+(?:Epic|Plan)\s+Audit")
    if not args.skip_commit:
        commit_lifecycle_stage_checkpoint(
            "docs(audit): complete final system 2 reverse audit",
            resolved_tracker,
            repo_root,
        )
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
        f"Model: {args.model} | Timeout: {args.timeout}s | Full-Lifecycle: {args.full_lifecycle}"
        f"{ANSIColors.RESET}\n",
        flush=True,
    )

    if args.dry_run:
        print(
            f"{ANSIColors.YELLOW}[DRY-RUN] Simulating phase execution without launching subprocesses:{ANSIColors.RESET}",
            flush=True,
        )
        for p in pending_phases:
            if args.full_lifecycle and not p.is_red_teamed and p.red_team_command:
                print(f"  - Phase {p.phase_num} [Tier 0 Red-Teaming]: {p.red_team_command}", flush=True)
            print(f"  - Phase {p.phase_num}: {p.title} -> {p.command}", flush=True)
        if args.full_lifecycle:
            cleaned_tracker = clean_path_arg(args.tracker)
            resolved_tracker = (
                cleaned_tracker
                if cleaned_tracker and cleaned_tracker.is_absolute()
                else (root / cleaned_tracker if cleaned_tracker else root)
            )
            if resolved_tracker.is_file():
                t_text = resolved_tracker.read_text(encoding="utf-8")
                t7 = parse_tracker_post_stage(
                    t_text, r"^###\s+Documentation\s*&\s*Knowledge\s+Item\s+Update", "/tier7-describe-architecture"
                )
                t8 = parse_tracker_post_stage(t_text, r"^###\s+Final\s+Epic\s+Audit", "/tier8-audit-epic")
                if t8.command is None:
                    t8 = parse_tracker_post_stage(t_text, r"^###\s+Final\s+Plan\s+Audit", "/tier8-audit-plan")
                print(
                    "  - [Post-Phase] Full-Stack Integration Checkpoint (Seed Vault, Zero-ORM, DTO Parity, Audits)",
                    flush=True,
                )
                if t7.command and not t7.is_completed:
                    print(f"  - [Post-Phase Tier 7]: {t7.command}", flush=True)
                if t8.command and not t8.is_completed:
                    print(f"  - [Post-Phase Tier 8]: {t8.command}", flush=True)
        return AutoPhaseRunSummaryDTO(
            tracker_path=args.tracker,
            total_phases=len(all_phases),
            executed_phases=0,
            succeeded_phases=0,
            failed_phases=0,
            results=[],
        )

    wake_lock_state = acquire_windows_wake_lock()
    try:
        results: list[PhaseExecutionResultDTO] = []
        executed_count = 0
        succeeded_count = 0
        failed_count = 0

        for phase in pending_phases:
            if args.full_lifecycle and not phase.is_red_teamed and phase.red_team_command:
                print(
                    f"\n{ANSIColors.BOLD}{ANSIColors.CYAN}"
                    f"=== Tier 0 Red-Teaming Phase {phase.phase_num}: {phase.title} ==="
                    f"{ANSIColors.RESET}\n"
                    f"Command: {phase.red_team_command}\n",
                    flush=True,
                )
                rt_prompt = (
                    f"{phase.red_team_command}. PERMISSION GRANTED for continuous full-auto red-teaming. "
                    f"Auto-apply any minor boundary or contract fixes directly to the plan and tracker "
                    f"without intermediate confirmations."
                )
                rt_res = execute_lifecycle_prompt_subagent(rt_prompt, args, root)
                if rt_res.is_timeout or rt_res.exit_code != 0:
                    failed_count += 1
                    err_msg = (
                        f"Tier 0 Red-Teaming timeout after {rt_res.duration_seconds:.1f}s"
                        if rt_res.is_timeout
                        else f"Tier 0 Red-Teaming exited with code {rt_res.exit_code}"
                    )
                    results.append(
                        PhaseExecutionResultDTO(
                            phase_num=phase.phase_num,
                            title=phase.title,
                            success=False,
                            duration_seconds=rt_res.duration_seconds,
                            error_message=err_msg,
                        )
                    )
                    break
                mark_red_teaming_completed_in_tracker(args.tracker, phase.phase_num)
                if not args.skip_commit:
                    commit_lifecycle_stage_checkpoint(
                        f"docs(phase{phase.phase_num}): complete tier 0 red-teaming for phase {phase.phase_num}",
                        args.tracker,
                        root,
                    )

            executed_count += 1
            print(
                f"\n{ANSIColors.BOLD}{ANSIColors.GREEN}"
                f"=== Starting Phase {phase.phase_num}: {phase.title} ==="
                f"{ANSIColors.RESET}\n"
                f"Command: {phase.command}\n",
                flush=True,
            )

            subagent_res = execute_phase_subagent(phase, args, root)

            if subagent_res.is_timeout:
                print(
                    f"\n{ANSIColors.RED}[TIMEOUT] Phase {phase.phase_num} timed out after "
                    f"{subagent_res.duration_seconds:.1f}s. Subprocess tree killed.{ANSIColors.RESET}",
                    flush=True,
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
                    f"{subagent_res.exit_code}. Halting pipeline immediately (circuit breaker).{ANSIColors.RESET}",
                    flush=True,
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

            print(
                f"\n{ANSIColors.CYAN}Verifying Phase {phase.phase_num} Universal Quality Gate...{ANSIColors.RESET}",
                flush=True,
            )
            qg_res = run_phase_quality_gate(phase, root)

            if not qg_res.success:
                print(
                    f"\n{ANSIColors.RED}[QUALITY GATE FAILED] Phase {phase.phase_num} audit loops failed "
                    f"with code {qg_res.exit_code}. Halting pipeline immediately.{ANSIColors.RESET}",
                    flush=True,
                )
                if qg_res.output:
                    print(f"\n{ANSIColors.YELLOW}--- Quality Gate Output ---{ANSIColors.RESET}", flush=True)
                    print(qg_res.output, flush=True)
                    print(f"{ANSIColors.YELLOW}--- End Quality Gate Output ---{ANSIColors.RESET}\n", flush=True)
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
                f"{ANSIColors.RESET}",
                flush=True,
            )

        # If all pending phases succeeded, run post-implementation hardening and full-lifecycle gates
        if failed_count == 0 and (executed_count > 0 or args.full_lifecycle):
            if not args.skip_hardening:
                hardening_code = run_post_hardening_gate(args.tracker, args, root)
                if hardening_code != 0:
                    print(
                        f"{ANSIColors.YELLOW}[WARNING] Post-implementation hardening gate "
                        f"exited with code {hardening_code}.{ANSIColors.RESET}",
                        flush=True,
                    )
                    if args.full_lifecycle:
                        failed_count += 1

            if args.full_lifecycle and failed_count == 0:
                ic_code = run_integration_checkpoint_gate(args.tracker, args, root)
                if ic_code != 0:
                    failed_count += 1
                else:
                    t7_code = run_tier7_documentation_gate(args.tracker, args, root)
                    if t7_code != 0:
                        failed_count += 1
                    else:
                        t8_code = run_tier8_final_audit_gate(args.tracker, args, root)
                        if t8_code != 0:
                            failed_count += 1

        return AutoPhaseRunSummaryDTO(
            tracker_path=args.tracker,
            total_phases=len(all_phases),
            executed_phases=executed_count,
            succeeded_phases=succeeded_count,
            failed_phases=failed_count,
            results=results,
        )
    finally:
        release_windows_wake_lock(wake_lock_state)


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

2. Execute FULL start-to-finish lifecycle (Tier 0 Red-Teaming -> Phases -> Hardening -> Seed/Parity/Audits -> Tier 7 -> Tier 8):
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --full-lifecycle --timeout 86400

3. Resume pipeline starting from Phase 3:
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --from-phase 3

4. Execute strictly Phase 2 (for targeted verification):
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --only-phase 2

5. Dry-run simulation (inspect discovered phases and commands without spawning subprocesses):
   uv run python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_042_tracker.md --full-lifecycle --dry-run

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
        default="gemini-4-carbon-high",
        help="Model name for agy subagent execution (default: gemini-4-carbon-high).",
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
        default="gemini-4-carbon-medium",
        help="LLM model override for hardening subagent (default: gemini-4-carbon-medium).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_SUBAGENT_TIMEOUT_SECONDS,
        help=f"Per-phase and per-subagent timeout in seconds (default: {DEFAULT_SUBAGENT_TIMEOUT_SECONDS}).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_SUBAGENT_MAX_RETRIES,
        help=f"Max automatic retries for transient subagent startup failures (default: {DEFAULT_SUBAGENT_MAX_RETRIES}).",
    )
    parser.add_argument(
        "--full-lifecycle",
        action="store_true",
        default=False,
        help=(
            "Execute complete start-to-finish Epic/Plan lifecycle: Tier 0 Red-Teaming, Tier 2 Phase Execution, "
            "Tier 2 AI Hardening, Full-Stack Integration Checkpoint, Tier 7 Describe Architecture, and Tier 8 Audit."
        ),
    )
    parser.add_argument(
        "--with-live-e2e",
        action="store_true",
        default=False,
        help="Include Live LLM E2E pytest verification during the Full-Stack Integration Checkpoint.",
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
            full_lifecycle=parsed.full_lifecycle,
            with_live_e2e=parsed.with_live_e2e,
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
