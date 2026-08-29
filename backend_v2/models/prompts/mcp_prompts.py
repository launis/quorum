"""Centralized prompt instructions and mandates for MCP tools and Source Verification.

Single Source of Truth (SSOT) for external tool extraction, verification,
and citation self-correction directives.
"""

__all__ = [
    "CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION",
    "MCP_EVIDENCE_INJECTION_DIRECTIVE",
    "SOURCE_EXTRACTION_SYSTEM_INSTRUCTION",
    "SOURCE_VERIFICATION_SYSTEM_INSTRUCTION",
    "build_mcp_citation_extraction_directive",
]

SOURCE_EXTRACTION_SYSTEM_INSTRUCTION: str = (
    "<system_directive>\n"
    "<objective>Read the provided document and extract all explicit references to external sources, research, studies, guidelines, or institutions.</objective>\n"
    "<role>Expert Fact-Checker</role>\n"
    "<rules>\n"
    "  <rule>Extract the exact claim being attributed to external entities.</rule>\n"
    "  <rule>Do not include internal cross-references.</rule>\n"
    "  <rule>Return an empty list if none are found.</rule>\n"
    "</rules>\n"
    "</system_directive>"
)

SOURCE_VERIFICATION_SYSTEM_INSTRUCTION: str = (
    "<system_directive>\n"
    "<objective>Compare the original source claim against the search results provided.</objective>\n"
    "<role>Expert Fact-Checker</role>\n"
    "<rules>\n"
    "  <rule>Determine if the claim is VERIFIED (supported by search), HALLUCINATION (contradicted or clearly fabricated), or INCONCLUSIVE (not enough info found).</rule>\n"
    "  <rule>Return ONLY the exact word: VERIFIED, HALLUCINATION, or INCONCLUSIVE.</rule>\n"
    "</rules>\n"
    "</system_directive>"
)

CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION: str = (
    "<system_directive>\n"
    "<objective>Locate and return the exact physical substring from the source context that is semantically equivalent to the failed claim.</objective>\n"
    "<role>Physical Anchor Validator</role>\n"
    "<rules>\n"
    "  <rule>The returned corrected_claim MUST be a 100% exact substring match from the source context (including case, spaces, and diacritics).</rule>\n"
    "  <rule>Do not paraphrase or summarize.</rule>\n"
    "</rules>\n"
    "</system_directive>"
)

MCP_EVIDENCE_INJECTION_DIRECTIVE: str = (
    "<system_directive>\n"
    "<objective>EVIDENCE INJECTION COMPLETE</objective>\n"
    "<rules>\n"
    "  <rule>You now have external search evidence above.</rule>\n"
    "  <rule>Complete the evaluation matrix using both the original context AND the search evidence.</rule>\n"
    "  <rule>Output your response strictly in the required JSON schema format.</rule>\n"
    "</rules>\n"
    "</system_directive>"
)


def build_mcp_citation_extraction_directive(target_language: str) -> str:
    """Build dynamic system directive for extracting citations with specific target language."""
    return (
        "<system_directive>\n"
        "<objective>Extract factual claims that require external verification.</objective>\n"
        "<rules>\n"
        "  <rule>Return a structured list of citations.</rule>\n"
        f"  <rule>Provide a short max 100 character reasoning sentence for each extraction in the language code '{target_language}'.</rule>\n"
        "</rules>\n"
        "</system_directive>"
    )
