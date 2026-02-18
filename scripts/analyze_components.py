
import json
from collections import Counter

def analyze_components():
    DB_PATH = r"c:\src\quorum\backend\data\db.json"
    OUT_PATH = r"c:\src\quorum\analysis_components.txt"
    try:
        with open(OUT_PATH, "w", encoding="utf-8") as out:
            def log(msg):
                out.write(msg + "\n")
                try:
                    print(msg) 
                except:
                    pass 
            
            log(f"--- COMPONENT ANALYSIS ({DB_PATH}) ---")
            try:
                with open(DB_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                log(f"Error reading DB: {e}")
                return

            components = data.get("components", {})
            if not components:
                log("No components found.")
                return

            log(f"Total Components: {len(components)}")

            # 1. Analyze Types
            types = []
            for cid, comp in components.items():
                c_type = comp.get("type", "UNKNOWN")
                types.append(c_type)
            
            counts = Counter(types)
            log("\nComponent Types:")
            for c_type, count in counts.items():
                log(f"  - {c_type}: {count}")

            # 2. Inspect 'knowledge' or similar types deeply
            log("\n--- DETAILED INSPECTION ---")
            
            for c_type in counts.keys():
                log(f"\nType: '{c_type}'")
                samples = [c for c in components.values() if c.get("type") == c_type][:3]
                for s in samples:
                    sid = s.get("id", "?")
                    label = s.get("label", "?")
                    content = s.get("content", "")
                    
                    content_preview = ""
                    if isinstance(content, str):
                        if len(content) > 100:
                            content_preview = content[:100].replace("\n", " ") + "..." + f" [{len(content)} chars]"
                        else:
                            content_preview = content.replace("\n", " ")
                    elif isinstance(content, list):
                        content_preview = f"[List with {len(content)} items] Sample: {str(content[:1])}..."
                    elif isinstance(content, dict):
                        content_preview = f"[Dict with keys: {list(content.keys())}]"
                    else:
                        class_name = type(content).__name__
                        content_preview = f"[{class_name}] {str(content)[:50]}..."
                    
                    log(f"  ID: {sid} | Label: {label}")
                    log(f"  Content Type: {type(content).__name__}")
                    log(f"  Content: {content_preview}")
                    
                    meta = s.get("metadata", {})
                    if meta:
                        log(f"  Metadata: {meta}")
                    log("-" * 40)
    except Exception as e:
        print(f"Top Level Error: {e}")

if __name__ == "__main__":
    analyze_components()
