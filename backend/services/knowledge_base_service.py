"""Service for managing Knowledge Base ingestion and retrieval."""

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi.concurrency import run_in_threadpool

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import (
    AgentExecutionError,
    AppException,
    ErrorCodes,
    ServiceUnavailableError,
    status,
)
from backend.llm.provider import LLMFactory
from backend.models.domain.retrieval import KnowledgeItem
from backend.schemas.knowledge import ConceptResponse, IngestionSummary
from backend.services.document_service import DocumentService
from backend.services.parsers.bibliography_parser import BibliographyParser
from backend.services.storage import get_storage_driver

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Coordinate the ingestion of Knowledge Base files into the database.

    Integrates Parsing, Storage, and Database Persistence layers.
    Operates asynchronously and reports status via unified ProgressTracker.
    """

    CHUNK_SIZE = 8000
    OVERLAP = 500

    def __init__(
        self,
        repository: AbstractWorkflowRepository,
        storage_client: Any | None = None,
        document_service: Any | None = None,
        registry: Any | None = None,
        usage_service: Any | None = None,
    ):
        """Initializes the service.

        Args:
            repository (AbstractWorkflowRepository): Database access.
            storage_client (Optional[Any]): File storage. Defaults to global factory.
            document_service (Optional[Any]): For parsing/extraction. Defaults to auto-init.
            registry (Optional[Any]): AgentRegistry for resolving model strategies dynamically.
            usage_service (Optional[Any]): UsageService for tracking token usage.

        """
        self.repository = repository
        self.registry = registry
        self.usage_service = usage_service

        # Log capability status
        if self.registry and self.usage_service:
            logger.info("[KBService] Smart Ingestion Capability Enabled (Dynamic Resolution).")
        else:
            logger.warning("[KBService] Smart Ingestion Capability Disabled (Missing Registry/Usage).")

        if storage_client:
            self.storage_client = storage_client
        else:
            self.storage_client = get_storage_driver()

        if document_service:
            self.document_service = document_service
        else:
            self.document_service = DocumentService(self.storage_client)

    async def ingest_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        tracker: Any,
        job_id: str | None = None,
        reset_db: bool = False,
        language: str = "auto",
        model_strategy: str | None = None,
    ) -> IngestionSummary:
        """Ingest content from memory (bytes), archive to storage, parse structure, and persist to DB.

        Args:
            file_content (bytes): Raw file data.
            filename (str): Original filename.
            tracker (Any): ProgressTracker instance for status updates.
            job_id (Optional[str]): Unique ingest job UUID.
            reset_db (bool): If True, clears existing KB before ingestion.
            language (str): Language code (e.g. 'en', 'fi', 'auto').
            model_strategy (str): Strategy to use for LLM extraction (e.g. 'fast', 'deep', 'custom').

        Returns:
            IngestionSummary: Summary stats (counts of concepts, refs, claims).

        Raises:
            AppException: On ingestion failure (Fail Fast).

        """
        # FAIL FAST: Empty Input
        if not file_content:
            raise AppException(
                message="File content is empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT},
            )

        if not job_id:
            job_id = str(uuid.uuid4())

        logger.info(
            f"[KBService] Starting ingestion job {job_id} for {filename} (reset_db={reset_db}, lang={language}, strategy={model_strategy})"
        )

        # Unified Start
        tracker.start({"job_id": job_id, "filename": filename, "language": language})
        tracker.update(stage="Archiving & Parsing", percent=5)

        # 0. optional Reset
        if reset_db:
            logger.warning("[KBService] Resetting Knowledge Base as requested.")
            try:
                await self.repository.clear_knowledge_base()
            except Exception as e:
                logger.error(f"[KBService] {ErrorCodes.KNOWLEDGE_RESET_FAILED.value}: Failed to reset KB: {e}")

        tracker.update(stage="Archiving & Parsing", percent=10)

        try:
            # If Strategy provided and Registry available, use Smart Ingestion
            if model_strategy and self.registry:
                tracker.update(stage="Extracting Text", percent=15)

                # 1. Call standard parsing to get References (and Headers as fallback concepts).
                parsed_data = await self.document_service.process_knowledge_base_file(file_content, filename, job_id)

                tracker.update(stage="AI Analysis (Chunking)", percent=20)

                # Extract Text from the file for LLM
                text = ""
                if filename.lower().endswith(".docx"):
                    # [Atomic Strike 37] Offload CPU-bound parsing
                    text = await run_in_threadpool(DocumentService._extract_text_from_docx, file_content)
                elif filename.lower().endswith(".md"):
                    text = file_content.decode("utf-8", errors="ignore")
                else:
                    text = file_content.decode("utf-8", errors="ignore")

                # [Atomic Strike 35] Bibliography Parsing
                bib_parser = BibliographyParser()
                # [Atomic Strike 37] Offload CPU-bound regex parsing
                ref_map = await run_in_threadpool(bib_parser.parse_references, text)

                if ref_map:
                    logger.info(f"[KBService] Found {len(ref_map)} references in bibliography.")

                llm_concepts = await self.extract_concepts_with_llm(
                    text, tracker, model_strategy, ref_map=ref_map, language=language
                )

                # Merge Strict Pydantic Models without mutating frozen arrays
                existing_terms = {c.term.lower() for c in parsed_data.concepts}
                from backend.models.domain.knowledge import Concept
                
                new_concepts = list(parsed_data.concepts)
                for c in llm_concepts:
                    if c["term"].lower() not in existing_terms:
                        term = c.get("term", "").strip()
                        defn = c.get("definition", "").strip()
                        if term and defn:
                            new_concepts.append(Concept(term=term, definition=defn))

                # Reconstruct strictly
                parsed_data = parsed_data.model_copy(update={"concepts": new_concepts})

            else:
                # FAIL FAST: If Strategy requested but Registry missing, raise Error.
                if model_strategy and not self.registry:
                    error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
                    logger.error(f"[KBService] {error_code.value}: Model Strategy requested but Registry unavailable.")
                    raise AppException(
                        message="Model Strategy requested but AgentRegistry is unavailable.",
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        details={"error_code": error_code},
                    )

                # Basic Parsing (No Strategy Requested)
                parsed_data = await self.document_service.process_knowledge_base_file(file_content, filename, job_id)

            tracker.update(stage="Storing to DB", percent=60)

            # 3. Import to DB
            result = await self._store_parsed_data(
                parsed_data,
                source_name=filename,
                job_id=job_id,
                tracker=tracker,
                language=language,
                file_size=len(file_content),
            )

            # Unified Success
            tracker.complete(result.model_dump())
            return result

        except Exception as e:
            error_code = ErrorCodes.KNOWLEDGE_INGESTION_FAILED
            logger.error(f"[KBService] {error_code.value}: Ingestion failed: {e}", exc_info=True)

            # Wrap in structured exception for Tracker/Route
            app_error = AppException(
                message=f"Ingestion failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code, "original_error": str(e)},
            )
            tracker.fail(app_error)
            raise app_error from e

    async def extract_concepts_with_llm(
        self,
        text: str,
        tracker: Any = None,
        strategy: str = "fast",
        ref_map: dict[str, str] | None = None,
        language: str = "auto",
    ) -> list[dict[str, str]]:
        """Chunk text and use configured LLM to extract theoretical concepts.

        Publicly accessible for ad-hoc extraction.

        Args:
            text (str): Input text content.
            tracker (Any, optional): ProgressTracker for status updates.
            strategy (str): Strategy name to resolve model (e.g. 'fast', 'deep').
            ref_map (dict[str, str], optional): Map of citation keys to full text.
            language (str): Content language description (e.g. 'fi', 'en').

        Returns:
            List[Dict[str, str]]: List of {'term': ..., 'definition': ...}.

        """
        # FAIL FAST
        if not text:
            logger.warning("[KBService] Empty text provided for extraction.")
            return []

        if not self.registry or not self.usage_service:
            if strategy:
                error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
                logger.error(
                    f"[KBService] {error_code.value}: Registry or UsageService unavailable for prompt-based extraction."
                )
                raise AppException(
                    message="Registry or UsageService unavailable for prompt-based extraction.",
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    details={"error_code": error_code},
                )
            logger.warning(
                "[KBService] Registry or UsageService missing. Skipping LLM extraction (No strategy requested)."
            )
            return []

        try:
            # Dynamic Resolution
            logger.info(f"[KBService] Resolving model for strategy: {strategy}")
            config = await self.registry.resolve_model_config(strategy)

            # Create transient provider for this job
            llm_provider = LLMFactory.create_provider(
                provider_type=config.provider, model_name=config.model_name, usage_service=self.usage_service
            )
            logger.info(f"[KBService] Using Model: {getattr(llm_provider, 'model_name', 'Unknown')}")

        except Exception as e:
            error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
            logger.error(
                f"[KBService] {error_code.value}: Failed to resolve/create provider for strategy '{strategy}': {e}",
                exc_info=True,
            )
            raise ServiceUnavailableError(
                message=f"Failed to resolve model strategy '{strategy}': {e}",
                details={"error_code": error_code, "original_error": str(e)},
            ) from e

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunks.append(text[start:end])
            start = end - self.OVERLAP

        total_chunks = len(chunks)
        extracted_concepts = []

        logger.info(f"[KBService] Processing {total_chunks} chunks with LLM.")

        for i, chunk in enumerate(chunks):
            # [Atomic Strike 37] Yield control to event loop to prevent blocking heartbeat/status checks
            if i % 5 == 0:
                await asyncio.sleep(0)

            current_pct = 20 + int((i / total_chunks) * 40)  # 20% to 60%
            tracker.update(stage=f"AI Analysis (Chunk {i + 1}/{total_chunks})", percent=current_pct)

            # [Atomic Strike 35] Inject References
            resolved_refs = []
            if ref_map:
                # Find [1], [12] in chunk
                citations = re.findall(r"\[(\d+)\]", chunk)
                for key in citations:
                    if key in ref_map:
                        resolved_refs.append(f"[{key}] {ref_map[key]}")

            ref_context = ""
            if resolved_refs:
                # Deduplicate and format
                unique_refs = sorted(list(set(resolved_refs)))
                ref_context = "\n\nREFERENCES IN THIS CHUNK:\n" + "\n".join(unique_refs)

            prompt = f"""
            You are an expert academic research assistant.
            Analyze the following text chunk (Language: {language}). Extract theoretical concepts, models, or frameworks defined in the text.

            STRICT GROUNDING RULES:
            1. EXTRACT ONLY concepts explicitly defined in the provided TEXT CHUNK.
            2. DO NOT invent, hallucinate, or infer concepts not present in the text.
            3. If a concept is mentioned but not defined, SKIP IT.
            4. If the text cites references (e.g. [1]), use the provided REFERENCE LIST only for context, not to invent new claims.
            5. If no concepts are found, return an empty list.
            6. Provide definitions in the SAME LANGUAGE as the text ({language}).

            TEXT CHUNK:
            {chunk}
            {ref_context}
            """

            try:
                # We use the provider directly with Pydantic Schema
                response = await llm_provider.generate(
                    prompt=prompt,
                    system_instruction="Extract concepts strictly conforming to the schema.",
                    response_schema=ConceptResponse,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    top_p=config.top_p,
                )

                # LiteLLMProvider guarantees valid JSON in content when response_schema is used
                data = json.loads(response.content)
                chunk_concepts = data.get("concepts", [])
                extracted_concepts.extend(chunk_concepts)

            except Exception as e:
                # [Fail Fast] Do not swallow errors. If 1 chunk fails, the integrity of the extraction is compromised.
                logger.error(f"[KBService] Error calling LLM for chunk {i}: {e}", exc_info=True)
                raise AgentExecutionError(
                    detail=ErrorCodes.MODEL_OUTPUT_LIMIT_EXCEEDED.value
                    if "limit" in str(e).lower()
                    else ErrorCodes.AGENT_EXECUTION_CRITICAL.value,
                    original_error=e,
                    agent_name="KnowledgeExtractor",
                    step_id=f"chunk-{i}",
                ) from e

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
        self,
        parsed_data: Any,  # Actually KnowledgeBaseDocument
        source_name: str,
        job_id: str,
        tracker: Any = None,
        language: str = "auto",
        file_size: int = 0,
    ) -> IngestionSummary:
        """Convert parsed data structures into Database records and insert them.

        Args:
            parsed_data (KnowledgeBaseDocument): Structure from parser.
            source_name (str): Origin filename.
            job_id (str): Ingestion Job ID.
            tracker (Optional[Any]): Progress tracker.
            language (str): Language code.

        Returns:
            dict[str, Any]: Final result summary.
        """
        # parsed_data is a Pydantic Model (KnowledgeBaseDocument)
        concepts = parsed_data.concepts
        refs = parsed_data.references
        claims = parsed_data.claims

        total_items = len(concepts) + len(refs) + len(claims)
        processed = 0

        count_concepts = 0
        for c in concepts:
            # c is Concept Pydantic model
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "concept",
                "term": c.term,
                "definition": c.definition,
                "source_file": source_name,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {"language": language},
            }
            await self.repository.add_concept(item)

            count_concepts += 1
            processed += 1
            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)

        count_refs = 0
        for r in refs:
            # r is Reference Pydantic model
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "reference",
                "term": r.short_citation or (r.citation[:50] + "..."),
                "definition": r.citation,  # Full citation as definition
                "doi_link": r.doi_link,
                "source_file": source_name,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {"short_citation": r.short_citation, "language": language},
            }
            await self.repository.add_reference(item)
            count_refs += 1
            processed += 1
            if tracker and total_items > 0 and processed % 10 == 0:
                percent = 60 + int((processed / total_items) * 35)
                tracker.update(stage=f"Storing items ({processed}/{total_items})", percent=percent)

        count_claims = 0
        for cl in claims:
            # cl is Claim Pydantic model
            item = {
                "id": str(uuid.uuid4()),
                "job_id": job_id,
                "type": "claim",
                "term": (cl.citation_text[:50] + "...") if cl.citation_text else "Claim",
                "definition": cl.claim_text,  # The claim itself is the "definition" or content
                "source_file": source_name,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "citation_keys": cl.citation_keys,
                    "citation_text": cl.citation_text,
                    "full_reference": cl.original_markdown,
                    "concept_context": cl.concept_context,
                    "language": language,
                },
            }
            await self.repository.add_claim(item)
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
            file_size=file_size,
            filename=source_name,
        )

    async def retrieve_context(self, query: str | None = None) -> list[KnowledgeItem]:
        """Retrieve context from the knowledge base.

        For MVP/Phase 2, this performs an in-memory filter of all knowledge base items.
        In the future (V3), this should be replaced with a Vector DB search.

        Args:
            query (str | None): Optional search term. If None, returns a summary of all items.

        Returns:
            list[KnowledgeItem]: A list of relevant knowledge items.
        """
        try:
            # 1. Fetch ALL items separated by collection (MVP approach)
            concepts = await self.repository.get_concepts()
            references = await self.repository.get_references()
            claims = await self.repository.get_claims()
            all_items = concepts + references + claims

            if not all_items:
                return []

            # 2. Filter in Memory
            matches = []
            if query:
                q = query.lower()
                for item in all_items:
                    term = item.get("term", "").lower()
                    defn = item.get("definition", "").lower()
                    # Simple substring match
                    if q in term or q in defn:
                        matches.append(item)
            else:
                # If no query, return everything (limit to top 20 to avoid context overflow)
                matches = all_items[:20]

            if not matches:
                return []

            # 3. Map to Domain Models
            results = []
            for m in matches:
                results.append(
                    KnowledgeItem(
                        id=m.get("id", "unknown"),
                        type=m.get("type", "unknown"),
                        term=m.get("term", "N/A"),
                        definition=m.get("definition", "N/A"),
                        source=m.get("source_file", "unknown"),
                        score=m.get("score", 0.0),
                    )
                )

            return results

        except Exception as e:
            error_code = ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED
            logger.error(f"[KBService] {error_code.value}: Retrieval failed: {e}", exc_info=True)

            raise ServiceUnavailableError(
                message=f"Knowledge Base retrieval failed: {e}",
                details={"error_code": error_code, "original_error": str(e)},
            ) from e
