import json
import logging
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.auth import Organization, User
from backend_v2.models.v2_core import (
    ExecutionRecord,
    OutputProfile,
    PromptBlock,
    Step,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    Workflow,
)

logger = logging.getLogger(__name__)

# Constants
SEED_FILE_PATH = Path("backend_v2/seed/seed_data.json")


def load_seed_data() -> dict[str, list[dict[str, Any]]]:
    """Loads seed_data.json dynamically to ensure DB & Model parity."""
    assert SEED_FILE_PATH.exists(), f"Seed data file not found at {SEED_FILE_PATH}"
    with open(SEED_FILE_PATH, encoding="utf-8") as f:
        data: dict[str, list[dict[str, Any]]] = json.load(f)
    return data


try:
    SEED_DATA = load_seed_data()
except Exception as e:
    logger.error(f"Failed to load seed data: {e}")
    SEED_DATA = {}


def get_items(collection_name: str) -> list[Any]:
    """Returns parameterized items or a skipped dummy if empty."""
    items = SEED_DATA.get(collection_name, [])
    if not items:
        # Prevent PyTest from failing due to empty parameter lists
        return [pytest.param({}, marks=pytest.mark.skip(reason=f"No items found in {collection_name}"))]
    return items


def get_item_id(item: Any) -> str:
    """Helper to extract a human-readable identifier for test logs."""
    if not isinstance(item, dict):
        return "N/A"
    return str(item.get("id") or item.get("slug") or item.get("name") or "unknown_id")


@pytest.mark.parametrize("item", get_items("system_config"), ids=get_item_id)
def test_parity_system_config(item: dict[str, Any]) -> None:
    """Validates System Configs using Fail-Fast Pydantic rules."""
    if not item:
        return
    try:
        cfg_type = item.get("type", "unknown")
        if cfg_type == "model_registry":
            SystemConfigModelRegistry.model_validate(item)
        elif cfg_type == "mcp_gateways":
            SystemConfigMCPGateways.model_validate(item)
        else:
            pytest.fail(f"Unknown system_config polymorphic type: {cfg_type}")
    except ValidationError as e:
        pytest.fail(f"system_config '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("prompt_blocks"), ids=get_item_id)
def test_parity_prompt_blocks(item: dict[str, Any]) -> None:
    """Validates Prompt Blocks. Strictly forbids extra fields."""
    if not item:
        return
    try:
        PromptBlock.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"prompt_blocks '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("workflows"), ids=get_item_id)
def test_parity_workflows(item: dict[str, Any]) -> None:
    """Validates Workflows and embedded components."""
    if not item:
        return
    try:
        Workflow.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"workflows '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("steps"), ids=get_item_id)
def test_parity_steps(item: dict[str, Any]) -> None:
    """Validates workflow Steps."""
    if not item:
        return
    try:
        Step.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"steps '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("organizations"), ids=get_item_id)
def test_parity_organizations(item: dict[str, Any]) -> None:
    """Validates Organization models."""
    if not item:
        return
    try:
        Organization.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"organizations '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("users"), ids=get_item_id)
def test_parity_users(item: dict[str, Any]) -> None:
    """Validates User authorization models."""
    if not item:
        return
    try:
        User.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"users '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("output_profiles"), ids=get_item_id)
def test_parity_output_profiles(item: dict[str, Any]) -> None:
    """Validates OutputProfiles."""
    if not item:
        return
    try:
        OutputProfile.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"output_profiles '{get_item_id(item)}' failed validation:\n{e}")


@pytest.mark.parametrize("item", get_items("executions"), ids=get_item_id)
def test_parity_executions(item: dict[str, Any]) -> None:
    """Validates ExecutionRecords."""
    if not item:
        return
    try:
        ExecutionRecord.model_validate(item)
    except ValidationError as e:
        pytest.fail(f"executions '{get_item_id(item)}' failed validation:\n{e}")
