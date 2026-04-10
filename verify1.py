import json

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def verify_structural_injection():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    target_count = 0
    found_prompts = []

    if "output_profiles" in data:
        for profile in data["output_profiles"]:
            layouts = profile.get("layouts", [])
            for layout in layouts:
                system_prompt = layout.get("synthesis", {}).get("system_prompt", "")
                if "MATHEMATICAL ANCHORING MANDATE" in system_prompt:
                    target_count += 1
                    title = layout.get("title", {}).get("translations", {}).get("fi", "Unknown Title")
                    found_prompts.append(title)

    print("=== SYNTHESIS INJECTION VERIFICATION (Script 1) ===")
    print(f"Goal: Find exactly 3 3D Matrix Prompts with 'MATHEMATICAL ANCHORING MANDATE'")
    print(f"Found: {target_count}")
    
    if target_count == 3:
        print("\n[SUCCESS] Structural Verification PASSED. The strict mathematical rules are injected.")
        print("Found in:")
        for t in found_prompts:
            print(f" - {t}")
    else:
        print("\n[FAILED] Expected 3 injections, found something else.")

if __name__ == "__main__":
    verify_structural_injection()
