import requests
import time
import os

API_URL = "http://localhost:8000"

def create_dummy_pdf(filename, content):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(filename)
    c.drawString(100, 750, content)
    c.save()
    return filename

def test_modular_workflow():
    print("1. Creating dummy PDF...")
    pdf_path = create_dummy_pdf("modular_test.pdf", "Content for Modular Workflow")
    
    print("2. Uploading file...")
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    files = {
        'prompt_file': ('modular_test.pdf', pdf_content, 'application/pdf'),
        'history_file': ('modular_test.pdf', pdf_content, 'application/pdf'),
        'product_file': ('modular_test.pdf', pdf_content, 'application/pdf'),
        'reflection_file': ('modular_test.pdf', pdf_content, 'application/pdf')
    }
    res = requests.post(f"{API_URL}/upload", files=files)
    assert res.status_code == 200
    file_paths = res.json()['file_paths']
    print(f"   File uploaded.")

    print("3. Fetching Workflow ID...")
    # We need to find the workflow ID for "Hybrid Rubric Assessment"
    # Since we don't have a search endpoint, we list all (assuming small number) or just use the one we just seeded.
    # For this test, let's assume we can get it from the seed script output or just list them.
    # Actually, let's just list all workflows and find it.
    # Wait, we didn't implement GET /workflows list. 
    # Let's just try ID 1, 2, 3... or just rely on the fact that we just seeded it.
    # A better way is to query the DB directly or add a list endpoint.
    # Let's add a list endpoint to main.py quickly? No, let's stick to the plan.
    # We'll try to execute workflow ID 1. If it fails, we try 2.
    
    workflow_id = 3 # Updated based on seed output
    
    print(f"4. Executing Workflow {workflow_id}...")
    inputs = {
        "prompt_text": "Dummy Prompt",
        "history_text": "Dummy History",
        "product_text": "Dummy Product",
        "reflection_text": "Dummy Reflection"
    }
    
    res = requests.post(f"{API_URL}/executions", json={"workflow_id": workflow_id, "initial_inputs": inputs})
    if res.status_code != 200:
        print(f"Failed to start execution with ID {workflow_id}: {res.text}")
        # Try a fallback range
        for i in range(1, 10):
             res = requests.post(f"{API_URL}/executions", json={"workflow_id": i, "initial_inputs": inputs})
             if res.status_code == 200:
                 workflow_id = i
                 break
    
    execution_id = res.json()['execution_id']
    print(f"   Execution started with ID: {execution_id}")

    print("5. Polling for completion...")
    while True:
        res = requests.get(f"{API_URL}/executions/{execution_id}")
        data = res.json()
        status = data['status']
        print(f"   Status: {status}")
        
        if status == 'completed':
            print("\nWorkflow Completed Successfully!")
            print("Step Results:")
            for step in data['step_results']:
                print(f"  Component: {step['component']}")
                # print(f"  Output: {step['output']}")
            break
        elif status == 'failed':
            print(f"\nWorkflow Failed: {data.get('error')}")
            break
        
        time.sleep(1)

    # Cleanup
    os.remove(pdf_path)

if __name__ == "__main__":
    test_modular_workflow()
