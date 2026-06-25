import json
from collections import defaultdict

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))

score_inverse = defaultdict(lambda: {"true": 0, "false": 0})
score_examples = defaultdict(list)

for b in d.get("prompt_blocks", []):
    if b.get("category_id") != "matrix":
        continue
    block_label = b.get("label", {}).get("translations", {}).get("en", "?")
    for scale in b.get("scales", []):
        score = scale.get("score")
        scale_name = scale.get("name", {}).get("translations", {}).get("en", "?")
        ai_label = scale.get("ai_label", "?")
        for claim in scale.get("claims", []):
            claim_label = claim.get("label", {}).get("translations", {}).get("en", "?")
            for tda in claim.get("tda_assertions", []):
                inv = tda.get("inverse_evidence", False)
                if inv:
                    score_inverse[score]["true"] += 1
                else:
                    score_inverse[score]["false"] += 1
                
                if len(score_examples[score]) < 2:
                    score_examples[score].append({
                        "tda_id": tda.get("tda_id"),
                        "inverse": inv,
                        "extraction_rule": (tda.get("extraction_rule") or "")[:80],
                        "scale_name": scale_name,
                        "ai_label": ai_label[:60],
                        "claim": claim_label[:80],
                        "block": block_label,
                    })

print("=== INVERSE_EVIDENCE BY BARS SCORE LEVEL ===")
print(f"{'Score':>6} | {'inverse=true':>13} | {'inverse=false':>14} | {'% inverse':>10} | BARS Level")
print("-" * 80)
for score in sorted(score_inverse.keys(), key=lambda x: x if x is not None else -1):
    t = score_inverse[score]["true"]
    f = score_inverse[score]["false"]
    pct = t / (t + f) * 100 if (t + f) > 0 else 0
    s = str(score) if score is not None else "None"
    # Determine BARS level description
    if score == 1:
        bars = "Weak / Error"
    elif score == 2:
        bars = "Below Average"
    elif score == 3:
        bars = "Average"
    elif score == 4:
        bars = "Good"
    elif score == 5:
        bars = "Excellent"
    else:
        bars = "?"
    print(f"{s:>6} | {t:>13} | {f:>14} | {pct:>9.1f}% | {bars}")

total_t = sum(v["true"] for v in score_inverse.values())
total_f = sum(v["false"] for v in score_inverse.values())
print("-" * 80)
print(f"{'TOTAL':>6} | {total_t:>13} | {total_f:>14} | {total_t/(total_t+total_f)*100:>9.1f}%")

# Show the HYPOTHESIS: Does inverse cluster in low scores?
print("\n=== HYPOTHESIS: Do inverse rules cluster at low scores? ===")
for score in sorted(score_inverse.keys(), key=lambda x: x if x is not None else -1):
    t = score_inverse[score]["true"]
    f = score_inverse[score]["false"]
    total = t + f
    inv_pct = t / total * 100 if total > 0 else 0
    bar = "█" * int(inv_pct / 2) + "░" * (50 - int(inv_pct / 2))
    s = str(score) if score is not None else "?"
    print(f"  Score {s}: {bar} {inv_pct:.0f}% inverse ({t}/{total})")

print("\n=== EXAMPLES PER SCORE ===")
for score in sorted(score_examples.keys(), key=lambda x: x if x is not None else -1):
    print(f"\n--- Score {score} ---")
    for ex in score_examples[score]:
        inv_str = "INVERSE" if ex["inverse"] else "NORMAL "
        print(f"  [{inv_str}] {ex['tda_id']}")
        print(f"    AI Label: {ex['ai_label']}")
        print(f"    Claim: {ex['claim']}")
        print(f"    Rule: {ex['extraction_rule']}")
