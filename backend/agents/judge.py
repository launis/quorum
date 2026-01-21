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

    Refactored to support dynamic Evaluation Matrix configurations with legacy fallback.
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

        # --- NORMALIZATION LOGIC (Legacy -> Standard) ---
        # The Goal: ALWAYS return an EvaluationResult compatible dictionary.
        
        # Check if we have legacy 'pisteet' structure
        if "pisteet" in result and "dimensions" not in result:
             logger.info("[JudgeAgent] formatting legacy 'pisteet' to standardized 'dimensions'")
             
             dimensions = []
             pisteet = result.get("pisteet", {})
             total_sum = 0
             count = 0
             
             # Map specific legacy keys to dimensions
             # Note: Dimension IDs should match your Matrix definitions
             for key, item in pisteet.items():
                 if not item: continue
                 
                 # Heuristic mapping for IDs
                 dim_id = key.lower() 
                 if "analy" in dim_id: dim_id = "analysis"
                 elif "arvio" in dim_id: dim_id = "evaluation"
                 elif "syn" in dim_id: dim_id = "synthesis"
                 
                 score_val = item.get("arvosana", 0)
                 
                 try:
                     score_num = float(score_val)
                 except (ValueError, TypeError):
                     score_num = 0
                 
                 dimensions.append({
                     "dimension_id": dim_id,
                     "score": score_num,
                     "reasoning": item.get("perustelu", "")
                 })
                 total_sum += score_num
                 if score_num > 0: count += 1

             result["dimensions"] = dimensions
             
             # Calculate total score if missing
             if "total_score" not in result:
                 result["total_score"] = round(total_sum / count, 2) if count > 0 else 0
                 
        # Check 'kriittiset_havainnot_yhteenveto' -> 'critical_findings'
        if "kriittiset_havainnot_yhteenveto" in result and "critical_findings" not in result:
             result["critical_findings"] = result["kriittiset_havainnot_yhteenveto"]

        # Ensure mandatory EvaluationResult fields
        # Force-overwrite matrix_id from configuration to prevent LLM hallucinations
        # (LLM often returns the Matrix Name "Kognitiivinen..." instead of ID "matrix_standard_v1")
        if execution_context and "matrix_id" in execution_context:
            result["matrix_id"] = execution_context["matrix_id"]
        elif "matrix_id" not in result:
             result["matrix_id"] = "unknown_matrix"
        
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

        except Exception as e:
            logger.critical(f"[JudgeAgent] STRICT SCALE RESOLUTION FAILED: {e}")
            raise AgentExecutionError(
                detail="JUDGE_STRICT_SCALE_FAILURE", 
                original_error=e
            )

        if "critical_findings" not in result: result["critical_findings"] = []
        if "dimensions" not in result: result["dimensions"] = []
        if "total_score" not in result: result["total_score"] = 0

        # Note: We deliberately drop 'pisteet' from the final standard object 
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
            if hasattr(data, "model_dump_json"):
                return data.model_dump_json(indent=2)
            if isinstance(data, dict):
                return json.dumps(data, indent=2, ensure_ascii=False)
            return str(data)

        # --- EVIDENCE COLLECTION STRATEGY ---
        # 1. Core Map (Analyst) - Token Optimized
        todistus_kartta = kwargs.get("todistus_kartta")
        if not todistus_kartta:
            todistus_kartta = input_data.get("step_analyst")

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

        # 4. Fallback to Raw Inputs 
        # Only if we literally have zero evidence maps (rare)
        if not eval_ctx:
            logger.warning("[JudgeAgent] No structured evidence found. Falling back to raw inputs.")
            try:
                # Basic keys expected in input_data
                if input_data.get("history_text"):
                    eval_ctx.append(f"### CHAT HISTORY TO EVALUATE:\n{input_data['history_text']}")
                if input_data.get("product_text"):
                    eval_ctx.append(f"### PRODUCT TO EVALUATE:\n{input_data['product_text']}")
                if input_data.get("reflection_text"):
                    eval_ctx.append(f"### STUDENT REFLECTION:\n{input_data['reflection_text']}")
            except Exception:
                pass

        if eval_ctx:
            return base_prompt + "\n\n" + "\n\n".join(eval_ctx)

        return base_prompt

    # _update_state removed (BaseAgent handles it now, returning dict)
    
    def post_process(self, response_data: Any) -> Any:
        # Scoring logic is in HOOKS
        return response_data
