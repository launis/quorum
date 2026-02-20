
import logging
from backend.services.chat_log_parser import ChatLogParser

def test_arrow_parser():
    # Simulation of the user's scenario:
    # A PDF that contains text, some User/AI labels presumably, and ARROWS.
    # And potentially is large.
    
    # 1. Simulate a large file with one arrow at the end
    # If the user says "reads too much", maybe it duplicates the preamble?
    
    preamble = "Content line.\n" * 1000 # 1000 lines
    text = preamble + "\u2192 User: Question"
    
    print(f"Input Length: {len(text)}")
    parsed = ChatLogParser.parse(text)
    print(f"Output Length: {len(parsed)}")
    
    if len(parsed) > len(text) * 1.5:
        print("CRITICAL: Output is significantly larger than input! Duplication detected.")
    else:
        print("Size check pass.")

    # 2. Simulate correct parsing structure
    # Does it preserve content or mess it up?
    sample = "Context\n\u2192 User: Q\nAI: A"
    print(f"\nInput: {sample}")
    print(f"Output: {ChatLogParser.parse(sample)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_arrow_parser()
