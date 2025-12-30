import requests
import json

try:
    res = requests.get("http://localhost:8000/config/components")
    if res.status_code == 200:
        components = res.json()
        rule_1 = next((c for c in components if c['id'] == 'RULE_1'), None)
        if rule_1:
            print("FOUND RULE_1 in API Response:")
            print(json.dumps(rule_1, indent=2, ensure_ascii=False))
            
            # Check if content matches Header Mandates
            if "OSA 1: KOGNITIIVISEN KVOORUMIN PERUSMANDAATIT" in rule_1['content']:
                print("\nCRITICAL: RULE_1 content matches HEADER_MANDATES!")
            else:
                print("\nOK: RULE_1 content does NOT match HEADER_MANDATES.")
        else:
            print("RULE_1 NOT FOUND in API response.")
    else:
        print(f"API Error: {res.status_code} {res.text}")
except Exception as e:
    print(f"Connection Error: {e}")
