"""Reference management hooks for bibliography generation."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
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
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (Dict[str, Any]): The knowledge base structure containing references and concepts.

    Returns:
        List[BibliographyItem]: A list of unique reference domain objects found in the text.
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
        error_code = ErrorCodes.CITATION_PARSING_FAILED
        logger.error("[ReferenceHook] %s: Bibliography generation failed: %s", error_code.name, e, exc_info=True)
        raise AppException(
            message=f"Bibliography generation failed: {e}", status_code=500, details={"error_code": error_code}
        ) from e


@hook_registry.register(name="generate_bibliography")
async def generate_bibliography_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Wrap generate_bibliography and inject its results."""
    logger.debug("[ReferenceHook] Running generate_bibliography_hook...")

    if not state:
        return HookResult(success=True, state_delta={})

    try:
        text_dump = ""

        try:
            parsed_inputs = ReferencesInputsDTO.model_validate(state.inputs)
            if parsed_inputs.root:
                for val in parsed_inputs.root.values():
                    text = str(val) if val else ""
                    text_dump += text + "\n"
        except ValidationError as e:
            error_code = ErrorCodes.INVALID_JSON_PAYLOAD
            logger.error("[ReferenceHook] %s: Invalid inputs schema: %s", error_code.name, e)
            raise AppException(
                message=f"Invalid inputs schema: {e}", status_code=400, details={"error_code": error_code.value}
            ) from e

        if state.global_context_vars is None:
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = "state.global_context_vars is strictly required but missing."
            logger.error("[ReferenceHook] %s: %s", error_code.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

        try:
            parsed_context = ReferencesContextDTO.model_validate(state.global_context_vars)
        except ValidationError as e:
            error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
            logger.error("[ReferenceHook] %s: Invalid context schema: %s", error_code.name, e)
            raise AppException(
                message=f"Invalid context schema: {e}", status_code=400, details={"error_code": error_code.value}
            ) from e

        if parsed_context.step_coach:
            text_dump += json.dumps(parsed_context.step_coach, ensure_ascii=False)

        if not text_dump.strip():
            logger.warning("[ReferenceHook] No text to scan.")
            return HookResult(success=True, state_delta={})

        knowledge_base = parsed_context.knowledge_base

        # 3. Generate References
        # This might raise REFERENCES_GENERATION_FAILED (AppException)
        generated_references: list[ReferenceDTO] = generate_bibliography(text_dump, knowledge_base)

        # 4. Map to Domain Models
        result_dto = BibliographyResultDTO(references=generated_references)

        logger.debug("[ReferenceHook] Generated %s references.", len(generated_references))
        delta: dict[str, Any] = {"bibliography_result": result_dto.model_dump()}

        if "knowledge_base" not in state.global_context_vars:
            delta["knowledge_base"] = knowledge_base

        return HookResult(success=True, state_delta=delta)

    except AppException:
        # Re-raise AppExceptions directly (Fail Fast)
        raise
    except Exception as e:
        # Catch unexpected errors in the hook wrapper
        error_code = ErrorCodes.HOOK_EXECUTION_FAILED
        logger.error("[ReferenceHook] %s: Hook execution failed: %s", error_code.name, e, exc_info=True)
        raise AppException(
            message=f"Bibliography hook failed: {e}", status_code=500, details={"error_code": error_code}
        ) from e
