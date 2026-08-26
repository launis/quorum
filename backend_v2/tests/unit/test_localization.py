import json
from pathlib import Path

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.localization import (
    LocalizationService,
    get_language,
    set_language,
)


@pytest.fixture(autouse=True)
def reset_localization_service() -> None:  # type: ignore
    """Reset the service state before each test."""
    original_dir = LocalizationService.L10N_DIR
    LocalizationService._loaded = False
    LocalizationService._translations = {}
    yield
    LocalizationService._loaded = False
    LocalizationService._translations = {}
    LocalizationService.L10N_DIR = original_dir


def test_set_and_get_language() -> None:
    set_language("fi")
    assert get_language() == "fi"


def test_load_if_needed_success(tmp_path: Path) -> None:
    # Mock the directory
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()

    # Create en.json and fi.json
    (l10n_dir / "en.json").write_text(json.dumps({"hello": "Hello"}), encoding="utf-8")
    (l10n_dir / "fi.json").write_text(json.dumps({"hello": "Hei"}), encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir
    LocalizationService.load_if_needed()

    assert LocalizationService._loaded is True
    assert "en" in LocalizationService._translations
    assert "fi" in LocalizationService._translations
    assert LocalizationService._translations["fi"]["hello"] == "Hei"


def test_load_if_needed_missing_dir() -> None:
    LocalizationService.L10N_DIR = Path("/does/not/exist/l10n")
    with pytest.raises(AppException) as exc_info:
        LocalizationService.load_if_needed()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


def test_load_if_needed_no_files(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()

    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.load_if_needed()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


def test_load_if_needed_corrupt_json(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text("invalid json", encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.load_if_needed()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


def test_translate_success(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"greeting": "Hello {name}"}), encoding="utf-8")
    (l10n_dir / "fi.json").write_text(json.dumps({"greeting": "Hei {name}"}), encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir

    # Test direct lang
    assert LocalizationService.translate("greeting", lang="fi", name="Matti") == "Hei Matti"

    # Test context lang
    set_language("en")
    assert LocalizationService.translate("greeting", name="John") == "Hello John"


def test_translate_fallback_to_en(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"only_en": "English only"}), encoding="utf-8")
    (l10n_dir / "fi.json").write_text(json.dumps({"hello": "Hei"}), encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir
    assert LocalizationService.translate("only_en", lang="fi") == "English only"


def test_translate_missing_key(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"hello": "Hello"}), encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.translate("missing_key", lang="en")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


def test_translate_missing_interpolation_arg(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"greeting": "Hello {name} {age}"}), encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.translate("greeting", lang="en", name="John")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
    assert exc_info.value.details["missing_arg"] == "age"


def test_get_alias(tmp_path: Path) -> None:
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"greeting": "Hello"}), encoding="utf-8")

    LocalizationService.L10N_DIR = l10n_dir
    assert LocalizationService.get("greeting", lang="en") == "Hello"


def test_localization_service_translate_and_formatting() -> None:
    # Use real repository l10n files
    LocalizationService.L10N_DIR = Path(__file__).parent.parent.parent / "l10n"
    LocalizationService.load_if_needed()

    assert LocalizationService.translate("metadata_user", "fi") == "Käyttäjä"
    assert LocalizationService.translate("metadata_user", "en") == "User"
    assert LocalizationService.translate("role_architect", "fi") == "Arkkitehti"
    assert LocalizationService.translate("role_architect", "en") == "Architect"
    assert LocalizationService.translate("col_quotes", "fi") == "Lainaukset"
    assert LocalizationService.translate("col_quotes", "en") == "Quotes"
    assert LocalizationService.translate("ext_variance_validation", "fi") == "Varianssin validointi"
    assert LocalizationService.translate("ext_variance_validation", "en") == "Variance Validation"

    # Formatting helpers
    from datetime import datetime

    dt = datetime(2026, 8, 26, 6, 44)
    assert LocalizationService.format_date(dt, "fi") == "26.08.2026 klo 06:44"
    assert LocalizationService.format_date(dt, "en") == "2026-08-26 06:44"

    assert LocalizationService.format_decimal(3.5, "fi") == "3,50"
    assert LocalizationService.format_decimal(3.5, "en") == "3.50"
    assert LocalizationService.format_decimal(3.546, "fi", decimals=1) == "3,5"

    assert LocalizationService.format_score(3.5, "fi") == "3,50"
    assert LocalizationService.format_score(3.5, "en") == "3.50"

    assert LocalizationService.format_percent(85.2, "fi") == "85,2 %"
    assert LocalizationService.format_percent(85.2, "en") == "85.2%"

    assert LocalizationService.format_cost(12.5, "fi") == "12,50 $"
    assert LocalizationService.format_cost(12.5, "en") == "$12.50"
    assert LocalizationService.format_cost(0.04, "fi") == "0,04 $"
    assert LocalizationService.format_cost(0.04, "en") == "$0.04"
