
import pytest
from backend.services.chat_log_parser import ChatLogParser
from backend.exceptions import AppException

class TestChatLogParser:

    def test_parse_explicit_format(self):
        """Test already formatted text (User:/AI: prefix)."""
        text = "User: Hello\nAI: Hi there"
        parsed = ChatLogParser.parse(text)
        assert parsed == text

    def test_parse_gemini_format(self):
        """Test Gemini copy-paste format."""
        text = """Gemini Chat
        
        Hello, I have a question.
        
        Sure, ask away!
        
        What is the capital of Finland?
        
        Helsinki is the capital.
        """
        parsed = ChatLogParser.parse(text)
        assert "User: Hello, I have a question." in parsed
        assert "AI: Sure, ask away!" in parsed
        assert "User: What is the capital" in parsed
        assert "AI: Helsinki" in parsed

    def test_parse_chatgpt_format(self):
        """Test ChatGPT copy-paste format."""
        text = """User
        Can you help me?
        ChatGPT
        Certainly! How can I help?
        """
        parsed = ChatLogParser.parse(text)
        assert "User: Can you help me?" in parsed
        assert "AI: Certainly!" in parsed

    def test_parse_claude_format(self):
        """Test Claude format (Human:/Assistant:)."""
        text = "Human: Who are you?\nAssistant: I am Claude."
        parsed = ChatLogParser.parse(text)
        assert "User: Who are you?" in parsed
        assert "AI: I am Claude." in parsed

    def test_parse_timestamp_format(self):
        """Test timestamp format [HH:MM] Name:."""
        text = "[12:00] Risto: Hello bot.\n[12:01] Gemini Bot: Hello human."
        parsed = ChatLogParser.parse(text)
        assert "User: Hello bot." in parsed
        assert "AI: Hello human." in parsed

    def test_parse_arrow_format_with_embedded_list(self):
        """Test Arrow format where User text is embedded in a list without newlines."""
        # This matches the raw extraction from the Sitra PDF
        text = "kehistyksen periaatteita. → mikä on sitran näkemys suunnasta eteenpäin ei siis toivetila 5. Ihmiset ja Hyvinvointi"
        parsed = ChatLogParser.parse(text)
        
        # We expect the parser to identify the arrow as User and the numbered list '5.' as the resume of AI
        assert "User: mikä on sitran näkemys" in parsed
        assert "toivetila" in parsed
        # The parser should ideally insert a break before "5. Ihmiset" to attribute it back to AI (or just keep it separate)
        # For now, let's just ensure User is detected.
        assert "AI: 5. Ihmiset" in parsed or "5. Ihmiset" not in parsed.split("User:")[1]

    def test_parse_arrow_with_header_response(self):
        """Test Arrow format where AI response starts with a Header (not a numbered list)."""
        text = "some context \u2192 koosta raportti Analyysi Megatrendeistä (2023)"
        parsed = ChatLogParser.parse(text)
        
        assert "User: koosta raportti" in parsed
        assert "AI: Analyysi Megatrendeistä" in parsed
    
    def test_empty_input_raises_error(self):
        """Test strict error handling for empty input."""
        with pytest.raises(AppException):
            ChatLogParser.parse("")

    def test_fallback_unknown_format(self):
        """Test fallback for unstructured text."""
        text = "Just some random text without structure."
        parsed = ChatLogParser.parse(text)
        assert parsed == f"User: {text}"
