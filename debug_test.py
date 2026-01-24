import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# Fake imports to run minimal test
import os
from pathlib import Path

# Mock modules before importing router
sys.modules["backend.dependencies"] = MagicMock()
sys.modules["backend.core.engine"] = MagicMock()
sys.modules["backend.core.registry"] = MagicMock()
sys.modules["backend.database.repository"] = MagicMock()
sys.modules["backend.logging_config"] = MagicMock()
sys.modules["backend.models.auth"] = MagicMock()
sys.modules["backend.models.view"] = MagicMock()
sys.modules["backend.api.bff_transformer"] = MagicMock()
sys.modules["sse_starlette.sse"] = MagicMock()

# We need TokenData and UserRole
from collections import namedtuple
TokenData = namedtuple("TokenData", ["uid", "role", "organization_id"])
class UserRole:
    ROOT = "root"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

sys.modules["backend.models.auth"].TokenData = TokenData
sys.modules["backend.models.auth"].UserRole = UserRole

# Mock Storage
class LocalFileStorage:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
    def exists(self, path): return True
    def save(self, path, data): return str(self.base_path / path)

sys.modules["backend.services.storage"] = MagicMock()
sys.modules["backend.services.storage"].LocalFileStorage = LocalFileStorage

# Now import the router function
# We need to mock 'backend.api.execution_router' imports
# This is hard because it imports a lot. 
# Better approach: Just run the test file using pytest but trace the output manually?
# Or write a small script that imports the test file and runs the specific test function?

print("Skipping full import complexity. Relying on simple check.")
