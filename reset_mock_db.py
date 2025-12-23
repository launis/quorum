
import json
from pathlib import Path

def reset_db():
    seed_path = Path("backend/database/seed_data.json")
    mock_db_path = Path("backend/database/db_mock.json")
    
    if not seed_path.exists():
        print(f"❌ Error: Seed data not found at {seed_path}")
        return
        
    print(f"Reading seed data from {seed_path}...")
    with open(seed_path, "r", encoding="utf-8") as f:
        seed_data = json.load(f)
        
    # Transform lists to TinyDB format (dict with string IDs)
    tinydb_data = {}
    
    for table_name, content in seed_data.items():
        if isinstance(content, list):
            # Convert list to dict: "1": item1, "2": item2
            table_dict = {}
            for i, item in enumerate(content, 1):
                table_dict[str(i)] = item
            tinydb_data[table_name] = table_dict
        elif isinstance(content, dict):
             # Already a dict (maybe metadata), keep as is or careful?
             # TinyDB expects tables to be dicts of docs.
             # If root keys are tables, assume they are good.
             tinydb_data[table_name] = content
        else:
             print(f"⚠️ Skipping unknown format for table '{table_name}'")

    # Ensure executions table is initialized
    if "executions" not in tinydb_data:
        tinydb_data["executions"] = {}
    
    print(f"Writing transformed data to {mock_db_path}...")
    with open(mock_db_path, "w", encoding="utf-8") as f:
        json.dump(tinydb_data, f, indent=4, ensure_ascii=False)
        
    print("✅ Database reset complete (TinyDB Format).")

if __name__ == "__main__":
    reset_db()
