"""Deterministic Auditor for Antigravity Skills Architecture & Rule Budget Sovereignty.

Verifies that all workspace playbooks reside in .agents/skills/<name>/SKILL.md
with valid YAML frontmatter, that no legacy .agents/workflows/*.md files exist,
that all relative skill resource/reference links resolve on disk, and that the
always_on rules token/byte budget stays within Antigravity inline limits.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path
from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, ValueError, io.UnsupportedOperation:
        pass

if isinstance(sys.stderr, io.TextIOWrapper):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError, ValueError, io.UnsupportedOperation:
        pass

# Phase 1, Step 1: Rule budget constants and canonical skill inventory
MAX_SINGLE_RULE_FILE_BYTES: Final[int] = 24_000
MAX_ALWAYS_ON_BYTES: Final[int] = 72_000

REQUIRED_QUORUM_SKILLS: Final[tuple[str, ...]] = (
    "sdui-parity-sync",
    "seed-vault-ops",
    "tier0-create-epic",
    "tier0-create-plan",
    "tier0-research-epic",
    "tier0-research-plan",
    "tier1-plan-tracker-generator",
    "tier1-planner",
    "tier1-tracker-generator",
    "tier2-execute",
    "tier2-hardening-backend",
    "tier2-hardening-frontend",
    "tier3-database-reset",
    "tier3-feature-refactor",
    "tier3-god-code-decomposition",
    "tier3-minify-customization",
    "tier4-bug-hunting",
    "tier5-resume",
    "tier5-session-handover",
    "tier6-execution-monitor",
    "tier7-describe-architecture",
    "tier8-audit-epic",
    "tier8-audit-feature",
    "tier8-audit-plan",
    "tier8-red-teaming-audit",
    "tier8-test-coverage-expansion",
    "trace-forensics",
)

_FRONTMATTER_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"\A---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|\Z)")
_FRONTMATTER_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
_FRONTMATTER_DESC_RE: Final[re.Pattern[str]] = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)
_FRONTMATTER_TRIGGER_RE: Final[re.Pattern[str]] = re.compile(r"^trigger:\s*(.+?)\s*$", re.MULTILINE)
_RELATIVE_SKILL_LINK_RE: Final[re.Pattern[str]] = re.compile(r"\]\((\./(?:resources|references)/[^)#\s]+)\)")
_AT_SKILL_REF_RE: Final[re.Pattern[str]] = re.compile(r"@\[(\.agents/(?:rules|skills)/[^\]#\s<>]+)\]")

__all__ = [
    "MAX_ALWAYS_ON_BYTES",
    "MAX_SINGLE_RULE_FILE_BYTES",
    "REQUIRED_QUORUM_SKILLS",
    "SkillsArchitectureAuditor",
    "SkillsAuditFindingDTO",
    "SkillsAuditSummaryDTO",
    "main",
]


class SkillsAuditFindingDTO(BaseModel):
    """Immutable DTO representing a single skills or rule-budget violation.

    Attributes:
        rule_code: Violation code SKL001-SKL004.
        file_path: Workspace-relative file path.
        message: Human-readable violation description.
        remediation: Deterministic remediation instruction.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[
        str,
        Field(pattern=r"^SKL\d{3}$", description="Violation code SKL001-SKL004"),
    ]
    file_path: Annotated[str, Field(min_length=1, description="Workspace-relative file path")]
    message: Annotated[str, Field(min_length=1, description="Human-readable violation description")]
    remediation: Annotated[
        str,
        Field(min_length=1, description="Deterministic remediation instruction"),
    ]


class SkillsAuditSummaryDTO(BaseModel):
    """Immutable DTO summarizing the full skills and rule-budget audit result.

    Attributes:
        verified_skills_count: Number of valid SKILL.md files verified.
        always_on_total_bytes: Total UTF-8 byte count of always_on rules.
        findings: Accumulated audit findings.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    verified_skills_count: Annotated[int, Field(ge=0, description="Number of valid SKILL.md files verified")]
    always_on_total_bytes: Annotated[int, Field(ge=0, description="Total UTF-8 byte count of always_on rules")]
    findings: Annotated[list[SkillsAuditFindingDTO], Field(description="Accumulated audit findings")]


class SkillsArchitectureAuditor:
    """Static verifier for Antigravity Skills topology and always_on rule budget.

    Attributes:
        repo_root: Repository root directory path.
        required_skills: Required skill directory names to enforce.
    """

    def __init__(
        self,
        repo_root: Path,
        required_skills: tuple[str, ...] = REQUIRED_QUORUM_SKILLS,
    ) -> None:
        """Initialize the auditor with repository root and required skill names.

        Args:
            repo_root: Root directory of the workspace to audit.
            required_skills: Tuple of required skill directory names.
        """
        self.repo_root = repo_root.resolve()
        self.required_skills = required_skills

    def run_audit(self) -> SkillsAuditSummaryDTO:
        """Execute all four verification stages and return an immutable summary DTO.

        Returns:
            Immutable summary containing verified counts, byte totals, and findings.
        """
        findings: list[SkillsAuditFindingDTO] = []
        findings.extend(self._check_legacy_workflows())
        verified_count, skill_findings = self._check_skills_directory()
        findings.extend(skill_findings)
        total_bytes, budget_findings = self._check_rule_budget()
        findings.extend(budget_findings)
        return SkillsAuditSummaryDTO(
            verified_skills_count=verified_count,
            always_on_total_bytes=total_bytes,
            findings=findings,
        )

    def _check_legacy_workflows(self) -> list[SkillsAuditFindingDTO]:
        """Verify zero .md or .bak files remain inside .agents/workflows/ (SKL001).

        Returns:
            List of SKL001 findings for any leftover legacy workflow files.
        """
        workflows_dir = self.repo_root / ".agents" / "workflows"
        if not workflows_dir.exists():
            return []

        findings: list[SkillsAuditFindingDTO] = []
        for candidate in sorted(workflows_dir.iterdir()):
            if candidate.is_file() and candidate.suffix in {".md", ".bak"}:
                rel_path = candidate.relative_to(self.repo_root).as_posix()
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL001",
                        file_path=rel_path,
                        message=f"Deprecated workflow file '{rel_path}' found in .agents/workflows/.",
                        remediation="Migrate playbook to .agents/skills/<name>/SKILL.md and delete the legacy file.",
                    )
                )
        return findings

    def _check_skills_directory(self) -> tuple[int, list[SkillsAuditFindingDTO]]:
        """Verify required and discovered skills for frontmatter and link integrity.

        Returns:
            2-tuple of (verified_skills_count, findings).
        """
        skills_dir = self.repo_root / ".agents" / "skills"
        findings: list[SkillsAuditFindingDTO] = []
        if not skills_dir.exists():
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL002",
                    file_path=".agents/skills",
                    message="Skills root directory '.agents/skills' does not exist.",
                    remediation="Create .agents/skills/<name>/SKILL.md for all required Quorum skills.",
                )
            )
            return 0, findings

        discovered_dirs = {p.name for p in skills_dir.iterdir() if p.is_dir()}
        for req_name in self.required_skills:
            if req_name not in discovered_dirs:
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL002",
                        file_path=f".agents/skills/{req_name}/SKILL.md",
                        message=f"Required skill '{req_name}' is missing from .agents/skills/.",
                        remediation=f"Create .agents/skills/{req_name}/SKILL.md with valid YAML frontmatter.",
                    )
                )

        verified_count = 0
        for skill_name in sorted(discovered_dirs):
            skill_folder = skills_dir / skill_name
            skill_findings = self._audit_single_skill(skill_folder)
            if not skill_findings:
                verified_count += 1
            findings.extend(skill_findings)

        return verified_count, findings

    def _audit_single_skill(self, skill_folder: Path) -> list[SkillsAuditFindingDTO]:
        """Audit a single skill directory for SKL002 frontmatter and SKL003 links.

        Args:
            skill_folder: Path to `.agents/skills/<name>`.

        Returns:
            List of findings for this skill directory.
        """
        skill_md = skill_folder / "SKILL.md"
        rel_skill_md = skill_md.relative_to(self.repo_root).as_posix()
        if not skill_md.is_file():
            return [
                SkillsAuditFindingDTO(
                    rule_code="SKL002",
                    file_path=rel_skill_md,
                    message=f"Skill directory '{skill_folder.name}' is missing SKILL.md.",
                    remediation=f"Create '{rel_skill_md}' with YAML frontmatter (name and description).",
                )
            ]

        content = skill_md.read_text(encoding="utf-8")
        findings = self._validate_skill_frontmatter(skill_folder.name, rel_skill_md, content)
        findings.extend(self._validate_skill_links(skill_folder, rel_skill_md, content))
        return findings

    def _validate_skill_frontmatter(
        self, expected_name: str, rel_skill_md: str, content: str
    ) -> list[SkillsAuditFindingDTO]:
        """Validate YAML frontmatter name and description fields (SKL002).

        Args:
            expected_name: Directory name of the skill.
            rel_skill_md: Workspace-relative path to SKILL.md.
            content: Raw UTF-8 text of SKILL.md.

        Returns:
            List of SKL002 findings if frontmatter is missing or invalid.
        """
        fm_match = _FRONTMATTER_BLOCK_RE.match(content)
        if fm_match is None:
            return [
                SkillsAuditFindingDTO(
                    rule_code="SKL002",
                    file_path=rel_skill_md,
                    message=f"'{rel_skill_md}' is missing leading YAML frontmatter block (--- ... ---).",
                    remediation="Prepend YAML frontmatter with 'name' and 'description' fields.",
                )
            ]

        fm_body = fm_match.group(1)
        name_match = _FRONTMATTER_NAME_RE.search(fm_body)
        desc_match = _FRONTMATTER_DESC_RE.search(fm_body)
        parsed_name = name_match.group(1).strip("\"'") if name_match else ""
        parsed_desc = desc_match.group(1).strip("\"'") if desc_match else ""

        findings: list[SkillsAuditFindingDTO] = []
        if parsed_name != expected_name:
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL002",
                    file_path=rel_skill_md,
                    message=(f"Frontmatter name '{parsed_name}' does not match directory name '{expected_name}'."),
                    remediation=f"Set 'name: {expected_name}' in {rel_skill_md} YAML frontmatter.",
                )
            )
        if not parsed_desc:
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL002",
                    file_path=rel_skill_md,
                    message=f"'{rel_skill_md}' has a missing or empty 'description' in YAML frontmatter.",
                    remediation="Add a non-empty 'description' field to the YAML frontmatter.",
                )
            )
        return findings

    def _validate_skill_links(self, skill_folder: Path, rel_skill_md: str, content: str) -> list[SkillsAuditFindingDTO]:
        """Validate relative resource/reference links and @[.agents/...] paths (SKL003).

        Args:
            skill_folder: Path to `.agents/skills/<name>`.
            rel_skill_md: Workspace-relative path to SKILL.md.
            content: Raw UTF-8 text of SKILL.md.

        Returns:
            List of SKL003 findings for broken links.
        """
        findings: list[SkillsAuditFindingDTO] = []
        for match in _RELATIVE_SKILL_LINK_RE.finditer(content):
            rel_target = match.group(1)
            resolved = (skill_folder / rel_target).resolve()
            if not resolved.is_file():
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL003",
                        file_path=rel_skill_md,
                        message=f"Broken relative skill link '{rel_target}' in '{rel_skill_md}'.",
                        remediation=f"Create the target file '{rel_target}' inside '{skill_folder.name}' or fix the link.",
                    )
                )

        for match in _AT_SKILL_REF_RE.finditer(content):
            repo_rel_target = match.group(1)
            if "*" in repo_rel_target or "..." in repo_rel_target:
                continue
            resolved = (self.repo_root / repo_rel_target).resolve()
            if not resolved.exists():
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL003",
                        file_path=rel_skill_md,
                        message=f"Broken workspace reference '@[{repo_rel_target}]' in '{rel_skill_md}'.",
                        remediation=f"Ensure '{repo_rel_target}' exists in the workspace or update the reference.",
                    )
                )
        return findings

    def _check_rule_budget(self) -> tuple[int, list[SkillsAuditFindingDTO]]:
        """Verify individual and aggregate byte sizes of always_on rule files (SKL004).

        Returns:
            2-tuple of (always_on_total_bytes, findings).
        """
        always_on_files: list[Path] = []
        for root_file_name in ("AGENTS.md", "GEMINI.md"):
            candidate = self.repo_root / root_file_name
            if candidate.is_file():
                always_on_files.append(candidate)

        rules_dir = self.repo_root / ".agents" / "rules"
        if rules_dir.is_dir():
            for rule_path in sorted(rules_dir.glob("*.md")):
                if self._is_always_on_rule(rule_path):
                    always_on_files.append(rule_path)

        total_bytes = 0
        findings: list[SkillsAuditFindingDTO] = []
        for rule_file in always_on_files:
            size_bytes = len(rule_file.read_bytes())
            total_bytes += size_bytes
            rel_path = rule_file.relative_to(self.repo_root).as_posix()
            if size_bytes > MAX_SINGLE_RULE_FILE_BYTES:
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL004",
                        file_path=rel_path,
                        message=(
                            f"Rule file '{rel_path}' is {size_bytes} bytes, exceeding "
                            f"MAX_SINGLE_RULE_FILE_BYTES ({MAX_SINGLE_RULE_FILE_BYTES})."
                        ),
                        remediation="Compress the rule file or convert domain-specific rules to trigger: model_decision.",
                    )
                )

        if total_bytes > MAX_ALWAYS_ON_BYTES:
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL004",
                    file_path="AGENTS.md",
                    message=(
                        f"Aggregate always_on rules size is {total_bytes} bytes "
                        f"(~{total_bytes // 4} tokens), exceeding MAX_ALWAYS_ON_BYTES ({MAX_ALWAYS_ON_BYTES})."
                    ),
                    remediation="Change domain-specific rule files to 'trigger: model_decision' or trim redundant tables.",
                )
            )
        return total_bytes, findings

    @staticmethod
    def _is_always_on_rule(rule_path: Path) -> bool:
        """Determine whether a rule Markdown file is loaded as always_on.

        Args:
            rule_path: Path to a `.agents/rules/*.md` file.

        Returns:
            True if the rule does not declare `trigger: model_decision` or `trigger: manual`.
        """
        content = rule_path.read_text(encoding="utf-8")
        fm_match = _FRONTMATTER_BLOCK_RE.match(content)
        if fm_match is None:
            return True
        trigger_match = _FRONTMATTER_TRIGGER_RE.search(fm_match.group(1))
        if trigger_match is None:
            return True
        trigger_val = trigger_match.group(1).strip("\"'").lower()
        return trigger_val not in {"model_decision", "manual", "glob"}


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser for the Skills Architecture Auditor.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="""Deterministic Antigravity Skills Architecture & Rule Budget Auditor.

Verifies workspace compliance across four architectural gates:
  - SKL001: Zero deprecated .md or .bak files inside .agents/workflows/.
  - SKL002: All 27 required Quorum skills exist in .agents/skills/<name>/SKILL.md with valid YAML frontmatter.
  - SKL003: All relative ./resources/... and ./references/... links inside SKILL.md resolve on disk.
  - SKL004: Individual always_on rules stay <= 24,000 bytes and aggregate always_on rules stay <= 72,000 bytes.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py
  $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_skills_architecture.py --repo-root .
""",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root directory to audit (default: workspace root).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for auditing Antigravity skills and rule budgets.

    Args:
        argv: Optional list of command-line arguments.

    Returns:
        Exit code 0 if all checks pass, or 1 if any SKL001-SKL004 violations exist.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    auditor = SkillsArchitectureAuditor(repo_root=args.repo_root)
    summary = auditor.run_audit()

    est_tokens = summary.always_on_total_bytes // 4
    print(
        f"Skills Architecture Audit: verified={summary.verified_skills_count}, "
        f"always_on_bytes={summary.always_on_total_bytes}/{MAX_ALWAYS_ON_BYTES} (~{est_tokens} tokens)"
    )
    if not summary.findings:
        print("SUCCESS: 0 skills architecture or rule budget violations detected.")
        return 0

    for finding in summary.findings:
        print(f"[{finding.rule_code}] {finding.file_path}: {finding.message}\n  Remediation: {finding.remediation}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
