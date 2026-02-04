"""Service for validatiing workflow configurations."""

import logging
from typing import Any

from backend.dependencies import RegistryDep

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
        known_keys = ["history_text", "product_text", "reflection_text", "bibliography_context"]
        errors = []
        trace_log: list[str] = []
        pseudo_state = list(known_keys)

        # Cache for loaded classes to avoid repeated imports
        loaded_classes = {}

        for i, step_id in enumerate(sequence):
            if step_id not in steps_db_map:
                errors.append(f"Unknown Step: {step_id}")
                continue

            step_doc = steps_db_map[step_id]
            # Support both new 'task_key' and legacy 'component'
            agent_ref = step_doc.get("task_key") or step_doc.get("component")

            if not agent_ref:
                errors.append(f"Step {step_id} missing task_key or component")
                continue

            # Resolve Agent Class dynamically
            if agent_ref in loaded_classes:
                agent_class = loaded_classes[agent_ref]
            else:
                # Ask AgentRegistry for component details
                # We need to access the repo behind the registry
                # registry is AgentRegistry instance
                comp = await registry.repository.get_component_by_name(agent_ref)
                if not comp:
                     errors.append(f"Unknown Agent/Task: {agent_ref} in {step_id}")
                     continue

                module_name = comp.get("module")
                class_name = comp.get("class_name")

                if not module_name or not class_name:
                    errors.append(f"Corrupt Registry: {agent_ref} missing module/class info")
                    continue

                try:
                    import importlib
                    mod = importlib.import_module(module_name)
                    agent_class = getattr(mod, class_name)
                    loaded_classes[agent_ref] = agent_class
                except Exception as e:
                    errors.append(f"Failed to load code for {agent_ref}: {e}")
                    continue

            # Static Inspection of Class Attributes
            reqs = getattr(agent_class, "REQUIRES_KEYS", [])
            missing = [r for r in reqs if r not in pseudo_state]
            if missing:
                errors.append(f"Step {i + 1} ({agent_ref}) Missing Inputs: {missing}")

            prods = getattr(agent_class, "PRODUCES_KEYS", [])
            for k in prods:
                if k not in pseudo_state:
                    pseudo_state.append(k)

        return {"valid": len(errors) == 0, "errors": errors, "trace": trace_log, "final_state_keys": pseudo_state}
