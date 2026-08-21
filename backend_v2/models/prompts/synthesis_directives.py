"""Centralized synthesis prompt directives and XML mandates.

This module acts as the Single Source of Truth (SSOT) for synthesis prompt blocks,
ensuring strict DRY compliance and zero-hardcoding across workers and hooks.
"""

from backend_v2.models.enums import TargetBlockType

__all__ = [
    "ANTI_JARGON_MANDATE_BLOCK",
    "EXECUTIVE_SUMMARY_DIRECTIVE",
    "EXECUTIVE_SUMMARY_SECTION_ID",
    "MATRIX_1D_SYNTHESIS_DIRECTIVE",
    "MATRIX_2D_SYNTHESIS_DIRECTIVE",
    "MATRIX_3D_SYNTHESIS_DIRECTIVE",
    "MATRIX_TEXT_SYNTHESIS_DIRECTIVE",
    "SDUI_SYNTHESIS_MANDATE_BLOCK",
    "SECTION_SYNTHESIS_DIRECTIVE_BLOCK",
    "SPARSE_DATA_SYNTHESIS_MANDATE",
    "STATE_ISOLATION_BLOCK",
]

SPARSE_DATA_SYNTHESIS_MANDATE: str = (
    "<sparse_data_synthesis_mandate>\n"
    "- CRITICAL SPARSE DATA INSTRUCTION: The evaluation dataset contains minimal atomic evidence.\n"
    "- You MUST be extremely concise, objective, and brief.\n"
    "- You MUST leave sections completely empty (empty strings or empty arrays) if there is no direct supporting data.\n"
    "- Do NOT invent narrative filler, do NOT guess, and do NOT generate generic consultant advice.\n"
    "- If a matrix dimension or report section lacks observations, output an empty structure according to schema.\n"
    "</sparse_data_synthesis_mandate>"
)

ANTI_JARGON_MANDATE_BLOCK: str = (
    "<anti_jargon_mandate>\n"
    "- ANTI-JARGON MANDATE: You MUST NOT use performative consulting clichés, empty buzzwords, or unsubstantiated meta-commentary.\n"
    "- State all findings using direct, plain, evidence-backed statements.\n"
    "</anti_jargon_mandate>"
)

EXECUTIVE_SUMMARY_SECTION_ID: str = TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value

EXECUTIVE_SUMMARY_DIRECTIVE: str = (
    "<executive_summary_directive>\n"
    "EXECUTIVE SUMMARY SYNTHESIS MANDATE:\n"
    "- Synthesize the high-level findings, systemic implications, and strategic executive coaching advice.\n"
    "- Structure the narrative into clear, logical paragraphs using SDUI ParagraphBlocks.\n"
    "- Reference key strengths, vulnerabilities, and strategic focus areas from the evaluated data.\n"
    "</executive_summary_directive>"
)

MATRIX_1D_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_1d_directive>\n"
    "1D METRICS SYNTHESIS MANDATE:\n"
    "- Focus on individual metric thresholds, isolated strengths, and isolated anomalies.\n"
    "- Provide clear, concise analytical takeaway for each evaluated dimension.\n"
    "- Structure your findings directly as SDUI blocks.\n"
    "</matrix_1d_directive>"
)

MATRIX_2D_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_2d_directive>\n"
    "2D COMPARISON SYNTHESIS MANDATE:\n"
    "- Compare and contrast the primary dimension against the secondary dimension.\n"
    "- Identify quadrants, balance, trade-offs, and tensions between the two dimensions.\n"
    "- Structure your findings directly as SDUI blocks.\n"
    "</matrix_2d_directive>"
)

MATRIX_3D_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_3d_directive>\n"
    "3D RADAR SYNTHESIS MANDATE:\n"
    "- Synthesize the holistic systemic profile across all evaluated radar axes.\n"
    "- Identify overall balance, center of gravity, systemic strengths, and critical vulnerabilities.\n"
    "- Structure your findings directly as SDUI blocks.\n"
    "</matrix_3d_directive>"
)

MATRIX_TEXT_SYNTHESIS_DIRECTIVE: str = (
    "<matrix_text_directive>\n"
    "TEXT-ONLY MATRIX SYNTHESIS MANDATE:\n"
    "- Synthesize the evaluated matrix dimensions into a cohesive analytical narrative.\n"
    "- Provide actionable takeaways and contextual explanations for each evaluated topic.\n"
    "- Structure your findings directly as SDUI ParagraphBlocks.\n"
    "</matrix_text_directive>"
)

SDUI_SYNTHESIS_MANDATE_BLOCK: str = (
    "<sdui_synthesis_mandate>\n"
    "- SDUI POLYMORPHIC SYNTHESIS MANDATE: Structure your response by mapping output directly "
    "into the section_syntheses dictionary using the requested layout IDs.\n"
    "- ALLOWED SDUI BLOCKS: 'ParagraphBlock', 'BulletListBlock', 'AlertBlock', 'QuoteBlock'. "
    "NO OTHER TYPES ARE ALLOWED.\n"
    "- NO RECURSION: Nested blocks inside blocks are strictly banned.\n"
    "- NO MARKDOWN: Do not use markdown syntax (like **bold**, *italic*, # headers) inside text fields. "
    "The UI will render text structurally.\n"
    "- CITATIONS ARRAYS: Instead of inline brackets like [1], provide an array of integers in the "
    "`citations: list[int]` field for each block that uses sources.\n"
    "- USER ROLE EXTRACTION: Deduce the user's role (ROLE_PASSENGER, ROLE_NAVIGATOR, ROLE_DRIVER, "
    "ROLE_ARCHITECT) and output it as the uppercase enum constant in `user_role` with reasoning in "
    "`user_role_justification`.\n"
    "</sdui_synthesis_mandate>"
)

SECTION_SYNTHESIS_DIRECTIVE_BLOCK: str = (
    "<section_synthesis_directive>\n"
    "CRITICAL: You MUST place the output for each section_instruction strictly inside the "
    "`sections` array using the exact target `layout_id`. All generated content blocks MUST be "
    "contained within `sections[].content_blocks` for that layout_id. Do NOT put section analysis "
    "in the global executive_summary, and do NOT invent sub-paragraph layout IDs.\n"
    "</section_synthesis_directive>"
)

STATE_ISOLATION_BLOCK: str = (
    "<state_isolation_mandate>\n"
    "STATE ISOLATION MANDATE: If &lt;HistoricalContext&gt; is provided, use it ONLY to understand "
    "the user's past trajectory, growth, or recurring blind spots. YOU MUST NOT synthesize, "
    "summarize, or report on the substantive topics, subjects, or domains discussed in the "
    "historical context. Your output must be STRICTLY based on the current &lt;source_data&gt;.\n"
    "</state_isolation_mandate>"
)
