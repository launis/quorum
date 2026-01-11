"""Security Hooks Tests."""

from backend.hooks.security import check_banned_phrases, sanitize_text


# Test PII redaction logic
def test_pii_sanitization():
    """Test standard PII redaction."""
    input_text = "My email is test@example.com and phone is 050 123 4567. Credit card 1234 5678 1234 5678."
    cleaned, threats = sanitize_text(input_text)

    # Verify content redaction
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_PHONE_FI]" in cleaned
    assert "[REDACTED_CREDIT_CARD]" in cleaned

    # Verify threats detection
    threat_str = str(threats)
    assert "EMAIL" in threat_str
    assert "PHONE" in threat_str or "CREDIT_CARD" in threat_str


# Test banned phrases logic
def test_banned_phrases_detection():
    """Test banned word detection."""
    input_text = "This text contains forbidden magic words."
    phrases = ["magic", "forbidden"]
    detected = check_banned_phrases(input_text, phrases)

    assert "magic" in detected
    assert "forbidden" in detected
    assert len(detected) == 2


def test_banned_phrases_empty():
    """Test safe text passes detection."""
    input_text = "Safe text here."
    phrases = ["magic"]
    detected = check_banned_phrases(input_text, phrases)
    assert len(detected) == 0
