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
    
    
    def __init__(self, repository: AbstractWorkflowRepository, storage_client: Optional[Any] = None):
        self.repository = repository
        if storage_client:
            self.storage_client = storage_client
        else:
            from backend.services.storage import get_storage_client
            try:
                self.storage_client = get_storage_client()
            except:
                self.storage_client = None

    
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
        tracker.update(stage="Archiving", percent=10)
        
        try:
            # 1. Save to Storage (Archive)
            saved_path = filename
            if self.storage_client:
                # Path structure: knowledge_base/{job_id}/{filename}
                relative_path = f"knowledge_base/{job_id}/{filename}"
                saved_path = self.storage_client.save(relative_path, file_content)
                logger.info(f"[KBService] Archived to storage: {saved_path}")

            tracker.update(stage="Parsing", percent=30)

            # 2. Parse (using bytes stream)
            import io
            file_stream = io.BytesIO(file_content)
            parsed_data = KnowledgeBaseParser.parse_docx(file_stream)
            
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
