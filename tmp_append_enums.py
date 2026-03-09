import subprocess
import os

print("Appending V1 enums to V2 enums...")
content = subprocess.check_output(["git", "show", "HEAD:backend/models/enums.py"], text=True, encoding="utf-8")

# remove module docstring and standard enum imports to avoid conflict
content = content.replace("from enum import Enum", "")
import re
content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', content, count=1) 

with open("backend_v2/models/enums.py", "a", encoding="utf-8") as f:
    f.write("\n# --- Restored V1 Enums ---\n" + content)
    
print("Appended V1 enums. Now running auto-restore again...")
os.system("uv run python tmp_auto_restore.py")
