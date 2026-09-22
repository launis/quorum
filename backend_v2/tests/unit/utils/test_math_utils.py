import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import AppException, MissingInputMappingError
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.utils.math_utils import (
    calculate_linear_ratio_score,
    calculate_scaled_score,
    clamp_score,
    normalize_score_to_100,
    resolve_dot_notation,
    scale_to_custom_range,
)


def test_normalize_score_to_100() -> None:
    """Test proportional normalization math."""
    assert normalize_score_to_100(3.0, 1.0, 5.0) == 50.0
    assert normalize_score_to_100(5.0, 1.0, 5.0) == 100.0
    assert normalize_score_to_100(0.0, 1.0, 5.0) == 0.0
    with pytest.raises(AppException):
        normalize_score_to_100(3.0, 5.0, 1.0)


def test_calculate_scaled_score() -> None:
    """Test absolute scaled score bounds."""
    assert calculate_scaled_score(3.0, 5, 1.0, 5.0) == 3.0
    assert calculate_scaled_score(6.0, 5, 1.0, 5.0) == 5.0
    assert calculate_scaled_score(0.0, 5, 1.0, 5.0) == 1.0
    with pytest.raises(AppException):
        calculate_scaled_score(3.0, 5, 5.0, 1.0)


def test_scale_to_custom_range() -> None:
    """Test linear custom range scaling."""
    assert scale_to_custom_range(3.0, 1.0, 5.0, 4.0, 10.0) == 7.0
    assert scale_to_custom_range(5.0, 1.0, 5.0, 4.0, 10.0) == 10.0
    assert scale_to_custom_range(0.0, 1.0, 5.0, 4.0, 10.0) == 4.0
    with pytest.raises(AppException):
        scale_to_custom_range(3.0, 5.0, 1.0, 4.0, 10.0)


def test_clamp_score() -> None:
    """Test clamping within, below, and above bounds."""
    assert clamp_score(3.0, 1.0, 5.0) == 3.0
    assert clamp_score(0.5, 1.0, 5.0) == 1.0
    assert clamp_score(5.5, 1.0, 5.0) == 5.0


def test_clamp_score_invalid_scale() -> None:
    """Test clamping with invalid mathematical scale bounds."""
    with pytest.raises(AppException):
        clamp_score(3.0, 5.0, 1.0)


def test_calculate_linear_ratio_score() -> None:
    """Test weighted average calculation across scale levels."""
    stats = {
        1.0: LevelStatsDTO(hits=100, total=100),
        2.0: LevelStatsDTO(hits=50, total=100),
    }
    score = calculate_linear_ratio_score(stats, 1.0, 5.0)
    assert score > 1.0

    with pytest.raises(AppException):
        calculate_linear_ratio_score(stats, 5.0, 1.0)

    # 0 max weights
    stats_empty = {
        1.0: LevelStatsDTO(hits=0, total=0),
    }
    assert calculate_linear_ratio_score(stats_empty, 1.0, 5.0) == 1.0


def test_resolve_dot_notation_dict() -> None:
    state = {"user": {"profile": {"age": 30}}}
    assert resolve_dot_notation(state, "user.profile.age") == 30


def test_resolve_dot_notation_object() -> None:
    class Profile:
        age = 30

    class User:
        profile = Profile()

    class State:
        user = User()

    state = State()
    assert resolve_dot_notation(state, "user.profile.age") == 30


def test_resolve_dot_notation_list() -> None:
    state = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    assert resolve_dot_notation(state, "users.1.name") == "Bob"


def test_resolve_dot_notation_missing_dict_key() -> None:
    state: dict[str, object] = {"user": {}}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.profile.age")
    assert "Failed at 'profile': KeyError" in exc_info.value.details["reason"]
    assert exc_info.value.status_code == 400


def test_resolve_dot_notation_missing_attribute() -> None:
    class User:
        pass

    state = {"user": User()}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "user.profile.age")
    assert "Failed at 'profile': AttributeError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_missing_index() -> None:
    state: dict[str, list[object]] = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.0")
    assert "Failed at '0': IndexError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_invalid_list_index() -> None:
    state: dict[str, list[object]] = {"users": []}
    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state, "users.not_an_int")
    assert "Failed at 'not_an_int': ValueError" in exc_info.value.details["reason"]


def test_resolve_dot_notation_empty_path() -> None:
    state = {"a": 1}
    assert resolve_dot_notation(state, "") == state


def test_math_utils_resolve_dot_notation_base_model_without_dict() -> None:
    """Test contract 4: BaseModel instance queried via dot-notation path resolves attribute via object.__getattribute__ with zero __dict__ reflection."""

    class SampleModel(BaseModel):
        name: str
        score: float

        model_config = ConfigDict(extra="forbid", strict=True)

    model = SampleModel(name="Alpha", score=95.5)
    assert resolve_dot_notation(model, "name") == "Alpha"
    assert resolve_dot_notation(model, "score") == 95.5

    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(model, "missing_field")
    assert "Failed at 'missing_field': KeyError" in exc_info.value.details["reason"]
