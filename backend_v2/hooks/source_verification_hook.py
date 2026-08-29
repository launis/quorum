"""Hook for verifying source claims before DAG execution.

This hook extracts explicit source claims from input documents and uses
the Tavily AI search client to verify them against live web data.
"""

import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.source_verification import SourceVerificationResultDTO
from backend_v2.models.dtos.source_extraction_schema import SourceVerificationInputsDTO
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.localization import set_language
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.source_verification_service import SourceVerificationService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["source_verification_hook"]


def _extract_text_polymorphically(inputs: Any) -> str:
    """Extract candidate text from heterogeneous input state partitions.

    Args:
        inputs: Heterogeneous inputs (str, dict, list, BaseModel).

    Returns:
        Consolidated input text.

    Raises:
        AppException: If input cannot be parsed or validated.
    """
    if not inputs:
        return ""

    if isinstance(inputs, str):
        return inputs.strip()

    if isinstance(inputs, dict):
        recognized_keys = ("document_text", "prior_analysis", "text", "document")
        if any(k in inputs for k in recognized_keys):
            try:
                inputs_dto = SourceVerificationInputsDTO.model_validate(inputs)
                return (
                    inputs_dto.document_text
                    or inputs_dto.prior_analysis
                    or inputs_dto.text
                    or inputs_dto.document
                    or ""
                ).strip()
            except Exception as e:
                msg = f"Invalid inputs for source verification hook: {e}"
                logger.error("[SourceVerificationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        else:
            text_parts: list[str] = []
            for val in inputs.values():
                if val is not None and str(val).strip():
                    text_parts.append(str(val).strip())
            return "\n\n".join(text_parts).strip()

    if isinstance(inputs, list):
        text_parts = [str(item).strip() for item in inputs if item is not None and str(item).strip()]
        return "\n\n".join(text_parts).strip()

    if isinstance(inputs, BaseModel):
        if isinstance(inputs, SourceVerificationInputsDTO):
            return (inputs.document_text or inputs.prior_analysis or inputs.text or inputs.document or "").strip()
        else:
            dumped = inputs.model_dump(mode="python")
            if isinstance(dumped, dict):
                return _extract_text_polymorphically(dumped)

    msg = "Invalid inputs format for source verification hook"
    logger.error("[SourceVerificationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
    raise AppException(
        message=msg,
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )


@hook_registry.register("source_verification_hook")
async def source_verification_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Extracts and verifies source claims from text inputs.

    Args:
        state: The current execution state.
        deps: Dependencies for execution.

    Returns:
        HookResult with state_delta containing metadata.mcp_audit_traces and global_context_vars.external_evidence.

    Raises:
        AppException: If configuration dependencies are missing or execution fails.
    """
    settings = get_settings()

    if not state.inputs:
        return HookResult(
            success=True,
            state_delta={
                "metadata": {"mcp_audit_traces": []},
                "global_context_vars": {"external_evidence": ""},
            },
        )

    candidate_text = _extract_text_polymorphically(state.inputs)

    if len(candidate_text) < settings.source_verification_min_text_length:
        return HookResult(
            success=True,
            state_delta={
                "metadata": {"mcp_audit_traces": []},
                "global_context_vars": {"external_evidence": ""},
            },
        )

    if not deps.system_repo:
        msg = "Missing system_repo in HookDependencies"
        logger.error("[SourceVerificationHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    if state.metadata and "target_locale" in state.metadata:
        set_language(state.metadata["target_locale"])

    try:
        llm_client = await LLMClient.from_strategy(
            "fast", repository=deps.system_repo, pipeline_name="source_verification"
        )
        task_executor = LLMTaskExecutor(PromptCompiler())
        service = SourceVerificationService(llm_task_executor=task_executor, llm_client=llm_client)

        result: SourceVerificationResultDTO = await service.run_full_verification(candidate_text)

        evidence_lines: list[str] = []
        for claim in result.claims:
            evidence_lines.append(
                f'<claim status="{claim.status.value}" query="{claim.claim_text}">\n'
                f"  <answer>{claim.tavily_answer or ''}</answer>\n"
                f"</claim>"
            )

        external_evidence_xml = ""
        if evidence_lines:
            joined_lines = "\n".join(evidence_lines)
            external_evidence_xml = f"<external_evidence>\n{joined_lines}\n</external_evidence>"

        raw_traces = [trace.model_dump(mode="python") for trace in result.audit_traces]

        return HookResult(
            success=True,
            state_delta={
                "metadata": {"mcp_audit_traces": raw_traces},
                "global_context_vars": {"external_evidence": external_evidence_xml},
            },
        )
    except Exception as e:
        logger.error("[SourceVerificationHook] Failed to verify sources: %s", e, exc_info=True)
        if isinstance(e, AppException):
            raise
        raise AppException(
            message=f"Source verification hook failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.FETCH_FAILED.value},
        ) from e
