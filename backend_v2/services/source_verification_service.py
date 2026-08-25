"""Source Verification Service.

Responsible for extracting source claims from text and verifying them via Tavily AI.
Adheres strictly to the SRP God Method Mandate, Single Source of Truth, and Pydantic Strict Nirvana.
"""

import asyncio
import html
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.mcp import TavilySearchResult
from backend_v2.models.domain.source_verification import (
    SourceClaimDTO,
    SourceVerificationResultDTO,
    SourceVerificationStatus,
    VerifiedSourceDTO,
)
from backend_v2.models.dtos.source_extraction_schema import SourceExtractionResponseSchema
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.tavily_search_client import tavily_search
from backend_v2.settings import get_settings

if TYPE_CHECKING:
    from backend_v2.database.interfaces import IComponentRepository, ISystemRepository
    from backend_v2.llm.client import LLMClient

__all__ = ["SourceVerificationService"]

logger = logging.getLogger(__name__)

# Cut off text length to avoid token limit explosions in fast models
MAX_EXTRACTION_CHARS: int = 30000

# Static English XML system instructions for 100% prompt caching efficiency
_EXTRACTION_SYSTEM_INSTRUCTION: str = (
    "<system_directive>\n"
    "<objective>Read the provided document and extract all explicit references to external sources, research, studies, guidelines, or institutions.</objective>\n"
    "<role>Expert Fact-Checker</role>\n"
    "<rules>\n"
    "  <rule>Extract the exact claim being attributed to external entities.</rule>\n"
    "  <rule>Do not include internal cross-references.</rule>\n"
    "  <rule>Return an empty list if none are found.</rule>\n"
    "</rules>\n"
    "</system_directive>"
)

_VERIFICATION_SYSTEM_INSTRUCTION: str = (
    "<system_directive>\n"
    "<objective>Compare the original source claim against the search results provided.</objective>\n"
    "<role>Expert Fact-Checker</role>\n"
    "<rules>\n"
    "  <rule>Determine if the claim is VERIFIED (supported by search), HALLUCINATION (contradicted or clearly fabricated), or INCONCLUSIVE (not enough info found).</rule>\n"
    "  <rule>Return ONLY the exact word: VERIFIED, HALLUCINATION, or INCONCLUSIVE.</rule>\n"
    "</rules>\n"
    "</system_directive>"
)


class SourceVerificationService:
    """Service handling the extraction and verification of source claims."""

    def __init__(
        self,
        llm_task_executor: LLMTaskExecutor | None = None,
        llm_client: LLMClient | None = None,
        comp_repo: IComponentRepository | None = None,
        system_repo: ISystemRepository | None = None,
    ) -> None:
        """Initializes the service.

        Args:
            llm_task_executor: Injected executor. If None, it initializes via LLMTaskExecutor.
            llm_client: Injected LLM client. If None, it loads via strategy registry.
            comp_repo: Optional component repository for strategy lookup.
            system_repo: Optional system repository for strategy lookup.
        """
        self.task_executor: LLMTaskExecutor | None = llm_task_executor
        self.llm_client: LLMClient | None = llm_client
        self.comp_repo: IComponentRepository | None = comp_repo
        self.system_repo: ISystemRepository | None = system_repo

    async def _ensure_initialized(self) -> None:
        if self.task_executor and self.llm_client:
            return

        from backend_v2.llm.client import LLMClient
        from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

        if not self.llm_client:
            repo = self.system_repo or self.comp_repo
            self.llm_client = await LLMClient.from_strategy("fast", repository=repo)
        if not self.task_executor:
            self.task_executor = LLMTaskExecutor(PromptCompiler())

    async def _extract_source_claims(self, text: str) -> list[SourceClaimDTO]:
        """Extracts source claims from text using structured LLM output.

        Args:
            text: Raw input text.

        Returns:
            List of SourceClaimDTO objects.

        Raises:
            AppException: If parsing fails or the LLM request crashes.
        """
        if not text or len(text.strip()) < get_settings().min_verifiable_text_length:
            return []

        await self._ensure_initialized()

        # Safe truncation and XML escaping
        safe_text = html.escape(text[:MAX_EXTRACTION_CHARS].strip())
        user_message = f"<source_data>\n{safe_text}\n</source_data>"

        try:
            messages = [
                {"role": "system", "content": _EXTRACTION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_message},
            ]
            if not self.llm_client or not self.task_executor:
                raise AppException(
                    message="Client not initialized",
                    status_code=500,
                    details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )

            result, _usage = await self.task_executor.execute_structured_task(
                client=self.llm_client,
                messages=messages,
                response_model=SourceExtractionResponseSchema,
            )
            return result.claims
        except Exception as e:
            msg = "Failed to extract source claims."
            logger.error("%s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value},
            ) from e

    async def _verify_single_claim(self, claim: SourceClaimDTO) -> VerifiedSourceDTO:
        """Verifies a single claim against the Tavily search tool.

        Args:
            claim: The claim to verify.

        Returns:
            The verification result.
        """
        query_parts = [f"Verify this claim: {claim.claim_text}"]
        if claim.institution_name:
            query_parts.append(f"by {claim.institution_name}")
        if claim.publication_year:
            query_parts.append(f"({claim.publication_year})")

        query = " ".join(query_parts)

        await self._ensure_initialized()

        try:
            search_res: TavilySearchResult = await tavily_search(query)

            escaped_claim = html.escape(claim.claim_text)
            escaped_answer = html.escape(search_res.answer or "")
            escaped_raw = html.escape(search_res.raw_content or "")

            user_msg = (
                f"<source_data>\n"
                f"  <claim>{escaped_claim}</claim>\n"
                f"  <search_results>\n"
                f"    <answer>{escaped_answer}</answer>\n"
                f"    <raw_content>{escaped_raw}</raw_content>\n"
                f"  </search_results>\n"
                f"</source_data>"
            )

            messages = [
                {"role": "system", "content": _VERIFICATION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_msg},
            ]
            if not self.llm_client or not self.task_executor:
                raise AppException(
                    message="Client not initialized",
                    status_code=500,
                    details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )

            eval_res_tuple = await self.task_executor.execute_chat_task(
                client=self.llm_client,
                messages=messages,
            )
            eval_res_str = eval_res_tuple[0] if isinstance(eval_res_tuple, tuple) else eval_res_tuple
            if isinstance(eval_res_str, dict):
                eval_res_str = str(eval_res_str.get("content", ""))

            status_str = eval_res_str.strip().upper() if isinstance(eval_res_str, str) else ""
            if status_str not in ["VERIFIED", "HALLUCINATION", "INCONCLUSIVE"]:
                status = SourceVerificationStatus.INCONCLUSIVE
            else:
                status = SourceVerificationStatus(status_str)

            return VerifiedSourceDTO(
                claim_text=claim.claim_text,
                status=status,
                source_urls=search_res.source_urls,
                tavily_answer=search_res.answer,
            )

        except Exception as e:
            # If search fails (e.g. rate limit), mark as INCONCLUSIVE and log
            logger.error(
                "Failed to verify claim '%s': %s",
                claim.claim_text,
                e,
                exc_info=True,
            )
            return VerifiedSourceDTO(
                claim_text=claim.claim_text,
                status=SourceVerificationStatus.INCONCLUSIVE,
            )

    async def verify_claims(self, claims: list[SourceClaimDTO]) -> list[VerifiedSourceDTO]:
        """Concurrently verifies a list of claims using an asyncio TaskGroup.

        Args:
            claims: List of claims to verify.

        Returns:
            List of verified claims.
        """
        if not claims:
            return []

        results: list[VerifiedSourceDTO] = []

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(self._verify_single_claim(c)) for c in claims]

            for t in tasks:
                results.append(t.result())
        except* Exception as e:
            msg = "Parallel source verification failed fatally."
            logger.error("%s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value},
            ) from e

        return results

    async def run_full_verification(self, text: str) -> SourceVerificationResultDTO:
        """Executes the complete extraction and verification pipeline.

        Args:
            text: Raw input text document.

        Returns:
            The structured verification result.
        """
        if not text or len(text.strip()) < get_settings().min_verifiable_text_length:
            return SourceVerificationResultDTO(
                claims=[],
                verification_timestamp=datetime.now(UTC).isoformat(),
                total_claims=0,
                verified_count=0,
                hallucination_count=0,
            )

        extracted_claims = await self._extract_source_claims(text)
        verified_claims = await self.verify_claims(extracted_claims)

        total = len(verified_claims)
        verified = sum(1 for c in verified_claims if c.status == SourceVerificationStatus.VERIFIED)
        hallucinated = sum(1 for c in verified_claims if c.status == SourceVerificationStatus.HALLUCINATION)

        return SourceVerificationResultDTO(
            claims=verified_claims,
            verification_timestamp=datetime.now(UTC).isoformat(),
            total_claims=total,
            verified_count=verified,
            hallucination_count=hallucinated,
        )
