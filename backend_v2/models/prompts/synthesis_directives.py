"""Centralized synthesis prompt directives and XML mandates.

This module acts as the Single Source of Truth (SSOT) for synthesis prompt blocks,
ensuring strict DRY compliance and zero-hardcoding across workers and hooks.
"""

__all__ = [
    "MATRIX_1D_SYNTHESIS_DIRECTIVE",
    "MATRIX_2D_SYNTHESIS_DIRECTIVE",
    "MATRIX_3D_SYNTHESIS_DIRECTIVE",
    "SDUI_SYNTHESIS_MANDATE_BLOCK",
    "SECTION_SYNTHESIS_DIRECTIVE_BLOCK",
    "STATE_ISOLATION_BLOCK",
]

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
    "`section_syntheses` dictionary using its exact `layout_id`. Do NOT put section analysis in "
    "the global executive_summary.\n"
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
