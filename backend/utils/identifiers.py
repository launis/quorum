import re
import uuid
from typing import Optional


def generate_unique_id(base_name: Optional[str] = None, prefix: Optional[str] = None) -> str:
    """
    Generates a unique, slugified identifier.

    Format: {prefix}-{slug}-{short_uuid}
    Example: "my-prefix-acme-corp-a1b2c3d4"

    If no base_name is provided, returns a full UUID.
    """
    suffix = str(uuid.uuid4())[:8]

    if not base_name:
        return str(uuid.uuid4())

    # Slugify: lowercase, replace non-alphanumeric with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-")

    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(slug)
    parts.append(suffix)

    return "-".join(parts)
