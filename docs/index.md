# Cognitive Quorum v2 Documentation

Welcome to the documentation for **Cognitive Quorum v2**, a generic, data-driven engine for orchestrating advanced AI workflows.

## Overview

Cognitive Quorum is designed to execute complex cognitive tasks by simulating a "quorum" of specialized AI agents and deterministic code modules. The system is architected as a highly configurable engine where the entire workflow—including the sequence of steps, agent personas, prompts, and business rules—is defined in a database. This data-driven approach allows for rapid adaptation and reconfiguration for various use cases without requiring changes to the underlying source code.

The engine processes inputs through a rigorous, multi-step workflow, ensuring that every stage of the process is transparent, auditable, and produces high-quality, hallucination-resistant results.

## Key Features

*   **Data-Driven Orchestration**: All workflow logic, prompts, agent instructions, and business rules are loaded from a database, enabling dynamic reconfiguration without code changes.
*   **Configurable Workflows**: Define complex, multi-step processes composed of specialized AI agents (e.g., Analyst, Critic, Judge) and deterministic Python functions (Hooks).
*   **Hybrid Execution**: Blends the reasoning capabilities of Large Language Models (LLMs) with the precision of deterministic code for tasks like data validation, calculations, and external API calls.
*   **Transparent Auditing**: Records every step of the workflow, from initial data ingestion to the final conclusion, providing a complete and verifiable audit trail.

## Documentation

### Core Concepts
*   **[System Architecture](architecture.md)**: A high-level overview of the technical design, including the FastAPI backend and Streamlit frontend.
*   **[The Workflow Engine](structured_cognitive_architecture.md)**: A deep dive into the core data-driven orchestration, detailing how workflow steps are executed and how agents and hooks interact.

### Building Blocks
*   **[Components: Agents & Hooks](components.md)**: A detailed breakdown of the system's primary building blocks.
*   **[Data Model](data_management.md)**: An explanation of how the system's behavior is defined and stored in the database.
*   **[Dynamic Prompts](prompt_engineering.md)**: A guide to the Jinja2-based templating system used for constructing dynamic, context-aware prompts.

### Usage & Management
*   **[Admin UI Guide](management_architecture.md)**: A walkthrough of the administrative interface for managing workflow configurations.
*   **[API Reference](reference.md)**: Technical reference for the backend REST API.

## Getting Started

To run the system locally:

1.  **Start the Services**:
    ```bash
    .\run_locally.bat
    ```
    This command starts both the FastAPI backend (port 8000) and the Streamlit frontend (port 8501).

2.  **Access the UI**:
    Open [http://localhost:8501](http://localhost:8501) in your browser.

3.  **View API Docs**:
    Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.