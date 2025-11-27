from typing import Dict, Any
from src.database.client import DatabaseClient
from src.models.schema_registry import SchemaRegistry
from src.components.hook_registry import HookRegistry
from src.engine.llm_handler import LLMHandler
from tinydb import Query

class Executor:
    def __init__(self):
        self.db_client = DatabaseClient()
        self.llm_handler = LLMHandler()

    def execute_step(self, step_id: str, context: Dict[str, Any], model_override: str = None) -> Dict[str, Any]:
        print(f"[EXECUTOR] Executing Step: {step_id}")
        
        # 1. Load Step Definition
        steps_table = self.db_client.get_table('steps')
        step = steps_table.get(Query().id == step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found.")

        config = step.get('execution_config', {})
        
        # 2. Input Validation
        input_schema_name = step.get('input_schema')
        if input_schema_name:
            InputModel = SchemaRegistry.get_schema(input_schema_name)
            # Filter context to match schema fields? Or just pass context and let pydantic ignore extras?
            # Strict mode might require exact match. Let's try passing context.
            # Actually, context might contain everything. We should probably extract relevant keys.
            # For simplicity, we assume context has the right keys.
            try:
                validated_input = InputModel(**context)
                print(f"[EXECUTOR] Input Validated: {input_schema_name}")
            except Exception as e:
                print(f"[EXECUTOR] Input Validation Failed: {e}")
                raise e
        else:
            validated_input = context

        current_data = validated_input.dict() if hasattr(validated_input, 'dict') else context

        # 3. Pre-Hooks
        for hook_name in config.get('pre_hooks', []):
            hook_func = HookRegistry.get_hook(hook_name)
            hook_result = hook_func(current_data)
            if hook_result:
                current_data.update(hook_result)

        # 4. LLM Execution
        prompts = []
        for prompt_id in config.get('llm_prompts', []):
            # Fetch prompt content from DB
            components_table = self.db_client.get_table('components')
            prompt_record = components_table.get(Query().id == prompt_id)
            if prompt_record:
                prompts.append({"content": prompt_record['content']})
            else:
                print(f"[EXECUTOR] Warning: Prompt {prompt_id} not found.")

        if prompts:
            llm_response = self.llm_handler.call_llm(prompts, model=model_override or "gemini-1.5-flash")
            # Assume LLM response maps to some key in output? 
            # Or does the post-hook parse it?
            # For now, let's store it in a generic key, or assume the step defines where it goes.
            # Let's assume it goes to 'llm_output'
            current_data['llm_output'] = llm_response

        # 5. Post-Hooks
        for hook_name in config.get('post_hooks', []):
            hook_func = HookRegistry.get_hook(hook_name)
            hook_result = hook_func(current_data)
            if hook_result:
                current_data.update(hook_result)

        # 6. Output Validation
        output_schema_name = step.get('output_schema')
        if output_schema_name:
            OutputModel = SchemaRegistry.get_schema(output_schema_name)
            try:
                validated_output = OutputModel(**current_data)
                print(f"[EXECUTOR] Output Validated: {output_schema_name}")
                return validated_output.dict()
            except Exception as e:
                print(f"[EXECUTOR] Output Validation Failed: {e}")
                raise e
        
        return current_data
