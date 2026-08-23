"""Hook for verifying source claims before DAG execution.

This hook extracts explicit source claims from input documents and uses
the Tavily AI search client to verify them against live web data.
"""

import logging
from datetime import UTC, datetime

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.source_verification import SourceVerificationResultDTO
from backend_v2.models.dtos.source_extraction_schema import SourceVerificationInputsDTO
from backend_v2.services.source_verification_service import (
    MIN_VERIFIABLE_TEXT_LENGTH,
    SourceVerificationService,
)

logger = logging.getLogger(__name__)


def _create_empty_verification_result() -> dict[str, object]:
    """Creates a fully valid serialized empty SourceVerificationResultDTO."""
    empty_dto = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp=datetime.now(UTC).isoformat(),
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
    )
    return empty_dto.model_dump(mode="json")


@hook_registry.register("source_verification")
async def source_verification_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Extracts and verifies source claims from text inputs.

    Args:
        state: The current execution state.
        deps: Dependencies for execution.

    Returns:
        HookResult with state_delta containing verified_sources.
    """
    if not state.inputs:
        return HookResult(
            success=True,
            state_delta={"verified_sources": _create_empty_verification_result()},
        )

    # Validate inputs using strict DTO
    try:
        # Check if structured document_text exists
        if "document_text" in state.inputs:
            inputs_dto = SourceVerificationInputsDTO(document_text=state.inputs["document_text"])
        else:
            text_parts = [val for val in state.inputs.values() if isinstance(val, str)]
            inputs_dto = SourceVerificationInputsDTO(document_text="\n\n".join(text_parts))
    except Exception as e:
        msg = f"Invalid inputs for source verification hook: {e}"
        logger.error("[SourceVerificationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    document_text = inputs_dto.document_text.strip()
    if len(document_text) < MIN_VERIFIABLE_TEXT_LENGTH:
        return HookResult(
            success=True,
            state_delta={"verified_sources": _create_empty_verification_result()},
        )

    try:
        service = SourceVerificationService(comp_repo=deps.comp_repo)
        result = await service.run_full_verification(document_text)

        return HookResult(
            success=True,
            state_delta={"verified_sources": result.model_dump(mode="json")},
        )
    except Exception as e:
        logger.error("[SourceVerificationHook] Failed to verify sources: %s", e, exc_info=True)
        raise
