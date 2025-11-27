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

The system follows a modular architecture:

```
src/
├── engine/             # Generic Orchestrator & Executor
├── components/         # Hybrid Components (Hooks & Templates)
├── models/             # Pydantic Schemas & Registry
└── database/           # Database Client & Initialization
```

*   **Orchestrator**: Manages the workflow lifecycle and state.
*   **Executor**: Runs individual steps, handling Pre-Hooks -> LLM -> Post-Hooks.
*   **Hooks**: Python functions that perform specific actions (e.g., `execute_google_search`, `parse_analyst_output`).

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.10+
*   Docker (optional, for containerized deployment)
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
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

## 🖥️ Usage

### Running the Streamlit UI
The primary interface is a Streamlit web application.

```bash
streamlit run app.py
```

1.  **Select Workflow**: Choose between `KVOORUMI_PHASED_A` (Detailed) or `KVOORUMI_OPTIMIZED` (Fast).
2.  **Upload Evidence**: Enter the text for Prompt, History, Product, and Reflection.
3.  **Run Assessment**: Click the button to start the workflow.
4.  **View Results**: See the final verdict, citations, and XAI report.

### Running Tests
```bash
python scripts/verify_optimized.py
```

## 📚 Documentation
Full documentation is available in the `docs/` directory and can be viewed with MkDocs:

```bash
mkdocs serve
```

## 📄 License
[MIT License](LICENSE)
