from pydantic import ValidationError
from backend.models.domain import ProfilerAnalysis

try:
    data = {
        "metrics": {
            "control_ratio": 0.6,
            "word_count": 100,
            "avg_sentence_length": 10.0,
            "lexical_diversity": 0.5,
            "capitalization_ratio": 0.1,
            "automation_bias": 0.1,
            "say_do_gap": 0.9
        },
        "author_intent": "Info",
        "emotional_tone": "Neutral",
        "cognitive_biases": ["Bias1"],
        "thought_process": "Thinking...",
        "conclusion": "Conclusion",
        "confidence_score": 0.9
    }
    model = ProfilerAnalysis(**data)
    print("SUCCESS")
except ValidationError as e:
    print(e)
except Exception as e:
    print(f"ERROR: {e}")
