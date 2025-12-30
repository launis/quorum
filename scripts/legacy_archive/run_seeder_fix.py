
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from backend.database.seeder import seed_database
    print("Starting database seed...")
    seed_database()
    print("Database seed completed successfully.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
