"""Centralized descriptions for Pydantic Field schemas.
Enforces DRY and ensures exact matching across all dynamic and static DTOs.
"""

DESC_EXACT_QUOTES = (
    "Extract up to 3 physically contiguous sentences. Do not stitch them together. "
    "ABSOLUTE PRIORITY over contextual override. MUST be empty if contextual_override is True. "
    'You MUST always return a JSON object list format: `[{"text": "..."}]`. '
    "If the rule is a negative constraint and the text complies with it, return an empty list []. "
)

DESC_CONTEXTUAL_OVERRIDE = (
    "ABSOLUTE LAST RESORT. True only if rule is satisfied contextually without a verbatim quote. "
    "exact_quotes MUST be empty if True."
)

# JSON Structure Mandate for fallback STRUCTURED_JSON parsing mode
DESC_REASONING_TRACE = (
    "Write an extensive analytical reasoning trace explaining your decision-making process. "
    "You MUST use Markdown formatting (e.g. bolding, bullet points, headers) INSIDE this JSON string to structure your analysis. "
    "You MUST write this trace in the {target_locale} locale."
)

DESC_TRANSLATION_MANDATE = (
    "MUST BE TRANSLATED TO <required_output_language>!"
)

DESC_EVALUATION_NOTES = "General qualitative evaluation notes and analytical synthesis."
STRICT_JSON_STRUCTURE_MANDATE = (
    "\n\n<json_structure_mandate>\n"
    "You MUST output a valid JSON object matching the following JSON Schema. "
    "All keys listed in the schema properties are absolutely required and case-sensitive. "
    "Do NOT omit any keys and do NOT add extra keys not listed in the schema.\n"
    "Required JSON Schema:\n{schema_json}\n"
    "</json_structure_mandate>"
)


# XAI Extension field descriptions (used as dynamic JSON schema prompts)
XAI_DESC_JUSTIFICATION = (
    "Extensive analytical reasoning and justification for the {block_id} output. "
    "STRICT MANDATE: DO NOT output any final mathematical scores, grades, "
    "or 'Arvosana' in this text. ONLY explain the qualitative reasoning."
)

XAI_DESC_CITATION = "Direct exact quote from the source text strongly supporting the {block_id} justification."

XAI_DESC_COACHING = (
    "STRICT MANDATE: Provide one concrete, actionable step to patch the observed data "
    "or logic gap. DO NOT give general tips or encouraging advice."
)

XAI_DESC_CONFIDENCE = "Numerical confidence from 0.0 to 100.0 based strictly on source evidence."

XAI_DESC_FALSIFICATION = (
    "STRICT MANDATE: Provide one direct counter-argument or missing perspective "
    "that challenges the {block_id} reasoning."
)
