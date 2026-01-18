
import requests

URL = "http://localhost:8000/tools/extract-text"
FILE_PATH = "docs/Holistinen Mestaruus.docx"

import os

def extract():
    print(f"Extracting {FILE_PATH} via {URL}...")
    try:
        with open(FILE_PATH, "rb") as f:
            files = {'file': (os.path.basename(FILE_PATH), f)}
            response = requests.post(URL, files=files)
        
        if response.status_code == 200:
            data = response.json()
            text = data.get("text", "")
            print("--- EXTRACTION SUCCESSFUL ---")
            print(text[:2000])  # Print first 2000 chars for inspection
            
            # Save to file for easy reading
            with open("temp_holistic_mastery.txt", "w", encoding="utf-8") as out:
                out.write(text)
            print("\nSaved full text to temp_holistic_mastery.txt")
            
        else:
            print(f"FAIL: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    extract()
