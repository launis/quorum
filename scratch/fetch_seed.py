import json
import urllib.request

url = 'https://raw.githubusercontent.com/launis/quorum/main/backend_v2/seed/seed_data.json'
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())

for pb in data.get('prompt_blocks', []):
    if pb.get('slug') in ['matrix_causal_analyst', 'matrix_archivist']:
        print(f"=== {pb.get('slug')} ===")
        print(json.dumps(pb.get('scales', []), indent=2))
