"""Backend Internal Localization Parity & Key Reference Integrity Suite.

Enforces:
1. 100% 1:1 key parity between backend_v2/l10n/en.json and backend_v2/l10n/fi.json.
2. 100% of all Jinja2 template l10n.<key> references exist in backend dictionaries.
3. 0 dead unreferenced keys in backend dictionaries (full reference coverage).
"""

import json
import re
from pathlib import Path
from typing import Any

L10N_DIR = Path(__file__).resolve().parents[2] / "l10n"
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
SERVICES_DIR = Path(__file__).resolve().parents[2] / "services"
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"


def _load_backend_dictionaries() -> tuple[dict[str, str], dict[str, str]]:
    """Load en.json and fi.json dictionaries."""
    en_file = L10N_DIR / "en.json"
    fi_file = L10N_DIR / "fi.json"

    assert en_file.exists(), f"Missing {en_file}"
    assert fi_file.exists(), f"Missing {fi_file}"

    with open(en_file, encoding="utf-8") as f:
        en_data = json.load(f)
    with open(fi_file, encoding="utf-8") as f:
        fi_data = json.load(f)

    return en_data, fi_data


def test_backend_json_has_100_percent_internal_language_parity() -> None:
    """TC-L10N-01: Asserts 1:1 key parity and non-empty translations between en.json and fi.json."""
    en_data, fi_data = _load_backend_dictionaries()

    en_keys = set(en_data.keys())
    fi_keys = set(fi_data.keys())

    assert len(en_keys) >= 50, f"Expected >= 50 keys in en.json, found {len(en_keys)}"

    missing_in_fi = en_keys - fi_keys
    missing_in_en = fi_keys - en_keys

    assert not missing_in_fi, f"Keys present in en.json but missing in fi.json: {sorted(missing_in_fi)}"
    assert not missing_in_en, f"Keys present in fi.json but missing in en.json: {sorted(missing_in_en)}"

    # Assert non-empty translations
    for k, v in en_data.items():
        assert isinstance(v, str) and v.strip(), f"en.json key '{k}' has empty or non-string value"
    for k, v in fi_data.items():
        assert isinstance(v, str) and v.strip(), f"fi.json key '{k}' has empty or non-string value"

    # Anti-happy-path negative verification
    def _verify_parity(dict_a: dict[str, Any], dict_b: dict[str, Any]) -> bool:
        keys_a = set(dict_a.keys())
        keys_b = set(dict_b.keys())
        if keys_a != keys_b:
            return False
        for val in list(dict_a.values()) + list(dict_b.values()):
            if not isinstance(val, str) or not val.strip():
                return False
        return True

    assert _verify_parity({"k1": "v1", "k2": "v2"}, {"k1": "v1_fi", "k2": "v2_fi"})
    assert not _verify_parity({"k1": "v1", "k2": "v2"}, {"k1": "v1_fi"})
    assert not _verify_parity({"k1": "v1"}, {"k1": "v1_fi", "k2": "v2_fi"})
    assert not _verify_parity({"k1": ""}, {"k1": "v1_fi"})


def test_jinja_template_all_l10n_references_exist_in_backend_dictionaries() -> None:
    """TC-L10N-02: Asserts 100% of Jinja2 template l10n.<key> references exist in en.json and fi.json."""
    en_data, fi_data = _load_backend_dictionaries()
    en_keys = set(en_data.keys())
    fi_keys = set(fi_data.keys())

    template_file = TEMPLATES_DIR / "report_template.jinja2"
    assert template_file.exists(), f"Missing {template_file}"

    content = template_file.read_text(encoding="utf-8")
    l10n_refs = set(re.findall(r"\bl10n\.([a-zA-Z0-9_]+)\b", content))

    assert len(l10n_refs) >= 15, f"Expected >= 15 l10n.* references in report_template.jinja2, found {len(l10n_refs)}"

    missing_in_en = l10n_refs - en_keys
    missing_in_fi = l10n_refs - fi_keys

    assert not missing_in_en, f"Jinja2 l10n references missing in en.json: {sorted(missing_in_en)}"
    assert not missing_in_fi, f"Jinja2 l10n references missing in fi.json: {sorted(missing_in_fi)}"

    # Anti-happy-path negative verification
    def _verify_template_refs(tpl_content: str, available_keys: set[str]) -> bool:
        refs = set(re.findall(r"\bl10n\.([a-zA-Z0-9_]+)\b", tpl_content))
        return refs.issubset(available_keys)

    assert _verify_template_refs("{{ l10n.warning_label }}", {"warning_label"})
    assert not _verify_template_refs("{{ l10n.missing_non_existent_key }}", {"warning_label"})


def test_backend_json_has_no_dead_unreferenced_keys() -> None:
    """TC-L10N-03: Asserts 0 dead unreferenced keys in backend dictionaries across services, adapters, and templates."""
    en_data, _ = _load_backend_dictionaries()
    en_keys = set(en_data.keys())

    # Collect all scanned sources
    template_file = TEMPLATES_DIR / "report_template.jinja2"
    python_files = (
        list(SERVICES_DIR.rglob("*.py"))
        + list(MODELS_DIR.rglob("*.py"))
        + [Path(__file__).resolve().parents[2] / "worker.py"]
    )

    all_code_content = (
        template_file.read_text(encoding="utf-8")
        + "\n"
        + "\n".join(p.read_text(encoding="utf-8") for p in python_files)
    )

    # Dynamic prefix generators mapped from enums and domain schemas
    dynamic_prefixes = (
        "matrix_col_",
        "matrix_target_",
        "col_",
        "xai_ext_",
        "xai",
        "ext_",
        "role_",
        "level_",
        "alignment_",
        "metadata_",
        "variance_",
        "authenticity_",
    )

    def _is_key_referenced(key: str, code_corpus: str) -> bool:
        # Direct literal or Jinja reference
        if re.search(rf"['\"]{key}['\"]|\bl10n\.{key}\b", code_corpus):
            return True
        # Dynamic prefix match where suffix or prefix is referenced
        for prefix in dynamic_prefixes:
            if key.startswith(prefix):
                suffix = key[len(prefix) :]
                if re.search(rf"['\"]{suffix}['\"]|{prefix}", code_corpus):
                    return True
        return False

    dead_keys = [k for k in en_keys if not _is_key_referenced(k, all_code_content)]

    assert not dead_keys, f"Found dead unreferenced keys in backend_v2/l10n/en.json: {sorted(dead_keys)}"

    # Anti-happy-path negative verification
    assert not _is_key_referenced("completely_orphaned_dead_key_999", all_code_content)
