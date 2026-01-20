
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.database.repository import TinyDBRepository
from backend.api.bff_transformer import ReportTransformer
from backend.models.view import SectionType

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")

from tinydb import TinyDB

async def main():
    print("=== STARTING BULK REPORT VERIFICATION ===")
    
    try:
        db_instance = TinyDB("data/db.json")
        repo = TinyDBRepository(db_instance)
        transformer = ReportTransformer()
        
        executions = await repo.get_all_executions()
        print(f"Found {len(executions)} executions in database.")
        
        success_count = 0
        failure_count = 0
        empty_dims_count = 0
        
        for exc in executions:
            exc_id = exc.get('id')
            
            # --- Emulate Router Logic for Scale Resolution ---
            # 1. Default
            scale_limit = (1.0, 4.0)
            
            # 2. Heuristic (simplified from router)
            judge_step = None
            results = exc.get("results", {})
            if "step_results" in results: steps = results["step_results"]
            else: steps = results
            
            if isinstance(steps, dict):
                 judge_step = steps.get("step_judge") or steps.get("step_judge_cognitive")
            
            raw_score = 0.0
            if judge_step:
                 val = judge_step.get("total_score") or judge_step.get("pisteet")
                 try: 
                     raw_score = float(val) if val is not None else 0.0
                 except: pass
            
            # Check DB for Matrix? (For this test, let's rely on the Heuristic which is the "safety net")
            # If score > 5, use 0-100
            if raw_score > 5.0:
                 scale_limit = (0.0, 100.0)
            
            # --- Transform ---
            try:
                view = transformer.transform(exc, valid_range=scale_limit)
                
                # Check for ScoreCard
                sc_cards = [s for s in view.sections if s.type == SectionType.SCORE_CARD]
                
                if not sc_cards:
                     print(f"[WARN] {exc_id}: No ScoreCards found.")
                
                # Check Analyst (DATA_TABLE)
                tables = [s for s in view.sections if s.type == SectionType.DATA_TABLE]
                for t in tables:
                    if not t.data.get("rows"):
                        print(f"[FAIL-CONTENT] {exc_id}: Analyst Table '{t.title}' exists but has NO ROWS.")
                    else:
                        success_count += 1 # Counting valid sections found
                
                # Check Profiler (KEY_VALUE_GRID)
                grids = [s for s in view.sections if s.type == SectionType.KEY_VALUE_GRID]
                for g in grids:
                    if not g.data.get("items"):
                        print(f"[FAIL-CONTENT] {exc_id}: Profiler Grid '{g.title}' exists but has NO ITEMS.")
                    else:
                        success_count += 1

                # Check ScoreCard Dimensions (Existing logic)
                for card in sc_cards:
                     data = card.data
                     dims = data.get("dimensions", [])
                     if dims:
                         success_count += 1
                     else:
                         empty_dims_count += 1
                         print(f"[FAIL-DIMS] {exc_id}: ScoreCard exists but dimensions empty! (Score: {raw_score})")
                         if judge_step:
                             print(f"DEBUG: judge_step keys: {list(judge_step.keys())}")
                             if "perustelut" in judge_step:
                                 print(f"DEBUG: perustelut type: {type(judge_step.get('perustelut'))}")
                                 print(f"DEBUG: perustelut content: {judge_step.get('perustelut')}")
                         if judge_step:
                             print(f"DEBUG: judge_step keys: {list(judge_step.keys())}")
                             if "perustelut" in judge_step:
                                 print(f"DEBUG: perustelut type: {type(judge_step.get('perustelut'))}")
                                 print(f"DEBUG: perustelut content: {judge_step.get('perustelut')}")

            except Exception as e:
                failure_count += 1
                print(f"[CRASH] {exc_id}: Transformation failed! Error: {e}")
                
        print("\n=== VERIFICATION SUMMARY ===")
        print(f"Total: {len(executions)}")
        print(f"Success (Valid Reports): {success_count}")
        print(f"Empty Dimensions: {empty_dims_count}")
        print(f"Crashes: {failure_count}")
        
    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
