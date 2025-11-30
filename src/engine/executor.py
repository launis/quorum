from typing import Any
from src.database.client import DatabaseClient
from src.models.schema_registry import SchemaRegistry
from src.components.hook_registry import HookRegistry
import src.components.hooks  # Register all hooks
from src.engine.llm_handler import LLMHandler
from tinydb import Query

class Executor:
    def __init__(self):
        self.db_client = DatabaseClient()
        self.llm_handler = LLMHandler()

    def execute_step(self, step_id: str, context: dict[str, Any], model_override: str = None) -> dict[str, Any]:
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

        # 4. LLM Execution & 6. Output Validation (Retry Loop)
        max_retries = 5
        attempt = 0
        last_error = None
        
        # Prepare initial prompts
        current_prompts = []
        for prompt_id in config.get('llm_prompts', []):
            components_table = self.db_client.get_table('components')
            prompt_record = components_table.get(Query().id == prompt_id)
            if prompt_record:
                current_prompts.append({"content": prompt_record['content']})
            else:
                print(f"[EXECUTOR] Warning: Prompt {prompt_id} not found.")

        import json
        data_context = f"\n\nCONTEXT DATA:\n{json.dumps(current_data, indent=2, default=str)}"
        current_prompts.append({"content": data_context})

        # Inject Output Schema
        output_schema_name = step.get('output_schema')
        if output_schema_name:
            try:
                OutputModel = SchemaRegistry.get_schema(output_schema_name)
                schema_json = json.dumps(OutputModel.model_json_schema(), indent=2)
                schema_instruction = f"\n\nSYSTEM: You must output a valid JSON object that strictly matches the following schema:\n{schema_json}\n\nEnsure your response is a valid JSON object."
                current_prompts.append({"content": schema_instruction})
            except Exception as e:
                print(f"[EXECUTOR] Warning: Failed to inject schema for {output_schema_name}: {e}")

        while attempt < max_retries:
            attempt += 1
            print(f"[EXECUTOR] Attempt {attempt}/{max_retries} for Step {step_id}")
            
            if attempt > 1 and last_error:
                # Add error feedback to prompts
                feedback = f"\n\nSYSTEM: Your previous response failed validation. Error: {last_error}. Please correct your JSON output to match the schema exactly."
                current_prompts.append({"content": feedback})

            if current_prompts:
                try:
                    llm_response = self.llm_handler.call_llm(current_prompts, model=model_override or "gemini-1.5-flash")
                    print(f"[DEBUG] Raw LLM Output: {llm_response[:1000]}...") # Print first 1000 chars
                    current_data['llm_output'] = llm_response
                except Exception as e:
                    print(f"[EXECUTOR] LLM Call Failed (Attempt {attempt}): {e}")
                    last_error = f"LLM Call Failed: {e}"
                    continue # Retry loop

            # 5. Automatic JSON Parsing (Run BEFORE hooks so they have access to data)
            output_schema_name = step.get('output_schema')
            if output_schema_name and 'llm_output' in current_data and isinstance(current_data['llm_output'], str):
                 try:
                     from src.components.hooks.parsing import _clean_and_parse_json
                     parsed_llm = _clean_and_parse_json(current_data['llm_output'])
                     if isinstance(parsed_llm, dict):
                         current_data.update(parsed_llm)
                         print(f"[EXECUTOR] Auto-parsed LLM output for {output_schema_name}")
                 except Exception as e:
                     print(f"[EXECUTOR] Auto-parsing failed: {e}")

            # 6. Post-Hooks (Run on every attempt to ensure fresh parsing)
            for hook_name in config.get('post_hooks', []):
                hook_func = HookRegistry.get_hook(hook_name)
                hook_result = hook_func(current_data)
                if hook_result:
                    current_data.update(hook_result)

            # 7. Output Validation
            # output_schema_name already retrieved above

            if output_schema_name:
                OutputModel = SchemaRegistry.get_schema(output_schema_name)
                try:
                    validated_output = OutputModel(**current_data)
                    print(f"[EXECUTOR] Output Validated: {output_schema_name}")
                    return validated_output.dict()
                except Exception as e:
                    print(f"[EXECUTOR] Validation Failed (Attempt {attempt}): {e}")
                    last_error = str(e)
                    # Loop continues to retry
            else:
                return current_data
        
        # If loop finishes without success
        raise Exception(f"Step {step_id} failed after {max_retries} attempts. Last error: {last_error}")
        
        return current_data
