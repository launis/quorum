import pytest
from pydantic import ValidationError

from backend.models.domain.falsifier import ReasoningFidelity
from backend.models.domain.logician import CognitiveLevel
from backend.models.domain.profiler import ProfilerMetrics
from backend.models.enums import BloomLevel, RoleClassification, StrategicDepth


def test_logician_cognitive_level_bloom_score_bounds():
    with pytest.raises(ValidationError):
        CognitiveLevel(
            bloom_level=BloomLevel.CREATING,
            strategic_depth=StrategicDepth.HIGH,
            bloom_score=7.0,  # Invalid
            strategic_score=2.0
        )

    with pytest.raises(ValidationError):
        CognitiveLevel(
            bloom_level=BloomLevel.CREATING,
            strategic_depth=StrategicDepth.HIGH,
            bloom_score=-1.0,  # Invalid
            strategic_score=2.0
        )

    # Valid
    c = CognitiveLevel(
        bloom_level=BloomLevel.CREATING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=0.0,
        strategic_score=2.0
    )
    assert c.bloom_score == 0.0


def test_falsifier_fidelity_abductive_score_bounds():
    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score="FIDELITY_HIGH",
            fidelity_numeric=4.0,  # Invalid
            abductive_score=2.0,
            plausibility_score=2.0,
            justification="Test"
        )

    with pytest.raises(ValidationError):
        ReasoningFidelity(
            fidelity_score="FIDELITY_HIGH",
            fidelity_numeric=2.0,
            abductive_score=4.0,  # Invalid
            plausibility_score=2.0,
            justification="Test"
        )
    
    # Valid
    f = ReasoningFidelity(
        fidelity_score="FIDELITY_HIGH",
        fidelity_numeric=3.0,
        abductive_score=2.5,
        plausibility_score=1.0,
        justification="Valid"
    )
    assert f.abductive_score == 2.5


def test_profiler_metrics_imperative_command_count():
    with pytest.raises(ValidationError):
        ProfilerMetrics(
            word_count=100,
            sentence_count=10,
            avg_sentence_length=10.0,
            lexical_diversity=0.5,
            capitalization_ratio=0.1,
            control_ratio=0.5,
            imperative_command_count=-1,  # Invalid
            role_classification=RoleClassification.PASSENGER
        )
    
    # Valid
    p = ProfilerMetrics(
        word_count=100,
        sentence_count=10,
        avg_sentence_length=10.0,
        lexical_diversity=0.5,
        capitalization_ratio=0.1,
        control_ratio=0.5,
        imperative_command_count=5,
        role_classification=RoleClassification.DRIVER
    )
    assert p.imperative_command_count == 5
