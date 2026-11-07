"""Deterministic Auditor for Antigravity Skills Architecture & Rule Budget Sovereignty.

Verifies that all workspace playbooks reside in .agents/skills/<name>/SKILL.md
with valid YAML frontmatter, that no legacy .agents/workflows/*.md files exist,
that all relative skill resource/reference links resolve on disk, and that the
always_on rules token/byte budget stays within Antigravity inline limits.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError

_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from scripts._ast_guardrails import scan_source_code_for_guardrails
from scripts.audit_dict_eradication import AuditViolation, DictEradicationVisitor

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

# Phase 1, Step 1: Rule budget constants and canonical skill/plugin inventory
MAX_SINGLE_RULE_FILE_BYTES: Final[int] = 24_000
MAX_ALWAYS_ON_BYTES: Final[int] = 72_000

REQUIRED_WORKSPACE_PLUGINS: Final[tuple[str, ...]] = (
    "flutter-dart",
    "github",
    "logfire",
    "postgres",
)

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
    "tier2-hardening-knowledge",
    "tier2-hardening-matrix",
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
_AT_SKILL_REF_RE: Final[re.Pattern[str]] = re.compile(r"@\[(\.agents/(?:rules|skills|plugins)/[^\]#\s<>]+)\]")
_ENV_PLACEHOLDER_RE: Final[re.Pattern[str]] = re.compile(r"\$\{[A-Z0-9_]+\}")
_KI_FILENAME_RE: Final[re.Pattern[str]] = re.compile(r"\b(ki_[a-z0-9_]+\.md)\b")
_SCRIPT_REF_RE: Final[re.Pattern[str]] = re.compile(r"\bscripts/([a-zA-Z0-9_]+\.py)\b")
_RULE_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r'<rule_block\s+id="([^"]+)">([\s\S]*?)</rule_block>')
_BANNED_TAG_RE: Final[re.Pattern[str]] = re.compile(r"<banned_pattern>([\s\S]*?)</banned_pattern>")
_MANDATORY_TAG_RE: Final[re.Pattern[str]] = re.compile(
    r"<(?:mandatory_pattern|mandate)>([\s\S]*?)</(?:mandatory_pattern|mandate)>"
)
_BAN_CLAUSE_CONSTRUCT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:NEVER\s+(?:exclusively\s+)?(?:use|call|invoke|import|write|allow|combine)"
    r"|(?:Using|Calling|Invoking|Importing)\b)\s+`([^`\n]{3,80})`"
)
_MANDATE_CLAUSE_CONSTRUCT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:ALWAYS|MUST)\s+(?:exclusively\s+)?(?:use|call|invoke|import|enforce)\s+`([^`\n]{3,80})`"
)

# Phase 1, Step 3: Planning, execution, and red-teaming skills enforcing factory & orthogonality mandates
PLANNING_AND_EXECUTION_FACTORY_SKILLS: Final[tuple[str, ...]] = (
    "tier0-create-epic",
    "tier0-create-plan",
    "tier0-research-plan",
    "tier1-planner",
    "tier2-execute",
    "tier8-red-teaming-audit",
)

REQUIRED_FACTORY_SKILL_TOKENS: Final[tuple[str, ...]] = (
    "schema_blast_radius_and_factory_mandate",
    "pairwise_rule_and_guardrail_orthogonality_mandate",
    "model_factories.py",
)

CANONICAL_RULE_SYNTAX_WITNESSES: Final[dict[str, str]] = {
    "qgr018_and_qgr020_strict_model_witness": (
        '"""Canonical syntax witness module for cross-checker orthogonality verification."""\n\n'
        "from __future__ import annotations\n\n"
        "from typing import Annotated\n\n"
        "from pydantic import BaseModel, ConfigDict, Field\n\n\n"
        "class CanonicalOrthogonalityWitnessDTO(BaseModel):\n"
        '    """Canonical strict Pydantic V2 witness model."""\n\n'
        '    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)\n\n'
        '    id: Annotated[str, Field(min_length=1, description="Canonical entity identifier")]\n'
        '    name: Annotated[str, Field(min_length=1, description="Canonical display name")]\n'
        '    tags: Annotated[list[str], Field(default_factory=list, description="Tag collection")]\n'
        '    notes: Annotated[str | None, Field(default=None, description="Optional notes")] = None\n'
    ),
}

# Phase 1B, Step 2: Canonical Knowledge Item artifacts and dynamic discovery
DEFAULT_CANONICAL_KI_ARTIFACTS: Final[frozenset[str]] = frozenset(
    {
        "ki_api_router_ssot_governance.md",
        "ki_deterministic_hardening_state.md",
        "ki_frontend_iam_role_segregation.md",
        "ki_global_config_sovereignty.md",
        "ki_god_code_prevention.md",
        "ki_mcp_gateway_architecture.md",
        "ki_router_ssot_and_crud_clone_lifecycle.md",
        "ki_zero_permissive_typing.md",
    }
)

PLACEHOLDER_KI_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "ki_name.md",
        "ki_filename.md",
        "ki_1.md",
        "ki_2.md",
    }
)


def discover_canonical_ki_artifacts(knowledge_dir: Path | None = None) -> frozenset[str]:
    """Discover canonical `ki_*.md` artifact filenames from the Antigravity knowledge directory.

    Args:
        knowledge_dir: Optional override path to the knowledge root directory.

    Returns:
        Frozenset of discovered `ki_*.md` filenames, or `DEFAULT_CANONICAL_KI_ARTIFACTS` when absent.
    """
    resolved_dir = (
        knowledge_dir if knowledge_dir is not None else (Path.home() / ".gemini" / "antigravity" / "knowledge")
    )
    if not resolved_dir.is_dir():
        return DEFAULT_CANONICAL_KI_ARTIFACTS
    discovered = frozenset(p.name for p in resolved_dir.rglob("ki_*.md") if p.is_file())
    return discovered if discovered else DEFAULT_CANONICAL_KI_ARTIFACTS


CANONICAL_KI_ARTIFACTS: frozenset[str] = discover_canonical_ki_artifacts()

__all__ = [
    "CANONICAL_KI_ARTIFACTS",
    "CANONICAL_RULE_SYNTAX_WITNESSES",
    "DEFAULT_CANONICAL_KI_ARTIFACTS",
    "MAX_ALWAYS_ON_BYTES",
    "MAX_SINGLE_RULE_FILE_BYTES",
    "McpConfigFileDTO",
    "McpServerEntryDTO",
    "PLACEHOLDER_KI_TOKENS",
    "PLANNING_AND_EXECUTION_FACTORY_SKILLS",
    "PluginManifestDTO",
    "REQUIRED_FACTORY_SKILL_TOKENS",
    "REQUIRED_QUORUM_SKILLS",
    "REQUIRED_WORKSPACE_PLUGINS",
    "RuleBlockSpecDTO",
    "SkillsArchitectureAuditor",
    "SkillsAuditFindingDTO",
    "SkillsAuditSummaryDTO",
    "build_arg_parser",
    "discover_canonical_ki_artifacts",
    "extract_rule_blocks_from_text",
    "main",
    "verify_candidate_rule_against_all",
    "verify_static_checker_orthogonality",
]


class PluginManifestDTO(BaseModel):
    """Immutable DTO validating .agents/plugins/<name>/plugin.json manifests.

    Attributes:
        name: Global unique plugin identifier.
        displayName: Optional human-readable title.
        description: Plugin purpose description.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(min_length=1, description="Global unique plugin identifier")]
    displayName: Annotated[str | None, Field(default=None, description="Optional human-readable title")] = None
    description: Annotated[str, Field(min_length=1, description="Plugin purpose description")]


class McpServerEntryDTO(BaseModel):
    """Immutable DTO validating an individual MCP server configuration entry.

    Attributes:
        command: Executable command for Stdio transport.
        args: Optional command-line arguments for Stdio transport.
        url: Remote endpoint URL for Streamable HTTP transport.
        serverUrl: Legacy remote endpoint URL.
        headers: Optional HTTP request headers.
        env: Optional environment variable map.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    command: Annotated[str | None, Field(default=None, description="Executable command for Stdio transport")] = None
    args: Annotated[list[str] | None, Field(default=None, description="Optional command-line arguments")] = None
    url: Annotated[str | None, Field(default=None, description="Remote endpoint URL")] = None
    serverUrl: Annotated[str | None, Field(default=None, description="Legacy remote endpoint URL")] = None
    headers: Annotated[dict[str, str] | None, Field(default=None, description="Optional HTTP request headers")] = None
    env: Annotated[dict[str, str] | None, Field(default=None, description="Optional environment variable map")] = None


class McpConfigFileDTO(BaseModel):
    """Immutable DTO validating .agents/plugins/<name>/mcp_config.json files.

    Attributes:
        mcpServers: Non-empty mapping of server identifiers to MCP server entries.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    mcpServers: Annotated[
        dict[str, McpServerEntryDTO],
        Field(min_length=1, description="Non-empty mapping of server identifiers to MCP server entries"),
    ]


class SkillsAuditFindingDTO(BaseModel):
    """Immutable DTO representing a single skills, plugin, or rule-budget violation.

    Attributes:
        rule_code: Violation code SKL001-SKL005.
        file_path: Workspace-relative file path.
        message: Human-readable violation description.
        remediation: Deterministic remediation instruction.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[
        str,
        Field(pattern=r"^SKL\d{3}$", description="Violation code SKL001-SKL005"),
    ]
    file_path: Annotated[str, Field(min_length=1, description="Workspace-relative file path")]
    message: Annotated[str, Field(min_length=1, description="Human-readable violation description")]
    remediation: Annotated[
        str,
        Field(min_length=1, description="Deterministic remediation instruction"),
    ]


class SkillsAuditSummaryDTO(BaseModel):
    """Immutable DTO summarizing the full skills, plugin, and rule-budget audit result.

    Attributes:
        verified_skills_count: Number of valid SKILL.md files verified.
        verified_plugins_count: Number of valid workspace plugins verified.
        always_on_total_bytes: Total UTF-8 byte count of always_on rules.
        findings: Accumulated audit findings.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    verified_skills_count: Annotated[int, Field(ge=0, description="Number of valid SKILL.md files verified")]
    verified_plugins_count: Annotated[int, Field(ge=0, description="Number of valid workspace plugins verified")]
    always_on_total_bytes: Annotated[int, Field(ge=0, description="Total UTF-8 byte count of always_on rules")]
    findings: Annotated[list[SkillsAuditFindingDTO], Field(description="Accumulated audit findings")]


# Phase 1, Step 3: Pairwise Rule Conflict & Static Checker Orthogonality DTO and Verifiers
class RuleBlockSpecDTO(BaseModel):
    """Immutable DTO representing a parsed <rule_block> specification for pairwise conflict auditing.

    Attributes:
        rule_id: Rule block identifier.
        file_path: Workspace-relative file path.
        banned_constructs: Normalized backticked constructs explicitly banned by this rule.
        mandatory_constructs: Normalized backticked constructs explicitly mandated by this rule.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_id: Annotated[str, Field(min_length=1, description="Rule block identifier")]
    file_path: Annotated[str, Field(min_length=1, description="Workspace-relative file path")]
    banned_constructs: Annotated[
        frozenset[str],
        Field(description="Normalized backticked constructs explicitly banned by this rule"),
    ]
    mandatory_constructs: Annotated[
        frozenset[str],
        Field(description="Normalized backticked constructs explicitly mandated by this rule"),
    ]


def _normalize_construct_tokens(matches: list[str]) -> set[str]:
    """Normalize extracted backticked construct tokens while filtering generic path/meta tokens.

    Args:
        matches: Raw backticked strings extracted from rule clauses.

    Returns:
        Normalized set of construct strings.
    """
    normalized: set[str] = set()
    for raw in matches:
        token = raw.strip()
        if len(token) >= 3 and not token.startswith(("@[", "./", "../", "<", "--")):
            normalized.add(token)
    return normalized


def extract_rule_blocks_from_text(content: str, file_path: str) -> list[RuleBlockSpecDTO]:
    """Extract <rule_block> definitions and their banned/mandatory constructs from Markdown/XML text.

    Args:
        content: Raw UTF-8 text of a rule or skill file.
        file_path: Workspace-relative POSIX path of the file.

    Returns:
        List of parsed RuleBlockSpecDTO instances.
    """
    specs: list[RuleBlockSpecDTO] = []
    for match in _RULE_BLOCK_RE.finditer(content):
        rule_id = match.group(1).strip()
        body = match.group(2)
        banned_sections = "\n".join(m.group(1) for m in _BANNED_TAG_RE.finditer(body))
        mandatory_sections = "\n".join(m.group(1) for m in _MANDATORY_TAG_RE.finditer(body))
        banned_raw = _normalize_construct_tokens(_BAN_CLAUSE_CONSTRUCT_RE.findall(banned_sections or body))
        mandatory_raw = _normalize_construct_tokens(_MANDATE_CLAUSE_CONSTRUCT_RE.findall(mandatory_sections or body))
        overlap = banned_raw & mandatory_raw
        specs.append(
            RuleBlockSpecDTO(
                rule_id=rule_id,
                file_path=file_path,
                banned_constructs=frozenset(banned_raw - overlap),
                mandatory_constructs=frozenset(mandatory_raw - overlap),
            )
        )
    return specs


def _rules_share_domain_scope(rule_a: RuleBlockSpecDTO, rule_b: RuleBlockSpecDTO) -> bool:
    """Determine whether two rules apply to overlapping language/domain scopes.

    Args:
        rule_a: First rule specification.
        rule_b: Second rule specification.

    Returns:
        True if the two rules govern overlapping domain scopes.
    """
    if rule_a.file_path == rule_b.file_path:
        return True
    isolated_pair = {".agents/rules/01-python-backend.md", ".agents/rules/02_flutter_desktop.md"}
    return {rule_a.file_path, rule_b.file_path} != isolated_pair


def verify_candidate_rule_against_all(
    candidate: RuleBlockSpecDTO,
    existing_rules: Sequence[RuleBlockSpecDTO],
) -> list[SkillsAuditFindingDTO]:
    """Verify a candidate rule one-by-one against all existing rules for mandate-vs-ban conflicts (SKL003).

    Args:
        candidate: Newly attached or inspected rule block specification.
        existing_rules: Sequence of existing rule block specifications to compare against.

    Returns:
        List of SKL003 findings for any detected pairwise polarity conflict.
    """
    findings: list[SkillsAuditFindingDTO] = []
    for other in existing_rules:
        if other.rule_id == candidate.rule_id and other.file_path == candidate.file_path:
            continue
        if not _rules_share_domain_scope(candidate, other):
            continue
        conflicts = sorted(
            (candidate.mandatory_constructs & other.banned_constructs)
            | (candidate.banned_constructs & other.mandatory_constructs)
        )
        if conflicts:
            joined = ", ".join(f"`{c}`" for c in conflicts)
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL003",
                    file_path=candidate.file_path,
                    message=(
                        f"Pairwise rule conflict between '{candidate.rule_id}' ({candidate.file_path}) and "
                        f"'{other.rule_id}' ({other.file_path}): mutually contradictory mandate/ban on {joined}."
                    ),
                    remediation=(
                        f"Align '{candidate.rule_id}' and '{other.rule_id}' so neither mandates a construct "
                        "explicitly banned by the other."
                    ),
                )
            )
    return findings


def verify_static_checker_orthogonality(
    witnesses: Mapping[str, str] = CANONICAL_RULE_SYNTAX_WITNESSES,
) -> list[SkillsAuditFindingDTO]:
    """Verify canonical compliant syntax witnesses pass both _ast_guardrails.py and DictEradicationVisitor (SKL003).

    Args:
        witnesses: Mapping of witness identifiers to compliant Python source snippets.

    Returns:
        List of SKL003 findings if any static checker rejects a canonical compliant syntax witness.
    """
    findings: list[SkillsAuditFindingDTO] = []
    synthetic_path = "backend_v2/models/domain/_orthogonality_witness.py"
    for witness_id, source_text in witnesses.items():
        source_bytes = source_text.encode("utf-8")
        qgr_violations = scan_source_code_for_guardrails(synthetic_path, source_bytes)
        dict_violations = _run_dict_visitor_on_witness(synthetic_path, source_bytes)
        if qgr_violations or dict_violations:
            qgr_msgs = [f"{v.rule_code}: {v.message}" for v in qgr_violations]
            dict_msgs = [f"{v.metric}: {v.message}" for v in dict_violations]
            combined = "; ".join([*qgr_msgs, *dict_msgs])
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL003",
                    file_path="scripts/audit_skills_architecture.py",
                    message=(f"Static checker orthogonality failure on witness '{witness_id}': {combined}"),
                    remediation=(
                        "Reconcile scripts/_ast_guardrails.py and scripts/audit_dict_eradication.py so "
                        "canonical compliant syntax passes all static checkers simultaneously."
                    ),
                )
            )
    return findings


def _run_dict_visitor_on_witness(synthetic_path: str, source_bytes: bytes) -> list[AuditViolation]:
    """Parse and run DictEradicationVisitor on a witness source snippet.

    Args:
        synthetic_path: Synthetic model file path for domain classification.
        source_bytes: UTF-8 encoded Python source code.

    Returns:
        List of AuditViolation records discovered by DictEradicationVisitor.
    """
    tree = ast.parse(source_bytes.decode("utf-8"), filename=synthetic_path)
    visitor = DictEradicationVisitor(synthetic_path, source_bytes, strict=True)
    visitor.visit(tree)
    return list(visitor.violations)


class SkillsArchitectureAuditor:
    """Static verifier for Antigravity Skills, Workspace Plugins, and always_on rule budget.

    Attributes:
        repo_root: Repository root directory path.
        required_skills: Required skill directory names to enforce.
        required_plugins: Required workspace plugin directory names to enforce.
    """

    def __init__(
        self,
        repo_root: Path,
        required_skills: tuple[str, ...] = REQUIRED_QUORUM_SKILLS,
        required_plugins: tuple[str, ...] = REQUIRED_WORKSPACE_PLUGINS,
        allowed_ki_artifacts: frozenset[str] = CANONICAL_KI_ARTIFACTS,
    ) -> None:
        """Initialize the auditor with repository root and required skill/plugin/KI names.

        Args:
            repo_root: Root directory of the workspace to audit.
            required_skills: Tuple of required skill directory names.
            required_plugins: Tuple of required workspace plugin directory names.
            allowed_ki_artifacts: Frozenset of canonical `ki_*.md` artifact filenames.
        """
        self.repo_root = repo_root.resolve()
        self.required_skills = required_skills
        self.required_plugins = required_plugins
        self.allowed_ki_artifacts = allowed_ki_artifacts

    def run_audit(self) -> SkillsAuditSummaryDTO:
        """Execute all verification stages and return an immutable summary DTO.

        Returns:
            Immutable summary containing verified counts, byte totals, and findings.
        """
        findings: list[SkillsAuditFindingDTO] = []
        findings.extend(self._check_legacy_workflows())
        verified_count, skill_findings = self._check_skills_directory()
        findings.extend(skill_findings)
        verified_plugins, plugin_findings = self._check_plugins_directory()
        findings.extend(plugin_findings)
        total_bytes, budget_findings = self._check_rule_budget()
        findings.extend(budget_findings)
        findings.extend(self._check_pairwise_rule_orthogonality())
        return SkillsAuditSummaryDTO(
            verified_skills_count=verified_count,
            verified_plugins_count=verified_plugins,
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

        findings.extend(self._check_hardening_skill_coverage(skills_dir))
        findings.extend(self._check_planning_and_execution_skill_contracts(skills_dir))
        return verified_count, findings

    def _check_hardening_skill_coverage(self, skills_dir: Path) -> list[SkillsAuditFindingDTO]:
        """Verify tier2-hardening-* skills collectively cover all canonical KIs and rules (SKL003).

        Args:
            skills_dir: Path to `.agents/skills`.

        Returns:
            List of SKL003 findings for omitted canonical KIs or rule files.
        """
        findings: list[SkillsAuditFindingDTO] = []
        backend_hardening_md = skills_dir / "tier2-hardening-backend" / "SKILL.md"
        frontend_hardening_md = skills_dir / "tier2-hardening-frontend" / "SKILL.md"
        if not (backend_hardening_md.is_file() and frontend_hardening_md.is_file()):
            return findings

        combined_hardening_text = (
            backend_hardening_md.read_text(encoding="utf-8", errors="replace")
            + "\n"
            + frontend_hardening_md.read_text(encoding="utf-8", errors="replace")
        )
        covered_kis = {m.group(1) for m in _KI_FILENAME_RE.finditer(combined_hardening_text)}
        for missing_ki in sorted(self.allowed_ki_artifacts - covered_kis):
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL003",
                    file_path=".agents/skills/tier2-hardening-backend/SKILL.md",
                    message=(
                        f"Canonical Knowledge Item '{missing_ki}' is not referenced in either "
                        "tier2-hardening-backend/SKILL.md or tier2-hardening-frontend/SKILL.md."
                    ),
                    remediation=(
                        f"Add '{missing_ki}' to DOMAIN_KI_RESOLUTION_GATE in tier2-hardening-backend/SKILL.md "
                        "or tier2-hardening-frontend/SKILL.md."
                    ),
                )
            )

        rules_dir = self.repo_root / ".agents" / "rules"
        if rules_dir.is_dir():
            for rule_file in sorted(rules_dir.glob("[0-9]*.md")):
                if rule_file.name not in combined_hardening_text:
                    findings.append(
                        SkillsAuditFindingDTO(
                            rule_code="SKL003",
                            file_path=".agents/skills/tier2-hardening-backend/SKILL.md",
                            message=(
                                f"Rule file '.agents/rules/{rule_file.name}' is not referenced in either "
                                "tier2-hardening-backend/SKILL.md or tier2-hardening-frontend/SKILL.md."
                            ),
                            remediation=(
                                f"Reference '.agents/rules/{rule_file.name}' in core_rules_routing of "
                                "tier2-hardening-backend/SKILL.md or tier2-hardening-frontend/SKILL.md."
                            ),
                        )
                    )
        return findings

    def _check_planning_and_execution_skill_contracts(self, skills_dir: Path) -> list[SkillsAuditFindingDTO]:
        """Verify planning, execution, and red-teaming skills declare factory and orthogonality mandates (SKL003).

        Args:
            skills_dir: Path to `.agents/skills`.

        Returns:
            List of SKL003 findings when required rule block IDs or factory references are missing.
        """
        findings: list[SkillsAuditFindingDTO] = []
        for skill_name in PLANNING_AND_EXECUTION_FACTORY_SKILLS:
            skill_md = skills_dir / skill_name / "SKILL.md"
            if not skill_md.is_file():
                continue
            rel_path = skill_md.relative_to(self.repo_root).as_posix()
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            for required_token in REQUIRED_FACTORY_SKILL_TOKENS:
                if required_token not in content:
                    findings.append(
                        SkillsAuditFindingDTO(
                            rule_code="SKL003",
                            file_path=rel_path,
                            message=(
                                f"Skill '{rel_path}' is missing required architectural contract token "
                                f"'{required_token}'."
                            ),
                            remediation=(
                                f"Add '{required_token}' to '{rel_path}' to enforce Polyfactory blast-radius "
                                "and pairwise rule/guardrail orthogonality governance."
                            ),
                        )
                    )
        return findings

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

        # Phase 1B, Step 2: Validate ki_*.md and scripts/*.py references in skill playbooks
        seen_bad_kis: set[str] = set()
        for match in _KI_FILENAME_RE.finditer(content):
            ki_name = match.group(1)
            if (
                ki_name not in PLACEHOLDER_KI_TOKENS
                and ki_name not in self.allowed_ki_artifacts
                and ki_name not in seen_bad_kis
            ):
                seen_bad_kis.add(ki_name)
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL003",
                        file_path=rel_skill_md,
                        message=f"Stale or non-existent Knowledge Item reference '{ki_name}' in '{rel_skill_md}'.",
                        remediation=(
                            f"Replace '{ki_name}' with an active canonical KI artifact from "
                            f"{sorted(self.allowed_ki_artifacts)}."
                        ),
                    )
                )

        scripts_dir = self.repo_root / "scripts"
        if scripts_dir.is_dir():
            seen_bad_scripts: set[str] = set()
            for match in _SCRIPT_REF_RE.finditer(content):
                script_name = match.group(1)
                if not (scripts_dir / script_name).is_file() and script_name not in seen_bad_scripts:
                    seen_bad_scripts.add(script_name)
                    findings.append(
                        SkillsAuditFindingDTO(
                            rule_code="SKL003",
                            file_path=rel_skill_md,
                            message=f"Broken script reference 'scripts/{script_name}' in '{rel_skill_md}'.",
                            remediation=f"Ensure 'scripts/{script_name}' exists on disk or update the reference.",
                        )
                    )
        return findings

    def _check_plugins_directory(self) -> tuple[int, list[SkillsAuditFindingDTO]]:
        """Verify workspace plugins in .agents/plugins/ and MCP security invariants (SKL005).

        Returns:
            2-tuple of (verified_plugins_count, findings).
        """
        findings: list[SkillsAuditFindingDTO] = []
        loose_mcp = self.repo_root / ".agents" / "mcp_config.json"
        if loose_mcp.is_file():
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL005",
                    file_path=".agents/mcp_config.json",
                    message="Loose '.agents/mcp_config.json' found outside a plugin bundle.",
                    remediation=(
                        "Package MCP servers inside '.agents/plugins/<name>/mcp_config.json' "
                        "and delete '.agents/mcp_config.json'."
                    ),
                )
            )

        plugins_dir = self.repo_root / ".agents" / "plugins"
        if not plugins_dir.is_dir():
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL005",
                    file_path=".agents/plugins",
                    message="Workspace plugins directory '.agents/plugins' does not exist.",
                    remediation="Create '.agents/plugins/<name>/' with plugin.json and mcp_config.json.",
                )
            )
            return 0, findings

        discovered_dirs = {p.name for p in plugins_dir.iterdir() if p.is_dir()}
        for req_plugin in self.required_plugins:
            if req_plugin not in discovered_dirs:
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL005",
                        file_path=f".agents/plugins/{req_plugin}/plugin.json",
                        message=f"Required workspace plugin '{req_plugin}' is missing from .agents/plugins/.",
                        remediation=f"Create '.agents/plugins/{req_plugin}/' with plugin.json and mcp_config.json.",
                    )
                )

        verified_count = 0
        for plugin_name in sorted(discovered_dirs):
            plugin_folder = plugins_dir / plugin_name
            plugin_findings = self._audit_single_plugin(plugin_folder)
            if not plugin_findings:
                verified_count += 1
            findings.extend(plugin_findings)

        return verified_count, findings

    def _audit_single_plugin(self, plugin_folder: Path) -> list[SkillsAuditFindingDTO]:
        """Audit a single workspace plugin directory for manifest and MCP security (SKL005).

        Args:
            plugin_folder: Path to `.agents/plugins/<name>`.

        Returns:
            List of SKL005 findings for this plugin directory.
        """
        findings: list[SkillsAuditFindingDTO] = []
        manifest_path = plugin_folder / "plugin.json"
        rel_manifest = manifest_path.relative_to(self.repo_root).as_posix()
        if not manifest_path.is_file():
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL005",
                    file_path=rel_manifest,
                    message=f"Plugin directory '{plugin_folder.name}' is missing 'plugin.json'.",
                    remediation=f"Create '{rel_manifest}' with valid 'name' and 'description' fields.",
                )
            )
        else:
            try:
                PluginManifestDTO.model_validate_json(manifest_path.read_text(encoding="utf-8"))
            except ValidationError as exc:
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL005",
                        file_path=rel_manifest,
                        message=f"Invalid plugin.json schema in '{rel_manifest}': {exc.errors()[0]['msg']}.",
                        remediation="Ensure plugin.json declares non-empty 'name' and 'description' fields.",
                    )
                )

        mcp_path = plugin_folder / "mcp_config.json"
        rel_mcp = mcp_path.relative_to(self.repo_root).as_posix()
        if not mcp_path.is_file():
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL005",
                    file_path=rel_mcp,
                    message=f"Plugin directory '{plugin_folder.name}' is missing 'mcp_config.json'.",
                    remediation=f"Create '{rel_mcp}' declaring the plugin's 'mcpServers' configuration.",
                )
            )
            return findings

        try:
            mcp_cfg = McpConfigFileDTO.model_validate_json(mcp_path.read_text(encoding="utf-8"))
        except ValidationError as exc:
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL005",
                    file_path=rel_mcp,
                    message=f"Invalid mcp_config.json schema in '{rel_mcp}': {exc.errors()[0]['msg']}.",
                    remediation="Ensure mcp_config.json defines a valid non-empty 'mcpServers' map.",
                )
            )
            return findings

        for server_id, entry in mcp_cfg.mcpServers.items():
            findings.extend(self._audit_mcp_server_entry(plugin_folder.name, rel_mcp, server_id, entry))
        return findings

    @staticmethod
    def _audit_mcp_server_entry(
        plugin_name: str,
        rel_mcp: str,
        server_id: str,
        entry: McpServerEntryDTO,
    ) -> list[SkillsAuditFindingDTO]:
        """Verify transport, credential interpolation, localhost ban, and read-only DB gates (SKL005).

        Args:
            plugin_name: Directory name of the plugin.
            rel_mcp: Workspace-relative path to `mcp_config.json`.
            server_id: MCP server key inside `mcpServers`.
            entry: Validated `McpServerEntryDTO` instance.

        Returns:
            List of SKL005 findings for this MCP server entry.
        """
        findings: list[SkillsAuditFindingDTO] = []
        endpoint_url = entry.url if entry.url is not None else entry.serverUrl
        if entry.command is None and endpoint_url is None:
            findings.append(
                SkillsAuditFindingDTO(
                    rule_code="SKL005",
                    file_path=rel_mcp,
                    message=f"MCP server '{server_id}' must declare either 'command' (Stdio) or 'url' (HTTP).",
                    remediation=f"Set 'command' or 'url' for server '{server_id}' in '{rel_mcp}'.",
                )
            )

        resolved_args = entry.args if entry.args is not None else ()
        url_and_args = [val for val in (entry.url, entry.serverUrl, *resolved_args) if val is not None]
        for target_str in url_and_args:
            lowered = target_str.lower()
            if "localhost" in lowered or "127.0.0.1" in lowered:
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL005",
                        file_path=rel_mcp,
                        message=(
                            f"MCP server '{server_id}' contains hardcoded localhost endpoint '{target_str}' "
                            "(violates localhost_endpoint_hardcoding_ban)."
                        ),
                        remediation="Inject connection URLs via '${ENV_VAR}' placeholders instead of localhost.",
                    )
                )

        if entry.headers is not None:
            for hdr_key, hdr_val in entry.headers.items():
                if hdr_key.lower() in {"authorization", "x-api-key"} and not _ENV_PLACEHOLDER_RE.search(hdr_val):
                    findings.append(
                        SkillsAuditFindingDTO(
                            rule_code="SKL005",
                            file_path=rel_mcp,
                            message=(
                                f"MCP server '{server_id}' header '{hdr_key}' contains a hardcoded credential "
                                "(violates credential_hardcoding_ban)."
                            ),
                            remediation=f"Replace hardcoded secret in '{hdr_key}' with '${{ENV_VAR}}' interpolation.",
                        )
                    )

        if entry.env is not None:
            for env_key, env_val in entry.env.items():
                upper_key = env_key.upper()
                is_secret_key = any(marker in upper_key for marker in ("TOKEN", "SECRET", "PASSWORD", "KEY", "URL"))
                if is_secret_key and not _ENV_PLACEHOLDER_RE.search(env_val):
                    findings.append(
                        SkillsAuditFindingDTO(
                            rule_code="SKL005",
                            file_path=rel_mcp,
                            message=(
                                f"MCP server '{server_id}' env var '{env_key}' contains a hardcoded secret "
                                "(violates credential_hardcoding_ban)."
                            ),
                            remediation=f"Set '{env_key}' to '${{{env_key}}}' in '{rel_mcp}'.",
                        )
                    )

        if plugin_name == "postgres":
            readonly_val = entry.env["DB_READONLY"] if entry.env is not None and "DB_READONLY" in entry.env else None
            if readonly_val != "true":
                findings.append(
                    SkillsAuditFindingDTO(
                        rule_code="SKL005",
                        file_path=rel_mcp,
                        message=f"PostgreSQL MCP server '{server_id}' must enforce 'DB_READONLY': 'true' in env.",
                        remediation='Add \'"env": {"DB_READONLY": "true"}\' to the postgres MCP configuration.',
                    )
                )
        return findings

    def _check_rule_budget(self) -> tuple[int, list[SkillsAuditFindingDTO]]:
        """Verify individual and aggregate byte sizes of always_on rule files (SKL004).

        Returns:
            2-tuple of (always_on_total_bytes, findings).
        """
        always_on_files: list[Path] = []
        all_rule_files: list[Path] = []
        for root_file_name in ("AGENTS.md", "GEMINI.md"):
            candidate = self.repo_root / root_file_name
            if candidate.is_file():
                always_on_files.append(candidate)
                all_rule_files.append(candidate)

        rules_dir = self.repo_root / ".agents" / "rules"
        if rules_dir.is_dir():
            for rule_path in sorted(rules_dir.glob("*.md")):
                all_rule_files.append(rule_path)
                if self._is_always_on_rule(rule_path):
                    always_on_files.append(rule_path)

        total_bytes = 0
        findings: list[SkillsAuditFindingDTO] = []

        # Phase 1B, Step 2: Validate ki_*.md references across all rule markdown files
        for rule_doc in all_rule_files:
            rel_rule_path = rule_doc.relative_to(self.repo_root).as_posix()
            rule_content = rule_doc.read_text(encoding="utf-8", errors="replace")
            seen_rule_bad_kis: set[str] = set()
            for match in _KI_FILENAME_RE.finditer(rule_content):
                ki_name = match.group(1)
                if (
                    ki_name not in PLACEHOLDER_KI_TOKENS
                    and ki_name not in self.allowed_ki_artifacts
                    and ki_name not in seen_rule_bad_kis
                ):
                    seen_rule_bad_kis.add(ki_name)
                    findings.append(
                        SkillsAuditFindingDTO(
                            rule_code="SKL003",
                            file_path=rel_rule_path,
                            message=f"Stale or non-existent Knowledge Item reference '{ki_name}' in '{rel_rule_path}'.",
                            remediation=(
                                f"Replace '{ki_name}' with an active canonical KI artifact from "
                                f"{sorted(self.allowed_ki_artifacts)}."
                            ),
                        )
                    )
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

    def _check_pairwise_rule_orthogonality(self) -> list[SkillsAuditFindingDTO]:
        """Verify all discovered <rule_block> specs pairwise and validate static checker witnesses (SKL003).

        Returns:
            List of SKL003 findings for any pairwise rule contradiction or static checker conflict.
        """
        rule_specs: list[RuleBlockSpecDTO] = []
        for doc_path in self._collect_rule_and_skill_markdown_files():
            rel_path = doc_path.relative_to(self.repo_root).as_posix()
            content = doc_path.read_text(encoding="utf-8", errors="replace")
            rule_specs.extend(extract_rule_blocks_from_text(content, rel_path))

        findings: list[SkillsAuditFindingDTO] = []
        seen_pairs: set[tuple[str, str]] = set()
        for idx, candidate in enumerate(rule_specs):
            prior_specs = rule_specs[:idx]
            for finding in verify_candidate_rule_against_all(candidate, prior_specs):
                pair_key = (candidate.file_path, finding.message)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    findings.append(finding)

        findings.extend(verify_static_checker_orthogonality())
        return findings

    def _collect_rule_and_skill_markdown_files(self) -> list[Path]:
        """Collect all root, .agents/rules/*.md, and .agents/skills/*/SKILL.md files in deterministic order.

        Returns:
            Ordered list of existing Markdown files containing rule blocks.
        """
        files: list[Path] = []
        for root_name in ("AGENTS.md", "GEMINI.md"):
            candidate = self.repo_root / root_name
            if candidate.is_file():
                files.append(candidate)
        rules_dir = self.repo_root / ".agents" / "rules"
        if rules_dir.is_dir():
            files.extend(sorted(rules_dir.glob("*.md")))
        skills_dir = self.repo_root / ".agents" / "skills"
        if skills_dir.is_dir():
            files.extend(sorted(skills_dir.glob("*/SKILL.md")))
        return files

    @staticmethod
    def _is_always_on_rule(rule_path: Path) -> bool:
        """Determine whether a rule Markdown file in .agents/rules/ is loaded as always_on.

        Args:
            rule_path: Path to a `.agents/rules/*.md` file.

        Returns:
            True if the rule declares `trigger: always_on` in YAML frontmatter.
        """
        content = rule_path.read_text(encoding="utf-8")
        fm_match = _FRONTMATTER_BLOCK_RE.match(content)
        if fm_match is None:
            return False
        trigger_match = _FRONTMATTER_TRIGGER_RE.search(fm_match.group(1))
        if trigger_match is None:
            return False
        trigger_val = trigger_match.group(1).strip("\"'").lower()
        return trigger_val == "always_on"


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser for the Skills Architecture Auditor.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="""Deterministic Antigravity Skills Architecture, Plugin & Rule Budget Auditor.

Verifies workspace compliance across five architectural gates:
  - SKL001: Zero deprecated .md or .bak files inside .agents/workflows/.
  - SKL002: All 29 required Quorum skills exist in .agents/skills/<name>/SKILL.md with valid YAML frontmatter.
  - SKL003: All relative ./resources/... and ./references/... links inside SKILL.md resolve on disk.
  - SKL004: Individual always_on rules stay <= 24,000 bytes and aggregate always_on rules stay <= 72,000 bytes.
  - SKL005: All 4 workspace plugins exist in .agents/plugins/<name>/ with valid manifests and zero hardcoded secrets.
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
    """CLI entrypoint for auditing Antigravity skills, plugins, and rule budgets.

    Args:
        argv: Optional list of command-line arguments.

    Returns:
        Exit code 0 if all checks pass, or 1 if any SKL001-SKL005 violations exist.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    auditor = SkillsArchitectureAuditor(repo_root=args.repo_root)
    summary = auditor.run_audit()

    est_tokens = summary.always_on_total_bytes // 4
    print(
        f"Skills Architecture Audit: verified_skills={summary.verified_skills_count}, "
        f"verified_plugins={summary.verified_plugins_count}, "
        f"always_on_bytes={summary.always_on_total_bytes}/{MAX_ALWAYS_ON_BYTES} (~{est_tokens} tokens)"
    )
    if not summary.findings:
        print("SUCCESS: 0 skills architecture, plugin, or rule budget violations detected.")
        return 0

    for finding in summary.findings:
        print(f"[{finding.rule_code}] {finding.file_path}: {finding.message}\n  Remediation: {finding.remediation}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
