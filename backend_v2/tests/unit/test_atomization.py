import pytest

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.models.enums import BlockDataType
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, PromptBlock
from backend_v2.services.orchestrator.atomizer import PromptAtomizer


@pytest.mark.asyncio
async def test_compile_atomizer_adds_15_atoms() -> None:
    """Tests that Kääntäjä-AI deeply atomizes claims if micro_atoms is missing."""
    repo = UnifiedWorkflowRepository(driver=None)  # type: ignore[arg-type]

    # Generate a block missing atoms
    block = PromptBlock(
        id="blk_testabcd12345678",
        slug="test-block",
        label=I18nText(default_locale="en", translations={"en": "Test Label"}),
        description=I18nText(default_locale="en", translations={"en": "Test Description"}),
        category_id="general",
        type=BlockDataType.FLOAT,
        scale_min=1,
        scale_max=2,
        scales=[
            MatrixScale(
                score=1,
                ai_label="POOR",
                claims=[
                    MatrixClaim(
                        label=I18nText(default_locale="en", translations={"en": "Claim to atomize"}),
                        ai_description="Instruction...",
                        micro_atoms=None,
                    )
                ],
            )
        ],
    )

    # The atomizer internally uses 'atomize_mock' explicitly handled in mock_data.py
    # via run_structured_task is_test wrapper. Or we can just rely on the LLMClient's
    # 'mock' identity routing.
    result = await PromptAtomizer.atomize_prompt_block(block, repository=repo, is_test=True)

    assert result.scales is not None
    assert len(result.scales) == 1
    assert len(result.scales[0].claims) == 1
    claim = result.scales[0].claims[0]

    assert claim.micro_atoms is not None
    assert len(claim.micro_atoms) == 15
    assert claim.micro_atoms[0] == "atom1"
    assert claim.micro_atoms[-1] == "atom15"
