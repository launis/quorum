"""Verify Builder Refactor Tool."""

import json
import sys

import requests

BASE_URL = "http://127.0.0.1:8000"


def check_steps(data):
    """Check if steps data is a list of dicts with 'id'."""
    return isinstance(data, list) and len(data) > 0 and "id" in data[0]


def check_strategies(data):
    """Check if strategies data is a dict containing 'fast' strategy."""
    # Should be a dict where keys are strategy names or list of keys?
    # Actually client expects: 'list(res.json().keys())' so backend likely returns dict
    return isinstance(data, dict) and "fast" in data


def check_template(data):
    """Check if the template data contains required fields."""
    return "steps" in data and "default_model_mapping" in data and data["name"] == "New Workflow"


def check_id_gen(data):
    """Check if the generated ID starts with the expected prefix."""
    return "id" in data and data["id"].startswith("test_")


def check_fusion_rules(data):
    """Check if fusion rules are a list and contain 'composite_step_id'."""
    # Should be a list of rules
    return isinstance(data, list) and len(data) > 0 and "composite_step_id" in data[0]


def check_prompt_types(data):
    """Check if prompt types are a list and contain 'prompt'."""
    return isinstance(data, list) and "prompt" in data


def test_endpoint(name, url, expected_status=200, check_fn=None, res_log=None):
    """Test a specific API endpoint and log the result."""
    try:
        res = requests.get(f"{BASE_URL}{url}", timeout=10)
        status = "PASSED"
        detail = ""

        if res.status_code != expected_status:
            status = "FAILED"
            detail = f"Status {res.status_code}. Response: {res.text[:200]}"
        elif check_fn and not check_fn(res.json()):
            status = "FAILED"
            detail = f"Content Check Failed. Response: {res.text[:200]}"

        res_log.append({"name": name, "url": url, "status": status, "detail": detail})
        return status == "PASSED"
    except Exception as e:
        res_log.append({"name": name, "url": url, "status": "FAILED", "detail": str(e)})
        return False


def run_tests():
    """Run all verification tests."""
    logs = []

    test_endpoint("Config Steps", "/config/steps", check_fn=check_steps, res_log=logs)
    test_endpoint("Model Strategies", "/config/models/strategies", check_fn=check_strategies, res_log=logs)
    test_endpoint("Workflow Template", "/builder/config/template", check_fn=check_template, res_log=logs)
    test_endpoint("ID Generation", "/builder/utils/generate-id?prefix=test", check_fn=check_id_gen, res_log=logs)
    test_endpoint("Fusion Rules", "/builder/config/fusion-rules", check_fn=check_fusion_rules, res_log=logs)
    test_endpoint("Prompt Types", "/builder/config/prompt-types", check_fn=check_prompt_types, res_log=logs)
    test_endpoint("Agents Config", "/builder/config/agents", res_log=logs)  # check_fn defaults to None

    with open("test_report.json", "w") as f:
        json.dump(logs, f, indent=2)

    if any(log_entry["status"] == "FAILED" for log_entry in logs):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    run_tests()
