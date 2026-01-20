
import json
from tinydb import TinyDB, Query
import logging

# Setup
db_path = "data/db.json"
db = TinyDB(db_path)
components_table = db.table("components")
logger = logging.getLogger("restore_matrix")
logging.basicConfig(level=logging.INFO)

def restore_matrix():
    # Definition for the missing matrix
    # ID: Kognitiivinen Quorum Unified Matrix (Using name as ID for legacy)
    # Scale: 0-100 (inferred from score 93.3)
    
    matrix_id = "Kognitiivinen Quorum Unified Matrix"
    
    # Check if exists
    Component = Query()
    existing = components_table.search(Component.id == matrix_id)
    
    if existing:
        logger.info(f"Matrix '{matrix_id}' already exists. Skipping.")
        return

    new_matrix = {
        "id": matrix_id,
        "type": "matrix",
        "name": "Kognitiivinen Quorum Unified Matrix",
        "description": "Legacy matrix restored for data integrity.",
        "content": {
            "scale": {
                "min": 0,
                "max": 100,
                "label_min": "Low",
                "label_max": "High"
            },
            "dimensions": [
                {"id": "relevance", "label": "Relevanssi", "weight": 1.0},
                {"id": "accuracy", "label": "Tarkkuus", "weight": 1.0},
                {"id": "clarity", "label": "Selkeys", "weight": 1.0}
            ]
        },
        "version": "1.0-legacy"
    }
    
    components_table.insert(new_matrix)
    logger.info(f"Successfully restored matrix: {matrix_id} with scale [0-100]")

if __name__ == "__main__":
    restore_matrix()
