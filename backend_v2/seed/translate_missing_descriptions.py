import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
SEED_DATA_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

MISSING_MAP = {
    # Matrices
    "matrix_toulmin": "Evaluates the quality of an argument using the Toulmin model.",
    "matrix_bloom": "Evaluates cognitive depth using Bloom's Taxonomy.",
    "matrix_kahneman": "Evaluates the speed and depth of cognitive processing using System 1/System 2.",
    "matrix_goodhart": "Evaluates whether the user acts as a driver or a passenger in the interaction.",
    "matrix_input_processing": "Evaluates how thoroughly the user analyzes provided inputs.",
    "matrix_archivist": "Evaluates compliance with organizational standards and precedent.",
    "matrix_causal_analyst": "Evaluates causal direction and guidance quality.",
    "matrix_falsifier": "Evaluates active testing and falsification of AI assumptions.",
    "matrix_judge": "Synthesizes multi-agent evaluations into a final verdict.",
    "matrix_xai_reporter": "Evaluates the transparency and clarity of the decision-making report.",
    "matrix_taskguard": "Evaluates adherence to security and input guardrails.",
    "matrix_causal_abductive": "Evaluates abductive reasoning patterns in the data.",

    # Roles
    "block_role_analyst": "Analyst role for systematic evidence breakdown.",
    "block_role_coach": "Coach role for providing constructive feedback and remediation.",
    "block_role_guard": "Guard role for enforcing security and ethical constraints.",
    "block_role_logician": "Logician role for evaluating deductive and inductive validity.",
    "block_role_overseer": "Overseer role for coordinating multi-agent workflows.",
    "block_role_profiler": "Profiler role for analyzing cognitive and behavioral patterns.",

    # Tasks
    "block_taskanalyst": "Task definition for systematic evidence breakdown.",
    "block_taskprofiler": "Task definition for behavioral profiling and cognitive analysis.",
    "block_tasklogician": "Task definition for logical deconstruction.",
    "block_taskfalsifier": "Task definition for rigorous hypothesis testing.",
    "block_taskoverseer": "Task definition for workflow oversight and aggregation.",
    "block_taskcausal": "Task definition for establishing causal pathways.",

    # Headers and Instructions
    "block_headermandates": "Header for overarching system mandates.",
    "block_instructionstrictscale": "Rules for calibrating strictness scaling.",
    "block_headerrules": "Header for core operational rules.",
    "block_headerprotocols": "Header for execution protocols.",
    "block_headerinstructions": "Header for execution instructions.",
    "block_mandate2": "Mandate enforcing source adherence.",
    "block_mandate3": "Mandate demanding absolute empirical grounding.",
    "block_mandate5": "Mandate enforcing logical consistency.",
    "block_rule1": "Rule enforcing strict operational boundaries.",
    "block_rule2": "Rule enforcing chronological processing sequences.",
    "block_rule3": "Rule enforcing validation before assumption.",
    "block_rule4": "Rule enforcing clarity and precision in outputs.",
    "block_rule5": "Rule enforcing objective separation of facts from opinions.",
    "block_rule6": "Rule mandating comprehensive fallback handling.",
    "block_globalcontext": "Establishes the global execution constraints and context.",
    "block_oprule1": "Operational Rule 1: Maintain scope boundaries.",
    "block_oprule2": "Operational Rule 2: Force explicit citation mapping.",
    "block_oprule3": "Operational Rule 3: Demand active user engagement.",
    "block_oprule4": "Operational Rule 4: Neutralize inherent biases.",
    "block_instructionnohallucination": "Strict instruction to prevent hallucinations.",
    "block_instructioncitationobligation": "Obligation to cite exact sources for claims.",
    "block_instructionnodataleak": "Instruction to prevent data leakage across sessions.",
    "block_instructionbiblicalgrounding": "Instruction to use foundational text as truth anchor.",
    "block_instructionlanguage_dynamic": "Instruction for dynamic output language adaptation."
}

def clean_missing():
    logging.info(f"Loading seed data from {SEED_DATA_PATH}")
    with open(SEED_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    count = 0

    for block in prompt_blocks:
        slug = block.get("slug")
        desc_en = block.get("description", {}).get("translations", {}).get("en", "")
        desc_fi = block.get("description", {}).get("translations", {}).get("fi", "")
        
        # Strip generic (EN) or [EN] suffixes off the fi
        if desc_fi:
            clean_fi = desc_fi.replace("(EN)", "").replace("[EN]", "").strip()
            block["description"]["translations"]["fi"] = clean_fi
            
        # Also let's clean the FI if it has "ROOLI:" inside it despite not being heavily contaminated
        if "ROOLI:" in block["description"]["translations"]["fi"]:
             first_sentence = block["description"]["translations"]["fi"].split(".")[0]
             block["description"]["translations"]["fi"] = first_sentence.replace("ROOLI:", "Rooli:").strip()

        # If it was unmapped or matching FI exactly:
        if slug in MISSING_MAP:
            block["description"]["translations"]["en"] = MISSING_MAP[slug]
            count += 1
            
    if count > 0:
        with open(SEED_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Cleanup complete. Replaced {count} descriptions.")
    else:
        logging.info("No descriptions needed cleaning.")

if __name__ == "__main__":
    clean_missing()
