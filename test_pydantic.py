import json
import sys
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(r'c:\src\quorum').resolve()))

from backend.models.dtos.config import ComponentResponse
from pydantic import ValidationError, TypeAdapter

adapter = TypeAdapter(ComponentResponse)
data=json.load(open('c:/src/quorum/data/db.json', encoding='utf-8'))

valid = 0
failed = 0
for c in data.get('components', {}).values():
    try:
        adapter.validate_python(c)
        valid += 1
    except ValidationError as e:
        failed += 1
        print(f"Failed ID: {c.get('id')} - {e.errors()[0]['msg']}")
        break

print(f"Total Valid: {valid}, Total Failed: {failed}")
