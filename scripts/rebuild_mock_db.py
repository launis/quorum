import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

def main():
    try:
        from backend.services.administration_service import AdministrationService
        from backend.database.wrapper import get_db_client
        from backend.database.repository import WorkflowRepository
        from backend.services.progress import InMemoryProgressTracker
        from backend.database.seeder import seed_database
        
        # EXPLICITLY define the mock path
        mock_db_path = os.path.join("backend", "database", "db_mock.json")
        print(f"Targeting MOCK DB at: {mock_db_path}")
        
        # We can bypass the service and call seeder directly for total control
        seed_database(target_db_path=mock_db_path)
        
        print("Explicit Seeding to MOCK DB Completed.")
        
    except Exception:
        with open("error.log", "w") as f:
            traceback.print_exc(file=f)
        print("Rebuild Failed! Check error.log")

if __name__ == "__main__":
    main()
