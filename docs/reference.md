# API Reference & Directory Structure

## Directory Structure

```
quorum/
├── backend/                # FastAPI Application (The Core Engine)
│   ├── agents/             # Workflow node implementations (e.g., LLMNode, CodeNode)
│   ├── api/                # REST API Routers
│   ├── config.py           # Configuration & Environment Variables
│   ├── engine.py           # Data-Driven Workflow Engine
│   ├── main.py             # App Entry Point
│   ├── schemas.py          # Pydantic Models (Data Structures)
│   └── seeder.py           # Database Initialization Script
├── data/                   # Data & Configuration Files
│   ├── db.json             # Runtime Database (TinyDB)
│   ├── seed_data.json      # Default workflow & node definitions
│   ├── fragments/          # Reusable prompt components (partials)
│   ├── templates/          # Jinja2 Prompt Templates
│   └── uploads/            # User-uploaded files for processing
├── docs/                   # Documentation (MkDocs)
├── frontend/               # Streamlit Web Interface
│   └── app.py              # Main UI Entry Point
├── pages/                  # UI pages for workflow management & execution
└── scripts/                # Utility & maintenance scripts
```

## API Reference

The backend exposes a RESTful API for managing and executing workflows. The API is documented using the OpenAPI standard.

**Interactive Documentation:**
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Workflow Execution
*   `POST /workflow/execute`: Initiate a new workflow execution.
*   `GET /workflow/status/{execution_id}`: Retrieve the status and results of a specific workflow execution.
*   `GET /workflow/history`: Get a list of past workflow executions.

#### Workflow Definitions
*   `GET /workflows`: List all available workflow definitions.
*   `POST /workflows`: Create or update a workflow definition.
*   `GET /workflows/{workflow_id}`: Get a specific workflow definition.
*   `GET /nodes`: List all available node types that can be used to build workflows.

#### Management
*   `POST /manage/reset-db`: Reset the database to its default state using seed data.