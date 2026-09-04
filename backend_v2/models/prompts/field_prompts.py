"""Centralized descriptions for Pydantic Field schemas.

Enforces DRY and ensures exact matching across all dynamic and static DTOs.
"""

from backend_v2.models.prompts.linguistic_directives import DESC_TRANSLATION_MANDATE

DESC_EXACT_QUOTES = "List of physically contiguous sentences extracted verbatim as evidence."

DESC_CONTEXTUAL_OVERRIDE = "True only if the rule is satisfied contextually without a verbatim quote."

DESC_SEMANTIC_REASONING = (
    f"Concise natural language explanation of the evaluation outcome or contextual override. {DESC_TRANSLATION_MANDATE}"
)

DESC_REASONING_TRACE = "Extensive analytical reasoning trace explaining the decision-making process."

DESC_EVALUATION_NOTES = "General qualitative evaluation notes and analytical synthesis."

STRICT_JSON_STRUCTURE_MANDATE = (
    "\n\n<json_structure_mandate>\nOutput must match this JSON Schema:\n{schema_json}\n</json_structure_mandate>"
)


# XAI Extension field descriptions (used as dynamic JSON schema prompts)
XAI_DESC_JUSTIFICATION = "Extensive analytical reasoning and justification for the {block_id} output."

XAI_DESC_CITATION = "Direct exact quote from the source text strongly supporting the {block_id} justification."

XAI_DESC_COACHING = "One concrete, actionable step to patch the observed data or logic gap."

XAI_DESC_CONFIDENCE = "Numerical confidence from 0.0 to 100.0 based strictly on source evidence."

XAI_DESC_FALSIFICATION = "One direct counter-argument or missing perspective that challenges the {block_id} reasoning."
