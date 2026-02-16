"""Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import AnalystOutput
from backend.models.state import WorkflowState

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Analyytikko-agentti (Analyst Agent).

    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    state_field = "step_analyst"

    # Contracts
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]
    PRODUCES_KEYS = ["step_analyst"]
    OUTPUT_SCHEMA = AnalystOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model for the agent's expected output.

        Returns:
            Optional[Type[BaseModel]]: The AnalystOutput schema.

        """
        return AnalystOutput

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> AnalystOutput:
        """Executes the analysis logic for Evidence Anchoring.

        Args:
            input_data (dict[str, Any]): Input texts (history, product, reflection).
            execution_context (dict[str, Any] | None, optional): Access to global state.
            system_instruction (str | None, optional): Prompt override.
            **kwargs: Additional parameters.

        Returns:
            AnalystOutput: The generated evidence map (AnalystOutput).

        Raises:
            ValueError: If input texts are too short (Fail Fast enforcement).
        """
        # FAIL FAST: Structural Validation
        # Since pre-hooks might not be configured, we enforce it here.
        inputs = input_data
        min_chars = 100
        for key in ["history_text", "product_text", "reflection_text"]:
            text = inputs.get(key, "")
            if not text or len(text) < min_chars:
                error_msg = (
                    f"[AnalystAgent] Input '{key}' is too short "
                    f"({len(text) if text else 0} chars). Analysis aborted."
                )
                logger.error(f"{ErrorCodes.EMPTY_INPUT}: {error_msg}")
                raise AgentExecutionError(
                    detail=ErrorCodes.EMPTY_INPUT,
                    original_error=ValueError(error_msg),
                )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, AnalystOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return AnalystOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"AnalystAgent returned {type(result_obj)} instead of AnalystOutput"),
                 agent_name="AnalystAgent"
             )

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
        """Lifecycle Hook: Post-Execution.

        Enforces sequential IDs for Hypotheses (PYTHON AUTHORITY).
        """
        # 1. Access hypotheses
        hypotheses = []

        # Helper to get hypotheses list
        if isinstance(response_data, BaseModel):
            hypotheses = getattr(response_data, "hypotheses", [])
        elif isinstance(response_data, dict):
            hypotheses = response_data.get("hypotheses", [])

        if not hypotheses:
            return response_data

        logger.info(f"[AnalystAgent] Enforcing Hypothesis IDs (Count: {len(hypotheses)})")

        updated_hypotheses: list[Any] = []
        changes_made = False

        for idx, hyp in enumerate(hypotheses, 1):
            new_id = f"HYP-{idx}"

            # Get current ID
            current_id = None
            if isinstance(hyp, BaseModel):
                current_id = getattr(hyp, "id", None)
            elif isinstance(hyp, dict):
                current_id = hyp.get("id")

            if current_id != new_id:
                # Create new hypothesis with updated ID
                if isinstance(hyp, BaseModel):
                    new_hyp = hyp.model_copy(update={"id": new_id})
                else:
                    # Fallback for dict/mapping
                    new_hyp = dict(hyp)
                    new_hyp["id"] = new_id

                updated_hypotheses.append(new_hyp)
                changes_made = True
            else:
                updated_hypotheses.append(hyp)

        if changes_made:
            # Update Response (Frozen or Dict)
            if isinstance(response_data, BaseModel):
                    return response_data.model_copy(update={"hypotheses": updated_hypotheses})
            else:
                    response_data["hypotheses"] = updated_hypotheses
                    return response_data

        return response_data
