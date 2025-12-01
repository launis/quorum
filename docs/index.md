# Cognitive Quorum v2

**Cognitive Quorum** is a next-generation **Agentic Workflow Engine** designed for high-stakes, multi-agent AI assessments. It bridges the gap between probabilistic Generative AI and deterministic software engineering by implementing a **Neuro-symbolic architecture**.

By treating prompts, rules, and workflows as data, Cognitive Quorum enables rapid iteration and precise control over complex reasoning chains.

## Key Features

- **🧩 Generic Engine**: A unified execution core that runs any workflow defined in JSON.
- **🤖 Hybrid Architecture**: Seamlessly orchestrates LLMs (such as Gemini and GPT-4) with deterministic Python Hooks for search, math, and logic.
- **💾 Data-Driven Core**: All business logic—prompts, rules, and workflows—is decoupled from the application code and stored in a database, seeded from modular fragments and templates.
- **🔍 Explainable AI (XAI)**: Built-in transparency with citation tracking, uncertainty quantification, and detailed audit trails.
- **⚡ Multi-Model Agnostic**: Switch language models at any step to optimize for cost, speed, or reasoning capability.

## Getting Started

1.  **Set Up Environment**: Ensure you have Python 3.10+ and all required dependencies installed.
2.  **Configure Secrets**: Create a `.env` file with your API keys (e.g., `GEMINI_API_KEY`, `OPENAI_API_KEY`).
3.  **Launch the UI**:
    ```bash
    streamlit run app.py
    ```
4.  **Execute a Workflow**: Select a workflow to run. For example, choose `KVOORUMI_PHASED_A` to perform a comprehensive assessment.

## Documentation Structure

- **[Architecture](architecture.md)**: A deep dive into the Generic Engine and Registry Pattern.
- **[Data Management](data_management.md)**: An explanation of the data-driven core (JSON, TinyDB, Templates).
- **[Prompt Engineering](prompt_engineering.md)**: Strategies for constructing effective agent prompts.
- **[Components & Hooks](components.md)**: A reference for available Python hooks and hybrid components.
- **[API Reference](reference.md)**: Technical documentation for the backend classes.
- **[Interactive API](swagger/index.md)**: A live Swagger UI for testing API endpoints.
- **[Standalone API Viewer](api-view.html)**: A lightweight, full-screen Swagger UI.