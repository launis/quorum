import socket
import requests
import json
import base64

HOST = "127.0.0.1"
PORT = 8000
API_URL = f"http://{HOST}:{PORT}/executions/" # Correct Endpoint

HEADERS = {
    "Authorization": "Bearer mock_token"
}

def check_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((HOST, PORT))
        if result == 0:
            print(f"Port {PORT} is OPEN.")
            return True
        else:
            print(f"Port {PORT} is CLOSED (Code: {result}). Backend not running?")
            return False
    finally:
        sock.close()

def test_upload():
    if not check_port():
        return

    # Metadata
    metadata = {
        "workflowId": "sequential_audit_chain",
        "inputs": {
            "history_text": "{{FILE: test_history.pdf}}",
            "product_text": "{{FILE: test_product.pdf}}",
            "reflection_text": "{{FILE: test_reflection.pdf}}"
        }
    }
    
    file_content = b"PDF_SIGNATURE_DUMMY"
    
    # Strict matching test
    files = [
        ('json_payload', (None, json.dumps(metadata), 'application/json')),
        ('history_text', ('test_history.pdf', file_content, 'application/pdf')),
        ('product_text', ('test_product.pdf', file_content, 'application/pdf')),
        ('reflection_text', ('test_reflection.pdf', file_content, 'application/pdf'))
    ]

    print(f"POST {API_URL} with Strict Keys and Auth...")
    try:
        resp = requests.post(API_URL, files=files, headers=HEADERS)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_upload()
