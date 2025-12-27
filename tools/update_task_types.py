from backend.database.wrapper import get_db_client
from backend.database.repository import TinyDBRepository
from tinydb import Query

def update_types():
    client = get_db_client()
    db = TinyDBRepository(client)
    
    targets = [
        "TASK_PERFORMATIVITY",
        "TASK_ARCHIVIST",
        "TASK_JUDGE",
        "TASK_COACH",
        "TASK_INTERACTION",
        "TASK_PANEL",
        "TASK_XAI"
    ]
    
    table = db.components._table # Access inner table for direct update if needed, or use search/update loop
    Q = Query()
    
    print(f"Updating {len(targets)} components to type='task'...")
    
    count = 0
    for cid in targets:
        # Check if exists
        item = table.search(Q.id == cid)
        if item:
            print(f"Updating {cid}...")
            table.update({"type": "task"}, Q.id == cid)
            count += 1
        else:
            print(f"Warning: Component {cid} not found.")
            
    print(f"Done. Updated {count} components.")

if __name__ == "__main__":
    update_types()
