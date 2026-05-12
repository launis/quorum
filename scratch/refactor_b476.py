import json
import uuid

def generate_tda_id():
    return "tda_" + uuid.uuid4().hex[:16]

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

found = False
for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_b476f89fb732448c":
        found = True
        
        # 1. XML + Theory Injection (Anti-Token Bloat)
        block["ai_description"] = (
            "<system_directive>\n"
            "<objective>Evaluate the user's attempt to actively falsify their own hypotheses and test the boundaries of the AI's output.</objective>\n"
            "<epistemic_anchor>Karl Popper. 'Conjectures and Refutations'. A scientific hypothesis must be falsifiable. Evaluates whether the user acts as a sycophant (confirming bias) or a scientist (actively attempting to disprove their own claims). Lexical markers of success include explicit edge-case testing, playing devil's advocate, or seeking contradictory data.</epistemic_anchor>\n"
            "<rules>\n"
            "<rule>Enforce the Null Hypothesis: Assume the user is exhibiting confirmation bias and sycophancy until explicit, proactive falsification attempts are identified.</rule>\n"
            "</rules>\n"
            "</system_directive>"
        )
        
        # Ensure theory grounding exists
        block["theory_grounding"] = {
            "citation_reference": "Popper, K. (1963). Conjectures and Refutations: The Growth of Scientific Knowledge.",
            "source_url": "https://plato.stanford.edu/entries/popper/"
        }
        
        # 2. MECE Triangulation (Exactly 3 claims per scale)
        block["scales"] = [
            {
                "score": 1,
                "name": {"default_locale": "fi", "translations": {"fi": "Myötäilyvinouma (Sycophancy)", "en": "Sycophancy"}},
                "ai_label": "CATASTROPHIC FAILURE - UNCRITICAL ACCEPTANCE",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Ensimmäinen vastaus hyväksytään sokeasti.", "en": "First response blindly accepted"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user passively accepts the AI's initial output without any challenge or verification.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user passively accepts the AI's initial output without any challenge, verification, or skepticism. Document the total lack of critical faculty in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vaihtoehtoisten näkökulmien puuttuminen.", "en": "Absence of alternative perspectives"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where obvious alternative hypotheses or failure modes are completely ignored.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where obvious alternative hypotheses or failure modes are completely ignored. Map the missing alternatives in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Absoluuttinen varmuus ilman testausta.", "en": "Absolute certainty without testing"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the treatment of AI output as infallible truth without empirical testing.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the treatment of AI output as infallible truth without demanding empirical evidence or testing. Document this hubris in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 2,
                "name": {"default_locale": "fi", "translations": {"fi": "Kosmeettinen Korjaaja", "en": "Aesthetic Refinement"}},
                "ai_label": "FUNDAMENTALLY FLAWED - CONFIRMATION BIAS",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Muutospyynnöt ovat pintapuolisia.", "en": "Superficial change requests"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an engagement that is purely cosmetic, focusing only on style or formatting.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an engagement that is purely cosmetic, focusing only on style, tone, or formatting instead of logical substance. Document the superficiality in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Alkuperäistä logiikkaa ei haasteta.", "en": "Original logic is unchallenged"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the user explicitly avoids challenging the core substantive logic.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the user explicitly avoids challenging the core substantive logic or underlying assumptions. Document the unchallenged core in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vahvistusharha (Confirmation Bias).", "en": "Confirmation Bias"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user only seeks information that confirms their existing belief.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where the user only seeks information or prompts the AI in a way that confirms their existing belief, ignoring contradictory evidence. Map the bias in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 3,
                "name": {"default_locale": "fi", "translations": {"fi": "Neutraali", "en": "Neutral"}},
                "ai_label": "NEUTRAL - REACTIVE CORRECTION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Mekaaninen virheiden korjaaminen.", "en": "Mechanical error correction"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of reactive error correction where obvious mistakes are fixed.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of reactive error correction where obvious mistakes are fixed, but without deeper structural probing. Document the reactive fix in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Epäsystemaattinen testaus.", "en": "Unsystematic testing"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE testing or challenges that are arbitrary or lack a systematic falsification method.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE testing or challenges that are arbitrary or lack a systematic falsification method. Document the randomness of the test in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Reunatapauksien sivuuttaminen.", "en": "Ignoring edge cases"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an analysis that fixes the main path but fails to proactively test edge cases.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an analysis that fixes the main path ('happy path') but completely fails to proactively test edge cases or stress boundaries. Map the ignored edge cases in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 4,
                "name": {"default_locale": "fi", "translations": {"fi": "Proaktiivinen", "en": "Proactive"}},
                "ai_label": "LOGICALLY SOUND - PROACTIVE VULNERABILITY TESTING",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Aktiivinen rajojen kokeilu.", "en": "Active boundary testing"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE explicit instances where the user actively pushes the AI's boundaries to find failure points.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE explicit instances where the user actively pushes the AI's boundaries to find logical or operational failure points. Document the boundary being tested in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vastahypoteesien formulointi.", "en": "Formulating counter-hypotheses"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND evidence that the user formulates explicit counter-hypotheses.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that the user formulates explicit counter-hypotheses (playing devil's advocate) to test against the primary claim. Document the formulated counter-hypothesis in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Rakenteellinen itsekritiikki.", "en": "Structural self-criticism"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an explicit acknowledgment of the limitations of the current testing methodology.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an explicit acknowledgment of the limitations of the current testing methodology or the user's own blind spots. Document the epistemic humility in reasoning_trace before quoting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    }
                ]
            },
            {
                "score": 5,
                "name": {"default_locale": "fi", "translations": {"fi": "Tieteellinen", "en": "Scientific"}},
                "ai_label": "THEORETICALLY PERFECT - MASTERFUL FALSIFICATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Systemaattinen falsifiointipyrkimys.", "en": "Systematic falsification attempt"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND a masterful execution where the user designs a rigorous test explicitly intended to falsify their own core hypothesis.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND a masterful execution where the user designs a rigorous test explicitly intended to falsify their own core hypothesis. Document the falsification method in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen vastaväitteiden integrointi.", "en": "Perfect integration of counterarguments"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an explicit integration where the strongest possible counterarguments are dismantled with verifiable data.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an explicit integration where the strongest possible counterarguments are not just mentioned, but proactively dismantled with verifiable data. Map the dismantled counterargument in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Kognitiivisen kitkan todentaminen.", "en": "Verification of cognitive friction"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT definitive 'System 2' deliberation demonstrating deep epistemic humility and scientific skepticism.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT definitive 'System 2' deliberation demonstrating deep epistemic humility and rigorous scientific skepticism, ensuring the final claim is completely battle-tested. Document the cognitive friction in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    }
                ]
            }
        ]
        break

if found:
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Successfully refactored blk_b476f89fb732448c with TDA mandates.")
else:
    print("Error: Block blk_b476f89fb732448c not found!")
