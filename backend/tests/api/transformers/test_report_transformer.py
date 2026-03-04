from backend.api.transformers.report_core import ReportTransformer
from backend.models.domain.execution import ExecutionRecord
from backend.models.view import (
    ReportView,
    SectionType,
)
from backend.models.view.semantic_models import (
    ArchivistDisplay,
    CausalDisplay,
    DriverProfileDisplay,
    LogicAnalysisDisplay,
    ProfilerDisplay,
    StressTestDisplay,
)
from backend.models.view.semantic_models import SemanticReport, SemanticBlock


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
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                    "precedents": "Prec",
                    "knowledge_items": [],
                },
                # Logic
                "step_logician": {
                    "logician_data": {
                        "cognitive_level": {
                            "strategic_depth": "STRAT_HIGH",
                            "strategic_score": 3.5,
                            "bloom_level": "BLOOM_EVALUATING",
                            "bloom_score": 5.8,
                        },
                        "toulmin_score": 5.0,
                        "toulmin_analysis": [{"id": "T1", "claim": "C1", "data": "D1", "warrant": "W1"}],
                        "walton_scheme": {"identified_scheme": "Expert Opinion", "critical_questions": ["Q1"]},
                    },
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                },
                # Stress
                "step_falsifier": {
                    "falsifier_data": {
                        "fidelity_audit": {
                            "fidelity_score": "FIDELITY_HIGH",
                            "fidelity_numeric": 3.0,
                            "justification": "Solid",
                            "post_hoc_rationalization": False,
                        },
                        "stress_test_findings": [{"question": "Q1", "evidence_held": True, "observation": "Obs1"}],
                    },
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                },
                # Causal
                "step_causal": {
                    "causal_analysis": {
                        "abductive_reasoning": {"verdict": "OK", "confidence_score": 0.9, "conclusion": "Conc1"},
                        "abductive_conclusion": "GENUINE",
                        "abductive_score": 3.0,
                        "counterfactual_test": {
                            "plausibility": "PLAUSIBLE",
                            "confidence_score": 0.8,
                            "actual_scenario": "A1",
                            "simulated_scenario": "S1",
                            "plausibility_score": "PLAUSIBLE",
                            "plausibility_numeric": 2.0,
                            "simulation_result": "SimResult",
                        },
                        "plausibility_check": {"score": 2.5},
                        "observation": "Obs1",
                        "hypothesis": "Hyp1",
                    },
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                },
                # Profiler
                "step_profiler": {
                    "metrics": {
                        "control_ratio": 0.6,
                        "word_count": 100,
                        "avg_sentence_length": 10.0,
                        "sentence_count": 10,
                        "lexical_diversity": 0.5,
                        "capitalization_ratio": 0.1,
                        "automation_bias": 0.1,
                        "say_do_gap": 0.9,
                    },
                    "author_intent": "Info",
                    "emotional_tone": "Neutral",
                    "cognitive_biases": ["Bias1"],
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                },
                # Driver
                "step_driver": {
                    "role_classification": "Driver",
                    "high_dependency": False,
                    "imperative_command_count": 2,
                    "strategy": "Zero-shot",
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                },
                # Archivist
                "step_archivist": {
                    "compliance_score": 9.5,
                    "compliance_analysis": "Aligned",
                    "description": "Good",
                    "relevant_cases": [],
                    "stare_decisis_adherence": True,
                    "thought_process": "Thinking...",
                    "conclusion": "Conclusion",
                    "confidence_score": 0.9,
                    "consistency_analysis": "Consistent",
                },
            }
        },
    }

    record = ExecutionRecord.model_validate(mock_execution)
    transformer = ReportTransformer()
    report = transformer.transform(record)

    assert isinstance(report, SemanticReport)
    assert report.report_id == "test-integration-001"

    # Check Sections Exist
    sec_ids = {s.id: s.value for s in report.blocks}

    assert "logic-analysis" in sec_ids
    assert isinstance(sec_ids["logic-analysis"], LogicAnalysisDisplay)

    assert "stress-test" in sec_ids
    assert isinstance(sec_ids["stress-test"], StressTestDisplay)

    assert "causal-analysis" in sec_ids
    assert isinstance(sec_ids["causal-analysis"], CausalDisplay)

    assert "profiler-analysis" in sec_ids
    assert isinstance(sec_ids["profiler-analysis"], ProfilerDisplay)

    assert "interaction-grid" in sec_ids
    assert isinstance(sec_ids["interaction-grid"], DriverProfileDisplay)

    assert "archivist-check" in sec_ids
    assert isinstance(sec_ids["archivist-check"], ArchivistDisplay)

def test_report_transformer_references():
    """Verify ReportTransformer extracts contextual citations correctly."""
    from backend.models.view.sdui import ReferenceIntent

    mock_execution = {
        "id": "test-refs-001",
        "status": "completed",
        "results": {
            "context_variables": {
                "search_result": {
                    "results": [
                        {"title": "Search2", "snippet": "Snip2", "link": "url2"}
                    ]
                },
                "bibliography_result": {
                    "items": [
                        {"title": "KB1", "snippet": "KB Snip1", "url": "kb_url1"}
                    ]
                }
            }
        }
    }

    record = ExecutionRecord.model_validate(mock_execution)

    from backend.models.domain.analyst import AnalystOutput
    from backend.models.domain.base import Metadata
    from backend.models.domain.coach import BibliographyResult
    from backend.models.domain.judge import JudgeOutput, JudgeScoreCard

    record.results["context_variables"]["step_analyst"] = AnalystOutput.model_construct(
        rag_evidence=["Raw Search Snippet"]
    )
    score_card = JudgeScoreCard.model_construct(
        agent_name="Test Judge",
        total_score=5.0,
        max_score=5,
        verdict="Great",
        scale_min=1.0,
        scale_max=5.0,
        dimensions=[]
    )
    record.results["context_variables"]["step_judge"] = JudgeOutput.model_construct(
        score_card=score_card,
        metadata=Metadata.model_construct(provider_metadata={"grounding_urls": ["vertex_url1"]})
    )
    record.results["context_variables"]["bibliography_result"] = BibliographyResult.model_construct(
        references=[{"title": "KB1", "snippet": "KB Snip1", "url": "kb_url1"}]
    )

    transformer = ReportTransformer()
    report = transformer.transform(record)

    assert report.references is not None
    assert len(report.references) == 4

    search_refs = [r for r in report.references if r.intent == ReferenceIntent.SEARCH]
    assert len(search_refs) == 2
    assert search_refs[0].title == "Verkkohaku"
    assert search_refs[0].snippet == "Raw Search Snippet"
    assert search_refs[1].title == "Search2"
    assert search_refs[1].url == "url2"

    grounding_refs = [r for r in report.references if r.intent == ReferenceIntent.GROUNDING]
    assert len(grounding_refs) == 1
    assert grounding_refs[0].url == "vertex_url1"

    kb_refs = [r for r in report.references if r.intent == ReferenceIntent.INTERNAL_KB]
    assert len(kb_refs) == 1
    assert kb_refs[0].title == "KB1"
    assert kb_refs[0].snippet == "KB Snip1"
