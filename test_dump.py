import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'c:\src\quorum').resolve()))
import json
from backend.models.dtos.config import _component_adapter

data = json.load(open('c:/src/quorum/data/db.json', encoding='utf-8'))['components']
c = next(v for v in data.values() if v['id'] == 'ca9d9ae7-41ce-44d4-8a8f-efd2e0bd80a9')
validated = _component_adapter.validate_python(c)
print('V dump keys:', list(validated.model_dump().keys()))
