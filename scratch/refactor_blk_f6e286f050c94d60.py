import json
import secrets

def generate_tda_id():
    return "tda_" + secrets.token_hex(8)

file_path = "backend_v2/seed/seed_data.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_f6e286f050c94d60":
        block["ai_description"] = "<system_directive>\n<role>XAI AUDITOR / ANTAGONISTIC PROSECUTOR (ZERO-TRUST)</role>\n<task>Evaluate the system's capacity to generate a fully intelligible and transparent report for the end-user using Lipton's framework of model interpretability.</task>\n<mandate>Assume the explanation is a post-hoc rationalization or a black box. Do NOT give the benefit of the doubt. You must actively search for opaque logic, missing variables, and unaddressed counterfactuals. True transparency requires explicit tracing from inputs to conclusions (Decomposability), documented System 2 friction, and dialectical synthesis.</mandate>\n<role_enforcement>Strictly adhere to 'user:' and 'ai:' prefixes where applicable. Differentiate between user input and AI generative reasoning.</role_enforcement>\n<banned_concepts>Do not evaluate subjective terms like 'clear', 'understandable', or 'good'. Use structural thresholds (e.g., presence of specific variable names, numerical weights, multi-step sequences).</banned_concepts>\n<epistemic_anchor>Anchored in Zachary C. Lipton's 'The Mythos of Model Interpretability' (2018). Strict enforcement of Transparency (Simulatability, Decomposability, Algorithmic Transparency) versus mere Post-hoc Explanations, requiring explicit tracing, boundary definition, and counterfactual refutation.</epistemic_anchor>\n</system_directive>"
        
        block["theory_grounding"] = {
            "citation_reference": "Lipton, Zachary C. (2018). The Mythos of Model Interpretability. Communications of the ACM, 61(10), 36-43.",
            "source_url": "https://arxiv.org/abs/1606.03490"
        }

        scales = block["scales"]
        
        # Scale 1
        scales[0]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. If role prefixes exist, focus on the 'ai:' block. BANNED LOGIC: Do not evaluate 'opaque' subjectively. STEP 1 (Lexical Anchor): Find a definitive conclusion or final answer (e.g. 'Therefore', 'The result is', 'In conclusion'). STEP 2 (Bounding Box): Scan the preceding text. If the conclusion is presented WITHOUT any preceding step-by-step mathematical, logical, or variable-level decomposition -> ACCEPT (flaw proven). If steps exist -> REJECT. ENFORCEMENT RULE: Document the missing decomposability in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[0]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from user input fields. BANNED LOGIC: Do not accept appeals to authority. STEP 1 (Lexical Anchor): Find heuristic or dismissive phrases (e.g. 'typically', 'usually', 'it is known', 'obviously'). STEP 2 (Bounding Box): Scan the sentence. If the phrase is used to justify a decision WITHOUT citing a specific dataset, numerical weight, or verifiable rule -> ACCEPT (heuristic flaw proven). If a specific source is cited -> REJECT. ENFORCEMENT RULE: Document the ungrounded heuristic in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[0]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not evaluate 'refusal' based on tone. STEP 1 (Lexical Anchor): Find evasive or black-box phrases (e.g. 'too complex to explain', 'beyond the scope', 'internal logic', 'black box'). STEP 2 (Bounding Box): Scan the paragraph. If the text explicitly states an inability or unwillingness to decompose a decision -> ACCEPT (evasion proven). Otherwise -> REJECT. ENFORCEMENT RULE: Document the explicit evasion in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Scale 2
        scales[1]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not judge 'vagueness' subjectively. STEP 1 (Lexical Anchor): Find a justification sentence (e.g. 'This is because', 'Due to'). STEP 2 (Bounding Box): Scan the sentence. If the justification DOES NOT contain any specific domain variables, numbers, or exact verbatim quotes from the input data (relying only on generic templates) -> ACCEPT (weak explainability proven). If specific variables are present -> REJECT. ENFORCEMENT RULE: Document the lack of specific variables in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[1]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess intent. STEP 1 (Lexical Anchor): Find an evaluation of success or a positive outcome. STEP 2 (Bounding Box): Scan the surrounding section. If the text details the positive outcome but COMPLETELY OMITs any epistemic boundary markers (e.g. 'however', 'limitations', 'failed to', 'uncertainty') -> ACCEPT (selective transparency proven). If limitations are explicitly stated -> REJECT. ENFORCEMENT RULE: Document the missing limitations in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[1]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not evaluate subjective 'importance'. STEP 1 (Lexical Anchor): Find a stated decision outcome. STEP 2 (Bounding Box): Scan the explanation. If the text mentions a causal factor but DOES NOT explicitly assign a quantitative weight, rank, or specific value to it (e.g. 'Factor X was considered' vs 'Factor X had a 40% impact') -> ACCEPT (missing variable weight). If weights/ranks exist -> REJECT. ENFORCEMENT RULE: Document the unweighted factor in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Scale 3
        scales[2]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not assume connections. STEP 1 (Lexical Anchor): Find a direct causal linkage statement (e.g. 'Because of X, Y happened', 'Input A resulted in B'). STEP 2 (Bounding Box): Scan the statement. If the exact input variable is explicitly named and connected to the specific output -> ACCEPT. If the connection is merely implied -> REJECT. ENFORCEMENT RULE: Map the explicit input-output connection in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[2]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not accept vague lists. STEP 1 (Lexical Anchor): Find an explicit listing of factors or variables (e.g. 'Based on the following factors:', 'Variables considered:'). STEP 2 (Bounding Box): Scan the list. If at least two distinct variables or weights are physically defined in the text -> ACCEPT. If fewer than two are defined -> REJECT. ENFORCEMENT RULE: Document the defined variables in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[2]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept implicit modesty. STEP 1 (Lexical Anchor): Find an explicit epistemic boundary marker (e.g. 'may not apply', 'exception', 'edge case', 'out of scope'). STEP 2 (Bounding Box): Scan the sentence. If the text physically identifies a scenario where the model or logic fails or is limited -> ACCEPT. If absent -> REJECT. ENFORCEMENT RULE: Document the specific edge case or limitation in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        # Scale 4
        scales[3]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not synthesize steps yourself. STEP 1 (Lexical Anchor): Find sequential logic markers (e.g. 'First', 'Second', 'Finally', 'Step 1'). STEP 2 (Bounding Box): Scan the block. If a continuous, unbroken chain of at least three explicit logical steps is documented -> ACCEPT. If fewer than three steps -> REJECT. ENFORCEMENT RULE: Map the 3-step causal chain in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[3]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not accept post-decision doubt. STEP 1 (Lexical Anchor): Find an option-weighing or friction marker (e.g. 'Option A vs B', 'Trade-off', 'On the other hand'). STEP 2 (Bounding Box): Scan the chronological flow. If the alternatives are explicitly compared and evaluated BEFORE the final decision is stated -> ACCEPT. If evaluated after -> REJECT. ENFORCEMENT RULE: Document the pre-decision weighing in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[3]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept generic disclaimers. STEP 1 (Lexical Anchor): Find an explicit warning or certainty boundary (e.g. 'Warning', 'Cannot guarantee', 'Strictly limited to'). STEP 2 (Bounding Box): Scan the sentence. If the warning specifies EXACTLY what the model or logic cannot do using specific domain terms -> ACCEPT. If it is a generic 'AI can make mistakes' disclaimer -> REJECT. ENFORCEMENT RULE: Document the exact specified boundary in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        # Scale 5
        scales[4]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept unproven assertions. STEP 1 (Lexical Anchor): Find a counterfactual scenario (e.g. 'What if', 'Alternatively', 'Had we used'). STEP 2 (Bounding Box): Scan the paragraph. If the scenario is systematically dismantled with specific data points or mathematical proofs to validate the primary conclusion -> ACCEPT. If it is merely mentioned without data-driven refutation -> REJECT. ENFORCEMENT RULE: Detail the systematic refutation in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[4]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept qualitative confidence (e.g. 'very sure'). STEP 1 (Lexical Anchor): Find a quantitative confidence metric or strict certainty boundary (e.g. 'Confidence level', 'Margin of error', 'p-value', '95%'). STEP 2 (Bounding Box): Scan the logic block. If the text rigorously defines the EXACT quantitative or structural boundary of its own certainty -> ACCEPT. If missing quantitative boundaries -> REJECT. ENFORCEMENT RULE: Document the quantitative boundary in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[4]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept generic AI knowledge. STEP 1 (Lexical Anchor): Find an external citation, mathematical theorem, or recognized academic framework. STEP 2 (Bounding Box): Scan the sentence. If the explanation explicitly tethers its logic to this external, verifiable source (e.g. applying a specific rule from the source) -> ACCEPT. If the source is merely named without application -> REJECT. ENFORCEMENT RULE: Document the external source and applied rule in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Block blk_f6e286f050c94d60 refactored successfully.")
