# API Reference & Directory Structure

This document provides a reference for the application's directory structure and the backend REST API.

## Directory Structure

The project is organized into a modular structure to separate concerns between the backend engine, user interface, data, and documentation.

```
quorum/
├── backend/                # FastAPI Application (The Core Engine)
│   ├── api/                # REST API Routers
│   ├── nodes/              # Implementations for various workflow node types
│   ├── config.py           # Configuration & Environment Variables
│   ├── engine.py           # The core data-driven workflow execution engine
│   ├── main.py             # Application entry point
│   ├── schemas.py          # Pydantic models for data validation
│   └── seeder.py           # Database initialization script
├── data/                   # Data & Configuration Files
│   ├── db.json             # Runtime database (TinyDB)
│   ├── seed_data.json      # Default workflow & node type definitions
│   ├── partials/           # Reusable template components
│   ├── templates/          # Jinja2 templates for data transformation
│   └── uploads/            # User-uploaded files for processing
├── docs/                   # Project documentation (MkDocs)
├── frontend/               # Streamlit Web Interface
│   └── app.py              # Main UI entry point
├── pages/                  # Streamlit UI pages
└── scripts/                # Utility & maintenance scripts
```

## API Reference

The backend exposes a RESTful API for managing and executing data-driven workflows. The API is documented using the OpenAPI standard, providing interactive exploration and testing capabilities.

**Interactive Documentation:**
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

Endpoints are grouped by resource type for clarity.

#### Workflows
*   `GET /workflows`: List all available workflow definitions.
*   `POST /workflows`: Create a new workflow definition.
*   `GET /workflows/{workflow_id}`: Retrieve a specific workflow definition.
*   `PUT /workflows/{workflow_id}`: Update an existing workflow definition.
*   `DELETE /workflows/{workflow_id}`: Delete a workflow definition.

#### Nodes
*   `GET /nodes/types`: List all available node types that can be used to build workflows.

#### Executions
*   `POST /workflows/{workflow_id}/run`: Initiate a new execution for a specific workflow.
*   `GET /executions`: Retrieve the history of all workflow executions.
*   `GET /executions/{execution_id}`: Retrieve the status and results of a specific execution.

#### System
*   `POST /system/reset-db`: Reset the database to its default state using the seed data.