"""Mock LLM Service for testing and offline development."""

import json
import logging
import random
import re
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.mock_data import AGENT_CLASS_TO_MOCK_KEY, MOCK_REGISTRY, get_fallback_data
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


class MockLLMService:
    """Simulates LLM responses for testing and development without API costs.

    Intercepts calls and returns pre-defined JSON responses based on agent identity or prompt heuristics.
    """

    def __init__(self) -> None:
        """Initializes the Mock Service."""
        if not get_settings().use_mock_llm:
            raise RuntimeError(
                "STRICT EXECUTION AUTHORITY: MockLLMService usage is FORBIDDEN when 'use_mock_llm' is False. "
                "The system attempted to fallback to mock data, which is strictly prohibited. "
                "Check credential configuration or provider selection."
            )

        # MAPPING: Role Class Name -> Mock Key
        # Centralized in mock_data.py
        self.agent_identity_map = AGENT_CLASS_TO_MOCK_KEY

    def generate_content(
        self,
        prompt: str,
        system_instruction: str | None = None,
        agent_identity: str | None = None,
        response_schema: Any | None = None,
    ) -> str:
        """Generates mocked content based on the input prompt and identity.

        Args:
            prompt (str): The user prompt.
            system_instruction (Optional[str]): The system instruction prompting the specific agent persona.
            agent_identity (Optional[str]): Explicit agent identifier (e.g. 'AnalystAgent') to bypass heuristics.
            response_schema (Optional[Type[BaseModel]]): The expected Pydantic schema class.

        Returns:
            str: JSON string representing the mocked agent output.

        """
        logger.info("[MockLLM] Intercepted call. Prompt length: %d", len(prompt))

        # 0. DIRECT REGISTRY LOOKUP (Robust)
        if response_schema:
            if isinstance(response_schema, type) and response_schema in MOCK_REGISTRY:
                logger.info("[MockLLM] Registry Hit: Returning mock data for schema '%s'.", response_schema.__name__)
                mock_obj = MOCK_REGISTRY[response_schema]
                return str(mock_obj.model_dump_json())
            elif isinstance(response_schema, dict):
                title = response_schema.get("title")
                if title:
                    for reg_type, mock_obj in MOCK_REGISTRY.items():
                        if reg_type.__name__ == title:
                            logger.info("[MockLLM] Registry Hit (via Dict Title '%s'): Returning mock data.", title)
                            return str(mock_obj.model_dump_json())

        # 1. Determine Identity
        key = None

        # A) Explicit Identity (Robust)
        if agent_identity:
            if agent_identity in self.agent_identity_map:
                key = self.agent_identity_map[agent_identity]
            else:
                key = agent_identity
            logger.info("[MockLLM] Identified agent via explicit identity: '%s' -> '%s'", agent_identity, key)
        else:
            msg = (
                "STRICT FAIL-FAST: Mock service was called without an explicit 'agent_identity'. "
                "Keyword heuristics are DEPRECATED."
            )
            logger.error("[MockLLM] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Replaced manual file write with logger.debug to use standard logging infrastructure
        logger.debug("--- NEW CALL ---\nAgent Identity: %s\nResolved Key: %s", agent_identity, key)
        logger.info("[MOCK RESPONSE] Generating response for: %s", key)

        return self._generate_fallback(key, prompt, system_instruction)

    def _generate_fallback(self, key: str, prompt: str = "", system_instruction: str | None = None) -> str:
        """Generates a minimal valid JSON response for the identified key, strictly matching backend/schemas.py.

        Delegates precise data generation to `mock_data.py`.

        Args:
            key (str): The mock key identifying the agent/type.
            prompt (str): The original prompt, used for dynamic value extraction (e.g. Judge dimensions).
            system_instruction (Optional[str]): System prompt, often containing schema/context.

        Returns:
            str: JSON string of the fallback data.

        """
        data = get_fallback_data(key)

        # --- DYNAMIC JUDGE HYDRATION ---
        # If we are mocking the Judge, we try to detect which dimensions were requested in the JSON schema or text.
        # We scan BOTH prompt and system_instruction.
        scan_text = (prompt or "") + "\n" + (system_instruction or "")

        if key == "judge_agent" and scan_text.strip():
            try:
                # Strategy A: Extract from Human Text (JudgeAgent prompt format: "- Label (ID: key):")
                keys_found = re.findall(r"\(ID:\s*([a-zA-Z0-9_]+)\)", scan_text)

                # Strategy B: Extract from JSON Schema (Backup)
                if not keys_found:
                    match = re.search(r'"scores"\s*:\s*\{.*?"properties"\s*:\s*\{(.*?)\}\s*,', scan_text, re.DOTALL)
                    if match:
                        props_inner = match.group(1)
                        keys_found = re.findall(r'"([a-z0-9_]+)"\s*:\s*\{', props_inner)

                if keys_found:
                    logger.info("[MockLLM] Dynamic Judge Keys Found: %s", keys_found)
                    dynamic_scores = {}
                    for k in keys_found:
                        dynamic_scores[k] = {
                            "arvosana": random.randint(2, 4),
                            "perustelu": f"[MOCK] Dynamic evaluation for '{k}'.",
                        }
                    data["pisteet"] = dynamic_scores
            except Exception as e:
                logger.error("[MockLLM] Failed hydration: %s", e)
                raise AppException(
                    message=f"Mock Hydration Failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        # Assuming get_fallback_data returns a dict; we need to stringify it for the 'LLM response'
        # Fix: Handle datetime objects (e.g. from MOCK_METADATA) using a custom default handler.
        def _json_serial(obj: Any) -> str:
            if hasattr(obj, "isoformat"):
                return str(obj.isoformat())
            raise TypeError(f"Type {type(obj)} not serializable")

        return json.dumps(data, ensure_ascii=False, default=_json_serial)
