"""V2 Seed Registry.
Strictly maps collections to V2 Pydantic models (Zero V1 leak).
"""

from typing import Annotated, Any

from pydantic import Discriminator, Tag, TypeAdapter

from backend_v2.models.auth import Organization, User
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.v2_core import (
    ExecutionRecord,
    OutputProfile,
    Step,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigPerformativeLexicons,
    Workflow,
)


def _system_config_discriminator(v: dict[str, Any] | Any) -> str:
    """Polymorphic Seeding: route by 'type' field.

    Args:
        v: The raw dictionary or object being validated.

    Returns:
        The discriminator string.
    """
    if isinstance(v, dict):
        return str(v["type"])
    return str(v.type)


SystemConfigUnion = Annotated[
    Annotated[SystemConfigModelRegistry, Tag("model_registry")]
    | Annotated[SystemConfigMCPGateways, Tag("mcp_gateways")]
    | Annotated[SystemConfigPerformativeLexicons, Tag("performative_lexicons")],
    Discriminator(_system_config_discriminator),
]

STANDARD_REGISTRY = {
    "system_config": {"table": "system_config", "model": TypeAdapter(SystemConfigUnion), "id_field": "id"},
    "workflows": {"table": "workflows", "model": TypeAdapter(Workflow), "id_field": "id"},
    "prompt_blocks": {"table": "prompt_blocks", "model": TypeAdapter(AnyPromptBlock), "id_field": "id"},
    "steps": {"table": "steps", "model": TypeAdapter(Step), "id_field": "id"},
    "output_profiles": {"table": "output_profiles", "model": TypeAdapter(OutputProfile), "id_field": "id"},
    "executions": {"table": "executions", "model": TypeAdapter(ExecutionRecord), "id_field": "id"},
    # IAM remains shared for now until isolated
    "organizations": {"table": "organizations", "model": TypeAdapter(Organization), "id_field": "id"},
    "users": {"table": "users", "model": TypeAdapter(User), "id_field": "id"},
}
