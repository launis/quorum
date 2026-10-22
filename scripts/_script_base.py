"""Script Infrastructure & Architectural SSOT Base.

Centralizes workspace root resolution, stdout UTF-8 reconfiguration, ANSI terminal styling,
guardrail severities, and base audit finding DTOs across Quorum developer tooling.
"""

from __future__ import annotations

import io
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


def get_repo_root() -> Path:
    """Resolve repository root directory from current script location.

    Returns:
        Absolute Path to the repository root directory.
    """
    return Path(__file__).resolve().parent.parent


def setup_script_environment() -> Path:
    """Reconfigure stdout/stderr to UTF-8 on Windows and inject repository root into sys.path.

    Returns:
        Resolved repository root Path.
    """
    if isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError, io.UnsupportedOperation:
            pass

    if isinstance(sys.stderr, io.TextIOWrapper):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError, io.UnsupportedOperation:
            pass

    repo_root = get_repo_root()
    root_str = str(repo_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    return repo_root


class GuardrailSeverity(StrEnum):
    """Severity classification for guardrail and audit violations."""

    WARNING = "WARNING"
    FATAL = "FATAL"


class ANSIColors:
    """ANSI escape sequences for terminal formatting and status colors."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class BaseAuditFindingDTO(BaseModel):
    """Pydantic V2 DTO representing a base audit finding."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[str, Field(description="Architectural or guardrail rule code")]
    message: Annotated[str, Field(description="Human-readable finding message")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    remediation: Annotated[str | None, Field(default=None, description="Deterministic remediation guidance")]
