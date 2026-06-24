import os
import json
import re

log_file = 'c:/src/quorum/backend_debug.log'
state_file = 'c:/src/quorum/data/files/executions/run_20260624_1058/monitor_state.json'

with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

last_read = state['last_read_line']

if not os.path.exists(log_file):
    print("Lokitiedostoa ei löydy vielä.")
    exit(0)

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[last_read:]
if not new_lines:
    print("Ei uusia lokiriveja.")
    exit(0)

new_errors = []
new_nodes = []

# Regex patterns
queue_pattern = re.compile(r'acquired semaphore lock in ([\d\.]+) ms')
llm_time_pattern = re.compile(r'completed in ([\d\.]+) ms')
tokens_pattern = re.compile(r'tokens: (\d+) prompt, (\d+) completion')
self_healing_pattern = re.compile(r'LLM Schema Validation Failed|Self-Healing successful')
node_complete_pattern = re.compile(r'\[DAG Exec\].*?Node ([\w\_]+) completed')

for line in new_lines:
    line = line.strip()
    if not line: continue
    
    if 'ERROR' in line or 'CRITICAL' in line or 'ValidationError' in line:
        new_errors.append(line)
        state['errors'].append(line)
        
    m_q = queue_pattern.search(line)
    if m_q:
        state['cumulative_queue_time_ms'] += float(m_q.group(1))
        
    m_llm = llm_time_pattern.search(line)
    if m_llm:
        state['cumulative_llm_time_ms'] += float(m_llm.group(1))
        state['total_llm_calls'] += 1
        
    m_tok = tokens_pattern.search(line)
    if m_tok:
        state['total_prompt_tokens'] += int(m_tok.group(1))
        state['total_completion_tokens'] += int(m_tok.group(2))
        
    if self_healing_pattern.search(line):
        state['self_healing_cycles'] += 1
        
    m_node = node_complete_pattern.search(line)
    if m_node:
        node_name = m_node.group(1)
        new_nodes.append(node_name)
        state['completed_nodes'].append(node_name)

state['last_read_line'] = len(lines)

with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2)

print("### Tilannepaivitys")
if new_nodes:
    print(f"**Valmistuneet vaiheet nyt:** {', '.join(new_nodes)}")
    
print(f"**Uusia LLM-kutsuja:** {state['total_llm_calls']}")
print(f"**Kumulatiivinen LLM-aika:** {state['cumulative_llm_time_ms']/1000:.1f} s")
print(f"**Kumulatiivinen jonotusaika (Semaphore):** {state['cumulative_queue_time_ms']/1000:.1f} s")
print(f"**Käytetyt tokenit (Prompt / Completion):** {state['total_prompt_tokens']} / {state['total_completion_tokens']}")
print(f"**Itsekorjauksia:** {state['self_healing_cycles']}")

if new_errors:
    print("\n**Havaitut uudet virheet:**")
    for e in new_errors[-5:]: # Show last 5
        print(f"- {e}")
