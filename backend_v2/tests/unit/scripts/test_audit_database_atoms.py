"""Unit tests for the Full Database Prompt Verification Engine (audit_database_atoms.py).

Tests all 7-collection inspection gates, Pydantic V2 DTOs, CLI behavior,
and AST zero-reflection enforcement according to ISTQB test partition design.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
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
    assert AuditIssue.model_config["frozen"] is True

    # Test extra='forbid' strictness
    with pytest.raises(ValidationError):
        AuditIssue.model_validate({**issue.model_dump(), "extra_field": "banned"})

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
    block_id: str = "blk_0195f3a0000070008123456789abcdef",
    tda_id: str = "tda_0123456789abcdef0123456789abcdef",
) -> Any:
    """Helper to generate a structurally clean matrix prompt block."""
    return {
        "id": block_id,
        "category_id": "matrix",
        "slug": "clean-matrix-block",
        "label": {"translations": {"en": "Clean Matrix"}},
        "description": {"translations": {"en": "Clean description"}},
        "ai_description": "Clean cognitive evaluation instructions.",
        "scales": [
            {
                "score": 1,
                "ai_label": "BASIC_LEVEL",
                "claims": [
                    {
                        "label": {"translations": {"en": "Valid claim"}},
                        "tda_assertions": [
                            {
                                "tda_id": tda_id,
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
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


def test_audit_atoms_ambiguity_tokens() -> None:
    """Test detection of open-ended ambiguity tokens (etc., such as)."""
    ambiguity_phrases = ["etc.", "such as"]
    for phrase in ambiguity_phrases:
        # In concept_description
        b1 = _create_clean_matrix_block()
        b1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
            f"Evaluates standards {phrase} industry guidelines."
        )
        issues1, _, _ = audit_prompt_blocks([b1])
        assert any(i.issue_type == "AMBIGUOUS_TOKEN" for i in issues1), f"Failed to flag ambiguity in concept: {phrase}"

        # In extraction_rule
        b2 = _create_clean_matrix_block()
        b2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = (
            f"Locates patterns {phrase} standard markers."
        )
        issues2, _, _ = audit_prompt_blocks([b2])
        assert any(i.issue_type == "AMBIGUOUS_TOKEN" for i in issues2), f"Failed to flag ambiguity in rule: {phrase}"


def test_audit_atoms_backend_leaks_and_overfitting() -> None:
    """Test detection of backend code leaks, institution overfitting, and toy domain tech names."""
    # 1. Backend code leak in concept_description
    b1 = _create_clean_matrix_block()
    b1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
        "Enforces pydantic validation across external requests."
    )
    issues1, _, _ = audit_prompt_blocks([b1])
    assert any(i.issue_type == "BACKEND_CODE_LEAK" for i in issues1)

    # 2. Institution overfit in extraction_rule
    b2 = _create_clean_matrix_block()
    b2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = (
        "Cites studies from Stanford University regarding cognitive load."
    )
    issues2, _, _ = audit_prompt_blocks([b2])
    assert any(i.issue_type == "INSTITUTION_OVERFIT" for i in issues2)

    # 3. Toy domain tech names in extraction_rule
    b3 = _create_clean_matrix_block()
    b3["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = (
        "Extracts query patterns from PostgreSQL database logs."
    )
    issues3, _, _ = audit_prompt_blocks([b3])
    assert any(i.issue_type == "TOY_DOMAIN_LEAK" for i in issues3)


def test_audit_non_matrix_best_practice_checks() -> None:
    """Test detection of ambiguity and backend code leaks in non-matrix instruction blocks."""
    non_matrix_block = {
        "id": "blk_instruction_001",
        "category_id": "system_rule",
        "instruction_text": "Verify input constraints (such as positive integers) via backend architecture hooks.",
    }
    issues, _, _ = audit_prompt_blocks([non_matrix_block])
    assert any(i.issue_type == "AMBIGUOUS_TOKEN" for i in issues)
    assert any(i.issue_type == "BACKEND_CODE_LEAK" for i in issues)


def test_audit_steps_referential_integrity() -> None:
    """Test detection of missing strategies, orphan criteria_block_ids, and orphan protocol_block_ids."""
    known_block_ids = {"blk_matrix_01", "blk_protocol_01"}

    # 1. Missing cognitive_tier
    step1 = {
        "id": "stp_001",
        "type": "llm",
        "cognitive_tier": None,
        "criteria_block_ids": ["blk_matrix_01"],
        "extraction_protocol_block_id": "blk_protocol_01",
    }
    issues1, _ = audit_steps([step1], known_block_ids)
    assert any(i.issue_type == "MISSING_COGNITIVE_TIER" for i in issues1)

    # 2. Orphan criteria block
    step2 = {
        "id": "stp_002",
        "type": "llm",
        "cognitive_tier": "fast",
        "criteria_block_ids": ["blk_unknown_matrix"],
        "extraction_protocol_block_id": "blk_protocol_01",
    }
    issues2, _ = audit_steps([step2], known_block_ids)
    assert any(i.issue_type == "ORPHAN_CRITERIA_BLOCK" for i in issues2)

    # 3. Orphan protocol block
    step3 = {
        "id": "stp_003",
        "type": "llm",
        "cognitive_tier": "fast",
        "criteria_block_ids": ["blk_matrix_01"],
        "extraction_protocol_block_id": "blk_unknown_protocol",
    }
    issues3, _ = audit_steps([step3], known_block_ids)
    assert any(i.issue_type == "ORPHAN_PROTOCOL_BLOCK" for i in issues3)


def test_audit_workflows_input_mappings() -> None:
    """Test detection of unresolved $inputs.key or $steps.key in workflow mappings."""
    known_step_blueprints = {"stp_0195f3a0000070008123456789abcdef"}

    workflow = {
        "id": "wor_0195f3a0000070008123456789abcdef",
        "slug": "clean-workflow",
        "name": {"translations": {"en": "Clean Workflow"}},
        "description": {"translations": {"en": "Description"}},
        "status": "ACTIVE",
        "version": 1,
        "model_registry_id": "sys_0195f3a00000700e826807f3bfa3454d",
        "historical_context_mode": "DISABLED",
        "expected_inputs": [
            {
                "input_key": "document_text",
                "label": {"translations": {"en": "Doc"}},
                "description": {"translations": {"en": "Desc"}},
                "required": True,
                "ai_description": "Clean input description.",
                "input_modes": ["text"],
            }
        ],
        "steps": [
            {
                "id": "sr_0195f3a0000070008123456789abcdef",
                "task_blueprint": "stp_0195f3a0000070008123456789abcdef",
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
    known_block_ids = {"blk_0195f3a0000070008123456789abcdef"}

    profile = {
        "id": "prf_0195f3a0000070008123456789abcdef",
        "workflow_id": "wor_0195f3a0000070008123456789abcdef",
        "name": {"translations": {"en": "Profile 1"}},
        "slug": "profile-1",
        "description": {"translations": {"en": "Description"}},
        "synthesis": {
            "system_prompt": "<synthesis_mandate>Be concise</synthesis_mandate>",
            "synthesis_block_id": "blk_unknown_synth",
        },
        "matrix_1d_synthesis_directive": "<directive>1D Directive</directive>",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0195f3a0000070008123456789abcdef",
                "title": {"translations": {"en": "Group 1"}},
                "target_blocks": ["blk_unknown_target"],
            }
        ],
    }
    issues, _ = audit_output_profiles([profile], known_block_ids)

    assert any(i.issue_type == "BANNED_SYNTHESIS_OBJECT" and "synthesis" in i.field_path for i in issues)
    assert any(i.issue_type == "RAW_XML" and "matrix_1d_synthesis_directive" in i.field_path for i in issues)
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
    with pytest.raises(SystemExit) as exc_info:
        main(["--seed-path", str(clean_file), "--strict"])
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

    # Corrupted with --strict exits with code 1
    with pytest.raises(SystemExit) as exc_info:
        main(["--seed-path", str(corrupt_file), "--strict"])
    assert exc_info.value.code == 1

    # Corrupted without --strict exits with code 0
    with pytest.raises(SystemExit) as exc_info:
        main(["--seed-path", str(corrupt_file)])
    assert exc_info.value.code == 0

    # Non-existent seed file exits with code 1
    with pytest.raises(SystemExit) as exc_info:
        main(["--seed-path", str(tmp_path / "does_not_exist.json")])
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


def test_helper_empty_string_handling() -> None:
    """Ensure empty strings return None/False safely across string checking helpers."""
    from scripts.audit_database_atoms import (
        _check_ambiguity_patterns,
        _check_backend_leak_patterns,
        _check_institution_overfit,
        _check_screaming_imperatives,
        _check_toy_domain_leak,
        _contains_raw_xml,
    )

    assert _contains_raw_xml("") is False
    assert _check_screaming_imperatives("") is None
    assert _check_ambiguity_patterns("") is None
    assert _check_backend_leak_patterns("") is None
    assert _check_institution_overfit("") is None
    assert _check_toy_domain_leak("") is None


def test_audit_matrix_schema_validation_error() -> None:
    """Ensure invalid matrix block triggers SCHEMA_VALIDATION_ERROR issue."""
    invalid_block = {
        "id": "blk_invalid_schema",
        "category_id": "matrix",
        "slug": "invalid-schema",
        "scales": "not-a-list",  # Causes Pydantic ValidationError
    }
    issues, matrices, _ = audit_prompt_blocks([invalid_block])
    assert matrices == 1
    assert any(i.issue_type == "SCHEMA_VALIDATION_ERROR" for i in issues)


def test_audit_concept_corrupted_and_patterns() -> None:
    """Test corrupted grammar and pattern checks in concept description."""
    # 1. Corrupted grammar ('in an block')
    b2 = _create_clean_matrix_block()
    b2["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "Verifies criteria in an block context."
    issues2, _, _ = audit_prompt_blocks([b2])
    assert any(i.issue_type == "CORRUPTED_GRAMMAR" for i in issues2)

    # 2. Chat hardcoding in concept description
    b3 = _create_clean_matrix_block()
    b3["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "Evaluates user inputs within dialogue."
    issues3, _, _ = audit_prompt_blocks([b3])
    assert any(i.issue_type == "CHAT_HARDCODING" for i in issues3)

    # 3. Institution overfit in concept description
    b4 = _create_clean_matrix_block()
    b4["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = (
        "Grounding on Työterveyslaitos guidelines."
    )
    issues4, _, _ = audit_prompt_blocks([b4])
    assert any(i.issue_type == "INSTITUTION_OVERFIT" for i in issues4)

    # 4. Toy domain leak in concept description
    b5 = _create_clean_matrix_block()
    b5["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "Queries stored in SQLite database."
    issues5, _, _ = audit_prompt_blocks([b5])
    assert any(i.issue_type == "TOY_DOMAIN_LEAK" for i in issues5)


def test_audit_extraction_rule_corrupted_and_banned() -> None:
    """Test corrupted grammar and banned phrase in extraction_rule."""
    b1 = _create_clean_matrix_block()
    b1["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = "Check phrases in an block structure."
    issues1, _, _ = audit_prompt_blocks([b1])
    assert any(i.issue_type == "CORRUPTED_GRAMMAR" for i in issues1)

    b2 = _create_clean_matrix_block()
    b2["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = "Apply FAIL FAST and discard quote."
    issues2, _, _ = audit_prompt_blocks([b2])
    assert any(i.issue_type == "BANNED_PHRASE" for i in issues2)

    b3 = _create_clean_matrix_block()
    b3["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = "Requires pydantic hooks for execution."
    issues3, _, _ = audit_prompt_blocks([b3])
    assert any(i.issue_type == "BACKEND_CODE_LEAK" for i in issues3)


def test_audit_steps_all_edge_cases() -> None:
    """Test steps with empty criteria_blocks, missing protocol, orphan role, orphan persona, and malformed inputs."""
    known_block_ids = {"blk_matrix_01", "blk_protocol_01"}

    # 1. Empty criteria_block_ids
    s1 = {
        "id": "stp_001",
        "type": "llm",
        "cognitive_tier": "fast",
        "criteria_block_ids": [],
        "extraction_protocol_block_id": "blk_protocol_01",
    }
    issues1, _ = audit_steps([s1], known_block_ids)
    assert any(i.issue_type == "EMPTY_CRITERIA_BLOCKS" for i in issues1)

    # 2. Missing extraction_protocol_block_id
    s2 = {
        "id": "stp_002",
        "type": "llm",
        "cognitive_tier": "fast",
        "criteria_block_ids": ["blk_matrix_01"],
        "extraction_protocol_block_id": None,
    }
    issues2, _ = audit_steps([s2], known_block_ids)
    assert any(i.issue_type == "MISSING_EXTRACTION_PROTOCOL" for i in issues2)

    # 3. Orphan role and persona blocks
    s3 = {
        "id": "stp_003",
        "type": "llm",
        "cognitive_tier": "fast",
        "criteria_block_ids": ["blk_matrix_01"],
        "extraction_protocol_block_id": "blk_protocol_01",
        "role_block_id": "blk_missing_role",
        "execution_persona_block_id": "blk_missing_persona",
        "expected_inputs": ["valid_key", "invalid key with spaces", ""],
    }
    issues3, _ = audit_steps([s3], known_block_ids)
    assert any(i.issue_type == "ORPHAN_ROLE_BLOCK" for i in issues3)
    assert any(i.issue_type == "ORPHAN_PERSONA_BLOCK" for i in issues3)
    assert any(i.issue_type == "MALFORMED_INPUT_KEY" for i in issues3)


def test_audit_workflow_validation_error_and_orphan_blueprint() -> None:
    """Test workflow validation error, raw XML in input description, and orphan step blueprint."""
    # 1. Schema validation error
    wf1 = {
        "id": "wor_invalid",
        "steps": "not-a-list",
    }
    issues1, _ = audit_workflows([wf1], set())
    assert any(i.issue_type == "SCHEMA_VALIDATION_ERROR" for i in issues1)

    # 2. Raw XML in input description & orphan step blueprint
    wf2 = {
        "id": "wor_0195f3a0000070008123456789abcdef",
        "slug": "clean-workflow-2",
        "name": {"translations": {"en": "Workflow 2"}},
        "description": {"translations": {"en": "Description"}},
        "status": "ACTIVE",
        "version": 1,
        "model_registry_id": "sys_0195f3a00000700e826807f3bfa3454d",
        "historical_context_mode": "DISABLED",
        "expected_inputs": [
            {
                "input_key": "raw_xml_input",
                "label": {"translations": {"en": "XML Input"}},
                "description": {"translations": {"en": "Desc"}},
                "required": True,
                "ai_description": "<directive>Raw XML in input</directive>",
                "input_modes": ["text"],
            }
        ],
        "steps": [
            {
                "id": "sr_0195f3a0000070008123456789abcdef",
                "task_blueprint": "stp_0195f3a0000070008123456789abcdef",
                "input_mappings": {},
            }
        ],
    }
    issues2, _ = audit_workflows([wf2], {"stp_known_1234567890"})
    assert any(i.issue_type == "RAW_XML" for i in issues2)
    assert any(i.issue_type == "ORPHAN_STEP_BLUEPRINT" for i in issues2)


def test_audit_output_profiles_validation_error_and_xml_directive() -> None:
    """Test output profile schema validation error and raw XML in executive_summary_directive."""
    # 1. Schema validation error
    prof1 = {
        "id": "prf_invalid",
        "matrix_synthesis_groups": "not-a-list",
    }
    issues1, _ = audit_output_profiles([prof1], set())
    assert any(i.issue_type == "SCHEMA_VALIDATION_ERROR" for i in issues1)

    # 2. Raw XML in executive_summary_directive
    prof2 = {
        "id": "prf_0195f3a0000070008123456789abcdef",
        "workflow_id": "wor_0195f3a0000070008123456789abcdef",
        "name": {"translations": {"en": "Profile XML"}},
        "slug": "profile-xml",
        "description": {"translations": {"en": "Description"}},
        "executive_summary_directive": "<directive>Executive directive with XML</directive>",
        "matrix_synthesis_groups": [
            {
                "id": "grp_0195f3a0000070008123456789abcdef",
                "title": {"translations": {"en": "Group 1"}},
                "target_blocks": ["blk_0195f3a0000070008123456789abcdef"],
            }
        ],
    }
    issues2, _ = audit_output_profiles([prof2], set())
    assert any(i.issue_type == "RAW_XML" and "executive_summary_directive" in i.field_path for i in issues2)


def test_print_audit_report_formatting(capsys: pytest.CaptureFixture[str]) -> None:
    """Ensure print_audit_report prints both summary and detailed findings."""
    from scripts.audit_database_atoms import print_audit_report

    issue = AuditIssue(
        collection="prompt_blocks",
        entity_id="tda_demo_01",
        field_path="concept_description",
        issue_type="DEMO_ISSUE",
        message="Demo message for printing.",
        severity="WARNING",
    )
    report = FullDatabaseAuditReport(
        total_matrices=2,
        total_atoms=10,
        total_steps=5,
        total_workflows=2,
        total_profiles=1,
        issues=[issue],
        all_passed=True,
    )
    print_audit_report(report)
    captured = capsys.readouterr().out
    assert "QUORUM FULL DATABASE PROMPT VERIFICATION REPORT" in captured
    assert "Total Matrices Inspected:  2" in captured
    assert "[001] WARNING | prompt_blocks | tda_demo_01 | DEMO_ISSUE" in captured


def test_audit_database_atoms_all_exports() -> None:
    """Verify explicit public interface exports in __all__."""
    import scripts.audit_database_atoms as mod

    assert "__all__" in dir(mod)
    assert "AuditIssue" in mod.__all__
    assert "FullDatabaseAuditReport" in mod.__all__
    assert "SEED_COLLECTION_ALLOWED_PREFIXES" in mod.__all__
    assert "SEED_COLLECTION_REQUIRED_DISPLAY_FIELD" in mod.__all__
    assert "BANNED_ALTERNATIVE_PK_KEYS" in mod.__all__
    assert "audit_canonical_entity_ids" in mod.__all__
    assert "run_full_database_audit" in mod.__all__
    assert "main" in mod.__all__


def test_audit_canonical_entity_ids_positive_and_negative_partitions(tmp_path: Path) -> None:
    """Verify 7-collection canonical id, required display name/label, banned alternative PKs, and FK referential integrity."""
    from scripts.audit_database_atoms import (
        BANNED_ALTERNATIVE_PK_KEYS,
        SEED_COLLECTION_ALLOWED_PREFIXES,
        SEED_COLLECTION_REQUIRED_DISPLAY_FIELD,
        audit_canonical_entity_ids,
    )

    # Phase 3, Step 3 (REQ-009): Positive path across all 7 collections
    assert "wf" in SEED_COLLECTION_ALLOWED_PREFIXES["workflows"]
    assert SEED_COLLECTION_REQUIRED_DISPLAY_FIELD["prompt_blocks"] == "label"
    assert "node_id" in BANNED_ALTERNATIVE_PK_KEYS

    org_id = "org_0195f3a0000070008000000000000001"
    usr_id = "usr_0195f3a0000070008000000000000002"
    sys_reg_id = "sys_0195f3a0000070008000000000000003"
    sys_mcp_id = "sys_0195f3a0000070008000000000000004"
    blk_id = "blk_0195f3a0000070008123456789abcdef"
    blk_proto_id = "blk_0195f3a0000070008123456789abcde0"
    stp_id = "stp_0195f3a0000070008000000000000005"
    wf_id = "wf_0195f3a0000070008000000000000006"
    prf_id = "prf_0195f3a0000070008000000000000007"

    clean_7_col_seed = {
        "organizations": [{"id": org_id, "name": "Quorum Org"}],
        "users": [{"id": usr_id, "name": "Root User", "organization_id": org_id}],
        "system_config": [
            {"id": sys_reg_id, "name": "Default Model Registry"},
            {"id": sys_mcp_id, "name": "Tavily MCP Gateway"},
        ],
        "prompt_blocks": [
            _create_clean_matrix_block(block_id=blk_id),
            {
                "id": blk_proto_id,
                "category_id": "extraction_protocol",
                "slug": "clean-protocol",
                "label": {"translations": {"en": "Clean Protocol"}},
                "description": {"translations": {"en": "Desc"}},
                "protocol_instructions": "Extract exact sentences from the source document.",
            },
        ],
        "steps": [
            {
                "id": stp_id,
                "slug": "clean-step",
                "name": {"translations": {"en": "Clean Step"}},
                "type": "llm",
                "cognitive_tier": "fast",
                "criteria_block_ids": [blk_id],
                "extraction_protocol_block_id": blk_proto_id,
                "expected_inputs": ["document_text"],
            }
        ],
        "workflows": [
            {
                "id": wf_id,
                "slug": "clean-workflow",
                "name": {"translations": {"en": "Clean Workflow"}},
                "description": {"translations": {"en": "Workflow description"}},
                "status": "ACTIVE",
                "version": 1,
                "organization_id": org_id,
                "model_registry_id": sys_reg_id,
                "mcp_gateway_id": sys_mcp_id,
                "default_profile_id": prf_id,
                "historical_context_mode": "DISABLED",
                "expected_inputs": [
                    {
                        "input_key": "document_text",
                        "label": {"translations": {"en": "Document"}},
                        "description": {"translations": {"en": "Input doc"}},
                        "required": True,
                        "ai_description": "Source document for analysis.",
                        "input_modes": ["text"],
                    }
                ],
                "steps": [
                    {
                        "id": "sr_0195f3a0000070008000000000000008",
                        "task_blueprint": stp_id,
                        "input_mappings": {"document_text": "$inputs.document_text"},
                    }
                ],
            }
        ],
        "output_profiles": [
            {
                "id": prf_id,
                "workflow_id": wf_id,
                "organization_id": org_id,
                "name": {"translations": {"en": "Clean Output Profile"}},
                "slug": "clean-profile",
                "description": {"translations": {"en": "Profile description"}},
                "variance_target_block": blk_id,
                "user_role_target_block": blk_id,
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0195f3a0000070008000000000000009",
                        "title": {"translations": {"en": "Group 1"}},
                        "target_blocks": [blk_id],
                    }
                ],
            }
        ],
    }

    seed_path = tmp_path / "valid_7_col_seed.json"
    seed_path.write_text(json.dumps(clean_7_col_seed), encoding="utf-8")
    report = run_full_database_audit(seed_path)
    assert report.all_passed is True
    assert report.issues == []

    # Negative path 1: Invalid ID, wrong prefix, duplicate ID, banned alternative PK key, and missing canonical name/label
    bad_pk_and_name_data = {
        "organizations": [
            {"id": org_id, "name": "Org 1"},
            {"id": org_id, "name": "   ", "node_id": "nod_legacy"},
        ],
        "users": [{"id": "usr_legacy_slug", "name": ""}],
        "system_config": [{"id": sys_reg_id}],
        "prompt_blocks": [{"id": blk_id, "label": {"translations": {}}}],
        "steps": [{"id": stp_id, "name": "not-an-i18n-dict"}],
        "workflows": [
            {"id": stp_id, "name": {"translations": {"en": "Wrong Prefix Workflow"}}, "model_registry_id": sys_reg_id}
        ],
        "output_profiles": [],
    }
    neg1_issues = audit_canonical_entity_ids(bad_pk_and_name_data)
    neg1_types = {i.issue_type for i in neg1_issues}
    assert "INVALID_CANONICAL_ID" in neg1_types
    assert "DUPLICATE_CANONICAL_ID" in neg1_types
    assert "BANNED_ALTERNATIVE_PK_FIELD" in neg1_types
    assert "MISSING_CANONICAL_NAME" in neg1_types

    # Negative path 2: Relational slug or orphan foreign keys across users, workflows, and output_profiles
    bad_fk_data = {
        "organizations": [{"id": org_id, "name": "Org 1"}],
        "users": [{"id": usr_id, "name": "User 1", "organization_id": "org_unknown"}],
        "system_config": [{"id": sys_reg_id, "name": "Registry"}],
        "prompt_blocks": [_create_clean_matrix_block(block_id=blk_id)],
        "steps": [],
        "workflows": [
            {
                "id": wf_id,
                "name": {"translations": {"en": "Workflow"}},
                "organization_id": "org_missing",
                "model_registry_id": "default_model_registry",
                "mcp_gateway_id": "default_mcp_gateway",
                "default_profile_id": "prf_missing",
            }
        ],
        "output_profiles": [
            {
                "id": prf_id,
                "name": {"translations": {"en": "Profile"}},
                "workflow_id": "wf_missing",
                "organization_id": "org_missing",
                "variance_target_block": "blk_missing_slug",
                "user_role_target_block": "blk_missing_role_slug",
            }
        ],
    }
    neg2_issues = audit_canonical_entity_ids(bad_fk_data)
    neg2_types = {i.issue_type for i in neg2_issues}
    assert "ORPHAN_ORGANIZATION_ID" in neg2_types
    assert "ORPHAN_MODEL_REGISTRY_ID" in neg2_types
    assert "ORPHAN_MCP_GATEWAY_ID" in neg2_types
    assert "ORPHAN_DEFAULT_PROFILE_ID" in neg2_types
    assert "ORPHAN_WORKFLOW_ID" in neg2_types
    assert "ORPHAN_TARGET_BLOCK" in neg2_types


def test_run_full_database_audit_negative_and_boundary_partitions(tmp_path: Path) -> None:
    """Verify AppException on missing/corrupt seed files, non-object JSON roots, and ISTQB BVA bounds."""
    # Negative Case 1: Non-existent file raises AppException(VALIDATION_FAILED)
    missing_file = tmp_path / "missing_seed_data.json"
    with pytest.raises(AppException) as exc_missing:
        run_full_database_audit(missing_file)
    assert exc_missing.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # Negative Case 2: Malformed JSON syntax raises AppException(VALIDATION_FAILED)
    corrupt_json_file = tmp_path / "corrupt_syntax.json"
    corrupt_json_file.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(AppException) as exc_syntax:
        run_full_database_audit(corrupt_json_file)
    assert exc_syntax.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # Negative Case 3: Non-object JSON root (list instead of mapping) raises AppException(VALIDATION_FAILED)
    list_root_file = tmp_path / "list_root.json"
    list_root_file.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(AppException) as exc_root:
        run_full_database_audit(list_root_file)
    assert exc_root.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # ISTQB Boundary Value Analysis on concept_description (min=10, max=180) and extraction_rule (min=10)
    b_concept_min_minus_1 = _create_clean_matrix_block()
    b_concept_min_minus_1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "A" * 9
    issues_concept_below, _, _ = audit_prompt_blocks([b_concept_min_minus_1])
    assert any(i.issue_type == "SCHEMA_VALIDATION_ERROR" for i in issues_concept_below)

    b_rule_min_minus_1 = _create_clean_matrix_block()
    b_rule_min_minus_1["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = "B" * 9
    issues_rule_below, _, _ = audit_prompt_blocks([b_rule_min_minus_1])
    assert any(i.issue_type == "EMPTY_EXTRACTION_RULE" for i in issues_rule_below)

    b_exact_bounds = _create_clean_matrix_block()
    b_exact_bounds["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "A" * 180
    b_exact_bounds["scales"][0]["claims"][0]["tda_assertions"][0]["extraction_rule"] = "B" * 10
    issues_exact, _, _ = audit_prompt_blocks([b_exact_bounds])
    assert not any(i.issue_type in {"SHORT_CONCEPT", "BLOATED_CONCEPT", "EMPTY_EXTRACTION_RULE"} for i in issues_exact)

    b_max_plus_1 = _create_clean_matrix_block()
    b_max_plus_1["scales"][0]["claims"][0]["tda_assertions"][0]["concept_description"] = "A" * 181
    issues_above, _, _ = audit_prompt_blocks([b_max_plus_1])
    assert any(i.issue_type == "BLOATED_CONCEPT" for i in issues_above)
