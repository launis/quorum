import os

file_path = r"c:\Users\risto\OneDrive\quorum\backend\models\domain.py"

try:
    with open(file_path, "rb") as f:
        content = f.read()

    # Check for null bytes
    if b'\x00' in content:
        print(f"Null bytes found in {file_path}. Cleaning...")
        cleaned = content.replace(b'\x00', b'')
        
        # Write back
        with open(file_path, "wb") as f:
            f.write(cleaned)
        print("File cleaned successfully.")
    else:
        print("No null bytes found.")

except Exception as e:
    print(f"Error: {e}")
