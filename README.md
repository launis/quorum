# Cognitive Quorum v2

**Cognitive Quorum** is an advanced, agentic AI system designed to perform rigorous, multi-step cognitive assessments. It utilizes a "System 2" thinking approach, employing a chain of specialized agents to analyze, validate, and grade complex inputs against a hybrid rubric.

## 🚀 Key Features

*   **9-Step Cognitive Workflow**: A sequential assembly line of agents (Guard, Analyst, Logician, Critics, Judge, etc.) ensuring deep analysis.
*   **Hybrid Architecture**: Combines **Mock Mode** (for cost-free testing) and **Production Mode** (Google Gemini API).
*   **Data-Driven Design**: Logic, rules, and prompts are stored as data (`db.json`), allowing dynamic updates without code changes.
*   **XAI Reporting**: Generates Explainable AI reports detailing *why* a certain verdict was reached.
*   **Management UI**: Built-in tools to manage prompts, rules, and system configuration.

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd quorum
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    *   Create a `.env` file in the root directory.
    *   Add the following configuration:

    ```env
    # --- Required for Production Mode ---
    GOOGLE_API_KEY=...                       # Your Google Gemini API Key
    GOOGLE_SEARCH_API_KEY=...                # Google Custom Search JSON API Key
    GOOGLE_SEARCH_CX=...                     # Google Custom Search Engine ID
    
    # --- System Modes ---
    USE_MOCK_LLM=False                       # Set True to use offline mock responses (no API cost)
    USE_MOCK_DB=True                         # Set True to use db_mock.json, False for db.json
    ```

## 🚦 Quick Start

### 1. Start the System (Backend + Frontend)
Use the provided script to launch both services:
```bash
./run_locally.bat
```
This will open:
*   **Frontend**: `http://localhost:8501`
*   **Backend API**: `http://localhost:8000/docs`

### 2. Manual Startup (Optional)
If you prefer to run services separately:
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
streamlit run ui.py
```

### 3. View Documentation
Comprehensive documentation is available via MkDocs.
```bash
mkdocs serve
```
Access at: `http://localhost:8000`

## 🔧 API Documentation

The backend exposes a full REST API.
*   **Swagger UI**: `http://localhost:8000/docs`
*   **ReDoc**: `http://localhost:8000/redoc`

## 📂 Project Structure

<!-- TREE_START -->
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── analyst.py
│   │   ├── base.py
│   │   ├── critics.py
│   │   ├── guard.py
│   │   ├── judge.py
│   │   ├── logician.py
│   │   ├── panel.py
│   │   └── xai.py
│   ├── api/
│   │   ├── admin_router.py
│   │   ├── agents_router.py
│   │   ├── config_router.py
│   │   ├── hooks_router.py
│   │   ├── llm_router.py
│   │   ├── templates_router.py
│   │   └── tools_router.py
│   ├── __init__.py
│   ├── component.py
│   ├── config.py
│   ├── data_handler.py
│   ├── Dockerfile
│   ├── engine.py
│   ├── exporter.py
│   ├── hooks.py
│   ├── list_models.py
│   ├── main.py
│   ├── mock_llm.py
│   ├── processor.py
│   ├── requirements.txt
│   ├── schemas.py
│   ├── seeder.py
│   └── verify_prompts.py
├── data/
│   ├── db/
│   │   └── db.json
│   ├── uploads/
│   │   ├── history.pdf
│   │   ├── modular_test.pdf
│   │   ├── product.pdf
│   │   ├── prompt.pdf
│   │   ├── reflection.pdf
│   │   └── workflow_test.pdf
│   ├── bibliography.txt
│   ├── bibliography_source.txt
│   ├── chapter2_source.txt
│   ├── db.json
│   ├── db_mock.json
│   ├── granular_components.json
│   ├── mock_responses.json
│   └── seed_data.json
├── docs/
│   ├── swagger/
│   │   ├── index.html
│   │   ├── index.md
│   │   └── openapi.json
│   ├── api-view.html
│   ├── architecture.md
│   ├── components.md
│   ├── data_management.md
│   ├── index.md
│   ├── management_architecture.md
│   ├── prompt_engineering.md
│   ├── reference.md
│   └── structured_cognitive_architecture.md
├── frontend/
│   ├── Dockerfile
│   └── requirements.txt
├── pages/
│   └── Management_Dashboard.py
├── scripts/
│   ├── add_hooks_to_seed.py
│   ├── add_panel_step.py
│   ├── apply_cleanup.py
│   ├── atomize_master_instructions.py
│   ├── check_models.py
│   ├── check_models_file.py
│   ├── clean_seed_prompts.py
│   ├── debug_api_500.py
│   ├── debug_api_rule1.py
│   ├── debug_report_print.py
│   ├── dump_step.py
│   ├── fix_prompts_for_v2.py
│   ├── force_seed_mock.py
│   ├── generate_openapi.py
│   ├── import_references.py
│   ├── import_rules.py
│   ├── inspect_failure.py
│   ├── rebuild_seed_data.py
│   ├── seed_mock_db.py
│   ├── seed_workflow.py
│   ├── split_components.py
│   ├── split_master_instructions.py
│   ├── test_executor_gemini.py
│   ├── test_full_workflow.py
│   ├── test_generic_workflow.py
│   ├── test_llm_direct.py
│   ├── test_modular_workflow.py
│   ├── test_parsing_robustness.py
│   ├── test_schemas_endpoint.py
│   ├── test_unified_endpoint.py
│   ├── test_upload.py
│   ├── update_docs.py
│   ├── update_seed_data.py
│   ├── update_seed_data_granular.py
│   ├── verify_optimized.py
│   ├── verify_refactor.py
│   ├── verify_unified_view.py
│   └── verify_v2.py
├── src/
│   ├── api/
│   │   ├── routers/
│   │   │   ├── db_router.py
│   │   │   ├── llm_router.py
│   │   │   ├── orchestrator_router.py
│   │   │   └── tools_router.py
│   │   ├── __init__.py
│   │   └── server.py
│   ├── components/
│   │   ├── hooks/
│   │   │   ├── __init__.py
│   │   │   ├── calculations.py
│   │   │   ├── parsing.py
│   │   │   ├── rag_logic.py
│   │   │   ├── reporting.py
│   │   │   ├── sanitization.py
│   │   │   └── search.py
│   │   ├── templates/
│   │   │   └── report_template.jinja2
│   │   ├── __init__.py
│   │   └── hook_registry.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── firestore_client.py
│   │   ├── initialization.py
│   │   └── tinydb_adapter.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── executor.py
│   │   ├── llm_handler.py
│   │   └── orchestrator.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   └── schema_registry.py
│   ├── ui/
│   ├── __init__.py
│   └── main.py
├── temp_uploads/
│   ├── 33c4f94f-4476-40d5-a3db-9579d7c3833f_keskusteluhistoria SITRA.pdf
│   ├── 33c4f94f-4476-40d5-a3db-9579d7c3833f_lopputuote sitra.pdf
│   ├── 33c4f94f-4476-40d5-a3db-9579d7c3833f_Reflektiodokumentti sitra.pdf
│   ├── 3d76c42a-9c80-453d-b2c1-14ab2a243ffa_keskusteluhistoria SITRA.pdf
│   ├── 3d76c42a-9c80-453d-b2c1-14ab2a243ffa_lopputuote sitra.pdf
│   ├── 3d76c42a-9c80-453d-b2c1-14ab2a243ffa_Reflektiodokumentti sitra.pdf
│   ├── 3dd41f1c-beb4-43d0-a28d-e334dd80e434_keskusteluhistoria SITRA.pdf
│   ├── 3dd41f1c-beb4-43d0-a28d-e334dd80e434_lopputuote sitra.pdf
│   ├── 3dd41f1c-beb4-43d0-a28d-e334dd80e434_Reflektiodokumentti sitra.pdf
│   ├── 684f7088-bb60-4920-bddc-c08a47370d97_keskusteluhistoria SITRA.pdf
│   ├── 684f7088-bb60-4920-bddc-c08a47370d97_lopputuote sitra.pdf
│   ├── 684f7088-bb60-4920-bddc-c08a47370d97_Reflektiodokumentti sitra.pdf
│   ├── 710b05e1-d512-4dd8-a3bc-cb7c7ed8d486_keskusteluhistoria SITRA.pdf
│   ├── 710b05e1-d512-4dd8-a3bc-cb7c7ed8d486_lopputuote sitra.pdf
│   ├── 710b05e1-d512-4dd8-a3bc-cb7c7ed8d486_Reflektiodokumentti sitra.pdf
│   ├── 83068d87-5af8-451d-94fb-c8dcd32ce966_keskusteluhistoria SITRA.pdf
│   ├── 83068d87-5af8-451d-94fb-c8dcd32ce966_lopputuote sitra.pdf
│   ├── 83068d87-5af8-451d-94fb-c8dcd32ce966_Reflektiodokumentti sitra.pdf
│   ├── 87022ec5-0ff8-4512-87f3-5c41f814caa2_keskusteluhistoria SITRA.pdf
│   ├── 87022ec5-0ff8-4512-87f3-5c41f814caa2_lopputuote sitra.pdf
│   ├── 87022ec5-0ff8-4512-87f3-5c41f814caa2_Reflektiodokumentti sitra.pdf
│   ├── 87fa624c-62bf-45c1-9e33-db6e07ab2906_keskusteluhistoria SITRA.pdf
│   ├── 87fa624c-62bf-45c1-9e33-db6e07ab2906_lopputuote sitra.pdf
│   ├── 87fa624c-62bf-45c1-9e33-db6e07ab2906_Reflektiodokumentti sitra.pdf
│   ├── 970c2665-4f3a-44f3-a16d-47d1ae8b5b97_keskusteluhistoria SITRA.pdf
│   ├── 970c2665-4f3a-44f3-a16d-47d1ae8b5b97_lopputuote sitra.pdf
│   ├── 970c2665-4f3a-44f3-a16d-47d1ae8b5b97_Reflektiodokumentti sitra.pdf
│   ├── ab9d610e-1e3f-49d4-bf72-7e61da31fb7d_keskusteluhistoria SITRA.pdf
│   ├── ab9d610e-1e3f-49d4-bf72-7e61da31fb7d_lopputuote sitra.pdf
│   ├── ab9d610e-1e3f-49d4-bf72-7e61da31fb7d_Reflektiodokumentti sitra.pdf
│   ├── b0585e65-aa46-48bd-8ef2-dfcf99c479c3_keskusteluhistoria SITRA.pdf
│   ├── b0585e65-aa46-48bd-8ef2-dfcf99c479c3_lopputuote sitra.pdf
│   ├── b0585e65-aa46-48bd-8ef2-dfcf99c479c3_Reflektiodokumentti sitra.pdf
│   ├── c54cc8a6-b980-4200-8e60-b1b424dac15a_keskusteluhistoria SITRA.pdf
│   ├── c54cc8a6-b980-4200-8e60-b1b424dac15a_lopputuote sitra.pdf
│   ├── c54cc8a6-b980-4200-8e60-b1b424dac15a_Reflektiodokumentti sitra.pdf
│   ├── dba31d87-de1a-46f0-b456-6e8e3703b105_keskusteluhistoria SITRA.pdf
│   ├── dba31d87-de1a-46f0-b456-6e8e3703b105_lopputuote sitra.pdf
│   ├── dba31d87-de1a-46f0-b456-6e8e3703b105_Reflektiodokumentti sitra.pdf
│   ├── df7c8d59-c6a2-48fd-bbab-226e2ea33627_keskusteluhistoria SITRA.pdf
│   ├── df7c8d59-c6a2-48fd-bbab-226e2ea33627_lopputuote sitra.pdf
│   ├── df7c8d59-c6a2-48fd-bbab-226e2ea33627_Reflektiodokumentti sitra.pdf
│   ├── e5701b55-de6c-46b6-ac16-d90231c4b1bf_keskusteluhistoria SITRA.pdf
│   ├── e5701b55-de6c-46b6-ac16-d90231c4b1bf_lopputuote sitra.pdf
│   ├── e5701b55-de6c-46b6-ac16-d90231c4b1bf_Reflektiodokumentti sitra.pdf
│   ├── ef16e6e3-7f1e-4e2e-a2cf-4f60b29cf4ba_keskusteluhistoria SITRA.pdf
│   ├── ef16e6e3-7f1e-4e2e-a2cf-4f60b29cf4ba_lopputuote sitra.pdf
│   └── ef16e6e3-7f1e-4e2e-a2cf-4f60b29cf4ba_Reflektiodokumentti sitra.pdf
├── tests/
│   ├── scenarios/
│   │   ├── error_models/
│   │   │   ├── corrupted.txt
│   │   │   └── empty.txt
│   │   ├── rule_violations/
│   │   │   ├── pii_leak.txt
│   │   │   └── prompt_injection.txt
│   │   └── workflow/
│   │       ├── keskusteluhistoria SITRA.pdf
│   │       ├── lopputuote sitra.pdf
│   │       └── Reflektiodokumentti sitra.pdf
│   ├── test_api.py
│   ├── test_api_new_endpoints.py
│   ├── test_banned_phrases_api.py
│   ├── test_db_scenarios.py
│   ├── test_guard_hybrid.py
│   ├── test_judge_scoring.py
│   ├── test_mock_workflow.py
│   ├── test_parsing_logic.py
│   ├── test_schema_validation.py
│   ├── test_workflow_construction.py
│   └── test_workflow_integration.py
├── backend_error.log
├── check_db_content.py
├── check_specific_components.py
├── config.py
├── current_log.txt
├── debug_json.py
├── debug_output_bypass.txt
├── debug_output_bypass_real.txt
├── debug_output_empty_args.txt
├── debug_output_final.txt
├── debug_output_granular.txt
├── debug_output_string_args.txt
├── debug_preview.py
├── docker-compose.yml
├── error_log.txt
├── error_response.txt
├── fast_import_refs.py
├── fix_rules.py
├── generate_openapi.py
├── inspect_last_execution.py
├── LICENSE
├── llm_errors.txt
├── logs.txt
├── logs_v2.txt
├── mkdocs.yml
├── models_list.txt
├── modular_test.pdf
├── openapi_dump.json
├── populate_citations.py
├── pytest.ini
├── README.md
├── refactor_error.txt
├── repro_output.txt
├── reproduce_issue.py
├── reproduce_parsing_issue.py
├── requirements.txt
├── run_locally.bat
├── run_locally.ps1
├── run_scenarios.py
├── standardize_content.py
├── start.bat
├── sync_rules_from_master.py
├── temp_step_3.json
├── test_llm_output.txt
├── test_output_api.txt
├── test_output_api_2.txt
├── test_output_api_2_utf8.txt
├── test_output_api_utf8.txt
├── ui.py
├── update_docs.bat
├── verification_output.txt
├── verify_config_update.py
└── verify_import.py
<!-- TREE_END -->

## 📜 License

[License Information Here]