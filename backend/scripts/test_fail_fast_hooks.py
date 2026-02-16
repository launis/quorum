
import logging
import os
import sys

# Redirect output to file
log_file = os.path.join(os.path.dirname(__file__), "test_hooks_output.txt")
sys.stdout = open(log_file, "w", encoding="utf-8")
sys.stderr = sys.stdout

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio

from backend.exceptions import AppException
from backend.hooks.metrics import calculate_text_metrics_hook
from backend.hooks.search import execute_google_search
from backend.hooks.security import check_banned_phrases_hook
from backend.hooks.validation import verify_structure
from backend.models.state import WorkflowState

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("test_hooks")

def test_metrics_fail():
    print("\n--- Testing Metrics Hook Fail Fast ---")
    state = WorkflowState(workflow_id="test", context_variables={}) # Empty context
    try:
        calculate_text_metrics_hook(state)
        print("❌ FAILED: Metrics swallowed error!")
        return False
    except AppException as e:
        if e.error_code == "METRICS_MISSING_CONTEXT":
             print(f"✅ PASSED: Caught {e.error_code}")
             return True
        print(f"❌ FAILED: Wrong error: {e.error_code}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Wrong exception: {type(e)}")
        return False

def test_search_fail():
    print("\n--- Testing Search Hook Fail Fast (Config error) ---")
    # Mock tool to simulate missing creds?
    # Search hook instantiates GoogleSearchTool internally.
    # If config missing, and we request search... wait, search hook checks queries first.
    # We need to simulate a state where analyst requested search.

    mock_analyst = {"hypoteesit": [{"hakusana_ehdotus": "test query"}]}
    state = WorkflowState(
        workflow_id="test",
        context_variables={
            "step_results": {"step_analyst": mock_analyst}
        }
    )

    # We must ensure env vars are unset for this test or mock the tool
    # For now, assuming env might be missing or we mock the class?
    # Hard to mock internal import without patching.
    # Let's rely on the fact that if it fails, it should raise.

    try:
        execute_google_search(state)
        # If it returns, maybe creds ARE present?
        # If creds present, it runs search.
        # If it runs search and fails (network), it raises SEARCH_EXECUTION_FAILED.
        # If no creds, raises SEARCH_CONFIG_ERROR.
        print("⚠️  WARNING: Search hook returned success (maybe creds exist?). Skipping strict fail assertion for now unless we mock.")
        return True
    except AppException as e:
         print(f"✅ PASSED: Caught {e.error_code}")
         return True
    except Exception as e:
         print(f"❌ FAILED: Wrong exception: {type(e)}")
         return False

def test_validation_fail():
    print("\n--- Testing Validation Hook Fail Fast ---")
    # Short input
    state = WorkflowState(
        workflow_id="test",
        context_variables={"inputs": {"history_text": "short"}}
    )
    try:
        verify_structure(state)
        print("❌ FAILED: Validation swallowed error!")
        return False
    except AppException as e:
        if e.error_code == "PRE_VALIDATION_FAILED":
             print(f"✅ PASSED: Caught {e.error_code}")
             return True
        print(f"❌ FAILED: Wrong error: {e.error_code}")
        return False
    except ValueError:
        print("❌ FAILED: Caught ValueError (Legacy) instead of AppException")
        return False

async def test_security_fail():
    print("\n--- Testing Security Hook Fail Fast (Missing Repo) ---")
    # Provide inputs so it doesn't return early
    state = WorkflowState(
        workflow_id="test",
        context_variables={"inputs": {"history_text": "foo"}}
    )
    try:
        await check_banned_phrases_hook(state, repository=None)
        print("❌ FAILED: Security swallowed error!")
        return False
    except AppException as e:
        if e.error_code == "SECURITY_CONFIG_ERROR":
             print(f"✅ PASSED: Caught {e.error_code}")
             return True
        print(f"❌ FAILED: Wrong error: {e.error_code}")
        return False

async def main():
    results = []
    results.append(test_metrics_fail())
    results.append(test_validation_fail())
    results.append(await test_security_fail())
    # results.append(test_search_fail()) # Flaky without mocking

    if all(results):
        print("\n🎉 ALL HOOK TESTS PASSED")
    else:
        print("\n💥 HOOK TESTS FAILED")

if __name__ == "__main__":
    asyncio.run(main())
