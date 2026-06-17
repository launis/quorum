import json

path1 = r'c:\src\quorum\data\files\executions\exe_59b39925936544eebf9e474a02eec1fa\execution_trace.json'
path2 = r'c:\src\quorum\data\files\executions\exe_59b39925936544eebf9e474a02eec1fa\frozen_context.json'

atom_to_block = {}
with open(path1, encoding='utf-8') as f:
    data = json.load(f)
for step in data:
    if 'content' in step and isinstance(step['content'], dict):
        evals = step['content'].get('evaluations')
        matrices = []
        eval_mats = step['content'].get('_evaluative_matrices', {})
        if isinstance(eval_mats, dict):
            matrices.extend(eval_mats.keys())
        elif isinstance(eval_mats, list):
            matrices.extend(eval_mats)
        
        if not matrices:
            matrices = [k for k in step['content'].keys() if k.startswith('blk_') and not k.endswith('_missing_context')]
            
        if isinstance(evals, list) and len(matrices) > 0:
            bid = matrices[0]
            for e in evals:
                atom_id = e.get('atom_id')
                if atom_id and atom_id not in atom_to_block:
                    atom_to_block[atom_id] = bid

print(f"Mapped {len(atom_to_block)} atoms to {len(set(atom_to_block.values()))} unique blocks.")

with open(path2, encoding='utf-8') as f:
    frozen_data = json.load(f)
hints = frozen_data.get('ui_hints_snapshot', {})

hint_keys = set(hints.keys())
mapped_blocks = set(atom_to_block.values())

print(f"Blocks in atom_to_block: {mapped_blocks}")
print(f"Blocks in ui_hints_snapshot: {hint_keys}")
print(f"Intersection: {mapped_blocks.intersection(hint_keys)}")
