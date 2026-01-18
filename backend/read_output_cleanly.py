
import sys
import os

path = r"c:\src\quorum\backend\debug_output.txt"
if not os.path.exists(path):
    print("Debug output file not found.")
    sys.exit(1)

# Try reading appropriately
try:
    # PowerShell > redirection often produces UCS-2 LE BOM (UTF-16)
    with open(path, "r", encoding="utf-16") as f:
        content = f.read()
        print(content)
except Exception as e:
    print(f"UTF-16 read failed: {e}")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            print(f.read())
    except Exception as e2:
        print(f"UTF-8 read failed: {e2}")
