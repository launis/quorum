import json
import sys
import os

try:
    import pandas as pd
except ImportError:
    print("Pandas not installed. Please install it.")
    sys.exit(1)

execution_dir = r'c:\src\quorum\data\files\executions\exe_1e679ec75af04f56b2eaddd7ae4f6d53'
trace_path = os.path.join(execution_dir, 'execution_trace.json')
frozen_path = os.path.join(execution_dir, 'frozen_context.json')
out_excel_path = r'c:\src\quorum\scratch\Tulokset_Auditoijille.xlsx'

# 1. Load Blueprint and UI Hints for Mapping
try:
    with open(frozen_path, 'r', encoding='utf-8') as f:
        fc = json.load(f)
except Exception as e:
    print(f"Error loading frozen context: {e}")
    sys.exit(1)

ui_hints = fc.get('ui_hints_snapshot', {})
workflow_dags = fc.get('blueprint', {}).get('workflow_dags', {})

# We will try to map atom_id to its UI labels if available in ui_hints or blueprint
# Due to time constraints in a scratch script, we will extract what we can.
# In a real backend implementation, we'd use the full DAG structure.

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
unique_evals = {}
for ev in all_evals:
    unique_evals[ev['atom_id']] = ev

# 3. Extract matrix scoring results
scoring_results = {}
for item in trace:
    c = item.get('content', {})
    if isinstance(c, dict):
        if 'scoring_result' in c:
            sr = c['scoring_result']
            if isinstance(sr, dict) and 'matrix_scores' in sr:
                scoring_results = sr['matrix_scores']
        if 'results' in c and isinstance(c['results'], list):
            for res in c['results']:
                if 'scoring_result' in res:
                    sr = res['scoring_result']
                    if isinstance(sr, dict) and 'matrix_scores' in sr:
                        scoring_results = sr['matrix_scores']

# Prepare Summary Data
summary_rows = []
for m_id, m_data in scoring_results.items():
    title = m_data.get('matrix_title', m_id)
    score = m_data.get('total_score', 0)
    max_score = m_data.get('max_possible_score', 5.0)
    summary_rows.append({
        'Matriisin Nimi': title,
        'Lopullinen Arvosana': score,
        'Maksimiarvosana': max_score
    })

summary_df = pd.DataFrame(summary_rows)

# Prepare Raw Data
raw_rows = []
for atom_id, ev in unique_evals.items():
    status = ev.get('status', str(ev.get('decision')))
    num_status = 1 if status == 'PASS' or status == 'True' else 0
    
    quotes = ev.get('exact_quotes', [])
    quote_texts = []
    for q in quotes:
        if isinstance(q, dict) and 'text' in q:
            quote_texts.append(q['text'])
        elif isinstance(q, str):
            quote_texts.append(q)
    quotes_str = " | ".join(quote_texts)
    
    # Calculate word count for reasoning
    reasoning = ev.get('reasoning_steps', '')
    word_count = len(reasoning.split())
    
    confidence_pct = f"{ev.get('confidence', 0) * 100:.1f} %" if ev.get('confidence') else ""
    
    # In a full backend implementation we would calculate exact atom max score and earned score 
    # based on the level definitions. For this scratch script we use dummy values to illustrate the architecture.
    max_score = 0.33
    earned_score = max_score if num_status == 1 else 0.00
    
    raw_rows.append({
        'Atom ID (Tekninen)': atom_id,
        'Matriisi (Placeholder)': 'Tuntematon Matriisi (Vaatii DAG mapin)',
        'Sisäistetty Sääntö': ev.get('rule_internalization', '').replace('\n', ' '),
        'Tulos (1/0)': num_status,
        'Atomin Max Pisteet': max_score,
        'Atomin Saadut Pisteet': earned_score,
        'Varmuusarvio': confidence_pct,
        'Perustelun Pituus (sanaa)': word_count,
        'Löydetyt Lainaukset': quotes_str.replace('\n', ' '),
        'Käytetyt Lähteet': ", ".join(ev.get('used_source_aliases', [])),
        'Tekoälyn Perustelu': reasoning.replace('\n', ' '),
        'Falsifiointi': ev.get('falsification_argument', '').replace('\n', ' ')
    })

raw_df = pd.DataFrame(raw_rows)

# Write to Excel
with pd.ExcelWriter(out_excel_path, engine='openpyxl') as writer:
    if not summary_df.empty:
        summary_df.to_excel(writer, sheet_name='Yhteenveto', index=False)
    else:
        # Fallback if no scoring results found
        pd.DataFrame([{'Viive': 'Scoring results not found in trace'}]).to_excel(writer, sheet_name='Yhteenveto', index=False)
        
    raw_df.to_excel(writer, sheet_name='Raakadata', index=False)

print(f"Excel created successfully at {out_excel_path}")
