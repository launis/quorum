"""TDD RED: Reproduce localized_anchors_found overflow crash.

Production crash: exe_51311c08e1fe4e299a3529dc49560363
Step sr_5a8ae009eee44fe2 (Analyst) failed because LLM returned 7
localized_anchors_found items from Finnish Sitra data, but Pydantic
schema enforced max_length=5.
"""

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import SystemConcurrency
from backend_v2.services.orchestrator.prompt_compiler import StrippedBaseTDAExtraction


# The exact payload from the production crash log (L530-532)
SITRA_ANCHORS_7 = [
    "Viite",
    "Sitran",
    "2017",
    "2020",
    "2023",
    "CSRD-direktiivin",
    "EU-taksonomian",
]


def test_localized_anchors_accepts_7_items() -> None:
    """Verify that StrippedBaseTDAExtraction accepts >5 localized anchors.

    This reproduces the exact production crash where Finnish multi-reference
    data legitimately produces more than 5 anchor keywords.
    """
    payload = {
        "localized_anchors_found": SITRA_ANCHORS_7,
        "semantic_reasoning": "Sitra megatrendien viittaus kattaa koko 2017-2023 aikajakson.",
        "contextual_override": False,
        "structural_location": "N/A",
        "exact_quote": "Sitran megatrendiraportti 2017–2023 ja CSRD-direktiivin vaatimukset",
    }

    # This MUST NOT raise ValidationError — 7 anchors is valid Finnish data
    instance = StrippedBaseTDAExtraction.model_validate(payload, strict=True)
    assert len(instance.localized_anchors_found) == 7


def test_schema_max_localized_anchors_is_at_least_10() -> None:
    """Verify the SystemConcurrency constant allows sufficient anchors."""
    assert SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS >= 10, (
        f"SCHEMA_MAX_LOCALIZED_ANCHORS={SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS} "
        f"is too low for multilingual data. Must be >= 10."
    )
