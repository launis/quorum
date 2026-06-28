import fitz
import pymupdf4llm
import ftfy
import os

pdf_path = r"c:\src\quorum\data\files\executions\exe_d32d71d71f204b2b99ef089d96f0f709\inputs\lopputuote sitra.pdf"
if not os.path.exists(pdf_path):
    # let's just find any pdf in inputs
    inputs_dir = r"c:\src\quorum\data\files\executions\exe_d32d71d71f204b2b99ef089d96f0f709\inputs"
    for f in os.listdir(inputs_dir):
        if f.endswith('.pdf'):
            pdf_path = os.path.join(inputs_dir, f)
            break

if not os.path.exists(pdf_path):
    print("No pdf found")
    exit(1)

doc = fitz.open(pdf_path)
md_text = str(pymupdf4llm.to_markdown(doc))
print("--- pymupdf4llm OUT ---")
print(md_text[:500])
print("--- ftfy OUT ---")
print(ftfy.fix_text(md_text)[:500])
