import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from fastapi import status

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Registry for looking up and resolving system components.
    
    Refactored to be stateless and use AbstractWorkflowRepository (Feb 2026).
    """

    @staticmethod
    async def get_component(repository: AbstractWorkflowRepository, component_id: str) -> Dict[str, Any]:
        """Retrieves a single component by ID using the repository.

        Args:
            repository: The repository instance.
            component_id: The ID of the component to retrieve.

        Returns:
            Dict[str, Any]: The component configuration.

        Raises:
            AppException: If component is not found (COMPONENT_NOT_FOUND).
        """
        comp = await repository.get_component_by_id(component_id)
        if comp:
            return comp
        
        # Fallback: Try by name as some IDs might be names in older configs
        comp = await repository.get_component_by_name(component_id)
        if comp:
            return comp

        # FAIL FAST
        error_code = ErrorCodes.COMPONENT_NOT_FOUND
        logger.error(f"[ComponentRegistry] Component '{component_id}' NOT FOUND.")
        raise AppException(
            message=f"Component '{component_id}' not found in registry.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code, "component_id": component_id}
        )

    @staticmethod
    async def resolve_prompts(repository: AbstractWorkflowRepository, prompt_ids: Tuple[str, ...]) -> str:
        """Resolves a list of prompt IDs into a single system instruction string.

        Args:
            repository: The repository instance.
            prompt_ids: Tuple of strings.

        Returns:
            str: Concatenated text content.

        Raises:
            AppException: If any component is missing (Fail Fast).
        """
        resolved_text: List[str] = []
        
        logger.info(f"[ComponentRegistry] Resolving prompts: {prompt_ids}")

        for pid in prompt_ids:
            # This will raise AppException immediately if not found
            comp = await ComponentRegistry.get_component(repository, pid)
            
            if "content" in comp:
                content = comp["content"]
                if isinstance(content, str):
                    resolved_text.append(content)
                elif isinstance(content, list):
                    # For headers or configs that might be lists
                    resolved_text.append("\n".join(str(x) for x in content))
            else:
                logger.warning(f"[ComponentRegistry] Component '{pid}' has no 'content' field.")

        result = "\n\n".join(resolved_text)
        logger.info(f"[ComponentRegistry] Resolved text length: {len(result)}")
        return result

    @staticmethod
    async def resolve_prompts_map(repository: AbstractWorkflowRepository, prompt_ids: Tuple[str, ...]) -> Dict[str, str]:
        """Resolves a list of prompt IDs into a map of {id: content}.

        Args:
            repository: The repository instance.
            prompt_ids: Tuple of strings.

        Returns:
            Dict[str, str]: Map of component ID to content string.
        """
        resolved_map: Dict[str, str] = {}
        
        for pid in prompt_ids:
            comp = await ComponentRegistry.get_component(repository, pid)
            
            if "content" in comp:
                content = comp["content"]
                if isinstance(content, str):
                    resolved_map[pid] = content
                elif isinstance(content, list):
                    resolved_map[pid] = "\n".join(str(x) for x in content)
            else:
                logger.warning(f"[ComponentRegistry] Component '{pid}' has no 'content' field.")
                resolved_map[pid] = ""

        return resolved_map
