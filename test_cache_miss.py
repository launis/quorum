import hashlib
import sys

sys.path.insert(0, r"c:\src\quorum")
from backend_v2.utils.normalization import normalize_evaluation_input

text1 = "hello world"
text2 = "hello\u00a0world"
norm1 = normalize_evaluation_input(text1)
norm2 = normalize_evaluation_input(text2)

print("Norm 1:", repr(norm1))
print("Norm 2:", repr(norm2))

h1 = hashlib.md5(norm1.encode()).hexdigest()
h2 = hashlib.md5(norm2.encode()).hexdigest()

print("Hash 1:", h1)
print("Hash 2:", h2)
print("Cache Hit?", h1 == h2)

try:
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    print("Tokens 1:", enc.encode(norm1))
    print("Tokens 2:", enc.encode(norm2))
except ImportError:
    print("tiktoken not installed")
