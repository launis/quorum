import requests
import json

def run():
    url = "http://127.0.0.1:8000/api/v2/execution/executions"
    payload = {
        "workflow_id": "wf_d653170e174847559e08af42b938d826",
        "target_locale": "fi",
        "raw_inputs": {
            "inputs": {
                "document": "Testidataa arviointia varten. Analysoi tämä vakavasti ja syvällisesti ja anna pisteet systemaattisesti."
            }
        }
    }
    
    print("Sending POST request to:", url)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer mock-token:usr_43ec77a438104814bd937f28853d569c"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print("Execution created successfully!")
            print(f"Execution ID: {data.get('id')}")
        else:
            print("Failed Response:", response.text)
    except Exception as e:
        print("Error sending request:", e)

if __name__ == "__main__":
    run()
