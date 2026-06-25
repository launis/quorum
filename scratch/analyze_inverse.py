import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))

inv_true = 0
inv_false = 0

for b in d.get("prompt_blocks", []):
    if b.get("category_id") != "matrix":
        continue
    for scale in b.get("scales", []):
        for claim in scale.get("claims", []):
            for tda in claim.get("tda_assertions", []):
                inv = tda.get("inverse_evidence", False)
                if inv:
                    inv_true += 1
                else:
                    inv_false += 1

total = inv_true + inv_false
print(f"INVERSE EVIDENCE DISTRIBUTION:")
print(f"  true:  {inv_true}/{total} ({inv_true / total * 100:.1f}%)")
print(f"  false: {inv_false}/{total} ({inv_false / total * 100:.1f}%)")
print()

# Now check the LLM prompt: does the LLM see the word "inverse" or "vice"?
# The answer is: YES, through the FAIL_FAST_MANDATE text in localization_compiler.py
# But the LLM does NOT see `decision: bool` with a description that tells it about inversion
# The description says: "True if the condition is physically met, False otherwise."
print("=== WHAT THE LLM SEES ===")
print("For inverse_evidence=true rules, the LLM prompt says:")
print('  "This is an inverse rule (Vice)."')
print('  "If rule_satisfied = True (no issues found), evidence_found MUST be False"')
print('  "If rule_satisfied = False (violation found), evidence_found MUST be True"')
print()
print("BUT the JSON schema says:")
print('  decision: bool = "True if the condition is physically met, False otherwise."')
print()
print("=== THE ACTUAL CONFUSION ===")
print("For a VICE rule like 'Find dogmatic markers without data':")
print("  LLM finds a dogmatic marker -> condition IS physically met -> decision=True")
print("  Backend sees evidence_found=True + inverse_evidence=True -> calculate_rule_satisfied returns NOT True = False")
print("  So the VICE is correctly detected as a violation (rule NOT satisfied)")
print()
print("BUT: If LLM interprets 'condition' as 'the text is GOOD' (no violation):")
print("  LLM finds a dogmatic marker -> text is NOT good -> decision=False")
print("  Backend sees evidence_found=True + inverse_evidence=True -> NOT True = False")
print("  Now it's a DOUBLE INVERSION: backend thinks rule is NOT satisfied, but it should be!")
print()
print("=== KEY INSIGHT ===")
print("The LLM sees TWO conflicting signals:")
print("  1. FAIL_FAST_MANDATE says 'this is inverse/vice'")
print("  2. Schema says 'True if condition is physically met'")
print("The LLM might pre-invert its answer, but the backend ALSO inverts -> double inversion")
