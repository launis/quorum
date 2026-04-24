from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
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
    criteria_blocks = [
        {
            "id": "block1",
            "category_id": "matrix",
            "scales": [
                {
                    "claims": [
                        {"micro_atoms": ["Atom 1", "Atom 2"]},
                    ]
                }
            ],
        }
    ]

    payload = PromptFactory.build(
        compiler=mock_compiler,
        criteria_blocks=criteria_blocks,
        target_locale="en",
        effective_mcp_tools=None,
        input_mappings={},
        llm_context_data={},
        expected_inputs=None,
    )

    assert "Complete the evaluation according to the provided schema." in payload.base_system_prompt
    assert "Static Instructions" in payload.base_system_prompt
    assert "Blind Instruction" in payload.base_system_prompt
    assert "MCP Instruction" in payload.base_system_prompt

    assert "<context></context>" in payload.user_payload
    assert "--- RUNTIME AWARENESS ---" in payload.user_payload
    assert "Dynamic Instructions" in payload.user_payload

    # Check atom hashing
    assert len(payload.atom_to_block_ids) == 2


def test_prompt_factory_missing_micro_atoms(mock_compiler: MagicMock) -> None:
    """Test Fail-Fast when micro_atoms are missing."""
    criteria_blocks = [
        {
            "id": "block1",
            "category_id": "matrix",
            "scales": [
                {
                    "claims": [
                        {"micro_atoms": []},  # Empty micro atoms should crash
                    ]
                }
            ],
        }
    ]

    with pytest.raises(AppException) as exc_info:
        PromptFactory.build(
            compiler=mock_compiler,
            criteria_blocks=criteria_blocks,
            target_locale="en",
            effective_mcp_tools=None,
            input_mappings={},
            llm_context_data={},
            expected_inputs=None,
        )

    assert exc_info.value.status_code == 500
    assert "missing mandatory 'micro_atoms'" in str(exc_info.value.message)
