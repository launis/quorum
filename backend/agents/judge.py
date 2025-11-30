from typing import Any
from backend.agents.base import BaseAgent

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
            'metadata'
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

    def _process(self, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        # Call LLM with Retry Logic
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )

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
            tuomio_data = {k: kwargs.get(k) for k in possible_fields if k in kwargs}

        relevant_keys = [
            'metodologinen_loki',
            'data', # Original input
            'metadata'
        ]
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        # Add the reconstructed or found tuomio data
        if tuomio_data:
            input_data['tuomiojapisteet'] = tuomio_data
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        return f"""
        INPUT DATA (TUOMIO JA PISTEET):
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
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
