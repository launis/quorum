from fastapi import APIRouter, HTTPException, Body
from backend.seeder import seed_database
from tinydb import TinyDB
import os

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/reset")
async def reset_system(reseed: bool = Body(True, embed=True)):
    """
    Resets the system by clearing the database and optionally re-seeding it.
    WARNING: This deletes all execution history!
    """
    try:
        # Resolve DB path (same logic as in main.py/seeder.py)
        # Ideally this should be a shared constant
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        DATA_DIR = os.path.join(BASE_DIR, 'data')
        DB_PATH = os.path.join(DATA_DIR, 'db.json')
        
        # 1. Clear Database
        db = TinyDB(DB_PATH)
        db.drop_tables()
        db.close()
        
        message = "Database cleared."
        
        # 2. Re-seed if requested
        if reseed:
            seed_database()
            message += " System re-seeded successfully."
            
        return {"status": "success", "message": message}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
