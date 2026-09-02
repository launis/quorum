"""Theory-Grounding Calibration & Micro-Slice Isolation Engine.

Provides isolated slice export, empirical contamination detection, coherence auditing,
adversarial Theory Opponent Card generation, atomic seed patching, and theory compendiums.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any

from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.enums import PromptBlockCategory
from scripts.audit_database_atoms import run_full_database_audit
from scripts.sanitize_seed_vault import atomic_save_seed_data, create_vault_backup

logger = logging.getLogger(__name__)

__all__ = [
    "append_matrix_theory_explanation",
    "apply_matrix_slice",
    "audit_atom_coherence",
    "detect_empirical_contamination",
    "export_matrix_slice",
    "generate_theory_opponent_card",
    "load_matrix_by_id",
]

FINNISH_PATTERN = re.compile(r"\b(etätyö|kokeilu|organisaatio|muutos|tiimi|johtam|työntekij|viestint)\b|[äöåÄÖÅ]", re.I)
EMPIRICAL_METRIC_PATTERN = re.compile(r"\b\d+%\b|\b(N=\d+|p<0\.\d+|kysely|haastattelu|tilasto)\b", re.I)
COMPARATIVE_RE = re.compile(r"\b(compar|relat|synthe|integrat|weigh|contrast|trade-?off)\b", re.I)


def load_matrix_by_id(matrix_id: str, seed_path: Path = Path("backend_v2/seed/seed_data.json")) -> MatrixPromptBlock:
    """Loads and validates a MatrixPromptBlock from seed_data.json."""
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    blocks: list[dict[str, Any]] = data["prompt_blocks"] if "prompt_blocks" in data else []
    for b in blocks:
        if b.get("id") == matrix_id and b.get("category_id") == PromptBlockCategory.MATRIX.value:
            return MatrixPromptBlock.model_validate(b)
    raise ValueError(f"Matrix with ID '{matrix_id}' not found in {seed_path} or is not category 'matrix'")


def detect_empirical_contamination(matrix: MatrixPromptBlock) -> list[dict[str, str]]:
    """Detects empirical run artifacts and Finnish case data in contrastive examples."""
    findings: list[dict[str, str]] = []

    def add_finding(tid: str, field: str, val: str) -> None:
        findings.append({"tda_id": tid, "field": field, "snippet": val[:80], "reason": "Empirical text"})

    for s in matrix.scales:
        for c in s.claims:
            for tda in c.tda_assertions:
                for f_name, val in [
                    ("extraction_rule", tda.extraction_rule or ""),
                    ("contrastive_example", tda.contrastive_example or ""),
                    ("concept_description", tda.concept_description),
                ]:
                    if FINNISH_PATTERN.search(val) or EMPIRICAL_METRIC_PATTERN.search(val):
                        add_finding(tda.tda_id, f_name, val)
    return findings


def audit_atom_coherence(matrix: MatrixPromptBlock) -> list[dict[str, str]]:
    """Audits cross-field coherence and steering control integrity across matrix atoms."""
    issues: list[dict[str, str]] = []

    def add_issue(tda_id: str, issue: str, desc: str) -> None:
        issues.append({"tda_id": tda_id, "issue": issue, "description": desc})

    for s in matrix.scales:
        for c in s.claims:
            for tda in c.tda_assertions:
                tid = tda.tda_id
                if tda.inverse_evidence and tda.aggregation_mode == "ALL_MUST_COMPLY":
                    add_issue(tid, "INVERSION_PARADOX", "inverse_evidence=True requires aggregation_mode='EXISTS'")
                if tda.enforce_pre_flight and len(tda.syntactic_anchors) == 0:
                    add_issue(tid, "PREFLIGHT_CHOKEPOINT", "enforce_pre_flight=True requires at least one anchor")
                rule_text = f"{tda.extraction_rule or ''} {tda.concept_description}"
                if tda.bounding_box_scope == "sentence" and COMPARATIVE_RE.search(rule_text):
                    add_issue(tid, "SCOPE_RULE_MISMATCH", "Relational rule requires paragraph scope")
                if tda.contrastive_example is not None:
                    ex = tda.contrastive_example
                    if "ACCEPTABLE:" not in ex or "UNACCEPTABLE:" not in ex or FINNISH_PATTERN.search(ex):
                        add_issue(tid, "EXEMPLAR_DEFECT", "contrastive_example must contain ACCEPTABLE/UNACCEPTABLE")
                if not tda.acceptance_criteria and tda.extraction_rule and len(tda.extraction_rule) > 80:
                    add_issue(tid, "CRITERIA_RULE_DISCORDANCE", "Formal extraction rule lacks acceptance_criteria")
    return issues


def export_matrix_slice(
    matrix_id: str, output_path: Path | None = None, seed_path: Path = Path("backend_v2/seed/seed_data.json")
) -> Path:
    """Exports an isolated, validated single-matrix slice JSON."""
    mat = load_matrix_by_id(matrix_id, seed_path)
    dest = output_path or Path("tmp/slices") / f"{matrix_id}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(mat.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return dest


def generate_theory_opponent_card(matrix_id: str, seed_path: Path = Path("backend_v2/seed/seed_data.json")) -> str:
    """Generates a structured Theory Opponent Card prompt for adversarial review."""
    mat = load_matrix_by_id(matrix_id, seed_path)
    theory = (
        f"Citation: {mat.theory_grounding.citation_reference}\nURL: {mat.theory_grounding.source_url}"
        if mat.theory_grounding
        else "[THEORY GROUNDING ABSENT - REQUIRED TO IDENTIFY ACADEMIC CANON]"
    )
    contam, coherence = detect_empirical_contamination(mat), audit_atom_coherence(mat)
    lines = [
        "<evaluator_mandate>\n"
        "You are an Adversarial Theory Opponent and Senior Epistemologist. Calibrate this matrix.\n"
        "</evaluator_mandate>",
        f"<theory_context>\nMatrix: {mat.label.resolve('en')}\n{theory}\n</theory_context>",
        f"<matrix_metadata>\nID: {mat.id}\n"
        f"allow_contextual_override={mat.allow_contextual_override}\n</matrix_metadata>",
        "<bars_scale_specifications>",
    ]
    for s in mat.scales:
        lines.append(f"## Level {s.score}: {s.name.resolve('en') if s.name else f'Level {s.score}'}")
        for c in s.claims:
            lines.append(f"- Claim: {c.label.resolve('en')}")
            for tda in c.tda_assertions:
                lines.append(
                    f"  - Atom [{tda.tda_id}]: Concept='{tda.concept_description}' Rule='{tda.extraction_rule}' "
                    f"Aggregation={tda.aggregation_mode} Inverse={tda.inverse_evidence} Scope={tda.bounding_box_scope}"
                )
    lines.append("</bars_scale_specifications>")
    audit_items = contam + coherence
    formatted_items = []
    for i in audit_items:
        k = i["field"] if "field" in i else i["issue"]
        v = i["snippet"] if "snippet" in i else i["description"]
        formatted_items.append(f"- {i['tda_id']} ({k}): {v}")
    audit_body = "\n".join(formatted_items) if formatted_items else "No defects detected."
    lines.append(
        f"<theory_calibration_audit>\n{audit_body}\n"
        "Mandate: Purge empirical run text and resolve all incoherencies into pure domain-agnostic English "
        "theoretical exemplars.\n</theory_calibration_audit>"
    )
    lines.append(
        "<control_theory_grounding>\n"
        "Epistemic Ontology:\n- concept_description: Theoretical construct\n- anchor_target: Saliency token\n"
        "- bounding_box_scope: Text window (sentence vs paragraph)\n"
        "- extraction_rule: Necessary-and-sufficient truth condition\n"
        "- acceptance_criteria: Deductive verification sequence\n- contrastive_example: Discriminative boundary\n\n"
        "Semantics of aggregation_mode:\n"
        "- ALL_MUST_COMPLY: Universal structural invariant across every analyzed chunk. "
        "NEVER pair with inverse_evidence.\n"
        "- EXISTS: Demonstrated competence or Error Radar anomaly.\n"
        "Requirement: Ground every steering control in cited theoretical literature.\n</control_theory_grounding>"
    )
    lines.append(
        "<theory_transformation_protocol>\n"
        "Transform all 6 fields to satisfy the Six-Point Isomorphic Chain derived directly from the citation.\n"
        "</theory_transformation_protocol>"
    )
    return "\n\n".join(lines)


def apply_matrix_slice(
    slice_path: Path, seed_path: Path = Path("backend_v2/seed/seed_data.json"), dry_run: bool = False
) -> None:
    """Atomically patches a validated matrix slice into seed_data.json with pre-flight audit and rollback."""
    slice_mat = MatrixPromptBlock.model_validate_json(slice_path.read_text(encoding="utf-8"))
    if slice_mat.category_id != PromptBlockCategory.MATRIX:
        raise ValueError(f"Slice '{slice_path}' category is not matrix")

    fatal_coherence = [
        i for i in audit_atom_coherence(slice_mat) if i["issue"] in ("INVERSION_PARADOX", "PREFLIGHT_CHOKEPOINT")
    ]
    if fatal_coherence:
        raise ValueError(f"Slice '{slice_mat.id}' contains fatal field incoherence: {fatal_coherence}")

    data: dict[str, Any] = json.loads(seed_path.read_text(encoding="utf-8"))
    blocks: list[dict[str, Any]] = data["prompt_blocks"] if "prompt_blocks" in data else []
    target_idx: int | None = None
    for i, b in enumerate(blocks):
        if b.get("id") == slice_mat.id and b.get("category_id") == PromptBlockCategory.MATRIX.value:
            target_idx = i
            break
    if target_idx is None:
        raise ValueError(f"Matrix '{slice_mat.id}' not found in {seed_path}")

    if not dry_run:
        backup_file = create_vault_backup(seed_path)
        blocks[target_idx] = slice_mat.model_dump(mode="json", exclude_none=True)
        atomic_save_seed_data(data, seed_path)
        report = run_full_database_audit(seed_path)
        if not report.all_passed:
            shutil.copyfile(backup_file, seed_path)
            raise RuntimeError(
                f"Pre-flight audit failed for slice '{slice_mat.id}'; restored backup from {backup_file}"
            )
        state_file = Path("tmp/matrix_hardening_state.json")
        if state_file.exists():
            from scripts.matrix_hardening_loop import mark_done

            mark_done(slice_mat.id)


def append_matrix_theory_explanation(
    matrix_id: str,
    compendium_path: Path = Path("docs/architecture/08_matrix_explanations.md"),
    seed_path: Path = Path("backend_v2/seed/seed_data.json"),
) -> None:
    """Appends or updates a 2-paragraph English theory explanation for a hardened matrix in the compendium."""
    mat = load_matrix_by_id(matrix_id, seed_path)
    title = f"### {mat.label.resolve('en')}"
    theory_name = mat.theory_grounding.citation_reference if mat.theory_grounding else "formal domain heuristics"
    p1 = (
        f"The {mat.label.resolve('en')} evaluation matrix is mathematically grounded in {theory_name}. "
        "It provides a structured Behaviorally Anchored Rating Scale (BARS) spanning Levels 1 to 5, "
        "transitioning from ungrounded claims and subjective rhetoric to rigorous, evidence-backed propositions. "
        "By eliminating cognitive biases and rhetorical ornamentation, it enforces objective, verifiable standards "
        "across analytical reasoning tasks."
    )
    p2 = (
        "Operationally, the matrix controls evaluation precision through targeted parameters including "
        f"contextual override permissions (allow_contextual_override={mat.allow_contextual_override}) "
        "and calibrated evidence search distance across bounding boxes. Steering mechanisms enforce strict "
        "distinction between universal structural invariants requiring all chunks to comply simultaneously "
        "and specialized error radars operating under existential detection to prevent evaluation distortion."
    )
    section_text = f"{title}\n\n{p1}\n\n{p2}\n"
    compendium_path.parent.mkdir(parents=True, exist_ok=True)
    if not compendium_path.exists():
        header = (
            "# Matrix Theory Explanations Compendium\n\n"
            "Architectural reference documenting theoretical grounding and steering controls "
            "for all Quorum matrices.\n\n"
        )
        compendium_path.write_text(header + section_text, encoding="utf-8")
        return

    content = compendium_path.read_text(encoding="utf-8")
    if title in content:
        pattern = re.compile(rf"{re.escape(title)}\n\n.*?(?=\n### |\Z)", re.DOTALL)
        compendium_path.write_text(pattern.sub(section_text, content), encoding="utf-8")
        return
    compendium_path.write_text(content.rstrip() + "\n\n" + section_text, encoding="utf-8")
