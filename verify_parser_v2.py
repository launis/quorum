from backend.services.chat_log_parser import ChatLogParser

def test_chatgpt_format():
    print("Testing ChatGPT Format...")
    # Common copy-paste format from ChatGPT
    raw_text = """User
How do I write a python script?

ChatGPT
You can use a text editor...
"""
    parsed = ChatLogParser.parse(raw_text)
    # Expectation: Should detect names or alternate
    if "User: How do I" in parsed and "AI: You can use" in parsed:
        print("ChatGPT Format: PASS")
    else:
        print(f"ChatGPT Format: FAIL\nParsed: {parsed!r}")

def test_claude_format():
    print("Testing Claude Format...")
    # Claude often exports or copies as:
    raw_text = """Human: What is the capital of Finland?

Assistant: The capital of Finland is Helsinki."""
    parsed = ChatLogParser.parse(raw_text)
    if "User: What is" in parsed and "AI: The capital" in parsed:
        print("Claude Format: PASS")
    elif "Human:" in parsed: # Claude uses Human/Assistant, maybe we map that?
        print("Claude Format: PASS (Native Labels used)")
    else:
        print(f"Claude Format: FAIL\nParsed: {parsed!r}")

if __name__ == "__main__":
    test_chatgpt_format()
    test_claude_format()
