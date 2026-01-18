
from backend.services.chat_log_parser import ChatLogParser

def test(name, text):
    print(f"\n--- TEST: {name} ---")
    print(f"INPUT:\n{repr(text)}")
    parsed = ChatLogParser.parse(text)
    print(f"OUTPUT:\n{parsed}")
    print("-" * 20)

# Case 1: Ideal (Double Newlines / Paragraphs)
# Logic: Empty lines trigger role flip.
text_ideal = """Gemini Chat
Moi
Mitä kuuluu?

Hyvää kuuluu.
Entä sinulle?

Kiitos kysymästä."""

# Case 2: Tight (Single Newlines only)
# Logic: No empty lines -> One big block (User)
text_tight = """Gemini Chat
Moi
Mitä kuuluu?
Hyvää kuuluu.
Entä sinulle?
Kiitos kysymästä."""

# Case 3: Explicit Labels (Single Newlines)
# Logic: Explicit "AI:" triggers role flip even without empty lines.
text_explicit = """Gemini Chat
User: Moi
Mitä kuuluu?
AI: Hyvää kuuluu.
Entä sinulle?
User: Kiitos."""

if __name__ == "__main__":
    test("Implicit (Paragraphs)", text_ideal)
    test("Implicit (Tight)", text_tight)
    test("Explicit Labels", text_explicit)
