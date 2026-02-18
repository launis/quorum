
import json

DB_PATH = r"c:\src\quorum\data\db.json"
OUT_PATH = r"c:\src\quorum\analysis_deep_keys.txt"

def list_keys_recursive(data, prefix="", depth=0, max_depth=2, out=None):
    if depth > max_depth:
        return
    
    if isinstance(data, dict):
        for k, v in data.items():
            line = f"{prefix}{k}"
            # Add type info
            if isinstance(v, list):
                line += f" [List: {len(v)}]"
            elif isinstance(v, dict):
                line += f" [Dict: {len(v)}]"
            out.write(line + "\n")
            
            # Recurse
            if isinstance(v, (dict, list)):
                list_keys_recursive(v, prefix + "  ", depth + 1, max_depth, out)
                
    elif isinstance(data, list):
        # Just show structure of first item if it's a dict
        if data and isinstance(data[0], dict):
             out.write(f"{prefix}[0] (Sample Item)\n")
             list_keys_recursive(data[0], prefix + "  ", depth + 1, max_depth, out)

if __name__ == "__main__":
    try:
        with open(OUT_PATH, "w", encoding="utf-8") as out:
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "knowledge_base" in data:
                out.write("FOUND: knowledge_base collection!\n")
                kb = data["knowledge_base"]
                if isinstance(kb, dict):
                    out.write(f"Type: Dict, Size: {len(kb)}\n")
                    # Sample first 5 items
                    for k, v in list(kb.items())[:5]:
                        out.write(f"  [{k}] Type: {v.get('type', 'N/A')}, Term: {v.get('term', 'N/A')}\n")
                        # Print full item for one
                        out.write(f"  FULL ITEM: {json.dumps(v, ensure_ascii=False)}\n")
                elif isinstance(kb, list):
                    out.write(f"Type: List, Size: {len(kb)}\n")
                    for headers in kb[:5]:
                         out.write(f"  Item: {str(headers)[:100]}...\n")
            else:
                out.write("NOT FOUND: knowledge_base key is missing in top level.\n")
                out.write(f"Top Level Keys: {list(data.keys())}\n")

        print(f"Analysis written to {OUT_PATH}")
    except Exception as e:
        print(f"Error: {e}")
