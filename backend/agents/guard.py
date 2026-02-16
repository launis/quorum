"""Guard Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes, FatalInterruption
from backend.models.domain import GuardOutput

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
    OUTPUT_SCHEMA = GuardOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the GuardOutput schema definition.

        Returns:
            Type[GuardOutput]: The schema class.

        """
        return GuardOutput

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> GuardOutput:
        """Executes the security analysis and sanitization logic.

        Args:
            input_data (dict[str, Any]): Inputs including history_text, product_text, etc.
            execution_context (dict[str, Any] | None, optional): Context/Config.
            system_instruction (str | None, optional): Prompt override.
            **kwargs: Additional args.

        Returns:
            GuardOutput: The security report (TaintedData).

        Raises:
            ValueError: If mandatory inputs are missing.
        """

        # FAIL FAST: Guard requires content to sanitize.
        for field in ["history_text", "product_text", "reflection_text"]:
             if not input_data.get(field):
                 # Fail Fast on ANY missing input as per strict requirements for Guard
                 error_msg = f"[GuardAgent] Mandatory input '{field}' missing. Sanitization aborted."
                 logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
                 raise AgentExecutionError(
                     detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                     original_error=ValueError(error_msg),
                     agent_name="GuardAgent"
                 )

        # Pass through to BaseAgent
        result_obj = await super().execute(
            input_data=input_data,
            execution_context=execution_context,
            system_instruction=system_instruction,
            **kwargs
        )

        if isinstance(result_obj, GuardOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return GuardOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"GuardAgent returned {type(result_obj)} instead of GuardOutput"),
                 agent_name="GuardAgent"
             )

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Performs Python-based banned phrase checks and sanitization.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: ignored.

        Returns:
            str | None: None. Only side-effects (logging/validation).

        Raises:
            FatalInterruption: If banned phrases are detected.
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
                logger.error(f"{ErrorCodes.SECURITY_BANNED_PHRASE_DETECTED}: [GuardAgent] Banned Phrase Detected via Schema: {e}")
                
                # FatalInterruption is correctly imported now
                raise FatalInterruption(
                    step_name="GuardSecurityCheck",
                    reason="Banned Phrase Detected (Schema Validation)",
                    details={"error": str(e)},
                ) from e
            else:
                # For any other ValueError from Pydantic, raise AgentExecutionError
                logger.error(f"{ErrorCodes.AGENT_EXECUTION_CRITICAL}: [GuardAgent] Unexpected validation error during GuardInput processing: {e}")
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                    original_error=e,
                    agent_name="GuardAgent"
                ) from e

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
        def get_field(obj: Any, key: str) -> Any:
            if isinstance(obj, dict):
                return obj.get(key)
            return getattr(obj, key, None)

        def set_field(obj: Any, key: str, val: Any) -> None:
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
        # unless we store it on self during prepare_context (checked: we do).

        if hasattr(self, "_sanitization_threats") and self._sanitization_threats:
            threats = self._sanitization_threats
            logger.info(f"[GuardAgent] Reporting sanitization actions: {threats}")

            # Update security_check
            msg = "Järjestelmä poisti automaattisesti PII-tietoja"
            report_append = f"\n{msg}: {', '.join(threats)}."

            if isinstance(security_check, dict):
                # Mutable Dict
                security_check["anonymisointi_tehty"] = True
                current = security_check.get("tietosuoja_raportti") or ""
                if msg not in current:
                    security_check["tietosuoja_raportti"] = (current + report_append).strip()

                # If root data is dict, we modified it in place (ref)
                # If root data is Model, we need to update it
                if not is_dict:
                     # This case: Data is Model, but field is Dict? Unlikely with strict typing.
                     pass

            else:
                # Pydantic Model (Frozen)
                # 1. Update SecurityCheck
                updates = {"anonymisointi_tehty": True}
                current = getattr(security_check, "tietosuoja_raportti", "") or ""

                if msg not in current:
                    updates["tietosuoja_raportti"] = (current + report_append).strip()

                # Create allowed copy
                new_security_check = security_check.model_copy(update=updates)

                # 2. Update Root Object (GuardOutput)
                if not is_dict:
                    # Data is frozen GuardOutput
                    data = data.model_copy(update={"security_check": new_security_check})
                else:
                    # Data is dict, but security_check was object?
                    data["security_check"] = new_security_check

        return data

    def sanitize_input(self, input_data: dict[str, Any]) -> None:
        """Pre-hook: Sanitizes and anonymizes input data (PII Redaction).

        Args:
            input_data (dict[str, Any]): Inputs to scan.
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
