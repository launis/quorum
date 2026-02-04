"""Guard Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import TaintedData

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class GuardAgent(BaseAgent):
    """Vartija-agentti (Guard Agent).

    Responsible for:
    1. Input Sanitization (Syötteen puhdistus)
    2. Security Check (Tietoturvatarkistus)
    3. Anonymization (Anonymisointi).
    """

    state_field = "step_guard"

    # Contracts
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]  # Reflection is optional
    PRODUCES_KEYS = ["step_guard"]
    # OUTPUT_SCHEMA is already handled by get_response_schema() logic generally,
    # but we can explicit it here if needed for static analysis.
    OUTPUT_SCHEMA = TaintedData

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the TaintedData schema definition.

        Returns:
            Type[TaintedData]: The schema class.

        """
        return TaintedData

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the security analysis and sanitization logic.

        Args:
            input_data (dict): Inputs including history_text, product_text, etc.
            execution_context (Optional[dict]): Context/Config.
            system_instruction (Optional[str]): Prompt override.
            **kwargs: Additional args.

        Returns:
            dict: The security report (TaintedData).
        """
        # Pass through to BaseAgent
        return await super().execute(
            input_data=input_data,
            execution_context=execution_context,
            system_instruction=system_instruction,
            **kwargs
        )

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Performs Python-based banned phrase checks and sanitization.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            **kwargs: ignored.

        Returns:
            Optional[str]: None. Only side-effects (logging/validation).
        """
        # 1. Banned Phrase Check (Via Schema Validation)
        try:
            # Load banned phrases from context/config or inputs
            # Assuming Engine injects them into execution_config or inputs
            banned_phrases = []
            if execution_context and "banned_phrases" in execution_context:
                banned_phrases = execution_context["banned_phrases"]
            elif "banned_phrases" in input_data:
                banned_phrases = input_data["banned_phrases"]

            banned_ctx = {"banned_phrases": banned_phrases}

            from backend.models.domain import GuardInput

            # This triggers @AfterValidator(validate_guard_input)
            GuardInput.model_validate(
                {
                    "history_text": input_data.get("history_text") or "",
                    "product_text": input_data.get("product_text") or "",
                    "reflection_text": input_data.get("reflection_text"),
                },
                context=banned_ctx,
            )

        except ValueError as e:
            # Convert Pydantic/Validator error to FatalInterruption for the Engine
            if "SECURITY_BANNED_PHRASE_DETECTED" in str(e):
                logger.error(f"[GuardAgent] Banned Phrase Detected via Schema: {e}")
                from backend.exceptions import FatalInterruption

                raise FatalInterruption(
                    step_name="GuardSecurityCheck",
                    reason="Banned Phrase Detected (Schema Validation)",
                    details={"error": str(e)},
                ) from e
            raise e

        # 2. Input Sanitization (Local Effect Only)
        # We sanitize locally to log threats.
        # Note: In strict stateless mode, we don't modify the upstream inputs.
        self.sanitize_input(input_data)

        return None

    def post_process(self, response_data: Any) -> Any:
        """Lifecycle Hook: Post-Execution.

        Ensures tainted data structure is populated and banned phrases are flagged.

        Args:
            response_data (Any): The result (dict or Model).

        Returns:
            Any: Processed result.
        """
        return self.ensure_tainted_data(response_data)

    def ensure_tainted_data(self, data: Any) -> Any:
        """Post-Hook: Ensures that the tainted data structure is correctly populated.

        Args:
            data (Any): Current result data.

        Returns:
            Any: Validated data.
        """
        logger.info("[GuardAgent] Running ensure_tainted_data...")

        # If it's a dict, wrap or check access
        # If it's a Model, access fields

        # We need to modify 'data' in place or return new data.
        # Since we might have Pydantic model or dict.

        is_dict = isinstance(data, dict)

        # Access helpers
        def get_field(obj, key):
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        def set_field(obj, key, val):
            if isinstance(obj, dict):
                obj[key] = val
            else:
                setattr(obj, key, val)

        security_check = get_field(data, "security_check")

        if not security_check:
            # Should not happen if schema is enforced, but safe fallback
            return data

        # --- 1. PII Sanitization Reporting ---
        # Issue: We don't have easy access to 'sanitization_log' from aux_data here
        # unless we store it on self during prepare_context (which is risky if instance shared, but Registry instantiates fresh per task)
        # Registry: "agent = agent_cls()" -> Fresh instance.
        # So we can store state on self!

        if hasattr(self, "_sanitization_threats") and self._sanitization_threats:
            threats = self._sanitization_threats
            logger.info(f"[GuardAgent] Reporting sanitization actions: {threats}")

            # Update security_check
            # If security_check is a dict (if data is dict) or object

            # Helper for nested update
            if isinstance(security_check, dict):
                security_check["anonymisointi_tehty"] = True
                current = security_check.get("tietosuoja_raportti") or ""
                msg = "Järjestelmä poisti automaattisesti PII-tietoja"
                if msg not in current:
                    security_check["tietosuoja_raportti"] = (current + f"\n{msg}: {', '.join(threats)}.").strip()
            else:
                security_check.anonymisointi_tehty = True
                current = security_check.tietosuoja_raportti or ""
                msg = "Järjestelmä poisti automaattisesti PII-tietoja"
                if msg not in current:
                    security_check.tietosuoja_raportti = (current + f"\n{msg}: {', '.join(threats)}.").strip()

        return data

    def sanitize_input(self, input_data: dict) -> None:
        """Pre-hook: Sanitizes and anonymizes input data (PII Redaction).

        Args:
            input_data (dict): Inputs to scan.
        """
        logger.info("[GuardAgent] Running sanitize_input (Pre-Hook)...")
        from backend.hooks.security import sanitize_text

        inputs_to_scan = {
            "history_text": input_data.get("history_text"),
            "product_text": input_data.get("product_text"),
            "reflection_text": input_data.get("reflection_text"),
        }

        all_threats = []

        for key, value in inputs_to_scan.items():
            if not value:
                continue

            clean_text, threats = sanitize_text(value)

            if threats:
                formatted_threats = [f"{t} ({key})" for t in threats]
                all_threats.extend(formatted_threats)

            if clean_text != value:
                # We modify the local input dict.
                # This affects the prompt construction in BaseAgent if it uses input_data.
                input_data[key] = clean_text

        if all_threats:
            logger.warning(f"[GuardAgent] PII Sanitization: {all_threats}")
            # Store for post_process
            self._sanitization_threats = all_threats
