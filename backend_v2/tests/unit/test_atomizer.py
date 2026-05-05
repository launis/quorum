from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, PromptBlock
from backend_v2.services.orchestrator.atomizer import AtomizationSchema, PromptAtomizer


@pytest.fixture
def sample_block() -> PromptBlock:
    return PromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test-block",
        label=I18nText(default_locale="en", translations={"en": "Test Label"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        category_id="test_cat",
        type=BlockDataType.STRING,
        scale_min=1,
        scale_max=5,
        scales=[
            MatrixScale(
                score=1,
                ai_label="FAIL",
                claims=[
                    MatrixClaim(
                        label=I18nText(default_locale="en", translations={"en": "This is a claim to atomize."}),
                        ai_description="Evaluate something.",
                        micro_atoms=None,
                    )
                ],
            )
        ],
    )


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.atomizer.LLMClient")
async def test_atomize_prompt_block_success(mock_llm_client_class: AsyncMock, sample_block: PromptBlock) -> None:
    # Setup mock LLM Client
    mock_client = AsyncMock()

    # Needs exactly 15 micro_atoms to satisfy Pydantic Schema
    mock_res = AtomizationSchema(micro_atoms=[f"atom_{str(i).zfill(10)}" for i in range(15)], rubric_cot="Test Rubric")
    mock_client.run_structured_task = AsyncMock(return_value=(mock_res, {}))
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client)

    result = await PromptAtomizer.atomize_prompt_block(sample_block, is_test=True)

    # Check if a new block was returned
    assert result is not sample_block
    assert result.scales is not None
    assert result.scales[0].claims[0].micro_atoms is not None
    assert len(result.scales[0].claims[0].micro_atoms) == 15
    assert result.scales[0].claims[0].micro_atoms[0] == "atom_0000000000"


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.atomizer.LLMClient")
async def test_atomize_prompt_block_missing_en_translation(
    mock_llm_client_class: AsyncMock, sample_block: PromptBlock
) -> None:
    mock_llm_client_class.from_strategy = AsyncMock()
    # Emulate missing translation but bypass Pydantic initial validation to test atomizer logic directly
    assert sample_block.scales is not None
    sample_dict = sample_block.model_dump()
    sample_dict["scales"][0]["claims"][0]["label"]["translations"] = {"fi": "Finnish Text"}
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        PromptBlock.model_validate(sample_dict)

    assert "I18nText must contain a valid English ('en') translation" in str(exc_info.value)
