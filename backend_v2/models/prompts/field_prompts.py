"""Centralized descriptions for Pydantic Field schemas.
Enforces DRY and ensures exact matching across all dynamic and static DTOs.
"""

DESC_EXACT_QUOTES = (
    "Extract up to 3 physically contiguous sentences. Do not stitch them together. "
    "ABSOLUTE PRIORITY over contextual override. MUST be empty if contextual_override is True. "
    "CRITICAL: MUST ALWAYS be extracted in the exact original language of the source text, "
    "as physically contiguous VERBATIM substrings (do not add/remove words, markdown, or fix typos). "
    "NEVER translate the quotes, even if your reasoning is in another language. "
    "You MUST always prefix the quote with the exact ID attribute from the <search_result> tag the quote was extracted from, "
    "followed by a colon. For example: `<<QRM-SRC-INT-INPUTSPRODUCTTEXT>>: [exact quote]`. "
    "Jos sääntö on negatiivinen rajoite ja teksti noudattaa sitä, palauta tyhjä lista []. Tyhjä lista on täysin oikea vastaus faktojen puuttuessa."
)

DESC_CONTEXTUAL_OVERRIDE = (
    "ABSOLUTE LAST RESORT. True only if rule is satisfied contextually without a verbatim quote. "
    "exact_quotes MUST be empty if True."
)
