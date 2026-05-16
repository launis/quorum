import re
import unicodedata
from rapidfuzz import fuzz

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[\W_]+", "", text)
    return text

exact_quote = "Tämä syntyy siitä, että **Luonnon kantokyky murenee**, mikä ajaa suoraan siihen, että\n**Talouden perusta rakoilee**"
source_text = "Tämä syntyy siitä, että luonnon kantokyky murenee, mikä ajaa suoraan siihen, että talouden perusta rakoilee."

norm_quote = normalize_text(exact_quote)
norm_src = normalize_text(source_text)

print(f"Norm Quote: {norm_quote}")
print(f"Norm Src: {norm_src}")
print(f"Fuzzy Match Score: {fuzz.partial_ratio(norm_quote, norm_src)}")
