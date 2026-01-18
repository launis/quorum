"""Judge Agent implementation."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError
from backend.models.domain import EvaluationResult

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

    async def execute(
        self,
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
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

        # FAIL FAST: Configuration Check
        if not matrix_id:
            msg = "JUDGE_CONFIGURATION_MISSING: No matrix_id configured."
            logger.error(msg)
            raise AgentExecutionError(detail="JUDGE_CONFIGURATION_MISSING", original_error=ValueError(msg))

        if not repo:
            # Should hopefully not happen if framework is robust, but for typed safety:
            raise AgentExecutionError(
                detail="REPOSITORY_MISSING", original_error=ValueError("Repository not injected.")
            )

        component = await repo.get_component_by_id(matrix_id)
        if not component:
            raise AgentExecutionError(
                detail="MATRIX_NOT_FOUND", original_error=ValueError(f"Matrix '{matrix_id}' not found.")
            )

        # Use shared formatter service (Metadata-Driven)
        from backend.services.matrix_formatter import format_matrix_component

        base_prompt = format_matrix_component(component)

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

        # FAIL FAST: Configuration Check
        if not matrix_id:
            msg = "JUDGE_CONFIGURATION_MISSING: No matrix_id configured."
            logger.error(msg)
            raise AgentExecutionError(detail="JUDGE_CONFIGURATION_MISSING", original_error=ValueError(msg))

        if not repo:
            # Should hopefully not happen if framework is robust, but for typed safety:
            raise AgentExecutionError(
                detail="REPOSITORY_MISSING", original_error=ValueError("Repository not injected.")
            )

        component = await repo.get_component_by_id(matrix_id)
        if not component:
            raise AgentExecutionError(
                detail="MATRIX_NOT_FOUND", original_error=ValueError(f"Matrix '{matrix_id}' not found.")
            )

        # Use shared formatter service (Metadata-Driven)
        from backend.services.matrix_formatter import format_matrix_component

        base_prompt = format_matrix_component(component)

        # Inject Context/Inputs to be evaluated
        eval_ctx = []

        # Helper for serializing evidence
        def serialize_evidence(data: Any) -> str:
            if hasattr(data, "model_dump_json"):
                return data.model_dump_json(indent=2)
            if isinstance(data, dict):
                return json.dumps(data, indent=2, ensure_ascii=False)
            return str(data)

        # --- EVIDENCE COLLECTION STRATEGY ---
        # 1. Core Map (Analyst) - Token Optimized
        todistus_kartta = kwargs.get("todistus_kartta")
        if not todistus_kartta and state:
            todistus_kartta = getattr(state, "step_analyst", None)

        if todistus_kartta:
            content = serialize_evidence(todistus_kartta)
            eval_ctx.append(f"### TODISTUSKARTTA (PROCESSED EVIDENCE):\n{content}")
            logger.info("[JudgeAgent] Using TodistusKartta (Step 2) for evaluation.")

        # 2. Evidence Collection (Config-Driven + Auto-Discovery)
        # Scan state for known critic outputs defined in configuration.
        # Fallback to hardcoded list if config is missing (Safety Net).
        monitored_steps = config.get("monitored_steps")
        if not monitored_steps:
             logger.warning("[JudgeAgent] 'monitored_steps' missing in config. Using fallback allowlist.")
             monitored_steps = {
                "step_profiler": "PROFILOIJA (BIAS AUDIT)",
                "step_logician": "LOOGIKKO (LOGIC AUDIT)",
                "step_falsifier": "FALSIFIOIJA (CRITICAL AUDIT)",
                "step_causal": "KAUSAALINEN (IMPACT AUDIT)",
                "step_detector": "PERFORMATIIVISUUS (ILLUSION AUDIT)",
                "step_overseer": "VALVOJA (FACTUAL AUDIT)",
                "step_archivist": "ARKISTONHOITAJA (BEST PRACTICES)",
                "step_panel": "PANEELIN HAVAINNOT (PANEL AUDIT)"
            }

        found_evidence_count = 0
        for key, title in monitored_steps.items():
            # Check inputs first (explicit mapping), then state (implicit discovery)
            evidence = kwargs.get(key)
            if not evidence and state:
                evidence = getattr(state, key, None)
            
            if evidence:
                content = serialize_evidence(evidence)
                eval_ctx.append(f"### {title}:\n{content}")
                logger.info(f"[JudgeAgent] Auto-Discovered evidence: {key}")
                found_evidence_count += 1

        if found_evidence_count > 0:
            logger.info(f"[JudgeAgent] Successfully injected {found_evidence_count} evidence blocks.")

        # 4. Fallback to Raw Inputs 
        # Only if we literally have zero evidence maps (rare)
        if not eval_ctx:
            logger.warning("[JudgeAgent] No structured evidence found. Falling back to raw inputs.")
            try:
                if hasattr(state, "inputs") and state.inputs:
                    if getattr(state.inputs, "history_text", None):
                        eval_ctx.append(f"### CHAT HISTORY TO EVALUATE:\n{state.inputs.history_text}")
                    if getattr(state.inputs, "product_text", None):
                        eval_ctx.append(f"### PRODUCT TO EVALUATE:\n{state.inputs.product_text}")
                    if getattr(state.inputs, "reflection_text", None):
                        eval_ctx.append(f"### STUDENT REFLECTION:\n{state.inputs.reflection_text}")
            except Exception:
                pass

        if eval_ctx:
            return base_prompt + "\n\n" + "\n\n".join(eval_ctx)

        return base_prompt

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
            # MODERNIZATION FIX: Handle pre-hydrated Pydantic objects
            if isinstance(response_data, EvaluationResult):
                # Dump to dict to reuse the enrichment logic below (Matrix ID, Scale injection)
                response_data = response_data.model_dump()

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

                # 2. Update Primary State Field (CRITICAL FIX)
                # Without this, downstream agents (Reporter/Coach) see None for 'step_judge'
                if hasattr(state, self.state_field):
                    setattr(state, self.state_field, res_obj)

                logger.info(
                    f"[JudgeAgent] Saved EvaluationResult to state.audit_results['{step_id}'] "
                    f"and state.{self.state_field} (Scale: {res_obj.scale_min}-{res_obj.scale_max})"
                )

            return state

        except Exception as e:
            error_code = "JUDGE_STATE_UPDATE_FAILED"
            logger.error(f"{error_code}: Error updating state - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """Post-process hook.

        Note: Scoring logic is now applied via centralized HOOK_MAPPING (post_hooks in seed_data.json).
        """
        return state
