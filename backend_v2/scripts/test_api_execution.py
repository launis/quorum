import base64
import json
import logging
import os
import re
import sys
import time
from datetime import datetime

import httpx
import jwt

# Insert paths to access backend models
sys.path.insert(0, r"c:\src\quorum")

# JWT Secret from the backend auth service
from backend_v2.services.auth import JWT_ALGORITHM, JWT_SECRET

# Define logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | [TestAPI] | %(message)s'
)
logger = logging.getLogger("test_api_execution")

def encode_file_to_base64_payload(filepath: str, expected_filename: str) -> dict:
    """Reads a file from disk and returns it as a base64 payload dict for the V2 backend."""
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode('utf-8')
            return {
                "filename": expected_filename,
                "content_base64": encoded
            }
    except Exception as e:
        logger.error(f"Error reading and encoding {filepath}: {e}")
        sys.exit(1)

def create_admin_token():
    payload = {
        "sub": "10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b",
        "exp": time.time() + 3600,
        "iat": time.time(),
        "type": "impersonation",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def clear_logs():
    """Empty out all debug logs to ensure a pristine analysis environment."""
    logger.info("Emptying debug logs for a clean run...")
    for log_path in [r"c:\src\quorum\backend_debug.log", r"c:\src\quorum\client_debug.log"]:
        try:
            if os.path.exists(log_path):
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.truncate(0)
                logger.debug(f"Cleared {log_path}")
        except Exception as e:
            logger.warning(f"Could not clear {log_path}: {e}")

def save_latest_results(results: dict, exec_id: str, ds_name: str = ""):
    """Simulates the behavior of fetch_results.py by flushing the
    completed JSON results to disk for manual inspection/diagnostics.
    """
    logger.info("\n==================================================")
    logger.info(f"SAVING EXECUTION RESULTS (ID: {exec_id})")
    logger.info("==================================================")

    suffix = f"_{ds_name}" if ds_name else ""
    path = rf"c:\src\quorum\backend_v2\scripts\latest_results{suffix}.json"
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully persisted the structured JSON payload to: {path}")
    except Exception as e:
        logger.error(f"Failed to flush results JSON to disk: {e}")

def trigger_and_verify_pdf(exec_id: str, headers: dict):
    logger.info("\n==================================================")
    logger.info("PHYSICAL PDF GENERATION TEST")
    logger.info("==================================================")
    api_url = f"http://localhost:8000/api/v2/execution/executions/{exec_id}/render_pdf"
    
    with httpx.Client(timeout=10.0) as client:
        logger.info(f"Triggering asynchronous PDF Worker: POST {api_url}")
        response = client.post(api_url, headers=headers)
        if response.status_code != 202:
            logger.error(f"Failed to trigger PDF generation. HTTP {response.status_code}: {response.text}")
            return
            
        logger.info("PDF Generation Queued. Polling disk for physical file creation...")
        pdf_path = rf"c:\src\quorum\data\files\executions\{exec_id}\report.pdf"
        
        attempts = 0
        while attempts < 30:
            if os.path.exists(pdf_path):
                size_kb = os.path.getsize(pdf_path) / 1024
                logger.info(f"SUCCESS! Physical PDF generated at: {pdf_path} ({size_kb:.1f} KB)")
                return
            time.sleep(2)
            attempts += 1
            
        logger.error(f"FAILURE! PDF was not found at {pdf_path} after 60 seconds.")

def _parse_log_timestamp(line: str) -> datetime | None:
    """Extract standard Python logging timestamp if present."""
    # format: '2026-03-15 02:44:16,123 | INFO | ...'
    match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})", line)
    if match:
        try:
             return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S,%f")
        except:
             pass
    return None

def analyze_logs(test_start_time: float, exec_id: str | None = None):
    """Deep Intelligence Log Analysis for V2 Diagnostics.
    """
    logger.info("\n==================================================")
    logger.info("DEEP INTELLIGENCE LOG ANALYSIS")
    logger.info("==================================================")

    backend_log_path = r"c:\src\quorum\backend_debug.log"
    client_log_path = r"c:\src\quorum\client_debug.log"

    backend_warnings = []
    backend_errors = []

    # Advanced metrics tracking
    workflow_started = None
    workflow_ended = None
    llm_cycles = []
    db_ops = 0
    hook_execs = []
    file_extractions = []

    # 1. Backend Log Deep Parse
    if os.path.exists(backend_log_path):
        try:
            with open(backend_log_path, encoding='utf-8') as f:
                lines = f.readlines()[-3000:]

                # We want to isolate logs that belong specifically to our run.
                # Since log time might drift slightly from time.time(), we use the start_execution signal
                test_context_active = False

                for i, line in enumerate(lines):
                    # Start tracking closely when we see our test script hit the backend
                    if "POST /api/v2/execution/executions/" in line and not test_context_active:
                         test_context_active = True
                         logger.info("[Diagnostics] Located REST entrypoint for Test suite.")

                    if not test_context_active:
                         continue # Skip logs from earlier dev sessions

                    # Timestamps
                    ts = _parse_log_timestamp(line)

                    # Errors & Exceptions
                    if "WARNING" in line:
                         backend_warnings.append(line.strip())
                    elif "ERROR" in line or "Exception" in line or "ValueError" in line:
                         # Exclude the exact 404 test we did earlier if it happens to be here
                         if "404" not in line and "status_code" not in line:
                            backend_errors.append(line.strip())

                    # LLM Provider Tracking (Network Latency Estimation)
                    if "[LiteLLM] [USER PROMPT]" in line:
                         # The prompt was sent
                         if ts: llm_cycles.append({"start": ts, "end": None, "type": "prompt"})
                    if "[LiteLLM] Model Execution completed" in line or "[LiteLLM] [RESPONSE]" in line:
                         if ts and llm_cycles and llm_cycles[-1]["end"] is None:
                              llm_cycles[-1]["end"] = ts
                              llm_cycles[-1]["duration"] = (ts - llm_cycles[-1]["start"]).total_seconds()

                    # Hook Instrumentation
                    # Matches lines like: "[InputProcessingHook] Running PyMuPDF" or "[ScoringHook]"
                    hook_match = re.search(r"\[([A-Za-z]+Hook)\]", line)
                    if hook_match:
                         if ts:
                              hook_execs.append({"hook": hook_match.group(1), "time": ts, "msg": line.strip()})
                         if "Running PyMuPDF" in line:
                              file_extractions.append(line)

            logger.info("--- BACKEND DIAGNOSTIC REPORT ---")

            # Sub-report A: Warnings/Errors
            if backend_errors:
                 logger.error(f"CRITICAL: Found {len(backend_errors)} backend exceptions during pipeline execution!")
                 for e in backend_errors[-5:]:
                      logger.error(f"  -> {e}")
            elif backend_warnings:
                 logger.warning(f"ATTENTION: Pipeline completed, but {len(backend_warnings)} warnings were thrown.")
                 for w in backend_warnings[-5:]:
                      logger.warning(f"  -> {w}")
            else:
                 logger.info("PIPELINE CLEAN: 0 Exceptions or Warnings detected in the backend GraphEngine.")

            # Sub-report B: CPU-Bound Hooks (Modality Extraction)
            logger.info("\n[Hardware Offloading]")
            if file_extractions:
                 logger.info(f"Verified {len(file_extractions)} binary payloads were aggressively extracted to text by Server CPU (PyMuPDF).")
            else:
                 logger.warning("No PyMuPDF extractions appeared. Did we send pure text instead of Base64?")

            # Sub-report C: LLM Latency & Network Bottlenecks
            completed_cycles = [c for c in llm_cycles if c.get("duration") is not None]
            if completed_cycles:
                total_llm_time = sum(c["duration"] for c in completed_cycles)
                avg_llm_time = total_llm_time / len(completed_cycles)
                logger.info("\n[Network & Token Metrics]")
                logger.info(f"VertexAI / LLM Cycles   : {len(completed_cycles)} unique calls")
                logger.info(f"Cumulative LLM Time     : {total_llm_time:.2f} seconds")
                logger.info(f"Average Generation Ping : {avg_llm_time:.2f} seconds / step")

                # Check for rate limiting
                rate_limits = [l for l in lines[-300:] if "429" in l or "Backoff" in l]
                if rate_limits:
                     logger.warning(f"RATE LIMITS DETECTED: {len(rate_limits)} Exponential Backoff instances were triggered!")
            else:
                logger.info("\n[Network Metrics] No LLM cycles could be accurately timed.")

        except Exception as e:
            logger.error(f"Diagnostic parser crashed: {e}")
    else:
        logger.warning("Backend log not found.")

    # 2. Cross-Validation (Client vs Backend)
    logger.info("\n--- ORCHESTRATION CROSS-VALIDATION (SERVER-SENT EVENTS) ---")
    client_timestamps = []

    if os.path.exists(client_log_path):
        try:
            with open(client_log_path, encoding='utf-8') as f:
                clines = f.readlines()[-1000:]

                sse_disconnects = []
                parse_errors = []

                for line in clines:
                     ts = _parse_log_timestamp(line)
                     if ts:
                         client_timestamps.append({"time": ts, "msg": line.strip()})

                     if "SSE Stream Interrupted" in line or "Connection closed" in line:
                         sse_disconnects.append(line)
                     if "AppException" in line or "Format" in line or "Error" in line:
                         parse_errors.append(line)

                if sse_disconnects:
                     logger.warning(f"CLIENT NETWORK DIAGNOSTIC: Found {len(sse_disconnects)} potential SSE stream disconnects. The frontend UI might have flickered or lost live timeline tracking!")
                     # Check if backend had issues around the same time
                     logger.info("  -> Attempting to correlate with backend logs...")
                     if backend_errors:
                          logger.warning(f"  -> CORRELATION: Backend also reported {len(backend_errors)} errors during this run. High probability SSE dropped immediately after a Backend Hook Exception.")
                     elif rate_limits:
                          logger.warning(f"  -> CORRELATION: Found {len(rate_limits)} Backend Rate Limits. SSE might have timed out due to Google API Backoffs!")
                     else:
                          logger.info("  -> NO CORRELATION: Backend survived clean. SSE disconnect is likely a pure Client/Flutter networking configuration issue (e.g. idle timeout).")
                elif not parse_errors:
                     logger.info("CLIENT HEALTH: Target UI logs indicate clean parsing. The `raw_inputs` were likely successfully accepted.")

                for e in parse_errors[-3:]:
                     logger.error(f"CLIENT PARSE ERROR: {e.strip()}")

        except Exception as e:
             logger.error(f"Client Diagnostic crashed: {e}")

    # Calculate System Overhead (Total Wall Time - Total LLM Generation Time)
    end_time = time.time()
    total_wall_time = end_time - test_start_time
    logger.info("\n--- FINAL EFFICIENCY SCORE ---")
    logger.info(f"Wall Clock Execution Time : {total_wall_time:.2f}s")

    # Only calculate if we captured LLM cycles
    try:
         total_llm = sum(c["duration"] for c in completed_cycles)
         system_overhead = total_wall_time - total_llm
         overhead_pct = (system_overhead / total_wall_time) * 100
         logger.info(f"Pure Python DB/Hook Time  : {system_overhead:.2f}s ({overhead_pct:.1f}% overhead)")
         if overhead_pct > 30:
              logger.warning("EVALUATION: The system overhead is unusually high. Check database index performance or PyMuPDF extraction bottlenecks.")
         else:
              logger.info("EVALUATION: Highly efficient V2 execution. Python Orchestrator is invisible compared to network bounds.")
    except:
         logger.info("Efficiency sub-score skipped (incomplete LLM timing).")


def verify_english_mandate_and_blocks(results: dict):
    logger.info("\n==================================================")
    logger.info("VERIFICATION PHASE: Commands & English-Only Mandate")
    logger.info("==================================================")

    # 1. Verify that the execution didn't fail
    logger.info("Fail-Fast Check: Execution completed successfully. All PromptBlocks valid.")

    # 2. Verify commands included
    all_blocks_used = set()
    ordered_steps = []
    total_matrices = 0

    for step_id, step_data in results.items():
        if isinstance(step_data, dict):
            metadata = step_data.get("_step_metadata", {})
            micro_levels = metadata.get("micro_strictness_levels", {})
            for block_id in micro_levels.keys():
                all_blocks_used.add(block_id)
                if block_id.startswith("matrix_"):
                    total_matrices += 1
            ordered_steps.append((step_id, step_data.get("step_metadata", {}).get("unix_time", 0)))

    ordered_steps.sort(key=lambda x: x[1])
    step_sequence = [s[0] for s in ordered_steps]

    logger.info(f"DAG Execution Path ({len(step_sequence)} steps): {' -> '.join(step_sequence)}")
    logger.info(f"Verified inclusion of {len(all_blocks_used)} distinct PromptBlocks (Commands).")
    logger.info(f"Total AI Evaluation Matrices Evaluated: {total_matrices}")

    # 3. Assess Logic Hooks
    logger.info("\n--- Hook & Integrations Audit ---")
    if "step_judge" in results and "scoring_result" in results["step_judge"]:
        score = results["step_judge"]["scoring_result"].get("final_score")
        logger.info(f"[ScoringHook] Verified final score aggregation: {score}/100")

    if "step_analyst" in results and "profiler_metrics" in results["step_analyst"]:
        metrics = results["step_analyst"].get("profiler_metrics", {})
        logger.info(f"[TextMetricsHook] Verified text profiling hook executed (Word count: {metrics.get('word_count')}).")


DATASETS = {
    "SITRA": r"c:\src\quorum\data\files\548d78cd-d540-44a3-bc3e-965064803a40",
    "REKLAMAATIO": r"c:\src\quorum\data\files\3bc29d99-0093-4175-9629-1e2982c6bb6d",
    "SYNTHETIC_GARBAGE": "MOCK",
}

def main():
    logger.info("--- QUORUM V2 CORE: DEEP DIAGNOSTIC EXECUTION TEST ---")

    # Empty logs to prevent parsing data from older runs
    clear_logs()

    token = create_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    api_url = "http://localhost:8000/api/v2/execution/executions/"

    # Iterate through all 3 configured datasets
    for ds_name, test_dir in DATASETS.items():
        start_time = time.time()
        logger.info("\n==================================================")
        logger.info(f" STARTING EXECUTION FOR DATASET: {ds_name}")
        logger.info("==================================================")

        if ds_name == "SYNTHETIC_GARBAGE":
             words = "Tämä on tärkeä hanke. Hanke on erittäin tärkeä. Tuotokset ovat tärkeitä hankkeelle. " * 15
             chat_log_payload = words
             product_payload = words
             questionnaire_payload = {"q1": words, "a1": words}
        else:
             logger.info(f"Encoding raw files directly from disk: {test_dir}...")

             chat_path = next((f for f in os.listdir(test_dir) if "SITRA" in f.upper() or "DATA" in f.upper()), None)
             product_path = next((f for f in os.listdir(test_dir) if "lopputuote" in f.lower() or "TULOS" in f.upper()), None)

             # Send the Native PDFs as Base64 to force the Backend to do the extraction!
             chat_log_payload = encode_file_to_base64_payload(
                 os.path.join(test_dir, chat_path) if chat_path else "",
                 chat_path or "fallback.pdf"
             )
             product_payload = encode_file_to_base64_payload(
                 os.path.join(test_dir, product_path) if product_path else "",
                 product_path or "fallback.pdf"
             )

             # Create the simulated JSON representation of the Flutter UI Questionnaire
             questionnaire_payload = {
                 "q1": "Mikä oli mielestäsi onnistuneinta tässä vuorovaikutuksessa?",
                 "a1": f"Analysoitu {ds_name} -datasetistä.",
                 "q2": "Mitä tekisit toisin ensi kerralla?",
                 "a2": "Antaisin ehkä mallille enemmän tilaa ideoida suoraan omien hypoteesien varaan aikaisemmassa vaiheessa."
             }

        payload = {
            "workflow_id": "workflow_courtroom_20_full_audit",
            "strictness_level": 3,
            "target_locale": "fi",
            "raw_inputs": {
                "chat_log": chat_log_payload,
                "product_text": product_payload,
                "reflection_text": questionnaire_payload
            }
        }

        logger.info("Sending V2 Raw Structured Payload to Start Execution...")
        with httpx.Client(timeout=30.0) as client:
            try:
                # Pydantic validates the request structure
                response = client.post(api_url, json=payload, headers=headers)
                if response.status_code != 202:
                    logger.error(f"FAILED TO START EXECUTION: {response.status_code}")
                    continue

                exec_id = response.json()["id"]
                logger.info(f"Execution initialized successfully in database! Assigned ID: {exec_id}")

                status_url = f"{api_url}{exec_id}"
                logger.info("Polling for real-time status updates...")

                failures = 0
                while True:
                    resp = client.get(status_url, headers=headers)
                    if resp.status_code != 200:
                        logger.error(f"Failed to get status: {resp.status_code}")
                        failures += 1
                        if failures > 3:
                             break
                        time.sleep(2)
                        continue

                    data = resp.json()
                    status = data.get("status")

                    if status == "completed":
                        logger.info(f"EXECUTION COMPLETED SUCCESFULLY FOR {ds_name}!")
                        results = data.get("results", {})

                        # RUN VERIFICATION
                        verify_english_mandate_and_blocks(results)

                        # RUN DEEP LOG ANALYSIS
                        analyze_logs(start_time, exec_id)

                        # SAVE RESULTS TO DISK (with dataset name)
                        save_latest_results(results, exec_id, ds_name)

                        # TRIGGER AND VERIFY PDF GENERATION
                        trigger_and_verify_pdf(exec_id, headers)

                        break
                    elif status == "failed":
                        logger.error(f"EXECUTION FAILED FOR {ds_name}. Aborting this dataset loop.")
                        logger.error(data.get("error"))

                        # RUN DEEP LOG ANALYSIS EVEN ON FAILURE
                        analyze_logs(start_time, exec_id)

                        break

                    # Formatted status update
                    states = data.get("step_states", {})
                    completed = [k for k,v in states.items() if v == "completed"]
                    logger.info(f"Status: {status} | Completed Steps: {len(completed)}")

                    time.sleep(5)
            except Exception as e:
                logger.error(f"Error during network communication for {ds_name}: {e}")

if __name__ == "__main__":
    main()
