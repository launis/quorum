"""Reference management hooks for bibliography generation."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.references import (
    BibliographyResultDTO,
    ReferenceDTO,
    ReferencesContextDTO,
    ReferencesInputsDTO,
)

logger = logging.getLogger(__name__)


def generate_bibliography(text_dump: str, knowledge_base: dict[str, object] | None) -> list[ReferenceDTO]:
    """Scan the provided text dump for references using the ReferenceManager.

    Supports "advanced scan" which detects both explicit citations (e.g. "Author 2020")
    and implicit conceptual links.

    Args:
        text_dump: The full text content to scan (e.g. serialized state).
        knowledge_base: The knowledge base structure containing references and concepts.

    Returns:
        A list of unique reference domain objects found in the text.

    Raises:
        AppException: If bibliography generation fails.
    """
    try:
        # Stubbed implementation of ReferenceManager (Not ported to V2)
        refs: list[ReferenceDTO] = [
            ReferenceDTO(
                source_id=f"ref_{uuid.uuid4().hex[:8]}",
                title="[MOCK REFERENCE] Lähdeluettelon generaattori (ReferenceManager) - Ei Kytketty",
                snippet=(
                    "Järjestelmän automaattinen lähdeluettelogeneraattori (Reference Hook) "
                    "pyörii onnistuneesti, mutta itse tekstin Parsija-moottoria ei ole vielä "
                    "asennettu V2-versioon. Tämä on Dummy-viite."
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
async def generate_bibliography_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Wrap generate_bibliography and inject its results.

    Args:
        state: The current execution state containing inputs and context.
        deps: Dependencies required for execution.

    Returns:
        A HookResult containing the generated bibliography in the state_delta.

    Raises:
        AppException: If input validation fails or the hook execution encounters an error.
    """
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    try:
        text_dump = ""

        raw_inputs = state.inputs.raw_inputs
        try:
            parsed_inputs = ReferencesInputsDTO.model_validate(raw_inputs)
            if parsed_inputs.root:
                for val in parsed_inputs.root.values():
                    text = str(val) if val else ""
                    text_dump += text + "\n"
        except ValidationError as e:
            logger.error("[ReferenceHook] %s: Invalid inputs schema: %s", ErrorCodes.INVALID_JSON_PAYLOAD.name, e)
            raise AppException(
                message=f"Invalid inputs schema: {e}",
                status_code=400,
                details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD.value},
            ) from e

        if state.global_context_vars is None:
            msg = "state.global_context_vars is strictly required but missing."
            logger.error("[ReferenceHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        gvars = state.global_context_vars.vars
        try:
            parsed_context = ReferencesContextDTO.model_validate(gvars)
        except ValidationError as e:
            logger.error("[ReferenceHook] %s: Invalid context schema: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, e)
            raise AppException(
                message=f"Invalid context schema: {e}",
                status_code=400,
                details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
            ) from e

        if parsed_context.step_coach:
            text_dump += json.dumps(parsed_context.step_coach, ensure_ascii=False)

        if not text_dump.strip():
            logger.warning("[ReferenceHook] No text to scan.")
            return HookResult(success=True, state_delta=HookDeltaDTO())

        knowledge_base = parsed_context.knowledge_base

        # 3. Generate References
        # This might raise REFERENCES_GENERATION_FAILED (AppException)
        generated_references: list[ReferenceDTO] = generate_bibliography(text_dump, knowledge_base)

        # 4. Map to Domain Models
        result_dto = BibliographyResultDTO(references=generated_references)

        logger.debug("[ReferenceHook] Generated %s references.", len(generated_references))
        delta: dict[str, Any] = {"bibliography_result": result_dto.model_dump(mode="json")}

        if "knowledge_base" not in gvars:
            delta["knowledge_base"] = knowledge_base

        return HookResult(success=True, state_delta=HookDeltaDTO(delta=delta))

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
