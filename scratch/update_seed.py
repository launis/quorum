import json

path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Add "reasoning" strategy to model_registry
for config in data.get('system_config', []):
    if config.get('type') == 'model_registry':
        models = config.get('models', {})
        if 'reasoning' not in models:
            reasoning_model = models.get('strict', {}).copy()
            reasoning_model['max_tokens'] = 65536
            reasoning_model['model_name'] = 'vertex_ai/gemini-2.5-pro'
            reasoning_model['provider'] = 'google'
            reasoning_model['additional_params'] = reasoning_model.get('additional_params', {}).copy()
            reasoning_model['additional_params']['thinking_budget_tokens'] = 2048
            models['reasoning'] = reasoning_model

# 2. Map engine_override and reasoning strategy
blueprint_map = {bp['id']: bp for bp in data.get('steps', [])}

for workflow in data.get('workflows', []):
    for step in workflow.get('steps', []):
        bp_id = step.get('task_blueprint')
        bp = blueprint_map.get(bp_id)
        if not bp:
            continue
        
        bp_name = str(bp.get('name', {})).lower()
        bp_slug = str(bp.get('slug', '')).lower()
        
        # Determine step type
        is_mcp = 'mcp_tavily_search' in bp.get('allowed_mcp_tools', [])
        is_analytical = any(role in bp_name or role in bp_slug for role in ['guard', 'analyst', 'logician', 'overseer', 'orchestrator', 'falsifier'])
        is_logic = bp.get('type') == 'logic'
        
        if is_mcp:
            step['engine_override'] = 'DYNAMIC_TOOL_AGENT'
        elif is_analytical:
            step['engine_override'] = 'PRE_HYDRATED_SYNTHESIS'
            bp['model_strategy'] = 'reasoning'
        elif bp.get('type') == 'llm':
            # Also apply PRE_HYDRATED_SYNTHESIS to other standard analytical LLM steps
            step['engine_override'] = 'PRE_HYDRATED_SYNTHESIS'

# 3. Cleanup Obsolete Opaque ID Prompts
target_str = "- Opaque Stripe IDs: All rule IDs are opaque 16-hex strings prefixed with tda_."
for block in data.get('prompt_blocks', []):
    if 'ai_description' in block and isinstance(block['ai_description'], str):
        if target_str in block['ai_description']:
            block['ai_description'] = block['ai_description'].replace(target_str, "").strip()
            
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
