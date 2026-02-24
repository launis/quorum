import json

def main():
    old_file = r"c:\src\quorum\backend\seed\seed_data copy.json"
    new_file = r"c:\src\quorum\backend\seed\seed_data.json"
    
    with open(old_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)
    
    with open(new_file, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    old_comps = old_data.get("components", [])
    new_comps = new_data.get("components", [])

    if len(old_comps) == len(new_comps):
        for old_c, new_c in zip(old_comps, new_comps):
            new_c["slug"] = old_c["id"]
        
        with open(new_file, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4)
        print(f"Patched {len(new_comps)} components successfully.")
    else:
        print("Length mismatch! Attempting to map by content.")
        # Fallback mapping if order shifted
        for new_c in new_comps:
            content = new_c.get("content")
            # Find matching old component by content
            for old_c in old_comps:
                if old_c.get("content") == content:
                    new_c["slug"] = old_c["id"]
                    break
                    
        with open(new_file, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=4)
        print("Applied heuristic content mapping.")

if __name__ == "__main__":
    main()
