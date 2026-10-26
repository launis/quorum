"""Centralized prompt instructions and mandates for MCP tools and Source Verification (Execution Layer).

Single Source of Truth (SSOT) for external tool extraction, verification,
and citation self-correction directives.
"""

__all__ = [
    "CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION",
    "MCP_EVIDENCE_INJECTION_DIRECTIVE",
    "MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION",
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

# Phase 1, Step 2: Static XML system instruction for JIT Micro-LLM MCP argument synthesis
MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION: str = (
    "<system_directive>\n"
    "<objective>Synthesize schema-compliant invocation arguments for an external MCP tool based on the verification claim, search query, and reasoning.</objective>\n"
    "<role>Deterministic MCP Argument Synthesizer</role>\n"
    "<rules>\n"
    "  <rule>Populate all required fields in the response schema using the semantic context of claim_text, search_query, and reasoning.</rule>\n"
    "  <rule>When studio_configured_parameters are provided in the user payload, preserve those exact values for the corresponding schema fields.</rule>\n"
    "  <rule>Infer domain-specific parameters (specifically country codes, categories, jurisdictions, or date bounds) directly from the claim context and language.</rule>\n"
    "  <rule>Output strictly according to the structured response schema with zero extraneous text.</rule>\n"
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


def build_mcp_citation_extraction_directive(target_language: str, query_guidance: str | None = None) -> str:
    """Build dynamic system directive for extracting citations with specific target language.

    Args:
        target_language: Two-letter ISO language code for reasoning output.
        query_guidance: Optional step-level query guidance instruction to append.

    Returns:
        Structured XML system directive string.
    """
    guidance_rule = ""
    if query_guidance and query_guidance.strip():
        guidance_rule = f"  <rule>{query_guidance.strip()}</rule>\n"

    return (
        "<system_directive>\n"
        "<objective>Extract factual claims that require external verification.</objective>\n"
        "<rules>\n"
        "  <rule>Return a structured list of citations.</rule>\n"
        f"  <rule>Provide a short max 100 character reasoning sentence for each extraction in the language code '{target_language}'.</rule>\n"
        "  <rule>Formulate 'search_query' strictly as concise entity or topic keywords (1-3 key terms, specifically: proper nouns, organization names, or core subject concepts). Do NOT include natural language questions, conjunctions, multi-entity clauses, or conversational filler phrases (specifically: 'tutkimus tulokset' or 'hybridityö tutkimus').</rule>\n"
        f"{guidance_rule}"
        "</rules>\n"
        "</system_directive>"
    )
