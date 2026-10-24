"""Headless CLI Hardening Runner (Overnight Multi-Process Pipeline).

Orchestrates unattended overnight post-implementation hardening across isolated subagent
processes with native markdown checklist discovery, audit verification loops, retry circuit
breaking with workspace rollback, and atomic git checkpointing.

Architectural Workflow & Lifecycle:
-----------------------------------
1. Target Discovery & Ingress:
   - Discovers unhardened target files from markdown tracker checklists (`- [ ] @[path]`)
     under `Tier 2 Hardening (Backend)` or `Tier 2 Hardening (Frontend)`.
   - Alternatively ingests targets from a persistent JSON state file (`hardening_state.json`)
     or explicit `--targets` CLI arguments.
2. Deterministic State Tracking (`REMAINING = TARGETS - DONE`):
   - Synchronizes state across sessions using a two-key JSON schema (`TARGETS` vs `DONE`).
   - Ensures zero duplicate work upon resume, maintaining stateful progress tracking.
3. Pre-Flight Snapshot & Circuit Breaker Rollback:
   - Takes a workspace snapshot (`git status --porcelain`) prior to hardening each target.
   - If quality gates fail after exhausting retries, rolls back newly modified and untracked
     files, preventing dirty workspace corruption.
4. Auto-Fix & Optional Subagent Pass:
   - Executes automated formatting (`ruff format` / `dart format`).
   - If `--agent-cmd` is provided, executes an AI subagent command template (e.g. `/tier2-hardening-backend`)
     to autonomously remediate AST, typing, or linting errors.
5. Universal Quality Gate Audit:
   - Backend: Runs `scripts/backend_audit_loop.py <target> --test --ast-strict`.
   - Frontend: Runs `scripts/flutter_audit_loop.py <target> --build`.
   - Verifies Ruff formatting, MyPy strict typing, AST guardrails, and unit tests.
6. Atomic Checkpointing & In-Place Tracker Marking:
   - Marks target checklist item `- [x]` in the tracker markdown in-place.
   - Automatically marks parent gate section `- [x]` once all child files are verified.
   - Updates `hardening_state.json` and performs an atomic git commit (`chore(hardening): complete <target>`).

CLI Usage Examples for Autonomous AI Agents:
--------------------------------------------
# 1. Standard unattended hardening from an implementation tracker:
uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --gate backend

# 2. Resume hardening from a saved sandbox state file:
uv run python scripts/auto_hardening_runner.py --state-file scratch/hardening_state.json --gate backend

# 3. Targeted hardening for specific explicit files:
uv run python scripts/auto_hardening_runner.py --targets backend_v2/services/foo.py backend_v2/models/bar.py

# 4. Dry-run inspection to preview discovered targets without executing audits or mutations:
uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --dry-run

# 5. AI-driven autonomous hardening with subagent execution per file:
uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --agent-cmd "agy --dangerously-skip-permissions -i '/tier2-hardening-backend @[{target}]'"
"""

from __future__ import annotations

import argparse
import re
import shlex
import shutil
import subprocess
import sys
import time
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Final

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, ValidationError

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from scripts._script_base import ANSIColors, get_repo_root, setup_script_environment

GIT_SUBPROCESS_TIMEOUT_SECONDS: Final[int] = 30
TASKKILL_TIMEOUT_SECONDS: Final[int] = 15
FORMATTER_TIMEOUT_SECONDS: Final[int] = 60
DEFAULT_AUDIT_TIMEOUT_SECONDS: Final[int] = 600

__all__ = [
    "CheckpointResultDTO",
    "DEFAULT_AUDIT_TIMEOUT_SECONDS",
    "FORMATTER_TIMEOUT_SECONDS",
    "GIT_SUBPROCESS_TIMEOUT_SECONDS",
    "HardeningGate",
    "HardeningIterationResultDTO",
    "HardeningRunSummaryDTO",
    "HardeningRunnerArgsDTO",
    "HardeningStateFileDTO",
    "QualityGateResultDTO",
    "TASKKILL_TIMEOUT_SECONDS",
    "WorkspaceSnapshotDTO",
    "capture_workspace_snapshot",
    "clean_path_arg",
    "execute_circuit_breaker_rollback",
    "execute_subagent_pass",
    "execute_subprocess_with_tree_kill",
    "fetch_unhardened_targets",
    "main",
    "mark_tracker_and_checkpoint",
    "mark_tracker_target_done",
    "parse_tracker_unhardened_targets",
    "process_target_with_retries",
    "run_hardening_pipeline",
    "run_quality_gate",
]


class HardeningGate(StrEnum):
    """Hardening gate category corresponding to tracker sections and audit runners."""

    BACKEND = "backend"
    FRONTEND = "frontend"


class HardeningRunnerArgsDTO(BaseModel):
    """Strict configuration parameters for the hardening runner pipeline."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tracker: Annotated[Path | None, Field(default=None, description="Path to tracker markdown file.")] = None
    state_file: Annotated[Path | None, Field(default=None, description="Path to hardening_state.json.")] = None
    gate: Annotated[HardeningGate, Field(default=HardeningGate.BACKEND, description="Hardening gate category.")] = (
        HardeningGate.BACKEND
    )
    targets: Annotated[list[str] | None, Field(default=None, description="Explicit target file paths.")] = None
    max_files: Annotated[int | None, Field(default=None, description="Maximum number of files to process.")] = None
    max_retries: Annotated[int, Field(default=2, ge=0, description="Maximum retries per file on audit failure.")] = 2
    timeout_seconds: Annotated[
        int, Field(default=DEFAULT_AUDIT_TIMEOUT_SECONDS, ge=1, description="Per-file audit timeout in seconds.")
    ] = DEFAULT_AUDIT_TIMEOUT_SECONDS
    agent_cmd: Annotated[
        str | None, Field(default=None, description="Optional command template for subagent execution before audit.")
    ] = None
    no_auto_fix: Annotated[
        bool, Field(default=False, description="Disable automatic ruff/dart format passes before audit.")
    ] = False
    fail_fast: Annotated[
        bool, Field(default=True, description="Halt execution immediately on unrecoverable failure.")
    ] = True
    continue_on_failure: Annotated[
        bool, Field(default=False, description="Continue to next target on failure rather than stopping.")
    ] = False
    dry_run: Annotated[
        bool, Field(default=False, description="Print planned execution steps without mutating disk or git.")
    ] = False
    verbose: Annotated[bool, Field(default=False, description="Enable verbose log output.")] = False


class HardeningIterationResultDTO(BaseModel):
    """Outcome record for an individual target file hardening iteration."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_file: Annotated[str, Field(description="Target file relative path.")]
    gate: Annotated[HardeningGate, Field(description="Target hardening gate.")]
    success: Annotated[bool, Field(description="Whether the target successfully passed quality gates.")]
    attempts: Annotated[int, Field(description="Number of attempts executed.")]
    duration_seconds: Annotated[float, Field(description="Duration of attempts in seconds.")]
    error_message: Annotated[
        str | None, Field(default=None, description="Failure diagnostic message if unsuccessful.")
    ] = None
    git_committed: Annotated[bool, Field(default=False, description="Whether atomic git commit was executed.")] = False
    tracker_marked: Annotated[bool, Field(default=False, description="Whether tracker markdown was updated.")] = False


class HardeningRunSummaryDTO(BaseModel):
    """Aggregate summary of an entire hardening pipeline execution run."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    total_targets: Annotated[int, Field(description="Total number of targets queued.")]
    processed_count: Annotated[int, Field(description="Number of targets processed.")]
    success_count: Annotated[int, Field(description="Number of targets successfully hardened.")]
    failure_count: Annotated[int, Field(description="Number of targets failed.")]
    skipped_count: Annotated[int, Field(description="Number of targets skipped.")]
    iterations: Annotated[
        list[HardeningIterationResultDTO] | None,
        Field(default=None, description="Per-target iteration records."),
    ] = None


class QualityGateResultDTO(BaseModel):
    """Structured result of an audit loop execution pass."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    success: Annotated[bool, Field(description="Whether audit loop succeeded with exit code 0.")]
    output: Annotated[str, Field(description="Combined stdout and stderr from the audit loop.")]
    exit_code: Annotated[int, Field(description="Process exit code.")]


class CheckpointResultDTO(BaseModel):
    """Outcome of in-place checkpointing across tracker, state file, and git."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tracker_marked: Annotated[bool, Field(description="Whether the tracker markdown was updated.")]
    state_file_updated: Annotated[bool, Field(description="Whether the JSON state file was updated.")]
    git_committed: Annotated[bool, Field(description="Whether git commit succeeded.")]


class WorkspaceSnapshotDTO(BaseModel):
    """Snapshot of tracked and untracked modifications for deterministic rollback diffs."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    modified_files: Annotated[list[str], Field(default_factory=list, description="Tracked files with modifications.")]
    untracked_files: Annotated[list[str], Field(default_factory=list, description="Untracked newly created files.")]


class HardeningStateFileDTO(BaseModel):
    """Two-key JSON schema governing hardening_state.json per deterministic hardening architecture."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    targets: Annotated[
        list[str],
        Field(
            default_factory=list,
            validation_alias=AliasChoices("TARGETS", "targets"),
            serialization_alias="TARGETS",
            description="Canonical list of target paths.",
        ),
    ]
    done: Annotated[
        list[str],
        Field(
            default_factory=list,
            validation_alias=AliasChoices("DONE", "done"),
            serialization_alias="DONE",
            description="Canonical list of completed target paths.",
        ),
    ]


def clean_path_arg(val: str | Path | None) -> Path | None:
    """Normalize and strip markdown link wrappers, quotes, and whitespace from a path argument.

    Args:
        val: Raw path string or Path instance, potentially wrapped in @[...] or quotes.

    Returns:
        Cleaned Path instance, or None if val is None.
    """
    if val is None:
        return None
    raw_str = str(val).strip().strip("`").strip("'").strip('"')
    if raw_str.startswith("@"):
        raw_str = raw_str[1:]
    raw_str = raw_str.strip().strip("[").strip("]").strip()
    if not raw_str:
        return None
    return Path(raw_str)


def parse_tracker_unhardened_targets(tracker_content: str, gate: HardeningGate) -> list[str]:
    """Parse unchecked checklist target items from tracker markdown under the specified gate section.

    Args:
        tracker_content: Raw tracker markdown content.
        gate: Hardening gate (backend or frontend) to extract items for.

    Returns:
        List of unhardened target relative paths.
    """
    # Parses unchecked target items under the corresponding Tier 2 Hardening section.
    # Expected markdown structure:
    #   - [ ] Tier 2 Hardening (Backend)
    #     - [ ] [NEW] @[backend_v2/services/foo.py]
    #     - [ ] @[backend_v2/models/bar.py]
    gate_name = "Backend" if gate == HardeningGate.BACKEND else "Frontend"
    header_pattern = re.compile(
        rf"^-\s*\[[ xX]\]\s*.*\bTier\s+2\s+Hardening\s*\({gate_name}\)",
        re.MULTILINE | re.IGNORECASE,
    )
    match = header_pattern.search(tracker_content)
    if not match:
        return []

    lines = tracker_content[match.end() :].splitlines()
    unhardened: list[str] = []
    item_pattern = re.compile(
        r"^\s+-\s*\[ \]\s*(?:\[(?:NEW|MODIFY|DELETE)\]\s*)?@?\[?([a-zA-Z0-9_/\\.-]+)\]?",
    )

    for line in lines:
        if line.startswith("- [") or line.startswith("## ") or line.startswith("### "):
            break
        m = item_pattern.match(line)
        if m:
            raw_path = m.group(1).replace("\\", "/").strip()
            if raw_path and not raw_path.startswith("["):
                unhardened.append(raw_path)

    return unhardened


def mark_tracker_target_done(tracker_path: Path, target_file: str) -> bool:
    """Mark a target checklist item as checked in the tracker markdown in-place.

    Also updates parent gate section checkbox if all child items are verified.

    Args:
        tracker_path: Path to tracker markdown file.
        target_file: Relative path of the target file to mark done.

    Returns:
        True if target was found and updated, False otherwise.
    """
    if not tracker_path.exists():
        return False

    content = tracker_path.read_text(encoding="utf-8")
    norm_target = target_file.replace("\\", "/").strip()
    escaped_target = re.escape(norm_target)

    pattern = re.compile(
        rf"^(\s+-\s*)\[ \](\s*(?:\[(?:NEW|MODIFY|DELETE)\]\s*)?@?\[?{escaped_target}\]?.*)$",
        re.MULTILINE,
    )

    if not pattern.search(content):
        return False

    new_content = pattern.sub(r"\g<1>[x]\g<2>", content)

    for gate_name in ("Backend", "Frontend"):
        section_pattern = re.compile(
            rf"^(?P<parent>-\s*\[ \]\s*(?:\*\*\[NOK\]\s*)?Tier\s+2\s+Hardening\s*\({gate_name}\)[^\n]*)"
            r"(?P<children>(?:\n\s+-\s*\[[ xX]\].*)+)",
            re.MULTILINE,
        )
        sec_match = section_pattern.search(new_content)
        if sec_match:
            children = sec_match.group("children")
            if "- [ ]" not in children:
                parent_line = sec_match.group("parent")
                updated_parent = parent_line.replace("- [ ]", "- [x]").replace("[NOK]", "[OK]")
                new_content = new_content.replace(parent_line, updated_parent, 1)

    tracker_path.write_text(new_content, encoding="utf-8")
    return True


def fetch_unhardened_targets(args: HardeningRunnerArgsDTO) -> list[str]:
    """Resolve target list from explicit arguments, tracker markdown, or persistent state file.

    Args:
        args: Hardening runner configuration parameters.

    Returns:
        List of unhardened target file paths.

    Raises:
        FileNotFoundError: If tracker or state_file does not exist.
        ValueError: If no target source is specified.
    """
    # Target resolution hierarchy:
    # 1. Explicit CLI arguments: --targets path1 path2
    if args.targets:
        cleaned_targets: list[str] = []
        for t in args.targets:
            p = clean_path_arg(t)
            if p is not None:
                cleaned_targets.append(str(p).replace("\\", "/"))
        return cleaned_targets

    # 2. Markdown tracker checklist: --tracker path/to/tracker.md
    if args.tracker:
        cleaned_tracker = clean_path_arg(args.tracker)
        if cleaned_tracker is None or not cleaned_tracker.exists():
            raise FileNotFoundError(f"Tracker file not found: {args.tracker}")
        content = cleaned_tracker.read_text(encoding="utf-8")
        return parse_tracker_unhardened_targets(content, args.gate)

    # 3. Persistent sandbox state JSON: --state-file scratch/hardening_state.json
    #    Computes pending targets dynamically: REMAINING = TARGETS - DONE
    if args.state_file:
        cleaned_state = clean_path_arg(args.state_file)
        if cleaned_state is None or not cleaned_state.exists():
            raise FileNotFoundError(f"State file not found: {args.state_file}")
        content = cleaned_state.read_text(encoding="utf-8")
        state = HardeningStateFileDTO.model_validate_json(content)
        done_set = set(state.done)
        return [t for t in state.targets if t not in done_set]

    raise ValueError("No target source provided. Specify --targets, --tracker, or --state-file.")


def execute_subprocess_with_tree_kill(
    cmd: list[str],
    timeout_seconds: int,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Execute subprocess with deterministic Windows process tree termination on timeout.

    Args:
        cmd: Argument vector to execute.
        timeout_seconds: Maximum duration before process tree kill.
        cwd: Working directory for process execution.

    Returns:
        CompletedProcess containing stdout, stderr, and exit code.

    Raises:
        subprocess.TimeoutExpired: When execution exceeds timeout_seconds.
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        shell=False,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
        )
    except subprocess.TimeoutExpired as exc:
        if sys.platform == "win32":
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    timeout=TASKKILL_TIMEOUT_SECONDS,
                    check=False,
                    shell=False,
                )
            except subprocess.SubprocessError, OSError:
                pass
        proc.kill()
        try:
            stdout, stderr = proc.communicate(timeout=TASKKILL_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired, subprocess.SubprocessError, OSError:
            stdout, stderr = "", ""
        raise subprocess.TimeoutExpired(
            cmd,
            timeout=timeout_seconds,
            output=stdout,
            stderr=stderr,
        ) from exc


def execute_subagent_pass(target_file: str, args: HardeningRunnerArgsDTO, repo_root: Path | None = None) -> bool:
    """Execute optional subagent command or automated pre-audit code formatting passes.

    Args:
        target_file: Path of target file being hardened.
        args: Hardening runner configuration parameters.
        repo_root: Root workspace path.

    Returns:
        True if formatting/subagent pass succeeded or was skipped, False on error.
    """
    root = repo_root or get_repo_root()

    if args.agent_cmd:
        formatted_cmd = args.agent_cmd.format(target=target_file, target_file=target_file)
        cmd_args = shlex.split(formatted_cmd, posix=False if sys.platform == "win32" else True)
        try:
            res = execute_subprocess_with_tree_kill(cmd_args, timeout_seconds=args.timeout_seconds, cwd=root)
            if res.returncode != 0:
                return False
        except subprocess.TimeoutExpired:
            return False

    if not args.no_auto_fix:
        if args.gate == HardeningGate.BACKEND and target_file.endswith(".py"):
            subprocess.run(
                ["uv", "run", "ruff", "check", "--fix", target_file],
                cwd=root,
                capture_output=True,
                timeout=FORMATTER_TIMEOUT_SECONDS,
                check=False,
                shell=False,
            )
            subprocess.run(
                ["uv", "run", "ruff", "format", target_file],
                cwd=root,
                capture_output=True,
                timeout=FORMATTER_TIMEOUT_SECONDS,
                check=False,
                shell=False,
            )
        elif args.gate == HardeningGate.FRONTEND and target_file.endswith(".dart"):
            subprocess.run(
                ["dart", "format", target_file],
                cwd=root,
                capture_output=True,
                timeout=FORMATTER_TIMEOUT_SECONDS,
                check=False,
                shell=sys.platform == "win32",
            )

    return True


def run_quality_gate(
    target_file: str, gate: HardeningGate, timeout_seconds: int, repo_root: Path | None = None
) -> QualityGateResultDTO:
    """Execute backend or flutter universal quality gate audit loop for the target.

    Args:
        target_file: Path of target file.
        gate: Hardening gate (backend or frontend).
        timeout_seconds: Per-target audit timeout duration.
        repo_root: Workspace root directory.

    Returns:
        QualityGateResultDTO encapsulating execution status and log output.
    """
    root = repo_root or get_repo_root()

    # Dispatches the designated quality gate audit loop with strict AST guardrails:
    # - Backend: uv run python scripts/backend_audit_loop.py <target_file> --test --ast-strict
    # - Frontend: uv run python scripts/flutter_audit_loop.py <target_file> --build
    if gate == HardeningGate.BACKEND:
        cmd = ["uv", "run", "python", "scripts/backend_audit_loop.py", target_file, "--test", "--ast-strict"]
    else:
        cmd = ["uv", "run", "python", "scripts/flutter_audit_loop.py", target_file, "--build"]

    try:
        res = execute_subprocess_with_tree_kill(cmd, timeout_seconds=timeout_seconds, cwd=root)
        output = f"{res.stdout}\n{res.stderr}".strip()
        return QualityGateResultDTO(
            success=res.returncode == 0,
            output=output,
            exit_code=res.returncode,
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.output or "") if isinstance(exc.output, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        return QualityGateResultDTO(
            success=False,
            output=f"Audit loop timed out after {timeout_seconds}s.\n{out}\n{err}".strip(),
            exit_code=124,
        )


def capture_workspace_snapshot(repo_root: Path | None = None) -> WorkspaceSnapshotDTO:
    """Capture current modified and untracked files snapshot from git status porcelain.

    Args:
        repo_root: Workspace root directory.

    Returns:
        WorkspaceSnapshotDTO encapsulating lists of modified and untracked file paths.
    """
    root = repo_root or get_repo_root()
    res = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
        check=False,
        shell=False,
    )
    if res.returncode != 0:
        return WorkspaceSnapshotDTO(modified_files=[], untracked_files=[])

    modified: list[str] = []
    untracked: list[str] = []
    for line in res.stdout.splitlines():
        if not line or len(line) < 3:
            continue
        status_code = line[:2]
        filepath = line[3:].strip()
        if filepath.startswith('"') and filepath.endswith('"'):
            filepath = filepath[1:-1]
        norm_path = filepath.replace("\\", "/")
        if status_code == "??":
            untracked.append(norm_path)
        else:
            modified.append(norm_path)

    return WorkspaceSnapshotDTO(modified_files=modified, untracked_files=untracked)


def execute_circuit_breaker_rollback(
    snapshot: WorkspaceSnapshotDTO,
    target_file: str,
    repo_root: Path | None = None,
) -> None:
    """Roll back working directory modifications, strictly preserving db_v2.json and hardening_state.json.

    Args:
        snapshot: Pre-attempt baseline workspace snapshot.
        target_file: Target file relative path.
        repo_root: Workspace root directory.
    """
    root = repo_root or get_repo_root()
    current = capture_workspace_snapshot(root)
    norm_target = target_file.replace("\\", "/")

    excluded = {"data/db_v2.json", "hardening_state.json"}

    to_restore: list[str] = []
    for f in current.modified_files:
        norm_f = f.replace("\\", "/")
        if norm_f in excluded or norm_f.endswith("/hardening_state.json") or norm_f.endswith("/db_v2.json"):
            continue
        if norm_f == norm_target or norm_f not in snapshot.modified_files:
            to_restore.append(norm_f)

    if norm_target in current.modified_files and norm_target not in to_restore:
        to_restore.append(norm_target)

    for f in to_restore:
        subprocess.run(
            ["git", "restore", f],
            cwd=root,
            capture_output=True,
            timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )

    for u in current.untracked_files:
        norm_u = u.replace("\\", "/")
        if norm_u in excluded or norm_u.endswith("/hardening_state.json") or norm_u.endswith("/db_v2.json"):
            continue
        if norm_u not in snapshot.untracked_files:
            file_path = root / norm_u
            if file_path.is_file():
                try:
                    file_path.unlink()
                except OSError:
                    pass
            elif file_path.is_dir():
                try:
                    shutil.rmtree(file_path)
                except OSError:
                    pass


def mark_tracker_and_checkpoint(
    target_file: str,
    tracker_path: Path | None,
    state_file: Path | None,
    repo_root: Path | None = None,
) -> CheckpointResultDTO:
    """Update tracker markdown and state file, then execute atomic git commit for the verified target.

    Args:
        target_file: Target file relative path.
        tracker_path: Path to tracker markdown file.
        state_file: Path to hardening_state.json.
        repo_root: Workspace root directory.

    Returns:
        CheckpointResultDTO documenting actions completed.
    """
    root = repo_root or get_repo_root()
    tracker_marked = False
    cleaned_tracker = clean_path_arg(tracker_path)
    if cleaned_tracker and cleaned_tracker.exists():
        tracker_marked = mark_tracker_target_done(cleaned_tracker, target_file)

    state_file_updated = False
    cleaned_state = clean_path_arg(state_file)
    if cleaned_state and cleaned_state.exists():
        content = cleaned_state.read_text(encoding="utf-8")
        state = HardeningStateFileDTO.model_validate_json(content)
        norm_target = target_file.replace("\\", "/")
        if norm_target not in state.done:
            updated_state = state.model_copy(update={"done": [*state.done, norm_target]})
            cleaned_state.write_text(updated_state.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
            state_file_updated = True

    files_to_stage = [target_file]
    if tracker_marked and cleaned_tracker:
        files_to_stage.append(str(cleaned_tracker))

    subprocess.run(
        ["git", "add", *files_to_stage],
        cwd=root,
        capture_output=True,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
        check=False,
        shell=False,
    )

    base_name = Path(target_file).name
    commit_msg = f"refactor(hardening): tighten {base_name}"
    commit_res = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=root,
        capture_output=True,
        timeout=GIT_SUBPROCESS_TIMEOUT_SECONDS,
        check=False,
        shell=False,
    )
    git_committed = commit_res.returncode == 0

    return CheckpointResultDTO(
        tracker_marked=tracker_marked,
        state_file_updated=state_file_updated,
        git_committed=git_committed,
    )


def process_target_with_retries(
    target_file: str,
    args: HardeningRunnerArgsDTO,
    repo_root: Path | None = None,
) -> HardeningIterationResultDTO:
    """Orchestrate the retry loop, automated fixes, quality gate audits, and circuit breaker rollback for a target.

    Args:
        target_file: Target file relative path.
        args: Hardening runner configuration parameters.
        repo_root: Workspace root directory.

    Returns:
        HardeningIterationResultDTO summarizing target hardening execution.
    """
    root = repo_root or get_repo_root()
    start_time = time.monotonic()
    attempts = 0
    max_attempts = max(1, args.max_retries + 1)
    last_error: str | None = None

    for attempt in range(1, max_attempts + 1):
        attempts = attempt
        snapshot = capture_workspace_snapshot(root)

        execute_subagent_pass(target_file, args, repo_root=root)
        gate_res = run_quality_gate(target_file, args.gate, args.timeout_seconds, repo_root=root)

        if gate_res.success:
            checkpoint = mark_tracker_and_checkpoint(target_file, args.tracker, args.state_file, repo_root=root)
            duration = time.monotonic() - start_time
            return HardeningIterationResultDTO(
                target_file=target_file,
                gate=args.gate,
                success=True,
                attempts=attempts,
                duration_seconds=duration,
                error_message=None,
                git_committed=checkpoint.git_committed,
                tracker_marked=checkpoint.tracker_marked,
            )

        last_error = gate_res.output
        execute_circuit_breaker_rollback(snapshot, target_file, repo_root=root)

    duration = time.monotonic() - start_time
    return HardeningIterationResultDTO(
        target_file=target_file,
        gate=args.gate,
        success=False,
        attempts=attempts,
        duration_seconds=duration,
        error_message=last_error,
        git_committed=False,
        tracker_marked=False,
    )


def run_hardening_pipeline(args: HardeningRunnerArgsDTO, repo_root: Path | None = None) -> HardeningRunSummaryDTO:
    """Execute the complete hardening queue pipeline across discovered target files.

    Args:
        args: Hardening runner configuration parameters.
        repo_root: Workspace root directory.

    Returns:
        HardeningRunSummaryDTO summarizing all target iterations.
    """
    root = repo_root or get_repo_root()
    all_targets = fetch_unhardened_targets(args)
    total_targets = len(all_targets)

    if args.max_files is not None and args.max_files >= 0:
        targets_to_run = all_targets[: args.max_files]
    else:
        targets_to_run = all_targets

    processed_count = len(targets_to_run)
    skipped_count = total_targets - processed_count

    if args.dry_run:
        print(f"\n{ANSIColors.CYAN}--- DRY RUN: Target Hardening Queue ({processed_count} files) ---{ANSIColors.RESET}")
        for idx, target in enumerate(targets_to_run, 1):
            gate_cmd = (
                f"uv run python scripts/backend_audit_loop.py {target} --test --ast-strict"
                if args.gate == HardeningGate.BACKEND
                else f"uv run python scripts/flutter_audit_loop.py {target} --build"
            )
            print(f"  [{idx}/{processed_count}] {target} -> Planned: {gate_cmd}")
        return HardeningRunSummaryDTO(
            total_targets=total_targets,
            processed_count=processed_count,
            success_count=0,
            failure_count=0,
            skipped_count=skipped_count,
            iterations=[],
        )

    iterations: list[HardeningIterationResultDTO] = []
    success_count = 0
    failure_count = 0

    print(f"\n{ANSIColors.BOLD}Starting Autonomous Hardening Queue: {processed_count} targets{ANSIColors.RESET}")

    for idx, target in enumerate(targets_to_run, 1):
        print(f"\n{ANSIColors.CYAN}[{idx}/{processed_count}] Target: {target} ({args.gate.value}){ANSIColors.RESET}")
        iter_res = process_target_with_retries(target, args, repo_root=root)
        iterations.append(iter_res)

        if iter_res.success:
            success_count += 1
            dur = iter_res.duration_seconds
            print(f"  {ANSIColors.GREEN}✅ SUCCESS: {target} (att: {iter_res.attempts}, {dur:.1f}s){ANSIColors.RESET}")
        else:
            failure_count += 1
            dur = iter_res.duration_seconds
            print(f"  {ANSIColors.RED}❌ FAILED: {target} (att: {iter_res.attempts}, {dur:.1f}s){ANSIColors.RESET}")
            if iter_res.error_message and args.verbose:
                print(f"     Error summary: {iter_res.error_message[:400]}")

            if args.fail_fast and not args.continue_on_failure:
                print(f"{ANSIColors.YELLOW}⚡ Circuit breaker tripped (fail-fast). Halting queue.{ANSIColors.RESET}")
                break

    return HardeningRunSummaryDTO(
        total_targets=total_targets,
        processed_count=len(iterations),
        success_count=success_count,
        failure_count=failure_count,
        skipped_count=total_targets - len(iterations),
        iterations=iterations,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the autonomous hardening runner.

    Args:
        argv: Command-line arguments vector, or None for sys.argv.

    Returns:
        Process exit code: 0 on success/clean completion, 1 on failure.
    """
    setup_script_environment()
    parser = argparse.ArgumentParser(
        prog="auto_hardening_runner.py",
        description="Autonomous Multi-Process CLI Hardening Runner (Overnight Pipeline).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Autonomous AI Subagent Execution Examples:
------------------------------------------
1. Unattended hardening from an implementation tracker:
   uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --gate backend

2. Resume hardening from a saved sandbox state file:
   uv run python scripts/auto_hardening_runner.py --state-file scratch/hardening_state.json --gate backend

3. Direct targeted hardening on explicit file paths:
   uv run python scripts/auto_hardening_runner.py --targets backend_v2/services/foo.py backend_v2/models/bar.py

4. Dry-run inspection (preview target queue and planned audit commands without mutations):
   uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --dry-run

5. AI subagent-driven automated fixing per file:
   uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --agent-cmd "agy --dangerously-skip-permissions -i '/tier2-hardening-backend @[{target}]'"

Key Behavioral Invariants for Autonomous AI Agents:
- State Synchronization: Supports `hardening_state.json` (TARGETS vs DONE). Safe to interrupt and resume.
- Circuit Breaker: Automatically snapshots git status before each file attempt and rolls back modifications
  via git checkout/clean if the audit fails, protecting the repository against partial corruptions.
- Checkpointing: Marks target items `- [x]` in tracker markdown and commits atomically after each success.
""",
    )
    parser.add_argument("--tracker", type=Path, default=None, help="Path to tracker markdown file.")
    parser.add_argument("--state-file", type=Path, default=None, help="Path to hardening_state.json.")
    parser.add_argument(
        "--gate",
        type=str,
        choices=["backend", "frontend"],
        default="backend",
        help="Hardening gate category (backend or frontend).",
    )
    parser.add_argument("--targets", nargs="+", default=[], help="Explicit list of target file paths.")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum number of files to process.")
    parser.add_argument("--max-retries", type=int, default=2, help="Maximum retries per file on audit failure.")
    parser.add_argument(
        "--timeout",
        dest="timeout_seconds",
        type=int,
        default=DEFAULT_AUDIT_TIMEOUT_SECONDS,
        help="Per-file audit timeout in seconds.",
    )
    parser.add_argument("--agent-cmd", type=str, default=None, help="Subagent command template e.g. 'echo {target}'.")
    parser.add_argument("--no-auto-fix", action="store_true", help="Disable automatic ruff/dart format passes.")
    parser.add_argument(
        "--fail-fast", action="store_true", default=True, help="Halt execution on first failure (default: True)."
    )
    parser.add_argument(
        "--continue-on-failure", action="store_true", default=False, help="Continue to next target on failure."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned target queue without mutations.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose diagnostics.")

    parsed = parser.parse_args(argv)

    tracker_arg = clean_path_arg(parsed.tracker)
    state_file_arg = clean_path_arg(parsed.state_file)
    clean_targets = [str(clean_path_arg(t)).replace("\\", "/") for t in parsed.targets if clean_path_arg(t) is not None]

    if not (tracker_arg or clean_targets or state_file_arg):
        sys.stderr.write(
            f"{ANSIColors.RED}❌ Error: No target sources specified. "
            f"Provide at least one of --tracker, --targets, or --state-file.{ANSIColors.RESET}\n"
        )
        return 1

    if tracker_arg and not tracker_arg.exists():
        sys.stderr.write(f"{ANSIColors.RED}❌ Error: Tracker file not found: {tracker_arg}{ANSIColors.RESET}\n")
        return 1

    if state_file_arg and not state_file_arg.exists():
        sys.stderr.write(f"{ANSIColors.RED}❌ Error: State file not found: {state_file_arg}{ANSIColors.RESET}\n")
        return 1

    try:
        dto = HardeningRunnerArgsDTO(
            tracker=tracker_arg,
            state_file=state_file_arg,
            gate=HardeningGate(parsed.gate),
            targets=clean_targets or None,
            max_files=parsed.max_files,
            max_retries=parsed.max_retries,
            timeout_seconds=parsed.timeout_seconds,
            agent_cmd=parsed.agent_cmd,
            no_auto_fix=parsed.no_auto_fix,
            fail_fast=parsed.fail_fast,
            continue_on_failure=parsed.continue_on_failure,
            dry_run=parsed.dry_run,
            verbose=parsed.verbose,
        )
    except (ValidationError, ValueError) as err:
        sys.stderr.write(f"{ANSIColors.RED}❌ Argument Validation Error: {err}{ANSIColors.RESET}\n")
        return 1

    summary = run_hardening_pipeline(dto)

    if summary.failure_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
