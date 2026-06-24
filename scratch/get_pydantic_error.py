import json

log_path = r"c:\src\quorum\backend_debug.log"
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "LLM Schema Validation Failed" in line:
            # The line might have 'validation_error' in it if we log it, or it's just plain text.
            # Let's just print the line and the next 2 lines
            print(line.strip())
