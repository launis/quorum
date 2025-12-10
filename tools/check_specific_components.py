from tinydb import TinyDB, Query
import sys
import os
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
DB_PATH = 'data/db_mock.json' # Force mock for check
print(f"Checking DB: {DB_PATH}")
db = TinyDB(DB_PATH)
components = db.table('components')
Component = Query()

ids_to_check = ['RULE_1', 'MANDATE_1_1', 'MANDATE_1.1', 'MANDATES', 'GLOBAL_RULES']

for cid in ids_to_check:
    res = components.search(Component.id == cid)
    if res:
        print(f"--- {cid} ---")
        try:
            content = str(res[0].get('content'))
            print(content[:500].encode('utf-8').decode('utf-8')) # Print first 500 chars safely
        except Exception as e:
            print(f"Error printing content: {e}")
        print("...")
    else:
        print(f"--- {cid} NOT FOUND ---")
