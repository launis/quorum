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

    def _process(self, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Guard Agent's logic.
        """
        print(f"[GuardAgent] kwargs keys: {list(kwargs.keys())}")
        print(f"[GuardAgent] System Instruction present: {'system_instruction' in kwargs}")
        if 'system_instruction' in kwargs:
             print(f"[GuardAgent] System Instruction length: {len(kwargs['system_instruction'])}")
        
        # Inputs are already sanitized by pre-hooks (sanitize_and_anonymize_input)
        
        # Inputs are already sanitized by pre-hooks (sanitize_and_anonymize_input)
        # We expect keys like 'prompt', 'history', 'product', 'reflection' in kwargs.
        
        # Construct the user content part of the prompt
        # The system instruction (Rules, Mandates, Agent Definition) is passed in kwargs['system_instruction']
        
        user_content = f"""
        INPUT DATA:
        ---
        Keskusteluhistoria: {kwargs.get('history_text', '')}
        ---
        Lopputuote: {kwargs.get('product_text', '')}
        ---
        Reflektiodokumentti: {kwargs.get('reflection_text', '')}
        ---
        """
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        return self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction
        )
