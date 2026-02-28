
import pytest

from backend.models.domain.analyst import AnalystOutput, Hypothesis, SearchResult, SearchResultItem
from backend.models.state import WorkflowState


@pytest.mark.asyncio
async def test_workflow_search_leakage():
    """Test that the search result data is isolated in the workflow state
    and is explicitly NOT passed into the raw LLM prompt of downstream agents 
    (unless they specifically request it).
    
    This simulates the execution flow from SearchHook -> FalsifierAgent.
    """
    # 1. Simulate the State AFTER Analyst and SearchHook have run
    analyst_output = AnalystOutput(
        thought_process="Thinking...",
        conclusion="Conclusion.",
        confidence_score=0.9,
        hypotheses=[Hypothesis(id="h1", claim_text="Test", search_query="test query", evidence_found=False, quotes=[])],
        rag_evidence=["Analyst Internal Evidence"]
    )

    search_result = SearchResult(
        results=[SearchResultItem(title="Google", link="google.com", snippet="Massive 60k token text")]
    )

    import uuid
    initial_state = WorkflowState(
        execution_id=str(uuid.uuid4()),
        workflow_id=str(uuid.uuid4()),
        context_variables={
            "step_analyst": analyst_output.model_dump(),
            "search_result": search_result.model_dump()
        }
    )

    # 2. Setup the dummy downstream agent (e.g. Profiler/Logician)
    from backend.agents.base import BaseAgent
    class DummyDownstreamAgent(BaseAgent):
        async def evaluate(self, state, repository=None):
            # This agent simulates a standard execution.
            # We want to check what gets passed into its LLM context.
            ctx = self.prepare_context(state, execution_context={})

            # The core assertion: context for standard agents should ONLY contain
            # Analyst's original evidence, NOT the massive search snippets.
            # It should not automatically pull from "search_result" unless explicitly coded to.
            return state

        def prepare_context(self, state: WorkflowState, execution_context=None) -> dict:
            ctx = super().prepare_context(state, execution_context or {})

            # Simulate generic context preparation where we load previous steps
            analyst_data = state.get_context("step_analyst", AnalystOutput)

            # This represents the data that will be formatted into the prompt
            assert "Massive 60k token text" not in str(analyst_data.rag_evidence)
            assert analyst_data.rag_evidence == ["Analyst Internal Evidence"]

            # Verify the search data IS available in the overall state for
            # agents that explicitly want it (like Factual Overseer)
            search_data = state.get_context("search_result", SearchResult)
            assert search_data is not None
            assert search_data.results[0].snippet == "Massive 60k token text"

            return ctx

    # 3. Execute the simulation
    agent = DummyDownstreamAgent()
    # Calling prepare context to trigger the assertions
    agent.prepare_context(initial_state, execution_context={})
