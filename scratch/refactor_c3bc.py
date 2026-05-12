import json
import uuid

def generate_tda_id():
    return f"tda_{uuid.uuid4().hex[:16]}"

FILE_PATH = "backend_v2/seed/seed_data.json"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_c3bc5f3eb8e74110":
        block["ai_description"] = """<system_directive>
ROLE: CAUSAL AUDITOR / ANTAGONISTIC PROSECUTOR (ZERO-TRUST).
TASK: Scrutinize the user's claimed causal influence over the AI's output using Judea Pearl's framework of causal inference.
MANDATE: Assume any claimed causal link is a post-hoc fallacy, that the user is intellectually lazy, and that any success was stochastic. You must actively search for post-hoc rationalizations, unaddressed counterfactuals, and claims presented as absolute facts without proof. Do NOT give the benefit of the doubt. True causal integrity requires documented pre-planning (Cognitive Friction), active falsification of alternatives, and explicit source anchoring.
<epistemic_anchor>
Anchored in Judea Pearl's Causal Inference and Abductive Reasoning principles. Strict enforcement against 'post hoc ergo propter hoc' fallacies, mandating counterfactual testing and explicit System 2 cognitive friction for any claims of causal direction.
</epistemic_anchor>
</system_directive>"""

        block["scales"] = [
            {
                "score": 1,
                "name": {
                    "default_locale": "fi",
                    "translations": { "fi": "Keksitty (Post-Hoc)", "en": "Fabricated (Post-Hoc)" }
                },
                "ai_label": "CATASTROPHIC FAILURE - POST-HOC FALLACY AND HUBRIS",
                "claims": [
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Käyttäjä selittää onnistunutta tulosta vasta jälkikäteen.", "en": "The user explains the successful result only in retrospect." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Identify the presence of a 'post hoc ergo propter hoc' fallacy. Look for instances where the user claims authorship of a strategy only after observing the outcome.",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for lexical markers of retrospective claiming such as 'as I intended', 'this shows my strategy', or 'exactly what I planned' (in the native language) that appear ONLY after the AI generated the output. Locate a sentence where the user claims causal influence without any prior documented instruction. Document the post-hoc rationalization step-by-step before extracting the exact_quote.",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    },
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Ei näyttöä etukäteen asetetuista tavoitteista.", "en": "No evidence of goals set in advance." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Identify the complete absence of pre-meditated intent. The user acted as a passive passenger.",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for conversational patterns indicating passive acceptance, such as 'continue', 'good', or generic prompts lacking specific strategic parameters (in the native language). Locate an instance where the AI generates a complex outcome from a minimal or non-directive prompt. Document the lack of upfront cognitive friction step-by-step before extracting the exact_quote.",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    },
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Olettamuksia esitetään absoluuttisina faktoina ilman todisteita.", "en": "Assumptions are presented as absolute facts without evidence." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Identify epistemic hubris where the user or AI presents unverified causal links as undeniable facts.",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for lexical markers of unwarranted certainty such as 'obviously caused by', 'proof that', or 'undeniably' (in the native language). Locate a specific sentence asserting a direct cause-and-effect relationship without citing external grounding, testing counterfactuals, or providing a logical mechanism. Deconstruct the unverified claim step-by-step before extracting the exact_quote.",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    }
                ]
            },
            {
                "score": 2,
                "name": {
                    "default_locale": "fi",
                    "translations": { "fi": "Epävarma (Uncertain)", "en": "Uncertain" }
                },
                "ai_label": "DEFICIENT - UNVERIFIED CORRELATION",
                "claims": [
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Kausaalisuhdetta on vaikea todentaa aineistosta.", "en": "It is difficult to verify the causal relationship from the material." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Identify ambiguity in causation. A correlation exists, but direct proof of the user driving the process is weak.",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for lexical markers of vague guidance such as 'make it better', 'improve this', or 'like this' (in the native language). Locate a sentence where the instruction is too broad to definitively link to the specific structural improvements in the final output. Document the verification gap step-by-step before extracting the exact_quote.",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    },
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Ei voida poissulkea, että tulos oli sattumaa.", "en": "It cannot be excluded that the result was a coincidence." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Identify instances failing to disprove the null hypothesis (that the AI's stochastic generation created the value, not the user).",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for instances where the system's output introduces novel, highly valuable concepts that were never explicitly requested or hinted at in the user's prompt. Locate a sentence where the system provides value independently of the prompt's constraints. Map the stochastic value generation step-by-step before extracting the exact_quote.",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    },
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Vaihtoehtoisia selitysmalleja ei ole tutkittu.", "en": "Alternative explanatory models have not been investigated." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Identify a failure to test counterfactuals or alternative paths (One-sided argument).",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for a linear progression of ideas without any instances of the user asking 'what if we did the opposite?' or 'could this fail?' (in the native language). Locate a major decision point where the user accepts the first proposed solution without systemic questioning or alternative testing. Document the absence of abductive reasoning step-by-step before extracting the exact_quote.",
                                "inverse_evidence": True,
                                "aggregation_mode": "EXISTS"
                            }
                        ]
                    }
                ]
            },
            {
                "score": 3,
                "name": {
                    "default_locale": "fi",
                    "translations": { "fi": "Aito (Genuine)", "en": "Genuine" }
                },
                "ai_label": "THEORETICAL PERFECTION - PROVABLE CAUSATION WITH EXPLICIT FRICTION",
                "claims": [
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Käyttäjä on todistetusti visioinut ratkaisun ja kognitiivinen kitka on kirjoitettu auki.", "en": "The user has verifiably envisioned the solution and cognitive friction is explicitly articulated." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Verify the presence of explicit, pre-meditated intent and documented System 2 cognitive friction (the 'how' and 'why').",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for lexical markers of forward-planning such as 'my hypothesis is', 'the goal is to establish', or 'we must first define' (in the native language) occurring BEFORE the final output. Locate a specific sentence where the user articulates a clear structural boundary, strategic constraint, or reasoning chain prior to execution. Map the cognitive friction step-by-step before extracting the exact_quote.",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY"
                            }
                        ]
                    },
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Vastaväitteet ja vaihtoehtoiset mallit on kumottu järjestelmällisesti.", "en": "Counterarguments and alternative models have been systematically refuted." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Verify that the user acted as an antagonistic prosecutor, actively testing counterfactuals to prove the causal chain's robustness.",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for lexical markers of abductive reasoning such as 'on the other hand', 'what if we assume', or 'to disprove this' (in the native language). Locate a sentence where the user or system explicitly explores a counterfactual scenario, tests a competing hypothesis, or dismantles a potential failure mode. Document the falsification process step-by-step before extracting the exact_quote.",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY"
                            }
                        ]
                    },
                    {
                        "label": {
                            "default_locale": "fi",
                            "translations": { "fi": "Syysuhde on ankkuroitu todennettaviin ulkoisiin asiantuntijalähteisiin.", "en": "The causal relationship is anchored to verifiable external expert sources." }
                        },
                        "ai_description": "CRITICAL DIRECTIVE: Verify mandatory source anchoring. The causal logic must be explicitly tethered to external, recognized frameworks.",
                        "tda_assertions": [
                            {
                                "tda_id": generate_tda_id(),
                                "ai_rule_description": "CRITICAL DIRECTIVE: Look for lexical markers of academic or professional grounding such as 'according to', 'based on the framework of', or specific methodology names. Locate a sentence where the reasoning is explicitly justified by citing an external theoretical framework, empirical study, or established standard (e.g., Judea Pearl's do-calculus). Document the architectural alignment step-by-step before extracting the exact_quote.",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY"
                            }
                        ]
                    }
                ]
            }
        ]
        break

with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Successfully refactored blk_c3bc5f3eb8e74110 with Judea Pearl Causal Inference anchor and exact 3 claims per scale.")
