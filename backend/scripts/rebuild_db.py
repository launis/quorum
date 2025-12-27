import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

def main():
    try:
        from backend.services.administration_service import AdministrationService
        from backend.database.wrapper import get_db_client
        from backend.database.repository import WorkflowRepository, AbstractWorkflowRepository
        from backend.services.progress import InMemoryProgressTracker

        print("Initializing DB Client...")
        db = get_db_client()
        print(f"Connected to DB: {db}")
        
        def tracker_callback(payload):
            print(f"TRACKER: {payload}")
            
        repo = WorkflowRepository(db)
        service = AdministrationService(repo)
        tracker = InMemoryProgressTracker(callback=tracker_callback)
        
        print("Starting Rebuild from seed_data.json...")
        result = service.rebuild_database(tracker)
        print("Rebuild Result:", result)
        
    except Exception:
        with open("error.log", "w") as f:
            traceback.print_exc(file=f)
        print("Rebuild Failed! Check error.log")

if __name__ == "__main__":
    main()
