"""V2 Seed Registry.

Strictly maps collections to V2 Pydantic models (Zero V1 leak).
"""

from enum import StrEnum
from typing import Annotated

from pydantic import Discriminator, Tag, TypeAdapter

from backend_v2.models.auth import Organization, User
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow

__all__ = ["STANDARD_REGISTRY", "SeedCollectionName", "SystemConfigUnion"]


class SeedCollectionName(StrEnum):
    """Canonical top-level collection names in seed_data.json."""

    ORGANIZATIONS = "organizations"
    USERS = "users"
    SYSTEM_CONFIG = "system_config"
    PROMPT_BLOCKS = "prompt_blocks"
    TASK_BRIEFS = "task_briefs"
    STEPS = "steps"
    WORKFLOWS = "workflows"
    OUTPUT_PROFILES = "output_profiles"
    EXECUTIONS = "executions"


SystemConfigUnion = Annotated[
    Annotated[SystemConfigModelRegistry, Tag("model_registry")]
    | Annotated[SystemConfigMCPGateways, Tag("mcp_gateways")],
    Discriminator("type"),
]

STANDARD_REGISTRY = {
    "system_config": {"table": "system_config", "model": TypeAdapter(SystemConfigUnion), "id_field": "id"},
    "workflows": {"table": "workflows", "model": TypeAdapter(Workflow), "id_field": "id"},
    "prompt_blocks": {"table": "prompt_blocks", "model": TypeAdapter(AnyPromptBlock), "id_field": "id"},
    "task_briefs": {"table": "task_briefs", "model": TypeAdapter(TaskBrief), "id_field": "id"},
    "steps": {"table": "steps", "model": TypeAdapter(Step), "id_field": "id"},
    "output_profiles": {"table": "output_profiles", "model": TypeAdapter(OutputProfile), "id_field": "id"},
    "executions": {"table": "executions", "model": TypeAdapter(ExecutionRecord), "id_field": "id"},
    # IAM remains shared for now until isolated
    "organizations": {"table": "organizations", "model": TypeAdapter(Organization), "id_field": "id"},
    "users": {"table": "users", "model": TypeAdapter(User), "id_field": "id"},
}
