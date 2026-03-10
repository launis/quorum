import json
from pathlib import Path

def patch_model_strategies():
    v1_path = Path("c:/src/quorum/data/github_seed_data.json")
    v2_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")

    print(f"Loading V1 data from {v1_path}...")
    with open(v1_path, "r", encoding="utf-8") as f:
        v1_data = json.load(f)

    # Extract model strategies from V1 system_config
    model_config = {}
    for config in v1_data.get("system_config", []):
        if config.get("id") == "model_registry":
            models = config.get("models", {}).get("google", {})
            model_config = models
            break

    # Manual mapping from V2 step slugs to V1 Agent keys
    slug_to_agent_key = {
        "step_input_processor": "InputProcessorAgent",
        "step_input_processing": "InputProcessorAgent",
        "step_guard": "GuardAgent",
        "step_retrieval_agent": "RetrievalAgent",
        "step_analyst": "AnalystAgent",
        "step_interaction_analyst": "InteractionAnalystAgent",
        "step_profiler": "ProfilerAgent",
        "step_panel": "PanelAgent",
        "step_archivist": "ArchivistAgent",
        "step_judge": "JudgeAgent",
        "step_cognitive_judge": "JudgeAgent",
        "step_coach": "CoachAgent",
        "step_xai_reporter": "XAIReporterAgent",
        "step_logician": "LogicianAgent",
        "step_falsifier": "LogicalFalsifierAgent",
        "step_causal_analyst": "CausalAnalystAgent",
        "step_performativity_detector": "PerformativityDetectorAgent",
        "step_overseer": "FactualOverseerAgent",
        "step_detector": "PerformativityDetectorAgent",
        "step_causal": "CausalAnalystAgent",
        "step_context": "RetrievalAgent",
        "step_interaction": "InteractionAnalystAgent"
    }

    print(f"Loading V2 data from {v2_path}...")
    with open(v2_path, "r", encoding="utf-8") as f:
        v2_data = json.load(f)

    patched_count = 0
    missing_mappings = set()

    # Patch Workflows
    for workflow in v2_data.get("workflows", []):
        for step_node in workflow.get("steps", []):
            blueprint_slug = step_node.get("task_blueprint")
            
            if blueprint_slug in slug_to_agent_key:
                agent_key = slug_to_agent_key[blueprint_slug]
                # Fallback to 'fast' if not found in config
                strategy = model_config.get(agent_key, "fast")
                
                # Apply the strategy
                step_node["model_strategy"] = strategy
                patched_count += 1
            else:
                missing_mappings.add(blueprint_slug)

    print(f"Patched {patched_count} step nodes with new model_strategy.")
    
    if missing_mappings:
        print(f"Warning: No mapping found for the following task blueprints: {missing_mappings}")

    print(f"Writing updated V2 data to {v2_path}...")
    with open(v2_path, "w", encoding="utf-8") as f:
        json.dump(v2_data, f, indent=4, ensure_ascii=False)

    print("Done!")

if __name__ == "__main__":
    patch_model_strategies()
