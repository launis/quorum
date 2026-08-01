import json
import re

with open(r'C:\Users\risto\.gemini\antigravity-ide\brain\191bf956-2baa-4654-b947-4a1f1fb98df4\.system_generated\tasks\task-159.log', encoding='utf-8') as f:
    text = f.read()
    
# Extract anything like "error": "..."
errors = re.findall(r'"error":\s*"([^"]+)"', text)
for e in errors:
    print(e)
