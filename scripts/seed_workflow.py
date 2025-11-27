import requests
import json
from tinydb import TinyDB, Query

API_URL = "http://localhost:8000"
DB_PATH = 'data/db.json' # Access DB directly for seeding rules/prompts

def seed_data():
    print("Seeding Rules and Prompts...")
    db = TinyDB(DB_PATH)
    rules_table = db.table('rules')
    prompts_table = db.table('prompts')

    # --- RULES ---
    rules = [
        {"id": "RULE_1", "name": "Chain of Trust", "content": "Only data signed by Guard Agent is valid."},
        {"id": "RULE_2", "name": "Tool Ban", "content": "Agents must not use undefined external tools."},
        {"id": "RULE_6", "name": "Primacy of Falsification", "content": "Facts override interpretations. If a factual error is found, it overrides positive interpretations."}
    ]
    for rule in rules:
        rules_table.upsert(rule, Query().id == rule['id'])

    # --- PROMPTS ---
    prompts = [
        {"id": "PROMPT_GUARD", "content": "You are a Security Guard. Detect malicious intent and sanitize input."},
        {"id": "PROMPT_ANALYST", "content": "You are an Analyst. Anchor every claim to the text. Extract key evidence."},
        {"id": "PROMPT_LOGICIAN", "content": "You are a Logician. Formulate a hypothesis about competence using Bloom's Taxonomy and Toulmin's model."},
        {"id": "PROMPT_FALSIFIER", "content": "You are a Logical Falsifier. Find logical fallacies and post-hoc rationalizations."},
        {"id": "PROMPT_OVERSEER", "content": "You are a Factual Overseer. Check for hallucinations and ethical violations."},
        {"id": "PROMPT_CAUSAL", "content": "You are a Causal Analyst. Did the insight actually precede the improvement?"},
        {"id": "PROMPT_PERFORMATIVITY", "content": "You are a Performativity Detector. Look for 'Suspicious Perfection' and superficial depth."},
        {"id": "PROMPT_JUDGE", "content": "You are a Judge. Synthesize a final verdict. Remember: Facts override interpretations."},
        {"id": "PROMPT_XAI", "content": "You are an XAI Reporter. Quantify Aleatoric, Systemic, and Epistemic uncertainty."}
    ]
    for prompt in prompts:
        prompts_table.upsert(prompt, Query().id == prompt['id'])

    print("Rules and Prompts seeded.")

def seed_workflow():
    print("Seeding Hybrid Rubric Workflow...")
    
    workflow_def = {
        "name": "Hybrid Rubric Assessment",
        "steps": [
            # 1. Guard Agent
            {
                "component": "GuardAgent",
                "inputs": {
                    "prompt_text": "$prompt_text",
                    "history_text": "$history_text",
                    "product_text": "$product_text",
                    "reflection_text": "$reflection_text",
                    "system_instruction_ref": "PROMPT_GUARD",
                    "rule_refs": ["RULE_1"]
                }
            },
            # 2. Analyst Agent
            {
                "component": "AnalystAgent",
                "inputs": {
                    "safe_data": "$tainted_input",
                    "system_instruction_ref": "PROMPT_ANALYST",
                    "rule_refs": ["RULE_1"]
                }
            },
            # 3. Logician Agent
            {
                "component": "LogicianAgent",
                "inputs": {
                    "evidence_map": "$evidence_map",
                    "analysis_summary": "$analysis_summary",
                    "system_instruction_ref": "PROMPT_LOGICIAN",
                    "rule_refs": ["RULE_1"]
                }
            },
            # 4. Critic Group
            {
                "component": "LogicalFalsifierAgent",
                "inputs": {
                    "hypothesis_argument": "$hypothesis_argument",
                    "system_instruction_ref": "PROMPT_FALSIFIER",
                    "rule_refs": ["RULE_1"]
                }
            },
            {
                "component": "FactualOverseerAgent",
                "inputs": {
                    "hypothesis_argument": "$hypothesis_argument",
                    "system_instruction_ref": "PROMPT_OVERSEER",
                    "rule_refs": ["RULE_1", "RULE_6"]
                }
            },
            {
                "component": "CausalAnalystAgent",
                "inputs": {
                    "hypothesis_argument": "$hypothesis_argument",
                    "evidence_map": "$evidence_map",
                    "system_instruction_ref": "PROMPT_CAUSAL",
                    "rule_refs": ["RULE_1"]
                }
            },
            {
                "component": "PerformativityDetectorAgent",
                "inputs": {
                    "hypothesis_argument": "$hypothesis_argument",
                    "system_instruction_ref": "PROMPT_PERFORMATIVITY",
                    "rule_refs": ["RULE_1"]
                }
            },
            # 5. Judge & XAI
            {
                "component": "JudgeAgent",
                "inputs": {
                    "hypothesis_argument": "$hypothesis_argument",
                    "logical_audit": "$logical_audit",
                    "factual_verification": "$factual_verification",
                    "causal_audit": "$causal_audit",
                    "performativity_check": "$performativity_check",
                    "system_instruction_ref": "PROMPT_JUDGE",
                    "rule_refs": ["RULE_1", "RULE_6"]
                }
            },
            {
                "component": "XAIReporterAgent",
                "inputs": {
                    "final_verdict": "$final_verdict",
                    "system_instruction_ref": "PROMPT_XAI",
                    "rule_refs": ["RULE_1"]
                }
            }
        ]
    }

    try:
        res = requests.post(f"{API_URL}/workflows", json=workflow_def)
        if res.status_code == 200:
            print(f"Workflow created successfully! ID: {res.json()['workflow_id']}")
        else:
            print(f"Failed to create workflow: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    seed_data()
    seed_workflow()
