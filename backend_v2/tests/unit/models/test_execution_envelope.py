"""Unit tests for StepExecutionEnvelope base model."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.execution_envelope import StepExecutionEnvelope


def test_step_execution_envelope_valid_instantiation_and_roundtrip() -> None:
    """Verify StepExecutionEnvelope valid instantiation, defaults, and JSON roundtrip."""
    default_envelope = StepExecutionEnvelope()
    assert default_envelope.execution_id is None
    assert default_envelope.workflow_id is None
    assert default_envelope.step_id is None
    assert default_envelope.initiator_id is None
    assert default_envelope.timestamp_isot is None
    assert default_envelope.unix_time is None
    assert default_envelope.v2_engine is None
    assert default_envelope.model_dump(mode="json", exclude_none=True) == {}

    exe_id = generate_opaque_id(EntityPrefix.EXECUTION)
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    stp_id = generate_opaque_id(EntityPrefix.STEP)
    usr_id = generate_opaque_id(EntityPrefix.USER)

    populated = StepExecutionEnvelope(
        execution_id=exe_id,
        workflow_id=wf_id,
        step_id=stp_id,
        initiator_id=usr_id,
        timestamp_isot="2026-11-11T04:57:39+00:00",
        unix_time=1794373059,
        v2_engine=True,
    )
    assert populated.execution_id == exe_id
    assert populated.workflow_id == wf_id
    assert populated.step_id == stp_id
    assert populated.initiator_id == usr_id
    assert populated.timestamp_isot == "2026-11-11T04:57:39+00:00"
    assert populated.unix_time == 1794373059
    assert populated.v2_engine is True

    rehydrated = StepExecutionEnvelope.model_validate_json(populated.model_dump_json())
    assert rehydrated == populated


def test_step_execution_envelope_negative_boundaries() -> None:
    """Verify StepExecutionEnvelope rejects extra fields, invalid types, and mutation."""
    # ISTQB Negative 1: Extra unrecognized field rejected (extra="forbid")
    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate(
            {
                "execution_id": generate_opaque_id(EntityPrefix.EXECUTION),
                "unexpected_field": "forbidden",
            }
        )

    # ISTQB Negative 2: Non-string execution_id rejected under strict=True
    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"execution_id": 12345})

    # ISTQB Negative 3: String unix_time and string v2_engine rejected under strict=True
    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"unix_time": "1794373059"})
    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"v2_engine": "true"})

    # ISTQB Negative 4: Float unix_time and integer timestamp_isot rejected under strict=True
    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"unix_time": 1794373059.5})
    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"timestamp_isot": 1794373059})
