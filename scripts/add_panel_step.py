from tinydb import TinyDB, Query
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')
db = TinyDB(DB_PATH, encoding='utf-8')
steps_table = db.table('steps')

panel_step = {
    "id": "STEP_CRITICS_PANEL",
    "name": "Combined Critics Panel",
    "component": "PanelAgent",
    "description": "Executes Logical, Causal, Performativity, and Factual analysis in a single LLM call.",
    "input_schema": "TodistusKartta",
    "output_schema": "AuditResults",
    "execution_config": {
        "llm_prompts": [
            "PROMPT_LOGICIAN",
            "PROMPT_FALSIFIER",
            "PROMPT_CAUSAL",
            "PROMPT_PERFORMATIVITY",
            "PROMPT_FACT_CHECKER"
        ],
        "post_hooks": []
    }
}

Step = Query()
if not steps_table.search(Step.id == "STEP_CRITICS_PANEL"):
    steps_table.insert(panel_step)
    print("Added STEP_CRITICS_PANEL to database.")
else:
    steps_table.update(panel_step, Step.id == "STEP_CRITICS_PANEL")
    print("Updated STEP_CRITICS_PANEL in database.")
