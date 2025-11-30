# Cognitive Quorum v2

**Cognitive Quorum** is a next-generation **Agentic Workflow Engine** designed for high-stakes, multi-agent AI assessments. It bridges the gap between probabilistic Generative AI and deterministic software engineering, implementing a **Neuro-symbolic architecture**.

By treating prompts, rules, and workflows as data, Cognitive Quorum enables rapid iteration and precise control over complex reasoning chains.

## Key Features

- **🧩 Generic Engine**: A unified execution core that runs any workflow defined in JSON.
- **🤖 Hybrid Architecture**: Seamlessly orchestrates LLMs (Gemini, GPT-4) with deterministic Python Hooks for Search, Math, and Logic.
- **💾 Data-Driven Core**: All business logic—Prompts, Rules, and Workflows—is decoupled from code and stored in the database.
- **🔍 Explainable AI (XAI)**: Built-in transparency with citation tracking, uncertainty quantification, and audit trails.
- **⚡ Multi-Model Agnostic**: Switch models per-step to optimize for cost, speed, or reasoning capability.

## Getting Started

1.  **Environment Setup**: Ensure you have Python 3.10+ and dependencies installed.
2.  **Configure Secrets**: Create a `.env` file with your API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`).
3.  **Launch the UI**:
    ```bash
    streamlit run app.py
    ```
4.  **Execute Workflow**: Select `KVOORUMI_PHASED_A` for a full deep-dive assessment.

## Documentation Structure

- **[Architecture](architecture.md)**: Deep dive into the Generic Engine and Registry Pattern.
- **[Data Management](data_management.md)**: Understanding the data-driven core (JSON, TinyDB, Templates).
- **[Prompt Engineering](prompt_engineering.md)**: Strategies for constructing effective agent prompts.
- **[Components & Hooks](components.md)**: Reference for available Python hooks and hybrid components.
- **[API Reference](reference.md)**: Technical documentation of the backend classes.
- **[Interactive API](swagger.md)**: Live Swagger UI for testing endpoints.
