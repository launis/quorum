"""Full Database Prompt & Matrix Atom Verification Engine.

Tämä skripti on Quorum-järjestelmän keskeinen Single Source of Truth (SSOT) -laadunvarmistustyökalu
tietokannan (`backend_v2/seed/seed_data.json`) prompt- ja matriisikokoelmille.

KÄYTTÖOHJEET JA TYÖNKULKU:
==========================
1. Yleinen laaduntarkastus (Kaikki kokoelmat):
   `uv run python scripts/audit_database_atoms.py --strict`
   - Tarkistaa, että kaikki prompt_blocks (matriisit), steps, workflows ja output_profiles
     ovat 100 % Pydantic V2 -yhteensopivia ilman skeemavirheitä tai tyhjiä kriteereitä.

2. Matriisien ja atomien kovennussilmukka (Matrix & Atom Hardening):
   `uv run python scripts/matrix_hardening_loop.py --status`
   - Tarkistaa atomitiheyden per taso (varoittaa, jos solussa on < 3 atomia -> Cliff-riski).
   - Tarkasta yksittäinen matriisi:
     `uv run python scripts/matrix_hardening_loop.py --inspect <matrix_id>`
   - Merkitse matriisi valmiiksi auditoiduksi:
     `uv run python scripts/matrix_hardening_loop.py --done <matrix_id>`

3. Automaattinen aukkojen kartoitus ja generointi:
   `uv run python scripts/matrix_hardening_generator.py --all-gaps`
   `uv run python scripts/matrix_hardening_generator.py --plan <matrix_id>`

4. Paikallisen tietokannan uudelleensiemennys validoinnin jälkeen:
   `uv run python backend_v2/seed/run_seed.py local`

AUDITOITAVAT KOKOELMAT:
-----------------------
1. prompt_blocks (Matriisien TDA-väitteet, persoonat, arviointisäännöt)
2. steps (LLM-suoritusvaiheet, strategiat, syötesopimukset)
3. workflows (DAG-orientoituneet työnkulut, reititykset)
4. output_profiles (Synteesiprofiilit, SDUI-lohkojen ryhmittelyt)

Strictly adheres to Zero-Reflection Mandate (no getattr/hasattr) and Pydantic V2.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import PromptBlockCategory


class AuditIssue(V2CoreBase):
    """Immutable record of a detected database validation or prompt issue.

    Attributes:
        collection: The database collection containing the issue.
        entity_id: The unique Opaque Stripe ID of the entity.
        field_path: The dot-delimited path to the problematic field.
        issue_type: Category identifier of the violation.
        message: Detailed explanation of the failure.
        severity: Severity level (e.g. 'ERROR', 'WARNING').
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    collection: str = Field(description="The database collection name.")
    entity_id: str = Field(description="Unique ID of the entity.")
    field_path: str = Field(description="Path to the affected field.")
    issue_type: str = Field(description="Type/category of the issue.")
    message: str = Field(description="Human-readable issue description.")
    severity: str = Field(default="ERROR", description="Severity level.")


class FullDatabaseAuditReport(V2CoreBase):
    """Aggregate audit report summarizing full database prompt verification.

    Attributes:
        total_matrices: Total count of inspected matrix blocks.
        total_atoms: Total count of inspected TDA assertion atoms.
        total_steps: Total count of inspected step blueprints.
        total_workflows: Total count of inspected workflow DAGs.
        total_profiles: Total count of inspected output profiles.
        issues: List of all detected AuditIssue items.
        all_passed: True if zero ERROR-severity issues exist.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    total_matrices: int = Field(description="Total matrices checked.")
    total_atoms: int = Field(description="Total TDA assertion atoms checked.")
    total_steps: int = Field(description="Total step blueprints checked.")
    total_workflows: int = Field(description="Total workflow DAGs checked.")
    total_profiles: int = Field(description="Total output profiles checked.")
    issues: list[AuditIssue] = Field(default_factory=list, description="List of issues.")
    all_passed: bool = Field(description="Whether the full audit passed cleanly.")


# Banned tokens and patterns for prompt atom inspection
BANNED_PHRASES: list[str] = [
    "BANNED SOURCES",
    "EXTRACTION CONDITION:",
    "FAIL FAST",
    "STEP 1:",
    "STEP 2:",
    "DEPRECATED",
    "ABSOLUTE MITIGATION ENFORCEMENT",
    "ABSOLUTE LEXICAL BOUNDARY",
    "ABSOLUTE LEXICAL ENFORCEMENT",
    "ABSOLUTE MITIGATION",
]

NEGATIVE_GUIDANCE_PATTERNS: list[str] = [
    "do not evaluate",
    "do not judge",
    "do not accept",
    "do not flag",
]

CHAT_HARDCODING_PATTERNS: list[str] = [
    "scan only user prompts",
    "scan only",
    "role prefixes (user: ai:)",
    "role prefixes",
    "user prompt",
    "user inputs",
    "ai output",
    "reject ai outputs",
]

CORRUPTED_GRAMMAR_PATTERNS: list[str] = [
    "in an block",
]

SCREAMING_IMPERATIVES: list[str] = [
    "CRITICAL DIRECTIVE",
    "IDENTIFY",
    "LOCATE",
    "Scan the document.",
    "Verify",
    "CHECK",
    "ABSOLUTE MITIGATION ENFORCEMENT",
    "ABSOLUTE LEXICAL BOUNDARY",
]

MECHANICAL_COUNTING_PATTERNS: list[str] = [
    "EXACTLY ZERO",
    "count is",
    "count of",
    "scan the paragraph",
]


def _contains_raw_xml(text: str) -> bool:
    """Checks whether raw XML tags or angle brackets exist in text.

    Args:
        text: The string to inspect.

    Returns:
        True if raw XML tags (<...>) or unbalanced delimiters are found.
    """
    if not text:
        return False
    return bool(re.search(r"<[a-zA-Z_][a-zA-Z0-9_\-]*.*?>", text) or ("<" in text and ">" in text))


def _check_screaming_imperatives(text: str) -> str | None:
    """Checks if text contains screaming imperative instructions.

    Args:
        text: The string to inspect.

    Returns:
        The matched imperative token if found, else None.
    """
    if not text:
        return None
    for imp in SCREAMING_IMPERATIVES:
        if imp in text:
            return imp
    return None


def audit_prompt_blocks(
    prompt_blocks: list[dict[str, Any]],
) -> tuple[list[AuditIssue], int, int]:
    """Audits the prompt_blocks collection across matrices and non-matrix blocks.

    Args:
        prompt_blocks: List of raw prompt block dictionaries.

    Returns:
        A tuple of (issues list, total_matrices count, total_atoms count).
    """
    issues: list[AuditIssue] = []
    total_matrices = 0
    total_atoms = 0

    for block in prompt_blocks:
        block_id = str(block["id"]) if "id" in block else "UNKNOWN_BLOCK"
        category_id = str(block["category_id"]) if "category_id" in block else ""

        # Check block-level ai_description
        ai_desc = block["ai_description"] if "ai_description" in block else None
        if isinstance(ai_desc, str) and _contains_raw_xml(ai_desc):
            issues.append(
                AuditIssue(
                    collection="prompt_blocks",
                    entity_id=block_id,
                    field_path="ai_description",
                    issue_type="RAW_XML",
                    message=f"Prompt block '{block_id}' contains raw XML in ai_description.",
                )
            )

        if category_id in (PromptBlockCategory.MATRIX, PromptBlockCategory.MATRIX.value):
            total_matrices += 1

            scales = block["scales"] if "scales" in block else []
            if not isinstance(scales, list):
                continue

            for scale_idx, scale in enumerate(scales):
                if not isinstance(scale, dict):
                    continue
                claims = scale["claims"] if "claims" in scale else []
                if not isinstance(claims, list):
                    continue

                for claim_idx, claim in enumerate(claims):
                    if not isinstance(claim, dict):
                        continue
                    tda_assertions = claim["tda_assertions"] if "tda_assertions" in claim else []
                    if not isinstance(tda_assertions, list):
                        continue

                    for tda_idx, assertion in enumerate(tda_assertions):
                        if not isinstance(assertion, dict):
                            continue
                        total_atoms += 1
                        tda_id = (
                            str(assertion["tda_id"])
                            if "tda_id" in assertion
                            else f"tda_s{scale_idx}_c{claim_idx}_a{tda_idx}"
                        )
                        prefix_path = f"scales[{scale_idx}].claims[{claim_idx}].tda_assertions[{tda_idx}]"

                        concept_desc = assertion["concept_description"] if "concept_description" in assertion else None
                        extraction_rule = assertion["extraction_rule"] if "extraction_rule" in assertion else None

                        # 1. Check concept_description presence and length
                        if not concept_desc or not isinstance(concept_desc, str) or len(concept_desc.strip()) < 10:
                            issues.append(
                                AuditIssue(
                                    collection="prompt_blocks",
                                    entity_id=tda_id,
                                    field_path=f"{prefix_path}.concept_description",
                                    issue_type="SHORT_CONCEPT",
                                    message=f"Atom '{tda_id}' has missing or short concept_description (min length 10).",
                                )
                            )
                        else:
                            # Check Banned Phrases in concept_description
                            for bp in BANNED_PHRASES:
                                if bp in concept_desc:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.concept_description",
                                            issue_type="BANNED_PHRASE",
                                            message=f"Atom '{tda_id}' concept_description contains banned phrase '{bp}'.",
                                        )
                                    )

                            # Check Negative Guidance in concept_description
                            concept_lower = concept_desc.lower()
                            for ng in NEGATIVE_GUIDANCE_PATTERNS:
                                if ng in concept_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.concept_description",
                                            issue_type="NEGATIVE_GUIDANCE",
                                            message=f"Atom '{tda_id}' concept_description contains negative guidance '{ng}'.",
                                        )
                                    )

                            # Check Chat Hardcoding in concept_description
                            for ch in CHAT_HARDCODING_PATTERNS:
                                if ch in concept_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.concept_description",
                                            issue_type="CHAT_HARDCODING",
                                            message=f"Atom '{tda_id}' concept_description contains chatbot hardcoding '{ch}'.",
                                        )
                                    )

                            # Check Raw XML in concept_description
                            if _contains_raw_xml(concept_desc):
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="RAW_XML",
                                        message=f"Atom '{tda_id}' concept_description contains raw XML tags.",
                                    )
                                )

                            # Check Corrupted Grammar in concept_description
                            for cg in CORRUPTED_GRAMMAR_PATTERNS:
                                if cg in concept_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.concept_description",
                                            issue_type="CORRUPTED_GRAMMAR",
                                            message=f"Atom '{tda_id}' concept_description contains corrupted fragment '{cg}'.",
                                        )
                                    )

                            # Check Screaming Imperatives in concept_description
                            imp_match = _check_screaming_imperatives(concept_desc)
                            if imp_match:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="SCREAMING_IMPERATIVE",
                                        message=f"Atom '{tda_id}' concept_description contains imperative '{imp_match}'.",
                                    )
                                )

                            # Check Bloated Concept in concept_description
                            if len(concept_desc) > 180:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="BLOATED_CONCEPT",
                                        message=f"Atom '{tda_id}' concept_description is bloated ({len(concept_desc)} chars > 180 max).",
                                    )
                                )

                            # Check Mechanical Counting in concept_description
                            for mc in MECHANICAL_COUNTING_PATTERNS:
                                if mc.lower() in concept_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.concept_description",
                                            issue_type="MECHANICAL_COUNTING",
                                            message=f"Atom '{tda_id}' concept_description contains mechanical counting pattern '{mc}'.",
                                        )
                                    )

                        # 2. Check extraction_rule presence and content
                        if (
                            not extraction_rule
                            or not isinstance(extraction_rule, str)
                            or len(extraction_rule.strip()) < 10
                        ):
                            issues.append(
                                AuditIssue(
                                    collection="prompt_blocks",
                                    entity_id=tda_id,
                                    field_path=f"{prefix_path}.extraction_rule",
                                    issue_type="EMPTY_EXTRACTION_RULE",
                                    message=f"Atom '{tda_id}' has empty or short extraction_rule (min length 10).",
                                )
                            )
                        else:
                            # Check Identical Concept and Rule
                            if concept_desc and concept_desc.strip() == extraction_rule.strip():
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}",
                                        issue_type="IDENTICAL_CONCEPT_AND_RULE",
                                        message=f"Atom '{tda_id}' has identical concept_description and extraction_rule.",
                                    )
                                )

                            # Check Banned Phrases in extraction_rule
                            for bp in BANNED_PHRASES:
                                if bp in extraction_rule:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.extraction_rule",
                                            issue_type="BANNED_PHRASE",
                                            message=f"Atom '{tda_id}' extraction_rule contains banned phrase '{bp}'.",
                                        )
                                    )

                            # Check Chat Hardcoding in extraction_rule
                            rule_lower = extraction_rule.lower()
                            for ch in CHAT_HARDCODING_PATTERNS:
                                if ch in rule_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.extraction_rule",
                                            issue_type="CHAT_HARDCODING",
                                            message=f"Atom '{tda_id}' extraction_rule contains chatbot hardcoding '{ch}'.",
                                        )
                                    )

                            # Check Mechanical Counting in extraction_rule
                            for mc in MECHANICAL_COUNTING_PATTERNS:
                                if mc.lower() in rule_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.extraction_rule",
                                            issue_type="MECHANICAL_COUNTING",
                                            message=f"Atom '{tda_id}' extraction_rule contains mechanical counting pattern '{mc}'.",
                                        )
                                    )

                            # Check Raw XML in extraction_rule
                            if _contains_raw_xml(extraction_rule):
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.extraction_rule",
                                        issue_type="RAW_XML",
                                        message=f"Atom '{tda_id}' extraction_rule contains raw XML tags.",
                                    )
                                )

                            # Check Corrupted Grammar in extraction_rule
                            for cg in CORRUPTED_GRAMMAR_PATTERNS:
                                if cg in rule_lower:
                                    issues.append(
                                        AuditIssue(
                                            collection="prompt_blocks",
                                            entity_id=tda_id,
                                            field_path=f"{prefix_path}.extraction_rule",
                                            issue_type="CORRUPTED_GRAMMAR",
                                            message=f"Atom '{tda_id}' extraction_rule contains corrupted fragment '{cg}'.",
                                        )
                                    )

        else:
            # Non-matrix blocks inspection
            for field_name in ["role_enforcement", "instruction_text", "protocol_instructions"]:
                if field_name in block:
                    val = block[field_name]
                    if isinstance(val, str) and _contains_raw_xml(val):
                        issues.append(
                            AuditIssue(
                                collection="prompt_blocks",
                                entity_id=block_id,
                                field_path=field_name,
                                issue_type="RAW_XML",
                                message=f"Prompt block '{block_id}' contains raw XML in '{field_name}'.",
                            )
                        )

    return issues, total_matrices, total_atoms


def audit_steps(
    steps: list[dict[str, Any]],
    prompt_block_ids: set[str],
) -> tuple[list[AuditIssue], int]:
    """Audits the steps collection for referential integrity and blueprint schemas.

    Args:
        steps: List of raw step dictionaries.
        prompt_block_ids: Set of valid prompt_block IDs.

    Returns:
        A tuple of (issues list, total_steps count).
    """
    issues: list[AuditIssue] = []
    total_steps = len(steps)

    for step in steps:
        step_id = str(step["id"]) if "id" in step else "UNKNOWN_STEP"
        step_type = str(step["type"]) if "type" in step else ""

        if step_type == "llm":
            # 1. Model Strategy Check
            model_strategy = step["model_strategy"] if "model_strategy" in step else None
            if not model_strategy or not isinstance(model_strategy, str):
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="model_strategy",
                        issue_type="MISSING_MODEL_STRATEGY",
                        message=f"LLM step '{step_id}' lacks explicit model_strategy.",
                    )
                )

            # 2. Criteria Block IDs Check
            criteria_block_ids = step["criteria_block_ids"] if "criteria_block_ids" in step else []
            if not isinstance(criteria_block_ids, list) or len(criteria_block_ids) == 0:
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="criteria_block_ids",
                        issue_type="EMPTY_CRITERIA_BLOCKS",
                        message=f"LLM step '{step_id}' defines zero criteria_block_ids.",
                    )
                )
            else:
                for c_idx, c_id in enumerate(criteria_block_ids):
                    if str(c_id) not in prompt_block_ids:
                        issues.append(
                            AuditIssue(
                                collection="steps",
                                entity_id=step_id,
                                field_path=f"criteria_block_ids[{c_idx}]",
                                issue_type="ORPHAN_CRITERIA_BLOCK",
                                message=f"LLM step '{step_id}' references unknown prompt_block '{c_id}'.",
                            )
                        )

            # 3. Extraction Protocol Block ID Check
            protocol_block_id = step["extraction_protocol_block_id"] if "extraction_protocol_block_id" in step else None
            if not protocol_block_id or not isinstance(protocol_block_id, str):
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="extraction_protocol_block_id",
                        issue_type="MISSING_EXTRACTION_PROTOCOL",
                        message=f"LLM step '{step_id}' lacks extraction_protocol_block_id.",
                    )
                )
            elif str(protocol_block_id) not in prompt_block_ids:
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="extraction_protocol_block_id",
                        issue_type="ORPHAN_PROTOCOL_BLOCK",
                        message=f"LLM step '{step_id}' references unknown protocol_block '{protocol_block_id}'.",
                    )
                )

            # 4. Optional Role Block ID Check
            role_block_id = step["role_block_id"] if "role_block_id" in step else None
            if role_block_id and str(role_block_id) not in prompt_block_ids:
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="role_block_id",
                        issue_type="ORPHAN_ROLE_BLOCK",
                        message=f"LLM step '{step_id}' references unknown role_block '{role_block_id}'.",
                    )
                )

            # 5. Optional Execution Persona Block ID Check
            persona_block_id = step["execution_persona_block_id"] if "execution_persona_block_id" in step else None
            if persona_block_id and str(persona_block_id) not in prompt_block_ids:
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="execution_persona_block_id",
                        issue_type="ORPHAN_PERSONA_BLOCK",
                        message=f"LLM step '{step_id}' references unknown persona_block '{persona_block_id}'.",
                    )
                )

        # Expected Inputs Formatting Check
        expected_inputs = step["expected_inputs"] if "expected_inputs" in step else []
        if isinstance(expected_inputs, list):
            for in_idx, inp_key in enumerate(expected_inputs):
                if not isinstance(inp_key, str) or not inp_key.strip() or " " in inp_key:
                    issues.append(
                        AuditIssue(
                            collection="steps",
                            entity_id=step_id,
                            field_path=f"expected_inputs[{in_idx}]",
                            issue_type="MALFORMED_INPUT_KEY",
                            message=f"Step '{step_id}' has malformed expected_input key '{inp_key}'.",
                        )
                    )

    return issues, total_steps


def audit_workflows(
    workflows: list[dict[str, Any]],
    step_blueprint_ids: set[str],
) -> tuple[list[AuditIssue], int]:
    """Audits the workflows collection for variable routing and input contract validity.

    Args:
        workflows: List of raw workflow dictionaries.
        step_blueprint_ids: Set of valid step blueprint IDs.

    Returns:
        A tuple of (issues list, total_workflows count).
    """
    issues: list[AuditIssue] = []
    total_workflows = len(workflows)

    for wf in workflows:
        wf_id = str(wf["id"]) if "id" in wf else "UNKNOWN_WORKFLOW"

        # 1. Check workflow-level expected_inputs
        wf_expected_inputs = wf["expected_inputs"] if "expected_inputs" in wf else []
        known_wf_input_keys: set[str] = set()

        if isinstance(wf_expected_inputs, list):
            for in_idx, exp_inp in enumerate(wf_expected_inputs):
                if not isinstance(exp_inp, dict):
                    continue
                input_key = str(exp_inp["input_key"]) if "input_key" in exp_inp else ""
                if input_key:
                    known_wf_input_keys.add(input_key)

                ai_desc = exp_inp["ai_description"] if "ai_description" in exp_inp else None
                if isinstance(ai_desc, str) and _contains_raw_xml(ai_desc):
                    issues.append(
                        AuditIssue(
                            collection="workflows",
                            entity_id=wf_id,
                            field_path=f"expected_inputs[{in_idx}].ai_description",
                            issue_type="RAW_XML",
                            message=f"Workflow '{wf_id}' input '{input_key}' contains raw XML in ai_description.",
                        )
                    )

        # 2. Check workflow system_prompt
        wf_sys_prompt = wf["system_prompt"] if "system_prompt" in wf else None
        if isinstance(wf_sys_prompt, str) and _contains_raw_xml(wf_sys_prompt):
            issues.append(
                AuditIssue(
                    collection="workflows",
                    entity_id=wf_id,
                    field_path="system_prompt",
                    issue_type="RAW_XML",
                    message=f"Workflow '{wf_id}' contains raw XML in system_prompt.",
                )
            )

        # 3. Check workflow steps and input_mappings
        wf_steps = wf["steps"] if "steps" in wf else []
        known_wf_step_ids: set[str] = set()
        if isinstance(wf_steps, list):
            for s in wf_steps:
                if isinstance(s, dict):
                    s_id = str(s["id"]) if "id" in s else ""
                    if s_id:
                        known_wf_step_ids.add(s_id)

            for s_idx, step_rule in enumerate(wf_steps):
                if not isinstance(step_rule, dict):
                    continue
                s_id = str(step_rule["id"]) if "id" in step_rule else f"step_rule_{s_idx}"
                blueprint_id = str(step_rule["task_blueprint"]) if "task_blueprint" in step_rule else ""

                if blueprint_id and blueprint_id not in step_blueprint_ids:
                    issues.append(
                        AuditIssue(
                            collection="workflows",
                            entity_id=wf_id,
                            field_path=f"steps[{s_idx}].task_blueprint",
                            issue_type="ORPHAN_STEP_BLUEPRINT",
                            message=f"Workflow '{wf_id}' step '{s_id}' references unknown task_blueprint '{blueprint_id}'.",
                        )
                    )

                input_mappings = step_rule["input_mappings"] if "input_mappings" in step_rule else {}
                if isinstance(input_mappings, dict):
                    for map_key, map_val in input_mappings.items():
                        if not isinstance(map_val, str):
                            continue
                        if map_val.startswith("$inputs."):
                            target_in_key = map_val[len("$inputs.") :]
                            if target_in_key not in known_wf_input_keys:
                                issues.append(
                                    AuditIssue(
                                        collection="workflows",
                                        entity_id=wf_id,
                                        field_path=f"steps[{s_idx}].input_mappings.{map_key}",
                                        issue_type="UNRESOLVED_INPUT_MAPPING",
                                        message=(
                                            f"Workflow '{wf_id}' step '{s_id}' maps to unknown input "
                                            f"'{target_in_key}' in '{map_val}'."
                                        ),
                                    )
                                )
                        elif map_val.startswith("$steps."):
                            parts = map_val.split(".")
                            if len(parts) >= 2:
                                target_step_id = parts[1]
                                if target_step_id not in known_wf_step_ids and target_step_id != "matrix_reducer":
                                    issues.append(
                                        AuditIssue(
                                            collection="workflows",
                                            entity_id=wf_id,
                                            field_path=f"steps[{s_idx}].input_mappings.{map_key}",
                                            issue_type="UNRESOLVED_STEP_MAPPING",
                                            message=(
                                                f"Workflow '{wf_id}' step '{s_id}' maps to unknown step "
                                                f"'{target_step_id}' in '{map_val}'."
                                            ),
                                        )
                                    )

    return issues, total_workflows


def audit_output_profiles(
    output_profiles: list[dict[str, Any]],
    prompt_block_ids: set[str],
) -> tuple[list[AuditIssue], int]:
    """Audits the output_profiles collection for XML hygiene and referential integrity.

    Args:
        output_profiles: List of raw output profile dictionaries.
        prompt_block_ids: Set of valid prompt_block IDs.

    Returns:
        A tuple of (issues list, total_profiles count).
    """
    issues: list[AuditIssue] = []
    total_profiles = len(output_profiles)

    for profile in output_profiles:
        profile_id = str(profile["id"]) if "id" in profile else "UNKNOWN_PROFILE"

        # 1. Ensure purged synthesis sub-object is absent
        if "synthesis" in profile:
            issues.append(
                AuditIssue(
                    collection="output_profiles",
                    entity_id=profile_id,
                    field_path="synthesis",
                    issue_type="BANNED_SYNTHESIS_OBJECT",
                    message=f"OutputProfile '{profile_id}' contains obsolete 'synthesis' sub-object.",
                )
            )

        # 1b. Check profile-level synthesis directives for raw XML
        for dir_field in [
            "executive_summary_directive",
            "matrix_1d_synthesis_directive",
            "matrix_2d_synthesis_directive",
            "matrix_3d_synthesis_directive",
            "matrix_text_synthesis_directive",
            "row_explanation_directive",
            "xai_synthesis_directive",
            "variance_synthesis_directive",
        ]:
            if dir_field in profile and profile[dir_field]:
                dir_val = profile[dir_field]
                texts_to_check: list[tuple[str, str]] = []
                if isinstance(dir_val, str):
                    texts_to_check.append((dir_field, dir_val))
                elif isinstance(dir_val, dict) and "translations" in dir_val and isinstance(dir_val["translations"], dict):
                    for lang, txt in dir_val["translations"].items():
                        if isinstance(txt, str):
                            texts_to_check.append((f"{dir_field}.translations.{lang}", txt))
                for f_path, txt in texts_to_check:
                    if _contains_raw_xml(txt):
                        issues.append(
                            AuditIssue(
                                collection="output_profiles",
                                entity_id=profile_id,
                                field_path=f_path,
                                issue_type="RAW_XML",
                                message=f"OutputProfile '{profile_id}' contains raw XML in '{f_path}'.",
                            )
                        )

        # 2. Check matrix synthesis groups
        matrix_groups = profile["matrix_synthesis_groups"] if "matrix_synthesis_groups" in profile else []
        if isinstance(matrix_groups, list):
            for g_idx, grp in enumerate(matrix_groups):
                if not isinstance(grp, dict):
                    continue
                grp_id = str(grp["id"]) if "id" in grp else f"group_{g_idx}"

                synthesis_directive = grp["synthesis_directive"] if "synthesis_directive" in grp else None
                if isinstance(synthesis_directive, str) and _contains_raw_xml(synthesis_directive):
                    issues.append(
                        AuditIssue(
                            collection="output_profiles",
                            entity_id=profile_id,
                            field_path=f"matrix_synthesis_groups[{g_idx}].synthesis_directive",
                            issue_type="RAW_XML",
                            message=f"OutputProfile '{profile_id}' group '{grp_id}' contains raw XML in directive.",
                        )
                    )

                target_blocks = grp["target_blocks"] if "target_blocks" in grp else []
                if isinstance(target_blocks, list):
                    for tb_idx, tb_id in enumerate(target_blocks):
                        if str(tb_id) not in prompt_block_ids:
                            issues.append(
                                AuditIssue(
                                    collection="output_profiles",
                                    entity_id=profile_id,
                                    field_path=f"matrix_synthesis_groups[{g_idx}].target_blocks[{tb_idx}]",
                                    issue_type="ORPHAN_TARGET_BLOCK",
                                    message=(
                                        f"OutputProfile '{profile_id}' group '{grp_id}' targets unknown "
                                        f"prompt_block '{tb_id}'."
                                    ),
                                )
                            )

    return issues, total_profiles


def run_full_database_audit(seed_data_path: Path) -> FullDatabaseAuditReport:
    """Executes the full database prompt audit across all 4 collections.

    Args:
        seed_data_path: Absolute or relative Path to seed_data.json.

    Returns:
        A validated FullDatabaseAuditReport DTO.
    """
    raw_text = seed_data_path.read_text(encoding="utf-8")
    data = json.loads(raw_text)

    prompt_blocks = data["prompt_blocks"] if "prompt_blocks" in data else []
    steps = data["steps"] if "steps" in data else []
    workflows = data["workflows"] if "workflows" in data else []
    output_profiles = data["output_profiles"] if "output_profiles" in data else []

    prompt_block_ids: set[str] = {str(b["id"]) for b in prompt_blocks if isinstance(b, dict) and "id" in b}
    step_blueprint_ids: set[str] = {str(s["id"]) for s in steps if isinstance(s, dict) and "id" in s}

    all_issues: list[AuditIssue] = []

    # Gate 1: prompt_blocks
    block_issues, total_matrices, total_atoms = audit_prompt_blocks(prompt_blocks)
    all_issues.extend(block_issues)

    # Gate 2: steps
    step_issues, total_steps = audit_steps(steps, prompt_block_ids)
    all_issues.extend(step_issues)

    # Gate 3: workflows
    wf_issues, total_workflows = audit_workflows(workflows, step_blueprint_ids)
    all_issues.extend(wf_issues)

    # Gate 4: output_profiles
    profile_issues, total_profiles = audit_output_profiles(output_profiles, prompt_block_ids)
    all_issues.extend(profile_issues)

    error_count = sum(1 for issue in all_issues if issue.severity == "ERROR")
    all_passed = error_count == 0

    return FullDatabaseAuditReport(
        total_matrices=total_matrices,
        total_atoms=total_atoms,
        total_steps=total_steps,
        total_workflows=total_workflows,
        total_profiles=total_profiles,
        issues=all_issues,
        all_passed=all_passed,
    )


def print_audit_report(report: FullDatabaseAuditReport) -> None:
    """Prints a structured summary of the audit report to stdout.

    Args:
        report: The FullDatabaseAuditReport to format and display.
    """
    print("=" * 80)
    print("[AUDIT] QUORUM FULL DATABASE PROMPT VERIFICATION REPORT")
    print("=" * 80)
    print(f"Total Matrices Inspected:  {report.total_matrices}")
    print(f"Total TDA Atoms Inspected: {report.total_atoms}")
    print(f"Total Steps Inspected:     {report.total_steps}")
    print(f"Total Workflows Inspected: {report.total_workflows}")
    print(f"Total Profiles Inspected:  {report.total_profiles}")
    print("-" * 80)
    print(f"Total Issues Found:        {len(report.issues)}")
    print(f"Status:                    {'PASSED (0 ERRORS)' if report.all_passed else 'FAILED (VIOLATIONS DETECTED)'}")
    print("=" * 80)

    if report.issues:
        print("\nDETAILED AUDIT FINDINGS:")
        for idx, issue in enumerate(report.issues, 1):
            print(f"[{idx:03d}] {issue.severity} | {issue.collection} | {issue.entity_id} | {issue.issue_type}")
            print(f"      Path: {issue.field_path}")
            print(f"      Message: {issue.message}")
            print()


def main() -> None:
    """CLI entrypoint for full database prompt verification."""
    parser = argparse.ArgumentParser(description="Audit Quorum database prompt collections.")
    parser.add_argument(
        "--seed-path",
        type=str,
        default="backend_v2/seed/seed_data.json",
        help="Path to seed_data.json file (default: backend_v2/seed/seed_data.json)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero exit code if any violations are detected.",
    )

    args = parser.parse_args()
    seed_path = Path(args.seed_path)

    if not seed_path.exists():
        print(f"Error: seed data file not found at '{seed_path}'", file=sys.stderr)
        sys.exit(1)

    report = run_full_database_audit(seed_path)
    print_audit_report(report)

    if args.strict and not report.all_passed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
