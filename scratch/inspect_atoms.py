import json


def get_atom_prompt(path, target_id):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    for step in data:
        if 'input_prompt' in step:
            prompt = step['input_prompt']
            if target_id in prompt:
                # Etsi target_id ja tulosta muutama rivi sen ympäriltä
                lines = prompt.split('\n')
                for i, line in enumerate(lines):
                    if target_id in line:
                        return "\n".join(lines[max(0, i-2):min(len(lines), i+3)])
    return "Not found"

print("Run 1:")
print(get_atom_prompt("data/files/executions/exe_0adc01fd7c9a40c99b7537e2d32b443c/execution_trace.json", "tda_6f4f8fc663c241acad6da5bff5abe321"))
print("\nRun 2:")
print(get_atom_prompt("data/files/executions/exe_e22f62d350d84d5289a9886c27c1947f/execution_trace.json", "tda_6f4f8fc663c241acad6da5bff5abe321"))
