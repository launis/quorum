import json
import os
import sys

def repair_json(file_path):
    print(f"Repairing {file_path}...")
    
    if not os.path.exists(file_path):
        print("File not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        # Use raw_decode to parse just the first valid JSON object
        decoder = json.JSONDecoder()
        data, index = decoder.raw_decode(content)
        
        print(f"Successfully decoded JSON. Length: {len(content)}, Valid End Index: {index}")
        
        if index < len(content):
            print("Found extra data (garbage). Truncating file...")
            # Write back only the valid part
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print("File repaired and saved.")
        else:
            print("File appears valid (no extra data found by raw_decode).")

    except json.JSONDecodeError as e:
        print(f"CRITICAL: Could not decode JSON even partially: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    repair_json("data/db.json")
