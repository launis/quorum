from typing import Any
from backend.agents.base import BaseAgent

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).
    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        # --- DATA RE-HYDRATION STRATEGY ---
        # GuardAgent (Step 1) now outputs placeholders ({{FILE: ...}}) in the 'data' field to save tokens.
        # However, AnalystAgent (Step 2) NEEDS the actual content to perform RAG and analysis.
        # Therefore, we must explicitly inject the raw text inputs ('history_text', etc.) 
        # alongside or instead of the placeholder 'data' object.
        
        # 1. Include Metadata & Logs from previous steps (Context)
        context_keys = ['safe_data', 'security_check', 'metodologinen_loki', 'metadata', 'data']
        context_data = {k: kwargs.get(k) for k in context_keys if k in kwargs}

        if not context_data:
             context_data = {"error": "No relevant input data found for AnalystAgent"}

        # 2. Raw Evidence (Unstructured Text)
        history_text = kwargs.get('history_text', 'N/A')
        product_text = kwargs.get('product_text', 'N/A')
        reflection_text = kwargs.get('reflection_text', 'N/A')

        return f"""
        CONTEXT DATA (JSON):
        ---
        {json.dumps(context_data, indent=2, ensure_ascii=False)}
        ---

        RAW EVIDENCE FOR ANALYSIS:
        
        === KESKUSTELUHISTORIA ===
        {history_text}
        
        === LOPPUTUOTE ===
        {product_text}
        
        === REFLEKTIODOKUMENTTI ===
        {reflection_text}
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Analyst Agent's logic.
        """
        user_content = self.construct_user_prompt(**kwargs)
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction,
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            # Handle list response (common with some models/prompts)
            if isinstance(response, list):
                print("[AnalystAgent] Response is a list. Wrapping in 'hypoteesit'.")
                
                # Normalize keys in the list items
                normalized_list = []
                for item in response:
                    if isinstance(item, dict):
                        new_item = item.copy()
                        # Map common variations to 'vaite_teksti'
                        for key in ['claim', 'text', 'statement', 'väite', 'vaite', 'description', 'content', 'detail', 'kuvaus', 'sisalto']:
                            if key in new_item and 'vaite_teksti' not in new_item:
                                new_item['vaite_teksti'] = new_item.pop(key)
                        
                        # Map common variations to 'loytyyko_todisteita'
                        for key in ['evidence_found', 'has_evidence', 'todisteet_löytyy', 'loytyyko']:
                            if key in new_item and 'loytyyko_todisteita' not in new_item:
                                new_item['loytyyko_todisteita'] = new_item.pop(key)
                                
                        # Ensure 'loytyyko_todisteita' has a boolean value
                        if 'loytyyko_todisteita' not in new_item:
                             new_item['loytyyko_todisteita'] = False
                             
                        # Ensure 'id' exists
                        if 'id' not in new_item:
                            import uuid
                            new_item['id'] = f"gen_{uuid.uuid4().hex[:8]}"
                            
                        normalized_list.append(new_item)
                    else:
                        normalized_list.append(item)

                response = {
                    "hypoteesit": normalized_list,
                    "metodologinen_loki": "Generaatio palautti listan. Loki generoitu automaattisesti.",
                    "metadata": {
                        "agentti": "AnalystAgent",
                        "luontiaika": "2024-01-01T00:00:00Z",
                        "vaihe": 2,
                        "versio": "2.0"
                    },
                    "edellisen_vaiheen_validointi": "N/A",
                    "semanttinen_tarkistussumma": "autogen"
                }

            if 'hypoteesit' not in response:
                print("[AnalystAgent] Warning: 'hypoteesit' missing. Injecting empty list.")
                response['hypoteesit'] = []
            if 'rag_todisteet' not in response:
                print("[AnalystAgent] Warning: 'rag_todisteet' missing. Injecting empty list.")
                response['rag_todisteet'] = []
                
        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[AnalystAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[AnalystAgent] Validation successful.")
            except Exception as e:
                print(f"[AnalystAgent] Validation failed after injection: {e}")
                raise e

        return response
