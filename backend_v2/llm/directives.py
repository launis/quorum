"""Centralized LLM architectural mandates and directives.

This module acts as the Single Source of Truth (SSOT) for global LLM behavioral constraints,
ensuring strict DRY compliance across PromptCompiler, Synthesis Hooks, and MCP executions.
"""

# Verbatim extraction mandate for all CoT quotes
VERBATIM_EXTRACTION_MANDATE = (
    "CRITICAL QUOTES RULE: Any extracted quote MUST be a physically contiguous, "
    "character-for-character verbatim substring from the source document. "
    "NEVER translate, fix grammar, paraphrase, or alter the language. "
    "You MUST preserve all original formatting exactly as written, including raw numbers, "
    "bullet points, typos, and markdown table artifacts. Do NOT strip or clean the text."
)

# Tone mandate for synthesis and user-facing reflections
TONE_MANDATE = (
    "CRITICAL TONE: Address the user directly (e.g., 'You stated...', 'Your approach...', 'Your text...'). "
    "Focus entirely on the user's input. Do not use passive voice."
)

# Anti-Score mandate to enforce the Blind Micro-Evaluator architecture
ANTI_SCORE_MANDATE = (
    "<ANTI_SCORE_MANDATE>\n"
    "CRITICAL ARCHITECTURAL RULE: You are a blind micro-evaluator. You MUST NEVER declare a final score, "
    "a final grade, or use text like 'Grade 4' or 'Scoring 3' in your justification text. "
    "Your ONLY job is to analytically explain the presence or absence of logical elements and evidence. "
    "The final mathematical calculation and grading will be done strictly by the backend system. "
    "Do NOT attempt to act as the final judge.\n"
    "</ANTI_SCORE_MANDATE>"
)

# Schema Purity mandate for Pydantic alignment
SCHEMA_PURITY_MANDATE = (
    "<SCHEMA_PURITY_MANDATE>\n"
    "CRITICAL SCHEMA RULE: You MUST strictly adhere to the provided JSON schema. "
    "You are FORBIDDEN from creating, hallucinating, or injecting any extra fields or keys "
    "that are not explicitly defined in the schema. Your output will be parsed with 'extra=forbid' strictness, "
    "and any unauthorized fields will cause an immediate systemic crash.\n"
    "</SCHEMA_PURITY_MANDATE>"
)

# Extension Anchoring mandate for XAI trace transparency
EXTENSION_ANCHORING_MANDATE = (
    "<EXTENSION_ANCHORING_MANDATE>\n"
    "CRITICAL XAI RULE: Every generated extension field (e.g. coaching, falsification, "
    "remediation, missing_context) MUST be explicitly anchored to the user's raw input "
    "or the extracted evidence quote. Do NOT output generic theoretical advice, assumed "
    "knowledge, or standard consultant jargon. If you offer a coaching tip, falsification, "
    "or point out missing context, it MUST directly address a specific flaw or gap found "
    "in the user's text.\n"
    "</EXTENSION_ANCHORING_MANDATE>"
)

# Anti-ID mandate to prevent hallucination of internal PKs
ANTI_ID_MANDATE = (
    "<ANTI_ID_MANDATE>\n"
    "CRITICAL FORMATTING RULE for textual fields (e.g., semantic_reasoning, exact_quote):\n"
    "Do NOT include raw system IDs in your explanatory text. "
    "Refer to concepts by their human-readable names in your text.\n"
    "HOWEVER, the JSON key `atom_id` MUST ALWAYS be populated with the correct system ID. "
    "Never omit the `atom_id` from the JSON object.\n"
    "</ANTI_ID_MANDATE>"
)

# Phase 1, Step 1: Add SEMANTIC_BLEED_MANDATE to prevent semantic bleeding from prompt examples
SEMANTIC_BLEED_MANDATE = (
    "CRITICAL PROMPT SAFETY: Under no circumstances are you allowed to extract evidence quotes "
    "from the instructions, rule calibration examples, or the system prompt itself. "
    "Quotes MUST ONLY be extracted from the user payload (<user_payload> tag)."
)

# Phase 1, Step 1: Add EPISTEMIC_GLOSSARY_MANDATE containing standard evaluation definitions
EPISTEMIC_GLOSSARY_MANDATE = (
    "<EPISTEMIC_GLOSSARY>\n"
    "CRITICAL DEFINITIONS FOR EVALUATION:\n"
    "- Empirical Data: Must contain verifiable numbers, citations, or observed physical metrics. Rhetoric or logical deductions do not count.\n"
    "- Formal Model: Must be an explicit mathematical, structural, or graphical framework. Metaphors do not count.\n"
    "- Rhetorical Dismissal: Rejecting a counter-argument using emotional language without providing empirical counter-data.\n"
    "- Absolute Claim: A statement presented as universal truth without qualifiers.\n"
    "</EPISTEMIC_GLOSSARY>"
)

# Phase 1, Step 1: Add NULL_HYPOTHESIS_MANDATE for absence verification
NULL_HYPOTHESIS_MANDATE = (
    "ABSENCE VERIFICATION PROTOCOL: If the rule requires verifying the ABSENCE of a feature "
    "(e.g., 'no jargon', 'without empirical data'), you must search for physical evidence of "
    "that feature. If you do NOT find physical evidence of it, you MUST return an empty list [] "
    "for `exact_quotes` and set `decision` to True. Only if you find physical evidence of it, "
    "do you return the matching `exact_quotes` and set `decision` to False."
)
