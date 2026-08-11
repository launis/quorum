import asyncio
import os
from unittest.mock import AsyncMock
from backend_v2.models.v2_core import Workflow, StepRule, I18nText
from backend_v2.models.enums import HistoricalContextMode, ExecutionStatus
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.models.domain.inputs import WorkflowInputs

async def main():
    repo = AsyncMock()
    repo.get_step_by_id.return_value = {
        "id": "stp_1234567890abcdef",
        "type": "llm",
        "model_strategy": "fast",
        "slug": "mock",
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
        "name": {"default_locale": "en", "translations": {"en": "mock"}},
        "description": {"default_locale": "en", "translations": {"en": "mock"}},
    }
    repo.get_execution.return_value = {
        "id": "exe_1111222233334444",
        "workflow_id": "wf_0000000000000000",
        "status": ExecutionStatus.PENDING,
        "raw_inputs": {"dynamic_inputs": {"log": "test"}},
        "metadata": {"profile_id": "prof_0000000000000000"},
    }
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_1234567890abcdef",
            "slug": "task_bp",
            "label": {"default_locale": "fi", "translations": {"fi": "Testi", "en": "Test"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Kuvaus", "en": "Desc"}},
            "ai_description": "Strict extraction protocol.",
            "category_id": "system_rule",
            "type": "string",
            "allow_decimals": False,
            "output_extensions": [],
        }
    ]
    repo.get_output_profile_by_id.return_value = {
        "id": "prof_0000000000000000",
        "slug": "test_profile",
        "workflow_id": "wf_0000000000000000",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "visible_block_extensions": [],
        "visible_workflow_extensions": [],
    }
    
    workflow = Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0000000000000000",
        slug="wf_ctx_bounds",
        status="draft",
        version=1,
        default_profile_id="prof_0000000000000000",
        name=I18nText(default_locale="en", translations={"en": "Bounds"}),
        description=I18nText(default_locale="en", translations={"en": "Bounds"}),
        steps=[StepRule(id="step_0000000000000000", task_blueprint="bp_fuzz")],
    )

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=AsyncMock(),
    )
    
    print(await repo.get_all_prompt_blocks())

    try:
        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
