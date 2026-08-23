from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import PromptBlockCategory
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory


@pytest.fixture
def mock_compiler() -> MagicMock:
    compiler = MagicMock()
    compiler.compile_static_instructions.return_value = "Static Instructions"
    compiler.compile_dynamic_instructions.return_value = "Dynamic Instructions"

    compiler.generate_mcp_instruction.return_value = "MCP Instruction"
    compiler.build_xml_context.return_value = "<context></context>"
    return compiler


def test_prompt_factory_build_success(mock_compiler: MagicMock) -> None:
    """Test successful compilation of PromptPayload."""
    from backend_v2.models.v2_core import PromptBlock

    criteria_blocks = [
        PromptBlock.model_validate(
            {
                "id": "blk_12345678901234567890123456789012",
                "slug": "test_slug",
                "label": {"default_locale": "en", "translations": {"en": "Test Label", "fi": "Testi"}},
                "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Testi"}},
                "type": "string",
                "category_id": "matrix",
                "scales": [
                    {
                        "score": 1,
                        "ai_label": "Scale 1",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Väite 1"}},
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_11111111111111111111111111111111",
                                        "concept_description": "Atom 1 concept description",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    },
                                    {
                                        "tda_id": "tda_22222222222222222222222222222222",
                                        "concept_description": "Atom 2 concept description",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    },
                                ],
                            },
                        ],
                    }
                ],
            }
        )
    ]

    payload = PromptFactory.build(
        compiler=mock_compiler,
        role_block=None,
        protocol_block=None,
        execution_persona_block=None,
        criteria_blocks=criteria_blocks,
        target_locale="en",
        effective_mcp_tools=None,
        input_mappings={},
        llm_context_data={},
        expected_inputs=None,
        has_shuffled_atoms=True,
    )

    # Layer 1 Global Mandates & Persona in base_system_prompt
    assert "<global_system_mandates>" in payload.base_system_prompt
    assert "<global_system_mandates>" not in payload.user_payload
    assert "You are a highly accurate, structured evaluation assistant." in payload.base_system_prompt
    assert "Static Instructions" in payload.base_system_prompt

    assert "MCP Instruction" in payload.base_system_prompt

    assert "context" in payload.user_payload
    assert "RUNTIME_AWARENESS" in payload.user_payload
    assert "Dynamic Instructions" in payload.user_payload

    # Check atom hashing
    assert len(payload.atom_to_block_ids) == 2


def test_prompt_factory_missing_tda_assertions(mock_compiler: MagicMock) -> None:
    """Test Fail-Fast when tda_assertions are missing."""
    from backend_v2.models.v2_core import MatrixClaim, MatrixScale, PromptBlock

    criteria_blocks = [
        PromptBlock.model_construct(  # type: ignore[call-arg]
            id="blk_12345678901234567890123456789012",
            category_id=PromptBlockCategory.MATRIX,
            scales=[
                MatrixScale.model_construct(  # type: ignore[call-arg]
                    score=1,
                    claims=[MatrixClaim.model_construct(tda_assertions=[])],  # type: ignore[call-arg]
                )
            ],
        )
    ]

    with pytest.raises(AppException) as exc_info:
        PromptFactory.build(
            compiler=mock_compiler,
            role_block=None,
            protocol_block=None,
            execution_persona_block=None,
            criteria_blocks=criteria_blocks,
            target_locale="en",
            effective_mcp_tools=None,
            input_mappings={},
            llm_context_data={},
            expected_inputs=None,
            has_shuffled_atoms=True,
        )

    assert exc_info.value.status_code == 500
    assert "missing mandatory 'tda_assertions'" in str(exc_info.value.message)


def test_prompt_factory_includes_language_mandate(mock_compiler: MagicMock) -> None:
    """Test that LANGUAGE_MANDATE is included in the user payload."""
    payload = PromptFactory.build(
        compiler=mock_compiler,
        role_block=None,
        protocol_block=None,
        execution_persona_block=None,
        criteria_blocks=[],
        target_locale="fi",
        effective_mcp_tools=None,
        input_mappings={},
        llm_context_data={},
        expected_inputs=None,
        has_shuffled_atoms=False,
    )

    # The LANGUAGE_MANDATE must be injected into the user_payload via linguistic_directives
    assert "CRITICAL LANGUAGE MANDATE" in payload.user_payload


def test_prompt_factory_prompt_purity_assertion(mock_compiler: MagicMock) -> None:
    """Test that mechanical_anchors are isolated in user_payload and not in base_system_prompt."""
    from backend_v2.models.enums import PromptBlockCategory
    from backend_v2.models.v2_core import PromptBlock

    criteria_blocks = [
        PromptBlock.model_construct(  # type: ignore[call-arg]
            id="blk_grounded",
            slug="matrix_causal_analyst",
            category_id=PromptBlockCategory.MATRIX,
            scales=[],
        )
    ]
    llm_context_data = {
        "word_count": 150,
        "say_do_gap": 0.5,
        "automation_bias": 0.2,
        "performative_phrases": ["test phrase"],
    }

    payload = PromptFactory.build(
        compiler=mock_compiler,
        role_block=None,
        protocol_block=None,
        execution_persona_block=None,
        criteria_blocks=criteria_blocks,
        target_locale="en",
        effective_mcp_tools=None,
        input_mappings={},
        llm_context_data=llm_context_data,
        expected_inputs=None,
        has_shuffled_atoms=False,
    )

    assert "<mechanical_anchors>" not in payload.base_system_prompt
    assert "<mechanical_anchors>" in payload.user_payload
    assert "<word_count>150</word_count>" in payload.user_payload


def test_prompt_factory_missing_anchors_data(mock_compiler: MagicMock) -> None:
    """Test that missing anchor data defaults correctly and maintains prompt purity."""
    from backend_v2.models.enums import PromptBlockCategory
    from backend_v2.models.v2_core import PromptBlock

    criteria_blocks = [
        PromptBlock.model_construct(  # type: ignore[call-arg]
            id="blk_grounded",
            slug="matrix_causal_analyst",
            category_id=PromptBlockCategory.MATRIX,
            scales=[],
        )
    ]

    payload = PromptFactory.build(
        compiler=mock_compiler,
        role_block=None,
        protocol_block=None,
        execution_persona_block=None,
        criteria_blocks=criteria_blocks,
        target_locale="en",
        effective_mcp_tools=None,
        input_mappings={},
        llm_context_data={},
        expected_inputs=None,
        has_shuffled_atoms=False,
    )

    assert "<mechanical_anchors>" not in payload.base_system_prompt
    assert "<mechanical_anchors>" in payload.user_payload
    assert "<word_count>0</word_count>" in payload.user_payload
    assert "<say_do_gap>0.0</say_do_gap>" in payload.user_payload
    assert "<automation_bias>0.0</automation_bias>" in payload.user_payload
    assert "<phrase_count>0</phrase_count>" in payload.user_payload


def test_prompt_factory_has_zero_reflection_via_ast() -> None:
    """AST Guardrail: Verify that PromptFactory contains zero hasattr or getattr calls."""
    import ast
    from pathlib import Path

    import backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory as pf_mod

    prompt_factory_path = Path(pf_mod.__file__)
    assert prompt_factory_path.exists(), f"Target file {prompt_factory_path} does not exist"

    tree = ast.parse(prompt_factory_path.read_text(encoding="utf-8"))

    banned_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("hasattr", "getattr", "setattr"):
                banned_calls.append(f"{node.func.id} on line {node.lineno}")

    assert len(banned_calls) == 0, f"Found banned reflection calls in prompt_factory.py: {banned_calls}"
