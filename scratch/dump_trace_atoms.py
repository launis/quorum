import json
import os

out_path = r'c:\src\quorum\scratch\atomit.md'
ctx_path = r'c:\src\quorum\data\files\executions\exe_06d5d862c2824b428af16cc12c9dc3f0\context_variables.json'

atoms = []
with open(ctx_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    bb = data.get('__GLOBAL_ATOM_BLACKBOARD__', {})
    for doc_id, atom_dict in bb.get('atoms_by_input', {}).items():
        if isinstance(atom_dict, dict):
            for atom in atom_dict.get('atoms', []):
                if isinstance(atom, dict):
                    atoms.append(atom)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'# Löydetyt Atomit (Yhteensä {len(atoms)} kpl)\n\n')
    for i, atom in enumerate(atoms, 1):
        f.write(f'## Atomi {i} (Draft ID: {atom.get("draft_id", "N/A")})\n')
        f.write('```json\n')
        f.write(json.dumps(atom, indent=2, ensure_ascii=False))
        f.write('\n```\n\n')

print(f'Dumped {len(atoms)} atoms to {out_path}')
