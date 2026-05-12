import json
import uuid

def generate_tda_id():
    return "tda_" + uuid.uuid4().hex[:16]

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

found = False
for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_ff72c2d79edb4ebf":
        found = True
        
        # 1. XML + Theory Injection (Anti-Token Bloat)
        block["ai_description"] = (
            "<system_directive>\n"
            "<objective>Evaluate the user's executive control and process ownership over the AI, distinguishing between a passive 'passenger' and a proactive 'Supreme Adjudicator'.</objective>\n"
            "<epistemic_anchor>W. Edwards Deming. 'Out of the Crisis' (Total Quality Management & PDCA Cycle). The user must act as the absolute executive authority, ensuring built-in quality control and continuous active steering (Plan-Do-Check-Act). Abdicating the 'Check' or 'Act' phases to the AI constitutes catastrophic failure. Lexical markers of success include explicit corrective commands, overriding AI choices, and demanding verifiable steps.</epistemic_anchor>\n"
            "<rules>\n"
            "<rule>Enforce the Null Hypothesis: Assume the user is a passive 'passenger' blindly accepting AI output until explicit, authoritative executive commands are demonstrated.</rule>\n"
            "</rules>\n"
            "</system_directive>"
        )
        
        # Ensure theory grounding exists
        block["theory_grounding"] = {
            "citation_reference": "Deming, W. E. (1986). Out of the Crisis. MIT Center for Advanced Engineering Study.",
            "source_url": "https://deming.org/explore/pdsa/"
        }
        
        # 2. MECE Triangulation (Exactly 3 claims per scale)
        block["scales"] = [
            {
                "score": 1,
                "name": {"default_locale": "fi", "translations": {"fi": "Täysi Matkustaja", "en": "Complete Passenger"}},
                "ai_label": "CATASTROPHIC FAILURE - TOTAL ABDICATION",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Vastuun täydellinen pakoilu.", "en": "Total abdication of responsibility"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user allows the AI to completely dictate the workflow and output without any steering.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user allows the AI to completely dictate the workflow and output without any steering. The user acts as a passive passenger. Document this total lack of executive control in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Sokea luottamus laatuun.", "en": "Blind trust in quality"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the user blindly accepts the final output without performing any verifiable quality check.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the user blindly accepts the final output without performing any verifiable quality check, violating Deming's PDCA 'Check' phase. Map the missing quality assurance in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Rakenteellisten rajoitteiden sivuuttaminen.", "en": "Ignoring structural constraints"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where foundational organizational rules or systemic constraints are completely ignored by the user.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where foundational organizational rules, prompt engineering limits, or systemic constraints are completely ignored by the user, leading to a rogue execution. Document the ignored rule in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 2,
                "name": {"default_locale": "fi", "translations": {"fi": "Reaktiivinen Seuraaja", "en": "Reactive Follower"}},
                "ai_label": "FUNDAMENTALLY FLAWED - REACTIVE ENGAGEMENT",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Viivästynyt puuttuminen.", "en": "Delayed intervention"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user only intervenes after a massive deviation has already occurred.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user only intervenes after a massive deviation has already occurred, rather than proactively steering the process. Document the delayed reaction in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Tekoälyn antamien vaihtoehtojen orja.", "en": "Slave to AI's alternatives"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the user only chooses from options provided by the AI, failing to inject their own external logic.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where the user only chooses from options provided by the AI, failing to inject their own external logic or demand a completely new approach. Document this constrained choice in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Pinnallinen hyväksyntä.", "en": "Superficial approval"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the user provides a generic 'looks good' without verifying the underlying mechanics of the solution.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where the user provides a generic 'looks good' without verifying the underlying mechanics or accuracy of the solution. Map the lack of deep inspection in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 3,
                "name": {"default_locale": "fi", "translations": {"fi": "Neutraali Osallistuja", "en": "Neutral Participant"}},
                "ai_label": "NEUTRAL - BASIC OVERSIGHT",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Perustason korjausliikkeet.", "en": "Baseline corrective actions"}},
                        "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of explicit commands that correct the AI's trajectory when it errs.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of explicit commands that correct the AI's trajectory when it errs. Document the explicit correction in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Puutteellinen ennakointi.", "en": "Lack of anticipation"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user guides the current step but fails to anticipate and plan for the next logical steps.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user adequately guides the current step but fails to set up constraints or anticipate risks for the subsequent steps. Document the missing foresight in reasoning_trace before extracting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Sääntöjen osittainen soveltaminen.", "en": "Partial rule application"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where some constraints are enforced but others are forgotten or allowed to slip.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where some operational constraints are enforced but others are forgotten or implicitly allowed to slip. Map the forgotten constraint in reasoning_trace before quoting.",
                            "inverse_evidence": True,
                            "aggregation_mode": "EXISTS"
                        }]
                    }
                ]
            },
            {
                "score": 4,
                "name": {"default_locale": "fi", "translations": {"fi": "Ohjaaja", "en": "Director"}},
                "ai_label": "LOGICALLY SOUND - PROACTIVE COMMAND",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Eksplisiittinen reitinmääritys.", "en": "Explicit pathfinding"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user proactively sets the analytical path, explicitly defining what the AI should NOT do.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the user proactively sets the analytical path, explicitly defining both the goal and negative constraints (what the AI should NOT do). Document the explicit boundary setting in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Välietappien vaatiminen.", "en": "Demanding milestones"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND evidence that the user forces the AI to output intermediate reasoning steps before reaching a conclusion.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that the user forces the AI to output intermediate reasoning steps or milestones before accepting a final conclusion. Document this forced 'Chain of Thought' control in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Itsenäisen laadunvarmistuksen pakottaminen.", "en": "Forcing autonomous QA"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT a command where the user forces the AI to review its own output against specific criteria.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a command where the user explicitly forces the AI to review or critique its own output against specific external criteria before proceeding. Document the QA loop in reasoning_trace before quoting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    }
                ]
            },
            {
                "score": 5,
                "name": {"default_locale": "fi", "translations": {"fi": "Ylituomari", "en": "Supreme Adjudicator"}},
                "ai_label": "THEORETICALLY PERFECT - MASTERFUL EXECUTIVE CONTROL",
                "claims": [
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Ehdottoman auktoriteetin käyttö.", "en": "Exercise of absolute authority"}},
                        "ai_description": "CRITICAL DIRECTIVE: FIND a masterful execution where the user decisively overrides the AI's logic with superior, externally verified reasoning.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: FIND a masterful execution where the user decisively overrides the AI's logic with superior, externally verified reasoning, asserting absolute executive control. Document the authoritative override in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "PDCA-syklin täydellinen hallinta.", "en": "Perfect mastery of PDCA cycle"}},
                        "ai_description": "CRITICAL DIRECTIVE: LOCATE an explicit multi-turn sequence where Plan, Do, Check, and Act phases are strictly governed by the user.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an explicit multi-turn sequence where the Deming PDCA (Plan, Do, Check, Act) phases are strictly governed by the user, leaving the AI as a pure processing engine. Map the full cycle in reasoning_trace before extracting.",
                            "inverse_evidence": False,
                            "aggregation_mode": "ALL_MUST_COMPLY"
                        }]
                    },
                    {
                        "label": {"default_locale": "fi", "translations": {"fi": "Arkkitehtuurin tason järjestelmällisyys.", "en": "Architectural-level systemic oversight"}},
                        "ai_description": "CRITICAL DIRECTIVE: EXTRACT definitive evidence of 'System 2' oversight where the user enforces systemic architectural rules flawlessly.",
                        "tda_assertions": [{
                            "tda_id": generate_tda_id(),
                            "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT definitive evidence of 'System 2' oversight where the user enforces systemic architectural rules flawlessly, preventing any hallucination or drift. Document the systemic enforcement in reasoning_trace before extracting.",
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
    print("Successfully refactored blk_ff72c2d79edb4ebf with TDA mandates.")
else:
    print("Error: Block blk_ff72c2d79edb4ebf not found!")
