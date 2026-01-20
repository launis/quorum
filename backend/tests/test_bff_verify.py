import pytest
from backend.api.bff_transformer import ReportTransformer
from backend.models.view import SectionType

class TestReportTransformer:
    
    def setup_method(self):
        self.transformer = ReportTransformer()

    def test_valid_score_card(self):
        """Test standard valid payload"""
        payload = {
            "id": "123",
            "results": {
                "step_judge": {
                    "scale_min": 1,
                    "scale_max": 4,
                    "total_score": 3.5,
                    "final_verdict": "Driver"
                }
            }
        }
        view = self.transformer.transform(payload)
        
        # Check Section 0 is ScoreCard
        assert len(view.sections) > 0
        card = view.sections[0]
        assert card.type == SectionType.SCORE_CARD
        assert card.data["total_score"] == 3.5
        assert card.data["verdict"] == "Driver"

    def test_strict_score_validation_overflow(self):
        """Test strict rejection of score > 4"""
        payload = {
            "id": "bad_score",
            "results": {
                "step_judge": {
                    "scale_min": 1,
                    "scale_max": 4,
                    "total_score": 5.0, # INVALID
                    "final_verdict": "Driver"
                }
            }
        }
        with pytest.raises(ValueError) as excinfo:
            self.transformer.transform(payload)
        
        assert "out of valid range" in str(excinfo.value)

    def test_strict_score_validation_underflow(self):
        """Test strict rejection of score < 1"""
        payload = {
            "id": "bad_score_low",
            "results": {
                "step_judge": {
                    "scale_min": 1,
                    "scale_max": 4,
                    "total_score": 0.5, # INVALID
                    "final_verdict": "Driver"
                }
            }
        }
        with pytest.raises(ValueError) as excinfo:
            self.transformer.transform(payload)
            
        assert "out of valid range" in str(excinfo.value)

    def test_new_format_score_cards(self):
        """Test handling of list-based score_cards format"""
        payload = {
            "id": "new_format",
            "results": {
                "step_judge_cognitive": {
                   "scale_min": 1,
                   "scale_max": 4,
                   "score_cards": [
                       {
                           "total_score": 2.2,
                           "verdict": "Passenger",
                           "dimensions": []
                       }
                   ]
                }
            }
        }
        view = self.transformer.transform(payload)
        card = view.sections[0]
        assert card.data["total_score"] == 2.2
        assert card.data["verdict"] == "Passenger"

    def test_audit_log_flattening(self):
        """Test that audit logs are flattened and sanitized"""
        payload = {
            "id": "logs",
            "results": {
                "step_judge": {
                     "scale_min": 1,
                     "scale_max": 4,
                     "total_score": 3.0,
                     "metadata": {
                         "luontiaika": "2026-01-01T12:00:00",
                         "audit_logs": [
                             {"role": "system", "content": "HIDDEN"},
                             {"role": "user", "content": "Show <<REFERENCE: ref>>"}
                         ]
                     }
                }
            }
        }
        view = self.transformer.transform(payload)
        
        # Find Timeline
        timeline = next(s for s in view.sections if s.type == SectionType.TIMELINE_FEED)
        entries = timeline.data["entries"]
        
        # Should have 1 entry (User), System hidden
        logs = [e for e in entries if e["type"] == "log"]
        assert len(logs) == 1
        assert "HIDDEN" not in logs[0]["message"]
        assert "[Viittaus: ref]" in logs[0]["message"]

    def test_dynamic_scale_override(self):
        """Test that we can override the scale dynamically (Propagated from DB)"""
        # Case: Matrix Logic uses 1-10
        payload = {
            "id": "scale_10",
            "results": {
                "step_judge": {
                    "total_score": 8.5, # Valid in 1-10, Invalid in 1-4
                    "final_verdict": "Driver"
                }
            }
        }
        
        # 1. Should fail because NO scale is present (Strict Mode)
        with pytest.raises(ValueError) as excinfo:
            self.transformer.transform(payload) 
        assert "Fallback is forbidden" in str(excinfo.value)

        # 2. Should pass with injected scale (1-10)
        view = self.transformer.transform(payload, valid_range=(1.0, 10.0))
        card = view.sections[0]
        assert card.data["total_score"] == 8.5
        assert card.data["max_score"] == 10.0

if __name__ == "__main__":
    # Allow running directly
    import sys
    try:
        t = TestReportTransformer()
        t.setup_method()
        print("Running test_valid_score_card...")
        t.test_valid_score_card()
        print("Running test_strict_score_validation_overflow...")
        t.test_strict_score_validation_overflow()
        print("Running test_strict_score_validation_underflow...")
        t.test_strict_score_validation_underflow()
        print("Running test_new_format_score_cards...")
        t.test_new_format_score_cards()
        print("Running test_audit_log_flattening...")
        t.test_audit_log_flattening()
        print("Running test_dynamic_scale_override...")
        t.test_dynamic_scale_override()
        print("All manual verify tests passed!")
    except Exception as e:
        print(f"FAILED AT STEP: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
