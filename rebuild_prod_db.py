import sys
import os
import traceback

# Add current directory to path
sys.path.append(os.getcwd())

def main():
    try:
        from backend.database.seeder import seed_database
        
        # EXPLICITLY define the PROD path
        # Assuming standard location
        prod_db_path = os.path.join("data", "db.json")
        print(f"Targeting PROD DB at: {prod_db_path}")
        
        # Seed explicitly
        seed_database(target_db_path=prod_db_path)
        
        print("Explicit Seeding to PROD DB Completed.")
        
    except Exception:
        with open("error_prod.log", "w") as f:
            traceback.print_exc(file=f)
        print("Rebuild Failed! Check error_prod.log")

if __name__ == "__main__":
    main()
