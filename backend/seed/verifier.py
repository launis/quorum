import json
import logging
from datetime import UTC
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Tables to EXCLUDE from verification (Runtime Data)
EXCLUDED_TABLES = {
    "executions",
    "execution_results",
    "audit_logs",
    "document_chunks",
    "uploaded_documents",
    "chat_history",
}


def load_json(path: Path) -> dict[str, Any]:
    """Loads a JSON file."""
    if not path.exists():
        logger.error(f"File not found: {path}")
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {path}: {e}")
        return {}


def normalize_tinydb(db_data: dict[str, Any]) -> dict[str, Any]:
    """Normalizes TinyDB structure to match seed_data.json structure.
    TinyDB assumes {"table_name": {"default": {"1": {...}, "2": {...}}}}
    Seed assumes {"table_name": [ ...list of items... ]} OR dicts.
    """
    normalized = {}

    # TinyDB often wraps tables in "_default" if using default table,
    # BUT current db.json seems to have top-level keys as tables?
    # Let's check structure. Based on db.json provided:
    # {"components": {"1": {...}}, "system_config": {"1": {...}}}
    # It seems to use numeric keys as IDs.

    for table_name, table_content in db_data.items():
        if table_name in EXCLUDED_TABLES:
            continue

        # Check if table_content is a dict of items (TinyDB style)
        if isinstance(table_content, dict):
            # Extract items to a list or dict keyed by ID.
            # We prefer dict keyed by 'id' field if available, for comparison.
            items_map = {}
            for key, item in table_content.items():
                # TinyDB keys are strings "1", "2".
                # Item usually has an "id".
                if isinstance(item, dict):
                    # Resolution Logic: Match 'normalize_seed' logic
                    # 1. Knowledge Base -> 'term' (or 'id')
                    # 2. Users -> 'uid' (or 'id')
                    # 3. Others -> 'id'
                    item_id = None
                    if table_name == "knowledge_base":
                        item_id = item.get("term") or item.get("id")
                    else:
                        item_id = item.get("id") or item.get("uid")
                    if item_id:
                        items_map[item_id] = item
                    else:
                        # If no ID, use the key? Or skip?
                        # Seed data usually has IDs.
                        items_map[f"__no_id_{key}"] = item
            normalized[table_name] = items_map
        elif isinstance(table_content, list):
            # Already a list?
            items_map = {}
            for item in table_content:
                if isinstance(item, dict):
                    item_id = item.get("id")
                    if item_id:
                        items_map[item_id] = item
            normalized[table_name] = items_map

    return normalized


def normalize_seed(seed_data: dict[str, Any]) -> dict[str, Any]:
    """Normalizes seed_data.json structure for comparison.
    Seed data is usually {"table_name": [ ...list... ]}.
    """
    normalized = {}
    for table_name, table_content in seed_data.items():
        if table_name in EXCLUDED_TABLES:
            continue

        if isinstance(table_content, list):
            items_map = {}
            for item in table_content:
                if isinstance(item, dict):
                    # Resolve primary key based on table type
                    # Logic must match seeder.py to ensure keys align (especially for Firestore)
                    item_id = None
                    if table_name == "knowledge_base":
                        item_id = item.get("term") or item.get("id")
                    else:
                        item_id = item.get("id") or item.get("uid")

                    if item_id:
                        items_map[item_id] = item
            normalized[table_name] = items_map
        elif isinstance(table_content, dict):
            # Sometimes seed data uses dicts directly?
            # Based on seed_data.json, "system_config" is a LIST.
            # "models" is inside system_config? No, top level keys.
            normalized[table_name] = table_content

    return normalized


def compare_dicts(source: dict[str, Any], target: dict[str, Any], context: str) -> list[str]:
    """Recursively compares two dictionaries."""
    diffs = []

    # 1. Check keys
    source_keys = set(source.keys())
    target_keys = set(target.keys())

    missing_in_target = source_keys - target_keys
    extra_in_target = target_keys - source_keys

    if missing_in_target:
        diffs.append(f"[{context}] Missing keys in target: {missing_in_target}")
    if extra_in_target:
        diffs.append(f"[{context}] Extra keys in target: {extra_in_target}")

    # 2. Check values for common keys
    common_keys = source_keys.intersection(target_keys)
    for key in common_keys:
        val_source = source[key]
        val_target = target[key]

        # Deep compare if dicts
        if isinstance(val_source, dict) and isinstance(val_target, dict):
            diffs.extend(compare_dicts(val_source, val_target, f"{context}.{key}"))
        elif val_source != val_target:
            # Try to be smart about lists order
            if isinstance(val_source, list) and isinstance(val_target, list):
                # Simple check
                if val_source != val_target:
                    diffs.append(f"[{context}.{key}] Content mismatch (List)")
            else:
                diffs.append(f"[{context}.{key}] Mismatch: Source='{val_source}' vs Target='{val_target}'")

    return diffs

    # ... (existing imports and exclusions)


try:
    from google.cloud import firestore
except ImportError:
    firestore = None


def load_firestore_data(credentials_path: Path, seed_keys: set[str]) -> dict[str, Any]:
    """Fetches data from Firestore for keys present in seed_data."""
    if not firestore:
        logger.warning("google-cloud-firestore not installed. Skipping Firestore verification.")
        return {}

    if not credentials_path.exists():
        logger.error(f"Service account file not found: {credentials_path}")
        return {}

    try:
        db = firestore.Client.from_service_account_json(str(credentials_path))
        data = {}

        print(f"   (Connecting to Firestore with {credentials_path.name}...)")

        for collection_name in seed_keys:
            if collection_name in EXCLUDED_TABLES:
                continue

            # Fetch all docs in collection
            docs = db.collection(collection_name).stream()
            items_map = {}
            for doc in docs:
                doc_dict = doc.to_dict()
                # Firestore items don't always have 'id' inside the dict,
                # but we usually start with doc.id
                item_id = doc.id

                # Special handling: Don't inject 'id' if checking Users (which use 'uid')
                # or if the item already has a likely primary key (like 'term').
                # Injecting 'id' blindly causes "Extra keys" diffs against Seed.
                should_inject_id = True
                if "uid" in doc_dict or "term" in doc_dict:
                    should_inject_id = False

                if should_inject_id and "id" not in doc_dict:
                    doc_dict["id"] = item_id

                if should_inject_id and "id" not in doc_dict:
                    doc_dict["id"] = item_id

                # CORRECT KEYING FOR COMPARISON:
                # If Knowledge Base, use the REAL term from body if available.
                # Firestore doc IDs might be sanitized (no slashes), but seed uses slashes.
                final_key = item_id
                if collection_name == "knowledge_base":
                    final_key = doc_dict.get("term") or item_id

                items_map[final_key] = doc_dict

            data[collection_name] = items_map
        return data
    except Exception as e:
        logger.error(f"Firestore connection failed: {e}")
        return {}


def run_verification(seed_path: Path, db_prod_path: Path, db_mock_path: Path, firestore_creds_path: Path = None):
    print("----------------------------------------------------------------")
    print("  DATABASE SYNCHRONIZATION VERIFIER")
    print("----------------------------------------------------------------")
    print(f"SEED: {seed_path}")
    print(f"PROD: {db_prod_path}")
    print(f"MOCK: {db_mock_path}")
    if firestore_creds_path:
        print(f"FIRE: {firestore_creds_path}")
    print("----------------------------------------------------------------")

    seed_raw = load_json(seed_path)
    prod_raw = load_json(db_prod_path)
    mock_raw = load_json(db_mock_path)

    if not seed_raw:
        print("[FATAL] Could not load Seed Data.")
        return

    # Normalize
    seed_norm = normalize_seed(seed_raw)
    prod_norm = normalize_tinydb(prod_raw)
    mock_norm = normalize_tinydb(mock_raw)

    # 1. Verify PROD
    print("\n--- VERIFYING PROD DB (data/db.json) ---")
    prod_diffs = compare_dicts(seed_norm, prod_norm, "ROOT")
    if not prod_diffs:
        print("[OK] PROD DB is fully SYNCED with Seed Data.")
    else:
        print(f"[WARN] PROD DB has {len(prod_diffs)} differences:")
        for d in prod_diffs[:10]:  # Limit output
            print(f"  - {d}")
        if len(prod_diffs) > 10:
            print(f"  ... and {len(prod_diffs) - 10} more.")

    # 2. Verify MOCK
    print("\n--- VERIFYING MOCK DB (backend/database/db_mock.json) ---")
    mock_diffs = compare_dicts(seed_norm, mock_norm, "ROOT")
    if not mock_diffs:
        print("[OK] MOCK DB is fully SYNCED with Seed Data.")
    else:
        print(f"[WARN] MOCK DB has {len(mock_diffs)} differences:")
        for d in mock_diffs[:10]:
            print(f"  - {d}")
        if len(mock_diffs) > 10:
            print(f"  ... and {len(mock_diffs) - 10} more.")

    # 3. Verify FIRESTORE
    firestore_diffs = []
    if firestore_creds_path:
        print("\n--- VERIFYING FIRESTORE (Cloud) ---")
        # We only look for collections that exist in seed_norm
        firestore_data = load_firestore_data(firestore_creds_path, set(seed_norm.keys()))
        if firestore_data:
            firestore_diffs = compare_dicts(seed_norm, firestore_data, "ROOT")
            if not firestore_diffs:
                print("[OK] FIRESTORE is fully SYNCED with Seed Data.")
            else:
                print(f"[WARN] FIRESTORE has {len(firestore_diffs)} differences:")
                for d in firestore_diffs[:10]:
                    print(f"  - {d}")
                if len(firestore_diffs) > 10:
                    print(f"  ... and {len(firestore_diffs) - 10} more.")
        else:
            print("[WARN] Skipped Firestore verification (No data or connection failed).")
            # Treat as error for final result? Or just warning?
            # Let's say diffs exist if connection failed implies we don't know status.

    # 4. Smart Recommendations
    print("\n--- SYNCHRONIZATION ANALYSIS ---")
    recommendations = []

    # Helper to find max timestamp in a dataset
    from datetime import datetime

    def get_max_timestamp(data: Any) -> datetime:
        # Start with a distinct minimum that is also timezone-aware (UTC)
        max_ts = datetime.min.replace(tzinfo=UTC)

        if isinstance(data, dict):
            for _k, v in data.items():
                if isinstance(v, (dict, list)):
                    ts = get_max_timestamp(v)
                    if ts > max_ts:
                        max_ts = ts
                elif isinstance(v, str):
                    # Check for ISO format-ish
                    if v.startswith("202") and "T" in v:
                        try:
                            # Normalize string format
                            iso_str = v.replace("Z", "+00:00")
                            ts = datetime.fromisoformat(iso_str)
                            # If the parsed timestamp is naive, assume UTC
                            if ts.tzinfo is None:
                                ts = ts.replace(tzinfo=UTC)
                            if ts > max_ts:
                                max_ts = ts
                        except ValueError:
                            pass
        elif isinstance(data, list):
            for item in data:
                ts = get_max_timestamp(item)
                if ts > max_ts:
                    max_ts = ts
        return max_ts

    # Limit timestamps scan to synced tables only to avoid false positives from runtime data
    # (e.g. recent logs/executions in Prod shouldn't make Seed look outdated)
    SYNCED_TABLES = [
        "organizations",
        "users",
        "system_config",
        "components",
        "steps",
        "workflows",
        "knowledge_base",
        "dimensions",
        "banned_phrases",
        "model_registry",
    ]

    def get_scoped_data(full_data: dict[str, Any]) -> dict[str, Any]:
        """Returns only the subsets of data that are subject to syncing."""
        if not isinstance(full_data, dict):
            return full_data
        return {k: v for k, v in full_data.items() if k in SYNCED_TABLES}

    ts_seed = get_max_timestamp(seed_raw)  # Seed is already scoped
    ts_prod = get_max_timestamp(get_scoped_data(prod_raw))
    ts_mock = get_max_timestamp(get_scoped_data(mock_raw))
    ts_fire = get_max_timestamp(firestore_data) if firestore_creds_path and firestore_data else datetime.min

    # Define a timezone-aware minimum for comparison
    MIN_DT = datetime.min.replace(tzinfo=UTC)

    print("LATEST UPDATES DETECTED:")
    print(f"  Seed  : {ts_seed if ts_seed > MIN_DT else 'N/A'}")
    print(f"  Prod  : {ts_prod if ts_prod > MIN_DT else 'N/A'}")
    print(f"  Mock  : {ts_mock if ts_mock > MIN_DT else 'N/A'}")
    if firestore_creds_path:
        print(f"  Fire  : {ts_fire if ts_fire > MIN_DT else 'N/A'}")
    print("")

    # Logic for PROD
    if prod_diffs:
        if ts_prod > ts_seed:
            recommendations.append(
                "[Prod -> Seed] Prod is NEWER.\n"
                "    Run the following commands in order:\n"
                "    1. python backend/seed/sync_db_to_seed.py\n"
                "    2. python backend/seed/seed_mock.py\n"
                "    3. python backend/seed/seed_firestore.py"
            )
        elif ts_seed > ts_prod:
            recommendations.append("[Seed -> Prod] Seed is NEWER.\n    Run: python backend/seed/seed_prod.py")
        else:
            recommendations.append("[?] Prod has diffs but timestamps match/unknown. Check manually.")

    # Logic for MOCK
    if mock_diffs:
        # Mock usually doesn't sync TO seed directly in scripts, usually deploy_mock_to_prod
        if ts_mock > ts_seed:
            recommendations.append(
                "[Mock -> Prod] Mock is NEWER.\n"
                "    Run the following commands in order:\n"
                "    1. python backend/seed/deploy_mock_to_prod.py\n"
                "    2. python backend/seed/sync_db_to_seed.py\n"
                "    3. python backend/seed/seed_firestore.py"
            )
        elif ts_seed > ts_mock:
            recommendations.append("[Seed -> Mock] Seed is NEWER.\n    Run: python backend/seed/seed_mock.py")
        else:
            # If timestamps match but diffs exist (e.g. dimensions table lacking timestamps),
            # it usually means Mock is outdated or missing data. Safe to re-seed mock.
            recommendations.append(
                "[Mock Out of Sync] Diffs detected despite timestamp match.\n    Run: python backend/seed/seed_mock.py"
            )

    # Logic for FIRESTORE
    if firestore_creds_path and firestore_diffs:
        if ts_fire > ts_seed:
            recommendations.append(
                "[WARN] Firestore is NEWER than Seed. No auto-sync script exists. Manually update seed_data.json?"
            )
        elif ts_seed > ts_fire:
            recommendations.append("[Seed -> Fire] Seed is NEWER. Run 'python backend/seed/seed_firestore.py'")

    if not recommendations:
        if not prod_diffs and not mock_diffs and (not firestore_creds_path or not firestore_diffs):
            print("RESULT: ALL SYSTEMS SYNCED.")
        else:
            # Diffs existed but timestamps were inconclusive
            print("RESULT: SYSTEMS OUT OF SYNC. Timestamps inconclusive.")
    else:
        print("RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  * {rec}")


if __name__ == "__main__":
    # If run directly for testing
    pass
