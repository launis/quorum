"""Inspect Audit Logs."""
import os

from tinydb import TinyDB

DB_PATH = "data/db.json"


def inspect_audit_logs():
    """Print the last 5 audit logs."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    db = TinyDB(DB_PATH)
    audit_table = db.table("audit_logs")

    logs = audit_table.all()
    print(f"Total Audit Logs: {len(logs)}")

    # Sort by timestamp (if present) or just take last
    # Using 'timestamp' field which is ISO string
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    print("\n--- Last 5 Audit Events ---")
    for log in logs[:5]:
        print(f"[{log.get('timestamp')}] {log.get('action')} by {log.get('actor_uid')}")
        print(f"  Details: {log.get('details')}")
        print("-" * 30)


if __name__ == "__main__":
    inspect_audit_logs()
