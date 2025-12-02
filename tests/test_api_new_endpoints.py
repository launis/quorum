import requests
import time

BASE_URL = "http://localhost:8000"

def test_get_models():
    print("Testing GET /llm/models...")
    try:
        res = requests.get(f"{BASE_URL}/llm/models")
        if res.status_code == 200:
            print("SUCCESS:", res.json())
        else:
            print("FAILED:", res.status_code, res.text)
    except Exception as e:
        print("ERROR:", e)

def test_self_test():
    print("\nTesting POST /admin/self-test...")
    try:
        res = requests.post(f"{BASE_URL}/admin/self-test")
        if res.status_code == 200:
            print("SUCCESS:", res.json())
        else:
            print("FAILED:", res.status_code, res.text)
    except Exception as e:
        print("ERROR:", e)

def test_docs_update():
    print("\nTesting POST /admin/docs/update (Dry run)...")
    # This triggers a background task, so we just check if it accepts the request
    try:
        res = requests.post(f"{BASE_URL}/admin/docs/update?ai_enhanced=false")
        if res.status_code == 200:
            print("SUCCESS:", res.json())
        else:
            print("FAILED:", res.status_code, res.text)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    test_get_models()
    test_self_test()
    test_docs_update()
