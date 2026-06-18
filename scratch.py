import json

with open('data/files/executions/exe_94c30a381bf348e3b934f6affada2a5e/execution_trace.json', encoding='utf-8') as f:
    trace = json.load(f)

with open('scratch_dump.txt', 'w', encoding='utf-8') as out:
    for step in trace:
        if 'evaluations' in step:
            for item in step['evaluations']:
                out.write(json.dumps(item) + "\n")
