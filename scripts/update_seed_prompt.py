import json
import os

files = [
    r"c:\src\quorum\backend_v2\seed\seed_data.json",
    r"c:\src\quorum\backend_v2\seed\seed_data_pretty.json"
]

target_text = "PARAGRAPH 2 (The Interaction Role): You MUST start this paragraph by explicitly highlighting the user's assigned interaction role (e.g., \"**Käyttäjän Rooli: Arkkitehti**\"). Following this, provide a concrete justification for why this specific role (from Passenger to Architect) was assigned based on the control ratio and their cognitive initiative in the current execution. Show exactly which user sentence reflects this role."
replacement_text = "PARAGRAPH 2 (The Interaction Role): You MUST start this paragraph by explicitly highlighting the user's assigned interaction role using EXACTLY the raw enum value from the data (e.g., \"**Käyttäjän Rooli: ROLE_ARCHITECT**\"). DO NOT translate the enum value (ROLE_ARCHITECT, ROLE_DRIVER, ROLE_NAVIGATOR, ROLE_PASSENGER). Following this, provide a concrete justification for why this specific role was assigned based on the control ratio and their cognitive initiative in the current execution. Show exactly which user sentence reflects this role."

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        modified = False
        if "output_profiles" in data:
            for profile in data["output_profiles"]:
                if profile.get("id") == "prf_5d6e7f8091a2b3c4":
                    if "synthesis" in profile and "system_prompt" in profile["synthesis"]:
                        prompt = profile["synthesis"]["system_prompt"]
                        if target_text in prompt:
                            profile["synthesis"]["system_prompt"] = prompt.replace(target_text, replacement_text)
                            modified = True
                            
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                if "pretty" in file_path:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, separators=(',', ':'))
            print(f"Updated {file_path}")
        else:
            print(f"Target text not found in {file_path}")
