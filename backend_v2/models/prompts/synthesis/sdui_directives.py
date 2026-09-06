"""SDUI structural and layout-routing prompt mandates (Synthesis Layer).

Single Source of Truth (SSOT) for structural presentation rules, allowed block discriminators,
section placement instructions, and historical context state isolation.
"""

__all__ = [
    "SDUI_BLOCK_STRUCTURE_MANDATE",
    "SDUI_SYNTHESIS_MANDATE_BLOCK",
    "SECTION_SYNTHESIS_DIRECTIVE_BLOCK",
    "STATE_ISOLATION_BLOCK",
    "SYNTHESIS_SDUI_MANDATES",
]

SDUI_BLOCK_STRUCTURE_MANDATE: str = (
    "<sdui_block_structure_mandate>\n"
    "- UNIVERSAL SDUI PRESENTATION RULE: Structure all report findings directly as Server-Driven UI (SDUI) blocks.\n"
    "- Format each analytical observation into an allowed block type ('paragraph', 'bullet_list', 'alert_box', 'quote_card', 'warning_card').\n"
    "</sdui_block_structure_mandate>"
)

SYNTHESIS_SDUI_MANDATES: str = (
    "<sdui_mandate>\n"
    "- SDUI POLYMORPHIC SYNTHESIS MANDATE: You must structure your entire response by mapping your output directly into the section_syntheses dictionary according to the requested layout IDs.\n"
    "- ALLOWED SDUI BLOCKS: 'paragraph', 'bullet_list', 'alert_box', 'quote_card', 'warning_card'. "
    "NO OTHER TYPES ARE ALLOWED.\n"
    '- BULLET LISTS MUST USE OBJECTS: For `bullet_list`, the `items` array MUST contain objects with a `text` field (e.g. `[{"text": "kohta 1"}]`), NOT raw strings!\n'
    "- NO RECURSION: Nested blocks inside blocks are strictly banned.\n"
    "- MCP CITATIONS: When citing information retrieved via ANY external tool (e.g., Jira, Web Search), you MUST use the exact tool call ID or the tool's defined identifier as the `source_id`.\n"
    "- NO MARKDOWN: Do not use markdown syntax (like **bold**, *italic*, # headers) inside "
    "text fields. The UI will render text structurally.\n"
    "- CITATIONS ARRAYS: Instead of inline brackets like [1], you must provide an array of "
    "integers in the `citations: list[int]` field for each block that uses sources.\n"
    "</sdui_mandate>"
)

# Alias for backward compatibility across modules
SDUI_SYNTHESIS_MANDATE_BLOCK: str = SYNTHESIS_SDUI_MANDATES

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
