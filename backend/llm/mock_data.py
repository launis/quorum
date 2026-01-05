from typing import Any

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
    "InteractionAnalystAgent": "interaction_agent",
}


def get_fallback_data(key: str) -> dict[str, Any]:
    """Returns generic valid JSON for the given proper mock key.
    Used when specific mock responses are missing from data/mock_responses.json.

    Args:
        key (str): The mock key (e.g. 'analyst_agent').

    Returns:
        Dict[str, Any]: A dictionary representing the mock response.

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
    elif key == "panel_agent":
        return _generate_panel_data()

    return {"error": "No mock data available", "mock_key": key}


def get_example_for_agent(agent_class_name: str) -> dict[str, Any] | None:
    """Retrieves the mock data example for a given agent class name.

    Args:
        agent_class_name (str): The class name of the agent.

    Returns:
        Optional[Dict[str, Any]]: The mock example or None if not found.

    """
    key = AGENT_CLASS_TO_MOCK_KEY.get(agent_class_name)
    if key:
        return get_fallback_data(key)
    return None


def _clone(base: dict, agent: str, vaihe: float) -> dict:
    """Helper to deep copy and set base metadata.

    Args:
        base (Dict): The base dictionary structure.
        agent (str): The agent name to inject.
        vaihe (float): The step number (phase).

    Returns:
        Dict: cloned and updated dictionary.

    """
    import copy

    new_data = copy.deepcopy(base)
    new_data["metadata"]["agentti"] = agent
    new_data["metadata"]["vaihe"] = vaihe
    return new_data


def _get_common_base() -> dict[str, Any]:
    """Helper to get common base data for fallback generators.

    Returns:
        Dict[str, Any]: Common base structure with metadata.

    """
    common_metadata = {
        "luontiaika": "2024-01-01T00:00:00Z",
        "agentti": "MockAgent",
        "vaihe": 0,
        "versio": "2.0",
        "suoritus_ymparisto": "Internal",
    }

    return {
        "metadata": common_metadata,
        "metodologinen_loki": "[MOCK] Fallback generation",
        "edellisen_vaiheen_validointi": "N/A",
        "semanttinen_tarkistussumma": "mock_hash",
    }


# --- Generator Functions ---


def _generate_guard_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Vartija", vaihe=1)
    data.update(
        {
            "data": {
                "keskusteluhistoria": "{{FILE: Keskusteluhistoria.pdf}}",
                "lopputuote": "{{FILE: Lopputuote.pdf}}",
                "reflektiodokumentti": "{{FILE: Reflektiodokumentti.pdf}}",
            },
            "security_check": {
                "uhka_havaittu": False,
                "adversariaalinen_simulaatio_tulos": "Clean",
                "riski_taso": "MATALA",
            },
            "safe_data": {
                "keskusteluhistoria": "Puhdistettu historia...",
                "lopputuote": "Puhdistettu tuotos...",
                "reflektiodokumentti": "Puhdistettu reflektio...",
            },
        }
    )
    return data


def _generate_analyst_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Analyytikko", vaihe=2)
    data.update(
        {
            "hypoteesit": [
                {
                    "id": "H1",
                    "vaite_teksti": "Opiskelija osoittaa kriittistä ajattelua.",
                    "loytyyko_todisteita": True,
                    "hakusana_ehdotus": "kriittinen ajattelu pedagogiikka",
                },
                {
                    "id": "H2",
                    "vaite_teksti": "Argumentaatio on puutteellista.",
                    "loytyyko_todisteita": False,
                    "hakusana_ehdotus": None,
                },
            ],
            "rag_todisteet": [
                {
                    "viittaa_hypoteesiin_id": "H1",
                    "perusteet": "Löytyy reflektiosta.",
                    "konteksti_segmentti": "Oivalsin, että argumentaatio vaatii tukea...",
                    "relevanssi_score": 90,
                }
            ],
        }
    )
    return data


def _generate_interaction_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Vuorovaikutus", vaihe=2.2)
    data.update(
        {
            "tunnistetut_strategiat": ["Iterative refinement", "Constraint-based"],
            "ohjausliikkeet": 3,
            "driver_classification": "Kartanlukija",
            "input_control_ratio": 0.35,
        }
    )
    return data


def _generate_profiler_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Profiloija", vaihe=2.5)
    data.update(
        {
            "intentio_analyysi": "Kirjoittajan intentio on vaikuttaa tunteisiin ja vakuuttaa.",
            "tunnetila_ja_savy": "Ahdistunut mutta toiveikas.",
            "tunnistetut_vinoumat": [
                {
                    "nimi": "Vahvistusharha",
                    "selitys": "Analyysi painottaa vain omaa puolta jättäen vasta-argumentit huomiotta.",
                }
            ],
            "psykologinen_profiili": "Puolustuskannalla oleva oppija, joka hakee hyväksyntää.",
            "manipulaatio_yritykset": "Ei havaittu.",
            "teksti_metriikka": {
                "word_count": 150,
                "sentence_count": 15,
                "avg_sentence_length": 10.0,
                "lexical_diversity": 0.6,
                "capitalization_ratio": 0.05,
            },
        }
    )
    return data


def _generate_logician_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Loogikko", vaihe=3)
    data.update(
        {
            "toulmin_analyysi": [
                {
                    "vaite_id": "H1",
                    "claim": "Tekoäly on hyödyllinen.",
                    "data": "Se nopeuttaa työtä.",
                    "warrant": "Nopeus on hyödyllistä.",
                    "backing": "Tutkimukset osoittavat tehokkuuden kasvun.",
                }
            ],
            "kognitiivinen_taso": {"bloom_taso": "Analyze", "strateginen_syvyys": "Syvä"},
            "walton_skeema": {
                "tunnistettu_skeema": "Argument from Expert Opinion",
                "kriittiset_kysymykset": [
                    "Onko asiantuntija luotettava?",
                    "Onko lausunto ristiriidassa muiden kanssa?",
                ],
            },
        }
    )
    return data


def _generate_falsifier_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Falsifioija", vaihe=4)
    data.update(
        {
            "walton_stressitesti_loydokset": [
                {
                    "kysymys": "Mitä jos oletus X on väärä?",
                    "kestiko_todistusaineisto": True,
                    "havainto": "Perustelu nojaa vahvaan dataan.",
                }
            ],
            "paattelyketjun_uskollisuus_auditointi": {
                "onko_post_hoc_rationalisointia": False,
                "perustelu": "Päättely etenee loogisesti premisseistä johtopäätökseen.",
                "uskollisuus_score": "KORKEA",
            },
        }
    )
    return data


def _generate_fact_checker_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Valvoja", vaihe=5)
    data.update(
        {
            "faktantarkistus_rfi": [
                {
                    "vaite": "Maa on pyöreä.",
                    "verifiointi_tulos": "Vahvistettu",
                    "lahde_tai_paattely": "Yleistieto / NASA",
                },
                {"vaite": "Kuu on juustoa.", "verifiointi_tulos": "Kumottu", "lahde_tai_paattely": "Apollo-lennot"},
            ],
            "eettiset_havainnot": [
                {"tyyppi": "Ei havaittu", "vakavuus": "N/A", "kuvaus": "Sisältö noudattaa turvallisuusohjeita."}
            ],
        }
    )
    return data


def _generate_causal_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Kausaalinen", vaihe=6)
    data.update(
        {
            "kausaalinen_auditointi": {
                "aikajana_validi": True,
                "havainnot": "Syys-seuraussuhteet ovat johdonmukaisia.",
            },
            "kontrafaktuaalinen_testi": {
                "skenaario_A_toteutunut": "Opiskelija käytti tekoälyä.",
                "skenaario_B_simulaatio": "Jos opiskelija ei olisi käyttänyt tekoälyä, tulos olisi ollut suppeampi.",
                "uskottavuus_arvio": "Uskottava",
            },
            "abduktiivinen_paatelma": "Aito Oivallus",
        }
    )
    return data


def _generate_performativity_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Performatiivisuus", vaihe=7)
    data.update(
        {
            "performatiivisuus_heuristiikat": [
                {"heuristiikka": "Buzzwords", "lippu_nostettu": False, "kuvaus": "Kieli on luonnollista."}
            ],
            "pre_mortem_analyysi": {"suoritettu": True, "hiljaiset_signaalit": ["Ei havaittu hälyttäviä signaaleja."]},
            "yleisarvio_aitoudesta": "Orgaaninen",
        }
    )
    return data


def _generate_judge_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Tuomari", vaihe=9)
    # UPDATED: Matches EvaluationResult schema (Dynamic Matrix) with explicit scale
    data.update(
        {
            "matrix_id": "matrix_standard_v1",
            "scale_min": 1,
            "scale_max": 5,
            "total_score": 3.3,
            "dimensions": [
                {
                    "dimension_id": "agency",
                    "score": 3,
                    "reasoning": "Käyttäjä ajoi prosessia (Kuski), mutta korjaukset olivat reaktiivisia.",
                },
                {
                    "dimension_id": "synteesi",
                    "score": 4,
                    "reasoning": "Synteesi on vahva ja luo uutta tietoa ('Supermegatrendit').",
                },
                {"dimension_id": "falsification", "score": 3, "reasoning": "Käyttäjä haastoi tekoälyä kohtuullisesti."},
            ],
            "critical_findings": ["Prosessin hallinta parani lopussa.", "Argumentaatio on vahvaa."],
        }
    )
    return data


def _generate_xai_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="XAI-Raportoija", vaihe=13)
    data.update(
        {
            "executive_summary": "Tämä on MOCK-yhteenveto. Järjestelmä on arvioinut suorituksen hyväksyttäväksi.",
            "final_verdict": "Hyväksytty (Kuski)",
            "confidence_score": 0.95,
            "analysis_strengths": "Vahva looginen päättely ja hyvä lähdekritiikki.",
            "analysis_weaknesses": "Hieman toistuvaa kieltä paikoitellen.",
            "analysis_opportunities": "Voisi syventää kausaalianalyysiä.",
            "analysis_recommendations": "Jatka samaan malliin, mutta kiinnitä huomiota kielen variaatioon.",
            "xai_report_formatted": (
                "# XAI Raportti\\n\\n**Päätös:** Hyväksytty.\\n\\nAnalyysi osoittaa vahvaa suoriutumista."
            ),
        }
    )
    return data


def _generate_archivist_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Arkistonhoitaja", vaihe=10)
    data.update(
        {
            "linjakkuus_analyysi": "Linjassa aiemman oikeuskäytännön kanssa.",
            "poikkeamat_linjasta": "Ei merkittäviä poikkeamia.",
            "suositus_tuomarille": "Hyväksy sellaisenaan.",
            "viitatut_ennakkotapaukset": ["Case-2023-001", "Case-2024-055"],
        }
    )
    return data


def _generate_coach_data() -> dict[str, Any]:
    data = _clone(_get_common_base(), agent="Valmentaja", vaihe=12)
    # Matches CoachingPlan(BaseJSON)
    data.update(
        {
            "kannustava_palaute": "Erinomaista työtä 'Supermegatrendit'-konseptin kanssa! "
            "Tämä oli kriittinen oivallus ('Mestaruus'-hetki), joka pakottaa tekoälyn siirtymään "
            "yksinkertaisesta tiivistämisestä korkeamman tason synteesiin (vrt. Toulmin 2003). "
            "Ilman tätä ohjausta raportti olisi jäänyt geneeriseksi listaukseksi.",
            "kehityskohteet_konkreettisesti": [
                {
                    "kategoria": "Prompt Engineering & Tehokkuus",
                    "kohdat": [
                        {
                            "otsikko": "Kontekstin Etupainotteisuus",
                            "kuvaus": "Määrittele rooli (neuvonantaja), kohderyhmä (johtoryhmä) ja tavoite heti alussa. "
                            "Tämä vähentää iteraatioita.",
                            "resurssit": ["Prompt Engineering: The CO-STAR Method"],
                        },
                        {
                            "otsikko": "Suunniteltu Rakenne",
                            "kuvaus": "Pyydä ensin sisällysluettelo hyväksyttäväksi ennen tekstin generointia.",
                            "resurssit": [],
                        },
                    ],
                },
                {
                    "kategoria": "Datan Validointi",
                    "kohdat": [
                        {
                            "otsikko": "Syötedatan Eheystarkistus",
                            "kuvaus": "Tee tarkistuslista (Checklist) syötedatalle. Huomioi puuttuvat raportit.",
                            "resurssit": ["Data Integrity Checklists"],
                        }
                    ],
                },
            ],
            "lopputuloksen_kehitysehdotukset": [
                "Lisää konkreettisia KPI-mittareita 'Kaupalliset Vaikutukset' -osioon.",
                "Täsmennä 'Supermegatrendien' keskinäisiä ristiriitoja (esim. Resurssiniukkuus vs. Teknologia).",
                "Huomioi myös kognitiiviset vinoumat (ks. Kahneman 2011) päätöksenteossa.",
            ],
            "lahdeluettelo": [
                "Toulmin, Stephen E. 2003: The uses of argument. Päivitetty painos. "
                "Cambridge: Cambridge University Press. DOI: 10.1017/CBO9780511802031.",
                "Kahneman, Daniel. 2011: Thinking, fast and slow. New York: Farrar, Straus and Giroux.",
            ],
        }
    )
    return data


def _generate_panel_data() -> dict[str, Any]:
    """Generates a COMPOSITE response for the PanelAgent.
    Must match the complex schema of PanelAgent output.

    Returns:
        Dict[str, Any]: Composite panel data.

    """
    data = _clone(_get_common_base(), agent="Tiedepaneeli", vaihe=6)

    # We essentially execute the sub-generators and merge them.
    # The keys must match what PanelAgent parser expects (snake_case of field names)

    data.update(
        {
            "logiikka_auditointi": _generate_logician_data(),
            "falsifiointi_auditointi": _generate_falsifier_data(),
            "etiikka_ja_fakta": _generate_fact_checker_data(),
            "kausaalinen_auditointi": _generate_causal_data(),
            "performatiivisuus_auditointi": _generate_performativity_data(),
        }
    )

    return data
