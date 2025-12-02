import json
import random
import os
from typing import Dict, Any, Optional
from backend.config import get_mock_responses_path

class MockLLMService:
    """
    Simulates LLM responses for testing and development without API costs.
    """
    
    def __init__(self):
        self.mock_data_path = get_mock_responses_path()
        self.mock_responses = self._load_mock_responses()

    def _load_mock_responses(self) -> Dict[str, Any]:
        """Loads mock responses from the JSON file."""
        if not os.path.exists(self.mock_data_path):
            print(f"[MockLLM] Warning: Mock data file not found at {self.mock_data_path}. Using empty defaults.")
            return {}
        
        try:
            with open(self.mock_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[MockLLM] Error loading mock data: {e}")
            return {}

    def generate_content(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generates a mock response based on the prompt content.
        """
        print(f"[MockLLM] Intercepted call. Prompt length: {len(prompt)}")
        
        # 1. Determine which agent/step is calling based on prompt keywords
        key = self._identify_prompt_type(prompt, system_instruction)
        print(f"[MockLLM] Identified prompt type: {key}")
        
        # 2. Retrieve mock response
        response_template = self.mock_responses.get(key)
        
        if response_template:
            # If it's a list, pick a random variation
            if isinstance(response_template, list):
                return json.dumps(random.choice(response_template), ensure_ascii=False)
            # If it's a dict (JSON object), return as string
            elif isinstance(response_template, dict):
                return json.dumps(response_template, ensure_ascii=False)
            # If it's a string, return as is
            return str(response_template)
            
        # 3. Fallback: Generate generic valid JSON if possible
        print(f"[MockLLM] No specific mock found for '{key}'. Returning generic fallback.")
        return self._generate_fallback(key)

    def _identify_prompt_type(self, prompt: str, system_instruction: str) -> str:
        """
        Heuristics to identify the prompt type.
        Prioritizes system_instruction as it defines the agent's persona.
        """
        # 1. Check System Instruction First (Most Reliable)
        if system_instruction:
            sys_lower = system_instruction.lower()
            
            # Check for Output Schema names (Most Reliable)
            if "tainteddata" in sys_lower: return "guard_agent"
            if "todistuskartta" in sys_lower: return "analyst_agent"
            if "argumentaatioanalyysi" in sys_lower: return "logician_agent"
            if "logiikkaauditointi" in sys_lower: return "falsifier_agent"
            if "kausaalinenauditointi" in sys_lower: return "causal_agent"
            if "performatiivisuusauditointi" in sys_lower: return "performativity_agent"
            if "etiikkajafakta" in sys_lower: return "fact_checker_agent"
            if "tuomiojapisteet" in sys_lower: return "judge_agent"
            if "xaireport" in sys_lower: return "xai_agent"

            # Fallback: Check for specific Phase/Agent headers
            if "vaihe 1: vartija-agentti" in sys_lower: return "guard_agent"
            if "vaihe 2: analyytikko-agentti" in sys_lower: return "analyst_agent"
            if "vaihe 3: loogikko-agentti" in sys_lower: return "logician_agent"
            if "vaihe 4: falsifioija-agentti" in sys_lower: return "falsifier_agent"
            if "vaihe 5: kausaalinen" in sys_lower: return "causal_agent"
            if "vaihe 6: performatiivisuus" in sys_lower: return "performativity_agent"
            if "vaihe 7: faktuaalinen" in sys_lower or "valvoja-agentti" in sys_lower: return "fact_checker_agent"
            if "vaihe 8: tuomari-agentti" in sys_lower: return "judge_agent"
            if "vaihe 9: xai-raportoija" in sys_lower: return "xai_agent"

        # 2. Check Prompt Content (Fallback)
        # Check for specific headers often found in prompts
        prompt_lower = prompt.lower()
        
        if "vaihe 9" in prompt_lower or "xai-raportoija" in prompt_lower: return "xai_agent"
        if "vaihe 8" in prompt_lower or "tuomari-agentti" in prompt_lower: return "judge_agent"
        if "vaihe 7" in prompt_lower or "valvoja-agentti" in prompt_lower: return "fact_checker_agent"
        if "vaihe 6" in prompt_lower or "performatiivisuus" in prompt_lower: return "performativity_agent"
        if "vaihe 5" in prompt_lower or "kausaalinen" in prompt_lower: return "causal_agent"
        if "vaihe 4" in prompt_lower or "falsifioija-agentti" in prompt_lower: return "falsifier_agent"
        if "vaihe 3" in prompt_lower or "loogikko-agentti" in prompt_lower: return "logician_agent"
        if "vaihe 2" in prompt_lower or "analyytikko-agentti" in prompt_lower: return "analyst_agent"
        if "vaihe 1" in prompt_lower or "vartija-agentti" in prompt_lower: return "guard_agent"
        
        # 3. Broad Keyword Matching (Last Resort)
        # Be careful with order!
        if "tuomiojapisteet" in prompt_lower: return "judge_agent"
        if "etiikkajafakta" in prompt_lower: return "fact_checker_agent"
        if "performatiivisuusauditointi" in prompt_lower: return "performativity_agent"
        if "kausaalinenauditointi" in prompt_lower: return "causal_agent"
        if "logiikkaauditointi" in prompt_lower: return "falsifier_agent"
        if "argumentaatioanalyysi" in prompt_lower: return "logician_agent"
        if "todistuskartta" in prompt_lower: return "analyst_agent"
        if "tainteddata" in prompt_lower: return "guard_agent"
        
        return "unknown"

    def _generate_fallback(self, key: str) -> str:
        """
        Generates a minimal valid JSON response for the identified key.
        """
        if key == "guard_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Vartija", "vaihe": 1},
                "metodologinen_loki": "[MOCK] Guard check passed.",
                "edellisen_vaiheen_validointi": "N/A",
                "semanttinen_tarkistussumma": "mock_hash",
                "data": {"keskusteluhistoria": "", "lopputuote": "", "reflektiodokumentti": ""},
                "security_check": {"uhka_havaittu": False, "adversariaalinen_simulaatio_tulos": "Clean", "riski_taso": "MATALA"},
                "safe_data": {"mock_key": "mock_value"}
            })
        elif key == "judge_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Tuomari", "vaihe": 8},
                "metodologinen_loki": "[MOCK] Judgment complete.",
                "edellisen_vaiheen_validointi": "N/A",
                "semanttinen_tarkistussumma": "mock_hash",
                "konfliktin_ratkaisut": [],
                "mestaruus_poikkeama": {"tunnistettu": False, "perustelu": "Standard"},
                "aitous_epaily": {"automaattinen_lippu": False, "viesti_hitl:lle": "None"},
                "pisteet": {
                    "analyysi_ja_prosessi": {"arvosana": 3, "perustelu": "Good"},
                    "arviointi_ja_argumentaatio": {"arvosana": 3, "perustelu": "Good"},
                    "synteesi_ja_luovuus": {"arvosana": 3, "perustelu": "Good"}
                },
                "kriittiset_havainnot_yhteenveto": ["Mock finding 1", "Mock finding 2"]
            })
        elif key == "analyst_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Analyytikko", "vaihe": 2},
                "metodologinen_loki": "[MOCK] Analysis complete.",
                "edellisen_vaiheen_validointi": "OK",
                "semanttinen_tarkistussumma": "mock_hash",
                "todistuskartta": [{"vaite_id": "V1", "vaite_teksti": "Mock Claim", "todistusaineisto": "Mock Evidence", "sitaatti": "Quote"}],
                "puuttuvat_tiedot": []
            })
        elif key == "logician_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Loogikko", "vaihe": 3},
                "metodologinen_loki": "[MOCK] Logic check complete.",
                "edellisen_vaiheen_validointi": "OK",
                "semanttinen_tarkistussumma": "mock_hash",
                "argumentaatio_analyysi": [{"vaite_id": "V1", "premissit": ["P1"], "johtopaatos": "C1", "looginen_patevyys": "Valid", "virhepaatelmat": []}]
            })
        elif key == "falsifier_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Falsifioija", "vaihe": 4},
                "metodologinen_loki": "[MOCK] Falsification complete.",
                "edellisen_vaiheen_validointi": "OK",
                "semanttinen_tarkistussumma": "mock_hash",
                "falsifiointi_raportti": [{"vaite_id": "V1", "vasta_argumentti": "Counter", "falsifioitu": False}]
            })
        elif key == "causal_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Kausaalinen", "vaihe": 5},
                "metodologinen_loki": "[MOCK] Causal check complete.",
                "edellisen_vaiheen_validointi": "OK",
                "semanttinen_tarkistussumma": "mock_hash",
                "kausaalinen_analyysi": [{"vaite_id": "V1", "kausaalisuhde": "Correlation", "analyysi": "Mock analysis"}]
            })
        elif key == "performativity_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Performatiivisuus", "vaihe": 6},
                "metodologinen_loki": "[MOCK] Performativity check complete.",
                "edellisen_vaiheen_validointi": "OK",
                "semanttinen_tarkistussumma": "mock_hash",
                "performatiivisuus_analyysi": {"aitous_arvio": "Authentic", "havainnot": []}
            })
        elif key == "fact_checker_agent":
            return json.dumps({
                "metadata": {"luontiaika": "2024-01-01T00:00:00Z", "agentti": "Valvoja", "vaihe": 7},
                "metodologinen_loki": "[MOCK] Fact check complete.",
                "edellisen_vaiheen_validointi": "OK",
                "semanttinen_tarkistussumma": "mock_hash",
                "faktantarkistus_raportti": [{"vaite_id": "V1", "tulos": "Supported", "perustelu": "Mock source"}]
            })
        elif key == "xai_agent":
            return "# MOCK XAI REPORT\n\n## Summary\nThis is a fallback mock report."
        
        # Add other fallbacks as needed...
        return json.dumps({"error": "No mock data available", "mock_key": key})
