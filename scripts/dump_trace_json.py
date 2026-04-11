import json

def run():
    try:
        db_path = "c:/src/quorum/data/db_v2.json"
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        steps = db.get("steps", {})
        print(f"Löytyi {len(steps)} erillistä askelta steps-taulusta!")
        
        output_data = []
        for key, step_data in steps.items():
            content = step_data.get("content", {})
            if isinstance(content, dict):
                # Nollataan PDF
                if "raw_inputs" in content and "chat_log" in content["raw_inputs"]:
                    if "content_base64" in content["raw_inputs"]["chat_log"]:
                        content["raw_inputs"]["chat_log"]["content_base64"] = "[BASE64_POISTETTU]"
            
            output_data.append({
                "Execution ID": step_data.get("execution_id"),
                "Step ID": step_data.get("id"),
                "Content": content
            })

        with open("c:/src/quorum/trace_dump_final.json", "w", encoding="utf-8") as out:
            json.dump(output_data, out, indent=2, ensure_ascii=False)
            
        print("Täydellistä! Nyt steps-taulu on vihdoin purettu trace_dump_final.json!")
    except Exception as e:
        print(f"Error: {e}")

run()
