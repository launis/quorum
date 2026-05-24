import json
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "db_v2.json"))

with open(db_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# TinyDB stores tables inside a "_default" key or custom tables
# Let's inspect the keys to find where 'executions' are stored
print("Database tables:")
for k in data.keys():
    print(f" - {k}")

# TinyDB stores tables, let's look for 'executions'
executions_table = data.get("executions", data.get("_default", {}))

executions = []
for k, v in executions_table.items():
    # TintDB record
    if isinstance(v, dict) and "id" in v:
        executions.append(v)
    elif isinstance(v, dict):
        for kk, vv in v.items():
            if isinstance(vv, dict) and "id" in vv:
                executions.append(vv)

# If still not found, let's dump a small portion to understand structure
if not executions:
    print("Could not find structured executions, let's print top-level keys inside the tables:")
    for table_name, table_data in data.items():
        print(f"Table: {table_name}")
        keys = list(table_data.keys())[:10]
        print(f"  Sample keys: {keys}")
        if keys:
            sample_val = table_data[keys[0]]
            print(f"  Sample value keys: {list(sample_val.keys()) if isinstance(sample_val, dict) else type(sample_val)}")

# Sort executions by created_at or other timestamp
try:
    executions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
except Exception:
    pass

print("\nRecent executions:")
for exe in executions[:10]:
    print(f"ID: {exe.get('id')} | Status: {exe.get('status')} | Created: {exe.get('created_at')} | Label: {exe.get('label')}")
