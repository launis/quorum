import logging
import uuid
import os
from typing import Dict, Any, Optional
from datetime import datetime
from backend.services.knowledge_base_parser import KnowledgeBaseParser
from backend.database.repository import AbstractWorkflowRepository

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """
    Coordinator for ingesting Knowledge Base files into the database.
    Now uses Unified ProgressTracker.
    """
    
    
    def __init__(self, repository: AbstractWorkflowRepository, storage_client: Optional[Any] = None, document_service: Optional[Any] = None):
        self.repository = repository
        if storage_client:
            self.storage_client = storage_client
        else:
            from backend.services.storage import get_storage_client
            try:
                self.storage_client = get_storage_client()
            except:
                self.storage_client = None
        
        if document_service:
            self.document_service = document_service
        else:
            from backend.services.document_service import DocumentService
            self.document_service = DocumentService(self.storage_client)

    
    def ingest_from_bytes(
        self, 
        file_content: bytes, 
        filename: str, 
        tracker: Any, # Typed as ProgressTracker but avoid circular imports if needed
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingests content from memory (bytes). Archives to storage first.
        Uses Unified ProgressTracker.
        """
        if not job_id:
            job_id = str(uuid.uuid4())
            
        logger.info(f"[KBService] Starting ingestion job {job_id} for {filename}")
        
        # Unified Start
        tracker.start({"job_id": job_id, "filename": filename})
        tracker.update(stage="Archiving & Parsing", percent=10)
        
        try:
            # 1. Delegate to DocumentService (Async method, but we are in Sync context here?)
            # Wait, `ingest_from_bytes` is Sync in the current definition, but DocumentService methods are Async.
            # We need to run it synchronously or change this method to async.
            # admin_router calls this synchronously inside a threadpool (_run_ingest).
            # So we can use asyncio.run or loop.run_until_complete? 
            # OR we make DocumentService synchronous? NO, run_in_threadpool is async friendly.
            # Actually, `run_in_threadpool` is for calling sync from async.
            # If we are in a background task thread, we can use asyncio.run()
            
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # If we are already in a loop?
            # Background tasks in FastAPI run in a threadpool (sync).
            
            parsed_data = asyncio.run(self.document_service.process_knowledge_base_file(file_content, filename, job_id))

            tracker.update(stage="Storing to DB", percent=60)
            
            # 3. Import to DB
            result = self._store_parsed_data(parsed_data, source_name=filename, job_id=job_id, tracker=tracker)
            
            # Unified Success
            tracker.complete(result)
            return result
            
        except Exception as e:
            logger.error(f"[KBService] Ingestion failed: {e}")
            tracker.fail(str(e))
            raise e

    def _store_parsed_data(self, parsed_data: Dict[str, Any], source_name: str, job_id: str, tracker: Any = None) -> Dict[str, Any]:
        concepts = parsed_data['concepts']
        refs = parsed_data['references']
        total_items = len(concepts) + len(refs)
        processed = 0
        
        count_concepts = 0
        for c in concepts:
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "concept",
                "term": c['term'],
                "definition": c['definition'],
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat()
            }
            self.repository.add_knowledge_base_item(item)
            count_concepts += 1
            processed += 1
            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)
            
        count_refs = 0
        for r in refs:
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "reference",
                "term": r['citation'][:50] + "...",
                "definition": r['citation'], # Full citation as definition
                "doi_link": r['doi_link'],
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat()
            }
            self.repository.add_knowledge_base_item(item)
            count_refs += 1
            processed += 1
            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)
        
        logger.info(f"[KBService] Ingestion complete. Concepts: {count_concepts}, Refs: {count_refs}")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "concepts_count": count_concepts,
            "references_count": count_refs
        }
