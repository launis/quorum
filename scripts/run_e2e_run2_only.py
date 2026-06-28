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
    if os.path.isdir(path):
        inputs: dict[str, Any] = {}
        extracted_dates = []
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isdir(file_path):
                continue
            key, ext = os.path.splitext(filename)
            ext = ext.lower()

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
    headers = {"Authorization": "Bearer mock-token:usr_18a0d5f6151349a5"}
    base_url = "http://127.0.0.1:8000/api/v2"

    w_res = requests.get(f"{base_url}/studio/workflows/", headers=headers, timeout=10)
    w_res.raise_for_status()
    workflows = w_res.json()
    workflow_id = workflows[0]["id"] if workflows else "wf_9d68c573802341db"

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


inputs_path = sys.argv[1] if len(sys.argv) > 1 else r"c:\src\quorum\docs\jwdatat"
print(f"Using inputs path: {inputs_path}")

# Tähän lisätään ensimmäisen ajon ID jotta diffaus voidaan suorittaa lopuksi molempien ajoja kesken
execution_ids = ["exe_ff733642a919433b9bbe2b1bee478ad5"]

print("\n=== RUN 2 (Standalone Recovery) ===")
print("Cleaning up old services...")
subprocess.run(
    [r"c:\src\quorum\kill_services.bat", "--no-pause"], input="\n", text=True, capture_output=True, shell=True
)

print("Waiting 5 seconds for Windows to release file locks...")
time.sleep(5)

print("Starting run_local.bat with FAST_DEV_MODE=false...")
backend_env = os.environ.copy()
backend_env["FAST_DEV_MODE"] = "false"
p = subprocess.Popen([r"c:\src\quorum\run_local.bat"], env=backend_env, creationflags=subprocess.CREATE_NEW_CONSOLE)

print("Waiting for backend to become responsive...")
if not check_backend():
    print("Backend failed to start!")
    sys.exit(1)

time.sleep(10)

raw_inputs = load_inputs_from_path(inputs_path)

print("Injecting noise into inputs for Run 2 (to test normalizer)...")


def inject_noise(text: str) -> str:
    if not text or " " not in text:
        return text
    space_variants = ["\u00a0", "\u2002", "\u2003", "\u202f"]
    # Indeksi 1 oli alkuperäisessä loopissa varattu toiselle ajolle
    char_to_inject = space_variants[1]
    print(f"Injected Unicode space variant (U+{ord(char_to_inject):04X}) in Run 2 to bypass cache")
    return text.replace(" ", char_to_inject, 1)


if "product_text" in raw_inputs and isinstance(raw_inputs["product_text"], str):
    raw_inputs["product_text"] = inject_noise(raw_inputs["product_text"])
else:
    injected = False
    for k, v in raw_inputs.items():
        if isinstance(v, str):
            raw_inputs[k] = inject_noise(v)
            injected = True
            break
    if not injected:
        print("Warning: Could not inject noise. No string fields found in raw_inputs.")

os.makedirs(r"c:\src\quorum\tmp", exist_ok=True)
output_path = r"c:\src\quorum\tmp\e2e_inputs_noisy.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(raw_inputs, f)
os.environ["TEST_INPUTS_FILE"] = output_path

exec_id = trigger_execution(raw_inputs)
if exec_id:
    execution_ids.append(exec_id)

print("Polling database for execution completion (max 120 mins)...")
db_path = r"c:\src\quorum\data\db_v2.json"
timeout = 7200
start = time.time()
done = False

while time.time() - start < timeout:
    time.sleep(5)
    try:
        with open(db_path, encoding="utf-8") as f:
            db_data = json.load(f)
        execs = list(db_data.get("executions", {}).values())
        if execs:
            target_exec = next((e for e in execs if e.get("id") == exec_id), None)
            if target_exec:
                status = str(target_exec.get("status")).upper()
                if status in ["COMPLETED", "FAILED"]:
                    print(f"Execution {exec_id} finished with status: {status}")
                    done = True
                    break
    except Exception:
        pass

if not done:
    print("Timeout waiting for execution!")
    sys.exit(1)

print("\n=== FINAL CLEANUP ===")
subprocess.run(
    [r"c:\src\quorum\kill_services.bat", "--no-pause"], input="\n", text=True, capture_output=True, shell=True
)

print("\n=== RUNNING DIFF EXECUTIONS ===")
diff_cmd = ["uv", "run", "python", r"c:\src\quorum\scripts\diff_executions.py"] + execution_ids
res = subprocess.run(diff_cmd, capture_output=True, text=True, shell=True)
print(res.stdout)
if res.stderr:
    print("STDERR:")
    print(res.stderr)
