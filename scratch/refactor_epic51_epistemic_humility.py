import json
import uuid

def generate_tda_id():
    return "tda_" + uuid.uuid4().hex[:8]

def main():
    file_path = "backend_v2/seed/seed_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_id = "blk_22e3598e06414409"
    block_found = False

    for block in data.get("prompt_blocks", []):
        if block.get("id") == target_id:
            block_found = True
            
            # Update theory_grounding
            block["theory_grounding"] = {
                "citation_reference": "Kahneman, D. (2011). Thinking, Fast and Slow; Floridi, L. (2014). The 4th Revolution. (Epistemic limits and informational humility).",
                "source_url": "https://doi.org/10.1007/s13347-020-00404-6"
            }
            
            # Update ai_description
            block["ai_description"] = "<system_directive>\n  <epistemic_anchor>Kahneman (2011); Floridi (2014). Epistemic humility requires acknowledging cognitive limits, avoiding overconfidence, and maintaining absolute theoretical grounding.</epistemic_anchor>\n</system_directive>\nROLE: EPISTEMIC AUDITOR / ANTAGONISTIC PROSECUTOR (ZERO-TRUST).\nTASK: Evaluate the model's output for unwarranted certainty, intellectual arrogance (Hubris), and superficial performative hedging.\nNULL HYPOTHESIS: Assume the text presents subjective interpretations, hallucinations, or incomplete data as absolute truth. You must actively search for overconfidence, performative hedging, and missing counterarguments. Do NOT give the benefit of the doubt. The model must rigorously qualify its assertions. To achieve perfection, the text must proactively state its limitations (Cognitive Friction), actively challenge its own conclusions, and anchor its logic to external expert reality.\nMANDATORY DIRECTIVE: Default all boolean claim evaluations to FALSE. You must never infer, guess, or synthesize compliance. A claim can only be evaluated as TRUE if you can extract direct, undeniable semantic proof from the text. Give absolutely no benefit of the doubt. Provide step-by-step chronological reasoning in the reasoning_trace before any extraction."
            
            # Update Scales
            scales = block.get("scales", [])
            
            # Scale 1 (Score 1)
            scales[0]["claims"][0]["ai_description"] = "<system_directive>\n  <epistemic_anchor>Kahneman (2011). System 1 overconfidence.</epistemic_anchor>\n  <fatal_flaw_context>Target absolute certainty lacking qualification.</fatal_flaw_context>\n</system_directive>"
            scales[0]["claims"][0]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL DIRECTIVE: Identify an explicit sentence where the text uses absolute lexical markers (e.g., 'undeniably', 'always', 'guaranteed', 'proven') to assert a complex or subjective issue as an incontrovertible fact. Document the logical leap before extracting the exact_quote.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
            
            scales[0]["claims"][1]["ai_description"] = "<system_directive>\n  <epistemic_anchor>Kahneman (2011). Illusion of validity.</epistemic_anchor>\n  <fatal_flaw_context>Target claims of absolute exhaustiveness.</fatal_flaw_context>\n</system_directive>"
            scales[0]["claims"][1]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL DIRECTIVE: Locate a statement where the text explicitly claims complete knowledge, absolute certainty, or exhaustive coverage of the topic, leaving zero room for doubt or unknown variables. Extract the exact_quote.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
            
            scales[0]["claims"][2]["ai_description"] = "<system_directive>\n  <epistemic_anchor>Kahneman (2011). Confirmation bias and derogation of alternatives.</epistemic_anchor>\n  <fatal_flaw_context>Target aggressive dismissal of competing views.</fatal_flaw_context>\n</system_directive>"
            scales[0]["claims"][2]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL DIRECTIVE: Find an instance where the text presents a singular narrative and actively dismisses, derogates, or aggressively marginalizes any alternative viewpoints without rigorous empirical refutation. Extract the exact_quote.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
            
            # Scale 2 (Score 2)
            scales[1]["claims"][0]["ai_description"] = "<system_directive>\n  <epistemic_anchor>Floridi (2014). Performative humility masking arrogance.</epistemic_anchor>\n  <fatal_flaw_context>Target superficial hedging.</fatal_flaw_context>\n</system_directive>"
            scales[1]["claims"][0]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL DIRECTIVE: Locate an instance of superficial or 'performative' hedging (e.g., 'it may be that...', 'some might say...') that merely provides a conversational illusion of humility without actually adjusting the absolute nature of the core conclusion. Extract the exact_quote.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
            
            scales[1]["claims"][1]["ai_description"] = "<system_directive>\n  <epistemic_anchor>Floridi (2014). Superficial engagement with critique.</epistemic_anchor>\n  <fatal_flaw_context>Target rapid dismissal of constraints.</fatal_flaw_context>\n</system_directive>"
            scales[1]["claims"][1]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL DIRECTIVE: Find a sentence where the text briefly acknowledges a limitation or counter-argument, but immediately dismisses it with a superficial rationalization rather than engaging in deep, systemic friction. Extract the exact_quote.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
            
            scales[1]["claims"][2]["ai_description"] = "<system_directive>\n  <epistemic_anchor>Kahneman (2011). WYSIATI (What You See Is All There Is).</epistemic_anchor>\n  <fatal_flaw_context>Target failure to deeply explore named alternatives.</fatal_flaw_context>\n</system_directive>"
            scales[1]["claims"][2]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL DIRECTIVE: Identify a specific section where an alternative model or perspective is mentioned by name, but is then bypassed or ignored without any rigorous, step-by-step counterfactual analysis. Extract the exact_quote.",
                "inverse_evidence": True,
                "aggregation_mode": "EXISTS"
            }]
            
            # Scale 3 (Score 3)
            scales[2]["claims"][0]["ai_description"] = "CRITICAL EVALUATION DIRECTIVE: The text consistently avoids absolute terms (e.g., uses 'indicates' instead of 'proves') and maintains a measured, neutral tone throughout its central assertions."
            scales[2]["claims"][0]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL EVALUATION DIRECTIVE: The text consistently avoids absolute terms (e.g., uses 'indicates' instead of 'proves') and maintains a measured, neutral tone throughout its central assertions.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            scales[2]["claims"][1]["ai_description"] = "ENFORCEMENT RULE: The text remains passive. It does not contain any explicit self-reflection or proactive identification of its own limitations, requiring the reader to independently infer the boundaries of its validity."
            scales[2]["claims"][1]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "ENFORCEMENT RULE: The text remains passive. It does not contain any explicit self-reflection or proactive identification of its own limitations, requiring the reader to independently infer the boundaries of its validity.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            scales[2]["claims"][2]["ai_description"] = "ENFORCEMENT RULE: The text presents its information straightforwardly but fails to discuss the structural limitations, potential biases, or margin of error inherent in its primary data sources."
            scales[2]["claims"][2]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "ENFORCEMENT RULE: The text presents its information straightforwardly but fails to discuss the structural limitations, potential biases, or margin of error inherent in its primary data sources.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            # Scale 4 (Score 4)
            scales[3]["claims"][0]["ai_description"] = "CRITICAL EVALUATION DIRECTIVE: The text proactively and explicitly identifies specific, key limitations, assumptions, or methodological constraints that affect its own findings or recommendations."
            scales[3]["claims"][0]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL EVALUATION DIRECTIVE: The text proactively and explicitly identifies specific, key limitations, assumptions, or methodological constraints that affect its own findings or recommendations.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            scales[3]["claims"][1]["ai_description"] = "CRITICAL EVALUATION DIRECTIVE: The text clearly states the boundaries of its perspective, acknowledging that its conclusions are conditional, context-dependent, and not universally applicable."
            scales[3]["claims"][1]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL EVALUATION DIRECTIVE: The text clearly states the boundaries of its perspective, acknowledging that its conclusions are conditional, context-dependent, and not universally applicable.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            scales[3]["claims"][2]["ai_description"] = "ENFORCEMENT RULE: The text actively engages with at least one credible counter-hypothesis or alternative perspective, demonstrating a willingness to address external variables that could challenge its primary conclusion."
            scales[3]["claims"][2]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "ENFORCEMENT RULE: The text actively engages with at least one credible counter-hypothesis or alternative perspective, demonstrating a willingness to address external variables that could challenge its primary conclusion.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            # Scale 5 (Score 5)
            scales[4]["claims"][0]["ai_description"] = "CRITICAL EVALUATION DIRECTIVE: The text comprehensively lists its own limitations, data gaps, and foundational assumptions without being prompted, treating its own reasoning as an object of critical scrutiny."
            scales[4]["claims"][0]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL EVALUATION DIRECTIVE: The text comprehensively lists its own limitations, data gaps, and foundational assumptions without being prompted, treating its own reasoning as an object of critical scrutiny.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            scales[4]["claims"][1]["ai_description"] = "CRITICAL EVALUATION DIRECTIVE: The text proactively outlines potential risks, thoroughly and fairly dismantles counterarguments, and rigorously defines the precise statistical or logical scope of its confidence."
            scales[4]["claims"][1]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "CRITICAL EVALUATION DIRECTIVE: The text proactively outlines potential risks, thoroughly and fairly dismantles counterarguments, and rigorously defines the precise statistical or logical scope of its confidence.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            scales[4]["claims"][2]["ai_description"] = "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. The text explicitly anchors its own epistemic boundaries by citing verifiable external literature or frameworks to justify why certain variables remain unknown or uncertain."
            scales[4]["claims"][2]["tda_assertions"] = [{
                "tda_id": generate_tda_id(),
                "ai_rule_description": "ENFORCEMENT RULE: MANDATORY SOURCE ANCHORING. The text explicitly anchors its own epistemic boundaries by citing verifiable external literature or frameworks to justify why certain variables remain unknown or uncertain.",
                "inverse_evidence": False,
                "aggregation_mode": "ALL_MUST_COMPLY"
            }]
            
            # Enforce Rule of 3: truncate any remaining claims
            for scale in scales:
                del scale["claims"][3:]
            
            break
            
    if not block_found:
        print("Error: Target block not found!")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
        
    print("Successfully refactored blk_22e3598e06414409")

if __name__ == "__main__":
    main()
