"""Regression test reproducing bug where local db_v2.json contains unmigrated prompt_blocks with ai_description."""

from pathlib import Path

from tinydb import TinyDB

from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.settings import get_settings


def test_live_db_prompt_blocks_conform_to_domain_schema() -> None:
    """Verifies that all prompt_blocks in live data/db_v2.json parse cleanly into PromptBlock domain models."""
    db_path = Path(get_settings().prod_db_path)
    assert db_path.exists(), f"Database file {db_path} does not exist"

    db = TinyDB(str(db_path), encoding="utf-8")
    table = db.table("prompt_blocks")
    records = table.all()
    assert len(records) > 0, "Database table prompt_blocks is empty"

    for record in records:
        PromptBlockAdapter.validate_python(record, strict=False)
