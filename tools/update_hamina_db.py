
import json
from tinydb import TinyDB, Query
DB_PATH = "data/db.json"
db = TinyDB(DB_PATH)
table = db.table('system_config')
QueryObj = Query()
entry = table.get(QueryObj.id == 'model_registry')
entry['models']['google']['fast']['model_name'] = "vertex_ai/gemini-2.5-flash"
entry['models']['google']['deep']['model_name'] = "vertex_ai/gemini-2.5-pro"
table.upsert(entry, QueryObj.id == 'model_registry')
print("HAMINA CONFIG UPDATED: vertex_ai/gemini-2.5-flash / vertex_ai/gemini-2.5-pro")
