import pytest
from backend.services.reference_manager import ReferenceManager
from backend.models.dtos.knowledge_base import KnowledgeBaseSchema, CitationReport
from backend.exceptions import AppException, ErrorCodes

class TestReferenceManager:
    
    def test_init_success_with_schema(self):
        """Test strict schema processing."""
        valid_kb = {
            "references": [
                {"short_citation": "Smith 2023", "citation": "Smith, J. (2023). Future of AI."}
            ],
            "concepts": [
                {"term": "AI", "definition": "Artificial Intelligence"}
            ]
        }
        
        manager = ReferenceManager(valid_kb)
        
        # Verify map built correctly
        assert "smith 2023" in manager.references_map
        assert manager.references_map["smith 2023"] == "Smith, J. (2023). Future of AI."
        print("\n[TEST] Init Success: References Mapped")

    def test_init_fail_fast_invalid_schema(self):
        """Test Fail Fast on invalid schema."""
        invalid_kb = {
            "references": [
                {"short_citation": ""} # EMPTY citation -> Should fail strict validator
            ],
            "concepts": []
        }
        
        with pytest.raises(AppException) as excinfo:
            ReferenceManager(invalid_kb)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.KNOWLEDGE_BASE_INVALID
        print("\n[TEST] Init Fail Fast: Invalid Schema Caught")

    def test_advanced_scan_typed_return(self):
        """Test advanced_scan returns strictly typed ReferenceReport."""
        valid_kb = {
            "references": [
                {"short_citation": "Smith 2023", "citation": "Smith, J. (2023). Future of AI."}
            ],
            "concepts": [
                {"term": "Machine Learning", "definition": "See (Smith 2023)."}
            ]
        }
        manager = ReferenceManager(valid_kb)
        
        # Text mentions "Machine Learning" concept, which links to Smith 2023
        report = manager.advanced_scan("The system uses Machine Learning extensively.")
        
        assert isinstance(report, CitationReport)
        assert len(report.relevance_map) > 0
        assert "Smith, J. (2023). Future of AI." in report.relevance_map
        print("\n[TEST] Advanced Scan: Typed Report Success")

if __name__ == "__main__":
    t = TestReferenceManager()
    t.test_init_success_with_schema()
    try:
        t.test_init_fail_fast_invalid_schema()
    except Exception as e:
        print(f"FAILED: {e}")
    t.test_advanced_scan_typed_return()
