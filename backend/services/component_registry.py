"""Component Registry Service.

Responsible for loading system components (prompts, rules, mandates) from seed data
and resolving them into full text instructions for Agents.
"""
import json
import logging
import os
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """Registry for looking up and resolving system components."""

    _instance = None
    _components: dict[str, dict[str, Any]] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
            cls._instance._load_components()
        return cls._instance

    def _load_components(self):
        """Loads components from data/db.json."""
        try:
            # Path relative to backend root or absolute
            # We assume running from root, so data/db.json
            db_path = "data/db.json"
            if not os.path.exists(db_path):
                # Fallback for different CWD
                db_path = os.path.join(os.getcwd(), "data", "db.json")

            if os.path.exists(db_path):
                with open(db_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._components = data.get("components", {})
                logger.info(f"[ComponentRegistry] Loaded {len(self._components)} components from {db_path}")
            else:
                logger.warning(f"[ComponentRegistry] db.json not found at {db_path}. Components empty.")

        except Exception as e:
            logger.error(f"[ComponentRegistry] Failed to load components: {e}")

    def get_component(self, component_id: str) -> dict[str, Any] | None:
        """Retrieves a single component by ID."""
        # The components dict in db.json is keyed by a numeric string ID usually,
        # but the meaningful ID is inside the object as "id".
        # OR, in some versions of db.json, it might be keyed by "id".
        # Let's check the structure based on previous view_file of db.json.
        # Structure seen: "components": {"1": {"id": "HEADER_MANDATES", ...}, ...}

        # Slow lookup (O(N)) because keyed by numeric ID.
        # Optimization: Build an index on load.
        for key, comp in self._components.items():
            if comp.get("id") == component_id:
                return comp
        return None

    @lru_cache(maxsize=128)
    def resolve_prompts(self, prompt_ids: tuple[str]) -> str:
        """Resolves a list of prompt IDs into a single system instruction string.

        Args:
            prompt_ids: Tuple of strings (tuple for lru_cache).

        Returns:
            Concatenated text content.
        """
        resolved_text = []
        missing = []

        logger.info(f"[ComponentRegistry] Resolving prompts: {prompt_ids}")

        for pid in prompt_ids:
            comp = self.get_component(pid)
            if comp and "content" in comp:
                content = comp["content"]
                # If content is list (e.g. output config), join it?
                # Usually prompts are strings.
                if isinstance(content, str):
                    resolved_text.append(content)
                elif isinstance(content, list):
                    # For headers or configs that might be lists
                    resolved_text.append("\n".join(str(x) for x in content))
            else:
                missing.append(pid)

        if missing:
            logger.warning(f"[ComponentRegistry] Missing components for prompt resolution: {missing}")

        result = "\n\n".join(resolved_text)
        logger.info(f"[ComponentRegistry] Resolved text length: {len(result)}")
        return result
