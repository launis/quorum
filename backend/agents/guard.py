"""Guard Agent implementation."""

from __future__ import annotations

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes, FatalInterruption
from backend.models.domain import GuardDTO, GuardInput, GuardOutput

logger = logging.getLogger(__name__)


class GuardAgent(BaseAgent[GuardInput, GuardOutput]):
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

    INPUT_SCHEMA = GuardInput
    DTO_SCHEMA = GuardDTO
    OUTPUT_SCHEMA = GuardOutput

    async def execute(
        self,
        input_data: GuardInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> GuardOutput:
        """Executes the security analysis and sanitization logic.

        Args:
            input_data (GuardInput): Inputs including history_text, product_text, etc.
            execution_context (dict[str, Any] | None, optional): Context/Config.
            system_instruction (str | None, optional): Prompt override.
            **kwargs: Additional args.

        Returns:
            GuardOutput: The security report (TaintedData).

        Raises:
            ValueError: If mandatory inputs are missing.
        """
        # Store context for hooks
        self.execution_context = execution_context or {}

        # 0. RESOLVE CONTEXT (User Knowledge)
        # In Strict Model mode, input_data is immutable. We can't set organization_id on it easily.
        # But GuardInput doesn't strictly require organization_id (it's not in the model definition above, unlike other inputs).
        # Checking backend/models/domain/guard.py: GuardInput only has history, product, reflection.
        # So we don't need to inject organization_id into input_data for validation.
        # We just need it for execution context.

        # FAIL FAST: Mandatory fields are already validated by Pydantic during BaseAgent.execute -> INPUT_SCHEMA validation.
        # So we don't need manual checks for history/product_text unless we want custom error messages.
        # Pydantic raises ValidationError which BaseAgent catches or propagates.

        # Pass through to BaseAgent
        result_obj = await super().execute(
            input_data=input_data, execution_context=execution_context, system_instruction=system_instruction, **kwargs
        )

        from backend.models.domain.guard import TaintedDataContent

        tainted_data = TaintedDataContent(
            chat_history=input_data.history_text,
            product_text=input_data.product_text,
            reflection_text=input_data.reflection_text or "Ei erillistä reflektiota",
            safe_data="Unsanitized raw input"
        )

        if isinstance(result_obj, GuardOutput):
            return result_obj
        elif isinstance(result_obj, self.DTO_SCHEMA):
            # Promote DTO -> Domain Model
            promoted = self.OUTPUT_SCHEMA(
                **result_obj.model_dump(),
                tainted_data=tainted_data
            )
            return self._apply_python_authority(promoted)
        else:
            # Should be unreachable due to BaseAgent strictness
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                original_error=TypeError(f"GuardAgent returned {type(result_obj)} instead of GuardOutput"),
                agent_name="GuardAgent",
            )

    async def prepare_context(
        self, input_data: GuardInput, execution_context: dict[str, Any] | None, **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Performs Python-based banned phrase checks and sanitization.

        Args:
            input_data (GuardInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: ignored.

        Returns:
            str | None: None. Only side-effects (logging/validation).

        Raises:
            FatalInterruption: If banned phrases are detected.
        """
        # 1. Banned Phrase Check
        # Already handled by GuardInput validator if context was passed during creation?
        # Expect BaseAgent to have validated it?
        # Actually, BaseAgent validates INPUT_SCHEMA globally.
        # But banned phrases require context. BaseAgent might not pass context during initial validation if it constructs model early.
        # Let's re-run validation logic manually or trust the model if it was built with context.

        # We can manually enforce it here using the model instance
        try:
            banned_phrases = []
            if execution_context and "banned_phrases" in execution_context:
                banned_phrases = execution_context["banned_phrases"]

            # Check explicitly
            if banned_phrases:
                for field, value in input_data.model_dump().items():
                    if isinstance(value, str):
                        for phrase in banned_phrases:
                            if phrase.lower() in value.lower():
                                raise ValueError(
                                    f"SECURITY_BANNED_PHRASE_DETECTED: Found '{phrase}' in field '{field}'"
                                )

        except ValueError as e:
            if "SECURITY_BANNED_PHRASE_DETECTED" in str(e):
                logger.error(f"{ErrorCodes.SECURITY_BANNED_PHRASE_DETECTED}: [GuardAgent] Banned Phrase Detected: {e}")
                raise FatalInterruption(
                    step_name="GuardSecurityCheck",
                    reason="Banned Phrase Detected",
                    details={"error": str(e)},
                ) from e
            raise

        # 2. Input Sanitization (Local Effect Only)
        # We sanitize locally to log threats.
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

        # Strict Pydantic Enforcement
        if isinstance(data, GuardOutput):
            # Handle Model (Post-Validation or Re-Entry)
            logger.info("[GuardAgent] Running ensure_tainted_data (Model Mode)...")
            security_check = data.security_check

            # 1. PII Sanitization Reporting
            if hasattr(self, "_sanitization_threats") and self._sanitization_threats:
                threats = self._sanitization_threats
                logger.info(f"[GuardAgent] Reporting sanitization actions: {threats}")

                # Update security_check
                # Pydantic Model (Frozen)
                metrics_update: dict[str, Any] = {"anonymized": True}

                current_findings = security_check.pii_findings or []
                # Create new list
                new_findings = list(current_findings) + [t for t in threats if t not in current_findings]
                metrics_update["pii_findings"] = new_findings

                # Create updated SecurityCheck
                new_security_check = security_check.model_copy(update=metrics_update)

                # Update Root Object
                data = data.model_copy(update={"security_check": new_security_check})

            # 2. Enhanced Metadata (Context Injection)
            current_meta = data.metadata
            meta_updates = {}

            org_id = self.execution_context.get("organization_id")
            workflow_name = self.execution_context.get("workflow_name", "standard_workflow")

            if org_id:
                meta_updates["organization_id"] = org_id
            if workflow_name:
                meta_updates["workflow"] = workflow_name

            if current_meta and meta_updates:
                new_meta = current_meta.model_copy(update=meta_updates)
                data = data.model_copy(update={"metadata": new_meta})

            return data

        # Default fallback should not be reached due to strict mode
        logger.warning(f"[GuardAgent] ensure_tainted_data received unexpected type {type(data)}. Returning as-is.")
        return data

    def sanitize_input(self, input_data: GuardInput) -> None:
        """Pre-hook: Sanitizes and anonymizes input data (PII Redaction).

        Args:
            input_data (GuardInput): Inputs to scan.
        """
        logger.info("[GuardAgent] Running sanitize_input (Pre-Hook)...")
        from backend.hooks.security import sanitize_text

        # Using dot notation for Pydantic model
        inputs_to_scan = {
            "history_text": input_data.history_text,
            "product_text": input_data.product_text,
            "reflection_text": input_data.reflection_text,
        }

        all_threats = []

        for key, value in inputs_to_scan.items():
            if not value:
                continue

            clean_text, threats = sanitize_text(value)

            if threats:
                formatted_threats = [f"{t} ({key})" for t in threats]
                all_threats.extend(formatted_threats)

            # NOTE: In Pydantic V2 models are immutable by default implies frozen=True?
            # GuardInput doesn't strictly say frozen=True but likely preferred.
            # Even if mutable, modifying input_data here might not be reflected upstream if passed by value (unlikely for objects).
            # But BaseAgent holds the reference.
            # However, if we want to actually *use* the sanitized text in the LLM prompt, we need to ensure
            # BaseAgent uses this modified model.

            # If GuardInput is a standard BaseModel, it's mutable unless ConfigDict(frozen=True).
            # Checking guard.py: GuardInput class definition doesn't show frozen=True.

            if clean_text != value:
                setattr(input_data, key, clean_text)

        if all_threats:
            logger.warning(f"[GuardAgent] PII Sanitization: {all_threats}")
            # Store for post_process
            self._sanitization_threats = all_threats
