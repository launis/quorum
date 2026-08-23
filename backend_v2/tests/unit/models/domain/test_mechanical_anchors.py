"""Unit tests for MechanicalAnchorsPayload domain model."""

from backend_v2.models.domain.mechanical_anchors import MechanicalAnchorsPayload
from backend_v2.models.domain.performativity import PerformativePattern


def test_mechanical_anchors_default_instantiation() -> None:
    """Test default values when instantiating MechanicalAnchorsPayload directly."""
    payload = MechanicalAnchorsPayload(performative_patterns=[])
    assert payload.word_count == 0
    assert payload.say_do_gap == 0.0
    assert payload.automation_bias == 0.0
    assert payload.performative_patterns == []


def test_mechanical_anchors_from_context_direct_keys() -> None:
    """Test deterministic extraction when keys are present at top level."""
    context = {
        "word_count": 250,
        "say_do_gap": 0.45,
        "automation_bias": 0.15,
        "performative_patterns": [
            {
                "pattern_id": "pat_1",
                "detected_phrase": "clearly state",
                "category": "hedging",
            },
            "raw phrase marker",
        ],
    }
    payload = MechanicalAnchorsPayload.from_context(context)
    assert payload.word_count == 250
    assert payload.say_do_gap == 0.45
    assert payload.automation_bias == 0.15
    assert len(payload.performative_patterns) == 2
    assert payload.performative_patterns[0].detected_phrase == "clearly state"
    assert payload.performative_patterns[1].detected_phrase == "raw phrase marker"


def test_mechanical_anchors_from_context_nested_raw_inputs() -> None:
    """Test deterministic extraction when metrics are inside raw_inputs."""
    context = {
        "raw_inputs": {
            "word_count": 120,
            "say_do_gap": 0.2,
            "automation_bias": 0.8,
            "performative_phrases": [
                PerformativePattern(
                    pattern_id="pat_inst",
                    detected_phrase="unquestionably true",
                    category="certainty",
                )
            ],
        }
    }
    payload = MechanicalAnchorsPayload.from_context(context)
    assert payload.word_count == 120
    assert payload.say_do_gap == 0.2
    assert payload.automation_bias == 0.8
    assert len(payload.performative_patterns) == 1
    assert payload.performative_patterns[0].detected_phrase == "unquestionably true"


def test_mechanical_anchors_from_context_empty_and_none() -> None:
    """Test safe extraction from empty or None context."""
    p_none = MechanicalAnchorsPayload.from_context(None)
    assert p_none.word_count == 0
    assert p_none.performative_patterns == []

    p_empty = MechanicalAnchorsPayload.from_context({})
    assert p_empty.word_count == 0
    assert p_empty.performative_patterns == []


def test_mechanical_anchors_to_xml() -> None:
    """Test <mechanical_anchors> XML generation."""
    patterns = [
        PerformativePattern(
            pattern_id="p1",
            detected_phrase="we believe",
            category="marker",
        ),
        PerformativePattern(
            pattern_id="p2",
            detected_phrase="obviously",
            category="marker",
        ),
    ]
    payload = MechanicalAnchorsPayload(
        word_count=500,
        say_do_gap=0.3,
        automation_bias=0.1,
        performative_patterns=patterns,
    )
    xml = payload.to_xml()

    assert "<mechanical_anchors>" in xml
    assert "<word_count>500</word_count>" in xml
    assert "<say_do_gap>0.3</say_do_gap>" in xml
    assert "<automation_bias>0.1</automation_bias>" in xml
    assert "<phrase_count>2</phrase_count>" in xml
    assert "<phrase>we believe</phrase>" in xml
    assert "<phrase>obviously</phrase>" in xml
    assert "</mechanical_anchors>" in xml
