import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from backend.hooks.security import sanitize_text, check_banned_phrases

def test_pii():
    print("Testing PII Sanitization...")
    input_text = "My email is test@example.com and phone is 050 123 4567. Credit card 1234 5678 1234 5678."
    cleaned, threats = sanitize_text(input_text)
    
    print(f"Original: {input_text}")
    print(f"Cleaned:  {cleaned}")
    print(f"Threats:  {threats}")
    
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_PHONE_FI]" in cleaned
    assert "[REDACTED_CREDIT_CARD]" in cleaned
    assert "EMAIL: 1 items" in threats or "EMAIL" in str(threats)
    print("PII Test PASSED.")

def test_banned():
    print("\nTesting Banned Phrases...")
    input_text = "This text contains forbidden magic words."
    phrases = ["magic", "forbidden"]
    detected = check_banned_phrases(input_text, phrases)
    
    print(f"Input: {input_text}")
    print(f"Banned: {phrases}")
    print(f"Detected: {detected}")
    
    assert "magic" in detected
    assert "forbidden" in detected
    print("Banned Test PASSED.")

if __name__ == "__main__":
    try:
        test_pii()
        test_banned()
        print("\nALL SECURITY HOOK TESTS PASSED.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
