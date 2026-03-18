"""Service for parsing unstructured pasted chat logs into strict JSON structures.

Uses an LLM (strategy: 'ChatParser') to decouple human conversation from UI garbage,
aligning with the V2 Fail-Fast architecture.
"""

import json
import logging
from typing import Any

from fastapi import status
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.v2_core import ChatHistoryDTO

logger = logging.getLogger(__name__)


class ChatParserService:
    @staticmethod
    async def parse_pasted_chat(raw_paste: str, repository: Any) -> ChatHistoryDTO:
        """Parse raw pasted chat logs into strict JSON using LLM.

        Args:
            raw_paste (str): Raw unstructured text pasted from a chat UI.
            repository (Any): AbstractWorkflowRepository instance.

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
            # Note: The system model_registry must have a 'fast' (or alias) strategy defined.
            llm_client = await LLMClient.from_strategy("fast", repository=repository)
        except ConfigurationError as e:
            error_code = ErrorCodes.CONFIGURATION_ERROR
            msg = f"Failed to initialize LLMClient for ChatParser: {e.message}"
            logger.error(f"[ChatParser] {error_code.name}: {msg}")
            raise AppException(
                message=msg, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": error_code.value}
            ) from e

        # Construct the Prompt
        # Mandates: Strip all AI UI fluff (Regenerate, Copy code, etc)
        prompt = f"""
        Olet datanlouhinta-asiantuntija. Tehtäväsi on ottaa vastaan käyttäjän selaimesta
        kopioima (copy-paste) sotkuinen raakateksti, joka on peräisin tekoälykeskustelusta
        (esim. ChatGPT, Gemini tai Claude).

        SÄÄNNÖT:
        1. Erottele tekstistä ihmisen (user) ja tekoälyn (ai) viestit. 'role' tulee olla joko 'user' tai 'ai'.
        2. KRIITTISTÄ - PDF-TULOSTEIDEN REKONSTRUKTIO: Käyttäjän syöte saattaa olla selaimentuloste (Print to PDF) ChatGPT-keskustelusta, jonka PyMuPDF on silppunnut pelkäksi pitkäksi tekstipötköksi vieden kaikki visuaaliset raja-aidat.
           - Etsi toistuvia tunnisteita kuten henkilön nimi ("You", omanimi, initials) vs "ChatGPT", "AI".
           - Vaikka näitä ei olisi, SINUN ON PÄÄTELTÄVÄ vuoronvaihdot kontekstista: ihmisen viestit ovat tyypillisesti kysymyksiä tai prompteja (esim. "Tee seuraavaksi...", "Mitä tarkoitat..."), jota seuraa koneen tuottama jäsennelty asiateksti.
           - Yhdistä pirstaleinen teksti saumattomasti yhteen kunkin roolin ('user' tai 'ai') alle, palauttaen alkuperäisen kysymys-vastaus -rytmin! Mieluummin liian pitkiä blokkeja kuin liian pirstaleista.
        3. Jätä täysin huomiotta kaikki käyttöliittymän roskateksti
           (esim. "Regenerate", "Copy code", aikaleimat, "Was this response better or worse?", 
           sivuvalikot, profiilien nimet).
        3. Oletus: viestit vuorottelevat. Jos teksti alkaa ihmisen kysymyksellä, ensimmäinen 'role' on 'user'.
        4. Palauta data TÄSMÄLLEEN pyydetyssä Pydantic JSON-muodossa.
        5. VAROITUS (FAIL-SAFE): Jos raakateksti ei missään nimessä näytä keskustelulta (esim. se on vain sekava PDF-tuloste oppilaan oppimispäiväkirjasta tai esseestä ilman vuorosanoja), ÄLÄ KOSKAAN palauta tyhjää listaa. Tässä hätätapauksessa aseta koko teksti yhtenä pitkänä viestinä 'user'-roolille.

        Tässä on käsiteltävä raakateksti:
        <raakateksti>
        {raw_paste}
        </raakateksti>
        """

        messages = [{"role": "user", "content": prompt}]

        try:
            # V2 Strict Output Generation
            parsed_data, _ = await llm_client.run_structured_task(
                messages=messages,
                response_model=ChatHistoryDTO
            )
            logger.info(f"[ChatParser] Parsing successful. Extracted {len(parsed_data.conversation)} messages.")
            return parsed_data

        except ValidationError as e:
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
