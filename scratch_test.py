import json
import os
from pprint import pprint

def main():
    json_path = r"C:\src\quorum\data\files\executions\exe_99086245d3af448f872c408f9dd7445a\execution.json"
    if not os.path.exists(json_path):
        print("execution.json not found")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    profile_cache = data.get("profile_syntheses", {}).get("sys_a9821f0088924b17", {})
    if not profile_cache:
        profile_cache = list(data.get("profile_syntheses", {}).values())[0]
        
    print("KEYS:", profile_cache.keys())
    
    # Check what is in content_blocks
    cb = profile_cache.get("content_blocks", [])
    print(f"content_blocks len: {len(cb)}")
    for i, b in enumerate(cb):
        print(f"[{i}] {b.get('block_type')} -> {str(b.get('text', ''))[:50]}")
        
    synth_md = profile_cache.get("synthesized_markdown", "")
    print(f"synthesized_markdown len: {len(synth_md)}")
    print(f"Snippet: {synth_md[:100]}")

if __name__ == "__main__":
    main()
