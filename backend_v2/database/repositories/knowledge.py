import uuid
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository


class KnowledgeRepositoryImpl(BaseRepository):
    """Repository implementation for Knowledge base, Banned phrases and Prompts."""

    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        return await self.driver.query("banned_phrases")

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if not existing:
            doc_id = str(uuid.uuid4())
            await self.driver.upsert("banned_phrases", {"phrase": phrase, "language": language, "id": doc_id}, doc_id)

    async def delete_banned_phrase(self, phrase: str) -> bool:
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if existing:
            return await self.driver.delete("banned_phrases", existing[0]["id"])
        return False

    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        res = await self.driver.get("prompts", template_id)
        if res:
            return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}

        res_list = await self.driver.query("prompts", [Filter("id", "==", template_id)], limit=1)
        if res_list:
            res = res_list[0]
            return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}

        return None

    async def get_concepts(self) -> list[dict[str, Any]]:
        return await self.driver.query("concepts")

    async def get_references(self) -> list[dict[str, Any]]:
        return await self.driver.query("references")

    async def get_claims(self) -> list[dict[str, Any]]:
        return await self.driver.query("claims")

    async def add_concept(self, item: dict[str, Any]) -> str:
        doc_id = item["id"]
        return await self.driver.upsert("concepts", item, doc_id)

    async def add_reference(self, item: dict[str, Any]) -> str:
        doc_id = item["id"]
        return await self.driver.upsert("references", item, doc_id)

    async def add_claim(self, item: dict[str, Any]) -> str:
        doc_id = item["id"]
        return await self.driver.upsert("claims", item, doc_id)

    async def clear_knowledge_base(self) -> None:
        await self.driver.clear("concepts")
        await self.driver.clear("references")
        await self.driver.clear("claims")
