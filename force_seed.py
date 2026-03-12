import asyncio
from backend_v2.seed.seed_registry import run_all_seeds

if __name__ == "__main__":
    print("Running seeds...")
    asyncio.run(run_all_seeds(mock=True))
    print("Seeding complete.")
