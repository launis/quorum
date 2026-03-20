import requests
import json
import sys

EXEC_ID = "exe_f5de7581c7f04f18838ee8f875211bde"
BASE_URL = "http://localhost:8000/api/v2/executions"

headers = {
    "accept-language": "fi",
    "Authorization": "Bearer test-dev-token",
    "X-User-ID": "usr_test",
    "X-Organization-ID": "org_test"
}

def check_json():
    print(f"Testing JSON render for {EXEC_ID}...")
    url = f"{BASE_URL}/{EXEC_ID}/render?format=json"
    r = requests.get(url, headers=headers)
    print(f"JSON Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Blueprint Version: {data.get('blueprint', {}).get('version')}")
        print(f"Components found: {len(data.get('blueprint', {}).get('components', []))}")
    else:
        print("Error content:")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)

def check_pdf():
    print(f"Testing PDF render for {EXEC_ID}...")
    url = f"{BASE_URL}/{EXEC_ID}/render?format=pdf"
    r = requests.get(url, headers=headers)
    print(f"PDF Status: {r.status_code}")
    if r.status_code == 200:
        with open("test_output.pdf", "wb") as f:
            f.write(r.content)
        print("Success: Saved 'test_output.pdf' to workspace.")
    else:
        print("Error content:")
        try:
            print(json.dumps(r.json(), indent=2))
        except:
            print(r.text)

if __name__ == "__main__":
    check_json()
    print("-" * 40)
    check_pdf()
