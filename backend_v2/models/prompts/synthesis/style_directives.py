"""Tone, style, and qualitative coaching behavioral prompt directives (Synthesis Layer).

Single Source of Truth (SSOT) for anti-jargon guidelines, sparse data handling,
and citation rules. Stylistic coaching tone and length constraints are dynamically
governed by OutputProfile in the database.
"""

__all__ = [
    "ANTI_JARGON_MANDATE_BLOCK",
    "SPARSE_DATA_SYNTHESIS_MANDATE",
    "SYNTHESIS_CITATION_RULES_HARVARD",
    "SYNTHESIS_NO_CITATION_RULES",
]

ANTI_JARGON_MANDATE_BLOCK: str = (
    "<anti_jargon_mandate>\n"
    "- ANTI-JARGON MANDATE: You MUST NOT use performative consulting clichés, empty buzzwords, or unsubstantiated meta-commentary.\n"
    "- State all findings using direct, plain, evidence-backed statements.\n"
    "- EVIDENCE GROUNDING: Never make generic claims. Every stated strength or positive observation MUST be directly substantiated using verbatim quotes provided in the context.\n"
    "- DEFICIT GROUNDING: When referencing a deficit or weakness, quote the author's own words if the concept was attempted poorly; if the concept was omitted entirely, cite the specific unfulfilled criterion from the evaluated data without fabricating quotes.\n"
    "</anti_jargon_mandate>"
)

SPARSE_DATA_SYNTHESIS_MANDATE: str = (
    "<sparse_data_synthesis_mandate>\n"
    "- CRITICAL SPARSE DATA INSTRUCTION: The evaluation dataset contains minimal atomic evidence.\n"
    "- You MUST be extremely concise, objective, and brief.\n"
    "- You MUST leave sections completely empty (empty strings or empty arrays) if there is no direct supporting data.\n"
    "- Do NOT invent narrative filler, do NOT guess, and do NOT generate generic consultant advice.\n"
    "- If a matrix dimension or report section lacks observations, output an empty structure according to schema.\n"
    "</sparse_data_synthesis_mandate>"
)

SYNTHESIS_CITATION_RULES_HARVARD: str = (
    "<citation_rules>\n"
    "HARVARD CITATION STANDARD MANDATE:\n"
    "- When referencing external empirical studies, organizational publications, or literature explicitly mentioned in the evaluated material, you MUST use inline Harvard author-date citation format, e.g. (Author, Year) or Author (Year).\n"
    "- For every inline Harvard citation of external literature in the narrative, append a matching complete bibliographic entry to the `cited_sources` list formatted as 'Author, Initial. (Year). Title. Publisher/URL'.\n"
    "- STRICT PROHIBITIONS:\n"
    "  * NEVER output Quorum internal scientific evaluation frameworks (such as Toulmin, Bloom 1956, Popper, Kahneman & Tversky) into `cited_sources`. Evaluation frameworks are tracked independently by the system architecture.\n"
    "  * `cited_sources` is reserved EXCLUSIVELY for empirical studies, literature, and organizational sources explicitly cited within the evaluated user document/transcript.\n"
    "  * NEVER use internal system identifiers, DAG step keys (e.g., 'sr_...', 'sp_...'), or raw JSON field names in text or cited_sources.\n"
    "  * NEVER invent citation tags for internal analysis sections or internal metrics.\n"
    "  * ONLY cite legitimate external research literature, methodologies, or verified source documents.\n"
    "</citation_rules>"
)

SYNTHESIS_NO_CITATION_RULES: str = (
    "<citation_rules>\n"
    "NO IN-TEXT CITATIONS MANDATE:\n"
    "- The report bibliography section is disabled. You MUST NOT generate any parenthetical or in-text citations "
    "(such as '(Author, Year)' or '[1]').\n"
    "- Write fluent, seamless executive prose presenting all findings directly without citation tags.\n"
    "- Leave `cited_sources` as an empty list `[]`.\n"
    "</citation_rules>"
)
