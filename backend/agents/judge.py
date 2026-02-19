"""Judge Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import JudgeDTO, JudgeInput, JudgeOutput, JudgeScoreCard

# 4. Domain Imports for Forward Ref Resolution
from backend.models.domain.analyst import AnalystOutput, SearchResult, SearchResultItem
from backend.models.domain.archivist import ArchivistOutput, ArchivistOutputDTO
from backend.models.domain.causal import CausalOutput, CausalAnalysis, CausalAnalysisData
from backend.models.domain.falsifier import FalsifierOutput, FalsifierData, WaltonStressTest, ReasoningFidelity
from backend.models.domain.guard import GuardOutput, TaintedDataContent, SanitizationResult
from backend.models.domain.logician import LogicianOutput, LogicianData, ToulminComponent, CognitiveLevel, WaltonScheme
from backend.models.domain.overseer import OverseerOutput, OverseerData
from backend.models.domain.panel import PanelOutput, PanelOutputDTO
from backend.models.domain.performativity import PerformativityOutput, PerformativityAnalysis, LinguisticsResult, PreMortemAnalysis
from backend.models.domain.profiler import ProfilerOutput

# Resolve refs
try:
    types_ns = {
        "AnalystOutput": AnalystOutput,
        "SearchResult": SearchResult,
        "SearchResultItem": SearchResultItem,
        "ArchivistOutput": ArchivistOutput,
        "ArchivistOutputDTO": ArchivistOutputDTO,
        "CausalOutput": CausalOutput,
        "CausalAnalysis": CausalAnalysis,
        "CausalAnalysisData": CausalAnalysisData,
        "FalsifierOutput": FalsifierOutput,
        "FalsifierData": FalsifierData,
        "WaltonStressTest": WaltonStressTest,
        "ReasoningFidelity": ReasoningFidelity,
        "GuardOutput": GuardOutput,
        "TaintedDataContent": TaintedDataContent,
        "SanitizationResult": SanitizationResult,
        "LogicianOutput": LogicianOutput,
        "LogicianData": LogicianData,
        "ToulminComponent": ToulminComponent,
        "CognitiveLevel": CognitiveLevel,
        "WaltonScheme": WaltonScheme,
        "OverseerOutput": OverseerOutput,
        "OverseerData": OverseerData,
        "PanelOutput": PanelOutput,
        "PanelOutputDTO": PanelOutputDTO,
        "PerformativityOutput": PerformativityOutput,
        "PerformativityAnalysis": PerformativityAnalysis,
        "LinguisticsResult": LinguisticsResult,
        "PreMortemAnalysis": PreMortemAnalysis,
        "ProfilerOutput": ProfilerOutput,
    }
    JudgeInput.model_rebuild(_types_namespace=types_ns)
except Exception as e:
    # Log warning but don't crash at import time if possible, though strict means crash.
    logging.getLogger(__name__).warning(f"JudgeInput rebuild failed: {e}")

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class JudgeAgent(BaseAgent[JudgeInput, JudgeOutput]):
    """Tuomari-agentti (Judge Agent).

    Refactored to support dynamic Evaluation Matrix configurations.
    """

    state_field = "step_judge"

    REQUIRES_KEYS = ["step_guard", "step_falsifier", "step_logician"]
    PRODUCES_KEYS = ["step_judge", "audit_results"]
    INPUT_SCHEMA = JudgeInput
    DTO_SCHEMA = JudgeDTO
    OUTPUT_SCHEMA = JudgeOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the JudgeOutput schema (English).

        Returns:
            type[BaseModel] | None: JudgeOutput schema.
        """
        return JudgeDTO

    async def execute(
        self,
        input_data: JudgeInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> JudgeOutput:
        """Executes the judgment/audit logic against the matrix.

        Args:
            input_data (JudgeInput): Strict inputs and audit results.
            execution_context (dict[str, Any] | None, optional): Config.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            JudgeOutput: JudgeOutput.

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
        
        if isinstance(result_obj, JudgeOutput):
            result = result_obj
        elif isinstance(result_obj, dict):
            # Strict Casting Phase 1
            result = JudgeOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"JudgeAgent returned {type(result_obj)} instead of JudgeOutput or dict"),
                 agent_name="JudgeAgent"
             )

        # STRICT SCALE & METADATA ENFORCEMENT
        # We manipulate the Pydantic Model directly using .model_copy()
        
        updates = {}
        
        # 1. Force Matrix ID
        if execution_context and "matrix_id" in execution_context:
            updates["matrix_id"] = execution_context["matrix_id"]
        
        # Use updated or existing (JudgeOutput now has matrix_id)
        matrix_id = updates.get("matrix_id", result.matrix_id) 
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
            updates["scale_min"] = scale["min"]
            updates["scale_max"] = scale["max"]

            # FIX: Propagate scale to child score_card (Singular in JudgeOutput)
            if result.score_card:
                new_card = result.score_card.model_copy(update={
                    "scale_min": scale["min"],
                    "scale_max": scale["max"]
                })
                updates["score_card"] = new_card

        except Exception as e:
            logger.critical(f"[JudgeAgent] STRICT SCALE RESOLUTION FAILED: {e}")
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e
            )

        # Apply updates so far
        result = result.model_copy(update=updates)

        # --- DETERMINISTIC SCORING HOOK ---
        # User Request: "Miten se lasketaan?" -> We use Python for math.
        from backend.hooks.scoring import enforce_scoring_penalties
        
        # Apply penalties to the result (Strict Pydantic Model)
        try:
            result = enforce_scoring_penalties(result, input_data)
        except Exception as e:
            logger.critical(f"[JudgeAgent] Scoring Hook Failed: {e}", exc_info=True)
            # STRICT FAIL FAST: No partial results. The scoring logic is mandatory.
            raise AgentExecutionError(
                detail=ErrorCodes.HOOK_EXECUTION_FAILED,
                original_error=e,
                agent_name="JudgeAgent"
            )

        # --- USER REQUEST: Semantic Labels in Reports ---
        # Inject labels into dimensions
        if result.score_card and result.score_card.dimensions and comp and comp.get("content"):
            criteria_list = comp["content"].get("criteria", [])
            label_map = {c.get("id"): c.get("label") for c in criteria_list if c.get("id") and c.get("label")}

            new_dimensions = []
            for dim in result.score_card.dimensions:
                if dim.dimension_id in label_map:
                    # Update label
                    new_dim = dim.model_copy(update={"dimension_label": label_map[dim.dimension_id]})
                    new_dimensions.append(new_dim)
                else:
                    # STRICT MODE: Fail Fast.
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                        original_error=ValueError(f"Strict Label Resolution Failed: Dimension ID '{dim.dimension_id}' not found in Matrix '{matrix_id}' criteria."),
                        agent_name="JudgeAgent"
                    )
            
            # Update score_card with new dimensions
            new_score_card = result.score_card.model_copy(update={"dimensions": new_dimensions})
            result = result.model_copy(update={"score_card": new_score_card})

        # FINAL RETURN (Already Validated)
        return result
    async def prepare_context(
        self,
        input_data: JudgeInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Loads and formats the Evaluation Matrix (rubric) from the repository/config.
        Injects the matrix instructions into the system prompt.

        Args:
            input_data (JudgeInput): Inputs.
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
        analyst_output = kwargs.get("step_analyst") or input_data.step_analyst

        if analyst_output:
            content = serialize_evidence(analyst_output)
            eval_ctx.append(f"### TODISTUSKARTTA (PROCESSED EVIDENCE):\n{content}")
            logger.info("[JudgeAgent] Using AnalystOutput (Step 2) for evaluation.")

        # 2. Evidence Collection (Config-Driven + Auto-Discovery)
        # Scan state for known critic outputs defined in configuration.
        monitored_steps = config.get("monitored_steps")
        if not monitored_steps:
             # FAIL FAST: monitored_steps is MANDATORY.
             msg = "JUDGE_CONFIGURATION_INVALID: 'monitored_steps' missing in config."
             logger.error(msg)
             raise AgentExecutionError(detail=ErrorCodes.AGENT_NOT_CONFIGURED, original_error=ValueError(msg), agent_name="JudgeAgent")

        found_evidence_count = 0
        for key, title in monitored_steps.items():
            # Check kwargs (injected) first, then inputs (model attributes)
            evidence = kwargs.get(key)
            if not evidence:
                # Dynamically access attribute from input_data model
                # Strict: access via getattr is necessary here because keys are dynamic (config-driven).
                # If the key is NOT in the model (but in config), it's a configuration/schema mismatch.
                try:
                    evidence = getattr(input_data, key)
                except AttributeError:
                    # Log warning but allow proceeding (maybe optional evidence?)
                    # strictly speaking, if config says "monitor step_foo" and input schema lacks "step_foo", it's a bug.
                    logger.warning(
                        f"[JudgeAgent] Configured step '{key}' not found in JudgeInput schema. "
                        "Check 'monitored_steps' config vs JudgeInput definition."
                    )
                    evidence = None

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
        """Lifecycle Hook: Post-Execution (Healing & Python Authority).
        
        Enforces:
        1. DETERMINISTIC MATH: Re-calculates total_score from dimensions.
        2. FAIL FAST: Raises error on empty dimensions or out-of-bounds scores.
        3. INTEGRITY: Ensures critical fields are present.
        """
        # 1. Access ScoreCard
        # response_data is JudgeDTO (Pydantic) or dict
        score_card = None
        if isinstance(response_data, dict):
            score_card = response_data.get("score_card")
        else:
            score_card = getattr(response_data, "score_card", None)
            
        if not score_card:
            # Let strict pydantic validation catch this later if missing,
            # or raise here if we want to fail fast on logic.
            # DTO schema says score_card is required, so we can skip strict check here
            # and let strict mode handle it, OR enforce it for "Healing".
            return response_data

        # 2. Access Dimensions
        dimensions = None
        if isinstance(score_card, dict):
            dimensions = score_card.get("dimensions", [])
        else:
            dimensions = getattr(score_card, "dimensions", [])

        # FAIL FAST: Empty Dimensions
        if not dimensions:
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_OUTPUT_SCHEMA,
                original_error=ValueError("Judge returned empty dimensions list. Assessment impossible."),
                agent_name="JudgeAgent"
            )

        # 3. Deterministic Math & Validation
        total_sum = 0.0
        count = 0
        
        # 3. Deterministic Math & Validation
        total_sum = 0.0
        count = 0
        
        # We need scale info for validation. 
        # CAUTION: scale_min/max might be in response_data or score_card.
        # If response_data is DTO, it has scale_min/max.
        scale_min = None
        scale_max = None
        
        if isinstance(response_data, dict):
             scale_min = response_data.get("scale_min")
             scale_max = response_data.get("scale_max")
        else:
             scale_min = getattr(response_data, "scale_min", None)
             scale_max = getattr(response_data, "scale_max", None)

        # FAIL FAST: Missing Scale (Part 18.2 No Default Values)
        if scale_min is None or scale_max is None:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_OUTPUT_SCHEMA,
                 original_error=ValueError("Judge output missing mandatory 'scale_min' or 'scale_max'. Cannot validate."),
                 agent_name="JudgeAgent"
             )

        # Validate Iterator
        for dim in dimensions:
            score = 0.0
            if isinstance(dim, dict):
                score = dim.get("score")
                if score is None:
                     raise AgentExecutionError(
                         detail=ErrorCodes.INVALID_OUTPUT_SCHEMA,
                         original_error=ValueError(f"Dimension {dim.get('dimension_id')} missing 'score'."),
                         agent_name="JudgeAgent"
                     )
            else:
                score = dim.score
            
            # STRICT BOUNDS CHECK
            # Part 14.1/14.2: If value is out of bounds, CRASH.
            if score < scale_min or score > scale_max:
                raise AgentExecutionError(
                    detail=ErrorCodes.VALIDATION_FAILED,
                    original_error=ValueError(f"Dimension score {score} is out of bounds [{scale_min}, {scale_max}]."),
                    agent_name="JudgeAgent"
                )
                
            total_sum += score
            count += 1
            
        # 4. Calculate Average
        calculated_average = total_sum / count if count > 0 else 0.0
        
        # 5. Overwrite (Healing)
        # We trust Python math over LLM hallucination.
        logger.info(f"[JudgeAgent] Recalculating Score: LLM says {getattr(score_card, "total_score", "N/A")} -> Python says {calculated_average}")
        
        if isinstance(score_card, dict):
            score_card["total_score"] = calculated_average
            return response_data
        else:
            # Pydantic is immutable-ish
            new_card = score_card.model_copy(update={"total_score": calculated_average})
            return response_data.model_copy(update={"score_card": new_card})
