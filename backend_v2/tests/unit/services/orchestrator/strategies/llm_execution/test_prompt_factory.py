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
    compiler.compile_blind_system_instruction.return_value = "Blind Instruction"
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
                "scale_min": 1,
                "scale_max": 5,
                "scales": [
                    {
                        "score": 1,
                        "ai_label": "Scale 1",
                        "claims": [
                            {
                                "label": {"default_locale": "en", "translations": {"en": "Claim 1", "fi": "Väite 1"}},
                                "ai_description": "Claim 1 Desc",
                                "tda_assertions": [
                                    {
                                        "tda_id": "tda_11111111111111111111111111111111",
                                        "concept_description": "Atom 1",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    },
                                    {
                                        "tda_id": "tda_22222222222222222222222222222222",
                                        "concept_description": "Atom 2",
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

    assert "You are a highly accurate, structured evaluation assistant." in payload.base_system_prompt
    assert "Static Instructions" in payload.base_system_prompt
    assert "Blind Instruction" in payload.base_system_prompt
    assert "MCP Instruction" in payload.base_system_prompt

    assert "context" in payload.user_payload
    assert "RUNTIME_AWARENESS" in payload.user_payload
    assert "Dynamic Instructions" in payload.user_payload

    # Check atom hashing
    assert len(payload.atom_to_block_ids) == 2


def test_prompt_factory_flat_instruction_no_blind_contamination(mock_compiler: MagicMock) -> None:
    """Test that when has_shuffled_atoms=False, blind_instruction is not compiled/injected."""
    from backend_v2.models.v2_core import PromptBlock

    criteria_blocks = [
        PromptBlock.model_validate(
            {
                "id": "blk_12345678901234567890123456789012",
                "slug": "test_slug",
                "label": {"default_locale": "en", "translations": {"en": "Test Label", "fi": "Testi"}},
                "description": {"default_locale": "en", "translations": {"en": "Test Desc", "fi": "Testi"}},
                "type": "string",
                "category_id": "system_rule",
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
        has_shuffled_atoms=False,
    )

    assert "You are a highly accurate, structured evaluation assistant." in payload.base_system_prompt
    assert "Static Instructions" in payload.base_system_prompt
    assert "Blind Instruction" not in payload.base_system_prompt
    assert "MCP Instruction" in payload.base_system_prompt


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
