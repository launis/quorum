import json
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    data = json.load(f)

# True parallel DAG based strictly on Pydantic AST Requirements
dag_fixes = {
    'step_input_processing': {
        'depends_on': [],
        'mappings': {'inputs': '$inputs'}
    },
    'step_guard': {
        'depends_on': ['step_node_1'],
        'mappings': {'inputs': '$inputs'}
    },
    'step_retrieval_agent': {
        'depends_on': ['step_node_2'],
        'mappings': {'inputs': '$inputs'}
    },
    'step_analyst': {
        'depends_on': ['step_node_3'],
        'mappings': {'inputs': '$inputs'}
    },
    'step_interaction_analyst': {
        'depends_on': ['step_node_3'], # Parallel with Analyst
        'mappings': {'inputs': '$inputs'}
    },
    'step_profiler': {
        'depends_on': ['step_node_3'], # Parallel with Analyst
        'mappings': {'inputs': '$inputs'}
    },
    'step_archivist': {
        'depends_on': ['step_node_3'], # Parallel with Analyst
        'mappings': {'inputs': '$inputs'}
    },
    'step_logician': {
        'depends_on': ['step_node_4'],
        'mappings': {'step_analyst': '$step_node_4.output', 'inputs': '$inputs'}
    },
    'step_falsifier': {
        'depends_on': ['step_node_4'],
        'mappings': {'step_analyst': '$step_node_4.output', 'inputs': '$inputs'}
    },
    'step_causal_analyst': {
        'depends_on': ['step_node_4'],
        'mappings': {'step_analyst': '$step_node_4.output', 'inputs': '$inputs'}
    },
    'step_performativity_detector': {
        'depends_on': ['step_node_4'],
        'mappings': {'step_analyst': '$step_node_4.output', 'inputs': '$inputs'}
    },
    'step_overseer': {
        'depends_on': ['step_node_4'],
        'mappings': {'step_analyst': '$step_node_4.output', 'inputs': '$inputs'}
    },
    'step_judge': {
        'depends_on': [
            'step_node_2', 'step_node_4', 'step_node_6', 'step_node_7', 
            'step_node_8', 'step_node_9', 'step_node_10', 'step_node_11', 'step_node_12'
        ],
        'mappings': {
            'inputs': '$inputs',
            'step_guard': '$step_node_2.output',
            'step_analyst': '$step_node_4.output',
            'step_profiler': '$step_node_6.output',
            'step_logician': '$step_node_7.output',
            'step_falsifier': '$step_node_8.output',
            'step_causal': '$step_node_9.output',
            'step_detector': '$step_node_10.output',
            'step_overseer': '$step_node_11.output',
            'step_archivist': '$step_node_12.output'
        }
    },
    'step_coach': {
        'depends_on': ['step_node_13'],
        'mappings': {'inputs': '$inputs', 'step_judge': '$step_node_13.output'}
    },
    'step_xai_reporter': {
        'depends_on': ['step_node_13'],
        'mappings': {'inputs': '$inputs', 'step_judge': '$step_node_13.output'}
    }
}

for wf in data.get('workflows', []):
    if wf['id'] == 'workflow_courtroom_20_full_audit':
        for node in wf.get('steps', []):
            bp = node.get('task_blueprint')
            if bp in dag_fixes:
                node['depends_on'] = dag_fixes[bp]['depends_on']
                node['input_mappings'] = dag_fixes[bp]['mappings']

def sort_blocks(blocks):
    task_blocks = [b for b in blocks if b.startswith('block_task')]
    trailing_blocks = [b for b in blocks if b in ('block_instructionstrictscale', 'block_instructioncoachcitation')]
    matrices = [b for b in blocks if b.startswith('matrix_')]
    others = [b for b in blocks if b not in task_blocks and b not in trailing_blocks and b not in matrices]
    
    # Standard psychological order for LLM context reading:
    # 1. Global Context & Rules
    # 2. Persona Matrix (Role)
    # 3. Exact Task with Schema Example
    # 4. Strict modifiers closely tied to schema
    return others + matrices + task_blocks + trailing_blocks

for step in data.get('steps', []):
    prompts = step.get('prompt_blocks', [])
    if step['id'] == 'step_guard':
        pass # Exception handled manually in previous iterations successfully
    else:
        step['prompt_blocks'] = sort_blocks(prompts)

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Parallel DAG edges constructed and prompt sequences perfectly aligned.")
