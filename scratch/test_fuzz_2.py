from rapidfuzz import fuzz
import unicodedata
import re

def normalize_text(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[\W_]+", "", text)

exact = "mikä ajaa suoraan siihen, että"
source = "Tämä syntyy siitä, että luonnon kantokyky murenee, mikä ajaa suoraan siihen, että talouden perusta rakoilee."

print(fuzz.partial_ratio(normalize_text(exact), normalize_text(source)))
