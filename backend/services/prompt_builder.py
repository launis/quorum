import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

import requests

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import StepNotFoundError, WorkflowNotFoundError
from backend.services.agent_registry import AgentRegistry

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Service responsible for constructing, enriching, and formatting LLM prompts.
    Handles dynamic variables, state injection, and schema exemplars.
    """

    def __init__(self, repository: AbstractWorkflowRepository, agent_registry: AgentRegistry):
        """
        Initializes PromptBuilder.

        Args:
            repository (AbstractWorkflowRepository): Storage for prompt templates.
            agent_registry (AgentRegistry): Service to lookup agent schemas.
        """
        self.repository = repository
        self.registry = agent_registry

    async def construct_prompt(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        """
        Fetches the step configuration and constructs the full system prompt
        by concatenating the content of all referenced prompt components.
        Injects dynamic variables (e.g., {{HISTORY_TEXT}}) if state is provided.
        """
        try:
            step_data = await self.repository.get_step_by_id(step_id)
            if not step_data:
                return ""

            # 1. Resolve Components
            prompt_parts = await self._resolve_prompt_components(step_data)

            # 2. Process Placeholders
            processed_parts = []
            for content in prompt_parts:
                # Banned Phrases
                content = await self._inject_banned_phrases(content)

                # State Variables
                if current_state:
                    content = self._inject_state_variables(content, current_state)

                # Global Variables
                content = self._inject_global_variables(content)

                # Schema Examples
                content = self._inject_schema_example(content, step_data)

                processed_parts.append(content)

            # Logging
            logger.debug(f"[PromptBuilder] Constructed PROMPT for {step_id} (Length: {len(processed_parts)} parts)")

            return "\n\n".join(processed_parts)
        except Exception as e:
            logger.error(f"[PromptBuilder] Error constructing prompt for step {step_id}: {e}")
            return ""

    # --- HELPER METHODS ---

    async def _resolve_prompt_components(self, step_data: Dict[str, Any]) -> list[str]:
        """
        Fetches content from all prompt components linked to the step.
        Resolves references stored in 'execution_config.llm_prompts'.
        """
        exec_config = step_data.get("execution_config", {})
        prompt_ids = exec_config.get("llm_prompts", [])
        parts = []

        for pid in prompt_ids:
            comp = await self.repository.get_component_by_id(pid)
            if comp:
                content = comp.get("content", "")
                if content:
                    if isinstance(content, list):
                        content = "\n".join(str(x) for x in content)
                    elif isinstance(content, dict):
                        if "text" in content:
                            ct = content["text"]
                            if "scale" in content:
                                s = content["scale"]
                                ct += "\n(SCORING SCALE: " + str(s.get("min", 1)) + " - " + str(s.get("max", 5)) + ")"
                            content = ct
                        else:
                            content = json.dumps(content, indent=2, ensure_ascii=False)
                    parts.append(content)
        return parts

    async def _inject_banned_phrases(self, content: str) -> str:
        """Injects the list of banned phrases into the {{BANNED_PHRASES}} placeholder."""
        if "{{BANNED_PHRASES}}" in content:
            phrases = [p["phrase"] for p in await self.repository.get_banned_phrases()]
            phrases_str = ", ".join([f'"{p}"' for p in phrases]) if phrases else "NONE"
            return content.replace("{{BANNED_PHRASES}}", phrases_str)
        return content

    def _inject_global_variables(self, content: str) -> str:
        """Injects environment data (Date, Time, Location) into placeholders."""
        if "{{CURRENT_DATE}}" in content:
            now_str = datetime.now().strftime("%d.%m.%Y")
            content = content.replace("{{CURRENT_DATE}}", now_str)

        if "{{DYNAMIC_TIME}}" in content:
            # Simple server time, e.g. 14:30
            time_str = datetime.now().strftime("%H:%M")
            content = content.replace("{{DYNAMIC_TIME}}", time_str)

        if "{{DYNAMIC_LOCATION}}" in content:
            location_str = ""
            try:
                # Short timeout to avoid blocking execution
                global_ip_api = "https://ipapi.co/json/"
                response = requests.get(global_ip_api, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    city = data.get("city")
                    country = data.get("country_name")
                    if city and country:
                        location_str = f"SIJAINTI: {city}, {country}."
            except Exception as e:
                # Fail silently/gracefully if no connection or timeout
                logger.warning(f"Failed to fetch dynamic location: {e}")

            content = content.replace("{{DYNAMIC_LOCATION}}", location_str)

        return content

    def _inject_state_variables(self, content: str, state: WorkflowState) -> str:
        """
        Injects dynamic values from the WorkflowState.
        Handles History, Product, Reflection, and previous outputs.
        """
        replacements = {
            "{{CURRENT_STEP_NAME}}": state.current_step_name or "Unknown",
            "{{HISTORY_TEXT}}": state.inputs.history_text,
            "{{PRODUCT_TEXT}}": state.inputs.product_text,
            "{{REFLECTION_TEXT}}": state.inputs.reflection_text,
            "{{PREVIOUS_STEP_OUTPUTS}}": state.get_previous_outputs_summary(),
        }

        for key, value in replacements.items():
            if key in content:
                content = content.replace(key, str(value))

        if "{{GOOGLE_SEARCH_RESULTS}}" in content:
            search_res = state.aux_data.get("google_search_results", "[]")
            content = content.replace("{{GOOGLE_SEARCH_RESULTS}}", str(search_res))

        if "{{PROFILER_METRICS}}" in content:
            metrics = state.aux_data.get("profiler_metrics", {})
            content = content.replace("{{PROFILER_METRICS}}", json.dumps(metrics, indent=2))

        return content

    def _inject_schema_example(self, content: str, step_data: Dict[str, Any]) -> str:
        """Injects a JSON schema example for the target agent into {{SCHEMA_EXAMPLE}}."""
        if "{{SCHEMA_EXAMPLE}}" not in content:
            return content

        agent_name = step_data.get("component")
        schema_example = "{}"

        if agent_name:
            agent_instance = self.registry.get_agent(agent_name)
            if agent_instance:
                schema_example = self._generate_schema_json(agent_instance)

        return content.replace("{{SCHEMA_EXAMPLE}}", str(schema_example))

    def _generate_schema_json(self, agent_instance: Any) -> str:
        """
        Extracts JSON schema example from an agent instance.
        """
        try:
            if hasattr(agent_instance, "get_response_schema"):
                schema_class = agent_instance.get_response_schema()
                if not schema_class:
                    return "{}"

                # Prefer Pydantic v2: model_json_schema()
                if hasattr(schema_class, "model_json_schema"):
                    try:
                        schema_json = schema_class.model_json_schema()
                        if (
                            "examples" in schema_json
                            and isinstance(schema_json["examples"], list)
                            and schema_json["examples"]
                        ):
                            return json.dumps(schema_json["examples"][0], indent=2, ensure_ascii=False)

                        if hasattr(schema_class, "Config") and hasattr(schema_class.Config, "json_schema_extra"):
                            extra = schema_class.Config.json_schema_extra
                            if isinstance(extra, dict) and "examples" in extra:
                                return json.dumps(extra["examples"][0], indent=2, ensure_ascii=False)

                        return json.dumps(schema_json, indent=2, ensure_ascii=False)
                    except Exception as e:
                        logger.warning(f"Failed to dump model_json_schema for {agent_instance.__class__.__name__}: {e}")

                from backend.llm.mock_data import get_example_for_agent

                mock_example = get_example_for_agent(agent_instance.__class__.__name__)
                if mock_example:
                    return json.dumps(mock_example, indent=2, ensure_ascii=False)

            return "Error: Agent schema extraction failed."
        except Exception as e:
            return f"Error generating schema example: {str(e)}"

    async def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        """
        Generates a preview of the prompt for a specific step.
        """
        # 1. Fetch Step Record
        step_data = await self.repository.get_step_by_id(step_id)
        if not step_data:
            raise StepNotFoundError(step_id)

        agent_class = step_data.get("component", "UnknownAgent")

        # 2. Construct Prompt
        prompt = await self.construct_prompt(step_id)
        if not prompt:
            logger.warning(f"Constructed prompt empty for {step_id}")

        # 3. Return Structured Data for UI
        preview_data = {
            "agent_class": agent_class,
            "system_instruction": prompt,
            "user_prompt": "Template Logic Not Available",
        }

        # Try to get the User Prompt Template from the Agent Class
        agent_instance = self.registry.get_agent(agent_class)
        if agent_instance:
            try:
                preview_data["user_prompt"] = agent_instance.get_user_prompt_template()
            except Exception as e:
                preview_data["user_prompt"] = f"Error retrieving template: {e}"

        return preview_data

    async def preview_full_chain_prompts(self, workflow_id: str) -> str:
        """
        Generates a markdown concatenation of ALL prompts in a workflow.
        """
        wf_record = await self.repository.get_workflow_by_id(workflow_id)
        if not wf_record:
            raise WorkflowNotFoundError(workflow_id)

        steps_ids = wf_record.get("steps", [])
        full_chain = []

        full_chain.append(f"# Workflow: {wf_record.get('name', 'Untitled')}")
        full_chain.append(f"ID: {workflow_id}\n")

        for i, step_id in enumerate(steps_ids):
            prompt = await self.construct_prompt(step_id)

            # Fetch step name/component for header
            s_rec = await self.repository.get_step_by_id(step_id)
            step_name = s_rec.get("id", step_id) if s_rec else step_id
            component = s_rec.get("component", "Unknown") if s_rec else "Unknown"

            full_chain.append(f"## Step {i + 1}: {step_name} ({component})")
            full_chain.append("-" * 40)
            full_chain.append(prompt if prompt else "(No Prompt Configured)")
            full_chain.append("\n" + "=" * 40 + "\n")

        return "\n".join(full_chain)
