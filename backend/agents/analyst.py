"""Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import AnalystDTO, AnalystInput, AnalystOutput
from backend.models.state import WorkflowState

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent[AnalystInput, AnalystOutput]):
    """Analyytikko-agentti (Analyst Agent).

    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    state_field = "step_analyst"

    # Contracts
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]
    PRODUCES_KEYS = ["step_analyst"]
    INPUT_SCHEMA = AnalystInput
    DTO_SCHEMA = AnalystDTO
    OUTPUT_SCHEMA = AnalystOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model for the agent's expected output.

        Returns:
            Optional[Type[BaseModel]]: The AnalystOutput schema.

        """
        return AnalystDTO

    async def execute(
        self,
        input_data: AnalystInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> AnalystOutput:
        """Executes the analysis logic for Evidence Anchoring.

        Args:
            input_data (AnalystInput): Input texts (history, product, reflection).
            execution_context (dict[str, Any] | None, optional): Access to global state.
            system_instruction (str | None, optional): Prompt override.
            **kwargs: Additional parameters.

        Returns:
            AnalystOutput: The generated evidence map (AnalystOutput).

        Raises:
            ValueError: If input texts are too short (Fail Fast enforcement).
        """
        # 0. Context Injection (Truth Protocol) - RAG
        # Note: input_data is immutable (Frozen). We cannot inject "rag_context" into it.
        # We must use execution_context or kwargs to pass RAG context to LLM Prompt,
        # OR prepare_context hook modifies system prompt.
        # BaseAgent.execute calls prepare_context.
        # But if we rely on input_data having it...
        # The prompt template {{rag_context}} looks for it in input_data (d).
        # We need to inject it into the prompt variables passed to provider.
        # But BaseAgent passes input_data.model_dump() to provider? No, it uses input_data as is.
        # If InputT is passed to LLM...
        # We should use prepare_context to return additional text.

        # For now, let's keep the logic but adapt to Read-Only input_data.
        # We cannot do `input_data["rag_context"] = ...`

        if execution_context:
            step_context = execution_context.get("step_context")
            if step_context:
                # ... extraction logic ...
                pass
                # We can't easily inject into frozen model.
                # We'll assume the System Prompt or prepare_context handles it.
                # Or we pass it in kwargs?
                # Let's trust prepare_context to handle dynamic context injection (which BaseAgent does).

        # FAIL FAST: Structural Validation
        # Strict Input Validation (Pydantic) handles types.
        # Length check:
        # Check history_text.
        text = input_data.history_text
        min_chars = 100
        if not text or len(text) < min_chars:
            error_msg = (
                f"[AnalystAgent] Input 'history_text' is too short "
                f"({len(text) if text else 0} chars). Analysis aborted."
            )
            logger.error(f"{ErrorCodes.EMPTY_INPUT}: {error_msg}")
            raise AgentExecutionError(
                detail=ErrorCodes.EMPTY_INPUT,
                original_error=ValueError(error_msg),
            )

        # BaseAgent guarantees AnalystOutput or raises error
        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)
        return result_obj

    def verify_structure(self, state: WorkflowState) -> WorkflowState:
        """HOOK: verify_structure.

        Pre-hook that validates whether the inputs have sufficient content for analysis.
        Delegates the actual check to the 'backend.hooks.validation' module.

        Args:
            state (WorkflowState): The current workflow state.

        Returns:
            WorkflowState: The validated workflow state.

        """
        logger.info("[AnalystAgent] Delegating to Validation Hook...")
        from backend.hooks.validation import verify_structure

        return verify_structure(state)

    def post_process(self, response_data: Any) -> Any:
        """Lifecycle Hook: Post-Execution (Healing).

        Enforces sequential IDs for Hypotheses (PYTHON AUTHORITY).

        PATTERN: Healing / Late Validation
        This hook receives the raw Dict from the LLM *before* strict Pydantic validation.
        This allows us to patch structural issues (like missing IDs) that would otherwise
        cause the validation to fail.

        Args:
            response_data (Any): Raw Dict (usually) or Pydantic Model.

        Returns:
            Any: Healed data ready for validation.
        """
        # 1. Access hypotheses
        hypotheses = []
        is_dict = isinstance(response_data, dict)

        if is_dict:
            hypotheses = response_data.get("hypotheses", [])
        else:
            # Strict Pydantic Access
            hypotheses = response_data.hypotheses or []

        if not hypotheses:
            return response_data

        logger.info(f"[AnalystAgent] Enforcing Hypothesis Order & IDs (Count: {len(hypotheses)})")

        # --- SORTING AUTHORITY (Deterministic) ---
        # 1. Sort by Evidence Found (True first)
        # 2. Sort by Original ID (Stable tie-breaker)
        def sort_key(h):
            # Access fields safely whether dict or object
            evidence = False
            orig_id = ""
            if isinstance(h, dict):
                evidence = h.get("evidence_found", False)
                orig_id = h.get("id", "")
            else:
                evidence = getattr(h, "evidence_found", False)
                orig_id = getattr(h, "id", "")

            # Tuple: (Has Evidence DESC, Original ID ASC)
            # False < True, so reverse boolean? Or use -1 for True?
            # evidence is boolean. True=1, False=0.
            # We want True first. So sort by (not evidence, orig_id)
            return (not evidence, orig_id)

        # Sort the list
        hypotheses.sort(key=sort_key)

        updated_hypotheses: list[Any] = []
        changes_made = True  # Force update since we sorted in-place (or need to reflect order)

        for idx, hyp in enumerate(hypotheses, 1):
            new_id = f"HYP-{idx:03d}"  # Zero-padded for clean sorting (HYP-001)

            # Access ID
            current_id = None
            if isinstance(hyp, dict):
                current_id = hyp.get("id")
            else:
                current_id = hyp.id

            if current_id != new_id:
                # Update ID
                if isinstance(hyp, dict):
                    new_hyp = hyp.copy()
                    new_hyp["id"] = new_id
                    updated_hypotheses.append(new_hyp)
                else:
                    new_hyp = hyp.model_copy(update={"id": new_id})
                    updated_hypotheses.append(new_hyp)
            else:
                updated_hypotheses.append(hyp)

        if changes_made:
            if is_dict:
                response_data["hypotheses"] = updated_hypotheses
                return response_data
            else:
                return response_data.model_copy(update={"hypotheses": updated_hypotheses})

        return response_data
