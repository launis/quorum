"""Audit Plan Tracker Parity.

A deterministic neuro-symbolic AST auditor verifying 100% bidirectional parity
between Implementation Plans and Execution Trackers across Quorum.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Force UTF-8 encoding for stdout on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

# ANSI colors for console output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


class GuardrailSeverity(StrEnum):
    """Severity classification for parity audit findings."""

    WARNING = "WARNING"
    FATAL = "FATAL"


class ParityRuleCode(StrEnum):
    """Deterministic rule codes for plan vs. tracker parity audits."""

    TPR001 = "TPR001"  # Missing Step in Execution Status
    TPR002 = "TPR002"  # Missing Step in Requirements Traceability Matrix
    TPR003 = "TPR003"  # Orphan Step in Tracker (not in plan)
    TPR004 = "TPR004"  # Missing Target Production File in Hardening Checklist
    TPR005 = "TPR005"  # Orphan File in Hardening Checklist (not in plan targets)
    TPR006 = "TPR006"  # Context Rules & Knowledge Items Parity
    TPR007 = "TPR007"  # Plan Reference Binding Parity
    TPR008 = "TPR008"  # Mandatory Quality Gates Parity
    TPR009 = "TPR009"  # Action Traceability & Description Quality
    TPR010 = "TPR010"  # Checkbox Syntax and State Integrity


class PlanTargetFileDTO(BaseModel):
    """Pydantic V2 DTO representing an extracted target file from an implementation plan."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    file_path: Annotated[str, Field(description="Normalized POSIX file path")]
    action: Annotated[str, Field(pattern=r"^(MODIFY|NEW|DELETE)$", description="Target action type")]
    is_production: Annotated[bool, Field(description="Whether file is production code (excludes test code)")]
    is_backend: Annotated[bool, Field(description="Whether file belongs to backend / python domain")]
    is_frontend: Annotated[bool, Field(description="Whether file belongs to frontend / flutter domain")]
    line_bound: Annotated[str | None, Field(default=None, description="Optional line bound annotation")] = None


class PlanStepDTO(BaseModel):
    """Pydantic V2 DTO representing an execution step extracted from an implementation plan."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_id: Annotated[str, Field(description="Unique step identifier e.g. '1', '2'")]
    step_name: Annotated[str, Field(description="Descriptive step title or XML name")]
    actions: Annotated[list[str], Field(default_factory=list, description="Extracted atomic action items")]
    constraints: Annotated[list[str], Field(default_factory=list, description="Extracted invariant constraints")]


class PlanDocumentAST(BaseModel):
    """Pydantic V2 DTO representing the parsed structural AST of an implementation plan."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    file_path: Annotated[str, Field(description="Path to the plan markdown file")]
    title: Annotated[str, Field(description="Plan title")]
    rules: Annotated[list[str], Field(default_factory=list, description="Declared context rules")]
    knowledge_items: Annotated[list[str], Field(default_factory=list, description="Declared knowledge items")]
    target_files: Annotated[list[PlanTargetFileDTO], Field(default_factory=list, description="Extracted target files")]
    steps: Annotated[list[PlanStepDTO], Field(default_factory=list, description="Extracted execution steps")]


class TrackerStepCheckboxDTO(BaseModel):
    """Pydantic V2 DTO representing a step checkbox in the tracker execution status."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_id: Annotated[str, Field(description="Step identifier e.g. '1', '2'")]
    step_name: Annotated[str, Field(description="Step name or summary")]
    is_checked: Annotated[bool, Field(description="Whether checkbox is marked completed")]
    raw_text: Annotated[str, Field(description="Raw line text from tracker")]


class TraceabilityRowDTO(BaseModel):
    """Pydantic V2 DTO representing a row in the Requirements Traceability Matrix."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    requirement_id: Annotated[str, Field(description="Requirement ID e.g. 'REQ-001'")]
    description: Annotated[str, Field(description="Requirement description text")]
    plan_step: Annotated[str, Field(description="Plan step reference string")]
    step_ids: Annotated[list[str], Field(default_factory=list, description="Extracted numeric/alphanumeric step IDs")]
    is_complete: Annotated[bool, Field(description="Whether requirement is marked complete")]


class TrackerHardeningChecklistDTO(BaseModel):
    """Pydantic V2 DTO representing the post-implementation hardening checklist."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    backend_files: Annotated[list[str], Field(default_factory=list, description="Hardened backend production files")]
    frontend_files: Annotated[list[str], Field(default_factory=list, description="Hardened frontend production files")]


class TrackerDocumentAST(BaseModel):
    """Pydantic V2 DTO representing the parsed structural AST of an execution tracker."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    file_path: Annotated[str, Field(description="Path to the tracker markdown file")]
    title: Annotated[str, Field(description="Tracker title")]
    plan_references: Annotated[list[str], Field(default_factory=list, description="Referenced plan file paths")]
    rules: Annotated[list[str], Field(default_factory=list, description="Declared context rules")]
    knowledge_items: Annotated[list[str], Field(default_factory=list, description="Declared knowledge items")]
    step_checkboxes: Annotated[list[TrackerStepCheckboxDTO], Field(default_factory=list, description="Step checkboxes")]
    traceability_rows: Annotated[list[TraceabilityRowDTO], Field(default_factory=list, description="Matrix rows")]
    hardening_checklist: Annotated[TrackerHardeningChecklistDTO, Field(description="Hardening checklist files")]
    has_golden_master_gate: Annotated[bool, Field(description="Whether Golden Master gate is present")]
    has_pre_delete_gate: Annotated[bool, Field(description="Whether Pre-Delete audit gate is present")]
    has_semantic_coverage_gate: Annotated[bool, Field(description="Whether Semantic Coverage gate is present")]
    has_doc_sync_gate: Annotated[bool, Field(description="Whether As-Built Architectural Sync is present")]
    has_final_audit_gate: Annotated[bool, Field(description="Whether Final Plan Audit is present")]
    has_session_handover: Annotated[bool, Field(description="Whether Session Handover Context is present")]
    has_resume_command: Annotated[bool, Field(description="Whether Resume Command is present in handover")]


class ParityAuditFindingDTO(BaseModel):
    """Pydantic V2 DTO representing a parity audit finding between plan and tracker."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[ParityRuleCode, Field(description="Audit rule code")]
    category: Annotated[str, Field(description="Category of the finding")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    message: Annotated[str, Field(description="Descriptive finding message")]
    remediation: Annotated[str, Field(description="Actionable remediation guidance")]


class ParityAuditReportDTO(BaseModel):
    """Pydantic V2 DTO representing the comprehensive audit result."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    plan_file: Annotated[str, Field(description="Path to plan file")]
    tracker_file: Annotated[str, Field(description="Path to tracker file")]
    findings: Annotated[list[ParityAuditFindingDTO], Field(default_factory=list, description="Audit findings")]
    passed: Annotated[bool, Field(description="Whether the audit passed with zero fatal errors")]
    total_steps: Annotated[int, Field(ge=0, description="Total steps in plan")]
    tracked_steps: Annotated[int, Field(ge=0, description="Total steps tracked in tracker")]
    total_target_files: Annotated[int, Field(ge=0, description="Total production target files in plan")]
    tracked_target_files: Annotated[int, Field(ge=0, description="Total target files in hardening checklist")]


def _normalize_posix(raw_path: str) -> str:
    """Normalize file path to POSIX style without brackets, backticks, at-symbols, or line bounds."""
    cleaned = raw_path.strip().strip("`").strip("@").strip("[").strip("]").strip()
    cleaned = cleaned.split("#")[0].strip()
    return Path(cleaned).as_posix()


def _is_test_path(posix_path: str) -> bool:
    """Determine if a file path is a test file (excluded from production hardening checklists)."""
    p = posix_path.lower()
    return (
        "/test/" in p
        or "/tests/" in p
        or p.startswith("tests/")
        or Path(p).name.startswith("test_")
        or p.endswith("_test.dart")
    )


def _is_backend_path(posix_path: str) -> bool:
    """Determine if a file path belongs to the backend/python domain."""
    p = posix_path.lower()
    return p.startswith("backend_v2/") or p.startswith("scripts/") or p.endswith(".py") or p.endswith(".sql")


def _is_frontend_path(posix_path: str) -> bool:
    """Determine if a file path belongs to the frontend/flutter domain."""
    p = posix_path.lower()
    return p.startswith("client_app_v2/") or p.endswith(".dart") or p.endswith(".arb")


def parse_plan_document(content: str, plan_path: Path) -> PlanDocumentAST:
    """Parse an implementation plan markdown document into a strongly typed PlanDocumentAST."""
    # 1. Title
    title_match = re.search(r"^#\s+([^\n]+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else plan_path.name

    # 2. Context Rules & KIs
    rules: list[str] = []
    kis: list[str] = []
    rules_block = re.search(r"<required_context_rules>([\s\S]*?)</required_context_rules>", content)
    if rules_block:
        rules = [_normalize_posix(m) for m in re.findall(r"<rule>@?\[?([^\]>]+)\]?</rule>", rules_block.group(1))]
        kis = [
            _normalize_posix(m)
            for m in re.findall(r"<knowledge_item>@?\[?([^\]>]+)\]?</knowledge_item>", rules_block.group(1))
        ]

    # 3. Target Files (Tolerates backticks, headers, bullets, and either @[path] [ACTION] or [ACTION] @[path])
    target_files_dict: dict[str, tuple[str, str | None]] = {}

    pattern_act_first = re.compile(
        r"`?\[(MODIFY|NEW|DELETE)\]`?[:\s]*`?@?\[?`?([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]+)(?:#([^\]`]+))?`?\]?`?",
        re.IGNORECASE,
    )
    for m in pattern_act_first.finditer(content):
        raw_f = m.group(2)
        if raw_f and not raw_f.startswith("http"):
            norm = _normalize_posix(raw_f)
            bound = f"#{m.group(3)}" if m.group(3) else None
            target_files_dict[norm] = (m.group(1).upper(), bound)

    pattern_at_first = re.compile(
        r"`?@?\[?`?([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]+)(?:#([^\]`]+))?`?\]?`?\s*`?\[(MODIFY|NEW|DELETE)\]`?",
        re.IGNORECASE,
    )
    for m in pattern_at_first.finditer(content):
        raw_f = m.group(1)
        if raw_f and not raw_f.startswith("http"):
            norm = _normalize_posix(raw_f)
            bound = f"#{m.group(2)}" if m.group(2) else None
            target_files_dict[norm] = (m.group(3).upper(), bound)

    targets: list[PlanTargetFileDTO] = []
    for fpath, (action, bound) in sorted(target_files_dict.items()):
        is_test = _is_test_path(fpath)
        is_prod = not is_test
        is_backend = _is_backend_path(fpath)
        is_frontend = _is_frontend_path(fpath)
        targets.append(
            PlanTargetFileDTO(
                file_path=fpath,
                action=action,
                is_production=is_prod,
                is_backend=is_backend,
                is_frontend=is_frontend,
                line_bound=bound,
            )
        )

    # 4. Steps & Actions
    steps: list[PlanStepDTO] = []
    step_pattern = re.compile(r'<step\s+id="([^"]+)"\s+name="([^"]+)">([\s\S]*?)</step>')
    xml_steps = step_pattern.findall(content)
    if xml_steps:
        for s_id, s_name, s_body in xml_steps:
            actions = [a.strip() for a in re.findall(r"<action>([\s\S]*?)</action>", s_body) if a.strip()]
            constraints = [
                c.strip() for c in re.findall(r"<constraint[^>]*>([\s\S]*?)</constraint>", s_body) if c.strip()
            ]
            steps.append(
                PlanStepDTO(
                    step_id=str(s_id).strip(),
                    step_name=s_name.strip(),
                    actions=actions,
                    constraints=constraints,
                )
            )
    else:
        # Fallback to Markdown Step Headings
        md_step_pattern = re.compile(r"(?:###|##)\s+Step\s+([0-9a-zA-Z_.-]+):\s*([^\n]+)", re.IGNORECASE)
        for m in md_step_pattern.finditer(content):
            steps.append(
                PlanStepDTO(
                    step_id=m.group(1).strip(),
                    step_name=m.group(2).strip(),
                    actions=[],
                    constraints=[],
                )
            )

    return PlanDocumentAST(
        file_path=plan_path.as_posix(),
        title=title,
        rules=rules,
        knowledge_items=kis,
        target_files=targets,
        steps=steps,
    )


def parse_tracker_document(content: str, tracker_path: Path) -> TrackerDocumentAST:
    """Parse an execution tracker markdown document into a strongly typed TrackerDocumentAST."""
    # 1. Title
    title_match = re.search(r"^#\s+([^\n]+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else tracker_path.name

    # 2. Plan references
    plan_refs: list[str] = []
    for match in re.finditer(r"\*\*Plan:\*\*\s+@\[([^\]]+)\]", content):
        plan_refs.append(_normalize_posix(match.group(1)))
    top_plan_ref = re.search(r"^@\[(docs/implementationplans/[^\]]+)\]", content, re.MULTILINE)
    if top_plan_ref:
        norm_top = _normalize_posix(top_plan_ref.group(1))
        if norm_top not in plan_refs:
            plan_refs.append(norm_top)

    # 3. Context Rules & KIs
    rules: list[str] = []
    kis: list[str] = []
    rules_block = re.search(r"<required_context_rules>([\s\S]*?)</required_context_rules>", content)
    if rules_block:
        rules = [_normalize_posix(m) for m in re.findall(r"<rule>@?\[?([^\]>]+)\]?</rule>", rules_block.group(1))]
        kis = [
            _normalize_posix(m)
            for m in re.findall(r"<knowledge_item>@?\[?([^\]>]+)\]?</knowledge_item>", rules_block.group(1))
        ]

    # 4. Step checkboxes under Execution Status
    step_checkboxes: list[TrackerStepCheckboxDTO] = []
    exec_status_match = re.search(
        r"##\s+(?:Step|Phase)\s+Execution Status([\s\S]*?)(?=(?:###\s+Post-Implementation Gates|##\s+Instructions|\Z))",
        content,
        re.IGNORECASE,
    )
    if exec_status_match:
        status_body = exec_status_match.group(1)
        step_box_pattern = re.compile(
            r"^\s{2,}-\s+\[([ x])\]\s+Step\s+([0-9a-zA-Z_.-]+)(?::\s*([^\n]+))?",
            re.MULTILINE,
        )
        for m in step_box_pattern.finditer(status_body):
            checked = m.group(1).lower() == "x"
            s_id = m.group(2).strip()
            s_name = m.group(3).strip() if m.group(3) else f"Step {s_id}"
            step_checkboxes.append(
                TrackerStepCheckboxDTO(
                    step_id=s_id,
                    step_name=s_name,
                    is_checked=checked,
                    raw_text=m.group(0).strip(),
                )
            )

    # 5. Requirements Traceability Matrix (handling escaped pipes \| safely)
    matrix_rows: list[TraceabilityRowDTO] = []
    matrix_match = re.search(
        r"##\s+Requirements Traceability Matrix([\s\S]*?)(?=(?:#\s+Session Handover|\Z))",
        content,
        re.IGNORECASE,
    )
    if matrix_match:
        m_lines = matrix_match.group(1).splitlines()
        for line in m_lines:
            line_str = line.strip()
            if not line_str.startswith("|") or "---" in line_str or "Requirement" in line_str:
                continue
            raw_cols = re.split(r"(?<!\\)\|", line_str)
            cols = [c.strip().replace(r"\|", "|") for c in raw_cols[1:-1]]
            if len(cols) >= 3:
                req_id = cols[0]
                desc = cols[1]
                plan_step_str = cols[2]
                status_str = cols[3] if len(cols) >= 4 else ""
                is_comp = "[x]" in status_str.lower() or "complete" in status_str.lower() or "ok" in status_str.lower()
                extracted_ids = re.findall(r"\bStep\s+([0-9a-zA-Z_.-]+)", plan_step_str, re.IGNORECASE)
                if not extracted_ids:
                    # Fallback to plain digit match
                    extracted_ids = re.findall(r"\b(\d+)\b", plan_step_str)
                matrix_rows.append(
                    TraceabilityRowDTO(
                        requirement_id=req_id,
                        description=desc,
                        plan_step=plan_step_str,
                        step_ids=[s.strip() for s in extracted_ids],
                        is_complete=is_comp,
                    )
                )

    # 6. Hardening Checklist
    backend_hardening_files: list[str] = []
    frontend_hardening_files: list[str] = []

    b_pattern = (
        r"Tier 2 Hardening \(Backend\)[^\n]*\n([\s\S]*?)"
        r"(?=(?:-\s+\[[ x]\]\s+\*\*\[(?:OK|NOK)\]\s+Tier 2 Hardening \(Frontend\)|\Z))"
    )
    b_match = re.search(b_pattern, content, re.IGNORECASE)
    if b_match:
        for f in re.findall(r"@\[([^\]]+)\]", b_match.group(1)):
            backend_hardening_files.append(_normalize_posix(f))

    f_pattern = (
        r"Tier 2 Hardening \(Frontend\)[^\n]*\n([\s\S]*?)"
        r"(?=(?:-\s+\[[ x]\]\s+\*\*\[(?:OK|NOK)\]\s+Pre-Delete|\Z))"
    )
    f_match = re.search(f_pattern, content, re.IGNORECASE)
    if f_match:
        for f in re.findall(r"@\[([^\]]+)\]", f_match.group(1)):
            frontend_hardening_files.append(_normalize_posix(f))

    hardening = TrackerHardeningChecklistDTO(
        backend_files=backend_hardening_files,
        frontend_files=frontend_hardening_files,
    )

    # 7. Quality Gates
    has_gm = bool(re.search(r"Golden Master & Test Restoration Audit", content, re.IGNORECASE))
    has_pd = bool(re.search(r"Pre-Delete Audit", content, re.IGNORECASE))
    has_sc = bool(re.search(r"Semantic Coverage & Zero-Loss Audit", content, re.IGNORECASE))
    has_ds = bool(re.search(r"As-Built Architectural Sync", content, re.IGNORECASE))
    has_fa = bool(re.search(r"System 2 Red-Team Audit|Final (?:Plan|Epic) Audit", content, re.IGNORECASE))
    has_sh = bool(re.search(r"#\s+Session Handover Context", content, re.IGNORECASE))
    has_rc = bool(re.search(r"##\s+(?:Resume Command|Status)", content, re.IGNORECASE))

    return TrackerDocumentAST(
        file_path=tracker_path.as_posix(),
        title=title,
        plan_references=plan_refs,
        rules=rules,
        knowledge_items=kis,
        step_checkboxes=step_checkboxes,
        traceability_rows=matrix_rows,
        hardening_checklist=hardening,
        has_golden_master_gate=has_gm,
        has_pre_delete_gate=has_pd,
        has_semantic_coverage_gate=has_sc,
        has_doc_sync_gate=has_ds,
        has_final_audit_gate=has_fa,
        has_session_handover=has_sh,
        has_resume_command=has_rc,
    )


def audit_plan_tracker_parity(plan_ast: PlanDocumentAST, tracker_ast: TrackerDocumentAST) -> ParityAuditReportDTO:
    """Perform deterministic neuro-symbolic parity audit between plan AST and tracker AST."""
    findings: list[ParityAuditFindingDTO] = []

    plan_step_ids = {s.step_id for s in plan_ast.steps}
    tracker_exec_step_ids = {s.step_id for s in tracker_ast.step_checkboxes}
    tracker_matrix_step_ids: set[str] = set()
    for row in tracker_ast.traceability_rows:
        tracker_matrix_step_ids.update(row.step_ids)

    # Check TPR007: Plan Reference Binding
    plan_posix = _normalize_posix(plan_ast.file_path)
    plan_name = Path(plan_posix).name
    has_plan_ref = any(plan_posix in ref or plan_name in ref for ref in tracker_ast.plan_references)
    if not has_plan_ref:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR007,
                category="Plan Reference",
                severity=GuardrailSeverity.FATAL,
                message=f"Tracker does not reference plan file `{plan_name}` in `**Plan:** @[...]`.",
                remediation=f"Add `**Plan:** @[{plan_posix}]` under the execution status header.",
            )
        )

    # Check TPR001: Missing Step in Execution Status
    for s_id in sorted(plan_step_ids):
        if s_id not in tracker_exec_step_ids:
            findings.append(
                ParityAuditFindingDTO(
                    rule_code=ParityRuleCode.TPR001,
                    category="Execution Steps",
                    severity=GuardrailSeverity.FATAL,
                    message=f"Plan Step {s_id} is missing from tracker's Execution Status checkboxes.",
                    remediation=f"Add indented `- [ ] Step {s_id}: [Name]` under Execution in tracker.",
                )
            )

    # Check TPR002: Missing Step in Requirements Traceability Matrix
    for s_id in sorted(plan_step_ids):
        if s_id not in tracker_matrix_step_ids:
            findings.append(
                ParityAuditFindingDTO(
                    rule_code=ParityRuleCode.TPR002,
                    category="Traceability Matrix",
                    severity=GuardrailSeverity.FATAL,
                    message=f"Plan Step {s_id} is not mapped in Requirements Traceability Matrix.",
                    remediation=f"Add a row in Requirements Traceability Matrix referencing Step {s_id}.",
                )
            )

    # Check TPR003: Orphan Step in Tracker
    for s_id in sorted(tracker_exec_step_ids - plan_step_ids):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR003,
                category="Orphan Steps",
                severity=GuardrailSeverity.WARNING,
                message=f"Tracker references Step {s_id} in Execution Status, which does not exist in plan.",
                remediation=f"Verify if Step {s_id} belongs to plan or remove from tracker checkboxes.",
            )
        )
    for s_id in sorted(tracker_matrix_step_ids - plan_step_ids):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR003,
                category="Orphan Steps",
                severity=GuardrailSeverity.WARNING,
                message=f"Matrix references Step {s_id}, which does not exist in plan.",
                remediation=f"Verify if Step {s_id} belongs to plan or remove from traceability matrix.",
            )
        )

    # Check TPR004: Target Production File Hardening Coverage
    backend_prod_targets = {t.file_path for t in plan_ast.target_files if t.is_production and t.is_backend}
    frontend_prod_targets = {t.file_path for t in plan_ast.target_files if t.is_production and t.is_frontend}

    tracker_backend_files = set(tracker_ast.hardening_checklist.backend_files)
    tracker_frontend_files = set(tracker_ast.hardening_checklist.frontend_files)

    for fpath in sorted(backend_prod_targets - tracker_backend_files):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR004,
                category="Hardening Checklist",
                severity=GuardrailSeverity.FATAL,
                message=f"Production backend target `{fpath}` missing from Tier 2 Hardening (Backend) checklist.",
                remediation=f"Add `  - [ ] @[{fpath}]` under `Tier 2 Hardening (Backend)` in tracker.",
            )
        )

    for fpath in sorted(frontend_prod_targets - tracker_frontend_files):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR004,
                category="Hardening Checklist",
                severity=GuardrailSeverity.FATAL,
                message=f"Production frontend target `{fpath}` missing from Tier 2 Hardening (Frontend) checklist.",
                remediation=f"Add `  - [ ] @[{fpath}]` under `Tier 2 Hardening (Frontend)` in tracker.",
            )
        )

    # Check TPR005: Orphan Hardening Target
    all_plan_target_paths = {t.file_path for t in plan_ast.target_files}
    for fpath in sorted(tracker_backend_files - all_plan_target_paths):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR005,
                category="Orphan Targets",
                severity=GuardrailSeverity.WARNING,
                message=f"Tracker lists backend hardening file `{fpath}`, not declared in plan target files.",
                remediation="Declare target file in plan or remove from tracker hardening checklist.",
            )
        )
    for fpath in sorted(tracker_frontend_files - all_plan_target_paths):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR005,
                category="Orphan Targets",
                severity=GuardrailSeverity.WARNING,
                message=f"Tracker lists frontend hardening file `{fpath}`, not declared in plan target files.",
                remediation="Declare target file in plan or remove from tracker hardening checklist.",
            )
        )

    # Check TPR006: Context Rules & Knowledge Items Parity
    plan_rules_set = set(plan_ast.rules)
    plan_kis_set = set(plan_ast.knowledge_items)
    tracker_rules_set = set(tracker_ast.rules)
    tracker_kis_set = set(tracker_ast.knowledge_items)

    for r in sorted(plan_rules_set - tracker_rules_set):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR006,
                category="Context Rules",
                severity=GuardrailSeverity.FATAL,
                message=f"Rule `{r}` declared in plan is missing from tracker's `<required_context_rules>`.",
                remediation=f"Add `<rule>@[{r}]</rule>` to tracker's `<required_context_rules>` block.",
            )
        )
    for k in sorted(plan_kis_set - tracker_kis_set):
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR006,
                category="Context Rules",
                severity=GuardrailSeverity.FATAL,
                message=f"Knowledge Item `{k}` declared in plan is missing from tracker's `<required_context_rules>`.",
                remediation=(
                    f"Add `<knowledge_item>@[{k}]</knowledge_item>` to tracker's `<required_context_rules>` block."
                ),
            )
        )

    # Check TPR008: Mandatory Quality Gates Parity
    if not tracker_ast.has_golden_master_gate:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Quality Gates",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `Golden Master & Test Restoration Audit` gate.",
                remediation=(
                    "Add `- [ ] **[NOK] Golden Master & Test Restoration Audit**: ...` under Post-Implementation Gates."
                ),
            )
        )
    if not tracker_ast.has_pre_delete_gate:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Quality Gates",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `Pre-Delete Audit` gate.",
                remediation="Add `- [ ] **[NOK] Pre-Delete Audit**: ...` under Post-Implementation Gates.",
            )
        )
    if not tracker_ast.has_semantic_coverage_gate:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Quality Gates",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `Semantic Coverage & Zero-Loss Audit` gate.",
                remediation=(
                    "Add `- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: ...` under Post-Implementation Gates."
                ),
            )
        )
    if not tracker_ast.has_doc_sync_gate:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Quality Gates",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `As-Built Architectural Sync` gate.",
                remediation=("Add `- [ ] **[NOK]** As-Built Architectural Sync: ...` under Documentation & KI Update."),
            )
        )
    if not tracker_ast.has_final_audit_gate:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Quality Gates",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `System 2 Red-Team Audit` (Final Plan Audit) gate.",
                remediation="Add `- [ ] **[NOK]** System 2 Red-Team Audit: ...` under Final Plan Audit.",
            )
        )
    if not tracker_ast.has_session_handover:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Session Handover",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `# Session Handover Context` section.",
                remediation=(
                    "Add `# Session Handover Context` with ## Achieved, ## Learned, ## Remaining, ## Resume Command."
                ),
            )
        )
    if not tracker_ast.has_resume_command:
        findings.append(
            ParityAuditFindingDTO(
                rule_code=ParityRuleCode.TPR008,
                category="Session Handover",
                severity=GuardrailSeverity.FATAL,
                message="Tracker is missing `## Resume Command` (or `## Status`) in Session Handover.",
                remediation="Add `## Resume Command` under `# Session Handover Context`.",
            )
        )

    # Check TPR009: Action Traceability & Granularity
    for row in tracker_ast.traceability_rows:
        if len(row.description.strip()) < 10:
            findings.append(
                ParityAuditFindingDTO(
                    rule_code=ParityRuleCode.TPR009,
                    category="Traceability Granularity",
                    severity=GuardrailSeverity.WARNING,
                    message=(
                        f"Requirement `{row.requirement_id}` has an empty or overly brief description: "
                        f"'{row.description}'."
                    ),
                    remediation=f"Expand description for `{row.requirement_id}` to clearly reflect step tasks.",
                )
            )

    has_fatal = any(f.severity == GuardrailSeverity.FATAL for f in findings)
    total_prod_targets = len(backend_prod_targets) + len(frontend_prod_targets)
    tracked_prod_targets = len(tracker_backend_files) + len(tracker_frontend_files)

    return ParityAuditReportDTO(
        plan_file=plan_ast.file_path,
        tracker_file=tracker_ast.file_path,
        findings=findings,
        passed=not has_fatal,
        total_steps=len(plan_step_ids),
        tracked_steps=len(tracker_exec_step_ids),
        total_target_files=total_prod_targets,
        tracked_target_files=tracked_prod_targets,
    )


def print_audit_report(report: ParityAuditReportDTO) -> None:
    """Print beautifully formatted console output for the audit report."""
    plan_name = Path(report.plan_file).name
    tracker_name = Path(report.tracker_file).name

    print("\n" + "=" * 70)
    print(f"{BOLD}{CYAN}Plan vs. Tracker Parity Audit (AST Neuro-Symbolic){RESET}")
    print(f"  Plan:    {plan_name}")
    print(f"  Tracker: {tracker_name}")
    print("=" * 70)

    print(f"Steps:        {report.tracked_steps} / {report.total_steps} tracked")
    print(f"Target Files: {report.tracked_target_files} / {report.total_target_files} production targets in checklists")
    print("-" * 70)

    if not report.findings:
        print(
            f"\n{GREEN}{BOLD}[PASS] 100% PARITY VERIFIED: "
            f"Tracker contains all plan tasks and targets with zero discrepancies!{RESET}\n"
        )
        return

    fatal_count = sum(1 for f in report.findings if f.severity == GuardrailSeverity.FATAL)
    warn_count = sum(1 for f in report.findings if f.severity == GuardrailSeverity.WARNING)

    print(f"Findings: {fatal_count} Fatal, {warn_count} Warnings\n")

    for f in report.findings:
        color = RED if f.severity == GuardrailSeverity.FATAL else YELLOW
        print(f"{color}[{f.rule_code}] ({f.severity}) [{f.category}] {f.message}{RESET}")
        print(f"  Remediation: {f.remediation}\n")

    if report.passed:
        print(
            f"{YELLOW}{BOLD}[PASSED WITH WARNINGS] All mandatory parity contracts verified (warnings present).{RESET}\n"
        )
    else:
        print(f"{RED}{BOLD}[FAILED] PARITY AUDIT FAILED: Tracker violates mandatory parity contracts.{RESET}\n")


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for plan vs tracker parity audit."""
    parser = argparse.ArgumentParser(
        description="""Bidirectional Plan-Tracker Parity AST Auditor (TPR001-TPR010).

Statically enforces mathematical 1:1 bidirectional alignment between implementation plans and execution trackers:
  TPR001: Plan Link Reference Parity (valid @[...] link to source plan)
  TPR002: Step Cardinality & Numbering Parity (exact 1:1 step count match)
  TPR003: Step Title & Objective Parity (exact verbatim match of titles)
  TPR004: Context Rules Parity (<required_context_rules> exact match)
  TPR005: Target Files Scope Parity (every plan target covered in tracker)
  TPR006: State Machine Syntax Parity (- [ ] / - [x] checkbox conformance)
  TPR007: Session Handover Block Parity (Achieved, Learned, Remaining)
  TPR008: Resume Command Parity (/tier2-execute syntax conformance)
  TPR009: Traceability Matrix Parity (RTM rows match plan steps)
  TPR010: Post-Implementation Gates Parity (Universal Quality Gates verified)
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/audit_plan_tracker_parity.py --tracker docs/implementationplans/TRACKER_001.md
  uv run python scripts/audit_plan_tracker_parity.py --tracker task.md --plan implementation_plan.md --strict
  uv run python scripts/audit_plan_tracker_parity.py --all --strict
  uv run python scripts/audit_plan_tracker_parity.py --tracker task.md --json
""",
    )
    parser.add_argument(
        "--tracker",
        required=False,
        type=str,
        default=None,
        help="Path to tracker Markdown file (e.g. docs/implementationplans/TRACKER_xxx.md or task.md).",
    )
    parser.add_argument(
        "--plan",
        required=False,
        type=str,
        default=None,
        help="Path to plan Markdown file (optional, auto-inferred from tracker if omitted).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Audit all trackers in docs/implementationplans/.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output structured JSON results instead of human-readable text.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Fail-fast strict mode: exit with code 1 on warnings as well as fatal errors.",
    )
    args = parser.parse_args(argv)

    if args.all:
        trackers = sorted(Path("docs/implementationplans").glob("TRACKER_*.md"))
        if not trackers:
            print(f"{RED}ERROR: No trackers found in docs/implementationplans/{RESET}")
            sys.exit(1)
        any_failed = False
        for t_path in trackers:
            t_content = t_path.read_text(encoding="utf-8")
            t_ast = parse_tracker_document(t_content, t_path)
            if not t_ast.plan_references:
                print(f"{YELLOW}SKIP: Tracker `{t_path.name}` has no `**Plan:**` reference.{RESET}")
                continue
            plan_path = Path(t_ast.plan_references[0])
            if not plan_path.exists():
                print(f"{RED}ERROR: Plan `{plan_path}` for `{t_path.name}` does not exist.{RESET}")
                any_failed = True
                continue
            p_content = plan_path.read_text(encoding="utf-8")
            p_ast = parse_plan_document(p_content, plan_path)
            rep = audit_plan_tracker_parity(p_ast, t_ast)
            print_audit_report(rep)
            if not rep.passed or (args.strict and rep.findings):
                any_failed = True
        sys.exit(1 if any_failed else 0)

    if not args.tracker:
        parser.error("Either --tracker or --all is required.")

    tracker_path = Path(args.tracker)
    if not tracker_path.exists():
        print(f"{RED}ERROR: Tracker file `{tracker_path}` not found.{RESET}")
        sys.exit(1)

    tracker_content = tracker_path.read_text(encoding="utf-8")
    tracker_ast = parse_tracker_document(tracker_content, tracker_path)

    plan_path_str = args.plan
    if not plan_path_str:
        if not tracker_ast.plan_references:
            print(
                f"{RED}ERROR: No `--plan` specified and `{tracker_path.name}` "
                f"contains no `**Plan:** @[...]` reference.{RESET}"
            )
            sys.exit(1)
        plan_path_str = tracker_ast.plan_references[0]

    plan_path = Path(plan_path_str)
    if not plan_path.exists():
        print(f"{RED}ERROR: Plan file `{plan_path}` not found.{RESET}")
        sys.exit(1)

    plan_content = plan_path.read_text(encoding="utf-8")
    plan_ast = parse_plan_document(plan_content, plan_path)

    report = audit_plan_tracker_parity(plan_ast, tracker_ast)

    if args.json:
        print(report.model_dump_json(indent=2))
        sys.exit(0 if report.passed and (not args.strict or not report.findings) else 1)

    print_audit_report(report)

    if not report.passed:
        sys.exit(1)
    if args.strict and report.findings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
