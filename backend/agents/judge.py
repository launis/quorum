"""Judge Agent implementation."""
from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import (
    EvaluationResult,
)

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class JudgeAgent(BaseAgent):
    """Tuomari-agentti (Judge Agent).
    Refactored to support dynamic Evaluation Matrix configurations with legacy fallback.
    """

    state_field = "step_judge"

    REQUIRES_KEYS = ["step_guard", "step_falsifier", "step_logician"]
    PRODUCES_KEYS = ["step_judge", "audit_results"]
    OUTPUT_SCHEMA = EvaluationResult

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the EvaluationResult schema.

        Returns:
            Optional[Type[BaseModel]]: EvaluationResult schema.
        """
        return EvaluationResult

    async def execute(self, state: WorkflowState, system_instruction: str | None = None, **kwargs) -> WorkflowState:
        """Executes the judgment/audit logic against the matrix.

        Input State:
            - state.inputs (history_text, product_text, reflection_text)
            - state.audit_results (read for context if needed)

        Output State:
            - state.step_judge (EvaluationResult): The primary evaluation result.
            - state.audit_results [Dict]: Updated with the evaluation result keyed by step_id.

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
            - ValueError: If Matrix ID is invalid or missing.
        """
        return await super().execute(state, system_instruction, **kwargs)

    async def prepare_context(self, state: WorkflowState, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Loads and formats the Evaluation Matrix (rubric) from the repository/config.
        Injects the matrix instructions into the system prompt.

        Args:
            state (WorkflowState): The current workflow state.
            **kwargs: Config and repository.

        Returns:
            Optional[str]: The formatted matrix context string.
        """
        config = kwargs.get("execution_config", {})
        matrix_id = config.get("matrix_id")
        repo = kwargs.get("repository")

        if not matrix_id:
            logger.warning("[JudgeAgent] No matrix_id configured.")
            return None

        if not repo:
            return None

        component = await repo.get_component_by_id(matrix_id)
        if not component:
            return f"ERROR: Matrix '{matrix_id}' not found."

        base_prompt = self._format_matrix_prompt(component)

        # Inject Context/Inputs to be evaluated
        eval_ctx = []
        try:
            if hasattr(state, "inputs") and state.inputs:
                if getattr(state.inputs, "history_text", None):
                    eval_ctx.append(f"### CHAT HISTORY TO EVALUATE:\n{state.inputs.history_text}")
                if getattr(state.inputs, "product_text", None):
                    eval_ctx.append(f"### PRODUCT TO EVALUATE:\n{state.inputs.product_text}")
                if getattr(state.inputs, "reflection_text", None):
                    eval_ctx.append(f"### STUDENT REFLECTION:\n{state.inputs.reflection_text}")
        except Exception:
            # Tolerated failure in prompt decoration
            pass

        if eval_ctx:
            return base_prompt + "\n\n" + "\n\n".join(eval_ctx)

        return base_prompt

    def _format_matrix_prompt(self, component: dict) -> str:
        """Formats a JSON-based Evaluation Matrix into a human-readable prompt string.

        Args:
            component (dict): The matrix component structure.

        Returns:
            str: The formatted string.
        """
        content = component.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                return "Error parsing matrix."

        name = content.get("name", "Audit Matrix")
        desc = content.get("description", "")
        role = content.get("role_description", "You are the Evaluator.")
        criteria = content.get("criteria", [])
        scale = content.get("scale", {"min": 1, "max": 4})

        prompt_lines = [
            f"### ROLE: {role}",
            f"### EVALUATION MATRIX: {name}",
            f"Description: {desc}",
            f"Scale: {scale.get('min')}-{scale.get('max')}",
            "",
            "### CRITERIA FOR EVALUATION:",
        ]

        for crit in criteria:
            c_label = crit.get("label", "Unknown")
            c_instr = crit.get("instruction", "")
            c_id = crit.get("id", "unknown")
            c_anchors = crit.get("anchors", {})

            prompt_lines.append(f"#### Dimension: {c_label} (ID: {c_id})")
            prompt_lines.append(f"Instruction: {c_instr}")
            prompt_lines.append("Proficiency Levels (Anchors):")
            try:
                sorted_anchors = sorted(c_anchors.items(), key=lambda x: int(x[0]))
            except Exception:
                sorted_anchors = c_anchors.items()

            for lvl, text in sorted_anchors:
                prompt_lines.append(f"  - Level {lvl}: {text}")
            prompt_lines.append("")

        return "\n".join(prompt_lines)

    async def _update_state(
        self, state: WorkflowState, response_data: Any, output_key: str | None = None, **kwargs
    ) -> WorkflowState:
        """Updates the state with the judge's evaluation result.

        Supports dynamic matrix ID handling and storing extra metadata (like scale min/max).

        Args:
            state (WorkflowState): Current state.
            response_data (Any): The LLM response (data).
            output_key (Optional[str]): Target key (default uses state_field).
            **kwargs: Extra execution config.

        Returns:
            WorkflowState: Updated state.

        Raises:
             Exception: If update fails.
        """
        step_id = kwargs.get("step_id", output_key or self.state_field or "unknown_step")

        try:
            if isinstance(response_data, dict):
                # Force matrix_id from config if available (trust config over LLM hallucination)
                config = kwargs.get("execution_config", {})
                forced_id = config.get("matrix_id")
                if forced_id:
                    response_data["matrix_id"] = forced_id
                elif "matrix_id" not in response_data or not response_data["matrix_id"]:
                    response_data["matrix_id"] = config.get("matrix_id", "unknown")

                # Inject Scale Metadata if available
                repo = kwargs.get("repository")
                if repo:
                    mat_id = response_data.get("matrix_id")
                    comp = await repo.get_component_by_id(mat_id)
                    if comp:
                        content = comp.get("content", {})
                        if isinstance(content, str):
                            try:
                                content = json.loads(content)
                            except Exception:
                                content = {}
                        scale = content.get("scale", {})
                        response_data["scale_min"] = scale.get("min", 1)
                        response_data["scale_max"] = scale.get("max", 5)

                res_obj = EvaluationResult(**response_data)

                # 1. Update Dynamic Store
                state.audit_results[step_id] = res_obj
                logger.info(
                    f"[JudgeAgent] Saved EvaluationResult to state.audit_results['{step_id}'] (Scale: {res_obj.scale_min}-{res_obj.scale_max})"
                )

            return state

        except Exception as e:
            logger.error(f"[JudgeAgent] Error updating state: {e}")
            raise e

    def post_process(self, state: WorkflowState) -> WorkflowState:
        # We rely on _update_state for population.
        return state
