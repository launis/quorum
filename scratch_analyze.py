import json
import sys
from collections import Counter


def analyze_atoms(file_path):
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)

    total_score_sum = 0
    total_matrices = 0

    # State counters
    atom_states = Counter()

    # Contextual override counters
    contextual_overrides = 0
    exact_quotes = 0

    print("=== Execution Analysis ===")

    for event in data:
        if event.get("event_type") == "output":
            step_name = event.get("step_name")
            content = event.get("content", {})

            # Check for matrix raw_score
            for k, v in content.items():
                if isinstance(v, dict) and "raw_score" in v:
                    score = v["raw_score"]
                    print(f"Matrix {k}: Score = {score}")
                    total_score_sum += score
                    total_matrices += 1

            # Look for evaluations array (from the raw step output)
            evals = content.get("evaluations", [])
            if not evals:
                # Sometimes it might be nested, let's search loosely
                for k, v in content.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) and "atom_id" in v[0]:
                        evals = v
                        break

            if evals:
                print(f"\nStep: {step_name}")
                print(f"Evaluated Atoms: {len(evals)}")

                for ev in evals:
                    # In V2, evaluation might not return a strict "state" like DLQ directly in the JSON response
                    # if it's evaluated natively. But let's check what fields we have:
                    atom_id = ev.get("atom_id")

                    # Usually, scoring hook calculates DLQ or TRUE/FALSE based on semantic reasoning and exact quote.
                    # But the raw LLM output has contextual_override, exact_quote, semantic_reasoning.
                    override = ev.get("contextual_override", False)
                    quote = ev.get("exact_quote")

                    if override:
                        contextual_overrides += 1
                        state = "CONTEXTUAL_TRUE"
                    elif quote and str(quote).strip():
                        exact_quotes += 1
                        state = "LITERAL_TRUE"
                    else:
                        state = "FALSE/DLQ (No evidence)"

                    atom_states[state] += 1

                    # Print interesting ones
                    if override:
                        print(f"  [Contextual Override] Atom {atom_id}: {ev.get('structural_location')} - {ev.get('semantic_reasoning')[:100]}...")

    print("\n=== Summary ===")
    print(f"Total Matrices evaluated: {total_matrices}")
    print(f"Atom States Distribution: {dict(atom_states)}")

if __name__ == "__main__":
    analyze_atoms(sys.argv[1])
