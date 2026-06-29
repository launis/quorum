"""Admin Studio Lexicons API Router.

Handles performative lexicons configuration and LLM discovery.
"""

import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import LexiconSuggestionListDTO, SystemConfigPerformativeLexicons

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lexicons", tags=["Admin Studio V2 - Performative Lexicons"])


@router.get("", response_model=SystemConfigPerformativeLexicons)
async def get_lexicons(
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigPerformativeLexicons:
    """Get performative lexicons configuration.

    Args:
        initiator: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The performative lexicons configuration.

    Raises:
        AppException: If fetching the configuration fails.
    """
    return await studio_service.get_performative_lexicons_config()


@router.put("", response_model=SystemConfigPerformativeLexicons)
async def update_lexicons(
    data: SystemConfigPerformativeLexicons,
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigPerformativeLexicons:
    """Update performative lexicons configuration.

    Args:
        data: The new configuration data.
        initiator: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The updated performative lexicons configuration.

    Raises:
        AppException: If updating the configuration fails.
    """
    return await studio_service.save_performative_lexicons_config(initiator, data)


@router.post("/discover/{lang}", response_model=LexiconSuggestionListDTO)
async def discover_new_performative_phrases(
    lang: str,
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> LexiconSuggestionListDTO:
    """Use LLM to discover completely new AI jargon phrases.

    Args:
        lang: The language code to discover phrases for.
        initiator: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of suggested performative phrases.

    Raises:
        AppException: If the discovery process fails.
    """
    return await studio_service.discover_new_performative_phrases(lang)


@router.post("/translate/{lang_code}", response_model=LexiconSuggestionListDTO)
async def translate_performative_phrases(
    lang_code: str,
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> LexiconSuggestionListDTO:
    """Translate missing slop words from the English master lexicon.

    Args:
        lang_code: The target language code for translation.
        initiator: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of translated performative phrases.

    Raises:
        AppException: If the translation process fails.
    """
    return await studio_service.translate_performative_phrases(lang_code)
