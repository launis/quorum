import json
import os
import sys
from typing import Dict, Any, Optional
from tinydb import TinyDB, Query

original_call_llm = BaseAgent._call_llm

def mock_get_json_response(self, prompt: str, system_instruction: Optional[str] = None, max_retries: int = 3) -> Dict[str, Any]:
    # Capture the prompt and system instruction
    CAPTURED_PROMPTS.append({
        "agent": self.__class__.__name__,
        "system_instruction": system_instruction,
        "user_content": prompt
    })
    
    # Return mock data based on agent type to allow workflow to proceed
    agent_name = self.__class__.__name__
    if agent_name == "GuardAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Guard", "vaihe": 1},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "data": {"keskusteluhistoria": "...", "lopputuote": "...", "reflektiodokumentti": "..."},
            "security_check": {"uhka_havaittu": False, "adversariaalinen_simulaatio_tulos": "Clean", "riski_taso": "MATALA"}
        }
    elif agent_name == "AnalystAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Analyst", "vaihe": 2},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "hypoteesit": [],
            "rag_todisteet": []
        }
    elif agent_name == "LogicianAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Logician", "vaihe": 3},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "toulmin_analyysi": [],
            "kognitiivinen_taso": {"bloom_taso": "3", "strateginen_syvyys": "High"},
            "walton_skeema": {"tunnistettu_skeema": "Expert Opinion", "kriittiset_kysymykset": []}
        }
    elif agent_name == "LogicalFalsifierAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Falsifier", "vaihe": 4},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "walton_stressitesti_loydokset": [],
            "paattelyketjun_uskollisuus_auditointi": {"onko_post_hoc_rationalisointia": False, "perustelu": "...", "uskollisuus_score": "KORKEA"}
        }
    elif agent_name == "CausalAnalystAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Causal", "vaihe": 5},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "kausaalinen_auditointi": {"aikajana_validi": True, "havainnot": "..."},
            "kontrafaktuaalinen_testi": {"skenaario_A_toteutunut": "...", "skenaario_B_simulaatio": "...", "uskottavuus_arvio": "..."},
            "abduktiivinen_paatelma": "Aito Oivallus"
        }
    elif agent_name == "PerformativityDetectorAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Performativity", "vaihe": 6},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "performatiivisuus_heuristiikat": [],
            "pre_mortem_analyysi": {"suoritettu": True, "hiljaiset_signaalit": []},
            "yleisarvio_aitoudesta": "Orgaaninen"
        }
    elif agent_name == "FactualOverseerAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "FactChecker", "vaihe": 7},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "faktantarkistus_rfi": [],
            "eettiset_havainnot": []
        }
    elif agent_name == "JudgeAgent":
        return {
            "metadata": {"luontiaika": "2023-01-01", "agentti": "Judge", "vaihe": 8},
            "metodologinen_loki": "Mock Log",
            "edellisen_vaiheen_validointi": "OK",
            "semanttinen_tarkistussumma": "123",
            "konfliktin_ratkaisut": [],
            "mestaruus_poikkeama": {"tunnistettu": False, "perustelu": "..."},
            "aitous_epaily": {"automaattinen_lippu": False, "viesti_hitl:lle": "..."},
            "pisteet": {
                "analyysi_ja_prosessi": {"arvosana": 3, "perustelu": "..."},
                "arviointi_ja_argumentaatio": {"arvosana": 3, "perustelu": "..."},
                "synteesi_ja_luovuus": {"arvosana": 3, "perustelu": "..."}
            },
            "kriittiset_havainnot_yhteenveto": []
        }
    
    return {}

def mock_call_llm(self, prompt: str, system_instruction: Optional[str] = None) -> str:
    # Capture for XAI Agent which uses _call_llm directly
    CAPTURED_PROMPTS.append({
        "agent": self.__class__.__name__,
        "system_instruction": system_instruction,
        "user_content": prompt
    })
    return "MOCK XAI REPORT"

BaseAgent.get_json_response = mock_get_json_response
BaseAgent._call_llm = mock_call_llm

def verify_prompts():
    print("Initializing Engine...")
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')
    engine = WorkflowEngine(db_path)
    
    print("Executing Workflow Simulation...")
    # We need to find the workflow ID.
    # Assuming HOLISTINEN_MESTARUUS_3 is the one.
    try:
        engine.execute_workflow('HOLISTINEN_MESTARUUS_3', MOCK_INPUTS)
    except Exception as e:
        print(f"Simulation finished (or failed): {e}")

    print(f"Captured {len(CAPTURED_PROMPTS)} steps.")

    with open('verification_output.txt', 'w', encoding='utf-8') as f:
        f.write("=== VERIFICATION OUTPUT: FULL PROMPTS ===\n")
        f.write("This file contains the EXACT prompts (System + User) generated by the system.\n")
        f.write("You can copy-paste these into an LLM to reproduce the step manually.\n\n")
        
        for i, capture in enumerate(CAPTURED_PROMPTS):
            f.write(f"--- STEP {i+1}: {capture['agent']} ---\n\n")
            
            f.write("### SYSTEM INSTRUCTION (Säännöt ja Roolit) ###\n")
            f.write(capture['system_instruction'] or "[NO SYSTEM INSTRUCTION]")
            f.write("\n\n")
            
            f.write("### USER CONTENT (Syöte ja Data) ###\n")
            f.write(capture['user_content'])
            f.write("\n\n")
            f.write("="*80 + "\n\n")

    print("Verification output written to verification_output.txt")

if __name__ == "__main__":
    verify_prompts()
