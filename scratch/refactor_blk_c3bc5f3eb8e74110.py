import json
import secrets

def generate_tda_id():
    return "tda_" + secrets.token_hex(8)

file_path = "backend_v2/seed/seed_data.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block.get("id") == "blk_c3bc5f3eb8e74110":
        block["ai_description"] = "<system_directive>\n<role>CAUSAL AUDITOR / ANTAGONISTIC PROSECUTOR (ZERO-TRUST)</role>\n<task>Scrutinize the user's claimed causal influence over the AI's output using Judea Pearl's framework of causal inference. Act as a Bounty Hunter to expose post-hoc rationalizations.</task>\n<mandate>Assume any claimed causal link is a post-hoc fallacy, that the user is intellectually lazy, and that any success was stochastic. You must actively search for post-hoc rationalizations, unaddressed counterfactuals, and claims presented as absolute facts without proof. Do NOT give the benefit of the doubt. True causal integrity requires documented pre-planning (Cognitive Friction), active falsification of alternatives, and explicit source anchoring.</mandate>\n<role_enforcement>Strictly adhere to 'user:' and 'ai:' prefixes where applicable. Differentiate between user intent and AI stochastic generation.</role_enforcement>\n<banned_concepts>Do not evaluate subjective terms like 'justified', 'good', or 'logical'. Use structural thresholds (e.g., number of steps, presence of counterfactual markers).</banned_concepts>\n<epistemic_anchor>Anchored in Judea Pearl's 'The Book of Why'. Employs the Ladder of Causation (Observation, Intervention, Counterfactuals) to demand structural proof of causal direction. Enforces strict tests against the 'post hoc ergo propter hoc' fallacy by demanding pre-generation intent and abductive reasoning paths.</epistemic_anchor>\n</system_directive>"

        scales = block["scales"]
        
        # Scale 1
        scales[0]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. If role prefixes (`user:`, `ai:`) exist, focus on the 'user:' block or un-prefixed text. BANNED SOURCES: System instructions. BANNED CONCEPTS: Do not evaluate subjective 'sincerity'. STEP 1 (Lexical Anchor): Find a retrospective claim of intent (e.g. 'That is what I meant', 'I intended', 'As expected'). STEP 2 (Bounding Box): Scan the text preceding this claim. If the original instruction DOES NOT contain the exact parameters claimed -> ACCEPT (Post-Hoc Fallacy found). If the prior instruction contains the parameters -> REJECT. ENFORCEMENT RULE: Document the timeline mapping in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[0]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. If role prefixes exist, focus on 'ai:' output compared to 'user:' input. BANNED LOGIC: Do not evaluate 'coincidence' abstractly. STEP 1 (Lexical Anchor): Identify a novel concept, specific methodology, or data point introduced by the AI. STEP 2 (Bounding Box): Scan the preceding 'user:' prompt. If the user prompt did NOT explicitly request this concept or methodology -> ACCEPT (Stochastic value found). If the user requested it -> REJECT. ENFORCEMENT RULE: Detail the missing causal link in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[0]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not look for 'absence' directly. BANNED SOURCES: Ignore system prompts. STEP 1 (Lexical Anchor): Find an absolute conclusion or decision (e.g. 'Therefore', 'The solution is', 'Must be'). STEP 2 (Bounding Box): Scan the paragraph containing this conclusion. If the paragraph DOES NOT contain a lexical marker of a counterfactual (e.g. 'Alternatively', 'What if', 'Although') -> ACCEPT (Failure to test counterfactuals). If counterfactuals are present -> REJECT. ENFORCEMENT RULE: Document the absolute claim and lack of alternative markers in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Scale 2
        scales[1]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. Focus on 'user:' blocks if prefixes exist. BANNED CONCEPTS: Do not judge 'vagueness' subjectively. STEP 1 (Lexical Anchor): Find a directive verb (e.g. 'Make', 'Improve', 'Change'). STEP 2 (Bounding Box): Scan the sentence containing the verb. If the sentence DOES NOT contain a measurable threshold, a specific framework name, or a quantifiable metric -> ACCEPT (Weak causal direction). If specific metrics exist -> REJECT. ENFORCEMENT RULE: Document the lack of parameters in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[1]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not guess psychological bias. STEP 1 (Lexical Anchor): Find an evaluation of an outcome (e.g. 'Success', 'Worked well', 'Correct'). STEP 2 (Bounding Box): Scan the surrounding section. If the text lists supporting evidence but completely omits any mention of edge cases, failures, or limitations (e.g. 'Failed', 'Error', 'However') in the same section -> ACCEPT (Confirmation bias detected). If limitations are discussed -> REJECT. ENFORCEMENT RULE: Document the one-sided evidence in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]
        scales[1]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not evaluate 'truth'. STEP 1 (Lexical Anchor): Find a causal claim (e.g. 'Because of X', 'Led to Y', 'Caused'). STEP 2 (Bounding Box): Scan the paragraph. If the text DOES NOT provide empirical data (numbers, logs, specific quotes) or a step-by-step mechanism to prove the link -> ACCEPT (Unproven causality). If data/mechanism exists -> REJECT. ENFORCEMENT RULE: Explain the missing empirical link in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Scale 3
        scales[2]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. Focus on 'user:' to 'ai:' interaction. BANNED LOGIC: Do not accept vague requests. STEP 1 (Lexical Anchor): Find an explicit user instruction containing at least two specific constraints (e.g. format, tone, length). STEP 2 (Bounding Box): Scan the subsequent user response. If the user explicitly verifies those exact constraints (e.g. 'Constraint A met, Constraint B failed') -> ACCEPT. If verification is absent or generic -> REJECT. ENFORCEMENT RULE: Document the constraints and verification in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[2]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not accept implicit alternatives. STEP 1 (Lexical Anchor): Find a comparative marker (e.g. 'Option A vs Option B', 'Instead of', 'Compared to'). STEP 2 (Bounding Box): Scan the surrounding sentences. If the text explicitly names at least two distinct approaches before selecting one -> ACCEPT. If only one approach is discussed -> REJECT. ENFORCEMENT RULE: List the compared options in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[2]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not use subjective words like 'good'. STEP 1 (Lexical Anchor): Find a stated objective containing a measurable goal (e.g. 'Reduce word count', 'Include 3 examples'). STEP 2 (Bounding Box): Scan the result evaluation. If the text quotes the exact measurable goal and confirms it with a physical measurement or count -> ACCEPT. If the confirmation is purely qualitative -> REJECT. ENFORCEMENT RULE: Document the numerical/objective match in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        # Scale 4
        scales[3]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Ignore system instructions. STEP 1 (Lexical Anchor): Find a falsification marker (e.g. 'Let\\'s try to break this', 'What if the opposite is true', 'Counter-argument'). STEP 2 (Bounding Box): Scan the paragraph. If the user explicitly introduces a scenario designed to make their own hypothesis fail -> ACCEPT. If no active stress-test is present -> REJECT. ENFORCEMENT RULE: Detail the falsification scenario in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[3]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not accept post-generation complaints. STEP 1 (Lexical Anchor): Find a friction marker prior to an action (e.g. 'This is difficult because', 'The risk here is', 'We must balance'). STEP 2 (Bounding Box): Scan the chronological flow. If the conflict or trade-off is articulated BEFORE the final output is generated -> ACCEPT. If the friction is only discussed afterwards -> REJECT. ENFORCEMENT RULE: Document the pre-generation trade-off in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[3]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED LOGIC: Do not assume connections. STEP 1 (Lexical Anchor): Find a multi-step sequence marker (e.g. 'Step 1... Step 2... Step 3', 'First... Then... Finally'). STEP 2 (Bounding Box): Scan the entire causal chain. If the text explicitly links at least three distinct sequential actions where each depends entirely on the previous one -> ACCEPT. If the chain is less than three steps or broken -> REJECT. ENFORCEMENT RULE: Map the 3-step causal chain in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        # Scale 5
        scales[4]["claims"][0]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. Focus on 'user:' blocks. BANNED LOGIC: Do not accept vague visions. STEP 1 (Lexical Anchor): Find a structural blueprint or architectural prediction (e.g. 'The architecture must contain X, Y, and Z'). STEP 2 (Bounding Box): Scan the sequence. If the user documents a complex, multi-variable constraint AND explicitly discusses the cognitive friction of solving it BEFORE the AI generates the solution -> ACCEPT. If the blueprint is missing or friction is omitted -> REJECT. ENFORCEMENT RULE: Document the structural blueprint in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[4]["claims"][1]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED CONCEPTS: Do not accept brief dismissals (e.g. 'Option B is bad'). STEP 1 (Lexical Anchor): Find an explicit reference to an established alternative model or framework. STEP 2 (Bounding Box): Scan the paragraph. If the text dismantles the alternative model by citing specific data points or logical contradictions that render it invalid in this context -> ACCEPT. If the alternative is dismissed without evidence -> REJECT. ENFORCEMENT RULE: Detail the systematic refutation in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]
        scales[4]["claims"][2]["tda_assertions"] = [{
            "tda_id": generate_tda_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Do not accept generic AI knowledge. STEP 1 (Lexical Anchor): Find a formal citation, academic framework, or recognized methodology (e.g. 'Pearl\\'s do-calculus', 'Bayesian updating'). STEP 2 (Bounding Box): Scan the sentence. If the causal reasoning is explicitly justified by applying the rules of this named external framework -> ACCEPT. If the framework is merely name-dropped without applying its rules -> REJECT. ENFORCEMENT RULE: Document the framework and its applied rule in reasoning_trace BEFORE extracting exact_quote.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Block blk_c3bc5f3eb8e74110 refactored successfully.")
