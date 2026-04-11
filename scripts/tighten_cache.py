import json
import os

CACHE_FILE = "backend_v2/seed/atomization_cache.json"
CLAIM_APPENDIX = " ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided. Implicit adherence or basic logical correctness MUST be rated as FALSE."

def main():
    if not os.path.exists(CACHE_FILE):
        print(f"Error: {CACHE_FILE} not found.")
        return

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    mutated_count = 0

    for cache_key, scales in data.items():
        if isinstance(scales, list):
            for scale in scales:
                claims = scale.get("claims", [])
                for claim in claims:
                    desc = claim.get("ai_description", "")
                    if "Evaluate as FALSE immediately unless explicit" not in desc:
                        claim["ai_description"] = desc + CLAIM_APPENDIX
                        mutated_count += 1
                        
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Cache payload tightening complete. Mutated {mutated_count} elements inside atomization_cache.json.")

if __name__ == "__main__":
    main()
