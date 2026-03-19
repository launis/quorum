import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

ROLE_MANDATE = "\n\nCRITICAL MANDATE: Embody this persona with absolute, unwavering strictness. Do not break character, do not soften your stance, and falsify immediately any claim that does not meet the highest standards of this role."
RULE_MANDATE = "\n\nCRITICAL ENFORCEMENT: Zero tolerance for deviation from this rule. Any failure to adhere to this protocol must result in immediate and severe penalization of the output."
TASK_MANDATE = "\n\nCRITICAL TASK OBLIGATION: Execute this task with surgical precision. Hallucinations, pleasantries, or superficial responses will be treated as catastrophic failures."

def tighten_other_rules():
    logging.info(f"Loading data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for block in data.get("prompt_blocks", []):
        cat = block.get("category_id")
        desc = block.get("ai_description", "")

        if not desc:
            continue

        suffix = ""
        if cat == "agent_role":
            suffix = ROLE_MANDATE
        elif cat in ["system_rule", "protocol"]:
            suffix = RULE_MANDATE
        elif cat == "task_definition":
            suffix = TASK_MANDATE

        if suffix and suffix.strip() not in desc:
            block["ai_description"] = desc + suffix
            count += 1

    if count > 0:
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Successfully tightened {count} rules/roles/tasks.")
    else:
        logging.info("No blocks needed tightening.")

if __name__ == "__main__":
    tighten_other_rules()
