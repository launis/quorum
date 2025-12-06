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
        with open("mock_debug.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- NEW CALL ---\n")
            f.write(f"System Instruction: {system_instruction}\n")
            f.write(f"Prompt Preview: {prompt[:100]}\n")
        
        key = self._identify_prompt_type(prompt, system_instruction)
        
        with open("mock_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Identified Key: {key}\n")
            
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

        # 2. Check Prompt Content (V2 & V1)
        prompt_lower = prompt.lower()
        
        # V2 Specific Headers (Strong Signal)
        if "input data to validate" in prompt_lower: return "guard_agent"
        if "input data for analysis" in prompt_lower: return "analyst_agent"
        if "todistuskartta (edellisestä vaiheesta)" in prompt_lower: return "logician_agent"
        if "argumentaatioanalyysi (edellisestä vaiheesta)" in prompt_lower: return "falsifier_agent"
        if "ulkoisen faktantarkistuksen tulokset" in prompt_lower: return "fact_checker_agent"
        if "kausaalinen analyytikko" in prompt_lower: return "causal_agent" # System instruction check fallback
        if "performatiivisuuden tunnistaja" in prompt_lower: return "performativity_agent" # System instruction check fallback
        if "input data (auditointiraportit)" in prompt_lower: return "judge_agent"
        if "input data (tuomio ja pisteet)" in prompt_lower: return "xai_agent"

        # V1 / Generic Headers
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
        Generates a minimal valid JSON response for the identified key, strictly matching backend/schemas.py.
        """
        import json
        
        common_metadata = {
            "luontiaika": "2024-01-01T00:00:00Z",
            "agentti": "MockAgent",
            "vaihe": 0,
            "versio": "2.0",
            "suoritus_ymparisto": "Internal"
        }
        
        common_base = {
            "metadata": common_metadata,
            "metodologinen_loki": "[MOCK] Fallback generation.",
            "edellisen_vaiheen_validointi": "N/A",
            "semanttinen_tarkistussumma": "mock_hash"
        }

        if key == "guard_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Vartija"
            data["metadata"]["vaihe"] = 1
            data.update({
                "data": {
                    "keskusteluhistoria": "{{FILE: Keskusteluhistoria.pdf}}",
                    "lopputuote": "{{FILE: Lopputuote.pdf}}",
                    "reflektiodokumentti": "{{FILE: Reflektiodokumentti.pdf}}"
                },
                "security_check": {
                    "uhka_havaittu": False,
                    "adversariaalinen_simulaatio_tulos": "Clean",
                    "riski_taso": "MATALA"
                },
                "safe_data": {"mock_key": "mock_value"}
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "analyst_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Analyytikko"
            data["metadata"]["vaihe"] = 2
            data.update({
                "hypoteesit": [
                    {"id": "H1", "vaite_teksti": "Opiskelija osoittaa kriittistä ajattelua.", "loytyyko_todisteita": True}
                ],
                "rag_todisteet": [
                    {
                        "viittaa_hypoteesiin_id": "H1",
                        "perusteet": "Löytyy reflektiosta.",
                        "konteksti_segmentti": "Oivalsin, että...",
                        "relevanssi_score": 9
                    }
                ]
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "logician_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Loogikko"
            data["metadata"]["vaihe"] = 3
            data.update({
                "toulmin_analyysi": [
                    {"vaite_id": "H1", "claim": "Claim text", "data": "Data text", "warrant": "Warrant text", "backing": "Backing text"}
                ],
                "kognitiivinen_taso": {
                    "bloom_taso": "Analyze",
                    "strateginen_syvyys": "Syvä"
                },
                "walton_skeema": {
                    "tunnistettu_skeema": "Expert Opinion",
                    "kriittiset_kysymykset": ["Q1?"]
                }
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "falsifier_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Falsifioija"
            data["metadata"]["vaihe"] = 4
            data.update({
                "walton_stressitesti_loydokset": [
                    {"kysymys": "Miksi?", "kestiko_todistusaineisto": True, "havainto": "Kesti."}
                ],
                "paattelyketjun_uskollisuus_auditointi": {
                    "onko_post_hoc_rationalisointia": False,
                    "perustelu": "Ei havaittu.",
                    "uskollisuus_score": "KORKEA"
                }
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "fact_checker_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Valvoja"
            data["metadata"]["vaihe"] = 5
            data.update({
                "faktantarkistus_rfi": [
                    {"vaite": "Maa on pyöreä", "verifiointi_tulos": "Vahvistettu", "lahde_tai_paattely": "Yleistieto"}
                ],
                "eettiset_havainnot": [
                    {"tyyppi": "Ei havaittu", "vakavuus": "N/A", "kuvaus": "OK"}
                ]
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "causal_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Kausaalinen"
            data["metadata"]["vaihe"] = 6
            data.update({
                "kausaalinen_auditointi": {
                    "aikajana_validi": True,
                    "havainnot": "Johdonmukainen."
                },
                "kontrafaktuaalinen_testi": {
                    "skenaario_A_toteutunut": "X tapahtui",
                    "skenaario_B_simulaatio": "Jos X ei, niin Y",
                    "uskottavuus_arvio": "Uskottava"
                },
                "abduktiivinen_paatelma": "Aito Oivallus"
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "performativity_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Performatiivisuus"
            data["metadata"]["vaihe"] = 7
            data.update({
                "performatiivisuus_heuristiikat": [
                    {"heuristiikka": "Buzzwords", "lippu_nostettu": False, "kuvaus": "Normaali kieli."}
                ],
                "pre_mortem_analyysi": {
                    "suoritettu": True,
                    "hiljaiset_signaalit": ["Ei signaaleja."]
                },
                "yleisarvio_aitoudesta": "Orgaaninen"
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "judge_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "Tuomari"
            data["metadata"]["vaihe"] = 8
            data.update({
                "konfliktin_ratkaisut": [],
                "mestaruus_poikkeama": {"tunnistettu": False, "perustelu": "Normaali suoritus."},
                "aitous_epaily": {"automaattinen_lippu": False, "viesti_hitl:lle": "Ei huomautettavaa."},
                "pisteet": {
                    "analyysi_ja_prosessi": {"arvosana": 3, "perustelu": "Hyvä."},
                    "arviointi_ja_argumentaatio": {"arvosana": 3, "perustelu": "Hyvä."},
                    "synteesi_ja_luovuus": {"arvosana": 3, "perustelu": "Hyvä."}
                },
                "kriittiset_havainnot_yhteenveto": ["Kaikki ok."]
            })
            return json.dumps(data, ensure_ascii=False)

        elif key == "xai_agent":
            data = common_base.copy()
            data["metadata"]["agentti"] = "XAI-Raportoija"
            data["metadata"]["vaihe"] = 9
            data.update({
                "executive_summary": "Tämä on automaattinen yhteenveto.",
                "detailed_analysis": [
                    {"title": "Osa 1", "content": "Sisältö...", "visualizations": []}
                ],
                "final_verdict": "Hyväksytty",
                "confidence_score": 0.95
            })
            return json.dumps(data, ensure_ascii=False)
        
        # Generic Fallback
        return json.dumps({"error": "No mock data available", "mock_key": key})
