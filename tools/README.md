# Quorum Tools & Utilities

This directory contains utility scripts, maintenance tools, and legacy runners for the Cognitive Quorum platform.

## 🏃 Legacy Runners (Moved from Root)

To keep the root directory clean, specialized runners have been moved here.

*   **`run_firestore.bat`**: Seeds/Runs the Firestore integration.
*   **`run_worker.bat` / `.ps1`**: Starts a specialized background worker (Arq/Redis).
*   **`setup_env.bat`**: Helper to initialize the environment variables.
*   **`start.bat`**: Legacy entry point.

## 🛠 Maintenance Tools

*   **`inspect_db.py`**: Dump Tinydb contents for debugging.
*   **`probe_model_availability.py`**: Check Vertex AI region status.
*   **`verify_refactor.py`**: Validates codebase structure against Pydantic V2 standards.
