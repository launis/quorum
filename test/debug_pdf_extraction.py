
import sys
import os
import fitz  # PyMuPDF
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.chat_log_parser import ChatLogParser
from backend.services.document_service import DocumentService

TARGET_DIR = r"c:\src\quorum\data\files\1e205b2c-c907-45a1-a5e5-3fa4cc10952f"

def debug_extraction():
    print("================================================================")
    print("STARTING DEBUG EXTRACTION")
    print(f"Target Directory: {TARGET_DIR}")
    print("================================================================")

    if not os.path.exists(TARGET_DIR):
        print(f"ERROR: Directory not found: {TARGET_DIR}")
        return

    files = os.listdir(TARGET_DIR)
    print(f"Found {len(files)} files in directory.")

    for filename in files:
        filepath = os.path.join(TARGET_DIR, filename)
        print("\n----------------------------------------------------------------")
        print(f"PROCESSING FILE: {filename}")
        print(f"Full Path: {filepath}")
        
        try:
            size = os.path.getsize(filepath)
            print(f"File Size: {size} bytes")
            if size == 0:
                print("WARNING: File is 0 bytes! This explains emptiness.")
                continue

            print("Reading file bytes...")
            with open(filepath, "rb") as f:
                content = f.read()
            print(f"Read {len(content)} bytes successfully.")

            text_content = ""
            if filename.lower().endswith(".pdf"):
                print("Detected PDF format. Attempting extraction via DocumentService._extract_text_from_pdf...")
                try:
                    text_content = DocumentService._extract_text_from_pdf(content)
                    print("Extraction complete.")
                except Exception as e:
                    print(f"CRITICAL ERROR during PDF extraction: {e}")
                    import traceback
                    traceback.print_exc()
                    continue

            elif filename.lower().endswith(".txt") or filename.lower().endswith(".log"):
                 print("Detected Text format. Decoding utf-8...")
                 text_content = content.decode("utf-8", errors="replace")
            
            else:
                print(f"Skipping extraction for unknown type: {filename}")
                continue

            print(f"Extracted Text Length: {len(text_content)} characters")
            
            if len(text_content) == 0:
                print("CRITICAL WARNING: Extracted text is EMPTY!")
            else:
                print("Preview (First 500 chars):")
                print(text_content[:500])
                print("...")

            print("\n--- Testing ChatLogParser ---")
            print("Inputting text to ChatLogParser.parse()...")
            parsed_text = ChatLogParser.parse(text_content)
            print(f"Parsed Text Length: {len(parsed_text)} characters")
            
            if len(parsed_text) == 0 and len(text_content) > 0:
                 print("CRITICAL WARNING: ChatLogParser returned EMPTY string from non-empty input!")
            elif len(parsed_text) == len(text_content):
                 print("Result: No parsing changes detected (returned raw).")
            else:
                 print("Result: Parsing modified the text (formatting detected).")
                 print("Preview Parsed (First 500 chars):")
                 print(parsed_text[:500])

        except Exception as e:
            print(f"UNEXPECTED ERROR processing file {filename}: {e}")
            import traceback
            traceback.print_exc()

    print("\n================================================================")
    print("DEBUGGING COMPLETE")
    print("================================================================")

if __name__ == "__main__":
    debug_extraction()
