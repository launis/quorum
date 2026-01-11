import sys
from pathlib import Path

from google.cloud import firestore
from google.oauth2 import service_account
from tinydb import TinyDB

# Adjust path to import backend modules if needed, roughly
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


def test_isolation():
    print("=" * 60)
    print(" 🧪 DATABASE ISOLATION TEST")
    print("=" * 60)

    # 1. Inspect Local DB (TinyDB)
    local_db_path = project_root / "data" / "db.json"
    print(f"\n[1] Checking Local DB: {local_db_path}")

    local_ids = set()
    if not local_db_path.exists():
        print("    -> File not found (Clean state?)")
    else:
        try:
            db = TinyDB(local_db_path)
            table = db.table("workflows")
            all_items = table.all()
            local_ids = {item.get("id") or item.get("execution_id") for item in all_items}
            print(f"    -> Found {len(local_ids)} workflows.")
            # print(f"    -> IDs: {sorted(list(local_ids))}")
        except Exception as e:
            print(f"    -> Error reading TinyDB: {e}")

    # 2. Inspect Firestore
    print("\n[2] Checking Firestore (Cloud)...")
    creds_path = project_root / "service-account.json"
    if not creds_path.exists():
        print(f"    -> CRITICAL: service-account.json not found at {creds_path}")
        return

    try:
        # Load creds explicitly
        creds = service_account.Credentials.from_service_account_file(str(creds_path))
        db_client = firestore.Client(credentials=creds)

        # Collection name assumed to be 'workflows' from repo logic
        docs = db_client.collection("workflows").stream()
        firestore_ids = set()
        for doc in docs:
            firestore_ids.add(doc.id)

        print(f"    -> Found {len(firestore_ids)} workflows.")
        # print(f"    -> IDs: {sorted(list(firestore_ids))}")

    except Exception as e:
        print(f"    -> Error connecting to Firestore: {e}")
        return

    # 3. Compare
    print("\n[3] Comparison")

    common = local_ids.intersection(firestore_ids)
    print(f"    -> Common IDs (Seeded/Duplicates): {len(common)}")

    unique_local = local_ids - firestore_ids
    print(f"    -> Unique to Local: {len(unique_local)}")
    if unique_local:
        print(f"       {sorted(list(unique_local))}")

    unique_firestore = firestore_ids - local_ids
    print(f"    -> Unique to Firestore: {len(unique_firestore)}")
    if unique_firestore:
        print(f"       {sorted(list(unique_firestore))}")

    # 4. Proving Isolation
    print("\n[4] Isolation Proof")
    test_id = "ISOLATION_TEST_LOCAL_ONLY"

    if test_id in firestore_ids:
        print(f"    -> ❌ FAIL: Test ID '{test_id}' found in Firestore! They are NOT isolated.")
    elif test_id in local_ids:
        print(f"    -> ✅ SUCCESS: Test ID '{test_id}' found ONLY in Local DB.")
        print("       (This means you modified Local DB and it did NOT leak to Firestore)")
    else:
        print(f"    -> 📝 Writing '{test_id}' to Local DB to prove isolation...")
        try:
            db = TinyDB(local_db_path)
            table = db.table("workflows")
            table.insert({"id": test_id, "name": "ISOLATION PROOF ITEM", "status": "TEST"})
            print("    -> Written. Now PLEASE RUN THIS SCRIPT AGAIN.")
            print("       If the next run shows it in Local but NOT Firestore, isolation is proven.")
        except Exception as e:
            print(f"    Error writing to Local DB: {e}")


if __name__ == "__main__":
    test_isolation()
