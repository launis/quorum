import sys
import re

path = r"c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Fix identity_repo=X -> identity_repo=X, system_repo=X
c = re.sub(r'identity_repo=(mock_repo_[a-zA-Z0-9_]+)\b(?!, system_repo=)', r'identity_repo=\1, system_repo=\1', c)
c = re.sub(r'identity_repo=AsyncMock\(\)(?!, system_repo=)', r'identity_repo=AsyncMock(), system_repo=AsyncMock()', c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed test_blueprint.py")
