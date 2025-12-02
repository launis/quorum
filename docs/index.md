# Cognitive Quorum v2 Documentation

Welcome to the documentation for **Cognitive Quorum**, an advanced AI-driven assessment and auditing system.

## Overview

Cognitive Quorum is designed to simulate a "quorum" of expert AI agents that evaluate, debate, and judge complex inputs. Unlike simple chatbot interactions, this system employs a rigorous, multi-step cognitive workflow to ensure high-quality, unbiased, and hallucination-resistant results.

## Key Features

*   **Multi-Agent Architecture**: Uses specialized agents (Analyst, Logician, Critics, Judge) to handle different cognitive tasks.
*   **Data-Driven Logic**: All prompts, rules, and workflow steps are defined in a database (`db.json`), allowing for dynamic reconfiguration without code changes.
*   **Hybrid Execution**: Combines Large Language Models (LLM) with deterministic Python code (Hooks) for tasks like fact-checking, math, and validation.
*   **Transparent Auditing**: Every step of the reasoning process is recorded, from initial evidence gathering to the final verdict.

## Documentation Structure

*   **[Architecture](architecture.md)**: High-level technical design, including the Backend (FastAPI) and Frontend (Streamlit).
*   **[Components & Agents](components.md)**: Detailed breakdown of the specific AI agents and hybrid hooks used in the system.
*   **[Data Management](data_management.md)**: How data is stored, seeded, and managed (TinyDB, Seed Data, Fragments).
*   **[Prompt Engineering](prompt_engineering.md)**: Explanation of the dynamic prompt construction system using Jinja2 templates.
*   **[Management UI](management_architecture.md)**: Guide to the administrative interface for managing rules and prompts.
*   **[API Reference](reference.md)**: Details on the backend REST API.

## Getting Started

To run the system locally:

1.  **Start the Services**:
    ```bash
    .\run_locally.bat
    ```
    This starts both the FastAPI backend (port 8000) and the Streamlit frontend (port 8501).

2.  **Access the UI**:
    Open [http://localhost:8501](http://localhost:8501) in your browser.

3.  **View API Docs**:
    Open [http://localhost:8000/docs](http://localhost:8000/docs) for the Swagger UI.