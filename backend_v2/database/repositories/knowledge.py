"""Database repository implementation module for Knowledge base, Banned phrases and Prompts."""

from __future__ import annotations

import logging
import uuid

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ErrorCodes
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

logger = logging.getLogger(__name__)


class KnowledgeRepositoryImpl(BaseRepository):
    """Repository implementation for Knowledge base, Banned phrases and Prompts."""

    async def get_banned_phrases(self) -> list[BannedPhrase]:
        """Retrieves all banned phrases.

        Returns:
            List of validated BannedPhrase domain models.
        """
        data = await self.driver.query("banned_phrases")
        phrases: list[BannedPhrase] = []
        for p in data:
            try:
                phrases.append(BannedPhrase.model_validate(p, strict=False))
            except Exception as e:
                item_id = p["id"] if "id" in p else "unknown"
                logger.error(
                    "[KnowledgeRepository] %s: Skipping corrupted banned phrase %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return phrases

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        """Adds a new banned phrase if not already existing.

        Args:
            phrase: The phrase string to ban.
            language: Language code for the phrase.
        """
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if not existing:
            doc_id = str(uuid.uuid4())
            await self.driver.upsert("banned_phrases", {"phrase": phrase, "language": language, "id": doc_id}, doc_id)

    async def delete_banned_phrase(self, phrase: str) -> bool:
        """Deletes a banned phrase.

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
        """Retrieves a prompt template by ID.

        Args:
            template_id: Unique identifier for the prompt template.

        Returns:
            The validated PromptTemplateDTO if found, otherwise None.
        """
        res = await self.driver.get("prompts", template_id)
        if res:
            sys_p = res["system_prompt"] if "system_prompt" in res else ""
            usr_p = res["user_prompt"] if "user_prompt" in res else ""
            return PromptTemplateDTO(system=sys_p, user=usr_p)

        res_list = await self.driver.query("prompts", [Filter("id", "==", template_id)], limit=1)
        if res_list:
            res = res_list[0]
            sys_p = res["system_prompt"] if "system_prompt" in res else ""
            usr_p = res["user_prompt"] if "user_prompt" in res else ""
            return PromptTemplateDTO(system=sys_p, user=usr_p)

        return None

    async def get_concepts(self) -> list[Concept]:
        """Retrieves all knowledge base concepts.

        Returns:
            List of validated Concept domain models.
        """
        data = await self.driver.query("concepts")
        concepts: list[Concept] = []
        for c in data:
            try:
                concepts.append(Concept.model_validate(c, strict=False))
            except Exception as e:
                item_id = c["id"] if "id" in c else "unknown"
                logger.error(
                    "[KnowledgeRepository] %s: Skipping corrupted concept %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return concepts

    async def get_references(self) -> list[Reference]:
        """Retrieves all knowledge base references.

        Returns:
            List of validated Reference domain models.
        """
        data = await self.driver.query("references")
        refs: list[Reference] = []
        for r in data:
            try:
                refs.append(Reference.model_validate(r, strict=False))
            except Exception as e:
                item_id = r["id"] if "id" in r else "unknown"
                logger.error(
                    "[KnowledgeRepository] %s: Skipping corrupted reference %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return refs

    async def get_claims(self) -> list[Claim]:
        """Retrieves all knowledge base claims.

        Returns:
            List of validated Claim domain models.
        """
        data = await self.driver.query("claims")
        claims: list[Claim] = []
        for c in data:
            try:
                claims.append(Claim.model_validate(c, strict=False))
            except Exception as e:
                item_id = c["id"] if "id" in c else "unknown"
                logger.error(
                    "[KnowledgeRepository] %s: Skipping corrupted claim %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return claims

    async def add_concept(self, item: ConceptCreateDTO) -> str:
        """Adds a concept to knowledge base.

        Args:
            item: ConceptCreateDTO data.

        Returns:
            The created concept ID.
        """
        payload = item.model_dump(mode="json")
        doc_id = str(uuid.uuid4())
        payload["id"] = doc_id
        return await self.driver.upsert("concepts", payload, doc_id)

    async def add_reference(self, item: ReferenceCreateDTO) -> str:
        """Adds a reference to knowledge base.

        Args:
            item: ReferenceCreateDTO data.

        Returns:
            The created reference ID.
        """
        payload = item.model_dump(mode="json")
        doc_id = str(uuid.uuid4())
        payload["id"] = doc_id
        return await self.driver.upsert("references", payload, doc_id)

    async def add_claim(self, item: ClaimCreateDTO) -> str:
        """Adds a claim to knowledge base.

        Args:
            item: ClaimCreateDTO data.

        Returns:
            The created claim ID.
        """
        payload = item.model_dump(mode="json")
        doc_id = str(uuid.uuid4())
        payload["id"] = doc_id
        return await self.driver.upsert("claims", payload, doc_id)

    async def clear_knowledge_base(self) -> None:
        """Clears all concepts, references, and claims from the database."""
        await self.driver.clear("concepts")
        await self.driver.clear("references")
        await self.driver.clear("claims")
