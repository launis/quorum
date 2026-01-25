"""Service for validatiing workflow configurations."""

import logging
from typing import Any

from fastapi import status

from backend.core.factory import AgentFactory
from backend.dependencies import RegistryDep
from backend.exceptions import AppException

logger = logging.getLogger(__name__)


class WorkflowValidator:
    """Service to validate workflow configurations."""

    @staticmethod
    async def validate_flow_configuration(
        sequence: list[str], steps_db_map: dict[str, Any], registry: RegistryDep
    ) -> dict[str, Any]:
        """Dry run validation logic extracted from router.

        Args:
            sequence: List of Step IDs to validate.
            steps_db_map: Dictionary of all available steps from DB.
            registry: The model registry dependency.

        Returns:
            Validation report dict.
        """
        # Strict Resolution: Use 'fast' strategy for validation dry-run
        try:
            config = await registry.resolve_model_config("fast")
            agents_map = AgentFactory.create_agents_map(initial_model=config["model_name"])
        except Exception as e:
            error_code = "FACTORY_ERROR"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message="Agent factory failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code, "original_error": str(e)},
            ) from e

        known_keys = ["history_text", "product_text", "reflection_text", "bibliography_context"]
        errors = []
        trace_log: list[str] = []
        pseudo_state = list(known_keys)

        for i, step_id in enumerate(sequence):
            if step_id not in steps_db_map:
                errors.append(f"Unknown Step: {step_id}")
                continue
            step_doc = steps_db_map[step_id]
            agent_name = step_doc.get("component")
            if not agent_name or agent_name not in agents_map:
                errors.append(f"Unknown Agent: {agent_name} in {step_id}")
                continue
            agent_instance = agents_map[agent_name]
            reqs = getattr(agent_instance, "REQUIRES_KEYS", [])
            missing = [r for r in reqs if r not in pseudo_state]
            if missing:
                errors.append(f"Step {i + 1} Missing: {missing}")
            prods = getattr(agent_instance, "PRODUCES_KEYS", [])
            for k in prods:
                if k not in pseudo_state:
                    pseudo_state.append(k)

        return {"valid": len(errors) == 0, "errors": errors, "trace": trace_log, "final_state_keys": pseudo_state}
