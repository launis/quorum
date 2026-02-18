
import json
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"c:\src\quorum\backend\data\db.json"
OUT_PATH = r"c:\src\quorum\analysis_large_content.txt"

def find_large_strings():
    print(f"--- SEARCHING FOR LARGE CONTENT (>500 chars) IN {DB_PATH} ---")
    
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        with open(OUT_PATH, "w", encoding="utf-8") as out:
            def recurse(obj, path):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        recurse(v, path + [k])
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        recurse(v, path + [str(i)])
                elif isinstance(obj, str):
                    if len(obj) > 500:
                        preview = obj[:100].replace("\n", " ")
                        msg = f"FOUND at [{' -> '.join(path)}]: Length={len(obj)}\nPreview: {preview}...\n"
                        print(msg)
                        out.write(msg + "\n")
                        # If it looks like the document, print more to file
                        out.write(f"--- FULL CONTENT START ---\n{obj}\n--- FULL CONTENT END ---\n\n")

            recurse(data, [])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_large_strings()
