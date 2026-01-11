"""Read Registry Tool."""
import json

from tinydb import Query, TinyDB

db = TinyDB("data/db.json")
Q = Query()
res = db.table("system_config").search(Q.type == "model_registry")
if res:
    print(json.dumps(res[0].get("models"), indent=2))
else:
    print("No registry found.")
