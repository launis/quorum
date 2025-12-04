from typing import Any
from backend.agents.base import BaseAgent
from backend.schemas import TuomioJaPisteet

class JudgeAgent(BaseAgent):
    """
    Tuomari-agentti (Judge Agent).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        relevant_keys = [
            'argumentaatioanalyysi', 
            'logiikkaauditointi', 
            'kausaalinenauditointi', 
            'performatiivisuusauditointi', 
            'etiikkajafakta',
            'metodologinen_loki',
            'metadata',
            'data'
        ]
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        return f"""
        INPUT DATA (AUDITOINTIRAPORTIT):
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        # Call LLM with Retry Logic and Schema Validation
        # Call LLM with Retry Logic and Schema Validation
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if 'konfliktin_ratkaisut' not in response:
                print("[JudgeAgent] Warning: 'konfliktin_ratkaisut' missing. Injecting empty list.")
                response['konfliktin_ratkaisut'] = []
            
            if 'mestaruus_poikkeama' not in response:
                print("[JudgeAgent] Warning: 'mestaruus_poikkeama' missing. Injecting default.")
                response['mestaruus_poikkeama'] = {
                    "tunnistettu": False,
                    "perustelu": "Ei tunnistettu poikkeamaa."
                }
                
            if 'aitous_epaily' not in response:
                print("[JudgeAgent] Warning: 'aitous_epaily' missing. Injecting default.")
                response['aitous_epaily'] = {
                    "automaattinen_lippu": False,
                    "viesti_hitl:lle": "Ei epäilyä."
                }
                
            if 'pisteet' not in response:
                print("[JudgeAgent] Warning: 'pisteet' missing. Injecting defaults.")
                response['pisteet'] = {
                    "analyysi_ja_prosessi": {"arvosana": 1, "perustelu": "N/A"},
                    "arviointi_ja_argumentaatio": {"arvosana": 1, "perustelu": "N/A"},
                    "synteesi_ja_luovuus": {"arvosana": 1, "perustelu": "N/A"}
                }
            
            if 'kriittiset_havainnot_yhteenveto' not in response:
                print("[JudgeAgent] Warning: 'kriittiset_havainnot_yhteenveto' missing. Injecting empty list.")
                response['kriittiset_havainnot_yhteenveto'] = []

        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[JudgeAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[JudgeAgent] Validation successful.")
            except Exception as e:
                print(f"[JudgeAgent] Validation failed after injection: {e}")
                pass

        # Python-side Calculation (Monolithic Validation Extension)
        if response and 'pisteet' in response:
            try:
                pisteet = response['pisteet']
                # Extract raw scores (assuming schema validation ensured structure)
                s1 = pisteet.get('analyysi_ja_prosessi', {}).get('arvosana', 0)
                s2 = pisteet.get('arviointi_ja_argumentaatio', {}).get('arvosana', 0)
                s3 = pisteet.get('synteesi_ja_luovuus', {}).get('arvosana', 0)
                
                total = s1 + s2 + s3
                avg = round(total / 3, 2)
                
                # Inject calculated values
                response['lasketut_yhteispisteet'] = total
                response['lasketut_keskiarvo'] = avg
                
                print(f"[JudgeAgent] Calculated Scores: Total={total}, Avg={avg}")
            except Exception as e:
                print(f"[JudgeAgent] Error calculating scores: {e}")
        
        return response

class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        # 1. Try to get 'tuomiojapisteet' directly
        tuomio_data = kwargs.get('tuomiojapisteet')
        
        # 2. If not found, try to reconstruct from flat context (JudgeAgent output)
        if not tuomio_data:
            possible_fields = [
                'pisteet', 
                'kriittiset_havainnot_yhteenveto', 
                'lasketut_yhteispisteet', 
                'lasketut_keskiarvo',
                'score_summary',
                'mestaruus_poikkeama',
                'aitous_epaily',
                'performatiivisuus_heuristiikat',
                'abduktiivinen_paatelma',
                'kausaalinen_auditointi',
                'paattelyketjun_uskollisuus_auditointi',
                'walton_stressitesti_loydokset',
                'walton_skeema',
                'kognitiivinen_taso',
                'toulmin_analyysi',
                'vaite_teksti',
                'id',
                'security_check',
                'reflektiodokumentti',
                'lopputuote'
            ]
            
            # Helper for case-insensitive lookup
            def get_ci(d, key):
                if key in d: return d[key]
                for k in d:
                    if k.lower() == key.lower():
                        return d[k]
                return None

            tuomio_data = {k: get_ci(kwargs, k) for k in possible_fields if get_ci(kwargs, k) is not None}

        relevant_keys = [
            'metodologinen_loki',
            'data', # Original input
            'metadata'
        ]
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        # Add the reconstructed or found tuomio data
        if tuomio_data:
            input_data['tuomiojapisteet'] = tuomio_data
            
        # Add Bibliography if present
        bib_section = ""
        if 'bibliography_context' in kwargs:
            bib_list = kwargs['bibliography_context']
            if bib_list and isinstance(bib_list, list):
                bib_text = "\n".join([f"- {item}" for item in sorted(bib_list)])
                bib_section = f"""
        LÄHDELUETTELO (KÄYTETYT LÄHTEET):
        ---
        {bib_text}
        ---
        """
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        return f"""
        INPUT DATA (TUOMIO JA PISTEET):
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        {bib_section}
        """

    def _process(self, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        llm_response = self._call_llm(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )
        
        # XAI Agent produces a TEXT REPORT, not necessarily JSON.
        # But the prompt says "SINUN TÄYTYY TUOTTAA TEKSTIRAPORTTI".
        # However, the engine might expect a dict to update context.
        # Let's return a dict with the report content.
        
        return {
            "xai_report_content": llm_response
        }
