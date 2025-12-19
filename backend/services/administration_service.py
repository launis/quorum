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
from backend.config import DATA_DIR, SCRIPTS_DIR

# Hardcoded rules source from original script

class AdministrationService:
    def __init__(self, repository: AbstractWorkflowRepository):
        self.repository = repository

    def import_references(self, tracker: ProgressTracker) -> Dict[str, Any]:
        """
        Imports References from data/bibliography.txt
        """
        tracker.start({"operation": "Import References"})
        bib_path = os.path.join(DATA_DIR, 'bibliography.txt')
        
        try:
            if not os.path.exists(bib_path):
                raise FileNotFoundError(f"Bibliography file not found: {bib_path}")

            tracker.update("Reading File", 10)
            with open(bib_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total_lines = len(lines)
            processed = 0
            imported = 0

            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Simple Parse
                parts = line.split('. ', 2)
                if len(parts) >= 2:
                    author_part = parts[0]
                    year_match = re.search(r'(\d{4})', line)
                    year = year_match.group(1) if year_match else "Unknown"
                    author_slug = author_part.split(',')[0].split(' ')[0].upper()
                    
                    ref_id = f"REF_{author_slug}_{year}"
                    
                    ref_comp = {
                        "id": ref_id,
                        "type": "reference",
                        "content": line,
                        "citation": f"({author_part.split(',')[0]} {year})",
                        "name": f"Ref: {author_part.split(',')[0]} {year}",
                        "description": "Bibliographic Reference",
                        "module": "config",
                        "class": "ConfigComponent"
                    }
                    
                    # Upsert using repository methods
                    # Check if repository supports add_component (it should)
                    # Note: Original code used update_component/add_component
                    if hasattr(self.repository, 'get_component_by_id'):
                         existing = self.repository.get_component_by_id(ref_id)
                         if existing:
                             if hasattr(self.repository, 'update_component'):
                                self.repository.update_component(ref_id, ref_comp)
                         else:
                             if hasattr(self.repository, 'add_component'):
                                self.repository.add_component(ref_comp)
                    
                    imported += 1
                
                processed += 1
                if total_lines > 0 and processed % 10 == 0:
                    percent = 10 + int((processed / total_lines) * 80)
                    tracker.update(f"Importing {processed}/{total_lines}", percent)
            
            result = {"status": "completed", "imported": imported}
            tracker.complete(result)
            return result
            
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
