"""Verify: Does _compress_synthesis_payload strip falsification_argument?

This is the ROOT CAUSE hypothesis: the compression function strips the very data
the LLM needs to produce XAI highlights.
"""
import json
import copy


def _strip_heavy_keys(obj):
    """Exact copy of the function from synthesis.py"""
    if isinstance(obj, dict):
        obj.pop("shuffled_atoms", None)
        
        if "evaluations" in obj:
            evals = obj["evaluations"]
            if isinstance(evals, list):
                lite_evals = []
                for ev in evals:
                    if isinstance(ev, dict):
                        eq_list = ev.get("exact_quotes", [])
                        sr = ev.get("semantic_reasoning")
                        
                        if not isinstance(eq_list, list):
                            eq_list = [eq_list] if eq_list else []
                        
                        valid_quotes = [
                            str(q).strip()
                            for q in eq_list
                            if q
                            and str(q).strip()
                            and str(q).strip() not in ("None", "null", "N/A", "N/A - insufficient data")
                            and not (str(q).strip().startswith("[") and str(q).strip().endswith("]"))
                        ]
                        
                        if valid_quotes:
                            lite_evals.append(
                                {
                                    "atom_id": ev.get("atom_id"),
                                    "exact_quotes": [q[:300] for q in valid_quotes],
                                    "semantic_reasoning": str(sr)[:300] if sr else None,
                                }
                            )
                lite_evals = lite_evals[:20]
                obj["evaluations"] = lite_evals if lite_evals else None
            else:
                obj["evaluations"] = None
            if not obj.get("evaluations"):
                obj.pop("evaluations", None)
        
        for _, val in list(obj.items()):
            _strip_heavy_keys(val)
    elif isinstance(obj, list):
        for item in obj:
            _strip_heavy_keys(item)


# Load a real evaluation from the failed trace
with open(r"c:\src\quorum\data\files\executions\exe_df88f3323fd441ab8fce2448b01c64a7\execution_trace.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Get the first matrix step output (event 3) which has evaluations with falsification_argument
event3 = data[3]
content = event3.get("content", {})
evals = content.get("evaluations", [])

print("=== BEFORE COMPRESSION ===")
print(f"Number of evaluations: {len(evals)}")
if evals:
    sample = evals[0]
    print(f"Sample evaluation keys: {list(sample.keys())}")
    fa = sample.get("falsification_argument", "NOT_FOUND")
    print(f"falsification_argument present: {'falsification_argument' in sample}")
    print(f"falsification_argument value: {str(fa)[:200]}")
    print(f"exact_quotes present: {'exact_quotes' in sample}")
    eq = sample.get("exact_quotes", [])
    print(f"exact_quotes value: {str(eq)[:200]}")

# Now compress
clean_content = copy.deepcopy(content)
_strip_heavy_keys(clean_content)

print("\n=== AFTER COMPRESSION ===")
compressed_evals = clean_content.get("evaluations")
print(f"evaluations present: {compressed_evals is not None}")
if compressed_evals:
    print(f"Number of evaluations after compression: {len(compressed_evals)}")
    if compressed_evals:
        print(f"Sample keys: {list(compressed_evals[0].keys())}")
        print(f"falsification_argument present: {'falsification_argument' in compressed_evals[0]}")
else:
    print("evaluations was STRIPPED ENTIRELY (no valid exact_quotes survived)")

# Now check: what DOES survive as extension data?
# The LLM is told to look for keys like 'blk_XXX_coaching' or 'blk_XXX_falsification'
# Check if those keys survive compression
print("\n=== EXTENSION SUFFIX KEYS IN CONTENT ===")
for key in content.keys():
    for ext in ["_coaching", "_falsification", "_theory_link", "_risk_flag"]:
        if ext in key:
            orig_val = content[key]
            comp_val = clean_content.get(key)
            print(f"  Key: {key}")
            print(f"    Original: {str(orig_val)[:100]}")
            print(f"    Compressed: {str(comp_val)[:100]}")
            print()

# Also check: do the matrix payload blocks (like blk_80732a33fe1947ee) survive?
print("\n=== MATRIX PAYLOAD BLOCKS (blk_*) ===")
for key in content.keys():
    if key.startswith("blk_") and "_" not in key[4:20]:  # Main matrix blocks, not extensions
        orig_val = content[key]
        comp_val = clean_content.get(key)
        if orig_val != comp_val:
            print(f"  {key}: CHANGED")
        else:
            print(f"  {key}: unchanged")
