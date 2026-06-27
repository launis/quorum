"""Source Verification Service.

Responsible for extracting source claims from text and verifying them via Tavily AI.
Adheres strictly to the SRP God Method Mandate and Pydantic Strict Nirvana.
"""

import asyncio
import logging
from datetime import UTC, datetime

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.prompt_builder import build_system_directive
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

logger = logging.getLogger(__name__)

# Cut off text length to avoid token limit explosions in fast models
MAX_EXTRACTION_CHARS = 30000


class SourceVerificationService:
    """Service handling the extraction and verification of source claims."""

    def __init__(self, llm_task_executor: LLMTaskExecutor | None = None) -> None:
        """Initializes the service.

        Args:
            llm_task_executor: Injected executor. If None, it initializes a fast strategy client locally.
        """
        self.task_executor: LLMTaskExecutor | None = llm_task_executor
        from backend_v2.llm.client import LLMClient

        self.llm_client: LLMClient | None = (
            getattr(llm_task_executor, "llm_client", None) if llm_task_executor else None
        )

    async def _ensure_initialized(self) -> None:
        if self.task_executor and self.llm_client:
            return

        from backend_v2.llm.client import LLMClient
        from backend_v2.models.llm import LLMProviderConfig
        from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

        config = LLMProviderConfig(
            id="local_fast",
            provider="litellm",
            model_name="gemini/gemini-2.5-flash",
            api_key="mock",
            temperature=0.0,
            tpm_limit=1000000,
            rpm_limit=1000,
            default_max_tokens=4096,
        )
        self.llm_client = LLMClient(config=config)
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
        if not text or not text.strip():
            return []

        await self._ensure_initialized()

        # Safe truncation
        safe_text = text[:MAX_EXTRACTION_CHARS]

        system_prompt = build_system_directive(
            objective="Read the provided document and extract all explicit references to external sources, research, studies, guidelines, or institutions.",
            role="Expert Fact-Checker",
            rules=[
                "Extract the exact claim being attributed to them.",
                "Do not include internal cross-references.",
                "Return an empty list if none are found.",
            ],
        )

        user_message = f"<source_data>\n{safe_text}\n</source_data>"

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]
            if not self.llm_client or not self.task_executor:
                raise AppException(message="Client not initialized", status_code=500)

            result, _usage = await self.task_executor.execute_structured_task(
                client=self.llm_client,
                messages=messages,
                response_model=SourceExtractionResponseSchema,
            )
            return result.claims
        except Exception as e:
            msg = "Failed to extract source claims."
            logger.error(f"{ErrorCodes.FETCH_FAILED.name}: {msg}", exc_info=True)
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

            # Fast chat evaluation to determine status based on Tavily context
            system_prompt = build_system_directive(
                objective="Compare the original source claim against the search results provided.",
                role="Expert Fact-Checker",
                rules=[
                    "Determine if the claim is VERIFIED (supported by search), HALLUCINATION (contradicted or clearly fabricated), or INCONCLUSIVE (not enough info found).",
                    "Return ONLY the exact word: VERIFIED, HALLUCINATION, or INCONCLUSIVE.",
                ],
            )
            user_msg = (
                f"<source_data>\n"
                f"  <claim>{claim.claim_text}</claim>\n"
                f"  <search_results>\n"
                f"    <answer>{search_res.answer}</answer>\n"
                f"    <raw_content>{search_res.raw_content}</raw_content>\n"
                f"  </search_results>\n"
                f"</source_data>"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ]
            if not self.llm_client or not self.task_executor:
                raise AppException(message="Client not initialized", status_code=500)

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
            # According to the rules, if a single search crashes or fails (e.g. rate limit),
            # we should mark it as INCONCLUSIVE and log it, rather than crashing the whole DAG.
            logger.error(
                f"Failed to verify claim '{claim.claim_text}': {e}",
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
            logger.error(f"{ErrorCodes.FETCH_FAILED.name}: {msg}", exc_info=True)
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
