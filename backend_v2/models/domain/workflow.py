"""Domain model for dynamic DAG workflows.

SSOT for Workflow orchestrator model.
"""

from __future__ import annotations

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.enums import LaxHistoricalContextMode, TargetBlockType

logger = logging.getLogger(__name__)

__all__ = [
    "Workflow",
]


class Workflow(V2CoreBase):
    """Dynamic Directed Acyclic Graph orchestrator model."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Unique Workflow ID")
    slug: str
    name: I18nText | str
    description: I18nText | str
    status: str
    version: int
    is_public: bool = Field(default=False)
    organization_id: str | None = Field(default=None)
    default_profile_id: Annotated[
        str | None,
        Field(default=None, description="The ID of the default output profile to use."),
    ] = None
    mcp_gateway_id: str | None = Field(
        default="sys_8172bda70c8641c5",
        pattern=r"^sys_[a-fA-F0-9]{16,32}$",
        description="The system_config ID of the MCP gateways configuration attached to this workflow.",
    )
    model_registry_id: str = Field(
        pattern=r"^(sys_[a-fA-F0-9]{16,32}|cfg_model_registry_\d{2})$",
        description="System config ID of the attached model registry",
    )
    default_strictness_level: Annotated[
        int,
        Field(default=50, ge=0, le=100, description="Sovereign workflow strictness level (0-100 continuous)."),
    ] = 50
    security_penalty: Annotated[
        float,
        Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Penalty ratio for security threats (default 0.0 = no penalty).",
        ),
    ] = 0.0
    post_hoc_penalty: Annotated[
        float,
        Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Penalty ratio for post-hoc rationalization (default 0.0 = no penalty).",
        ),
    ] = 0.0
    passivity_penalty: Annotated[
        float,
        Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Penalty ratio for passivity or lowest-quality score (default 0.0 = no penalty).",
        ),
    ] = 0.0
    enable_contextual_overrides: bool = Field(
        default=False,
        description="Global flag to enable contextual overrides across assertions.",
    )
    enable_semantic_smoothing: bool = Field(
        default=False,
        description=(
            "If True, uses SpaCy to fix hyphenations and merge broken PDF lines into cohesive semantic sentences."
        ),
    )
    enable_eager_anonymization: bool = Field(
        default=False,
        description=(
            "If True, Microsoft Presidio will mask all PII data from raw inputs before they enter the system state."
        ),
    )
    system_audit_trail: bool = Field(
        default=False,
        description="If True, activates the background XAI Citation Extraction tracking mechanism.",
    )
    expected_inputs: list[ExpectedInput] = Field(
        default_factory=list,
        description="List of dynamic expected inputs required by the workflow",
    )
    steps: list[StepRule] = Field(default_factory=list)
    historical_context_mode: Annotated[
        LaxHistoricalContextMode,
        Field(description="Mode for fetching historical context at workflow level."),
    ]

    @model_validator(mode="after")
    def validate_dag_integrity(self) -> Workflow:
        """Enforces Directed Acyclic Graph (DAG) structural integrity.

        Raises:
            AppException: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized Workflow matching schema expectations.
        """
        step_ids = {step.id for step in self.steps}
        graph: dict[str, list[str]] = {step.id: [] for step in self.steps}

        # 1. Orphan Reference Check
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    msg = f"Step '{step.id}' depends on '{dep}', which does not exist in this workflow."
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)
                graph[step.id].append(dep)

        # 2. Cycle Detection (DFS)
        visited = set()
        rec_stack = set()

        def is_cyclic(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in step_ids:
            if node not in visited:
                if is_cyclic(node):
                    msg = (
                        f"Circular dependency detected involving step '{node}'. "
                        "Workflows must be strict Directed Acyclic Graphs (DAG)."
                    )
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)

        return self

    def get_allowed_layout_targets(self, hydrated_steps: list[Step]) -> set[str]:
        """Calculates all allowed layout targets including system blocks.

        Args:
            hydrated_steps: List of full Step objects from the database.

        Returns:
            A set of allowed block IDs and system TargetBlockTypes.
        """
        allowed_blocks = set()

        # 1. Add blocks from the hydrated steps that belong to this workflow
        task_blueprints = {rule.task_blueprint for rule in self.steps}
        for step in hydrated_steps:
            if step.id in task_blueprints:
                if step.role_block_id:
                    allowed_blocks.add(step.role_block_id)
                if step.extraction_protocol_block_id:
                    allowed_blocks.add(step.extraction_protocol_block_id)
                if step.criteria_block_ids:
                    allowed_blocks.update(step.criteria_block_ids)

        # 2. Add system blocks natively supported by the architecture
        allowed_blocks.update([e.value for e in TargetBlockType])

        return allowed_blocks
