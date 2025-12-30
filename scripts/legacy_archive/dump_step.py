from tinydb import TinyDB, Query
import json

def dump_step():
    db = TinyDB('data/db_mock.json', encoding='utf-8')
    step = db.table('steps').get(Query().id == 'step_1')
    print(json.dumps(step, indent=2))

if __name__ == "__main__":
    dump_step()
