from typing import Any
from backend.agents.base import BaseAgent

class JudgeAgent(BaseAgent):
    """
    Tuomari-agentti (Judge Agent).
    """
    def _process(self, **kwargs) -> dict[str, Any]:
        import json
        
        # Needs: 7_etiikkajafakta.json (FactChecker output) which contains accumulated context
        # Actually, Judge needs everything:
        # 3_argumentaatioanalyysi.json
        # 4_logiikkaauditointi.json
        # 5_kausaalinenauditointi.json
        # 6_performatiivisuusauditointi.json
        # 7_etiikkajafakta.json
        
        relevant_keys = [
            'argumentaatioanalyysi', 
            'logiikkaauditointi', 
            'kausaalinenauditointi', 
            'performatiivisuusauditointi', 
            'etiikkajafakta',
            'metodologinen_loki'
        ]
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA (AUDITOINTIRAPORTIT):
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """
        
        # Call LLM with Retry Logic
        return self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction')
        )

class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).
    """
    def _process(self, **kwargs) -> dict[str, Any]:
        import json
        
        # Needs: 8_tuomiojapisteet.json (Judge output)
        # And potentially everything else for the full report context
        
        relevant_keys = [
            'tuomiojapisteet',
            'metodologinen_loki',
            'data' # Original input
        ]
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA (TUOMIO JA PISTEET):
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """
        
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
