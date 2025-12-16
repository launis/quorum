import docx
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class KnowledgeBaseParser:
    """
    Parses 'Holistinen Mestaruus.docx' into concepts and bibliography.
    """

    @staticmethod
    def parse_docx(file_input: Any) -> Dict[str, Any]:
        """
        Parses DOCX from file path (str) or file-like object (bytes/stream).
        """
        logger.info(f"[KBParser] Parsing input (Type: {type(file_input)})")
        try:
            doc = docx.Document(file_input)
        except Exception as e:
            logger.error(f"[KBParser] Failed to open document: {e}")
            raise e

        # Data structure
        knowledge_base = {
            "concepts": [], # List of {term, definition}
            "references": [], # List of {citation, doi_link}
            "metadata": {"source": str(file_input)[:100]}
        }

        # Regex for DOI
        # Matches: 10.xxxx/xxxxx usually.
        # Captures: 10.\d{4,9}/[-._;()/:A-Z0-9]+
        doi_pattern = re.compile(r'\b(10.\d{4,9}/[-._;()/:A-Z0-9]+)\b', re.IGNORECASE)

        current_concept = None
        current_definition = []
        
        in_bibliography = False

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Heuristics
            style_name = para.style.name.lower()
            
            # Detect Bibliography Section
            if "lähdeluettelo" in text.lower() or "bibliography" in text.lower():
                # If header style or just bold/standalone
                if "heading" in style_name or len(text) < 20: 
                    in_bibliography = True
                    # Close previous concept if any
                    if current_concept:
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": "\n".join(current_definition)
                        })
                        current_concept = None
                        current_definition = []
                    logger.info("[KBParser] Bibliography section detected.")
                    continue

            if in_bibliography:
                # Every paragraph is a reference
                citation = text
                # Find DOI
                doi_match = doi_pattern.search(citation)
                doi_link = None
                if doi_match:
                    doi_raw = doi_match.group(1)
                    doi_link = f"https://doi.org/{doi_raw}"
                    # Maybe clear trailing punctuation from regex capture if necessary
                
                
                knowledge_base["references"].append({
                    "citation": citation,
                    "short_citation": KnowledgeBaseParser.extract_short_citation(citation),
                    "doi_link": doi_link
                })
            else:
                # Concepts Processing
                # Assume Heading 1 or Heading 2 is a Concept
                if "heading" in style_name and "1" not in style_name: 
                    # Generally H2 is specific enough. H1 might be "Theory"
                    # But if the doc is flat, everything is H1.
                    # Let's assume standard structure: H1=Title, H2=Concept
                    
                    # Close previous
                    if current_concept:
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": "\n".join(current_definition)
                        })
                    
                    current_concept = text
                    current_definition = []
                elif "heading" in style_name or (len(text) < 50 and text.isupper()): 
                     # Maybe H1 or ALL CAPS line is broad concept or section separator?
                     
                     # Close previous
                     if current_concept:
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": "\n".join(current_definition)
                        })
                     
                     current_concept = text
                     current_definition = []
                else:
                    if current_concept:
                        current_definition.append(text)
                        pass
        
        # Flush last
        if current_concept:
            knowledge_base["concepts"].append({
                "term": current_concept,
                "definition": "\n".join(current_definition)
            })

        logger.info(f"[KBParser] Extracted {len(knowledge_base['concepts'])} concepts and {len(knowledge_base['references'])} references.")
        return knowledge_base

    @staticmethod
    def extract_short_citation(full_entry: str) -> Optional[str]:
        """
        Extracts 'Author Year' or 'Author & Author Year' from full entry.
        Example: "Acemoglu, Daron & Restrepo, Pascual. 2018:" -> "Acemoglu & Restrepo 2018"
        """
        if not full_entry:
            return None
            
        # Pattern: Start of string, capture names until year
        match = re.match(r'^(.+?)\.\s*(\d{4}[a-z]?)[.:]', full_entry)
        if match:
            authors_part = match.group(1)
            year = match.group(2)
            
            # Remove (toim.) etc
            authors_part = re.sub(r'\s*\(.*?\)', '', authors_part)
            
            authors = []
            # Split by & first
            parts = authors_part.split('&')
            for part in parts:
                # Split by comma to get surname
                names = part.strip().split(',')
                surname = names[0].strip()
                authors.append(surname)
                
            short_authors = " & ".join(authors)
            return f"{short_authors} {year}"
        return None
