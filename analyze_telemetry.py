import json

file_path = r"c:\src\quorum\data\files\executions\exe_b95c652a631647d0b43ba07eb56f1071\llm_telemetry.jsonl"
lines = []
with open(file_path, encoding="utf-8") as f:
    for line in f:
        lines.append(json.loads(line))

hits = [row for row in lines if row.get("cache_hit")]
misses = [row for row in lines if not row.get("cache_hit")]
total_tokens = sum(row.get("tokens", 0) for row in lines)

print(f"Total LLM Calls: {len(lines)}")
print(f"Cache Hits: {len(hits)} ({(len(hits) / len(lines) * 100) if lines else 0:.1f}%)")
print(f"Total Tokens Processed: {total_tokens:,}")

avg_hit = (sum(row.get("duration_ms", 0) for row in hits) / len(hits) / 1000) if hits else 0
avg_miss = (sum(row.get("duration_ms", 0) for row in misses) / len(misses) / 1000) if misses else 0

print(f"Avg latency for cache miss: {avg_miss:.1f}s")
print(f"Avg latency for cache hit: {avg_hit:.1f}s")

# Get unique step IDs
steps = set(row.get("step_id") for row in lines)
print(f"Unique DAG steps processed: {len(steps)}")
