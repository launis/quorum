import json

with open("data/files/executions/exe_0adc01fd7c9a40c99b7537e2d32b443c/execution_trace.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

for step in data:
    if 'content' in step:
        print("Keys in step:", list(step.keys()))
        if 'content' in step and isinstance(step['content'], dict):
            print("Keys in content:", list(step['content'].keys()))
            if 'evaluations' in step['content']:
                print("First evaluation:", step['content']['evaluations'][0])
                break
