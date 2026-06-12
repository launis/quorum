import json
from collections import Counter

path = r'C:\src\quorum\data\files\executions\exe_ec05ce44941c4d82b4c61dcc84788bb6\execution_trace.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

pass_count = 0
fail_count = 0
system_error_count = 0
fail_reasons = Counter()

for item in data:
    if item.get('event_type') == 'output':
        parsed = item.get('content', {})
        evals = parsed.get('evaluations', [])

        for ev in evals:
            status = ev.get('status', 'N/A')
            reasoning = ev.get('semantic_reasoning', '')
            quote = ev.get('exact_quote')

            if 'LLM Unable to verify' in reasoning:
                system_error_count += 1
            elif status == 'PASS':
                pass_count += 1
            else:
                fail_count += 1
                if not quote:
                    fail_reasons['No exact quote provided'] += 1
                else:
                    fail_reasons['Quote provided but still failed'] += 1

print(f"Total Evaluations: {pass_count + fail_count + system_error_count}")
print(f"PASS: {pass_count}")
print(f"FAIL: {fail_count}")
print(f"SYSTEM ERROR (Fallback Collateral): {system_error_count}")
print("\nFAIL Breakdown:")
for reason, c in fail_reasons.items():
    print(f"  {reason}: {c}")

