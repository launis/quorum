import os
import re

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DART_ENUM_PATH = os.path.join(repo_root, "client_app_v2", "lib", "core", "models", "enums.dart")
PYTHON_V2_CORE_PATH = os.path.join(repo_root, "backend_v2", "models", "v2_core.py")
PYTHON_ENUMS_PATH = os.path.join(repo_root, "backend_v2", "models", "enums.py")
PYTHON_SDUI_PATH = os.path.join(repo_root, "backend_v2", "models", "view", "sdui.py")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_dart_enum_json_values(dart_code: str, enum_name: str) -> set[str]:
    """Extracts all @JsonValue('...') strings for a specific enum."""
    # Find the enum block
    enum_pattern = rf"enum\s+{enum_name}\s+{{(.*?)}}"
    match = re.search(enum_pattern, dart_code, re.DOTALL)
    if not match:
        raise ValueError(f"Enum {enum_name} not found in Dart file.")

    enum_body = match.group(1)

    # Find all @JsonValue('something') mappings
    # Allow single or double quotes
    values = re.findall(r"@JsonValue\(['\"]([^'\"]+)['\"]\)", enum_body)
    return set(values)


def get_python_literal_values(python_code: str, prop_name: str) -> set[str]:
    """Finds a property like preset_view: Literal['A', 'B'] and extracts the values."""
    pattern = rf"{prop_name}:\s*Literal\[([^\]]+)\]"
    match = re.search(pattern, python_code)
    if not match:
        raise ValueError(f"Literal for {prop_name} not found in Python v2_core.py.")

    literal_content = match.group(1)
    values = re.findall(r"['\"]([^'\"]+)['\"]", literal_content)
    return set(values)


def get_python_enum_values(python_code: str, enum_name: str) -> set[str]:
    """Finds an Enum string class like class XaiExtensionType(str, Enum): A = 'a'."""
    enum_pattern = rf"class\s+{enum_name}\s*\(.+?\):\s*(?:\"\"\".*?\"\"\"\s*)?(.+?)(?=\n\nclass |\Z)"
    match = re.search(enum_pattern, python_code, re.DOTALL)
    if not match:
        raise ValueError(f"Enum {enum_name} not found in Python backend enums.py.")

    enum_body = match.group(1)
    values = re.findall(r"^\s*[A-Z0-9_]+\s*=\s*['\"]([^'\"]+)['\"]", enum_body, re.MULTILINE)
    return set(values)


def test_parity_preset_view() -> None:
    """Fail-Fast Check: Asserts Python PresetView Literals equal Dart PresetView Enums."""
    dart_code = read_file(DART_ENUM_PATH)
    py_core_code = read_file(PYTHON_V2_CORE_PATH)

    dart_values = extract_dart_enum_json_values(dart_code, "PresetView")
    py_values = get_python_literal_values(py_core_code, "preset_view")

    missing_in_dart = py_values - dart_values
    missing_in_python = dart_values - py_values

    assert not missing_in_dart, (
        f"CROSS-LANGUAGE PARITY FAILURE: Python allows preset_view {missing_in_dart}"
        " but Dart does not parse it! Add to enums.dart @JsonValue!"
    )
    assert not missing_in_python, (
        f"CROSS-LANGUAGE PARITY FAILURE: Dart defines PresetView {missing_in_python}"
        " but Python does not allow it! Update v2_core.py Literal!"
    )


def test_parity_xai_extensions() -> None:
    """Fail-Fast Check: Asserts Python XaiExtensionType equals Dart XaiExtensionType Enums."""
    dart_code = read_file(DART_ENUM_PATH)
    py_enums_code = read_file(PYTHON_ENUMS_PATH)

    dart_values = extract_dart_enum_json_values(dart_code, "XaiExtensionType")
    py_values = get_python_enum_values(py_enums_code, "XaiExtensionType")

    missing_in_dart = py_values - dart_values
    missing_in_python = dart_values - py_values

    assert not missing_in_dart, (
        f"CROSS-LANGUAGE PARITY FAILURE: The backend throws new XaiExtensionType {missing_in_dart}"
        " but Dart cannot parse it! Update enums.dart!"
    )
    assert not missing_in_python, (
        f"CROSS-LANGUAGE PARITY FAILURE: Dart listens to XaiExtensionType {missing_in_python}"
        " but the backend doesn't know it! Update enums.py!"
    )


PYTHON_SDUI_PATH = os.path.join(repo_root, "backend_v2", "models", "view", "sdui.py")
JINJA_TEMPLATE_PATH = os.path.join(repo_root, "backend_v2", "templates", "report_template.jinja2")


def get_python_sdui_block_types(python_code: str) -> set[str]:
    """Finds all block_type Literal values in SDUI models."""
    values = re.findall(r"block_type:\s*Literal\[['\"]([^'\"]+)['\"]\]", python_code)
    return set(values)


def get_jinja_sdui_block_types(jinja_code: str) -> set[str]:
    """Finds all handled block_type checks in the Jinja template."""
    values = re.findall(r"block\.block_type\s*==\s*['\"]([^'\"]+)['\"]", jinja_code)
    return set(values)


def test_parity_sdui_block_types() -> None:
    """Fail-Fast Check: Asserts Python SDUI block_types exist in Dart and Jinja."""
    dart_code = read_file(DART_ENUM_PATH)
    py_sdui_code = read_file(PYTHON_SDUI_PATH)
    jinja_code = read_file(JINJA_TEMPLATE_PATH)

    py_values = get_python_sdui_block_types(py_sdui_code)
    jinja_values = get_jinja_sdui_block_types(jinja_code)

    try:
        dart_values = extract_dart_enum_json_values(dart_code, "SduiBlockType")
    except ValueError:
        dart_values = set()

    missing_in_dart = py_values - dart_values
    missing_in_python = dart_values - py_values
    missing_in_jinja = py_values - jinja_values

    assert not missing_in_dart, (
        f"CROSS-LANGUAGE PARITY FAILURE: Python allows SDUI block_type {missing_in_dart} "
        "but Dart does not parse it! Add to enums.dart SduiBlockType with @JsonValue!"
    )
    assert not missing_in_python, (
        f"CROSS-LANGUAGE PARITY FAILURE: Dart defines SduiBlockType {missing_in_python} "
        "but Python does not allow it! Update sdui.py Literals!"
    )
    assert not missing_in_jinja, (
        f"CROSS-LANGUAGE PARITY FAILURE: Python allows SDUI block_type {missing_in_jinja} "
        "but PDF jinja template ignores it! Add to render_sdui_blocks in report_template.jinja2!"
    )


def test_parity_visual_intent() -> None:
    """Fail-Fast Check: Asserts Python VisualIntent equals Dart VisualIntent Enums."""
    dart_code = read_file(DART_ENUM_PATH)
    py_enums_code = read_file(PYTHON_ENUMS_PATH)

    dart_values = extract_dart_enum_json_values(dart_code, "VisualIntent")
    py_values = get_python_enum_values(py_enums_code, "VisualIntent")

    missing_in_dart = py_values - dart_values
    missing_in_python = dart_values - py_values

    assert not missing_in_dart, (
        f"CROSS-LANGUAGE PARITY FAILURE: The backend throws new VisualIntent {missing_in_dart}"
        " but Dart cannot parse it! Update enums.dart!"
    )
    assert not missing_in_python, (
        f"CROSS-LANGUAGE PARITY FAILURE: Dart listens to VisualIntent {missing_in_python}"
        " but the backend doesn't know it! Update enums.py!"
    )
