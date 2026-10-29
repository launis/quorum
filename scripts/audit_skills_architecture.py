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

from pydantic import BaseModel, ConfigDict, Field, ValidationError

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

__all__ = [
    "MAX_ALWAYS_ON_BYTES",
    "MAX_SINGLE_RULE_FILE_BYTES",
    "McpConfigFileDTO",
    "McpServerEntryDTO",
    "PluginManifestDTO",
    "REQUIRED_QUORUM_SKILLS",
    "REQUIRED_WORKSPACE_PLUGINS",
    "SkillsArchitectureAuditor",
    "SkillsAuditFindingDTO",
    "SkillsAuditSummaryDTO",
    "main",
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
    verified_plugins_count: Annotated[int, Field(ge=0, description="Number of valid workspace plugins verified")] = 0
    always_on_total_bytes: Annotated[int, Field(ge=0, description="Total UTF-8 byte count of always_on rules")]
    findings: Annotated[list[SkillsAuditFindingDTO], Field(description="Accumulated audit findings")]


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
    ) -> None:
        """Initialize the auditor with repository root and required skill/plugin names.

        Args:
            repo_root: Root directory of the workspace to audit.
            required_skills: Tuple of required skill directory names.
            required_plugins: Tuple of required workspace plugin directory names.
        """
        self.repo_root = repo_root.resolve()
        self.required_skills = required_skills
        self.required_plugins = required_plugins

    def run_audit(self) -> SkillsAuditSummaryDTO:
        """Execute all five verification stages and return an immutable summary DTO.

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

        url_and_args = [val for val in (entry.url, entry.serverUrl, *(entry.args or [])) if val is not None]
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
