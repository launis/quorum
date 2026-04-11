import json
from tinydb import TinyDB, Query

def restore_users():
    print("Reading users from seed_data.json...")
    with open("c:/src/quorum/backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    users = data.get("users", [])
    if not users:
        print("Error: No users found in seed data!")
        return

    print("Restoring users to db_v2.json...")
    db = TinyDB("c:/src/quorum/data/db_v2.json")
    user_table = db.table("users")
    
    count = 0
    for u in users:
        user_table.upsert(u, Query().id == u["id"])
        count += 1
        
    db.close()
    print(f"✅ Risto, restored {count} mock users successfully. You can login now!")

if __name__ == "__main__":
    restore_users()
