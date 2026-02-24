import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'c:\src\quorum').resolve()))
import json
from backend.api.routes.config.components import _component_adapter

data = json.load(open('c:/src/quorum/data/db.json', encoding='utf-8'))['components']
valid = 0
for c in data.values():
    try:
        _component_adapter.validate_python(c)
        valid += 1
    except Exception as e:
        print(f"Dropped {c.get('id')}: {e}")
        break
print(f"Valid: {valid}")
