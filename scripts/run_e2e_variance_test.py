"""End-to-End Variance and Reliability Test Runner.

Orchestrates sequential end-to-end execution runs with verified process isolation,
Unicode noise perturbation, database polling, and automated differential report synthesis.

Usage Examples:
    # 1. Run with default test inputs fixture (minimal synthetic fixture):
    uv run python scripts/run_e2e_variance_test.py

    # 2. Run with a custom inputs directory containing real evaluation files (RECOMMENDED):
    uv run python scripts/run_e2e_variance_test.py "path/to/my_inputs_dir"

    # 3. Run with a custom JSON inputs file:
    uv run python scripts/run_e2e_variance_test.py "path/to/custom_inputs.json"

    # 4. Optional: Run in fast development mode using environment variable:
    $env:DEV_EXECUTION_MODE="fast"; uv run python scripts/run_e2e_variance_test.py "path/to/my_inputs_dir"

    # 5. Comparing already completed executions (without re-running pipeline):
    #    Use scripts/diff_executions.py directly with execution IDs or directory paths:
    uv run python scripts/diff_executions.py exe_6c9e2f3b2ea14f9d exe_f16d8b0e40e44316
    uv run python scripts/diff_executions.py data/files/executions/exe_1 data/files/executions/exe_2
    uv run python scripts/diff_executions.py  # compares 3 latest runs automatically

Input Format and Default Fixture Notice:
    - Default fixture (`backend_v2/tests/test_data/exe_c0bc_inputs.json`):
      Contains minimal mock text fields (`chat_log`, `product_text`, `reflection_text`, `document_date`).
      This default is intended only as a lightweight synthetic fallback for smoke-testing.
    - Custom Directory (RECOMMENDED):
      It is strongly recommended to provide a directory containing realistic evaluation files
      (e.g., PDF transcripts, raw JSONs, markdown or text documents).
      When a directory is provided, the loader automatically extracts text from `.pdf`, `.json`,
      `.txt`, and `.md` files, and automatically maps Finnish domain filenames:
        * Files containing 'keskusteluhistoria' -> mapped to 'chat_log'
        * Files containing 'lopputuote'          -> mapped to 'product_text'
        * Files containing 'reflektio'           -> mapped to 'reflection_text'
      PDF metadata timestamps are also extracted dynamically to establish `document_date`.
"""

from __future__ import annotations

import argparse
import copy
import datetime
import io
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path before any local or third-party project imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

if sys.platform == "win32":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")

import requests
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO
from scripts.diff_executions import UNICODE_SPACE_REGISTRY

__all__ = [
    "MarkedInputsPayloadDTO",
    "RunMarkerMetadataDTO",
    "UNICODE_SPACE_REGISTRY",
    "check_backend",
    "force_kill_services",
    "inject_unique_run_marker",
    "load_inputs_from_path",
    "main",
    "make_noise_injector",
    "run_variance_test",
    "trigger_execution",
    "validate_execution_kelvollisuus",
]


def check_backend(base_url: str = "http://127.0.0.1:8000/docs", max_retries: int = 45) -> bool:
    """Check if the backend FastAPI service is online and responding.

    Args:
        base_url: Target URL for readiness probing.
        max_retries: Maximum number of probe attempts.

    Returns:
        True if the backend responded with HTTP 200, False otherwise.
    """
    for attempt in range(max_retries):
        try:
            r = requests.get(base_url, timeout=2)
            if r.status_code == 200:
                return True
        except requests.RequestException as e:
            if attempt % 10 == 0:
                print(f"[Probe] Readiness probe attempt {attempt + 1}/{max_retries}: {e}")
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
            inputs["document_date"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return inputs

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, dict):
            msg = "JSON inputs file must contain a dictionary."
            raise ValueError(msg)
        return data


class RunMarkerMetadataDTO(BaseModel):
    """Metadata describing the deterministic Unicode marker injected for a run."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    run_index: int = Field(..., description="0-indexed run number")
    injected_char: str = Field(..., description="Injected Unicode character")
    injected_char_hex: str = Field(..., description="Hex codepoint of injected character (e.g. U+00A0)")
    injected_char_name: str = Field(..., description="Human-readable name of injected character")
    replacement_offset: int = Field(..., description="Positional offset used for modulo replacement in 2D encoding")
    stride: int = Field(..., description="Stride interval used for multi-point whitespace injection")
    injected_keys: list[str] = Field(..., description="List of input keys where markers were successfully injected")


class MarkedInputsPayloadDTO(BaseModel):
    """Strongly-typed payload containing the marked inputs and forensic metadata."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    marked_inputs: dict[str, Any] = Field(..., description="Deep copy of inputs dictionary with injected markers")
    marker_metadata: RunMarkerMetadataDTO = Field(..., description="Metadata describing the injected marker")


# Phase 1, Step 1.6: Guarantee user-turn marker injection for conversational inputs
def _ensure_user_turn_marker(text: str, char_to_inject: str) -> str:
    """Guarantee that conversational text carries the Unicode marker in human user turns.

    Args:
        text: Reconstructed chat text.
        char_to_inject: The unique Unicode space marker for this run.

    Returns:
        The chat text with guaranteed user-turn marker injection.
    """
    # 1. Check if JSON formatted chat
    stripped = text.strip()
    if stripped.startswith(("{", "[")):
        try:
            parsed = json.loads(text)
            is_raw_list = isinstance(parsed, list)
            if is_raw_list:
                chat_dto = ChatHistoryDTO.model_validate({"conversation": parsed})
            elif isinstance(parsed, dict):
                chat_dto = ChatHistoryDTO.model_validate(parsed)
            else:
                chat_dto = None

            if chat_dto is not None:
                modified = False
                updated_turns: list[ChatMessageDTO] = []
                for turn in chat_dto.conversation:
                    if (
                        not modified
                        and turn.role.lower() == "user"
                        and char_to_inject not in turn.content
                        and " " in turn.content
                    ):
                        updated_turns.append(
                            ChatMessageDTO(
                                role=turn.role,
                                content=turn.content.replace(" ", char_to_inject, 1),
                            )
                        )
                        modified = True
                    else:
                        updated_turns.append(turn)
                if modified:
                    if is_raw_list:
                        return json.dumps(
                            [t.model_dump(mode="json") for t in updated_turns],
                            ensure_ascii=False,
                        )
                    return ChatHistoryDTO(conversation=updated_turns).model_dump_json()
        except json.JSONDecodeError, ValidationError, KeyError, TypeError, ValueError:
            pass

    # 2. Check for explicit user role prefix labels (User:, Käyttäjä:, etc.)
    user_prefix_regex = re.compile(
        r"^(User|Human|You|Käyttäjä|Sinä|Ihminen)\s*:",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(user_prefix_regex.finditer(text))
    if matches:
        ai_prefix_regex = re.compile(
            r"^(Assistant|AI|ChatGPT|Claude|Gemini|Assistentti|Avustaja|Tekoäly)\s*:",
            re.IGNORECASE | re.MULTILINE,
        )
        has_in_user = False
        first_user_match = matches[0]
        for i, match in enumerate(matches):
            start = match.end()
            next_ai = ai_prefix_regex.search(text, pos=start)
            next_user = matches[i + 1] if i + 1 < len(matches) else None
            end_pos = len(text)
            if next_ai and next_user:
                end_pos = min(next_ai.start(), next_user.start())
            elif next_ai:
                end_pos = next_ai.start()
            elif next_user:
                end_pos = next_user.start()
            user_turn_text = text[start:end_pos]
            boundary_chars = " \t\r\n" + "".join(UNICODE_SPACE_REGISTRY.keys())
            inner_user_content = user_turn_text.strip(boundary_chars)
            if char_to_inject in inner_user_content:
                has_in_user = True
                break

        if not has_in_user:
            start = first_user_match.end()
            next_ai = ai_prefix_regex.search(text, pos=start)
            end_pos = next_ai.start() if next_ai else len(text)
            user_turn_text = text[start:end_pos]
            boundary_chars = " \t" + "".join(UNICODE_SPACE_REGISTRY.keys())
            lstripped = user_turn_text.lstrip(boundary_chars)
            leading_ws = user_turn_text[: len(user_turn_text) - len(lstripped)]
            if " " in lstripped:
                replaced_user_turn = leading_ws + lstripped.replace(" ", char_to_inject, 1)
                return text[:start] + replaced_user_turn + text[end_pos:]

    # 3. Fallback for un-prefixed dialogue (chat starting directly with user prompt before AI response):
    # Guarantee injection within the user prompt section or the first 100 characters containing a space
    ai_prefix_regex = re.compile(
        r"^(Assistant|AI|ChatGPT|Claude|Gemini|Assistentti|Avustaja|Tekoäly|Talous-Timo|"
        r"[A-ZÄÖÅ][a-zäöå0-9_\- \t]{2,20})[ \t]*:",
        re.IGNORECASE | re.MULTILINE,
    )
    ai_match = ai_prefix_regex.search(text)
    user_end = ai_match.start() if ai_match else len(text)
    user_part = text[:user_end]
    boundary_chars = " \t" + "".join(UNICODE_SPACE_REGISTRY.keys())
    user_lstripped = user_part.lstrip(boundary_chars)
    user_leading = user_part[: len(user_part) - len(user_lstripped)]
    stripped_user = user_part.strip(" \t\r\n" + "".join(UNICODE_SPACE_REGISTRY.keys()))
    if char_to_inject not in stripped_user and " " in user_lstripped:
        return user_leading + user_lstripped.replace(" ", char_to_inject, 1) + text[user_end:]
    if char_to_inject not in text[:100] and " " in text[:100]:
        return text[:100].replace(" ", char_to_inject, 1) + text[100:]

    return text


def inject_unique_run_marker(
    inputs: dict[str, Any],
    run_index: int,
    stride: int = 50,
) -> MarkedInputsPayloadDTO:
    """Inject a deterministic unique Unicode marker into all N runs with distributed whitespace injection.

    Every run i (including Run 1 / index 0) receives a dedicated, deterministic marker.
    Distributed multi-point whitespace injection replaces every stride-th whitespace,
    with a fallback to the first whitespace if text has fewer whitespaces than stride.
    For run_index >= 16, a 2D positional encoding is applied across space occurrences
    to guarantee zero SHA-256 collisions for arbitrary N.

    Args:
        inputs: Input dictionary containing text fields.
        run_index: 0-indexed run number.
        stride: Frequency of whitespace substitution.

    Returns:
        MarkedInputsPayloadDTO containing the marked inputs copy and metadata.
    """
    variants = list(UNICODE_SPACE_REGISTRY.keys())
    num_variants = len(variants)
    variant_idx = run_index % num_variants
    char_to_inject = variants[variant_idx]
    replacement_offset = run_index // num_variants

    marked_inputs = copy.deepcopy(inputs)
    injected_keys: list[str] = []

    for k, v in marked_inputs.items():
        if isinstance(v, str) and " " in v:
            tokens = v.split(" ")
            num_spaces = len(tokens) - 1
            if num_spaces <= 0:
                continue

            # Multi-point distributed replacement with 2D positional encoding
            reconstructed_parts: list[str] = []
            for sp_idx, part in enumerate(tokens[:-1]):
                reconstructed_parts.append(part)
                # Determine if this space occurrence should be substituted
                is_stride_match = (sp_idx + replacement_offset) % stride == 0
                if is_stride_match:
                    reconstructed_parts.append(char_to_inject)
                else:
                    reconstructed_parts.append(" ")
            reconstructed_parts.append(tokens[-1])
            new_text = "".join(reconstructed_parts)

            # Fallback if text was shorter than stride and no replacement occurred
            if char_to_inject not in new_text:
                fallback_idx = replacement_offset % max(1, num_spaces)
                tokens_fb = v.split(" ")
                reconstructed_parts_fb: list[str] = []
                for sp_idx, part in enumerate(tokens_fb[:-1]):
                    reconstructed_parts_fb.append(part)
                    if sp_idx == fallback_idx:
                        reconstructed_parts_fb.append(char_to_inject)
                    else:
                        reconstructed_parts_fb.append(" ")
                reconstructed_parts_fb.append(tokens_fb[-1])
                new_text = "".join(reconstructed_parts_fb)

            # Phase 1, Step 1.6: Explicitly guarantee user dialogue turns carry the marker for chat inputs
            if k.lower() in ("chat_log", "input_chat_log", "keskusteluhistoria") or "chat" in k.lower():
                new_text = _ensure_user_turn_marker(new_text, char_to_inject)

            marked_inputs[k] = new_text
            injected_keys.append(k)

    char_hex = f"U+{ord(char_to_inject):04X}"
    # Phase 1, Step 1.5: Direct dictionary key lookup to eradicate QGR002
    char_name = UNICODE_SPACE_REGISTRY[char_to_inject]

    metadata = RunMarkerMetadataDTO(
        run_index=run_index,
        injected_char=char_to_inject,
        injected_char_hex=char_hex,
        injected_char_name=char_name,
        replacement_offset=replacement_offset,
        stride=stride,
        injected_keys=injected_keys,
    )

    return MarkedInputsPayloadDTO(marked_inputs=marked_inputs, marker_metadata=metadata)


def make_noise_injector(run_index: int) -> Callable[[str], str]:
    """Create a deterministic Unicode space injector to bypass LLM cache.

    Args:
        run_index: 0-indexed run number.

    Returns:
        Callable that replaces standard spaces with a unique Unicode space variant.
    """

    def injector(text: str) -> str:
        if not text or " " not in text:
            return text
        dummy_inputs = {"text": text}
        marked_payload = inject_unique_run_marker(dummy_inputs, run_index=run_index)
        # Phase 1, Step 1.5: Direct key access to eradicate QGR002
        return str(marked_payload.marked_inputs["text"])

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
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                shell=True,
                timeout=30,
            )
        except (subprocess.SubprocessError, OSError) as e:
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
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        if res.stdout.strip():
            print(f"[Clean-up] Terminated lingering process PIDs: {res.stdout.strip().split()}")
    except (subprocess.SubprocessError, OSError) as e:
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
    except (subprocess.SubprocessError, OSError) as e:
        print(f"[Clean-up] Redis flush skipped or unavailable: {e}")

    print("[Clean-up] Verifying ports and process cleanup...")
    for attempt in range(10):
        net_check = subprocess.run(
            "netstat -ano | findstr :8000 | findstr LISTENING",
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
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
            encoding="utf-8",
            errors="replace",
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
    if not workflows:
        msg = "No workflows found in database"
        raise RuntimeError(msg)
    if "id" not in workflows[0] or not workflows[0]["id"]:
        msg = "Workflow definition missing 'id'"
        raise RuntimeError(msg)
    workflow_id = str(workflows[0]["id"])

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
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:
            print(f"[Kelvollisuus] Warning reading trace file {trace_path}: {e}")

    return True, "Execution is valid and contains sufficient observations"


def run_variance_test(
    inputs_target: str | None = None,
    num_runs: int = 2,
    timeout_seconds: int = 7200,
    db_path: str | Path | None = None,
    no_cache: bool = False,
    cooldown_seconds: int = 0,
    dev: bool = False,
) -> list[str]:
    """Execute automated end-to-end variance test suite across multiple runs.

    Args:
        inputs_target: File or directory path containing test inputs.
        num_runs: Number of consecutive runs to compare.
        timeout_seconds: Maximum polling timeout per execution in seconds.
        db_path: Optional path to the database file (defaults to data/db_v2.json).
        no_cache: Whether to bypass native LLM provider context cache.
        cooldown_seconds: Cool-down pause between runs in seconds.
        dev: Whether to run in fast development mode instead of full production.

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

        if cooldown_seconds > 0 and i > 0:
            print(f"[Cooldown] Pausing for {cooldown_seconds}s for port and TCP socket drain...")
            time.sleep(cooldown_seconds)

        print("Starting run_local.bat...")
        environment = "development" if dev else "production"
        os.environ["ENVIRONMENT"] = environment
        backend_env = os.environ.copy()
        backend_env["ENVIRONMENT"] = environment

        run_bat = Path("run_local.bat").resolve()
        cmd: list[str] = [str(run_bat)]
        if environment == "production":
            cmd.append("--prod")
        else:
            cmd.append("--dev")

        if no_cache:
            cmd.append("--no-cache")
            backend_env["DISABLE_VERTEX_CACHE"] = "true"
            print("[Cache Policy] Native Vertex cache disabled via --no-cache CLI argument to run_local.bat")

        subprocess.Popen(
            cmd,
            env=backend_env,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        print(f"Waiting for backend to become responsive (environment: {environment})...")
        if not check_backend():
            print("Backend failed to start!")
            sys.exit(1)

        time.sleep(10)
        raw_inputs = load_inputs_from_path(inputs_target)

        print(f"Injecting unique deterministic marker into inputs for Run {i + 1}...")
        marked_payload = inject_unique_run_marker(raw_inputs, run_index=i)
        marked_inputs = marked_payload.marked_inputs
        meta = marked_payload.marker_metadata

        if not meta.injected_keys:
            msg = "Failed to inject Unicode noise: No whitespace found in any string input fields"
            raise RuntimeError(msg)

        print(
            f"Injected Unicode space variant {meta.injected_char_hex} ({meta.injected_char_name}) "
            f"into {len(meta.injected_keys)} input fields: {meta.injected_keys} "
            f"(stride={meta.stride}, offset={meta.replacement_offset})"
        )

        scratch_inputs_dir = Path("scratch/variance_inputs")
        scratch_inputs_dir.mkdir(parents=True, exist_ok=True)
        output_filename = f"e2e_inputs_run{i + 1}.json"
        output_path = scratch_inputs_dir / output_filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(marked_inputs, f)
        os.environ["TEST_INPUTS_FILE"] = str(output_path.resolve())

        exec_id = trigger_execution(marked_inputs)
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
            except (json.JSONDecodeError, OSError) as e:
                print(f"[Polling] Notice while reading database {target_db_path}: {e}")

        if not done or not target_exec:
            print("Timeout waiting for execution!")
            sys.exit(1)

        # Validate kelvollisuus (Data Starvation & Sufficiency Check)
        trace_file = Path(f"data/files/executions/{exec_id}/execution_trace.json")
        is_valid, reason = validate_execution_kelvollisuus(target_exec, trace_file)
        if not is_valid:
            print("\n[FAILED] AJO KESKEYTETTY (KELVOTON AINEISTO / DATA STARVATION):")
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
    res = subprocess.run(
        diff_cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True,
    )
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print("STDERR:")
        print(res.stderr)

    return execution_ids


def main(argv: list[str] | None = None) -> list[str]:
    """CLI entrypoint for end-to-end variance test runner."""
    parser = argparse.ArgumentParser(description="End-to-End Variance and Reliability Test Runner")
    parser.add_argument("inputs_target", nargs="?", default=None, help="File or directory path containing test inputs")
    parser.add_argument("--no-cache", action="store_true", help="Bypass native LLM provider context cache")
    parser.add_argument("--cooldown-seconds", type=int, default=0, help="Cool-down pause between runs in seconds")
    parser.add_argument("--num-runs", type=int, default=2, help="Number of consecutive runs to compare")
    parser.add_argument("--timeout-seconds", type=int, default=7200, help="Polling timeout per execution in seconds")
    parser.add_argument("--dev", action="store_true", help="Run in fast development mode instead of full production")

    args = parser.parse_args(argv)
    return run_variance_test(
        inputs_target=args.inputs_target,
        num_runs=args.num_runs,
        timeout_seconds=args.timeout_seconds,
        no_cache=args.no_cache,
        cooldown_seconds=args.cooldown_seconds,
        dev=args.dev,
    )


if __name__ == "__main__":
    main()
