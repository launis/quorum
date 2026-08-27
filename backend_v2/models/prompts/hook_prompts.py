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
    "correction, and guidance.\n"
    "- ROLE_ARCHITECT: The user proactively provides high-level architectural schemas, defines "
    "system boundaries, and orchestrates multi-agent flows.\n"
    "- HEURISTIC CONSTRAINTS: You must calculate your classification against the raw metrics in the "
    "<execution_parameters> tag. The mathematical `control_ratio` is the ultimate baseline. "
    "If the user's control ratio is low, they CANNOT be an Architect, regardless of their tone.\n"
    "- Do NOT output Markdown. You MUST output ONLY the requested strict JSON schema matching InteractionAnalysisDTO.\n"
    "</interaction_rules>"
)

SYNTHESIS_XAI_CURATION = (
    "<xai_curation_mandate>\n"
    "XAI HIGHLIGHTS CURATION: Review the `extensions` fields inside the input data (if any). Synthesize and combine "
    "all insights across all inputs for the requested extension categories: <requested_extensions>. "
    "Create up to <max_extension_items> MOST CRITICAL items for each requested category. Format them as objects in the "
    "`xai_highlights` array, ensuring each has an `extension_type` EXACTLY matching one of the requested categories, and `content`. "
    "Make each item's content an ultra-short, punchy bullet point (max 1 sentence).\n"
    "CRITICAL LANGUAGE MANDATE: All synthesized items MUST be generated in the <required_output_language>. Do NOT use English unless explicitly requested.\n"
    "</xai_curation_mandate>"
)

SYNTHESIS_SECTION_RULES_PREFIX = (
    "<section_rules>\n"
    "## Section-Level Synthesis\n"
    "- CRITICAL BREVITY MANDATE: Limit every section summary to an absolute maximum of 2-3 "
    "short sentences.\n"
    "- You MUST ALSO provide targeted synthesized summaries for the following distinct "
    "sections as an array in `section_syntheses`.\n\n"
)
