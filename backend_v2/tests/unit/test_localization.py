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
def reset_localization_service():
    """Reset the service state before each test."""
    original_dir = LocalizationService.L10N_DIR
    LocalizationService._loaded = False
    LocalizationService._translations = {}
    yield
    LocalizationService._loaded = False
    LocalizationService._translations = {}
    LocalizationService.L10N_DIR = original_dir


def test_set_and_get_language():
    set_language("fi")
    assert get_language() == "fi"


def test_load_if_needed_success(tmp_path: Path):
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


def test_load_if_needed_missing_dir():
    LocalizationService.L10N_DIR = Path("/does/not/exist/l10n")
    with pytest.raises(AppException) as exc_info:
        LocalizationService.load_if_needed()
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


def test_load_if_needed_no_files(tmp_path: Path):
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    
    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.load_if_needed()
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


def test_load_if_needed_corrupt_json(tmp_path: Path):
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text("invalid json", encoding="utf-8")
    
    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.load_if_needed()
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


def test_translate_success(tmp_path: Path):
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


def test_translate_fallback_to_en(tmp_path: Path):
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"only_en": "English only"}), encoding="utf-8")
    (l10n_dir / "fi.json").write_text(json.dumps({"hello": "Hei"}), encoding="utf-8")
    
    LocalizationService.L10N_DIR = l10n_dir
    assert LocalizationService.translate("only_en", lang="fi") == "English only"


def test_translate_missing_key(tmp_path: Path):
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"hello": "Hello"}), encoding="utf-8")
    
    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.translate("missing_key", lang="en")
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


def test_translate_missing_interpolation_arg(tmp_path: Path):
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"greeting": "Hello {name} {age}"}), encoding="utf-8")
    
    LocalizationService.L10N_DIR = l10n_dir
    with pytest.raises(AppException) as exc_info:
        LocalizationService.translate("greeting", lang="en", name="John")
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
    assert exc_info.value.details["missing_arg"] == "age"


def test_get_alias(tmp_path: Path):
    l10n_dir = tmp_path / "l10n"
    l10n_dir.mkdir()
    (l10n_dir / "en.json").write_text(json.dumps({"greeting": "Hello"}), encoding="utf-8")
    
    LocalizationService.L10N_DIR = l10n_dir
    assert LocalizationService.get("greeting", lang="en") == "Hello"
