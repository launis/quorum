import urllib.request
import json
import traceback

def main():
    try:
        req = urllib.request.Request(
            'http://localhost:8000/builder/workflows', 
            headers={'x-user-role': 'ROOT', 'x-user-id': 'SystemId', 'x-org-id': 'system', 'Accept': 'application/json'}
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode())
        
        print(f"Palautettiin {len(data)} työnkulkua.")
        for w in data:
            print(f"ID: {w.get('id')}")
            desc = w.get('description')
            print(f"  Description: {desc!r} (type: {type(desc).__name__})")
            print("-" * 30)
            
    except Exception as e:
        print(f"Virhe: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
