import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_metrics():
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
        # Maybe it's TinyDB default table?
        default = data.get("_default", {})
        if default:
            workflows = default
            logger.info(f"Using _default table with {len(workflows)} items")
        else:
             logger.warning("No 'workflows' or '_default' table found.")

    found_metrics = 0
    total_items = 0

    for key, val in workflows.items():
        total_items += 1
        # Check context_variables
        context = val.get("context_variables", {})
        metrics = context.get("audit_metrics")

        if metrics:
            found_metrics += 1
            logger.info(f"[metrics found] ID: {val.get('id', key)} | Words: {metrics.get('word_count')} | Sentences: {metrics.get('sentence_count')}")
        else:
            # Check root level just in case
            if "audit_metrics" in val:
                 found_metrics += 1
                 m = val["audit_metrics"]
                 logger.info(f"[metrics found (root)] ID: {val.get('id', key)} | Words: {m.get('word_count')}")

    logger.info(f"Scan Complete. Found metrics in {found_metrics}/{total_items} workflows.")

if __name__ == "__main__":
    check_metrics()
