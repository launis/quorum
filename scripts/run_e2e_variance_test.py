import base64
import json
import os
import subprocess
import sys
import time
from typing import Any

import requests

# Ensure root of project is in sys.path for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def check_backend() -> bool:
    for _ in range(45):
        try:
            r = requests.get("http://127.0.0.1:8000/docs", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def load_inputs_from_path(path: str) -> dict[str, Any]:
    """Load inputs from a directory of files or a single JSON file.

    Process files in the directory based on their extensions:
    - PDF files are parsed and their text is extracted eagerly to allow text injection.
    - JSON files are parsed and inserted as structured objects.
    - TXT/MD files are loaded as raw string inputs.
    """
    if os.path.isdir(path):
        inputs: dict[str, Any] = {}
        extracted_dates = []
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isdir(file_path):
                continue
            key, ext = os.path.splitext(filename)
            ext = ext.lower()

            # Map user-provided Finnish filenames to standard workflow input keys
            norm_key = key.lower().strip()
            if "keskusteluhistoria" in norm_key:
                mapped_key = "chat_log"
            elif "lopputuote" in norm_key:
                mapped_key = "product_text"
            elif "reflektio" in norm_key:
                mapped_key = "reflection_text"
            else:
                mapped_key = key

            if ext == ".pdf":
                import fitz
                import pymupdf4llm
                with open(file_path, "rb") as f:
                    content_bytes = f.read()
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                try:
                    md_text = str(pymupdf4llm.to_markdown(doc))
                    inputs[mapped_key] = md_text.strip()

                    # Extract metadata date if available
                    metadata = doc.metadata or {}
                    pdf_date = metadata.get("modDate") or metadata.get("creationDate")
                    if pdf_date:
                        from backend_v2.services.document_extraction import DocumentExtractionService
                        parsed_date = DocumentExtractionService.parse_pdf_date(pdf_date)
                        if parsed_date:
                            extracted_dates.append(parsed_date)
                finally:
                    doc.close()
            elif ext == ".json":
                with open(file_path, encoding="utf-8") as f:
                    inputs[mapped_key] = json.load(f)
            elif ext in (".txt", ".md"):
                with open(file_path, encoding="utf-8") as f:
                    inputs[mapped_key] = f.read()
        
        if extracted_dates:
            valid_dates = sorted(extracted_dates, reverse=True)
            inputs["document_date"] = valid_dates[0]
        else:
            inputs["document_date"] = "2026-06-25T07:38:55+03:00"

        return inputs
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("JSON inputs file must contain a dictionary")
            return data


def trigger_execution(raw_inputs: dict[str, Any]) -> str:
    print("Triggering E2E execution natively via Python requests...")
    import requests

    # 2. Setup requests session
    headers = {"Authorization": "Bearer mock-token:usr_18a0d5f6151349a5"}
    base_url = "http://127.0.0.1:8000/api/v2"

    # 3. Get Workflow ID
    w_res = requests.get(f"{base_url}/studio/workflows/", headers=headers, timeout=10)
    w_res.raise_for_status()
    workflows = w_res.json()
    workflow_id = workflows[0]["id"] if workflows else "wf_9d68c573802341db"

    # 4. Trigger Execution
    print(f"Sending POST to {base_url}/execution/executions/ using workflow {workflow_id}")
    resp = requests.post(
        f"{base_url}/execution/executions/",
        headers=headers,
        json={
            "workflow_id": workflow_id,
            "profile_id": "prf_5d6e7f8091a2b3c4",
            "raw_inputs": {"dynamic_inputs": raw_inputs},
            "target_locale": "fi",
        },
        timeout=300,
    )
    if not resp.ok:
        print(f"HTTP ERROR {resp.status_code}: {resp.text}")
    resp.raise_for_status()

    # 5. Save Trace
    out_trace = r"c:\src\quorum\backend_v2\tests\test_data\e2e_new_trace.json"
    resp_data = resp.json()
    trace_data = resp_data.get("execution_trace")
    if trace_data is not None:
        with open(out_trace, "w", encoding="utf-8") as f:
            json.dump(trace_data, f)
        print("Saved trace successfully.")
    else:
        print("Error: execution_trace missing from response!")
        sys.exit(1)
    exec_id = resp_data.get("id")
    return str(exec_id) if exec_id else ""


# Resolve input path from arguments, environment, or the default fallback file
inputs_path = ""
if len(sys.argv) > 1:
    inputs_path = sys.argv[1]
else:
    inputs_path = os.environ.get("TEST_INPUTS_PATH", "")
    if not inputs_path:
        inputs_path = os.environ.get("TEST_INPUTS_FILE", "")

if not inputs_path:
    inputs_path = r"c:\src\quorum\backend_v2\tests\test_data\exe_c0bc_inputs.json"

print(f"Using inputs path: {inputs_path}")

execution_ids = []

for i in range(2):
    print(f"\n=== RUN {i + 1} ===")
    print("Cleaning up old services...")
    subprocess.run([r"c:\src\quorum\kill_services.bat", "--no-pause"], input="\n", text=True, capture_output=True, shell=True)

    # Allow Windows sufficient time to release file and DLL locks from killed processes
    print("Waiting 5 seconds for Windows to release file locks...")
    time.sleep(5)

    print("Starting run_local.bat...")
    # creationflags=subprocess.CREATE_NEW_CONSOLE allows it to spawn detached windows just like a user double-clicking it
    p = subprocess.Popen([r"c:\src\quorum\run_local.bat"], creationflags=subprocess.CREATE_NEW_CONSOLE)

    print("Waiting for backend to become responsive...")
    if not check_backend():
        print("Backend failed to start!")
        sys.exit(1)

    # Wait extra time for the worker to fully boot up and connect to Redis
    time.sleep(10)

    # Load raw inputs dynamically for this run
    raw_inputs = load_inputs_from_path(inputs_path)

    # Inject noise for Run 2 to test the normalizer
    if i == 1:
        print("Injecting noise into inputs for Run 2 (to test normalizer)...")
        # Add a zero-width space, some trailing spaces, and change a regular space to multiple spaces in product_text
        def inject_noise(text: str) -> str:
            if " a " in text:
                print("Injected English noise (' a ' -> ' aa ')")
                return text.replace(" a ", " aa ", 1)
            elif " ja " in text:
                print("Injected Finnish noise (' ja ' -> ' jja ')")
                return text.replace(" ja ", " jja ", 1)
            elif " on " in text:
                print("Injected Finnish noise (' on ' -> ' oon ')")
                return text.replace(" on ", " oon ", 1)
            elif " " in text:
                print("Injected space noise (' ' -> '  ')")
                return text.replace(" ", "  ", 1)
            return text + " x"

        if "product_text" in raw_inputs and isinstance(raw_inputs["product_text"], str):
            raw_inputs["product_text"] = inject_noise(raw_inputs["product_text"])
        else:
            # Fallback to injecting noise in any available string value
            injected = False
            for k, v in raw_inputs.items():
                if isinstance(v, str):
                    raw_inputs[k] = inject_noise(v)
                    injected = True
                    break
            if not injected:
                print("Warning: Could not inject noise. No string fields found in raw_inputs.")

        # Write noisy inputs to tmp for client diagnostics and compatibility
        os.makedirs(r"c:\src\quorum\tmp", exist_ok=True)
        noisy_path = r"c:\src\quorum\tmp\e2e_inputs_noisy.json"
        with open(noisy_path, "w", encoding="utf-8") as f:
            json.dump(raw_inputs, f)
        os.environ["TEST_INPUTS_FILE"] = noisy_path
    else:
        # Write default inputs to tmp for client diagnostics and compatibility
        os.makedirs(r"c:\src\quorum\tmp", exist_ok=True)
        run1_path = r"c:\src\quorum\tmp\e2e_inputs_run1.json"
        with open(run1_path, "w", encoding="utf-8") as f:
            json.dump(raw_inputs, f)
        os.environ["TEST_INPUTS_FILE"] = run1_path

    exec_id = trigger_execution(raw_inputs)
    if exec_id:
        execution_ids.append(exec_id)

    print("Polling database for execution completion (max 60 mins)...")
    db_path = r"c:\src\quorum\data\db_v2.json"
    timeout = 3600
    start = time.time()
    done = False

    while time.time() - start < timeout:
        time.sleep(5)
        try:
            with open(db_path, encoding="utf-8") as f:
                db_data = json.load(f)
            execs = list(db_data.get("executions", {}).values())
            if execs:
                latest = sorted(execs, key=lambda x: x.get("created_at", ""), reverse=True)[0]
                status = str(latest.get("status")).upper()
                if status in ["COMPLETED", "FAILED"]:
                    print(f"Execution {latest.get('id')} finished with status: {status}")
                    done = True
                    break
        except Exception:
            pass

    if not done:
        print("Timeout waiting for execution!")
        sys.exit(1)

print("\n=== FINAL CLEANUP ===")
subprocess.run([r"c:\src\quorum\kill_services.bat", "--no-pause"], input="\n", text=True, capture_output=True, shell=True)

print("\n=== RUNNING DIFF EXECUTIONS ===")
diff_cmd = ["uv", "run", "python", r"c:\src\quorum\scripts\diff_executions.py"] + execution_ids
res = subprocess.run(diff_cmd, capture_output=True, text=True, shell=True)
print(res.stdout)
if res.stderr:
    print("STDERR:")
    print(res.stderr)
