from tinydb import TinyDB
try:
    db = TinyDB('data/db.json')
    workflows = db.table('workflows').all()
    print("--- WORKFLOWS ---")
    for w in workflows:
        print(f"ID: {w.get('id')} | Name: {w.get('name')}")
except Exception as e:
    print(e)
