# Cognitive Quorum v2


![Build Status](https://img.shields.io/badge/build-passing-brightgreen)


![Python Version](https://img.shields.io/badge/python-3.9+-blue)


![License](https://img.shields.io/badge/license-MIT-informational)


Cognitive Quorum is a highly configurable, data-driven engine for creating and executing complex agentic AI workflows. It orchestrates a sequence of specialized AI agents to perform rigorous, multi-step analysis and evaluation tasks. The system's core logic, including agent responsibilities, prompts, and operational rules, is externalized to a database, allowing for dynamic workflow modifications without altering the underlying code.

---

## Table of Contents

- [✨ Key Features](#-key-features)
- [🏛️ Architecture Overview](#️-architecture-overview)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
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

*   **Dynamic Agentic Workflows**: Define complex, multi-step agent "assembly lines" through simple JSON configuration. The number of steps, agent roles, and their sequence are not hardcoded.
*   **Data-Centric Design**: Core system logic, prompts, and validation rules are stored as data (`db.json`). This allows for rapid iteration and adaptation of the system's cognitive processes without code changes.
*   **Dual Execution Modes**:
    *   **Production Mode**: Utilizes the Google Gemini API for state-of-the-art analysis.
    *   **Mock Mode**: A cost-free, offline mode that uses pre-recorded responses for testing, development, and debugging.
*   **Explainable AI (XAI) Reporting**: Generates detailed reports that trace the decision-making process through each agent, providing clear justification for the final verdict.
*   **Integrated Management UI**: A Streamlit-based user interface for managing prompts, rules, system configuration, and viewing workflow results.

## 🏛️ Architecture Overview

Cognitive Quorum operates as a generic workflow engine. Its behavior is not predefined in code but is instead dictated by a configuration loaded from a database (`db.json` or `db_mock.json`).

1.  **Workflow Definition**: A workflow is defined as a sequence of "steps" in the database.
2.  **Agent Instantiation**: For each step, the engine instantiates a generic agent.
3.  **Data-Driven Behavior**: The agent's specific role, instructions (prompt), and tools are loaded from the database entry corresponding to that step.
4.  **Sequential Execution**: An input is passed through this dynamically constructed chain of agents, with the output of one agent becoming the input for the next.

This decoupled architecture makes the system extremely flexible, allowing it to be reconfigured for entirely different cognitive tasks by simply changing the data it consumes.

## 🚀 Getting Started

### Prerequisites

*   Python 3.9+
*   Git
*   `pip` package manager

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd cognitive-quorum-v2 # or your repository directory name
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**
    Create a file named `.env` in the root directory of the project. Copy the contents of `.env.example` (if provided) or use the template below.

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

# For PowerShell
./run_locally.ps1
```

For manual startup in separate terminals:

```bash
# Terminal 1: Start the Backend API
uvicorn backend.main:app --reload

# Terminal 2: Start the Frontend UI
streamlit run ui.py
```

### Accessing the Services

Once running, the following services will be available:

*   **Frontend UI**: `http://localhost:8501`
*   **Backend API Docs**: `http://localhost:8000/docs`

## ⚙️ Configuration

System behavior is controlled by environment variables in the `.env` file.

| Variable                | Description                                                                                              | Default   |
| ----------------------- | -------------------------------------------------------------------------------------------------------- | --------- |
| `GOOGLE_API_KEY`        | **Required for Production.** Your API key for Google Gemini.                                             | `None`    |
| `GOOGLE_SEARCH_API_KEY` | **Required for Production.** Your API key for the Google Custom Search JSON API.                         | `None`    |
| `GOOGLE_SEARCH_CX`      | **Required for Production.** Your Programmable Search Engine ID.                                         | `None`    |
| `USE_MOCK_LLM`          | If `True`, the system uses pre-recorded responses from `mock_responses.json` instead of calling the LLM. | `False`   |
| `USE_MOCK_DB`           | If `True`, the system loads its configuration from `db_mock.json` instead of the primary `db.json`.        | `True`    |

## 🛠️ Development

### API Documentation

The backend exposes a full REST API with interactive documentation.

*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`

### Project Structure

A high-level overview of the key directories:

```
├── backend/            # FastAPI backend application, agent logic, and API routers
├── data/               # Data files, including db.json, mock data, and uploads
├── docs/               # MkDocs documentation source files
├── scripts/            # Helper and utility scripts for development and data management
├── src/                # Core engine logic, database clients, and component registries
├── tests/              # Pytest integration and unit tests
├── ui.py               # Main Streamlit frontend application file
├── docker-compose.yml  # Docker configuration for containerized deployment
└── requirements.txt    # Python package dependencies
```

### Running Tests

To run the full suite of integration and unit tests, use `pytest`.

```bash
pytest
```

### Building Documentation

The project uses MkDocs for comprehensive documentation.

```bash
mkdocs serve
```
The documentation site will be available at `http://localhost:8000`.

## 📜 License

This project is licensed under the [Your License Here] License - see the `LICENSE` file for details.