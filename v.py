import sys
import json
sys.path.insert(0, 'c:/src/quorum')
from backend.models.dtos.config import ComponentResponse
from pydantic import TypeAdapter

adapter = TypeAdapter(ComponentResponse)
db = 'data/db.json'
with open(db, encoding='utf-8') as f:
    data = json.load(f)['components']

drops = 0
for k, c in data.items():
    try:
        adapter.validate_python(c)
    except Exception as e:
        drops += 1
        print(f"FAILED {c.get('type')} ({c.get('id')}): {e}")

print(f"Total: {len(data)}, Drops: {drops}")
