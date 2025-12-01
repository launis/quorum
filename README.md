# Cognitive Quorum - Dynamic Workflow Engine

**Cognitive Quorum** is an advanced, data-driven workflow engine designed for complex, multi-agent AI assessments. It orchestrates interactions between Large Language Models (LLMs) and deterministic Python code (Hooks) to produce high-quality, verifiable, and transparent results.

## 🚀 Key Features

*   **Generic Workflow Engine**: A single, agnostic engine executes any workflow defined in the database. No hardcoded agent logic.
*   **Hybrid Architecture**: Seamlessly combines LLMs (e.g., Google Gemini, OpenAI GPT-4) for reasoning and generation with deterministic Python Hooks for tasks like calculations, data parsing, and external API calls.
*   **Data-Driven Configuration**: Workflows, prompts, execution steps, and business rules are defined as data in a document database, seeded from modular JSON fragments and Jinja2 templates. This allows for rapid iteration and modification without code changes.
*   **Dynamic Registries**: Utilizes a registry pattern for dynamically mapping string identifiers to Pydantic schemas (`SchemaRegistry`) and Python functions (`HookRegistry`), enabling flexible and extensible design.
*   **Reliability & Robustness**:
    *   **UTF-8 Support**: Ensures full compatibility with international character sets across the entire stack.
    *   **Error Fallbacks**: Implements automatic retry logic and model switching (e.g., from a faster to a more powerful model on failure) to enhance resilience.
*   **Adversarial Testing**: Includes a comprehensive test suite for simulating rule violations (e.g., Prompt Injection, PII Leaks) and technical failures.
*   **External Integrations**: Supports connections to external services like the Google Custom Search API for real-time fact-checking and provides a framework for Retrieval-Augmented Generation (RAG).
*   **Transparency & Explainability (XAI)**: Designed for full traceability of inputs, outputs, and data sources. Capable of generating detailed XAI reports with uncertainty quantification.

## 🏗️ System Architecture

The system is built on a modern, service-oriented architecture, designed for scalability and maintainability. The core logic is encapsulated in the `src/` directory, promoting a clean separation of concerns.

```
.
├── src/
│   ├── api/                # FastAPI routers and server logic
│   ├── components/         # Core building blocks like Hooks and Registries
│   │   └── hooks/          # Deterministic Python functions (e.g., search, parsing)
│   ├── database/           # Database clients and adapters (TinyDB, Firestore)
│   ├── engine/             # The main workflow orchestration and execution logic
│   │   ├── orchestrator.py # Manages the overall workflow execution
│   │   └── executor.py     # Executes individual steps (LLM calls or Hook calls)
│   ├── models/             # Pydantic models and schema definitions
│   └── main.py             # Application entry point
├── data/
│   ├── db.json             # Default local database (TinyDB)
│   ├── fragments/          # Reusable JSON components for building workflows
│   └── templates/          # Jinja2 templates for generating prompts
├── tests/
│   ├── scenarios/         # Test data for various scenarios
│   └── test_*.py           # Pytest integration and unit tests
├── scripts/                # Helper and utility scripts (e.g., database seeding)
├── docs/                   # Project documentation
├── config.py               # Centralized configuration
├── docker-compose.yml      # Docker Compose for local deployment
├── requirements.txt        # Python package dependencies
└── README.md
```

## ⚙️ Getting Started

### Prerequisites

*   Python 3.10+
*   Docker and Docker Compose
*   API keys for required services (e.g., Google AI, OpenAI, Google Custom Search)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/cognitive-quorum.git
    cd cognitive-quorum
    ```

2.  **Install Python dependencies:**
    ```bash
# Cognitive Quorum - Dynamic Workflow Engine

**Cognitive Quorum** is an advanced, data-driven workflow engine designed for complex, multi-agent AI assessments. It orchestrates interactions between Large Language Models (LLMs) and deterministic Python code (Hooks) to produce high-quality, verifiable, and transparent results.

## 🚀 Key Features

*   **Generic Workflow Engine**: A single, agnostic engine executes any workflow defined in the database. No hardcoded agent logic.
*   **Hybrid Architecture**: Seamlessly combines LLMs (e.g., Google Gemini, OpenAI GPT-4) for reasoning and generation with deterministic Python Hooks for tasks like calculations, data parsing, and external API calls.
*   **Data-Driven Configuration**: Workflows, prompts, execution steps, and business rules are defined as data in a document database, seeded from modular JSON fragments and Jinja2 templates. This allows for rapid iteration and modification without code changes.
*   **Dynamic Registries**: Utilizes a registry pattern for dynamically mapping string identifiers to Pydantic schemas (`SchemaRegistry`) and Python functions (`HookRegistry`), enabling flexible and extensible design.
*   **Reliability & Robustness**:
    *   **UTF-8 Support**: Ensures full compatibility with international character sets across the entire stack.
    *   **Error Fallbacks**: Implements automatic retry logic and model switching (e.g., from a faster to a more powerful model on failure) to enhance resilience.
*   **Adversarial Testing**: Includes a comprehensive test suite for simulating rule violations (e.g., Prompt Injection, PII Leaks) and technical failures.
*   **External Integrations**: Supports connections to external services like the Google Custom Search API for real-time fact-checking and provides a framework for Retrieval-Augmented Generation (RAG).
*   **Transparency & Explainability (XAI)**: Designed for full traceability of inputs, outputs, and data sources. Capable of generating detailed XAI reports with uncertainty quantification.

## 🏗️ System Architecture

The system is built on a modern, service-oriented architecture, designed for scalability and maintainability. The core logic is encapsulated in the `src/` directory, promoting a clean separation of concerns.

```
.
├── src/
│   ├── api/                # FastAPI routers and server logic
│   ├── components/         # Core building blocks like Hooks and Registries
│   │   └── hooks/          # Deterministic Python functions (e.g., search, parsing)
│   ├── database/           # Database clients and adapters (TinyDB, Firestore)
│   ├── engine/             # The main workflow orchestration and execution logic
│   │   ├── orchestrator.py # Manages the overall workflow execution
│   │   └── executor.py     # Executes individual steps (LLM calls or Hook calls)
│   ├── models/             # Pydantic models and schema definitions
│   └── main.py             # Application entry point
├── data/
│   ├── db.json             # Default local database (TinyDB)
│   ├── fragments/          # Reusable JSON components for building workflows
│   └── templates/          # Jinja2 templates for generating prompts
├── tests/
│   ├── scenarios/         # Test data for various scenarios
│   └── test_*.py           # Pytest integration and unit tests
├── scripts/                # Helper and utility scripts (e.g., database seeding)
├── docs/                   # Project documentation
├── config.py               # Centralized configuration
├── docker-compose.yml      # Docker Compose for local deployment
├── requirements.txt        # Python package dependencies
└── README.md
```

## ⚙️ Getting Started

### Prerequisites

*   Python 3.10+
*   Docker and Docker Compose
*   API keys for required services (e.g., Google AI, OpenAI, Google Custom Search)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/cognitive-quorum.git
    cd cognitive-quorum
    ```

2.  **Install Python dependencies:**
# Cognitive Quorum - Dynamic Workflow Engine

**Cognitive Quorum** is an advanced, data-driven workflow engine designed for complex, multi-agent AI assessments. It orchestrates interactions between Large Language Models (LLMs) and deterministic Python code (Hooks) to produce high-quality, verifiable, and transparent results.

## 🚀 Key Features

*   **Generic Workflow Engine**: A single, agnostic engine executes any workflow defined in the database. No hardcoded agent logic.
*   **Hybrid Architecture**: Seamlessly combines LLMs (e.g., Google Gemini, OpenAI GPT-4) for reasoning and generation with deterministic Python Hooks for tasks like calculations, data parsing, and external API calls.
*   **Data-Driven Configuration**: Workflows, prompts, execution steps, and business rules are defined as data in a document database, seeded from modular JSON fragments and Jinja2 templates. This allows for rapid iteration and modification without code changes.
*   **Dynamic Registries**: Utilizes a registry pattern for dynamically mapping string identifiers to Pydantic schemas (`SchemaRegistry`) and Python functions (`HookRegistry`), enabling flexible and extensible design.
*   **Reliability & Robustness**:
    *   **UTF-8 Support**: Ensures full compatibility with international character sets across the entire stack.
    *   **Error Fallbacks**: Implements automatic retry logic and model switching (e.g., from a faster to a more powerful model on failure) to enhance resilience.
*   **Adversarial Testing**: Includes a comprehensive test suite for simulating rule violations (e.g., Prompt Injection, PII Leaks) and technical failures.
*   **External Integrations**: Supports connections to external services like the Google Custom Search API for real-time fact-checking and provides a framework for Retrieval-Augmented Generation (RAG).
*   **Transparency & Explainability (XAI)**: Designed for full traceability of inputs, outputs, and data sources. Capable of generating detailed XAI reports with uncertainty quantification.

## 🏗️ System Architecture

The system is built on a modern, service-oriented architecture, designed for scalability and maintainability. The core logic is encapsulated in the `src/` directory, promoting a clean separation of concerns.

```
.
├── src/
│   ├── api/                # FastAPI routers and server logic
│   ├── components/         # Core building blocks like Hooks and Registries
│   │   └── hooks/          # Deterministic Python functions (e.g., search, parsing)
│   ├── database/           # Database clients and adapters (TinyDB, Firestore)
│   ├── engine/             # The main workflow orchestration and execution logic
│   │   ├── orchestrator.py # Manages the overall workflow execution
│   │   └── executor.py     # Executes individual steps (LLM calls or Hook calls)
│   ├── models/             # Pydantic models and schema definitions
│   └── main.py             # Application entry point
├── data/
│   ├── db.json             # Default local database (TinyDB)
│   ├── fragments/          # Reusable JSON components for building workflows
│   └── templates/          # Jinja2 templates for generating prompts
├── tests/
│   ├── scenarios/         # Test data for various scenarios
│   └── test_*.py           # Pytest integration and unit tests
├── scripts/                # Helper and utility scripts (e.g., database seeding)
├── docs/                   # Project documentation
├── config.py               # Centralized configuration
├── docker-compose.yml      # Docker Compose for local deployment
├── requirements.txt        # Python package dependencies
└── README.md
```

## ⚙️ Getting Started

### Prerequisites

*   Python 3.10+
*   Docker and Docker Compose
*   API keys for required services (e.g., Google AI, OpenAI, Google Custom Search)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/cognitive-quorum.git
    cd cognitive-quorum
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory and add your API keys. Refer to `config.py` for the required variable names.
    ```env
    GOOGLE_API_KEY="your_google_api_key"
    OPENAI_API_KEY="your_openai_api_key"
    GOOGLE_SEARCH_API_KEY="your_search_api_key"
    GOOGLE_SEARCH_CX="your_search_cx"
    ```

## 🧪 Running Tests

To ensure the system is functioning correctly, run the test suite:
```bash
pytest
```

## 📖 Viewing Documentation

**Option 1: Online**
[View GitHub Pages](https://launis.github.io/quorum/)

**Option 2: Local Server**
```bash
mkdocs serve -a localhost:8001
# Open http://localhost:8001
```