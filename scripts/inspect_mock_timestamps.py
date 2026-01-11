"""Inspect Timestamp Formatting in Mock DB."""
import json
import os
from datetime import datetime

mock_db_path = os.path.join("backend", "database", "db_mock.json")
try:
    with open(mock_db_path, encoding="utf-8") as f:
        data = json.load(f)
        # TinyDB format: {"_default": {"1": {...}, "2": {...}}} or {"executions": {"1": ...}}
        # Assuming table name is "executions"

        tables = data.get("executions", {})
        print(f"Reading {mock_db_path}...")
        print(f"Found {len(tables)} records in 'executions'.")

        for _key, record in tables.items():
            # Execution timestamps might be 'created_at' or 'start_time'
            ts = record.get("created_at") or record.get("start_time")
            exe_id = record.get("execution_id")

            # Convert timestamp to human readable if possible
            readable = "Unknown"
            if ts:
                try:
                    # Try ISO format
                    dt = datetime.fromisoformat(str(ts))
                    readable = dt.strftime("%H:%M")
                except Exception:
                    # Try timestamp float
                    try:
                        dt = datetime.fromtimestamp(float(ts))
                        readable = dt.strftime("%H:%M")
                    except Exception:
                        readable = str(ts)

            print(f"Execution {exe_id}: Timestamp={ts} ({readable})")

except Exception as e:
    print(f"Error: {e}")
