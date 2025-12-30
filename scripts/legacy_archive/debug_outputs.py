import json
import os

def check_outputs():
    db_path = 'c:/Users/risto/OneDrive/quorum/data/db_mock.json'
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return

    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    executions = data.get('executions', {})
    if not executions:
        print("No executions found.")
        return

    # Sort executions by start_time to get the latest
    latest_exec_id = max(executions.keys(), key=lambda k: executions[k]['start_time'])
    latest_exec = executions[latest_exec_id]

    with open('c:/Users/risto/OneDrive/quorum/debug_report.txt', 'w', encoding='utf-8') as outfile:
        outfile.write(f"Latest Execution ID: {latest_exec_id}\n")
        outfile.write(f"Status: {latest_exec.get('status')}\n")
        
        result = latest_exec.get('result', {})
        
        # Check Judge Output (Step 8)
        judge_output = result.get('step_8_judge')
        if judge_output:
            outfile.write("\n--- Step 8: Judge Output ---\n")
            outfile.write(json.dumps(judge_output, indent=2, ensure_ascii=False))
        else:
            outfile.write("\nStep 8: Judge Output NOT FOUND in result.\n")

        # Check XAI Report (Step 9)
        xai_output = result.get('step_9_reporter')
        if xai_output:
            outfile.write("\n--- Step 9: XAI Report ---\n")
            outfile.write(json.dumps(xai_output, indent=2, ensure_ascii=False))
        else:
            outfile.write("\nStep 9: XAI Report NOT FOUND in result.\n")

    # Check if there are explicit files mentioned in the logs or otherwise
    # (Since I couldn't find where they are written, I rely on the DB)

if __name__ == "__main__":
    check_outputs()
