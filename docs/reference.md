# API Reference & Directory Structure

This document provides a reference for the application's directory structure and the backend REST API.

## Directory Structure (V2.0)

```
quorum/
├── backend/                # Modular Monolith Core
│   ├── agents/             # Specialized Agent Classes (Guard, Judge, etc.)
│   ├── api/                # FastAPI Routers
│   ├── core/               # Workflow Engine & Pipeline Runner
│   ├── database/           # DB Wrapper & Seeder
│   ├── hooks/              # Deterministic Logic (PII, Causal, Search)
│   ├── llm/                # LLM Provider Adapters
│   ├── models/             # Pydantic V2 Data Models (State, Domain)
│   ├── services/           # Business Logic Services
│   ├── config.py           # Configuration
│   └── main.py             # App Entry Point
├── data/                   # Data Persistence
│   ├── db.json             # Runtime Database
│   ├── seed_data.json      # Configuration Source of Truth
│   └── uploads/            # User Uploads
├── docs/                   # MkDocs Documentation
├── frontend/               # Streamlit Interface
└── scripts/                # Utility Scripts
```

## API Reference

The backend exposes a RESTful API.

**Interactive Documentation:**
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Workflows
*   `GET /workflows`: List definitions.
*   `POST /workflows/{id}/run`: Execute a workflow.

#### System
*   `POST /system/reset-db`: Reset runtime DB from seed.