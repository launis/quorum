import requests
import time
import os
from fpdf import FPDF

API_URL = "http://localhost:8000"

def create_dummy_pdf(filename, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=content, ln=1, align="C")
    pdf.output(filename)
    return filename

def test_generic_workflow():
    print("1. Creating dummy PDF...")
    pdf_path = create_dummy_pdf("workflow_test.pdf", "Content for Workflow Engine")
    
    print("2. Uploading file...")
    # Read file content into memory to avoid keeping handles open
    with open(pdf_path, "rb") as f:
        pdf_content = f.read()

    files = {
        'prompt_file': ('workflow_test.pdf', pdf_content, 'application/pdf'),
        'history_file': ('workflow_test.pdf', pdf_content, 'application/pdf'),
        'product_file': ('workflow_test.pdf', pdf_content, 'application/pdf'),
        'reflection_file': ('workflow_test.pdf', pdf_content, 'application/pdf')
    }
    res = requests.post(f"{API_URL}/upload", files=files)
    assert res.status_code == 200
    file_paths = res.json()['file_paths']
    uploaded_path = file_paths['prompt_path']
    print(f"   File uploaded to: {uploaded_path}")

    print("3. Creating Workflow Definition...")
    workflow_def = {
        "name": "PDF Extraction Workflow",
        "steps": [
            {
                "component": "PDFExtractor",
                "inputs": {
                    "file_path": "$input_file"
                }
            }
        ]
    }
    res = requests.post(f"{API_URL}/workflows", json=workflow_def)
    assert res.status_code == 200
    workflow_id = res.json()['workflow_id']
    print(f"   Workflow created with ID: {workflow_id}")

    print("4. Executing Workflow...")
    exec_req = {
        "workflow_id": workflow_id,
        "inputs": {
            "input_file": uploaded_path
        }
    }
    res = requests.post(f"{API_URL}/executions", json=exec_req)
    assert res.status_code == 200
    execution_id = res.json()['execution_id']
    print(f"   Execution started with ID: {execution_id}")

    print("5. Polling for completion...")
    for _ in range(10):
        res = requests.get(f"{API_URL}/executions/{execution_id}")
        status = res.json()
        print(f"   Status: {status['status']}")
        if status['status'] in ['completed', 'failed']:
            break
        time.sleep(1)
    
    if status['status'] == 'completed':
        print("\nWorkflow Completed Successfully!")
        results = status['step_results']
        print("Step Results:")
        for step in results:
            print(f"  Component: {step['component']}")
            print(f"  Output: {step['output']}")
            if "Content for Workflow Engine" in str(step['output']):
                print("  VERIFICATION PASSED: Extracted text matches.")
            else:
                print("  VERIFICATION FAILED: Text mismatch.")
    else:
        print(f"\nWorkflow Failed: {status.get('error')}")

    # Cleanup
    if os.path.exists("workflow_test.pdf"):
        os.remove("workflow_test.pdf")

if __name__ == "__main__":
    test_generic_workflow()
