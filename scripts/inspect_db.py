
import json
import os

db_path = r"c:\src\quorum\data\db.json"

if not os.path.exists(db_path):
    print(f"Error: {db_path} does not exist.")
    exit(1)

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Database loaded from {db_path}")
    print("Top-level keys (Tables):")
    for key in data.keys():
        count = len(data[key]) if isinstance(data[key], (dict, list)) else "N/A"
        print(f" - {key}: {count} items")
        
        # If we find executions, lets print the last one's ID and Status
        if key in ["workflow_executions", "executions", "runs", "_default"]:
             print(f"   Inspecting {key}...")
             items = data[key]
             if isinstance(items, dict):
                 # TinyDB default format is {"_default": {"1": {...}, "2": {...}}}
                 # But here it seems we have named tables like "workflows".
                 # If "workflow_executions" is a dict of ID -> Item
                 last_id = list(items.keys())[-1]
                 last_item = items[last_id]
                 print(f"   Last Item ID: {last_id}")
                 print(f"   Last Item Status: {last_item.get('status', 'Unknown')}")
                 print(f"   Last Item Context Keys: {list(last_item.get('context', {}).keys())}")
                 
                 # Check specific fields relevant to the issue
                 if 'step_trace' in last_item:
                     print(f"   Step Trace Length: {len(last_item['step_trace'])}")
                     # Check if XAI step exists
                     xai_step = next((s for s in last_item['step_trace'] if s.get('step_id') == 'step_xai'), None)
                     if xai_step:
                         print("   XAI Step found in trace.")
                         print(f"   XAI Step Output: {xai_step.get('output')}")
                     else:
                        print("   XAI Step NOT found in trace.")

except Exception as e:
    print(f"Error reading DB: {e}")
