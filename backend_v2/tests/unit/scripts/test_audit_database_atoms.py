"""Unit tests for the Full Database Prompt Verification Engine (audit_database_atoms.py).

Tests all 4-collection inspection gates, Pydantic V2 DTOs, CLI behavior,
and AST zero-reflection enforcement according to ISTQB test partition design.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from scripts.audit_database_atoms import (
    AuditIssue,
    FullDatabaseAuditReport,
    audit_output_profiles,
    audit_prompt_blocks,
    audit_steps,
    audit_workflows,
    main,
    run_full_database_audit,
)


def test_audit_dto_structure() -> None:
    """Test AuditIssue and FullDatabaseAuditReport creation, immutability, and serialization."""
    issue = AuditIssue(
        collection="prompt_blocks",
        entity_id="tda_1234567890abcdef1234567890abcdef",
        field_path="scales[0].claims[0].tda_assertions[0].concept_description",
        issue_type="BANNED_PHRASE",
        message="Contains banned phrase.",
        severity="ERROR",
    )
    assert issue.collection == "prompt_blocks"
    assert issue.severity == "ERROR"

    # Test immutability (frozen=True)
    with pytest.raises(ValidationError):
        # Mutating frozen field should fail
        issue.collection = "steps"  # type: ignore[misc]

    report = FullDatabaseAuditReport(
        total_matrices=1,
        total_atoms=1,
        total_steps=1,
        total_workflows=1,
        total_profiles=1,
        issues=[issue],
        all_passed=False,
    )
    assert report.all_passed is False
    assert len(report.issues) == 1
    dumped = report.model_dump(mode="json")
    assert dumped["total_matrices"] == 1
    assert dumped["issues"][0]["issue_type"] == "BANNED_PHRASE"


def _create_clean_matrix_block(
    block_id: str = "blk_matrix_clean_001",
    tda_id: str = "tda_clean_assertion_001",
) -> dict[str, Any]:
    """Helper to generate a structurally clean matrix prompt block."""
    return {
        "id": block_id,
        "category_id": "matrix",
        "ai_description": "Clean cognitive evaluation instructions.",
        "scales": [
            {
                "score": 1,
                "claims": [
                    {
                        "id": "clm_clean_001",
                        "tda_assertions": [
                            {
                                "tda_id": tda_id,
                                "concept_description": "A valid empirical claim backed by structured data.",
                                "extraction_rule": "Locate sentences containing quantitative metrics or statistical indicators.",
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_audit_clean_pass() -> None:
    """Test that valid and sanitized data produces 0 issues and passes cleanly."""
    clean_blocks = [_create_clean_matrix_block()]
    issues, matrices, atoms = audit_prompt_blocks(clean_blocks)

    assert len(issues) == 0
    assert matrices == 1
    assert atoms == 1


def test_audit_atoms_banned_phrases() -> None:
    """Test detection of banned phrases: BANNED SOURCES, FAIL FAST, EXTRACTION CONDITION, DEPRECATED."""
    bad_phrases = [
        "BANNED SOURCES",
        "FAIL FAST",
        "EXTRACTION CONDITION:",
        "DEPRECATED",
        "STEP 1:",
        "ABSOLUTE MITIGATION ENFORCEMENT",
        "ABSOLUTE LEXICAL BOUNDARY",
    ]
    for phrase in bad_phrases:
        block = _create_clean_matrix_block()
        block["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
            f"Concept description containing {phrase} here."
        )
        issues, _, _ = audit_prompt_blocks([block])
        assert any(i.issue_type == "BANNED_PHRASE" for i in issues), f"Failed to flag banned phrase: {phrase}"


def test_audit_atoms_mechanical_counting() -> None:
    """Test detection of mechanical counting patterns in concept_description and extraction_rule."""
    counting_phrases = ["EXACTLY ZERO", "count is 0", "count of markers", "scan the paragraph"]
    for phrase in counting_phrases:
        # 1. In concept_description
        block1 = _create_clean_matrix_block()
        block1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
            f"Concept description with {phrase} pattern."
        )
        issues1, _, _ = audit_prompt_blocks([block1])
        assert any(i.issue_type == "MECHANICAL_COUNTING" for i in issues1), f"Failed to flag count in concept: {phrase}"

        # 2. In extraction_rule
        block2 = _create_clean_matrix_block()
        block2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = (
            f"Extraction rule with {phrase} pattern."
        )
        issues2, _, _ = audit_prompt_blocks([block2])
        assert any(i.issue_type == "MECHANICAL_COUNTING" for i in issues2), f"Failed to flag count in rule: {phrase}"


def test_audit_atoms_bloated_and_identical_concepts() -> None:
    """Test detection of bloated concept descriptions (>180 chars) and identical concept/rule strings."""
    # 1. Bloated concept description
    block1 = _create_clean_matrix_block()
    block1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "A" * 185
    issues1, _, _ = audit_prompt_blocks([block1])
    assert any(i.issue_type == "BLOATED_CONCEPT" for i in issues1), "Failed to flag bloated concept description."

    # 2. Identical concept_description and extraction_rule
    block2 = _create_clean_matrix_block()
    same_text = "This exact text is used for both the concept description and extraction rule."
    block2["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = same_text
    block2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = same_text
    issues2, _, _ = audit_prompt_blocks([block2])
    assert any(i.issue_type == "IDENTICAL_CONCEPT_AND_RULE" for i in issues2), (
        "Failed to flag identical concept and rule."
    )


def test_audit_atoms_negative_guidance() -> None:
    """Test detection of negative guidance phrases in concept_description."""
    negative_phrases = ["Do not evaluate", "Do not judge", "Do not accept", "Do not flag"]
    for phrase in negative_phrases:
        block = _create_clean_matrix_block()
        block["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
            f"Concept description with {phrase} subjective elements."
        )
        issues, _, _ = audit_prompt_blocks([block])
        assert any(i.issue_type == "NEGATIVE_GUIDANCE" for i in issues), f"Failed to flag negative phrase: {phrase}"


def test_audit_atoms_chat_hardcoding() -> None:
    """Test detection of chatbot-specific hardcoding and modality coupling."""
    chat_phrases = ["Scan ONLY user prompts", "role prefixes", "user prompt", "AI output", "Reject AI outputs"]
    for phrase in chat_phrases:
        block = _create_clean_matrix_block()
        block["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = (
            f"Extraction rule with {phrase} matching."
        )
        issues, _, _ = audit_prompt_blocks([block])
        assert any(i.issue_type == "CHAT_HARDCODING" for i in issues), f"Failed to flag chat phrase: {phrase}"


def test_audit_atoms_raw_xml() -> None:
    """Test detection of raw XML tags and angle brackets in fields."""
    # 1. XML in concept_description
    block1 = _create_clean_matrix_block()
    block1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
        "<ambiguity_protocol>Description with raw XML</ambiguity_protocol>"
    )
    issues1, _, _ = audit_prompt_blocks([block1])
    assert any(i.issue_type == "RAW_XML" for i in issues1)

    # 2. XML in extraction_rule
    block2 = _create_clean_matrix_block()
    block2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = (
        "<rule_enforcement>Rule with raw XML</rule_enforcement>"
    )
    issues2, _, _ = audit_prompt_blocks([block2])
    assert any(i.issue_type == "RAW_XML" for i in issues2)

    # 3. XML in non-matrix block ai_description and role_enforcement
    non_matrix_block = {
        "id": "blk_persona_001",
        "category_id": "execution_persona",
        "ai_description": "<role>Executive Coach</role>",
        "role_enforcement": "<mandate>Be strict</mandate>",
    }
    issues3, _, _ = audit_prompt_blocks([non_matrix_block])
    assert len([i for i in issues3 if i.issue_type == "RAW_XML"]) == 2


def test_audit_atoms_empty_rules() -> None:
    """Test detection of empty or short extraction rules (< 10 chars)."""
    block = _create_clean_matrix_block()
    block["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = ""
    issues, _, _ = audit_prompt_blocks([block])
    assert any(i.issue_type == "EMPTY_EXTRACTION_RULE" for i in issues)

    block2 = _create_clean_matrix_block()
    block2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = "short"
    issues2, _, _ = audit_prompt_blocks([block2])
    assert any(i.issue_type == "EMPTY_EXTRACTION_RULE" for i in issues2)


def test_audit_atoms_screaming_imperatives() -> None:
    """Test detection of screaming imperatives in concept_description."""
    imperatives = ["CRITICAL DIRECTIVE", "LOCATE", "IDENTIFY", "Scan the document.", "Verify", "CHECK"]
    for imp in imperatives:
        block = _create_clean_matrix_block()
        block["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
            f"Header {imp}: this concept must be verified."
        )
        issues, _, _ = audit_prompt_blocks([block])
        assert any(i.issue_type == "SCREAMING_IMPERATIVE" for i in issues), f"Failed to flag imperative: {imp}"


def test_audit_steps_referential_integrity() -> None:
    """Test detection of missing strategies, orphan criteria_block_ids, and orphan protocol_block_ids."""
    known_block_ids = {"blk_matrix_01", "blk_protocol_01"}

    # 1. Missing model_strategy
    step1 = {
        "id": "stp_001",
        "type": "llm",
        "model_strategy": None,
        "criteria_block_ids": ["blk_matrix_01"],
        "extraction_protocol_block_id": "blk_protocol_01",
    }
    issues1, _ = audit_steps([step1], known_block_ids)
    assert any(i.issue_type == "MISSING_MODEL_STRATEGY" for i in issues1)

    # 2. Orphan criteria block
    step2 = {
        "id": "stp_002",
        "type": "llm",
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_unknown_matrix"],
        "extraction_protocol_block_id": "blk_protocol_01",
    }
    issues2, _ = audit_steps([step2], known_block_ids)
    assert any(i.issue_type == "ORPHAN_CRITERIA_BLOCK" for i in issues2)

    # 3. Orphan protocol block
    step3 = {
        "id": "stp_003",
        "type": "llm",
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_matrix_01"],
        "extraction_protocol_block_id": "blk_unknown_protocol",
    }
    issues3, _ = audit_steps([step3], known_block_ids)
    assert any(i.issue_type == "ORPHAN_PROTOCOL_BLOCK" for i in issues3)


def test_audit_workflows_input_mappings() -> None:
    """Test detection of unresolved $inputs.key or $steps.key in workflow mappings."""
    known_step_blueprints = {"stp_001"}

    workflow = {
        "id": "wor_001",
        "expected_inputs": [
            {
                "input_key": "document_text",
                "ai_description": "Clean input description.",
            }
        ],
        "steps": [
            {
                "id": "sr_001",
                "task_blueprint": "stp_001",
                "input_mappings": {
                    "context": "$inputs.unknown_document_key",
                    "history": "$steps.sr_unknown.output",
                },
            }
        ],
    }
    issues, _ = audit_workflows([workflow], known_step_blueprints)

    assert any(i.issue_type == "UNRESOLVED_INPUT_MAPPING" for i in issues)
    assert any(i.issue_type == "UNRESOLVED_STEP_MAPPING" for i in issues)


def test_audit_output_profiles_directives() -> None:
    """Test detection of raw XML in synthesis directives and orphan target_blocks in output_profiles."""
    known_block_ids = {"blk_matrix_01"}

    profile = {
        "id": "prf_001",
        "synthesis": {
            "system_prompt": "<synthesis_mandate>Be concise</synthesis_mandate>",
            "synthesis_block_id": "blk_unknown_synth",
        },
        "matrix_synthesis_groups": [
            {
                "id": "grp_001",
                "synthesis_directive": "<directive>Group 1</directive>",
                "target_blocks": ["blk_unknown_target"],
            }
        ],
    }
    issues, _ = audit_output_profiles([profile], known_block_ids)

    assert any(i.issue_type == "BANNED_SYNTHESIS_OBJECT" and "synthesis" in i.field_path for i in issues)
    assert any(i.issue_type == "RAW_XML" and "matrix_synthesis_groups" in i.field_path for i in issues)
    assert any(i.issue_type == "ORPHAN_TARGET_BLOCK" for i in issues)


def test_audit_cli_exit_codes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI exit code 0 on clean pass and code 1 on strict failure."""
    # 1. Clean file
    clean_data = {
        "prompt_blocks": [_create_clean_matrix_block()],
        "steps": [],
        "workflows": [],
        "output_profiles": [],
    }
    clean_file = tmp_path / "clean_seed.json"
    clean_file.write_text(json.dumps(clean_data), encoding="utf-8")

    report = run_full_database_audit(clean_file)
    assert report.all_passed is True

    # Test main() with clean file
    monkeypatch.setattr("sys.argv", ["audit_database_atoms.py", "--seed-path", str(clean_file), "--strict"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0

    # 2. Corrupted file
    corrupt_block = _create_clean_matrix_block()
    corrupt_block["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "FAIL FAST and abort"
    corrupt_data = {
        "prompt_blocks": [corrupt_block],
        "steps": [],
        "workflows": [],
        "output_profiles": [],
    }
    corrupt_file = tmp_path / "corrupt_seed.json"
    corrupt_file.write_text(json.dumps(corrupt_data), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["audit_database_atoms.py", "--seed-path", str(corrupt_file), "--strict"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_audit_zero_reflection() -> None:
    """Uses Python AST parser to mathematically verify zero getattr/hasattr calls in audit_database_atoms.py."""
    target_script = Path("scripts/audit_database_atoms.py")
    assert target_script.exists(), "audit_database_atoms.py script must exist."

    tree = ast.parse(target_script.read_text(encoding="utf-8"), filename=str(target_script))

    banned_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("getattr", "hasattr", "setattr"):
                banned_calls.append(node.func.id)

    assert len(banned_calls) == 0, f"Found reflection calls {banned_calls} in audit_database_atoms.py."
