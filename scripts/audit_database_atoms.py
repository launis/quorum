"""Full Database Prompt & Matrix Atom Verification Engine.

This script serves as the Single Source of Truth (SSOT) quality gate
for database (`backend_v2/seed/seed_data.json`) prompt and matrix collections.

WORKFLOW AND USAGE:
===================
1. General Quality Audit (All Collections):
   `uv run python scripts/audit_database_atoms.py --strict`
   - Validates that all prompt_blocks (matrices), steps, workflows, and output_profiles
     are 100% Pydantic V2 compliant without schema errors or empty criteria.

2. Local Database Reseeding After Validation:
   `uv run python backend_v2/seed/run_seed.py local`

AUDITED COLLECTIONS:
--------------------
1. prompt_blocks (Matrix TDA assertions, personas, evaluation guidelines)
2. steps (LLM execution steps, strategies, expected inputs contracts)
3. workflows (DAG-oriented execution workflows, variable routing)
4. output_profiles (Synthesis profiles, SDUI block groupings)

Strictly adheres to Zero-Reflection Mandate (no getattr/hasattr) and Pydantic V2.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Any

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EntityPrefix, PromptBlockCategory

logger = logging.getLogger(__name__)

__all__ = [
    "BANNED_ALTERNATIVE_PK_KEYS",
    "SEED_COLLECTION_ALLOWED_PREFIXES",
    "SEED_COLLECTION_REQUIRED_DISPLAY_FIELD",
    "AuditIssue",
    "FullDatabaseAuditReport",
    "audit_canonical_entity_ids",
    "audit_output_profiles",
    "audit_prompt_blocks",
    "audit_steps",
    "audit_workflows",
    "main",
    "print_audit_report",
    "run_full_database_audit",
]

# 7-collection canonical Opaque Stripe ID prefix and display field contracts
SEED_COLLECTION_ALLOWED_PREFIXES: dict[str, frozenset[str]] = {
    "organizations": frozenset({EntityPrefix.ORGANIZATION}),
    "users": frozenset({EntityPrefix.USER}),
    "system_config": frozenset({EntityPrefix.SYSTEM_CONFIG}),
    "prompt_blocks": frozenset({EntityPrefix.PROMPT_BLOCK, EntityPrefix.STEP_REFERENCE}),
    "steps": frozenset({EntityPrefix.STEP}),
    "workflows": frozenset({EntityPrefix.WORKFLOW}),
    "output_profiles": frozenset({EntityPrefix.OUTPUT_PROFILE}),
}

SEED_COLLECTION_REQUIRED_DISPLAY_FIELD: dict[str, str] = {
    "organizations": "name",
    "users": "name",
    "system_config": "name",
    "prompt_blocks": "label",
    "steps": "name",
    "workflows": "name",
    "output_profiles": "name",
}

BANNED_ALTERNATIVE_PK_KEYS: frozenset[str] = frozenset(
    {
        "uuid",
        "pk",
        "primary_key",
        "entity_id",
        "node_id",
        "edge_id",
        "report_id",
        "workflow_key",
        "step_key",
        "block_key",
    }
)

_OPAQUE_STRIPE_ID_COMPILED = re.compile(OPAQUE_STRIPE_ID_REGEX)
_SYSTEM_ORGANIZATION_SENTINELS: frozenset[str] = frozenset({"SYSTEM", "ROOT_SYSTEM"})


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

    collection: Annotated[str, Field(description="The database collection name.")]
    entity_id: Annotated[str, Field(description="Unique ID of the entity.")]
    field_path: Annotated[str, Field(description="Path to the affected field.")]
    issue_type: Annotated[str, Field(description="Type/category of the issue.")]
    message: Annotated[str, Field(description="Human-readable issue description.")]
    severity: Annotated[str, Field(description="Severity level.")] = "ERROR"


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

    total_matrices: Annotated[int, Field(description="Total matrices checked.")]
    total_atoms: Annotated[int, Field(description="Total TDA assertion atoms checked.")]
    total_steps: Annotated[int, Field(description="Total step blueprints checked.")]
    total_workflows: Annotated[int, Field(description="Total workflow DAGs checked.")]
    total_profiles: Annotated[int, Field(description="Total output profiles checked.")]
    issues: Annotated[list[AuditIssue], Field(default_factory=list, description="List of issues.")]
    all_passed: Annotated[bool, Field(description="Whether the full audit passed cleanly.")]


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

# Illustrative examples (e.g. 'a0', 'a1') are explicitly permitted in prompt instructions
# per 05_llm_architecture.md (prompt_illustrative_examples_mandate).
AMBIGUITY_REGEX: re.Pattern[str] = re.compile(r"\b(?:etc\.|etc|such as)(?!\w)", re.IGNORECASE)
BACKEND_LEAK_REGEX: re.Pattern[str] = re.compile(r"\b(pydantic|backend architecture|pydantic hooks)\b", re.IGNORECASE)
INSTITUTION_OVERFIT_REGEX: re.Pattern[str] = re.compile(r"\b(stanford|työterveyslaitos)\b", re.IGNORECASE)
TOY_DOMAIN_REGEX: re.Pattern[str] = re.compile(r"\b(postgresql|sqlite|mongodb)\b", re.IGNORECASE)


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


def _check_ambiguity_patterns(text: str) -> str | None:
    """Checks if text contains open-ended ambiguity tokens (etc., such as).

    Per 05_llm_architecture.md (prompt_illustrative_examples_mandate), illustrative
    examples (e.g., 'a0', 'a1') in LLM instructions and prompt blocks are explicitly
    exempted and permitted.

    Args:
        text: The string to inspect.

    Returns:
        The matched ambiguity token if found, else None.
    """
    if not text:
        return None
    # Strip parenthesized illustrative examples: (e.g., ...) or (i.e., ...)
    sanitized = re.sub(r"\((?:e\.g\.|i\.e\.)[^)]*\)", "", text, flags=re.IGNORECASE)
    sanitized = re.sub(r"\b(?:e\.g\.|i\.e\.)\b", "", sanitized, flags=re.IGNORECASE)
    match = AMBIGUITY_REGEX.search(sanitized)
    return match.group(0) if match else None


def _check_backend_leak_patterns(text: str) -> str | None:
    """Checks if text leaks backend software architecture or internal frameworks.

    Args:
        text: The string to inspect.

    Returns:
        The matched backend architecture leak string if found, else None.
    """
    if not text:
        return None
    match = BACKEND_LEAK_REGEX.search(text)
    return match.group(0) if match else None


def _check_institution_overfit(text: str) -> str | None:
    """Checks if text overfits to specific real-world institutions.

    Args:
        text: The string to inspect.

    Returns:
        The matched institution name if found, else None.
    """
    if not text:
        return None
    match = INSTITUTION_OVERFIT_REGEX.search(text)
    return match.group(0) if match else None


def _check_toy_domain_leak(text: str) -> str | None:
    """Checks if text contains toy-domain database references.

    Args:
        text: The string to inspect.

    Returns:
        The matched database technology name if found, else None.
    """
    if not text:
        return None
    match = TOY_DOMAIN_REGEX.search(text)
    return match.group(0) if match else None


def audit_prompt_blocks(
    prompt_blocks: Sequence[Any],
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
        if isinstance(ai_desc, str):
            if _contains_raw_xml(ai_desc):
                issues.append(
                    AuditIssue(
                        collection="prompt_blocks",
                        entity_id=block_id,
                        field_path="ai_description",
                        issue_type="RAW_XML",
                        message=f"Prompt block '{block_id}' contains raw XML in ai_description.",
                    )
                )
            ambig_desc = _check_ambiguity_patterns(ai_desc)
            if ambig_desc:
                issues.append(
                    AuditIssue(
                        collection="prompt_blocks",
                        entity_id=block_id,
                        field_path="ai_description",
                        issue_type="AMBIGUOUS_TOKEN",
                        message=f"Prompt block '{block_id}' ai_description contains ambiguity token '{ambig_desc}'.",
                        severity="WARNING",
                    )
                )
            leak_desc = _check_backend_leak_patterns(ai_desc)
            if leak_desc:
                issues.append(
                    AuditIssue(
                        collection="prompt_blocks",
                        entity_id=block_id,
                        field_path="ai_description",
                        issue_type="BACKEND_CODE_LEAK",
                        message=f"Prompt block '{block_id}' ai_description contains backend implementation leak '{leak_desc}'.",
                    )
                )

        if category_id in (PromptBlockCategory.MATRIX, PromptBlockCategory.MATRIX.value):
            total_matrices += 1
            try:
                matrix_block = MatrixPromptBlock.model_validate(block)
            except ValidationError as err:
                issues.append(
                    AuditIssue(
                        collection="prompt_blocks",
                        entity_id=block_id,
                        field_path="scales",
                        issue_type="SCHEMA_VALIDATION_ERROR",
                        message=f"Matrix block '{block_id}' failed schema validation: {err}",
                    )
                )
                continue

            for scale_idx, scale in enumerate(matrix_block.scales):
                for claim_idx, claim in enumerate(scale.claims):
                    for tda_idx, assertion in enumerate(claim.tda_assertions):
                        total_atoms += 1
                        tda_id = assertion.tda_id if assertion.tda_id else f"tda_s{scale_idx}_c{claim_idx}_a{tda_idx}"
                        prefix_path = f"scales[{scale_idx}].claims[{claim_idx}].tda_assertions[{tda_idx}]"

                        concept_desc = assertion.concept_description
                        extraction_rule = assertion.extraction_rule

                        # 1. Check concept_description presence and length
                        if not concept_desc or len(concept_desc.strip()) < 10:
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

                            # Check Ambiguity Patterns in concept_description
                            ambig_match = _check_ambiguity_patterns(concept_desc)
                            if ambig_match:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="AMBIGUOUS_TOKEN",
                                        message=f"Atom '{tda_id}' concept_description contains open-ended ambiguity token '{ambig_match}'.",
                                    )
                                )

                            # Check Backend Leak Patterns in concept_description
                            leak_match = _check_backend_leak_patterns(concept_desc)
                            if leak_match:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="BACKEND_CODE_LEAK",
                                        message=f"Atom '{tda_id}' concept_description contains backend implementation leak '{leak_match}'.",
                                    )
                                )

                            # Check Institution Overfitting in concept_description
                            inst_match = _check_institution_overfit(concept_desc)
                            if inst_match:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="INSTITUTION_OVERFIT",
                                        message=f"Atom '{tda_id}' concept_description contains institution overfit '{inst_match}'.",
                                    )
                                )

                            # Check Toy Domain Leak in concept_description
                            toy_match = _check_toy_domain_leak(concept_desc)
                            if toy_match:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.concept_description",
                                        issue_type="TOY_DOMAIN_LEAK",
                                        message=f"Atom '{tda_id}' concept_description contains toy domain reference '{toy_match}'.",
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

                            # Check Ambiguity Patterns in extraction_rule
                            ambig_rule = _check_ambiguity_patterns(extraction_rule)
                            if ambig_rule:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.extraction_rule",
                                        issue_type="AMBIGUOUS_TOKEN",
                                        message=f"Atom '{tda_id}' extraction_rule contains open-ended ambiguity token '{ambig_rule}'.",
                                    )
                                )

                            # Check Backend Leak Patterns in extraction_rule
                            leak_rule = _check_backend_leak_patterns(extraction_rule)
                            if leak_rule:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.extraction_rule",
                                        issue_type="BACKEND_CODE_LEAK",
                                        message=f"Atom '{tda_id}' extraction_rule contains backend implementation leak '{leak_rule}'.",
                                    )
                                )

                            # Check Institution Overfitting in extraction_rule
                            inst_rule = _check_institution_overfit(extraction_rule)
                            if inst_rule:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.extraction_rule",
                                        issue_type="INSTITUTION_OVERFIT",
                                        message=f"Atom '{tda_id}' extraction_rule contains institution overfit '{inst_rule}'.",
                                    )
                                )

                            # Check Toy Domain Leak in extraction_rule
                            toy_rule = _check_toy_domain_leak(extraction_rule)
                            if toy_rule:
                                issues.append(
                                    AuditIssue(
                                        collection="prompt_blocks",
                                        entity_id=tda_id,
                                        field_path=f"{prefix_path}.extraction_rule",
                                        issue_type="TOY_DOMAIN_LEAK",
                                        message=f"Atom '{tda_id}' extraction_rule contains toy domain reference '{toy_rule}'.",
                                    )
                                )

        else:
            # Non-matrix blocks inspection
            for field_name in ["role_enforcement", "instruction_text", "protocol_instructions"]:
                if field_name in block:
                    val = block[field_name]
                    if isinstance(val, str):
                        if _contains_raw_xml(val):
                            issues.append(
                                AuditIssue(
                                    collection="prompt_blocks",
                                    entity_id=block_id,
                                    field_path=field_name,
                                    issue_type="RAW_XML",
                                    message=f"Prompt block '{block_id}' contains raw XML in '{field_name}'.",
                                )
                            )
                        ambig_blk = _check_ambiguity_patterns(val)
                        if ambig_blk:
                            issues.append(
                                AuditIssue(
                                    collection="prompt_blocks",
                                    entity_id=block_id,
                                    field_path=field_name,
                                    issue_type="AMBIGUOUS_TOKEN",
                                    message=f"Prompt block '{block_id}' contains open-ended ambiguity token '{ambig_blk}' in '{field_name}'.",
                                    severity="WARNING",
                                )
                            )
                        leak_blk = _check_backend_leak_patterns(val)
                        if leak_blk:
                            issues.append(
                                AuditIssue(
                                    collection="prompt_blocks",
                                    entity_id=block_id,
                                    field_path=field_name,
                                    issue_type="BACKEND_CODE_LEAK",
                                    message=f"Prompt block '{block_id}' contains backend implementation leak '{leak_blk}' in '{field_name}'.",
                                )
                            )
                        inst_blk = _check_institution_overfit(val)
                        if inst_blk:
                            issues.append(
                                AuditIssue(
                                    collection="prompt_blocks",
                                    entity_id=block_id,
                                    field_path=field_name,
                                    issue_type="INSTITUTION_OVERFIT",
                                    message=f"Prompt block '{block_id}' contains institution overfit '{inst_blk}' in '{field_name}'.",
                                )
                            )

    return issues, total_matrices, total_atoms


def audit_steps(
    steps: Sequence[Any],
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
            # 1. Cognitive Tier Check
            cognitive_tier = step["cognitive_tier"] if "cognitive_tier" in step else None
            if not cognitive_tier or cognitive_tier not in ("fast", "balanced", "deep", "reasoning"):
                issues.append(
                    AuditIssue(
                        collection="steps",
                        entity_id=step_id,
                        field_path="cognitive_tier",
                        issue_type="MISSING_COGNITIVE_TIER",
                        message=f"LLM step '{step_id}' lacks explicit valid cognitive_tier.",
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
    workflows: Sequence[Any],
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
        try:
            wf_model = Workflow.model_validate(wf)
        except ValidationError as err:
            issues.append(
                AuditIssue(
                    collection="workflows",
                    entity_id=wf_id,
                    field_path="",
                    issue_type="SCHEMA_VALIDATION_ERROR",
                    message=f"Workflow '{wf_id}' failed schema validation: {err}",
                )
            )
            continue

        # 1. Check workflow-level expected_inputs
        known_wf_input_keys: set[str] = set()
        for in_idx, exp_inp in enumerate(wf_model.expected_inputs):
            if exp_inp.input_key:
                known_wf_input_keys.add(exp_inp.input_key)

            if exp_inp.ai_description and _contains_raw_xml(exp_inp.ai_description):
                issues.append(
                    AuditIssue(
                        collection="workflows",
                        entity_id=wf_id,
                        field_path=f"expected_inputs[{in_idx}].ai_description",
                        issue_type="RAW_XML",
                        message=f"Workflow '{wf_id}' input '{exp_inp.input_key}' contains raw XML in ai_description.",
                    )
                )

        # 3. Check workflow steps and input_mappings
        known_wf_step_ids: set[str] = {s.id for s in wf_model.steps if s.id}

        for s_idx, step_rule in enumerate(wf_model.steps):
            s_id = step_rule.id if step_rule.id else f"step_rule_{s_idx}"
            blueprint_id = step_rule.task_blueprint if step_rule.task_blueprint else ""

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

            for map_key, map_val in step_rule.input_mappings.items():
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
    output_profiles: Sequence[Any],
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

        prof_to_validate = {k: v for k, v in profile.items() if k != "synthesis"}
        try:
            profile_model = OutputProfile.model_validate(prof_to_validate)
        except ValidationError as err:
            issues.append(
                AuditIssue(
                    collection="output_profiles",
                    entity_id=profile_id,
                    field_path="",
                    issue_type="SCHEMA_VALIDATION_ERROR",
                    message=f"OutputProfile '{profile_id}' failed schema validation: {err}",
                )
            )
            continue

        # 1b. Check profile-level synthesis directives for raw XML
        for dir_field, dir_val in [
            ("executive_summary_directive", profile_model.executive_summary_directive),
            ("matrix_1d_synthesis_directive", profile_model.matrix_1d_synthesis_directive),
            ("matrix_2d_synthesis_directive", profile_model.matrix_2d_synthesis_directive),
            ("matrix_3d_synthesis_directive", profile_model.matrix_3d_synthesis_directive),
            ("matrix_text_synthesis_directive", profile_model.matrix_text_synthesis_directive),
            ("row_explanation_directive", profile_model.row_explanation_directive),
            ("xai_synthesis_directive", profile_model.xai_synthesis_directive),
            ("variance_synthesis_directive", profile_model.variance_synthesis_directive),
        ]:
            if isinstance(dir_val, str) and _contains_raw_xml(dir_val):
                issues.append(
                    AuditIssue(
                        collection="output_profiles",
                        entity_id=profile_id,
                        field_path=dir_field,
                        issue_type="RAW_XML",
                        message=f"OutputProfile '{profile_id}' contains raw XML in '{dir_field}'.",
                    )
                )

        # 2. Check matrix synthesis groups
        for g_idx, grp in enumerate(profile_model.matrix_synthesis_groups):
            grp_id = grp.id
            for tb_idx, tb_id in enumerate(grp.target_blocks):
                if tb_id not in prompt_block_ids:
                    issues.append(
                        AuditIssue(
                            collection="output_profiles",
                            entity_id=profile_id,
                            field_path=f"matrix_synthesis_groups[{g_idx}].target_blocks[{tb_idx}]",
                            issue_type="ORPHAN_TARGET_BLOCK",
                            message=(
                                f"OutputProfile '{profile_id}' group '{grp_id}' targets unknown prompt_block '{tb_id}'."
                            ),
                        )
                    )

    return issues, total_profiles


def _has_valid_display_value(collection: str, display_val: Any) -> bool:
    """Verify whether a seed record provides a non-empty canonical human-readable display field.

    Args:
        collection: Seed collection name.
        display_val: Raw value of the required display field (`name` or `label`).

    Returns:
        True if the display field is present and non-empty.
    """
    if collection in {"organizations", "users", "system_config"}:
        return isinstance(display_val, str) and bool(display_val.strip())
    if display_val is None or isinstance(display_val, (str, int, float, bool, list, tuple, set)):
        return False
    try:
        parsed_i18n = I18nText.model_validate(display_val)
        return any(isinstance(v, str) and bool(v.strip()) for v in parsed_i18n.translations.values())
    except ValidationError, AppException:
        if "translations" not in display_val:
            return False
        raw_translations = display_val["translations"]
        if raw_translations is None or isinstance(raw_translations, (str, int, float, bool, list, tuple, set)):
            return False
        try:
            return any(isinstance(v, str) and bool(v.strip()) for v in raw_translations.values())
        except AttributeError, TypeError:
            return False


def audit_canonical_entity_ids(data: Any) -> list[AuditIssue]:
    """Audit all 7 seed collections for canonical Opaque Stripe IDs, display names, and FK integrity.

    Args:
        data: Top-level seed dictionary mapping collection names to record sequences.

    Returns:
        List of AuditIssue violations discovered across the 7 collections.
    """
    # Enforce 7-collection canonical id, display name, and FK referential integrity
    issues: list[AuditIssue] = []
    seen_ids: set[str] = set()
    collection_ids: dict[str, set[str]] = {col: set() for col in SEED_COLLECTION_ALLOWED_PREFIXES}

    for collection, allowed_prefixes in SEED_COLLECTION_ALLOWED_PREFIXES.items():
        records = data[collection] if collection in data else []
        display_field = SEED_COLLECTION_REQUIRED_DISPLAY_FIELD[collection]

        for idx, record in enumerate(records):
            raw_id = record["id"] if "id" in record else None
            entity_id = str(raw_id) if isinstance(raw_id, str) and raw_id.strip() else f"{collection}[{idx}]"

            id_match = _OPAQUE_STRIPE_ID_COMPILED.match(raw_id) if isinstance(raw_id, str) else None
            if id_match is None or id_match.group(1) not in allowed_prefixes:
                issues.append(
                    AuditIssue(
                        collection=collection,
                        entity_id=entity_id,
                        field_path="id",
                        issue_type="INVALID_CANONICAL_ID",
                        message=(
                            f"Entity '{entity_id}' in '{collection}' has invalid canonical id; "
                            f"expected 32-hex UUIDv7 with prefix in {sorted(allowed_prefixes)}."
                        ),
                    )
                )
            else:
                canonical_id = str(raw_id)
                if canonical_id in seen_ids:
                    issues.append(
                        AuditIssue(
                            collection=collection,
                            entity_id=canonical_id,
                            field_path="id",
                            issue_type="DUPLICATE_CANONICAL_ID",
                            message=f"Duplicate canonical id '{canonical_id}' detected in '{collection}'.",
                        )
                    )
                seen_ids.add(canonical_id)
                collection_ids[collection].add(canonical_id)

            for banned_key in sorted(BANNED_ALTERNATIVE_PK_KEYS):
                if banned_key in record:
                    issues.append(
                        AuditIssue(
                            collection=collection,
                            entity_id=entity_id,
                            field_path=banned_key,
                            issue_type="BANNED_ALTERNATIVE_PK_FIELD",
                            message=(
                                f"Entity '{entity_id}' in '{collection}' declares banned alternative "
                                f"primary key field '{banned_key}'."
                            ),
                        )
                    )

            display_val = record[display_field] if display_field in record else None
            if not _has_valid_display_value(collection, display_val):
                issues.append(
                    AuditIssue(
                        collection=collection,
                        entity_id=entity_id,
                        field_path=display_field,
                        issue_type="MISSING_CANONICAL_NAME",
                        message=(
                            f"Entity '{entity_id}' in '{collection}' is missing required non-empty "
                            f"canonical display field '{display_field}'."
                        ),
                    )
                )

    organization_ids = collection_ids["organizations"] | set(_SYSTEM_ORGANIZATION_SENTINELS)
    system_config_ids = collection_ids["system_config"]
    output_profile_ids = collection_ids["output_profiles"]
    workflow_ids = collection_ids["workflows"]
    prompt_block_ids = collection_ids["prompt_blocks"]

    users = data["users"] if "users" in data else []
    for idx, usr in enumerate(users):
        usr_id = str(usr["id"]) if "id" in usr else f"users[{idx}]"
        org_id = usr["organization_id"] if "organization_id" in usr else None
        if org_id is not None and str(org_id) not in organization_ids:
            issues.append(
                AuditIssue(
                    collection="users",
                    entity_id=usr_id,
                    field_path="organization_id",
                    issue_type="ORPHAN_ORGANIZATION_ID",
                    message=f"User '{usr_id}' references unknown organization_id '{org_id}'.",
                )
            )

    workflows = data["workflows"] if "workflows" in data else []
    for idx, wf in enumerate(workflows):
        wf_id = str(wf["id"]) if "id" in wf else f"workflows[{idx}]"
        model_reg_id = wf["model_registry_id"] if "model_registry_id" in wf else None
        if not isinstance(model_reg_id, str) or model_reg_id not in system_config_ids:
            issues.append(
                AuditIssue(
                    collection="workflows",
                    entity_id=wf_id,
                    field_path="model_registry_id",
                    issue_type="ORPHAN_MODEL_REGISTRY_ID",
                    message=f"Workflow '{wf_id}' references unknown model_registry_id '{model_reg_id}'.",
                )
            )

        mcp_gw_id = wf["mcp_gateway_id"] if "mcp_gateway_id" in wf else None
        if mcp_gw_id is not None and str(mcp_gw_id) not in system_config_ids:
            issues.append(
                AuditIssue(
                    collection="workflows",
                    entity_id=wf_id,
                    field_path="mcp_gateway_id",
                    issue_type="ORPHAN_MCP_GATEWAY_ID",
                    message=f"Workflow '{wf_id}' references unknown mcp_gateway_id '{mcp_gw_id}'.",
                )
            )

        default_prof_id = wf["default_profile_id"] if "default_profile_id" in wf else None
        if default_prof_id is not None and str(default_prof_id) not in output_profile_ids:
            issues.append(
                AuditIssue(
                    collection="workflows",
                    entity_id=wf_id,
                    field_path="default_profile_id",
                    issue_type="ORPHAN_DEFAULT_PROFILE_ID",
                    message=f"Workflow '{wf_id}' references unknown default_profile_id '{default_prof_id}'.",
                )
            )

        org_id = wf["organization_id"] if "organization_id" in wf else None
        if org_id is not None and str(org_id) not in organization_ids:
            issues.append(
                AuditIssue(
                    collection="workflows",
                    entity_id=wf_id,
                    field_path="organization_id",
                    issue_type="ORPHAN_ORGANIZATION_ID",
                    message=f"Workflow '{wf_id}' references unknown organization_id '{org_id}'.",
                )
            )

    output_profiles = data["output_profiles"] if "output_profiles" in data else []
    for idx, prof in enumerate(output_profiles):
        prof_id = str(prof["id"]) if "id" in prof else f"output_profiles[{idx}]"
        wf_ref_id = prof["workflow_id"] if "workflow_id" in prof else None
        if not isinstance(wf_ref_id, str) or wf_ref_id not in workflow_ids:
            issues.append(
                AuditIssue(
                    collection="output_profiles",
                    entity_id=prof_id,
                    field_path="workflow_id",
                    issue_type="ORPHAN_WORKFLOW_ID",
                    message=f"OutputProfile '{prof_id}' references unknown workflow_id '{wf_ref_id}'.",
                )
            )

        org_id = prof["organization_id"] if "organization_id" in prof else None
        if org_id is not None and str(org_id) not in organization_ids:
            issues.append(
                AuditIssue(
                    collection="output_profiles",
                    entity_id=prof_id,
                    field_path="organization_id",
                    issue_type="ORPHAN_ORGANIZATION_ID",
                    message=f"OutputProfile '{prof_id}' references unknown organization_id '{org_id}'.",
                )
            )

        for target_field in ("variance_target_block", "user_role_target_block"):
            target_blk = prof[target_field] if target_field in prof else None
            if target_blk is not None and str(target_blk) not in prompt_block_ids:
                issues.append(
                    AuditIssue(
                        collection="output_profiles",
                        entity_id=prof_id,
                        field_path=target_field,
                        issue_type="ORPHAN_TARGET_BLOCK",
                        message=f"OutputProfile '{prof_id}' references unknown {target_field} '{target_blk}'.",
                    )
                )

    return issues


def run_full_database_audit(seed_data_path: Path) -> FullDatabaseAuditReport:
    """Executes the full database prompt audit across all 7 collections.

    Args:
        seed_data_path: Absolute or relative Path to seed_data.json.

    Returns:
        A validated FullDatabaseAuditReport DTO.

    Raises:
        AppException: With ``ErrorCodes.VALIDATION_FAILED`` if ``seed_data_path`` cannot
            be read, contains malformed JSON, or does not decode to a top-level JSON object.
    """
    try:
        raw_text = seed_data_path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error(
            "Failed to read or parse seed data JSON file",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "seed_path": str(seed_data_path)},
            exc_info=True,
        )
        raise AppException(
            message=f"Failed to read or parse seed data file: {seed_data_path}",
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from exc

    if data is None or isinstance(data, (str, int, float, bool, list, tuple, set)):
        logger.error(
            "Seed data root payload must be a JSON object mapping collection names to record arrays",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "seed_path": str(seed_data_path)},
            exc_info=True,
        )
        raise AppException(
            message="Seed data root payload must be a JSON object.",
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    prompt_blocks = data["prompt_blocks"] if "prompt_blocks" in data else []
    steps = data["steps"] if "steps" in data else []
    workflows = data["workflows"] if "workflows" in data else []
    output_profiles = data["output_profiles"] if "output_profiles" in data else []

    prompt_block_ids: set[str] = {str(b["id"]) for b in prompt_blocks if "id" in b}
    step_blueprint_ids: set[str] = {str(s["id"]) for s in steps if "id" in s}

    all_issues: list[AuditIssue] = []

    # Gate 0: 7-collection canonical ID, display name, and cross-collection FK integrity
    all_issues.extend(audit_canonical_entity_ids(data))

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


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for full database prompt verification.

    Args:
        argv: Optional command-line argument list (defaults to sys.argv[1:]).
    """
    parser = argparse.ArgumentParser(
        description="""Comprehensive Database Atom & Prompt Audit Gate.

Statically verifies database invariants across all prompt collections in seed_data.json:
  - Atom Uniqueness: Ensures zero duplicate TDA/Claim/Scale/Block IDs.
  - Scale Bound Conformance: Derives min/max levels strictly from scale arrays without hardcoding.
  - Schema Conformance: Validates prompt blocks against Pydantic V2 domain models with extra='forbid'.
  - Linguistic Neutrality: Enforces English system language and detects ambiguous tokens.
  - Referential Integrity: Checks cross-references between workflows, steps, and prompt blocks.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/audit_database_atoms.py
  uv run python scripts/audit_database_atoms.py --strict
  uv run python scripts/audit_database_atoms.py --seed-path backend_v2/seed/seed_data.json --strict
""",
    )
    parser.add_argument(
        "--seed-path",
        type=str,
        default="backend_v2/seed/seed_data.json",
        help="Filesystem path to seed_data.json (default: backend_v2/seed/seed_data.json).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict mode: exit with code 1 if any advisory warnings or violations are detected.",
    )

    args = parser.parse_args(argv)
    seed_path = Path(args.seed_path)

    if not seed_path.exists():
        print(f"Error: seed data file not found at '{seed_path}'", file=sys.stderr)
        sys.exit(1)

    report = run_full_database_audit(seed_path)
    print_audit_report(report)

    if args.strict and (not report.all_passed or len(report.issues) > 0):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
