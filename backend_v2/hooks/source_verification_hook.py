"""Hook for verifying source claims before DAG execution.

This hook extracts explicit source claims from input documents and uses
the Tavily AI search client to verify them against live web data.
"""

import logging
from datetime import UTC, datetime

from pydantic import BaseModel

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.source_verification import SourceVerificationResultDTO
from backend_v2.models.dtos.source_extraction_schema import SourceVerificationInputsDTO
from backend_v2.services.source_verification_service import SourceVerificationService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


def _create_empty_verification_result() -> SourceVerificationResultDTO:
    """Creates a fully valid typed empty SourceVerificationResultDTO."""
    return SourceVerificationResultDTO(
        claims=[],
        verification_timestamp=datetime.now(UTC).isoformat(),
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
    )


@hook_registry.register("source_verification")
async def source_verification_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Extracts and verifies source claims from text inputs.

    Args:
        state: The current execution state.
        deps: Dependencies for execution.

    Returns:
        HookResult with state_delta containing verified_sources as SourceVerificationResultDTO.
    """
    if not state.inputs:
        return HookResult(
            success=True,
            state_delta={"verified_sources": _create_empty_verification_result()},
        )

    candidate_text = ""

    if isinstance(state.inputs, dict):
        recognized_keys = ("document_text", "prior_analysis", "text", "document")
        if any(k in state.inputs for k in recognized_keys):
            try:
                inputs_dto = SourceVerificationInputsDTO.model_validate(state.inputs)
                candidate_text = (
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
            for val in state.inputs.values():
                if not isinstance(val, str):
                    msg = "Invalid inputs for source verification hook: non-string value found"
                    logger.error(
                        "[SourceVerificationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True
                    )
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                text_parts.append(val)
            candidate_text = "\n\n".join(text_parts).strip()
    elif isinstance(state.inputs, BaseModel):
        if isinstance(state.inputs, SourceVerificationInputsDTO):
            candidate_text = (
                state.inputs.document_text
                or state.inputs.prior_analysis
                or state.inputs.text
                or state.inputs.document
                or ""
            ).strip()
        else:
            msg = "Invalid inputs DTO for source verification hook"
            logger.error("[SourceVerificationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
    else:
        msg = "Invalid inputs format for source verification hook"
        logger.error("[SourceVerificationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if len(candidate_text) < get_settings().min_verifiable_text_length:
        return HookResult(
            success=True,
            state_delta={"verified_sources": _create_empty_verification_result()},
        )

    try:
        service = SourceVerificationService(comp_repo=deps.comp_repo, system_repo=deps.system_repo)
        result: SourceVerificationResultDTO = await service.run_full_verification(candidate_text)

        return HookResult(
            success=True,
            state_delta={"verified_sources": result},
        )
    except Exception as e:
        logger.error("[SourceVerificationHook] Failed to verify sources: %s", e, exc_info=True)
        raise
