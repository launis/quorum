# Cognitive Quorum - Dynamic Workflow Engine (v2)

**Cognitive Quorum** is an advanced, data-driven workflow engine designed for complex, multi-agent AI assessments. It orchestrates interactions between Large Language Models (LLMs) and deterministic code (Python Hooks) to produce high-quality, verifiable, and transparent results.

## 🚀 Key Features

*   **Generic Workflow Engine**: A single, agnostic engine executes any workflow defined in the database. No hardcoded agent logic.
*   **Hybrid Architecture**: Seamlessly combines:
    *   **LLMs** (Google Gemini, OpenAI GPT-4) for reasoning and generation.
    *   **Python Hooks** for deterministic tasks (Math, Parsing, Search, RAG).
*   **Data-Driven Logic**: All Rules, Prompts, Steps, and Workflows are stored in a JSON-based database (`seed_data.json`), allowing for easy modification without code changes.
*   **Registry Pattern**: Dynamic mapping of string identifiers to Pydantic models (`SchemaRegistry`) and Python functions (`HookRegistry`).
*   **Reliability & Robustness**:
    *   **UTF-8 Everywhere**: Full support for Scandinavian characters in database, logs, and LLM calls.
    *   **Error Fallback**: Automatic retry logic and model switching (e.g., Gemini Flash -> Pro) on failure.
*   **Adversarial Testing**: Built-in test suite (`run_scenarios.py`) for simulating rule violations (Prompt Injection, PII Leaks) and technical errors.
*   **External Integrations**:
    *   **Google Custom Search API** for real-time fact-checking.
    *   **RAG (Retrieval-Augmented Generation)** stub for document context.
*   **Transparency & XAI**: Full traceability of inputs, outputs, and citations. Generates detailed XAI reports with uncertainty quantification.

## 🏗️ Architecture

The system follows a modern **Cloud Native** architecture, designed for scalability on Google Cloud Platform:

```
backend/                # FastAPI Backend (REST API)
│   ├── api/            # API Endpoints (Orchestrator, DB, LLM)
│   ├── agents/         # AI Agents (Guard, Analyst, Judge, etc.)
│   ├── engine.py       # Generic Orchestrator & Executor
│   ├── component.py    # Base Component Class
│   └── main.py         # App Entry Point
data/                   # Data Storage
│   ├── seed_data.json  # Initial Database State
│   └── templates/      # Jinja2 Prompts
ui.py                   # Streamlit Frontend
```

*   **Backend (FastAPI)**: Handles all business logic, workflow execution, and database interactions.
*   **Frontend (Streamlit)**: A lightweight UI that consumes the REST API.
*   **Database**: Supports **Google Cloud Firestore** (Production) and **TinyDB** (Local Development).
*   **Storage**: Supports **Google Cloud Storage** and local file system.

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.10+
*   API Keys for Google Gemini, OpenAI, and Google Custom Search.

### 1. Clone the Repository
```bash
git clone https://github.com/launis/quorum.git
cd quorum
```

### 2. Configure Secrets
Create a `.env` file in the root directory with your API keys:
```env
GOOGLE_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
GOOGLE_SEARCH_API_KEY=your_search_key
GOOGLE_SEARCH_CX=your_search_cx
# Optional: Set for Cloud Mode
# GOOGLE_CLOUD_PROJECT=your_project_id
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🖥️ Usage

### Running Locally (Recommended)
We provide a helper script to start both the Backend and Frontend simultaneously:

**Windows:**
```bash
run_locally.bat
```

**Manual Start:**
1. **Backend**: `uvicorn src.api.server:app --reload --port 8000`
2. **Frontend**: `streamlit run ui.py`

### Workflow Selection
1.  **Select Workflow**: The primary workflow is **`WORKFLOW_MAIN`**, which implements the full 9-step assessment process (Guard -> Analyst -> Logician -> Critics -> Judge -> XAI).
2.  **Upload Evidence**: Upload PDF/Text files for History, Product, and Reflection.
3.  **Run Assessment**: Click the button to start the asynchronous job.
4.  **View Results**: The UI polls the backend and displays the final XAI report.

## 📚 Documentation
Full documentation is available in the `docs/` directory.

### 📖 Viewing Documentation

**Option 1: Online (GitHub Pages)**
[View Documentation](https://github.com/launis/quorum)

**Option 2: Local Server**
To view the documentation locally with live reloading:
```bash
mkdocs serve -a localhost:8001
```
Then open [http://localhost:8001](http://localhost:8001) in your browser.

## 📄 License
[MIT License](LICENSE)
