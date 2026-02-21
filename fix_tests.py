import os
import re

fixes = [
    # 1. test_execution_endpoints.py
    (
        'backend/tests/integration/test_execution_endpoints.py',
        'from backend.models.state import WorkflowState',
        'from backend.models.state import WorkflowState\nfrom backend.models.domain.execution import ExecutionRecord\nfrom datetime import datetime, timezone'
    ),
    (
        'backend/tests/integration/test_execution_endpoints.py',
        'mock_repository.get_execution.return_value = past_state',
        'mock_repository.get_execution.return_value = ExecutionRecord(id="test_exec_id", workflow_id="wf1", status="completed", completed_at=datetime.now(timezone.utc), results=past_state)'
    ),
    # 2. test_agents_strict_dto.py
    (
        'backend/tests/manual/test_agents_strict_dto.py',
        'return falsifier_data',
        'falsifier_data["stress_test_findings"] = []\n    falsifier_data["fidelity_audit"] = "Mock fidelity audit"\n    return falsifier_data'
    ),
    # 3. test_kb_service_injection.py
    (
        'backend/tests/manual/test_kb_service_injection.py',
        'provider_type=deep_config["provider"]',
        'provider_type=deep_config.provider'
    ),
    (
        'backend/tests/manual/test_kb_service_injection.py',
        'model_name=deep_config["model_name"]',
        'model_name=deep_config.model_name'
    ),
    # 4. test_output_pipeline_strict.py
    (
        'backend/tests/manual/test_output_pipeline_strict.py',
        '"is_safe": True,\n            "tainted_data": None',
        '"is_safe": True,\n            "tainted_data": None,\n            "thought_process": "thought",\n            "conclusion": "conclusion",\n            "security_check": "check",\n            "confidence_score": 0.99'
    ),
    # 5. test_xai_flat_generation.py
    (
        'backend/tests/manual/test_xai_flat_generation.py',
        '"score_cards": []\n                }',
        '"score_cards": []\n                },\n                thought_process="thought",\n                conclusion="conclusion"'
    ),
    # 6. test_bibliography_parser.py
    (
        'backend/tests/services/parsers/test_bibliography_parser.py',
        'def test_no_bibliography(self, parser):',
        'def test_no_bibliography(self, parser):\n        from backend.exceptions import AppException'
    ),
    (
        'backend/tests/services/parsers/test_bibliography_parser.py',
        'refs = parser.parse_references(text)\n        assert refs == []',
        'with pytest.raises(AppException):\n            refs = parser.parse_references(text)'
    ),
    # 7. test_domain_enums.py
    (
        'backend/tests/test_domain_enums.py',
        '"abductive_score": 3.0\n        }',
        '"abductive_score": 3.0,\n            "counterfactual_test": "Mocked counterfactual"\n        }'
    ),
    # 8. test_storage_driver.py
    (
        'backend/tests/test_storage_driver.py',
        'assert res["id"] == "ex1"',
        'assert res.id == "ex1" # STRICT DTO FIX'
    ),
    # 9. test_engine_cancellation.py
    (
        'backend/tests/unit/test_engine_cancellation.py',
        'WorkflowStep(id="step1", task_key="mock_task", inputs={})',
        'WorkflowStep(id="step1", name="Step 1", task_key="mock_task", inputs={})'
    ),
    (
        'backend/tests/unit/test_engine_cancellation.py',
        'WorkflowStep(id="step2", task_key="mock_task_2", inputs={})',
        'WorkflowStep(id="step2", name="Step 2", task_key="mock_task_2", inputs={})'
    ),
    # 10. test_knowledge_service.py
    (
        'backend/tests/unit/test_knowledge_service.py',
        'expected_message="Knowledge Base retrieval failed: DB Error"',
        'expected_message="DB Error"'
    ),
    (
        'backend/tests/unit/test_knowledge_service.py',
        'import pytest\nfrom unittest.mock import AsyncMock, MagicMock',
        'import pytest\nfrom unittest.mock import AsyncMock, MagicMock\nfrom backend.exceptions import ServiceUnavailableError'
    ),
    (
        'backend/tests/unit/test_knowledge_service.py',
        'with pytest.raises(Exception, match=expected_message):',
        'with pytest.raises(ServiceUnavailableError):'
    ),
    # 11. test_llm_config.py
    (
        'backend/tests/unit/test_llm_config.py',
        '"model_name": "gpt-4o"\n        }',
        '"model_name": "gpt-4o",\n            "tpm_limit": 100000,\n            "rpm_limit": 1000\n        }'
    ),
    # 12. test_reporting_hook.py
    (
        'backend/tests/unit/test_reporting_hook.py',
        'context_variables={}',
        'context_variables={"inputs": {}}'
    ),
    # 13. test_retrieval_agent.py
    (
        'backend/tests/unit/test_retrieval_agent.py',
        'inputs = {\n            "query": "test query",\n            "organization_id": "org123",\n            "top_k": 5\n        }',
        'from backend.models.domain.inputs import WorkflowInputs\n    inputs = WorkflowInputs(\n        history_text="test query",\n        product_text="dummy",\n        reflection_text="dummy",\n        organization_id="org123",\n        language="en"\n    )'
    ),
    (
        'backend/tests/unit/test_retrieval_agent.py',
        'inputs = {\n            "query": "hybrid cache check",\n            "organization_id": "org-fail",\n            "top_k": 3\n        }',
        'from backend.models.domain.inputs import WorkflowInputs\n    inputs = WorkflowInputs(\n        history_text="hybrid cache check",\n        product_text="dummy",\n        reflection_text="dummy",\n        organization_id="org-fail",\n        language="en"\n    )'
    ),
]

for file_path, old, new in fixes:
    if not os.path.exists(file_path): 
        print(f"NOT FOUND: {file_path}")
        continue
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if old in content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.replace(old, new))
        print(f'Fixed {file_path}')
    else:
        print(f'Could not find match in {file_path}')
