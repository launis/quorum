import json
import os

def analyze_trace():
    trace_path = r'c:\src\quorum\data\files\executions\exe_add8965fdc7342c5950678fd9745dfb6\execution_trace.json'
    with open(trace_path, 'r', encoding='utf-8') as f:
        trace = json.load(f)

    # We want to check the payloads sent to the LLM (system prompt, user messages)
    # The trace might contain 'workflow_context', 'steps', etc.
    
    steps = trace.get("steps", {})
    
    # Let's find an LLM step, e.g. Analyst or similar, that processed chunks.
    # We will look for prompt fragments that prove P1, P4, P3.
    
    p1_found = False
    p4_rule_anchor_found = False
    p3_inverse_in_prompt = False
    p4_scoped_rubric = False
    
    print(f"Total steps in trace: {len(steps)}")
    
    for step_id, step_data in steps.items():
        if "llm_payloads" in step_data:
            payloads = step_data["llm_payloads"]
            for p in payloads:
                system_prompt = p.get("system_prompt", "")
                user_prompt = p.get("user_prompt", "")
                
                # Check P1: SCHEMA_PURITY_MANDATE
                if "SCHEMA_PURITY_MANDATE" in system_prompt or "strictly forbid" in system_prompt.lower():
                    p1_found = True
                    
                # Check P3: Inverse logic in prompt?
                if "If inverse_evidence is true" in system_prompt or "käänteislogiikka" in system_prompt.lower():
                    p3_inverse_in_prompt = True
                    
                # Check P4: rule_anchor in user_prompt
                if "rule_anchor" in user_prompt or "rule_anchor" in system_prompt:
                    p4_rule_anchor_found = True
                    
                # Check P4: scoped rubric. Does the XML rubric only contain rules for the atoms in this chunk?
                # We can just check if rule_anchor is present.
                
                # We can break early if we found examples
                if p1_found and p4_rule_anchor_found:
                    break
                    
    print(f"P1 (Schema Purity) in prompt: {p1_found}")
    print(f"P3 (Inverse logic STILL in prompt): {p3_inverse_in_prompt}")
    print(f"P4 (rule_anchor in prompt): {p4_rule_anchor_found}")
    
    # Check if there are any broken atoms (P0/P2) evaluated
    # Check evaluations in the trace
    broken_atoms = 0
    total_atoms = 0
    for step_id, step_data in steps.items():
        outputs = step_data.get("outputs", {})
        if isinstance(outputs, dict) and "evaluations" in outputs:
            for eval_item in outputs["evaluations"]:
                total_atoms += 1
                q = eval_item.get("question", "")
                if not q or "Do not evaluate" in q:
                    broken_atoms += 1
                    
    print(f"Total atoms evaluated: {total_atoms}")
    print(f"Broken atoms evaluated (P0/P2): {broken_atoms}")

if __name__ == '__main__':
    analyze_trace()
