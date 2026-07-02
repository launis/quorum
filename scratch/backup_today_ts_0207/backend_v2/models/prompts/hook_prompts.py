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
