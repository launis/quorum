import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import Step, PromptBlock, I18nText
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory


def test_step_validation_fails_without_criteria_or_protocol() -> None:
    """Test 1: Verify that a Step object without criteria blocks or without an extraction protocol block fails validation at construction."""
    # 1. Missing criteria_block_ids
    with pytest.raises(ValidationError) as exc_info:
        Step(
            id="stp_1234567890123456",
            slug="test_step_missing_criteria",
            name=I18nText(default_locale="en", translations={"en": "Test Step", "fi": "Testi"}),
            type="llm",
            model_strategy="fast",
            extraction_protocol_block_id="blk_a1b2c3d4e5f60011",
            criteria_block_ids=[],  # Empty list
        )
    assert "must define at least one criteria_block_id" in str(exc_info.value)

    # 2. Missing extraction_protocol_block_id
    with pytest.raises(ValidationError) as exc_info:
        Step(
            id="stp_1234567890123457",
            slug="test_step_missing_protocol",
            name=I18nText(default_locale="en", translations={"en": "Test Step", "fi": "Testi"}),
            type="llm",
            model_strategy="fast",
            extraction_protocol_block_id=None,  # Missing protocol
            criteria_block_ids=["blk_a1b2c3d4e5f60012"],
        )
    assert "must define a valid extraction_protocol_block_id" in str(exc_info.value)


def test_prompt_factory_build_integrates_decoupled_blocks() -> None:
    """Test 2: Verify that PromptFactory.build properly integrates role_block.ai_description and protocol_block.ai_description into the base_system_prompt."""
    compiler = MagicMock()
    compiler.compile_static_instructions.return_value = "Compiled Criteria Instructions"
    compiler.compile_dynamic_instructions.return_value = "Dynamic Instructions"
    compiler.compile_blind_system_instruction.return_value = "Blind Instruction"
    compiler.generate_mcp_instruction.return_value = "MCP Instruction"
    compiler.build_xml_context.return_value = "<context></context>"

    role_block = PromptBlock.model_validate(
        {
            "id": "blk_1122334455667788",
            "slug": "role_critic",
            "label": {"default_locale": "en", "translations": {"en": "Role Critic", "fi": "Kriitikko"}},
            "description": {"default_locale": "en", "translations": {"en": "Role Desc", "fi": "Kuvaus"}},
            "ai_description": "ROLE: ANTAGONISTIC PROSECUTOR",
            "category_id": "role",
            "type": "string",
        }
    )

    protocol_block = PromptBlock.model_validate(
        {
            "id": "blk_9988776655443322",
            "slug": "extraction_protocol",
            "label": {"default_locale": "en", "translations": {"en": "Extraction Protocol", "fi": "Protokolla"}},
            "description": {"default_locale": "en", "translations": {"en": "Protocol Desc", "fi": "Kuvaus"}},
            "ai_description": "EXTRACTION INSTRUCTION: Locate raw facts and return exact quotes.",
            "category_id": "instruction",
            "type": "instruction",
        }
    )

    criteria_blocks = [
        PromptBlock.model_validate(
            {
                "id": "blk_12345678901234567890123456789012",
                "slug": "criteria_matrix",
                "label": {"default_locale": "en", "translations": {"en": "Criteria Matrix", "fi": "Matriisi"}},
                "description": {"default_locale": "en", "translations": {"en": "Criteria Desc", "fi": "Kuvaus"}},
                "ai_description": "CRITERIA: Evaluate Toulmin logic.",
                "category_id": "matrix",
                "type": "string",
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
                                        "tda_id": "tda_1111111111111111",
                                        "ai_rule_description": "Atom 1",
                                        "inverse_evidence": False,
                                        "aggregation_mode": "EXISTS",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        )
    ]

    payload = PromptFactory.build(
        compiler=compiler,
        role_block=role_block,
        protocol_block=protocol_block,
        criteria_blocks=criteria_blocks,
        target_locale="en",
        effective_mcp_tools=None,
        input_mappings={},
        llm_context_data={},
        expected_inputs=None,
        has_shuffled_atoms=True,
    )

    # 1. Assert role persona is integrated
    assert "ROLE: ANTAGONISTIC PROSECUTOR" in payload.base_system_prompt

    # 2. Assert extraction protocol is integrated
    assert "EXTRACTION INSTRUCTION: Locate raw facts and return exact quotes." in payload.base_system_prompt

    # 3. Assert criteria compiled instructions are integrated
    assert "Compiled Criteria Instructions" in payload.base_system_prompt
