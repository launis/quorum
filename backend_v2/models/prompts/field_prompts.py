"""Centralized descriptions for Pydantic Field schemas.
Enforces DRY and ensures exact matching across all dynamic and static DTOs.
"""

DESC_EXACT_QUOTES = (
    "Extract up to 3 physically contiguous sentences. Do not stitch them together. "
    "ABSOLUTE PRIORITY over contextual override. MUST be empty if contextual_override is True. "
    "CRITICAL: MUST ALWAYS be extracted in the exact original language of the source text, "
    "as physically contiguous VERBATIM substrings (do not add/remove words, markdown, or fix typos). "
    "NEVER translate the quotes, even if your reasoning is in another language."
)

DESC_CONTEXTUAL_OVERRIDE = (
    "ABSOLUTE LAST RESORT. True only if rule is satisfied contextually without a verbatim quote. "
    "exact_quotes MUST be empty if True."
)
