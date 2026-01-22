import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_synth")

def synthesize_config():
    target_path = 'c:/src/quorum/backend/seed/seed_data.json'
    
    # Correct Structure: List of objects, not a single dict
    new_system_config = [
        {
            "id": "model_registry",
            "type": "model_registry",
            "models": {
                "google": {
                    "deep": {
                        "max_tokens": 16384,
                        "model_name": "vertex_ai/gemini-2.5-pro",
                        "temperature": 0.5,
                        "top_p": None
                    },
                    "fast": {
                        "max_tokens": 16384,
                        "model_name": "vertex_ai/gemini-2.5-flash",
                        "temperature": 0.7,
                        "top_p": None
                    },
                    "strict": {
                        "max_tokens": 16384,
                        "model_name": "vertex_ai/gemini-2.5-flash",
                        "temperature": 0.0,
                        "top_p": None
                    },
                    "precise": {
                        "max_tokens": 16384,
                        "model_name": "vertex_ai/gemini-2.5-pro",
                        "temperature": 0.2,
                        "top_p": None
                    },
                    "AnalystAgent": "precise",
                    "InteractionAnalystAgent": "deep",
                    "ProfilerAgent": "deep",
                    "LogicianAgent": "precise",
                    "LogicalFalsifierAgent": "precise",
                    "CausalAnalystAgent": "deep",
                    "PerformativityDetectorAgent": "deep",
                    "FactualOverseerAgent": "precise",
                    "ArchivistAgent": "precise",
                    "JudgeAgent": "deep",
                    "CoachAgent": "deep",
                    "XAIReporterAgent": "deep",
                    "PanelAgent": "deep",
                    "GuardAgent": "strict",
                    "RetrievalAgent": "strict"
                }
            }
        },
        {
            "id": "knowledge_base",
            "type": "knowledge_base",
            "content": []
        }
    ]

    logger.info("Synthesized new system_config (LIST format).")

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Overwrite content
        data['system_config'] = new_system_config
        
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        logger.info(f"Successfully injected synthesized config into {target_path}")
        
    except Exception as e:
        logger.error(f"Failed to update seed data: {e}")

if __name__ == "__main__":
    synthesize_config()
