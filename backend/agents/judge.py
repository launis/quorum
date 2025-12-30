from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import TuomioJaPisteet, EvaluationResult, DimensionResultItem, Pisteet, PisteetKriteeri, Metadata, MestaruusPoikkeama, AitousEpaily, KonfliktinRatkaisu
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

class JudgeAgent(BaseAgent):
    """
    Tuomari-agentti (Judge Agent).
    Refactored to support dynamic Evaluation Matrix configurations with legacy fallback.
    """

    state_field = "step_judge" 
    
    REQUIRES_KEYS = ["step_guard", "step_falsifier", "step_logician"] 
    PRODUCES_KEYS = ["step_judge", "audit_results"]
    OUTPUT_SCHEMA = EvaluationResult 

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return EvaluationResult

    async def prepare_context(self, state: WorkflowState, **kwargs) -> Optional[str]:
        config = kwargs.get('execution_config', {})
        matrix_id = config.get('matrix_id')
        repo = kwargs.get('repository')
        
        if not matrix_id:
            logger.warning("[JudgeAgent] No matrix_id configured.")
            return None
        
        if not repo:
             return None

        component = repo.get_component_by_id(matrix_id)
        if not component:
            return f"ERROR: Matrix '{matrix_id}' not found."
            
        base_prompt = self._format_matrix_prompt(component)
        
        # Inject Context/Inputs to be evaluated
        eval_ctx = []
        try:
            if hasattr(state, 'inputs') and state.inputs:
                if getattr(state.inputs, 'history_text', None):
                    eval_ctx.append(f"### CHAT HISTORY TO EVALUATE:\n{state.inputs.history_text}")
                if getattr(state.inputs, 'product_text', None):
                    eval_ctx.append(f"### PRODUCT TO EVALUATE:\n{state.inputs.product_text}")
                if getattr(state.inputs, 'reflection_text', None):
                    eval_ctx.append(f"### STUDENT REFLECTION:\n{state.inputs.reflection_text}")
        except Exception:
            # Tolerated failure in prompt decoration
            pass

        if eval_ctx:
             return base_prompt + "\n\n" + "\n\n".join(eval_ctx)
             
        return base_prompt

    def _format_matrix_prompt(self, component: dict) -> str:
        content = component.get('content', {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                return "Error parsing matrix."
        
        name = content.get('name', 'Audit Matrix')
        desc = content.get('description', '')
        role = content.get('role_description', 'You are the Evaluator.')
        criteria = content.get('criteria', [])
        scale = content.get('scale', {'min': 1, 'max': 4})
        
        prompt_lines = [
            f"### ROLE: {role}",
            f"### EVALUATION MATRIX: {name}",
            f"Description: {desc}",
            f"Scale: {scale.get('min')}-{scale.get('max')}",
            "",
            "### CRITERIA FOR EVALUATION:",
        ]
        
        for crit in criteria:
            c_label = crit.get('label', 'Unknown')
            c_instr = crit.get('instruction', '')
            c_id = crit.get('id', 'unknown')
            c_anchors = crit.get('anchors', {})
            
            prompt_lines.append(f"#### Dimension: {c_label} (ID: {c_id})")
            prompt_lines.append(f"Instruction: {c_instr}")
            prompt_lines.append("Proficiency Levels (Anchors):")
            try:
                sorted_anchors = sorted(c_anchors.items(), key=lambda x: int(x[0]))
            except:
                sorted_anchors = c_anchors.items()
                
            for lvl, text in sorted_anchors:
                prompt_lines.append(f"  - Level {lvl}: {text}")
            prompt_lines.append("")
            
        return "\n".join(prompt_lines)

    def _update_state(self, state: WorkflowState, response_data: Any, output_key: Optional[str] = None, **kwargs) -> WorkflowState:
        step_id = kwargs.get('step_id', output_key or self.state_field or 'unknown_step')
        
        try:
            if isinstance(response_data, dict):
                # Force matrix_id from config if available (trust config over LLM hallucination)
                config = kwargs.get('execution_config', {})
                forced_id = config.get('matrix_id')
                if forced_id:
                    response_data['matrix_id'] = forced_id
                elif 'matrix_id' not in response_data or not response_data['matrix_id']:
                     response_data['matrix_id'] = config.get('matrix_id', 'unknown')

                # Inject Scale Metadata if available
                repo = kwargs.get('repository')
                if repo:
                    mat_id = response_data.get('matrix_id')
                    comp = repo.get_component_by_id(mat_id)
                    if comp:
                        content = comp.get('content', {})
                        if isinstance(content, str):
                            try:
                                content = json.loads(content)
                            except:
                                content = {}
                        scale = content.get('scale', {})
                        response_data['scale_min'] = scale.get('min', 1)
                        response_data['scale_max'] = scale.get('max', 5)

                res_obj = EvaluationResult(**response_data)
                
                # 1. Update Dynamic Store
                state.audit_results[step_id] = res_obj
                logger.info(f"[JudgeAgent] Saved EvaluationResult to state.audit_results['{step_id}'] (Scale: {res_obj.scale_min}-{res_obj.scale_max})")
                
                # 2. Update Legacy Fields (if output_key matches legacy slots)
                if output_key in ["step_judge", "step_judge_cognitive"]:
                    legacy_obj = self._adapt_to_legacy(res_obj)
                    setattr(state, output_key, legacy_obj)
                    logger.info(f"[JudgeAgent] Populated legacy field '{output_key}'")
                
            return state

        except Exception as e:
            logger.error(f"[JudgeAgent] Error updating state: {e}")
            raise e

    def _adapt_to_legacy(self, result: EvaluationResult) -> TuomioJaPisteet:
        """Best-effort mapping to legacy TuomioJaPisteet structure."""
        
        default_crit = PisteetKriteeri(arvosana=1, perustelu="Ei arvioitu (Mappaus puuttuu)")
        # Convert List[DimensionResultItem] to Dict for legacy lookup
        scores_map = {d.dimension_id: d for d in result.dimensions} if result.dimensions else {}
        
        def get_crit(keys):
            for k in keys:
                if k in scores_map:
                    s = scores_map[k]
                    return PisteetKriteeri(arvosana=s.score, perustelu=s.reasoning)
            return default_crit
            
        # Default handling for standard fields
        analyysi=get_crit(['analyysi', 'agency'])
        arviointi=get_crit(['arviointi', 'engineering'])
        synteesi=get_crit(['synteesi', 'falsification'])
        
        # Create base Pisteet object
        pisteet = Pisteet(
            analyysi=analyysi,
            arviointi=arviointi,
            synteesi=synteesi
        )

        # Inject ALL dynamic keys not already covered
        standard_keys = ['analyysi', 'agency', 'arviointi', 'engineering', 'synteesi', 'falsification']
        for dim_id, dim_res in scores_map.items():
            if dim_id not in standard_keys:
                # Add as dynamic field
                setattr(pisteet, dim_id, PisteetKriteeri(
                    arvosana=dim_res.score, 
                    perustelu=dim_res.reasoning
                ))
        
        hits = "; ".join(result.critical_findings) if result.critical_findings else "Ei kriittisiä havaintoja."
        
        return TuomioJaPisteet(
            metadata=result.metadata,
            metodologinen_loki=result.metodologinen_loki,
            edellisen_vaiheen_validointi=result.edellisen_vaiheen_validointi,
            semanttinen_tarkistussumma=result.semanttinen_tarkistussumma,
            konfliktin_ratkaisut=[],
            mestaruus_poikkeama=MestaruusPoikkeama(tunnistettu=False, perustelu=""),
            aitous_epaily=AitousEpaily(automaattinen_lippu=False, **{"viesti_hitl:lle": hits}),
            pisteet=pisteet,
            kriittiset_havainnot_yhteenveto=[hits],
            # Back-ported dynamic fields
            matrix_id=result.matrix_id,
            scale_min=result.scale_min,
            scale_max=result.scale_max
        )

    def post_process(self, state: WorkflowState) -> WorkflowState:
        # We rely on _update_state for population.
        # Legacy hook execution is skipped here to avoid double calculation issues, 
        # unless 'calculate_final_scores' is absolutely needed for other side effects.
        # Given we populate 'step_judge', downstream hooks should work.
        return state
