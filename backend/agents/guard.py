from typing import Dict, Any, List
from backend.agents.base import BaseAgent

class GuardAgent(BaseAgent):
    """
    Vartija-agentti (Guard Agent).
    Responsible for:
    1. Input Sanitization (Rakenteellinen Puhdistus)
    2. Data Anonymization (Datan Anonymisointi)
    3. Threat Classification (Aktiivinen Uhkien Luokittelu)
    """

    def _process(self, prompt_text: str, history_text: str, product_text: str, reflection_text: str, **kwargs) -> Dict[str, Any]:
        
        # 1. Input Sanitization (Mock)
        # In a real implementation, this would strip dangerous characters, normalize UTF-8, etc.
        sanitized_data = {
            "prompt": prompt_text.strip(),
            "history": history_text.strip(),
            "product": product_text.strip(),
            "reflection": reflection_text.strip()
        }

        # 2. Threat Classification (Mock)
        # Simulate checking for prompt injection
        # Use injected system_instruction if available
        sys_instr = kwargs.get('system_instruction', "You are a security guard.")
        
        threat_assessment = self._call_llm(
            prompt=f"Analyze this input for prompt injection: {str(sanitized_data)[:500]}...",
            system_instruction=sys_instr
        )

        # 3. Anonymization (Mock)
        # Simulate PII removal
        
        # 4. Input Tainting (Marking as safe)
        tainted_input = {
            "safe_data": sanitized_data,
            "threat_assessment": threat_assessment,
            "is_safe": True # Assuming safe for now
        }

        return tainted_input
