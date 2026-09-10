"""Deterministic Seed Vault Migration Script for ContrastivePairDTO.

Migrates all 305 legacy string `contrastive_example` fields in `backend_v2/seed/seed_data.json`
from multiline strings ("ACCEPTABLE: ...\\nUNACCEPTABLE: ...") into 100% valid Pydantic V2
ContrastivePairDTO structures: {"acceptable": "...", "rejected": "..."}.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend_v2.models.v2_core import ContrastivePairDTO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SEED_FILE_PATH = Path("backend_v2/seed/seed_data.json")
BACKUP_DIR = Path("backend_v2/seed/backups")


def parse_contrastive_text(raw_text: str) -> dict[str, str] | None:
    """Parses legacy multiline contrastive example into acceptable and rejected strings.

    Args:
        raw_text: Raw multiline text containing ACCEPTABLE and UNACCEPTABLE/REJECTED prefixes.

    Returns:
        Dictionary with 'acceptable' and 'rejected' strings if valid, None otherwise.
    """
    cleaned = raw_text.strip()
    # Normalize potential UTF-8 mojibake or artifacts if present
    cleaned = cleaned.replace("â€œ", '"').replace("â€", '"').replace("â€”", "—")

    # Match ACCEPTABLE and UNACCEPTABLE or REJECTED
    # Handles multiline blocks with quotes or unquoted text
    pattern = re.compile(
        r"^ACCEPTABLE:\s*(.*?)\s*\n\s*(?:UNACCEPTABLE|REJECTED):\s*(.*?)$",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.match(cleaned)
    if not match:
        return None

    acceptable_raw = match.group(1).strip()
    rejected_raw = match.group(2).strip()

    # Strip outer quotation marks if wrapped in quotes
    if (acceptable_raw.startswith('"') and acceptable_raw.endswith('"')) or (
        acceptable_raw.startswith("'") and acceptable_raw.endswith("'")
    ):
        acceptable_raw = acceptable_raw[1:-1].strip()

    if (rejected_raw.startswith('"') and rejected_raw.endswith('"')) or (
        rejected_raw.startswith("'") and rejected_raw.endswith("'")
    ):
        rejected_raw = rejected_raw[1:-1].strip()

    return {"acceptable": acceptable_raw, "rejected": rejected_raw}


def migrate_seed_data(seed_path: Path = SEED_FILE_PATH) -> tuple[int, int, int]:
    """Migrates contrastive_example entries in seed_data.json to ContrastivePairDTO dicts.

    Args:
        seed_path: Path to seed_data.json.

    Returns:
        Tuple of (migrated_count, null_skipped_count, parse_failed_count).
    """
    if not seed_path.exists():
        logger.error("Seed data file not found at %s", seed_path)
        sys.exit(1)

    with open(seed_path, "r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    # 1. Create timestamped and canonical backup copies
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    timestamped_backup = BACKUP_DIR / f"seed_data_backup_{timestamp}.json"
    canonical_backup = BACKUP_DIR / "seed_data_backup_contrastive_pre.json"

    with open(timestamped_backup, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(canonical_backup, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Created pre-migration backups: %s and %s", timestamped_backup, canonical_backup)

    migrated_count = 0
    null_skipped_count = 0
    parse_failed_count = 0
    failed_atoms: list[tuple[str, str]] = []

    prompt_blocks = data.get("prompt_blocks", [])
    for block in prompt_blocks:
        scales = block.get("scales", [])
        for scale in scales:
            claims = scale.get("claims", [])
            for claim in claims:
                tdas = claim.get("tda_assertions", [])
                for tda in tdas:
                    raw_contrastive = tda.get("contrastive_example")
                    if raw_contrastive is None:
                        null_skipped_count += 1
                        continue

                    if isinstance(raw_contrastive, dict):
                        # Already migrated
                        try:
                            ContrastivePairDTO.model_validate(raw_contrastive)
                            migrated_count += 1
                        except Exception as e:
                            parse_failed_count += 1
                            failed_atoms.append((tda.get("tda_id", "unknown"), str(e)))
                        continue

                    if isinstance(raw_contrastive, str):
                        parsed = parse_contrastive_text(raw_contrastive)
                        if not parsed:
                            parse_failed_count += 1
                            failed_atoms.append((tda.get("tda_id", "unknown"), raw_contrastive[:80]))
                            continue

                        try:
                            # Validate through strict Pydantic V2 model
                            dto = ContrastivePairDTO.model_validate(parsed)
                            tda["contrastive_example"] = dto.model_dump(mode="json")
                            migrated_count += 1
                        except Exception as exc:
                            parse_failed_count += 1
                            failed_atoms.append((tda.get("tda_id", "unknown"), f"ValidationError: {exc}"))

    summary = {
        "migrated": migrated_count,
        "null_skipped": null_skipped_count,
        "parse_failed": parse_failed_count,
    }
    logger.info("Migration Summary: %s", json.dumps(summary, indent=2))

    if parse_failed_count > 0:
        logger.error("Migration failed on %d atoms: %s", parse_failed_count, failed_atoms[:10])
        sys.exit(1)

    # 2. Atomic persistence using NamedTemporaryFile, fsync, and os.replace
    target_dir = seed_path.parent
    with tempfile.NamedTemporaryFile("w", dir=str(target_dir), delete=False, encoding="utf-8") as tf:
        temp_path = Path(tf.name)
        json.dump(data, tf, indent=2, ensure_ascii=False)
        tf.flush()
        os.fsync(tf.fileno())

    # Pre-flight reload check
    with open(temp_path, "r", encoding="utf-8") as f:
        json.load(f)

    temp_path.replace(seed_path)
    logger.info("Successfully atomically updated %s with migrated ContrastivePairDTO entries.", seed_path)

    return migrated_count, null_skipped_count, parse_failed_count


if __name__ == "__main__":
    migrate_seed_data()
