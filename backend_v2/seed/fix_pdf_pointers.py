import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    db_path = 'c:/src/quorum/data/db_v2.json'
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    executions = db.get('executions', {})
    changed = False
    
    for exe_id, data in executions.items():
        rsp = data.get("results_storage_path")
        if rsp and isinstance(rsp, str) and rsp.endswith(".pdf"):
            logger.info(f"Fixing corrupted storage path for {exe_id}: renamed {rsp} to pdf_report_path and deleted results_storage_path.")
            data["pdf_report_path"] = rsp
            del data["results_storage_path"]
            changed = True
            
    if changed:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        logger.info("Successfully patched db_v2.json for pdf storage paths.")
    else:
        logger.info("No corrupt PDF storage paths found in db_v2.json")

if __name__ == '__main__':
    run()
