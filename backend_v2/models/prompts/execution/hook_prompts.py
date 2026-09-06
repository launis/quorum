"""Centralized prompt instructions and mandates for execution hooks (Execution Layer).

Focuses strictly on user interaction role detection during Phase 1 DAG runs.
"""

__all__ = [
    "INTERACTION_OBJECTIVE",
    "INTERACTION_RULES",
]

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
