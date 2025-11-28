# Cognitive Quorum - Dynamic Workflow Engine (v2)

**Cognitive Quorum** is an advanced, data-driven workflow engine designed for complex, multi-agent AI assessments. It orchestrates interactions between Large Language Models (LLMs) and deterministic code (Python Hooks) to produce high-quality, verifiable, and transparent results.

## 🚀 Key Features

*   **Generic Workflow Engine**: A single, agnostic engine executes any workflow defined in the database. No hardcoded agent logic.
*   **Hybrid Architecture**: Seamlessly combines:
    *   **LLMs** (Google Gemini, OpenAI GPT-4) for reasoning and generation.
    *   **Python Hooks** for deterministic tasks (Math, Parsing, Search, RAG).
*   **Data-Driven Logic**: All Rules, Prompts, Steps, and Workflows are stored in a JSON-based database (`seed_data.json`), allowing for easy modification without code changes.
*   **Registry Pattern**: Dynamic mapping of string identifiers to Pydantic models (`SchemaRegistry`) and Python functions (`HookRegistry`).
*   **External Integrations**:
    *   **Google Custom Search API** for real-time fact-checking.
    *   **RAG (Retrieval-Augmented Generation)** stub for document context.
*   **Transparency & XAI**: Full traceability of inputs, outputs, and citations. Generates detailed XAI reports with uncertainty quantification.

## 🏗️ Architecture

The system follows a modern **Cloud Native** architecture, designed for scalability on Google Cloud Platform:

```
src/
├── api/                # FastAPI Backend (REST API)
│   ├── routers/        # API Endpoints (Orchestrator, DB, LLM)
│   └── server.py       # App Entry Point
├── engine/             # Generic Orchestrator & Executor
├── components/         # Hybrid Components (Hooks & Templates)
├── database/           # Database Client (Firestore & TinyDB)
└── models/             # Pydantic Schemas & Registry
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
1.  **Select Workflow**: Choose between `HOLISTINEN_MESTARUUS_3` (Full) or `KVOORUMI_OPTIMIZED` (Fast).
2.  **Upload Evidence**: Upload PDF/Text files for History, Product, and Reflection.
3.  **Run Assessment**: Click the button to start the asynchronous job.
4.  **View Results**: The UI polls the backend and displays the final XAI report.

## 📚 Documentation
Full documentation is available in the `docs/` directory and can be viewed with MkDocs:

```bash
mkdocs serve
```

## 📄 License
[MIT License](LICENSE)
