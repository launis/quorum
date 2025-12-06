
import requests
import json

def test_llm_generate():
    url = "http://localhost:8000/llm/generate"
    payload = {
        "prompts": [{"role": "user", "parts": ["Hello, are you working?"]}],
        "model": "gemini-2.5-pro"
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        try:
            print("Response JSON:", json.dumps(response.json(), indent=2))
        except:
            print("Response Text:", response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_llm_generate()
