"""Service for managing Knowledge Base ingestion and retrieval."""

import logging
import uuid
from datetime import datetime
from typing import Any

from backend.database.repository import AbstractWorkflowRepository
from backend.schemas.knowledge import IngestionSummary

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Coordinator for ingesting Knowledge Base files into the database.

    Integrates Parsing, Storage, and Database Persistence layers.
    Operates asynchronously and reports status via unified ProgressTracker.
    """

    def __init__(
        self,
        repository: AbstractWorkflowRepository,
        storage_client: Any | None = None,
        document_service: Any | None = None,
        llm_provider: Any | None = None,
    ):
        """Initializes the service.

        Args:
            repository (AbstractWorkflowRepository): Database access.
            storage_client (Optional[Any]): File storage. Defaults to global factory.
            document_service (Optional[Any]): For parsing/extraction. Defaults to auto-init.
            llm_provider (Optional[Any]): For AI enrichment (optional).

        """
        self.repository = repository
        self.llm_provider = llm_provider

        if storage_client:
            self.storage_client = storage_client
        else:
            from backend.services.storage import get_storage_client

            try:
                self.storage_client = get_storage_client()
            except Exception:
                self.storage_client = None

        if document_service:
            self.document_service = document_service
        else:
            from backend.services.document_service import DocumentService

            self.document_service = DocumentService(self.storage_client)

    async def ingest_from_bytes(
        self, file_content: bytes, filename: str, tracker: Any, job_id: str | None = None, reset_db: bool = False
    ) -> IngestionSummary:
        """Ingests content from memory (bytes). Archives to storage, parses structure, and persists to DB.

        Workflow:
        1. Archive to Storage.
        2. Parse (DOCX/MD) to extract Concepts, References, Claims.
        3. (Optional) Enrich with LLM if provider configured.
        4. Store extracted items in Database.

        Args:
            file_content (bytes): Raw file data.
            filename (str): Original filename.
            tracker (Any): ProgressTracker instance for status updates.
            job_id (Optional[str]): Unique ingest job UUID.
            reset_db (bool): If True, clears existing KB before ingestion.

        Returns:
            IngestionSummary: Summary stats (counts of concepts, refs, claims).

        Raises:
            Exception: On ingestion failure.

        """
        if not job_id:
            job_id = str(uuid.uuid4())

        logger.info(f"[KBService] Starting ingestion job {job_id} for {filename} (reset_db={reset_db})")

        # Unified Start
        tracker.start({"job_id": job_id, "filename": filename})
        tracker.update(stage="Archiving & Parsing", percent=5)

        # 0. optional Reset
        if reset_db:
            logger.warning("[KBService] Resetting Knowledge Base as requested.")
            try:
                await self.repository.clear_knowledge_base()
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
                existing_terms = {c["term"].lower() for c in parsed_data.get("concepts", [])}

                for c in llm_concepts:
                    if c["term"].lower() not in existing_terms:
                        parsed_data["concepts"].append(c)
                    else:
                        # Update definition?
                        pass

            else:
                # Legacy / Fallback
                parsed_data = await self.document_service.process_knowledge_base_file(file_content, filename, job_id)

            tracker.update(stage="Storing to DB", percent=60)

            # 3. Import to DB
            result = await self._store_parsed_data(parsed_data, source_name=filename, job_id=job_id, tracker=tracker)

            # Unified Success
            tracker.complete(result.model_dump())
            return result

        except Exception as e:
            logger.error(f"[KBService] Ingestion failed: {e}")
            tracker.fail(str(e))
            raise e from e

    async def extract_concepts_with_llm(self, text: str, tracker: Any = None) -> list[dict[str, str]]:
        """Chunks text and uses configured LLM to extract theoretical concepts.

        Publicly accessible for ad-hoc extraction.

        Args:
            text (str): Input text content.
            tracker (Any, optional): ProgressTracker for status updates.

        Returns:
            List[Dict[str, str]]: List of {'term': ..., 'definition': ...}.

        """
        if not self.llm_provider:
            logger.warning("[KBService] No LLM Provider configured. Skipping extraction.")
            return []

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
            current_pct = 20 + int((i / total_chunks) * 40)  # 20% to 60%
            tracker.update(stage=f"AI Analysis (Chunk {i + 1}/{total_chunks})", percent=current_pct)

            # New Pattern: Structured Output via Schema
            from backend.schemas.knowledge import ConceptResponse

            prompt = f"""
            You are an expert academic research assistant.
            Analyze the following text chunk. Extract theoretical concepts, models, or frameworks defined in the text.
            
            TEXT CHUNK:
            {chunk}
            """

            try:
                # We use the provider directly with Pydantic Schema
                response = await self.llm_provider.generate(
                    prompt=prompt, 
                    system_instruction="Extract concepts strictly conforming to the schema.",
                    response_schema=ConceptResponse
                )

                # LiteLLMProvider guarantees valid JSON in content when response_schema is used
                import json
                data = json.loads(response.content)
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
            if not term or not defn:
                continue

            if term not in final_map:
                final_map[term] = defn
            else:
                if len(defn) > len(final_map[term]):
                    final_map[term] = defn

        return [{"term": t, "definition": d} for t, d in final_map.items()]

    async def _store_parsed_data(
        self, parsed_data: dict[str, Any], source_name: str, job_id: str, tracker: Any = None
    ) -> IngestionSummary:
        """Internal: Converts parsed data structures into Database Records and inserts them.

        Args:
            parsed_data (dict): Structure from parser.
            source_name (str): Origin filename.
            job_id (str): Ingestion Job ID.
            tracker (Optional[Any]): Progress tracker.

        Returns:
            dict[str, Any]: Final result summary.
        """
        concepts = parsed_data.get("concepts", [])
        refs = parsed_data.get("references", [])
        claims = parsed_data.get("claims", [])

        total_items = len(concepts) + len(refs) + len(claims)
        processed = 0

        count_concepts = 0
        for c in concepts:
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "concept",
                "term": c["term"],
                "definition": c["definition"],
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat(),
                "metadata": {},
            }
            await self.repository.add_knowledge_base_item(item)
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
                "term": r.get("short_citation") or (r["citation"][:50] + "..."),
                "definition": r["citation"],  # Full citation as definition
                "doi_link": r.get("doi_link"),
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat(),
                "metadata": {"short_citation": r.get("short_citation")},
            }
            await self.repository.add_knowledge_base_item(item)
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
                "term": cl["citation_text"][:50] + "...",  # Use short citation as term or snippet?
                "definition": cl["claim_text"],  # The claim itself is the "definition" or content
                "source_file": source_name,
                "ingested_at": datetime.now().isoformat(),
                "metadata": {
                    "citation_keys": cl.get("citation_keys"),
                    "citation_text": cl.get("citation_text"),
                    "full_reference": cl.get("original_markdown"),
                    "concept_context": cl.get("concept_context"),
                },
            }
            await self.repository.add_knowledge_base_item(item)
            count_claims += 1
            processed += 1

            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)

        logger.info(
            f"[KBService] Ingestion complete. Concepts: {count_concepts}, Refs: {count_refs}, Claims: {count_claims}"
        )

        return IngestionSummary(
            job_id=job_id,
            status="completed",
            concepts_count=count_concepts,
            references_count=count_refs,
            claims_count=count_claims,
            filename=source_name
        )

    async def retrieve_context(self, query: str) -> str:
        """Retrieves context for a query.

        Args:
            query (str): Search query.

        Returns:
            str: Retrieved context (mocked for now).
        """
        # Placeholder implementation
        return f"Context for {query}"
