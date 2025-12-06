from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.state import WorkflowState
from backend.schemas import TuomioJaPisteet
from pydantic import BaseModel

class JudgeAgent(BaseAgent):
    """
    Tuomari-agentti (Judge Agent).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Judge needs EVERYTHING
        context = {
            "logiikka": state.step_4_falsifier.model_dump_json(indent=2) if state.step_4_falsifier else "N/A",
            "faktat": state.step_5_overseer.model_dump_json(indent=2) if state.step_5_overseer else "N/A",
            "kausaalisuus": state.step_6_causal.model_dump_json(indent=2) if state.step_6_causal else "N/A",
            "performatiivisuus": state.step_7_detector.model_dump_json(indent=2) if state.step_7_detector else "N/A",
            "argumentaatio": state.step_3_logician.model_dump_json(indent=2) if state.step_3_logician else "N/A"
        }
        
        import json
        
        # Get Example
        example_text = self.get_schema_example(TuomioJaPisteet)

        return f"""
        TASK: Synthesize audit reports and assign a final score.

        {example_text}

        INPUT DATA (AUDITOINTIRAPORTIT):
        ---
        {json.dumps(context, indent=2, ensure_ascii=False)}
        ---
        RAW EVIDENCE:
        {state.inputs.product_text[:5000]}...
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return TuomioJaPisteet

    def get_system_instruction(self) -> str:
        return """
        You are the Judge Agent. Your task is to synthesize all audit reports and assign a final score.
        
        1. Resolve conflicts between different agents (e.g., if Logician says X but Falsifier says Y).
        2. Check for 'Mastery Deviation' (is the work suspiciously good?).
        3. Assign scores (1-4) for: Analysis, Argumentation, Synthesis.
        
        Output must be a valid JSON object matching the TuomioJaPisteet schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_8_judge = TuomioJaPisteet(**response_data)
        except Exception as e:
            print(f"[JudgeAgent] State update failed: {e}")
            raise e
        return state

    def calculate_final_scores(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: calculate_final_scores
        Calculates averages and summary of the scores.
        """
        print("[JudgeAgent] Running calculate_final_scores...")
        
        if not state.step_8_judge or not state.step_8_judge.pisteet:
            print("   [JudgeAgent] No scores to calculate.")
            return state
            
        try:
            p = state.step_8_judge.pisteet
            
            # Helper to safely get score
            def get_val(s): return s.arvosana if s else 0
            
            val1 = get_val(p.analyysi_ja_prosessi)
            val2 = get_val(p.arviointi_ja_argumentaatio)
            val3 = get_val(p.synteesi_ja_luovuus)
            
            total = val1 + val2 + val3
            count = 3 # Fixed count for now
            average = total / count
            
            summary = f"Total Score: {total}/{count*4} (Avg: {average:.2f})"
            print(f"   {summary}")
            
            # We can store this in aux_data for reference, or update the model if schema allows.
            # The schema TuomioJaPisteet might not have 'calculated_avg'.
            # We'll store in aux_data to be safe.
            state.aux_data['score_summary'] = summary
            state.aux_data['calculated_average'] = average
            
        except Exception as e:
            print(f"[JudgeAgent] Calculation failed: {e}")
            
        return state
