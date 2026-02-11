
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.api.bff_transformer import AssessmentTransformer

def test_reconstruct_fix():
    transformer = AssessmentTransformer()
    
    # Test case 1: Event with None metadata in content
    # This was causing the error: content["metadata"] is None
    trace = [
        {
            "event_type": "output",
            "step_name": "step_test",
            "content": {"metadata": None}, # Explicitly None
            "timestamp": "2024-01-01T12:00:00Z"
        }
    ]
    
    try:
        result = transformer._reconstruct_state_from_trace(trace)
        print("Success: _reconstruct_state_from_trace handled None metadata.")
        # Verify it initialized it
        if result["step_test"]["metadata"]["luontiaika"] == "2024-01-01T12:00:00Z":
            print("Verified: Timestamp correctly injected.")
    except Exception as e:
        print(f"FAILED: _reconstruct_state_from_trace raised {e}")

def test_transform_signature():
    transformer = AssessmentTransformer()
    # Check if we can call transform with valid_range
    try:
        # Minimal raw data
        raw_data = {"execution_id": "123", "status": "pending"}
        transformer.transform(raw_data, valid_range=(0.0, 1.0))
        print("Success: transform accepted valid_range.")
    except TypeError as e:
        print(f"FAILED: transform raised TypeError: {e}")
    except Exception as e:
        # Ignore other errors (like missing data), we just want to check signature
        print(f"Success (Signature check): transform accepted args, failed later with {e}")

if __name__ == "__main__":
    test_reconstruct_fix()
    test_transform_signature()
