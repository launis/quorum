import json
import os

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

DIRECTIVES = {
    "product_text": "SOURCE EVIDENCE DIRECTIVE: This artifact represents the final target output of the audited process. It must be evaluated strictly on its own merits without assuming any external context or hidden intentions. Treat this as the definitive end-result of the cognitive process.",
    "chat_log": "PROCESS EVIDENCE DIRECTIVE: This artifact contains the chronological dialogue unspooled between the human operator and the AI system leading up to the final product. You must analyze this strictly for developmental trajectory, cognitive dependencies, prompt compliance, and the balance of intellectual labor. Do not treat this as the final product itself, but rather the scaffolding that built it.",
    "reflection_text": "META-COGNITIVE EVIDENCE DIRECTIVE: This artifact contains the human operator's post-hoc reflection on the interaction. Analyze this to establish the operator's self-awareness, critical distance, and theoretical grounding regarding the process. Evaluate if the reflection aligns transparently with the actual events logged in the chat history."
}

def apply_mutations():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    mutated = False
    for workflow in data.get("workflows", []):
        if workflow.get("slug") == "kokonaisvaltainen_auditointi":
            inputs = workflow.get("expected_inputs", [])
            for inp in inputs:
                k = inp.get("input_key")
                if k in DIRECTIVES:
                    inp["ai_description"] = DIRECTIVES[k]
                    mutated = True
                    print(f"[MUTATOR] Successfully injected {k} directive.")

    if mutated:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("[MUTATOR] Target workflow updated and file written successfully.")
    else:
        print("[MUTATOR] No targets found or mutated.")

if __name__ == "__main__":
    apply_mutations()
