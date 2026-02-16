"""Judge Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import EvaluationResult

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class JudgeAgent(BaseAgent):
    """Tuomari-agentti (Judge Agent).

    Refactored to support dynamic Evaluation Matrix configurations.
    """

    state_field = "step_judge"

    REQUIRES_KEYS = ["step_guard", "step_falsifier", "step_logician"]
    PRODUCES_KEYS = ["step_judge", "audit_results"]
    OUTPUT_SCHEMA = EvaluationResult

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the EvaluationResult schema (English).

        Returns:
            type[BaseModel] | None: EvaluationResult schema.
        """
        return EvaluationResult

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> EvaluationResult:
        """Executes the judgment/audit logic against the matrix.

        Args:
            input_data (dict[str, Any]): Inputs and audit results.
            execution_context (dict[str, Any] | None, optional): Config.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            EvaluationResult: EvaluationResult.

        Raises:
            AgentExecutionError: If strict scale resolution fails.
        """
        # STRICT FAIL FAST: Judge requires scoring_logic to function.
        # This is typically passed in execution_context.
        if not execution_context or "scoring_logic" not in execution_context:
             # Check if inputs contain it? Assuming standard flow, it's config.
             # If "matrix_id" is provided, we might fetch logic, but basic scoring_logic is required.
             if not (execution_context and execution_context.get("matrix_id")):
                  raise AgentExecutionError(
                      detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                      original_error=ValueError("JudgeAgent: Missing mandatory context 'scoring_logic' (or 'matrix_id'). Cannot evaluate without rules."),
                      agent_name="JudgeAgent"
                  )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)
        
        if isinstance(result_obj, EvaluationResult):
            result = result_obj.model_dump() # We need dict to inject fields, then re-validate or just use model logic
        elif isinstance(result_obj, dict):
            result = result_obj
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"JudgeAgent returned {type(result_obj)} instead of EvaluationResult or dict"),
                 agent_name="JudgeAgent"
             )



        # Ensure mandatory EvaluationResult fields
        # Force-overwrite matrix_id from configuration to prevent LLM hallucinations
        # (LLM often returns the Matrix Name "Kognitiivinen..." instead of ID "matrix_standard_v1")
        if execution_context and "matrix_id" in execution_context:
            result["matrix_id"] = execution_context["matrix_id"]

        # STRICT SCALE ENFORCEMENT (User Mandate: "ikinä ei saa palata default arvoihin")
        # We must fetch the Truth from the Database. If we can't, we crash.
        matrix_id = result.get("matrix_id")
        repo = kwargs.get("repository")

        if not matrix_id or not repo:
             raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError("Cannot resolve scale: Missing matrix_id or repository.")
            )

        try:
            # Re-fetch component to "hoist" the truth
            comp = await repo.get_component_by_id(matrix_id)
            if not comp or not comp.get("content"):
                 raise AgentExecutionError(
                     detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                     original_error=ValueError(f"Matrix component '{matrix_id}' not found or empty."),
                     agent_name="JudgeAgent"
                 )

            scale = comp.get("content", {}).get("scale")
            if not scale or "min" not in scale or "max" not in scale:
                 raise AgentExecutionError(
                     detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                     original_error=ValueError(f"Matrix '{matrix_id}' has no defined scale in DB."),
                     agent_name="JudgeAgent"
                 )

            # FORCE OVERWRITE - The DB is the only Truth.
            result["scale_min"] = scale["min"]
            result["scale_max"] = scale["max"]

            # FIX: Propagate scale to all child score_cards if present
            # This ensures bff_transformer can rigorously validate each card.
            if "score_cards" in result and isinstance(result["score_cards"], list):
                for card in result["score_cards"]:
                    if isinstance(card, dict):
                        card["scale_min"] = scale["min"]
                        card["scale_max"] = scale["max"]

        except Exception as e:
            logger.critical(f"[JudgeAgent] STRICT SCALE RESOLUTION FAILED: {e}")
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e
            )

        # --- FIX: DETERMINISTIC SCORING (User Request: "Miten se lasketaan?") ---
        # The LLM often hallucinates the 'total_score' (e.g., summing them up instead of averaging).
        # We enforces a strict mathematical AVERAGE of the dimensions to ensure consistency
        # and checking that it falls within the scale.

        # 1. Update Root Total Score
        # SCORING AUTHORITY MOVED TO HOOK: 'apply_scoring_logic'
        # We do NOT calculate averages here. We trust the Hook to overwrite the LLM's raw output.
        # This prevents "Ghost Logic" where the Agent and Hook compete for truth.
        # The LLM might output a score, but the Hook is the final authority.
        pass

        # 2. Update Child Score Cards (if any) - Handled by Hook if necessary, or left as is for now.
        pass


        if "critical_findings" not in result:
            result["critical_findings"] = []



        # --- USER REQUEST: Semantic Labels in Reports ---
        # Populate 'dimension_label' using the source of truth (DB Component).
        # result["dimensions"] has [{dimension_id, score, ...}]
        # comp["content"]["criteria"] has [{id, label, ...}]
        if "dimensions" in result and result["dimensions"] and comp and comp.get("content"):
            criteria_list = comp["content"].get("criteria", [])
            # Create lookup map: id -> label
            label_map = {}
            for c in criteria_list:
                c_id = c.get("id")
                c_label = c.get("label")
                if c_id and c_label:
                    label_map[c_id] = c_label

            # Inject labels
            for dim in result["dimensions"]:
                d_id = dim.get("dimension_id")
                if d_id in label_map:
                    dim["dimension_label"] = label_map[d_id]
                else:
                    # STRICT MODE: Fail Fast.
                    # The database configuration MUST match the agent output.
                    # If we don't know the label, the Matrix Config is likely desynchronized or corrupt.
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                        original_error=ValueError(f"Strict Label Resolution Failed: Dimension ID '{d_id}' not found in Matrix '{matrix_id}' criteria."),
                        agent_name="JudgeAgent"
                    )
        # unless we want to keep it for backwards compat. EvaluationResult doesn't have it.
        # But BaseJSON allows extra fields. Let's keep it for safety if debugging.

        # FINAL VALIDATION & CAST
        try:
             # If we modified dictionary, re-validate
             final_result = EvaluationResult(**result)
             return final_result
        except Exception as e:
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
                 original_error=e,
                 agent_name="JudgeAgent"
             )

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Loads and formats the Evaluation Matrix (rubric) from the repository/config.
        Injects the matrix instructions into the system prompt.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Config.
            **kwargs: Config and repository.

        Returns:
            str | None: The formatted matrix context string or None.

        Raises:
            AgentExecutionError: If configuration is invalid.
        """
        config = execution_context or {}
        matrix_id = config.get("matrix_id")
        repo = kwargs.get("repository")

        # FAIL FAST: Configuration Check
        if not matrix_id:
            msg = "JUDGE_CONFIGURATION_MISSING: No matrix_id configured."
            logger.error(msg)
            # Use SSOT ErrorCode
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError(msg)
            )

        if not repo:
            # Should hopefully not happen if framework is robust, but for typed safety:
            raise AgentExecutionError(
                detail=ErrorCodes.INTERNAL_SERVER_ERROR,
                original_error=ValueError("Repository not injected.")
            )

        component = await repo.get_component_by_id(matrix_id)
        if not component:
            raise AgentExecutionError(
                detail=ErrorCodes.WORKFLOW_EXECUTION_FAILED,
                original_error=ValueError(f"Matrix '{matrix_id}' not found.")
            )

        # Use shared formatter service (Metadata-Driven)
        from backend.services.matrix_formatter import format_matrix_component

        base_prompt = format_matrix_component(component)

        # Inject Context/Inputs to be evaluated
        eval_ctx = []

        from backend.utils.json_utils import flexible_json_dump

        # Helper for serializing evidence
        def serialize_evidence(data: Any) -> str:
            return flexible_json_dump(data)

        # --- EVIDENCE COLLECTION STRATEGY ---
        # 1. Core Map (Analyst) - Token Optimized
        analyst_output = kwargs.get("step_analyst")
        if not analyst_output:
            analyst_output = input_data.get("step_analyst")

        if analyst_output:
            content = serialize_evidence(analyst_output)
            eval_ctx.append(f"### TODISTUSKARTTA (PROCESSED EVIDENCE):\n{content}")
            logger.info("[JudgeAgent] Using AnalystOutput (Step 2) for evaluation.")

        # 2. Evidence Collection (Config-Driven + Auto-Discovery)
        # Scan state for known critic outputs defined in configuration.
        # Fallback to hardcoded list if config is missing (Safety Net) -> REMOVED per user request
        monitored_steps = config.get("monitored_steps")
        if not monitored_steps:
             # FAIL FAST: monitored_steps is MANDATORY.
             msg = "JUDGE_CONFIGURATION_INVALID: 'monitored_steps' missing in config."
             logger.error(msg)
             raise AgentExecutionError(detail=ErrorCodes.AGENT_NOT_CONFIGURED, original_error=ValueError(msg), agent_name="JudgeAgent")

        found_evidence_count = 0
        for key, title in monitored_steps.items():
            # Check inputs first (explicit mapping), then input_data
            evidence = kwargs.get(key)
            if not evidence:
                evidence = input_data.get(key)

            if evidence:
                content = serialize_evidence(evidence)
                eval_ctx.append(f"### {title}:\n{content}")
                logger.info(f"[JudgeAgent] Auto-Discovered evidence: {key}")
                found_evidence_count += 1

        if found_evidence_count > 0:
            logger.info(f"[JudgeAgent] Successfully injected {found_evidence_count} evidence blocks.")

        # 4. STRICT EVIDENCE REQUIREMENT
        # We must have structured evidence or an AnalystOutput.
        if not eval_ctx:
            msg = "JUDGE_EVIDENCE_MISSING: No structured evidence found (Analyst or Critic outputs)."
            logger.error(f"[JudgeAgent] {msg}")
            raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=ValueError(msg), agent_name="JudgeAgent")

        if eval_ctx:
            return base_prompt + "\n\n" + "\n\n".join(eval_ctx)

        return base_prompt

    # _update_state removed (BaseAgent handles it now, returning dict)

    def post_process(self, response_data: Any) -> Any:
        # Scoring logic is in HOOKS
        return response_data
