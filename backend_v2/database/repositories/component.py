from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import PromptBlock


class ComponentRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Components, PromptBlocks, Agents, Blueprints and Output Profiles."""

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if type:
            filters.append(Filter("type", "==", type))

        components = await self.driver.query("components", filters)

        if exclude_types:
            components = [c for c in components if c.get("type") not in exclude_types]

        return components

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        return await self.driver.get("components", component_id)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        res = await self.driver.query("components", [Filter("name", "==", name)], limit=1)
        return res[0] if res else None

    async def get_component_by_slug(self, slug: str) -> dict[str, Any] | None:
        res = await self.driver.query("components", [Filter("slug", "==", slug)], limit=1)
        return res[0] if res else None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.update("components", component_id, {"module": module, "class_name": component_class})

    async def register_component(self, component_data: dict[str, Any]) -> str:
        doc_id = component_data["id"]
        return await self.driver.upsert("components", component_data, doc_id)

    async def create_component(self, component_data: dict[str, Any]) -> str:
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: dict[str, Any]) -> str:
        comp = await self.get_component_by_id(component_id)
        if not comp:
            raise ResourceNotFoundError(resource_type="LegacyPromptBlock", resource_id=component_id)
        await self.driver.update("components", component_id, updates)
        return component_id

    async def delete_component(self, component_id: str) -> bool:
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.delete("components", component_id)

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        matrices = await self.get_all_components(type="evaluation_matrix")
        matches = []
        for m in matrices:
            content = m.get("content", {})
            if not isinstance(content, dict):
                continue
            criteria = content.get("criteria", [])
            if not isinstance(criteria, list):
                continue
            for crit in criteria:
                if isinstance(crit, dict) and crit.get("dimension_id") == dimension_id:
                    matches.append(m["id"])
                    break
        return matches

    # --- PromptBlocks ---

    async def get_prompt_block_by_id(self, block_id: str) -> dict[str, Any] | None:
        return await self.driver.get("prompt_blocks", block_id)

    async def get_prompt_block(self, block_id: str) -> dict[str, Any] | None:
        return await self.get_prompt_block_by_id(block_id)

    async def get_prompt_block_by_slug(self, slug: str) -> dict[str, Any] | None:
        res = await self.driver.query("prompt_blocks", [Filter("slug", "==", slug)], limit=1)
        return res[0] if res else None

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        return await self.driver.query("prompt_blocks")

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        data = await self.get_all_prompt_blocks()
        models = []
        for b in data:
            try:
                models.append(PromptBlock.model_validate(b, strict=False))
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error("Failed to parse PromptBlock %s: %s", b.get("id"), e, exc_info=True)
                from backend_v2.exceptions import AppException, ErrorCodes

                raise AppException(
                    message=f"Failed to parse PromptBlock {b.get('id')} from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

    async def create_prompt_block(self, block_data: dict[str, Any]) -> str:
        doc_id = block_data["id"]
        return await self.driver.upsert("prompt_blocks", block_data, doc_id)

    async def update_prompt_block(self, block_id: str, updates: dict[str, Any]) -> bool:
        old_doc = await self.get_prompt_block_by_id(block_id)
        if not old_doc:
            return False

        await self.driver.update("prompt_blocks", block_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(block_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("prompt_blocks", new_doc, new_id)
        return True

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        block = await self.get_prompt_block_by_id(block_id)
        if not block:
            return False

        if not force_delete:
            steps = await self.driver.query("steps")
            for s in steps:
                if block_id in s.get("prompt_blocks", []):
                    step_ref = str(s.get("id", "unknown"))
                    raise AppException(
                        message="PromptBlock delete blocked by step usage.",
                        details={
                            "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                            "prompt_block_id": block_id,
                            "step_id": step_ref,
                        },
                        status_code=400,
                    )

        return await self.driver.delete("prompt_blocks", block_id)

    # --- Agents ---

    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        return await self.driver.get("agents", agent_id)

    async def get_all_agents(self) -> list[dict[str, Any]]:
        return await self.driver.query("agents")

    async def create_agent(self, agent_data: dict[str, Any]) -> str:
        doc_id = agent_data["id"]
        return await self.driver.upsert("agents", agent_data, doc_id)

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        old_doc = await self.get_agent_by_id(agent_id)
        if not old_doc:
            return False

        await self.driver.update("agents", agent_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(agent_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("agents", new_doc, new_id)
        return True

    async def delete_agent(self, agent_id: str) -> bool:
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return False
        return await self.driver.delete("agents", agent_id)

    # --- Task Blueprints ---

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> dict[str, Any] | None:
        return await self.driver.get("task_blueprints", blueprint_id)

    async def get_all_task_blueprints(self) -> list[dict[str, Any]]:
        return await self.driver.query("task_blueprints")

    async def create_task_blueprint(self, blueprint_data: dict[str, Any]) -> str:
        doc_id = blueprint_data["id"]
        return await self.driver.upsert("task_blueprints", blueprint_data, doc_id)

    async def update_task_blueprint(self, blueprint_id: str, updates: dict[str, Any]) -> bool:
        old_doc = await self.get_task_blueprint_by_id(blueprint_id)
        if not old_doc:
            return False

        await self.driver.update("task_blueprints", blueprint_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(blueprint_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("task_blueprints", new_doc, new_id)
        return True

    async def delete_task_blueprint(self, blueprint_id: str) -> bool:
        blueprint = await self.get_task_blueprint_by_id(blueprint_id)
        if not blueprint:
            return False
        return await self.driver.delete("task_blueprints", blueprint_id)

    # --- Output Profiles ---

    async def get_all_output_profiles(self) -> list[dict[str, Any]]:
        return await self.driver.query("output_profiles")

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        data = await self.get_all_output_profiles()
        models = []
        for pd in data:
            try:
                models.append(OutputProfile.model_validate(pd, strict=False))
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error("Failed to parse OutputProfile %s: %s", pd.get("id"), e, exc_info=True)
                from backend_v2.exceptions import AppException, ErrorCodes

                raise AppException(
                    message="Failed to parse profile from database",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
        return models

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any] | None:
        return await self.driver.get("output_profiles", profile_id)

    async def create_output_profile(self, profile_data: dict[str, Any]) -> str:
        doc_id = profile_data["id"]
        return await self.driver.upsert("output_profiles", profile_data, doc_id)

    async def update_output_profile(self, profile_id: str, updates: dict[str, Any]) -> bool:
        return await self.driver.update("output_profiles", profile_id, updates)

    async def delete_output_profile(self, profile_id: str) -> bool:
        return await self.driver.delete("output_profiles", profile_id)
