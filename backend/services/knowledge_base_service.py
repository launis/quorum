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
    
    
    def __init__(self, repository: AbstractWorkflowRepository, storage_client: Optional[Any] = None, document_service: Optional[Any] = None, llm_provider: Optional[Any] = None):
        self.repository = repository
        self.llm_provider = llm_provider
        
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

    
    async def ingest_from_bytes(
        self, 
        file_content: bytes, 
        filename: str, 
        tracker: Any, 
        job_id: Optional[str] = None,
        reset_db: bool = False
    ) -> Dict[str, Any]:
        """
        Ingests content from memory (bytes). Archives to storage first.
        Uses Unified ProgressTracker.
        """
        if not job_id:
            job_id = str(uuid.uuid4())
            
        logger.info(f"[KBService] Starting ingestion job {job_id} for {filename} (reset_db={reset_db})")
        
        # Unified Start
        tracker.start({"job_id": job_id, "filename": filename})
        tracker.update(stage="Archiving & Parsing", percent=5)
        
        # 0. optional Reset
        if reset_db:
             logger.warning(f"[KBService] Resetting Knowledge Base as requested.")
             try:
                 self.repository.clear_knowledge_base()
             except Exception as e:
                 logger.error(f"[KBService] Failed to reset KB: {e}")
                 
        tracker.update(stage="Archiving & Parsing", percent=10)
        
        try:
            # If LLM Provider is available, use Smart Ingestion
            if self.llm_provider:
                tracker.update(stage="Extracting Text", percent=15)
                
                # 1. Call standard parsing to get References (and Headers as fallback concepts).
                parsed_data = await self.document_service.process_knowledge_base_file(file_content, filename, job_id)
                
                tracker.update(stage="AI Analysis (Chunking)", percent=20)
                
                # 2. Extract Text from the file for LLM
                from backend.services.document_service import DocumentService
                text = ""
                if filename.lower().endswith(".docx"):
                     text = DocumentService._extract_text_from_docx(file_content)
                elif filename.lower().endswith(".md"):
                     text = file_content.decode("utf-8", errors="ignore")
                else:
                     text = file_content.decode("utf-8", errors="ignore")
                
                # 3. Process with LLM
                llm_concepts = await self.extract_concepts_with_llm(text, tracker)
                
                # 4. Merge
                existing_terms = {c['term'].lower() for c in parsed_data.get('concepts', [])}
                
                for c in llm_concepts:
                    if c['term'].lower() not in existing_terms:
                        parsed_data['concepts'].append(c)
                    else:
                        # Update definition?
                        pass
                        
            else:
                # Legacy / Fallback
                parsed_data = await self.document_service.process_knowledge_base_file(file_content, filename, job_id)

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

    async def extract_concepts_with_llm(self, text: str, tracker: Any = None) -> list:
        """
        Chunks text and uses LLM to extract concepts. Publicly accessible.
        """
        # 1. Chunking
        chunk_size = 8000
        overlap = 500
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
            
        total_chunks = len(chunks)
        extracted_concepts = []
        
        logger.info(f"[KBService] Processing {total_chunks} chunks with LLM.")
        
        import json
        
        for i, chunk in enumerate(chunks):
            current_pct = 20 + int((i / total_chunks) * 40) # 20% to 60%
            tracker.update(stage=f"AI Analysis (Chunk {i+1}/{total_chunks})", percent=current_pct)
            
            prompt = f"""
            You are an expert academic research assistant.
            Analyze the following text chunk. Extract theoretical concepts, models, or frameworks defined in the text.
            
            Return a JSON object with a key "concepts" which is a list of objects.
            Each object must have:
            - "term": The name of the concept (Capitalized).
            - "definition": A precise definition or explanation found in the text. Preferably include citations (Author Year) if present in the text.
            
            If no concepts are found, return {{"concepts": []}}.
            
            TEXT CHUNK:
            {chunk}
            """
            
            try:
                # We use the provider directly
                response = await self.llm_provider.generate(
                    prompt=prompt,
                    system_instruction="You are a strict JSON extraction engine. Output valid JSON only."
                )
                
                # Parse JSON
                cleaned = str(response).strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                     cleaned = cleaned.split("```")[1].split("```")[0].strip()
                     
                data = json.loads(cleaned)
                chunk_concepts = data.get("concepts", [])
                extracted_concepts.extend(chunk_concepts)
                
            except Exception as e:
                logger.error(f"[KBService] Error calling LLM for chunk {i}: {e}")
                continue
                
        # Deduplicate
        final_map = {}
        for c in extracted_concepts:
            term = c.get("term")
            defn = c.get("definition")
            if not term or not defn: continue
            
            if term not in final_map:
                final_map[term] = defn
            else:
                if len(defn) > len(final_map[term]):
                    final_map[term] = defn
                    
        return [{"term": t, "definition": d} for t, d in final_map.items()]

    def _store_parsed_data(self, parsed_data: Dict[str, Any], source_name: str, job_id: str, tracker: Any = None) -> Dict[str, Any]:
        concepts = parsed_data.get('concepts', [])
        refs = parsed_data.get('references', [])
        claims = parsed_data.get('claims', [])
        
        total_items = len(concepts) + len(refs) + len(claims)
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
                "ingested_at": datetime.now().isoformat(),
                "metadata": {}
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
                "term": r.get('short_citation') or (r['citation'][:50] + "..."),
                "definition": r['citation'], # Full citation as definition
                "doi_link": r.get('doi_link'),
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat(),
                "metadata": {
                    "short_citation": r.get('short_citation')
                }
            }
            self.repository.add_knowledge_base_item(item)
            count_refs += 1
            processed += 1
            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)

        count_claims = 0
        for cl in claims:
            # Claim structure: {claim_text, citation_keys, citation_text, original_markdown...}
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "claim",
                "term": cl['citation_text'][:50] + "...", # Use short citation as term or snippet?
                "definition": cl['claim_text'], # The claim itself is the "definition" or content
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat(),
                "metadata": {
                    "citation_keys": cl.get('citation_keys'),
                    "citation_text": cl.get('citation_text'),
                    "full_reference": cl.get('original_markdown'),
                    "concept_context": cl.get('concept_context')
                }
            }
            self.repository.add_knowledge_base_item(item)
            count_claims += 1
            processed += 1
            
            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)
        
        logger.info(f"[KBService] Ingestion complete. Concepts: {count_concepts}, Refs: {count_refs}, Claims: {count_claims}")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "concepts_count": count_concepts,
            "references_count": count_refs,
            "claims_count": count_claims
        }


