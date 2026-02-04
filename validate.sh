#!/bin/bash

# Validation script for Python and Flutter projects
# Exits with 0 if all checks pass, 1 otherwise.

EXIT_CODE=0

# Detect project type
if [ -f "pubspec.yaml" ]; then
    echo "Detected Flutter project"
    PROJECT_TYPE="FLUTTER"
elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
    echo "Detected Python project"
    PROJECT_TYPE="PYTHON"
else
    echo "Error: Could not detect project type. Ensure you are in the root of a Python (pyproject.toml/requirements.txt) or Flutter (pubspec.yaml) project."
    exit 1
fi

if [ "$PROJECT_TYPE" = "PYTHON" ]; then
    echo "Running Python checks..."

    # ruff check . --fix (Fail if errors remain)
    echo "[1/3] Running ruff check . --fix"
    ruff check . --fix
    if [ $? -ne 0 ]; then
        echo "❌ Ruff check failed."
        EXIT_CODE=1
    fi

    # mypy . (Fail if type errors found)
    echo "[2/3] Running mypy ."
    mypy .
    if [ $? -ne 0 ]; then
        echo "❌ Mypy check failed."
        EXIT_CODE=1
    fi

    # pytest . (Fail if tests fail)
    echo "[3/3] Running pytest ."
    pytest .
    if [ $? -ne 0 ]; then
        echo "❌ Pytest failed."
        EXIT_CODE=1
    fi

elif [ "$PROJECT_TYPE" = "FLUTTER" ]; then
    echo "Running Flutter checks..."

    # dart format . --set-exit-if-changed (Fail if formatting needed)
    echo "[1/3] Running dart format . --set-exit-if-changed"
    dart format . --set-exit-if-changed
    if [ $? -ne 0 ]; then
        echo "❌ Dart format failed."
        EXIT_CODE=1
    fi

    # dart analyze . (Fail if analysis issues found)
    echo "[2/3] Running dart analyze ."
    dart analyze .
    if [ $? -ne 0 ]; then
        echo "❌ Dart analyze failed."
        EXIT_CODE=1
    fi

    # flutter test (Fail if tests fail)
    echo "[3/3] Running flutter test"
    flutter test
    if [ $? -ne 0 ]; then
        echo "❌ Flutter test failed."
        EXIT_CODE=1
    fi
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "❌ Validation failed."
    exit 1
fi
