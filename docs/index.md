# Cognitive Quorum v2.0 Documentation

**Robust, Data-Driven AI Orchestration.**

## Overview

Cognitive Quorum v2.0 is a Modular Monolith designed for **Auditable AI**. It orchestrates a pipeline of 12 specialized agents to perform rigorous cognitive labor, from logical mapping to causal inference.

## Key Features (V2.2 - "Enterprise Core")

*   **Vertex AI (Hamina):** 100% Data Residency in `europe-north1`. No data leaves the EU.
*   **Gemini 2.5 Integration:** High-fidelity reasoning with **Heuristic JSON Repair** layer.
*   **3-Tier Database:** Consistent `Mock -> Local Prod -> Cloud Prod` environment synchronization.
*   **12-Agent Assembly Line:** Detailed pipeline including Archivist, Coach, and Panel agents.
*   **Strict Typing:** Powered by Pydantic V2 `Annotated` models and generic state management.

## Navigation

### Architecture
*   [System Architecture](architecture.md) - The Modular Monolith.
*   [Cognitive Whitepaper](structured_cognitive_architecture.md) - The theory behind the 12 agents.
*   [Architecture Analysis](architecture_analysis.md) - Deep dive into RAG, Causal, and PII layers.

### Implementation
*   [Components](components.md) - Agents and Hooks reference.
*   [Data Management](data_management.md) - DB structure and persistence.
*   [Prompt Engineering](prompt_engineering.md) - Jinja2 + Pydantic strategy.
*   [API Reference](reference.md) - Endpoints and Directory Structure.

### Status
*   [Refactoring Status](refactoring_status.md) - Audit of the V2.0 codebase.

## Quick Start

1.  **Run**: `.\run_locally.bat`
2.  **UI**: [http://localhost:8501](http://localhost:8501)
3.  **API**: [http://localhost:8000/docs](http://localhost:8000/docs)