
import json
import logging
from pathlib import Path
import sys

# Hack to import from backend
sys.path.append(str(Path.cwd()))

from backend.llm.mock_data import (
    _generate_guard_data,
    _generate_analyst_data,
    _generate_interaction_data,
    _generate_profiler_data,
    _generate_logician_data,
    _generate_falsifier_data,
    _generate_causal_data,
    _generate_performativity_data,
    _generate_fact_checker_data,
    _generate_judge_data,
    _generate_archivist_data,
    _generate_coach_data,
    _generate_xai_data
)

def populate():
    # Map identities used in Provider/Mock to generators
    # Keys must match what MockLLMService._identify_agent_key/heuristics expects
    # 'guard_agent', 'analyst_agent', etc.
    
    mapping = {
        "guard_agent": _generate_guard_data,
        "analyst_agent": _generate_analyst_data,
        "interaction_agent": _generate_interaction_data,
        "profiler_agent": _generate_profiler_data,
        "logician_agent": _generate_logician_data,
        "falsifier_agent": _generate_falsifier_data,
        "causal_agent": _generate_causal_data,
        "performativity_agent": _generate_performativity_data,
        "fact_checker_agent": _generate_fact_checker_data, # Overseer
        "judge_agent": _generate_judge_data,
        "archivist_agent": _generate_archivist_data,
        "coach_agent": _generate_coach_data,
        "xai_agent": _generate_xai_data,
        "reporter_agent": _generate_xai_data # Alias?
    }
    
    responses = {}
    
    print("Generating Mock Responses from mock_data.py...")
    for key, generator in mapping.items():
        try:
            data = generator()
            responses[key] = data
            print(f"✅ Generated {key}")
        except Exception as e:
            print(f"❌ Failed to generate {key}: {e}")

    out_path = Path("data/mock_responses.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccessfully wrote {len(responses)} mock responses to {out_path}")
    print("This file acts as the 'Verified Database' for Mock Mode.")

if __name__ == "__main__":
    populate()
