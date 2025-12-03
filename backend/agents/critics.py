from typing import Any
from backend.agents.base import BaseAgent

class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        return f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=validation_schema
        )


class FactualOverseerAgent(BaseAgent):
    """
    Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        # Optimize input data to avoid timeouts
        # FactualOverseer needs: todistuskartta, argumentaatioanalyysi, google_search_results
        # It does NOT need the full raw data (history, product, reflection) if it has the analysis.
        
        optimized_input = {}
        if 'todistuskartta' in kwargs:
            optimized_input['todistuskartta'] = kwargs['todistuskartta']
        if 'argumentaatioanalyysi' in kwargs:
            optimized_input['argumentaatioanalyysi'] = kwargs['argumentaatioanalyysi']
        if 'metodologinen_loki' in kwargs:
            optimized_input['metodologinen_loki'] = kwargs['metodologinen_loki']
            
        # If we have absolutely no structured data, fallback to raw but truncated
        if not optimized_input:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}
             # Truncate large strings if falling back
             for k, v in input_data.items():
                 if isinstance(v, str) and len(v) > 5000:
                     input_data[k] = v[:5000] + "... [TRUNCATED]"
             optimized_input = input_data

        return f"""
        INPUT DATA:
        ---
        {json.dumps(optimized_input, indent=2, ensure_ascii=False)}
        ---
        ULKOISEN FAKTANTARKISTUKSEN TULOKSET:
        {kwargs.get('google_search_results', 'Ei hakutuloksia.')}
        ---
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=validation_schema
        )


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        return f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=validation_schema
        )


class PerformativityDetectorAgent(BaseAgent):
    """
    Performatiivisuuden Tunnistaja-agentti (Performativity Detector).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        relevant_keys = ['todistuskartta', 'argumentaatioanalyysi', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        return f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=validation_schema
        )
