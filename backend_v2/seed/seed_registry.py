"""V2 Seed Registry.
Strictly maps collections to V2 Pydantic models (Zero V1 leak).
"""

from typing import Annotated

from pydantic import Discriminator, Tag, TypeAdapter

from backend_v2.models.auth import Organization, User
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import (
    ExecutionRecord,
    PromptBlock,
    Role,
    Step,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    Workflow,
)


def _system_config_discriminator(v: dict) -> str:  # type: ignore[type-arg]
    """Polymorphic Seeding: route by 'type' field."""
    if isinstance(v, dict):
        return v.get("type", "model_registry")
    return getattr(v, "type", "model_registry")


SystemConfigUnion = Annotated[
    Annotated[SystemConfigModelRegistry, Tag("model_registry")] | Annotated[SystemConfigMCPGateways, Tag("mcp_gateways")],
    Discriminator(_system_config_discriminator),
]

STANDARD_REGISTRY = {
    "system_config": {"table": "system_config", "model": TypeAdapter(SystemConfigUnion), "id_field": "id"},
    "workflows": {"table": "workflows", "model": TypeAdapter(Workflow), "id_field": "id"},
    "agents": {"table": "agents", "model": TypeAdapter(Role), "id_field": "id"},
    "prompt_blocks": {"table": "prompt_blocks", "model": TypeAdapter(PromptBlock), "id_field": "id"},
    "steps": {"table": "steps", "model": TypeAdapter(Step), "id_field": "id"},
    "output_profiles": {"table": "output_profiles", "model": TypeAdapter(OutputProfile), "id_field": "id"},
    "executions": {"table": "executions", "model": TypeAdapter(ExecutionRecord), "id_field": "id"},

    # IAM remains shared for now until isolated
    "organizations": {"table": "organizations", "model": TypeAdapter(Organization), "id_field": "id"},
    "users": {"table": "users", "model": TypeAdapter(User), "id_field": "id"},
}
