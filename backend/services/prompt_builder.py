import logging
import json
from typing import Dict, Any, Optional
from backend.database.repository import WorkflowRepository
from backend.services.agent_registry import AgentRegistry
from backend.models.state import WorkflowState
from backend.exceptions import StepNotFoundError, WorkflowNotFoundError, AppException
from datetime import datetime

logger = logging.getLogger(__name__)

class PromptBuilder:
    def __init__(self, repository: WorkflowRepository, agent_registry: AgentRegistry):
        self.repository = repository
        self.registry = agent_registry

    def construct_prompt(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        """
        Fetches the step configuration and constructs the full system prompt
        by concatenating the content of all referenced prompt components.
        Also inspects for placeholders like {{BANNED_PHRASES}} and state variables.
        """
        try:
            step_data = self.repository.get_step_by_id(step_id)
            if not step_data:
                return ""
            exec_config = step_data.get('execution_config', {})
            prompt_ids = exec_config.get('llm_prompts', [])
            
            full_prompt_parts = []
            
            # Pre-fetch banned phrases if needed
            banned_phrases_list = []
            
            for pid in prompt_ids:
                comp = self.repository.get_component_by_id(pid)
                if comp:
                    content = comp.get('content', '')
                    if content:
                        # Ensure content is string
                        if isinstance(content, list):
                            content = "\n".join(str(x) for x in content)
                        elif isinstance(content, dict):
                            content = json.dumps(content, indent=2, ensure_ascii=False)
                        
                        # 1. Check/Replace BANNED_PHRASES
                        if "{{BANNED_PHRASES}}" in content:
                            if not banned_phrases_list:
                                banned_phrases_list = [p['phrase'] for p in self.repository.get_banned_phrases()]
                            
                            phrases_str = ", ".join([f'"{p}"' for p in banned_phrases_list]) if banned_phrases_list else "NONE"
                            content = content.replace("{{BANNED_PHRASES}}", phrases_str)
                            
                        # 2. Check/Replace CURRENT_DATE
                        if "{{CURRENT_DATE}}" in content:
                            now_str = datetime.now().strftime("%d.%m.%Y")
                            content = content.replace("{{CURRENT_DATE}}", now_str)

                        # 3. Inject State Variables (if state is provided)
                        if current_state:
                            if "{{CURRENT_STEP_NAME}}" in content:
                                content = content.replace("{{CURRENT_STEP_NAME}}", current_state.current_step_name)
                            if "{{HISTORY_TEXT}}" in content:
                                content = content.replace("{{HISTORY_TEXT}}", current_state.inputs.history_text)
                            if "{{PRODUCT_TEXT}}" in content:
                                content = content.replace("{{PRODUCT_TEXT}}", current_state.inputs.product_text)
                            if "{{REFLECTION_TEXT}}" in content:
                                content = content.replace("{{REFLECTION_TEXT}}", current_state.inputs.reflection_text)
                            if "{{PREVIOUS_STEP_OUTPUTS}}" in content:
                                content = content.replace("{{PREVIOUS_STEP_OUTPUTS}}", current_state.get_previous_outputs_summary())
                            if "{{GOOGLE_SEARCH_RESULTS}}" in content:
                                search_res = current_state.aux_data.get('google_search_results', '[]')
                                content = content.replace("{{GOOGLE_SEARCH_RESULTS}}", str(search_res))

                        
                        # 4. Inject Schema Example
                        if "{{SCHEMA_EXAMPLE}}" in content:
                            agent_name = step_data.get('component')
                            schema_example = "{}"
                            
                            if agent_name:
                                agent_instance = self.registry.get_agent(agent_name)
                                if agent_instance:
                                    try:
                                        # Try to get example from schema
                                        if hasattr(agent_instance, 'get_response_schema'):
                                            schema_class = agent_instance.get_response_schema()
                                            # Check for json_schema_extra example
                                            if hasattr(schema_class, 'Config') and hasattr(schema_class.Config, 'json_schema_extra'):
                                                examples = schema_class.Config.json_schema_extra.get('examples')
                                                if examples:
                                                    schema_example = json.dumps(examples[0], indent=2, ensure_ascii=False)
                                                else:
                                                     schema_example = schema_class.schema_json(indent=2)
                                            elif hasattr(schema_class, 'model_json_schema'): # Pydantic v2
                                                schema_json = schema_class.model_json_schema()
                                                if 'examples' in schema_json:
                                                     schema_example = json.dumps(schema_json['examples'][0], indent=2, ensure_ascii=False)
                                                else:
                                                     schema_example = json.dumps(schema_json, indent=2, ensure_ascii=False)
                                            else:
                                                # Fallback to simple schema dumping
                                                try:
                                                    schema_example = schema_class.schema_json(indent=2)
                                                except:
                                                    schema_json = schema_class.model_json_schema() # Pydantic v2 fallback
                                                    schema_example = json.dumps(schema_json, indent=2, ensure_ascii=False)
                                        else:
                                            schema_example = "Error: Agent does not expose get_response_schema()"
                                    except Exception as e:
                                        schema_example = f"Error generating schema example: {str(e)}"
                            
                            content = content.replace("{{SCHEMA_EXAMPLE}}", str(schema_example))
                            
                        full_prompt_parts.append(content)
            
            # LOGGING: Trace constructed prompt (truncated)
            logger.debug(f"[PromptBuilder] Constructed PROMPT for {step_id} (Length: {len(full_prompt_parts)} parts)")
            for i, part in enumerate(full_prompt_parts):
                logger.debug(f"   [PART {i+1}] {part[:100]}...")

            return "\n\n".join(full_prompt_parts)
        except Exception as e:
            logger.error(f"[PromptBuilder] Error constructing prompt for step {step_id}: {e}")
            return ""

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
