import re

log_path = r"c:\src\quorum\backend_debug.log"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Look for traceback or exact error messages around "Schema Validation Failed"
lines = content.splitlines()
for i, line in enumerate(lines):
    if "LLM Schema Validation Failed" in line:
        print(f"--- Error at line {i} ---")
        # Print next 15 lines to see the traceback
        for j in range(max(0, i-2), min(len(lines), i + 20)):
            if "ValidationError" in lines[j] or "1 validation error" in lines[j] or "ValueError" in lines[j] or "Input should be" in lines[j]:
                print(lines[j])
