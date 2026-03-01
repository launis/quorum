import json
import logging
from typing import Any

import pydantic
from fastapi import status

from backend.exceptions import AppException, ConfigurationError, ErrorCodes
from backend.llm.client import LLMClient
from backend.models.dtos.chat_history import ChatHistoryDTO

logger = logging.getLogger(__name__)


async def parse_pasted_chat(raw_paste: str, repository: Any = None) -> ChatHistoryDTO:
    """Parse raw pasted chat logs into strict JSON using LLM.

    Args:
        raw_paste (str): Raw unstructured text pasted from a chat UI.
        repository (Any, optional): Repository instance for tracing if needed by LLMClient.

    Returns:
        ChatHistoryDTO: Strictly typed chat history object.

    Raises:
        AppException: If input is empty, LLM fails, or validation fails.
    """
    logger.debug("[ChatParser] parse_pasted_chat CALLED")

    if not raw_paste or not raw_paste.strip():
        # Fail Fast: Cannot parse empty text
        error_code = ErrorCodes.EMPTY_INPUT
        msg = "ChatParser received empty input."
        logger.error(f"[ChatParser] {error_code.name}: {msg}")
        raise AppException(
            message=msg, status_code=status.HTTP_400_BAD_REQUEST, details={"error_code": error_code.value}
        )

    # Initialize LLM Client via Strategy Pattern
    try:
        # Request the 'ChatParser' strategy from the registry.
        # This allows dynamic configuration in DB (e.g. mapping to 'fast' or 'strict').
        llm_client = await LLMClient.from_strategy("ChatParser", repository=repository)
    except ConfigurationError as e:
        error_code = ErrorCodes.CONFIGURATION_ERROR
        msg = f"Failed to initialize LLMClient for ChatParser: {e.message}"
        logger.error(f"[ChatParser] {error_code.name}: {msg}")
        raise AppException(
            message=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code.value}
        ) from e

    # Construct the Prompt
    prompt = f"""
    Olet datanlouhinta-asiantuntija. Tehtäväsi on ottaa vastaan käyttäjän selaimesta 
    kopioima (copy-paste) sotkuinen raakateksti, joka on peräisin tekoälykeskustelusta 
    (esim. ChatGPT, Gemini tai Claude).

    SÄÄNNÖT:
    1. Erottele tekstistä ihmisen (User) ja tekoälyn (AI) viestit.
    2. Jätä täysin huomiotta kaikki käyttöliittymän roskateksti (esim. "Regenerate", "Copy code", aikaleimat, "Was this response better or worse?", sivuvalikot, profiilien nimet).
    3. Palauta data TÄSMÄLLEEN pyydetyssä JSON-muodossa.

    Tässä on käsiteltävä raakateksti:
    <raakateksti>
    {raw_paste}
    </raakateksti>
    """

    messages = [{"role": "user", "content": prompt}]

    try:
        # Require strict structured output as defined by the DTO model
        parsed_data = await llm_client.run_structured_task(
            messages=messages,
            temperature=0.0,
            response_model=ChatHistoryDTO
        )
        # Log success diagnostically without exposing sensitive logs
        logger.info(f"[ChatParser] Parsing successful. Extracted {len(parsed_data.conversation)} messages.")
        return parsed_data

    except pydantic.ValidationError as e:
        error_code = ErrorCodes.VALIDATION_FAILED
        msg = f"LLM output validation failed to match ChatHistoryDTO schema: {e}"
        logger.error(f"[ChatParser] {error_code.name}: {msg}", exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code.value, "original_error": str(e)},
        ) from e
    except json.JSONDecodeError as e:
        error_code = ErrorCodes.VALIDATION_FAILED
        msg = f"LLM returned invalid JSON: {e}"
        logger.error(f"[ChatParser] {error_code.name}: {msg}", exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code.value, "original_error": str(e)},
        ) from e
    except Exception as e:
        if isinstance(e, AppException):
            raise e

        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        msg = f"LLM generation failed: {e}"
        logger.error(f"[ChatParser] {error_code.name}: {msg}", exc_info=True)
        raise AppException(
            message=msg, status_code=status.HTTP_502_BAD_GATEWAY, details={"error_code": error_code.value}
        ) from e
