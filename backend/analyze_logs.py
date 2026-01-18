
import json
import re
import sys

def analyze_log(filepath):
    try:
        # PowerShell redirection often creates UTF-16LE
        with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
            content = f.read()
    except Exception:
        # Fallback to utf-8 if utf-16 fails
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

    print(f"Log Size: {len(content)} characters")

    # 1. Check Execution Status
    status_match = re.search(r"Status: (\w+)", content)
    status = status_match.group(1) if status_match else "Unknown"
    print(f"Workflow Status: {status}")

    # Search for specific agent logs
    print("\n--- AGENT EXECUTION VERIFICATION ---")
    agents_to_check = ["RetrievalAgent", "XAIReporterAgent", "GuardAgent", "JudgeAgent"]
    
    for line in content.splitlines():
        for agent in agents_to_check:
            if f"[{agent}]" in line or f"Task '{agent}'" in line or (agent == "RetrievalAgent" and "RetrievalAgent" in line):
                print(f"FOUND {agent}: {line.strip()[:200]}") # Print first 200 chars

    # Confirm Status from content if regex failed (manual check)
    if "EXECUTION COMPLETE" in content:
        print("\nWorkflow Execution: APPEARS COMPLETE")
    else:
        print("\nWorkflow Execution: INCOMPLETE / INTERRUPTED")

    # Debug failure of results printing
    if "CRITICAL EXECUTION FAILURE" in content:
        print("\n!!! CRITICAL FAILURE DETECTED !!!")
        # print context
        idx = content.find("CRITICAL EXECUTION FAILURE")
        print(content[idx:idx+300])


if __name__ == "__main__":
    analyze_log("c:/src/quorum/backend/full_debug_log.txt")
