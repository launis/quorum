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

    @staticmethod
    def parse_md(file_input: Any) -> Dict[str, Any]:
        """
        Parses Markdown from file path (str) or file-like object (bytes/stream).
        """
        logger.info(f"[KBParser] Parsing MD input (Type: {type(file_input)})")
        
        content_str = ""
        if isinstance(file_input, str):
            with open(file_input, 'r', encoding='utf-8') as f:
                content_str = f.read()
        else:
            # Assume stream/bytes
            if hasattr(file_input, 'read'):
                content = file_input.read()
                if isinstance(content, bytes):
                    content_str = content.decode('utf-8')
                else:
                    content_str = content
            elif isinstance(file_input, bytes):
                content_str = file_input.decode('utf-8')
        
        lines = content_str.splitlines()

        # Data structure
        knowledge_base = {
            "concepts": [], # List of {term, definition}
            "references": [], # List of {citation, doi_link}
            "metadata": {"source": "markdown_upload"}
        }

        # Regex for DOI
        doi_pattern = re.compile(r'\b(10.\d{4,9}/[-._;()/:A-Z0-9]+)\b', re.IGNORECASE)
        # Regex for Bibliography Header
        # Allow HTML tags (like <a id="...">) between #'s and the text
        bib_header_pattern = re.compile(r'^#+\s*(?:<[^>]+>\s*)*(Lähdeluettelo|Bibliography|Lähteet|References)', re.IGNORECASE)
        # Regex for Concept Header
        concept_header_pattern = re.compile(r'^(#+)\s*(.+)')

        current_concept = None
        current_definition = []
        
        in_bibliography = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for Bibliography Header
            if bib_header_pattern.match(line):
                in_bibliography = True
                # Close previous concept
                if current_concept:
                    knowledge_base["concepts"].append({
                        "term": current_concept,
                        "definition": "\n".join(current_definition)
                    })
                    current_concept = None
                    current_definition = []
                logger.info("[KBParser] Bibliography section detected (MD).")
                continue

            if in_bibliography:
                # Capture bullet points as references
                if line.startswith(('*', '-')):
                    citation = line.lstrip('*- ').strip()
                    
                    # Find DOI
                    doi_match = doi_pattern.search(citation)
                    doi_link = None
                    if doi_match:
                        doi_raw = doi_match.group(1)
                        doi_link = f"https://doi.org/{doi_raw}"
                    
                    # Remove HTML tags if present (e.g. <a href...>) for clean text
                    clean_citation = re.sub(r'<[^>]+>', '', citation)

                    knowledge_base["references"].append({
                        "citation": clean_citation,
                        "short_citation": KnowledgeBaseParser.extract_short_citation(clean_citation),
                        "doi_link": doi_link
                    })
                else:
                    # Continuation of previous reference? Or just ignore?
                    # For now, ignore non-bullet lines in bibliography unless strictly needed.
                    pass
            else:
                # Concepts Processing
                header_match = concept_header_pattern.match(line)
                if header_match:
                    # H1, H2, H3...
                    # Generally treat header text as concept term
                    term = header_match.group(2).strip()
                    
                    # Close previous
                    if current_concept:
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": "\n".join(current_definition)
                        })
                    
                    # Remove anchor tags from term if present (e.g. <a id="foo"></a>Term)
                    term_clean = re.sub(r'<[^>]+>', '', term).strip()
                    
                    current_concept = term_clean
                    current_definition = []
                else:
                    if current_concept:
                        current_definition.append(line)

        # Flush last
        if current_concept:
            knowledge_base["concepts"].append({
                "term": current_concept,
                "definition": "\n".join(current_definition)
            })

        logger.info(f"[KBParser] Extracted {len(knowledge_base['concepts'])} concepts and {len(knowledge_base['references'])} references form MD.")
        return knowledge_base
