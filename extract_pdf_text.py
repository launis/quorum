
import sys
import os

try:
    from pypdf import PdfReader
except ImportError:
    print("pypdf not installed. Attempting basic file read (binary inspection)...")
    PdfReader = None

def extract_text(pdf_path):
    if PdfReader:
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF with pypdf: {e}"
    else:
        # Fallback: very rough binary scan for keywords
        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()
                # Look for common markers
                markers = [b'Judge', b'Analysis', b'Conclusion', b'Evidence']
                found = []
                for m in markers:
                    if m in content:
                        found.append(m.decode('utf-8'))
                return f"Binary scan found keywords: {found}. (Install pypdf for full text)"
        except Exception as e:
             return f"Error reading file: {e}"

if __name__ == "__main__":
    path = r"c:\src\quorum\data\files\executions\73c5c6e0-7865-4ea6-83d6-5484baa10ca9\report.pdf"
    if os.path.exists(path):
        print(extract_text(path))
    else:
        print(f"File not found: {path}")
