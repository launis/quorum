
import requests

URL = "http://localhost:8000/tools/extract-text"

def verify():
    print(f"Testing {URL}...")
    try:
        # Create dummy file
        files = {'file': ('test.txt', b'This is a test content.')}
        response = requests.post(URL, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Endpoint is reachable.")
        elif response.status_code == 404:
            print("FAIL: Endpoint is 404 (Not Found). Fix did not work or reload failed.")
        else:
            print(f"FAIL: Endpoint returned {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify()
