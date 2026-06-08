import json
from pathlib import Path

OLD_EXE = Path(r"c:\src\quorum\tmp\data\files\executions\exe_0a3128e6248a4cb8a5e2b4213b8ad290\execution_trace.json")
NEW_EXE = Path(r"c:\src\quorum\data\files\executions\exe_1b0c6ec14c244061a98fdf1c4d7d6932\execution_trace.json")

def print_stats(name, path):
    if not path.exists():
        print(f"{name}: File not found")
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"=== {name} ===")

    total_tokens = 0
    analyst_anchors = 0
    synthesis_payload_evals = 0

    for event in data:
        event_type = event.get("event_type", "").lower()
        step_name = event.get("step_name", "")
        content = event.get("content", {})

        # Count tokens
        if event_type == "api_call":
            usage = content.get("usage", {})
            tokens = usage.get("total_tokens", 0)
            total_tokens += tokens

            # If it's synthesis, count how many evals went into the prompt
            if "synthesis" in step_name.lower():
                prompt = str(content.get("prompt", ""))
                # Count how many times exact_quote appears in the prompt to estimate evals
                synthesis_payload_evals = prompt.count("exact_quote")
                print(f"  Synthesis Step Tokens: {tokens} (Prompt Evals: {synthesis_payload_evals})")

        # Count anchors from analyst
        if event_type == "step_output" and step_name == "sr_5a8ae009eee44fe2":
            result = content.get("output", {})
            if isinstance(result, dict):
                for k, v in result.items():
                    if isinstance(v, dict) and "localized_anchors_found" in v:
                        analyst_anchors += len(v["localized_anchors_found"])

    print(f"  Total API Tokens: {total_tokens}")
    print(f"  Analyst Anchors Found: {analyst_anchors}")
    print(f"  Total Events: {len(data)}\n")

print_stats("OLD (Ennen korjausta)", OLD_EXE)
print_stats("NEW (Korjauksen j\u00e4lkeen)", NEW_EXE)
