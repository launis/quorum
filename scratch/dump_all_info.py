import json
import os

def dump_execution_details(path, run_label):
    print(f"\n========================================================")
    print(f"AUDITING DETAILS FOR {run_label}: {path}")
    print(f"========================================================")
    
    if not os.path.exists(path):
        print(f"Error: {path} does not exist.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        trace_list = json.load(f)
    
    if not isinstance(trace_list, list):
        print(f"Error: trace is not a list. Type is {type(trace_list)}")
        return

    print(f"Total outer events/steps in trace: {len(trace_list)}")
    
    # Resolve final step and other steps
    final_step = None
    all_matrices = {}
    profiler_metrics = {}
    
    for idx, step in enumerate(trace_list):
        content = step.get('content', {})
        if not content:
            continue
            
        # Collect matrices
        if '_evaluative_matrices' in content:
            all_matrices.update(content['_evaluative_matrices'])
            
        # Collect profiler metrics
        if 'profiler_metrics' in content:
            profiler_metrics = content['profiler_metrics']
            
        # Find step with scoring_result
        if 'scoring_result' in content or 'raw_inputs' in content:
            final_step = step
            print(f"Found final result wrapper at index {idx} in trace_list.")

    if not final_step and len(trace_list) > 16:
        final_step = trace_list[16]
        print(f"Fallback: using step index 16 as final step.")

    if not final_step:
        print("Error: Final step not found.")
        return

    final_content = final_step.get('content', {})
    raw_inputs = final_content.get('raw_inputs', {})
    scoring_result = final_content.get('scoring_result', {})
    
    # 1. Inputs (Phase 1)
    print("\n--- PHASE 1: Raw Inputs Validation ---")
    product_text = raw_inputs.get('product_text', '')
    chat_log = raw_inputs.get('chat_log', '')
    reflection_text = raw_inputs.get('reflection_text', '')
    print(f"Product Text length: {len(product_text)} chars ({len(product_text.split())} words)")
    print(f"Chat Log length: {len(chat_log)} chars ({len(chat_log.split())} words)")
    print(f"Reflection Text length: {len(reflection_text)} chars ({len(reflection_text.split())} words)")
    
    # 2. Assertions / Steps (Phase 2 & 3)
    # Let's inspect evaluations in all steps
    tda_evals = []
    for idx, step in enumerate(trace_list):
        content = step.get('content', {})
        if 'evaluations' in content:
            evals = content['evaluations']
            if isinstance(evals, list):
                tda_evals.extend(evals)
            elif isinstance(evals, dict):
                # if it is a dict, gather items
                tda_evals.extend(evals.values())

    print("\n--- PHASE 2: TDA Assertions ---")
    print(f"Total TDA evaluations found in trace: {len(tda_evals)}")
    true_count = sum(1 for e in tda_evals if e.get('rule_satisfied') is True)
    false_count = sum(1 for e in tda_evals if e.get('rule_satisfied') is False)
    dlq_count = sum(1 for e in tda_evals if e.get('rule_satisfied') is None or e.get('is_dlq') is True)
    print(f"Satisfied rules (True): {true_count}")
    print(f"Unsatisfied rules (False): {false_count}")
    print(f"DLQ rules: {dlq_count}")

    print("\n--- PHASE 3: Evaluative Matrices ---")
    print(f"Scoring Result from final step:")
    print(json.dumps(scoring_result, indent=2, ensure_ascii=False))
    print(f"\nAll collected _evaluative_matrices ({len(all_matrices)}):")
    for k, v in all_matrices.items():
        print(f"  {k}: {v}")
    if all_matrices:
        avg = sum(all_matrices.values()) / len(all_matrices)
        print(f"  Calculated Commensurate Average of {len(all_matrices)} matrices: {avg:.6f}")
        
    print("\n--- PHASE 4: Role & Control Metrics ---")
    print(f"Profiler Metrics: {profiler_metrics}")
    
    # Let's search for synthesized reports or evaluations to find qualitative references (Phase 5)
    print("\n--- PHASE 5: Qualitative Synthesis & Theories ---")
    found_synthesis = False
    
    # Let's search inside the final step's evaluations or other steps for synthesis text
    for idx, step in enumerate(trace_list):
        content = step.get('content', {})
        for k, v in content.items():
            if isinstance(v, str) and any(x in v.lower() for x in ['kahneman', 'toulmin', 'popper', 'systeemi', 'system 1', 'falsifio', 'perustel', 'auditoi', 'passenger', 'architect', 'arkkitehti']):
                print(f"Step {idx} field '{k}' contains theory/role reference (length {len(v)} chars):")
                print(v[:1200] + "\n... [truncated]\n")
                found_synthesis = True
            elif isinstance(v, dict):
                for nk, nv in v.items():
                    if isinstance(nv, str) and any(x in nv.lower() for x in ['kahneman', 'toulmin', 'popper', 'systeemi', 'system 1', 'falsifio', 'perustel', 'auditoi', 'passenger', 'architect', 'arkkitehti']):
                        print(f"Step {idx} field '{k}.{nk}' contains theory/role reference (length {len(nv)} chars):")
                        print(nv[:1200] + "\n... [truncated]\n")
                        found_synthesis = True
            elif isinstance(v, list):
                for i, item_v in enumerate(v):
                    if isinstance(item_v, str) and any(x in item_v.lower() for x in ['kahneman', 'toulmin', 'popper', 'systeemi', 'system 1', 'falsifio', 'perustel', 'auditoi', 'passenger', 'architect', 'arkkitehti']):
                        print(f"Step {idx} field '{k}[{i}]' contains theory/role reference (length {len(item_v)} chars):")
                        print(item_v[:1200] + "\n... [truncated]\n")
                        found_synthesis = True

dump_execution_details("data/files/executions/exe_b6c7f868eccf4e8988889daf3ae1dfd4/execution_trace.json", "Run 1 (exe_b6c7)")
dump_execution_details("data/files/executions/exe_2609de8feb6e47db8222e7385c45a796/execution_trace.json", "Run 2 (exe_2609)")

