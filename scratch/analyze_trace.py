import json

with open(r'c:\src\quorum\data\files\executions\exe_b28992472f37463cb21d3dcf336289ba\execution_trace.json', encoding='utf-8') as f:
    events = json.load(f)

print(f"Total events: {len(events)}")

# Collect all flattened atoms
all_atoms = []
for e in events:
    if e.get("event_type") == "AtomFlatteningEvent":
        all_atoms.extend(e.get("content", {}).get("flattened_atoms", []))

print(f"Total flattened atoms: {len(all_atoms)}")

failed = 0
passed = 0
high_entropy_failed = 0
high_entropy_total = 0

for a in all_atoms:
    res = a.get("boolean_result")
    if res:
        passed += 1
    else:
        failed += 1

    tda = a.get("tda_assertion", {})
    if tda.get("high_entropy"):
        high_entropy_total += 1
        if not res:
            high_entropy_failed += 1

print(f"Passed atoms: {passed}, Failed atoms: {failed}")
print(f"High Entropy atoms: {high_entropy_total}, Failed HE atoms: {high_entropy_failed}")

# Let's also print some reasons for failure of high entropy atoms
print("\nSample reasoning for failed High Entropy atoms:")
samples_printed = 0
for a in all_atoms:
    tda = a.get("tda_assertion", {})
    if tda.get("high_entropy") and not a.get("boolean_result"):
        print(f"--- Rule: {tda.get('ai_rule_description')[:100]}...")
        print(f"--- Justification: {a.get('justification')}")
        samples_printed += 1
        if samples_printed >= 3:
            break
