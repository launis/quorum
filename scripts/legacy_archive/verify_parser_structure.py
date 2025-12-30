
import sys
import os
from unittest.mock import MagicMock

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.knowledge_base_parser import KnowledgeBaseParser

def test_parser_structure():
    print("\n--- Testing KnowledgeBaseParser Structure Splitting ---")
    
    # Mock docx Document and Paragraphs
    mock_doc = MagicMock()
    
    def create_para(text, style):
        p = MagicMock()
        p.text = text
        p.style.name = style
        return p
        
    paragraphs = [
        create_para("Intro", "Normal"),
        create_para("Concept A", "Heading 1"),
        create_para("Definition A1.", "Normal"),
        create_para("Definition A2.", "Normal"),
        create_para("Concept B", "Heading 2"),
        create_para("Definition B1.", "Normal"),
        create_para("NON-CONCEPT HEADING", "Heading 3"), # Test rejection/acceptance logic?
        create_para("Concept C", "HEADING 1") # Case insensitive style?
    ]
    
    mock_doc.paragraphs = paragraphs
    
    # Inject mock into docx.Document but wait, parse_docx takes file input and calls docx.Document(file_input)
    # So we need to patch docx.Document
    
    import docx
    original_Document = docx.Document
    docx.Document = MagicMock(return_value=mock_doc)
    
    try:
        kb = KnowledgeBaseParser.parse_docx("dummy.docx")
        concepts = kb['concepts']
        
        print(f"Extracted {len(concepts)} concepts: {[c['term'] for c in concepts]}")
        
        # Expected: Concept A, Concept B, Concept C (maybe?)
        # My suspicion: It might have merged them or skipped "Concept B" if logic is broken.
        
        if len(concepts) >= 2:
            print("PASS: Multiple concepts extracted.")
            for c in concepts:
                print(f"  Concept: {c['term']}")
                print(f"  Definition Length: {len(c['definition'])}")
        else:
            print("FAIL: Concepts not split correctly.")
            
    finally:
        docx.Document = original_Document

if __name__ == "__main__":
    try:
        test_parser_structure()
    except Exception as e:
        print(f"Test Error: {e}")
