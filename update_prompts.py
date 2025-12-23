
import logging
from tinydb import TinyDB, Query
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_database(db_path: str, seed_path: str):
    logger.info(f"Updating database: {db_path}")
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return

    try:
        db = TinyDB(db_path)
        components_table = db.table('components')
        
        # Load seed data
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
            
        # Find GLOBAL_CONTEXT in seed
        new_context = None
        for comp in seed_data.get('components', []):
            if comp.get('id') == 'GLOBAL_CONTEXT':
                new_context = comp
                break
        
        if not new_context:
            logger.error("GLOBAL_CONTEXT not found in seed_data!")
            return

        # Update in DB
        Component = Query()
        # Check if exists
        existing = components_table.search(Component.id == 'GLOBAL_CONTEXT')
        
        if existing:
            # Update content content
            components_table.update(
                {'content': new_context['content']}, 
                Component.id == 'GLOBAL_CONTEXT'
            )
            logger.info("Successfully updated GLOBAL_CONTEXT content in existing record.")
        else:
            # Insert if missing
            components_table.insert(new_context)
            logger.info("GLOBAL_CONTEXT missing, inserted new record.")

        logger.info(f"Database {db_path} update complete.\n")

    except Exception as e:
        logger.error(f"Failed to update {db_path}: {e}")

if __name__ == "__main__":
    SEED_PATH = r"c:\Users\risto\OneDrive\quorum\backend\database\seed_data.json"
    
    # List of DBs to update (Production and potentially Mock/Test/Dev if they verify)
    # Based on your previous context, real DB is at data/db.json
    # Mock DB is usually data/db_mock.json
    
    dbs_to_update = [
        r"c:\Users\risto\OneDrive\quorum\data\db.json",
        r"c:\Users\risto\OneDrive\quorum\data\db_mock.json" 
    ]

    for db in dbs_to_update:
        update_database(db, SEED_PATH)
