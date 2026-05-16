import json
import logging

logging.basicConfig(filename=r'c:\src\quorum\scratch\debug.log', level=logging.INFO)

path = r"c:\src\quorum\data\db_v2.json"
with open(path, "r", encoding="utf-8") as f:
    db = json.load(f)

# Find execution step sr_5f3dd7712a7f4bb3 in executions
for exec_id, exec_data in db.get("executions", {}).items():
    if "sr_5f3dd7712a7f4bb3" in exec_data.get("step_states", {}):
        logging.info(f"Found execution: {exec_id}")
        # Look for the step blueprint
        steps = db.get("steps", {})
        blueprint = steps.get("sp_192910b5f5a34c79")
        if blueprint:
            logging.info(f"Blueprint prompt blocks: {blueprint.get('prompt_blocks')}")
            for pb_id in blueprint.get('prompt_blocks', []):
                pb = db.get("prompt_blocks", {}).get(pb_id, {})
                logging.info(f"  Block {pb_id}: persona={pb.get('execution_persona')} label={pb.get('label')}")
        else:
            logging.info("Blueprint sp_192910b5f5a34c79 not found in db_v2.json")
