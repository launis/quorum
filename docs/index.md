# Cognitive Quorum v2

**Cognitive Quorum** is a Dynamic Workflow Engine designed for complex, multi-agent AI assessments. It combines the flexibility of Large Language Models (LLMs) with the reliability of structured data and deterministic code.

## Key Features

- **Generic Engine**: Define workflows in JSON, execute them with a single engine.
- **Hybrid Architecture**: Mix LLM generation with Python code (Hooks) for Search, Math, and Parsing.
- **Data-Driven**: Rules, Prompts, and Workflow logic are stored in the database, not hardcoded.
- **Multi-Model Support**: Seamlessly switch between Google Gemini and OpenAI GPT-4.
- **Transparency**: Full XAI reporting with citations and uncertainty quantification.

## Getting Started

1.  **Configure Secrets**: Create a `.env` file with your API keys.
2.  **Run the App**: `streamlit run app.py`
3.  **Select Workflow**: Choose between `KVOORUMI_PHASED_A` (Detailed) or `KVOORUMI_OPTIMIZED` (Fast).

## Documentation Structure

- **[Architecture](architecture.md)**: Deep dive into the Generic Engine and Registry Pattern.
- **[Components & Hooks](components.md)**: Reference for available Python hooks and hybrid components.
- **[API Reference](reference.md)**: Technical documentation of the backend classes.
