
import os
import sys

from jinja2 import Environment, FileSystemLoader


# Mock translation filter
def translate_filter(key):
    return f"[[{key}]]"

def render_strict_test():
    # 1. Setup Environment
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["translate"] = translate_filter

    # 2. Mock Data with MISSING/NONE values (Strict Test)
    # Must match ReportView structure
    mock_view = {
        "title": "Strict SDUI Test",
        "view_id": "TEST-STRICT-001",
        "status_theme": "warning",
        "metrics": {
            "word_count": 0,
            "sentence_count": 0,
            "lexical_diversity": 0.0
        },
        "sections": [
            {
                "type": "LOGIC_ANALYSIS",
                "title": "Logic Analysis",
                "data": {
                    "logic_display": {
                        "bloom_score": None,
                        "bloom_percent": None,
                        "bloom_label_key": None,
                        "strategic_score": None,
                        "strategic_percent": None,
                        "strategic_label_key": None,
                        "toulmin_score": None,
                        "toulmin_percent": None,
                        "quadrant_key": None,
                        "quadrant_label_key": None,
                        "position_label": None,
                        "bloom_level_raw": None,
                        "strategic_depth_raw": None,
                        "arguments": []
                    }
                }
            },
            {
                "type": "STRESS_TEST",
                "title": "Stress Test",
                "data": {
                    "stress_display": {
                        "fidelity_audit": None,
                        "abductive_score": None,
                        "abductive_percent": None,
                        "abductive_conclusion": None,
                        "counterfactual_actual": None,
                        "counterfactual_simulated": None,
                        "plausibility_score": None,
                        "plausibility_percent": None
                    }
                }
            },
            {
                "type": "PERFORMATIVITY_CHECK",
                "title": "Performativity",
                "data": {
                    "performativity_display": {
                        "authenticity_score": None,
                        "authenticity_percent": None,
                        "authenticity_assessment": None,
                        "heuristics": []
                    }
                }
            },
            {
                "type": "FACT_CHECK",
                "title": "Fact Check",
                "data": {
                    "fact_check_display": {
                        "verified_facts": [],
                        "ethical_issues": []
                    }
                }
            },
            {
                "type": "SECURITY_CHECK",
                "title": "Security",
                "data": {
                    "security_display": {
                        "threat_detected": False,
                        "threat_color": "green",
                        "threat_label": "UHKA: EI",
                        "risk_level": None,
                        "risk_color": "grey",
                        "anonymized": False,
                        "anonymized_color": "orange",
                        "anonymized_label": "EI ANONYMISOITU",
                        "findings": []
                    },
                    "profiler_display": {
                        "control_ratio_percent": None,
                        "control_label_key": None,
                        "control_help": "Help",
                        "word_count": 0,
                        "word_count_help": "Help",
                        "avg_sentence_length": 0.0,
                        "lexical_diversity": 0.0,
                        "capitalization_ratio_percent": 0,
                        "automation_bias_label": "NONE",
                        "automation_bias_color": "black",
                        "say_do_gap_label": "NONE",
                        "say_do_gap_color": "black",
                        "psychological_profile": None,
                        "intent_analysis": None
                    },
                    "archivist_display": {
                        "compliance_score": None,
                        "compliance_analysis": None,
                        "compliance_help": "Help",
                        "recommendations": []
                    },
                    "driver_display": {
                        "classification": None,
                        "input_quality_label": None,
                        "strategies": []
                    }
                }
            }
        ]
    }

    # 3. Render
    try:
        template = env.get_template("dashboard_pdf.html")
        # Pass 'view' as expected by the template
        html_out = template.render(view=mock_view)

        output_path = os.path.abspath("preview_strict.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_out)

        print(f" Strict verification successful. Output written to {output_path}")
        return 0
    except Exception as e:
        print(f"ERROR: Template failed to render with None values: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(render_strict_test())
