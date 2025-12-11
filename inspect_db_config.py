import json
from tinydb import TinyDB, Query

DB_PATH = r"c:\Users\risto\OneDrive\quorum\backend\database\db_mock.json"

try:
    db = TinyDB(DB_PATH, encoding='utf-8')
    table = db.table('system_config')
    Config = Query()
    res = table.search(Config.type == 'model_registry')

    if res:
        print("FOUND system_config (model_registry):")
        print(json.dumps(res[0], indent=2))
    else:
        print("No system_config entry found with type='model_registry'")

except Exception as e:
    print(f"Error: {e}")
