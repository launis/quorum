
import os
import shutil

FILE_PATH = r"c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json"

def fix_encoding():
    print(f"Checking encoding for {FILE_PATH}...")
    
    content = None
    
    # Try reading as UTF-16 (PowerShell default)
    try:
        with open(FILE_PATH, 'r', encoding='utf-16') as f:
            content = f.read()
        print("Read successfully as UTF-16.")
    except Exception:
        print("Not UTF-16.")
        
    if content is None:
        # Try UTF-8 with BOM?
        try:
            with open(FILE_PATH, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            print("Read successfully as UTF-8-SIG.")
        except Exception:
            pass

    if content is None:
        print("Could not read file with expected encodings. Aborting.")
        return

    # Write back as UTF-8
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Saved back as standard UTF-8.")

if __name__ == "__main__":
    fix_encoding()
