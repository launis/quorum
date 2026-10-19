"""Centralized descriptions for Pydantic Field schemas.

Enforces DRY and ensures exact matching across all dynamic and static DTOs.
"""

__all__ = [
    "DESC_ALIAS",
    "DESC_COACHING",
    "DESC_CONTEXTUAL_OVERRIDE",
    "DESC_EVALUATION_NOTES",
    "DESC_EXACT_QUOTES",
    "DESC_EXACT_QUOTE_TEXT",
    "DESC_FALSIFICATION",
    "DESC_IS_TRUE",
    "DESC_REASONING_TRACE",
    "DESC_REMEDIATION_STEPS",
    "DESC_SEMANTIC_REASONING",
    "DESC_SOURCE_QUOTE",
    "DESC_SOURCE_QUOTES",
    "STRICT_JSON_STRUCTURE_MANDATE",
    "XAI_DESC_CITATION",
    "XAI_DESC_COACHING",
    "XAI_DESC_CONFIDENCE",
    "XAI_DESC_EMOTIONAL_SENTIMENT",
    "XAI_DESC_FALSIFICATION",
    "XAI_DESC_JUSTIFICATION",
    "XAI_DESC_MISSING_CONTEXT",
    "XAI_DESC_REMEDIATION_STEPS",
    "XAI_DESC_RISK_FLAG",
    "XAI_DESC_THEORY_LINK",
]

DESC_EXACT_QUOTES = (
    "List of physically contiguous sentences extracted verbatim as evidence strictly entailing "
    "the claim in its asserted modality."
)

DESC_ALIAS = "The short identifier alias assigned to the claim (e.g., 'a0', 'a1')."

DESC_IS_TRUE = (
    "True if the text confirms the claim AND is grounded by exact source_quotes (or contextual_override=True). "
    "If no verbatim quote exists and no contextual override applies, must be False."
)

DESC_CONTEXTUAL_OVERRIDE = (
    "Set to True if and only if the rule is verified contextually without verbatim source_quotes "
    "(in which case source_quotes must be null)."
)

DESC_SEMANTIC_REASONING = (
    "Concise natural language explanation of propositional entailment, evaluation outcome, or contextual override."
)

DESC_SOURCE_QUOTES = (
    "Ordered list of 1 to 3 exact verbatim sentence segments strictly entailing the claim in its asserted modality. "
    "Mandatory non-empty array when is_true is True (unless contextual_override is True). "
    "Must be null when is_true is False or contextual_override is True."
)
DESC_SOURCE_QUOTE = DESC_SOURCE_QUOTES

DESC_COACHING = "Provide a concrete, actionable coaching tip if the claim failed."

DESC_FALSIFICATION = "Provide a falsification argument or counter-evidence if the claim failed."

DESC_REMEDIATION_STEPS = "List of concrete step-by-step remediation actions if the claim failed."

DESC_REASONING_TRACE = "Extensive analytical reasoning trace explaining the decision-making process."

DESC_EVALUATION_NOTES = "General qualitative evaluation notes and analytical synthesis."

DESC_EXACT_QUOTE_TEXT = (
    "Exact verbatim sentence strictly entailing the claim in its asserted modality "
    "extracted directly from the source text."
)

STRICT_JSON_STRUCTURE_MANDATE = (
    "\n\n<json_structure_mandate>\nOutput must match this JSON Schema:\n{schema_json}\n</json_structure_mandate>"
)


# XAI Extension field descriptions (used as dynamic JSON schema prompts)
XAI_DESC_JUSTIFICATION = "Extensive analytical reasoning and justification for the {block_id} output."

XAI_DESC_CITATION = "Direct exact quote from the source text strongly supporting the {block_id} justification."

XAI_DESC_COACHING = "One concrete, actionable step to patch the observed data or logic gap."

XAI_DESC_CONFIDENCE = "Numerical confidence from 0.0 to 100.0 based strictly on source evidence."

XAI_DESC_FALSIFICATION = "One direct counter-argument or missing perspective that challenges the {block_id} reasoning."

XAI_DESC_MISSING_CONTEXT = (
    "Exact missing data from the provided text that would have altered the evaluation score. "
    "No theoretical assumptions."
)

XAI_DESC_RISK_FLAG = "True ONLY if there is a severe, documentable risk present; False otherwise."

XAI_DESC_REMEDIATION_STEPS = "Numbered actionable list of distinct textual remediation steps."

XAI_DESC_EMOTIONAL_SENTIMENT = "Analysis of the user's emotional state or tone regarding this metric."

XAI_DESC_THEORY_LINK = "Direct logical connection of the observation back to the governing theory framework."
