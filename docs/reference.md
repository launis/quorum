# API Reference & Directory Structure

## Directory Structure

```
quorum/
├── backend/                # FastAPI Application
│   ├── agents/             # AI Agent Implementations (BaseAgent, Judge, etc.)
│   ├── api/                # REST API Routers
│   ├── config.py           # Configuration & Environment Variables
│   ├── engine.py           # Workflow Engine (The Core)
│   ├── main.py             # App Entry Point
│   ├── schemas.py          # Pydantic Models (Data Structures)
│   └── seeder.py           # Database Initialization Script
├── data/                   # Data Storage
│   ├── db.json             # Runtime Database (TinyDB)
│   ├── seed_data.json      # Factory Settings
│   ├── fragments/          # Prompt Snippets (Rules, Mandates)
│   ├── templates/          # Jinja2 Prompt Templates
│   └── uploads/            # User Uploaded Files
├── docs/                   # Documentation (MkDocs)
├── frontend/               # Streamlit Application
│   └── ui.py               # Main UI Entry Point
├── pages/                  # Streamlit Pages
│   └── management.py       # Management Dashboard
└── scripts/                # Utility Scripts
```

## API Reference

The backend exposes a RESTful API documented via OpenAPI (Swagger).

**Interactive Documentation:**
*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoints

#### Workflow
*   `POST /workflow/start`: Start a new assessment workflow.
*   `GET /workflow/status/{execution_id}`: Get the status and results of a running workflow.
varmista, että 
#### Configuration
*   `GET /config/prompts`: List all available prompts.
*   `POST /config/prompts`: Create or update a prompt.
*   `GET /config/rules`: List all system rules.

#### Management
*   `POST /manage/reset-db`: Reset the database to seed state.
*   `POST /manage/deploy-mock-to-prod`: Promote mock configuration to production.