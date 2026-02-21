from backend.api.transformers.report_core import ReportTransformer
from backend.models.view import ReportView, SectionType
from backend.models.view import (
    ArchivistDisplay,
    CausalDisplay,
    DriverProfileDisplay,
    LogicAnalysisDisplay,
    ProfilerDisplay,
    StressTestDisplay,
)
from backend.models.domain.execution import ExecutionRecord

def test_report_transformer_process_all_stages():
    """Verify ReportTransformer handles a full workflow execution correctly."""
    # Extensive mock data mirroring debug_report_uvm.py structure
    mock_execution = {
        "id": "test-integration-001",
        "status": "completed",
        "results": {
            "step_results": {
                # Context
                "step_context": {
                    "context_data": {
                        "thought_process": "Thinking...",
                        "conclusion": "Conclusion",
                        "confidence_score": 0.9,
                        "precedents": "Prec",
                        "knowledge_items": []
                    }
                },
                # Logic
                "step_logician": {
                    "logician_data": {
                        "cognitive_level": {
                            "strategic_depth": "STRAT_HIGH",
                            "strategic_score": 3.5,
                            "bloom_level": "BLOOM_EVALUATING",
                            "bloom_score": 5.8
                        },
                        "toulmin_score": 5.0,
                        "toulmin_analysis": [{"id": "T1", "claim": "C1", "data": "D1", "warrant": "W1"}],
                        "walton_scheme": {"identified_scheme": "Expert Opinion", "critical_questions": ["Q1"]}
                    },
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9
                },
                # Stress
                "step_falsifier": {
                    "falsifier_data": {
                        "fidelity_audit": {
                            "fidelity_score": "FIDELITY_HIGH",
                            "fidelity_numeric": 3.0,
                            "justification": "Solid",
                            "post_hoc_rationalization": False
                        },
                        "stress_test_findings": [
                            {
                                "question": "Q1",
                                "evidence_held": True,
                                "observation": "Obs1"
                            }
                        ]
                    },
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9
                },
                # Causal
                "step_causal": {
                    "causal_analysis": {
                        "abductive_reasoning": {"verdict": "OK", "confidence_score": 0.9, "conclusion": "Conc1"},
                        "abductive_conclusion": "ABDUCT_GENUINE",
                        "abductive_score": 3.0,
                        "counterfactual_test": {
                            "plausibility": "PLAUSIBLE",
                            "confidence_score": 0.8,
                            "actual_scenario": "A1",
                            "simulated_scenario": "S1",
                            "plausibility_score": "PLAUS_PLAUSIBLE",
                            "plausibility_numeric": 2.0,
                            "simulation_result": "SimResult"
                        },
                        "plausibility_check": {"score": 2.5},
                        "observation": "Obs1",
                        "hypothesis": "Hyp1"
                    },
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9
                },
                # Profiler
                "step_profiler": {
                    "profiler_data": {
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
                },
                # Driver
                "step_driver": {
                    "interaction_analysis": {
                        "role_classification": "Driver",
                        "input_quality_score": 0.9,
                        "improvement_suggestions": ["Direct"],
                        "thought_process": "Thinking...",
                        "conclusion": "Conclusion",
                        "confidence_score": 0.9
                    }
                },
                # Archivist
                "step_archivist": {
                     "archivist_data": {
                         "compliance_score": 9.5,
                         "compliance_analysis": "Aligned",
                         "description": "Good",
                         "relevant_cases": [],
                         "stare_decisis_adherence": True,
                         "thought_process": "Thinking...",
                         "conclusion": "Conclusion",
                         "confidence_score": 0.9,
                         "consistency_analysis": "Consistent"
                     }
                }
            }
        }
    }

    record = ExecutionRecord(**mock_execution)
    transformer = ReportTransformer()
    report = transformer.transform(record)

    assert isinstance(report, ReportView)
    assert report.view_id == "test-integration-001"

    # Check Sections Exist
    sec_types = {s.type: s.data for s in report.sections}

    assert SectionType.LOGIC_ANALYSIS in sec_types
    assert isinstance(sec_types[SectionType.LOGIC_ANALYSIS], LogicAnalysisDisplay)

    assert SectionType.STRESS_TEST in sec_types
    assert isinstance(sec_types[SectionType.STRESS_TEST], StressTestDisplay)

    assert SectionType.CAUSAL_ANALYSIS in sec_types
    assert isinstance(sec_types[SectionType.CAUSAL_ANALYSIS], CausalDisplay)

    assert SectionType.PROFILER_ANALYSIS in sec_types
    assert isinstance(sec_types[SectionType.PROFILER_ANALYSIS], ProfilerDisplay)

    assert SectionType.DRIVER_PROFILE in sec_types
    assert isinstance(sec_types[SectionType.DRIVER_PROFILE], DriverProfileDisplay)

    assert SectionType.ARCHIVIST_CHECK in sec_types
    assert isinstance(sec_types[SectionType.ARCHIVIST_CHECK], ArchivistDisplay)

