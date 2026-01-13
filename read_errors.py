"""Script to read and display backend errors from JSON logs."""

import json

try:
    try:
        with open("backend_errors.json", encoding="utf-16") as f:
            data = json.load(f)
    except Exception:
        with open("backend_errors.json", encoding="utf-8") as f:
            data = json.load(f)

    for error in data:
        print(f"{error['filename']}:{error['location']['row']}")
except Exception as e:
    print(f"Error reading JSON: {e}")
