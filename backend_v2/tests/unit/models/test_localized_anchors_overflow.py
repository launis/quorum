"""TDD RED: Reproduce localized_anchors_found overflow crash.

Production crash: exe_51311c08e1fe4e299a3529dc49560363
Step sr_5a8ae009eee44fe2 (Analyst) failed because LLM returned 7
localized_anchors_found items from Finnish Sitra data, but Pydantic
schema enforced max_length=5.

NEW Production crash (Jun 8): exe_34c81955401d4a0688476416402f06bb
Step failed because LLM returned 12 localized_anchors_found items
(e.g., 'Koska', 'johtaneet', etc.), but Pydantic enforced max_length=10.
"""

from backend_v2.models.enums import SystemConcurrency

# The exact payload from the new production crash log
SITRA_ANCHORS_12 = [
    "Koska",
    "johtaneet",
    "estää",
    "mahdollistaa",
    "pitää",
    "Jos",
    "täyttyvät",
    "ei puututa",
    "Kun",
    "voimme",
    "säästää",
    "vapauttaa",
]


def test_localized_anchors_accepts_12_items() -> None:
    """Verify that StrippedBaseTDAExtraction accepts >10 localized anchors.

    This reproduces the exact production crash where the strictly formatted
    XML prompt mandates extracting all physical anchors, legitimately producing
    12 anchor keywords.
    """
    from backend_v2.models.v2_core import BaseTDAExtraction

    payload = {
        "localized_anchors_found": SITRA_ANCHORS_12,
        "semantic_reasoning": "Säännön ankkurit löydetty monikollisesti tekstistä.",
        "contextual_override": False,
        "exact_quotes": [{"source_alias": "test_alias", "text": "Koska syyt ovat johtaneet tähän..."}],
    }

    # This MUST NOT raise ValidationError
    instance = BaseTDAExtraction.model_validate(payload, strict=True)
    assert len(instance.localized_anchors_found) == 12


def test_schema_max_localized_anchors_is_at_least_15() -> None:
    """Verify the SystemConcurrency constant allows sufficient anchors."""
    assert SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS >= 15, (
        f"SCHEMA_MAX_LOCALIZED_ANCHORS={SystemConcurrency.SCHEMA_MAX_LOCALIZED_ANCHORS} "
        "should be >= 15 for the overflow test."
    )
