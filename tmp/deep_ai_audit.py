import json

def analyze_theoretical_blindspots():
    with open('c:/src/quorum/backend_v2/seed/seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    workflows = data.get('workflows', [])
    steps = data.get('steps', [])
    pb_dict = {pb['id']: pb for pb in data.get('prompt_blocks', [])}

    print("=== DEEP AI AUDIT: THEORETICAL BLINDSPOTS & INTERACTIONS ===\n")
    
    # 1. Dependency Analysis - Are critics sharing too much context?
    # In the current parallel DAG, Analysts feed Logician, Falsifier, Causal, Performativity.
    # Are logicians forced to accept Analyst hypotheses without questioning them?
    
    print("1. EVALUATING ANALYST HYPOTHESIS BOTTLENECK")
    analyst_task = pb_dict.get('block_taskanalyst', {})
    print("Analyst Task Description snippets (FI):")
    fi_desc = analyst_task.get('description', {}).get('translations', {}).get('fi', '')
    print(fi_desc[:500] + "...\n")
    
    # Check if critics evaluate the SOURCE TEXT or just the Analyst's hypotheses.
    print("2. EVALUATING CRITIC AUTONOMY")
    falsifier_task = pb_dict.get('block_taskfalsifier', {})
    fi_falsifier = falsifier_task.get('description', {}).get('translations', {}).get('fi', '')
    if 'history_text' in fi_falsifier or 'Alkuperäinen teksti' in fi_falsifier or 'keskusteluhistoria' in fi_falsifier:
        print("[OK] Falsifier seems to have access to original text.")
    else:
        print("[WARNING] Falsifier might be blind to original text and only sees Analyst hypotheses!")
        print("Falsifier task snippet:", fi_falsifier[:300])
        
    logician_task = pb_dict.get('block_tasklogician', {})
    fi_logician = logician_task.get('description', {}).get('translations', {}).get('fi', '')
    if 'history_text' in fi_logician or 'alkuperäinen' in fi_logician:
        print("[OK] Logician seems to have access to original text.")
    else:
        print("[WARNING] Logician might be evaluating hypotheses in a vacuum!")
        print("Logician task snippet:", fi_logician[:300])

    # 3. Ontological Conflicts
    print("\n3. EVALUATING ONTOLOGICAL CONFLICTS")
    # Does the Judge have mechanisms to resolve when Logician (Toulmin) says "Invalid" but Causal says "Highly Correlated"?
    judge_task = pb_dict.get('block_taskjudge', {})
    fi_judge = judge_task.get('description', {}).get('translations', {}).get('fi', '')
    print("Judge task snippet for conflict resolution:", fi_judge[:400])
    
    # 4. Feedback loops
    print("\n4. EVALUATING CYBERNETIC FEEDBACK LOOPS")
    # A true intelligent system needs feedback. Are any of the agents able to request MORE information from retrieval if something is amiss?
    # Checked Overseer FactCheckRFI earlier. Let's see if it just "claims" unverified or actively triggers loops.
    overseer_task = pb_dict.get('block_taskoverseer', {})
    fi_overseer = overseer_task.get('description', {}).get('translations', {}).get('fi', '')
    print("Overseer task snippet:", fi_overseer[:400])

if __name__ == "__main__":
    analyze_theoretical_blindspots()
