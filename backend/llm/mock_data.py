from typing import Dict, Any, Optional
import json

AGENT_CLASS_TO_MOCK_KEY = {
    "GuardAgent": "guard_agent",
    "AnalystAgent": "analyst_agent",
    "ProfilerAgent": "profiler_agent",
    "LogicianAgent": "logician_agent",
    "LogicalFalsifierAgent": "falsifier_agent",
    "FactualOverseerAgent": "fact_checker_agent",
    "CausalAnalystAgent": "causal_agent",
    "PerformativityDetectorAgent": "performativity_agent",
    "JudgeAgent": "judge_agent",
    "XAIReporterAgent": "xai_agent",
    "ArchivistAgent": "archivist_agent",
    "CoachAgent": "coach_agent",
    "PanelAgent": "panel_agent",
    "InteractionAnalystAgent": "interaction_agent"
}

def get_fallback_data(key: str) -> Dict[str, Any]:
    """
    Returns generic valid JSON for the given proper mock key.
    Used when specific mock responses are missing from data/mock_responses.json.
    """
    if key == "guard_agent":
        return _generate_guard_data()
    elif key == "analyst_agent":
        return _generate_analyst_data()
    elif key == "interaction_agent":
        return _generate_interaction_data()
    elif key == "profiler_agent":
        return _generate_profiler_data()
    elif key == "logician_agent":
        return _generate_logician_data()
    elif key == "falsifier_agent":
        return _generate_falsifier_data()
    elif key == "fact_checker_agent":
        return _generate_fact_checker_data()
    elif key == "causal_agent":
        return _generate_causal_data()
    elif key == "archivist_agent":
        return _generate_archivist_data()
    elif key == "performativity_agent":
        return _generate_performativity_data()
    elif key == "judge_agent":
        return _generate_judge_data()
    elif key == "xai_agent":
        return _generate_xai_data()
    elif key == "coach_agent":
        return _generate_coach_data()
        
    return {"error": "No mock data available", "mock_key": key}

def get_example_for_agent(agent_class_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the mock data example for a given agent class name.
    """
    key = AGENT_CLASS_TO_MOCK_KEY.get(agent_class_name)
    if key:
        return get_fallback_data(key)
    return None

def _clone(base: Dict, agent: str, vaihe: float) -> Dict:
    """Helper to deep copy and set base metadata"""
    import copy
    new_data = copy.deepcopy(base)
    new_data["metadata"]["agentti"] = agent
    new_data["metadata"]["vaihe"] = vaihe
    return new_data

def _get_common_base() -> Dict[str, Any]:
    """Helper to get common base data for fallback generators."""
    common_metadata = {
        "luontiaika": "2024-01-01T00:00:00Z",
        "agentti": "MockAgent",
        "vaihe": 0,
        "versio": "2.0",
        "suoritus_ymparisto": "Internal"
    }
    
    return {
        "metadata": common_metadata,
        "metodologinen_loki": "[MOCK] Fallback generation", 
        "edellisen_vaiheen_validointi": "N/A",
        "semanttinen_tarkistussumma": "mock_hash"
    }

# --- Generator Functions ---

def _generate_guard_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Vartija", vaihe=1)
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
    return data

def _generate_analyst_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Analyytikko", vaihe=2)
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
    return data

def _generate_interaction_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Vuorovaikutus", vaihe=2.2)
    data.update({
        "tunnistetut_strategiat": ["Täsmällinen kontekstointi", "Roolitus"],
        "ohjausliikkeet": 3,
        "driver_classification": "Kartanlukija",
        "input_control_ratio": 0.35
    })
    return data

def _generate_profiler_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Profiloija", vaihe=2.5)
    data.update({
        "intentio_analyysi": "Kirjoittajan intentio on vaikuttaa tunteisiin.",
        "tunnetila_ja_savy": "Ahdistunut mutta toiveikas.",
        "tunnistetut_vinoumat": [
             {"nimi": "Vahvistusharha", "selitys": "Analyysi painottaa vain omaa puolta."}
        ],
        "psykologinen_profiili": "Puolustuskannalla oleva oppija.",
        "manipulaatio_yritykset": "Ei havaittu."
    })
    return data

def _generate_logician_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Loogikko", vaihe=3)
    data.update({
        "toulmin_analyysi": [
            {"vaite_id": "H1", "claim": "Claim text", "data": "Data", "warrant": "Warrant", "backing": "Backing"}
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
    return data

def _generate_falsifier_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Falsifioija", vaihe=4)
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
    return data

def _generate_fact_checker_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Valvoja", vaihe=5)
    data.update({
        "faktantarkistus_rfi": [
            {"vaite": "Maa on pyöreä", "verifiointi_tulos": "Vahvistettu", "lahde_tai_paattely": "Yleistieto"}
        ],
        "eettiset_havainnot": [
             {"tyyppi": "Ei havaittu", "vakavuus": "N/A", "kuvaus": "OK"}
        ]
    })
    return data

def _generate_causal_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Kausaalinen", vaihe=6)
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
    return data

def _generate_performativity_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Performatiivisuus", vaihe=7)
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
    return data

def _generate_judge_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Tuomari", vaihe=8)
    data.update({
        "konfliktin_ratkaisut": [],
        "mestaruus_poikkeama": {"tunnistettu": False, "perustelu": "Normaali suoritus."},
        "aitous_epaily": {"automaattinen_lippu": False, "viesti_hitl:lle": "Ei huomautettavaa."},
        "pisteet": {
            "analyysi": {"arvosana": 3, "perustelu": "Hyvä."},
            "arviointi": {"arvosana": 3, "perustelu": "Hyvä."},
            "synteesi": {"arvosana": 3, "perustelu": "Hyvä."}
        },
        "kriittiset_havainnot_yhteenveto": ["Kaikki ok."]
    })
    return data

def _generate_xai_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="XAI-Raportoija", vaihe=9)
    data.update({
        "executive_summary": "Tämä on automaattinen yhteenveto.",
        "final_verdict": "Hyväksytty",
        "confidence_score": 0.95,
        "analysis_strengths": "Vahvuudet...",
        "analysis_weaknesses": "Heikkoudet...",
        "analysis_opportunities": "Mahdollisuudet...",
        "analysis_recommendations": "Suositukset..."
    })
    return data

def _generate_archivist_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Arkistonhoitaja", vaihe=8.5)
    data.update({
        "linjakkuus_analyysi": "Linjassa.",
        "poikkeamat_linjasta": "Ei poikkeamia.",
        "suositus_tuomarille": "Neutraali.",
        "viitatut_ennakkotapaukset": ["Case-123"]
    })
    return data

def _generate_coach_data() -> Dict[str, Any]:
    data = _clone(_get_common_base(), agent="Valmentaja", vaihe=10)
    data.update({
        "kannustava_palaute": "Hyvää työtä!",
        "kehityskohteet_konkreettisesti": [
            {
                "kategoria": "Logiikka",
                "kohdat": [
                    {"otsikko": "Argumentaatio", "kuvaus": "Syvennä perusteluja.", "resurssit": ["Toulmin 2003"]}
                ]
            }
        ],
        "lopputuloksen_kehitysehdotukset": ["Parempi jäsentely."],
        "lahdeluettelo": ["Toulmin, S. (2003). The Uses of Argument."]
    })
    return data
