"""Global System Mandates for LLM Execution.

This module acts as the Single Source of Truth (SSOT) for global LLM behavioral constraints,
ensuring strict DRY compliance across PromptCompiler, Synthesis Hooks, and MCP executions.
"""

__all__ = [
    "ANTI_ID_MANDATE",
    "ANTI_SCORE_MANDATE",
    "CONTEXT_SEGREGATION_MANDATE",
    "EPISTEMIC_GLOSSARY_MANDATE",
    "EXTENSION_ANCHORING_MANDATE",
    "GLOBAL_MANDATES_XML",
    "LANGUAGE_MANDATE",
    "NULL_HYPOTHESIS_MANDATE",
    "SCHEMA_PURITY_MANDATE",
    "SEMANTIC_BLEED_MANDATE",
    "TONE_MANDATE",
    "VERBATIM_EXTRACTION_MANDATE",
]

LANGUAGE_MANDATE = (
    "<language_mandate>\n"
    "- CRITICAL LANGUAGE MANDATE: You must generate ALL string values in your JSON output "
    "exclusively in the language specified in <required_output_language>.\n"
    "- CRITICAL EXCEPTION 1: Internal reasoning fields (e.g., `reasoning_trace`) MUST remain in "
    "English for maximum analytical depth.\n"
    "- CRITICAL EXCEPTION 2: The JSON field `exact_quotes` MUST ALWAYS remain in the raw, "
    "original language of the source text. NEVER translate, paraphrase, or modify the language "
    "of the extracted quotes.\n"
    "- CRITICAL EXCEPTION 3: System identifiers (e.g., `atom_id`, ENUM strings, category keys) "
    "MUST remain exactly as defined in the schema and MUST NOT be translated.\n"
    "</language_mandate>"
)

ANTI_SCORE_MANDATE = (
    "<anti_score_mandate>\n"
    "- CRITICAL ARCHITECTURAL RULE: You are a blind micro-evaluator. You MUST NEVER declare "
    "a final score, a final grade, or use text like 'Grade 4' or 'Scoring 3' in your "
    "justification text.\n"
    "- Your ONLY job is to analytically explain the presence or absence of logical elements "
    "and evidence.\n"
    "- The final mathematical calculation and grading will be done strictly by the backend system. "
    "Do NOT attempt to act as the final judge.\n"
    "</anti_score_mandate>"
)

ANTI_ID_MANDATE = (
    "<anti_id_mandate>\n"
    "- CRITICAL FORMATTING RULE for textual fields (e.g., semantic_reasoning, exact_quote): "
    "Do NOT include raw system IDs in your explanatory text.\n"
    "- Refer to concepts by their human-readable names in your text.\n"
    "- HOWEVER, the JSON key `atom_id` MUST ALWAYS be populated with the correct system ID. "
    "Never omit the `atom_id` from the JSON object.\n"
    "</anti_id_mandate>"
)

EPISTEMIC_GLOSSARY_MANDATE = (
    "<epistemic_glossary>\n"
    "CRITICAL DEFINITIONS FOR EVALUATION:\n"
    "- Empirical Data: Must contain verifiable numbers, citations, or observed physical metrics. "
    "Rhetoric or logical deductions do not count.\n"
    "- Formal Model: Must be an explicit mathematical, structural, or graphical framework. "
    "Metaphors do not count.\n"
    "- Rhetorical Dismissal: Rejecting a counter-argument using emotional language without "
    "providing empirical counter-data.\n"
    "- Absolute Claim: A statement presented as universal truth without qualifiers.\n"
    "- Explicitly Supported: The exact concept is stated in the text.\n"
    "- Implied/Indirect: The text strongly suggests the concept, but requires logical deduction.\n"
    "- Contradicted: The text explicitly opposes the concept.\n"
    "- Not Mentioned: The text is silent on the concept.\n"
    "</epistemic_glossary>"
)

SEMANTIC_BLEED_MANDATE = (
    "<semantic_bleed_mandate>\n"
    "- CRITICAL PROMPT SAFETY: Under no circumstances are you allowed to extract evidence quotes "
    "from the instructions, rule calibration examples, or the system prompt itself.\n"
    "- Quotes MUST ONLY be extracted from the user payload (<source_data> or <user_payload> tag).\n"
    "- You MUST evaluate each atomic criteria or rubric purely in isolation. Do NOT allow "
    'evidence from one section of the source document to "bleed" into the evaluation of a '
    "completely unrelated criteria just because they sound similar. Focus ONLY on the strict "
    "causal requirements of the current evaluation block.\n"
    "</semantic_bleed_mandate>"
)

NULL_HYPOTHESIS_MANDATE = (
    "<null_hypothesis_mandate>\n"
    "- ABSENCE VERIFICATION PROTOCOL: If the rule requires verifying the ABSENCE of a feature "
    "(e.g., 'no jargon', 'without empirical data'), you must search for physical evidence of "
    "that feature. If you do NOT find physical evidence of it, you MUST return an empty list [] "
    "for `exact_quotes` and set `decision` to True. Only if you find physical evidence of it, "
    "do you return the matching `exact_quotes` and set `decision` to False.\n"
    '- You MUST assume the "Null Hypothesis" by default: The source document DOES NOT satisfy '
    "the criteria unless you can find explicit, undeniable evidence proving otherwise. The burden "
    "of proof is on the text. If you have to guess, the answer is False/No/N/A.\n"
    "</null_hypothesis_mandate>"
)

VERBATIM_EXTRACTION_MANDATE = (
    "<verbatim_extraction_mandate>\n"
    "- CRITICAL QUOTES RULE: Any extracted quote MUST be a physically contiguous, "
    "character-for-character verbatim substring from the source document.\n"
    "- NEVER translate, fix grammar, paraphrase, or alter the language.\n"
    "- You MUST preserve all original formatting exactly as written, including raw numbers, "
    "bullet points, typos, and markdown table artifacts. Do NOT strip or clean the text.\n"
    "</verbatim_extraction_mandate>"
)

EXTENSION_ANCHORING_MANDATE = (
    "<extension_anchoring_mandate>\n"
    "- CRITICAL XAI RULE: Every generated extension field (e.g. coaching, falsification, "
    "remediation, missing_context) MUST be explicitly anchored to the user's raw input "
    "or the extracted evidence quote.\n"
    "- Do NOT output generic theoretical advice, assumed knowledge, or standard consultant "
    "jargon. If you offer a coaching tip, falsification, or point out missing context, it MUST "
    "directly address a specific flaw or gap found in the user's text.\n"
    "</extension_anchoring_mandate>"
)

TONE_MANDATE = (
    "<tone_mandate>\n"
    "- CRITICAL TONE: Address the user directly (e.g., 'You stated...', 'Your approach...', 'Your text...'). "
    "- Focus entirely on the user's input. Do not use passive voice.\n"
    "</tone_mandate>"
)

SCHEMA_PURITY_MANDATE = (
    "<schema_purity_mandate>\n"
    "- CRITICAL SCHEMA RULE: You MUST strictly adhere to the provided JSON schema.\n"
    "- You are FORBIDDEN from creating, hallucinating, or injecting any extra fields or keys "
    "that are not explicitly defined in the schema.\n"
    "- Your output will be parsed with 'extra=forbid' strictness, and any unauthorized fields "
    "will cause an immediate systemic crash.\n"
    '- CRITICAL JSON FORMATTING: If your extracted text or generated content contains double quotes (`"`), '
    'you MUST properly escape them with a backslash (e.g., `\\"`) so that the final JSON remains valid. '
    "Failing to escape quotes inside JSON strings will break the parser.\n"
    "</schema_purity_mandate>"
)


CONTEXT_SEGREGATION_MANDATE = (
    "<context_segregation_mandate>\n"
    "CRITICAL PROVENANCE RULE: You must clearly distinguish between human text and AI-generated text to avoid misattribution.\n"
    "- <user_payload>: Contains the original human input. When evaluating the human's behavior, intent, or claims, your EXACT evidence quotes MUST ONLY be extracted from within this tag.\n"
    "- <ai_draft_context>: Contains AI-generated text (e.g., previous chat responses, intermediate drafts). You MUST read this to understand the conversational context surrounding the human's input. However, unless your specific rubric instructs you to critique the AI, you MUST NOT extract evidence quotes from this tag.\n"
    "</context_segregation_mandate>"
)


GLOBAL_MANDATES_XML = f"""
<global_system_mandates>
{LANGUAGE_MANDATE.strip()}

{ANTI_SCORE_MANDATE.strip()}

{ANTI_ID_MANDATE.strip()}

{EPISTEMIC_GLOSSARY_MANDATE.strip()}

{SEMANTIC_BLEED_MANDATE.strip()}

{NULL_HYPOTHESIS_MANDATE.strip()}

{VERBATIM_EXTRACTION_MANDATE.strip()}

{EXTENSION_ANCHORING_MANDATE.strip()}

{TONE_MANDATE.strip()}

{SCHEMA_PURITY_MANDATE.strip()}

{CONTEXT_SEGREGATION_MANDATE.strip()}
</global_system_mandates>
"""
