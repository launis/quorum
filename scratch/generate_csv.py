import json
import csv
import sys
import os

execution_dir = r'c:\src\quorum\data\files\executions\exe_1e679ec75af04f56b2eaddd7ae4f6d53'
trace_path = os.path.join(execution_dir, 'execution_trace.json')
frozen_path = os.path.join(execution_dir, 'frozen_context.json')
out_csv_path = r'c:\src\quorum\scratch\tulokset.csv'

# 1. Load Blueprint and UI Hints for Mapping
try:
    with open(frozen_path, 'r', encoding='utf-8') as f:
        fc = json.load(f)
except Exception as e:
    print(f"Error loading frozen context: {e}")
    sys.exit(1)

ui_hints = fc.get('ui_hints_snapshot', {})
workflow_dags = fc.get('blueprint', {}).get('workflow_dags', {})

atom_mapping = {}

# We need to map atom_id -> Matrix Title, Level, Level Title
for dag_id, dag_data in workflow_dags.items():
    for node in dag_data.get('nodes', []):
        if 'matrix' in node.get('component_type', '').lower() or node.get('component_type') == 'evaluation_matrix':
            matrix_id = node.get('id')
            matrix_title = node.get('ui_metadata', {}).get('title', matrix_id)
            
            # The structure often has 'children' inside the matrix node
            # Or the levels are defined in 'matrix_levels'
            # This can vary, let's just dump what we find in ui_hints for fallback
            pass

# Let's use ui_hints to get titles if possible
def get_translation(label_obj, locale='fi'):
    if not isinstance(label_obj, dict): return str(label_obj)
    translations = label_obj.get('translations', {})
    return translations.get(locale, label_obj.get('default_locale', ''))

# 2. Extract evaluations from trace
try:
    with open(trace_path, 'r', encoding='utf-8') as f:
        trace = json.load(f)
except Exception as e:
    print(f"Error loading trace: {e}")
    sys.exit(1)

def find_evals(obj):
    found = []
    if isinstance(obj, dict):
        if 'atom_id' in obj and ('status' in obj or 'decision' in obj):
            found.append(obj)
        for k, v in obj.items():
            found.extend(find_evals(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(find_evals(item))
    return found

all_evals = find_evals(trace)
print(f"Found {len(all_evals)} atomic evaluations.")

# Filter out duplicates (often same atom is evaluated in retry loops, we take the latest)
unique_evals = {}
for ev in all_evals:
    unique_evals[ev['atom_id']] = ev

# Write to CSV
headers = [
    'Atom ID', 
    'Status', 
    'Confidence', 
    'Rule Internalization', 
    'Reasoning Steps', 
    'Quotes Found', 
    'Falsification Argument'
]

with open(out_csv_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(headers)
    
    for atom_id, ev in unique_evals.items():
        quotes = ev.get('exact_quotes', [])
        quote_texts = []
        for q in quotes:
            if isinstance(q, dict) and 'text' in q:
                quote_texts.append(q['text'])
            elif isinstance(q, str):
                quote_texts.append(q)
        quotes_str = " | ".join(quote_texts)
        
        row = [
            atom_id,
            ev.get('status', str(ev.get('decision'))),
            ev.get('confidence', ''),
            ev.get('rule_internalization', '').replace('\n', ' '),
            ev.get('reasoning_steps', '').replace('\n', ' '),
            quotes_str.replace('\n', ' '),
            ev.get('falsification_argument', '').replace('\n', ' ')
        ]
        writer.writerow(row)

print(f"CSV created successfully at {out_csv_path}")
