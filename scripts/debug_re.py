import re
text = '### content\n{\n  "reasoning_trace": "test text abc@example.com"\n}\n\n### empty_key\n{\n  "reasoning_trace": ""\n}'
print("Eka:", text)
text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[REDACTED EMAIL]", text)
print("Toka:", text)
pattern = r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
text = re.sub(pattern, "[REDACTED PHONE]", text)
print("Kolmas:", text)
