"""End-to-End Variance and Reliability Test Runner.

Orchestrates sequential end-to-end execution runs with verified process isolation,
Unicode noise perturbation, database polling, and automated differential report synthesis.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import requests

__all__ = [
    "check_backend",
    "force_kill_services",
    "load_inputs_from_path",
    "make_noise_injector",
    "run_variance_test",
    "trigger_execution",
    "validate_execution_kelvollisuus",
]

# Ensure project root is in sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def check_backend(base_url: str = "http://127.0.0.1:8000/docs", max_retries: int = 45) -> bool:
    """Check if the backend FastAPI service is online and responding.

    Args:
        base_url: Target URL for readiness probing.
        max_retries: Maximum number of probe attempts.

    Returns:
        True if the backend responded with HTTP 200, False otherwise.
    """
    for _ in range(max_retries):
        try:
            r = requests.get(base_url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def load_inputs_from_path(path: str | Path) -> dict[str, Any]:
    """Load inputs from a directory of files or a single JSON file.

    Processes files in the directory based on extension:
    - PDF files: text extracted eagerly to allow text injection.
    - JSON files: parsed and inserted as structured objects.
    - TXT/MD files: loaded as raw string inputs.

    Args:
        path: Path to a file or directory containing test inputs.

    Returns:
        Dictionary of input key-value pairs for execution payload.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        ValueError: If the JSON file does not contain a dictionary.
    """
    input_path = Path(path)
    if not input_path.exists():
        msg = f"Inputs path does not exist: {input_path}"
        raise FileNotFoundError(msg)

    if input_path.is_dir():
        inputs: dict[str, Any] = {}
        extracted_dates: list[str] = []
        for file_path in input_path.iterdir():
            if file_path.is_dir():
                continue
            key = file_path.stem
            ext = file_path.suffix.lower()

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

                with file_path.open("rb") as f:
                    content_bytes = f.read()
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                try:
                    md_text = str(pymupdf4llm.to_markdown(doc))
                    inputs[mapped_key] = md_text.strip()

                    metadata = doc.metadata or {}
                    pdf_date = metadata.get("modDate") or metadata.get("creationDate")
                    if pdf_date:
                        from backend_v2.services.document_extraction import (
                            DocumentExtractionService,
                        )

                        parsed_date = DocumentExtractionService.parse_pdf_date(pdf_date)
                        if parsed_date:
                            extracted_dates.append(parsed_date)
                finally:
                    doc.close()
            elif ext == ".json":
                with file_path.open("r", encoding="utf-8") as f:
                    inputs[mapped_key] = json.load(f)
            elif ext in (".txt", ".md"):
                with file_path.open("r", encoding="utf-8") as f:
                    inputs[mapped_key] = f.read()

        if extracted_dates:
            valid_dates = sorted(extracted_dates, reverse=True)
            inputs["document_date"] = valid_dates[0]
        else:
            inputs["document_date"] = "2026-06-25T07:38:55+03:00"

        return inputs

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, dict):
            msg = "JSON inputs file must contain a dictionary."
            raise ValueError(msg)
        return data


def make_noise_injector(run_index: int) -> Callable[[str], str]:
    """Create a deterministic Unicode space injector to bypass LLM cache.

    Args:
        run_index: 0-indexed run number.

    Returns:
        Callable that replaces the first standard space with a unique Unicode space variant.
    """

    def injector(text: str) -> str:
        if not text or " " not in text:
            return text
        space_variants = ["\u00a0", "\u2002", "\u2003", "\u202f"]
        char_to_inject = space_variants[run_index % len(space_variants)]
        print(f"Injected Unicode space variant (U+{ord(char_to_inject):04X}) in Run {run_index + 1} to bypass cache")
        return text.replace(" ", char_to_inject, 1)

    return injector


def force_kill_services() -> None:
    """Force 100% reliable termination of all background Quorum services and workers."""
    print("[Clean-up] Enforcing 100% reliable process termination...")
    kill_script = Path("kill_services.bat")
    if kill_script.exists():
        try:
            subprocess.run(
                [str(kill_script.resolve()), "--no-pause"],
                input="\n",
                text=True,
                capture_output=True,
                shell=True,
                timeout=30,
            )
        except Exception as e:
            print(f"Warning running kill_services.bat: {e}")

    current_pid = os.getpid()
    ps_cmd = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { "
        "  ($_.Name -eq 'python.exe' -or $_.Name -eq 'uv.exe') -and "
        "  ($_.CommandLine -match 'backend_v2|run_worker|uvicorn|arq') -and "
        f"  ($_.ProcessId -ne {current_pid}) "
        "} | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; $_.ProcessId }"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if res.stdout.strip():
            print(f"[Clean-up] Terminated lingering process PIDs: {res.stdout.strip().split()}")
    except Exception as e:
        print(f"Warning in PowerShell process kill: {e}")

    subprocess.run('taskkill /F /T /FI "WINDOWTITLE eq CQ Worker V2*" 2>nul', shell=True, capture_output=True)
    subprocess.run('taskkill /F /T /FI "WINDOWTITLE eq CQ Backend V2*" 2>nul', shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM uvicorn.exe /T 2>nul", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM arq.exe /T 2>nul", shell=True, capture_output=True)

    try:
        subprocess.run("redis-cli flushall", shell=True, capture_output=True, timeout=5)
        subprocess.run(
            "docker exec quorum-redis-1 redis-cli FLUSHALL",
            shell=True,
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass

    print("[Clean-up] Verifying ports and process cleanup...")
    for attempt in range(10):
        net_check = subprocess.run(
            "netstat -ano | findstr :8000 | findstr LISTENING",
            shell=True,
            capture_output=True,
            text=True,
        )
        check_ps = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { "
            "  ($_.Name -eq 'python.exe') -and "
            "  ($_.CommandLine -match 'run_worker|backend_v2.main') -and "
            f"  ($_.ProcessId -ne {current_pid}) "
            "} | Measure-Object | Select-Object -ExpandProperty Count"
        )
        w_check = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", check_ps],
            capture_output=True,
            text=True,
        )
        worker_count = 0
        try:
            worker_count = int(w_check.stdout.strip() or "0")
        except ValueError:
            worker_count = 0

        is_port_busy = bool(net_check.stdout.strip())
        if not is_port_busy and worker_count == 0:
            print(f"[Clean-up] Verification successful (attempt {attempt + 1}): 0 lingering workers, port 8000 free.")
            break

        if is_port_busy:
            for line in net_check.stdout.strip().splitlines():
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    subprocess.run(f"taskkill /F /T /PID {pid} 2>nul", shell=True, capture_output=True)

        time.sleep(1)
    else:
        print("[Clean-up] Warning: Port or worker verification timed out after 10s.")

    time.sleep(2)


def trigger_execution(raw_inputs: dict[str, Any]) -> str:
    """Trigger native execution over HTTP API and save response trace.

    Args:
        raw_inputs: Dictionary of dynamic input fields.

    Returns:
        Generated execution ID.
    """
    print("Triggering E2E execution natively via Python requests...")
    from backend_v2.settings import get_settings

    settings = get_settings()
    headers = {"Authorization": f"Bearer mock-token:{settings.mock_admin_user_id}"}
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

    resp_data = resp.json()
    exec_id = resp_data.get("id")
    trace_data = resp_data.get("execution_trace")
    if trace_data is not None:
        out_trace = Path("backend_v2/tests/test_data/e2e_new_trace.json")
        out_trace.parent.mkdir(parents=True, exist_ok=True)
        with out_trace.open("w", encoding="utf-8") as f:
            json.dump(trace_data, f)
        print("Saved trace successfully.")
    else:
        print("Error: execution_trace missing from response!")
        sys.exit(1)

    return str(exec_id) if exec_id else ""


def validate_execution_kelvollisuus(
    target_exec: dict[str, Any],
    trace_path: Path | None = None,
) -> tuple[bool, str]:
    """Validate that execution output is valid and did not suffer from data starvation.

    Args:
        target_exec: Execution record dictionary from database.
        trace_path: Optional path to execution_trace.json for deep trace event validation.

    Returns:
        Tuple of (is_valid: bool, reason: str).
    """
    status = str(target_exec.get("status", "")).upper()
    if status != "PASSED":
        return False, f"Execution ended with non-passed status: '{status}'"

    # 1. Check profile_syntheses for DataStarvationEvent
    profile_syntheses = target_exec.get("profile_syntheses", {})
    if isinstance(profile_syntheses, dict):
        for profile_id, synth in profile_syntheses.items():
            if isinstance(synth, dict):
                starvation = synth.get("data_starvation")
                if starvation and isinstance(starvation, dict):
                    reason = starvation.get("reason", "Data starvation: insufficient observations")
                    return False, f"Profile '{profile_id}' data starvation: {reason}"

    # 2. Check execution_trace.json for starvation trace events
    if trace_path and trace_path.exists():
        try:
            with trace_path.open("r", encoding="utf-8") as f:
                trace_data = json.load(f)
            if isinstance(trace_data, list):
                for step in trace_data:
                    if isinstance(step, dict):
                        content = step.get("content")
                        if isinstance(content, dict) and content.get("event_type") == "starvation":
                            reason = content.get("reason", "Data starvation in step trace")
                            return (
                                False,
                                f"Trace event starvation in step '{step.get('step_id', 'unknown')}': {reason}",
                            )
        except Exception:
            pass

    return True, "Execution is valid and contains sufficient observations"


def run_variance_test(
    inputs_target: str | None = None,
    num_runs: int = 2,
    timeout_seconds: int = 7200,
    db_path: str | Path | None = None,
) -> list[str]:
    """Execute automated end-to-end variance test suite across multiple runs.

    Args:
        inputs_target: File or directory path containing test inputs.
        num_runs: Number of consecutive runs to compare.
        timeout_seconds: Maximum polling timeout per execution in seconds.
        db_path: Optional path to the database file (defaults to data/db_v2.json).

    Returns:
        List of generated execution IDs.
    """
    if not inputs_target:
        inputs_target = os.environ.get("TEST_INPUTS_PATH", "")
        if not inputs_target:
            inputs_target = os.environ.get("TEST_INPUTS_FILE", "")
        if not inputs_target:
            inputs_target = "backend_v2/tests/test_data/exe_c0bc_inputs.json"

    target_db_path = Path(db_path) if db_path else Path("data/db_v2.json")
    print(f"Using inputs path: {inputs_target}")
    execution_ids: list[str] = []

    for i in range(num_runs):
        print(f"\n=== RUN {i + 1} ===")
        force_kill_services()

        print("Starting run_local.bat...")
        dev_mode = os.environ.get("DEV_EXECUTION_MODE", "full")
        os.environ["DEV_EXECUTION_MODE"] = dev_mode
        backend_env = os.environ.copy()
        backend_env["DEV_EXECUTION_MODE"] = dev_mode

        run_bat = Path("run_local.bat").resolve()
        subprocess.Popen(
            [str(run_bat)],
            env=backend_env,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        print(f"Waiting for backend to become responsive (mode: {dev_mode})...")
        if not check_backend():
            print("Backend failed to start!")
            sys.exit(1)

        time.sleep(10)
        raw_inputs = load_inputs_from_path(inputs_target)

        print(f"Injecting noise into inputs for Run {i + 1} (to test normalizer)...")
        inject_noise = make_noise_injector(i)

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

        tmp_dir = Path("tmp")
        tmp_dir.mkdir(exist_ok=True)
        output_filename = "e2e_inputs_run1.json" if i == 0 else "e2e_inputs_noisy.json"
        output_path = tmp_dir / output_filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(raw_inputs, f)
        os.environ["TEST_INPUTS_FILE"] = str(output_path.resolve())

        exec_id = trigger_execution(raw_inputs)
        if exec_id:
            execution_ids.append(exec_id)

        print(f"Polling database for execution {exec_id} completion (max {timeout_seconds // 60} mins)...")
        start = time.time()
        done = False
        target_exec: dict[str, Any] | None = None

        while time.time() - start < timeout_seconds:
            time.sleep(5)
            try:
                with target_db_path.open("r", encoding="utf-8") as f:
                    db_data = json.load(f)
                execs = list(db_data.get("executions", {}).values())
                if execs:
                    found_exec = next((e for e in execs if e.get("id") == exec_id), None)
                    if found_exec:
                        status = str(found_exec.get("status")).upper()
                        if status in ["PASSED", "FAILED", "SYSTEM_ERROR"]:
                            print(f"Execution {exec_id} finished with status: {status}")
                            target_exec = found_exec
                            done = True
                            break
            except Exception:
                pass

        if not done or not target_exec:
            print("Timeout waiting for execution!")
            sys.exit(1)

        # Validate kelvollisuus (Data Starvation & Sufficiency Check)
        trace_file = Path(f"data/files/executions/{exec_id}/execution_trace.json")
        is_valid, reason = validate_execution_kelvollisuus(target_exec, trace_file)
        if not is_valid:
            print("\n❌ AJO KESKEYTETTY (KELVOTON AINEISTO / DATA STARVATION):")
            print(f"   Execution ID: {exec_id}")
            print(f"   Syy: {reason}")
            print("   Arviointiaineisto ei sisältänyt riittävästi havaintoja synteesin tuottamiseksi.")
            print("   Varianssitesti keskeytetään, koska kelvottomalla aineistolla ei voida laskea varianssia.")
            sys.exit(1)

    print("\n=== FINAL CLEANUP ===")
    force_kill_services()

    print("\n=== RUNNING DIFF EXECUTIONS ===")
    diff_script = Path("scripts/diff_executions.py").resolve()
    diff_cmd = ["uv", "run", "python", str(diff_script)] + execution_ids
    res = subprocess.run(diff_cmd, capture_output=True, text=True, shell=True)
    print(res.stdout)
    if res.stderr:
        print("STDERR:")
        print(res.stderr)

    return execution_ids


if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_variance_test(target_arg)
