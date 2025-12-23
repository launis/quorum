import logging
import inspect
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.models.state import WorkflowState, InputData
from backend.exceptions import AgentExecutionError, FatalInterruption

logger = logging.getLogger(__name__)

class PipelineRunner:
    """
    Responsible for executing the sequential agent loop and individual steps.
    """
    def __init__(self, repository, registry, prompt_builder):
        self.repository = repository
        self.registry = registry
        self.prompt_builder = prompt_builder

    async def initialize_state(self, execution_id: str, raw_inputs: Dict[str, Any]) -> WorkflowState:
        """Helper to create initial WorkflowState from Inputs."""
        try:
            input_data = InputData(
                history_text=raw_inputs.get('history_text', ''),
                product_text=raw_inputs.get('product_text', ''),
                reflection_text=raw_inputs.get('reflection_text', ''),
                bibliography_context=raw_inputs.get('bibliography_context', [])
            )
            
            current_state = WorkflowState(
                execution_id=execution_id,
                inputs=input_data
            )
            
            # Inject Global Configuration
            try:
                banned_raw = self.repository.get_banned_phrases()
                current_state.aux_data['banned_phrases'] = [r['phrase'].lower() for r in banned_raw] if banned_raw else []
            except Exception as e:
                logger.error(f"[PipelineRunner] Failed to load banned phrases: {e}")
                current_state.aux_data['banned_phrases'] = []
            
            logger.debug(f"[PipelineRunner] State initialized with inputs: {raw_inputs.keys()}")
            return current_state
        except Exception as e:
            logger.error(f"[PipelineRunner] Failed to initialize state: {e}")
            raise FatalInterruption("StateInitialization", f"Failed to initialize state: {e}", {"error": str(e)})

    async def execute_loop(
        self, 
        state: WorkflowState, 
        pipeline_steps: List[Any], 
        tracker: Any, 
        execution_id: str,
        start_index: int = 0,
        total_steps_count: int = 0
    ) -> Any:
        """Runs the sequential agent loop."""
        print(f"DEBUG: PipelineRunner.execute_loop START. Steps: {len(pipeline_steps)}", flush=True)
        total_steps = total_steps_count or len(pipeline_steps)
        current_state = state
        
        for index, (agent, step_doc) in enumerate(pipeline_steps):
            # Absolute step number logic
            current_abs_index = start_index + index
            step_num = current_abs_index + 1
            
            percent = int((step_num / total_steps) * 100)
            stage_name = f"Step {step_num}/{total_steps}: {agent.__class__.__name__}"
            
            # Checkpoint: Save current state to DB (trace)
            trace_dump = current_state.model_dump(mode='json')
            tracker.update(stage=stage_name, percent=percent, details={'trace': trace_dump})

            current_state = await self._execute_step(current_state, agent, step_doc, execution_id)
            
            # Check for Early Exit (Security)
            if isinstance(current_state, dict) and "security_alert" in current_state:
                    return current_state
                    
        return current_state

    async def _execute_step(self, current_state: WorkflowState, agent: Any, step_doc: Dict[str, Any], execution_id: str) -> Any:
        """Helper to execute a single step (Pre-hooks -> Model -> Agent -> Post-hooks -> Validation)."""
        step_id = step_doc['id']
        agent_name = agent.__class__.__name__
        current_state.current_step_name = agent_name
        logger.info(f"[PipelineRunner] Running step: {agent_name} (Step ID: {step_id})")

        # 1. Pre-Hooks
        config = step_doc.get('execution_config') or {}
        print(f"DEBUG: Step {agent_name} Config Hooks: {config.get('pre_hooks')}", flush=True)
        for hook in config.get('pre_hooks') or []:
            print(f"DEBUG: Executing Pre-Hook {hook}", flush=True)
            current_state = self._execute_hook(hook, agent, current_state)

        # 2. Dynamic Model Selection
        model_config = self._configure_agent_model(agent, step_id, execution_id)
        
        # 3. Prompt Construction
        system_instruction = self.prompt_builder.construct_prompt(step_id, current_state) if step_id else None

        # 4. Agent Execution (Async)
        try:
            # Inject repository based on DDD refactoring
            # Pass model configuration (max_tokens, temperature) as kwargs
            exec_kwargs = {
                "system_instruction": system_instruction,
                "repository": self.repository
            }
            if model_config:
                if "max_tokens" in model_config: exec_kwargs["max_tokens"] = model_config["max_tokens"]
                if "temperature" in model_config: exec_kwargs["temperature"] = model_config["temperature"]

            current_state = await agent.execute(current_state, **exec_kwargs)
            
        except Exception as e:
            raise AgentExecutionError(agent_name, step_id, e)

        # 5. Post-Hooks
        for hook in config.get('post_hooks') or []:
            current_state = self._execute_hook(hook, agent, current_state)

        # 6. Validation
        self._validate_step_output(agent_name, step_id, current_state, step_doc)

        # 7. Update DB - HANDLED BY TRACKER UPSTREAM

        # 8. Security Check
        if current_state.step_guard and current_state.step_guard.security_check.uhka_havaittu:
            return self._handle_security_intervention(execution_id, current_state)
            
        # DEBUG TRACE
        try:
            from backend.core.debug_helper import debug_dump_state
            debug_dump_state(current_state, agent_name)
        except: pass

        return current_state

    def _execute_hook(self, hook_name: str, agent: Any, state: WorkflowState) -> WorkflowState:
        """Executes a hook (Agent-method ONLY)."""
        if hasattr(agent, hook_name):
            logger.debug(f"[PipelineRunner] Executing Hook: {agent.__class__.__name__}.{hook_name}")
            try:
                hook_method = getattr(agent, hook_name)
                
                # Inspect signature
                sig = inspect.signature(hook_method)
                kwargs = {}
                
                if 'repository' in sig.parameters:
                    kwargs['repository'] = self.repository
                
                if kwargs:
                    return hook_method(state, **kwargs)
                else:
                    return hook_method(state)
            except Exception as e:
                logger.error(f"[PipelineRunner] Hook {hook_name} failed: {e}")
                return state
        else:
            if not hook_name.startswith('parse_'):
                logger.warning(f"[PipelineRunner] Warning: Hook '{hook_name}' not found on Agent {agent.__class__.__name__}. Skipping.")
            return state

    def _configure_agent_model(self, agent: Any, step_id: str, execution_id: str) -> Dict[str, Any]:
        """Resolves and sets the specific model for an agent."""
        step_model_key = None
        
        try:
             exec_rec = self.repository.get_execution(execution_id)
             if exec_rec:
                 wf_rec = self.repository.get_workflow_by_id(exec_rec['workflow_id'])
                 if wf_rec:
                     mapping = wf_rec.get('default_model_mapping', {})
                     step_model_key = mapping.get(step_id)
        except Exception as e:
             logger.error(f"[PipelineRunner] Model lookup failed: {e}")
             raise e

        # If still not found (e.g. mapping missing), we could check step_doc
        if not step_model_key:
             # Try getting step config directly again
             step_doc = self.repository.get_step_by_id(step_id)
             if step_doc:
                 config = step_doc.get('execution_config', {})
                 step_model_key = config.get('model_strategy')
        
        if not step_model_key:
             raise ValueError(f"[PipelineRunner] CRITICAL: No model strategy (e.g. 'fast'/'deep') found for step {step_id}. Check Workflow/Step Config.")

        resolved_config = self.registry.resolve_model_config(step_model_key)
        resolved_model_name = resolved_config.get("model_name")
        resolved_provider = resolved_config.get("provider")
        
        if resolved_model_name and hasattr(agent, 'set_model'):
            agent.set_model(resolved_model_name, provider=resolved_provider)
            logger.debug(f"[PipelineRunner] Configured {agent.__class__.__name__} with {resolved_model_name} (Provider: {resolved_provider})")
            
        return resolved_config

    def _validate_step_output(self, agent_name: str, step_id: str, state: WorkflowState, step_doc: Dict[str, Any]):
        """Validates output against component schemas."""
        output_config_id = step_doc.get('output_config_component')
        if output_config_id:
            comp_record = self.repository.get_component_by_id(output_config_id)
            if comp_record:
                required_fields = comp_record.get('content', [])
                if isinstance(required_fields, list):
                    state_key = step_doc.get('state_key')
                    if state_key and hasattr(state, state_key):
                        output_obj = getattr(state, state_key)
                        if output_obj:
                            output_data = output_obj.model_dump(mode='json')
                            missing = [f for f in required_fields if "." not in f and f not in output_data]
                            if missing:
                                error_msg = f"Validation Failed: Missing fields {missing} in {agent_name}"
                                logger.error(f"[PipelineRunner] {error_msg}")
                                raise AgentExecutionError(agent_name, step_id, ValueError(error_msg))

    def _handle_security_intervention(self, execution_id: str, state: WorkflowState) -> Dict[str, Any]:
        """Handles security check failures."""
        msg = f"[PipelineRunner] SECURITY INTERVENTION: Threat detected."
        logger.critical(msg)
        
        rejection_details = {
            "security_alert": "Execution aborted due to security violation.",
            "risk_level": state.step_guard.security_check.riski_taso,
            "analysis": state.step_guard.security_check.adversariaalinen_simulaatio_tulos,
            "guard_data": state.step_guard.model_dump()
        }
        
        self.repository.update_execution(execution_id, {
            'status': 'rejected',
            'error': f"Security Threat Detected: {state.step_guard.security_check.riski_taso}",
            'end_time': datetime.now().isoformat(),
            'result': rejection_details
        })
        return rejection_details
