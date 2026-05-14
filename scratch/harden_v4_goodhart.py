import json
import secrets

def get_id():
    return "tda_" + secrets.token_hex(8)

with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for block in data['prompt_blocks']:
    if block.get('id') == 'blk_53f32679aa514fcb':
        # Update Epistemic Anchor in top-level description
        block['ai_description'] = """<system_directive>
<objective>Evaluate the user's interaction dynamic (Driver vs. Passenger) and susceptibility to Goodhart's Law and Performativity.</objective>
<epistemic_anchor>Stumborg, M. F., et al. (2022) & Strathern, M. (1997). Goodhart's Law and Performativity in Audit Cultures. When a measure becomes a target, it ceases to be a good measure. Users may fall into 'Sycophancy' loops, where AI outputs performative agreement rather than truth.</epistemic_anchor>
<rules>
<rule>Bounty Hunter Paradigm: In FATAL FLAW directives, find ONE occurrence of the described anti-pattern.</rule>
<rule>Strict Boolean Logic: Evaluate claims as single-pole facts. Ignore complex AND/OR evaluations.</rule>
<rule>Enforce the Null Hypothesis: Assume the user is a passive passenger, blindly accepting AI outputs or superficial metrics without understanding the true objective.</rule>
</rules>
</system_directive>"""

        scales = block['scales']
        
        # Level 1
        scales[0]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY extreme goal-hacking where the user accepts the first response without structural challenge."
        scales[0]['claims'][0]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: Never read matches from 'ai:' output blocks. STEP 1 (Lexical Anchor): Find affirmative acceptance phrases by the user (e.g., 'looks good', 'thanks', 'perfect'). STEP 2 (Bounding Box): Scan the user's prompt. If the user accepts an AI output without requesting a single structural or logical change -> ACCEPT. If the user requests a modification -> REJECT. BANNED CONCEPTS: Do not evaluate if the response was actually 'good'. ENFORCEMENT RULE: Document the passive role in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        scales[0]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY if the user actively commands the AI to ignore its own stated uncertainties."
        scales[0]['claims'][1]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: System prompts. STEP 1 (Lexical Anchor): Find AI uncertainty markers (e.g., 'I am not sure', 'might be inaccurate', 'as an AI'). STEP 2 (Bounding Box): Scan the user's subsequent reply. If the user commands the AI to proceed anyway without verifying the uncertainty (e.g., 'just write it', 'ignore that') -> ACCEPT. If the user provides the missing data -> REJECT. BANNED CONCEPTS: Do not accept if the user actively resolves the AI's uncertainty. ENFORCEMENT RULE: Document the logical oversight in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        scales[0]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY if the user treats the AI's probabilistic generation as an infallible oracle."
        scales[0]['claims'][2]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. BANNED SOURCES: AI responses. STEP 1 (Lexical Anchor): Find user requests for absolute truth without external verification (e.g., 'give me the absolute fact', 'what is the exact truth'). STEP 2 (Bounding Box): Scan the user's prompt. If the user asks the AI to act as an infallible oracle without providing an external source or document to ground it -> ACCEPT. If a document or source is provided -> REJECT. BANNED CONCEPTS: Requests grounded in explicitly provided documents. ENFORCEMENT RULE: Document the authority bias in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Level 2
        scales[1]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY active corrections limited to factual, stylistic, or formatting details."
        scales[1]['claims'][0]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find superficial correction commands by the user (e.g., 'fix the typo', 'make it shorter', 'bold the headers'). STEP 2 (Bounding Box): Scan the user's prompt. If the user ONLY requests formatting or minor lexical changes without challenging the logic -> ACCEPT. If logical changes are requested -> REJECT. BANNED CONCEPTS: Do not accept if the user challenges the underlying reasoning. ENFORCEMENT RULE: Document the surface-level correction in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        scales[1]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY explicit optimization for a proxy metric (MOP) over the qualitative goal (Goodhart's Law)."
        scales[1]['claims'][1]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find explicit optimization commands for proxy metrics (e.g., 'maximize the score', 'increase the word count', 'make it sound professional'). STEP 2 (Bounding Box): Scan the user's prompt. If the user demands optimization of a surface metric without linking it to a qualitative real-world outcome -> ACCEPT. BANNED CONCEPTS: Do not accept if the metric is explicitly tied back to a measure of effectiveness. ENFORCEMENT RULE: Analyze the metric fixation in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        scales[1]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user actively adopts the AI's proposed methodology without any structural negotiation."
        scales[1]['claims'][2]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find user phrases adopting AI methodology blindly (e.g., 'let us use your structure', 'proceed with that approach', 'do what you suggested'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly adopts the AI's proposed framework without adding their own constraints -> ACCEPT. BANNED CONCEPTS: Do not accept if the user modifies the AI's framework. ENFORCEMENT RULE: Document the methodological adoption in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Level 3
        scales[2]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user actively engages with the output but only targets symptoms rather than generative logic."
        scales[2]['claims'][0]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find user instructions that modify an output (e.g., 'change this paragraph to'). STEP 2 (Bounding Box): Scan the interaction. If the user modifies the final output but leaves the original AI system prompt or generative logic exactly the same -> ACCEPT. If the user alters the underlying instructions/logic -> REJECT. BANNED CONCEPTS: Deep structural refactoring. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        scales[2]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user accepts stylistic or minor tweaks while leaving the substantive core argument unchallenged."
        scales[2]['claims'][1]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find user commands focused on tone (e.g., 'make it sound more persuasive', 'make it more academic'). STEP 2 (Bounding Box): Scan the user's prompt. If the user focuses solely on the performativity (tone/style) while ignoring substantive factual gaps -> ACCEPT. BANNED CONCEPTS: Revisions containing factual additions. ENFORCEMENT RULE: Explain the superficial correction in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        scales[2]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY one-sided execution without demand for alternative models."
        scales[2]['claims'][2]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "CRITICAL DIRECTIVE (FATAL FLAW): Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find single-path commands (e.g., 'just write the final version', 'skip the analysis'). STEP 2 (Bounding Box): Scan the user prompt. If the user actively refuses to explore counter-arguments or alternative models -> ACCEPT. BANNED CONCEPTS: Do not accept if the user asks for pros and cons. ENFORCEMENT RULE: Explain the missing alternatives in reasoning_trace before extracting.",
            "inverse_evidence": True,
            "aggregation_mode": "EXISTS"
        }]

        # Level 4
        scales[3]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user actively prevents Goodhart's Law by questioning the reliability of the metric."
        scales[3]['claims'][0]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find tension markers between metrics and goals (e.g., 'this metric is flawed because', 'we need to ensure this actually works'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly questions the reliability of a proxy metric in relation to the ultimate qualitative goal -> ACCEPT. BANNED CONCEPTS: Do not accept simple metric tracking. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        scales[3]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user forces the AI to acknowledge foundational premises and edge cases."
        scales[3]['claims'][1]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find boundary conditions (e.g., 'assuming that', 'only if', 'the exception is'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly forces the AI to acknowledge a specific edge case or foundational premise -> ACCEPT. BANNED CONCEPTS: Broad, unconditional statements. ENFORCEMENT RULE: Map this explicit logic in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        scales[3]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user demands acknowledgment of uncertainties."
        scales[3]['claims'][2]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find demands for epistemological humility (e.g., 'tell me what you do not know', 'what are the limitations of this analysis'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly commands the AI to state its uncertainties or missing data -> ACCEPT. BANNED CONCEPTS: Demands for absolute certainty. ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        # Level 5
        scales[4]['claims'][0]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user acts as an antagonistic prosecutor, challenging the AI's logic."
        scales[4]['claims'][0]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find antagonistic or prosecutorial language by the user (e.g., 'your logic is flawed here', 'this contradicts what you said', 'you are hallucinating'). STEP 2 (Bounding Box): Scan the user's prompt. If the user actively dismantles the AI's reasoning and demands a structural correction -> ACCEPT. BANNED CONCEPTS: Do not accept polite suggestions or simple typos. ENFORCEMENT RULE: Map this explicit logic in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        scales[4]['claims'][1]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user explicitly documents the 'how' and 'why' they are challenging the AI."
        scales[4]['claims'][1]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find explicit reasoning markers by the user (e.g., 'I am challenging this because', 'the reason this is wrong is'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly documents the 'why' behind their challenge to the AI -> ACCEPT. BANNED CONCEPTS: Do not accept unreasoned rejections ('this is bad'). ENFORCEMENT RULE: Document the logical step-by-step evaluation in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

        scales[4]['claims'][2]['ai_description'] = "CRITICAL DIRECTIVE: IDENTIFY where the user demands external grounding and concrete expert verification."
        scales[4]['claims'][2]['tda_assertions'] = [{
            "tda_id": get_id(),
            "ai_rule_description": "REQUIRED TARGET: Scan ONLY the Target Data. STEP 1 (Lexical Anchor): Find demands for external grounding (e.g., 'cite a specific source', 'base this strictly on the provided document', 'give me the exact quote'). STEP 2 (Bounding Box): Scan the user's prompt. If the user explicitly restricts the AI to an external, objective anchor -> ACCEPT. BANNED CONCEPTS: Acceptance of unsourced hallucinated facts. ENFORCEMENT RULE: Map this explicit logic in reasoning_trace before extracting.",
            "inverse_evidence": False,
            "aggregation_mode": "ALL_MUST_COMPLY"
        }]

with open('backend_v2/seed/seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Modification complete.")
