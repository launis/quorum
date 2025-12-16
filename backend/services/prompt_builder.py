import logging
import json
from typing import Dict, Any, Optional
from backend.database.repository import AbstractWorkflowRepository
from backend.services.agent_registry import AgentRegistry
from backend.models.state import WorkflowState
from backend.exceptions import StepNotFoundError, WorkflowNotFoundError, AppException
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptBuilder:
    def __init__(self, repository: AbstractWorkflowRepository, agent_registry: AgentRegistry):
        self.repository = repository
        self.registry = agent_registry

    def construct_prompt(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        """
        Fetches the step configuration and constructs the full system prompt
        by concatenating the content of all referenced prompt components.
        Refactored to use helper methods for component resolution and variable injection.
        """
        try:
            step_data = self.repository.get_step_by_id(step_id)
            if not step_data:
                return ""
            
            # 1. Resolve Components
            prompt_parts = self._resolve_prompt_components(step_data)
            
            # 2. Process Placeholders
            processed_parts = []
            for content in prompt_parts:
                # Banned Phrases
                content = self._inject_banned_phrases(content)
                
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

    def _resolve_prompt_components(self, step_data: Dict[str, Any]) -> list[str]:
        """Fetches content from all prompt components linked to the step."""
        exec_config = step_data.get('execution_config', {})
        prompt_ids = exec_config.get('llm_prompts', [])
        parts = []
        
        for pid in prompt_ids:
            comp = self.repository.get_component_by_id(pid)
            if comp:
                content = comp.get('content', '')
                if content:
                    if isinstance(content, list):
                        content = "\n".join(str(x) for x in content)
                    elif isinstance(content, dict):
                        content = json.dumps(content, indent=2, ensure_ascii=False)
                    parts.append(content)
        return parts

    def _inject_banned_phrases(self, content: str) -> str:
        if "{{BANNED_PHRASES}}" in content:
            phrases = [p['phrase'] for p in self.repository.get_banned_phrases()]
            phrases_str = ", ".join([f'"{p}"' for p in phrases]) if phrases else "NONE"
            return content.replace("{{BANNED_PHRASES}}", phrases_str)
        return content

    def _inject_global_variables(self, content: str) -> str:
        if "{{CURRENT_DATE}}" in content:
            now_str = datetime.now().strftime("%d.%m.%Y")
            return content.replace("{{CURRENT_DATE}}", now_str)
        return content

    def _inject_state_variables(self, content: str, state: WorkflowState) -> str:
        """Injects dynamic state values into the prompt content."""
        replacements = {
            "{{CURRENT_STEP_NAME}}": state.current_step_name or "Unknown",
            "{{HISTORY_TEXT}}": state.inputs.history_text,
            "{{PRODUCT_TEXT}}": state.inputs.product_text,
            "{{REFLECTION_TEXT}}": state.inputs.reflection_text,
            "{{PREVIOUS_STEP_OUTPUTS}}": state.get_previous_outputs_summary()
        }
        
        for key, value in replacements.items():
            if key in content:
                content = content.replace(key, str(value))
                
        if "{{GOOGLE_SEARCH_RESULTS}}" in content:
            search_res = state.aux_data.get('google_search_results', '[]')
            content = content.replace("{{GOOGLE_SEARCH_RESULTS}}", str(search_res))
            
        return content

    def _inject_schema_example(self, content: str, step_data: Dict[str, Any]) -> str:
        if "{{SCHEMA_EXAMPLE}}" not in content:
            return content
            
        agent_name = step_data.get('component')
        schema_example = "{}"
        
        if agent_name:
            agent_instance = self.registry.get_agent(agent_name)
            if agent_instance:
                 schema_example = self._generate_schema_json(agent_instance)
        
        return content.replace("{{SCHEMA_EXAMPLE}}", str(schema_example))

    def _generate_schema_json(self, agent_instance: Any) -> str:
        """Helper to safely extract JSON schema example from an agent."""
        try:
            if hasattr(agent_instance, 'get_response_schema'):
                schema_class = agent_instance.get_response_schema()
                if not schema_class:
                     return "{}"

                # 1. Try Config.json_schema_extra (Pydantic v2 compatible if set manually)
                if hasattr(schema_class, 'Config') and hasattr(schema_class.Config, 'json_schema_extra'):
                    examples = schema_class.Config.json_schema_extra.get('examples')
                    if examples:
                        return json.dumps(examples[0], indent=2, ensure_ascii=False)
                
                # 2. Try Standard Schema Dump
                if hasattr(schema_class, 'model_json_schema'): # Pydantic v2
                    schema_json = schema_class.model_json_schema()
                    if 'examples' in schema_json:
                         return json.dumps(schema_json['examples'][0], indent=2, ensure_ascii=False)
                    return json.dumps(schema_json, indent=2, ensure_ascii=False)
                
                # 3. Fallback Pydantic v1
                if hasattr(schema_class, 'schema_json'):
                    return schema_class.schema_json(indent=2)
                    
            return "Error: Agent does not expose get_response_schema()"
        except Exception as e:
            return f"Error generating schema example: {str(e)}"

    def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        # 1. Fetch Step Record
        step_data = self.repository.get_step_by_id(step_id)
        if not step_data:
            raise StepNotFoundError(step_id)
            
        agent_class = step_data.get('component', 'UnknownAgent')
        
        # 2. Construct Prompt
        prompt = self.construct_prompt(step_id)
        if not prompt:
            # Maybe raise exception or return empty?
            # prompt construction failing might be app error
            logger.warning(f"Constructed prompt empty for {step_id}")
        
        # 3. Return Structured Data for UI
        preview_data = {
            "agent_class": agent_class,
            "system_instruction": prompt,
            "user_prompt": "Template Logic Not Available" 
        }

        # Try to get the User Prompt Template from the Agent Class
        agent_instance = self.registry.get_agent(agent_class)
        if agent_instance:
            try:
                preview_data["user_prompt"] = agent_instance.get_user_prompt_template()
            except Exception as e:
                preview_data["user_prompt"] = f"Error retrieving template: {e}"
        
        return preview_data

    def preview_full_chain_prompts(self, workflow_id: str) -> str:
        wf_record = self.repository.get_workflow_by_id(workflow_id)
        if not wf_record:
            raise WorkflowNotFoundError(workflow_id)
        
        steps_ids = wf_record.get('steps', [])
        full_chain = []
        
        full_chain.append(f"# Workflow: {wf_record.get('name', 'Untitled')}")
        full_chain.append(f"ID: {workflow_id}\n")
        
        for i, step_id in enumerate(steps_ids):
            prompt = self.construct_prompt(step_id)
            
            # Fetch step name/component for header
            s_rec = self.repository.get_step_by_id(step_id)
            step_name = s_rec.get('id', step_id) if s_rec else step_id
            component = s_rec.get('component', 'Unknown') if s_rec else 'Unknown'
            
            full_chain.append(f"## Step {i+1}: {step_name} ({component})")
            full_chain.append("-" * 40)
            full_chain.append(prompt if prompt else "(No Prompt Configured)")
            full_chain.append("\n" + "="*40 + "\n")
            
        return "\n".join(full_chain)
