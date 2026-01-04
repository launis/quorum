# Cognitive Quorum Test Library

This directory contains the comprehensive test suite for the Cognitive Quorum platform. It includes unit tests, integration tests, and security regression tests.

## 🚀 Quick Start: Test Runners

We provide batch scripts to make running tests easy and reproducible.

### 1. Full Regression Suite (SAFE)
*   **Script**: `tests\run_regression_tests.bat`
*   **Command**: `.\tests\run_regression_tests.bat`
*   **What it does**: Runs **ALL** tests in the library (>45 files).
*   **Mode**:
    *   **LLM**: MOCK (Zero cost, offline).
    *   **DB**: MOCK (Safe, uses temporary DB).
*   **Use Case**: Run this before every commit to ensure you haven't broken anything.

### 2. Live LLM Integration Tests (COSTS MONEY)
*   **Script**: `tests\run_live_tests.bat`
*   **Command**: `.\tests\run_live_tests.bat`
*   **What it does**: Runs specific integration tests that hit the real Vertex AI / Gemini API.
*   **Mode**:
    *   **LLM**: **REAL** (Connects to Google Cloud).
    *   **DB**: MOCK (Safe).
*   **Use Case**: Run this sparingly to verify that the LLM connection and prompt schemas are working correctly.

---

## 📂 Output Logs

To keep your terminal clean, all test runners redirect their output to the `output/` directory:

*   **Regression Logs**: `tests/output/regression_results.txt`
*   **Live Test Logs**: `tests/output/live_test_results.txt`

(Note: This directory is git-ignored, so logs won't pollute your version control.)

---

## 🛠 Manual Execution

You can always run tests manually using `pytest` if you want to target a specific file:

```powershell
# Run a single test file
uv run pytest tests/test_fusion_deep.py

# Run with verbose output
uv run pytest tests/test_iam.py -v
```

## 🧪 Key Test Categories

| File Prefix | Description |
| :--- | :--- |
| `test_api_*.py` | Tests for FastAPI endpoints and routes. |
| `test_fusion_*.py` | Tests for the core Multi-Agent System (Fusion) logic. |
| `test_iam_*.py` | Tests for Identity & Access Management (RBAC). |
| `test_guard_*.py` | Tests for the GuardRails and Safety mechanisms. |
| `test_live_*.py` | **Live** tests requiring real API credentials. |
