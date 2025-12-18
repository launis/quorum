from typing import Dict, Tuple, Any, Optional
import logging
import io
from fastapi.concurrency import run_in_threadpool
from backend.services.document_processor import DocumentProcessor
from backend.services.knowledge_base_parser import KnowledgeBaseParser
from backend.exceptions import FatalInterruption
from backend.services.storage import AbstractStorage

logger = logging.getLogger(__name__)

class DocumentService:
    """
    Unified service for handling document ingestion, processing, and archiving.
    Supports:
    - Evidence files (PDF/DOCX -> Text) for WorkflowEngine
    - Knowledge Base files (DOCX -> Structured JSON) for KnowledgeBaseService
    """
    def __init__(self, storage_client: AbstractStorage):
        self.storage_client = storage_client

    async def process_evidence_files(self, execution_id: str, files: Dict[str, Tuple[str, bytes]]) -> Dict[str, str]:
        """
        Archives files to storage and extracts text for workflow execution.
        Returns dictionary of {input_key: extracted_text}
        files format: { "input_key": ("filename.ext", b"file_bytes") }
        """
        extracted_data = {}
        
        for input_key, (filename, file_bytes) in files.items():
            try:
                # 1. Archive to Storage (IO-bound)
                relative_path = f"{execution_id}/{filename}"
                saved_path = await run_in_threadpool(self.storage_client.save, relative_path, file_bytes)
                
                # 2. Extract Text (CPU-bound)
                lower_name = filename.lower()
                text = ""
                
                if lower_name.endswith(".pdf"):
                    try:
                        text = await run_in_threadpool(DocumentProcessor.extract_text_from_pdf, file_bytes)
                    except Exception as e:
                         logger.error(f"PDF extraction failed for {filename}: {e}")
                         raise FatalInterruption("DocumentService", f"PDF extraction failed for {filename}: {e}", {"filename": filename})

                elif lower_name.endswith(".docx"):
                    try:
                        text = await run_in_threadpool(DocumentProcessor.extract_text_from_docx, file_bytes)
                    except Exception as e:
                         logger.error(f"DOCX extraction failed for {filename}: {e}")
                         raise FatalInterruption("DocumentService", f"DOCX extraction failed for {filename}: {e}", {"filename": filename})
                else:
                    # Treat as text file
                    text = file_bytes.decode('utf-8', errors='ignore')

                extracted_data[input_key] = text
                
                logger.info(f"[DocumentService] Evidence {filename} processed. Extracted {len(text)} chars. Storage: {saved_path}")
                
            except FatalInterruption as fi:
                 raise fi
            except Exception as e:
                logger.error(f"[DocumentService] Failed to ingest evidence {filename} ({input_key}): {e}")
                raise FatalInterruption(
                    step_name="DocumentService",
                    reason=f"Failed to ingest evidence {filename}: {str(e)}",
                    details={"filename": filename, "error": str(e)}
                )
                
        return extracted_data

    async def process_knowledge_base_file(self, content: bytes, filename: str, job_id: str) -> Dict[str, Any]:
        """
        Archives KB file and parses it into concepts/references.
        Returns structured data (JSON-compatible dict).
        """
        if not filename.lower().endswith(".docx"):
             raise ValueError("Knowledge Base must be a DOCX file.")

        try:
            # 1. Archive
            relative_path = f"knowledge_base/{job_id}/{filename}"
            saved_path = await run_in_threadpool(self.storage_client.save, relative_path, content)
            
            # 2. Parse (CPU-bound)
            # Wrap bytes in stream for parser
            file_stream = io.BytesIO(content)
            
            parsed_data = await run_in_threadpool(KnowledgeBaseParser.parse_docx, file_stream)
            
            logger.info(f"[DocumentService] KB {filename} processed. Found {len(parsed_data.get('concepts', []))} concepts.")
            return parsed_data
            
        except Exception as e:
            logger.error(f"[DocumentService] KB processing failed for {filename}: {e}")
            raise e
