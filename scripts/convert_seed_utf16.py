
import os
import json

FILE_PATH = r"c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json"

def convert_to_utf16():
    print(f"Converting {FILE_PATH} to UTF-16...")
    
    # Read existing content (try typical encodings)
    content = None
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            content = json.load(f)
    except Exception:
        try:
            with open(FILE_PATH, 'r', encoding='utf-16') as f:
                content = json.load(f)
        except Exception:
            print("Failed to read file in UTF-8 or UTF-16.")
            return

    # Write back as UTF-16
    with open(FILE_PATH, 'w', encoding='utf-16') as f:
        json.dump(content, f, indent=4, ensure_ascii=False)
        
    print("Successfully converted/verified as UTF-16.")

if __name__ == "__main__":
    convert_to_utf16()
