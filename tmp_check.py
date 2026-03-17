import json
with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
    print("Keys:", d.keys())
    wfs = d.get('workflows', [])
    print(f"Number of workflows: {len(wfs)}")
    for w in wfs:
        print("ID:", w.get('id'), "SLUG:", w.get('slug'))
