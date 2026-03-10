"""V2 Seed Registry.
Strictly maps collections to V2 Pydantic models (Zero V1 leak).
"""

from pydantic import TypeAdapter

from backend_v2.models.auth import Organization, User
from backend_v2.models.v2_core import (
    Observation,
    OutputConfig,
    PromptBlock,
    Reference,
    Role,
    Step,
    SystemConfigModelRegistry,
    Workflow,
)

SystemConfigUnion = SystemConfigModelRegistry

STANDARD_REGISTRY = {
    "system_config": {"table": "system_config", "model": TypeAdapter(SystemConfigUnion), "id_field": "id"},
    "workflows": {"table": "workflows", "model": TypeAdapter(Workflow), "id_field": "id"},
    "agents": {"table": "agents", "model": TypeAdapter(Role), "id_field": "id"},
    "prompt_blocks": {"table": "prompt_blocks", "model": TypeAdapter(PromptBlock), "id_field": "id"},
    "steps": {"table": "steps", "model": TypeAdapter(Step), "id_field": "id"},

    # Dynamic Raw V1 Collections Mapping to V2 Strict Types
    "output_configs": {"table": "output_configs", "model": TypeAdapter(OutputConfig), "id_field": "id"},
    "dimensions": {"table": "dimensions", "model": TypeAdapter(Observation), "id_field": "id"},
    "references": {"table": "references", "model": TypeAdapter(Reference), "id_field": "id"},

    # IAM remains shared for now until isolated
    "organizations": {"table": "organizations", "model": TypeAdapter(Organization), "id_field": "id"},
    "users": {"table": "users", "model": TypeAdapter(User), "id_field": "id"},
}
