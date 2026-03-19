import urllib.request
import json

try:
    req = urllib.request.Request("http://localhost:8000/api/v2/execution/executions/")
    with urllib.request.urlopen(req) as response:
        executions = json.loads(response.read())
        
    if not executions:
        print("No executions!")
    else:
        latest = executions[0]["id"]
        print(f"Latest execution: {latest}")
        
        req2 = urllib.request.Request(f"http://localhost:8000/api/v2/execution/executions/{latest}/render?format=json")
        with urllib.request.urlopen(req2) as response2:
            payload = json.loads(response2.read())
            
        for c in payload.get("blueprint", {}).get("components", []):
            if c.get("title") == "overall_system_profile" or c.get("type") == "1d_gauge":
                print(json.dumps(c, indent=2))
except Exception as e:
    print(f"Error: {e}")
