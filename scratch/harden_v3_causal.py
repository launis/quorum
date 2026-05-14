import json


def harden_v3_causal():
    seed_path = "backend_v2/seed/seed_data.json"
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    # Pearl's Do-Calculus & Causal Inference
    causal_claims = {
        0: [ # 1 - Impossible (Catastrophic Failure - Post Hoc Fallacy)
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen Post Hoc -virhe", "en": "Complete Post Hoc fallacy"}},
                "ai_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. LOCATE an explicit declaration that X caused Y solely because X preceded Y.",
                "tda_assertions": [{
                    "tda_id": "tda_c1_1",
                    "ai_rule_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. LOCATE an explicit declaration that X caused Y solely because X preceded Y temporally. BANNED: Do not extract simple sequential descriptions. Find the active, false causal claim. Document the temporal logical leap in reasoning_trace before extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Harhauttava taustamuuttuja (Confounding)", "en": "Unacknowledged Confounder"}},
                "ai_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. EXTRACT an outcome explicitly attributed to a variable, while ignoring the obvious common cause (Confounder).",
                "tda_assertions": [{
                    "tda_id": "tda_c1_2",
                    "ai_rule_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. EXTRACT an outcome explicitly attributed to a surface variable, while completely ignoring the obvious common cause (Confounder/Z-variable) that drives both. Map the ignored confounder in reasoning_trace before quoting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Sokea assosiaatio (Rung 1)", "en": "Blind Association"}},
                "ai_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. IDENTIFY where passive observation (correlation) is forcefully asserted as intervention (causation).",
                "tda_assertions": [{
                    "tda_id": "tda_c1_3",
                    "ai_rule_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. IDENTIFY where passive observation (Pearl's Rung 1: Association) is forcefully asserted as active intervention (Rung 2). Anti-Proxies: The text treats 'associated with' as 'caused by'. Document the categorical error in reasoning_trace before extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            }
        ],
        1: [ # 2 - Unlikely (Spurious Correlation)
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Pinnallinen korrelaatio", "en": "Superficial Correlation"}},
                "ai_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. LOCATE a superficial correlation treated as actionable intelligence.",
                "tda_assertions": [{
                    "tda_id": "tda_c2_1",
                    "ai_rule_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. LOCATE a superficial correlation treated as actionable intelligence without any proposed mechanical bridge. Document the missing 'how' in reasoning_trace before extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Käänteisen kausaation sivuuttaminen", "en": "Ignoring Reverse Causation"}},
                "ai_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. EXTRACT an instance where Y causing X is completely unaddressed as an alternative.",
                "tda_assertions": [{
                    "tda_id": "tda_c2_2",
                    "ai_rule_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. EXTRACT an instance where the author asserts X causes Y, but completely fails to address the highly plausible alternative that Y causes X (Reverse Causation). Document the reverse potential in reasoning_trace before quoting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Välittävän mekanismin ohittaminen", "en": "Bypassing the Mediator"}},
                "ai_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. IDENTIFY a direct causal claim that ignores the necessary intermediary step (Mediator).",
                "tda_assertions": [{
                    "tda_id": "tda_c2_3",
                    "ai_rule_description": "FATAL FLAW DIRECTIVE: BOUNTY HUNTER MANDATE. IDENTIFY a direct causal claim between distant variables that actively ignores the necessary intermediary step (Mediator variable). Map the missing mediator in reasoning_trace before extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            }
        ],
        2: [ # 3 - Neutral (Implicit Causation)
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Mekaaninen Rung 2 -interventio", "en": "Mechanical Rung 2 Intervention"}},
                "ai_description": "CRITICAL DIRECTIVE: IDENTIFY baseline evidence of an active intervention (doing) producing an expected outcome.",
                "tda_assertions": [{
                    "tda_id": "tda_c3_1",
                    "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY baseline evidence of an active intervention (Pearl's Rung 2: 'Doing'). The text explicitly describes an action taken and its direct physical/logical outcome. Document the action-outcome pair in reasoning_trace before extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Implisiittinen olettama", "en": "Implicit Assumption"}},
                "ai_description": "CRITICAL DIRECTIVE: LOCATE causation that relies on unstated but plausible contextual mechanisms.",
                "tda_assertions": [{
                    "tda_id": "tda_c3_2",
                    "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where causation is plausible but relies heavily on unstated background assumptions. The mechanism is implied rather than proven. Identify the hidden assumption in reasoning_trace before extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Vaihtoehtojen passiivinen poissulkematta jättäminen", "en": "Passive Failure to Exclude Alternatives"}},
                "ai_description": "CRITICAL DIRECTIVE: EXTRACT a conclusion that establishes a basic link but fails to actively neutralize alternative paths.",
                "tda_assertions": [{
                    "tda_id": "tda_c3_3",
                    "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a conclusion that establishes a basic Rung 2 link but fails to actively neutralize alternative paths or confounding factors. Document the unaddressed alternatives in reasoning_trace before extracting.",
                    "inverse_evidence": True,
                    "aggregation_mode": "EXISTS"
                }]
            }
        ],
        3: [ # 4 - Probable (Logically Sound)
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Eksplisiittinen kausaalimekanismi", "en": "Explicit Causal Mechanism"}},
                "ai_description": "CRITICAL DIRECTIVE: LOCATE a robust argument where the step-by-step causal mechanism is explicitly detailed.",
                "tda_assertions": [{
                    "tda_id": "tda_c4_1",
                    "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE a robust argument where the step-by-step causal mechanism linking input to outcome is explicitly detailed. The 'how' is fully mapped. Document the mechanism steps in reasoning_trace before extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Taustamuuttujien hallittu eristäminen", "en": "Controlled Isolation of Confounders"}},
                "ai_description": "CRITICAL DIRECTIVE: FIND evidence that confounding variables have been systematically identified and isolated.",
                "tda_assertions": [{
                    "tda_id": "tda_c4_2",
                    "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that potential confounding variables have been systematically acknowledged and explicitly neutralized. Document the isolated confounder in reasoning_trace before extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Suhteellisuudentajuinen varmuus", "en": "Proportionate certainty"}},
                "ai_description": "CRITICAL DIRECTIVE: EXTRACT an analysis where the certainty strictly matches the evidence, avoiding over-extrapolation.",
                "tda_assertions": [{
                    "tda_id": "tda_c4_3",
                    "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an analysis demonstrating epistemic humility. The author's certainty strictly matches the evidence provided, explicitly stating the boundaries of the causal claim. Document this boundary in reasoning_trace before quoting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            }
        ],
        4: [ # 5 - Absolute Certainty (Perfect Causal Integrity)
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Kontrafaktuaalinen testaus (Rung 3)", "en": "Counterfactual Testing (Rung 3)"}},
                "ai_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. FIND explicit 'System 2' counterfactual reasoning (Pearl's Rung 3).",
                "tda_assertions": [{
                    "tda_id": "tda_c5_1",
                    "ai_rule_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. FIND explicit 'System 2' counterfactual reasoning (Pearl's Rung 3: 'What if X had not happened?'). The author must actively simulate the alternate timeline to prove necessary causation. Document the counterfactual test in reasoning_trace before extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Do-operaattorin aukoton todistus", "en": "Watertight Do-Operator Proof"}},
                "ai_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. EXTRACT a definitive causal chain that perfectly isolates the true cause.",
                "tda_assertions": [{
                    "tda_id": "tda_c5_2",
                    "ai_rule_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. EXTRACT a definitive causal chain that perfectly isolates the true cause, leaving zero room for post hoc rationalization or latent colliders. Map the flawless triad in reasoning_trace before extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            },
            {
                "label": {"default_locale": "fi", "translations": {"fi": "Kausaalimallin ulkoinen ankkurointi", "en": "External Anchoring of the Causal Model"}},
                "ai_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. LOCATE where the causal mechanism is backed by established structural models.",
                "tda_assertions": [{
                    "tda_id": "tda_c5_3",
                    "ai_rule_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. LOCATE where the causal mechanism is explicitly backed by established structural models, scientific laws, or formal logic, proving the intervention. Map the connection to the external anchor in reasoning_trace before extracting.",
                    "inverse_evidence": False,
                    "aggregation_mode": "ALL_MUST_COMPLY"
                }]
            }
        ]
    }

    for block in data.get("prompt_blocks", []):
        if block.get("id") == "blk_c5804a9143c34cb1":
            for i in range(5):
                block["scales"][i]["claims"] = causal_claims[i]
            break

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("Successfully deep-hardened blk_c5804a9143c34cb1")

if __name__ == "__main__":
    harden_v3_causal()
