from backend.services.chat_log_parser import ChatLogParser

def test_gemini_format():
    print("Testing Gemini Format...")
    raw_text = """Gemini Chat\n\nHello, who are you?\n\nI am a large language model, trained by Google."""
    parsed = ChatLogParser.parse(raw_text)
    assert "User: Hello" in parsed
    assert "AI: I am a large" in parsed
    print("Gemini Format: PASS")

def test_timestamp_format():
    print("Testing Timestamp Format...")
    raw_text = """[14:05] Risto: Hello\n[14:06] Gemini: Hi there."""
    parsed = ChatLogParser.parse(raw_text)
    assert "User: Hello" in parsed
    assert "AI: Hi there" in parsed
    print("Timestamp Format: PASS")

def test_fallback():
    print("Testing Fallback...")
    raw_text = "Just some random text."
    parsed = ChatLogParser.parse(raw_text)
    assert parsed == raw_text
    print("Fallback: PASS")

if __name__ == "__main__":
    test_gemini_format()
    test_timestamp_format()
    test_fallback()
