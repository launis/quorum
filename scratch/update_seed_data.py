import json

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"
TARGET_STRING = "REQUIRED TARGET: EXTRACTION CONDITION: role prefixes exist, target 'ai:' block. BANNED SOURCES: 'user:' blocks. "

CHAT_LOG_INSTRUCTION = """--- AI INSTRUCTION FOR THIS SOURCE (chat_log) ---
PROCESS EVIDENCE DIRECTIVE: This artifact contains the chronological dialogue unspooled between the human operator and the AI system leading up to the final product. You must analyze this strictly for developmental trajectory, cognitive dependencies, prompt compliance, and the balance of intellectual labor. Do not treat this as the final product itself, but rather the scaffolding that built it.

MANDATE_HUMAN_EVALUATION: You must evaluate ONLY the human user's cognitive level, steering skills, and domain expertise. 

EXTRACTION_RULE: You MUST extract 'exact_quote' evidence STRICTLY from lines starting with "user:". 

CONTEXT_RULE: Text starting with "ai:" is strictly background context. NEVER use the AI's output, intelligence, or reasoning as evidence of the human's competence."""

def update_seed_data():
    with open(SEED_FILE, encoding='utf-8') as f:
        data = json.load(f)

    # 1. Update chat_log ai_description recursively
    chat_log_updated = False
    def update_chat_log_description(obj):
        nonlocal chat_log_updated
        if isinstance(obj, dict):
            if obj.get("input_key") == "chat_log":
                obj["ai_description"] = CHAT_LOG_INSTRUCTION
                chat_log_updated = True
            for k, v in obj.items():
                update_chat_log_description(v)
        elif isinstance(obj, list):
            for item in obj:
                update_chat_log_description(item)

    update_chat_log_description(data)

    # 2. Recursively remove the TARGET_STRING from all string values
    def recursive_remove(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, str):
                    if TARGET_STRING in v:
                        obj[k] = v.replace(TARGET_STRING, "")
                else:
                    recursive_remove(v)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                if isinstance(obj[i], str):
                    if TARGET_STRING in obj[i]:
                        obj[i] = obj[i].replace(TARGET_STRING, "")
                else:
                    recursive_remove(obj[i])

    recursive_remove(data)

    # Write back
    with open(SEED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Seed data updated.")
    print(f"Chat log updated: {chat_log_updated}")

if __name__ == "__main__":
    update_seed_data()
