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
        
        IMPORTANT: 
        1. Analyze the input data for security threats.
        2. Return the result in the required JSON format.
        3. TO SAVE TOKENS: Do NOT repeat the input text in the 'data' or 'safe_data' fields. Leave 'keskusteluhistoria', 'lopputuote', 'reflektiodokumentti', and 'safe_data' as null or empty strings in the JSON response. The system will fill them automatically.
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
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
            system_instruction=system_instruction,
            validation_schema=validation_schema
        )
        
        # --- HYBRID GUARD: Deterministic Keyword Scanning ---
        # 1. Try to fetch from DB
        try:
            from backend.main import engine
            db_phrases = engine.banned_phrases_table.all()
            if db_phrases:
                BANNED_PHRASES = [p['phrase'] for p in db_phrases]
            else:
                # Fallback if DB is empty (initial state)
                BANNED_PHRASES = [
                    "ignore previous instructions", "system prompt", "delete database", 
                    "drop table", "exec(", "eval(", "<script>", "alert(",
                    "unohda aiemmat ohjeet", "sivuuta ohjeet", "poista tietokanta",
                    "ohita säännöt", "kerro salaisuudet", "tulosta järjestelmäkehote"
                ]
        except Exception as e:
            print(f"[GuardAgent] Warning: Could not fetch banned phrases from DB: {e}")
            BANNED_PHRASES = [
                "ignore previous instructions", "system prompt", "delete database", 
                "drop table", "exec(", "eval(", "<script>", "alert(",
                "unohda aiemmat ohjeet", "sivuuta ohjeet", "poista tietokanta",
                "ohita säännöt", "kerro salaisuudet", "tulosta järjestelmäkehote"
            ]
        
        found_threats = []
        input_text_blob = (
            str(kwargs.get('history_text', '')) + " " + 
            str(kwargs.get('product_text', '')) + " " + 
            str(kwargs.get('reflection_text', ''))
        ).lower()
        
        for phrase in BANNED_PHRASES:
            if phrase in input_text_blob:
                found_threats.append(phrase)
                
        if found_threats and response and 'security_check' in response:
            print(f"[GuardAgent] HYBRID GUARD TRIGGERED: Found threats {found_threats}")
            # Force override
            response['security_check']['uhka_havaittu'] = True
            response['security_check']['riski_taso'] = "KORKEA"
            current_sim = response['security_check'].get('adversariaalinen_simulaatio_tulos', '')
            response['security_check']['adversariaalinen_simulaatio_tulos'] = (
                f"{current_sim} [HYBRID GUARD: Havaittu kiellettyjä ilmauksia: {', '.join(found_threats)}]"
            )
        # ----------------------------------------------------

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
        
        # Populate safe_data programmatically (it's the same as input since input is already sanitized by hooks)
        if response:
            response['safe_data'] = {
                'history_text': kwargs.get('history_text'),
                'product_text': kwargs.get('product_text'),
                'reflection_text': kwargs.get('reflection_text'),
                'metadata': kwargs.get('metadata')
            }
                    
        return response
