"""ISTQB Unit Test Suite for scripts/audit_skills_architecture.py.

Verifies SKL001 (legacy workflow remnant), SKL002 (missing/mismatched skill frontmatter),
SKL003 (broken relative skill resource/reference links), and SKL004 (always_on rule
byte budget boundary value analysis).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.audit_skills_architecture import (
    MAX_ALWAYS_ON_BYTES,
    MAX_SINGLE_RULE_FILE_BYTES,
    REQUIRED_QUORUM_SKILLS,
    SkillsArchitectureAuditor,
    SkillsAuditFindingDTO,
    SkillsAuditSummaryDTO,
    main,
)


def _populate_compliant_workspace(root: Path) -> None:
    """Create a compliant workspace tree with all 27 required skills and valid rules.

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
    for skill_name in REQUIRED_QUORUM_SKILLS:
        s_dir = skills_dir / skill_name
        res_dir = s_dir / "resources"
        res_dir.mkdir(parents=True, exist_ok=True)
        (res_dir / "template.md").write_text("# Template\n", encoding="utf-8")
        (s_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Canonical skill {skill_name}\n---\n"
            f"See [template](./resources/template.md) and @[.agents/rules/00-antigravity-core.md].\n",
            encoding="utf-8",
        )


def test_scenario_1_happy_path_valid_skills_and_rule_budget(tmp_path: Path) -> None:
    """Verify compliant skills topology and always_on budget produce zero findings."""
    _populate_compliant_workspace(tmp_path)
    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    assert isinstance(summary, SkillsAuditSummaryDTO)
    assert summary.findings == []
    assert summary.verified_skills_count == len(REQUIRED_QUORUM_SKILLS)
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
    oversized_single = "a" * (MAX_SINGLE_RULE_FILE_BYTES + 1)
    (rules_dir / "00-antigravity-core.md").write_text(oversized_single, encoding="utf-8")

    # Add two more always_on files so aggregate exceeds MAX_ALWAYS_ON_BYTES (72,000 bytes)
    (rules_dir / "extra_always_on_1.md").write_text("b" * 24_000, encoding="utf-8")
    (rules_dir / "extra_always_on_2.md").write_text("c" * 24_000, encoding="utf-8")

    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()

    skl004_findings = [f for f in summary.findings if f.rule_code == "SKL004"]
    assert len(skl004_findings) == 2
    assert summary.always_on_total_bytes > MAX_ALWAYS_ON_BYTES


def test_missing_skills_directory_and_dto_strictness(tmp_path: Path) -> None:
    """Verify missing .agents/skills directory emits SKL002 and DTOs reject invalid fields."""
    auditor = SkillsArchitectureAuditor(repo_root=tmp_path)
    summary = auditor.run_audit()
    assert any(f.rule_code == "SKL002" and f.file_path == ".agents/skills" for f in summary.findings)

    with pytest.raises(ValidationError):
        SkillsAuditFindingDTO(
            rule_code="INVALID",
            file_path="AGENTS.md",
            message="Invalid code",
            remediation="Fix code",
        )
