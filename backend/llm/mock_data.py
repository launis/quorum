from typing import Dict, Any
import json

def get_fallback_data(key: str) -> Dict[str, Any]:
    """
    Returns the fallback mock data structure for a given agent key.
    Refactored from mock.py to reduce file size.
    """
    
    common_metadata = {
        "luontiaika": "2024-01-01T00:00:00Z",
        "agentti": "MockAgent",
        "vaihe": 0,
        "versio": "2.0",
        "suoritus_ymparisto": "Internal"
    }
    
    common_base = {
        "metadata": common_metadata,
        "metodologinen_loki": "[MOCK] Fallback generation", 
        "edellisen_vaiheen_validointi": "N/A",
        "semanttinen_tarkistussumma": "mock_hash"
    }

    if key == "guard_agent":
        data = _clone(common_base, agent="Vartija", vaihe=1)
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

    elif key == "analyst_agent":
        data = _clone(common_base, agent="Analyytikko", vaihe=2)
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

    elif key == "profiler_agent":
        data = _clone(common_base, agent="Profiloija", vaihe=2.5)
        data.update({
            "intentio_analyysi": "Kirjoittajan intentio on vaikuttaa tunteisiin vetoamalla.",
            "tunnetila_ja_savy": "Ahdistunut mutta toiveikas.",
            "tunnistetut_vinoumat": [
                {"nimi": "Vahvistusharha (Confirmation Bias)", "selitys": "Analyysi painottaa vain omaa näkökulmaa tukevia havaintoja."},
                {"nimi": "Kehystämisvaikutus (Framing Effect)", "selitys": "Asiat on kehystetty korostetun negatiivisesti ilman tasapuolisuutta."}
            ],
            "psykologinen_profiili": "Puolustuskannalla oleva oppija.",
            "manipulaatio_yritykset": "Ei havaittu selkeää manipulaatiota."
        })
        return data

    elif key == "logician_agent":
        data = _clone(common_base, agent="Loogikko", vaihe=3)
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
        return data

    elif key == "falsifier_agent":
        data = _clone(common_base, agent="Falsifioija", vaihe=4)
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

    elif key == "fact_checker_agent":
        data = _clone(common_base, agent="Valvoja", vaihe=5)
        data.update({
            "faktantarkistus_rfi": [
                {"vaite": "Maa on pyöreä", "verifiointi_tulos": "Vahvistettu", "lahde_tai_paattely": "Yleistieto"}
            ],
            "eettiset_havainnot": [
                {"tyyppi": "Ei havaittu", "vakavuus": "N/A", "kuvaus": "OK"}
            ]
        })
        return data

    elif key == "causal_agent":
        data = _clone(common_base, agent="Kausaalinen", vaihe=6)
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

    elif key == "archivist_agent":
        data = _clone(common_base, agent="Arkistonhoitaja", vaihe=8.5)
        data.update({
            "linjakkuus_analyysi": "Suoritus on linjassa aiempien tapausten kanssa.",
            "poikkeamat_linjasta": "Ei merkittäviä poikkeamia.",
            "suositus_tuomarille": "Suosittelen neutraalia arviota.",
            "viitatut_ennakkotapaukset": ["Case-123"]
        })
        return data

    elif key == "performativity_agent":
        data = _clone(common_base, agent="Performatiivisuus", vaihe=7)
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

    elif key == "judge_agent":
        data = _clone(common_base, agent="Tuomari", vaihe=8)
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

    elif key == "xai_agent":
        data = _clone(common_base, agent="XAI-Raportoija", vaihe=9)
        data.update({
            "executive_summary": "Tämä on automaattinen yhteenveto.",
            "analysis_strengths": "Vahvuudet...",
            "analysis_weaknesses": "Heikkoudet...",
            "analysis_opportunities": "Mahdollisuudet...",
            "analysis_recommendations": "Suositukset...",
            "final_verdict": "Hyväksytty",
            "confidence_score": 0.95
        })
        return data

    elif key == "coach_agent":
        data = _clone(common_base, agent="Valmentaja", vaihe=10)
        data.update({
            "kannustava_palaute": "Hyvää työtä analyysin kanssa!",
            "kehityskohteet_konkreettisesti": [
                {"otsikko": "Argumentaation syventäminen", "kuvaus": "Tutustu Toulmin malliin tarkemmin.", "resurssit": []}
            ],
            "lopputuloksen_kehitysehdotukset": ["Parempi jäsentely."],
            "oppimispolku_viikko": "Maanantai: Lue teoria. Tiistai: Harjoittele."
        })
        return data
        
    return {"error": "No mock data available", "mock_key": key}

def _clone(base: Dict, agent: str, vaihe: float) -> Dict:
    """Helper to deep copy and set base metadata"""
    import copy
    new_data = copy.deepcopy(base)
    new_data["metadata"]["agentti"] = agent
    new_data["metadata"]["vaihe"] = vaihe
    return new_data
