import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_inputs():
    db_path = "data/db.json"
    if not os.path.exists(db_path):
        logger.error(f"DB file not found at {db_path}")
        return

    try:
        with open(db_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read DB: {e}")
        return

    # Inspect structure
    workflows = data.get("workflows", {})
    if not workflows:
        default = data.get("_default", {})
        if default:
            workflows = default

    total_items = 0
    items_with_inputs = 0
    items_with_history = 0

    for key, val in workflows.items():
        total_items += 1
        ctx = val.get("context_variables", {})
        inputs = ctx.get("inputs")

        has_inputs = False
        has_history = False

        if inputs and isinstance(inputs, dict):
            has_inputs = True
            items_with_inputs += 1
            if inputs.get("history_text"):
                has_history = True
                items_with_history += 1

        metrics = ctx.get("audit_metrics")

        logger.info(f"ID: {key} | Inputs: {has_inputs} | History: {has_history} | Metrics: {metrics is not None}")
        if not has_inputs:
             logger.info(f"  -> Context Keys: {list(ctx.keys())}")

    logger.info(f"Stats: Total={total_items}, WithInputs={items_with_inputs}, WithHistory={items_with_history}")

if __name__ == "__main__":
    check_inputs()
