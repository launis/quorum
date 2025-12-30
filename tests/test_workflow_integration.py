import os
import time
import requests
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
WORKFLOW_ID = "fused_audit_chain_dual"
SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "scenarios", "workflow")

def wait_for_backend(base_url: str, timeout: int = 60):
    """Polls the backend health endpoint until it returns 200 or timeout."""
    health_url = f"{base_url}/health"
    print(f"[TEST] Waiting for backend at {health_url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print("[TEST] Backend is ready!")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    pytest.fail(f"Backend not ready at {base_url} after {timeout} seconds.")

@pytest.mark.live
def test_full_workflow_execution():
    """
    Tests the full workflow execution using PDF files from tests/scenarios/workflow.
    Supports running against local or cloud API via API_BASE_URL.
    """
    # 0. Ensure Backend is Ready
    wait_for_backend(API_BASE_URL)

    print(f"\n[TEST] Running full workflow test against: {API_BASE_URL}")
    
    # 1. Prepare Files
    history_path = os.path.join(SCENARIOS_DIR, "keskusteluhistoria SITRA.pdf")
    product_path = os.path.join(SCENARIOS_DIR, "lopputuote sitra.pdf")
    reflection_path = os.path.join(SCENARIOS_DIR, "Reflektiodokumentti sitra.pdf")
    
    # Verify files exist
    assert os.path.exists(history_path), f"History file not found: {history_path}"
    assert os.path.exists(product_path), f"Product file not found: {product_path}"
    assert os.path.exists(reflection_path), f"Reflection file not found: {reflection_path}"
    
    files = {
        'history_file': ('keskusteluhistoria SITRA.pdf', open(history_path, 'rb'), 'application/pdf'),
        'product_file': ('lopputuote sitra.pdf', open(product_path, 'rb'), 'application/pdf'),
        'reflection_file': ('Reflektiodokumentti sitra.pdf', open(reflection_path, 'rb'), 'application/pdf')
    }
    
    # 2. Start Workflow
    # 2. Start Workflow
    start_url = f"{API_BASE_URL}/executions"
    data_payload = {"workflow_id": WORKFLOW_ID}
    
    print(f"[TEST] Sending request to {start_url}...")
    try:
        # Note: 'data' sends form fields, 'files' sends multipart files. 
        # API expects workflow_id in form data, not query params.
        response = requests.post(start_url, data=data_payload, files=files)
        response.raise_for_status()
        data = response.json()
        execution_id = data.get("execution_id")
        print(f"[TEST] Workflow started. Execution ID: {execution_id}")
        assert execution_id is not None, "Execution ID not returned"
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Failed to start workflow: {e}")
    finally:
        # Close files
        for f in files.values():
            f[1].close()

    # 3. Poll for Completion
    status_url = f"{API_BASE_URL}/executions/{execution_id}"
    max_retries = 60 # 60 * 5s = 5 minutes timeout
    
    for i in range(max_retries):
        try:
            status_res = requests.get(status_url)
            status_res.raise_for_status()
            status_data = status_res.json()
            status = status_data.get("status")
            
            print(f"[TEST] Polling status ({i+1}/{max_retries}): {status}")
            
            if status in ["completed", "COMPLETED"]:
                print("[TEST] Workflow completed successfully!")
                result = status_data.get("result", {})
                
                # --- DEEP AUDIT: Verify that each LLM Agent followed instructions ---
                
                # Helper to handle V1/V2 structure differences
                def get_step_data(res, step_key):
                     # V2 Nested access (Preferred)
                     if "Raw_Steps" in res and res["Raw_Steps"] and step_key in res["Raw_Steps"]:
                         return res["Raw_Steps"][step_key]
                     # Fallback to Root
                     if step_key in res: return res[step_key]
                     return {}

                # --- DEEP AUDIT: Verify that each LLM Agent followed instructions ---

                # 1. GuardAgent: Did it define the safety status? 
                guard = get_step_data(result, "step_guard")
                print(f"[AUDIT] GuardAgent: {guard}")
                
                # Check deeper structure (TaintedData)
                sec_check = guard.get('security_check', {})
                if sec_check:
                     assert "uhka_havaittu" in sec_check or "anonymisointi_tehty" in sec_check, "GuardAgent security_check incomplete"
                else:
                     assert "tainted" in guard or "is_clean" in guard or "analyysi" in guard or "security_check" in guard, "GuardAgent output missing critical keys"

                # 2. AnalystAgent: Did it extract evidence?
                analyst = get_step_data(result, "step_analyst")
                # Structure: {'rag_todisteet': [...], 'hypoteesit': [...]}
                evidence_count = len(analyst.get("rag_todisteet", []) or analyst.get("havainnot", []) or [])
                print(f"[AUDIT] AnalystAgent found {evidence_count} pieces of evidence.")
                assert evidence_count > 0 or analyst.get('hypoteesit'), "AnalystAgent failed to extract specific evidence or return valid structure."

                # 3. PanelAgent: Did it fan-out to specialized critics?
                panel = get_step_data(result, "step_panel")
                # In V2, Panel output contains sub-audits directly (e.g. logiikka_auditointi, falsifiointi_auditointi)
                # OR it might be flattened.
                print(f"[AUDIT] PanelAgent Keys: {list(panel.keys())}")
                
                has_sub_audit = "logiikka_auditointi" in panel or "falsifiointi_auditointi" in panel or "kausaalinen_auditointi" in panel
                # Legacy check: did it spawn separate steps? (Not in Panel schema, but in workflow exec)
                # But PanelAgent usually runs sequentially inside one step or parallel. 
                # If PanelAgent returns 'PanelAudit' object, checking keys is enough.
                assert has_sub_audit or len(panel) > 0, "PanelAgent failed to produce sub-audits."

                # 4. JudgeAgent: Did it produce a numeric score?
                # Check report first for hoisted scores
                report = result.get("Report", {})
                scores = report.get("scores", {})
                
                if scores:
                    print(f"[AUDIT] Judge Scores (via Report): {scores}")
                    assert len(scores) > 0
                else:
                    judge = get_step_data(result, "step_judge")
                    # V2: "pisteet" object
                    pisteet = judge.get("pisteet", {})
                    # Legacy: "total_score"
                    total_score = judge.get("total_score")
                    
                    print(f"[AUDIT] JudgeAgent Score Data: {pisteet or total_score}")
                    assert pisteet or total_score is not None, "JudgeAgent failed to produce a final score."

                # 5. CoachAgent: Did it create a plan?
                coach = get_step_data(result, "step_coach")
                # Schema: CoachingPlan -> kannustava_palaute, kehityskohteet_konkreettisesti
                plan_exists = "kannustava_palaute" in coach or "palaute_yhteenveto" in report
                print(f"[AUDIT] CoachAgent Plan found: {plan_exists}")
                assert plan_exists, "CoachAgent failed to generate a coaching plan."

                # 6. XAIReporter: Is the final report substantial?
                report_content = result.get("xai_report") or result.get("report_content") or result.get("xai_report_content")
                assert report_content and len(report_content) > 100, "Final Report is suspiciously short or missing."
                
                print("[TEST] >>> DEEP AUDIT PASSED: All Agents performed correctly. <<<")
                
                return # Success
                
            elif status == "FAILED":
                error_msg = status_data.get("error", "Unknown error")
                pytest.fail(f"Workflow failed: {error_msg}")
                
            time.sleep(5)
            
        except requests.exceptions.RequestException as e:
            print(f"[TEST] Warning: Status poll failed: {e}")
            time.sleep(5)
            
    pytest.fail("Workflow execution timed out.")

if __name__ == "__main__":
    # Allow running directly with python
    test_full_workflow_execution()
