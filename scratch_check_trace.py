import json

path = r'C:\src\quorum\data\files\executions\exe_ec05ce44941c4d82b4c61dcc84788bb6\execution_trace.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item.get('event_type') == 'output':
        step_name = item.get('step_name')
        parsed = item.get('content', {})
        evals = parsed.get('evaluations', [])

        print(f"\nSTEP: {step_name} | EVALS: {len(evals)}")
        for ev in evals:
            quote = ev.get('exact_quote')
            override = ev.get('contextual_override')
            atom_id = ev.get('atom_id')
            status = ev.get('status', 'N/A')
            short_quote = (str(quote)[:60] + "...") if quote and len(str(quote)) > 60 else str(quote)
            print(f"  -> Atom: {atom_id} - Status: {status} - Override: {override} - Quote: {short_quote}")
