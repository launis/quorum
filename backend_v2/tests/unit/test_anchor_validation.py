from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService, SemanticFallbackResponse


def test_normalization() -> None:
    """Test Phase 1 Normalization."""
    # Empty cases
    assert AnchorValidationService.normalize_text("") == ""

    # Lowercasing and regex cleanup
    assert AnchorValidationService.normalize_text("Hello World! 123") == "helloworld123"
    assert AnchorValidationService.normalize_text("Tämä on testi.") == "tmontesti"  # ä removed by [^a-z0-9]
    # NFKC testing
    assert AnchorValidationService.normalize_text("ﬃ") == "ffi"  # ligature


def test_fuzzy_match() -> None:
    """Test Phase 2 RapidFuzz O(N) anchoring."""
    pdf_text = "This is a long document about various things. The exact quote we want is here."

    # Exact match
    assert AnchorValidationService.fuzzy_match(pdf_text, "The exact quote we want is here.") is True

    # Fuzzy match (minor typo)
    assert AnchorValidationService.fuzzy_match(pdf_text, "The ecxat quote we want is here") is True

    # Non-match
    assert AnchorValidationService.fuzzy_match(pdf_text, "Something completely different.") is False

    # Empty cases
    assert AnchorValidationService.fuzzy_match("", "quote") is False
    assert AnchorValidationService.fuzzy_match(pdf_text, "") is False


@pytest.mark.asyncio
async def test_validate_evidence_fast_path() -> None:
    """Test the deterministic RapidFuzz path avoiding LLM."""
    mock_executor = MagicMock(spec=LLMTaskExecutor)
    service = AnchorValidationService(executor=mock_executor)

    pdf_text = "This is a long document. Very important evidence is right here. And some more."
    quote = "Very important evidence is right here"

    is_valid, final_quote = await service.validate_evidence(pdf_text, quote, repo=None)

    assert is_valid is True
    assert final_quote == quote
    mock_executor.execute_structured_task.assert_not_called()


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.anchor_validation_service.LLMClient.from_strategy", new_callable=AsyncMock)
async def test_validate_evidence_semantic_fallback_success(mock_from_strategy: AsyncMock) -> None:
    """Test the LLM semantic cascade when fuzzy match fails but LLM approves."""
    mock_executor = AsyncMock(spec=LLMTaskExecutor)
    service = AnchorValidationService(executor=mock_executor)

    # Mocking the successful fallback response
    mock_executor.execute_structured_task.return_value = (
        SemanticFallbackResponse(is_equivalent=True),
        MagicMock(),  # Usage mock
    )

    pdf_text = "The document says that the user must log in before accessing the dashboard."
    quote = "Authentication is required to view the main panel."

    is_valid, final_quote = await service.validate_evidence(pdf_text, quote, repo=None)

    assert is_valid is True
    assert final_quote == quote
    mock_executor.execute_structured_task.assert_called_once()


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.anchor_validation_service.LLMClient.from_strategy", new_callable=AsyncMock)
async def test_validate_evidence_semantic_fallback_failure(mock_from_strategy: AsyncMock) -> None:
    """Test the LLM semantic cascade when both fuzzy match and LLM fail (Route to DLQ)."""
    mock_executor = AsyncMock(spec=LLMTaskExecutor)
    service = AnchorValidationService(executor=mock_executor)

    # Mocking the failed fallback response
    mock_executor.execute_structured_task.return_value = (
        SemanticFallbackResponse(is_equivalent=False),
        MagicMock(),  # Usage mock
    )

    pdf_text = "The system is currently operational and green."
    quote = "The system has encountered a critical failure."

    is_valid, final_quote = await service.validate_evidence(pdf_text, quote, repo=None)

    assert is_valid is False
    assert final_quote == ""
    mock_executor.execute_structured_task.assert_called_once()
