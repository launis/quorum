
import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.core.engine import GraphEngine
from backend.models.workflow import WorkflowDefinition, WorkflowStep
from backend.models.domain.base import ReasoningTrace
from backend.models.domain.analyst import AnalystOutput, Hypothesis
from backend.tasks.critique import register_critique_tasks

# Register tasks manually for standalone test
register_critique_tasks()

# Initialize Logger (Debug)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def run_debug_test():
    """
    Run workflow with explicit step logging and verify Falsifier injection.
    """
    logger.info("Starting DEBUG Workflow Execution...")

    # 1. Load Workflow Definition (from seed or manual)
    # Since seed is missing falsifier, we will construct/inject it.
    
    # Minimal Example Definition
    steps = [
        # For this test, we focus on Falsifier.
        WorkflowStep(
            id="step_falsifier",
            task_key="falsifier",
            inputs={
                "history_text": "inputs.history_text",
                "step_analyst": "inputs.mock_analyst" # Mocking previous step output
            },
            config={
                "model": "gemini-pro", # Use valid model
                "provider": "google",
                "temperature": 0.7
            }
        )
    ]

    definition = WorkflowDefinition(
        id="debug_workflow",
        name="Debug Workflow",
        description="Testing Falsifier with Step Logging",
        steps=steps
    )

    # 2. Mock Initial Inputs
    try:
        mock_analyst = AnalystOutput(
            hypotheses=[
                Hypothesis(
                    id="hyp1",
                    claim_text="The earth is flat.",
                    evidence_found=False,
                    search_query="earth shape proof",
                    quotes=[]
                )
            ],
            rag_evidence=[],
            critical_violation=False,
            # Mandatory ReasoningTrace fields
            thought_process="Mock thought process",
            conclusion="Mock conclusion",
            confidence_score=0.9,
            metadata=None,
            semanttinen_tarkistussumma="mock_checksum"
        )
    except Exception as e:
        logger.error(f"Failed to create Mock AnalystOutput: {e}")
        return
    
    initial_input = {
        "inputs": {
            "history_text": "User: I believe the earth is flat because I can see the horizon is flat.",
            "mock_analyst": mock_analyst
        }
    }

    # 3. Execute with GraphEngine
    engine = GraphEngine()
    
    # MOCK LLM PROVIDER to avoid API keys and network calls
    from unittest.mock import MagicMock
    from backend.llm.provider import LLMProvider
    from backend.models.domain.falsifier import FalsifierOutput, FalsifierData, WaltonStressTest, ReasoningFidelity
    from backend.models.enums import FidelityLevel

    # Pre-construct valid output
    mock_output_obj = FalsifierOutput(
        falsifier_data=FalsifierData(
            stress_test_findings=[
                WaltonStressTest(question="Is the evidence reliable?", evidence_held=False, observation="No evidence provided.")
            ],
            fidelity_audit=ReasoningFidelity(
                fidelity_score=FidelityLevel.WEAK, 
                fidelity_numeric=1.0, 
                justification="Claim is unsupported."
            )
        ),
        thought_process="Mock thought",
        conclusion="Mock conclusion",
        confidence_score=0.9,
        metadata=None,
        semanttinen_tarkistussumma="mock_checksum"
    )

    # Patch the agent *instance* creation? No, GraphEngine instantiates it.
    # We can patch LLMFactory.create_provider to return a mock provider.
    from backend.llm.provider import LLMFactory
    
    mock_provider = MagicMock(spec=LLMProvider)
    # The agent calls generate() which returns a response object with .content
    mock_response = MagicMock()
    mock_response.content = mock_output_obj.model_dump_json()
    mock_response.parsed_content = None 
    mock_response.token_usage = {"total": 10}
    mock_response.messages = []
    
    # Async mock for generate
    async def async_generate(*args, **kwargs):
        return mock_response
    mock_provider.generate = async_generate

    # Patch Factory
    LLMFactory.create_provider = MagicMock(return_value=mock_provider)
    
    logger.info("Injecting Falsifier step into execution flow...")
    
    try:
        # We need a repository for tools that require it? Engine.execute_workflow accepts None.
        result = await engine.execute_workflow(
            definition=definition,
            initial_input=initial_input,
            repository=None # No persistence needed for this debug run
        )
        
        logger.info("Workflow Execution Completed.")
        logger.info(f"Final State Status: {result.get('status')}")
        
        # Verify Falsifier Output
        trace = result.get("execution_trace", [])
        falsifier_event = next((e for e in trace if e['step_name'] == "step_falsifier"), None)
        
        if falsifier_event:
             logger.info("✅ step_falsifier executed successfully!")
             # Clean dump
             def json_serial(obj):
                if isinstance(obj, (datetime, datetime.date)):
                    return obj.isoformat()
                raise TypeError ("Type %s not serializable" % type(obj))
             
             logger.info(f"Output: {json.dumps(falsifier_event, indent=2, default=json_serial)}")
        else:
             logger.error("❌ step_falsifier did NOT execute.")
             # Check if there were errors
             errors = [e for e in trace if e['event_type'] == 'error']
             if errors:
                 logger.error(f"Errors found: {json.dumps(errors, indent=2, default=str)}")
             
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_debug_test())
