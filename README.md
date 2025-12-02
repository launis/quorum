# Cognitive Quorum v2

**Cognitive Quorum** is an advanced, agentic AI system designed to perform rigorous, multi-step cognitive assessments. It utilizes a "System 2" thinking approach, employing a chain of specialized agents to analyze, validate, and grade complex inputs against a hybrid rubric.

## 🚀 Key Features

*   **9-Step Cognitive Workflow**: A sequential assembly line of agents (Guard, Analyst, Logician, Critics, Judge, etc.) ensuring deep analysis.
*   **Hybrid Architecture**: Combines **Mock Mode** (for cost-free testing) and **Production Mode** (Google Gemini API).
*   **Data-Driven Design**: Logic, rules, and prompts are stored as data (`db.json`), allowing dynamic updates without code changes.
*   **XAI Reporting**: Generates Explainable AI reports detailing *why* a certain verdict was reached.
*   **Management UI**: Built-in tools to manage prompts, rules, and system configuration.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd quorum
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    *   Create a `.env` file in the root directory.
    *   Add the following configuration:

    ```env
    # --- Required for Production Mode ---
    GOOGLE_API_KEY=...                 # Your Google Gemini API Key
    
    # --- Optional: Google Search Integration ---
    GOOGLE_SEARCH_API_KEY=...          # Google Custom Search JSON API Key
    GOOGLE_SEARCH_CX=...               # Google Custom Search Engine ID
    
    # --- System Modes ---
    USE_MOCK_LLM=False                       # Set True to use offline mock responses (no API cost)
    USE_MOCK_DB=True                         # Set True to use db_mock.json, False for db.json
    BACKEND_URL=http://localhost:8000        # URL for the FastAPI backend
    ```

    ### Environment Variable Reference

    | Variable | Required | Default | Description |
    | :--- | :---: | :--- | :--- |
    | `GOOGLE_API_KEY` | Yes* | - | Required for Gemini API calls unless `USE_MOCK_LLM=True`. |
    | `USE_MOCK_LLM` | No | `False` | Toggle to `True` to disable real API calls and use cached/mock responses. |
    | `USE_MOCK_DB` | No | `True` | Toggle to `False` to use the production database (`db.json`). |
    | `GOOGLE_SEARCH_API_KEY` | No | - | Required for the *Factual Overseer* agent to perform live web searches. |
    | `GOOGLE_SEARCH_CX` | No | - | Custom Search Engine ID for the *Factual Overseer*. |
    | `BACKEND_URL` | No | `http://localhost:8000` | URL where the frontend looks for the API. |

    ### 🔑 Obtaining API Keys

    1.  **GOOGLE_API_KEY**:
        *   Visit [Google AI Studio](https://aistudio.google.com/).
        *   Create a new API key.
        *   *Required* for the LLM to function (unless `USE_MOCK_LLM=True`).

    2.  **GOOGLE_SEARCH_API_KEY & CX** (Optional):
        *   Required for the *Factual Overseer* agent.
        *   Enable the **Custom Search API** in [Google Cloud Console](https://console.cloud.google.com/).
        *   Create a Search Engine at [Programmable Search Engine](https://programmablesearchengine.google.com/) to get the `CX` ID.

## 🚦 Quick Start

### 1. Start the Backend
The FastAPI backend handles all logic and database interactions.
```bash
./run_locally.bat
```
*Or manually:* `uvicorn backend.main:app --reload`

### 2. Start the Frontend
The Streamlit UI provides the interactive dashboard.
```bash
streamlit run ui.py
```

### 3. View Documentation
Comprehensive documentation is available via MkDocs.
```bash
mkdocs serve
```
Access at: `http://localhost:8000`

## 🔧 API Documentation

The backend exposes a full REST API.
*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`

## 📜 License

[License Information Here]