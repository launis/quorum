import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("c:/src/quorum/data/db.json")

def update_judge_inputs():
    if not DB_PATH.exists():
        logger.error(f"Database file not found at {DB_PATH}")
        return

    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        
        # 1. Update 'sequential_audit_chain' (ID: "1")
        workflow_1 = data.get("workflows", {}).get("1")
        if workflow_1:
            steps = workflow_1.get("steps", [])
            for step in steps:
                if step.get("id") == "step_judge":
                    logger.info("Found step_judge in workflow 1. Updating inputs...")
                    current_inputs = step.get("inputs", {})
                    
                    # Add missing mappings for sequential chain
                    new_mappings = {
                        "step_profiler": "$step_profiler",
                        "step_logician": "$step_logician",
                        "step_falsifier": "$step_falsifier",
                        "step_causal": "$step_causal",
                        "step_detector": "$step_detector",
                        "step_overseer": "$step_overseer",
                        "step_archivist": "$step_archivist"
                    }
                    
                    current_inputs.update(new_mappings)
                    step["inputs"] = current_inputs
                    logger.info(f"Updated inputs for step_judge: {list(current_inputs.keys())}")
        
        # 2. Update 'sequential_audit_chain_cognitive' (ID: "3") - likely same structure
        workflow_3 = data.get("workflows", {}).get("3")
        if workflow_3:
            steps = workflow_3.get("steps", [])
            for step in steps:
                if step.get("id") == "step_judge_cognitive" or step.get("task_key") == "judge":
                    logger.info("Found judge step in workflow 3. Updating inputs...")
                    current_inputs = step.get("inputs", {})
                    
                    # Add missing mappings
                    new_mappings = {
                        "step_profiler": "$step_profiler",
                        "step_logician": "$step_logician",
                        "step_falsifier": "$step_falsifier",
                        "step_causal": "$step_causal",
                        "step_detector": "$step_detector",
                        "step_overseer": "$step_overseer",
                        "step_archivist": "$step_archivist"
                    }
                     
                    current_inputs.update(new_mappings)
                    step["inputs"] = current_inputs
                    logger.info(f"Updated inputs for judge step in workflow 3")

        # 3. Update 'sequential_audit_chain_dual' (ID: "5")
        workflow_5 = data.get("workflows", {}).get("5")
        if workflow_5:
            steps = workflow_5.get("steps", [])
            for step in steps:
                 if step.get("id") == "step_judge" or step.get("task_key") == "judge":
                    logger.info("Found judge step in workflow 5. Updating inputs...")
                    current_inputs = step.get("inputs", {})
                    # Add missing mappings
                    new_mappings = {
                        "step_profiler": "$step_profiler",
                        "step_logician": "$step_logician",
                        "step_falsifier": "$step_falsifier",
                        "step_causal": "$step_causal",
                        "step_detector": "$step_detector",
                        "step_overseer": "$step_overseer",
                        "step_archivist": "$step_archivist"
                    }
                    current_inputs.update(new_mappings)
                    step["inputs"] = current_inputs 

        # Write back to file
        DB_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")
        logger.info("Successfully updated db.json")

    except Exception as e:
        logger.error(f"Failed to update db.json: {e}")

if __name__ == "__main__":
    update_judge_inputs()
