
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.models.domain.guard import GuardInput
from backend.models.domain.analyst import AnalystInput
from backend.models.domain.profiler import ProfilerInput
from backend.models.domain.logician import LogicianInput
from backend.models.domain.judge import JudgeInput
from backend.models.domain.panel import PanelInput
from backend.models.domain.xai import XAIReporterInput
from backend.models.domain.interaction import InteractionInput
from backend.models.domain.coach import CoachInput
from backend.models.domain.archivist import ArchivistInput
from backend.models.domain.falsifier import FalsifierInput
from backend.models.domain.overseer import OverseerInput
from backend.models.domain.causal import CausalInput
from backend.models.domain.performativity import PerformativityInput
from backend.models.domain.retrieval import RetrievalInput

def test_inputs():
    print("Verifying Input Models accept 'last_reasoning_trace'...")
    
    trace = "test_trace_content"
    
    try:
        # Guard
        g = GuardInput(history_text="h", product_text="p", last_reasoning_trace=trace)
        print(f"GuardInput: OK")
        
        # Analyst
        a = AnalystInput(history_text="h", last_reasoning_trace=trace)
        print(f"AnalystInput: OK")
        
        # Profiler
        p = ProfilerInput(history_text="h", last_reasoning_trace=trace)
        print(f"ProfilerInput: OK")
        
        # Logician
        l = LogicianInput(history_text="h", last_reasoning_trace=trace)
        print(f"LogicianInput: OK")

        # Judge
        j = JudgeInput(history_text="h", last_reasoning_trace=trace)
        print(f"JudgeInput: OK")

        # Panel
        pn = PanelInput(history_text="h", product_text="p", last_reasoning_trace=trace)
        print(f"PanelInput: OK")

        # XAI
        x = XAIReporterInput(last_reasoning_trace=trace, step_judge_1={})
        print(f"XAIReporterInput: OK")

        # Interaction
        i = InteractionInput(history_text="h", last_reasoning_trace=trace)
        print(f"InteractionInput: OK")

        # Coach
        c = CoachInput(history_text="h", step_judge={}, last_reasoning_trace=trace)
        print(f"CoachInput: OK")

        # Archivist
        ar = ArchivistInput(history_text="h", last_reasoning_trace=trace)
        print(f"ArchivistInput: OK")

        # Falsifier
        f = FalsifierInput(history_text="h", last_reasoning_trace=trace)
        print(f"FalsifierInput: OK")

        # Overseer
        o = OverseerInput(history_text="h", last_reasoning_trace=trace)
        print(f"OverseerInput: OK")

        # Causal
        ca = CausalInput(history_text="h", last_reasoning_trace=trace)
        print(f"CausalInput: OK")

        # Performativity
        pe = PerformativityInput(history_text="h", last_reasoning_trace=trace)
        print(f"PerformativityInput: OK")

        # Retrieval
        r = RetrievalInput(organization_id="org_1", query="q", last_reasoning_trace=trace)
        print(f"RetrievalInput: OK")

        print("\nSUCCESS: All Input Models updated correctly.")

    except Exception as e:
        print(f"\nFAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_inputs()
