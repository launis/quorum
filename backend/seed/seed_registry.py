from pydantic import TypeAdapter

from backend.models.auth import Organization, User

# removed KBItem import
from backend.models.dtos.config import (
    AgentComponentResponse,
    ComponentResponse,
    ConfigComponentResponse,
    DimensionDefinition,
    MatrixComponentResponse,
    StepDefinition,
)
from backend.models.llm import AgentSystemConfig, LLMProviderConfig, ModelRegistryConfig
from backend.models.workflow import WorkflowDefinition

SystemConfigItem = LLMProviderConfig | AgentSystemConfig | ModelRegistryConfig | ConfigComponentResponse

from backend.models.domain.knowledge_items import KBClaim, KBConcept, KBReference

# Define Universal Registry for Seed Scripts (Single Source of Truth)
STANDARD_REGISTRY = {
    "workflows": {"table": "workflows", "model": TypeAdapter(WorkflowDefinition), "id_field": "id"},
    "concepts": {"table": "concepts", "model": TypeAdapter(KBConcept), "id_field": "id"},
    "claims": {"table": "claims", "model": TypeAdapter(KBClaim), "id_field": "id"},
    "references": {"table": "references", "model": TypeAdapter(KBReference), "id_field": "id"},
    "dimensions": {"table": "dimensions", "model": TypeAdapter(DimensionDefinition), "id_field": "id"},
    "organizations": {"table": "organizations", "model": TypeAdapter(Organization), "id_field": "id"},
    "users": {"table": "users", "model": TypeAdapter(User), "id_field": "id"},
    "steps": {"table": "steps", "model": TypeAdapter(StepDefinition), "id_field": "id"},
    "agents": {"table": "agents", "model": TypeAdapter(AgentComponentResponse), "id_field": "id"},
    "components": {"table": "components", "model": TypeAdapter(ComponentResponse), "id_field": "id"},
    "matrices": {"table": "matrices", "model": TypeAdapter(MatrixComponentResponse), "id_field": "id"},
    "output_configs": {"table": "output_configs", "model": TypeAdapter(ConfigComponentResponse), "id_field": "id"},
    "system_config": {"table": "system_config", "model": TypeAdapter(SystemConfigItem), "id_field": "id"},
}
