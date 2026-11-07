"""ISTQB Unit Test Suite for scripts/audit_skills_architecture.py.

Verifies SKL001 (legacy workflow remnant), SKL002 (missing/mismatched skill frontmatter),
SKL003 (broken relative skill resource/reference links), SKL004 (always_on rule
byte budget boundary value analysis), and SKL005 (workspace plugin manifest and MCP
security invariants).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.audit_skills_architecture import (
    CANONICAL_KI_ARTIFACTS,
    CANONICAL_RULE_SYNTAX_WITNESSES,
    DEFAULT_CANONICAL_KI_ARTIFACTS,
    MAX_ALWAYS_ON_BYTES,
    MAX_SINGLE_RULE_FILE_BYTES,
    PLACEHOLDER_KI_TOKENS,
    PLANNING_AND_EXECUTION_FACTORY_SKILLS,
    REQUIRED_QUORUM_SKILLS,
    REQUIRED_WORKSPACE_PLUGINS,
    RuleBlockSpecDTO,
    SkillsArchitectureAuditor,
    SkillsAuditFindingDTO,
    SkillsAuditSummaryDTO,
    discover_canonical_ki_artifacts,
    extract_rule_blocks_from_text,
    main,
    verify_candidate_rule_against_all,
    verify_static_checker_orthogonality,
)


def _populate_compliant_workspace(root: Path) -> None:
    """Create a compliant workspace tree with all required skills, plugins, and rules.

    Args:
        root: Temporary directory root representing the repository.
    """
    (root / "AGENTS.md").write_text("# Root Agent Config\n", encoding="utf-8")
    (root / "GEMINI.md").write_text("# Gemini Config\n", encoding="utf-8")

    rules_dir = root / ".agents" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "00-antigravity-core.md").write_text(
        "---\ntrigger: always_on\n---\n# Core Rules\n",
        encoding="utf-8",
    )
    (rules_dir / "05_llm_architecture.md").write_text(
        "---\ntrigger: model_decision\ndescription: LLM rules\n---\n" + ("x" * 20_000),
        encoding="utf-8",
    )

    workflows_dir = root / ".agents" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    skills_dir = root / ".agents" / "skills"
    ki_refs_str = " ".join(sorted(CANONICAL_KI_ARTIFACTS))
    for skill_name in REQUIRED_QUORUM_SKILLS:
        s_dir = skills_dir / skill_name
        res_dir = s_dir / "resources"
        res_dir.mkdir(parents=True, exist_ok=True)
        (res_dir / "template.md").write_text("# Template\n", encoding="utf-8")
        extra_hardening_refs = ""
        if skill_name in {"tier2-hardening-backend", "tier2-hardening-frontend"}:
            extra_hardening_refs = (
                f"Covers {ki_refs_str}, placeholder ki_name.md, and @[.agents/rules/05_llm_architecture.md].\n"
            )
        extra_factory_refs = ""
        if skill_name in PLANNING_AND_EXECUTION_FACTORY_SKILLS:
            extra_factory_refs = (
                '<rule_block id="schema_blast_radius_and_factory_mandate">\n'
                "  <mandatory_pattern>ALWAYS use `ModelFactory.build(...)` from "
                "backend_v2/tests/factories/model_factories.py.</mandatory_pattern>\n"
                "</rule_block>\n"
                '<rule_block id="pairwise_rule_and_guardrail_orthogonality_mandate">\n'
                "  <mandatory_pattern>ALWAYS run `scripts/audit_skills_architecture.py`.</mandatory_pattern>\n"
                "</rule_block>\n"
            )
        (s_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Canonical skill {skill_name}\n---\n"
            f"See [template](./resources/template.md) and @[.agents/rules/00-antigravity-core.md].\n"
            f"{extra_hardening_refs}{extra_factory_refs}",
            encoding="utf-8",
        )

    plugins_dir = root / ".agents" / "plugins"
    for plugin_name in REQUIRED_WORKSPACE_PLUGINS:
        p_dir = plugins_dir / plugin_name
        p_dir.mkdir(parents=True, exist_ok=True)
        (p_dir / "plugin.json").write_text(
            f'{{"name": "quorum-{plugin_name}", "description": "Plugin {plugin_name}"}}\n',
            encoding="utf-8",
        )
        if plugin_name == "logfire":
            (p_dir / "mcp_config.json").write_text(
                '{"mcpServers": {"logfire": {"url": "https://logfire-eu.pydantic.dev/mcp", '
                '"headers": {"Authorization": "Bearer ${LOGFIRE_MCP_TOKEN}"}}}}\n',
                encoding="utf-8",
            )
        elif plugin_name == "postgres":
            (p_dir / "mcp_config.json").write_text(
                '{"mcpServers": {"quorum-postgres-mcp": {"command": "npx", '
                '"args": ["-y", "@modelcontextprotocol/server-postgres", "${POSTGRES_MCP_URL}"], '
                '"env": {"DB_READONLY": "true"}}}}\n',
                encoding="utf-8",
            )
        elif plugin_name == "github":
            (p_dir / "mcp_config.json").write_text(
                '{"mcpServers": {"quorum-github-mcp": {"command": "npx", '
                '"args": ["-y", "@modelcontextprotocol/server-github"], '
                '"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}}}}\n',
                encoding="utf-8",
            )
        else:
            (p_dir / "mcp_config.json").write_text(
                '{"mcpServers": {"quorum-dart-mcp": {"command": "dart", "args": ["mcp-server"]}}}\n',
                encoding="utf-8",
            )


def test_scenario_1_happy_path_valid_skills_and_rule_budget(tmp_path: Path) -> None:
    """Verify compliant skills, plugins, and always_on budget produce zero findings."""
    _populate_compliant_workspace(tmp_path)
    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    assert isinstance(summary, SkillsAuditSummaryDTO)
    assert summary.findings == []
    assert summary.verified_skills_count == len(REQUIRED_QUORUM_SKILLS)
    assert summary.verified_plugins_count == len(REQUIRED_WORKSPACE_PLUGINS)
    assert 0 < summary.always_on_total_bytes < MAX_ALWAYS_ON_BYTES
    assert main(["--repo-root", str(tmp_path)]) == 0


def test_scenario_2_negative_legacy_workflow_remnant_skl001(tmp_path: Path) -> None:
    """Verify leftover .agents/workflows/*.md or .bak file triggers fatal SKL001."""
    _populate_compliant_workspace(tmp_path)
    legacy_file = tmp_path / ".agents" / "workflows" / "tier2-execute.md"
    legacy_file.write_text("# Deprecated workflow\n", encoding="utf-8")

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    codes = [f.rule_code for f in summary.findings]
    assert "SKL001" in codes
    assert any(f.file_path == ".agents/workflows/tier2-execute.md" for f in summary.findings)
    assert main(["--repo-root", str(tmp_path)]) == 1


def test_scenario_3_negative_malformed_frontmatter_and_broken_links_skl002_skl003(
    tmp_path: Path,
) -> None:
    """Verify missing description, mismatched name, and broken links trigger SKL002 and SKL003."""
    _populate_compliant_workspace(tmp_path)

    # 1. Skill with mismatched name, missing description, and broken ./resources/missing.md link
    custom_skill_dir = tmp_path / ".agents" / "skills" / "my-skill"
    custom_skill_dir.mkdir(parents=True, exist_ok=True)
    (custom_skill_dir / "SKILL.md").write_text(
        "---\nname: wrong-name\n---\n"
        "Broken [link](./resources/missing.md) and @[.agents/rules/non_existent_rule.md].\n",
        encoding="utf-8",
    )

    # 2. Skill missing YAML frontmatter block completely
    no_fm_dir = tmp_path / ".agents" / "skills" / "no-frontmatter-skill"
    no_fm_dir.mkdir(parents=True, exist_ok=True)
    (no_fm_dir / "SKILL.md").write_text("# Just Markdown without frontmatter\n", encoding="utf-8")

    # 3. Empty skill directory missing SKILL.md
    empty_skill_dir = tmp_path / ".agents" / "skills" / "empty-skill"
    empty_skill_dir.mkdir(parents=True, exist_ok=True)

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl002_findings = [f for f in summary.findings if f.rule_code == "SKL002"]
    skl003_findings = [f for f in summary.findings if f.rule_code == "SKL003"]
    assert len(skl002_findings) >= 4
    assert len(skl003_findings) == 2


def test_scenario_4_negative_rule_budget_boundary_violation_skl004(
    tmp_path: Path,
) -> None:
    """Verify single-file (24,001B) and aggregate (72,001B) boundary violations trigger SKL004."""
    _populate_compliant_workspace(tmp_path)
    rules_dir = tmp_path / ".agents" / "rules"

    # Boundary value: MAX_SINGLE_RULE_FILE_BYTES + 1 (24,001 bytes)
    fm_header = "---\ntrigger: always_on\n---\n"
    oversized_single = fm_header + ("a" * (MAX_SINGLE_RULE_FILE_BYTES + 1 - len(fm_header)))
    (rules_dir / "00-antigravity-core.md").write_text(oversized_single, encoding="utf-8", newline="\n")

    # Add two more always_on files so aggregate exceeds MAX_ALWAYS_ON_BYTES (72,000 bytes)
    exact_cap_body = fm_header + ("b" * (MAX_SINGLE_RULE_FILE_BYTES - len(fm_header)))
    (rules_dir / "extra_always_on_1.md").write_text(exact_cap_body, encoding="utf-8", newline="\n")
    (rules_dir / "extra_always_on_2.md").write_text(exact_cap_body, encoding="utf-8", newline="\n")

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl004_findings = [f for f in summary.findings if f.rule_code == "SKL004"]
    assert len(skl004_findings) == 2
    assert summary.always_on_total_bytes > MAX_ALWAYS_ON_BYTES


def test_missing_skills_directory_and_dto_strictness(tmp_path: Path) -> None:
    """Verify missing .agents/skills and .agents/plugins directories emit SKL002/SKL005 and DTOs reject invalid fields."""
    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()
    assert any(f.rule_code == "SKL002" and f.file_path == ".agents/skills" for f in summary.findings)
    assert any(f.rule_code == "SKL005" and f.file_path == ".agents/plugins" for f in summary.findings)

    with pytest.raises(ValidationError):
        SkillsAuditFindingDTO(
            rule_code="INVALID",
            file_path="AGENTS.md",
            message="Invalid code",
            remediation="Fix code",
        )


def test_scenario_5_negative_loose_mcp_config_and_missing_plugin_skl005(tmp_path: Path) -> None:
    """Verify loose .agents/mcp_config.json and missing/malformed plugin manifests trigger SKL005."""
    _populate_compliant_workspace(tmp_path)

    # 1. Loose .agents/mcp_config.json at root
    (tmp_path / ".agents" / "mcp_config.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")

    # 2. Malformed plugin.json inside logfire
    (tmp_path / ".agents" / "plugins" / "logfire" / "plugin.json").write_text(
        '{"name": ""}\n',
        encoding="utf-8",
    )

    # 3. Missing mcp_config.json inside github
    (tmp_path / ".agents" / "plugins" / "github" / "mcp_config.json").unlink()

    # 4. Extra plugin directory missing plugin.json and having invalid mcp_config.json
    extra_plugin = tmp_path / ".agents" / "plugins" / "broken-plugin"
    extra_plugin.mkdir(parents=True, exist_ok=True)
    (extra_plugin / "mcp_config.json").write_text("not-json", encoding="utf-8")

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl005_findings = [f for f in summary.findings if f.rule_code == "SKL005"]
    assert len(skl005_findings) >= 5
    assert any(f.file_path == ".agents/mcp_config.json" for f in skl005_findings)


def test_scenario_6_negative_plugin_hardcoded_credentials_localhost_and_readonly_skl005(
    tmp_path: Path,
) -> None:
    """Verify hardcoded tokens, localhost URLs, and non-readonly postgres config trigger SKL005."""
    _populate_compliant_workspace(tmp_path)

    # 1. Hardcoded Authorization token and localhost URL in logfire
    (tmp_path / ".agents" / "plugins" / "logfire" / "mcp_config.json").write_text(
        '{"mcpServers": {"logfire": {"url": "http://localhost:8000/mcp", '
        '"headers": {"Authorization": "Bearer sk_live_hardcoded_secret"}}}}\n',
        encoding="utf-8",
    )

    # 2. Hardcoded token in env and missing command/url in github
    (tmp_path / ".agents" / "plugins" / "github" / "mcp_config.json").write_text(
        '{"mcpServers": {"quorum-github-mcp": {"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_raw_secret"}}}}\n',
        encoding="utf-8",
    )

    # 3. Postgres plugin missing DB_READONLY="true" and using hardcoded localhost URL in args
    (tmp_path / ".agents" / "plugins" / "postgres" / "mcp_config.json").write_text(
        '{"mcpServers": {"quorum-postgres-mcp": {"command": "npx", '
        '"args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://127.0.0.1:5432/db"], '
        '"env": {"DB_READONLY": "false"}}}}\n',
        encoding="utf-8",
    )

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl005_findings = [f for f in summary.findings if f.rule_code == "SKL005"]
    assert len(skl005_findings) >= 5


def test_discover_canonical_ki_artifacts_positive_and_fallback(tmp_path: Path) -> None:
    """Verify discover_canonical_ki_artifacts resolves ki_*.md files or falls back when missing/empty."""
    missing_dir = tmp_path / "does_not_exist"
    assert discover_canonical_ki_artifacts(missing_dir) == DEFAULT_CANONICAL_KI_ARTIFACTS

    empty_dir = tmp_path / "empty_knowledge"
    empty_dir.mkdir(parents=True)
    assert discover_canonical_ki_artifacts(empty_dir) == DEFAULT_CANONICAL_KI_ARTIFACTS

    custom_dir = tmp_path / "custom_knowledge" / "sub" / "artifacts"
    custom_dir.mkdir(parents=True)
    (custom_dir / "ki_custom_one.md").write_text("# Custom 1\n", encoding="utf-8")
    (custom_dir / "ki_custom_two.md").write_text("# Custom 2\n", encoding="utf-8")
    discovered = discover_canonical_ki_artifacts(tmp_path / "custom_knowledge")
    assert discovered == frozenset({"ki_custom_one.md", "ki_custom_two.md"})
    assert "ki_name.md" in PLACEHOLDER_KI_TOKENS


def test_scenario_7_negative_phantom_ki_missing_script_and_omitted_hardening_ki_skl003(
    tmp_path: Path,
) -> None:
    """Verify phantom ki_*.md in skills/rules, missing scripts/*.py, and omitted canonical KIs trigger SKL003."""
    _populate_compliant_workspace(tmp_path)

    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "existing_script.py").write_text("# Existing\n", encoding="utf-8")

    # 1. Skill referencing a phantom deleted KI and a non-existent script
    sdui_skill_md = tmp_path / ".agents" / "skills" / "sdui-parity-sync" / "SKILL.md"
    sdui_skill_md.write_text(
        "---\nname: sdui-parity-sync\ndescription: SDUI parity\n---\n"
        "See [template](./resources/template.md), ki_phantom_deleted_artifact.md, "
        "scripts/existing_script.py, and scripts/missing_script.py.\n",
        encoding="utf-8",
    )

    # 2. Rule file referencing a phantom deleted KI
    core_rule_md = tmp_path / ".agents" / "rules" / "00-antigravity-core.md"
    core_rule_md.write_text(
        "---\ntrigger: always_on\n---\n# Core Rules\nReferences @[ki_sdui_matrix_synthesis.md] and ki_name.md.\n",
        encoding="utf-8",
    )

    # 3. Hardening skills omitting ki_zero_permissive_typing.md and a rule file
    partial_kis = " ".join(sorted(CANONICAL_KI_ARTIFACTS - {"ki_zero_permissive_typing.md"}))
    for h_skill in ("tier2-hardening-backend", "tier2-hardening-frontend"):
        (tmp_path / ".agents" / "skills" / h_skill / "SKILL.md").write_text(
            f"---\nname: {h_skill}\ndescription: Hardening {h_skill}\n---\n"
            f"See [template](./resources/template.md), @[.agents/rules/00-antigravity-core.md], and {partial_kis}.\n",
            encoding="utf-8",
        )

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl003_findings = [f for f in summary.findings if f.rule_code == "SKL003"]
    messages = [f.message for f in skl003_findings]
    assert any("ki_phantom_deleted_artifact.md" in m for m in messages)
    assert any("scripts/missing_script.py" in m for m in messages)
    assert any("ki_sdui_matrix_synthesis.md" in m for m in messages)
    assert any("ki_zero_permissive_typing.md" in m for m in messages)
    assert any("05_llm_architecture.md" in m for m in messages)


def test_scenario_8_negative_missing_schema_blast_radius_and_factory_mandate_skl003(
    tmp_path: Path,
) -> None:
    """Verify omitting schema_blast_radius_and_factory_mandate or model_factories.py in planning/execution skills emits SKL003."""
    _populate_compliant_workspace(tmp_path)

    create_plan_md = tmp_path / ".agents" / "skills" / "tier0-create-plan" / "SKILL.md"
    create_plan_md.write_text(
        "---\nname: tier0-create-plan\ndescription: Create plan\n---\n"
        "See [template](./resources/template.md) and @[.agents/rules/00-antigravity-core.md].\n",
        encoding="utf-8",
    )

    execute_md = tmp_path / ".agents" / "skills" / "tier2-execute" / "SKILL.md"
    execute_md.write_text(
        "---\nname: tier2-execute\ndescription: Execute plan\n---\n"
        "See [template](./resources/template.md), schema_blast_radius_and_factory_mandate, "
        "and pairwise_rule_and_guardrail_orthogonality_mandate.\n",
        encoding="utf-8",
    )

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl003_findings = [f for f in summary.findings if f.rule_code == "SKL003"]
    assert any(
        f.file_path == ".agents/skills/tier0-create-plan/SKILL.md"
        and "schema_blast_radius_and_factory_mandate" in f.message
        for f in skl003_findings
    )
    assert any(
        f.file_path == ".agents/skills/tier0-create-plan/SKILL.md"
        and "pairwise_rule_and_guardrail_orthogonality_mandate" in f.message
        for f in skl003_findings
    )
    assert any(
        f.file_path == ".agents/skills/tier2-execute/SKILL.md" and "model_factories.py" in f.message
        for f in skl003_findings
    )


def test_scenario_9_negative_pairwise_rule_conflict_detection_skl003(
    tmp_path: Path,
) -> None:
    """Verify verify_candidate_rule_against_all and run_audit emit SKL003 when two rules contradict each other."""
    _populate_compliant_workspace(tmp_path)

    core_rule_md = tmp_path / ".agents" / "rules" / "00-antigravity-core.md"
    core_rule_md.write_text(
        "---\ntrigger: always_on\n---\n"
        '<rule_block id="legacy_helper_ban">\n'
        "  <banned_pattern>NEVER use `legacy_helper()` in services.</banned_pattern>\n"
        "  <mandatory_pattern>ALWAYS use `modern_helper()` in services.</mandatory_pattern>\n"
        "</rule_block>\n",
        encoding="utf-8",
    )

    backend_rule_md = tmp_path / ".agents" / "rules" / "01-python-backend.md"
    backend_rule_md.write_text(
        "# Backend Rules\n"
        '<rule_block id="contradictory_new_rule">\n'
        "  <mandatory_pattern>ALWAYS use `legacy_helper()` for service calls.</mandatory_pattern>\n"
        "</rule_block>\n",
        encoding="utf-8",
    )

    # Also ensure hardening skill references 01-python-backend.md so hardening coverage stays satisfied
    ki_refs_str = " ".join(sorted(CANONICAL_KI_ARTIFACTS))
    (tmp_path / ".agents" / "skills" / "tier2-hardening-backend" / "SKILL.md").write_text(
        "---\nname: tier2-hardening-backend\ndescription: Backend hardening\n---\n"
        f"Covers {ki_refs_str}, @[.agents/rules/00-antigravity-core.md], "
        "@[.agents/rules/01-python-backend.md], and @[.agents/rules/05_llm_architecture.md].\n",
        encoding="utf-8",
    )

    parsed_core = extract_rule_blocks_from_text(
        core_rule_md.read_text(encoding="utf-8"), ".agents/rules/00-antigravity-core.md"
    )
    parsed_new = extract_rule_blocks_from_text(
        backend_rule_md.read_text(encoding="utf-8"), ".agents/rules/01-python-backend.md"
    )
    assert len(parsed_core) == 1
    assert len(parsed_new) == 1
    assert isinstance(parsed_new[0], RuleBlockSpecDTO)

    direct_findings = verify_candidate_rule_against_all(parsed_new[0], parsed_core)
    assert len(direct_findings) == 1
    assert direct_findings[0].rule_code == "SKL003"
    assert "legacy_helper()" in direct_findings[0].message
    assert "contradictory_new_rule" in direct_findings[0].message
    assert "legacy_helper_ban" in direct_findings[0].message

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()
    assert any(
        f.rule_code == "SKL003" and "legacy_helper()" in f.message and "contradictory_new_rule" in f.message
        for f in summary.findings
    )


def test_scenario_10_static_checker_orthogonality_witness_verification_skl003() -> None:
    """Verify verify_static_checker_orthogonality passes on canonical witnesses and emits SKL003 on conflicting syntax."""
    assert verify_static_checker_orthogonality(CANONICAL_RULE_SYNTAX_WITNESSES) == []

    conflicting_witness = {
        "qgr020_vs_dict_eradication_conflict": (
            '"""Conflicting witness module."""\n\n'
            "from typing import Annotated\n"
            "from pydantic import BaseModel, ConfigDict, Field\n\n\n"
            "class ConflictingWitnessDTO(BaseModel):\n"
            '    """Witness with duplicate Field() on Annotated default_factory."""\n\n'
            '    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)\n\n'
            '    items: Annotated[list[str], Field(default_factory=list, description="Items")] = Field(default_factory=list)\n'
        )
    }
    findings = verify_static_checker_orthogonality(conflicting_witness)
    assert len(findings) >= 1
    assert all(f.rule_code == "SKL003" for f in findings)
    assert any("qgr020_vs_dict_eradication_conflict" in f.message for f in findings)
