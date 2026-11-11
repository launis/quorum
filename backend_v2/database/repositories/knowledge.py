"""Database repository implementation module for Knowledge base, Banned phrases and Prompts."""

from __future__ import annotations

import logging

from pydantic import BaseModel

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.knowledge import (
    BannedPhrase,
    Claim,
    ClaimCreateDTO,
    Concept,
    ConceptCreateDTO,
    PromptTemplateDTO,
    Reference,
    ReferenceCreateDTO,
)
from backend_v2.models.enums import SystemLocale

logger = logging.getLogger(__name__)

__all__ = ["KnowledgeRepositoryImpl"]


class KnowledgeRepositoryImpl(BaseRepository):
    """Repository implementation for Knowledge base, Banned phrases and Prompts."""

    async def _query_and_validate[T: BaseModel](
        self,
        collection: str,
        model_cls: type[T],
        entity_label: str,
    ) -> list[T]:
        """Query a storage collection and hydrate records into a typed domain model list.

        Args:
            collection: Target storage collection name.
            model_cls: Target Pydantic domain model class.
            entity_label: Human-readable entity label for RFC 7807 error reporting.

        Returns:
            List of validated domain model instances.

        Raises:
            AppException: If a stored record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        data = await self.driver.query(collection)
        items: list[T] = []
        for record in data:
            try:
                items.append(model_cls.model_validate(record, strict=False))
            except Exception as e:
                item_id = "unknown"
                if "id" in record:
                    item_id = str(record["id"])
                logger.error(
                    "[KnowledgeRepository] %s: Corrupted %s %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    entity_label,
                    item_id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Corrupted {entity_label} {item_id}: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "item_id": item_id},
                ) from e
        return items

    async def _upsert_knowledge_item(self, collection: str, item: BaseModel) -> str:
        """Serialize a creation DTO with a generated UUIDv7 identifier and upsert it.

        Args:
            collection: Target storage collection name.
            item: Validated creation DTO instance.

        Returns:
            The persisted entity identifier.
        """
        payload = item.model_dump(mode="json")
        doc_id = str(generate_uuid7())
        payload["id"] = doc_id
        return await self.driver.upsert(collection, payload, doc_id)

    async def get_banned_phrases(self) -> list[BannedPhrase]:
        """Retrieve all banned phrases.

        Returns:
            List of validated BannedPhrase domain models.

        Raises:
            AppException: If a banned phrase record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._query_and_validate("banned_phrases", BannedPhrase, "banned phrase")

    async def add_banned_phrase(self, phrase: str, language: str = SystemLocale.EN.value) -> None:
        """Add a new banned phrase if not already existing.

        Args:
            phrase: The phrase string to ban.
            language: Language code for the phrase.
        """
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if not existing:
            doc_id = str(generate_uuid7())
            await self.driver.upsert("banned_phrases", {"phrase": phrase, "language": language, "id": doc_id}, doc_id)

    async def delete_banned_phrase(self, phrase: str) -> bool:
        """Delete a banned phrase.

        Args:
            phrase: The phrase string to remove.

        Returns:
            True if removed, False if not found.
        """
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if existing:
            return await self.driver.delete("banned_phrases", existing[0]["id"])
        return False

    async def get_prompt_template(self, template_id: str) -> PromptTemplateDTO | None:
        """Retrieve a prompt template by ID via O(1) primary-key lookup.

        Args:
            template_id: Unique identifier for the prompt template.

        Returns:
            The validated PromptTemplateDTO if found, otherwise None.
        """
        res = await self.driver.get("prompts", template_id)
        if not res:
            return None

        sys_p = ""
        if "system_prompt" in res:
            sys_p = str(res["system_prompt"])
        usr_p = ""
        if "user_prompt" in res:
            usr_p = str(res["user_prompt"])
        return PromptTemplateDTO(system=sys_p, user=usr_p)

    async def get_concepts(self) -> list[Concept]:
        """Retrieve all knowledge base concepts.

        Returns:
            List of validated Concept domain models.

        Raises:
            AppException: If a concept record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._query_and_validate("concepts", Concept, "concept")

    async def get_references(self) -> list[Reference]:
        """Retrieve all knowledge base references.

        Returns:
            List of validated Reference domain models.

        Raises:
            AppException: If a reference record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._query_and_validate("references", Reference, "reference")

    async def get_claims(self) -> list[Claim]:
        """Retrieve all knowledge base claims.

        Returns:
            List of validated Claim domain models.

        Raises:
            AppException: If a claim record fails validation (ErrorCodes.VALIDATION_FAILED).
        """
        return await self._query_and_validate("claims", Claim, "claim")

    async def add_concept(self, item: ConceptCreateDTO) -> str:
        """Add a concept to the knowledge base.

        Args:
            item: ConceptCreateDTO data.

        Returns:
            The created concept ID.
        """
        return await self._upsert_knowledge_item("concepts", item)

    async def add_reference(self, item: ReferenceCreateDTO) -> str:
        """Add a reference to the knowledge base.

        Args:
            item: ReferenceCreateDTO data.

        Returns:
            The created reference ID.
        """
        return await self._upsert_knowledge_item("references", item)

    async def add_claim(self, item: ClaimCreateDTO) -> str:
        """Add a claim to the knowledge base.

        Args:
            item: ClaimCreateDTO data.

        Returns:
            The created claim ID.
        """
        return await self._upsert_knowledge_item("claims", item)

    async def clear_knowledge_base(self) -> None:
        """Clear all concepts, references, and claims from the database."""
        await self.driver.clear("concepts")
        await self.driver.clear("references")
        await self.driver.clear("claims")
