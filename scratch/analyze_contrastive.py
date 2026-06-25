import json
from collections import Counter

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))

contrastive_examples = []
unique_patterns = Counter()

for b in d.get("prompt_blocks", []):
    if b.get("category_id") != "matrix":
        continue
    for scale in b.get("scales", []):
        for claim in scale.get("claims", []):
            for tda in claim.get("tda_assertions", []):
                ce = tda.get("contrastive_example", "")
                if ce:
                    contrastive_examples.append(ce)
                    # Extract the ACCEPTABLE part for pattern analysis
                    acc = ce.split("UNACCEPTABLE")[0].strip()
                    unique_patterns[acc] += 1

print(f"=== CONTRASTIVE EXAMPLE DISTRIBUTION ===")
print(f"Total TDAs with contrastive_example: {len(contrastive_examples)}")
print(f"Unique patterns: {len(unique_patterns)}")
print()

print(f"=== TOP PATTERNS (by frequency) ===")
for pattern, count in unique_patterns.most_common(15):
    uses_xy = "X" in pattern and ("Y" in pattern or "Z" in pattern)
    marker = " [X/Y ABSTRACT]" if uses_xy else " [CONCRETE]"
    print(f"  [{count:3d}x]{marker}: {pattern[:120]}")
    print()

# Count how many use X/Y vs concrete
xy_count = sum(c for p, c in unique_patterns.items() if "X" in p and ("Y" in p or "Z" in p))
concrete_count = len(contrastive_examples) - xy_count
print(f"\n=== SUMMARY ===")
print(f"  X/Y abstract patterns: {xy_count}/{len(contrastive_examples)} ({xy_count/len(contrastive_examples)*100:.1f}%)")
print(f"  Concrete patterns:     {concrete_count}/{len(contrastive_examples)} ({concrete_count/len(contrastive_examples)*100:.1f}%)")
