import json

with open('data/files/executions/exe_94c30a381bf348e3b934f6affada2a5e/execution_trace.json', encoding='utf-8') as f:
    trace = json.load(f)

with open('scratch_quotes.txt', 'w', encoding='utf-8') as out:
    def extract_quotes(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "exact_quotes" and v:
                    out.write(f"{path}: {v}\n")
                elif k == "exact_quote" and v:
                    out.write(f"{path}: {v}\n")
                else:
                    extract_quotes(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                extract_quotes(v, f"{path}[{i}]")

    extract_quotes(trace)
