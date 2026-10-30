"""Reference management hooks for bibliography generation."""

from __future__ import annotations

import json
import logging

from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.references import (
    BibliographyResultDTO,
    ReferenceDTO,
    ReferencesInputsDTO,
)

logger = logging.getLogger(__name__)

__all__ = [
    "generate_bibliography",
    "generate_bibliography_hook",
]


def generate_bibliography(
    text_dump: str, knowledge_base: dict[str, str | int | float | bool | list[str]] | None
) -> list[ReferenceDTO]:
    """Scan the provided text dump for references using the ReferenceManager.

    Supports "advanced scan" which detects both explicit citations (e.g. "Author 2020")
    and implicit conceptual links.

    Args:
        text_dump: The full text content to scan (e.g. serialized state).
        knowledge_base: The knowledge base structure containing references and concepts.

    Returns:
        A list of unique reference domain objects found in the text.

    Raises:
        AppException: If bibliography generation fails (ErrorCodes.CITATION_PARSING_FAILED).
    """
    try:
        # Stubbed implementation of ReferenceManager (Not ported to V2)
        refs: list[ReferenceDTO] = [
            ReferenceDTO(
                # Phase 3, Step 3: Generate canonical 32-hex RFC 9562 UUIDv7 reference source ID
                source_id=f"ref_{generate_uuid7().hex}",
                title="[MOCK REFERENCE] Bibliography Generator (ReferenceManager) - Not Connected",
                snippet=(
                    "The automated bibliography generator (Reference Hook) executed successfully, "
                    "but the text citation parser engine has not yet been connected in V2. "
                    "This is a placeholder reference."
                ),
                url="https://github.com/v2-migration-pending",
            )
        ]

        logger.debug("[ReferenceHook] Scan complete. Found %s unique references.", len(refs))
        return refs

    except AppException:
        raise
    except Exception as e:
        logger.error(
            "[ReferenceHook] %s: Bibliography generation failed: %s",
            ErrorCodes.CITATION_PARSING_FAILED.name,
            e,
            exc_info=True,
        )
        raise AppException(
            message=f"Bibliography generation failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.CITATION_PARSING_FAILED.value},
        ) from e


@hook_registry.register(name="generate_bibliography")
async def generate_bibliography_hook(state: HookState | None, deps: HookDependencies) -> HookResult:
    """Wrap generate_bibliography and inject its results.

    Args:
        state: The current execution state containing inputs and context.
        deps: Dependencies required for execution.

    Returns:
        A HookResult containing the generated bibliography in the state_delta.

    Raises:
        AppException: If input validation fails or the hook execution encounters an error
            (ErrorCodes.INVALID_JSON_PAYLOAD, ErrorCodes.VALIDATION_FAILED,
            ErrorCodes.CITATION_PARSING_FAILED, ErrorCodes.HOOK_EXECUTION_FAILED).
    """
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    try:
        text_dump = ""

        raw_inputs = state.inputs.raw_inputs
        try:
            parsed_inputs = ReferencesInputsDTO.model_validate({"root": raw_inputs})
            if parsed_inputs.root:
                for val in parsed_inputs.root.values():
                    if val:
                        text_dump += str(val) + "\n"
        except ValidationError as e:
            logger.error(
                "[ReferenceHook] %s: Invalid inputs schema: %s",
                ErrorCodes.INVALID_JSON_PAYLOAD.name,
                e,
                exc_info=True,
            )
            raise AppException(
                message=f"Invalid inputs schema: {e}",
                status_code=400,
                details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD.value},
            ) from e

        if state.global_context_vars is None:
            msg = "state.global_context_vars is strictly required but missing."
            logger.error("[ReferenceHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        if state.global_context_vars.step_coach:
            text_dump += json.dumps(state.global_context_vars.step_coach, ensure_ascii=False)

        if not text_dump.strip():
            logger.warning("[ReferenceHook] No text to scan.")
            return HookResult(success=True, state_delta=HookDeltaDTO())

        knowledge_base = state.global_context_vars.knowledge_base

        # 3. Generate References
        # This might raise CITATION_PARSING_FAILED (AppException)
        generated_references: list[ReferenceDTO] = generate_bibliography(text_dump, knowledge_base)

        # 4. Map to Domain Models
        result_dto = BibliographyResultDTO(references=generated_references)

        logger.debug("[ReferenceHook] Generated %s references.", len(generated_references))

        return HookResult(success=True, state_delta=HookDeltaDTO(delta=result_dto))

    except AppException:
        # Re-raise AppExceptions directly (Fail Fast)
        raise
    except Exception as e:
        # Catch unexpected errors in the hook wrapper
        logger.error(
            "[ReferenceHook] %s: Hook execution failed: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, e, exc_info=True
        )
        raise AppException(
            message=f"Bibliography hook failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e
