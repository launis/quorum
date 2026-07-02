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

INTERACTION_RULES = [
    (
        "You must classify the user into one of four roles: ROLE_PASSENGER, ROLE_NAVIGATOR, "
        "ROLE_DRIVER, or ROLE_ARCHITECT."
    ),
    (
        "ROLE_PASSENGER: The user provides minimal input, relying almost entirely on the AI "
        "to lead, structure, and generate content."
    ),
    ("ROLE_NAVIGATOR: The user provides direction and goals but relies on the AI to execute the details."),
    (
        "ROLE_DRIVER: The user actively controls the execution, providing specific constraints, "
        "structural requirements, and detailed data."
    ),
    (
        "ROLE_ARCHITECT: The user defines the entire conceptual framework, methodology, and "
        "strict rules, treating the AI purely as a compiler or executor of their complex design."
    ),
    (
        "HYBRID TRUTH MANDATE: You MUST respect the hard mathematical metrics provided in the "
        "<execution_parameters> tag. The mathematical `control_ratio` is the ultimate baseline. "
        "If the user's control ratio is low, they CANNOT be an Architect, regardless of their tone."
    ),
    ("Do NOT output Markdown. You MUST output ONLY the requested strict JSON schema matching InteractionAnalysisDTO."),
]

# ============================================================================
# SYNTHESIS HOOK RULES (backend_v2/hooks/synthesis.py)
# ============================================================================

SYNTHESIS_CITATION_RULES = (
    "CITATION MANDATE: You must append [srcX] to the end of every sentence that relies on the provided <source_data>."
)
SYNTHESIS_LENGTH_CONSTRAINT = (
    "LENGTH MANDATE: You must adhere strictly to the length constraint specified in <global_length_constraint_chars>."
)
SYNTHESIS_SDUI_MANDATES = [
    "You are a master synthesizer formatting data for SDUI display.",
    "Do NOT output unstructured markdown. Your output MUST strictly follow the JSON schema requested.",
]
SYNTHESIS_SECTION_RULES_PREFIX = (
    "SECTION-LEVEL SYNTHESIS INSTRUCTIONS:\n"
    "Follow these block-specific instructions when generating content for specific layout_id blocks."
)
SYNTHESIS_STATE_ISOLATION_MANDATE = (
    "STATE ISOLATION MANDATE: You must synthesize only the data explicitly provided. Do not hallucinate."
)
SYNTHESIS_XAI_CURATION = "XAI HIGHLIGHTS CURATION: Review the <raw_extensions> XML block. Synthesize and combine all insights across all inputs for each extension category. Create up to <max_extension_items> MOST CRITICAL items for each individual category. Format them as objects in the `xai_highlights` array, ensuring each has an `extension_type` and `content`. Make each item's content an ultra-short, punchy bullet point (max 1 sentence)."
