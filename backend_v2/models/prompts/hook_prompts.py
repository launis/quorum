"""Centralized prompt instructions and mandates specific to individual hooks.

This module enforces DRY by moving large prompt strings out of the business logic
(hooks/*.py) and into the centralized prompt architecture models.
"""

# ============================================================================
# INTERACTION HOOK RULES (backend_v2/hooks/interaction_hook.py)
# ============================================================================

INTERACTION_OBJECTIVE = (
    "Analyze the user's interaction behavior and assign a precise cognitive role based on "
    "the provided conversation history and hard mathematical heuristics."
)

INTERACTION_RULES = (
    "<interaction_rules>\n"
    "- You must classify the user into one of four roles: ROLE_PASSENGER, ROLE_NAVIGATOR, "
    "ROLE_DRIVER, or ROLE_ARCHITECT.\n"
    "- ROLE_PASSENGER: The user provides minimal input, relying almost entirely on the AI "
    "to lead, structure, and generate content.\n"
    "- ROLE_NAVIGATOR: The user provides direction and goals but relies on the AI to execute the details.\n"
    "- ROLE_DRIVER: The user actively controls the execution, providing specific constraints, "
    "structural requirements, and detailed data.\n"
    "- ROLE_ARCHITECT: The user defines the entire conceptual framework, methodology, and "
    "strict rules, treating the AI purely as a compiler or executor of their complex design.\n"
    "- HYBRID TRUTH MANDATE: You MUST respect the hard mathematical metrics provided in the "
    "<execution_parameters> tag. The mathematical `control_ratio` is the ultimate baseline. "
    "If the user's control ratio is low, they CANNOT be an Architect, regardless of their tone.\n"
    "- Do NOT output Markdown. You MUST output ONLY the requested strict JSON schema matching InteractionAnalysisDTO.\n"
    "</interaction_rules>"
)

# ============================================================================
# SYNTHESIS HOOK RULES (backend_v2/hooks/synthesis.py)
# ============================================================================

SYNTHESIS_SDUI_MANDATES = (
    "<sdui_mandate>\n"
    "- SDUI CONTENT BLOCKS MANDATE: You must structure your entire response using ONLY "
    "the allowed SDUI `content_blocks`.\n"
    "- ALLOWED SDUI BLOCKS: 'paragraph', 'bullet_list', 'alert_box', 'quote_card', 'warning_card'. "
    "NO OTHER TYPES ARE ALLOWED.\n"
    '- BULLET LISTS MUST USE OBJECTS: For `bullet_list`, the `items` array MUST contain objects with a `text` field (e.g. `[{"text": "kohta 1"}]`), NOT raw strings!\n'
    "- NO RECURSION: Nested blocks inside blocks are strictly banned.\n"
    "- MCP CITATIONS: When citing information retrieved via ANY external tool (e.g., Jira, Web Search), you MUST use the exact tool call ID or the tool's defined identifier as the `source_id`.\n"
    "- NO MARKDOWN: Do not use markdown syntax (like **bold**, *italic*, # headers) inside "
    "text fields. The UI will render text structurally.\n"
    "- CITATIONS ARRAYS: Instead of inline brackets like [1], you must provide an array of "
    "integers in the `citations: list[int]` field for each block that uses sources.\n"
    "- USER ROLE EXTRACTION (CRITICAL): You MUST deduce the user's role (ROLE_PASSENGER, ROLE_NAVIGATOR, ROLE_DRIVER, ROLE_ARCHITECT) and output it EXACTLY as the uppercase enum constant in the JSON field `user_role`. Provide reasoning in `user_role_justification`.\n"
    "- ROLE TRANSLATION: Do NOT translate role constants. Output them exactly as they are so the UI can translate and format them.\n"
    "</sdui_mandate>"
)

SYNTHESIS_XAI_CURATION = (
    "<xai_curation_mandate>\n"
    "XAI HIGHLIGHTS CURATION: Review the `extensions` fields inside the input data (if any). Synthesize and combine "
    "all insights across all inputs for the requested extension categories: <requested_extensions>. "
    "Create up to <max_extension_items> MOST CRITICAL items for each requested category. Format them as objects in the "
    "`xai_highlights` array, ensuring each has an `extension_type` EXACTLY matching one of the requested categories, and `content`. "
    "Make each item's content an ultra-short, punchy bullet point (max 1 sentence).\n"
    "</xai_curation_mandate>"
)

SYNTHESIS_LENGTH_CONSTRAINT = (
    "<length_constraint>\n"
    "GLOBAL SYNTHESIS LENGTH CONSTRAINT: The global output should be roughly the length "
    "specified in <global_length_constraint_chars>.\n"
    "</length_constraint>"
)

SYNTHESIS_SECTION_RULES_PREFIX = (
    "<section_rules>\n"
    "## Section-Level Synthesis\n"
    "- CRITICAL BREVITY MANDATE: Limit every section summary to an absolute maximum of 2-3 "
    "short sentences.\n"
    "- You MUST ALSO provide targeted synthesized summaries for the following distinct "
    "sections as an array in `section_syntheses`.\n\n"
)

SYNTHESIS_CITATION_RULES = (
    "<citation_rules>\n"
    "Omit internal system identifiers or raw JSON keys. When referring to information, use "
    "inline numerical tags like [1], [2].\n"
    "CRITICAL RULE FOR CITATIONS: The numbers in your inline tags MUST perfectly correspond "
    "to the items in the `cited_sources` list (1-indexed). ONLY create a numerical citation "
    "tag AND add an entry to `cited_sources` if the source is an actual literary reference, "
    "empirical citation, methodology framework, or external document. DO NOT use citation tags for general analysis sections, step titles, "
    "or internal data dumps. If you mention internal findings, state them directly without "
    "using it.\n"
    "</citation_rules>"
)

SYNTHESIS_STATE_ISOLATION_MANDATE = (
    "<state_isolation_mandate>\n"
    "STATE ISOLATION MANDATE: If <HistoricalContext> is provided, use it ONLY to understand "
    "the user's past trajectory, growth, or recurring blind spots. YOU MUST NOT synthesize, "
    "summarize, or report on the substantive topics, subjects, or domains discussed in the "
    "historical context. Your output must be STRICTLY based on the current <source_data>.\n"
    "</state_isolation_mandate>"
)
