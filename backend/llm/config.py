"""LLM Configuration Module.

Defines Rate Limits (TPM/RPM) for specific models to be enforced by LiteLLM Router.
"""

from typing import TypedDict


class ModelLimit(TypedDict):
    """Type definition for Token and Request Rate Limits."""

    tpm: int
    rpm: int


# Default Limits based on typical Scaled Tier (e.g. Tier 2/3)
# These should ideally come from DB/Env, but hardcoded as baseline for V2.9.
MODEL_LIMITS: dict[str, ModelLimit] = {
    # Google Vertex AI / Gemini
    "gemini-1.5-pro": {"tpm": 100000, "rpm": 60},
    "gemini-1.5-flash": {"tpm": 500000, "rpm": 120},
    "gemini-2.0-flash-exp": {"tpm": 500000, "rpm": 120},  # Experimental
    # OpenAI
    "gpt-4o": {"tpm": 30000, "rpm": 100},
    "gpt-4o-mini": {"tpm": 100000, "rpm": 200},
    "o1-mini": {"tpm": 100000, "rpm": 100},
    # Anthropic
    "claude-3-5-sonnet@20240620": {"tpm": 40000, "rpm": 50},
}
