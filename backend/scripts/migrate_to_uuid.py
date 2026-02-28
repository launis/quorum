import json
import os
import uuid

SEED_FILE = os.path.join(os.path.dirname(__file__), "..", "seed", "seed_data.json")

def generate_uuid():
    return str(uuid.uuid4())

def main():
    print(f"Loading {SEED_FILE}...")
    with open(SEED_FILE, encoding='utf-8') as f:
        data = json.load(f)

    # Pass 1: Mapping
    id_map = {}  # old_id -> new_id

    # We want to process these top-level lists
    # Note: 'system_config' items like models don't necessarily need UUIDs if they are fixed singletons,
    # but the plan says "Iterate through all top-level domains".
    domains_to_map = [
        "system_config", "organizations", "users", "components", "workflows",
        "steps", "agents", "concepts", "references", "claims", "matrices", "output_configs", "dimensions"
    ]

    for domain in domains_to_map:
        if domain not in data:
            continue

        print(f"Pass 1: Mapping {domain}...")
        for item in data[domain]:
            # Special case for users: rename uid to id
            if domain == "users" and "uid" in item:
                old_id = item.pop("uid")
                new_id = generate_uuid()
                item["id"] = new_id
                item["slug"] = old_id
                id_map[old_id] = new_id
            elif "id" in item:
                old_id = item["id"]
                # Skip if already a UUID (just in case it's run twice)
                try:
                    uuid.UUID(old_id)
                    continue  # already UUID
                except ValueError:
                    pass

                new_id = generate_uuid()
                item["id"] = new_id
                item["slug"] = old_id
                id_map[old_id] = new_id

    # Add exceptions or special mappings
    # If there are system IDs that must remain constant, we can revert them,
    # but the instructions say map them in slug and replace everywhere.

    print(f"Created map with {len(id_map)} entities.")

    # Pass 2: Relation Update
    # Let's write a generic recursive function that updates IDs
    def transform_value(val):
        """Recursively update string values if they exactly match an old_id."""
        if isinstance(val, str):
            if val in id_map:
                return id_map[val]
            # Check for "$step_name" syntax used in inputs mapping
            if val.startswith("$") and val[1:] in id_map:
                return "$" + id_map[val[1:]]
            return val
        elif isinstance(val, list):
            return [transform_value(v) for v in val]
        elif isinstance(val, dict):
            new_dict = {}
            for k, v in val.items():
                # Some keys in inputs dictionaries are also the step IDs
                new_k = id_map[k] if k in id_map else k
                new_dict[new_k] = transform_value(v)
            return new_dict
        else:
            return val

    print("Pass 2: Updating foreign keys...")

    for domain in domains_to_map:
        if domain not in data:
            continue
        # Apply transformation to the whole domain list
        data[domain] = transform_value(data[domain])

    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print("Migration complete. Run Round-Trip Protocol to verify.")
    # save mapping just in case
    map_file = os.path.join(os.path.dirname(__file__), "id_map.json")
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(id_map, f, indent=4)
    print(f"Saved mapping to {map_file}")

if __name__ == "__main__":
    main()
