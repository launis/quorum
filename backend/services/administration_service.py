import os
import json
import logging
import re
import datetime
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.database.repository import AbstractWorkflowRepository
from backend.services.progress import ProgressTracker
# from backend.config import DATA_DIR, SCRIPTS_DIR # Removed

# Hardcoded rules source from original script

class AdministrationService:
    def __init__(self, repository: AbstractWorkflowRepository):
        self.repository = repository



    def export_seed_data(self, tracker: ProgressTracker) -> Dict[str, Any]:
        """
        Exports the current DB configuration to seed_data.json
        """
        from backend.database.exporter import export_db_to_files
        
        tracker.start({"operation": "Export Seed Data"})
        try:
             # Use the exporter module
             tracker.update("Exporting Workflows & components...", 10)
             # By default uses settings.start_db_path which is correct for current env
             result = export_db_to_files() 
             tracker.update("Export Completed", 100)
             
             final_res = {"status": "completed", "message": result.get("message", "Export done")}
             tracker.complete(final_res)
             return final_res
        except Exception as e:
            tracker.fail(str(e))
            raise e

    def rebuild_database(self, tracker: ProgressTracker) -> Dict[str, Any]:
        """
        Rebuilds database using the centralized seeder.
        """
        from backend.database.seeder import seed_database
        
        tracker.start({"operation": "Rebuild Database"})
        try:
             # Use the seeder internally. It will use the configured DB path from backend.config.
             # This ensures we respect the current environment (Mock vs Prod).
             tracker.update("Seeding Database", 10)
             seed_database() 
             tracker.update("Seeding Completed", 100)
             
             result = {"status": "completed", "message": "Database rebuilt from seed_data.json"}
             tracker.complete(result)
             return result
        except Exception as e:
            tracker.fail(str(e))
            raise e
