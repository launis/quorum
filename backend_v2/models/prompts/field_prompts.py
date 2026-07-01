"""Centralized descriptions for Pydantic Field schemas.
Enforces DRY and ensures exact matching across all dynamic and static DTOs.
"""

DESC_EXACT_QUOTES = (
    "Extract up to 3 physically contiguous sentences. Do not stitch them together. "
    "ABSOLUTE PRIORITY over contextual override. MUST be empty if contextual_override is True. "
    "CRITICAL: MUST ALWAYS be extracted in the exact original language of the source text, "
    "as physically contiguous VERBATIM substrings (do not add/remove words, markdown, or fix typos). "
    "NEVER translate the quotes, even if your reasoning is in another language. "
    'You MUST always return a JSON object list format: `[{"text": "..."}]`. '
    "Jos sääntö on negatiivinen rajoite ja teksti noudattaa sitä, palauta tyhjä lista []. Tyhjä lista on täysin oikea vastaus faktojen puuttuessa."
)

DESC_CONTEXTUAL_OVERRIDE = (
    "ABSOLUTE LAST RESORT. True only if rule is satisfied contextually without a verbatim quote. "
    "exact_quotes MUST be empty if True."
)

# JSON Structure Mandate for fallback STRUCTURED_JSON parsing mode
STRICT_JSON_STRUCTURE_MANDATE = (
    "\n\n[SYSTEM: STRICT JSON STRUCTURE MANDATE]\n"
    "You MUST output a valid JSON object matching the following JSON Schema. "
    "All keys listed in the schema properties are absolutely required and case-sensitive. "
    "Do NOT omit any keys and do NOT add extra keys not listed in the schema.\n"
    "Required JSON Schema:\n{schema_json}"
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
