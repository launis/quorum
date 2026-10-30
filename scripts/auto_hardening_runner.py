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
4. Mandatory AI Subagent Hardening & Auto-Fix Pass:
   - Executes an isolated AI subagent pass (`DEFAULT_BACKEND_AGENT_TEMPLATE` / `/tier2-hardening-backend`
     for `.py` or `DEFAULT_FRONTEND_AGENT_TEMPLATE` / `/tier2-hardening-frontend` for `.dart`, or a custom
     `--agent-cmd` template) by default across ALL gates (`backend`, `frontend`, `all`) to audit ~180 rules
     and 7 KI invariants, followed by automated formatting (`ruff format` / `dart format`).
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
# 1. Standard unattended AI-driven hardening from an implementation tracker:
uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"

# 2. Resume hardening from a saved sandbox state file:
uv run python scripts/auto_hardening_runner.py --state-file scratch/hardening_state.json --gate backend

# 3. Targeted hardening for specific explicit files:
uv run python scripts/auto_hardening_runner.py --targets backend_v2/services/foo.py backend_v2/models/bar.py

# 4. Dry-run inspection to preview discovered targets without executing audits or mutations:
uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --dry-run

# 5. Frontend AI-driven autonomous hardening with subagent execution per file:
uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"
"""

from __future__ import annotations

import argparse
import hashlib
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
DEFAULT_AUDIT_TIMEOUT_SECONDS: Final[int] = 1800
DEFAULT_SUBAGENT_MAX_RETRIES: Final[int] = 3
DEFAULT_SUBAGENT_RETRY_BACKOFF_SECONDS: Final[float] = 3.0
# Step 2: Parameterize default subagent templates with {model}
DEFAULT_BACKEND_AGENT_TEMPLATE: Final[str] = (
    'agy --model {model} --dangerously-skip-permissions --print "/tier2-hardening-backend @[{target}]"'
)
DEFAULT_FRONTEND_AGENT_TEMPLATE: Final[str] = (
    'agy --model {model} --dangerously-skip-permissions --print "/tier2-hardening-frontend @[{target}]"'
)
# Phase 2, Step 4: Content-addressed SHA-256 hardening cache path and historical completed trackers
DEFAULT_HARDENING_CACHE_PATH: Final[Path] = Path("data/hardening_cache.json")
HISTORICAL_COMPLETED_TRACKERS: Final[tuple[str, ...]] = (
    "docs/implementationplans/TRACKER_Backend_Targeted_Hardening.md",
    "docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave2.md",
    "docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave3.md",
    "docs/implementationplans/TRACKER_Backend_Targeted_Hardening_Wave4.md",
    "docs/implementationplans/TRACKER_Prefixed_UUIDv7_Cutover.md",
    "docs/implementationplans/TRACKER_Universal_UUIDv4_Eradication_and_32Hex_UUIDv7_Enforcement.md",
)

__all__ = [
    "CheckpointResultDTO",
    "DEFAULT_AUDIT_TIMEOUT_SECONDS",
    "DEFAULT_BACKEND_AGENT_TEMPLATE",
    "DEFAULT_FRONTEND_AGENT_TEMPLATE",
    "DEFAULT_HARDENING_CACHE_PATH",
    "DEFAULT_SUBAGENT_MAX_RETRIES",
    "DEFAULT_SUBAGENT_RETRY_BACKOFF_SECONDS",
    "FORMATTER_TIMEOUT_SECONDS",
    "GIT_SUBPROCESS_TIMEOUT_SECONDS",
    "HISTORICAL_COMPLETED_TRACKERS",
    "HardeningCacheEntryDTO",
    "HardeningCacheManifestDTO",
    "HardeningGate",
    "HardeningIterationResultDTO",
    "HardeningRunSummaryDTO",
    "HardeningRunnerArgsDTO",
    "HardeningStateFileDTO",
    "QualityGateResultDTO",
    "TASKKILL_TIMEOUT_SECONDS",
    "WorkspaceSnapshotDTO",
    "capture_workspace_snapshot",
    "check_tracker_has_unparsed_hardening_items",
    "clean_path_arg",
    "compute_file_sha256",
    "compute_rules_sha256",
    "compute_target_cache_entry",
    "execute_circuit_breaker_rollback",
    "execute_subagent_pass",
    "execute_subprocess_with_tree_kill",
    "fetch_unhardened_targets",
    "load_or_seed_hardening_cache",
    "main",
    "mark_tracker_and_checkpoint",
    "mark_tracker_target_done",
    "parse_tracker_hardened_targets",
    "parse_tracker_unhardened_targets",
    "process_target_with_retries",
    "resolve_target_unit_test_files",
    "run_hardening_pipeline",
    "run_macro_quality_gate",
    "run_quality_gate",
    "save_hardening_cache",
    "unquote_git_path",
]


class HardeningGate(StrEnum):
    """Hardening gate category corresponding to tracker sections and audit runners."""

    BACKEND = "backend"
    FRONTEND = "frontend"
    ALL = "all"


class HardeningCacheEntryDTO(BaseModel):
    """Immutable SHA-256 content-addressed cache record for a verified target file."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_file: Annotated[str, Field(description="Normalized POSIX relative path of the hardened target.")]
    target_sha256: Annotated[
        str, Field(pattern=r"^[a-f0-9]{64}$", description="SHA-256 hex digest of target file content.")
    ]
    unit_test_sha256: Annotated[
        str, Field(pattern=r"^[a-f0-9]{64}$", description="Composite SHA-256 hex digest of resolved unit test file(s).")
    ]
    rules_sha256: Annotated[
        str, Field(pattern=r"^[a-f0-9]{64}$", description="Composite SHA-256 hex digest of .agents/rules/ files.")
    ]
    composite_sha256: Annotated[
        str,
        Field(pattern=r"^[a-f0-9]{64}$", description="Combined SHA-256 hex digest of target, unit tests, and rules."),
    ]
    source_tracker: Annotated[
        str | None, Field(default=None, description="Tracker markdown path where target was hardened.")
    ] = None


class HardeningCacheManifestDTO(BaseModel):
    """Persistent manifest of SHA-256 content-addressed hardening cache entries."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    entries: Annotated[
        dict[str, HardeningCacheEntryDTO],
        Field(default_factory=dict, description="Map of target relative path to cache entry."),
    ]


class HardeningRunnerArgsDTO(BaseModel):
    """Strict configuration parameters for the hardening runner pipeline."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tracker: Annotated[Path | None, Field(default=None, description="Path to tracker markdown file.")] = None
    state_file: Annotated[Path | None, Field(default=None, description="Path to hardening_state.json.")] = None
    gate: Annotated[HardeningGate, Field(default=HardeningGate.ALL, description="Hardening gate category.")] = (
        HardeningGate.ALL
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
    no_agent: Annotated[
        bool, Field(default=False, description="Disable automatic AI subagent execution before audit.")
    ] = False
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
    # Step 2: Add model selection and micro_audit configuration to HardeningRunnerArgsDTO
    model: Annotated[
        str,
        Field(default="gemini-4-argon-medium", description="AI model identifier for subagent hardening iterations."),
    ] = "gemini-4-argon-medium"
    micro_audit: Annotated[
        bool,
        Field(
            default=True,
            description="Use fast micro-audit during per-target iterations and run macro-audit at completion.",
        ),
    ] = True
    # Phase 2, Step 4: Add SHA-256 hardening cache configuration fields
    no_cache: Annotated[
        bool,
        Field(default=False, description="Bypass SHA-256 hardening cache and force execution."),
    ] = False
    cache_file: Annotated[
        Path,
        Field(default=DEFAULT_HARDENING_CACHE_PATH, description="Path to SHA-256 hardening cache JSON."),
    ] = DEFAULT_HARDENING_CACHE_PATH


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
    cache_hit: Annotated[
        bool, Field(default=False, description="Whether target was satisfied via 0s SHA-256 cache hit.")
    ] = False


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
    if "#" in raw_str:
        raw_str = raw_str.split("#")[0].strip()
    raw_str = raw_str.strip().strip("`").strip("'").strip('"')
    if not raw_str:
        return None
    return Path(raw_str)


def unquote_git_path(raw_path: str) -> str:
    """Decode and strip C-quoted octal escape sequences from a git status --porcelain path.

    Args:
        raw_path: Raw path entry extracted from git status --porcelain output.

    Returns:
        Unquoted UTF-8 path string with forward slashes.
    """
    cleaned = raw_path.strip()
    if " -> " in cleaned:
        cleaned = cleaned.split(" -> ", 1)[1].strip()
    if len(cleaned) >= 2 and cleaned.startswith('"') and cleaned.endswith('"'):
        inner = cleaned[1:-1]
        byte_buf = bytearray()
        idx = 0
        n = len(inner)
        escape_map = {"n": ord("\n"), "t": ord("\t"), "r": ord("\r"), '"': ord('"'), "\\": ord("\\")}
        while idx < n:
            ch = inner[idx]
            if ch == "\\" and idx + 1 < n:
                nxt = inner[idx + 1]
                if idx + 3 < n and all(c in "01234567" for c in inner[idx + 1 : idx + 4]):
                    byte_buf.append(int(inner[idx + 1 : idx + 4], 8))
                    idx += 4
                    continue
                if nxt in escape_map:
                    byte_buf.append(escape_map[nxt])
                    idx += 2
                    continue
            byte_buf.extend(ch.encode("utf-8"))
            idx += 1
        cleaned = byte_buf.decode("utf-8", errors="replace")
    return cleaned.replace("\\", "/")


def _has_invalid_git_path_chars(path_str: str) -> bool:
    """Check whether a decoded git path contains control or Private Use Area characters.

    Args:
        path_str: Unquoted git path string.

    Returns:
        True if the path contains invalid control characters or Unicode Private Use Area codepoints.
    """
    return any(ord(c) < 32 or (0xE000 <= ord(c) <= 0xF8FF) for c in path_str)


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
    if gate == HardeningGate.ALL:
        backend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.BACKEND)
        frontend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.FRONTEND)
        return backend_targets + frontend_targets

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
    # Step 3: Make Tracker Target Parsing Resilient to Backticks and Quoting
    item_pattern = re.compile(
        r"^\s+-\s*\[ \]\s*(?:`?\[(?:NEW|MODIFY|DELETE)\]\s*`?)?"
        r"`?(?:@\[?([a-zA-Z0-9_/\\.-]+?)(?:#[^`\]\n]+)?\]|"
        r"([a-zA-Z0-9_.-]+(?:[/\\][a-zA-Z0-9_.-]+)*\.[a-zA-Z0-9]+(?:#[^`\]\n]+)?))`?",
    )

    for line in lines:
        if line.startswith("- [") or line.startswith("## ") or line.startswith("### "):
            break
        if "[DELETE]" in line:
            continue
        m = item_pattern.match(line)
        if m:
            raw_path = (m.group(1) or m.group(2) or "").replace("\\", "/").strip()
            clean_path = raw_path.split("#")[0].strip()
            if clean_path and not clean_path.startswith("["):
                if gate == HardeningGate.BACKEND and not clean_path.endswith(".py"):
                    continue
                if gate == HardeningGate.FRONTEND and not clean_path.endswith(".dart"):
                    continue
                unhardened.append(clean_path)

    return unhardened


def parse_tracker_hardened_targets(tracker_content: str, gate: HardeningGate) -> list[str]:
    """Extract checked (`- [x]`) target items from tracker markdown under the specified gate section.

    Args:
        tracker_content: Raw tracker markdown content.
        gate: Hardening gate (backend, frontend, or all) to extract completed items for.

    Returns:
        List of checked target relative paths.
    """
    # Phase 2, Step 4: Parse checked - [x] targets under Tier 2 Hardening (Backend / Frontend)
    if gate == HardeningGate.ALL:
        backend_targets = parse_tracker_hardened_targets(tracker_content, HardeningGate.BACKEND)
        frontend_targets = parse_tracker_hardened_targets(tracker_content, HardeningGate.FRONTEND)
        return backend_targets + frontend_targets

    gate_name = "Backend" if gate == HardeningGate.BACKEND else "Frontend"
    header_pattern = re.compile(
        rf"^-\s*\[[ xX]\]\s*.*\bTier\s+2\s+Hardening\s*\({gate_name}\)",
        re.MULTILINE | re.IGNORECASE,
    )
    match = header_pattern.search(tracker_content)
    if not match:
        return []

    lines = tracker_content[match.end() :].splitlines()
    hardened: list[str] = []
    item_pattern = re.compile(
        r"^\s+-\s*\[[xX]\]\s*(?:`?\[(?:NEW|MODIFY|DELETE)\]\s*`?)?"
        r"`?(?:@\[?([a-zA-Z0-9_/\\.-]+?)(?:#[^`\]\n]+)?\]|"
        r"([a-zA-Z0-9_.-]+(?:[/\\][a-zA-Z0-9_.-]+)*\.[a-zA-Z0-9]+(?:#[^`\]\n]+)?))`?",
    )

    for line in lines:
        if line.startswith("- [") or line.startswith("## ") or line.startswith("### "):
            break
        if "[DELETE]" in line:
            continue
        m = item_pattern.match(line)
        if m:
            raw_path = (m.group(1) or m.group(2) or "").replace("\\", "/").strip()
            clean_path = raw_path.split("#")[0].strip()
            if clean_path and not clean_path.startswith("["):
                if gate == HardeningGate.BACKEND and not clean_path.endswith(".py"):
                    continue
                if gate == HardeningGate.FRONTEND and not clean_path.endswith(".dart"):
                    continue
                hardened.append(clean_path)

    return hardened


def compute_file_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hexadecimal digest of a file on disk.

    Args:
        file_path: Path to the file to hash.

    Returns:
        Lowercase 64-character hexadecimal SHA-256 digest string.
    """
    # Phase 2, Step 4: Compute deterministic SHA-256 hex digest of file bytes
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def resolve_target_unit_test_files(target_file: str, repo_root: Path) -> list[Path]:
    """Resolve existing unit test files corresponding to a backend, script, or frontend target.

    Args:
        target_file: Relative path of the target file.
        repo_root: Workspace root directory.

    Returns:
        Sorted list of existing unit test Paths corresponding to target_file.
    """
    # Phase 2, Step 4: Resolve unit test files for composite SHA-256 cache invalidation
    norm_target = target_file.replace("\\", "/").strip()
    candidates: set[Path] = set()

    if norm_target.startswith("backend_v2/tests/"):
        direct = repo_root / norm_target
        if direct.is_file():
            candidates.add(direct)
    elif norm_target.startswith("backend_v2/") and norm_target.endswith(".py"):
        rel = Path(norm_target).relative_to("backend_v2")
        unit_root = repo_root / "backend_v2" / "tests" / "unit"
        direct_candidate = unit_root / rel.parent / f"test_{rel.name}"
        if direct_candidate.is_file():
            candidates.add(direct_candidate)
        if rel.name == "__init__.py":
            for suffix in ("facade", "init"):
                pkg_candidate = unit_root / rel.parent / f"test_{rel.parent.name}_{suffix}.py"
                if pkg_candidate.is_file():
                    candidates.add(pkg_candidate)
    elif norm_target.startswith("scripts/") and norm_target.endswith(".py"):
        script_name = Path(norm_target).name
        if script_name.startswith("_"):
            script_test = repo_root / "backend_v2" / "tests" / "unit" / "scripts" / f"test{script_name}"
        else:
            script_test = repo_root / "backend_v2" / "tests" / "unit" / "scripts" / f"test_{script_name}"
        if script_test.is_file():
            candidates.add(script_test)
    elif norm_target.startswith("client_app_v2/lib/") and norm_target.endswith(".dart"):
        rel = Path(norm_target).relative_to("client_app_v2/lib")
        for prefix in (repo_root / "client_app_v2" / "test" / "unit", repo_root / "client_app_v2" / "test"):
            dart_test = prefix / rel.parent / f"{rel.stem}_test.dart"
            if dart_test.is_file():
                candidates.add(dart_test)

    return sorted(candidates, key=lambda p: p.as_posix())


def compute_rules_sha256(repo_root: Path) -> str:
    """Compute a composite SHA-256 hexadecimal digest across all `.agents/rules/*.md` files.

    Args:
        repo_root: Workspace root directory.

    Returns:
        Lowercase 64-character hexadecimal SHA-256 digest of all rule files.
    """
    # Phase 2, Step 4: Include .agents/rules/*.md in composite SHA-256 to invalidate cache on rule changes
    hasher = hashlib.sha256()
    rules_dir = repo_root / ".agents" / "rules"
    if rules_dir.is_dir():
        for rule_file in sorted(rules_dir.glob("*.md"), key=lambda p: p.name):
            if rule_file.is_file():
                file_digest = compute_file_sha256(rule_file)
                hasher.update(f"{rule_file.name}:{file_digest}\n".encode())
    return hasher.hexdigest()


def compute_target_cache_entry(
    target_file: str,
    repo_root: Path,
    rules_sha256: str | None = None,
    source_tracker: str | None = None,
) -> HardeningCacheEntryDTO | None:
    """Compute the SHA-256 cache entry for a target file if it exists on disk.

    Args:
        target_file: Relative path of the target file.
        repo_root: Workspace root directory.
        rules_sha256: Precomputed SHA-256 digest of `.agents/rules/*.md`, or None to compute on demand.
        source_tracker: Optional tracker path where the target was verified.

    Returns:
        Populated HardeningCacheEntryDTO if target_file exists on disk, or None if missing.
    """
    # Phase 2, Step 4: Build composite SHA-256 cache entry over (target + unit_tests + rules)
    norm_target = target_file.replace("\\", "/").strip()
    target_path = repo_root / norm_target
    if not target_path.is_file():
        return None

    target_digest = compute_file_sha256(target_path)
    test_files = resolve_target_unit_test_files(norm_target, repo_root)
    unit_hasher = hashlib.sha256()
    for tf in test_files:
        rel_tf = tf.relative_to(repo_root).as_posix()
        unit_hasher.update(f"{rel_tf}:{compute_file_sha256(tf)}\n".encode())
    unit_test_digest = unit_hasher.hexdigest()

    resolved_rules_digest = rules_sha256 if rules_sha256 is not None else compute_rules_sha256(repo_root)

    comp_hasher = hashlib.sha256()
    comp_hasher.update(f"target:{norm_target}:{target_digest}\n".encode())
    comp_hasher.update(f"tests:{unit_test_digest}\n".encode())
    comp_hasher.update(f"rules:{resolved_rules_digest}\n".encode())
    composite_digest = comp_hasher.hexdigest()

    return HardeningCacheEntryDTO(
        target_file=norm_target,
        target_sha256=target_digest,
        unit_test_sha256=unit_test_digest,
        rules_sha256=resolved_rules_digest,
        composite_sha256=composite_digest,
        source_tracker=source_tracker,
    )


def save_hardening_cache(
    cache_path: Path,
    manifest: HardeningCacheManifestDTO,
    repo_root: Path,
) -> None:
    """Persist the HardeningCacheManifestDTO to disk as formatted JSON.

    Args:
        cache_path: Relative or absolute path to the hardening cache JSON file.
        manifest: Validated HardeningCacheManifestDTO to write.
        repo_root: Workspace root directory.
    """
    # Phase 2, Step 4: Persist strongly typed SHA-256 hardening cache manifest
    resolved_path = cache_path if cache_path.is_absolute() else (repo_root / cache_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def load_or_seed_hardening_cache(
    cache_path: Path,
    repo_root: Path,
) -> HardeningCacheManifestDTO:
    """Load the SHA-256 hardening cache manifest and seed missing `- [x]` targets from completed trackers.

    Args:
        cache_path: Relative or absolute path to the hardening cache JSON file.
        repo_root: Workspace root directory.

    Returns:
        Validated HardeningCacheManifestDTO containing existing and newly seeded entries.
    """
    # Phase 2, Step 4: Load hardening_cache.json and automatically seed completed Wave 1-4 and UUIDv7 trackers
    resolved_path = cache_path if cache_path.is_absolute() else (repo_root / cache_path)
    entries: dict[str, HardeningCacheEntryDTO] = {}
    if resolved_path.is_file():
        try:
            loaded = HardeningCacheManifestDTO.model_validate_json(resolved_path.read_text(encoding="utf-8"))
            entries = dict(loaded.entries)
        except ValidationError, ValueError, OSError:
            entries = {}

    rules_digest = compute_rules_sha256(repo_root)
    tracker_rel_paths: list[str] = list(HISTORICAL_COMPLETED_TRACKERS)
    impl_dir = repo_root / "docs" / "implementationplans"
    if impl_dir.is_dir():
        for p in sorted(impl_dir.glob("TRACKER_*.md")):
            rel_p = p.relative_to(repo_root).as_posix()
            if rel_p not in tracker_rel_paths:
                tracker_rel_paths.append(rel_p)
    epic_dir = repo_root / "docs" / "epic"
    if epic_dir.is_dir():
        for p in sorted(epic_dir.glob("*_tracker.md")):
            rel_p = p.relative_to(repo_root).as_posix()
            if rel_p not in tracker_rel_paths:
                tracker_rel_paths.append(rel_p)

    # Collect any target currently marked unchecked `- [ ]` in any tracker so in-progress files are not auto-seeded
    unchecked_targets: set[str] = set()
    for rel_tracker in tracker_rel_paths:
        t_path = repo_root / rel_tracker
        if t_path.is_file():
            try:
                t_content = t_path.read_text(encoding="utf-8")
                for ut in parse_tracker_unhardened_targets(t_content, HardeningGate.ALL):
                    unchecked_targets.add(ut)
            except OSError:
                continue

    seeded_new = False
    for rel_tracker in tracker_rel_paths:
        t_path = repo_root / rel_tracker
        if not t_path.is_file():
            continue
        try:
            t_content = t_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for hardened_target in parse_tracker_hardened_targets(t_content, HardeningGate.ALL):
            if hardened_target in entries or hardened_target in unchecked_targets:
                continue
            entry = compute_target_cache_entry(
                hardened_target,
                repo_root,
                rules_sha256=rules_digest,
                source_tracker=rel_tracker,
            )
            if entry is not None:
                entries[hardened_target] = entry
                seeded_new = True

    manifest = HardeningCacheManifestDTO(entries=entries)
    if seeded_new:
        save_hardening_cache(cache_path, manifest, repo_root)
    return manifest


def check_tracker_has_unparsed_hardening_items(tracker_content: str, gate: HardeningGate) -> bool:
    """Check whether a hardening gate section is unchecked and contains child items that failed to parse.

    Args:
        tracker_content: Raw tracker markdown content.
        gate: Hardening gate (backend, frontend, or all) to inspect.

    Returns:
        True if the gate is unchecked and has pending child checklist lines, False otherwise.
    """
    if gate == HardeningGate.ALL:
        return check_tracker_has_unparsed_hardening_items(
            tracker_content, HardeningGate.BACKEND
        ) or check_tracker_has_unparsed_hardening_items(tracker_content, HardeningGate.FRONTEND)

    gate_name = "Backend" if gate == HardeningGate.BACKEND else "Frontend"
    header_pattern = re.compile(
        rf"^-\s*\[ \]\s*.*\bTier\s+2\s+Hardening\s*\({gate_name}\)",
        re.MULTILINE | re.IGNORECASE,
    )
    match = header_pattern.search(tracker_content)
    if not match:
        return False

    lines = tracker_content[match.end() :].splitlines()
    for line in lines:
        if line.startswith("- [") or line.startswith("## ") or line.startswith("### "):
            break
        if re.match(r"^\s+-\s*\[ \]", line) and "[DELETE]" not in line:
            return True
    return False


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

    # Step 3: Make mark_tracker_target_done Resilient to Backticks and Quoting
    pattern = re.compile(
        rf"^(\s+-\s*)\[ \](\s*(?:`?\[(?:NEW|MODIFY|DELETE)\]\s*`?)?`?@?\[?{escaped_target}(?:#[^`\]\n]+)?\]?`?.*)$",
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
            for sub_t in str(t).split(","):
                p = clean_path_arg(sub_t.strip())
                if p is not None:
                    cleaned_targets.append(str(p).replace("\\", "/"))
        return cleaned_targets

    # 2. Markdown tracker checklist: --tracker path/to/tracker.md
    if args.tracker:
        cleaned_tracker = clean_path_arg(args.tracker)
        if cleaned_tracker is None or not cleaned_tracker.exists():
            raise FileNotFoundError(f"Tracker file not found: {args.tracker}")
        content = cleaned_tracker.read_text(encoding="utf-8")
        targets = parse_tracker_unhardened_targets(content, args.gate)
        if not targets and check_tracker_has_unparsed_hardening_items(content, args.gate):
            gate_str = "Backend" if args.gate == HardeningGate.BACKEND else "Frontend"
            raise ValueError(
                f"Tracker {args.tracker} has pending Tier 2 Hardening ({gate_str}) checklist items, "
                f"but zero targets could be parsed into valid file paths."
            )
        return targets

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
        stdin=subprocess.DEVNULL,
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


def _is_transient_subagent_startup_error(returncode: int, output: str) -> bool:
    """Detect whether a subagent command failure was caused by a transient startup or network glitch.

    Args:
        returncode: Subprocess return code.
        output: Combined stdout and stderr output.

    Returns:
        True if the failure appears to be a transient startup or network error eligible for retry.
    """
    if returncode <= 0:
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
    output_lower = output.lower()
    for indicator in transient_indicators:
        if indicator.lower() in output_lower:
            return True

    # If the subagent process exited immediately with zero output, treat as startup crash
    if not output.strip():
        return True

    return False


def execute_subagent_pass(target_file: str, args: HardeningRunnerArgsDTO, repo_root: Path | None = None) -> bool:
    """Execute mandatory AI subagent hardening pass and automated pre-audit code formatting passes.

    Always invokes the AI subagent (`DEFAULT_BACKEND_AGENT_TEMPLATE` or `DEFAULT_FRONTEND_AGENT_TEMPLATE`
    when `args.agent_cmd` is omitted) across all gates (`backend`, `frontend`, `all`) unless `args.no_agent`
    is explicitly set. Retries transient subagent startup errors (such as remote model catalog fetch failures
    or network drops) up to DEFAULT_SUBAGENT_MAX_RETRIES attempts before failing.

    Args:
        target_file: Path of target file being hardened.
        args: Hardening runner configuration parameters.
        repo_root: Root workspace path.

    Returns:
        True if subagent and formatting passes succeeded or were explicitly skipped, False on error.
    """
    root = repo_root or get_repo_root()

    subagent_template = args.agent_cmd
    if not subagent_template and not args.no_agent:
        subagent_template = (
            DEFAULT_FRONTEND_AGENT_TEMPLATE if target_file.endswith(".dart") else DEFAULT_BACKEND_AGENT_TEMPLATE
        )

    if subagent_template and not args.no_agent:
        if target_file.endswith(".dart") and "/tier2-hardening-backend" in subagent_template:
            subagent_template = subagent_template.replace("/tier2-hardening-backend", "/tier2-hardening-frontend")

        # Step 2: Format subagent_template with model=args.model
        formatted_cmd = subagent_template.format(model=args.model, target=target_file, target_file=target_file)
        cmd_args = shlex.split(formatted_cmd, posix=False if sys.platform == "win32" else True)
        subagent_success = False

        for attempt in range(1, DEFAULT_SUBAGENT_MAX_RETRIES + 1):
            try:
                res = execute_subprocess_with_tree_kill(cmd_args, timeout_seconds=args.timeout_seconds, cwd=root)
                if res.returncode == 0:
                    subagent_success = True
                    break

                output = f"{res.stdout}\n{res.stderr}".strip()
                if _is_transient_subagent_startup_error(res.returncode, output):
                    if attempt < DEFAULT_SUBAGENT_MAX_RETRIES:
                        backoff = DEFAULT_SUBAGENT_RETRY_BACKOFF_SECONDS * attempt
                        print(
                            f"\n{ANSIColors.YELLOW}[RETRY] Transient subagent startup error on {target_file} "
                            f"(exit code {res.returncode}). Retrying attempt {attempt + 1}/{DEFAULT_SUBAGENT_MAX_RETRIES} in {backoff:.1f}s...{ANSIColors.RESET}\n",
                            flush=True,
                        )
                        time.sleep(backoff)
                        continue

                break
            except subprocess.TimeoutExpired:
                break

        if not subagent_success:
            return False

    if not args.no_auto_fix:
        if target_file.endswith(".py"):
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
        elif target_file.endswith(".dart"):
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
    target_file: str,
    gate: HardeningGate,
    timeout_seconds: int,
    repo_root: Path | None = None,
    *,
    micro_audit: bool = False,
) -> QualityGateResultDTO:
    """Execute backend or flutter universal quality gate audit loop for the target.

    Args:
        target_file: Path of target file.
        gate: Hardening gate (backend, frontend, or all).
        timeout_seconds: Per-target audit timeout duration.
        repo_root: Workspace root directory.
        micro_audit: When True on backend targets, executes fast single-file micro-audit mode.

    Returns:
        QualityGateResultDTO encapsulating execution status and log output.
    """
    root = repo_root or get_repo_root()

    # Step 2: Dispatch --micro --no-logfire during per-target iterations when micro_audit is True
    if gate == HardeningGate.BACKEND or (gate == HardeningGate.ALL and not target_file.endswith(".dart")):
        cmd = ["uv", "run", "python", "scripts/backend_audit_loop.py", target_file, "--test", "--ast-strict"]
        if micro_audit:
            cmd.extend(["--micro", "--no-logfire"])
    else:
        cmd = ["uv", "run", "python", "scripts/flutter_audit_loop.py", target_file, "--build", "--strict"]

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


def run_macro_quality_gate(
    targets: list[str],
    timeout_seconds: int,
    repo_root: Path | None = None,
) -> QualityGateResultDTO:
    """Execute the full 10-stage backend macro quality gate across all hardened backend targets.

    Args:
        targets: List of hardened backend target file paths.
        timeout_seconds: Audit timeout duration in seconds.
        repo_root: Workspace root directory.

    Returns:
        QualityGateResultDTO encapsulating macro-audit execution status and log output.
    """
    root = repo_root or get_repo_root()
    cmd = ["uv", "run", "python", "scripts/backend_audit_loop.py", *targets, "--test", "--ast-strict"]
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
            output=f"Macro-audit loop timed out after {timeout_seconds}s.\n{out}\n{err}".strip(),
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
        norm_path = unquote_git_path(line[3:].strip())
        if not norm_path or _has_invalid_git_path_chars(norm_path):
            continue
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
    """Roll back working directory modifications, strictly preserving hardening_state.json.

    Args:
        snapshot: Pre-attempt baseline workspace snapshot.
        target_file: Target file relative path.
        repo_root: Workspace root directory.
    """
    root = repo_root or get_repo_root()
    current = capture_workspace_snapshot(root)
    norm_target = target_file.replace("\\", "/")

    excluded = {"hardening_state.json", "hardening_cache.json", "data/hardening_cache.json"}

    to_restore: list[str] = []
    for f in current.modified_files:
        norm_f = f.replace("\\", "/")
        if norm_f in excluded or norm_f.endswith(("/hardening_state.json", "/hardening_cache.json")):
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
        if norm_u in excluded or norm_u.endswith(("/hardening_state.json", "/hardening_cache.json")):
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
    norm_target = target_file.replace("\\", "/").strip()

    # Phase 2, Step 4: Check SHA-256 content-addressed hardening cache for 0s short-circuit
    if not args.no_cache:
        manifest = load_or_seed_hardening_cache(args.cache_file, root)
        current_entry = compute_target_cache_entry(norm_target, root)
        existing_entry = manifest.entries[norm_target] if norm_target in manifest.entries else None
        if (
            existing_entry is not None
            and current_entry is not None
            and existing_entry.composite_sha256 == current_entry.composite_sha256
        ):
            print(
                f"  {ANSIColors.GREEN}⚡ CACHE HIT: {target_file} "
                f"(SHA-256 unchanged, 0.0s — skipped LLM subagent){ANSIColors.RESET}",
                flush=True,
            )
            checkpoint = mark_tracker_and_checkpoint(target_file, args.tracker, args.state_file, repo_root=root)
            return HardeningIterationResultDTO(
                target_file=target_file,
                gate=args.gate,
                success=True,
                attempts=0,
                duration_seconds=0.0,
                error_message=None,
                git_committed=checkpoint.git_committed,
                tracker_marked=checkpoint.tracker_marked,
                cache_hit=True,
            )

    start_time = time.monotonic()
    attempts = 0
    max_attempts = max(1, args.max_retries + 1)
    last_error: str | None = None

    for attempt in range(1, max_attempts + 1):
        attempts = attempt
        snapshot = capture_workspace_snapshot(root)

        execute_subagent_pass(target_file, args, repo_root=root)
        gate_res = run_quality_gate(
            target_file, args.gate, args.timeout_seconds, repo_root=root, micro_audit=args.micro_audit
        )

        if gate_res.success:
            if not args.no_cache:
                manifest = load_or_seed_hardening_cache(args.cache_file, root)
                tracker_str = args.tracker.as_posix() if args.tracker is not None else None
                updated_entry = compute_target_cache_entry(norm_target, root, source_tracker=tracker_str)
                if updated_entry is not None:
                    updated_manifest = manifest.model_copy(
                        update={"entries": {**manifest.entries, norm_target: updated_entry}}
                    )
                    save_hardening_cache(args.cache_file, updated_manifest, root)
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
                cache_hit=False,
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
        cache_hit=False,
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

    if args.gate == HardeningGate.ALL and not args.targets:
        backend_agent = args.agent_cmd or (DEFAULT_BACKEND_AGENT_TEMPLATE if not args.no_agent else None)
        backend_args = args.model_copy(update={"gate": HardeningGate.BACKEND, "agent_cmd": backend_agent})
        backend_summary = run_hardening_pipeline(backend_args, repo_root=root)
        if backend_summary.failure_count > 0 and args.fail_fast and not args.continue_on_failure:
            return backend_summary

        rem_max = max(0, args.max_files - backend_summary.processed_count) if args.max_files is not None else None
        frontend_agent = args.agent_cmd
        if frontend_agent and "/tier2-hardening-backend" in frontend_agent:
            frontend_agent = frontend_agent.replace("/tier2-hardening-backend", "/tier2-hardening-frontend")
        elif not frontend_agent and not args.no_agent:
            frontend_agent = DEFAULT_FRONTEND_AGENT_TEMPLATE

        frontend_args = args.model_copy(
            update={"gate": HardeningGate.FRONTEND, "agent_cmd": frontend_agent, "max_files": rem_max}
        )
        frontend_summary = run_hardening_pipeline(frontend_args, repo_root=root)

        b_iters = backend_summary.iterations or []
        f_iters = frontend_summary.iterations or []
        return HardeningRunSummaryDTO(
            total_targets=backend_summary.total_targets + frontend_summary.total_targets,
            processed_count=backend_summary.processed_count + frontend_summary.processed_count,
            success_count=backend_summary.success_count + frontend_summary.success_count,
            failure_count=backend_summary.failure_count + frontend_summary.failure_count,
            skipped_count=backend_summary.skipped_count + frontend_summary.skipped_count,
            iterations=b_iters + f_iters,
        )

    all_targets = fetch_unhardened_targets(args)
    total_targets = len(all_targets)

    if args.max_files is not None and args.max_files >= 0:
        targets_to_run = all_targets[: args.max_files]
    else:
        targets_to_run = all_targets

    processed_count = len(targets_to_run)
    skipped_count = total_targets - processed_count

    if args.dry_run:
        print(
            f"\n{ANSIColors.CYAN}--- DRY RUN: Target Hardening Queue ({processed_count} files) ---{ANSIColors.RESET}",
            flush=True,
        )
        micro_flags = " --micro --no-logfire" if args.micro_audit else ""
        for idx, target in enumerate(targets_to_run, 1):
            is_backend = args.gate == HardeningGate.BACKEND or (
                args.gate == HardeningGate.ALL and not target.endswith(".dart")
            )
            gate_cmd = (
                f"uv run python scripts/backend_audit_loop.py {target} --test --ast-strict{micro_flags}"
                if is_backend
                else f"uv run python scripts/flutter_audit_loop.py {target} --build"
            )
            print(f"  [{idx}/{processed_count}] {target} -> Planned: {gate_cmd}", flush=True)
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

    print(
        f"\n{ANSIColors.BOLD}Starting Autonomous Hardening Queue: {processed_count} targets{ANSIColors.RESET}",
        flush=True,
    )

    for idx, target in enumerate(targets_to_run, 1):
        print(
            f"\n{ANSIColors.CYAN}[{idx}/{processed_count}] Target: {target} ({args.gate.value}){ANSIColors.RESET}",
            flush=True,
        )
        iter_res = process_target_with_retries(target, args, repo_root=root)
        iterations.append(iter_res)

        if iter_res.success:
            success_count += 1
            dur = iter_res.duration_seconds
            print(
                f"  {ANSIColors.GREEN}✅ SUCCESS: {target} (att: {iter_res.attempts}, {dur:.1f}s){ANSIColors.RESET}",
                flush=True,
            )
        else:
            failure_count += 1
            dur = iter_res.duration_seconds
            print(
                f"  {ANSIColors.RED}❌ FAILED: {target} (att: {iter_res.attempts}, {dur:.1f}s){ANSIColors.RESET}",
                flush=True,
            )
            if iter_res.error_message and args.verbose:
                print(f"     Error summary: {iter_res.error_message[:400]}", flush=True)

            if args.fail_fast and not args.continue_on_failure:
                print(
                    f"{ANSIColors.YELLOW}⚡ Circuit breaker tripped (fail-fast). Halting queue.{ANSIColors.RESET}",
                    flush=True,
                )
                break

    # Step 2: Execute universal macro-audit once across all hardened backend targets at queue completion
    successful_backend_targets = [
        it.target_file for it in iterations if it.success and not it.cache_hit and it.target_file.endswith(".py")
    ]
    if args.micro_audit and successful_backend_targets and (failure_count == 0 or args.continue_on_failure):
        print(
            f"\n{ANSIColors.CYAN}🔍 Executing Final Macro-Audit Completion Gate across "
            f"{len(successful_backend_targets)} hardened backend target(s)...{ANSIColors.RESET}",
            flush=True,
        )
        macro_res = run_macro_quality_gate(successful_backend_targets, args.timeout_seconds, repo_root=root)
        if macro_res.success:
            print(f"  {ANSIColors.GREEN}✅ Final Macro-Audit Completion Gate PASSED.{ANSIColors.RESET}", flush=True)
        else:
            failure_count += 1
            print(f"  {ANSIColors.RED}❌ Final Macro-Audit Completion Gate FAILED!{ANSIColors.RESET}", flush=True)
            if macro_res.output:
                print(macro_res.output, flush=True)

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
   uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_xxx.md --agent-cmd "agy --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"

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
        choices=["backend", "frontend", "all"],
        default="all",
        help="Hardening gate category (backend, frontend, or all; default: all).",
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
    parser.add_argument(
        "--agent-cmd",
        type=str,
        default=None,
        help=(
            "Subagent command template (defaults to DEFAULT_BACKEND_AGENT_TEMPLATE / DEFAULT_FRONTEND_AGENT_TEMPLATE "
            "across all gates unless --no-agent is set)."
        ),
    )
    parser.add_argument(
        "--no-agent",
        action="store_true",
        default=False,
        help="Disable automatic AI subagent execution before audit (run quality gates only).",
    )
    parser.add_argument("--no-auto-fix", action="store_true", help="Disable automatic ruff/dart format passes.")
    parser.add_argument(
        "--fail-fast", action="store_true", default=True, help="Halt execution on first failure (default: True)."
    )
    parser.add_argument(
        "--continue-on-failure", action="store_true", default=False, help="Continue to next target on failure."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned target queue without mutations.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose diagnostics.")
    # Step 2: Expose --model and --no-micro CLI arguments in main
    parser.add_argument(
        "--model",
        type=str,
        choices=["gemini-4-argon-medium", "gemini-4-argon-high", "gemini-3.8-flash-high", "gemini-3.8-flash"],
        default="gemini-4-argon-medium",
        help="AI model identifier for subagent hardening iterations (default: gemini-4-argon-medium).",
    )
    parser.add_argument(
        "--no-micro",
        action="store_false",
        dest="micro_audit",
        default=True,
        help="Disable fast micro-audit mode during per-target iterations and run full 10-stage audit per file.",
    )
    # Phase 2, Step 4: Expose --no-cache / --force-agent and --cache-file CLI flags
    parser.add_argument(
        "--no-cache",
        "--force-agent",
        dest="no_cache",
        action="store_true",
        default=False,
        help="Bypass SHA-256 content-addressed hardening cache and force subagent + audit execution.",
    )
    parser.add_argument(
        "--cache-file",
        dest="cache_file",
        type=Path,
        default=DEFAULT_HARDENING_CACHE_PATH,
        help="Path to SHA-256 hardening cache JSON manifest (default: data/hardening_cache.json).",
    )

    parsed = parser.parse_args(argv)

    tracker_arg = clean_path_arg(parsed.tracker)
    state_file_arg = clean_path_arg(parsed.state_file)
    clean_targets: list[str] = []
    for t in parsed.targets:
        for sub_t in str(t).split(","):
            p = clean_path_arg(sub_t.strip())
            if p is not None:
                clean_targets.append(str(p).replace("\\", "/"))

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

    resolved_agent_cmd: str | None = parsed.agent_cmd
    if not resolved_agent_cmd and not parsed.no_agent:
        if parsed.gate == "backend":
            resolved_agent_cmd = DEFAULT_BACKEND_AGENT_TEMPLATE
        elif parsed.gate == "frontend":
            resolved_agent_cmd = DEFAULT_FRONTEND_AGENT_TEMPLATE
        else:
            resolved_agent_cmd = None

    try:
        dto = HardeningRunnerArgsDTO(
            tracker=tracker_arg,
            state_file=state_file_arg,
            gate=HardeningGate(parsed.gate),
            targets=clean_targets or None,
            max_files=parsed.max_files,
            max_retries=parsed.max_retries,
            timeout_seconds=parsed.timeout_seconds,
            agent_cmd=resolved_agent_cmd,
            no_agent=parsed.no_agent,
            no_auto_fix=parsed.no_auto_fix,
            fail_fast=parsed.fail_fast,
            continue_on_failure=parsed.continue_on_failure,
            dry_run=parsed.dry_run,
            verbose=parsed.verbose,
            model=parsed.model,
            micro_audit=parsed.micro_audit,
            no_cache=parsed.no_cache,
            cache_file=clean_path_arg(parsed.cache_file) or DEFAULT_HARDENING_CACHE_PATH,
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
