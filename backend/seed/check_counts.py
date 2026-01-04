import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

try:
    from backend.seed.verifier import EXCLUDED_TABLES, load_firestore_data
    # We will manually load json files to be sure
except ImportError as e:
    print(f"Error importing verifier: {e}")
    sys.exit(1)


def load_json(path):
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def count_items(data, name):
    counts = {}
    if not data:
        return counts

    for key, value in data.items():
        if key in EXCLUDED_TABLES:
            continue
        if key == "_default":  # TinyDB artifact
            for default_key, default_val in value.items():
                if isinstance(default_val, dict):
                    counts[default_key] = len(default_val)
            continue

        if isinstance(value, list):
            counts[key] = len(value)
        elif isinstance(value, dict):
            # Check if it's a TinyDB table (dict of dicts) or just a dict
            # If the first item is a dict, likely it's a table.
            if value and isinstance(list(value.values())[0], dict):
                counts[key] = len(value)
            else:
                # It might be a single object (like system_config sometimes?)
                # But usually our tables are lists or dicts of items.
                counts[key] = len(value)
    return counts


def main():
    root_dir = Path(__file__).resolve().parent.parent.parent
    seed_path = root_dir / "backend" / "seed" / "seed_data.json"
    prod_path = root_dir / "data" / "db.json"
    mock_path = root_dir / "backend" / "database" / "db_mock.json"
    creds_path = root_dir / "service-account.json"

    print("--- DATABASE RECORD COUNTS ---")

    seed_data = load_json(seed_path)
    seed_counts = count_items(seed_data, "SEED")

    prod_data = load_json(prod_path)
    prod_counts = count_items(prod_data, "PROD")

    mock_data = load_json(mock_path)
    mock_counts = count_items(mock_data, "MOCK")

    # Firestore
    # We need to know which keys to fetch. Use Seed keys.
    keys_to_fetch = set(seed_data.keys())
    firestore_data = load_firestore_data(creds_path, keys_to_fetch)
    fire_counts = count_items(firestore_data, "FIRE")

    all_keys = set(seed_counts.keys()) | set(prod_counts.keys()) | set(mock_counts.keys()) | set(fire_counts.keys())

    print(f"{'TABLE':<25} | {'SEED':<6} | {'PROD':<6} | {'MOCK':<6} | {'FIRE':<6}")
    print("-" * 65)

    for key in sorted(all_keys):
        if key in EXCLUDED_TABLES:
            continue
        s = seed_counts.get(key, 0)
        p = prod_counts.get(key, 0)
        m = mock_counts.get(key, 0)
        f = fire_counts.get(key, 0)

        # Highlight mismatches
        match = s == p == m == f
        marker = " " if match else "*"

        print(f"{key:<25} | {s:<6} | {p:<6} | {m:<6} | {f:<6} {marker}")

    print("-" * 65)
    print("* indicates mismatch in counts")


if __name__ == "__main__":
    main()
