
import sys, os
sys.path.insert(0, os.getcwd())
import json, fitz, pymupdf4llm
from backend_v2.services.ingress.pdf_chat_extractor import PdfChatExtractorService
from backend_v2.services.document_extraction import DocumentExtractionService

file_path = sys.argv[1]
doc = fitz.open(file_path)
try:
    if PdfChatExtractorService.is_conversation_pdf(doc):
        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        text = chat_dto.model_dump_json()
    else:
        text = pymupdf4llm.to_markdown(doc).strip()
    metadata = doc.metadata or {}
    pdf_date = metadata.get('modDate') or metadata.get('creationDate')
    parsed_date = DocumentExtractionService.parse_pdf_date(pdf_date) if pdf_date else None
finally:
    doc.close()

result = {'text': text, 'date': parsed_date}
with open(sys.argv[2], 'w', encoding='utf-8') as out_f:
    json.dump(result, out_f)
