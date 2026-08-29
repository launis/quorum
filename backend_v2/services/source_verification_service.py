"""Source Verification Service.

Responsible for extracting source claims from text and verifying them via Tavily AI.
Adheres strictly to the SRP God Method Mandate, Single Source of Truth, and Pydantic Strict Nirvana.
"""

import asyncio
import html
import logging
from datetime import UTC, datetime

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.source_verification import (
    SourceClaimDTO,
    SourceVerificationResultDTO,
    SourceVerificationStatus,
    VerifiedSourceDTO,
)
from backend_v2.models.dtos.source_extraction_schema import SourceExtractionResponseSchema
from backend_v2.models.v2_core import MCPAuditTrace
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.localization import get_language
from backend_v2.services.mcp.mcp_tool_loop import DISPATCHER
from backend_v2.services.mcp.tools.tavily import TAVILY_TOOL_ID
from backend_v2.settings import get_settings

__all__ = ["SourceVerificationService"]

logger = logging.getLogger(__name__)

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
        llm_task_executor: LLMTaskExecutor,
        llm_client: LLMClient,
    ) -> None:
        """Initializes the service with strict dependency injection.

        Args:
            llm_task_executor: Injected structured task executor.
            llm_client: Injected LLM client strategy instance.
        """
        self.task_executor: LLMTaskExecutor = llm_task_executor
        self.llm_client: LLMClient = llm_client

    async def _extract_source_claims(self, text: str) -> list[SourceClaimDTO]:
        """Extracts source claims from text using structured LLM output.

        Args:
            text: Raw input text.

        Returns:
            List of SourceClaimDTO objects.

        Raises:
            AppException: If extraction fails due to structural or network errors.
        """
        settings = get_settings()
        if not text or len(text.strip()) < settings.source_verification_min_text_length:
            return []

        safe_text = html.escape(text[: settings.source_extraction_max_chars].strip())
        user_message = f"<source_data>\n{safe_text}\n</source_data>"

        try:
            messages = [
                {"role": "system", "content": _EXTRACTION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_message},
            ]

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

    async def _verify_single_claim(self, claim: SourceClaimDTO) -> tuple[VerifiedSourceDTO, MCPAuditTrace | None]:
        """Verifies a single claim against the Tavily search tool.

        Args:
            claim: The claim to verify.

        Returns:
            Tuple containing VerifiedSourceDTO and optional MCPAuditTrace.
        """
        query_parts = [f"Verify this claim: {claim.claim_text}"]
        if claim.institution_name:
            query_parts.append(f"by {claim.institution_name}")
        if claim.publication_year:
            query_parts.append(f"({claim.publication_year})")

        query = " ".join(query_parts)

        try:
            audit_trace: MCPAuditTrace = await DISPATCHER.execute_tool(
                tool_id=TAVILY_TOOL_ID,
                query=query,
                step_name="source_verification",
                target_language=get_language(),
                llm_client=self.llm_client,
                claim_text=claim.claim_text,
            )

            escaped_claim = html.escape(claim.claim_text)
            escaped_answer = html.escape(audit_trace.response_summary or "")

            user_msg = (
                f"<source_data>\n"
                f"  <claim>{escaped_claim}</claim>\n"
                f"  <search_results>\n"
                f"    <answer>{escaped_answer}</answer>\n"
                f"  </search_results>\n"
                f"</source_data>"
            )

            messages = [
                {"role": "system", "content": _VERIFICATION_SYSTEM_INSTRUCTION},
                {"role": "user", "content": user_msg},
            ]

            eval_res = await self.task_executor.execute_chat_task(
                client=self.llm_client,
                messages=messages,
            )
            if isinstance(eval_res, dict):
                content_val = eval_res.get("content", "")
                status_str = str(content_val).strip().upper()
            else:
                status_str = str(eval_res).strip().upper()

            if status_str not in ["VERIFIED", "HALLUCINATION", "INCONCLUSIVE"]:
                status = SourceVerificationStatus.INCONCLUSIVE
            else:
                status = SourceVerificationStatus(status_str)

            return (
                VerifiedSourceDTO(
                    claim_text=claim.claim_text,
                    status=status,
                    source_urls=audit_trace.source_urls,
                    tavily_answer=audit_trace.response_summary,
                ),
                audit_trace,
            )

        except Exception as e:
            # Circuit Breaker degradation for per-claim Tavily API failures
            logger.error(
                "Failed to verify claim '%s': %s",
                claim.claim_text,
                e,
                extra={"error_code": ErrorCodes.FETCH_FAILED.name},
                exc_info=True,
            )
            return (
                VerifiedSourceDTO(
                    claim_text=claim.claim_text,
                    status=SourceVerificationStatus.INCONCLUSIVE,
                    source_urls=[],
                    tavily_answer=None,
                ),
                None,
            )

    async def verify_claims(self, claims: list[SourceClaimDTO]) -> tuple[list[VerifiedSourceDTO], list[MCPAuditTrace]]:
        """Concurrently verifies a list of claims using an asyncio TaskGroup.

        Args:
            claims: List of claims to verify.

        Returns:
            Tuple of verified claims list and audit traces list.

        Raises:
            AppException: If parallel task execution crashes unrecoverably.
        """
        if not claims:
            return [], []

        verified_list: list[VerifiedSourceDTO] = []
        audit_traces: list[MCPAuditTrace] = []

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(self._verify_single_claim(c)) for c in claims]

            for t in tasks:
                dto, trace = t.result()
                verified_list.append(dto)
                if trace is not None:
                    audit_traces.append(trace)
        except* Exception as e:
            msg = "Parallel source verification failed fatally."
            logger.error("%s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value},
            ) from e

        return verified_list, audit_traces

    async def run_full_verification(self, text: str) -> SourceVerificationResultDTO:
        """Executes the complete extraction and verification pipeline.

        Args:
            text: Raw input text document.

        Returns:
            The structured verification result containing verified claims and audit traces.
        """
        settings = get_settings()
        if not text or len(text.strip()) < settings.source_verification_min_text_length:
            return SourceVerificationResultDTO(
                claims=[],
                verification_timestamp=datetime.now(UTC).isoformat(),
                total_claims=0,
                verified_count=0,
                hallucination_count=0,
                audit_traces=[],
            )

        extracted_claims = await self._extract_source_claims(text)
        verified_claims, audit_traces = await self.verify_claims(extracted_claims)

        total = len(verified_claims)
        verified = sum(1 for c in verified_claims if c.status == SourceVerificationStatus.VERIFIED)
        hallucinated = sum(1 for c in verified_claims if c.status == SourceVerificationStatus.HALLUCINATION)

        return SourceVerificationResultDTO(
            claims=verified_claims,
            verification_timestamp=datetime.now(UTC).isoformat(),
            total_claims=total,
            verified_count=verified,
            hallucination_count=hallucinated,
            audit_traces=audit_traces,
        )
