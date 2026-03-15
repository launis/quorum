import sys
sys.path.insert(0, r'c:\src\quorum')
import httpx
import jwt
import json
import time
from backend_v2.services.auth import JWT_SECRET, JWT_ALGORITHM

token = jwt.encode(
    {'sub': '10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b', 'exp': time.time()+3600, 'type': 'impersonation'},
    JWT_SECRET, algorithm=JWT_ALGORITHM
)

res = httpx.get(
    'http://localhost:8000/api/v2/execution/executions/9734afec-08b7-40f2-9162-b36866fb5ee0',
    headers={'Authorization': 'Bearer ' + token}
)
data = res.json().get('results', {})

# Save to file
path = r'c:\src\quorum\docs\latest_results.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print(f"Results written to {path}")
