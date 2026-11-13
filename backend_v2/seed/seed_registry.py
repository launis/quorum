"""V2 Seed Registry.

Strictly maps collections to V2 Pydantic models (Zero V1 leak).
"""

from enum import StrEnum

from pydantic import TypeAdapter

from backend_v2.models.auth import Organization, User
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow

__all__ = ["STANDARD_REGISTRY", "SeedCollectionName"]


class SeedCollectionName(StrEnum):
    """Canonical top-level collection names in seed_data.json."""

    ORGANIZATIONS = "organizations"
    USERS = "users"
    MODEL_REGISTRIES = "model_registries"
    MCP_GATEWAYS = "mcp_gateways"
    PROMPT_BLOCKS = "prompt_blocks"
    TASK_BRIEFS = "task_briefs"
    STEPS = "steps"
    WORKFLOWS = "workflows"
    OUTPUT_PROFILES = "output_profiles"
    EXECUTIONS = "executions"


STANDARD_REGISTRY = {
    "model_registries": {
        "table": "model_registries",
        "model": TypeAdapter(SystemConfigModelRegistry),
        "id_field": "id",
    },
    "mcp_gateways": {
        "table": "mcp_gateways",
        "model": TypeAdapter(SystemConfigMCPGateways),
        "id_field": "id",
    },
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
