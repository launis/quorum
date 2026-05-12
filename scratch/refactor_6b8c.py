import json
import secrets

FILE_PATH = "backend_v2/seed/seed_data.json"

def main():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    found = False
    for section_key, item_list in data.items():
        if not isinstance(item_list, list):
            continue
        for block in item_list:
            if isinstance(block, dict) and block.get("id") == "blk_6b8c766185294f7e":
                found = True
            
                # 1. Update Matrix-level AI Description (Hybrid Prompting & DARPA XAI)
                block["ai_description"] = (
                    "<system_directive>\n"
                    "<objective>Evaluate the Explainable Artificial Intelligence (XAI) transparency, traceability, and logical coherence of the final synthesized recommendation.</objective>\n"
                    "<epistemic_anchor>DARPA XAI Program (2017). The synthesis must be perfectly transparent and answer 'Why did you do that?' and 'Why not something else?'. It must be free from 'black-box' hallucinations. Every conclusion must be explicitly linked to verifiable evidence from the constituent agents. Unresolved contradictions or subjective probabilistic leaps constitute severe XAI failures.</epistemic_anchor>\n"
                    "<rules>\n"
                    "<rule>Enforce the Null Hypothesis: Assume the synthesis is an unsubstantiated hallucination (Score 1) until explicitly forced Chain-of-Thought (CoT) and verifiable source anchoring demonstrate otherwise.</rule>\n"
                    "</rules>\n"
                    "</system_directive>"
                )
                
                # 2. Refactor Scales to enforce the "Rule of 3" and TDA mandates
                block["scales"] = [
                    {
                        "score": 1,
                        "name": {"default_locale": "fi", "translations": {"fi": "Erittäin Epävarma (0%)", "en": "Highly Uncertain (0%)"}},
                        "ai_label": "CATASTROPHIC FAILURE - UNRESOLVABLE CONTRADICTIONS AND HUBRIS",
                        "claims": [
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen ristiriita agenttien välillä.", "en": "Complete contradiction among agents."}},
                                "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the constituent agents provide fundamentally contradictory analyses that are left completely unresolved.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the synthesis includes fundamentally contradictory statements (e.g., lexical markers of conflict like 'however', 'but', 'contradicts' in the native language) that are left completely unresolved. Document this logical void in reasoning_trace before extracting the exact_quote.",
                                    "inverse_evidence": True,
                                    "aggregation_mode": "EXISTS"
                                }]
                            },
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Faktojen puuttuminen ja subjektiivinen hallusinaatio.", "en": "Absence of facts and subjective hallucination."}},
                                "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where definitive conclusions are drawn using probabilistic assumptions presented as absolute truths.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where definitive conclusions are drawn using probabilistic assumptions or subjective views presented as absolute truths (look for markers like 'probably', 'I think', 'maybe' masked as facts in the native language). Map the unverified assumption in reasoning_trace before quoting the exact_quote.",
                                    "inverse_evidence": True,
                                    "aggregation_mode": "EXISTS"
                                }]
                            },
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Mustan laatikon päättely (Black Box).", "en": "Black box reasoning."}},
                                "ai_description": "CRITICAL DIRECTIVE: IDENTIFY where the AI provides a final decision but explicitly refuses or fails to explain 'Why did you do that?', operating as a black box.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY where the synthesis provides a final decision but explicitly uses black-box reasoning, making sudden inductive leaps without prior premises (look for sudden conclusions like 'therefore', 'so' without supporting facts in the native language). Document this XAI hubris in reasoning_trace before extracting the exact_quote.",
                                    "inverse_evidence": True,
                                    "aggregation_mode": "EXISTS"
                                }]
                            }
                        ]
                    },
                    {
                        "score": 2,
                        "name": {"default_locale": "fi", "translations": {"fi": "Keskivarma (50%)", "en": "Moderately Certain (50%)"}},
                        "ai_label": "MAJOR DISCREPANCY - PARTIAL CONSENSUS ONLY",
                        "claims": [
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Osittainen konsensus.", "en": "Partial consensus."}},
                                "ai_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of a partial consensus among agents, even if some minor ambiguities remain.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: IDENTIFY the baseline presence of a partial consensus among agents, where they agree on the main points (look for markers like 'mostly agree', 'general consensus', 'aligns' in the native language), even if some minor ambiguities remain. Document the partial alignment in reasoning_trace before extracting the exact_quote.",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY"
                                }]
                            },
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Käsittelemättömät vastaväitteet.", "en": "Unaddressed counterarguments."}},
                                "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where the synthesis presents a conclusion but actively ignores or dismisses alternative hypotheses.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where the synthesis presents a conclusion but actively ignores or dismisses alternative hypotheses without evidence (failing the DARPA XAI 'Why not something else?' test). Look for dismissive markers like 'regardless', 'anyway' in the native language. Document this one-sidedness in reasoning_trace before extracting the exact_quote.",
                                    "inverse_evidence": True,
                                    "aggregation_mode": "EXISTS"
                                }]
                            },
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Fragmentoitu todistusaineisto.", "en": "Fragmented evidence."}},
                                "ai_description": "CRITICAL DIRECTIVE: EXTRACT an instance where a conclusion relies on fragmented or isolated quotes, ignoring the broader context.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT an instance where a conclusion relies on fragmented or isolated quotes, presenting them out of context to force a narrative (look for abruptly inserted quotes without transition in the native language). Map the fragmented logic in reasoning_trace before quoting the exact_quote.",
                                    "inverse_evidence": True,
                                    "aggregation_mode": "EXISTS"
                                }]
                            }
                        ]
                    },
                    {
                        "score": 3,
                        "name": {"default_locale": "fi", "translations": {"fi": "Täysi Varmuus (100%)", "en": "Complete Certainty (100%)"}},
                        "ai_label": "LOGICAL PERFECTION - EXPLICIT FRICTION AND ANCHORING",
                        "claims": [
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Täydellinen yksimielisyys.", "en": "Complete unanimity."}},
                                "ai_description": "CRITICAL DIRECTIVE: LOCATE an instance where all contributing agents support the exact same synthesized outcome with absolute, verifiable consensus.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: LOCATE an instance where all contributing agents support the exact same synthesized outcome with absolute, verifiable consensus (look for markers like 'unanimously', 'completely agree', 'all evidence points to' in the native language). Document this perfect alignment in reasoning_trace before extracting the exact_quote.",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY"
                                }]
                            },
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Eksplisiittinen kognitiivinen kitka (Deep Explanation).", "en": "Explicit cognitive friction / Deep Explanation."}},
                                "ai_description": "CRITICAL DIRECTIVE: FIND evidence that the report explicitly documents the 'how' and 'why' of the synthesized conclusion, demonstrating Deep Explanation.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: FIND evidence that the report explicitly documents the 'how' and 'why' of the synthesized conclusion, fulfilling the DARPA XAI 'Why did you do that?' requirement (look for logical connectors like 'because', 'due to the fact that', 'this implies' in the native language). Document the step-by-step logic in reasoning_trace before extracting the exact_quote.",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY"
                                }]
                            },
                            {
                                "label": {"default_locale": "fi", "translations": {"fi": "Ehdoton lähdeankkurointi.", "en": "Absolute source anchoring."}},
                                "ai_description": "CRITICAL DIRECTIVE: EXTRACT a section where the final logical synthesis is flawlessly and explicitly tethered to external, verifiable references or source data.",
                                "tda_assertions": [{
                                    "tda_id": f"tda_{secrets.token_hex(8)}",
                                    "ai_rule_description": "CRITICAL DIRECTIVE: EXTRACT a section where the final logical synthesis is flawlessly and explicitly tethered to external, verifiable references or source data, ensuring zero-trust compliance (look for citation markers like 'according to', 'as seen in', 'referenced in' in the native language). Document the exact source anchor in reasoning_trace before quoting the exact_quote.",
                                    "inverse_evidence": False,
                                    "aggregation_mode": "ALL_MUST_COMPLY"
                                }]
                            }
                        ]
                    }
                ]
                break

    if found:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Successfully refactored blk_6b8c766185294f7e with DARPA XAI anchor and TDA mandates.")
    else:
        print("Error: Block not found.")

if __name__ == "__main__":
    main()
