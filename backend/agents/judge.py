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
            Optional[Type[BaseModel]]: EvaluationResult schema.
        """
        return EvaluationResult

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the judgment/audit logic against the matrix.

        Args:
            input_data (dict): Inputs and audit results.
            execution_context (dict): Config.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: EvaluationResult.
        """
        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)
        if isinstance(result_obj, BaseModel):
            result = result_obj.model_dump()
        else:
            result = result_obj



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
                detail="JUDGE_SCALE_RESOLUTION_FAILED",
                original_error=ValueError("Cannot resolve scale: Missing matrix_id or repository.")
            )

        try:
            # Re-fetch component to "hoist" the truth
            comp = await repo.get_component_by_id(matrix_id)
            if not comp or not comp.get("content"):
                 raise ValueError(f"Matrix component '{matrix_id}' not found or empty.")

            scale = comp.get("content", {}).get("scale")
            if not scale or "min" not in scale or "max" not in scale:
                 raise ValueError(f"Matrix '{matrix_id}' has no defined scale in DB.")

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
                detail="JUDGE_STRICT_SCALE_FAILURE",
                original_error=e
            )

            raise AgentExecutionError(
                detail="JUDGE_STRICT_SCALE_FAILURE",
                original_error=e
            )

        # --- FIX: DETERMINISTIC SCORING (User Request: "Miten se lasketaan?") ---
        # The LLM often hallucinates the 'total_score' (e.g., summing them up instead of averaging).
        # We enforces a strict mathematical AVERAGE of the dimensions to ensure consistency
        # and checking that it falls within the scale.

        def calculate_average_score(dimensions: list[dict]) -> float:
            if not dimensions:
                return 0.0
            
            total_sum = 0.0
            count = 0
            for d in dimensions:
                val = d.get("score")
                if val is not None:
                    # Handle string numbers if necessary
                    try:
                        total_sum += float(val)
                        count += 1
                    except (ValueError, TypeError):
                        pass
            
            if count == 0:
                return 0.0
                
            return round(total_sum / count, 2)

        # 1. Update Root Total Score
        if "dimensions" in result:
             # Just in case dimensions is None
             dims = result.get("dimensions") or []
             result["total_score"] = calculate_average_score(dims)
             logger.info(f"[JudgeAgent] Calculated Deterministic Total Score: {result['total_score']}")

        # 2. Update Child Score Cards (if any)
        if "score_cards" in result and isinstance(result["score_cards"], list):
            for card in result["score_cards"]:
                if isinstance(card, dict) and "dimensions" in card:
                    dims = card.get("dimensions") or []
                    card["total_score"] = calculate_average_score(dims)


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
                    raise ValueError(f"Strict Label Resolution Failed: Dimension ID '{d_id}' not found in Matrix '{matrix_id}' criteria.")
        # unless we want to keep it for backwards compat. EvaluationResult doesn't have it.
        # But BaseJSON allows extra fields. Let's keep it for safety if debugging.

        return result

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Loads and formats the Evaluation Matrix (rubric) from the repository/config.
        Injects the matrix instructions into the system prompt.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Config.
            **kwargs: Config and repository.

        Returns:
            Optional[str]: The formatted matrix context string.
        """
        config = execution_context or {}
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
            # Custom serializer for datetime consistency (ISO 8601)
            def json_default(obj):
                if hasattr(obj, "isoformat"):
                    return obj.isoformat()
                return str(obj)

            if hasattr(data, "model_dump_json"):
                return data.model_dump_json(indent=2)
            if isinstance(data, (dict, list)):
                return json.dumps(data, indent=2, ensure_ascii=False, default=json_default)
            return str(data)

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
             raise AgentExecutionError(detail="JUDGE_CONFIGURATION_INVALID", original_error=ValueError(msg))

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
            raise AgentExecutionError(detail="JUDGE_EVIDENCE_MISSING", original_error=ValueError(msg))

        if eval_ctx:
            return base_prompt + "\n\n" + "\n\n".join(eval_ctx)

        return base_prompt

    # _update_state removed (BaseAgent handles it now, returning dict)

    def post_process(self, response_data: Any) -> Any:
        # Scoring logic is in HOOKS
        return response_data
