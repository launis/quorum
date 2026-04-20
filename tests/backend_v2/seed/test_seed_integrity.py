import json
import os
import pytest

def test_waterfall_scoring_hook_requires_atom_flattening_hook():
    """
    Tier 4 Bug Hunting: If a step uses waterfall_scoring_hook, it MUST use atom_flattening_hook.
    """
    seed_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend_v2', 'seed', 'seed_data.json')
    if not os.path.exists(seed_path):
        pytest.skip(f"Could not find {seed_path}")
        
    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    invalid_steps = []
    
    for step in data.get('steps', []):
        post_hooks = step.get('post_hooks', [])
        pre_hooks = step.get('pre_hooks', [])
        
        if 'waterfall_scoring_hook' in post_hooks:
            # Check if this step has any prompt blocks of category 'matrix'
            prompt_block_ids = step.get('prompt_blocks', [])
            has_matrix = False
            for pb_id in prompt_block_ids:
                for pb in data.get('prompt_blocks', []):
                    if pb.get('id') == pb_id and pb.get('category_id') == 'matrix':
                        has_matrix = True
                        break
            
            # if the step has a matrix block, it MUST have the atom_flattening_hook
            if has_matrix and 'atom_flattening_hook' not in pre_hooks:
                invalid_steps.append(step.get('id'))
                
    assert not invalid_steps, f"Steps missing 'atom_flattening_hook' but requiring 'waterfall_scoring_hook' with matrix blocks: {invalid_steps}"
