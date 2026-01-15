
import json
import os

DB_PATH = "c:/src/quorum/data/db.json"

def patch_db():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        executions = data.get("executions", {})
        if not executions:
            print("No executions found.")
            return

        # Find latest
        sorted_executions = sorted(
            executions.items(),
            key=lambda x: x[1].get("started_at", ""),
            reverse=True
        )
        latest_id, latest_exec = sorted_executions[0]
        print(f"Patching Execution ID: {latest_id}")


        step_xai = latest_exec.get("results", {}).get("step_xai")
        if not step_xai:
            print("No step_xai found.")
            return

        # 1. Hoist Fields to Top Level (Done previously, but good to ensure)
        hoist_fields = [
            "final_verdict", 
            "confidence_score",
            "executive_summary",
            "analysis_strengths",
            "analysis_weaknesses",
            "analysis_opportunities",
            "analysis_recommendations",
            "xai_report_formatted" # Ensure this is hoisted too
        ]

        changes_made = False
        for field in hoist_fields:
            if field in step_xai:
                latest_exec[field] = step_xai[field]
                print(f"Hoisted: {field}")
                changes_made = True


        # 2. ALIAS step_xai -> Report (Frontend Compatibility)
        if "results" in latest_exec:
            # Report Alias
            latest_exec["results"]["Report"] = step_xai
            
            # Confidence Alias (score -> confidence) for Frontend
            if "confidence_score" in step_xai:
                step_xai["confidence"] = step_xai["confidence_score"]
                latest_exec["results"]["Report"]["confidence"] = step_xai["confidence_score"]
                print(f"Aliased 'confidence_score' to 'confidence'.")

            print("Aliased 'step_xai' to 'Report' inside results.")
            
            # System Status Alias (step_guard -> System_Status)
            step_guard = latest_exec.get("results", {}).get("step_guard")
            if step_guard and "security_check" in step_guard:
                 latest_exec["results"]["System_Status"] = step_guard["security_check"]
                 print("Aliased 'step_guard.security_check' to 'System_Status'.")
            
            changes_made = True
        
        if changes_made:
            executions[latest_id] = latest_exec


            data["executions"] = executions # Ensure structure is kept if executions was modified in place
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Database updated.")
        else:
            print("No changes made.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    patch_db()
