import json

def run():
    try:
        db_path = "c:/src/quorum/data/db_v2.json"
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        steps = db.get("steps", {})
        count = 0
        
        # Otetaan pelkkä PURE JSON talteen koko steps-taulusta 50 ensimmäiseltä askeleelta!
        output_data = []
        for key, step_data in list(steps.items())[:50]:
            content = step_data.get("content", {})
            if isinstance(content, dict):
                if "raw_inputs" in content and "chat_log" in content["raw_inputs"]:
                    if "content_base64" in content["raw_inputs"]["chat_log"]:
                        content["raw_inputs"]["chat_log"]["content_base64"] = "[REMOVED]"
                        
            output_data.append(step_data)
        
        with open("c:/src/quorum/debug_steps_raw.json", "w", encoding="utf-8") as out:
            json.dump(output_data, out, indent=2, ensure_ascii=False)
            
        print("Steps dumpattu! debug_steps_raw.json on valmis.")
            
    except Exception as e:
        print(f"Error: {e}")

run()
