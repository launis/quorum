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
    def extract_claims_from_text(text: str) -> List[Dict[str, Any]]:
        """
        Extracts sentences containing citations (claims) from text.
        Returns:
            claim_text: Clean text WITHOUT citation
            citation_text: The internal text representation of the citation (e.g. "Author 2020")
            citation_keys: Machine ID for matching (e.g. "author2020")
            original_markdown: Will be populated with Full Bibliography Reference later.
        """
        claims = []
        if not text:
            return claims

        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Regex for Markdown Link: [Text](#anchor)
        link_pattern = re.compile(r'\[([^\]]+)\]\(#([a-zA-Z0-9_-]+)\)')
        # Regex for Text Citation: (Author 2020)
        text_cit_pattern = re.compile(r'(\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\))')

        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 10: continue

            matches_link = link_pattern.findall(sent) # List of (text, anchor)
            matches_text = text_cit_pattern.findall(sent) # List of full strings "(Author 2020)"
            
            if matches_link or matches_text:
                # 1. Clean Claim Text
                clean_claim = sent
                clean_claim = link_pattern.sub('', clean_claim)
                clean_claim = text_cit_pattern.sub('', clean_claim)
                
                # Cleanup
                clean_claim = re.sub(r'\s+', ' ', clean_claim)
                clean_claim = re.sub(r'\s+\.', '.', clean_claim)
                clean_claim = re.sub(r'\s+,', ',', clean_claim)
                clean_claim = re.sub(r'\(\)', '', clean_claim)
                clean_claim = clean_claim.strip()

                # Filter out empty or punctuation-only claims
                # Must have at least 3 alphanumeric chars
                if len(re.findall(r'[a-zA-ZäöåÄÖÅ0-9]', clean_claim)) < 3:
                     continue

                if len(clean_claim) < 5: continue

                # 2. Extract Labels
                citation_labels = []
                citation_keys = []
                
                for text_p, anchor_p in matches_link:
                    citation_labels.append(text_p)
                    citation_keys.append(anchor_p)
                    
                for match_txt in matches_text:
                    lbl = match_txt.strip("()")
                    if lbl.startswith("vrt. "):
                         lbl = lbl.replace("vrt. ", "")
                    # Deduplicate
                    if lbl not in citation_labels:
                         citation_labels.append(lbl)

                claims.append({
                    "claim_text": clean_claim,
                    "citation_keys": citation_keys,
                    "citation_text": "; ".join(citation_labels), # Short citation label
                    "original_markdown": "", # To be filled with full reference
                    "matches_text_citation": bool(matches_text)
                })
        return claims

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
            "claims": [], # List of {claim_text, citation_keys...}
            "metadata": {"source": str(file_input)[:100]}
        }

        # Regex for DOI
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
            # More robust detection: Allow "Lähteet", handle longer headers (e.g. "Chapter 7: References")
            triggers = ["lähdeluettelo", "bibliography", "lähteet", "references"]
            if any(t in text.lower() for t in triggers):
                # Loose check: Heading style OR bold OR distinct short text
                is_header = "heading" in style_name or len(text) < 60
                # Could assume explicit "Lähdeluettelo" on its own line is a header
                if is_header:
                    in_bibliography = True
                    # Close previous concept if open
                    if current_concept:
                        def_text = "\n".join(current_definition)
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": def_text
                        })
                        # Extract Claims
                        section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
                        for c in section_claims:
                            c['concept_context'] = current_concept
                            knowledge_base["claims"].append(c)
                            
                        current_concept = None
                        current_definition = []
                    
                    logger.info(f"[KBParser] Bibliography section start detected at: '{text}'")
                    continue

            if in_bibliography:
                citation = text
                doi_match = doi_pattern.search(citation)
                doi_link = None
                if doi_match:
                    doi_raw = doi_match.group(1)
                    doi_link = f"https://doi.org/{doi_raw}"
                
                knowledge_base["references"].append({
                    "citation": citation,
                    "short_citation": KnowledgeBaseParser.extract_short_citation(citation),
                    "doi_link": doi_link
                })
            else:
                if "heading" in style_name and "1" not in style_name: 
                    if current_concept:
                        def_text = "\n".join(current_definition)
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": def_text
                        })
                        # Extract Claims
                        section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
                        for c in section_claims:
                            c['concept_context'] = current_concept
                            knowledge_base["claims"].append(c)

                    current_concept = text
                    current_definition = []
                elif "heading" in style_name or (len(text) < 50 and text.isupper()): 
                     if current_concept:
                        def_text = "\n".join(current_definition)
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": def_text
                        })
                        # Extract Claims
                        section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
                        for c in section_claims:
                            c['concept_context'] = current_concept
                            knowledge_base["claims"].append(c)
                     
                     current_concept = text
                     current_definition = []
                else:
                    if current_concept:
                        current_definition.append(text)
        
        # Flush last
        if current_concept:
            def_text = "\n".join(current_definition)
            knowledge_base["concepts"].append({
                "term": current_concept,
                "definition": def_text
            })
            # Extract Claims
            section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
            for c in section_claims:
                c['concept_context'] = current_concept
                knowledge_base["claims"].append(c)

        # Resolve Claims to Full References
        KnowledgeBaseParser._resolve_claims(knowledge_base)

        logger.info(f"[KBParser] Extracted {len(knowledge_base['concepts'])} concepts, {len(knowledge_base['references'])} references, and {len(knowledge_base['claims'])} claims from DOCX.")
        return knowledge_base

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalizes text by removing invisible Word artifacts.
        - Non-breaking spaces (\xa0) -> space
        - Long dashes (–, —) -> hyphen (-)
        - Multiple spaces -> single space
        """
        if not text: return ""
        text = text.replace('\xa0', ' ').replace('–', '-').replace('—', '-')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def extract_short_citation(full_entry: str) -> Optional[str]:
        """
        Extracts 'Author Year' or 'Author & Author Year' from full entry.
        Supports formats:
        - "Acemoglu, D. & Restrepo, P. 2018:"
        - "Acemoglu (2018)."
        - "Acemoglu, D. 2018."
        """
        if not full_entry:
            return None
        
        full_entry = KnowledgeBaseParser.clean_text(full_entry)

        # Regex strategies
        patterns = [
            # 1. Standard: "Name. 2023:" or "Name. 2023."
            r'^(.+?)\.\s*(\d{4}[a-z]?)[.:]', 
            # 2. Parentheses: "Name (2023)."
            r'^(.+?)\s*\((\d{4}[a-z]?)\)',
            # 3. No dot: "Name 2023" (rare but possible in headers)
            r'^(.+?)\s+(\d{4}[a-z]?)' 
        ]

        match = None
        for p in patterns:
            m = re.match(p, full_entry)
            if m:
                match = m
                break
        
        if match:
            authors_part = match.group(1)
            year = match.group(2)
            
            # Remove (toim.) / (eds.)
            authors_part = re.sub(r'\s*\(.*?\)', '', authors_part)
            
            # Extract surnames
            authors = []
            # Normalize separators to &
            authors_part = authors_part.replace(' and ', ' & ').replace(' ja ', ' & ')
            
            parts = authors_part.split('&')
            for part in parts:
                # Split by comma to get surname (assumes "Surname, Firstname")
                # If just "Surname", split returns [Surname]
                names = re.split(r'[,]', part)
                surname = names[0].strip()
                # Simple heuristic: Surname should have letters
                if surname and any(c.isalpha() for c in surname):
                    authors.append(surname)
            
            # Construct short citation
            if not authors: 
                # Fallback: use first word of authors_part if parsing failed but regex matched
                authors = [authors_part.split()[0]]

            short_authors = " & ".join(authors)
            if len(authors) > 2:
                 short_authors = f"{authors[0]} ym."
                 
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
            "claims": [], # List of {claim_text, citation_keys...}
            "metadata": {"source": "markdown_upload"}
        }

        # Regex for DOI
        doi_pattern = re.compile(r'\b(10.\d{4,9}/[-._;()/:A-Z0-9]+)\b', re.IGNORECASE)
        # Regex for Bibliography Header
        # Allow HTML tags (like <a id="...">) between #'s and the text
        bib_header_pattern = re.compile(r'^#+\s*(?:<[^>]+>\s*)*(Lähdeluettelo|Bibliography|Lähteet|References)', re.IGNORECASE)
        # Regex for Concept Header
        concept_header_pattern = re.compile(r'^(#+)\s*(.+)')
        
        # Regex for DOI
        doi_pattern = re.compile(r'\b(10.\d{4,9}/[-._;()/:A-Z0-9]+)\b', re.IGNORECASE)
        # Regex for Anchor ID in Bibliography: {#id} or <a id="id">
        anchor_pattern = re.compile(r'(?:\{\#([a-zA-Z0-9_-]+)\}|<a\s+id="([a-zA-Z0-9_-]+)">)')

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
                    def_text = "\n".join(current_definition)
                    knowledge_base["concepts"].append({
                        "term": current_concept,
                        "definition": def_text
                    })
                    # Extract Claims from this section
                    section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
                    for c in section_claims:
                        c['concept_context'] = current_concept
                        knowledge_base["claims"].append(c)

                    current_concept = None
                    current_definition = []
                logger.info("[KBParser] Bibliography section detected (MD).")
                continue

            if in_bibliography:
                # Capture bullet points as references
                if line.startswith(('*', '-')):
                    citation = line.lstrip('*- ').strip()
                    
                    # 1. Extract Anchor ID if present
                    anchor_id = None
                    anchor_match = anchor_pattern.search(citation)
                    if anchor_match:
                        # Group 1 is {#id}, Group 2 is <a id>
                        anchor_id = anchor_match.group(1) or anchor_match.group(2)
                        
                        # Remove the anchor part from citation text
                        citation = anchor_pattern.sub('', citation).strip()
                        # Also remove [] if left over from []{#id}
                        citation = citation.replace('[]', '').strip()

                    # 2. Find DOI
                    doi_match = doi_pattern.search(citation)
                    doi_link = None
                    if doi_match:
                        doi_raw = doi_match.group(1)
                        doi_link = f"https://doi.org/{doi_raw}"
                    
                    # 3. Clean
                    clean_citation = re.sub(r'<[^>]+>', '', citation)

                    knowledge_base["references"].append({
                        "citation": clean_citation,
                        "short_citation": KnowledgeBaseParser.extract_short_citation(clean_citation),
                        "doi_link": doi_link,
                        "anchor_id": anchor_id
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
                        def_text = "\n".join(current_definition)
                        knowledge_base["concepts"].append({
                            "term": current_concept,
                            "definition": def_text
                        })
                        # Extract Claims from this section
                        section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
                        for c in section_claims:
                            c['concept_context'] = current_concept
                            knowledge_base["claims"].append(c)
                    
                    # Remove anchor tags from term if present (e.g. <a id="foo"></a>Term)
                    term_clean = re.sub(r'<[^>]+>', '', term).strip()
                    
                    current_concept = term_clean
                    current_definition = []
                else:
                    if current_concept:
                        current_definition.append(line)

        # Flush last
        if current_concept:
            def_text = "\n".join(current_definition)
            knowledge_base["concepts"].append({
                "term": current_concept,
                "definition": def_text
            })
            # Extract Claims from this section
            section_claims = KnowledgeBaseParser.extract_claims_from_text(def_text)
            for c in section_claims:
                c['concept_context'] = current_concept
                knowledge_base["claims"].append(c)

        # Resolve Claims to Full References
        KnowledgeBaseParser._resolve_claims(knowledge_base)

        logger.info(f"[KBParser] Extracted {len(knowledge_base['concepts'])} concepts, {len(knowledge_base['references'])} references, and {len(knowledge_base['claims'])} claims from MD.")
        return knowledge_base

    @staticmethod
    def _resolve_claims(knowledge_base: Dict[str, Any]):
        """
        Matches claims to references to populate 'original_markdown' (Full Bibliography).
        Match Logic:
        1. Explicit ID match (claim.citation_keys -> ref.anchor_id)
        2. Short Citation match (claim.citation_text -> ref.short_citation)
        """
        refs = knowledge_base.get('references', [])
        claims = knowledge_base.get('claims', [])
        
        # Build lookup maps
        id_map = {}
        short_map = {}
        
        for r in refs:
            if r.get('anchor_id'):
                id_map[r['anchor_id']] = r['citation']
            
            sc = r.get('short_citation')
            if sc:
                short_map[sc.lower()] = r['citation']

        for c in claims:
            full_ref = None
            
            # 1. Try Key Match
            if c.get('citation_keys'):
                for key in c['citation_keys']:
                    if key in id_map:
                        full_ref = id_map[key]
                        break
            
            # 2. Try Text Match
            if not full_ref and c.get('citation_text'):
                lbl = c['citation_text'].split(';')[0].strip().lower()
                # Try direct match
                if lbl in short_map:
                    full_ref = short_map[lbl]
                else:
                    # Fuzzy / Contains match?
                    # "Acemoglu & Restrepo 2018"
                    for s_key, s_val in short_map.items():
                        if lbl in s_key or s_key in lbl:
                            full_ref = s_val
                            break
            
            if full_ref:
                c['original_markdown'] = full_ref
