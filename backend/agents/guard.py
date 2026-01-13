"""Guard Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import FatalInterruption
from backend.models.domain import TaintedData

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

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
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes the security analysis and sanitization logic.

        Input State:
            - state.inputs.history_text
            - state.inputs.product_text
            - state.inputs.reflection_text
            - state.aux_data.banned_phrases (checked via hooks)

        Output State:
            - state.step_guard (TaintedData): Security report and PII/Phrase status.
            - state.inputs (Modified in place if PII redacted via hooks).

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
            - FatalInterruption: If strict banned phrases are detected (raises immediately).
        """
        return await super().execute(state, system_instruction, **kwargs)

    async def prepare_context(self, state: WorkflowState, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Performs Python-based banned phrase checks and sanitization.

        Args:
            state (WorkflowState): Current state.
            **kwargs: ignored.

        Returns:
            Optional[str]: None. Only side-effects on state.

        """
        # 1. Banned Phrase Check (Injects warning into prompt if found)
        self.check_banned_phrases_python(state)

        # 2. Input Sanitization (Modifies state inputs in-place)
        self.sanitize_input(state)

        return None

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """Lifecycle Hook: Post-Execution.

        Ensures tainted data structure is populated and banned phrases are flagged.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Processed state.

        """
        return self.ensure_tainted_data(state)

    def ensure_tainted_data(self, state: WorkflowState) -> WorkflowState:
        """Post-Hook: Ensures that the tainted data structure is correctly populated.

        Also performs strict Python-side banned phrase check.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Validated and potentially updated state.
        """
        logger.info("[GuardAgent] Running ensure_tainted_data...")

        if not state.step_guard:
            return state

        validated_data = state.step_guard

        # --- 1. PII Sanitization Reporting ---
        sanitization_log = state.aux_data.get("sanitization_log")
        if sanitization_log and sanitization_log.get("threats_detected"):
            threats = sanitization_log["threats_detected"]
            logger.info(f"[GuardAgent] Reporting sanitization actions: {threats}")
            if validated_data.security_check:
                validated_data.security_check.anonymisointi_tehty = True
                current_report = validated_data.security_check.tietosuoja_raportti or ""
                # Avoid duplicating if already present
                msg_part = "Järjestelmä poisti automaattisesti PII-tietoja"
                if msg_part not in current_report:
                    validated_data.security_check.tietosuoja_raportti = (
                        current_report + f"\n{msg_part}: {', '.join(threats)}."
                    ).strip()

        # --- 2. Python Banned Phrases Check Overlay ---
        try:
            # Load banned phrases from aux_data (Injected by Engine)
            banned_phrases = state.aux_data.get("banned_phrases", [])

            if banned_phrases:
                from backend.hooks.security import check_banned_phrases

                detected = []
                # Scan all inputs
                inputs_to_scan = [state.inputs.history_text, state.inputs.product_text, state.inputs.reflection_text]

                for text in inputs_to_scan:
                    if not text:
                        continue
                    found = check_banned_phrases(text, banned_phrases)
                    detected.extend(found)

                if detected:
                    # Deduplicate
                    detected = list(set(detected))
                    logger.warning(f"[GuardAgent] STRICT CHECK: Found banned phrases: {detected}")
                    validated_data.security_check.uhka_havaittu = True
                    if validated_data.security_check.adversariaalinen_simulaatio_tulos:
                        validated_data.security_check.adversariaalinen_simulaatio_tulos += (
                            f"\n[SYSTEM ALERT] Banned phrases detected by strict filter: {', '.join(detected)}"
                        )
                    else:
                        validated_data.security_check.adversariaalinen_simulaatio_tulos = (
                            f"[SYSTEM ALERT] Banned phrases detected by strict filter: {', '.join(detected)}"
                        )

        except Exception as e:
            logger.error(f"[GuardAgent] Banned phrase check failed: {e}")
            from backend.exceptions import FatalInterruption

            raise FatalInterruption("GuardSecurityCheck", f"Banned phrase check failed: {e}", {"error": str(e)}) from e

        return state

    def extract_text_from_inputs(self, state: WorkflowState) -> WorkflowState:
        """Public hook method (Pre-Hook).

        Legacy pass-through hook.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: The same state.

        """
        logger.info("[GuardAgent] PDF Extraction Pre-Hook: Pass-through (Handled by Engine).")
        return state

    def check_banned_phrases_python(self, state: WorkflowState) -> WorkflowState:
        """Public hook method (Pre-Hook).

        Scans inputs for banned phrases BEFORE the LLM sees them.
        Injects alerts into inputs if necessary.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Updated state.

        """
        logger.info("[GuardAgent] Executing Python-based Banned Phrases Scan (Pre-Hook)...")

        try:
            # Load banned phrases from aux_data (Injected by Engine)
            banned_phrases = state.aux_data.get("banned_phrases", [])

            if not banned_phrases:
                logger.warning("[GuardAgent] No banned_phrases found in state.aux_data. Skipping scan.")
                return state

            detected = []
            # Scan all inputs
            inputs_to_scan = {
                "History": state.inputs.history_text,
                "Product": state.inputs.product_text,
                "Reflection": state.inputs.reflection_text,
            }

            for key, text in inputs_to_scan.items():
                if not text:
                    continue
                text_lower = text.lower()
                for phrase in banned_phrases:
                    if phrase in text_lower:
                        detected.append(f"{phrase} ({key})")

            if detected:
                distinct_phrases = list(set(detected))
                logger.warning(f"[GuardAgent] PRE-HOOK: Found banned phrases: {distinct_phrases}")

                # INJECT WARNING into the product text so the LLM sees it clearly
                injection = (
                    f"\n\n[SYSTEM SECURITY ALERT]: The following BANNED PHRASES were detected in the input "
                    f"via strict regex scan: {', '.join(distinct_phrases)}. "
                    "You MUST reject this and flag 'uhka_havaittu' as True."
                )

                # We append it to product_text ensures it's part of the analyzed content
                state.inputs.product_text += injection

                # ECHO PROTOCOL: Log Security Event
                error_code = "SECURITY_BANNED_PHRASE_DETECTED"
                logger.error(f"{error_code}: Banned phrases found - {distinct_phrases}", exc_info=True)
                raise FatalInterruption(
                    "GuardSecurityCheck",
                    f"Banned phrases detected: {distinct_phrases}",
                    {"code": error_code, "phrases": distinct_phrases},
                )

        except Exception as e:
            error_code = "SECURITY_CHECK_CRITICAL_FAILURE"
            logger.error(f"{error_code}: Pre-hook scan failed - {e}", exc_info=True)
            # Ensure we raise a clean exception if not already raised
            if isinstance(e, FatalInterruption):
                raise e
            raise FatalInterruption(
                "GuardPreHook", f"Pre-hook scan failed: {e}", {"error": str(e), "code": error_code}
            ) from e

        return state

    def sanitize_input(self, state: WorkflowState) -> WorkflowState:
        """Pre-hook: Sanitizes and anonymizes input data (PII Redaction).

        Delegates to backend.hooks.security.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Updates state (aux_data & inputs).
        """
        logger.info("[GuardAgent] Running sanitize_input (Pre-Hook)...")
        from backend.hooks.security import sanitize_text

        inputs_to_scan = {
            "history_text": state.inputs.history_text,
            "product_text": state.inputs.product_text,
            "reflection_text": state.inputs.reflection_text,
        }

        updates = {}
        all_threats = []

        for key, value in inputs_to_scan.items():
            if not value:
                continue

            clean_text, threats = sanitize_text(value)

            if threats:
                formatted_threats = [f"{t} ({key})" for t in threats]
                all_threats.extend(formatted_threats)

            if clean_text != value:
                updates[key] = clean_text

        # Apply updates in-place
        if "history_text" in updates:
            state.inputs.history_text = updates["history_text"]
        if "product_text" in updates:
            state.inputs.product_text = updates["product_text"]
        if "reflection_text" in updates:
            state.inputs.reflection_text = updates["reflection_text"]

        # Store metadata about detection in aux_data
        state.aux_data["sanitization_log"] = {"threats_detected": all_threats, "timestamp": "Now"}

        if all_threats:
            logger.warning(f"[GuardAgent] PII Sanitization: {all_threats}")

        return state

    async def _update_state(
        self, state: WorkflowState, response_data: Any, output_key: str | None = None, **kwargs
    ) -> WorkflowState:
        return await super()._update_state(state, response_data, output_key=output_key, **kwargs)
