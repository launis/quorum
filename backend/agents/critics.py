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
        
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if 'walton_stressitesti_loydokset' not in response:
                print("[LogicalFalsifierAgent] Warning: 'walton_stressitesti_loydokset' missing. Injecting empty list.")
                response['walton_stressitesti_loydokset'] = []
                
            if 'paattelyketjun_uskollisuus_auditointi' not in response:
                print("[LogicalFalsifierAgent] Warning: 'paattelyketjun_uskollisuus_auditointi' missing. Injecting default.")
                response['paattelyketjun_uskollisuus_auditointi'] = {
                    "onko_post_hoc_rationalisointia": False,
                    "perustelu": "Automaattinen täydennys (LLM ei palauttanut arviota).",
                    "uskollisuus_score": "EPÄVARMA"
                }

        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[LogicalFalsifierAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[LogicalFalsifierAgent] Validation successful.")
            except Exception as e:
                print(f"[LogicalFalsifierAgent] Validation failed after injection: {e}")
                pass

        return response


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
        
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if 'faktantarkistus_rfi' not in response:
                print("[FactualOverseerAgent] Warning: 'faktantarkistus_rfi' missing. Injecting empty list.")
                response['faktantarkistus_rfi'] = []
            if 'eettiset_havainnot' not in response:
                print("[FactualOverseerAgent] Warning: 'eettiset_havainnot' missing. Injecting empty list.")
                response['eettiset_havainnot'] = []
                
        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[FactualOverseerAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[FactualOverseerAgent] Validation successful.")
            except Exception as e:
                print(f"[FactualOverseerAgent] Validation failed after injection: {e}")
                pass

        return response


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
        
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if 'kausaalinen_auditointi' not in response:
                print("[CausalAnalystAgent] Warning: 'kausaalinen_auditointi' missing. Injecting default.")
                response['kausaalinen_auditointi'] = {
                    "aikajana_validi": False,
                    "havainnot": "Automaattinen täydennys (LLM ei palauttanut arviota)."
                }
                
            if 'kontrafaktuaalinen_testi' not in response:
                print("[CausalAnalystAgent] Warning: 'kontrafaktuaalinen_testi' missing. Injecting default.")
                response['kontrafaktuaalinen_testi'] = {
                    "skenaario_A_toteutunut": "N/A",
                    "skenaario_B_simulaatio": "N/A",
                    "uskottavuus_arvio": "N/A"
                }
                
            if 'abduktiivinen_paatelma' not in response:
                print("[CausalAnalystAgent] Warning: 'abduktiivinen_paatelma' missing. Injecting default.")
                response['abduktiivinen_paatelma'] = "Epävarma"

        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[CausalAnalystAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[CausalAnalystAgent] Validation successful.")
            except Exception as e:
                print(f"[CausalAnalystAgent] Validation failed after injection: {e}")
                pass

        return response


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
        
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if 'performatiivisuus_heuristiikat' not in response:
                print("[PerformativityDetectorAgent] Warning: 'performatiivisuus_heuristiikat' missing. Injecting empty list.")
                response['performatiivisuus_heuristiikat'] = []
                
            if 'pre_mortem_analyysi' not in response:
                print("[PerformativityDetectorAgent] Warning: 'pre_mortem_analyysi' missing. Injecting default.")
                response['pre_mortem_analyysi'] = {
                    "suoritettu": False,
                    "hiljaiset_signaalit": []
                }
                
            if 'yleisarvio_aitoudesta' not in response:
                print("[PerformativityDetectorAgent] Warning: 'yleisarvio_aitoudesta' missing. Injecting default.")
                response['yleisarvio_aitoudesta'] = "Epäilyttävä"

        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[PerformativityDetectorAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[PerformativityDetectorAgent] Validation successful.")
            except Exception as e:
                print(f"[PerformativityDetectorAgent] Validation failed after injection: {e}")
                pass

        return response
