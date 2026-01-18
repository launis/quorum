
from backend.services.chat_log_parser import ChatLogParser

def test_parser():
    print("--- CHAT LOG PARSER TEST ---")
    parser = ChatLogParser()
    
    # Case 1: Standard Format (Should work)
    text_standard = "User: Hello\nAI: Hi there."
    result_std = parser.parse(text_standard)
    print(f"Type of result: {type(result_std)}")
    print(f"Standard Result: {result_std}")
    
    # Case 2: Raw Text / Unformatted
    text_raw = "Hello I have a question about the megatrends."
    result_raw = parser.parse(text_raw)
    print(f"Raw Result: {result_raw}")

    # Case 3: Weird spacing
    text_weird = "User : Hello\n AI : Hi"
    result_weird = parser.parse(text_weird)
    print(f"Weird Result: {result_weird}")

if __name__ == "__main__":
    test_parser()
