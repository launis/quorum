
import asyncio
import os
import sys

# Add backend to path
sys.path.append("c:/src/quorum")

from backend.services.document_service import DocumentService
from backend.services.chat_log_parser import ChatLogParser

async def test_extraction():
    file_path = "c:/src/quorum/backend/files/executions/0a52b142-7773-4c11-9775-eb3606dd6b43/keskusteluhistoria SITRA.pdf"
    
    print(f"Testing file: {file_path}")
    if not os.path.exists(file_path):
        print("ERROR: File not found!")
        return

    try:
        # 1. Read Bytes
        with open(file_path, "rb") as f:
            content = f.read()
        print(f"File size: {len(content)} bytes")

        # 2. Extract Text
        print("Extracting text...")
        text = DocumentService._extract_text_from_pdf(content)
        print(f"Extracted text length: {len(text)}")
        print(f"FIRST 500 CHARS:\n{text[:500]}\n")
        print("-" * 50)

        # 3. Parse Chat Log
        print("Parsing chat log...")
        parsed = ChatLogParser.parse(text)
        print(f"Parsed text length: {len(parsed)}")
        print(f"PARSED SAMPLE:\n{parsed[:500]}\n")

    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    with open("reproduce_out.txt", "w", encoding="utf-8") as out:
        sys.stdout = out
        asyncio.run(test_extraction())

