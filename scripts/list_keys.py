
import json

def print_keys(path, label):
    print(f"\n--- {label} KEYS ---")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k in sorted(data.keys()):
                print(k)
            
            if "dimensions" in data and label == "PROD":
                print("\nSAMPLE DIMENSION:")
                dims = data["dimensions"]
                if isinstance(dims, dict) and dims:
                    k = list(dims.keys())[0]
                    # Print full dimension to check if it's "knowledge"
                    print(json.dumps(dims[k], indent=2, ensure_ascii=False))
                elif isinstance(dims, list) and dims:
                    print(json.dumps(dims[0], indent=2, ensure_ascii=False))

            if "components" in data and label == "PROD":
                print("\nSAMPLE COMPONENT:")
                comps = data["components"]
                if isinstance(comps, dict) and comps:
                     found = False
                     # prioritizing prompts or knowledge items
                     for k, v in comps.items():
                         if v.get("type") in ["prompt", "knowledge"]:
                             print(json.dumps(v, indent=2, ensure_ascii=False))
                             found = True
                             break
                     if not found:
                         k = list(comps.keys())[0]
                         print(json.dumps(comps[k], indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    print_keys(r"c:\src\quorum\backend\data\db.json", "PROD")
    print_keys(r"c:\src\quorum\backend\seed\seed_data.json", "SEED")
