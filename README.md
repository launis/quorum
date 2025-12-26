# Cognitive Quorum v2


![Build Status](https://img.shields.io/badge/build-passing-brightgreen)


![Python Version](https://img.shields.io/badge/python-3.9+-blue)


![License](https://img.shields.io/badge/license-MIT-informational)


Cognitive Quorum is a highly configurable, data-driven engine for creating and executing complex AI agent workflows. It orchestrates sequences of specialized AI agents to perform rigorous, multi-step analysis and evaluation tasks. The system's core logic—including agent responsibilities, prompts, and operational rules—is externalized to a database, allowing for dynamic workflow modifications without altering the underlying code.

---

## Table of Contents

- [✨ Key Features](#-key-features)
- [🏛️ Architecture Overview](#️-architecture-overview)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [🚦 Usage](#-usage)
  - [Running the System](#running-the-system)
  - [Accessing the Services](#accessing-the-services)
- [⚙️ Configuration](#️-configuration)
- [🛠️ Development](#️-development)
  - [API Documentation](#api-documentation)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
  - [Building Documentation](#building-documentation)
- [📜 License](#-license)

## ✨ Key Features

*   **Data-Driven Workflow Engine**: Define complex, multi-step agent "assembly lines" through simple JSON configuration. The number of steps, agent roles, and their sequence are not hardcoded.
*   **Externalized Logic**: Core system behavior, prompts, and validation rules are stored as data (`db.json`). This allows for rapid iteration and adaptation of the system's cognitive processes without code changes.
*   **Dual Execution Modes**:
    *   **Production Mode**: Utilizes the Google Gemini API for state-of-the-art analysis.
    *   **Mock Mode**: A cost-free, offline mode that uses pre-recorded responses for testing, development, and debugging.
*   **Transparent & Auditable**: Generates detailed reports that trace the decision-making process through each agent, providing clear justification for the final verdict.
*   **Integrated Management UI**: A Streamlit-based user interface for managing prompts, rules, system configuration, and viewing workflow results.
*   **Fused Critics Workflow (Courtroom 3.0)**: An optimized workflow that fuses multiple critic roles (Logician, Falsifier, Causal Analyst) into a single `PanelAgent` step, reducing latency and cost while maintaining rigorous multi-perspective analysis.

## 🏛️ Architecture Overview

Cognitive Quorum operates as a generic workflow engine. Its behavior is not predefined in code but is instead dictated by a configuration loaded from a database (`db.json`).

The execution flow is as follows:

1.  **Workflow Definition**: The engine loads a workflow, which is defined as an ordered sequence of "steps" in the database.
2.  **Agent Instantiation**: For each step in the sequence, the engine instantiates a generic agent.
3.  **Data-Driven Behavior**: The agent's specific role, instructions (prompt), and available tools are loaded from the database entry corresponding to that step.
4.  **Sequential Execution**: An input is passed through this dynamically constructed chain of agents. The output of one agent becomes the input for the next, forming a "cognitive assembly line."

This decoupled architecture makes the system extremely flexible, allowing it to be reconfigured for entirely different cognitive tasks by simply changing the data it consumes.

## 🚀 Getting Started

### Prerequisites

*   Python 3.9+
*   Git
*   `pip` package manager

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/cognitive-quorum-v2.git
    cd cognitive-quorum-v2
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**
    Create a `.env` file in the project root by copying the example file.

    ```bash
    cp .env.example .env
    ```

    Now, edit the `.env` file and add your API keys.

    ```env
    # --- Required for Production Mode ---
    GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
    GOOGLE_SEARCH_API_KEY="YOUR_GOOGLE_SEARCH_API_KEY"
    GOOGLE_SEARCH_CX="YOUR_GOOGLE_SEARCH_ENGINE_ID"

    # --- System Configuration ---
    # Set to 'True' to use offline mock responses (no API cost)
    USE_MOCK_LLM=False
    # Set to 'True' to use the mock database (db_mock.json)
    USE_MOCK_DB=True
    ```

## 🚦 Usage

### Running the System

A convenience script is provided to launch both the backend API and the frontend UI simultaneously.

```bash
# For Windows
./run_locally.bat

# For PowerShell / Linux / macOS
./run_locally.ps1
```

Alternatively, you can run the services manually in separate terminals.

```bash
# Terminal 1: Start the Backend API
uvicorn backend.main:app --reload
```

```bash
# Terminal 2: Start the Frontend UI
streamlit run ui.py
```

### Accessing the Services

Once running, the services will be available at the following local addresses:

*   **Frontend UI**: `http://localhost:8501`
*   **Backend API Docs**: `http://localhost:8000/docs`

## ⚙️ Configuration

System behavior is controlled by environment variables in the `.env` file.

| Variable                | Description                                                                                              | Default   |
| ----------------------- | -------------------------------------------------------------------------------------------------------- | --------- |
| `GOOGLE_API_KEY`        | **Required for Production.** API key for Google Gemini.                                                  | `None`    |
| `GOOGLE_SEARCH_API_KEY` | **Required for Production.** API key for the Google Custom Search JSON API.                              | `None`    |
| `GOOGLE_SEARCH_CX`      | **Required for Production.** Your Programmable Search Engine ID.                                         | `None`    |
| `USE_MOCK_LLM`          | If `True`, the system uses pre-recorded responses from `mock_responses.json` instead of calling the LLM. | `False`   |
| `USE_MOCK_DB`           | If `True`, the system loads its configuration from `db_mock.json` instead of the primary `db.json`.        | `True`    |

### Database Management

The system uses `TinyDB` for configuration storage. The database file used depends on the `USE_MOCK_DB` setting in `.env`.

*   **Mock DB**: `backend/database/db_mock.json` (Default)
*   **Production DB**: `data/db.json`

If you modify `backend/database/seed_data.json` to update prompts, workflows, or rules, you **MUST** rebuild the active database for changes to take effect.

**To rebuild the Production Database:**
```bash
python rebuild_prod_db.py
```

**To rebuild the Mock Database:**
```bash
python rebuild_mock_db.py
```

## 🛠️ Development

### API Documentation

The backend exposes a full REST API with interactive documentation generated via FastAPI.

*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`

### Project Structure

```
.
├── backend/            # FastAPI backend application, agent logic, and API routers
├── data/               # Data files, including db.json, mock data, and uploads
├── docs/               # MkDocs documentation source files
├── scripts/            # Helper and utility scripts
├── src/                # Core engine logic, database clients, and components
├── tests/              # Pytest integration and unit tests
├── .env.example        # Example environment variables file
├── docker-compose.yml  # Docker configuration for containerized deployment
├── requirements.txt    # Python package dependencies
└── ui.py               # Main Streamlit frontend application file
```

### Running Tests

The project uses `pytest` for unit and integration testing.

```bash
pytest
```

### Building Documentation

The project uses MkDocs for documentation. To serve the documentation site locally:

```bash
# Serve the docs on a different port to avoid conflict with the API
mkdocs serve --dev-addr localhost:8001
```
The documentation site will be available at `http://localhost:8001`.

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.