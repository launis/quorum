from typing import Any
from backend.agents.base import BaseAgent

class GuardAgent(BaseAgent):
    """
    Vartija-agentti (Guard Agent).
    Responsible for:
    1. Input Sanitization (Rakenteellinen Puhdistus)
    2. Data Anonymization (Datan Anonymisointi)
    3. Threat Classification (Aktiivinen Uhkien Luokittelu)
    """

    def construct_user_prompt(self, **kwargs) -> str:
        return f"""
        INPUT DATA:
        ---
        Keskusteluhistoria: {kwargs.get('history_text', '')}
        ---
        Lopputuote: {kwargs.get('product_text', '')}
        ---
        Reflektiodokumentti: {kwargs.get('reflection_text', '')}
        ---
        """

    def _process(self, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Guard Agent's logic.
        """
        print(f"[GuardAgent] kwargs keys: {list(kwargs.keys())}")
        print(f"[GuardAgent] System Instruction present: {'system_instruction' in kwargs}")
        if 'system_instruction' in kwargs:
             print(f"[GuardAgent] System Instruction length: {len(kwargs['system_instruction'])}")
        
        user_content = self.construct_user_prompt(**kwargs)
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction
        )
        
        # Post-processing: Restore original content if LLM returned empty strings
        # This prevents overwriting the context with empty data while saving tokens in the LLM response.
        if response and 'data' in response:
            data_content = response['data']
            if isinstance(data_content, dict):
                if not data_content.get('keskusteluhistoria'):
                    data_content['keskusteluhistoria'] = kwargs.get('history_text')
                if not data_content.get('lopputuote'):
                    data_content['lopputuote'] = kwargs.get('product_text')
                if not data_content.get('reflektiodokumentti'):
                    data_content['reflektiodokumentti'] = kwargs.get('reflection_text')
                    
        return response
