"""Unit tests for SourceVerificationService."""

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.mcp import TavilySearchResult
from backend_v2.models.domain.source_verification import (
    SourceClaimDTO,
    SourceVerificationStatus,
)
from backend_v2.models.dtos.source_extraction_schema import SourceExtractionResponseSchema
from backend_v2.services.source_verification_service import SourceVerificationService


@pytest.fixture
def mock_task_executor() -> AsyncMock:
    """Returns a mock LLMTaskExecutor."""
    executor = AsyncMock()
    executor.llm_client = AsyncMock()
    return executor


@pytest.fixture
def service(mock_task_executor: AsyncMock) -> SourceVerificationService:
    """Returns a SourceVerificationService with a mocked executor."""
    return SourceVerificationService(llm_task_executor=mock_task_executor)


@pytest.mark.asyncio
async def test_extract_source_claims_success(service: SourceVerificationService, mock_task_executor: AsyncMock) -> None:
    """Tests successful extraction of claims."""
    mock_response = SourceExtractionResponseSchema(
        claims=[
            SourceClaimDTO(claim_text="Test claim 1", institution_name="Test Inst", publication_year=2024),
            SourceClaimDTO(claim_text="Test claim 2"),
        ]
    )
    mock_task_executor.execute_structured_task.return_value = (mock_response, None)

    claims = await service._extract_source_claims("Some text with claims")

    assert len(claims) == 2
    assert claims[0].institution_name == "Test Inst"
    mock_task_executor.execute_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_extract_source_claims_empty_text(service: SourceVerificationService) -> None:
    """Tests that empty text returns empty list without calling LLM."""
    claims = await service._extract_source_claims("   ")
    assert claims == []


@pytest.mark.asyncio
async def test_extract_source_claims_failure(service: SourceVerificationService, mock_task_executor: AsyncMock) -> None:
    """Tests failure during extraction raises AppException."""
    mock_task_executor.execute_structured_task.side_effect = Exception("LLM Error")

    with pytest.raises(AppException) as exc:
        await service._extract_source_claims("Test text")

    assert exc.value.status_code == 502


@pytest.mark.asyncio
@patch("backend_v2.services.source_verification_service.tavily_search")
async def test_verify_single_claim_verified(
    mock_tavily: AsyncMock, service: SourceVerificationService, mock_task_executor: AsyncMock
) -> None:
    """Tests verifying a single claim successfully."""
    claim = SourceClaimDTO(claim_text="Test claim 1", institution_name="Inst A", publication_year=2023)

    mock_tavily.return_value = TavilySearchResult(
        query="Verify this claim: Test claim 1 by Inst A (2023)",
        answer="Yes, it is true.",
        source_urls=["http://test.com"],
        raw_content="Content",
        duration_ms=100,
    )
    mock_task_executor.execute_chat_task.return_value = ("VERIFIED", None)

    result = await service._verify_single_claim(claim)

    assert result.status == SourceVerificationStatus.VERIFIED
    assert result.source_urls == ["http://test.com"]
    assert result.tavily_answer == "Yes, it is true."
    mock_tavily.assert_called_once()


@pytest.mark.asyncio
@patch("backend_v2.services.source_verification_service.tavily_search")
async def test_verify_single_claim_inconclusive_fallback(
    mock_tavily: AsyncMock, service: SourceVerificationService
) -> None:
    """Tests that a failure in search results in INCONCLUSIVE status."""
    claim = SourceClaimDTO(claim_text="Test claim")
    mock_tavily.side_effect = AppException(message="Search timeout", status_code=502, details={})

    result = await service._verify_single_claim(claim)

    assert result.status == SourceVerificationStatus.INCONCLUSIVE


@pytest.mark.asyncio
@patch("backend_v2.services.source_verification_service.tavily_search")
async def test_run_full_verification(
    mock_tavily: AsyncMock, service: SourceVerificationService, mock_task_executor: AsyncMock
) -> None:
    """Tests the full orchestration method."""
    # 1. Mock Extraction
    mock_task_executor.execute_structured_task.return_value = (
        SourceExtractionResponseSchema(
            claims=[
                SourceClaimDTO(claim_text="Claim A"),
                SourceClaimDTO(claim_text="Claim B"),
            ]
        ),
        None,
    )

    # 2. Mock Search (called twice concurrently, we just return a static result)
    mock_tavily.return_value = TavilySearchResult(
        query="test", answer="answer", source_urls=[], raw_content="raw", duration_ms=10
    )

    # 3. Mock Evaluation (1 VERIFIED, 1 HALLUCINATION)
    mock_task_executor.execute_chat_task.side_effect = [("VERIFIED", None), ("HALLUCINATION", None)]

    result = await service.run_full_verification("Some document")

    assert result.total_claims == 2
    assert result.verified_count == 1
    assert result.hallucination_count == 1
    assert len(result.claims) == 2
