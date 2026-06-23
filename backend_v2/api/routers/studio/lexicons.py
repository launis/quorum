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
    """Get performative lexicons configuration."""
    return await studio_service.get_performative_lexicons_config()


@router.put("", response_model=SystemConfigPerformativeLexicons)
async def update_lexicons(
    data: SystemConfigPerformativeLexicons,
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigPerformativeLexicons:
    """Update performative lexicons configuration."""
    return await studio_service.save_performative_lexicons_config(initiator, data)


@router.post("/discover/{lang}", response_model=LexiconSuggestionListDTO)
async def discover_new_performative_phrases(
    lang: str,
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> LexiconSuggestionListDTO:
    """Use LLM to discover completely new AI jargon phrases."""
    return await studio_service.discover_new_performative_phrases(lang)


@router.post("/translate/{lang_code}", response_model=LexiconSuggestionListDTO)
async def translate_performative_phrases(
    lang_code: str,
    initiator: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> LexiconSuggestionListDTO:
    """Translate missing slop words from the English master lexicon."""
    return await studio_service.translate_performative_phrases(lang_code)
