import json
import uuid

def generate_tda_id():
    return "tda_" + uuid.uuid4().hex[:16]

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

found = False
for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_c5804a9143c34cb1":
        found = True
        
        # 1. XML + Theory Injection (Anti-Token Bloat)
        block["ai_description"] = (
            "<system_directive>\n"
            "<objective>Evaluate the structural integrity of causal claims, identifying spurious correlations and validating strict causal mechanisms.</objective>\n"
            "<epistemic_anchor>Pearl, J. 'The Book of Why: The New Science of Cause and Effect'. Evaluates the transition from observation (correlation) to intervention and counterfactual reasoning. Lexical markers of success include explicit counterfactuals ('if not X, then not Y') or isolation of confounders.</epistemic_anchor>\n"
            "<rules>\n"
            "<rule>Enforce the Null Hypothesis: Assume all claimed causal links are post hoc fallacies or spurious correlations until an explicit causal mechanism is proven.</rule>\n"
            "</rules>\n"
            "</system_directive>"
        )
        
        # Ensure theory grounding exists
        block["theory_grounding"] = {
            "citation_reference": "Pearl, J., & Mackenzie, D. (2018). The Book of Why: The New Science of Cause and Effect.",
            "source_url": "https://plato.stanford.edu/entries/causal-models/"
        }
        
        # 2. MECE Triangulation (Exactly 3 claims per scale)
        block["scales"] = [
            {
                "score": 1,
                "name": {"default_locale": "fi", "translations": {"fi": "Mahdoton (Impossible)", "en": "Impossible"}},
                "ai_label": "CATASTROPHIC FAILURE - POST HOC FALLACY",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen Post Hoc -virhe", "en": "Complete Post Hoc fallacy"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE a gross logical fallacy where the claimed cause has no demonstrable connection to the effect.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE a gross logical fallacy where the claimed cause has no demonstrable connection to the effect. The outcome is purely coincidental. Document the missing causal link in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Harhauttava taustamuuttuja", "en": "Confounding variable"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an outcome clearly driven by an unacknowledged confounding variable rather than the stated cause.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an outcome that is clearly driven by an unacknowledged confounding variable (a common cause affecting both) rather than the stated cause. Map the confounder in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Täysin satunnainen yhteys", "en": "Purely coincidental connection"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY a purely coincidental or temporal sequence presented falsely as causation.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY a purely coincidental or temporal sequence presented falsely as causation. Look for 'X happened, then Y happened, therefore X caused Y'. Document the fallacy in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 2,
                "name": {"default_locale": "fi", "translations": {"fi": "Epätodennäköinen (Unlikely)", "en": "Unlikely"}},
                "ai_label": "FUNDAMENTALLY FLAWED - SPURIOUS CORRELATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Pinnallinen korrelaatio", "en": "Superficial correlation"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE a superficial correlation where two events occur together, but no causal mechanism is proposed.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE a superficial correlation where two events occur together, but no causal mechanism is proposed or tested. Document the difference between correlation and causation here in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Riittämätön ohjaus", "en": "Insufficient causal input"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the cause is too vague or weak to logically produce the highly specific outcome.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the stated cause (e.g., user input) is too vague or weak to logically produce the highly specific outcome claimed. Document the disproportionate effect in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Kausaalisen mekanismin sivuuttaminen", "en": "Ignoring the causal mechanism"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY an argument that assumes causation without explaining the step-by-step mechanism.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY an argument that aggressively assumes causation while completely ignoring the step-by-step mechanical bridge required to link cause to effect. Map the missing bridge in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 3,
                "name": {"default_locale": "fi", "translations": {"fi": "Mahdollinen (Plausible)", "en": "Plausible"}},
                "ai_label": "NEUTRAL - IMPLICIT CAUSATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Mekaaninen perussyy-seuraus", "en": "Mechanical baseline causation"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of a plausible temporal and logical sequence linking cause to effect.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of a plausible temporal and logical sequence linking a cause to an effect. Document the basic causal pair in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Oletettujen mekanismien varassa", "en": "Reliance on assumed mechanisms"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE causation that relies heavily on implicit assumptions rather than explicit proof.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where causation is plausible but relies heavily on implicit assumptions rather than explicitly stated proof. Identify the hidden assumption in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vaihtoehtoisten syiden sivuuttaminen", "en": "Ignoring alternative causes"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT a conclusion that fails to actively rule out alternative causes.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a conclusion that establishes a basic link but fails to actively rule out alternative causes or confounding factors. Document the unaddressed alternatives in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 4,
                "name": {"default_locale": "fi", "translations": {"fi": "Todennäköinen (Probable)", "en": "Probable"}},
                "ai_label": "LOGICALLY SOUND - VERIFIABLE CAUSATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Eksplisiittinen kausaalimekanismi", "en": "Explicit causal mechanism"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE a robust argument where the step-by-step causal mechanism is explicitly detailed.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE a robust argument where the step-by-step causal mechanism linking input to outcome is explicitly and verifiably detailed. Map the explicit steps in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vaihtoehtojen hallittu poissulkeminen", "en": "Controlled exclusion of alternatives"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND evidence that obvious alternative causes have been systematically ruled out.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that obvious alternative causes or confounders have been systematically acknowledged and actively ruled out. Document the exclusion logic in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Suhteellisuudentajuinen varmuus", "en": "Proportionate certainty"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an analysis where the level of certainty in the claim matches the strength of the evidence.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an analysis where the level of certainty in the causal claim is epistemically humble, perfectly matching the strength of the provided evidence. Document this balance in reasoning_trace before quoting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    }
                ]
            },
            {
                "score": 5,
                "name": {"default_locale": "fi", "translations": {"fi": "Täysin Varma (Absolute Certainty)", "en": "Absolute Certainty"}},
                "ai_label": "THEORETICALLY PERFECT - CAUSAL INTEGRITY",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen kausaalinen eristys", "en": "Perfect causal isolation"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND a masterfully constructed argument that perfectly isolates the true cause.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND a masterfully constructed argument that perfectly isolates the true cause, explicitly demonstrating how all intervening variables and confounders were neutralized. Map this isolation in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Kontrafaktuaalinen analyysi", "en": "Counterfactual analysis"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE explicit 'System 2' deliberation using counterfactual reasoning.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE explicit 'System 2' deliberation using rigorous counterfactual reasoning (e.g., 'If X had not occurred, Y would not have happened'). Document the counterfactual test in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Aukoton kausaalinen ketju", "en": "Watertight causal chain"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT a definitive causal chain that is completely anchored in verifiable evidence.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a definitive causal chain that is completely anchored in verifiable evidence, leaving absolute zero room for logical fallacy or post hoc rationalization. Map the flawless triad in reasoning_trace before extracting the conclusion.",
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
    print("Successfully refactored blk_c5804a9143c34cb1 with TDA mandates.")
else:
    print("Error: Block blk_c5804a9143c34cb1 not found!")
