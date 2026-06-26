import sys
import re

path = r"c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Fix identity_repo=X, system_repo=X followed by system_repo=X
c = re.sub(r'(identity_repo=[^,]+),\s*system_repo=[^,\n]+,\n\s*system_repo=[^,\n]+', r'\1,\n        system_repo=mock_repo_transformer', c)

# Fix identity_repo=AsyncMock(), system_repo=AsyncMock(), followed by system_repo=...
c = re.sub(r'(identity_repo=AsyncMock\(\)),\s*system_repo=AsyncMock\(\),\n\s*system_repo=[^\n]+', r'\1,\n        system_repo=mock_system_repo', c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("Fixed duplicates in test_blueprint.py")
