from typing import Any
from backend.agents.base import BaseAgent
from backend.schemas import TuomioJaPisteet

class JudgeAgent(BaseAgent):
    """
    Tuomari-agentti (Judge Agent).
    """
    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        # 1. Context from previous steps
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
        context_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not context_data:
             context_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        # 2. Raw Evidence (Unstructured Text)
        history_text = kwargs.get('history_text', 'N/A')
        product_text = kwargs.get('product_text', 'N/A')
        reflection_text = kwargs.get('reflection_text', 'N/A')

        return f"""
        INPUT DATA (AUDITOINTIRAPORTIT):
        ---
        {json.dumps(context_data, indent=2, ensure_ascii=False)}
        ---
        
        RAW EVIDENCE FOR VERIFICATION:
        
        === KESKUSTELUHISTORIA ===
        {history_text}
        
        === LOPPUTUOTE ===
        {product_text}
        
        === REFLEKTIODOKUMENTTI ===
        {reflection_text}
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        # Call LLM with Retry Logic and Schema Validation
        # Call LLM with Retry Logic
        # We pass validation_schema=None initially to allow partial JSON, 
        # then we inject defaults, and FINALLY validate against the schema.
        schema_to_use = validation_schema if validation_schema else TuomioJaPisteet
        
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None # Allow partial JSON for injection logic
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if isinstance(response, list):
                print("[JudgeAgent] Response is a list. Wrapping in 'konfliktin_ratkaisut'.")
                response = {"konfliktin_ratkaisut": response}

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
        if schema_to_use and response:
            try:
                print(f"[JudgeAgent] Validating against schema: {schema_to_use.__name__}")
                schema_to_use.model_validate(response)
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
        
        IMPORTANT: You MUST output a valid JSON object containing the XAI report.
        Strictly follow the 'XAIRaportti' schema. Do not include any Markdown formatting outside the JSON.
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        from backend.schemas import XAIRaportti
        import json
        
        user_content = self.construct_user_prompt(**kwargs)
        
        # 1. Get raw JSON without strict schema validation first to allow structural fixes
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=kwargs.get('system_instruction'),
            validation_schema=None 
        )
        
        if response:
            # --- NEW CLEANING LOGIC ---
            if isinstance(response, str):
                try:
                    # Try to extract JSON from the string, ignoring trailing text
                    response_str = response.strip()
                    start_idx = response_str.find('{')
                    if start_idx != -1:
                        response_str = response_str[start_idx:]
                        # raw_decode returns (obj, end_index)
                        response, _ = json.JSONDecoder().raw_decode(response_str)
                        print("[XAIReporterAgent] Successfully extracted JSON from mixed output.")
                except Exception as e:
                    print(f"[XAIReporterAgent] Failed to parse raw response string: {e}")
            # --------------------------

            # 2. Check and Fix Structure (Missing Root Key)
            if "kognitiivinen_arviointiraportti" not in response:
                # Check if it looks like the inner content
                if "analyyttinen_arviointimatriisi_JEM_A" in response:
                    print("[XAIReporterAgent] Missing root key 'kognitiivinen_arviointiraportti'. Wrapping response.")
                    response = {"kognitiivinen_arviointiraportti": response}
            
            # 3. Validate manually
            try:
                XAIRaportti.model_validate(response)
                print("[XAIReporterAgent] Schema validation successful.")
            except Exception as e:
                print(f"[XAIReporterAgent] Validation failed after fixing: {e}")
                # Proceeding with best effort
        
        return {
            "xai_report_content": json.dumps(response, ensure_ascii=False) if response else "{}"
        }
