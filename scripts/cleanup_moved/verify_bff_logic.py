
import json


def verify_scale_resolution():
    try:
        with open(r'c:\src\quorum\data\db.json', encoding='utf-8') as f:
            db_data = json.load(f)

        executions = db_data.get('executions', {})
        components = db_data.get('components', {})
        workflows = db_data.get('workflows', {})

        if not executions:
            print("No executions found in db.json")
            return

        # Sort executions by start_time to get latest
        sorted_execs = sorted(executions.values(), key=lambda x: x.get('start_time', ''), reverse=True)
        latest_exec = sorted_execs[0]
        print(f"Latest Execution ID: {latest_exec.get('id')}")
        print(f"Workflow ID: {latest_exec.get('workflow_id')}")

        raw_data = latest_exec
        results = raw_data.get("results", {})
        if "step_results" in results:
            steps = results["step_results"]
        else:
            steps = results

        print("Steps found: ", list(steps.keys()))

        # Logic from execution_router.py
        scale_limit = (1.0, 4.0)
        matrix_id = None

        # A. Try Result Metadata
        judge_step = steps.get("step_judge") or steps.get("step_judge_cognitive")

        if judge_step:
            print("Found judge step.")
            if "matrix_id" in judge_step:
                matrix_id = judge_step["matrix_id"]
                print(f"Found matrix_id in result: {matrix_id}")
            elif "metadata" in judge_step and "matrix_id" in judge_step["metadata"]:
                matrix_id = judge_step["metadata"]["matrix_id"]
                print(f"Found matrix_id in result metadata: {matrix_id}")
            elif "config" in judge_step and "matrix_id" in judge_step["config"]:
                 matrix_id = judge_step["config"]["matrix_id"]
                 print(f"Found matrix_id in result config: {matrix_id}")

        # B. Fallback to Workflow Config
        if not matrix_id:
            print("Matrix ID not in result, checking workflow...")
            workflow_id = raw_data.get("workflow_id")
            if workflow_id and workflow_id in workflows:
                workflow = workflows[workflow_id]
                steps_def = workflow.get("steps", [])
                for step in steps_def:
                    # task_key might be in dict
                    task_key = step.get("task_key")
                    if task_key in ["judge", "cognitive_judge"]:
                        config = step.get("config", {})
                        matrix_id = config.get("matrix_id")
                        print(f"Found matrix_id in workflow definition: {matrix_id}")
                        break

        # C. Fetch Matrix Component
        if matrix_id:
            # Handle tinyDB structure where components might be keyed by ID or just a dict
            matrix = None
            if matrix_id in components:
                matrix = components[matrix_id]
            else:
                 # Search by ID field
                 for k, v in components.items():
                     if v.get('id') == matrix_id:
                         matrix = v
                         break

            if matrix:
                content = matrix.get("content", {})
                if "scale" in content:
                     scale = content["scale"]
                     scale_limit = (float(scale["min"]), float(scale["max"]))
                     print(f"Resolved scale from matrix['content']['scale']: {scale_limit}")
                elif "scale" in matrix:
                     scale = matrix["scale"]
                     scale_limit = (float(scale["min"]), float(scale["max"]))
                     print(f"Resolved scale from matrix['scale']: {scale_limit}")
                elif "scale_min" in matrix and "scale_max" in matrix:
                     scale_limit = (float(matrix["scale_min"]), float(matrix["scale_max"]))
                     print(f"Resolved scale from flattened matrix component: {scale_limit}")
                else:
                    print("Matrix found but no scale keys.")
            else:
                print(f"Matrix component {matrix_id} not found.")
        else:
            print("No matrix_id resolved.")

        print(f"FINAL RESOLVED SCALE LIMIT: {scale_limit}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_scale_resolution()
