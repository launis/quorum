import json


def apply_mece_to_matrix(block_id, consolidations):
    seed_path = "backend_v2/seed/seed_data.json"

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    for block in data.get("prompt_blocks", []):
        if block.get("id") == block_id:
            for scale_idx, new_claims in consolidations.items():
                block["scales"][scale_idx]["claims"] = new_claims
            break

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully applied MECE rule of 3 to {block_id}")

# ---------------- Kahneman Consolidation (blk_109dab5b6b3f403a) ----------------
# Level 1: Currently 4. Merge (2) WYSIATI and (3) Biases.
kahneman_consolidations = {
    0: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Reaktiivinen nopeus", "en": "Reactive Speed"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of unexamined System 1 thinking. The output is instantaneous, automatic, and lacks analytical depth.",
            "tda_assertions": [{
                "tda_id": "tda_k1_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of unexamined System 1 thinking. Look for instantaneous or automatic conclusions without analytical depth. Document the lack of self-correction in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Heuristiikat ja vinoumat", "en": "Heuristics and Biases"}
            },
            "ai_description": "CRITICAL DIRECTIVE: EXTRACT evidence of cognitive biases or mental shortcuts.",
            "tda_assertions": [{
                "tda_id": "tda_k1_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT evidence of cognitive biases (confirmation bias, halo effect) or 'What You See Is All There Is' (WYSIATI) heuristic leaps. Document the detected bias in reasoning_trace before extracting the biased statement.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Hybris", "en": "Hubris"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY subjective views or initial reactions presented as absolute truth.",
            "tda_assertions": [{
                "tda_id": "tda_k1_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY subjective views, initial reactions, or lazy extrapolations presented as absolute truth without epistemological humility. Document the hubris in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    1: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Pinnallinen hidastuminen", "en": "Superficial Deceleration"}
            },
            "ai_description": "CRITICAL DIRECTIVE: FIND a weak or performative attempt to engage System 2 by questioning intuition.",
            "tda_assertions": [{
                "tda_id": "tda_k2_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: FIND a weak, perhaps merely performative, attempt to engage System 2. The author questions intuition but fails to fully override System 1 defaults, resulting in superficial analysis. Map the incomplete transition in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Yksipuolinen kehystys", "en": "One-Sided Framing"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY a one-sided argument that fails to systematically address alternative hypotheses.",
            "tda_assertions": [{
                "tda_id": "tda_k2_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY a one-sided argument that fails to systematically address alternative hypotheses. Lack of epistemological humility prevents progression. Document the missing alternatives in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Sivuutetut vastaväitteet", "en": "Ignored Rebuttals"}
            },
            "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the text actively ignores or dismisses rebuttals.",
            "tda_assertions": [{
                "tda_id": "tda_k2_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the text does not anticipate and engage with opposing arguments (rebuttals). Explain how counterarguments were ignored in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    2: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Systemaattinen purkaminen", "en": "Systematic Deconstruction"}
            },
            "ai_description": "CRITICAL DIRECTIVE: LOCATE where the response systematically deconstructs the problem, explicitly overriding initial intuitions.",
            "tda_assertions": [{
                "tda_id": "tda_k3_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE where the response systematically deconstructs the problem, consciously overriding initial intuitions and evaluating evidence with strict logical rigor. Map the cognitive friction ('how' and 'why') in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Dialektinen synteesi", "en": "Dialectical Synthesis"}
            },
            "ai_description": "CRITICAL DIRECTIVE: FIND evidence of the author acting as a prosecutor against their own ideas and thoughtfully engaging rebuttals.",
            "tda_assertions": [{
                "tda_id": "tda_k3_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT thoughtful identification of and response to rebuttals. The author acts as an antagonistic prosecutor against their own ideas, dismantling biases and engaging opposing arguments. Explain the dialectical synthesis in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Episteeminen ankkurointi", "en": "Epistemic Anchoring"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the structured logic is explicitly tethered to external expert references.",
            "tda_assertions": [{
                "tda_id": "tda_k3_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where the structured logic is explicitly tethered to external, verifiable expert references or data. True System 2 processing does not operate in a vacuum. Document the external anchor in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        }
    ]
}

# ---------------- Goodhart Consolidation (blk_53f32679aa514fcb) ----------------
goodhart_consolidations = {
    0: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Passiivinen hyväksyntä", "en": "Passive Acceptance"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY extreme goal-hacking where the user accepts the first response without structural challenge.",
            "tda_assertions": [{
                "tda_id": "tda_g1_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY if the user accepts the first response without any structural challenge, allowing the interaction to be entirely driven by the AI's assumptions. Document the passive role in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Rakenteellinen sokeus", "en": "Structural Blindness"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY if the user demonstrates zero critical oversight over logical errors.",
            "tda_assertions": [{
                "tda_id": "tda_g1_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY if the user demonstrates zero critical oversight, letting hallucinated or flawed logic pass through completely unchallenged. Document the logical oversight in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Auktoriteettiharha", "en": "Authority Bias"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY if the user treats the AI's probabilistic generation as an infallible source of truth.",
            "tda_assertions": [{
                "tda_id": "tda_g1_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY if the user treats the AI's probabilistic generation as an infallible source of truth without demanding evidence or source criticism. Document the hubris in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    # Score 2 is already 3 claims
    2: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Reaktiivinen osallistuminen", "en": "Reactive Engagement"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user actively engages with the output but only targets symptoms rather than root causes.",
            "tda_assertions": [{
                "tda_id": "tda_g3_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where the user addresses the outputs (symptoms) and accepts minor tweaks, leaving the underlying generative logic or prompt architecture (root causes) unchallenged. Map the engagement in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Mittarifiksaatio", "en": "Metric Fixation"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user accepts stylistic or minor tweaks while leaving the substantive core argument unchallenged.",
            "tda_assertions": [{
                "tda_id": "tda_g3_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where the user accepts stylistic or minor tweaks while leaving the substantive core argument unchallenged. Explain the superficial correction in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Yksipuolinen suorittaminen", "en": "One-Sided Execution"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY one-sided execution without demand for alternative models.",
            "tda_assertions": [{
                "tda_id": "tda_g3_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY one-sided execution where the user does not demand alternative models or explore counterarguments (rebuttals). Explain the missing alternatives in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    3: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Strateginen navigointi", "en": "Strategic Navigation"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user actively prevents Goodhart's Law by questioning the reliability of the metric and relating it to the ultimate goal.",
            "tda_assertions": [{
                "tda_id": "tda_g4_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: The user successfully navigates the tension between the proxy metric and the true overarching goal, preventing Goodhart's Law. Map this explicit logic in reasoning_trace before extracting the insight.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Rajaehtojen käsittely", "en": "Boundary Integration"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user forces the AI to acknowledge foundational premises and edge cases.",
            "tda_assertions": [{
                "tda_id": "tda_g4_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: The user actively identifies and integrates boundary conditions, underlying assumptions, and exceptions into the analysis. Map this explicit logic in reasoning_trace before extracting the insight.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Epävarmuuden tunnistaminen", "en": "Identification of Uncertainty"}
            },
            "ai_description": "ENFORCEMENT RULE: EPISTEMOLOGICAL HUMILITY REQUIRED. Verify that the user demands acknowledgment of uncertainties.",
            "tda_assertions": [{
                "tda_id": "tda_g4_3",
                "ai_rule_description": "ENFORCEMENT RULE: EPISTEMOLOGICAL HUMILITY REQUIRED. Verify that the user demands acknowledgment of uncertainties. Map this explicit logic in reasoning_trace before extracting the insight.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        }
    ],
    4: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Antagonistinen ohjaus", "en": "Antagonistic Driving"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user acts as an antagonistic prosecutor, challenging the AI's logic and restructuring the interaction.",
            "tda_assertions": [{
                "tda_id": "tda_g5_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: ABSOLUTE ZERO-TRUST. The user acts as an antagonistic prosecutor, dismantling the AI's structural reasoning, demanding corrections, and delegating only execution while maintaining cognitive control. Map this explicit logic in reasoning_trace before extracting the insight.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Kognitiivisen kitkan dokumentointi", "en": "Documentation of Cognitive Friction"}
            },
            "ai_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. The interaction MUST explicitly articulate 'how' and 'why' the user is challenging the AI.",
            "tda_assertions": [{
                "tda_id": "tda_g5_2",
                "ai_rule_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. The interaction MUST explicitly articulate 'how' and 'why' the user is challenging the AI. It must show the slow, deliberate work of reasoning. Map this explicit logic in reasoning_trace before extracting the insight.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Objektiivinen ankkurointi", "en": "Objective Anchoring"}
            },
            "ai_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. The user must demand external grounding and expert verification.",
            "tda_assertions": [{
                "tda_id": "tda_g5_3",
                "ai_rule_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. The user must demand external grounding and concrete expert verification. A perfect interaction without demonstrable anchoring in external reality is suspicious. Map this explicit logic in reasoning_trace before extracting the insight.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        }
    ]
}

# ---------------- Archival Compliance Audit Consolidation (blk_fb15f8dcf23f4865) ----------------
archival_consolidations = {
    0: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Ohjeiden täydellinen sivuuttaminen", "en": "Complete disregard of instructions"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY blatant fabrication where the output contradicts foundational constraints.",
            "tda_assertions": [{
                "tda_id": "tda_ar1_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY blatant fabrication where the output contradicts foundational constraints or explicitly disregards provided instructions. Look for lexical markers of autonomous hallucination (e.g., 'I created', 'Instead of'). Document the deviation in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Absoluuttinen varmuus ilman lähdeviitettä", "en": "Absolute certainty without provenance"}
            },
            "ai_description": "CRITICAL DIRECTIVE: EXTRACT an assertion presented as absolute truth without verifiable provenance.",
            "tda_assertions": [{
                "tda_id": "tda_ar1_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an assertion presented as absolute truth without verifiable provenance or structural anchor (ARMA Integrity violation). Look for hubristic markers like 'it is guaranteed' or 'always'. Document the missing provenance in reasoning_trace before quoting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Yksityisyyden tai suojauksen vaarantaminen", "en": "Compromising privacy or protection"}
            },
            "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where sensitive or restricted information is exposed or mishandled.",
            "tda_assertions": [{
                "tda_id": "tda_ar1_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where sensitive, restricted, or private information is mishandled, explicitly violating the ARMA Protection principle. Document the operational breach in reasoning_trace before extracting the violating text.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    1: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Irralliset käytännöt ilman rakennetta", "en": "Isolated practices without structure"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of isolated compliance without overarching structural integrity.",
            "tda_assertions": [{
                "tda_id": "tda_ar2_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of isolated compliance where scattered correct elements exist, but lack overarching structural integrity (ARMA Accountability). Document the fragmented adherence in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Ohjeiden ohittaminen mukavuussyistä", "en": "Bypassing instructions for convenience"}
            },
            "ai_description": "CRITICAL DIRECTIVE: EXTRACT evidence where a required standard operating procedure is explicitly bypassed.",
            "tda_assertions": [{
                "tda_id": "tda_ar2_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT evidence where a required standard operating procedure or compliance rule is explicitly bypassed for convenience. Look for dismissive markers (e.g., 'we can skip', 'not strictly necessary'). Document the bypassed rule in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Yksipuolinen ja sokea suorittaminen", "en": "One-sided and blind execution"}
            },
            "ai_description": "CRITICAL DIRECTIVE: LOCATE an execution that blindly follows one rule while completely ignoring conflicting constraints.",
            "tda_assertions": [{
                "tda_id": "tda_ar2_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an execution that blindly follows a single rule while actively ignoring known conflicting constraints or alternative models. Map the ignored constraints in reasoning_trace before quoting the tunnel-visioned execution.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    2: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Mekaaninen perusprosessin noudattaminen", "en": "Mechanical adherence to basic process"}
            },
            "ai_description": "CRITICAL DIRECTIVE: FIND evidence that the basic compliance process is followed in a mechanical, literal manner.",
            "tda_assertions": [{
                "tda_id": "tda_ar3_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that the basic compliance process is followed in a mechanical, literal manner without strategic synthesis. Document the literal interpretation in reasoning_trace before extracting the compliant text.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Haasteiden ja riskien sivuuttaminen", "en": "Ignoring challenges and risks"}
            },
            "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the author avoids acknowledging operational risks or compliance ambiguities.",
            "tda_assertions": [{
                "tda_id": "tda_ar3_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the author avoids acknowledging operational risks, compliance ambiguities, or necessary rebuttals. Look for sweeping generic statements that hide complexity. Explain the hidden risk in reasoning_trace before extracting.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Lähdekritiikin puute", "en": "Lack of source criticism"}
            },
            "ai_description": "CRITICAL DIRECTIVE: IDENTIFY a reliance on undocumented or unverified internal knowledge.",
            "tda_assertions": [{
                "tda_id": "tda_ar3_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY a reliance on undocumented or unverified internal knowledge rather than established external guidelines (violating ARMA Transparency). Document the missing verifiability in reasoning_trace before quoting the unsupported claim.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
        }
    ],
    3: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Jäsennelty ja todistettava ohjausmalli", "en": "Structured and verifiable steering model"}
            },
            "ai_description": "CRITICAL DIRECTIVE: LOCATE explicit adherence to structured directives where the chain of reasoning is clearly verifiable.",
            "tda_assertions": [{
                "tda_id": "tda_ar4_1",
                "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE explicit adherence to structured directives where the chain of reasoning is clearly verifiable and transparent. Look for lexical markers like 'according to the guidelines' or 'based on the procedure'. Document the structural alignment in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Rajoitteiden ja reunaehtojen tunnistaminen", "en": "Identification of constraints and boundary conditions"}
            },
            "ai_description": "CRITICAL DIRECTIVE: FIND epistemological humility where limitations and boundary conditions are explicitly stated.",
            "tda_assertions": [{
                "tda_id": "tda_ar4_2",
                "ai_rule_description": "CRITICAL DIRECTIVE: FIND epistemological humility where limitations, operational constraints, and boundary conditions are explicitly stated. Look for scoping markers like 'within the scope of' or 'subject to'. Document the bounded context in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Vastaväitteiden ennakoiva käsittely", "en": "Proactive handling of counterarguments"}
            },
            "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where potential compliance conflicts are systematically addressed.",
            "tda_assertions": [{
                "tda_id": "tda_ar4_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where potential compliance conflicts or alternative operational models are systematically addressed and resolved. Document the conflict resolution logic in reasoning_trace before quoting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        }
    ],
    4: [
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Kognitiivisen kitkan eksplisiittinen dokumentointi", "en": "Explicit documentation of cognitive friction"}
            },
            "ai_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. FIND evidence of 'System 2' deliberation detailing why specific compliance tradeoffs were made.",
            "tda_assertions": [{
                "tda_id": "tda_ar5_1",
                "ai_rule_description": "ENFORCEMENT RULE: SYSTEM 2 REQUIREMENT. FIND evidence of 'System 2' deliberation detailing exactly why specific compliance tradeoffs were made. Look for complex dialectical reasoning ('we chose X over Y because'). Document the cognitive friction step-by-step in reasoning_trace before extracting.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Täydellinen ulkoinen ankkurointi", "en": "Perfect external anchoring"}
            },
            "ai_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. LOCATE where the execution is fortified by explicit backing from external expert frameworks.",
            "tda_assertions": [{
                "tda_id": "tda_ar5_2",
                "ai_rule_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. LOCATE where the execution is fortified by explicit backing from external expert frameworks (like ARMA Principles or ISO standards). Map the connection to the external anchor in reasoning_trace before extracting the definitively compliant quote.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        },
        {
            "label": {
                "default_locale": "fi",
                "translations": {"fi": "Tavoitteiden ja riskien mestarillinen tasapainottelu", "en": "Masterful balancing of goals and risks"}
            },
            "ai_description": "CRITICAL DIRECTIVE: EXTRACT a masterfully constructed resolution that seamlessly balances strict compliance with operational goals.",
            "tda_assertions": [{
                "tda_id": "tda_ar5_3",
                "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a masterfully constructed resolution that seamlessly balances strict compliance (Integrity/Protection) with operational goals (Availability). Document the perfect equilibrium triad in reasoning_trace before extracting the definitive conclusion.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
        }
    ]
}

if __name__ == "__main__":
    apply_mece_to_matrix("blk_109dab5b6b3f403a", kahneman_consolidations)
    apply_mece_to_matrix("blk_53f32679aa514fcb", goodhart_consolidations)
    apply_mece_to_matrix("blk_fb15f8dcf23f4865", archival_consolidations)

