import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.models.v2_core import Workflow, WorkflowInputs, I18nText, ExecutionRecord
from backend_v2.services.orchestrator.dag_executor import DAGExecutor

@pytest.fixture
def mock_repo() -> Any:
    return AsyncMock()

@pytest.fixture
def mock_compiler() -> Any:
    return AsyncMock()

@pytest.mark.asyncio
async def test_dag_executor_eagerly_loads_input_files(mock_repo: Any, mock_compiler: Any, tmp_path: Path) -> None:
    """
    Tier 4 Bug Hunting: RED STATE
    Varmistetaan, että DAG Executor lataa .md tiedostot inputs/ kansiosta muistiin.
    """
    execution_id = "exe_1234567890abcdef"
    
    # Mock database record: inputs is empty {}
    existing_record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_5555555555555555",
        status="queued",
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
    )
    mock_repo.get_execution.return_value = existing_record

    # Setup physical file system
    files_dir = tmp_path / "files"
    inputs_dir = files_dir / "executions" / execution_id / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a mock physical input file
    mock_file = inputs_dir / "input_chat_log.md"
    mock_file.write_text("Hello World! Tässä on testitekstiä.", encoding="utf-8")

    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = Workflow(
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        steps=[],
    )

    # Patch get_settings to return our tmp_path as data_dir
    with patch("backend_v2.services.orchestrator.dag_executor.get_settings") as mock_settings:
        # Pydantic Settings mock
        mock_settings.return_value.data_dir = str(tmp_path)
        
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock()
            
            # Execute workflow
            record = await executor.execute_workflow(
                execution_id=execution_id,
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={}),
            )
            
            # The critical assertion: Eager Extraction should have loaded the physical file into raw_inputs
            assert "input_chat_log" in record.raw_inputs.dynamic_inputs, "Eager Extraction ei ladannut .md tiedostoa inputs/ kansiosta!"
            assert "Tässä on testitekstiä" in record.raw_inputs.dynamic_inputs["input_chat_log"]
