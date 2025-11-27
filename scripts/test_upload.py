import requests
from fpdf import FPDF
import os

API_URL = "http://localhost:8000"

def create_dummy_pdf(filename, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=content, ln=1, align="C")
    pdf.output(filename)
    return filename

def test_upload():
    print("Creating dummy PDFs...")
    files_to_create = {
        "prompt.pdf": "This is the PROMPT content.",
        "history.pdf": "This is the HISTORY content.",
        "product.pdf": "This is the PRODUCT content.",
        "reflection.pdf": "This is the REFLECTION content."
    }
    
    files = {}
    for fname, content in files_to_create.items():
        create_dummy_pdf(fname, content)
        files[fname] = open(fname, "rb")

    upload_files = [
        ('prompt_file', ('prompt.pdf', files['prompt.pdf'], 'application/pdf')),
        ('history_file', ('history.pdf', files['history.pdf'], 'application/pdf')),
        ('product_file', ('product.pdf', files['product.pdf'], 'application/pdf')),
        ('reflection_file', ('reflection.pdf', files['reflection.pdf'], 'application/pdf'))
    ]

    print("Uploading files...")
    try:
        response = requests.post(f"{API_URL}/upload", files=upload_files)
        
        if response.status_code == 200:
            data = response.json()
            print("\nUpload Successful!")
            print(f"Status: {data['status']}")
            print("Extracted Data:")
            print(f"  Prompt: {data['data']['prompt_text']}")
            print(f"  History: {data['data']['history_text']}")
            print(f"  Product: {data['data']['product_text']}")
            print(f"  Reflection: {data['data']['reflection_text']}")
            
            # Verify content matches
            assert "PROMPT" in data['data']['prompt_text']
            assert "HISTORY" in data['data']['history_text']
            assert "PRODUCT" in data['data']['product_text']
            assert "REFLECTION" in data['data']['reflection_text']
            print("\nVerification PASSED: Extracted text matches expected content.")
        else:
            print(f"\nUpload Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        for f in files.values():
            f.close()
        for fname in files_to_create.keys():
            if os.path.exists(fname):
                os.remove(fname)

if __name__ == "__main__":
    test_upload()
