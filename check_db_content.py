import json
from tinydb import TinyDB

db = TinyDB(r'c:\Users\risto\OneDrive\quorum\data\db.json')
components = db.table('components').all()

print(f"Total components: {len(components)}")
for comp in components:
    content = comp.get('content', '')
    if not content:
        print(f"EMPTY CONTENT: {comp.get('id')}")
    else:
        print(f"OK: {comp.get('id')} (Length: {len(content)})")
