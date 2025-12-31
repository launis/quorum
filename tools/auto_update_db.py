
import json
from tinydb import TinyDB, Query
DB_PATH = "data/db.json"
db = TinyDB(DB_PATH)
table = db.table('system_config')
Query = Query()
entry = table.get(Query.id == 'model_registry')
entry['models']['google']['fast']['model_name'] = "vertex_ai/gemini-2.0-flash-exp"
entry['models']['google']['deep']['model_name'] = "vertex_ai/gemini-2.0-flash-exp"
table.upsert(entry, Query.id == 'model_registry')
print("DB UPDATED AUTOMATICALLY")
