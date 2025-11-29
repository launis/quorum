from typing import Any
from backend.agents.base import BaseAgent

class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).
    """
    def _process(self, **kwargs) -> dict[str, Any]:
        import json
        
        # Needs: 2_todistuskartta.json, 3_argumentaatioanalyysi.json, 1_tainted_data.json
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
from typing import Dict, Any, List
from backend.agents.base import BaseAgent

class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).
    """
    def _process(self, **kwargs) -> Dict[str, Any]:
        import json
        
        # Needs: 2_todistuskartta.json, 3_argumentaatioanalyysi.json, 1_tainted_data.json
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )


class FactualOverseerAgent(BaseAgent):
    """
    Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).
    """
    def _process(self, **kwargs) -> dict[str, Any]:
        import json
        
        # Needs: 2_todistuskartta.json, 3_argumentaatioanalyysi.json, 1_tainted_data.json
        # AND google_search_results from pre-hook
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'google_search_results', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        ULKOISEN FAKTANTARKISTUKSEN TULOKSET:
        {kwargs.get('google_search_results', 'Ei hakutuloksia.')}
        ---
        """
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).
    """
    def _process(self, **kwargs) -> dict[str, Any]:
        import json
        
        # Needs: 2_todistuskartta.json, 3_argumentaatioanalyysi.json, 1_tainted_data.json
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )


class PerformativityDetectorAgent(BaseAgent):
    """
    Performatiivisuuden Tunnistaja-agentti (Performativity Detector).
    """
    def _process(self, **kwargs) -> dict[str, Any]:
        import json
        
        # Needs: 2_todistuskartta.json, 3_argumentaatioanalyysi.json, 1_tainted_data.json
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )
