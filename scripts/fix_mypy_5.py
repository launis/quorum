import os

path = 'backend_v2/tests/unit/test_document_extraction.py'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('"not_a_dict"', '"not_a_dict"  # type: ignore')
    content = content.replace('"# Extracted PDF Content"', '"# Extracted PDF Content"  # type: ignore')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

path2 = 'backend_v2/tests/unit/test_mcp_tool_loop.py'
if os.path.exists(path2):
    with open(path2, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('content=None', 'content=""')
    with open(path2, 'w', encoding='utf-8') as f:
        f.write(content)
        
path3 = 'backend_v2/tests/unit/test_progress.py'
if os.path.exists(path3):
    with open(path3, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('dict | None', 'dict[str, Any] | None')
    if 'from typing import Any' not in content:
        content = 'from typing import Any\n' + content
    with open(path3, 'w', encoding='utf-8') as f:
        f.write(content)
