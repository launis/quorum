import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Define Regex patterns for PII
PII_PATTERNS = {
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "PHONE_FI": r'\b(?:\+358|0)[\s-]?\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,4}\b',
    "HETU": r'\b\d{6}[+A-]\d{3}[0-9A-Z]\b', # Finnish SSN
    "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b',
    "IP_ADDRESS": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
}

def sanitize_text(text: str) -> Tuple[str, List[str]]:
    """
    Sanitizes a single string by redacting Personally Identifiable Information (PII)
    based on predefined Regex patterns (e.g. Email, SSN, Credit Card).

    Args:
        text (str): Input text to sanitize.

    Returns:
        Tuple[str, List[str]]: A tuple containing:
            1. The sanitized text with PII replaced by [REDACTED_TYPE].
            2. A list of strings describing what was detected/redacted (e.g. "EMAIL: 2 items").
    """
    if not text:
        return text, []

    threats_detected = []
    # 1. Normalize Unicode (Basic)
    clean_value = "".join(ch for ch in text if ch.isprintable())
    
    # 2. Robust PII Redaction
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, clean_value)
        if matches:
            distinct_matches = list(set(matches))
            threats_detected.append(f"{pii_type}: {len(distinct_matches)} items")
            
            # Redact
            clean_value = re.sub(pattern, f"[REDACTED_{pii_type}]", clean_value)
            
    return clean_value, threats_detected

def check_banned_phrases(text: str, phrases: List[str]) -> List[str]:
    """
    Checks if the input text contains any of the specified banned phrases (case-insensitive).

    Args:
        text (str): The text to scan.
        phrases (List[str]): List of banned phrases or keywords.

    Returns:
        List[str]: A list of unique banned phrases found in the text.
    """
    if not text or not phrases:
        return []
        
    detected = []
    text_lower = text.lower()
    for phrase in phrases:
        if phrase.lower() in text_lower:
            detected.append(phrase)
            
    return list(set(detected))
