import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def audit_legacy():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    legacy_ids = []
    for comp in data['components']:
        cid = comp['id']
        # Check for rule_N, mandate_N, protocol_N, method_N where N is a digit
        if any(cid.startswith(prefix) and cid.split('_')[-1].isdigit() for prefix in ['rule_', 'mandate_', 'protocol_', 'method_']):
            legacy_ids.append((cid, comp['name'], comp.get('content', '')[:50]))
    
    print(f"Found {len(legacy_ids)} legacy numbered components:")
    for lid in legacy_ids:
        print(f"  {lid[0]}: {lid[1]} - {lid[2]}...")

if __name__ == "__main__":
    audit_legacy()
