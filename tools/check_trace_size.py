import json
from collections import defaultdict
from pathlib import Path


def analyze_traces():
    db_path = Path(r"c:\src\quorum\data\db_v2.json")
    if not db_path.exists():
        print(f"File not found: {db_path}")
        return

    with open(db_path, encoding="utf-8") as f:
        db = json.load(f)

    execs = db.get("executions", {})
    if not execs:
        print("No executions found.")
        return

    print(f"Found {len(execs)} executions. Analyzing all of them:\n")

    for ex_id, execution in execs.items():
        trace = execution.get("execution_trace", [])
        print(f"\n--- EXEC {ex_id} ---")
        if not trace:
            print("Trace Events: 0 (Skipping)")
            continue

        print(f"Trace Events: {len(trace)}")
        total_tokens = 0
        key_sizes = defaultdict(int)

        for i, event in enumerate(trace):
            e_type = event.get("event_type", "unknown")
            s_name = event.get("step_name", "unknown")
            content = event.get("content", {})

            content_str = json.dumps(content, ensure_ascii=False)
            est_tokens = len(content_str) // 4
            total_tokens += est_tokens
            key_sizes[s_name] += est_tokens

            size_kb = len(content_str) / 1024
            if est_tokens > 10000:
                print(
                    f"[{i:02d}] {e_type.ljust(8)} | {s_name.ljust(25)} | Size: {size_kb:.1f} KB (~{est_tokens} tokens)"
                )

        print(f"Total theoretical trace volume for {ex_id}: ~{total_tokens} tokens")
        if total_tokens > 0:
            top = sorted(key_sizes.items(), key=lambda x: x[1], reverse=True)[0]
            print(f"Top contributor: {top[0]} = ~{top[1]} tokens")


if __name__ == "__main__":
    analyze_traces()
